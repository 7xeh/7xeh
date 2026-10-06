#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import projects as project_list
import render

OWNER = "7xeh"
ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
ASSETS = ROOT / "assets"

INTRO = "Sup nerd. I build Spicetify extensions, Blender tooling, and Windows automation scripts."
TOOLBOX = ",".join(
    "ts js py react css nodejs bun blender windows powershell vscode git githubactions cloudflare".split()
)
TOOLBOX_ALT = (
    "TypeScript, JavaScript, Python, React, CSS, Node.js, Bun, Blender, Windows, "
    "PowerShell, VS Code, Git, GitHub Actions, Cloudflare"
)

VERSION_TAG = re.compile(r"^v?\d+(\.\d+){1,3}$")


def api(path: str) -> dict | list | None:
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{OWNER}-readme-updater",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def picture(dark: str, light: str, alt: str, *, width: str | None = None, href: str | None = None) -> str:
    size = f' width="{width}"' if width else ""
    tag = (
        "<picture>"
        f'<source media="(prefers-color-scheme: dark)" srcset="{dark}" />'
        f'<source media="(prefers-color-scheme: light)" srcset="{light}" />'
        f'<img alt="{alt}" src="{dark}"{size} />'
        "</picture>"
    )
    return f'<a href="{href}">{tag}</a>' if href else tag


def asset(name: str, alt: str, **kwargs) -> str:
    return picture(f"./assets/{name}-dark.svg", f"./assets/{name}-light.svg", alt, **kwargs)


def render_both(name: str, build) -> None:
    for mode, theme in render.THEMES.items():
        render.write(ASSETS / f"{name}-{mode}.svg", build(theme))


def build_card(project: dict[str, str]) -> str:
    name = project["repo"]

    repo = api(f"/repos/{OWNER}/{name}")
    if repo is None:
        raise SystemExit(f"{OWNER}/{name} does not exist -- fix projects.toml.")

    summary = (project.get("summary") or repo.get("description") or "").strip() or "—"
    release = api(f"/repos/{OWNER}/{name}/releases/latest")
    tag = (release or {}).get("tag_name", "")

    render_both(
        f"cards/{name}",
        lambda theme: render.card(
            theme,
            name=name,
            summary=summary,
            language=repo.get("language"),
            version=tag if VERSION_TAG.match(tag) else None,
            stars=repo["stargazers_count"],
            pushed_at=repo["pushed_at"],
        ),
    )
    return asset(f"cards/{name}", f"{name}: {summary}", width="49%", href=repo["html_url"])


def build_projects() -> str:
    listed = project_list.load()
    cards = [build_card(project) for project in listed]

    keep = {f"{p['repo']}-{mode}.svg" for p in listed for mode in render.THEMES}
    for stale in (ASSETS / "cards").glob("*.svg"):
        if stale.name not in keep:
            stale.unlink()

    rows = ["\n".join(cards[i:i + 2]) for i in range(0, len(cards), 2)]
    return '<p align="center">\n' + "\n<br />\n".join(rows) + "\n</p>"


def build_readme() -> str:
    divider = asset("divider", "", width="100%")
    toolbox = f'<img alt="{TOOLBOX_ALT}" src="https://skillicons.dev/icons?i={TOOLBOX}&perline=14" />'
    return f"""<a href="https://7xeh.dev"><img alt="7Softworks" src="./assets/banner.webp" width="100%" /></a>

<p align="center">{INTRO}</p>

<p align="center">
  <a href="https://7xeh.dev"><img alt="Website" src="https://img.shields.io/badge/7xeh.dev-ff3ea5?style=for-the-badge&logo=googlechrome&logoColor=white&labelColor=1d0f22" /></a>
  <a href="mailto:7xeh@7xeh.dev"><img alt="Email" src="https://img.shields.io/badge/7xeh@7xeh.dev-d946ef?style=for-the-badge&logo=maildotru&logoColor=white&labelColor=1d0f22" /></a>
  <img alt="Profile views" src="https://komarev.com/ghpvc/?username={OWNER}&style=for-the-badge&color=8b5cf6&label=views" />
</p>

{divider}

### ✦ Featured work

{build_projects()}

### ✦ Toolbox

<p align="center">
  {toolbox}
</p>

{divider}

<p align="center">
  <sub>Want to collaborate? Open an issue or PR on the relevant repo — that keeps the discussion next to the code.<br />Anything else: <a href="mailto:7xeh@7xeh.dev">7xeh@7xeh.dev</a></sub>
</p>
"""


def main() -> int:
    render_both("divider", render.divider)

    readme = README.read_text(encoding="utf-8") if README.exists() else ""
    updated = build_readme()

    if updated == readme:
        print("README already up to date.")
        return 0

    README.write_text(updated, encoding="utf-8", newline="\n")
    print("README refreshed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
