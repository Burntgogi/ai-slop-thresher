"""Protect historical reports from current-candidate relabeling."""
import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HistoryTests(unittest.TestCase):
    def test_current_candidate_does_not_overwrite_history(self):
        names = ("reports/ai-slop-thresher-report.md", "reports/comparisons.md", "research/artifact-manifest.json")
        before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}
        result = subprocess.run([sys.executable, "evaluation/build_report.py"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no files written", result.stderr)
        self.assertEqual(before, {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names})


if __name__ == "__main__":
    unittest.main()
