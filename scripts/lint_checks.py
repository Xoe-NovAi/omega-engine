#!/usr/bin/env python3
"""lint_checks.py — Omega Engine code-quality gates.

Gates (aligns with docs/CODE_QUALITY.md):
  1. anyio purity:   no bare asyncio/trio imports in first-party scripts
  2. exceptions:     no bare `except:` / `except Exception: pass`
  3. torch ban:      no first-party torch/torchvision imports

Run:  make lint        (or)  python3 scripts/lint_checks.py
Exit 1 on any violation. Structured output only.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

ANYIO_BAD = re.compile(r"^\s*(import|from)\s+(asyncio|trio)\b", re.M)
BARE_EXCEPT = re.compile(r"^\s*except\s*:\s*(#.*)?$")
BARE_EXCEPT_ERR = re.compile(r"^\s*except\s+Exception\s*:\s*(#.*)?$")
TORCH_BAD = re.compile(r"^\s*(import|from)\s+(torch|torchvision)\b", re.M)


def scan() -> list[str]:
    problems: list[str] = []
    for p in sorted(SCRIPTS.rglob("*.py")):
        rel = p.relative_to(REPO)
        lines = p.read_text().splitlines()
        text = "\n".join(lines)
        for m in ANYIO_BAD.finditer(text):
            problems.append(f"{rel}: bare asyncio/trio ({m.group(0)!r})")
        for i, l in enumerate(lines):
            if BARE_EXCEPT.match(l):
                problems.append(f"{rel}:{i+1}: bare except:")
            if BARE_EXCEPT_ERR.match(l):
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if nxt in ("pass", "continue", "break"):
                    problems.append(f"{rel}:{i+1}: bare except Exception: -> {nxt}")
        for m in TORCH_BAD.finditer(text):
            problems.append(f"{rel}: torch import ({m.group(0)!r})")
    return problems


def main() -> int:
    problems = scan()
    if problems:
        print("\n".join(f"  ✗ {p}" for p in problems))
        print("FAIL: lint gates violated — see docs/CODE_QUALITY.md")
        return 1
    print("  ✓ anyio purity")
    print("  ✓ no bare exceptions")
    print("  ✓ no torch")
    return 0


if __name__ == "__main__":
    sys.exit(main())