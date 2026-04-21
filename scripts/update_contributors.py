#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


START_MARKER = "<!-- contributors:start -->"
END_MARKER = "<!-- contributors:end -->"


def fetch_display_name(login: str, token: str | None) -> str | None:
    if not token:
        return None

    req = urllib.request.Request(
        f"https://api.github.com/users/{login}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
    except urllib.error.URLError:
        return None

    name = (data.get("name") or "").strip()
    return name or None


def render_entry(login: str, display_name: str | None) -> str:
    url = f"https://github.com/{login}"
    if display_name and display_name.casefold() != login.casefold():
        return f"- [{display_name}]({url}) (@{login})"
    return f"- [{login}]({url})"


def extract_block_lines(text: str) -> tuple[int, int, list[str]]:
    start = text.find(START_MARKER)
    end = text.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise ValueError("Contributor markers are missing or malformed in book/index.md")

    block_start = start + len(START_MARKER)
    current_block = text[block_start:end]
    lines = [line.strip() for line in current_block.splitlines() if line.strip()]
    return block_start, end, lines


def login_from_entry(line: str) -> str:
    match = re.search(r"\(@([^)]+)\)", line)
    if match:
        return match.group(1).casefold()

    match = re.search(r"https://github\.com/([A-Za-z0-9-]+)", line)
    if match:
        return match.group(1).casefold()

    return line.casefold()


def main() -> int:
    login = os.environ["CONTRIBUTOR_LOGIN"].strip()
    if not login:
        raise ValueError("CONTRIBUTOR_LOGIN is required")

    display_name = os.environ.get("CONTRIBUTOR_DISPLAY_NAME", "").strip() or None
    if display_name is None:
        display_name = fetch_display_name(login, os.environ.get("GITHUB_TOKEN"))

    index_path = Path(os.environ.get("INDEX_PATH", "book/index.md"))
    text = index_path.read_text()
    block_start, block_end, lines = extract_block_lines(text)

    existing_logins = {login_from_entry(line) for line in lines}
    if login.casefold() in existing_logins:
        print(f"Contributor @{login} already listed")
        return 0

    lines.append(render_entry(login, display_name))
    lines.sort(key=login_from_entry)

    new_block = "\n" + "\n".join(lines) + "\n"
    updated = text[:block_start] + new_block + text[block_end:]
    index_path.write_text(updated)
    print(f"Added contributor @{login}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
