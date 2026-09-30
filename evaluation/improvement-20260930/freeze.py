"""Freeze an exact text review packet; public candidate material only."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def freeze():
    names = ["README.md", "README.en.md", "CHANGELOG.md", "LICENSE", "NOTICE", "ATTRIBUTIONS.md", "docs/installation.md", "docs/verification.md",
             "scripts/distribute.py", "tests/test_distribution.py", "tests/test_legacy_report.py",
             "evaluation/package_artifacts.py", "evaluation/build_report.py", ".agents/plugins/marketplace.json",
             "research/package-validation-current.json"]
    for folder in ("skills", "integrations", "plugins"):
        names += [file.relative_to(ROOT).as_posix() for file in (ROOT / folder).rglob("*") if file.is_file()]
    for name in ("protocol.md", "inputs.json", "semantic-criteria.json", "round-1-outputs.json", "round-5-outputs.json",
                 "boundary-inputs.json", "boundary-outputs.json", "round-4-packaging.json", "round-5-legacy-before.json",
                 "round-5-legacy-after.json", "post-review-recovery.json", "record.py", "freeze.py", "validation.json"):
        names.append((HERE / name).relative_to(ROOT).as_posix())
    for number in range(1, 6):
        names.append((HERE / f"round-{number}/review.json").relative_to(ROOT).as_posix())
    entries = []
    identities = {}
    for name in sorted(set(names)):
        raw = (ROOT / name).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        identities[name] = {"bytes": len(raw), "sha256": sha}
        entries.append({"path": name, **identities[name], "utf8": raw.decode("utf-8")})
    encoded = json.dumps(identities, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    manifest = {"candidate": "1.2.0-unreleased", "base_commit": "1ce5dddaff01c4353a71bbaf2abcb03f66dd4965",
                "manifest_sha256": hashlib.sha256(encoded).hexdigest(), "files": identities,
                "scope": "Implementation, generated plugin, user docs and selected evaluation evidence. Final review responses and the report are added afterward; the workbench ZIP will be rebuilt to include them."}
    (HERE / "review-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (HERE / "review-packet.json").write_text(json.dumps({"manifest": manifest, "entries": entries}, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return manifest


if __name__ == "__main__":
    print(json.dumps(freeze(), ensure_ascii=False, indent=2))
