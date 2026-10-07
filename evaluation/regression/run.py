"""Run skill versions on the saved fixtures and probes with Codex, for release-to-release comparison.

Each ref is a git tag/commit, or WORKTREE for the current skills/ folder. Outputs go to
<work>/out/<label>/<case>-<run>.txt with Codex JSON events beside them. Existing outputs are kept,
so an interrupted run can be resumed.

  python -B evaluation/regression/run.py --work ../regression-work --refs v1.2.2 WORKTREE
  python -B evaluation/regression/run.py --work ../regression-work --refs WORKTREE --cases C08,P05 --runs 4

The Codex binary comes from CODEX_BIN or --codex. Runs use a read-only sandbox and ephemeral sessions.
"""

import argparse
import concurrent.futures as cf
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cases import ROOT, load_cases, label  # noqa: E402

PROMPT = ("이 폴더의 skills/ai-slop-thresher/SKILL.md를 읽고 그 지침(필요하면 references 포함)만 따라 아래 요청을 처리하라. "
          "다른 위치의 스킬은 사용하지 마라. 파일을 만들거나 고치지 말고 결과 텍스트만 출력하라.\n\n요청: {request}\n\n원문:\n<<<\n{source}\n>>>")


def prepare(work, ref):
    target = work / label(ref)
    if ref == "WORKTREE" and (target / "skills").exists():
        shutil.rmtree(target / "skills")  # always compare the current instructions
    elif (target / "skills").exists():
        return target
    target.mkdir(parents=True, exist_ok=True)
    if ref == "WORKTREE":
        shutil.copytree(ROOT / "skills", target / "skills")
    else:
        archive = subprocess.run(["git", "-C", str(ROOT), "archive", ref, "skills"], capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(target)], input=archive, check=True)
    return target


def run_one(args, folder, case, n):
    out = args.work / "out" / folder.name / f"{case['id']}-{n}.txt"
    if out.exists() and out.stat().st_size:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    command = [args.codex, "exec", "-m", args.model, "-c", f"model_reasoning_effort={args.effort}", "-s", "read-only",
               "--skip-git-repo-check", "--ephemeral", "--json", "-o", str(out),
               PROMPT.format(request=case["request"], source=case["source"])]
    for attempt in range(3):
        started = time.time()
        done = subprocess.run(command, cwd=folder, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=900)
        out.with_suffix(".events.jsonl").write_text(done.stdout, encoding="utf-8")
        if done.returncode == 0 and out.exists() and out.stat().st_size:
            break
        out.with_suffix(".err").write_text(done.stderr[-3000:], encoding="utf-8")
        time.sleep(20)
    else:
        if out.exists():  # a partial answer must not count as a finished run on resume
            out.replace(out.with_suffix(".failed.txt"))
    print(folder.name, case["id"], n, round(time.time() - started), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--refs", nargs="+", required=True)
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--cases", help="comma-separated ids; default all fixtures and probes")
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--effort", default="xhigh")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--codex", default=os.environ.get("CODEX_BIN", "codex"))
    args = parser.parse_args()
    args.work = args.work.resolve()
    if args.work.is_relative_to(ROOT):
        parser.error("--work must be outside the repository")
    cases = load_cases()
    if args.cases:
        wanted = set(args.cases.split(","))
        cases = [case for case in cases if case["id"] in wanted]
    folders = [prepare(args.work, ref) for ref in args.refs]
    jobs = [(folder, case, n) for n in range(1, args.runs + 1) for case in cases for folder in folders]
    with cf.ThreadPoolExecutor(args.workers) as pool:
        list(pool.map(lambda job: run_one(args, *job), jobs))
    print("done", len(jobs))


if __name__ == "__main__":
    main()
