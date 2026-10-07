"""One plugin directory serves Codex and Claude Code; manifests stay in step with the skills."""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("distribution", ROOT / "scripts/distribute.py")
distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(distribution)


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class ClaudePluginTests(unittest.TestCase):
    def test_every_distribution_shares_one_version(self):
        # One release number for the skills, the Codex plugin and the Claude Code plugin.
        versions = {read_json("integrations/claude-code/plugin.json")["version"],
                    read_json("integrations/codex/plugin.json")["version"]}
        self.assertEqual(versions, {distribution.version(ROOT)})

    def test_both_marketplaces_point_to_the_shared_projection(self):
        claude = read_json(".claude-plugin/marketplace.json")["plugins"]
        self.assertEqual(len(claude), 1)
        self.assertEqual(claude[0]["name"], read_json("integrations/claude-code/plugin.json")["name"])
        self.assertEqual(claude[0]["source"], "./" + distribution.PLUGIN_DIR)
        codex = read_json(".agents/plugins/marketplace.json")["plugins"]
        self.assertEqual(codex[0]["source"]["path"], "./" + distribution.PLUGIN_DIR)

    def test_repository_root_is_a_marketplace_not_a_plugin(self):
        # A root plugin.json would make Claude Code copy the whole repository into its cache.
        self.assertFalse((ROOT / ".claude-plugin/plugin.json").exists())
        for name in ("commands", "agents", "hooks", "output-styles", "bin", "workflows", "themes", "monitors",
                     "settings.json", ".mcp.json", ".lsp.json"):
            self.assertFalse((ROOT / distribution.PLUGIN_DIR / name).exists(), name)

    def test_projection_carries_claude_only_frontmatter(self):
        files = distribution.plugin_files(ROOT)
        thresh = files["skills/thresh/SKILL.md"].decode("utf-8").split("\n---", 1)[0]
        self.assertIn("\ndisable-model-invocation: true", thresh)
        self.assertIn(".claude-plugin/plugin.json", files)
        # The portable skill and the Codex store package keep only Agent Skills fields.
        portable = (ROOT / "skills/thresh/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("disable-model-invocation", portable)
        store = distribution.plugin_files(ROOT, claude=False)
        self.assertEqual(store["skills/thresh/SKILL.md"], (ROOT / "skills/thresh/SKILL.md").read_bytes())
        self.assertFalse(any(name.startswith(".claude-plugin/") for name in store))

    def test_host_frontmatter_cannot_override_source_fields(self):
        data = (ROOT / "skills/thresh/SKILL.md").read_bytes()
        with self.assertRaisesRegex(distribution.DistributionError, "already in source"):
            distribution.with_frontmatter(data, {"description": "x"}, "thresh")
        with self.assertRaisesRegex(distribution.DistributionError, "invalid host frontmatter"):
            distribution.with_frontmatter(data, {"bad key": "x"}, "thresh")


if __name__ == "__main__":
    unittest.main()
