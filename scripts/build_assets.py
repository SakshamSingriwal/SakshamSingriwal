"""Builds every static SVG in assets/.  Run:  python scripts/build_assets.py

The live scoreboard is built separately by scripts/scoreboard.py inside GitHub Actions.
"""

from __future__ import annotations

import html
import re
import random
import sys
from pathlib import Path

from pixel import (AMBER, BG0, BG1, BG2, BG3, CYAN, DIM, LIME, LINE, MONO, MUTED, ORANGE, PINK,
                   SPRITE_H, SPRITE_W, TEXT, VIOLET, corners, esc, mono, num, ptext, sprite,
                   svg_close, svg_open, text_width, wrap)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
W = 1280

# Each panel's accessible label. It is also the alt text of the panel's <img> in README.md, word for
# word; check_readme() at the end of the build fails if the two drift apart.
ALT = {
    "hero.svg": "Saksham Singriwal, Forward Deployed Engineer at NOVIXO AI. Press start.",
    "player.svg": "Player select: Saksham Singriwal. Class: Forward Deployed Engineer. Guild: NOVIXO AI. "
                  "Base: New Delhi, India. Origin: founder of three 24x7 gaming cafés.",
    "stages.svg": "How I work. 1, Understand: sit with the people who do the work and the people who pay for it, "
                  "and turn a loose need into requirements, a data model and a plan they sign off. 2, Build: cloud "
                  "services, APIs and integrations, data and AI components, tested, auditable and secure enough for "
                  "a regulated customer to accept. 3, Deliver: deploy, train, measure and iterate with the customer. "
                  "Own the outcome, not the ticket.",
    "products.svg": "NOVIXO Safety product map, all six products complete and online: Case Intake, Literature "
                    "Monitoring, Quality Control, Aggregate Reporting, Submissions and Acknowledgements, and Signal "
                    "Detection and Management.",
    "head-clients.svg": "Side quests: client delivery.",
    "erp.svg": "Bonus level, a product from my own business: a gaming café ERP. I ran the cafés this was built for, "
               "so the requirements came from the floor: one session and billing engine for every table and console, "
               "a live floor view, customers and memberships, a wallet, bookings without clashes, a food and beverage "
               "counter, and separate apps for the owner and for customers. Built with NestJS, PostgreSQL, Prisma, "
               "React, Socket.IO and Docker.",
    "head-open.svg": "Open work: earlier projects from my data science and machine learning work, all public.",
    "card-1.svg": "Sentinel: fraud-risk analytics studio. Python, XGBoost, CatBoost, SHAP, Streamlit.",
    "card-2.svg": "Apex DS: offline analytics platform. Python, AutoGluon, DuckDB, Prophet, Ollama.",
    "card-3.svg": "DS Studio: data science studio for any tabular problem. Python, scikit-learn, Optuna, Streamlit.",
    "card-4.svg": "Galactic Data Forge: guided eleven-step modelling pipeline. Python, scikit-learn, TensorFlow, "
                  "Streamlit.",
    "career.svg": "Career mode: founder and operations manager of StunnShot, three 24x7 gaming cafés (2017 to 2020); "
                  "BCA (2020 to 2023); MBA in Business Analytics and HR (2024 to 2026); HR intern at Engineers India "
                  "Limited (2025); Data Science intern at Spinnaker Analytics (2025); Associate Data Scientist at "
                  "NOVIXO AI (Jan to Oct 2026); now Forward Deployed Engineer at NOVIXO AI (since Oct 2026); next, "
                  "enterprise solution delivery.",
    "achievements.svg": "Education: MBA in Business Analytics and Human Resources (2024 to 2026, grade A) and Bachelor "
                        "of Computer Applications (2020 to 2023, grade A), both at BVIMR, Bharati Vidyapeeth "
                        "University, offline. Certifications: Diploma in Data Science and Diploma in Artificial "
                        "Intelligence, Boston Institute of Analytics, offline; Business Analytics Plus, IMS Proschool "
                        "(2026), offline; Business Analytics Specialization, Wharton Online, University of "
                        "Pennsylvania, online; Forward Deployed Engineering programme, NeuraPath Academy, offline.",
    "inventory.svg": "Toolbox. Languages and data: Python, TypeScript, SQL, PostgreSQL, DynamoDB. Cloud and delivery: "
                     "AWS Lambda, API Gateway, S3, Cognito, CDK, Bedrock, Vercel, Docker, continuous integration. "
                     "Applications: React, Next.js, NestJS, FastAPI, Hono, REST APIs, webhooks, role-based access, "
                     "audit trails. Data and AI: machine learning, model explainability, forecasting, language-model "
                     "applications with retrieval, evaluation and guardrails. With customers: requirements, solution "
                     "design, demos, training, documentation, stakeholder management.",
    "footer.svg": "Thanks for playing. Open to conversations about forward deployed engineering, solutions "
                  "engineering and enterprise AI delivery.",
    "btn-linkedin.svg": "LinkedIn",
    "btn-email.svg": "Email sakshamsingriwal1997@gmail.com",
    "btn-github.svg": "GitHub repositories",
}

MONO_ADVANCE = 0.6  # width of one monospace character, in em (JetBrains Mono, SF Mono and Menlo are 0.6)


def mono_width(text: str, size: float) -> float:
    return len(text) * size * MONO_ADVANCE


def fits(text: str, size: float, room: float, where: str) -> None:
    """Stop the build if a line of monospace text would run out of its box."""
    if mono_width(text, size) > room:
        sys.exit(f"overflow in {where}: {text!r} needs {mono_width(text, size):.0f}px, has {room:.0f}px")


def check_readme() -> None:
    """Every README image of a panel must carry that panel's label, word for word, as its alt text."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    seen, bad = set(), []
    for src, alt in re.findall(r'<img src="assets/([^"]+)"[^>]*?alt="([^"]*)"', readme):
        seen.add(src)
        if ALT.get(src) != html.unescape(alt):
            bad.append(src)
    bad += [name for name in ALT if name not in seen]
    if bad:
        sys.exit("README alt text and SVG label differ for: " + ", ".join(sorted(set(bad))))
    print("  README alt text matches every panel label")


def save(name: str, svg: str) -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(svg, encoding="utf-8")
    print(f"  {name:<24} {len(svg) / 1024:6.1f} KB")


def chip(x: float, y: float, label: str, color: str, size: float = 13, pad: float = 12,
         filled: bool = False) -> tuple[str, float]:
    w = len(label) * size * 0.62 + pad * 2
    h = size + 13
    fill = color if filled else BG2
    txt = BG0 if filled else TEXT
    svg = (f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="4" fill="{fill}" '
           f'stroke="{color}" stroke-width="1.4" stroke-opacity=".85"/>'
           f'<rect x="{num(x + 7)}" y="{num(y + h / 2 - 2.5)}" width="5" height="5" fill="{color if not filled else BG0}"/>'
           + mono(label, x + pad + 7, y + h / 2 + size * 0.36, size, txt, weight=600 if filled else 500))
    return svg, w + 7


# ---------------------------------------------------------------------------
# 1. Hero: the attract screen
# ---------------------------------------------------------------------------
def hero() -> None:
    H, HORIZON = 500, 352
    rnd = random.Random(7)
    css = """
