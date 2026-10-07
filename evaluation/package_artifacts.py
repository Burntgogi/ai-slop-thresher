"""Build candidate artifacts in a new output directory; default is a read-only plan."""
import argparse
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("distribution", ROOT / "scripts/distribute.py")
distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(distribution)

LOCAL_ONLY = {
    "research/install-receipt.json", "research/history/install-receipt-1.0.0.json",
    "research/history/skill-validation-1.0.0.json", "research/bundle-checksum.json",
    "research/bundle-checksum-current.json", "docs/preview/frontpage-desktop.png",
    "docs/preview/frontpage-mobile.png", "docs/preview/release-desktop.png",
    "docs/preview/release-mobile.png",
}
ROOT_FILES = {"README.md", "README.en.md", "RELEASE_NOTES.md", "CHANGELOG.md",
              *distribution.LEGAL, ".gitignore", ".gitattributes"}
FOLDERS = {"skills", "integrations", "plugins", "scripts", "tests", ".agents", ".claude-plugin", ".github",
           "reports", "evaluation", "research", "assets", "docs"}


def source_names(root, include):
    # Workbench archives carry the source inventory for rebuilding without Git.
    inventory = root / "research/build-inputs.json"
    if (root / ".git").exists():
        result = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                                check=True, capture_output=True)
        names = result.stdout.decode("utf-8").split("\0")
    elif inventory.is_file():
        names = json.loads(inventory.read_text(encoding="utf-8"))["files"]
    else:
        raise distribution.DistributionError("source requires Git or research/build-inputs.json")
    selected = set()
    for name in [*names, *include]:
        if not name:
            continue
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise distribution.DistributionError(f"invalid source member: {name}")
        if name in LOCAL_ONLY or "__pycache__" in relative.parts or relative.suffix in (".pyc", ".pyo"):
            continue
        if name in ROOT_FILES or relative.parts[0] in FOLDERS:
            distribution.plain_path(root / relative)
            selected.add(relative.as_posix())
        elif name in include:
            raise distribution.DistributionError(f"source outside the workbench scope: {name}")
    return sorted(selected)


def build_artifacts(root=ROOT, output=None, apply=False, include=()):
    root = distribution.plain_path(root).resolve()
    portable = distribution.portable_files(root)
    plugin = distribution.plugin_files(root)  # repo projection shared by Codex and Claude Code
    codex_store = distribution.plugin_files(root, claude=False)
    selected = source_names(root, include)
    destination = distribution.plain_path(output).resolve() if output is not None else None
    if apply and destination is None:
        raise distribution.DistributionError("--apply requires an explicit new --output directory")
    if destination is not None and (destination.is_relative_to(root) or destination.exists()):
        raise distribution.DistributionError("output must be a new directory outside the source tree")
    result = {"version": distribution.version(root), "dry_run": not apply,
              "output": str(destination) if destination else None, "source_files": len(selected),
              "source_files_selected": selected, "files_written_to_source": 0}
    if not apply:
        return result
    archives = {"ai-slop-thresher-portable.zip": distribution.archive_bytes(portable),
                "ai-slop-thresher-codex-plugin.zip": distribution.archive_bytes(codex_store)}
    archives["ai-slop-thresher.zip"] = archives["ai-slop-thresher-portable.zip"]
    files = {name: (root / name).read_bytes() for name in selected}
    prefix = distribution.PLUGIN_DIR + "/"
    for name in list(files):
        if name.startswith(prefix):
            del files[name]
    files.update({prefix + name: data for name, data in plugin.items()})
    files[prefix + distribution.RECEIPT] = (json.dumps({name: distribution.digest(data) for name, data in plugin.items()}, indent=2)+"\n").encode()
    files["research/build-inputs.json"] = (json.dumps({"files": selected}, indent=2)+"\n").encode()
    files["research/package-validation-current.json"] = (json.dumps({
        "version": result["version"], "portable_skill_files": len(portable)-len(distribution.LEGAL),
        "plugin_projection_files": len(plugin), "codex_store_files": len(codex_store), "references_resolve": True,
        "archive_bytes_match_sources": True,
        "packages": [{"file": name, "bytes": len(data), "sha256": distribution.digest(data)}
                     for name, data in archives.items()],
    }, indent=2)+"\n").encode()
    files.update({"dist/" + name: data for name, data in archives.items()})
    archives["ai-slop-thresher-workbench.zip"] = distribution.archive_bytes(files)
    result["packages"] = [{"file": name, "bytes": len(data), "sha256": distribution.digest(data)} for name, data in archives.items()]
    result["source_sha256"] = {name: distribution.digest((root/name).read_bytes()) for name in selected}
    result["generated_workbench_members"] = ["research/build-inputs.json", "research/package-validation-current.json", prefix + distribution.RECEIPT]
    destination.mkdir(parents=True)
    payloads = {**archives,
                "SHA256SUMS": "".join(f"{x['sha256']}  {x['file']}\n" for x in result["packages"]).encode(),
                "build-report.json": (json.dumps(result, ensure_ascii=False, indent=2)+"\n").encode("utf-8")}
    for name, data in payloads.items():
        with (destination / name).open("xb") as stream:
            stream.write(data)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--include", action="append", default=[], help="explicit additional source-relative file")
    args = parser.parse_args()
    try:
        print(json.dumps(build_artifacts(output=args.output, apply=args.apply, include=args.include), ensure_ascii=False, indent=2))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f"error: {error}\n")
