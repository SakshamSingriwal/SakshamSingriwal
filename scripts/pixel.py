"""Shared drawing kit for the arcade profile: a 5x7 pixel font, palette and SVG helpers.

Every asset in assets/ is generated from these primitives, so the whole profile reads
as one machine. Text is drawn as vector pixels (no web fonts), which GitHub renders
identically on every device.
"""

from __future__ import annotations

import html

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
BG0 = "#07060F"
BG1 = "#0E0A22"
BG2 = "#171033"
BG3 = "#221A48"
LINE = "#2E2560"
CYAN = "#2DE2E6"
PINK = "#FF3CAC"
AMBER = "#FFD23F"
LIME = "#7CFF6B"
VIOLET = "#9B5CFF"
ORANGE = "#FF8A3D"
TEXT = "#ECE9FF"
MUTED = "#9A94C7"
DIM = "#5B5490"

MONO = ("'JetBrains Mono','Cascadia Mono','Cascadia Code','SF Mono',SFMono-Regular,"
        "Consolas,'Liberation Mono',Menlo,monospace")

# ---------------------------------------------------------------------------
# 5x7 pixel font
# ---------------------------------------------------------------------------
_B = "....."
FONT: dict[str, list[str]] = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [_B] * 7,
    ".": [_B, _B, _B, _B, _B, _B, "..#.."],
    ",": [_B, _B, _B, _B, _B, "..#..", ".#..."],
    "-": [_B, _B, _B, ".###.", _B, _B, _B],
    "_": [_B, _B, _B, _B, _B, _B, "#####"],
    ":": [_B, "..#..", _B, _B, _B, "..#..", _B],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", _B, "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", _B, "..#.."],
    ">": ["#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."],
    "<": ["....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "+": [_B, "..#..", "..#..", "#####", "..#..", "..#..", _B],
    "'": ["..#..", "..#..", _B, _B, _B, _B, _B],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "·": [_B, _B, _B, "..#..", _B, _B, _B],
    "×": [_B, "#...#", ".#.#.", "..#..", ".#.#.", "#...#", _B],
    "→": [_B, "..#..", "...#.", "#####", "...#.", "..#..", _B],
    "▶": ["#....", "##...", "###..", "####.", "###..", "##...", "#...."],
    "◀": ["....#", "...##", "..###", ".####", "..###", "...##", "....#"],
    "▼": [_B, "#####", "#####", ".###.", ".###.", "..#..", _B],
    "♥": [_B, ".#.#.", "#####", "#####", ".###.", "..#..", _B],
    "★": ["..#..", "..#..", "#####", ".###.", ".###.", "##.##", "#...#"],
}


def num(v: float) -> str:
    """Compact number for SVG attributes."""
    r = round(v, 2)
    return str(int(r)) if r == int(r) else f"{r:g}"


def text_width(text: str, s: float, spacing: float = 1) -> float:
    n = len(text)
    return 0 if n == 0 else n * (5 + spacing) * s - spacing * s


def glyph_path(text: str, x: float, y: float, s: float, spacing: float = 1) -> str:
    """Path data drawing `text` in the pixel font; each run of pixels becomes one rect."""
    d: list[str] = []
    cx = x
    for ch in text.upper():
        rows = FONT.get(ch, FONT["?"])
        for r, row in enumerate(rows):
            c = 0
            while c < 5:
                if row[c] == "#":
                    start = c
                    while c < 5 and row[c] == "#":
                        c += 1
                    w = (c - start) * s
                    d.append(f"M{num(cx + start * s)} {num(y + r * s)}h{num(w)}v{num(s)}h{num(-w)}z")
                else:
                    c += 1
        cx += (5 + spacing) * s
    return "".join(d)


def ptext(text: str, x: float, y: float, s: float, fill: str, anchor: str = "start",
          spacing: float = 1, attrs: str = "") -> str:
    """Pixel text. (x, y) is the top-left (or top-centre / top-right with anchor)."""
    w = text_width(text, s, spacing)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    return f'<path d="{glyph_path(text, x, y, s, spacing)}" fill="{fill}" {attrs}/>'


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def mono(text: str, x: float, y: float, size: float, fill: str, anchor: str = "start",
         weight: int = 400, attrs: str = "") -> str:
    return (f'<text x="{num(x)}" y="{num(y)}" font-family="{MONO}" font-size="{num(size)}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {attrs}>{esc(text)}</text>')