@keyframes glitchA{0%,92%,100%{transform:translate(-3px,0)}93%{transform:translate(-11px,2px)}95%{transform:translate(6px,-2px)}97%{transform:translate(-3px,0)}}
@keyframes glitchB{0%,92%,100%{transform:translate(3px,0)}93%{transform:translate(10px,-2px)}95%{transform:translate(-7px,2px)}97%{transform:translate(3px,0)}}
@keyframes win{0%,100%{opacity:.25}50%{opacity:1}}
.ga{animation:glitchA 6s steps(1) infinite;mix-blend-mode:screen}
.gb{animation:glitchB 6s steps(1) infinite;mix-blend-mode:screen}
"""
    defs = (
        f'<linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/>'
        f'<stop offset=".46" stop-color="#C9F7FF"/><stop offset=".54" stop-color="#FF7AD9"/>'
        f'<stop offset="1" stop-color="{AMBER}"/></linearGradient>'
        f'<radialGradient id="sky" cx=".5" cy="1" r=".7"><stop offset="0" stop-color="{PINK}" stop-opacity=".38"/>'
        f'<stop offset=".5" stop-color="{VIOLET}" stop-opacity=".12"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="floorfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".35" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff"/></linearGradient>'
        f'<mask id="fm"><rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="url(#floorfade)"/></mask>'
    )
    p = [svg_open(W, H, ALT["hero.svg"], css, defs)]
    p.append(f'<rect y="{HORIZON - 260}" width="{W}" height="260" fill="url(#sky)"/>')

    # starfield
    stars = []
    for _ in range(110):
        x, y = rnd.uniform(14, W - 14), rnd.uniform(14, HORIZON - 70)
        s = rnd.choice((2, 2, 2, 3))
        col = rnd.choice((TEXT, TEXT, TEXT, CYAN, PINK, AMBER))
        dur, delay = rnd.uniform(2.2, 5.5), rnd.uniform(-5, 0)
        stars.append(f'<rect x="{num(x)}" y="{num(y)}" width="{s}" height="{s}" fill="{col}" '
                     f'style="animation:twinkle {dur:.1f}s ease-in-out {delay:.1f}s infinite"/>')
    p.append("".join(stars))

    # skyline on the horizon, a few windows lit
    x, bld, wins = 0, [], []
    while x < W:
        bw = rnd.choice((26, 34, 42, 50, 58))
        bh = rnd.choice((18, 26, 34, 44, 56, 70))
        if 470 < x < 810:  # keep the centre low so the tagline breathes
            bh = rnd.choice((10, 14, 18))
        bld.append(f"M{x} {HORIZON}v{-bh}h{bw}v{bh}z")
        for wy in range(HORIZON - bh + 6, HORIZON - 6, 9):
            for wx in range(x + 5, x + bw - 6, 9):
                if rnd.random() < 0.16:
                    col = rnd.choice((AMBER, AMBER, CYAN, PINK))
                    wins.append(f'<rect x="{wx}" y="{wy}" width="3" height="3" fill="{col}" '
                                f'style="animation:win {rnd.uniform(2, 7):.1f}s steps(2) {rnd.uniform(-6, 0):.1f}s infinite"/>')
        x += bw + rnd.choice((0, 2, 4))
    p.append(f'<path d="{"".join(bld)}" fill="#120B2B"/>' + "".join(wins))

    # neon floor
    p.append(f'<rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="{BG0}"/>')
    floor = []
    for k in range(-14, 15):
        floor.append(f'<line x1="{W / 2}" y1="{HORIZON}" x2="{num(W / 2 + k * 150)}" y2="{H}"/>')
    for k in range(7):
        floor.append(
            f'<line x1="0" x2="{W}" y1="{HORIZON}" y2="{HORIZON}">'
            f'<animate attributeName="y1" values="{HORIZON};{H + 4}" dur="3.5s" begin="{-k * 0.5}s" '
            f'repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines=".55 0 1 1"/>'
            f'<animate attributeName="y2" values="{HORIZON};{H + 4}" dur="3.5s" begin="{-k * 0.5}s" '
            f'repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines=".55 0 1 1"/></line>')
    p.append(f'<g mask="url(#fm)" stroke="{PINK}" stroke-width="1.6" opacity=".55">{"".join(floor)}</g>')
    p.append(f'<rect y="{HORIZON - 1}" width="{W}" height="2" fill="{PINK}" filter="url(#glow)"/>')

    # HUD
    hud = [("1UP", "FDE", 70, "start", PINK, True), ("NOW PLAYING", "NOVIXO AI", W / 2, "middle", AMBER, False),
           ("CREDITS", "03 CAFES", W - 70, "end", CYAN, False)]
    for label, value, hx, anchor, col, blinking in hud:
        cls = 'class="blink"' if blinking else ""
        p.append(ptext(label, hx, 34, 2.4, col, anchor, attrs=cls))
        p.append(ptext(value, hx, 58, 2.4, TEXT, anchor))

    # name with chromatic aberration
    name, s = "SAKSHAM SINGRIWAL", 9
    p.append(f'<g opacity=".75"><g class="ga">{ptext(name, W / 2, 112, s, CYAN, "middle")}</g>'
             f'<g class="gb">{ptext(name, W / 2, 112, s, PINK, "middle")}</g></g>')
    p.append(ptext(name, W / 2, 112, s, "url(#chrome)", "middle", attrs='filter="url(#glow)"'))
    p.append(ptext("FORWARD DEPLOYED ENGINEER", W / 2, 204, 3.2, CYAN, "middle", spacing=1.6,
                   attrs='filter="url(#glow)"'))

    # typed taglines
    lines = ["customer problem → technical solution → business outcome",
             "from three 24×7 gaming cafés to enterprise AI",
             "drug-safety software, built for regulated customers",
             "own the outcome, not the ticket"]
    size, cw, slot = 19, 19 * 0.6, 4.5
    total = slot * len(lines)
    ty = 268
    for i, line in enumerate(lines):
        full = "> " + line
        n = len(full)
        tw = n * cw
        x0 = W / 2 - tw / 2
        t0 = i * slot
        times, widths = [0.0], [0.0]
        type_dur = min(2.2, n * 0.045)
        for k in range(1, n + 1):
            times.append(t0 + type_dur * k / n)
            widths.append(k * cw)
        times += [t0 + slot - 0.35, t0 + slot - 0.05]
        widths += [tw + 30, 0]
        if t0 > 0:
            times.insert(1, t0)
            widths.insert(1, 0)
        kt = ";".join(f"{t / total:.4f}" for t in times) + (";1" if times[-1] < total else "")
        wv = ";".join(num(w) for w in widths) + (";0" if times[-1] < total else "")
        xv = ";".join(num(x0 + min(w, tw)) for w in widths) + (f";{num(x0)}" if times[-1] < total else "")
        cid = f"t{i}"
        p.append(f'<clipPath id="{cid}"><rect x="{num(x0 - 2)}" y="{ty - 22}" width="0" height="32">'
                 f'<animate attributeName="width" values="{wv}" keyTimes="{kt}" dur="{total}s" '
                 f'calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>')
        p.append(f'<g clip-path="url(#{cid})">'
                 f'<text x="{num(x0)}" y="{ty}" font-family="{MONO}" font-size="{size}" fill="{TEXT}" '
                 f'textLength="{num(tw)}" lengthAdjust="spacingAndGlyphs">'
                 f'<tspan fill="{PINK}">&gt; </tspan>{esc(line)}</text>'
                 f'<rect x="0" y="{ty - 17}" width="11" height="21" fill="{LIME}">'
                 f'<animate attributeName="x" values="{xv}" keyTimes="{kt}" dur="{total}s" '
                 f'calcMode="discrete" repeatCount="indefinite"/></rect></g>')

    # press start
    p.append(f'<rect x="{W / 2 - 170}" y="{H - 82}" width="340" height="46" rx="6" fill="{BG0}" opacity=".7"/>')
    p.append(ptext("PRESS START", W / 2, H - 70, 3.4, AMBER, "middle", attrs='class="blink" filter="url(#glow)"'))
    p.append(ptext("NEW DELHI, INDIA", 40, H - 30, 1.8, DIM))
    p.append(ptext("EST. 2017", W - 40, H - 30, 1.8, DIM, "end"))
    p.append(svg_close(W, H))
    save("hero.svg", "".join(p))


# ---------------------------------------------------------------------------
# 2. Player select
# ---------------------------------------------------------------------------
def player() -> None:
    H = 452
    css = """
