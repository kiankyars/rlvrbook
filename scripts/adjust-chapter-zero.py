#!/usr/bin/env python3

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


CHAPTER_SPAN_RE = re.compile(
    r'(<span class="chapter-number">)(\d+)(</span>)'
)
TITLE_RE = re.compile(r"(<title>)(\d+)(&nbsp;\s*)")


def decrement(match: re.Match[str]) -> str:
    number = int(match.group(2))
    return f"{match.group(1)}{number - 1}{match.group(3)}"


def rewrite_html(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = CHAPTER_SPAN_RE.sub(decrement, original)
    updated = TITLE_RE.sub(decrement, updated)

    if updated == original:
        return False

    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    output_dir = os.environ.get("QUARTO_PROJECT_OUTPUT_DIR")
    if not output_dir:
        print("adjust-chapter-zero: QUARTO_PROJECT_OUTPUT_DIR is unset", file=sys.stderr)
        return 1

    root = Path(output_dir)
    if not root.is_absolute():
        root = Path.cwd() / root

    if not root.exists():
        return 0

    changed = 0
    for html_path in sorted(root.rglob("*.html")):
        if rewrite_html(html_path):
            changed += 1

    print(f"adjust-chapter-zero: updated {changed} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
