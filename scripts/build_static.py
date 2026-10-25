"""Generates the static terminal-style SVGs (header + projects) for the profile README.
Run:  python scripts/build_static.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

# ---- palette -------------------------------------------------------------
BG = "#060606"
PANEL = "#0b0b0b"
BORDER = "#2b2b2b"
NEON = "#f4efe6"
GREEN = "#bdbdbd"
DIM = "#3c3c3c"
TEXT = "#d9d6d0"
MUTED = "#7b7b7b"
FONT = "ui-monospace,'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"

# ---- 5x7 pixel font ------------------------------------------------------
FONT5 = {
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
}


def pixel_text(word, x, y, s, color, glow_id=None):
    parts = []
    cx = x
    for ch in word:
        g = FONT5[ch]
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == "1":
                    parts.append(
                        f'<rect x="{cx + c * s}" y="{y + r * s}" width="{s - 1}" height="{s - 1}"/>'
                    )
        cx += 6 * s
    filt = f' filter="url(#{glow_id})"' if glow_id else ""
    return f'<g fill="{color}"{filt}>' + "".join(parts) + "</g>", cx - x


# ---- pixel portrait from assets/src/photo.png ---------------------------
PHOTO = Path(__file__).resolve().parent.parent / "assets" / "src" / "photo.png"
CROP = (148, 36, 292, 180)  # (left, top, right, bottom) in the source photo
GRID = 60
LEVELS = 9


def portrait_art(x, y, s):
    from PIL import Image, ImageOps, ImageEnhance

    im = Image.open(PHOTO).convert("L").crop(CROP)
    im = ImageOps.autocontrast(im, cutoff=0.5)
    im = im.point(lambda v: int(255 * (v / 255) ** 0.62))  # lift the shadows so the face reads
    im = ImageEnhance.Contrast(im).enhance(1.1)
    im = im.resize((GRID, GRID), Image.LANCZOS)
    px = im.load()
    rows = []
    for r in range(GRID):
        cells = []
        for c in range(GRID):
            q = round(px[c, r] / 255 * (LEVELS - 1))
            v = int(22 + q / (LEVELS - 1) * 222)
            cells.append(f'<rect x="{x + c*s}" y="{y + r*s}" width="{s-0.6}" height="{s-0.6}" fill="#{v:02x}{v:02x}{v:02x}"/>')
        rows.append("".join(cells))
    return rows


def defs():
    return f"""<defs>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="2.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#000" opacity=".35"/>
  </pattern>
</defs>"""


def titlebar(w, title):
    return f"""<rect x="0.5" y="0.5" width="{w-1}" height="34" rx="10" fill="#111111" stroke="{BORDER}"/>
<rect x="1" y="20" width="{w-2}" height="15" fill="#111111"/>
<circle cx="22" cy="18" r="5" fill="#5a5a5a"/>
<circle cx="40" cy="18" r="5" fill="#3f3f3f"/>
<circle cx="58" cy="18" r="5" fill="#2a2a2a"/>
<text x="{w/2}" y="22" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}">{title}</text>"""


def typed(x, y, text, begin, dur, size=15, color=TEXT, cid="t"):
    """Typewriter effect: clip width grows in discrete steps."""
    cw = size * 0.6
    n = len(text)
    vals = ";".join(str(round(i * cw, 1)) for i in range(n + 1))
    text = text.replace("&", "&amp;")
    return f"""<clipPath id="{cid}"><rect x="{x}" y="{y-size}" height="{size*1.6}" width="0">
  <animate attributeName="width" values="{vals}" calcMode="discrete" begin="{begin}s" dur="{dur}s" fill="freeze"/></rect></clipPath>
<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}" clip-path="url(#{cid})" xml:space="preserve">{text}</text>"""


def tag(x, y, label):
    w = len(label) * 7.8 + 22
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="3" fill="#141414" stroke="{GREEN}"/>'
        f'<text x="{x + w/2}" y="{y+16}" text-anchor="middle" font-family="{FONT}" font-size="12" '
        f'font-weight="700" fill="{NEON}">{label}</text>',
        w,
    )


