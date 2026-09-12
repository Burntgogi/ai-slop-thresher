"""Reproduce fixture checks and verify that deliberate corruptions are caught."""

import json
from pathlib import Path

from check_results import check_case, evaluate


def main():
    root = Path(__file__).resolve().parent
    cases = json.loads((root / "cases.json").read_text(encoding="utf-8"))
    transfer = json.loads((root / "transfer-cases.json").read_text(encoding="utf-8"))
    final = json.loads((root / "final-results.json").read_text(encoding="utf-8"))["outputs"]
    assert {c["id"] for c in cases} == {r["id"] for r in final}, "Incomplete final outputs"
    summary = {}
    checks = root / "checks"
    checks.mkdir(exist_ok=True)
    for number in range(1, 6):
        data = json.loads((root / "rounds" / f"round-{number}.json").read_text(encoding="utf-8"))
        result = evaluate(cases, data["outputs"])
        assert result["failed"] == 0, result
        (checks / f"round-{number}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary[f"round_{number}"] = {k: result[k] for k in ("evaluated", "passed", "failed")}
    transfer_outputs = json.loads((root / "transfer-results.json").read_text(encoding="utf-8"))["outputs"]
    assert {c["id"] for c in transfer} == {r["id"] for r in transfer_outputs}, "Incomplete transfer outputs"
    result = evaluate(transfer, transfer_outputs)
    assert result["failed"] == 0, result
    (checks / "transfer.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
    for name, case_id, output, expected_type in corruptions:
        result = check_case(by_id[case_id], output)
        detected = any(item["type"] == expected_type for item in result["failures"])
        assert detected, (name, result)
        controls.append({"name": name, "case": case_id, "expected_failure_caught": detected})
    summary["negative_controls"] = controls
    summary["all_checks_passed"] = True
    summary["limits"] = "Checks inspect saved text only; all outputs and semantic reviews were authored by the same agent."
    (checks / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
