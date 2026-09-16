#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import projects as project_list
import update_readme

NOTIFIER_TEMPLATE = project_list.ROOT / ".github" / "templates" / "notify-profile-readme.yml"
NOTIFIER_PATH = Path(".github") / "workflows" / "notify-profile-readme.yml"


def find(projects: list[dict[str, str]], name: str) -> int:
    for index, project in enumerate(projects):
        if project["repo"].lower() == name.lower():
            return index
    raise SystemExit(f"{name} is not in {project_list.PROJECTS_FILE.name}.")


def clamp_position(position: int | None, size: int) -> int:
    if position is None or position < 1 or position > size:
        return size
    return position - 1


def cmd_list(args: argparse.Namespace) -> None:
    for number, project in enumerate(project_list.load(), start=1):
        extra = f'  (summary: "{project["summary"]}")' if project.get("summary") else ""
        print(f"{number}. {project['repo']}{extra}")


def cmd_add(args: argparse.Namespace) -> None:
    projects = project_list.load()
    if any(p["repo"].lower() == args.repo.lower() for p in projects):
        raise SystemExit(f"{args.repo} is already listed.")

    repo = update_readme.api(f"/repos/{update_readme.OWNER}/{args.repo}")
    if repo is None:
        raise SystemExit(f"{update_readme.OWNER}/{args.repo} does not exist (or is private).")

    entry = {"repo": repo["name"]}
    if args.summary:
        entry["summary"] = args.summary
    projects.insert(clamp_position(args.position, len(projects)), entry)
    project_list.save(projects)
    print(f"Added {entry['repo']}.")


def cmd_remove(args: argparse.Namespace) -> None:
    projects = project_list.load()
    removed = projects.pop(find(projects, args.repo))
    project_list.save(projects)
    print(f"Removed {removed['repo']}.")


def cmd_move(args: argparse.Namespace) -> None:
    projects = project_list.load()
    entry = projects.pop(find(projects, args.repo))
    projects.insert(clamp_position(args.position, len(projects)), entry)
    project_list.save(projects)
    print(f"Moved {entry['repo']} to position {projects.index(entry) + 1}.")


def cmd_summary(args: argparse.Namespace) -> None:
    projects = project_list.load()
    entry = projects[find(projects, args.repo)]
    if args.text:
        entry["summary"] = args.text
    else:
        entry.pop("summary", None)
    project_list.save(projects)
    print(f"Updated summary for {entry['repo']}.")


def local_clone(name: str) -> Path | None:
    pattern = re.compile(rf"[:/]{update_readme.OWNER}/{re.escape(name)}(\.git)?/?$", re.IGNORECASE)
    for folder in project_list.ROOT.parent.iterdir():
        if not (folder / ".git").exists():
            continue
        result = subprocess.run(
            ["git", "-C", str(folder), "remote", "get-url", "origin"],
            capture_output=True, text=True,
        )
        if pattern.search(result.stdout.strip()):
            return folder
    return None


def cmd_notify(args: argparse.Namespace) -> None:
    folder = Path(args.path) if args.path else local_clone(args.repo)
    if folder is None:
        raise SystemExit(
            f"No local clone of {args.repo} found next to this repo. Pass --path, or copy\n"
            f"{NOTIFIER_TEMPLATE.relative_to(project_list.ROOT)} into that repo's .github/workflows/."
        )
    target = folder / NOTIFIER_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(NOTIFIER_TEMPLATE, target)
    print(f"Wrote {target}\nCommit and push it from that repo. It needs the PROFILE_README_TOKEN secret.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the repos shown on the profile README.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="show the current list").set_defaults(func=cmd_list, mutates=False)

    add = sub.add_parser("add", help="add a repo")
    add.add_argument("repo")
    add.add_argument("--summary", help="override the GitHub description")
    add.add_argument("--position", type=int, help="1-based slot (default: end)")
    add.set_defaults(func=cmd_add, mutates=True)

    remove = sub.add_parser("remove", help="remove a repo")
    remove.add_argument("repo")
    remove.set_defaults(func=cmd_remove, mutates=True)

    move = sub.add_parser("move", help="change a repo's position")
    move.add_argument("repo")
    move.add_argument("position", type=int, help="1-based slot")
    move.set_defaults(func=cmd_move, mutates=True)

    summary = sub.add_parser("summary", help='set or clear ("") a summary override')
    summary.add_argument("repo")
    summary.add_argument("text")
    summary.set_defaults(func=cmd_summary, mutates=True)

    notify = sub.add_parser("notify", help="install the instant-update workflow into a local clone")
    notify.add_argument("repo")
    notify.add_argument("--path", help="path to the clone (default: auto-detect sibling folder)")
    notify.set_defaults(func=cmd_notify, mutates=False)

    for command in (add, remove, move, summary):
        command.add_argument("--render", action="store_true", help="rebuild README.md now")

    args = parser.parse_args()
    args.func(args)
    if args.mutates and args.render:
        update_readme.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