@keyframes fill{0%,4%{opacity:.12}12%,90%{opacity:1}100%{opacity:.12}}
@keyframes eyes{0%,94%,100%{opacity:0}95%,98%{opacity:1}}
.bob{animation:bob 1.6s steps(2) infinite}
"""
    defs = (f'<radialGradient id="spot" cx=".5" cy=".35" r=".6"><stop offset="0" stop-color="{CYAN}" stop-opacity=".28"/>'
            f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="nm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/>'
            f'<stop offset="1" stop-color="#C9C2FF"/></linearGradient>')
    p = [svg_open(W, H, ALT["player.svg"], css, defs)]
    p.append(ptext("◀ SELECT YOUR PLAYER ▶", W / 2, 30, 3, AMBER, "middle", attrs='filter="url(#glow)"'))

    # portrait card
    cx, cy, cw, ch = 44, 84, 380, 330
    p.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="10" fill="{BG2}"/>')
    p.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="10" fill="url(#spot)"/>')
    for gx in range(cx + 20, cx + cw, 24):
        p.append(f'<rect x="{gx}" y="{cy + 8}" width="1" height="{ch - 16}" fill="{LINE}" opacity=".35"/>')
    p.append(corners(cx - 6, cy - 6, cw + 12, ch + 12, CYAN, 22, 4))
    p.append(f'<rect x="{cx + 14}" y="{cy + 14}" width="46" height="26" rx="3" fill="{PINK}"/>'
             + ptext("P1", cx + 37, cy + 20, 2, BG0, "middle"))
    p.append(f'<ellipse cx="{cx + cw / 2}" cy="{cy + ch - 46}" rx="120" ry="16" fill="{CYAN}" opacity=".35" filter="url(#softglow)"/>'
             f'<ellipse cx="{cx + cw / 2}" cy="{cy + ch - 46}" rx="104" ry="11" fill="none" stroke="{CYAN}" stroke-width="2"/>')
    px = 13
    sx, sy = cx + cw / 2 - SPRITE_W * px / 2, cy + ch - 52 - SPRITE_H * px
    skin = "#C68642"
    p.append(f'<g class="bob">{sprite(sx, sy, px)}'
             f'<g style="animation:eyes 4.5s infinite"><rect x="{sx + 6 * px}" y="{sy + 5 * px}" width="{px}" height="{px}" fill="{skin}"/>'
             f'<rect x="{sx + 9 * px}" y="{sy + 5 * px}" width="{px}" height="{px}" fill="{skin}"/></g></g>')

    # bio
    rx = 476
    p.append(ptext("PLAYER 1", rx, 96, 2.2, PINK))
    p.append(ptext("READY", W - 48, 96, 2.2, LIME, "end", attrs='class="blink"'))
    p.append(ptext("SAKSHAM SINGRIWAL", rx, 122, 5.4, "url(#nm)"))
    p.append(f'<rect x="{rx}" y="{176}" width="{W - 48 - rx}" height="2" fill="{LINE}"/>'
             f'<rect x="{rx}" y="{176}" width="120" height="2" fill="{CYAN}"/>')
    rows = [("CLASS", "Forward Deployed Engineer"), ("GUILD", "NOVIXO AI · drug-safety software"),
            ("BASE", "New Delhi, India"), ("ORIGIN", "Founder, three 24×7 gaming cafés (2017–2020)"),
            ("SPECIAL", "Customer problem → software people actually use")]
    for i, (k, v) in enumerate(rows):
        y = 214 + i * 31
        p.append(ptext(k, rx, y - 12, 2, AMBER))
        p.append(mono(v, rx + 120, y, 17, TEXT))

    # stat meters
    stats = [("UNDERSTAND", 10, CYAN), ("BUILD", 8, PINK), ("DELIVER", 10, AMBER),
             ("DRUG SAFETY", 9, LIME), ("BUSINESS", 9, VIOLET)]
    colw = (W - 48 - rx) / len(stats)
    for i, (label, val, col) in enumerate(stats):
        x = rx + i * colw
        p.append(ptext(label, x, 376, 1.8, MUTED))
        for k in range(10):
            on = k < val
            style = (f'style="animation:fill 8s steps(1) {k * 0.09 + i * 0.18:.2f}s infinite both"' if on else "")
            p.append(f'<rect x="{num(x + k * 13.5)}" y="396" width="10.5" height="18" fill="{col if on else BG3}" {style}/>')
    p.append(svg_close(W, H))
    save("player.svg", "".join(p))


# ---------------------------------------------------------------------------
# 3. How I work: the world map
# ---------------------------------------------------------------------------
def stages() -> None:
    H, NY = 410, 180
    nodes = [(230, "UNDERSTAND", CYAN, ["Sit with the people who do the work",
                                         "and the people who pay for it.",
                                         "Turn a loose need into requirements,",
                                         "a data model and a plan they sign off."]),
             (640, "BUILD", PINK, ["Cloud services, APIs and integrations,",
                                   "data and AI components. Tested,",
                                   "auditable and secure enough for a",
                                   "regulated customer to accept."]),
             (1050, "DELIVER", AMBER, ["Deploy, train, measure and iterate",
                                       "with the customer.", "",
                                       "Own the outcome, not the ticket."])]
    css = "@keyframes flow{to{stroke-dashoffset:-40}}"
    path = f"M230 {NY} C 380 {NY - 70}, 490 {NY + 70}, 640 {NY} C 790 {NY - 70}, 900 {NY + 70}, 1050 {NY}"
    p = [svg_open(W, H, ALT["stages.svg"], css)]
    p.append(ptext("WORLD 1", 48, 30, 2, PINK) + ptext("HOW I WORK", 48, 52, 3.4, TEXT))
    p.append(ptext("3 STAGES", W - 48, 30, 2, MUTED, "end") + ptext("NO CONTINUES NEEDED", W - 48, 52, 2, DIM, "end"))
    p.append(f'<path d="{path}" fill="none" stroke="{LINE}" stroke-width="10" stroke-linecap="round"/>'
             f'<path d="{path}" fill="none" stroke="{VIOLET}" stroke-width="3" stroke-dasharray="4 16" '
             f'stroke-linecap="square" style="animation:flow 1.2s linear infinite"/>')
    dur, holds = 9, [(0, .2), (.4, .6), (.8, 1)]
    for i, (x, label, col, desc) in enumerate(nodes):
        a, b = holds[i]
        # ring lights up while the player stands on this stage
        vals = "0;0;1;1;0;0" if a > 0 else "1;1;0;0"
        kts = f"0;{a};{a + .001};{b};{b + .001};1" if a > 0 else f"0;{b};{b + .001};1"
        p.append(f'<circle cx="{x}" cy="{NY}" r="62" fill="{col}" opacity="0" filter="url(#softglow)">'
                 f'<animate attributeName="opacity" values="{vals.replace("1", ".55")}" keyTimes="{kts}" dur="{dur}s" '
                 f'calcMode="discrete" repeatCount="indefinite"/></circle>')
        p.append(f'<circle cx="{x}" cy="{NY}" r="46" fill="{BG2}" stroke="{col}" stroke-width="4"/>'
                 f'<circle cx="{x}" cy="{NY}" r="36" fill="none" stroke="{col}" stroke-width="1" opacity=".5" stroke-dasharray="3 5"/>')
        p.append(ptext(str(i + 1), x, NY - 17.5, 5, col, "middle"))
        p.append(ptext(label, x, NY + 66, 3, col, "middle", attrs='filter="url(#glow)"'))
        for k, line in enumerate(desc):
            hl = line.startswith("Own the outcome")
            p.append(mono(line, x, NY + 120 + k * 23, 15, AMBER if hl else MUTED, "middle", 700 if hl else 400))
    # player walking the map
    px = 3
    p.append(f'<g><g transform="translate({-SPRITE_W * px / 2},{-SPRITE_H * px - 50})">{sprite(0, 0, px)}</g>'
             f'<animateMotion path="{path}" dur="{dur}s" repeatCount="indefinite" calcMode="linear" '
             f'keyPoints="0;0;.5;.5;1;1" keyTimes="0;.2;.4;.6;.8;1"/>'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.97;.98;1" dur="{dur}s" repeatCount="indefinite"/></g>')
    p.append(svg_close(W, H))
    save("stages.svg", "".join(p))


# ---------------------------------------------------------------------------
# 4. NOVIXO Safety: the product map
# ---------------------------------------------------------------------------
def products() -> None:
    H = 300
    css = """
