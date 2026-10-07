"""Read-only verification, isolated builds and corruption controls."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
import test_distribution as fixtures

ROOT = Path(__file__).resolve().parents[1]

def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

builder = load("candidate_artifacts", "evaluation/package_artifacts.py")
verifier = load("read_only_release", "scripts/verify_release.py")

def snapshot(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts and ".git" not in p.parts}

class ReleaseArtifactsTests(unittest.TestCase):
    setUp = fixtures.DistributionTests.setUp
    tearDown = fixtures.DistributionTests.tearDown

    def inventory(self):
        research = self.source / "research"
        research.mkdir(exist_ok=True)
        names = sorted(p.relative_to(self.source).as_posix() for p in self.source.rglob("*") if p.is_file())
        (research / "build-inputs.json").write_text(json.dumps({"files": names}), encoding="utf-8")

    def test_plan_build_and_verification_preserve_source(self):
        self.inventory()
        before = snapshot(self.source)
        output = self.base / "candidate"
        self.assertTrue(builder.build_artifacts(self.source, output)["dry_run"])
        self.assertFalse(output.exists())
        builder.build_artifacts(self.source, output, apply=True)
        self.assertEqual(snapshot(self.source), before)
        produced = snapshot(output)
        self.assertTrue(verifier.verify_release(output, self.source)["verified"])
        self.assertEqual(snapshot(output), produced)

    def test_codex_zip_omits_claude_settings_and_still_verifies(self):
        claude = self.source / "integrations/claude-code"
        claude.mkdir(parents=True)
        (claude / "plugin.json").write_text(json.dumps({"name": "ai-slop-thresher", "version": "1.2.0"}), encoding="utf-8")
        (claude / "frontmatter.json").write_text(json.dumps({"thresh": {"disable-model-invocation": "true"}}), encoding="utf-8")
        self.inventory()
        output = self.base / "candidate"
        builder.build_artifacts(self.source, output, apply=True)
        with zipfile.ZipFile(output / "ai-slop-thresher-codex-plugin.zip") as archive:
            self.assertFalse(any(name.startswith(".claude-plugin/") for name in archive.namelist()))
            self.assertNotIn(b"disable-model-invocation", archive.read("skills/thresh/SKILL.md"))
        self.assertTrue(verifier.verify_release(output, self.source)["verified"])

    def test_existing_source_or_missing_output_cannot_write(self):
        self.inventory()
        existing = self.base / "published"
        existing.mkdir()
        (existing / "SHA256SUMS").write_text("KEEP", encoding="utf-8")
        before = snapshot(self.base)
        for output in (existing, self.source / "dist", None):
            with self.assertRaises(ValueError):
                builder.build_artifacts(self.source, output, apply=True)
        self.assertEqual(snapshot(self.base), before)

    def test_corrupted_zip_is_rejected(self):
        self.inventory()
        output = self.base / "candidate"
        builder.build_artifacts(self.source, output, apply=True)
        archive = output / "ai-slop-thresher-portable.zip"
        archive.write_bytes(archive.read_bytes()+b"corruption")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            verifier.verify_release(output)

    def test_old_integrity_and_current_source_are_separate(self):
        self.inventory()
        output = self.base / "candidate"
        builder.build_artifacts(self.source, output, apply=True)
        (self.source / "skills/ai-slop-thresher/references/fixture.md").write_text("NEW SOURCE", encoding="utf-8")
        self.assertTrue(verifier.verify_release(output)["verified"])
        with self.assertRaisesRegex(ValueError, "selected source"):
            verifier.verify_release(output, self.source)

    def test_traversal_checksum_is_rejected(self):
        output = self.base / "bad"
        output.mkdir()
        (output / "SHA256SUMS").write_text("0"*64+"  ../outside.zip\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid"):
            verifier.verify_release(output)

    def test_unlisted_draft_requires_explicit_include(self):
        self.inventory()
        draft = self.source / "reports/draft.md"
        draft.parent.mkdir()
        draft.write_text("DRAFT", encoding="utf-8")
        output = self.base / "candidate"
        builder.build_artifacts(self.source, output, apply=True)
        with zipfile.ZipFile(output / "ai-slop-thresher-workbench.zip") as archive:
            self.assertNotIn("reports/draft.md", archive.namelist())
        included = builder.build_artifacts(self.source, self.base / "explicit", apply=True, include=["reports/draft.md"])
        self.assertIn("reports/draft.md", included["source_sha256"])

    def test_fixture_and_ab_rechecks_preserve_recorded_files(self):
        folders = (ROOT,)
        before = [snapshot(folder) for folder in folders]
        for script in ("evaluation/run_checks.py", "evaluation/ab-20260930/aggregate.py"):
            result = subprocess.run([sys.executable, "-B", script], cwd=ROOT, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        self.assertEqual([snapshot(folder) for folder in folders], before)

if __name__ == "__main__":
    unittest.main()
