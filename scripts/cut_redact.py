#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0
"""P0-2 exposure redaction — cut-time scrub of infrastructure identifiers.

Rewrites literal identity strings (tailnet IDs, node IPs, mount paths,
personal emails, machine hostnames) to RFC-2606-safe placeholders in a
target tree. The working tree on `internal` KEEPS the real values (they
are live runtime config: hub allowlists, MagicDNS hostnames, mount
defaults). This script runs ONLY on the public cut product.

Patterns live in `scripts/cut_redaction_patterns.tsv` (INTERNAL-ONLY —
excluded from the public cut; this script ships but is inert without it).
Format: one `literal<TAB>replacement` pair per line, # comments. Order
matters: first match wins per occurrence, so specific strings precede
their prefixes.

Usage:
    python3 scripts/cut_redact.py --check  <tree>   # report hits, exit 1 if any
    python3 scripts/cut_redact.py --apply  <tree>   # rewrite in place

Exit codes: 0 clean / applied, 1 hits remain (--check), 2 config error (M23).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PATTERNS_FILE = REPO_ROOT / "scripts" / "cut_redaction_patterns.tsv"

SKIP_DIRS = {".git", "dist", "build", ".venv", "node_modules", "__pycache__"}
SKIP_FILES = {"cut_redaction_patterns.tsv"}
BINARY_EXTS = {
    ".whl", ".gguf", ".sqlite", ".db", ".png", ".jpg", ".gif", ".ico",
    ".zip", ".gz", ".tar", ".xz", ".so", ".bin", ".pdf", ".pkl", ".onnx",
}


def load_patterns(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        print(f"[FATAL] patterns file missing: {path} (internal-only file; "
              f"redaction cannot run on this tree)", file=sys.stderr)
        sys.exit(2)
    patterns: list[tuple[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2 or not parts[0] or parts[0] == parts[1]:
            print(f"[FATAL] malformed pattern line: {raw!r}", file=sys.stderr)
            sys.exit(2)
        patterns.append((parts[0], parts[1]))
    if not patterns:
        print("[FATAL] patterns file contains no entries", file=sys.stderr)
        sys.exit(2)
    return patterns


def iter_text_files(tree: Path):
    for p in sorted(tree.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(tree)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.name in SKIP_FILES or p.suffix.lower() in BINARY_EXTS:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable — not a redaction target
        yield p, rel, text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", metavar="TREE")
    ap.add_argument("--apply", metavar="TREE")
    args = ap.parse_args()
    if bool(args.check) == bool(args.apply):
        ap.error("exactly one of --check or --apply is required")

    tree = Path(args.check or args.apply).resolve()
    if not tree.is_dir():
        print(f"[FATAL] not a directory: {tree}", file=sys.stderr)
        return 2

    patterns = load_patterns(PATTERNS_FILE)
    apply_mode = bool(args.apply)
    total_hits = 0
    files_hit = 0

    for path, rel, text in iter_text_files(tree):
        hits = 0
        out = text
        for needle, repl in patterns:
            count = out.count(needle)
            if count:
                hits += count
                out = out.replace(needle, repl)
        if not hits:
            continue
        files_hit += 1
        total_hits += hits
        verb = "REDACTED" if apply_mode else "HIT"
        print(f"  {verb} {rel} ({hits})")
        if apply_mode:
            path.write_text(out, encoding="utf-8")

    mode = "applied" if apply_mode else "remain"
    print(f"\n[redact] {total_hits} occurrences in {files_hit} files {mode} "
          f"(tree: {tree})")
    if apply_mode:
        return 0
    return 1 if total_hits else 0


if __name__ == "__main__":
    sys.exit(main())
