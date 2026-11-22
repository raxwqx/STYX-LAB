import io
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest
from http.client import HTTPException
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab.tui import DIM, display_width, draw_box, fit, health, unlock_splash  # noqa: E402

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
BOX_PREFIXES = ("╔", "╠", "╚", "║", "╭", "├", "╰", "│")


class FakeTTY(io.StringIO):
    def isatty(self):
        return True


class FakeResponse:
    status = 200

    def __init__(self, body):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


def box_widths(buffer):
    plain = ANSI.sub("", buffer.getvalue())
    lines = [line for line in plain.splitlines() if line.startswith(BOX_PREFIXES)]
    return {display_width(line) for line in lines}


class DisplayWidthTests(unittest.TestCase):
    def test_width_counts_emoji_as_two_cells(self):
        self.assertEqual(display_width("ABC"), 3)
        self.assertEqual(display_width("🔒"), 2)
        self.assertEqual(display_width("A🔒B"), 4)
        # Combining accents and emoji variation selectors occupy no cell.
        self.assertEqual(display_width("e\u0301"), 1)
        self.assertEqual(display_width("\ufe0f"), 0)

    def test_fit_pads_and_truncates_to_exact_cell_width(self):
        self.assertEqual(display_width(fit("🔒", 6)), 6)
        self.assertEqual(display_width(fit("🔒🔒🔒", 3)), 3)
        self.assertEqual(fit("abcdef", 3), "abc")
        self.assertEqual(fit("", 4), "    ")
        self.assertEqual(display_width(fit("🔒 LOCKED", 11)), 11)


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
        self.assertIn("Launch weak profile", result.stdout)
        self.assertIn("Stay sharp", result.stdout)

    def test_interactive_splash_animates_locked_to_unlocked(self):
        fake_stdout = FakeTTY()
        with patch.dict(os.environ, {"TERM": "xterm"}, clear=False):
            with patch.dict(os.environ, {"STYXLAB_NO_ANIMATION": ""}, clear=False):
                with patch("sys.stdout", fake_stdout):
                    with patch("lab.tui.time.sleep"):
                        with patch(
                            "lab.tui.shutil.get_terminal_size",
                            return_value=os.terminal_size((80, 24)),
                        ):
                            unlock_splash()
        output = fake_stdout.getvalue()
        self.assertIn("STYHQ // SECURE ACCESS GATE", output)
        self.assertIn("🔒", output)
        self.assertIn("🔓", output)
        self.assertIn("ACCESS GRANTED", output)
        self.assertIn("NO LOGIN OR AUTH CHECK IS PERFORMED", output)

    def test_splash_rows_stay_aligned_with_emoji(self):
        fake_stdout = FakeTTY()
        with patch.dict(os.environ, {"TERM": "xterm"}, clear=False):
            with patch.dict(os.environ, {"STYXLAB_NO_ANIMATION": ""}, clear=False):
                with patch("sys.stdout", fake_stdout):
                    with patch("lab.tui.time.sleep"):
                        with patch(
                            "lab.tui.shutil.get_terminal_size",
                            return_value=os.terminal_size((80, 24)),
                        ):
                            unlock_splash()
        self.assertEqual(box_widths(fake_stdout), {78})

    def test_draw_box_rows_stay_aligned_with_emoji(self):
        fake_stdout = FakeTTY()
        with patch("sys.stdout", fake_stdout):
            with patch(
                "lab.tui.shutil.get_terminal_size",
                return_value=os.terminal_size((80, 24)),
            ):
                draw_box("STYX-LAB", [("🔒 LOCKED", DIM), ("plain", DIM), ("🔓" * 30, DIM)])
        self.assertEqual(box_widths(fake_stdout), {78})


class HealthProbeTests(unittest.TestCase):
    def test_non_object_json_is_treated_as_offline(self):
        for body in (b"[]", b"null", b"42", b'"text"'):
            with self.subTest(body=body), patch(
                "lab.tui.urlopen", return_value=FakeResponse(body)
            ):
                self.assertIsNone(health(8766))

    def test_missing_or_invalid_profile_becomes_unknown(self):
        for body in (
            b'{"status": "ok"}',
            b'{"status": "ok", "profile": null}',
            b'{"status": "ok", "profile": 7}',
            b'{"status": "ok", "profile": ""}',
        ):
            with self.subTest(body=body), patch(
                "lab.tui.urlopen", return_value=FakeResponse(body)
            ):
                self.assertEqual(health(8766), "unknown")

    def test_healthy_profile_is_returned(self):
        body = b'{"status": "ok", "profile": "secure"}'
        with patch("lab.tui.urlopen", return_value=FakeResponse(body)):
            self.assertEqual(health(8766), "secure")

    def test_connection_failure_returns_none(self):
        with patch("lab.tui.urlopen", side_effect=OSError("connection refused")):
            self.assertIsNone(health(8766))

    def test_malformed_http_framing_returns_none(self):
        with patch("lab.tui.urlopen", side_effect=HTTPException("bad status line")):
            self.assertIsNone(health(8766))


if __name__ == "__main__":
    unittest.main()
