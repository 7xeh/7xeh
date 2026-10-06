from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

SANS = "'Segoe UI Variable Display','Segoe UI',-apple-system,BlinkMacSystemFont,'Inter',ui-sans-serif,system-ui,sans-serif"
MONO = "ui-monospace,'Cascadia Code','JetBrains Mono',SFMono-Regular,Consolas,monospace"

THEMES = {
    "dark": {
        "bg": "#0c0510",
        "card": "#130a17",
        "border": "#2f1b35",
        "text": "#fdf2fa",
        "muted": "#b39ab0",
        "subtle": "#6f5670",
        "pill": "#1d0f22",
        "accent": "#ff3ea5",
        "accent2": "#d946ef",
        "accent3": "#8b5cf6",
    },
    "light": {
        "bg": "#fff7fb",
        "card": "#ffffff",
        "border": "#f0dbe8",
        "text": "#1a0d17",
        "muted": "#6b5265",
        "subtle": "#a58d9f",
        "pill": "#fcedf5",
        "accent": "#d6136f",
        "accent2": "#a21caf",
        "accent3": "#6d28d9",
    },
}

LANG_COLORS = {
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Python": "#3572a5",
    "CSS": "#663399",
    "SCSS": "#c6538c",
    "HTML": "#e34c26",
    "PowerShell": "#012456",
    "Shell": "#89e051",
    "Batchfile": "#c1f12e",
    "C#": "#178600",
    "C++": "#f34b7d",
    "C": "#555555",
    "Lua": "#000080",
    "Rust": "#dea584",
    "Go": "#00add8",
    "GLSL": "#5686a5",
    "AutoHotkey": "#6594b9",
}
OTHER_COLOR = "#8b8aa0"

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def lang_color(name: str | None, theme: dict) -> str:
    color = LANG_COLORS.get(name or "", OTHER_COLOR)
    if theme is THEMES["dark"] and color in ("#012456", "#000080", "#555555"):
        return "#5b8def"
    return color


