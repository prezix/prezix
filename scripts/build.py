#!/usr/bin/env python3
"""Генерирует assets/terminal-{dark,light}.svg из ПУБЛИЧНЫХ данных GitHub (только stdlib).

Приватные репозитории не попадают никуда: используется публичный эндпоинт
/users/{user}/repos, который их не отдаёт.

Пишет оба файла только если оба запроса к API прошли успешно — при сбое
(лимит запросов, сеть) старые файлы остаются как есть и скрипт завершается
с ошибкой, чтобы это было видно в логе Action, но ничего не затирает.
"""
import html
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone

USER = os.environ.get("PROFILE_USER", "prezix")
SKIP = {USER, "github-achievements"}  # профильный и тренировочный репозитории

LANG_COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572a5",
    "C": "#8a9bb0", "C++": "#f34b7d", "C#": "#9b4f96", "Java": "#e76f00",
    "Lua": "#6c6cff", "HTML": "#e34c26", "CSS": "#9b6bff", "Go": "#00add8",
    "Rust": "#dea584", "Shell": "#89e051",
}
STACK = [
    ("React", "#61dafb"), ("TypeScript", "#3178c6"), ("CSS", "#9b6bff"),
    ("Python", "#4b8bbe"), ("Node.js", "#68a063"), ("C", "#8a9bb0"),
    ("C++", "#f34b7d"), ("C#", "#9b4f96"), ("Java", "#e76f00"),
    ("Lua", "#6c6cff"), ("gLua", "#00b4ff"), ("Blender", "#f5792a"),
    ("PyTorch", "#ee4c2c"), ("Photoshop", "#31a8ff"),
]

# Палитры для тёмной и светлой темы GitHub (переключение через <picture>
# + prefers-color-scheme в README.md — см. scripts/render_banner.py).
PALETTES = {
    "dark": dict(bg="#0d1117", panel="#161b22", border="#30363d",
                 fg="#e6edf3", dim="#7d8590", accent="#22d3ee"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", border="#d0d7de",
                  fg="#1f2328", dim="#59636e", accent="#0b7285"),
}
CHAR_W = 8.4  # ширина символа моноширинного шрифта при 14px


def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-builder"},
    )
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def esc(s):
    return html.escape(str(s), quote=True)


def typewriter(width, begin, dur, steps):
    """SMIL: ступенчатое раскрытие clip-rect — эффект набора текста."""
    vals = ";".join(f"{width * i / steps:.1f}" for i in range(steps + 1))
    kt = ";".join(f"{i / steps:.4f}" for i in range(steps + 1))
    return (f'<animate attributeName="width" values="{vals}" keyTimes="{kt}" '
            f'calcMode="discrete" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>')


