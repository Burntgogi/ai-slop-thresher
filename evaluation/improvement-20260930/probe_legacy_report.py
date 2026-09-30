"""Probe the legacy generator on a temporary copy, without changing history."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def probe():
    with tempfile.TemporaryDirectory() as temp:
        copy = Path(temp)
        for name in ("skills", "evaluation", "research", "reports"):
            shutil.copytree(ROOT / name, copy / name, ignore=shutil.ignore_patterns("__pycache__"))
        history = copy / "reports/ai-slop-thresher-report.md"
        before = hashlib.sha256(history.read_bytes()).hexdigest()
        result = subprocess.run([sys.executable, "evaluation/build_report.py"], cwd=copy, capture_output=True, text=True, encoding="utf-8")
        return {"exit_code": result.returncode,
                "history_changed": before != hashlib.sha256(history.read_bytes()).hexdigest(),
                "manifest_version": json.loads((copy / "research/artifact-manifest.json").read_text(encoding="utf-8"))["version"],
                "stderr": result.stderr.strip(),
                "scope": "temporary copy only; live history untouched"}


if __name__ == "__main__":
    output = Path(sys.argv[1])
    output.write_text(json.dumps(probe(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
