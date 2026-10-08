#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Secret-history gate: every credential-shaped string in durable refs must be
audited in .secret-history-baseline.toml.

The previous `make gate-secrets` regex section failed on any non-zero match
count, with no way to record a disposition — so it failed on history the
project had already audited (gitleaks passed the same findings through
.gitleaksignore) and could never go green.

This checker hashes every distinct token it finds and compares the hash to the
baseline. Consequences:

- An un-audited token fails the gate and must be rotated, purged, or audited.
- A token baselined as "revoked" must never appear in the working tree; if it
  reappears, the gate fails even though history is unchanged.
- No secret material is stored in the baseline, so it can ship publicly.

Exit codes: 0 = clean, 1 = un-audited finding or revoked token in tree,
2 = the checker itself could not run (M23: never synthesise a pass).
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = REPO_ROOT / ".secret-history-baseline.toml"

# name -> regex. Each regex is anchored to a provider's credential shape.
PATTERNS: dict[str, re.Pattern[str]] = {
    "firecrawl": re.compile(r"fc-[A-Za-z0-9_-]{16,}"),
    "google_api_key": re.compile(r"AIzaSy[A-Za-z0-9_-]{20,}"),
    "tavily": re.compile(r"tvly-[A-Za-z0-9]{10,}"),
    "jwt": re.compile(r"eyJhbGci[A-Za-z0-9_.-]{30,}"),
    "gocspx": re.compile(r"GOCSPX-[A-Za-z0-9_-]{10,}"),
}

HASH_PREFIX_LEN = 16
# Dispositions that must not reappear in the working tree.
TREE_FORBIDDEN_DISPOSITIONS = frozenset({"revoked", "purged"})


class ToolchainCollapse(RuntimeError):
    """Raised when the checker cannot perform its scan (M23)."""


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:HASH_PREFIX_LEN]


def load_baseline(path: Path = BASELINE_PATH) -> dict[str, dict[str, str]]:
    """Map token hash -> baseline entry. Raises ToolchainCollapse if unusable."""
    if not path.is_file():
        raise ToolchainCollapse(f"baseline missing: {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ToolchainCollapse(f"baseline unreadable: {exc}") from exc
    entries: dict[str, dict[str, str]] = {}
    for entry in data.get("entries", []):
        digest = entry.get("sha256_16")
        if not digest or not entry.get("disposition") or not entry.get("why"):
            raise ToolchainCollapse(f"incomplete baseline entry: {entry.get('id')!r}")
        if digest in entries:
            raise ToolchainCollapse(f"duplicate baseline hash: {digest}")
        entries[digest] = entry
    if not entries:
        raise ToolchainCollapse("baseline has no entries")
    return entries


def _git(*args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ToolchainCollapse(f"git {' '.join(args)} failed: {exc}") from exc
    return proc.stdout


def scan_history() -> dict[str, set[str]]:
    """Return token hash -> set of file paths, across durable refs only.

    Durable refs (branches + tags) are what a public clone receives; IDE
    checkpoint shadow refs are deliberately excluded.
    """
    # git -G uses POSIX extended regex: plain alternation, no (?:...) groups.
    combined = "|".join(rx.pattern for rx in PATTERNS.values())
    patch = _git("log", "-p", "-G", combined, "--branches", "--tags", "--format=%H")

    found: dict[str, set[str]] = {}
    current_file = "<unknown>"
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            current_file = line.split(" b/")[-1].strip()
            continue
        if line.startswith(("+++", "---")):
            continue
        for rx in PATTERNS.values():
            match = rx.search(line)
            if match:
                found.setdefault(token_hash(match.group(0)), set()).add(current_file)
                break
    return found


def scan_tree() -> dict[str, set[str]]:
    """Return token hash -> tracked files containing it, in the working tree."""
    found: dict[str, set[str]] = {}
    for rel in _git("ls-files").splitlines():
        rel = rel.strip()
        if not rel:
            continue
        try:
            text = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for rx in PATTERNS.values():
            match = rx.search(text)
            if match:
                found.setdefault(token_hash(match.group(0)), set()).add(rel)
                break
    return found


def main() -> int:
    try:
        baseline = load_baseline()
        history = scan_history()
        tree = scan_tree()
    except ToolchainCollapse as exc:
        print(f"[TOOL-CHAIN-COLLAPSE] secret-history gate could not run: {exc}")
        return 2

    print("=== gate-secrets: history scan against audited baseline ===")
    print(f"  baseline entries: {len(baseline)}")
    print(f"  distinct tokens in durable refs: {len(history)}")

    unaudited: list[tuple[str, str]] = []
    for digest, files in sorted(history.items()):
        entry = baseline.get(digest)
        if entry is None:
            unaudited.append((digest, ", ".join(sorted(files)[:3])))
            continue
        print(
            f"  OK  {entry['id']:<18} {entry['disposition']:<16} "
            f"({len(files)} file(s) in history)"
        )

    reappearances: list[tuple[str, str, str]] = []
    for digest, files in sorted(tree.items()):
        entry = baseline.get(digest)
        if entry is None:
            unaudited.append((digest, f"WORKING TREE: {', '.join(sorted(files)[:3])}"))
        elif entry["disposition"] in TREE_FORBIDDEN_DISPOSITIONS:
            reappearances.append(
                (entry["id"], entry["disposition"], ", ".join(sorted(files)[:3]))
            )

    for digest, where in unaudited:
        print(f"  FAIL un-audited token sha256_16={digest} in {where}")
        print(
            "       -> rotate/purge it, or audit it in "
            f"{BASELINE_PATH.name} with a disposition + WHY"
        )
    for entry_id, disposition, where in reappearances:
        print(
            f"  FAIL {entry_id} is baselined '{disposition}' but appears in the "
            f"working tree: {where}"
        )
        print("       -> a rotated credential must never be pasted back into a tracked file")

    if unaudited or reappearances:
        print("secret-history gate FAILED")
        return 1

    retained = sum(
        1
        for e in baseline.values()
        if e["disposition"] not in TREE_FORBIDDEN_DISPOSITIONS
    )
    print(f"  audited: {len(history)} history token(s), {retained} retained-public")
    print("secret-history gate PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

