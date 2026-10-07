import json, os, subprocess, sys, concurrent.futures as cf, time
from pathlib import Path
# Usage: run.py <work dir containing v1.2.0/skills and v1.2.1/skills>
R = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; repo = HERE.parents[1]
CODEX = os.environ.get("CODEX_BIN", "codex")  # codex-cli 0.160.1 was used
cases = (json.loads((repo/"evaluation/cases.json").read_text(encoding="utf-8"))
         + json.loads((repo/"evaluation/transfer-cases.json").read_text(encoding="utf-8"))
         + json.loads((HERE/"probes.json").read_text(encoding="utf-8")))
def run(job):
    v, c, n = job
    out = R/"out"/v/f"{c['id']}-{n}.txt"
    if out.exists() and out.stat().st_size: return
    out.parent.mkdir(parents=True, exist_ok=True)
    prompt = ("이 폴더의 skills/ai-slop-thresher/SKILL.md를 읽고 그 지침(필요하면 references 포함)만 따라 아래 요청을 처리하라. "
              "다른 위치의 스킬은 사용하지 마라. 파일을 만들거나 고치지 말고 결과 텍스트만 출력하라.\n\n"
              f"요청: {c['request']}\n\n원문:\n<<<\n{c['source']}\n>>>")
    for attempt in range(3):
        t = time.time()
        p = subprocess.run([CODEX,"exec","-m","gpt-6.1-sol","-c","model_reasoning_effort=xhigh","-s","read-only",
                            "--skip-git-repo-check","--ephemeral","--json","-o",str(out),prompt],
                           cwd=R/v, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=900)
        (R/"out"/v/f"{c['id']}-{n}.events.jsonl").write_text(p.stdout, encoding="utf-8")
        if p.returncode == 0 and out.exists() and out.stat().st_size: break
        (R/"out"/v/f"{c['id']}-{n}.err").write_text(p.stderr[-3000:], encoding="utf-8"); time.sleep(20)
    print(v, c["id"], n, round(time.time()-t), flush=True)
jobs = [(v, c, n) for n in (1, 2) for c in cases for v in ("v1.2.0", "v1.2.1")]
with cf.ThreadPoolExecutor(4) as ex: list(ex.map(run, jobs))
print("done", len(jobs))
