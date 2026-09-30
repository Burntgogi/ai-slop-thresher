"""Preserve input snapshots and validate recorded improvement evidence; no generation."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(number):
    folder = HERE / f"round-{number}"
    folder.mkdir()
    files = {}
    for source in sorted((ROOT / "skills").rglob("*")):
        if source.is_file():
            relative = source.relative_to(ROOT)
            target = folder / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            files[relative.as_posix()] = digest(target)
    files["inputs.json"] = digest(HERE / "inputs.json")
    (folder / "input-manifest.json").write_text(json.dumps({
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify():
    inputs = json.loads((HERE / "inputs.json").read_text(encoding="utf-8"))
    expected = {case["id"] for case in inputs}
    evidence = []
    for number in range(1, 6):
        folder = HERE / f"round-{number}"
        manifest = json.loads((folder / "input-manifest.json").read_text(encoding="utf-8"))
        for name, sha in manifest["files"].items():
            path = HERE / name if name == "inputs.json" else folder / name
            if digest(path) != sha:
                raise ValueError(f"input snapshot changed: round {number}: {name}")
        output = HERE / f"round-{number}-outputs.json"
        rows = json.loads(output.read_text(encoding="utf-8"))
        if len(rows) != len(expected) or {row["id"] for row in rows} != expected:
            raise ValueError(f"missing or duplicate outputs: round {number}")
        if any(not isinstance(row.get("output"), str) or not row["output"].strip() for row in rows):
            raise ValueError(f"invalid output: round {number}")
        review = json.loads((folder / "review.json").read_text(encoding="utf-8"))
        if review["output_sha256"] != digest(output):
            raise ValueError(f"review does not match raw output: round {number}")
        if set(review["case_reviews"]) != expected:
            raise ValueError(f"incomplete semantic review: round {number}")
        if not review["observations"] or not review["changes"]:
            raise ValueError(f"missing recursive rationale: round {number}")
        evidence.append({"round": number, "outputs": len(rows), "output_sha256": digest(output)})
    return {"verified": True, "rounds": evidence,
            "limits": "Integrity and coverage only. Semantic reviews are recorded judgments, not automated proof; the same Codex evaluator was reused."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("snapshot", "verify"))
    parser.add_argument("--round", type=int, choices=range(1, 6))
    args = parser.parse_args()
    if args.operation == "snapshot":
        if args.round is None:
            parser.error("snapshot requires --round")
        snapshot(args.round)
    else:
        print(json.dumps(verify(), ensure_ascii=False, indent=2))
