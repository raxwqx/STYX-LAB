"""STYX-LAB animated terminal control deck with STYHQ branding."""

import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
import json

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "lab" / "web" / "security_headers_lab.py"
SCENARIO = ROOT / "docs" / "scenarios" / "web-security-headers.md"

CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
DIM = "\033[90m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
APP_VERSION = "1.0.1"


def color(text, code):
    if sys.stdout.isatty() and "NO_COLOR" not in os.environ:
        return f"{code}{text}{RESET}"
    return text


def clear():
    if sys.stdout.isatty() and os.environ.get("TERM") != "dumb":
        print("\033[2J\033[H", end="")
    else:
        print("\n")


def animate(message, frames=10):
    symbols = ("◢", "◣", "◤", "◥")
    if not sys.stdout.isatty() or os.environ.get("STYXLAB_NO_ANIMATION"):
        print(f"[*] {message}")
        return
    for index in range(frames):
        print("\r" + color(symbols[index % len(symbols)], CYAN) + " " + message, end="", flush=True)
        time.sleep(0.045)
    print("\r" + color("[OK]", GREEN) + " " + message + " " * 8)


def unlock_splash():
    """Play a short lock-to-unlocked startup sequence in an interactive TTY.

    Non-interactive runs and tests get a concise textual boot notice instead
    of terminal control codes or deliberate delays.
    """
    interactive = (
        sys.stdout.isatty()
        and os.environ.get("TERM") != "dumb"
        and not os.environ.get("STYXLAB_NO_ANIMATION")
    )
    if not interactive:
        print(color("STYHQ // SECURE ACCESS GATE", CYAN))
        print(color("[BOOT] LOCK SEQUENCE SKIPPED (non-interactive mode)", DIM))
        print(color("[READY] STYHQ CONTROL DECK // visual intro only", GREEN))
        return

    terminal_columns = shutil.get_terminal_size((80, 24)).columns
    width = min(max(terminal_columns - 2, 58), 82)
    inner = width - 4
    bar_width = min(28, inner - 12)
    frames = [
        ("🔒", "GATE LOCKED", "Powering the local control deck", 0, CYAN, 0.14),
        ("🔒", "INITIALIZING", "Loading the STYX-LAB interface", 18, CYAN, 0.14),
        ("🔒", "VERIFYING MODULES", "Checking local lab components", 38, BLUE, 0.16),
        ("🔐", "RELEASING LATCH", "Preparing the interface", 58, MAGENTA, 0.16),
        ("🔓", "GATE UNLOCKED", "STYHQ control deck is ready", 82, GREEN, 0.18),
        ("🔓", "ACCESS GRANTED", "Opening the STYX-LAB command center", 100, GREEN, 0.42),
    ]

    def row(text="", code=DIM):
        text = str(text)
        if len(text) > inner:
            text = text[:inner]
        # Lock emoji can occupy two terminal cells; keep a little visual slack.
        left = max(0, (inner - len(text)) // 2)
        payload = (" " * left + text).ljust(inner)
        print(color("║", CYAN) + " " + color(payload, code) + " " + color("║", CYAN))

    for lock_icon, state, detail, percent, state_color, delay in frames:
        clear()
        print(color("╔" + "═" * (width - 2) + "╗", CYAN))
        row("STYHQ // SECURE ACCESS GATE", CYAN)
        row(f"STYX-LAB v{APP_VERSION}  •  LOCAL-FIRST SECURITY LAB", DIM)
        print(color("╠" + "═" * (width - 2) + "╣", CYAN))
        row()
        row(lock_icon, state_color)
        row(state, state_color)
        row()
        row(detail, CYAN)
        filled = round(bar_width * percent / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        row(f"[{bar}] {percent:3d}%", GREEN if percent == 100 else CYAN)
        row()
        row("VISUAL INTRO ONLY • NO LOGIN OR AUTH CHECK IS PERFORMED", DIM)
        row("LOCAL CONTROL DECK // 127.0.0.1", DIM)
        print(color("╚" + "═" * (width - 2) + "╝", CYAN))
        time.sleep(delay)

    # Give the open-lock / access-granted state a small readable pause.
    time.sleep(0.18)


def port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
            return True
    except OSError:
        return False


def health(port):
    try:
        with urlopen(f"http://127.0.0.1:{port}/health", timeout=0.6) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if response.status == 200 and payload.get("status") == "ok":
                return payload.get("profile", "unknown")
    except (OSError, URLError, ValueError, json.JSONDecodeError):
        pass
    return None


def draw_box(title, lines):
    terminal_width = shutil.get_terminal_size((80, 24)).columns
    width = min(max(terminal_width - 2, 48), 84)
    inner = width - 4
    print(color("╭" + "─" * (width - 2) + "╮", CYAN))
    heading = (" " + title + " ")[:inner].ljust(inner)
    print(color("│", CYAN) + " " + color(heading, CYAN) + " " + color("│", CYAN))
    print(color("├" + "─" * (width - 2) + "┤", CYAN))
    for text, code in lines:
        text = str(text)[:inner].ljust(inner)
        print(color("│", CYAN) + " " + color(text, code) + " " + color("│", CYAN))
    print(color("╰" + "─" * (width - 2) + "╯", CYAN))


def dashboard():
    clear()
    draw_box("STYX-LAB // CYBERSECURITY CONTROL DECK", [
        ("LOCAL-FIRST DEFENSIVE TRAINING PLATFORM", DIM),
        ("", DIM),
        ("   ╭───────────────╮", MAGENTA),
        ("   │    STYHQ      │", MAGENTA),
        ("   │  SECURITY HQ  │", MAGENTA),
        ("   ╰───────────────╯", MAGENTA),
    ])
    secure = health(8766)
    baseline = health(8765)
    draw_box("LIVE STATUS", [
        (f"SECURE   127.0.0.1:8766  [{secure.upper() if secure else 'OFFLINE'}]", GREEN if secure else DIM),
        (f"BASELINE 127.0.0.1:8765  [{baseline.upper() if baseline else 'OFFLINE'}]", GREEN if baseline else DIM),
        (f"PYTHON {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", CYAN),
        (f"LOCAL TIME {time.strftime('%Y-%m-%d %H:%M:%S')}", DIM),
    ])
    draw_box("COMMAND CENTER", [
        ("[1] Launch secure profile", GREEN),
        ("[2] Launch baseline profile", YELLOW),
        ("[3] Run automated tests", CYAN),
        ("[4] Run local assessment + export reports", CYAN),
        ("[5] Read scenario guide", MAGENTA),
        ("[0] Exit control deck", DIM),
    ])
    return input(color("STYHQ // STYX-LAB", CYAN) + color(" > ", GREEN)).strip()


def pause():
    try:
        input(color("\nPress Enter to return to the control deck...", DIM))
    except (EOFError, KeyboardInterrupt):
        pass


def launch_lab(profile, default_port):
    if not SERVER.is_file():
        print(color(f"Missing server module: {SERVER}", RED))
        pause()
        return
    try:
        raw = input(f"Port [{default_port}]: ").strip()
        port = int(raw) if raw else default_port
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        print(color("Port must be a number from 1 to 65535.", RED))
        pause()
        return
    if port_open(port):
        profile = health(port)
        detail = f"STYX-LAB profile '{profile}' is responding" if profile else "another service may be using this port"
        print(color(f"Port {port} is already in use; {detail}. Choose another port.", YELLOW))
        pause()
        return
    animate(f"Starting {profile.upper()} local profile")
    print(color(f"Local URL: http://127.0.0.1:{port}/", GREEN))
    print(color("Press Ctrl+C to stop the service and return to the panel.", DIM))
    try:
        subprocess.run([sys.executable, str(SERVER), "--profile", profile, "--port", str(port)], cwd=ROOT, check=False)
    except KeyboardInterrupt:
        print(color("\nService stopped.", YELLOW))
    pause()


def run_tests():
    print(color("\nSTYHQ // AUTOMATED QUALITY GATE\n", CYAN))
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=False)
    print(color("\n[PASS] Test suite passed." if result.returncode == 0 else f"\n[FAIL] Test suite exited with {result.returncode}.", GREEN if result.returncode == 0 else RED))
    pause()


def run_assessment():
    raw = input("Local port to assess [8766]: ").strip()
    try:
        port = int(raw) if raw else 8766
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        print(color("Port must be a number from 1 to 65535.", RED))
        pause()
        return
    print(color("Assessing loopback only; no remote hosts are contacted.", DIM))
    result = subprocess.run([sys.executable, "-m", "lab.report", "--port", str(port)], cwd=ROOT, check=False)
    if result.returncode == 0:
        print(color("Assessment completed. Review JSON and Markdown evidence in reports/.", GREEN))
    else:
        print(color("Assessment found failures or the local service is unavailable. Review report details.", YELLOW))
    pause()


def read_scenario():
    clear()
    if SCENARIO.is_file():
        print(color("STYX-LAB // SCENARIO GUIDE", CYAN))
        print(SCENARIO.read_text(encoding="utf-8"))
    else:
        print(color("Scenario document not found.", RED))
    pause()


def main():
    if not SERVER.is_file():
        print(color("ERROR: Web security module not found.", RED))
        return 1
    unlock_splash()
    while True:
        try:
            choice = dashboard()
            if choice == "1":
                launch_lab("secure", 8766)
            elif choice == "2":
                launch_lab("baseline", 8765)
            elif choice == "3":
                run_tests()
            elif choice == "4":
                run_assessment()
            elif choice == "5":
                read_scenario()
            elif choice == "0":
                animate("Closing STYHQ control deck", 6)
                print(color("Stay sharp. Stay defensive. STYHQ / STYX-LAB.", GREEN))
                return 0
            else:
                print(color("Unknown option. Choose 0-5.", RED))
                time.sleep(0.8)
        except (KeyboardInterrupt, EOFError):
            print(color("\nSTYX-LAB interface closed.", YELLOW))
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
