#!/usr/bin/env python3
"""Генерирует assets/banner-{dark,light}.svg — декоративный, без данных из API.

Не запускается в CI: баннер статичный (имя + тэглайн), перегенерировать
вручную при правке текста/цветов:  python -I scripts/render_banner.py
"""
import xml.dom.minidom as minidom

NAME = "prezix"
TAGLINE = "a little bit coding here"

PALETTES = {
    "dark": dict(
        bg0="#0b1220", bg1="#0d1117",
        ink0="#22d3ee", ink1="#a78bfa",
        scan="#22d3ee", scan_op="0.22",
        grid="#22d3ee", grid_op="0.06",
        subtitle="#9db4c8",
        accent="#22d3ee", accent_op="0.8",
        border_op="0.35",
        deco2="#a78bfa", deco2_op="0.5",
    ),
    "light": dict(
        bg0="#f8fafc", bg1="#ffffff",
        ink0="#0b7285", ink1="#7c3aed",
        scan="#0b7285", scan_op="0.12",
        grid="#0b7285", grid_op="0.07",
        subtitle="#475569",
        accent="#0b7285", accent_op="0.85",
        border_op="0.35",
        deco2="#7c3aed", deco2_op="0.45",
    ),
}


def render(theme):
    p = PALETTES[theme]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="820" height="200" viewBox="0 0 820 200" role="img" aria-label="{NAME} — {TAGLINE}">
<style>
.big{{font:800 84px ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace;letter-spacing:-2px}}
.sub{{font:15px ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace;letter-spacing:1px}}
.tag{{font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:2px}}
</style>
<defs>
<linearGradient id="bg{theme}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p['bg0']}"/><stop offset="1" stop-color="{p['bg1']}"/></linearGradient>
<linearGradient id="ink{theme}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p['ink0']}"/><stop offset="1" stop-color="{p['ink1']}"/></linearGradient>
<linearGradient id="scan{theme}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p['scan']}" stop-opacity="0"/><stop offset="0.5" stop-color="{p['scan']}" stop-opacity="{p['scan_op']}"/><stop offset="1" stop-color="{p['scan']}" stop-opacity="0"/></linearGradient>
<pattern id="grid{theme}" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{p['grid']}" stroke-opacity="{p['grid_op']}"/></pattern>
<clipPath id="card{theme}"><rect width="820" height="200" rx="14"/></clipPath>
<clipPath id="type{theme}"><rect x="48" y="138" width="0" height="26"><animate attributeName="width" values="0;10;20;30;40;50;60;70;80;90;100;110;120;130;140;150;160;170;180;190;200;210;220;230;240" keyTimes="0.0000;0.1200;0.1367;0.1533;0.1700;0.1867;0.2033;0.2200;0.2367;0.2533;0.2700;0.2867;0.3033;0.3200;0.3367;0.3533;0.3700;0.3867;0.4033;0.4200;0.4367;0.4533;0.4700;0.4867;0.5033" calcMode="discrete" dur="6s" fill="freeze"/></rect></clipPath>
</defs>
<g clip-path="url(#card{theme})">
<rect width="820" height="200" fill="url(#bg{theme})"/>
<rect width="820" height="200" fill="url(#grid{theme})"/>
<rect y="-60" width="820" height="60" fill="url(#scan{theme})"><animate attributeName="y" values="-60;200" dur="4.5s" repeatCount="indefinite"/></rect>
<!-- «глитч»: смещённые копии имени -->
<text x="46" y="118" class="big" fill="{p['ink0']}" opacity="0.0">{NAME}<animate attributeName="opacity" values="0;0;0.55;0;0;0.4;0;0" keyTimes="0;0.70;0.71;0.73;0.90;0.91;0.93;1" dur="7s" repeatCount="indefinite"/><animate attributeName="x" values="46;46;41;46;46;52;46;46" keyTimes="0;0.70;0.71;0.73;0.90;0.91;0.93;1" dur="7s" repeatCount="indefinite"/></text>
<text x="46" y="118" class="big" fill="#f472b6" opacity="0.0">{NAME}<animate attributeName="opacity" values="0;0;0.5;0;0;0.4;0;0" keyTimes="0;0.70;0.71;0.73;0.90;0.91;0.93;1" dur="7s" repeatCount="indefinite"/><animate attributeName="x" values="46;46;51;46;46;40;46;46" keyTimes="0;0.70;0.71;0.73;0.90;0.91;0.93;1" dur="7s" repeatCount="indefinite"/></text>
<text x="46" y="118" class="big" fill="url(#ink{theme})">{NAME}</text>
<g clip-path="url(#type{theme})"><text x="48" y="157" class="sub" fill="{p['subtitle']}">{TAGLINE}</text></g>
<rect x="48" y="141" width="9" height="19" fill="{p['accent']}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/><animate attributeName="x" values="48;58;68;78;88;98;108;118;128;138;148;158;168;178;188;198;208;218;228;238;248;258;268;278;288" keyTimes="0.0000;0.1200;0.1367;0.1533;0.1700;0.1867;0.2033;0.2200;0.2367;0.2533;0.2700;0.2867;0.3033;0.3200;0.3367;0.3533;0.3700;0.3867;0.4033;0.4200;0.4367;0.4533;0.4700;0.4867;0.5033" calcMode="discrete" dur="6s" fill="freeze"/></rect>
<text x="48" y="36" class="tag" fill="{p['accent']}" fill-opacity="{p['accent_op']}">// PREZIX.EXE · SESSION OPEN</text>
<g transform="translate(700,40)" fill="none" stroke="{p['accent']}" stroke-opacity="0.35" stroke-width="1.5">
<path d="M0 30 L20 10 L40 30 L20 50Z"><animateTransform attributeName="transform" type="rotate" from="0 20 30" to="360 20 30" dur="18s" repeatCount="indefinite"/></path>
<path d="M60 90 L90 90 M75 75 L75 105" stroke="{p['deco2']}" stroke-opacity="{p['deco2_op']}"/>
<circle cx="75" cy="30" r="3" fill="{p['accent']}" stroke="none"><animate attributeName="opacity" values="1;0.2;1" dur="2.4s" repeatCount="indefinite"/></circle>
</g>
</g>
<rect x="0.75" y="0.75" width="818.5" height="198.5" rx="13.5" fill="none" stroke="{p['accent']}" stroke-opacity="{p['border_op']}"/>
</svg>
'''


def main():
    for theme in ("dark", "light"):
        svg = render(theme)
        minidom.parseString(svg)  # fail fast on malformed XML
        path = f"assets/banner-{theme}.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
