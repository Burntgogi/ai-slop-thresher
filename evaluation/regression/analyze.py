"""Judge outputs from run.py with evaluation/check_results.py and summarize them per version.

  python -B evaluation/regression/analyze.py --work ../regression-work --refs v1.2.2 WORKTREE --out ../regression-work/results.json

Every failure still needs a human read: wording checks are literal, and a pass is not a style judgment.
A run whose Codex events mention the user's installed skills is flagged as contaminated.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from cases import load_cases, label  # noqa: E402
from check_results import check_case  # noqa: E402


def describe(failure):
    detail = failure.get("value", failure.get("values", failure.get("subject", failure.get("pattern", ""))))
    return f"{failure['type']}:{detail}"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--refs", nargs="+", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    cases = load_cases()
    rows = []
    for case in cases:
        for ref in args.refs:
            folder = args.work / "out" / label(ref)
            for path in sorted(folder.glob(f"{case['id']}-*.txt"), key=lambda p: int(p.stem.rsplit("-", 1)[1])):
                output = path.read_text(encoding="utf-8").strip()
                events = path.with_suffix(".events.jsonl")
                # Installed copies: ~/.codex/skills, ~/.claude/skills, ~/.agents/skills, or a plugin cache.
                contaminated = events.exists() and bool(re.search(r"\.(codex|claude|agents)[\\/]+skills|plugins[\\/]+cache", events.read_text(encoding="utf-8"), re.I))
                result = check_case(case, output)
                rows.append({"id": case["id"], "ref": ref, "run": int(path.stem.rsplit("-", 1)[1]), "pass": result["passed"],
                             "fails": [describe(f) for f in result["failures"]], "len_ratio": round(len(output) / len(case["source"]), 2),
                             "similarity": round(SequenceMatcher(None, case["source"], output).ratio(), 2),
                             "contaminated": contaminated, "output": output})
    totals = defaultdict(lambda: [0, 0, 0.0, 0])
    for row in rows:
        total = totals[row["ref"]]
        total[0] += row["pass"]; total[1] += 1; total[2] += row["len_ratio"]; total[3] += row["contaminated"]
    for ref in args.refs:
        passed, count, ratio, contaminated = totals[ref]
        print(f"{ref}: pass {passed}/{count}, mean length ratio {ratio / max(count, 1):.2f}, contaminated {contaminated}")
    for row in rows:
        if not row["pass"]:
            print(f"  FAIL {row['ref']} {row['id']}#{row['run']}: {'; '.join(row['fails'])}")
    if args.out:
        skills = {ref: hashlib.sha256((args.work / label(ref) / "skills/ai-slop-thresher/SKILL.md").read_bytes()).hexdigest()
                  for ref in args.refs if (args.work / label(ref) / "skills/ai-slop-thresher/SKILL.md").exists()}
        report = {"refs": args.refs, "skill_sha256": skills, "rows": rows}
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