def render(theme, user, repos, langs_top, total, years, last):
    pal = PALETTES[theme]
    BG, PANEL, BORDER, FG, DIM, ACCENT = (pal[k] for k in ("bg", "panel", "border", "fg", "dim", "accent"))

    W, LH, X = 820, 24, 28
    body = []      # элементы SVG
    clips = []     # clipPath'ы
    y = 84
    t = 0.6        # текущее время анимации
    cid = 0

    def command(cmd):
        nonlocal y, t, cid
        cid += 1
        w = (len(cmd) + 2) * CHAR_W + 6
        dur = max(0.4, len(cmd) * 0.045)
        clips.append(f'<clipPath id="c{cid}"><rect x="{X}" y="{y - 16}" width="0" height="22">'
                     f'{typewriter(w, t, dur, len(cmd) + 2)}</rect></clipPath>')
        body.append(f'<g clip-path="url(#c{cid})"><text x="{X}" y="{y}" class="m">'
                    f'<tspan fill="{ACCENT}">❯</tspan> <tspan fill="{FG}">{esc(cmd)}</tspan></text></g>')
        t += dur + 0.25
        y += LH

    def fade(svg_inner, dur=0.35):
        nonlocal t
        body.append(f'<g opacity="0">{svg_inner}'
                    f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" '
                    f'dur="{dur}s" fill="freeze"/></g>')
        t += 0.18

    # --- whoami
    command("whoami")
    fade(f'<text x="{X + 16}" y="{y}" class="m" fill="{FG}">{esc(USER)} '
         f'<tspan fill="{DIM}">·</tspan> <tspan fill="{ACCENT}">{esc(user.get("bio") or "")}</tspan></text>')
    y += LH + 10

    # --- stats
    command("cat ~/stats")
    def stat(label, value, color=FG):
        nonlocal y
        fade(f'<text x="{X + 16}" y="{y}" class="m"><tspan fill="{DIM}" x="{X + 16}">{esc(label)}</tspan>'
             f'<tspan fill="{color}" x="{X + 16 + 14 * CHAR_W}">{esc(value)}</tspan></text>')
        y += LH
    stat("public repos", str(len(repos)), ACCENT)
    stat("followers", str(user["followers"]))
    stat("on github", f"{years:.1f} years")
    stat("last push", last)
    y += 4

    # --- языковая полоса
    fade(f'<text x="{X + 16}" y="{y}" class="m" fill="{DIM}">languages <tspan opacity="0.6">(public repos)</tspan></text>')
    y += 12
    bar_x, bar_w, bar_h = X + 16, W - 2 * X - 32, 12
    clips.append(f'<clipPath id="bar{theme}"><rect x="{bar_x}" y="{y}" width="0" height="{bar_h}" rx="6">'
                 f'<animate attributeName="width" from="0" to="{bar_w}" begin="{t:.2f}s" dur="0.9s" '
                 f'fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect></clipPath>')
    seg = [f'<g clip-path="url(#bar{theme})">']
    cx = bar_x
    for name, n in langs_top:
        w = bar_w * n / total
        seg.append(f'<rect x="{cx:.1f}" y="{y}" width="{w + 0.5:.1f}" height="{bar_h}" '
                   f'fill="{LANG_COLORS.get(name, "#6e7681")}"/>')
        cx += w
    seg.append('</g>')
    body.append("".join(seg))
    t += 0.9
    y += bar_h + 20
    lx = bar_x
    items = []
    for name, n in langs_top:
        label = f"{name} {round(100 * n / total)}%"
        items.append(f'<circle cx="{lx + 4}" cy="{y - 4}" r="4" fill="{LANG_COLORS.get(name, "#6e7681")}"/>'
                     f'<text x="{lx + 14}" y="{y}" class="s" fill="{DIM}">{esc(label)}</text>')
        lx += 14 + len(label) * 7.4 + 16
    fade("".join(items))
    y += LH + 14

    # --- стек
    command("ls ~/stack")
    px, py = X + 16, y - 6
    pills = []
    for name, color in STACK:
        w = len(name) * 8.2 + 30
        if px + w > W - X:
            px, py = X + 16, py + 32
        pills.append(f'<g><rect x="{px:.1f}" y="{py}" width="{w:.1f}" height="24" rx="12" '
                     f'fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-opacity="0.55"/>'
                     f'<circle cx="{px + 13:.1f}" cy="{py + 12}" r="3.5" fill="{color}"/>'
                     f'<text x="{px + 24:.1f}" y="{py + 16}" class="s" fill="{FG}">{esc(name)}</text></g>')
        px += w + 8
    fade("".join(pills), 0.6)
    y = py + 24 + 30

    # --- курсор
    cid += 1
    body.append(f'<text x="{X}" y="{y}" class="m"><tspan fill="{ACCENT}">❯</tspan> '
                f'<tspan fill="{ACCENT}" opacity="0">█<animate attributeName="opacity" values="0;1;1;0;0" '
                f'keyTimes="0;0.01;0.5;0.51;1" dur="1.1s" begin="{t:.2f}s" repeatCount="indefinite"/></tspan></text>')
    H = y + 28

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{USER} terminal profile">
<style>
.m{{font:14px ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace;white-space:pre}}
.s{{font:12.5px ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace}}
.t{{font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
</style>
<defs>
<linearGradient id="glow{theme}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0.35"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0.35"/></linearGradient>
{"".join(clips)}
</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="url(#glow{theme})" stroke-width="1.5"/>
<path d="M0.5 36 H{W - 0.5}" stroke="{BORDER}"/>
<path d="M12 0.5 H{W - 12} A11.5 11.5 0 0 1 {W - 0.5} 12 V36 H0.5 V12 A11.5 11.5 0 0 1 12 0.5Z" fill="{PANEL}"/>
<circle cx="24" cy="18" r="6" fill="#ff5f56"/><circle cx="46" cy="18" r="6" fill="#ffbd2e"/><circle cx="68" cy="18" r="6" fill="#27c93f"/>
<text x="{W / 2}" y="22" text-anchor="middle" class="t" fill="{DIM}">{esc(USER)}@github: ~</text>
{"".join(body)}
</svg>
'''


def main():
    try:
        user = api(f"/users/{USER}")
        repos = [r for r in api(f"/users/{USER}/repos?per_page=100&type=owner")
                 if not r["fork"] and r["name"] not in SKIP]
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"GitHub API unavailable ({e}); leaving existing assets untouched.", file=sys.stderr)
        sys.exit(1)

    langs = Counter(r["language"] for r in repos if r["language"])
    total = sum(langs.values()) or 1
    top = langs.most_common(5)
    other = total - sum(n for _, n in top)
    if other > 0:
        top.append(("other", other))

    since = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    years = (datetime.now(timezone.utc) - since).days / 365.25
    last = max((r["pushed_at"] for r in repos), default=user["created_at"])
    last = datetime.fromisoformat(last.replace("Z", "+00:00")).strftime("%Y-%m-%d")

    os.makedirs("assets", exist_ok=True)
    sizes = []
    for theme in ("dark", "light"):
        svg = render(theme, user, repos, top, total, years, last)
        path = f"assets/terminal-{theme}.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        sizes.append(f"{theme}={len(svg.splitlines())}L")

    print(f"ok: {len(repos)} public repos, {len(top)} langs, {', '.join(sizes)}")


if __name__ == "__main__":
    main()