def write(path: Path, svg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cleaned = "\n".join(line.rstrip() for line in svg.strip().splitlines()) + "\n"
    path.write_text(cleaned, encoding="utf-8", newline="\n")


def wrap(text: str, width: int, lines: int) -> list[str]:
    words, out, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= width:
            current = candidate
            continue
        out.append(current)
        current = word
        if len(out) == lines:
            break
    else:
        if current:
            out.append(current)
        return out[:lines]
    last = out[-1]
    out[-1] = (last[: width - 1].rstrip() + "…") if len(last) >= width else last + "…"
    return out


def relative(iso: str) -> str:
    then = datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
    days = (datetime.now(timezone.utc).date() - then).days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 30:
        return f"{days}d ago"
    if days < 365:
        return f"{days // 30}mo ago"
    return f"{days // 365}y ago"


STAR = "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"
CLOCK = "M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Zm7-3.25v2.992l2.028.812a.75.75 0 0 1-.557 1.392l-2.5-1A.751.751 0 0 1 7 8.25v-3.5a.75.75 0 0 1 1.5 0Z"
TAG = "M1 7.775V2.75C1 1.784 1.784 1 2.75 1h5.025c.464 0 .91.184 1.238.513l6.25 6.25a1.75 1.75 0 0 1 0 2.474l-5.026 5.026a1.75 1.75 0 0 1-2.474 0l-6.25-6.25A1.752 1.752 0 0 1 1 7.775Zm1.5 0c0 .066.026.13.073.177l6.25 6.25a.25.25 0 0 0 .354 0l5.025-5.025a.25.25 0 0 0 0-.354l-6.25-6.25a.25.25 0 0 0-.177-.073H2.75a.25.25 0 0 0-.25.25ZM6 5a1 1 0 1 1 0 2 1 1 0 0 1 0-2Z"
REPO = "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"


def card(theme: dict, *, name: str, summary: str, language: str | None,
         version: str | None, stars: int, pushed_at: str) -> str:
    w, h = 480, 170
    lines = wrap(summary, 60, 2)
    summary_svg = "".join(
        f'<tspan x="24" dy="{0 if i == 0 else 20}">{escape(line)}</tspan>' for i, line in enumerate(lines)
    )
    lang_svg = ""
    meta_x = 24
    if language:
        lang_svg = (
            f'<circle cx="{meta_x + 6}" cy="139" r="6" fill="{lang_color(language, theme)}"/>'
            f'<text x="{meta_x + 18}" y="144" class="sans meta">{escape(language)}</text>'
        )
        meta_x += 30 + len(language) * 7.4
    star_x = meta_x
    clock_x = star_x + 36 + len(str(stars)) * 7.4

    updated = relative(pushed_at)
    tag_x = clock_x + 36 + len(updated) * 6.6

    version_svg = ""
    if version:
        version_svg = (
            f'<path d="{TAG}" transform="translate({tag_x:.0f} 131)" fill="{theme["subtle"]}"/>'
            f'<text x="{tag_x + 22:.0f}" y="144" class="sans meta">{escape(version)}</text>'
        )

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(name)}: {escape(summary)}">
  <title>{escape(name)}</title>
  <style>
    .sans{{font-family:{SANS}}}
    .mono{{font-family:{MONO}}}
    .name{{font-size:19px;font-weight:700;fill:{theme['text']}}}
    .desc{{font-size:14px;fill:{theme['muted']}}}
    .meta{{font-size:12.5px;fill:{theme['muted']}}}
    .edge{{animation:spin 6s linear infinite}}
    @keyframes spin{{to{{stroke-dashoffset:-1300}}}}
    {REDUCED_MOTION}
  </style>
  <defs>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{theme['accent']}"/>
      <stop offset="0.5" stop-color="{theme['accent2']}"/>
      <stop offset="1" stop-color="{theme['accent3']}"/>
    </linearGradient>
    <radialGradient id="glow" cx="1" cy="0" r="1">
      <stop offset="0" stop-color="{theme['accent']}" stop-opacity="0.16"/>
      <stop offset="0.6" stop-color="{theme['accent']}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="{theme['card']}" stroke="{theme['border']}"/>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="url(#glow)"/>
  <rect class="edge" x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="url(#edge)" stroke-width="1.5" stroke-dasharray="140 1160" stroke-linecap="round"/>
  <path d="{REPO}" transform="translate(24 21)" fill="{theme['subtle']}"/>
  <text x="48" y="37" class="sans name">{escape(name)}</text>
  <text y="78" class="sans desc">{summary_svg}</text>
  <line x1="24" x2="{w - 24}" y1="116" y2="116" stroke="{theme['border']}"/>
  {lang_svg}
  <path d="{STAR}" transform="translate({star_x:.0f} 131)" fill="#e3b341"/>
  <text x="{star_x + 22:.0f}" y="144" class="sans meta">{stars}</text>
  <path d="{CLOCK}" transform="translate({clock_x:.0f} 131)" fill="{theme['subtle']}"/>
  <text x="{clock_x + 22:.0f}" y="144" class="sans meta">{updated}</text>
  {version_svg}
</svg>"""


def divider(theme: dict) -> str:
    w, h = 1000, 24
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">
  <style>.dot{{animation:slide 5s ease-in-out infinite alternate}}@keyframes slide{{to{{transform:translateX(400px)}}}}{REDUCED_MOTION}</style>
  <defs>
    <linearGradient id="line" x1="0" x2="1">
      <stop offset="0" stop-color="{theme['accent']}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{theme['accent']}" stop-opacity="0.7"/>
      <stop offset="1" stop-color="{theme['accent2']}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="0" y="11.5" width="{w}" height="1" fill="url(#line)"/>
  <circle class="dot" cx="300" cy="12" r="3" fill="{theme['accent2']}"/>
</svg>"""

