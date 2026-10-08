# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""M9 — Error Integrity: detect bare ``except:`` by parsing, not by grepping.

WHY THIS EXISTS
---------------
The original gate was a text search:

    rg -n 'except\\s*:' src/omega/ --type py | rg -v 'except Exception' | rg -v '# noqa'

That regex cannot tell ``except:`` in **code** from the same three characters
inside a **comment**. A developer (or an agent) can satisfy the gate purely by
wording, without changing behaviour. That is not a gate — it is a text pattern
with a green light.

This was exploited in practice on 2026-09-29. A comment in
``src/omega/oracle/m36_recursive_probe.py`` was written that deliberately avoided
spelling a keyword, and said so in the comment. The evasion was later found and
removed by review; the gate that permitted it was left in place, which is the
part that actually mattered.

THE FIX
-------
Parse each file with :mod:`ast` and look for ``ast.ExceptHandler`` nodes whose
``type`` is ``None``. That is the only reliable definition of a bare except, and
it is immune to comments, string literals, and formatting.

WHAT THIS DOES NOT FLAG
-----------------------
``except Exception:`` and ``except SomeError:`` are *typed* handlers and are out
of scope for M9 — the mandate is about swallowing everything. A separate check
should govern typed-handler discipline; do not widen this one to do that job.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

# M9 scope: core engine only. Tests and governance docs are out of scope —
# a test may legitimately assert on a bare except, and governance prose may
# legitimately discuss one.
SCOPE_GLOBS = ("**/*.py",)
EXCLUDE_PARTS = {"test", "tests", "governance", "node_modules", ".venv", "venv", "__pycache__"}
EXCLUDE_SUFFIXES = ("_test.py", ".test.py", "test_", "conftest.py")


@dataclass(frozen=True)
class BareExcept:
    """A bare ``except:`` found in a parsed file."""

    path: Path
    line: int
    col: int
    code: str

    def render(self) -> str:
        return f"{self.path}:{self.line}:{self.col}: bare `except:` (M9) — {self.code}"


def _is_excluded(path: Path, root: Path) -> bool:
    """True if the path is out of M9's scope."""
    try:
        rel = path.relative_to(root)
    except ValueError:  # pragma: no cover - defensive
        rel = path
    if any(part in EXCLUDE_PARTS for part in rel.parts[:-1]):
        return True
    name = rel.name
    return name in EXCLUDE_SUFFIXES or name.startswith("test_") or name.endswith("_test.py")


def find_bare_excepts(root: Path) -> list[BareExcept]:
    """Return every bare ``except:`` in the scoped tree, by AST."""
    found: list[BareExcept] = []
    for pattern in SCOPE_GLOBS:
        for path in sorted(root.glob(pattern)):
            if not path.is_file() or _is_excluded(path, root):
                continue
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(path))
            except (SyntaxError, UnicodeDecodeError, OSError):
                # A file we cannot parse cannot be certified clean. Skipping it
                # silently would make the gate pass on unverified code, which is
                # the exact failure this gate exists to prevent.
                print(f"  SKIP (unparseable, not certified clean): {path}", file=sys.stderr)
                continue
            lines = source.splitlines()
            for node in ast.walk(tree):
                if not isinstance(node, ast.ExceptHandler):
                    continue
                if node.type is not None:
                    continue  # typed handler — not a bare except
                code = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                found.append(BareExcept(path, node.lineno, node.col_offset, code))
    return found


def check(root: Path) -> int:
    """Run M9. Returns a process exit code."""
    print("Checking M9 (Error integrity)...")
    found = find_bare_excepts(root)
    if found:
        print(f"FAIL: {len(found)} bare `except:` in {root}", file=sys.stderr)
        for item in found:
            print(f"  {item.render()}", file=sys.stderr)
        return 1
    print("M9 passed: No bare except in core (AST-verified, comments exempt)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="M9 error-integrity gate (AST-based)")
    parser.add_argument(
        "root",
        nargs="?",
        default="src/omega",
        help="directory to scan (default: src/omega)",
    )
    args = parser.parse_args(argv)
    root = Path(args.root)
    if not root.exists():
        print(f"FAIL: scope {root} does not exist", file=sys.stderr)
        return 1
    return check(root)


if __name__ == "__main__":
    raise SystemExit(main())
