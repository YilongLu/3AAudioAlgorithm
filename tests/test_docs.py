import unittest
from pathlib import Path


class TestDocumentation(unittest.TestCase):
    def test_readme_has_no_merge_conflict_markers(self) -> None:
        readme = Path(__file__).resolve().parents[1] / "README.md"
        content = readme.read_text(encoding="utf-8")
        self.assertNotIn("<<<<<<<", content)
        self.assertNotIn("=======", content)
        self.assertNotIn(">>>>>>>", content)
