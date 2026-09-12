"""Package only deliverables and check every member against the source bytes."""

import hashlib
import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_ONLY = {
    "research/install-receipt.json",
    "research/history/install-receipt-1.0.0.json",
    "research/history/skill-validation-1.0.0.json",
    "docs/preview/frontpage-desktop.png",
    "docs/preview/frontpage-mobile.png",
    "docs/preview/release-desktop.png",
    "docs/preview/release-mobile.png",
}


def bundle(target, entries):
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file, name in entries:
            archive.write(file, name)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(entries)
        for file, name in entries:
            assert archive.read(name) == file.read_bytes(), name
    return {"file": target.name, "members": len(entries), "bytes": target.stat().st_size, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}


def main():
    skill = ROOT / "skills/ai-slop-thresher"
    files = sorted(p for p in skill.rglob("*") if p.is_file())
    expected = {"SKILL.md", "agents/openai.yaml", "references/edge-cases.md", "references/design-sources.md"}
    assert {p.relative_to(skill).as_posix() for p in files} == expected
    shortcut = ROOT / "skills/thresh"
    shortcut_files = sorted(p for p in shortcut.rglob("*") if p.is_file())
    assert {p.relative_to(shortcut).as_posix() for p in shortcut_files} == {"SKILL.md", "agents/openai.yaml"}
    all_files = files + shortcut_files
    for file in (p for p in all_files if p.suffix == ".md"):
        body = file.read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", body):
            if "://" not in link:
                assert (file.parent / link).is_file(), (file, link)
        assert "[TODO:" not in body
    dist = ROOT / "dist"
    package_entries = [(p, p.relative_to(ROOT / "skills").as_posix()) for p in all_files]
    package_entries.append((ROOT / "LICENSE", "LICENSE"))
    package_entries.append((ROOT / "ATTRIBUTIONS.md", "ATTRIBUTIONS.md"))
    package_entries.append((ROOT / "NOTICE", "NOTICE"))
    packages = [bundle(dist / "ai-slop-thresher.zip", package_entries)]
    result = {"skill_files": len(all_files), "references_resolve": True, "archive_bytes_match_sources": True, "packages": list(packages)}
    (ROOT / "research/package-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    entries = [(ROOT / name, name) for name in ("README.md", "RELEASE_NOTES.md", "CHANGELOG.md", "LICENSE", "ATTRIBUTIONS.md", "NOTICE", ".gitignore", ".gitattributes")]
    for folder in ("skills", "reports", "evaluation", "research", "assets", "docs"):
        for p in sorted((ROOT / folder).rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.name != "bundle-checksum.json" and p.relative_to(ROOT).as_posix() not in LOCAL_ONLY:
                entries.append((p, p.relative_to(ROOT).as_posix()))
    entries.append((dist / "ai-slop-thresher.zip", "dist/ai-slop-thresher.zip"))
    packages.append(bundle(dist / "ai-slop-thresher-workbench.zip", entries))
    result = {"skill_files": len(all_files), "references_resolve": True, "archive_bytes_match_sources": True, "packages": packages}
    (ROOT / "research/bundle-checksum.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (dist / "SHA256SUMS").write_text("".join(f"{p['sha256']}  {p['file']}\n" for p in packages), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