def header():
    W, H = 900, 400
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', defs()]
    o.append(f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{PANEL}" stroke="{BORDER}"/>')
    o.append(titlebar(W, "makleyn@github: ~/profile — zsh"))

    # left column
    o.append(f'<text x="36" y="70" font-family="{FONT}" font-size="11" fill="{MUTED}" letter-spacing="2">SYSTEM BOOT // IDENTITY LOADED</text>')
    o.append(f'<text x="36" y="98" font-family="{FONT}" font-size="16" font-weight="700" fill="{GREEN}">&gt; HELLO, WORLD<tspan fill="{NEON}">_<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>')
    name, nw = pixel_text("MAKLEYN", 36, 116, 7, NEON, "glow")
    o.append(name)
    o.append(typed(36, 197, "$ whoami", 0.3, 0.6, 14, MUTED, "t1"))
    o.append(typed(36, 221, "→ embedded systems & python meraklısı", 1.0, 2.2, 14, TEXT, "t2"))
    o.append(typed(36, 245, "→ ESP32 ile kendi akıllı saatimi yapıyorum", 3.3, 2.4, 14, TEXT, "t3"))

    tx = 36
    for label in ["ESP32", "C++", "PYTHON", "IoT", "ARDUINO"]:
        svg, w = tag(tx, 268, label)
        o.append(svg)
        tx += w + 10

    o.append(f'<line x1="36" y1="312" x2="560" y2="312" stroke="{BORDER}" stroke-dasharray="3 4"/>')
    o.append(f'<text x="36" y="336" font-family="{FONT}" font-size="12" fill="{MUTED}">◆ <tspan fill="{TEXT}">İstanbul Kültür Üniversitesi</tspan>   ⌖ <tspan fill="{TEXT}">İstanbul, TR</tspan>   @ <tspan fill="{TEXT}">_makleyn_</tspan></text>')
    o.append(f'<text x="36" y="362" font-family="{FONT}" font-size="11" fill="{DIM}">&gt; status: <tspan fill="{GREEN}">online</tspan> · uptime: 24/7 · coffee: ████████░░ 80%</text>')

    # right panel: printing watch
    px, py, pw, ph = 600, 56, 270, 316
    o.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="6" fill="#050505" stroke="{BORDER}"/>')
    o.append(f'<text x="{px+14}" y="{py+22}" font-family="{FONT}" font-size="11" fill="{MUTED}">portrait.svg</text>')

    s = 4
    ax = px + (pw - GRID * s) // 2
    ay = py + 36
    rows = portrait_art(ax, ay, s)
    total = len(rows)
    cycle = 12.0  # seconds per print loop
    print_t = 6.0
    for i, r in enumerate(rows):
        t0 = (i / total) * print_t / cycle
        t1 = min(t0 + 0.004, 0.999)
        kt = f"0;{t0:.3f};{t1:.3f};0.94;0.98;1"
        o.append(f'<g opacity="0">{r}<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="{cycle}s" repeatCount="indefinite"/></g>')
    # print head line
    o.append(f'<rect x="{ax-6}" y="{ay}" width="{GRID*s+12}" height="2" fill="{NEON}" filter="url(#glow)">'
             f'<animate attributeName="y" values="{ay};{ay + total*s};{ay + total*s};{ay}" keyTimes="0;{print_t/cycle:.3f};0.999;1" dur="{cycle}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{print_t/cycle:.3f};{print_t/cycle+0.01:.3f};1" dur="{cycle}s" repeatCount="indefinite"/></rect>')

    # PRINTING xx% label (discrete frames)
    steps = list(range(0, 101, 5))
    for k, pct in enumerate(steps):
        a = (k / len(steps)) * print_t / cycle
        b = ((k + 1) / len(steps)) * print_t / cycle if pct < 100 else 0.94
        label = f"PRINTING {pct}%" if pct < 100 else "DONE ✓ 100%"
        kt = f"0;{a:.3f};{b:.3f};1"
        o.append(f'<text x="{px+pw-14}" y="{py+22}" text-anchor="end" font-family="{FONT}" font-size="11" font-weight="700" fill="{NEON}" opacity="0">{label}'
                 f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="{kt}" calcMode="discrete" dur="{cycle}s" repeatCount="indefinite"/></text>')
    # progress bar
    by = py + ph - 26
    o.append(f'<rect x="{px+14}" y="{by}" width="{pw-28}" height="8" fill="#141414" stroke="{DIM}"/>')
    o.append(f'<rect x="{px+15}" y="{by+1}" height="6" width="0" fill="{GREEN}">'
             f'<animate attributeName="width" values="0;{pw-30};{pw-30};0" keyTimes="0;{print_t/cycle:.3f};0.98;1" dur="{cycle}s" repeatCount="indefinite"/></rect>')

    o.append(f'<rect width="{W}" height="{H}" rx="10" fill="url(#scan)" pointer-events="none"/>')
    o.append("</svg>")
    (OUT / "header.svg").write_text("\n".join(o), encoding="utf-8")


PROJECTS = [
    {
        "name": "esp32-watch",
        "desc": "ESP32 tabanlı DIY akıllı saat projesi",
        "rows": [
            ("Stack", "ESP32 · C++ · Arduino"),
            ("Donanım", "ESP32 + ekran + pil yönetimi"),
            ("Durum", "geliştirme aşamasında ▓▓▓▓▓░░░"),
            ("Repo", "github.com/The-MakleyN/esp32-watch"),
        ],
    },
    {
        "name": "Proje-6-Yemek-Tarifi",
        "desc": "Takım çalışması · yemek tarifi uygulaması",
        "rows": [
            ("Stack", "Python"),
            ("Tür", "ekip projesi (BizlikIs)"),
            ("Repo", "github.com/The-MakleyN/Proje-6-Yemek-Tarifi"),
        ],
    },
]


def projects():
    W = 900
    lh = 26
    h = 70
    for p in PROJECTS:
        h += 46 + len(p["rows"]) * lh + 18
    h += 90
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">', defs()]
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="10" fill="{PANEL}" stroke="{BORDER}"/>')
    o.append(titlebar(W, "makleyn@github: ~/projects"))
    y = 68
    o.append(f'<text x="30" y="{y}" font-family="{FONT}" font-size="15" fill="{NEON}" font-weight="700">$ <tspan fill="{TEXT}">cat projects.md</tspan></text>')
    y += 16
    delay = 0.2
    for p in PROJECTS:
        y += 30
        g = [f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur=".4s" fill="freeze"/>']
        g.append(f'<text x="30" y="{y}" font-family="{FONT}" font-size="15" font-weight="700" fill="{GREEN}">▸ {p["name"]} <tspan fill="{MUTED}" font-weight="400" font-size="13">— {p["desc"]}</tspan></text>')
        ty = y + 14
        th = len(p["rows"]) * lh
        g.append(f'<rect x="30" y="{ty}" width="{W-60}" height="{th}" fill="none" stroke="{BORDER}"/>')
        g.append(f'<line x1="150" y1="{ty}" x2="150" y2="{ty+th}" stroke="{BORDER}"/>')
        for i, (k, v) in enumerate(p["rows"]):
            ry = ty + i * lh
            if i:
                g.append(f'<line x1="30" y1="{ry}" x2="{W-30}" y2="{ry}" stroke="{BORDER}"/>')
            col = "#ffffff" if k == "Repo" else TEXT
            g.append(f'<text x="42" y="{ry+17}" font-family="{FONT}" font-size="13" fill="{MUTED}">{k}</text>')
            g.append(f'<text x="164" y="{ry+17}" font-family="{FONT}" font-size="13" fill="{col}">{v}</text>')
        g.append("</g>")
        o.append("".join(g))
        y = ty + th + 18
        delay += 0.6
    y += 24
    o.append(f'<text x="30" y="{y}" font-family="{FONT}" font-size="15" fill="{NEON}" font-weight="700">$ <tspan fill="{TEXT}">ls ~/skills</tspan></text>')
    o.append(f'<text x="30" y="{y+26}" font-family="{FONT}" font-size="13" fill="{GREEN}">esp32/  c++/  python/  arduino/  iot/  git/  <tspan fill="{NEON}">█<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>')
    o.append(f'<rect width="{W}" height="{h}" rx="10" fill="url(#scan)"/>')
    o.append("</svg>")
    (OUT / "projects.svg").write_text("\n".join(o), encoding="utf-8")


def button(fname, label):
    w = len(label) * 9 + 36
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="34" viewBox="0 0 {w} 34">
<rect x="1" y="1" width="{w-2}" height="32" fill="#ece8e0"/>
<text x="{w/2}" y="22" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="700" letter-spacing="2" fill="#0a0a0a">{label}</text>
</svg>"""
    (OUT / fname).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    header()
    projects()
    button("btn-github.svg", "GITHUB")
    button("btn-instagram.svg", "INSTAGRAM")
    button("btn-email.svg", "EMAIL")
    button("btn-linkedin.svg", "LINKEDIN")
    print("ok")
