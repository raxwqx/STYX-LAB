import io
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab.tui import unlock_splash  # noqa: E402


class FakeTTY(io.StringIO):
    def isatty(self):
        return True


class TerminalInterfaceTests(unittest.TestCase):
    def test_menu_starts_displays_sty_hq_branding_and_exits(self):
        env = os.environ.copy()
        env["STYXLAB_NO_ANIMATION"] = "1"
        result = subprocess.run(
            [sys.executable, str(ROOT / "lab" / "tui.py")],
            input="0\n",
            capture_output=True,
            text=True,
            cwd=ROOT,
            env=env,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("STYHQ", result.stdout)
        self.assertIn("LOCK SEQUENCE SKIPPED", result.stdout)
        self.assertIn("COMMAND CENTER", result.stdout)
        self.assertIn("Stay sharp", result.stdout)

    def test_interactive_splash_animates_locked_to_unlocked(self):
        fake_stdout = FakeTTY()
        with patch.dict(os.environ, {"TERM": "xterm"}, clear=False):
            with patch.dict(os.environ, {"STYXLAB_NO_ANIMATION": ""}, clear=False):
                with patch("sys.stdout", fake_stdout):
                    with patch("lab.tui.time.sleep"):
                        with patch("lab.tui.shutil.get_terminal_size", return_value=os.terminal_size((80, 24))):
                            unlock_splash()
        output = fake_stdout.getvalue()
        self.assertIn("STYHQ // SECURE ACCESS GATE", output)
        self.assertIn("🔒", output)
        self.assertIn("🔓", output)
        self.assertIn("ACCESS GRANTED", output)
        self.assertIn("NO LOGIN OR AUTH CHECK IS PERFORMED", output)


if __name__ == "__main__":
    unittest.main()
