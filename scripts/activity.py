"""Builds assets/activity.svg: a terminal-style contribution heatmap.
Runs inside GitHub Actions (needs GITHUB_TOKEN). Without a token it renders demo data.
"""
import json
import os
import random
import urllib.request
from datetime import date, timedelta
from pathlib import Path

USER = os.environ.get("GH_USER", "The-MakleyN")
OUT = Path(__file__).resolve().parent.parent / "assets" / "activity.svg"

BG, PANEL, BORDER = "#060606", "#0b0b0b", "#2b2b2b"
NEON, GREEN, TEXT, MUTED = "#f4efe6", "#bdbdbd", "#d9d6d0", "#7b7b7b"
LEVELS = ["#171717", "#3d3d3d", "#6e6e6e", "#a8a8a8", "#f4efe6"]
FONT = "ui-monospace,'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"
MONTHS_TR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
LVL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return demo()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    data = json.load(urllib.request.urlopen(req))
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [
        [(date.fromisoformat(d["date"]), d["contributionCount"], LVL[d["contributionLevel"]]) for d in w["contributionDays"]]
        for w in cal["weeks"]
    ]
    return cal["totalContributions"], weeks


def demo():
    random.seed(7)
    start = date.today() - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    weeks, d, total = [], start, 0
    while d <= date.today():
        wk = []
        for _ in range(7):
            if d > date.today():
                break
            lvl = random.choices([0, 1, 2, 3, 4], [35, 25, 20, 12, 8])[0]
            c = [0, 1, 3, 6, 10][lvl]
            total += c
            wk.append((d, c, lvl))
            d += timedelta(days=1)
        weeks.append(wk)
    return total, weeks


def render(total, weeks):
    cell, gap = 12, 3
    left, top = 64, 104
    W = left + len(weeks) * (cell + gap) + 40
    H = top + 7 * (cell + gap) + 72
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    o.append('<defs><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern></defs>')
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{PANEL}" stroke="{BORDER}"/>')
    o.append(f'<text x="24" y="28" font-family="{FONT}" font-size="11" fill="{MUTED}">~/The-MakleyN/README.md</text>')
    o.append(f'<line x1="0" y1="42" x2="{W}" y2="42" stroke="{BORDER}"/>')
    o.append(f'<text x="24" y="74" font-family="{FONT}" font-size="18" font-weight="700" fill="{TEXT}">{total:,} contributions <tspan fill="{MUTED}" font-weight="400" font-size="14">in the last year</tspan></text>')
    o.append(f'<rect x="{W-128}" y="56" width="104" height="26" rx="4" fill="none" stroke="{GREEN}"/>')
    o.append(f'<text x="{W-76}" y="73" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{NEON}">Son 1 yıl</text>')

    last_m = None
    for i, wk in enumerate(weeks):
        m = wk[0][0].month
        if m != last_m and wk[0][0].day <= 7:
            o.append(f'<text x="{left + i*(cell+gap)}" y="{top-10}" font-family="{FONT}" font-size="10" fill="{MUTED}">{MONTHS_TR[m-1]}</text>')
            last_m = m
    for r, lab in [(1, "Pzt"), (3, "Çar"), (5, "Cum")]:
        o.append(f'<text x="24" y="{top + r*(cell+gap) + 10}" font-family="{FONT}" font-size="10" fill="{MUTED}">{lab}</text>')

    n = len(weeks)
    for i, wk in enumerate(weeks):
        begin = round(i / n * 2.2, 3)
        cells = []
        for d, c, lvl in wk:
            r = (d.weekday() + 1) % 7
            x, y = left + i * (cell + gap), top + r * (cell + gap)
            cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{LEVELS[lvl]}"><title>{d.isoformat()}: {c}</title></rect>')
        o.append(f'<g opacity="0">{"".join(cells)}<animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur=".25s" fill="freeze"/></g>')

    fy = H - 28
    o.append(f'<text x="24" y="{fy}" font-family="{FONT}" font-size="11" fill="{MUTED}">&gt; github activity heatmap // <tspan fill="{GREEN}">contribution stream online</tspan></text>')
    lx = W - 200
    o.append(f'<text x="{lx}" y="{fy}" font-family="{FONT}" font-size="10" fill="{MUTED}">az</text>')
    for k, col in enumerate(LEVELS):
        o.append(f'<rect x="{lx + 22 + k*15}" y="{fy-10}" width="11" height="11" rx="2" fill="{col}"/>')
    o.append(f'<text x="{lx + 22 + 5*15 + 4}" y="{fy}" font-family="{FONT}" font-size="10" fill="{MUTED}">çok</text>')
    o.append(f'<rect width="{W}" height="{H}" rx="10" fill="url(#scan)"/>')
    o.append("</svg>")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(o), encoding="utf-8")


if __name__ == "__main__":
    render(*fetch())
    print("activity.svg written")
