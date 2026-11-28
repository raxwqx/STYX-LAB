"""Generate the repository artwork from real output.

Everything is deterministic except the timestamps and log lines that the lab
itself emits:

    python3 tools/make_assets.py

Outputs:

    assets/hero.svg       banner with the STYX-LAB mark
    assets/pipeline.svg   assessment pipeline diagram
    assets/demo.gif       terminal recording of a real weak-profile run
    assets/demo.mp4       the same recording, H.264

The transcript starts the real lab server, queries it with curl, runs the real
report command, and stops the server again. No output is typed by hand.
"""

from __future__ import annotations

import base64
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

BG = "#0b1524"
PANEL = "#101e31"
EDGE = "#2a3e57"
TEXT = "#cfc7b5"
DIM = "#7c8a9e"
MUTED = "#93a0b4"
CREAM = "#f2e8d5"
WARN = "#e8ae72"

NAVY = "#14243a"
NAVY_GRID = "#1b2f49"
NAVY_EDGE = "#33465f"
NAVY_DIM = "#8fa0b5"

MONO = "/usr/share/fonts/truetype/firacode/FiraCode-Regular.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/firacode/FiraCode-Bold.ttf"

WIDTH, HEIGHT = 1040, 600
PAD = 40
LINE = 24
FONT_SIZE = 16
PORT = 8767
CURL_CMD = (
    "curl -sI 127.0.0.1:8767 "
    "| grep -E 'HTTP|Server|Content-Security|X-Frame|Referrer'"
)


# -- real transcript --------------------------------------------------


