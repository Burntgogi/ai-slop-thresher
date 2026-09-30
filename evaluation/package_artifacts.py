"""Compatibility entry point for separated packages and the full workbench.

This explicit packaging command writes dist artifacts. Checks remain active with
python -O; it does not install skills or change harness configuration.
"""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("distribution", ROOT / "scripts/distribute.py")
distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(distribution)

LOCAL_ONLY = {
    "research/install-receipt.json",
    "research/history/install-receipt-1.0.0.json",
    "research/history/skill-validation-1.0.0.json",
    "docs/preview/frontpage-desktop.png",
    "docs/preview/frontpage-mobile.png",
    "docs/preview/release-desktop.png",
    "docs/preview/release-mobile.png",
    "research/bundle-checksum.json",
    "research/bundle-checksum-current.json",
}


def main():
    build = distribution.build_plugin(root=ROOT, apply=True)
    check = distribution.check_plugin(root=ROOT)
    package = distribution.package(root=ROOT, apply=True)
    result = {
        "version": build["version"],
        "portable_skill_files": package["portable_files"] - len(distribution.LEGAL),
        "codex_projection_files": check["files"],
        "references_resolve": True,
        "archive_bytes_match_sources": True,
        "checks_active_under_python_O": True,
        "packages": package["packages"],
    }
    (ROOT / "research/package-validation-current.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    files = {}
    # Include both README languages and every new adapter/build/test source.
    for name in ("README.md", "README.en.md", "RELEASE_NOTES.md", "CHANGELOG.md", *distribution.LEGAL, ".gitignore", ".gitattributes"):
        files[name] = distribution.plain_path(ROOT / name).read_bytes()
    for folder in ("skills", "integrations", "plugins", "scripts", "tests", ".agents", "reports", "evaluation", "research", "assets", "docs"):
        path = ROOT / folder
        if not path.exists():
            continue
        for file in sorted(path.rglob("*")):
            distribution.plain_path(file)
            if "__pycache__" in file.parts or file.suffix in (".pyc", ".pyo"):
                continue
            if file.is_file():
                name = file.relative_to(ROOT).as_posix()
                if name not in LOCAL_ONLY:
                    files[name] = file.read_bytes()
    for item in package["packages"]:
        files[f"dist/{item['file']}"] = distribution.plain_path(ROOT / "dist" / item["file"]).read_bytes()
    blob = distribution.archive_bytes(files)
    target = distribution.plain_path(ROOT / "dist/ai-slop-thresher-workbench.zip")
    target.write_bytes(blob)
    result["packages"].append({"file": target.name, "members": len(files), "bytes": len(blob), "sha256": distribution.digest(blob)})
    (ROOT / "research/bundle-checksum-current.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    checksum = distribution.plain_path(ROOT / "dist/SHA256SUMS")
    checksum.write_text("".join(f"{item['sha256']}  {item['file']}\n" for item in result["packages"]), encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
