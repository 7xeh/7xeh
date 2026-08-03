#!/usr/bin/env python3
"""Regenerate the Featured Work table in README.md from live GitHub data.

Curated repo list lives in PROJECTS below -- add a repo there and it shows up.
Everything else (description, stars, latest release, last push) is pulled from
the API, so the table can't drift out of sync with reality.

Run: python .github/scripts/update_readme.py
Set GITHUB_TOKEN to avoid the 60 req/hr unauthenticated rate limit.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

OWNER = "7xeh"
README = Path(__file__).resolve().parents[2] / "README.md"

START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"

PROJECTS: list[dict[str, str]] = [
    {"repo": "SpicyLyricTranslator"},
    {"repo": "SpicyThemes"},
    {"repo": "SpotifyModernEQ"},
    {"repo": "CarX-Blender-Tools"},
    {"repo": "NightyScripts", "summary": "Automation scripts for the Nighty selfbot."},
]

VERSION_TAG = re.compile(r"^v?\d+(\.\d+){1,3}$")


def api(path: str) -> dict | None:
    """GET an API path. Returns None on 404, raises on anything else."""
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


def build_row(project: dict[str, str]) -> str:
    name = project["repo"]

    repo = api(f"/repos/{OWNER}/{name}")
    if repo is None:
        raise SystemExit(f"{OWNER}/{name} does not exist -- fix the PROJECTS list.")

    summary = project.get("summary") or repo.get("description") or "—"
    summary = summary.replace("|", "\\|").strip()

    release = api(f"/repos/{OWNER}/{name}/releases/latest")
    tag = (release or {}).get("tag_name", "")
    latest = f"`{tag}`" if VERSION_TAG.match(tag) else "—"

    updated = repo["pushed_at"][:10]
    stars = repo["stargazers_count"]

    return (
        f"| [**{name}**]({repo['html_url']}) | {summary} | {latest} | {stars} | `{updated}` |"
    )


def build_table() -> str:
    rows = [build_row(project) for project in PROJECTS]
    return "\n".join(
        [
            "| Project | What it does | Latest | ★ | Updated |",
            "| :--- | :--- | :--- | ---: | :--- |",
            *rows,
        ]
    )


def main() -> int:
    readme = README.read_text(encoding="utf-8")

    start = readme.find(START)
    end = readme.find(END)
    if start == -1 or end == -1:
        raise SystemExit(f"Missing {START} / {END} markers in {README.name}.")

    table = build_table()
    updated = f"{readme[:start]}{START}\n{table}\n{readme[end:]}"

    if updated == readme:
        print("README already up to date.")
        return 0

    README.write_text(updated, encoding="utf-8", newline="\n")
    print("README project table refreshed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
