"""Check saved humanizer specimens. Does not generate text or detect AI authorship."""

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path


NUMBER = r"(?<![A-Za-z0-9])[-+]?\d+(?:,\d{3})*(?:\.\d+)?%?"


def numbers(text):
    return set(re.findall(NUMBER, text))


def unbound_numbers(text, bindings):
    """Each subject must be followed, in the same sentence and before another subject, by its values in order."""
    subjects = [b["subject"] for b in bindings]
    failures = []
    for binding in bindings:
        bound = False
        for sentence in re.split(r"(?<=[.!?])\s+|\n", text):
            for match in re.finditer(re.escape(binding["subject"]), sentence):
                segment = sentence[match.end():]
                ends = [segment.find(s) for s in subjects if s != binding["subject"] and s in segment]
                tokens = iter(re.findall(NUMBER, segment[:min(ends)] if ends else segment))
                if all(value in tokens for value in binding["values"]):
                    bound = True
        if not bound:
            failures.append({"type": "unbound_numbers", "subject": binding["subject"], "values": binding["values"]})
    return failures


def editable(text, protected):
    for span in sorted(protected, key=len, reverse=True):
        text = text.replace(span, " ")
    return text


def metrics(text, protected):
    prose = editable(text, protected)
    return {
        "characters": len(text),
        "staging_phrases": len(re.findall(r"흥미로운 점|흥미있는 부분|재미있는 점|재미있는 부분|주목할 점|중요하고 핵심적인 부분|시사하는 바가 크", prose)),
        "commas_in_editable_text": prose.count(","),
        "single_quote_marks_in_editable_text": sum(prose.count(x) for x in "'‘’"),
        "dash_marks_in_editable_text": len(re.findall(r"[—–]|(?m:^[ \t]*- )|(?<= )-(?= )", prose)),
        "bold_spans_in_editable_text": len(re.findall(r"\*\*[^\n]+?\*\*", prose)),
    }


def check_case(case, output):
    failures = []
    # anchor_alternatives lists wordings accepted in place of a literal anchor.
    alternatives = case.get("anchor_alternatives", {})
    for span in case.get("anchors", []):
        if not any(option in output for option in [span, *alternatives.get(span, [])]):
            failures.append({"type": "missing_anchor", "value": span})
    for span in case.get("protected", []):
        if span not in output:
            failures.append({"type": "changed_protected_span", "value": span})
    old_numbers, new_numbers = numbers(case["source"]), numbers(output)
    if old_numbers - new_numbers:
        failures.append({"type": "missing_numbers", "values": sorted(old_numbers - new_numbers)})
    added = new_numbers - old_numbers - set(case.get("allow_new_numbers", []))
    if added and not case.get("allow_new_step_numbers", False):
        failures.append({"type": "new_numbers", "values": sorted(added)})
    failures.extend(unbound_numbers(output, case.get("bound_numbers", [])))
    for span in case.get("forbidden", []):
        if span in output:
            failures.append({"type": "forbidden_wording", "value": span})
    for group in case.get("required_any", []):
        if not any(option in output for option in group):
            failures.append({"type": "missing_any", "values": group})
    for rule in case.get("min_pattern", []):
        if len(re.findall(rule["pattern"], output)) < rule["count"]:
            failures.append({"type": "pattern_below_minimum", "pattern": rule["pattern"], "count": rule["count"]})
    if "min_similarity" in case:
        ratio = SequenceMatcher(None, case["source"], output).ratio()
        if ratio < case["min_similarity"]:
            failures.append({"type": "over_edited", "similarity": round(ratio, 2)})
    after = metrics(output, case.get("protected", []))
    if not case.get("allow_decorative_format", False):
        for key in ("dash_marks_in_editable_text", "bold_spans_in_editable_text"):
            if after[key]:
                failures.append({"type": "unexpected_decoration", "metric": key, "count": after[key]})
    return {
        "id": case["id"],
        "passed": not failures,
        "failures": failures,
        "before": metrics(case["source"], case.get("protected", [])),
        "after": after,
    }


def evaluate(cases, outputs):
    by_id = {case["id"]: case for case in cases}
    ids = [row["id"] for row in outputs]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate output IDs")
    rows = [check_case(by_id[row["id"]], row["output"]) for row in outputs]
    return {
        "scope": "Saved output fixtures: literal anchors, numeric tokens, protected spans, decorative marks. Not semantic verification or an AI detector.",
        "evaluated": len(rows),
        "passed": sum(row["passed"] for row in rows),
        "failed": sum(not row["passed"] for row in rows),
        "cases": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", type=Path)
    parser.add_argument("outputs", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    data = json.loads(args.outputs.read_text(encoding="utf-8"))
    result = evaluate(cases, data["outputs"])
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, ensure_ascii=False))
    for row in result["cases"]:
        if not row["passed"]:
            print(json.dumps({"id": row["id"], "failures": row["failures"]}, ensure_ascii=False))
    return int(result["failed"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())
