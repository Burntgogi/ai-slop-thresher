"""Build anonymized, randomized pairs without exposing release mapping."""
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def write(name, value):
    path = HERE / name
    if path.exists():
        raise RuntimeError("Refusing to overwrite frozen judge material: " + name)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main(repetition):
    manifest = read("experiment-manifest.json")
    cases = read("inputs.json")
    expected = {c["id"] for c in cases}
    results = {}
    hashes = {}
    for arm in ("q", "r"):
        name = f"outputs-{arm}-{repetition}.json"
        rows = read(name)
        if len(rows) != 28 or {x["id"] for x in rows} != expected or any(not isinstance(x["output"], str) or not x["output"].strip() for x in rows):
            raise RuntimeError("Output coverage mismatch: " + name)
        results[arm] = {row["id"]: row["output"] for row in rows}
        hashes[name] = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    rng = random.Random(manifest["assignment_seed"] ^ (repetition * 104729))
    rng.shuffle(cases)
    pairs, mapping = [], {}
    for index, case in enumerate(cases, 1):
        left = rng.choice(("q", "r"))
        right = "r" if left == "q" else "q"
        identity = f"P{repetition}-{index:02d}"
        pairs.append({"pair_id": identity, "case_id": case["id"], "request": case["request"], "source": case["source"], "left": results[left][case["id"]], "right": results[right][case["id"]]})
        mapping[identity] = {"case_id": case["id"], "left": left, "right": right, "suite": case["suite"]}
    write(f"judge-pairs-{repetition}.json", pairs)
    write(f"judge-mapping-{repetition}.json", {"repetition": repetition, "output_sha256": hashes, "pairs": mapping})
    print(json.dumps({"pairs": len(pairs), "repetition": repetition, "output_sha256": hashes}, indent=2))


if __name__ == "__main__":
    main(int(sys.argv[1]))
