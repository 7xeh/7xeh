from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_FILE = ROOT / "projects.toml"

def load() -> list[dict[str, str]]:
    data = tomllib.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
    projects = data.get("project", [])
    for index, project in enumerate(projects, start=1):
        if not project.get("repo"):
            raise SystemExit(f"{PROJECTS_FILE.name}: entry #{index} is missing `repo`.")
    return projects


def save(projects: list[dict[str, str]]) -> None:
    blocks = []
    for project in projects:
        lines = ["[[project]]", f"repo = {json.dumps(project['repo'], ensure_ascii=False)}"]
        if project.get("summary"):
            lines.append(f"summary = {json.dumps(project['summary'], ensure_ascii=False)}")
        blocks.append("\n".join(lines))
    PROJECTS_FILE.write_text("\n\n".join(blocks) + "\n", encoding="utf-8", newline="\n")
