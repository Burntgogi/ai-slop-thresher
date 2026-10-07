import json, re, sys
from difflib import SequenceMatcher
from pathlib import Path
# Usage: analyze.py <work dir used by run.py>; writes results.json next to this script
R = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; repo = HERE.parents[1]
sys.path.insert(0, str(repo / "evaluation"))
from check_results import check_case
cases = (json.loads((repo/"evaluation/cases.json").read_text(encoding="utf-8"))
         + json.loads((repo/"evaluation/transfer-cases.json").read_text(encoding="utf-8"))
         + json.loads((HERE/"probes.json").read_text(encoding="utf-8")))
bind = json.loads((repo/"evaluation/number-bindings.json").read_text(encoding="utf-8"))["cases"]
for c in cases:
    if c["id"] in bind: c["bound_numbers"] = bind[c["id"]]
def extra(c, out):
    f = []
    for s in c.get("forbidden", []):
        if s in out: f.append(f"forbidden:{s}")
    for group in c.get("required_any", []):
        if not any(g in out for g in group): f.append(f"missing_any:{'/'.join(group)}")
    if c.get("min_possibility") and len(re.findall(r"수 있|가능성", out)) < c["min_possibility"]: f.append("possibility_weakened")
    if c.get("expect_minimal") and SequenceMatcher(None, c["source"], out).ratio() < 0.85: f.append("over_edited_natural_text")
    return f
rows = []
for c in cases:
    for v in ("v1.2.0", "v1.2.1", "v1.2.2"):
        for p in sorted((R/"out"/v).glob(f"{c['id']}-*.txt"), key=lambda q: int(q.stem.rsplit("-", 1)[1])):
            n = int(p.stem.rsplit("-", 1)[1])
            out = p.read_text(encoding="utf-8").strip()
            ev = (R/"out"/v/f"{c['id']}-{n}.events.jsonl")
            contaminated = bool(ev.exists() and re.search(r"\.codex[\/]+skills", ev.read_text(encoding="utf-8"), re.I))
            r = check_case(c, out)
            fails = [x["type"] + (":" + str(x.get("value", x.get("values", x.get("subject", ""))))) for x in r["failures"]] + extra(c, out)
            rows.append({"id": c["id"], "v": v, "n": n, "pass": not fails, "fails": fails, "len_ratio": round(len(out)/len(c["source"]), 2),
                         "sim": round(SequenceMatcher(None, c["source"], out).ratio(), 2), "contaminated": contaminated, "out": out})
import hashlib
meta = {"model": "gpt-6.1-sol", "reasoning_effort": "xhigh", "harness": "codex exec 0.160.1, read-only sandbox, ephemeral", "date": "2026-10-07",
        "skill_sha256": {v: hashlib.sha256((R/v/"skills/ai-slop-thresher/SKILL.md").read_bytes()).hexdigest() for v in ("v1.2.0", "v1.2.1", "v1.2.2") if (R/v).exists()},
        "installed_skill_reads": sum(r["contaminated"] for r in rows), "rows": rows}
json.dump(meta, open(HERE/"results.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
from collections import defaultdict
agg = defaultdict(lambda: [0, 0, 0.0, 0])
for r in rows:
    a = agg[r["v"]]; a[0] += r["pass"]; a[1] += 1; a[2] += r["len_ratio"]; a[3] += r["contaminated"]
for v, (p, t, lr, cont) in sorted(agg.items()): print(f"{v}: pass {p}/{t}, mean length ratio {lr/t:.2f}, contaminated {cont}")
print("\nper-case (v1.2.0 runs | v1.2.1 runs):")
for c in cases:
    s = lambda v: " ".join(("P" if r["pass"] else "F") for r in rows if r["id"] == c["id"] and r["v"] == v)
    l = lambda v: "/".join(str(r["len_ratio"]) for r in rows if r["id"] == c["id"] and r["v"] == v)
    fl = sorted({f for r in rows if r["id"] == c["id"] for f in r["fails"]})
    print(f"{c['id']:4} {s('v1.2.0'):5} | {s('v1.2.1'):5}  len {l('v1.2.0'):9} | {l('v1.2.1'):9} {('  '+'; '.join(fl)) if fl else ''}")
