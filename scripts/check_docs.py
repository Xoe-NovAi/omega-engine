"""Validate internal Markdown links and heading anchors."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")


def _slug(value: str) -> str:
    value = unquote(value).strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    return re.sub(r"\s+", "-", value)


def _markdown_files(root: Path) -> list[Path]:
    tracked = subprocess.check_output(
        ["git", "-c", "core.quotePath=false", "ls-files", "-z", "*.md"],
        cwd=root,
    )
    files = {root / item.decode() for item in tracked.split(b"\0") if item}
    files.update((root / "docs").rglob("*.md"))
    files.add(root / "README.md")
    return sorted(path for path in files if path.exists())


def _anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = HEADING_RE.match(line)
        if match:
            anchors.add(_slug(match.group(1)))
    return anchors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures: list[str] = []
    checked = 0
    for source in _markdown_files(root):
        text = source.read_text(encoding="utf-8", errors="replace")
        for raw_target in LINK_RE.findall(text):
            target = raw_target.split("#", 1)[0].strip()
            fragment = raw_target.split("#", 1)[1] if "#" in raw_target else ""
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            checked += 1
            destination = (source.parent / target).resolve()
            if not destination.exists():
                failures.append(f"{source.relative_to(root)} -> missing path: {raw_target}")
                continue
            if fragment and destination.suffix.lower() == ".md":
                normalized = _slug(fragment)
                if normalized not in _anchors(destination):
                    failures.append(
                        f"{source.relative_to(root)} -> missing anchor: {raw_target}"
                    )
    print(f"documentation links checked: {checked}")
    if failures:
        print("\n".join(failures))
        return 1
    print("documentation links: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