def wrap(text: str, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# The CRT "screen" every asset is drawn on
# ---------------------------------------------------------------------------
BASE_CSS = """
@keyframes blink{0%,55%{opacity:1}56%,100%{opacity:0}}
@keyframes twinkle{0%,100%{opacity:.15}50%{opacity:1}}
@keyframes sweep{0%{transform:translateY(-120px)}100%{transform:translateY(var(--h))}}
@keyframes pulse{0%,100%{opacity:.55}50%{opacity:1}}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.blink{animation:blink 1.1s steps(1) infinite}
.pulse{animation:pulse 2.4s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def svg_open(w: int, h: int, label: str, css: str = "", defs: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(label)}"><title>{esc(label)}</title>'
        f"<style>{BASE_CSS}{css}</style>"
        "<defs>"
        f'<clipPath id="clip"><rect width="{w}" height="{h}" rx="18"/></clipPath>'
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG1}"/>'
        f'<stop offset="1" stop-color="{BG0}"/></linearGradient>'
        '<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/>'
        f'<stop offset="1" stop-color="{PINK}"/></linearGradient>'
        '<radialGradient id="vig" cx=".5" cy=".5" r=".75">'
        '<stop offset=".6" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>'
        '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="1.2" fill="#000" opacity=".32"/></pattern>'
        '<linearGradient id="band" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".045"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        '<filter id="glow" x="-20%" y="-60%" width="140%" height="220%">'
        '<feGaussianBlur stdDeviation="3.5" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="8"/></filter>'
        f"{defs}</defs>"
        f'<g clip-path="url(#clip)"><rect width="{w}" height="{h}" fill="url(#bg)"/>'
    )


def svg_close(w: int, h: int) -> str:
    """CRT finish: scanlines, a slow refresh band, vignette and a neon bezel."""
    return (
        f'<rect width="{w}" height="{h}" fill="url(#scan)"/>'
        f'<rect width="{w}" height="120" fill="url(#band)" style="--h:{h + 120}px;'
        f'animation:sweep 7s linear infinite"/>'
        f'<rect width="{w}" height="{h}" fill="url(#vig)"/>'
        "</g>"
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="17" fill="none" '
        'stroke="url(#edge)" stroke-width="2" opacity=".9"/>'
        f'<rect x="5" y="5" width="{w - 10}" height="{h - 10}" rx="14" fill="none" '
        f'stroke="{LINE}" stroke-width="1" opacity=".6"/>'
        "</svg>"
    )


def corners(x: float, y: float, w: float, h: float, color: str, size: float = 14,
            t: float = 3) -> str:
    """Pixel corner brackets, the arcade 'selected' frame."""
    s, out = size, []
    for cx, cy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        hx = cx if dx > 0 else cx - s
        vy = cy if dy > 0 else cy - s
        out.append(f'<rect x="{num(hx)}" y="{num(cy if dy > 0 else cy - t)}" width="{num(s)}" height="{num(t)}"/>')
        out.append(f'<rect x="{num(cx if dx > 0 else cx - t)}" y="{num(vy)}" width="{num(t)}" height="{num(s)}"/>')
    return f'<g fill="{color}">{"".join(out)}</g>'


# ---------------------------------------------------------------------------
# Player sprite (16 x 17), drawn pixel by pixel
# ---------------------------------------------------------------------------
SPRITE = [
    ".....KKKKKK.....",
    "....KHHHHHHK....",
    "...KHHHHHHHHK...",
    "..MKHHHHHHHHKM..",
    "..MKHHSSSSHHKM..",
    "..MKSSESSESSKM..",
    "..MKSSSSSSSSKM..",
    "...KSSSssSSSK...",
    "....KSSSSSSK....",
    ".....KKSSKK.....",
    "...KKCCCCCCKK...",
    "..KCCCCMMCCCCK..",
    ".KCCcCCCCCCcCCK.",
    ".KCCcKKKKKKcCCK.",
    ".KSSKLLLLLLKSSK.",
    ".KKKKLLllLLKKKK.",
    "....KKKKKKKK....",
]
SPRITE_COLORS = {
    "K": "#140B24", "H": "#2B1B3D", "S": "#C68642", "s": "#9E6230", "E": "#140B24",
    "M": PINK, "C": CYAN, "c": "#159CA6", "L": "#8F96B8", "l": LIME,
}


def sprite(x: float, y: float, px: float) -> str:
    """The player character at (x, y), `px` units per pixel, grouped by colour."""
    by_color: dict[str, list[str]] = {}
    for r, row in enumerate(SPRITE):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == ch:
                c += 1
            w = (c - start) * px
            by_color.setdefault(SPRITE_COLORS[ch], []).append(
                f"M{num(x + start * px)} {num(y + r * px)}h{num(w)}v{num(px)}h{num(-w)}z")
    return "".join(f'<path d="{"".join(d)}" fill="{col}"/>' for col, d in by_color.items())


SPRITE_W, SPRITE_H = 16, 17
