"""Render a concise, reproducible hackathon demo video from verified project facts."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts"
WIDTH, HEIGHT = 1920, 1080
BG = "#07111f"
PANEL = "#101f33"
TEXT = "#f4f7fb"
MUTED = "#a9b8ca"
CYAN = "#48d7d0"
AMBER = "#ffbd59"
RED = "#ff6b6b"
GREEN = "#66db8b"


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        name = "CascadiaMono.ttf"
    elif bold:
        name = "segoeuib.ttf"
    else:
        name = "segoeui.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int,
            fill: str = TEXT, size: int = 42, spacing: int = 16, bold: bool = False) -> int:
    words = text.split()
    lines: list[str] = []
    current = ""
    face = font(size, bold=bold)
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=face) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += size + spacing
    return y


def base(kicker: str, title: str, number: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((70, 55, 1850, 1025), radius=34, fill=PANEL)
    draw.rectangle((70, 55, 86, 1025), fill=CYAN)
    draw.text((130, 105), kicker.upper(), font=font(28, bold=True), fill=CYAN)
    draw.text((130, 158), title, font=font(70, bold=True), fill=TEXT)
    draw.text((1725, 105), number, font=font(28, bold=True), fill=MUTED)
    return image, draw


def save_slide(index: int, kicker: str, title: str, body: list[tuple[str, str]],
               duration: int) -> tuple[Path, int]:
    image, draw = base(kicker, title, f"{index:02d}")
    y = 315
    for text, color in body:
        y = wrapped(draw, text, (145, y), 1550, fill=color, size=44, spacing=18)
        y += 35
    path = OUT / f"slide-{index:02d}.png"
    image.save(path)
    return path, duration


def architecture_slide(index: int, duration: int) -> tuple[Path, int]:
    image, draw = base("How it works", "Evidence before effort", f"{index:02d}")
    labels = [
        ("Lead", "Aggregator or URL"),
        ("Strands agent", "Plans verification"),
        ("Safe tools", "Reads original source"),
        ("Hard gates", "Explains pursue / reject"),
    ]
    x_positions = [130, 560, 990, 1420]
    for i, ((head, sub), x) in enumerate(zip(labels, x_positions, strict=True)):
        draw.rounded_rectangle((x, 390, x + 330, 680), radius=24, fill="#162b45", outline=CYAN, width=3)
        draw.text((x + 28, 445), head, font=font(36, bold=True), fill=TEXT)
        wrapped(draw, sub, (x + 28, 520), 270, fill=MUTED, size=28, spacing=10)
        if i < len(labels) - 1:
            draw.line((x + 340, 535, x + 405, 535), fill=AMBER, width=8)
            draw.polygon([(x + 405, 535), (x + 382, 520), (x + 382, 550)], fill=AMBER)
    draw.text((145, 800), "Reward size never overrides missing evidence.", font=font(46, bold=True), fill=AMBER)
    path = OUT / f"slide-{index:02d}.png"
    image.save(path)
    return path, duration


def terminal_slide(index: int, duration: int) -> tuple[Path, int]:
    image, draw = base("Live agent", "A real tool call, running locally", f"{index:02d}")
    draw.rounded_rectangle((130, 310, 1790, 855), radius=22, fill="#04090f", outline="#294560", width=3)
    terminal = [
        ("> opportunity-compass Inspect https://agentsforhumans.devpost.com/", CYAN),
        ("", TEXT),
        ("HTTP status: 200", GREEN),
        ("Page title: Agents for Humans Hackathon", TEXT),
        ("Deadline evidence: Sep 14, 2026 @ 5:00pm PDT", AMBER),
    ]
    y = 375
    for line, color in terminal:
        draw.text((185, y), line, font=font(31, mono=True), fill=color)
        y += 78
    draw.text((145, 920), "Strands Agents SDK  •  Ollama  •  zero API spend", font=font(34, bold=True), fill=MUTED)
    path = OUT / f"slide-{index:02d}.png"
    image.save(path)
    return path, duration


def main() -> None:
    OUT.mkdir(exist_ok=True)
    slides = [
        save_slide(1, "Opportunity Compass", "Stop chasing phantom rewards", [
            ("Online opportunities advertise money. The original source often tells a different story.", TEXT),
            ("Our agent verifies first—before a human spends hours.", CYAN),
        ], 10),
        save_slide(2, "The problem", "$1,500 can still be worth $0", [
            ("A bounty aggregator showed a $1,500 reward.", AMBER),
            ("The original GitHub issue was deleted. That single fact should end the chase.", RED),
        ], 10),
        architecture_slide(3, 12),
        terminal_slide(4, 13),
        save_slide(5, "Safety by design", "Conservative, bounded, auditable", [
            ("HTTPS-only fetching • private-network rejection • every redirect revalidated", TEXT),
            ("Bounded response size • inert HTML parsing • no security testing", TEXT),
            ("Unknown stays unknown.", CYAN),
        ], 12),
        save_slide(6, "Hard gates", "The model cannot talk its way around evidence", [
            ("Deleted source → reject", RED),
            ("Closed or expired → reject", RED),
            ("Entry fee in zero-cost mode → reject", RED),
            ("AI assistance prohibited → reject", RED),
        ], 12),
        save_slide(7, "Verified", "Built to be reproduced", [
            ("10 automated tests passing • Ruff clean • MIT licensed", GREEN),
            ("Public-source evidence and an explainable score for every decision.", TEXT),
        ], 10),
        save_slide(8, "Why it matters", "Protect the resource you cannot earn back", [
            ("Opportunity Compass saves people something scarcer than an advertised reward:", TEXT),
            ("their time.", CYAN),
        ], 10),
    ]
    concat = OUT / "slides.txt"
    lines: list[str] = []
    for path, duration in slides:
        lines.extend([f"file '{path.as_posix()}'", f"duration {duration}"])
    lines.append(f"file '{slides[-1][0].as_posix()}'")
    concat.write_text("\n".join(lines), encoding="utf-8")

    ffmpeg = next((Path.home() / "AppData/Local/Microsoft/WinGet/Packages").rglob("ffmpeg.exe"))
    target = OUT / "opportunity-compass-demo.mp4"
    subprocess.run([
        str(ffmpeg), "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium",
        "-crf", "20", "-movflags", "+faststart", str(target),
    ], check=True)
    print(target)


if __name__ == "__main__":
    main()
