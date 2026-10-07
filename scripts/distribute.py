"""Build separated distributions and install skills without altering harness settings.

Python 3.10+, standard library only. All CLI commands default to a dry run.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("ai-slop-thresher", "thresh")
LEGAL = ("LICENSE", "NOTICE", "ATTRIBUTIONS.md")
TARGETS = {
    "codex": {"user": ".agents/skills", "project": ".agents/skills"},
    "claude-code": {"user": ".claude/skills", "project": ".claude/skills"},
    "opencode": {"user": ".config/opencode/skills", "project": ".opencode/skills"},
    "cursor": {"user": ".cursor/skills", "project": ".cursor/skills"},
}
RECEIPT = ".build-receipt.json"
# One plugin directory serves Codex (.codex-plugin) and Claude Code (.claude-plugin).
PLUGIN_DIR = "plugins/ai-slop-thresher"
CLAUDE_DIR = "integrations/claude-code"


class DistributionError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def plain_path(path):
    """Reject symlinks and Windows junctions before resolving any existing ancestor."""
    absolute = Path(os.path.abspath(Path(path).expanduser()))
    for part in (absolute, *absolute.parents):
        try:
            attributes = getattr(part.lstat(), "st_file_attributes", 0)
        except FileNotFoundError:
            attributes = 0
        if part.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise DistributionError(f"linked path is not permitted: {part}")
    return absolute


def read_tree(folder):
    folder = plain_path(folder)
    if not folder.is_dir():
        raise DistributionError(f"missing directory: {folder}")
    result = {}
    for file in sorted(folder.rglob("*")):
        plain_path(file)
        if file.is_file():
            result[file.relative_to(folder).as_posix()] = file.read_bytes()
        elif not file.is_dir():
            raise DistributionError(f"unsupported source entry: {file}")
    return result


def skill_frontmatter(data, name):
    """Read this project's flat fields and string metadata map, not general YAML.

    Only the initial fenced frontmatter is searched. Quoted/unquoted single-line
    string values are supported; multiline YAML is outside this builder's scope.
    """
    body = data.decode("utf-8") if isinstance(data, bytes) else data
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", body, re.DOTALL)
    if not match:
        raise DistributionError(f"missing or unterminated frontmatter: {name}")
    fields, metadata = {}, {}
    in_metadata = False
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parsed = re.fullmatch(r"([ \t]*)([a-zA-Z_][a-zA-Z_0-9-]*):[ \t]*(.*)", line)
        if not parsed:
            raise DistributionError(f"unsupported frontmatter syntax: {name}: {line}")
        indentation, key, raw = parsed.groups()
        if not indentation:
            in_metadata = key == "metadata"
            if in_metadata:
                if raw:
                    raise DistributionError(f"metadata must be an indented string map: {name}")
                continue
            values = fields
        else:
            if not in_metadata or indentation != "  ":
                raise DistributionError(f"unsupported frontmatter indentation: {name}")
            values = metadata
        if key in values:
            raise DistributionError(f"duplicate frontmatter field: {name}: {key}")
        value = raw.strip()
        if value.startswith(('"', "'")):
            if len(value) < 2 or value[-1] != value[0]:
                raise DistributionError(f"invalid quoted frontmatter value: {name}: {key}")
            value = value[1:-1]
        elif value in ("|", ">"):
            raise DistributionError(f"multiline frontmatter is unsupported: {name}: {key}")
        values[key] = value
    if fields.get("name") != name:
        raise DistributionError(f"skill name mismatch: {name}")
    if not fields.get("description"):
        raise DistributionError(f"missing description: {name}")
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", metadata.get("version", "")):
        raise DistributionError(f"metadata.version must be a release semantic version: {name}")
    return fields, metadata


def portable_files(root=ROOT):
    root = plain_path(root)
    files = {}
    skill_metadata = {}
    for name in SKILLS:
        tree = read_tree(root / "skills" / name)
        if "SKILL.md" not in tree:
            raise DistributionError(f"missing SKILL.md: {name}")
        if any(key.startswith("agents/") or ".codex-plugin" in key for key in tree):
            raise DistributionError(f"Codex metadata found in portable skill: {name}")
        _, skill_metadata[name] = skill_frontmatter(tree["SKILL.md"], name)
        files.update({f"{name}/{key}": data for key, data in tree.items()})
    canonical = skill_metadata["ai-slop-thresher"]
    alias = skill_metadata["thresh"]
    if alias["version"] != canonical["version"]:
        raise DistributionError("canonical and alias metadata.version must match")
    if "canonical_skill" in alias and alias["canonical_skill"] != "ai-slop-thresher":
        raise DistributionError("alias canonical_skill must be ai-slop-thresher")
    for name in LEGAL:
        files[name] = plain_path(root / name).read_bytes()
    validate_links(files)
    return files


def validate_links(files):
    """Check local Markdown file references against an in-memory package root."""
    import posixpath

    for name, data in files.items():
        if not name.endswith(".md"):
            continue
        body = data.decode("utf-8")
        if "[TODO:" in body:
            raise DistributionError(f"unfinished reference: {name}")
        for raw in re.findall(r"\]\(([^)]+)\)", body):
            link = raw.strip().strip("<>")
            parsed = urlsplit(link)
            if parsed.scheme or not parsed.path:
                continue
            relative = unquote(parsed.path)
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), relative))
            if relative.startswith(("/", "\\")) or "\\" in relative or target.startswith("../"):
                raise DistributionError(f"reference escapes package: {name}: {raw}")
            if target not in files:
                raise DistributionError(f"unresolved reference: {name}: {raw}")


def version(root=ROOT):
    data = plain_path(Path(root) / "skills/ai-slop-thresher/SKILL.md").read_bytes()
    _, metadata = skill_frontmatter(data, "ai-slop-thresher")
    return metadata["version"]


def with_frontmatter(data, extra, name):
    """Append host-only frontmatter fields (flat string values) before the closing fence."""
    body = data.decode("utf-8")
    match = re.match(r"\A---(\r?\n)(.*?)\r?\n---", body, re.DOTALL)
    if not match:
        raise DistributionError(f"missing or unterminated frontmatter: {name}")
    lines = []
    for key, value in extra.items():
        if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9-]*", key) or not isinstance(value, str) or "\n" in value:
            raise DistributionError(f"invalid host frontmatter field: {name}: {key}")
        if re.search(rf"(?m)^{re.escape(key)}:", match.group(2)):
            raise DistributionError(f"host frontmatter field already in source: {name}: {key}")
        lines.append(f"{key}: {value}")
    newline = match.group(1)
    insert = match.end(2)
    return (body[:insert] + "".join(newline + line for line in lines) + body[insert:]).encode("utf-8")


def claude_files(root=ROOT):
    """Claude Code manifest and per-skill frontmatter, kept apart from the portable skills."""
    folder = Path(root) / CLAUDE_DIR
    manifest_path = plain_path(folder / "plugin.json")
    if not manifest_path.is_file():
        return {}, {}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("name") != "ai-slop-thresher":
        raise DistributionError("Claude Code manifest must identify ai-slop-thresher")
    overlay_path = plain_path(folder / "frontmatter.json")
    overlay = json.loads(overlay_path.read_text(encoding="utf-8")) if overlay_path.is_file() else {}
    if set(overlay) - set(SKILLS):
        raise DistributionError("Claude Code frontmatter names an unknown skill")
    return {".claude-plugin/plugin.json": manifest_path.read_bytes()}, overlay


def plugin_files(root=ROOT, claude=True):
    """Files of plugins/ai-slop-thresher. claude=False gives the Codex-only store package."""
    portable = portable_files(root)
    files = {key if key in LEGAL else f"skills/{key}": data for key, data in portable.items()}
    for name in SKILLS:
        metadata = Path(root) / "integrations/codex/agents" / name / "openai.yaml"
        files[f"skills/{name}/agents/openai.yaml"] = plain_path(metadata).read_bytes()
    manifest = {
        "name": "ai-slop-thresher", "version": version(root),
        "description": "한국어 AI 문체 윤문과 의미 보존 검토를 위한 스킬 모음",
        "author": {"name": "Burntgogi"},
        "homepage": "https://github.com/Burntgogi/ai-slop-thresher",
        "repository": "https://github.com/Burntgogi/ai-slop-thresher",
        "license": "Apache-2.0", "skills": "./skills/",
        "interface": {"displayName": "AI Slop 탈곡기", "shortDescription": "뜻을 보존하며 AI 문체를 다듬는 한국어 윤문 스킬"},
    }
    manifest_source = plain_path(Path(root) / "integrations/codex/plugin.json")
    if manifest_source.is_file():
        manifest = json.loads(manifest_source.read_text(encoding="utf-8"))
        if manifest.get("name") != "ai-slop-thresher" or manifest.get("skills") != "./skills/":
            raise DistributionError("Codex manifest must identify ai-slop-thresher and its packaged skills")
        if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", manifest.get("version", "")):
            raise DistributionError("Codex manifest version must be a release semantic version")
        interface = manifest.get("interface", {})
        assets = [interface[field] for field in ("logo", "composerIcon", "logoDark", "composerIconDark") if field in interface]
        assets.extend(interface.get("screenshots", []))
        for relative in assets:
            if not isinstance(relative, str) or not relative.startswith("./assets/") or ".." in relative.split("/") or "\\" in relative:
                raise DistributionError(f"invalid packaged asset path: {relative}")
            name = relative[2:]
            files[name] = plain_path(Path(root) / name).read_bytes()
    files[".codex-plugin/plugin.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if claude:
        manifests, overlay = claude_files(root)
        files.update(manifests)
        for name, extra in overlay.items():
            files[f"skills/{name}/SKILL.md"] = with_frontmatter(files[f"skills/{name}/SKILL.md"], extra, name)
    validate_links(files)
    return files


def write_files(folder, files):
    for name, data in files.items():
        file = folder / name
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open("xb") as stream:
            stream.write(data)


def build_plugin(root=ROOT, output=None, apply=False):
    files = plugin_files(root)
    output = plain_path(output or Path(root) / PLUGIN_DIR)
    # An interrupted/failed restoration is never adopted or deleted on retry.
    # These random sibling names do not identify a particular output, so block
    # conservatively until the user restores or relocates the preserved backup.
    pending = sorted(output.parent.glob(".thresher-old-*"))
    if pending:
        raise DistributionError(f"unresolved plugin backup at {plain_path(pending[0])}; restore or relocate it before retrying build")
    expected = {name: digest(data) for name, data in files.items()}
    if output.exists():
        current = read_tree(output)
        try:
            prior = json.loads(current.pop(RECEIPT).decode("utf-8"))
        except (KeyError, ValueError, UnicodeDecodeError) as error:
            raise DistributionError(f"refusing unmanaged output: {output}") from error
        if prior != {name: digest(data) for name, data in current.items()}:
            raise DistributionError(f"refusing edited generated output: {output}")
    if apply:
        output.parent.mkdir(parents=True, exist_ok=True)
        plain_path(output.parent)
        staging = Path(tempfile.mkdtemp(prefix=".thresher-build-", dir=output.parent))
        backup = None
        replacement_complete = False
        try:
            write_files(staging, files)
            (staging / RECEIPT).write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
            # Reserve a random empty sibling rather than a predictable backup path.
            if output.exists():
                backup = Path(tempfile.mkdtemp(prefix=".thresher-old-", dir=output.parent))
                backup.rmdir()
                output.rename(backup)
            staging.rename(output)
            replacement_complete = True
        except Exception as build_error:
            if backup is not None and backup.exists():
                if output.exists():
                    raise DistributionError(f"build failed ({build_error}); original plugin preserved at {backup}; output already exists, resolve backup before retrying") from build_error
                try:
                    backup.rename(output)
                except Exception as restore_error:
                    raise DistributionError(f"build failed ({build_error}); backup restoration failed ({restore_error}); original plugin preserved at {backup}; restore it before retrying build") from restore_error
            raise
        finally:
            active_error = sys.exc_info()[1]
            # The old tree can be deleted only after a replacement succeeded.
            # If restoration succeeded, rename already moved it back to output.
            cleanup = [staging]
            if replacement_complete:
                cleanup.append(backup)
            for owned in cleanup:
                if owned is not None and owned.exists():
                    plain_path(owned)
                    if owned.parent != output.parent:
                        raise DistributionError("cleanup path escaped output parent")
                    try:
                        shutil.rmtree(owned)
                    except Exception as cleanup_error:
                        if active_error is None:
                            raise DistributionError(f"cleanup failed for preserved path {owned}: {cleanup_error}") from cleanup_error
                        # Keep the original recovery error (and backup path)
                        # visible even when temporary-tree cleanup also fails.
                        if hasattr(active_error, "add_note"):
                            active_error.add_note(f"temporary cleanup failed for {owned}: {cleanup_error}")
    return {"operation": "build", "dry_run": not apply, "output": str(output), "files": len(files), "version": json.loads(files[".codex-plugin/plugin.json"])["version"], "skill_version": version(root)}


def check_plugin(root=ROOT, output=None):
    expected = plugin_files(root)
    actual = read_tree(output or Path(root) / PLUGIN_DIR)
    receipt = actual.pop(RECEIPT, None)
    if actual != expected or receipt is None:
        raise DistributionError("Codex projection is stale; run build --apply")
    if json.loads(receipt) != {name: digest(data) for name, data in expected.items()}:
        raise DistributionError("invalid build receipt")
    marketplace_path = plain_path(Path(root) / ".agents/plugins/marketplace.json")
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    entries = marketplace.get("plugins", [])
    if len(entries) != 1 or entries[0].get("source") != {"source": "local", "path": "./" + PLUGIN_DIR}:
        raise DistributionError("marketplace must point to the repo plugin projection")
    if not plain_path(Path(root) / entries[0]["source"]["path"]).is_dir():
        raise DistributionError("marketplace plugin directory is missing")
    claude_market = plain_path(Path(root) / ".claude-plugin/marketplace.json")
    if claude_market.is_file():
        claude_entries = json.loads(claude_market.read_text(encoding="utf-8")).get("plugins", [])
        if len(claude_entries) != 1 or claude_entries[0].get("source") != "./" + PLUGIN_DIR:
            raise DistributionError("Claude Code marketplace must point to the repo plugin projection")
    return {"operation": "check", "files": len(expected), "projection_matches_source": True, "local_references_resolve": True, "marketplace_path_resolves": True}


def install_skills(target, scope="user", project=None, destination=None, home=None, root=ROOT, apply=False):
    files = portable_files(root)
    if target == "generic" and destination is None:
        raise DistributionError("generic target requires --destination")
    if destination is not None and (project is not None or scope != "user"):
        raise DistributionError("--destination cannot be combined with --project or --scope project")
    if scope == "project" and project is None:
        raise DistributionError("project scope requires --project")
    if scope == "user" and project is not None:
        raise DistributionError("--project requires --scope project")
    if destination is None:
        base = Path(project) if scope == "project" else Path(home or Path.home())
        destination = base / TARGETS[target][scope]
    destination = plain_path(destination)
    if destination.exists() and not destination.is_dir():
        raise DistributionError(f"destination must be a directory: {destination}")
    for name in SKILLS:
        path = plain_path(destination / name)
        if path.exists():
            raise DistributionError(f"existing skill will not be overwritten: {path}")
    # Keep notices with each installed skill; a shared skills root may already
    # contain unrelated license files. The alias keeps its sibling reference.
    install_files = {name: data for name, data in files.items() if name not in LEGAL}
    if target == "codex":
        for skill in SKILLS:
            metadata = Path(root) / "integrations/codex/agents" / skill / "openai.yaml"
            install_files[f"{skill}/agents/openai.yaml"] = plain_path(metadata).read_bytes()
    for skill in SKILLS:
        for name in LEGAL:
            install_files[f"{skill}/{name}"] = files[name]
    validate_links(install_files)
    if apply:
        destination.mkdir(parents=True, exist_ok=True)
        plain_path(destination)
        created = []
        try:
            for name in SKILLS:
                plain_path(destination / name)
                (destination / name).mkdir()  # Exclusive creation, no overwrite.
                created.append(destination / name)
                subset = {key[len(name) + 1:]: data for key, data in install_files.items() if key.startswith(name + "/")}
                write_files(destination / name, subset)
        except Exception:
            for path in created:
                plain_path(path)
                if path.parent != destination or path.name not in SKILLS:
                    raise DistributionError("rollback path escaped destination")
                shutil.rmtree(path)
            raise
    return {"operation": "install", "target": target, "scope": scope, "dry_run": not apply, "destination": str(destination), "skills": list(SKILLS), "files": len(install_files), "settings_modified": False}


def archive_bytes(files):
    import io

    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    result = stream.getvalue()
    with zipfile.ZipFile(io.BytesIO(result)) as archive:
        if archive.testzip() is not None or {name: archive.read(name) for name in archive.namelist()} != files:
            raise DistributionError("archive does not match source bytes")
    return result


def package(root=ROOT, output=None, apply=False):
    if apply and output is None:
        raise DistributionError("package --apply requires an explicit new --output directory")
    portable = portable_files(root)
    plugin = plugin_files(root, claude=False)
    output = plain_path(output or Path(root) / "dist")
    archives = {"ai-slop-thresher-portable.zip": archive_bytes(portable), "ai-slop-thresher-codex-plugin.zip": archive_bytes(plugin)}
    # Existing portable download name remains available, with identical bytes.
    archives["ai-slop-thresher.zip"] = archives["ai-slop-thresher-portable.zip"]
    if apply:
        if output.exists():
            raise DistributionError(f"refusing existing archive output: {output}")
        output.mkdir(parents=True)
        plain_path(output)
        for name, data in archives.items():
            file = plain_path(output / name)
            with file.open("xb") as stream:
                stream.write(data)
    return {"operation": "package", "dry_run": not apply, "output": str(output), "portable_files": len(portable), "plugin_files": len(plugin), "packages": [{"file": name, "bytes": len(data), "sha256": digest(data)} for name, data in archives.items()]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("build", "check", "package"):
        option = sub.add_parser(command)
        option.add_argument("--output", type=Path)
        if command != "check":
            mutation = option.add_mutually_exclusive_group()
            mutation.add_argument("--apply", action="store_true")
            mutation.add_argument("--dry-run", action="store_true", help="default; write no files")
    option = sub.add_parser("install")
    option.add_argument("--target", choices=[*TARGETS, "generic"], required=True)
    option.add_argument("--scope", choices=("user", "project"), default="user")
    option.add_argument("--project", type=Path)
    option.add_argument("--destination", type=Path)
    mutation = option.add_mutually_exclusive_group()
    mutation.add_argument("--apply", action="store_true")
    mutation.add_argument("--dry-run", action="store_true", help="default; write no files")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            result = build_plugin(output=args.output, apply=args.apply)
        elif args.command == "check":
            result = check_plugin(output=args.output)
        elif args.command == "package":
            result = package(output=args.output, apply=args.apply)
        else:
            result = install_skills(args.target, args.scope, args.project, args.destination, apply=args.apply)
    except (DistributionError, OSError) as error:
        parser.exit(1, f"error: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
