"""Builds the live HIGH SCORES panel from the GitHub contribution calendar.

Usage:  GITHUB_TOKEN=... GITHUB_USERNAME=SakshamSingriwal python scripts/scoreboard.py dist/scoreboard.svg
Runs in .github/workflows/arcade.yml once a day; the result is published to the `output` branch.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

from pixel import (AMBER, BG3, CYAN, DIM, LIME, MUTED, PINK, TEXT, VIOLET, mono, num, ptext,
                   svg_close, svg_open)

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""

LEVEL = {"NONE": BG3, "FIRST_QUARTILE": "#4A1F78", "SECOND_QUARTILE": "#8C2AA8",
         "THIRD_QUARTILE": "#D6339C", "FOURTH_QUARTILE": PINK}


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "arcade-profile-scoreboard"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    current = 0
    tail = days[:-1] if days and days[-1]["contributionCount"] == 0 else days  # today may still be empty
    for d in reversed(tail):
        if d["contributionCount"] == 0:
            break
        current += 1
    return current, longest


def render(cal: dict) -> str:
    W, H = 1280, 330
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    current, longest = streaks(days)
    best = max((d["contributionCount"] for d in days), default=0)
    active = sum(1 for d in days if d["contributionCount"] > 0)
    total = cal["totalContributions"]
    today = dt.date.today().strftime("%d %b %Y").upper()

    css = """
@keyframes beam{0%{transform:translateX(-60px)}100%{transform:translateX(720px)}}
"""
    defs = (f'<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{CYAN}" stop-opacity=".45"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>')
    label = (f"High scores over the last twelve months: {total} contributions, current streak {current} days, "
             f"longest streak {longest} days, best day {best}, {active} active days.")
    p = [svg_open(W, H, label, css, defs)]
    p.append(ptext("LIVE FEED", 48, 30, 2, PINK) + ptext("HIGH SCORES", 48, 52, 3.4, TEXT))
    p.append(ptext(f"UPDATED {today}", W - 48, 40, 1.8, MUTED, "end"))

    # leaderboard
    p.append(ptext("RANK", 48, 108, 1.8, DIM) + ptext("SCORE", 128, 108, 1.8, DIM) + ptext("NAME", 260, 108, 1.8, DIM))
    rows = [("1ST", total, "CONTRIBUTIONS", AMBER), ("2ND", current, "CURRENT STREAK", CYAN),
            ("3RD", longest, "LONGEST STREAK", PINK), ("4TH", best, "BEST DAY", LIME),
            ("5TH", active, "ACTIVE DAYS", VIOLET)]
    for i, (rank, score, name, col) in enumerate(rows):
        y = 136 + i * 36
        p.append(ptext(rank, 48, y, 2.6, col))
        p.append(ptext(f"{score:05d}", 128, y, 2.6, TEXT, attrs='filter="url(#glow)"' if i == 0 else ""))
        p.append(ptext(name, 260, y + 2, 2.2, col))

    # contribution grid
    gx, gy, step, cell = 560, 108, 12.7, 10.4
    cells, months, last_month = [], [], None
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            wd = (dt.date.fromisoformat(d["date"]).weekday() + 1) % 7  # Sunday = 0
            cells.append(f'<rect x="{num(gx + wi * step)}" y="{num(gy + 22 + wd * step)}" width="{cell}" height="{cell}" '
                         f'rx="2" fill="{LEVEL.get(d["contributionLevel"], BG3)}"/>')
        m = dt.date.fromisoformat(w["contributionDays"][0]["date"]).month
        if m != last_month and wi < len(weeks) - 2:
            months.append(mono(dt.date(2000, m, 1).strftime("%b"), gx + wi * step, gy + 12, 12, MUTED))
            last_month = m
    p.append("".join(months) + "".join(cells))
    gw = len(weeks) * step
    p.append(f'<svg x="{gx}" y="{gy + 16}" width="{num(gw)}" height="{num(7 * step + 10)}">'
             f'<rect width="60" height="100" fill="url(#beam)" style="animation:beam 5s linear infinite;mix-blend-mode:screen"/></svg>')
    ly = gy + 22 + 7 * step + 18
    p.append(mono("less", gx, ly + 10, 12, MUTED))
    for k, col in enumerate(LEVEL.values()):
        p.append(f'<rect x="{gx + 40 + k * 16}" y="{ly}" width="{cell}" height="{cell}" rx="2" fill="{col}"/>')
    p.append(mono("more", gx + 40 + 5 * 16 + 4, ly + 10, 12, MUTED))
    p.append(ptext("INSERT COMMIT TO CONTINUE", gx + gw, ly + 1, 1.6, DIM, "end"))
    p.append(svg_close(W, H))
    return "".join(p)


def main() -> None:
    login = os.environ.get("GITHUB_USERNAME", "SakshamSingriwal")
    token = os.environ["GITHUB_TOKEN"]
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist/scoreboard.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(fetch(login, token)), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
