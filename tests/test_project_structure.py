import ast
from pathlib import Path
import unittest

from lab import __version__
from lab.tui import APP_VERSION
from lab.web.security_headers_lab import VERSION

ROOT = Path(__file__).resolve().parents[1]


class ProjectStructureTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md",
            "CHANGELOG.md", ".gitignore", "pyproject.toml", "CITATION.cff",
            "ROADMAP.md", "docs/ARCHITECTURE.md", ".github/workflows/tests.yml",
            "docs/methodology/README.md", "docs/scenarios/TEMPLATE.md",
            "docs/scenarios/web-security-headers.md", "lab/__init__.py",
            "lab/web/__init__.py", "lab/web/security_headers_lab.py",
            "lab/report.py", "lab/tui.py", "tests/test_tui.py", "tests/test_project_structure.py",
            "tests/test_security_headers_lab.py", "tests/test_report.py",
        ]
        for name in required:
            with self.subTest(path=name):
                self.assertTrue((ROOT / name).is_file(), f"Missing: {name}")

    def test_all_python_sources_parse(self):
        ignored = {".git", "__pycache__", ".venv", "venv"}
        sources = [
            path for path in ROOT.rglob("*.py")
            if not any(part in ignored for part in path.parts)
        ]
        self.assertTrue(sources, "No Python source files found")
        for path in sources:
            with self.subTest(path=str(path.relative_to(ROOT))):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_release_versions_are_consistent(self):
        self.assertEqual(__version__, "1.0.1")
        self.assertEqual(VERSION, __version__)
        self.assertEqual(APP_VERSION, __version__)

    def test_readme_describes_real_features(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in ("lab/tui.py", "lab.report", "127.0.0.1", "unittest"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, readme)


if __name__ == "__main__":
    unittest.main()