@keyframes stripes{to{transform:translateX(24px)}}
@keyframes grow{0%{width:0}60%,100%{width:var(--w)}}
"""
    defs = (f'<pattern id="hatch" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="6" height="12" fill="{AMBER}"/><rect x="6" width="6" height="12" fill="{ORANGE}"/></pattern>')
    items = [("CASE INTAKE", ["Case", "Intake"], "online"),
             ("LITERATURE", ["Literature", "Monitoring"], "online"),
             ("QUALITY", ["Quality", "Control"], "online"),
             ("AGGREGATE", ["Aggregate", "Reporting"], "online"),
             ("SUBMISSIONS", ["Submissions and", "Acknowledgements"], "online"),
             ("SIGNALS", ["Signal Detection", "and Management"], "online")]
    p = [svg_open(W, H, ALT["products.svg"], css, defs)]
    p.append(ptext("WORLD 2", 48, 30, 2, PINK) + ptext("NOVIXO SAFETY", 48, 52, 3.4, TEXT))
    p.append(mono("A drug-safety (pharmacovigilance) platform · multi-tenant, serverless on AWS · built for inspection",
                  48, 100, 14.5, MUTED))
    legend = [("6/6 COMPLETE", TEXT), ("ONLINE", LIME)]
    lx = W - 48
    for label, col in reversed(legend):
        lw = text_width(label, 1.8)
        p.append(ptext(label, lx, 36, 1.8, col, "end") + f'<rect x="{num(lx - lw - 16)}" y="35" width="9" height="9" fill="{col}"/>')
        lx -= lw + 34
    tw, gap, x0, y0, th = 186, 14, 48, 128, 140
    for i, (_, name, state) in enumerate(items):
        x = x0 + i * (tw + gap)
        col = {"online": LIME, "built": CYAN, "building": AMBER, "roadmap": VIOLET}[state]
        locked = state == "roadmap"
        dash = 'stroke-dasharray="6 5"' if locked else ""
        p.append(f'<rect x="{x}" y="{y0}" width="{tw}" height="{th}" rx="8" fill="{BG2 if not locked else BG1}" '
                 f'stroke="{col}" stroke-width="2" {dash} stroke-opacity="{".6" if locked else "1"}"/>')
        if i < len(items) - 1:
            p.append(ptext("▶", x + tw + gap / 2, y0 + th / 2 - 5, 1.4, DIM, "middle"))
        p.append(ptext(f"0{i + 1}", x + 16, y0 + 16, 2, col))
        if locked:  # pixel padlock
            lx2, ly2 = x + tw - 34, y0 + 12
            p.append(f'<g fill="{VIOLET}"><rect x="{lx2 + 4}" y="{ly2}" width="10" height="3"/>'
                     f'<rect x="{lx2 + 2}" y="{ly2 + 2}" width="3" height="8"/><rect x="{lx2 + 13}" y="{ly2 + 2}" width="3" height="8"/>'
                     f'<rect x="{lx2}" y="{ly2 + 9}" width="18" height="12"/></g><rect x="{lx2 + 8}" y="{ly2 + 13}" width="2" height="4" fill="{BG1}"/>')
        elif state == "online":
            p.append(f'<circle cx="{x + tw - 22}" cy="{y0 + 22}" r="5" fill="{LIME}" class="pulse"/>')
        for k, ln in enumerate(name):
            p.append(mono(ln, x + 16, y0 + 66 + k * 22, 16.5, TEXT if not locked else MUTED, weight=700))
        by = y0 + th - 26
        if state == "building":
            p.append(f'<rect x="{x + 16}" y="{by}" width="{tw - 32}" height="12" rx="2" fill="{BG3}"/>'
                     f'<svg x="{x + 16}" y="{by}" width="{tw - 32}" height="12"><rect width="0" height="12" '
                     f'style="--w:{(tw - 32) * 0.55:.0f}px;animation:grow 5s ease-out infinite"/>'
                     f'<g style="animation:stripes .8s linear infinite"><rect x="-24" width="{tw + 24}" height="12" fill="url(#hatch)" '
                     f'mask="url(#m{i})"/></g><mask id="m{i}"><rect width="0" height="12" fill="#fff" '
                     f'style="--w:{(tw - 32) * 0.55:.0f}px;animation:grow 5s ease-out infinite"/></mask></svg>')
        else:
            label = {"online": "ONLINE", "built": "BUILT · IN REVIEW"}.get(state, "ON THE ROADMAP")
            p.append(ptext(label, x + 16, by + 2, 1.6, col))
    p.append(svg_close(W, H))
    save("products.svg", "".join(p))


# ---------------------------------------------------------------------------
# 5. Section header strip
# ---------------------------------------------------------------------------
def header(name: str, kicker: str, title: str, color: str, note: str) -> None:
    H = 96
    css = "@keyframes run{0%{transform:translateX(0)}100%{transform:translateX(-36px)}}"
    p = [svg_open(W, H, ALT[name], css)]
    p.append(ptext(kicker, 48, 26, 2, color) + ptext(title, 48, 48, 3.4, TEXT))
    tw = max(text_width(title, 3.4), text_width(kicker, 2))
    sx = 48 + tw + 40
    p.append(f'<svg x="{num(sx)}" y="56" width="{num(W - 48 - sx - 260)}" height="8">'
             f'<g style="animation:run 1.4s linear infinite">'
             + "".join(f'<rect x="{k * 18}" y="0" width="8" height="8" fill="{color}" opacity="{.25 + .5 * (k % 2)}"/>'
                       for k in range(0, 120))
             + "</g></svg>")
    p.append(ptext(note, W - 48, 40, 1.8, MUTED, "end"))
    p.append(svg_close(W, H))
    save(name, "".join(p))


# ---------------------------------------------------------------------------
# 6. Gaming cafe ERP: the live floor
# ---------------------------------------------------------------------------
def erp() -> None:
    H = 392
    css = """
