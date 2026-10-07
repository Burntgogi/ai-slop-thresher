"""Release helpers: preflight checks, release body, and verification of a published release.

Python 3.10+, standard library only. Nothing here pushes, tags or publishes; see docs/releasing.md.

  python -B scripts/release.py preflight v1.2.3
  python -B scripts/release.py body v1.2.3 --output ../release-candidates/v1.2.3/release-body.md
  python -B scripts/release.py verify-published v1.2.3 --artifacts ../release-candidates/v1.2.3
"""

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "Burntgogi/ai-slop-thresher"
NOREPLY = "@users.noreply.github.com"
ASSETS = ("ai-slop-thresher-portable.zip", "ai-slop-thresher-codex-plugin.zip", "ai-slop-thresher.zip",
          "ai-slop-thresher-workbench.zip", "SHA256SUMS")
PREVIEWS = {"README.md": "index.html", "README.en.md": "index.en.html", "RELEASE_NOTES.md": "release-notes.html"}

spec = importlib.util.spec_from_file_location("distribution", ROOT / "scripts/distribute.py")
distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(distribution)


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, encoding="utf-8").stdout


def number(tag):
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise SystemExit(f"tag must look like v1.2.3: {tag}")
    return tag[1:]


def preflight(tag):
    version, problems = number(tag), []
    if distribution.version(ROOT) != version:
        problems.append(f"skills metadata.version is {distribution.version(ROOT)}, not {version}")
    for manifest in ("integrations/codex/plugin.json", "integrations/claude-code/plugin.json"):
        found = json.loads((ROOT / manifest).read_text(encoding="utf-8")).get("version")
        if found != version:
            problems.append(f"{manifest} version is {found}")
    if git("status", "--porcelain").strip():
        problems.append("working tree has uncommitted changes")
    # GitHub rejects pushes that would publish a private address (GH007).
    emails = set(git("log", "origin/main..HEAD", "--format=%ae%n%ce").split())
    private = sorted(e for e in emails if not e.endswith(NOREPLY))
    if private:
        problems.append(f"unpushed commits use non-noreply emails {private}; set git config user.email and rewrite them")
    if f"## {version}" not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
        problems.append(f"CHANGELOG.md has no '## {version}' entry")
    if not (ROOT / f"docs/releases/{tag}.md").is_file():
        problems.append(f"docs/releases/{tag}.md is missing")
    if tag not in (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8").splitlines()[0]:
        problems.append("RELEASE_NOTES.md title does not name the tag")
    for readme in ("README.md", "README.en.md"):
        if f"releases/tag/{tag}" not in (ROOT / readme).read_text(encoding="utf-8"):
            problems.append(f"{readme} badges do not point to {tag}")
    for source, preview in PREVIEWS.items():
        html = (ROOT / "docs/preview" / preview).read_text(encoding="utf-8")
        if hashlib.sha256((ROOT / source).read_bytes()).hexdigest() not in html:
            problems.append(f"docs/preview/{preview} is stale; run node evaluation/build_frontpage.cjs")
    try:
        distribution.check_plugin(ROOT)
    except distribution.DistributionError as error:
        problems.append(f"plugin projection: {error}")
    if git("ls-remote", "--tags", "origin", f"refs/tags/{tag}").strip():
        problems.append(f"{tag} already exists on origin")
    return {"tag": tag, "ok": not problems, "problems": problems}


def body(tag):
    """RELEASE_NOTES.md with relative links pinned to the tag, as on earlier releases."""
    number(tag)
    base = f"https://github.com/{REPOSITORY}/blob/{tag}/"
    text = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
    return re.sub(r"\]\((?![a-z][a-z0-9+.-]*:|#)([^)]+)\)", lambda m: f"]({base}{m.group(1)})", text)


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "ai-slop-thresher-release-check"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def verify_published(tag, artifacts):
    artifacts = Path(artifacts)
    expected = dict(reversed(line.split(None, 1)) for line in (artifacts / "SHA256SUMS").read_text(encoding="utf-8").splitlines() if line.strip())
    release = json.loads(fetch(f"https://api.github.com/repos/{REPOSITORY}/releases/tags/{tag}"))
    problems = []
    if release.get("draft") or release.get("prerelease"):
        problems.append("release is a draft or prerelease")
    names = {asset["name"] for asset in release.get("assets", [])}
    if names != set(ASSETS):
        problems.append(f"asset set differs: missing {sorted(set(ASSETS) - names)}, extra {sorted(names - set(ASSETS))}")
    for asset in release.get("assets", []):
        data = fetch(asset["browser_download_url"])
        if asset["name"] == "SHA256SUMS":
            if data != (artifacts / "SHA256SUMS").read_bytes():
                problems.append("published SHA256SUMS differs from the local candidate")
        elif hashlib.sha256(data).hexdigest() != expected.get(asset["name"]):
            problems.append(f"{asset['name']} checksum differs")
    if (release.get("body") or "").replace("\r\n", "\n").strip() != body(tag).strip():
        problems.append("release body differs from RELEASE_NOTES.md at this checkout")
    return {"tag": tag, "url": release.get("html_url"), "ok": not problems, "problems": problems}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "body", "verify-published"):
        option = sub.add_parser(name)
        option.add_argument("tag")
        if name == "body":
            option.add_argument("--output", type=Path)
        if name == "verify-published":
            option.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "body":
        text = body(args.tag)
        if args.output:
            args.output.write_text(text, encoding="utf-8", newline="\n")
        else:
            sys.stdout.write(text)
        return
    result = preflight(args.tag) if args.command == "preflight" else verify_published(args.tag, args.artifacts)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
