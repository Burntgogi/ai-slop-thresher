"""Fixtures and probes for execution comparisons, with the relation and wording overlays applied."""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVALUATION = ROOT / "evaluation"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases():
    cases = read(EVALUATION / "cases.json") + read(EVALUATION / "transfer-cases.json") + read(HERE / "probes.json")
    bindings = read(EVALUATION / "number-bindings.json")["cases"]
    alternatives = read(EVALUATION / "anchor-alternatives.json")["cases"]
    for case in cases:
        if case["id"] in bindings:
            case["bound_numbers"] = bindings[case["id"]]
        if case["id"] in alternatives:
            case["anchor_alternatives"] = {**case.get("anchor_alternatives", {}), **alternatives[case["id"]]}
    return cases


def label(ref):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", ref)