def _port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def transcript() -> list[tuple[str, str]]:
    """Run the lab and the report, and return the real terminal lines."""
    if not _port_is_free(PORT):
        raise SystemExit(f"port {PORT} is busy; stop the lab server first")

    server = subprocess.Popen(
        [sys.executable, "-u", "lab/web/security_headers_lab.py",
         "--profile", "weak", "--port", str(PORT)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        banner = [server.stdout.readline().rstrip() for _ in range(3)]

        curl = subprocess.run(
            ["bash", "-c", CURL_CMD],
            capture_output=True, text=True, check=True,
        ).stdout.splitlines()
        headers = [
            line for line in curl
            if re.match(r"^(HTTP|Server|Content-Security|X-Frame|Referrer)", line)
        ]

        shutil.rmtree(ROOT / "reports", ignore_errors=True)
        report = subprocess.run(
            [sys.executable, "-m", "lab.report", "--port", str(PORT),
             "--fail-on", "medium"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        output = report.stdout.splitlines()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        shutil.rmtree(ROOT / "reports", ignore_errors=True)

    lines: list[tuple[str, str]] = [
        ("cmd", f"python3 lab/web/security_headers_lab.py --profile weak --port {PORT}"),
    ]
    lines += [("out", line) for line in banner]
    lines.append(("blank", ""))
    lines.append(("cmd", CURL_CMD))
    lines += [("out", line) for line in headers]
    lines.append(("blank", ""))
    lines.append(("cmd", f"python3 -m lab.report --port {PORT} --fail-on medium"))
    for line in output:
        if line.startswith("error:"):
            lines.append(("warn", line))
        elif line.startswith("Assessment result:"):
            lines.append(("ok", line))
        elif line.startswith("Header findings:"):
            lines.append(("stat", line))
        elif line.startswith(("JSON report:", "Markdown report:")):
            lines.append(("dim", line))
        else:
            lines.append(("out", line))
    return lines


# -- terminal recording ----------------------------------------------


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = MONO_BOLD if bold else MONO
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _panel_mask():
    scale = 4
    mask = Image.new("L", (WIDTH * scale, HEIGHT * scale), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        (12 * scale, 12 * scale, (WIDTH - 12) * scale, (HEIGHT - 12) * scale),
        radius=14 * scale,
        fill=255,
    )
    return mask.resize((WIDTH, HEIGHT), Image.LANCZOS)


MASK = _panel_mask()


def frame(lines, cursor=True, inline=False):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    draw.rectangle((12, 12, WIDTH - 12, HEIGHT - 12), fill=PANEL)
    draw.rounded_rectangle(
        (12, 12, WIDTH - 12, HEIGHT - 12), radius=14, outline=EDGE
    )
    draw.line((12, 62, WIDTH - 12, 62), fill=EDGE)
    for index in range(3):
        x = 40 + index * 22
        draw.ellipse((x, 31, x + 11, 41), outline=DIM, width=1)
    draw.text(
        (WIDTH / 2, 30), "styx-lab  ·  weak profile",
        font=font(14), fill=MUTED, anchor="ma",
    )

    body = font(FONT_SIZE)
    y = 82
    inline_x = PAD

    for kind, text in lines:
        if kind == "blank":
            y += LINE
            continue
        if kind == "cmd":
            draw.text((PAD, y), "$", font=font(FONT_SIZE, bold=True), fill=CREAM)
            draw.text((PAD + 22, y), text, font=body, fill=CREAM)
            inline_x = PAD + 22 + body.getlength(text)
        elif kind == "ok":
            draw.text((PAD, y), text, font=font(FONT_SIZE, bold=True), fill=CREAM)
            inline_x = PAD + body.getlength(text)
        elif kind == "stat":
            draw.text((PAD, y), text, font=font(FONT_SIZE, bold=True), fill=WARN)
            inline_x = PAD + body.getlength(text)
        elif kind == "warn":
            draw.text((PAD, y), text, font=font(FONT_SIZE, bold=True), fill=WARN)
            inline_x = PAD + body.getlength(text)
        elif kind == "dim":
            draw.text((PAD, y), text, font=body, fill=DIM)
            inline_x = PAD + body.getlength(text)
        else:
            draw.text((PAD, y), text, font=body, fill=TEXT)
            inline_x = PAD + body.getlength(text)
        y += LINE

    if cursor:
        if inline:
            draw.rectangle(
                (inline_x + 2, y - LINE + 3, inline_x + 11, y - LINE + 19),
                fill=CREAM,
            )
        else:
            draw.rectangle((PAD, y + 3, PAD + 9, y + 19), fill=CREAM)

    return Image.composite(image, Image.new("RGB", (WIDTH, HEIGHT), BG), MASK)


def build_gif(lines):
    frames, durations, shown = [], [], []

    def push(cursor=True, delay=60, inline=False):
        frames.append(frame(shown, cursor=cursor, inline=inline))
        durations.append(delay)

    for kind, text in lines:
        if kind == "cmd":
            typed = ""
            for index in range(0, len(text), 4):
                typed = text[: index + 4]
                shown.append((kind, typed))
                push(delay=22, inline=True)
                shown.pop()
            shown.append((kind, typed))
            push(delay=240)
        elif kind == "blank":
            shown.append((kind, text))
            push(delay=80)
        else:
            shown.append((kind, text))
            push(delay=70 if kind not in ("ok", "stat", "warn") else 260)

    for _ in range(2):
        push(cursor=True, delay=380)
        push(cursor=False, delay=380)

    palette = frame(lines, cursor=False).quantize(colors=96)
    bg_index = palette.getpixel((0, 0))
    indexed = [
        image.quantize(palette=palette, dither=Image.Dither.NONE)
        for image in frames
    ]
    indexed[0].save(
        ASSETS / "demo.gif",
        save_all=True,
        append_images=indexed[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
        transparency=bg_index,
    )
    return frames, durations


def build_mp4(frames, durations):
    frames_dir = ROOT / "reports" / "_frames"
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True)

    saved = 0
    for image, duration in zip(frames, durations):
        repeats = max(1, round(duration / 80))
        for _ in range(repeats):
            image.save(frames_dir / f"{saved:04d}.png")
            saved += 1

    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-framerate", "12.5",
            "-i", str(frames_dir / "%04d.png"),
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            str(ASSETS / "demo.mp4"),
        ],
        check=True,
    )
    shutil.rmtree(frames_dir, ignore_errors=True)
    shutil.rmtree(ROOT / "reports", ignore_errors=True)


# -- svg --------------------------------------------------------------


def build_mark():
    """Extract the cream emblem from the logo into a transparent PNG."""
    source = Image.open(ASSETS / "styx-lab-logo.png").convert("RGB")
    pixels = source.load()
    width, height = source.size
    out = Image.new("RGBA", (width, height))
    alpha = out.load()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            value = max(0.0, min(1.0, (lum - 45) / 150))
            alpha[x, y] = (242, 232, 213, int(round(value * 255)))
    strong = out.getchannel("A").point(lambda v: 255 if v > 60 else 0)
    box = strong.getbbox()
    pad = 10
    crop = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
    out.crop(crop).save(ASSETS / "styx-mark.png")


def build_hero():
    mark = base64.b64encode((ASSETS / "styx-mark.png").read_bytes()).decode()
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="420"
     viewBox="0 0 1280 420" role="img" aria-label="STYX-LAB">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1a2d46"/>
      <stop offset="0.55" stop-color="#122235"/>
      <stop offset="1" stop-color="#0b1624"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.78" cy="0.26" r="0.62">
      <stop offset="0" stop-color="{CREAM}" stop-opacity="0.12"/>
      <stop offset="1" stop-color="{CREAM}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow2" cx="0.10" cy="0.92" r="0.55">
      <stop offset="0" stop-color="#4d7bab" stop-opacity="0.22"/>
      <stop offset="1" stop-color="#4d7bab" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#1e3350" stroke-width="1"/>
    </pattern>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{CREAM}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{CREAM}" stop-opacity="0.28"/>
      <stop offset="1" stop-color="{CREAM}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="card">
      <rect x="1" y="1" width="1278" height="418" rx="22"/>
    </clipPath>
  </defs>

  <rect x="1" y="1" width="1278" height="418" rx="22" fill="url(#bg)"/>
  <g clip-path="url(#card)">
    <rect width="1280" height="420" fill="url(#grid)" opacity="0.5"/>
    <rect width="1280" height="420" fill="url(#glow)"/>
    <rect width="1280" height="420" fill="url(#glow2)"/>
    <path d="M0 0 L470 0 L250 420 L0 420Z" fill="{CREAM}" opacity="0.025"/>
  </g>
  <rect x="1" y="1" width="1278" height="418" rx="22"
        fill="none" stroke="#2c4058"/>

  <g stroke="{CREAM}" stroke-opacity="0.22" stroke-width="1.5" fill="none">
    <path d="M26 48V26H48"/>
    <path d="M1232 26H1254V48"/>
    <path d="M26 372V394H48"/>
    <path d="M1254 372V394H1232"/>
  </g>

  <text x="1208" y="52" text-anchor="end"
        font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="11"
        letter-spacing="3" fill="#7d8ea4">LAB 01 / HEADERS</text>

  <line x1="72" y1="86" x2="98" y2="86" stroke="{CREAM}" stroke-opacity="0.5"/>
  <text x="110" y="91" font-family="Fira Code, DejaVu Sans Mono, monospace"
        font-size="15" letter-spacing="7" fill="{NAVY_DIM}">LOCAL-FIRST SECURITY LABORATORY</text>

  <text x="70" y="212" font-family="Fira Code, DejaVu Sans Mono, monospace"
        font-size="94" font-weight="700" letter-spacing="2" fill="{CREAM}">STYX-LAB</text>

  <text x="72" y="252" font-family="Fira Code, DejaVu Sans Mono, monospace"
        font-size="18" fill="{TEXT}">HTTP security headers &#183; graded findings &#183; evidence reports</text>

  <g font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="12">
    <rect x="72" y="286" width="146" height="32" rx="16"
          fill="#0f1d2f" fill-opacity="0.72" stroke="#2c4058"/>
    <circle cx="92" cy="302" r="3.5" fill="#7fc8a0"/>
    <text x="104" y="306" fill="#d8d0be">secure</text>
    <text x="204" y="306" text-anchor="end" fill="#7c8a9e">8766</text>

    <rect x="230" y="286" width="158" height="32" rx="16"
          fill="#0f1d2f" fill-opacity="0.72" stroke="#2c4058"/>
    <circle cx="250" cy="302" r="3.5" fill="#93a0b4"/>
    <text x="262" y="306" fill="#d8d0be">baseline</text>
    <text x="374" y="306" text-anchor="end" fill="#7c8a9e">8765</text>

    <rect x="400" y="286" width="136" height="32" rx="16"
          fill="#0f1d2f" fill-opacity="0.72" stroke="#2c4058"/>
    <circle cx="420" cy="302" r="3.5" fill="{WARN}"/>
    <text x="432" y="306" fill="#d8d0be">weak</text>
    <text x="522" y="306" text-anchor="end" fill="#7c8a9e">8767</text>
  </g>

  <g font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="12.5" fill="#8fa0b5">
    <text x="72" y="370">5 headers</text>
    <text x="148" y="370" fill="#51627a">&#183;</text>
    <text x="164" y="370">9 checks</text>
    <text x="238" y="370" fill="#51627a">&#183;</text>
    <text x="254" y="370">0 external hosts</text>
  </g>

  <line x1="72" y1="394" x2="1208" y2="394" stroke="url(#fade)"/>

  <image x="966" y="52" width="228" height="226"
         href="data:image/png;base64,{mark}"/>

  <rect x="966" y="294" width="228" height="30" rx="15"
        fill="#0f1d2f" fill-opacity="0.72" stroke="#2c4058"/>
  <text x="1080" y="313" text-anchor="middle"
        font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="11"
        letter-spacing="1.5" fill="#a9b6c8">127.0.0.1 only</text>
  <text x="1080" y="350" text-anchor="middle"
        font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="10"
        letter-spacing="1" fill="#6f8198">no external hosts contacted</text>
  <text x="1080" y="378" text-anchor="middle"
        font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="11"
        letter-spacing="1" fill="#7d8ea4">v1.1.0</text>

  <line x1="890" y1="56" x2="890" y2="368" stroke="{CREAM}" stroke-opacity="0.10"
        stroke-dasharray="2 7"/>
</svg>
"""
    (ASSETS / "hero.svg").write_text(svg, encoding="utf-8")


def build_pipeline():
    nodes = [
        ("PROFILE", "secure / baseline / weak"),
        ("SERVE", "127.0.0.1 only"),
        ("INSPECT", "headers + health"),
        ("ASSESS", "9 checks + grading"),
        ("REPORT", "JSON + Markdown"),
    ]
    width, gap, left, top, height = 196, 36, 72, 88, 88
    parts = []
    for index, (title, sub) in enumerate(nodes):
        x = left + index * (width + gap)
        begin = f"{index * 1.2:.1f}s"
        parts.append(
            f'<g>'
            f'<rect x="{x}" y="{top}" width="{width}" height="{height}" rx="12" '
            f'fill="#0f1d2f" fill-opacity="0.72" stroke="{NAVY_EDGE}"/>'
            f'<rect x="{x}" y="{top}" width="{width}" height="{height}" rx="12" '
            f'fill="none" stroke="{CREAM}" stroke-opacity="0.25">'
            f'<animate attributeName="stroke-opacity" values="0.18;0.85;0.18" '
            f'dur="6s" begin="{begin}" repeatCount="indefinite"/></rect>'
            f'<text x="{x + 16}" y="{top + 22}" '
            f'font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="9" '
            f'letter-spacing="1" fill="#6f8198">0{index + 1}</text>'
            f'<text x="{x + width / 2}" y="{top + 44}" text-anchor="middle" '
            f'font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="16" '
            f'letter-spacing="3" fill="{CREAM}">{title}</text>'
            f'<text x="{x + width / 2}" y="{top + 68}" text-anchor="middle" '
            f'font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="10" '
            f'fill="{NAVY_DIM}">{sub}</text>'
            f'</g>'
        )
        if index < len(nodes) - 1:
            x1 = x + width + 6
            x2 = x + width + gap - 6
            y = top + height / 2
            parts.append(
                f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" '
                f'stroke="{CREAM}" stroke-opacity="0.30"/>'
                f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" '
                f'stroke="{CREAM}" stroke-opacity="0.70" stroke-dasharray="4 4">'
                f'<animate attributeName="stroke-dashoffset" values="8;0" '
                f'dur="1.1s" repeatCount="indefinite"/></line>'
                f'<path d="M{x2} {y} l-4 -2.5 v5 z" fill="{CREAM}" fill-opacity="0.65"/>'
            )
    dots = "".join(
        f'<circle cx="{left}" cy="{top + height / 2}" r="3" fill="{CREAM}" opacity="0.9">'
        f'<animateMotion dur="7s" begin="{i * 1.4:.1f}s" repeatCount="indefinite" '
        f'path="M{left} {top + height / 2} H{left + 4 * (width + gap) + width}"/></circle>'
        for i in range(2)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="260"
     viewBox="0 0 1280 260" role="img" aria-label="STYX-LAB assessment pipeline">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1a2d46"/>
      <stop offset="0.55" stop-color="#122235"/>
      <stop offset="1" stop-color="#0b1624"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#1e3350" stroke-width="1"/>
    </pattern>
    <clipPath id="card"><rect x="1" y="1" width="1278" height="258" rx="22"/></clipPath>
  </defs>
  <rect x="1" y="1" width="1278" height="258" rx="22" fill="url(#bg)"/>
  <g clip-path="url(#card)">
    <rect width="1280" height="260" fill="url(#grid)" opacity="0.45"/>
  </g>
  <rect x="1" y="1" width="1278" height="258" rx="22" fill="none" stroke="#2c4058"/>

  <text x="72" y="50" font-family="Fira Code, DejaVu Sans Mono, monospace"
        font-size="13" letter-spacing="6" fill="{NAVY_DIM}">ASSESSMENT PIPELINE</text>
  <text x="1208" y="50" text-anchor="end"
        font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="10"
        letter-spacing="2" fill="#6f8198">9 CHECKS &#183; 5 HEADERS</text>
  {''.join(parts)}
  {dots}
  <text x="72" y="222" font-family="Fira Code, DejaVu Sans Mono, monospace"
        font-size="12" letter-spacing="1" fill="#7d8ea4">loopback only &#183; no external hosts contacted</text>
  <text x="1208" y="222" text-anchor="end"
        font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="11"
        letter-spacing="1" fill="#6f8198">v1.1.0</text>
</svg>
"""
    (ASSETS / "pipeline.svg").write_text(svg, encoding="utf-8")


def build_divider():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="28"
     viewBox="0 0 1280 28" role="img" aria-label="">
  <defs>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#8b949e" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#8b949e" stop-opacity="0.8"/>
      <stop offset="1" stop-color="#8b949e" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <line x1="0" y1="14" x2="614" y2="14" stroke="url(#fade)" stroke-width="1.2"/>
  <line x1="666" y1="14" x2="1280" y2="14" stroke="url(#fade)" stroke-width="1.2"/>
  <rect x="634" y="8" width="12" height="12" transform="rotate(45 640 14)"
        fill="none" stroke="#8b949e" stroke-opacity="0.95"/>
</svg>
"""
    (ASSETS / "divider.svg").write_text(svg, encoding="utf-8")


def main():
    ASSETS.mkdir(exist_ok=True)
    build_mark()
    build_hero()
    build_pipeline()
    build_divider()
    lines = transcript()
    frames, durations = build_gif(lines)
    build_mp4(frames, durations)
    print(f"hero.svg, pipeline.svg, demo.gif ({len(frames)} frames), demo.mp4")


if __name__ == "__main__":
    main()
