"""README and local previews: fresh previews, resolvable links and anchors. Standard library only."""

import hashlib
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
PAGES = {"README.md": "index.html", "README.en.md": "index.en.html", "RELEASE_NOTES.md": "release-notes.html"}
REBUILD = "rebuild with: node evaluation/build_frontpage.cjs (needs the marked package)"


def local_targets(text):
    for link in re.findall(r'\]\(([^)\s]+)\)|(?:src|href)="([^"]+)"', text):
        target = next(part for part in link if part)
        if not re.match(r"[a-z][a-z0-9+.-]*:|//|#", target):
            yield target


class FrontpageTests(unittest.TestCase):
    def test_previews_match_their_markdown(self):
        for source, preview in PAGES.items():
            html = (ROOT / "docs/preview" / preview).read_text(encoding="utf-8")
            recorded = re.search(r'<meta name="source-sha256" content="([0-9a-f]{64})">', html)
            expected = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
            with self.subTest(preview=preview):
                self.assertIsNotNone(recorded, f"{preview} has no source hash; {REBUILD}")
                self.assertEqual(recorded.group(1), expected, f"{preview} is stale for {source}; {REBUILD}")

    def test_markdown_local_links_resolve(self):
        for source in PAGES:
            for target in local_targets((ROOT / source).read_text(encoding="utf-8")):
                path = (ROOT / unquote(target.split("#")[0])).resolve()
                with self.subTest(source=source, target=target):
                    self.assertTrue(path.exists(), f"{source} links to missing {target}")

    def test_preview_links_images_and_anchors_resolve(self):
        folder = ROOT / "docs/preview"
        for preview in PAGES.values():
            html = (folder / preview).read_text(encoding="utf-8")
            ids = set(re.findall(r'id="([^"]+)"', html))
            for target in re.findall(r'(?:src|href)="([^"]+)"', html):
                with self.subTest(preview=preview, target=target):
                    if target.startswith("#"):
                        self.assertIn(unquote(target[1:]), ids, f"{preview} has no anchor {target}")
                    elif not re.match(r"[a-z][a-z0-9+.-]*:|//", target):
                        self.assertTrue((folder / unquote(target.split("#")[0])).resolve().exists(), f"{preview} links to missing {target}")


if __name__ == "__main__":
    unittest.main()
