"""Reproduce fixture checks and verify that deliberate corruptions are caught."""

import argparse
import json
from pathlib import Path

from check_results import check_case, evaluate


def main(output=None):
    root = Path(__file__).resolve().parent
    cases = json.loads((root / "cases.json").read_text(encoding="utf-8"))
    transfer = json.loads((root / "transfer-cases.json").read_text(encoding="utf-8"))
    final = json.loads((root / "final-results.json").read_text(encoding="utf-8"))["outputs"]
    assert {c["id"] for c in cases} == {r["id"] for r in final}, "Incomplete final outputs"
    summary = {}
    results = {}
    for number in range(1, 6):
        data = json.loads((root / "rounds" / f"round-{number}.json").read_text(encoding="utf-8"))
        result = evaluate(cases, data["outputs"])
        assert result["failed"] == 0, result
        results[f"round-{number}.json"] = result
        summary[f"round_{number}"] = {k: result[k] for k in ("evaluated", "passed", "failed")}
    transfer_outputs = json.loads((root / "transfer-results.json").read_text(encoding="utf-8"))["outputs"]
    assert {c["id"] for c in transfer} == {r["id"] for r in transfer_outputs}, "Incomplete transfer outputs"
    result = evaluate(transfer, transfer_outputs)
    assert result["failed"] == 0, result
    results["transfer.json"] = result
    summary["transfer"] = {k: result[k] for k in ("evaluated", "passed", "failed")}

    by_id = {case["id"]: case for case in cases}
    text_by_id = {row["id"]: row["output"] for row in final}
    corruptions = [
        ("changed_amount", "C05", text_by_id["C05"].replace("3,000원", "5,000원"), "new_numbers"),
        ("changed_command", "C06", text_by_id["C06"].replace("--dry-run", "--apply"), "changed_protected_span"),
        ("changed_quote", "C07", text_by_id["C07"].replace("최종 승인은 아니라는", "최종 승인이라는"), "changed_protected_span"),
        ("dropped_feature", "C09", text_by_id["C09"].replace("OCR 추출, ", ""), "missing_anchor"),
    ]
    controls = []
    for name, case_id, corrupted_output, expected_type in corruptions:
        result = check_case(by_id[case_id], corrupted_output)
        detected = any(item["type"] == expected_type for item in result["failures"])
        assert detected, (name, result)
        controls.append({"name": name, "case": case_id, "expected_failure_caught": detected})
    summary["negative_controls"] = controls
    summary["all_checks_passed"] = True
    summary["limits"] = "Checks inspect saved text only; all outputs and semantic reviews were authored by the same agent."
    results["summary.json"] = summary
    if output is not None:
        output = Path(output).resolve()
        if output.is_relative_to(root) or output.exists():
            raise ValueError("results require a new directory outside the frozen evaluation tree")
        output.mkdir(parents=True)
        for name, value in results.items():
            with (output / name).open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply and args.output is None:
        parser.error("--apply requires --output")
    main(args.output if args.apply else None)
