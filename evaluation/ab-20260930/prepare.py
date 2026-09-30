"""Download actual published release assets and freeze the paired experiment."""
import hashlib
import io
import json
import random
import subprocess
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = "Burntgogi/ai-slop-thresher"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Codex-release-AB", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def prepare():
    manifest_path = HERE / "experiment-manifest.json"
    if manifest_path.exists():
        raise RuntimeError("Experiment already frozen; refusing to overwrite")
    cases = []
    for file, suite in [(ROOT / "evaluation/improvement-20260930/inputs.json", "development"),
                        (ROOT / "evaluation/improvement-20260930/boundary-inputs.json", "development"),
                        (HERE / "new-inputs.json", "new")]:
        for item in json.loads(file.read_text(encoding="utf-8")):
            cases.append({**item, "suite": suite})
    if len(cases) != 28 or len({c["id"] for c in cases}) != 28:
        raise RuntimeError("Case count/identity mismatch")
    write_json(HERE / "inputs.json", cases)
    seed = random.SystemRandom().getrandbits(64)
    rng = random.Random(seed)
    versions = ["v1.1.0", "v1.2.0"]
    rng.shuffle(versions)
    arms = {}
    for label, tag in zip(("q", "r"), versions):
        release = json.loads(get("https://api.github.com/repos/" + REPO + "/releases/tags/" + tag))
        if release["draft"] or release["prerelease"]:
            raise RuntimeError("Expected published full release")
        wanted = "ai-slop-thresher.zip" if tag == "v1.1.0" else "ai-slop-thresher-portable.zip"
        asset = next(a for a in release["assets"] if a["name"] == wanted)
        blob = get(asset["browser_download_url"])
        if asset.get("digest") != "sha256:" + sha(blob) or len(blob) != asset["size"]:
            raise RuntimeError("Published release asset digest differs")
        folder = HERE / "artifacts" / tag
        folder.mkdir(parents=True, exist_ok=True)
        (folder / wanted).write_bytes(blob)
        members = {}
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            if archive.testzip() is not None:
                raise RuntimeError("Corrupt release ZIP")
            for name in archive.namelist():
                members[name] = {"bytes": len(archive.read(name)), "sha256": sha(archive.read(name))}
            for name in ("ai-slop-thresher/SKILL.md", "ai-slop-thresher/references/edge-cases.md"):
                data = archive.read(name)
                destination = HERE / "arms" / label / Path(name).name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
        commit = subprocess.check_output(["git", "rev-parse", tag + "^{commit}"], cwd=ROOT, text=True).strip()
        arms[label] = {"tag": tag, "commit": commit, "release_url": release["html_url"], "published_at": release["published_at"],
                       "asset_name": wanted, "asset_url": asset["browser_download_url"], "asset_sha256": sha(blob), "asset_bytes": len(blob), "members": members}
    orders = {}
    for repetition in (1, 2):
        order = cases.copy()
        rng.shuffle(order)
        write_json(HERE / f"generation-inputs-{repetition}.json", [{k: c[k] for k in ("id", "request", "source")} for c in order])
        orders[str(repetition)] = [c["id"] for c in order]
    frozen = {name: sha((HERE / name).read_bytes()) for name in ("protocol.md", "new-inputs.json", "inputs.json", "generation-inputs-1.json", "generation-inputs-2.json")}
    manifest = {"prepared_at_utc": datetime.now(timezone.utc).isoformat(), "case_count": 28, "development_cases": 18, "new_cases": 10,
                "repetitions": 2, "assignment_seed": seed, "arms": arms, "input_orders": orders, "pre_generation_sha256": frozen,
                "model": "inherited Codex model; exact identifier unavailable to agents", "temperature": "not controlled/exposed", "model_seed": "not controlled/exposed"}
    write_json(manifest_path, manifest)
    print(json.dumps({"cases": 28, "repetitions": 2, "arms": {k: {x: v[x] for x in ("tag", "commit", "asset_sha256")} for k, v in arms.items()}, "manifest_sha256": sha(manifest_path.read_bytes())}, indent=2))


if __name__ == "__main__":
    prepare()
