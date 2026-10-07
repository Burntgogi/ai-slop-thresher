"""Distribution safety and harness separation; no live user installation."""

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("distribution", ROOT / "scripts/distribute.py")
distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(distribution)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        for name in distribution.SKILLS:
            folder = self.source / "skills" / name
            folder.mkdir(parents=True)
            body = f"---\nname: {name}\ndescription: Test skill\nmetadata:\n  version: \"1.2.0\"\n---\n\n"
            if name == "thresh":
                body += "[canonical](../ai-slop-thresher/SKILL.md)\n"
            else:
                (folder / "references").mkdir()
                (folder / "references/fixture.md").write_text("Fixture\n", encoding="utf-8")
                body += "[reference](references/fixture.md)\n"
            (folder / "SKILL.md").write_text(body, encoding="utf-8")
            metadata = self.source / "integrations/codex/agents" / name
            metadata.mkdir(parents=True)
            (metadata / "openai.yaml").write_text("interface:\n  display_name: Test\n", encoding="utf-8")
        for name in distribution.LEGAL:
            (self.source / name).write_text("Legal notice\n", encoding="utf-8")
        market = self.source / ".agents/plugins"
        market.mkdir(parents=True)
        (market / "marketplace.json").write_text(json.dumps({"plugins": [{"source": {"source": "local", "path": "./plugins/codex/ai-slop-thresher"}}]}), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def install(self, **kwargs):
        return distribution.install_skills(root=self.source, home=self.base / "home", **kwargs)

    def test_all_harness_user_paths_dry_run(self):
        for target, config in distribution.TARGETS.items():
            result = self.install(target=target)
            self.assertTrue(result["dry_run"])
            self.assertEqual(Path(result["destination"]), self.base / "home" / config["user"])
        self.assertFalse((self.base / "home").exists())

    def test_all_harness_project_installations(self):
        for target, config in distribution.TARGETS.items():
            project = self.base / target
            result = self.install(target=target, scope="project", project=project, apply=True)
            destination = project / config["project"]
            self.assertFalse(result["settings_modified"])
            self.assertTrue((destination / "thresh/SKILL.md").is_file())
            self.assertTrue((destination / "ai-slop-thresher/references/fixture.md").is_file())
            self.assertTrue((destination / "thresh/NOTICE").is_file())
            self.assertEqual((destination / "ai-slop-thresher/SKILL.md").read_bytes(), (self.source / "skills/ai-slop-thresher/SKILL.md").read_bytes())
            self.assertEqual((destination / "thresh/NOTICE").read_bytes(), (self.source / "NOTICE").read_bytes())
            self.assertEqual((destination / "ai-slop-thresher/agents/openai.yaml").exists(), target == "codex")
            self.assertEqual((destination / "thresh/agents/openai.yaml").exists(), target == "codex")

    def test_generic_destination_and_alias_sibling(self):
        destination = self.base / "explicit"
        self.install(target="generic", destination=destination, apply=True)
        self.assertTrue((destination / "thresh/../ai-slop-thresher/SKILL.md").is_file())

    def test_generic_requires_destination(self):
        with self.assertRaises(distribution.DistributionError):
            self.install(target="generic")

    def test_scope_arguments_cannot_silently_conflict(self):
        for kwargs in ({"scope": "project"}, {"project": self.base}, {"destination": self.base, "scope": "project", "project": self.base}):
            with self.subTest(kwargs=kwargs), self.assertRaises(distribution.DistributionError):
                self.install(target="codex", **kwargs)

    def test_existing_skill_prevents_both_installs(self):
        destination = self.base / "existing"
        existing = destination / "thresh"
        existing.mkdir(parents=True)
        original = existing / "SKILL.md"
        original.write_text("USER EDIT", encoding="utf-8")
        with self.assertRaises(distribution.DistributionError):
            self.install(target="generic", destination=destination, apply=True)
        self.assertEqual(original.read_text(encoding="utf-8"), "USER EDIT")
        self.assertFalse((destination / "ai-slop-thresher").exists())

    def make_link(self, link, target, directory=True):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError:
            self.skipTest("symlink creation unavailable on this host")

    def test_linked_destination_ancestor_is_rejected(self):
        real = self.base / "real"
        real.mkdir()
        link = self.base / "link"
        self.make_link(link, real)
        with self.assertRaises(distribution.DistributionError):
            self.install(target="generic", destination=link / "skills", apply=True)
        self.assertEqual(list(real.iterdir()), [])

    def test_dangling_skill_link_is_rejected(self):
        destination = self.base / "dangling"
        destination.mkdir()
        self.make_link(destination / "thresh", self.base / "missing")
        with self.assertRaises(distribution.DistributionError):
            self.install(target="generic", destination=destination, apply=True)
        self.assertFalse((destination / "ai-slop-thresher").exists())

    def test_source_symlink_rejected(self):
        file = self.source / "skills/ai-slop-thresher/references/fixture.md"
        file.unlink()
        target = self.base / "external.md"
        target.write_text("External", encoding="utf-8")
        self.make_link(file, target, directory=False)
        with self.assertRaises(distribution.DistributionError):
            distribution.portable_files(self.source)

    def test_windows_junction_destination_rejected(self):
        if sys.platform != "win32" or not hasattr(Path, "is_junction"):
            self.skipTest("Windows junction test requires Windows Python 3.12+")
        real = self.base / "junction-target"
        real.mkdir()
        link = self.base / "junction"
        command = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(real)], capture_output=True, text=True)
        if command.returncode:
            self.skipTest("junction creation unavailable")
        try:
            with self.assertRaises(distribution.DistributionError):
                self.install(target="generic", destination=link / "skills", apply=True)
            self.assertEqual(list(real.iterdir()), [])
        finally:
            link.rmdir()

    def test_portable_rejects_codex_metadata(self):
        metadata = self.source / "skills/thresh/agents"
        metadata.mkdir()
        (metadata / "openai.yaml").write_text("unexpected", encoding="utf-8")
        with self.assertRaises(distribution.DistributionError):
            distribution.portable_files(self.source)

    def test_local_reference_must_be_present(self):
        (self.source / "skills/ai-slop-thresher/references/fixture.md").unlink()
        with self.assertRaises(distribution.DistributionError):
            distribution.portable_files(self.source)

    def test_local_reference_cannot_escape_package(self):
        file = self.source / "skills/thresh/SKILL.md"
        file.write_text(file.read_text(encoding="utf-8") + "[private](../../secrets.md)\n", encoding="utf-8")
        with self.assertRaises(distribution.DistributionError):
            distribution.portable_files(self.source)

    def test_metadata_name_must_match_directory(self):
        file = self.source / "skills/thresh/SKILL.md"
        file.write_text(file.read_text(encoding="utf-8").replace("name: thresh", "name: impostor"), encoding="utf-8")
        with self.assertRaises(distribution.DistributionError):
            distribution.portable_files(self.source)

    def test_alias_version_mismatch_rejects_every_distribution_entrypoint(self):
        file = self.source / "skills/thresh/SKILL.md"
        file.write_text(file.read_text(encoding="utf-8").replace('version: "1.2.0"', 'version: "1.1.0"'), encoding="utf-8")
        operations = (
            lambda: distribution.portable_files(self.source),
            lambda: distribution.plugin_files(self.source),
            lambda: distribution.package(root=self.source, output=self.base / "archives", apply=True),
            lambda: self.install(target="generic", destination=self.base / "install", apply=True),
            lambda: self.install(target="codex", apply=True),
        )
        for operation in operations:
            with self.assertRaisesRegex(distribution.DistributionError, "metadata.version must match"):
                operation()
        self.assertFalse((self.base / "archives").exists())
        self.assertFalse((self.base / "install").exists())
        self.assertFalse((self.base / "home").exists())

    def test_alias_canonical_skill_when_declared_must_match(self):
        file = self.source / "skills/thresh/SKILL.md"
        body = file.read_text(encoding="utf-8")
        file.write_text(body.replace('  version: "1.2.0"', '  version: "1.2.0"\n  canonical_skill: "wrong-skill"'), encoding="utf-8")
        with self.assertRaisesRegex(distribution.DistributionError, "alias canonical_skill"):
            distribution.portable_files(self.source)
        file.write_text(body.replace('  version: "1.2.0"', '  version: "1.2.0"\n  canonical_skill: "ai-slop-thresher"'), encoding="utf-8")
        distribution.portable_files(self.source)

    def test_body_version_cannot_replace_missing_metadata_version(self):
        file = self.source / "skills/ai-slop-thresher/SKILL.md"
        body = file.read_text(encoding="utf-8")
        file.write_text(body.replace('  version: "1.2.0"\n', '') + '\n  version: "9.9.9"\n', encoding="utf-8")
        with self.assertRaisesRegex(distribution.DistributionError, "metadata.version"):
            distribution.version(self.source)
        with self.assertRaisesRegex(distribution.DistributionError, "metadata.version"):
            distribution.portable_files(self.source)

    def test_body_version_does_not_override_frontmatter(self):
        file = self.source / "skills/ai-slop-thresher/SKILL.md"
        body = file.read_text(encoding="utf-8")
        file.write_text(body + '\n  version: "9.9.9"\n', encoding="utf-8")
        self.assertEqual(distribution.version(self.source), "1.2.0")

    def test_unterminated_frontmatter_is_rejected(self):
        file = self.source / "skills/thresh/SKILL.md"
        file.write_text(file.read_text(encoding="utf-8").replace('---\n\n', ''), encoding="utf-8")
        with self.assertRaisesRegex(distribution.DistributionError, "unterminated frontmatter"):
            distribution.portable_files(self.source)

    def test_duplicate_frontmatter_field_is_rejected(self):
        file = self.source / "skills/thresh/SKILL.md"
        body = file.read_text(encoding="utf-8")
        file.write_text(body.replace('  version: "1.2.0"', '  version: "1.2.0"\n  version: "1.1.0"'), encoding="utf-8")
        with self.assertRaisesRegex(distribution.DistributionError, "duplicate frontmatter field"):
            distribution.portable_files(self.source)

    def test_metadata_supports_single_quotes_and_unquoted_strings(self):
        for name in distribution.SKILLS:
            file = self.source / "skills" / name / "SKILL.md"
            body = file.read_text(encoding="utf-8")
            file.write_text(body.replace('version: "1.2.0"', "version: '1.2.0'"), encoding="utf-8")
        distribution.portable_files(self.source)
        for name in distribution.SKILLS:
            file = self.source / "skills" / name / "SKILL.md"
            body = file.read_text(encoding="utf-8")
            file.write_text(body.replace("version: '1.2.0'", "version: 1.2.0"), encoding="utf-8")
        distribution.portable_files(self.source)

    def test_projection_rebuild_and_stale_check(self):
        distribution.build_plugin(root=self.source, apply=True)
        distribution.check_plugin(root=self.source)
        file = self.source / "skills/ai-slop-thresher/references/fixture.md"
        file.write_text("Updated reference\n", encoding="utf-8")
        with self.assertRaises(distribution.DistributionError):
            distribution.check_plugin(root=self.source)
        distribution.build_plugin(root=self.source, apply=True)
        distribution.check_plugin(root=self.source)

    def test_build_defaults_to_no_changes(self):
        distribution.build_plugin(root=self.source)
        self.assertFalse((self.source / "plugins").exists())

    def test_check_rejects_missing_marketplace_target(self):
        output = self.base / "custom"
        distribution.build_plugin(root=self.source, output=output, apply=True)
        with self.assertRaises(distribution.DistributionError):
            distribution.check_plugin(root=self.source, output=output)

    def test_check_rejects_wrong_marketplace_path(self):
        distribution.build_plugin(root=self.source, apply=True)
        marketplace = self.source / ".agents/plugins/marketplace.json"
        marketplace.write_text(json.dumps({"plugins": [{"source": {"source": "local", "path": "../../wrong"}}]}), encoding="utf-8")
        with self.assertRaises(distribution.DistributionError):
            distribution.check_plugin(root=self.source)

    def test_build_rejects_unmanaged_output(self):
        output = self.base / "unmanaged"
        output.mkdir()
        (output / "user.md").write_text("user", encoding="utf-8")
        with self.assertRaises(distribution.DistributionError):
            distribution.build_plugin(root=self.source, output=output, apply=True)
        self.assertEqual((output / "user.md").read_text(), "user")

    def test_build_rejects_edited_generated_output(self):
        output = self.base / "generated"
        distribution.build_plugin(root=self.source, output=output, apply=True)
        (output / "NOTICE").write_text("local edit", encoding="utf-8")
        with self.assertRaises(distribution.DistributionError):
            distribution.build_plugin(root=self.source, output=output, apply=True)

    def test_build_failed_install_restores_original(self):
        output = self.base / "generated"
        distribution.build_plugin(root=self.source, output=output, apply=True)
        original = distribution.read_tree(output)
        rename = Path.rename

        def fail_install(path, target):
            if path.name.startswith(".thresher-build-"):
                raise OSError("injected staging install failure")
            return rename(path, target)

        with patch.object(Path, "rename", fail_install), self.assertRaisesRegex(OSError, "injected staging"):
            distribution.build_plugin(root=self.source, output=output, apply=True)
        self.assertEqual(distribution.read_tree(output), original)
        self.assertEqual(list(output.parent.glob(".thresher-old-*")), [])
        self.assertEqual(list(output.parent.glob(".thresher-build-*")), [])

    def test_build_two_rename_failures_preserve_backup_and_block_retry(self):
        output = self.base / "generated"
        distribution.build_plugin(root=self.source, output=output, apply=True)
        original = distribution.read_tree(output)
        rename = Path.rename

        def fail_install_and_restore(path, target):
            if path.name.startswith(".thresher-build-"):
                raise OSError("injected staging install failure")
            if path.name.startswith(".thresher-old-"):
                raise OSError("injected backup restore failure")
            return rename(path, target)

        with patch.object(Path, "rename", fail_install_and_restore), self.assertRaises(distribution.DistributionError) as caught:
            distribution.build_plugin(root=self.source, output=output, apply=True)
        self.assertFalse(output.exists())
        backups = list(output.parent.glob(".thresher-old-*"))
        self.assertEqual(len(backups), 1)
        self.assertIn(str(backups[0]), str(caught.exception))
        self.assertEqual(distribution.read_tree(backups[0]), original)
        self.assertEqual(list(output.parent.glob(".thresher-build-*")), [])
        with self.assertRaisesRegex(distribution.DistributionError, "unresolved plugin backup"):
            distribution.build_plugin(root=self.source, output=output, apply=True)
        self.assertFalse(output.exists())
        self.assertEqual(distribution.read_tree(backups[0]), original)
        backups[0].rename(output)  # Explicit recovery after injected failures end.
        distribution.build_plugin(root=self.source, output=output, apply=True)
        self.assertEqual(distribution.read_tree(output), original)

    def test_successful_build_removes_only_its_superseded_backup(self):
        output = self.base / "generated"
        distribution.build_plugin(root=self.source, output=output, apply=True)
        reference = self.source / "skills/ai-slop-thresher/references/fixture.md"
        reference.write_text("New reference\n", encoding="utf-8")
        distribution.build_plugin(root=self.source, output=output, apply=True)
        self.assertEqual((output / "skills/ai-slop-thresher/references/fixture.md").read_bytes(), reference.read_bytes())
        self.assertEqual(list(output.parent.glob(".thresher-old-*")), [])
        self.assertEqual(list(output.parent.glob(".thresher-build-*")), [])

    def test_cleanup_failure_does_not_hide_preserved_backup(self):
        output = self.base / "generated"
        distribution.build_plugin(root=self.source, output=output, apply=True)
        original = distribution.read_tree(output)
        rename = Path.rename

        def fail_install_and_restore(path, target):
            if path.name.startswith((".thresher-build-", ".thresher-old-")):
                raise OSError("injected rename failure")
            return rename(path, target)

        with patch.object(Path, "rename", fail_install_and_restore), patch.object(distribution.shutil, "rmtree", side_effect=OSError("injected cleanup failure")), self.assertRaises(distribution.DistributionError) as caught:
            distribution.build_plugin(root=self.source, output=output, apply=True)
        backup = list(output.parent.glob(".thresher-old-*"))[0]
        self.assertIn(str(backup), str(caught.exception))
        self.assertEqual(distribution.read_tree(backup), original)

    def test_separate_self_contained_reproducible_archives(self):
        output = self.base / "archives"
        result = distribution.package(root=self.source, output=output)
        self.assertFalse(output.exists())
        self.assertTrue(result["dry_run"])
        first = distribution.package(root=self.source, output=output, apply=True)
        second = distribution.package(root=self.source, output=self.base / "second-archives", apply=True)
        self.assertEqual(first["packages"], second["packages"])
        with self.assertRaisesRegex(distribution.DistributionError, "existing archive"):
            distribution.package(root=self.source, output=output, apply=True)
        with zipfile.ZipFile(output / "ai-slop-thresher-portable.zip") as archive:
            self.assertFalse(any("agents/" in name or ".codex-plugin" in name for name in archive.namelist()))
            self.assertTrue(all(name in archive.namelist() for name in distribution.LEGAL))
        with zipfile.ZipFile(output / "ai-slop-thresher-codex-plugin.zip") as archive:
            self.assertIn(".codex-plugin/plugin.json", archive.namelist())
            self.assertIn("skills/thresh/agents/openai.yaml", archive.namelist())
            manifest = json.loads(archive.read(".codex-plugin/plugin.json"))
            self.assertEqual(manifest["skills"], "./skills/")
            self.assertEqual(manifest["version"], "1.2.0")
            self.assertTrue(all(name in archive.namelist() for name in distribution.LEGAL))
        self.assertEqual((output / "ai-slop-thresher.zip").read_bytes(), (output / "ai-slop-thresher-portable.zip").read_bytes())

    def test_archive_external_members_do_not_appear(self):
        files = distribution.plugin_files(self.source)
        blob = distribution.archive_bytes(files)
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            self.assertEqual({name: archive.read(name) for name in archive.namelist()}, files)

    def store_manifest(self, icon="./assets/icon.png"):
        manifest = {
            "name": "ai-slop-thresher", "version": "1.2.2", "skills": "./skills/",
            "interface": {"logo": icon, "composerIcon": icon},
        }
        path = self.source / "integrations/codex/plugin.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path, manifest

    def test_store_manifest_packages_assets_without_changing_skill_version(self):
        self.store_manifest()
        icon = self.source / "assets/icon.png"
        icon.parent.mkdir()
        icon.write_bytes(b"image fixture")
        files = distribution.plugin_files(self.source)
        self.assertEqual(files["assets/icon.png"], b"image fixture")
        self.assertEqual(json.loads(files[".codex-plugin/plugin.json"])["version"], "1.2.2")
        self.assertEqual(distribution.version(self.source), "1.2.0")
        self.assertEqual(files["skills/ai-slop-thresher/SKILL.md"], (self.source / "skills/ai-slop-thresher/SKILL.md").read_bytes())
        result = distribution.build_plugin(root=self.source, output=self.base / "store")
        self.assertEqual((result["version"], result["skill_version"]), ("1.2.2", "1.2.0"))

    def test_store_manifest_requires_every_referenced_asset(self):
        self.store_manifest()
        with self.assertRaises(FileNotFoundError):
            distribution.plugin_files(self.source)

    def test_store_manifest_rejects_asset_path_escape(self):
        for icon in ("./assets/../../private.png", "C:/private.png", "./assets\\icon.png"):
            self.store_manifest(icon)
            with self.subTest(icon=icon), self.assertRaisesRegex(distribution.DistributionError, "asset path"):
                distribution.plugin_files(self.source)

    def test_store_manifest_cannot_redirect_plugin_identity_or_skills(self):
        for key, value in (("name", "unrelated"), ("skills", "../external")):
            path, manifest = self.store_manifest()
            manifest[key] = value
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.subTest(key=key), self.assertRaisesRegex(distribution.DistributionError, "identify"):
                distribution.plugin_files(self.source)


if __name__ == "__main__":
    unittest.main()
