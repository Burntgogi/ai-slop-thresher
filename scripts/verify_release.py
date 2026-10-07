"""Read-only verification of recorded release checksums and optional source bytes."""
import argparse
import importlib.util
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_distribution", ROOT / "scripts/distribute.py")
distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(distribution)
ARCHIVES = {"ai-slop-thresher-portable.zip", "ai-slop-thresher-codex-plugin.zip",
            "ai-slop-thresher.zip", "ai-slop-thresher-workbench.zip"}


def verify_release(artifacts, source=None):
    folder = distribution.plain_path(artifacts)
    rows = {}
    for line in (folder / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if not match or match[2] in rows:
            raise distribution.DistributionError("invalid or duplicate checksum entry")
        rows[match[2]] = match[1]
    if set(rows) != ARCHIVES:
        raise distribution.DistributionError("release must record all four expected ZIPs")
    members = {}
    for name, expected in rows.items():
        path = distribution.plain_path(folder / name)
        if distribution.digest(path.read_bytes()) != expected:
            raise distribution.DistributionError(f"checksum mismatch: {name}")
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or archive.testzip() is not None:
                raise distribution.DistributionError(f"invalid ZIP members: {name}")
            members[name] = {key: archive.read(key) for key in names}
    if members["ai-slop-thresher.zip"] != members["ai-slop-thresher-portable.zip"]:
        raise distribution.DistributionError("portable compatibility ZIP differs")
    if source is not None:
        if members["ai-slop-thresher-portable.zip"] != distribution.portable_files(source):
            raise distribution.DistributionError("portable ZIP differs from the selected source")
        if members["ai-slop-thresher-codex-plugin.zip"] != distribution.plugin_files(source, claude=False):
            raise distribution.DistributionError("Codex ZIP differs from the selected source")
    return {"verified": True, "files_written": 0, "archives": sorted(rows),
            "source_bytes_checked": source is not None,
            "scope": "Recorded checksum consistency, not authenticity or semantic quality."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify_release(args.artifacts, args.source), ensure_ascii=False, indent=2))
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.exit(1, f"error: {error}\n")