@keyframes sess{0%{width:0}100%{width:var(--w)}}
@keyframes flick{0%,100%{opacity:1}50%{opacity:.35}}
"""
    p = [svg_open(W, H, ALT["erp.svg"], css)]
    p.append(ptext("BONUS LEVEL · HOME TURF", 48, 30, 2, AMBER))
    p.append(ptext("GAMING CAFE ERP", 48, 54, 4, TEXT, attrs='filter="url(#glow)"'))
    desc = ("I ran the cafés this was built for, so the requirements came from the floor: one session and billing "
            "engine for every table and console, a live floor view, customers and memberships, a wallet, bookings "
            "without clashes, a food and beverage counter, and separate apps for the owner and for customers.")
    for k, ln in enumerate(wrap(desc, 56)):
        p.append(mono(ln, 48, 118 + k * 25, 15.5, MUTED))
    cx = 48
    for t in ["NestJS", "PostgreSQL", "Prisma", "React", "Socket.IO", "Docker"]:
        s, w = chip(cx, 318, t, AMBER, 13)
        p.append(s)
        cx += w + 4

    # live floor panel
    fx, fy, fw, fh = 700, 32, 532, 328
    p.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="10" fill="{BG0}" stroke="{LINE}" stroke-width="2"/>')
    p.append(ptext("LIVE FLOOR", fx + 20, fy + 18, 2, CYAN) +
             f'<circle cx="{fx + 160}" cy="{fy + 24}" r="5" fill="{PINK}" class="blink"/>' +
             ptext("REC", fx + 172, fy + 18, 2, PINK, attrs='class="blink"'))
    p.append(ptext("SHIFT 24×7", fx + fw - 20, fy + 18, 2, MUTED, "end"))
    rnd = random.Random(3)
    stations = ["PC-01", "PC-02", "PC-03", "PC-04", "PC-05", "PC-06", "PS-01", "PS-02", "PS-03",
                "POOL-1", "POOL-2", "SNK-1"]
    sw, sh, g = 158, 54, 12
    for i, st in enumerate(stations):
        r, c = divmod(i, 3)
        x, y = fx + 20 + c * (sw + g), fy + 52 + r * (sh + g + 4)
        state = rnd.choice(("play", "play", "play", "free", "booked"))
        col = {"play": LIME, "free": DIM, "booked": AMBER}[state]
        p.append(f'<rect x="{x}" y="{y}" width="{sw}" height="{sh}" rx="5" fill="{BG2}" stroke="{col}" '
                 f'stroke-opacity="{.9 if state != "free" else .5}" stroke-width="1.5"/>')
        p.append(ptext(st, x + 12, y + 12, 1.7, TEXT if state != "free" else MUTED))
        lab = {"play": "LIVE", "free": "FREE", "booked": "BOOKED"}[state]
        p.append(ptext(lab, x + sw - 12, y + 13, 1.4, col, "end",
                       attrs='style="animation:flick 2s steps(1) infinite"' if state == "booked" else ""))
        p.append(f'<rect x="{x + 12}" y="{y + 34}" width="{sw - 24}" height="8" rx="2" fill="{BG3}"/>')
        if state == "play":
            bw = (sw - 24) * rnd.uniform(.35, .95)
            d = rnd.uniform(9, 22)
            p.append(f'<rect x="{x + 12}" y="{y + 34}" width="0" height="8" rx="2" fill="{LIME}" '
                     f'style="--w:{bw:.0f}px;animation:sess {d:.0f}s linear {-rnd.uniform(0, d):.1f}s infinite"/>')
    p.append(svg_close(W, H))
    save("erp.svg", "".join(p))


# ---------------------------------------------------------------------------
# 7. Open work: cartridge cards
# ---------------------------------------------------------------------------
def cards() -> None:
    data = [("SENTINEL", "Fraud-risk analytics studio. Chooses supervised models or anomaly detection from the data it "
                          "is given, guards against leakage, and explains each result in plain language.",
             ["Python", "XGBoost", "CatBoost", "SHAP", "Streamlit"], CYAN),
            ("APEX DS", "Analytics platform that runs fully offline: automated modelling, forecasting, clustering, "
                        "document chat and question-to-SQL.", ["Python", "AutoGluon", "DuckDB", "Prophet", "Ollama"], PINK),
            ("DS STUDIO", "The general form of Sentinel for any tabular problem: classification, regression, anomaly "
                          "detection and forecasting, with tuned models and explanations.",
             ["Python", "scikit-learn", "Optuna", "Streamlit"], AMBER),
            ("GALACTIC DATA FORGE", "A guided eleven-step pipeline from raw data through hypothesis tests and "
                                    "preprocessing to trained models.", ["Python", "scikit-learn", "TensorFlow", "Streamlit"], LIME)]
    CW, CH = 620, 252
    for i, (name, desc, stack, col) in enumerate(data, 1):
        p = [svg_open(CW, CH, ALT[f"card-{i}.svg"])]
        p.append(f'<rect x="0" y="0" width="12" height="{CH}" fill="{col}" opacity=".9"/>')
        for k in range(6):
            p.append(f'<rect x="{CW - 56 + (k % 2) * 14}" y="{30 + k * 10}" width="8" height="4" fill="{LINE}"/>')
        p.append(ptext(f"CARTRIDGE 0{i}", 36, 28, 1.8, col))
        p.append(ptext("PUBLIC", CW - 76, 28, 1.6, LIME, "end"))
        p.append(ptext(name, 36, 52, 4 if len(name) < 14 else 3.4, TEXT, attrs='filter="url(#glow)"'))
        for k, ln in enumerate(wrap(desc, 62)):
            p.append(mono(ln, 36, 118 + k * 22, 14.5, MUTED))
        cx = 36
        for t in stack:
            s, w = chip(cx, 192, t, col, 12, 10)
            p.append(s)
            cx += w + 2
        p.append(ptext("▶ PLAY", CW - 36, 202, 2, col, "end", attrs='class="blink"'))
        p.append(svg_close(CW, CH))
        save(f"card-{i}.svg", "".join(p))


# ---------------------------------------------------------------------------
# 8. Career mode
# ---------------------------------------------------------------------------
def career() -> None:
    H = 486
    css = "@keyframes coin{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.15)}}"
    TS, OS, YS = 16, 13.5, 2.2  # title size, organisation size, pixel scale of the dates
    # (dates, lines, colour, kind); a line is (text, "t") for a title or (text, "o") for an organisation
    levels = [("2017-2020", [("Founder and", "t"), ("operations", "t"), ("manager", "t"),
                             ("StunnShot, 3 cafés", "o")], VIOLET, ""),
              ("2020-2023", [("Bachelor of", "t"), ("Computer", "t"), ("Applications", "t"), ("BVIMR", "o")],
               "#6C7BFF", ""),
              ("2024-2026", [("MBA, Business", "t"), ("Analytics and HR", "t"), ("BVIMR", "o")], "#6C7BFF", ""),
              ("2025", [("HR intern", "t"), ("Engineers India Limited", "o"), ("Data science intern", "t"),
                        ("Spinnaker Analytics", "o")], LIME, ""),
              ("JAN 2026", [("Associate", "t"), ("Data Scientist", "t"), ("NOVIXO AI", "o")], CYAN, ""),
              ("OCT 2026", [("Forward Deployed", "t"), ("Engineer", "t"), ("NOVIXO AI", "o")], PINK, "now"),
              ("NEXT", [("Enterprise", "t"), ("solution", "t"), ("delivery", "t"), ("the next stage", "o")],
               AMBER, "next")]
    n, gap = len(levels), 16
    here = "YOU ARE HERE ▼"
    # each column is as wide as its longest line, and the spare width is shared out evenly
    need = [max([text_width(yrs, YS)] + [mono_width(t, TS if k == "t" else OS) for t, k in lines]
                + ([text_width(here, 1.8)] if kind == "now" else []))
            for yrs, lines, _, kind in levels]
    slack = (W - 96 - gap * (n - 1) - sum(need)) / n
    if slack < 8:
        sys.exit(f"career.svg is too crowded: {slack:.1f}px of spare width per column")

    p = [svg_open(W, H, ALT["career.svg"], css)]
    p.append(ptext("CAREER MODE", 48, 30, 2, PINK) + ptext("EXPERIENCE", 48, 52, 3.4, TEXT))
    p.append(ptext(f"{n} LEVELS · 1 LIFE", W - 48, 40, 2, MUTED, "end"))
    x = 48.0
    for i, (yrs, lines, col, kind) in enumerate(levels):
        pw = need[i] + slack
        top = 394 - i * 30
        nxt, now = kind == "next", kind == "now"
        if nxt:
            p.append(f'<rect x="{num(x)}" y="{top}" width="{num(pw)}" height="{H - top + 10}" fill="none" stroke="{col}" '
                     f'stroke-width="2" stroke-dasharray="7 6" opacity=".7"/>')
        else:
            p.append(f'<rect x="{num(x)}" y="{top}" width="{num(pw)}" height="{H - top + 10}" fill="{BG2}"/>')
            for by in range(top + 14, H, 16):
                off = 0 if ((by - top) // 16) % 2 else 18
                for bx in range(int(x) + off - 18, int(x + pw), 36):
                    l, r = max(bx, x), min(bx + 34, x + pw)
                    if r > l:
                        p.append(f'<rect x="{num(l)}" y="{by}" width="{num(r - l)}" height="14" fill="{BG3}"/>')
            p.append(f'<rect x="{num(x)}" y="{top}" width="{num(pw)}" height="8" fill="{col}"/>')
        if now:
            p.append(f'<rect x="{num(x)}" y="{top}" width="{num(pw)}" height="40" fill="{col}" opacity=".35" filter="url(#softglow)"/>')
        p.append(ptext(f"LV {i + 1}", x + 14, top + 22, 2, col))
        ty = top - 124
        if now:
            p.append(ptext(here, x + pw / 2, ty - 28, 1.8, PINK, "middle", attrs='class="blink"'))
        p.append(ptext(yrs, x, ty, YS, col))
        ly, prev = ty + 38, None
        for text, k in lines:
            if prev is not None:
                ly += 21 if (prev, k) == ("t", "t") else 23 if k == "o" else 25
            fits(text, TS if k == "t" else OS, pw, "career.svg")
            if k == "t":
                p.append(mono(text, x, ly, TS, TEXT if not nxt else MUTED, weight=700))
            else:
                p.append(mono(text, x, ly, OS, MUTED))
            prev = k
        if i < n - 1:  # coin between levels
            ccx, ccy = x + pw + gap / 2, ty - 40
            p.append(f'<g transform="translate({num(ccx)} {ccy})"><g style="animation:coin 1.3s ease-in-out {i * .3:.1f}s infinite">'
                     f'<rect x="-6" y="-9" width="12" height="18" rx="3" fill="{AMBER}"/>'
                     f'<rect x="-1.5" y="-5" width="3" height="10" fill="{ORANGE}"/></g></g>')
        x += pw + gap
    p.append(svg_close(W, H))
    save("career.svg", "".join(p))


# ---------------------------------------------------------------------------
# 9. Achievements (education and certifications)
# ---------------------------------------------------------------------------
def achievements() -> None:
    H = 504
    css = "@keyframes grow{0%{width:0}70%,100%{width:var(--w)}}@keyframes shine{0%,80%{transform:translateX(-80px)}100%{transform:translateX(420px)}}"
    bvimr = "BVIMR, Bharati Vidyapeeth University"
    bia = "Boston Institute of Analytics"
    # (title, organisation, badge, colour, in progress)
    # every badge ends with how the course was taken: OFFLINE (in person) or ONLINE
    items = [("MBA, Business Analytics and HR", bvimr, "2024-2026 · GRADE A · OFFLINE", AMBER, False),
             ("Bachelor of Computer Applications", bvimr, "2020-2023 · GRADE A · OFFLINE", AMBER, False),
             ("Diploma in Data Science", bia, "UNLOCKED · OFFLINE", CYAN, False),
             ("Diploma in Artificial Intelligence", bia, "UNLOCKED · OFFLINE", CYAN, False),
             ("Business Analytics Plus", "IMS Proschool", "UNLOCKED 2026 · OFFLINE", CYAN, False),
             ("Business Analytics Specialization", "Wharton Online, Univ. of Pennsylvania", "UNLOCKED · ONLINE",
              CYAN, False),
             ("Forward Deployed Engineering", "NeuraPath Academy", "COMPLETED · OFFLINE", CYAN, False)]
    done = sum(not prog for *_, prog in items)
    p = [svg_open(W, H, ALT["achievements.svg"], css)]
    p.append(ptext("TROPHY ROOM", 48, 30, 2, AMBER) + ptext("EDUCATION & CERTIFICATIONS", 48, 52, 3.4, TEXT))
    p.append(ptext(f"{done}/{len(items)} UNLOCKED", W - 48, 40, 2, MUTED, "end"))
    tw, th, gx, gy = 384, 112, 20, 20

    def pixels(px: float, py: float, rows: list[str], colours: dict[str, str], t: float = 4) -> str:
        return "".join(f'<rect x="{num(px + cc * t)}" y="{num(py + rr * t)}" width="{t}" height="{t}" fill="{colours[ch]}"/>'
                       for rr, row in enumerate(rows) for cc, ch in enumerate(row) if ch in colours)

    for i, (title, org, badge, col, prog) in enumerate(items):
        r, c = divmod(i, 3)
        x, y = 48 + c * (tw + gx), 104 + r * (th + gy)
        p.append(f'<svg x="{x}" y="{y}" width="{tw}" height="{th}">'
                 f'<rect width="{tw}" height="{th}" rx="8" fill="{BG2}" stroke="{col}" stroke-opacity=".55" stroke-width="1.5"/>'
                 f'<rect y="0" width="40" height="{th}" fill="#fff" opacity=".05" transform="skewX(-20)" '
                 f'style="animation:shine 6s ease-in-out {i * .5:.1f}s infinite"/></svg>')
        # pixel trophy
        tx, ty_, t = x + 22, y + 38, 4
        cup_col = col if not prog else DIM
        p.append(pixels(tx, ty_, ["#######", "#######", ".#####.", "..###..", "...#...", "..###..", ".#####."],
                        {"#": cup_col}))
        p.append(f'<rect x="{tx - t}" y="{ty_}" width="{t}" height="{t * 2}" fill="{cup_col}"/>'
                 f'<rect x="{tx + 7 * t}" y="{ty_}" width="{t}" height="{t * 2}" fill="{cup_col}"/>')
        lx = x + 72
        room = x + tw - 12 - lx
        if text_width(badge, 1.5) > room:
            sys.exit(f"overflow in achievements.svg: badge {badge!r}")
        fits(title, 14.5, room, "achievements.svg")
        fits(org, 12.5, room, "achievements.svg")
        p.append(ptext(badge, lx, y + 24, 1.5, col))
        p.append(mono(title, lx, y + 60, 14.5, TEXT, weight=700))
        p.append(mono(org, lx, y + 82, 12.5, MUTED))
        if prog:
            bw = tw - 72 - 22
            p.append(f'<rect x="{lx}" y="{y + 92}" width="{bw}" height="6" rx="2" fill="{BG3}"/>'
                     f'<rect x="{lx}" y="{y + 92}" width="0" height="6" rx="2" fill="{PINK}" style="--w:{bw * .45:.0f}px;animation:grow 4s ease-out infinite"/>')

    p.append(svg_close(W, H))
    save("achievements.svg", "".join(p))


# ---------------------------------------------------------------------------
# 10. Inventory (toolbox)
# ---------------------------------------------------------------------------
def inventory() -> None:
    cats = [("LANGUAGES & DATA", CYAN, ["Python", "TypeScript", "SQL", "PostgreSQL", "DynamoDB"]),
            ("CLOUD & DELIVERY", PINK, ["AWS Lambda", "API Gateway", "S3", "Cognito", "CDK", "Bedrock", "Vercel",
                                        "Docker", "Continuous integration"]),
            ("APPLICATIONS", AMBER, ["React", "Next.js", "NestJS", "FastAPI", "Hono", "REST APIs", "Webhooks",
                                     "Role-based access", "Audit trails"]),
            ("DATA & AI", LIME, ["Machine learning", "Model explainability", "Forecasting",
                                 "LLM apps with retrieval", "Evaluation", "Guardrails"]),
            ("WITH CUSTOMERS", VIOLET, ["Requirements", "Solution design", "Demos", "Training", "Documentation",
                                        "Stakeholder management"])]
    lx, cx0, right = 48, 330, W - 48
    rows_svg, y = [], 104
    for label, col, items in cats:
        rows_svg.append(f'<rect x="{lx}" y="{y + 4}" width="6" height="22" fill="{col}"/>')
        rows_svg.append(ptext(label, lx + 18, y + 9, 2, TEXT))
        rows_svg.append(ptext(f"×{len(items):02d}", lx + 18, y + 31, 1.6, col))
        cx, cy = cx0, y
        for it in items:
            w = len(it) * 14 * 0.62 + 31
            if cx + w > right:
                cx, cy = cx0, cy + 40
            s, w = chip(cx, cy, it, col, 14)
            rows_svg.append(s)
            cx += w + 4
        y = max(cy + 40, y + 50) + 22
        rows_svg.append(f'<rect x="{lx}" y="{y - 20}" width="{right - lx}" height="1" fill="{LINE}"/>')
    H = y + 14
    p = [svg_open(W, H, ALT["inventory.svg"])]
    p.append(ptext("INVENTORY", 48, 30, 2, LIME) + ptext("TOOLBOX", 48, 52, 3.4, TEXT))
    p.append(ptext(f"{sum(len(i) for _, _, i in cats)} ITEMS EQUIPPED", W - 48, 40, 2, MUTED, "end"))
    p.extend(rows_svg[:-1])
    p.append(svg_close(W, H))
    save("inventory.svg", "".join(p))


# ---------------------------------------------------------------------------
# 11. Footer and buttons
# ---------------------------------------------------------------------------
def footer() -> None:
    H = 260
    p = [svg_open(W, H, ALT["footer.svg"],
                  defs=f'<linearGradient id="nm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/>'
                       f'<stop offset="1" stop-color="{PINK}"/></linearGradient>')]
    p.append(ptext("CONTINUE?", W / 2 - 30, 40, 4, AMBER, "middle", attrs='filter="url(#glow)"'))
    dx = W / 2 - 30 + text_width("CONTINUE?", 4) / 2 + 26
    for d in range(10):
        digit = str(9 - d)
        vals = ";".join("1" if k == d else "0" for k in range(10))
        p.append(f'<g opacity="{1 if d == 0 else 0}">{ptext(digit, dx, 40, 4, PINK)}'
                 f'<animate attributeName="opacity" values="{vals}" dur="10s" calcMode="discrete" repeatCount="indefinite"/></g>')
    p.append(ptext("THANKS FOR PLAYING", W / 2, 104, 6, "url(#nm)", "middle", attrs='filter="url(#glow)"'))
    p.append(mono("Open to conversations about forward deployed engineering,", W / 2, 188, 17, MUTED, "middle"))
    p.append(mono("solutions engineering and enterprise AI delivery.", W / 2, 214, 17, MUTED, "middle"))
    p.append(ptext("♥", 48, H - 34, 2, PINK) + ptext("♥", 64, H - 34, 2, PINK) + ptext("♥", 80, H - 34, 2, PINK))
    p.append(ptext("HI-SCORE: STILL GOING", W - 48, H - 34, 1.8, DIM, "end"))
    p.append(svg_close(W, H))
    save("footer.svg", "".join(p))

    for name, label, col in [("btn-linkedin.svg", "LINKEDIN", CYAN), ("btn-email.svg", "EMAIL", PINK),
                             ("btn-github.svg", "GITHUB", AMBER)]:
        bw, bh = 250, 64
        b = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{bw}" height="{bh}" viewBox="0 0 {bw} {bh}" role="img" '
             f'aria-label="{esc(ALT[name])}"><title>{esc(ALT[name])}</title>'
             f'<style>@keyframes blink{{0%,55%{{opacity:1}}56%,100%{{opacity:.25}}}}'
             f'@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>'
             f'<rect x="2" y="8" width="{bw - 4}" height="{bh - 10}" rx="10" fill="{BG0}"/>'
             f'<rect x="2" y="2" width="{bw - 4}" height="{bh - 12}" rx="10" fill="{BG2}" stroke="{col}" stroke-width="2"/>'
             f'<circle cx="30" cy="{(bh - 10) / 2 + 2}" r="9" fill="{col}" style="animation:blink 1.4s steps(1) infinite"/>'
             + ptext("▶ " + label, 54, (bh - 10) / 2 + 2 - 8, 2.3, TEXT) + "</svg>")
        save(name, b)


if __name__ == "__main__":
    print(f"Writing assets to {OUT}")
    hero()
    player()
    stages()
    products()
    header("head-clients.svg", "SIDE QUESTS", "CLIENT DELIVERY", CYAN, "CODE IS PRIVATE")
    header("head-open.svg", "ARCADE", "OPEN WORK", LIME, "ALL PUBLIC · PRESS PLAY")
    erp()
    cards()
    career()
    achievements()
    inventory()
    footer()
    check_readme()
