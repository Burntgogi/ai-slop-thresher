"""Verify frozen evidence and unblind the recorded judgments; no text scoring."""
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    experiment = read("experiment-manifest.json")
    raw_cases = read("inputs.json")
    cases = {c["id"]: c for c in raw_cases}
    if len(raw_cases) != 28 or len(cases) != 28:
        raise RuntimeError("Input case identities are not 28 unique cases")
    for name, expected in experiment["pre_generation_sha256"].items():
        if digest(HERE / name) != expected:
            raise RuntimeError("Frozen input changed: " + name)
    tags = {arm: a["tag"] for arm, a in experiment["arms"].items()}
    for arm, artifact in experiment["arms"].items():
        archive_path = HERE / "artifacts" / artifact["tag"] / artifact["asset_name"]
        if digest(archive_path) != artifact["asset_sha256"] or archive_path.stat().st_size != artifact["asset_bytes"]:
            raise RuntimeError("Release asset changed")
        with zipfile.ZipFile(archive_path) as archive:
            if archive.testzip() is not None or set(archive.namelist()) != set(artifact["members"]):
                raise RuntimeError("Release archive members changed")
            for name, identity in artifact["members"].items():
                data = archive.read(name)
                if identity != {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}:
                    raise RuntimeError("Release member differs from frozen identity")
            for name in ("SKILL.md", "edge-cases.md"):
                member = "ai-slop-thresher/" + (name if name == "SKILL.md" else "references/" + name)
                if (HERE / "arms" / arm / name).read_bytes() != archive.read(member):
                    raise RuntimeError("Applied skill differs from downloaded release")
    suites = {name: {tag: Counter(total=0, semantic_pass=0, request_pass=0, both_pass=0) for tag in tags.values()} for name in ("all", "development", "new")}
    preferences = {name: Counter(left=0, right=0, tie=0, not_comparable=0, **{tag: 0 for tag in tags.values()}) for name in suites}
    rows = []
    for repetition in (1, 2):
        mapping = read(f"judge-mapping-{repetition}.json")
        raw_packet = read(f"judge-pairs-{repetition}.json")
        packet = {p["pair_id"]: p for p in raw_packet}
        if len(raw_packet) != 28 or len(packet) != 28 or {p["case_id"] for p in raw_packet} != set(cases):
            raise RuntimeError("Packet pair/case coverage mismatch")
        if set(mapping["pairs"]) != set(packet) or mapping["repetition"] != repetition:
            raise RuntimeError("Mapping pair coverage/repetition mismatch")
        judgments = read(f"judgments-{repetition}.json")
        if len(judgments) != 28 or {j["pair_id"] for j in judgments} != set(packet):
            raise RuntimeError("Judge coverage mismatch")
        expected_output_names = {f"outputs-{arm}-{repetition}.json" for arm in tags}
        if set(mapping["output_sha256"]) != expected_output_names:
            raise RuntimeError("Mapping output hash coverage mismatch")
        for name, expected in mapping["output_sha256"].items():
            if digest(HERE / name) != expected:
                raise RuntimeError("Raw generation changed: " + name)
        outputs = {}
        for arm in tags:
            raw_output = read(f"outputs-{arm}-{repetition}.json")
            if len(raw_output) != 28 or {o["id"] for o in raw_output} != set(cases) or any(not isinstance(o["output"], str) or not o["output"].strip() for o in raw_output):
                raise RuntimeError("Raw output identity/coverage mismatch")
            outputs[arm] = {o["id"]: o["output"] for o in raw_output}
        for arm in tags:
            run = read(f"run-{arm}-{repetition}.json")
            if run["case_count"] != 28 or run["self_edits_after_generation"] is not False or run["agent_id"] != f"/root/ab_{arm}{repetition}":
                raise RuntimeError("Generator metadata mismatch")
            expected_inputs = {f"arms/{arm}/SKILL.md", f"arms/{arm}/edge-cases.md", f"generation-inputs-{repetition}.json"}
            if set(run["input_sha256"]) != expected_inputs:
                raise RuntimeError("Generator input hash coverage/arm mismatch")
            for name, expected in run["input_sha256"].items():
                if digest(HERE / name) != expected.lower():
                    raise RuntimeError("Generator input hash mismatch: " + name)
        judge_run = read(f"judge-run-{repetition}.json")
        if judge_run.get("version_mapping_not_provided") is not True or judge_run.get("agent_id") != f"/root/ab_judge{repetition}" or judge_run.get("pair_count") != 28:
            raise RuntimeError("Judge blinding record missing")
        if "input_sha256" in judge_run:
            judge_hashes = judge_run["input_sha256"]
        else:
            raw_hashes = judge_run.get("input_files", [])
            judge_hashes = {x["path"]: x["sha256"] for x in raw_hashes}
            if len(raw_hashes) != len(judge_hashes):
                raise RuntimeError("Duplicate judge input hash identity")
        if set(judge_hashes) != {"judge-rubric.md", f"judge-pairs-{repetition}.json"}:
            raise RuntimeError("Judge input hash coverage mismatch")
        if any(digest(HERE / name) != expected.lower() for name, expected in judge_hashes.items()):
            raise RuntimeError("Judge input changed after recorded read")
        for judgment in judgments:
            identity = judgment["pair_id"]
            pair, assignment = packet[identity], mapping["pairs"][identity]
            case_id = pair["case_id"]
            if judgment["case_id"] != case_id or assignment["case_id"] != case_id:
                raise RuntimeError("Pair identity mismatch")
            if {assignment["left"], assignment["right"]} != {"q", "r"} or assignment["suite"] != cases[case_id]["suite"]:
                raise RuntimeError("Pair arm/suite assignment mismatch")
            if pair["source"] != cases[case_id]["source"] or pair["request"] != cases[case_id]["request"]:
                raise RuntimeError("Judge source changed")
            eligible = True
            resolved = {}
            for side in ("left", "right"):
                arm = assignment[side]
                if pair[side] != outputs[arm][case_id]:
                    raise RuntimeError("Judge output changed")
                verdict = judgment[side]
                if any(type(verdict[k]) is not bool for k in ("semantic_pass", "request_pass")):
                    raise RuntimeError("Non-boolean verdict")
                if not isinstance(verdict["issues"], list) or any(not isinstance(x, str) for x in verdict["issues"]) or not isinstance(verdict["evidence"], str) or not verdict["evidence"].strip():
                    raise RuntimeError("Judge evidence missing")
                both = verdict["semantic_pass"] and verdict["request_pass"]
                eligible &= both
                tag = tags[arm]
                resolved[tag] = {**verdict, "output": pair[side]}
                for suite in ("all", assignment["suite"]):
                    count = suites[suite][tag]
                    count.update(total=1, semantic_pass=int(verdict["semantic_pass"]), request_pass=int(verdict["request_pass"]), both_pass=int(both))
            winner = judgment["style_winner"]
            if not isinstance(judgment["style_reason"], str) or not judgment["style_reason"].strip():
                raise RuntimeError("Style comparison evidence missing")
            if winner not in ("left", "right", "tie", "not_comparable") or (eligible != (winner != "not_comparable")):
                raise RuntimeError("Style eligibility mismatch")
            unblinded = tags[assignment[winner]] if winner in ("left", "right") else winner
            for suite in ("all", assignment["suite"]):
                preferences[suite][unblinded] += 1
                if winner in ("left", "right"):
                    preferences[suite][winner] += 1
            rows.append({"pair_id": identity, "repetition": repetition, "case_id": case_id, "suite": assignment["suite"],
                         "source": pair["source"], "request": pair["request"], "versions": resolved,
                         "style_winner": unblinded, "style_reason": judgment["style_reason"]})
    counts = {suite: {tag: dict(counter) for tag, counter in table.items()} for suite, table in suites.items()}
    result = {"cases": 28, "development_cases": 18, "new_cases": 10, "repetitions": 2, "outputs": 112, "pairs": 56,
              "counts": counts, "style_preferences": {name: dict(c) for name, c in preferences.items()},
              "failed_outputs": [{"pair_id": row["pair_id"], "case_id": row["case_id"], "repetition": row["repetition"], "tag": tag,
                                  "semantic_pass": value["semantic_pass"], "request_pass": value["request_pass"], "issues": value["issues"], "evidence": value["evidence"]}
                                 for row in rows for tag, value in row["versions"].items() if not (value["semantic_pass"] and value["request_pass"])],
              "scope": "Recorded blinded agent judgments on synthetic cases, repeated within the same Codex harness; not independent human or cross-model performance."}
    write("unblinded-results.json", rows)
    write("summary.json", result)
    hashes = {p.relative_to(HERE).as_posix(): digest(p) for p in sorted(HERE.rglob("*")) if p.is_file() and p.name != "integrity.json" and "__pycache__" not in p.parts}
    write("integrity.json", {"inventory_kind": "Post-evaluation inventory, not independently signed proof of generation", "sha256": hashes, "frozen_inputs_match": True, "output_pairs_match_originals": True, "coverage_verified": True})
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
