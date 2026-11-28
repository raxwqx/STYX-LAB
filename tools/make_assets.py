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


def frame(lines, cursor=True, inline=False):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (12, 12, WIDTH - 12, HEIGHT - 12), radius=14, fill=PANEL, outline=EDGE
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
    return image


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
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="400"
     viewBox="0 0 1280 400" role="img" aria-label="STYX-LAB">
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="{NAVY_GRID}" stroke-width="1"/>
    </pattern>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{CREAM}" stop-opacity="0.50"/>
      <stop offset="0.6" stop-color="{CREAM}" stop-opacity="0.10"/>
      <stop offset="1" stop-color="{CREAM}" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.80" cy="0.45" r="0.5">
      <stop offset="0" stop-color="{CREAM}" stop-opacity="0.07"/>
      <stop offset="1" stop-color="{CREAM}" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="1280" height="400" fill="{NAVY}"/>
  <rect width="1280" height="400" fill="url(#grid)"/>
  <rect width="1280" height="400" fill="url(#glow)"/>
  <rect width="1280" height="2" fill="url(#fade)"/>

  <image x="952" y="76" width="252" height="250"
         href="data:image/png;base64,{mark}"/>

  <text x="80" y="114" font-family="Fira Code, DejaVu Sans Mono, monospace"
        font-size="16" letter-spacing="7.5" fill="{NAVY_DIM}">LOCAL-FIRST SECURITY LABORATORY</text>

  <text x="78" y="236" font-family="Fira Code, DejaVu Sans Mono, monospace"
        font-size="92" font-weight="700" letter-spacing="2" fill="{CREAM}">STYX-LAB</text>

  <line x1="80" y1="272" x2="700" y2="272" stroke="{NAVY_EDGE}"/>

  <text x="80" y="314" font-family="Fira Code, DejaVu Sans Mono, monospace"
        font-size="19" fill="{TEXT}">HTTP security headers &#183; graded findings &#183; evidence reports</text>

  <g font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="14" fill="{NAVY_DIM}">
    <text x="80" y="356">3 profiles</text>
    <text x="232" y="356">9 checks</text>
    <text x="376" y="356">8 findings</text>
    <text x="552" y="356">0 external hosts</text>
  </g>

  <g font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="13">
    <rect x="760" y="340" width="78" height="22" rx="11"
          fill="none" stroke="{NAVY_EDGE}"/>
    <text x="799" y="355" text-anchor="middle" fill="{NAVY_DIM}">v1.1.0</text>
  </g>
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
    width, gap, left, top, height = 196, 36, 80, 92, 84
    parts = []
    for index, (title, sub) in enumerate(nodes):
        x = left + index * (width + gap)
        begin = f"{index * 1.2:.1f}s"
        parts.append(
            f'<g>'
            f'<rect x="{x}" y="{top}" width="{width}" height="{height}" rx="10" '
            f'fill="{PANEL}" stroke="{NAVY_EDGE}"/>'
            f'<rect x="{x}" y="{top}" width="{width}" height="{height}" rx="10" '
            f'fill="none" stroke="{CREAM}" stroke-opacity="0.25">'
            f'<animate attributeName="stroke-opacity" values="0.18;0.85;0.18" '
            f'dur="6s" begin="{begin}" repeatCount="indefinite"/></rect>'
            f'<text x="{x + width / 2}" y="{top + 34}" text-anchor="middle" '
            f'font-family="Fira Code, DejaVu Sans Mono, monospace" font-size="16" '
            f'letter-spacing="3" fill="{CREAM}">{title}</text>'
            f'<text x="{x + width / 2}" y="{top + 58}" text-anchor="middle" '
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
                f'stroke="{CREAM}" stroke-opacity="0.55" stroke-dasharray="4 4">'
                f'<animate attributeName="stroke-dashoffset" values="8;0" '
                f'dur="1.1s" repeatCount="indefinite"/></line>'
            )
    dots = "".join(
        f'<circle cx="{left}" cy="{top + height / 2}" r="3" fill="{CREAM}" opacity="0.9">'
        f'<animateMotion dur="7s" begin="{i * 1.4:.1f}s" repeatCount="indefinite" '
        f'path="M{left} {top + height / 2} H{left + 4 * (width + gap) + width}"/></circle>'
        for i in range(2)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="240"
     viewBox="0 0 1280 240" role="img" aria-label="STYX-LAB assessment pipeline">
  <rect width="1280" height="240" fill="{NAVY}"/>
  <text x="80" y="52" font-family="Fira Code, DejaVu Sans Mono, monospace"
        font-size="13" letter-spacing="6" fill="{NAVY_DIM}">ASSESSMENT PIPELINE</text>
  {''.join(parts)}
  {dots}
  <text x="80" y="212" font-family="Fira Code, DejaVu Sans Mono, monospace"
        font-size="12" letter-spacing="1" fill="#7d8ea4">loopback only &#183; no external hosts contacted</text>
</svg>
"""
    (ASSETS / "pipeline.svg").write_text(svg, encoding="utf-8")


def main():
    ASSETS.mkdir(exist_ok=True)
    build_mark()
    build_hero()
    build_pipeline()
    lines = transcript()
    frames, durations = build_gif(lines)
    build_mp4(frames, durations)
    print(f"hero.svg, pipeline.svg, demo.gif ({len(frames)} frames), demo.mp4")


if __name__ == "__main__":
    main()
