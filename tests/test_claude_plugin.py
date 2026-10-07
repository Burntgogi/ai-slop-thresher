"""Claude Code plugin manifests stay in step with the portable skills; no live installation."""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("distribution", ROOT / "scripts/distribute.py")
distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(distribution)


def manifest(name):
    return json.loads((ROOT / ".claude-plugin" / name).read_text(encoding="utf-8"))


class ClaudePluginTests(unittest.TestCase):
    def test_plugin_version_matches_skills(self):
        plugin = manifest("plugin.json")
        self.assertEqual(plugin["name"], "ai-slop-thresher")
        self.assertEqual(plugin["version"], distribution.version(ROOT))

    def test_marketplace_points_to_repository_root(self):
        entries = manifest("marketplace.json")["plugins"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], manifest("plugin.json")["name"])
        self.assertEqual(entries[0]["source"], "./")

    def test_root_skills_are_the_portable_pair(self):
        # Claude Code discovers skills/<name>/SKILL.md at the plugin root.
        found = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(found, sorted(distribution.SKILLS))
        distribution.portable_files(ROOT)  # Rejects Codex metadata and broken links.

    def test_no_unintended_plugin_components_at_root(self):
        # These root entries would be loaded as extra Claude Code plugin components.
        for name in ("commands", "agents", "hooks", "output-styles", "bin", "workflows", "themes", "monitors",
                     "settings.json", ".mcp.json", ".lsp.json"):
            self.assertFalse((ROOT / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
