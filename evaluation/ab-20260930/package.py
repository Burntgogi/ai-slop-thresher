"""Package the follow-up A/B evidence separately from immutable release ZIPs."""
import hashlib
import importlib.util
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    specification = importlib.util.spec_from_file_location("distribution", ROOT / "scripts/distribute.py")
    distribution = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(distribution)
    files = {}
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    for name in ("reports/ab-comparison-20260930.md", "reports/ab-method-review-20260930.md", "LICENSE", "NOTICE", "ATTRIBUTIONS.md"):
        files[name] = (ROOT / name).read_bytes()
    blob = distribution.archive_bytes(files)
    target = ROOT / "dist/ai-slop-thresher-ab-v1.1.0-v1.2.0.zip"
    target.write_bytes(blob)
    report = ROOT / "dist/ab-comparison-v1.1.0-v1.2.0.md"
    report.write_bytes((ROOT / "reports/ab-comparison-20260930.md").read_bytes())
    checksums = "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in (target, report))
    (ROOT / "dist/AB_SHA256SUMS").write_text(checksums, encoding="utf-8", newline="\n")
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None or {n: archive.read(n) for n in archive.namelist()} != files:
            raise RuntimeError("A/B evidence package mismatch")
    print(f"Packaged {len(files)} evidence files; {len(blob)} ZIP bytes. Original release ZIPs and SHA256SUMS unchanged.")


if __name__ == "__main__":
    main()
