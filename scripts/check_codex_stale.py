#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Codex freshness checker — gate for Makefile targets.

Returns exit code 0 if Codex matches current source content.
Returns exit code 1 if Codex is stale (source files changed) or missing.
Prints actionable status to stdout.

Usage:
    python3 scripts/check_codex_stale.py          # Check only, exit 1 if stale
    python3 scripts/check_codex_stale.py --fix     # Auto-regenerate if stale
    python3 scripts/check_codex_stale.py --force   # Force regeneration regardless
"""

import argparse
import hashlib
import json
import logging
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

CODEX_PATH = Path(__file__).parent.parent / "OMEGA_CODEX.md"
GROUPS_FILE = Path(__file__).parent.parent / "scripts" / "groups.json"
HYDRATION_HEADER = Path(__file__).parent.parent / "scripts" / "hydration_header.md"
CODEX_CAT = Path(__file__).parent / "codex_cat.py"


def compute_source_hash() -> str:
    """Compute SHA256 hash of all source files that the CODEX depends on."""
    h = hashlib.sha256()
    
    # 1. The groups.json file (defines what goes into the CODEX)
    if GROUPS_FILE.exists():
        h.update(GROUPS_FILE.read_bytes())
    
    # 2. The hydration header template
    if HYDRATION_HEADER.exists():
        h.update(HYDRATION_HEADER.read_bytes())
    
    # 3. All source files listed in groups.json
    if GROUPS_FILE.exists():
        try:
            with open(GROUPS_FILE) as f:
                groups = json.load(f)
            for group, files in groups.items():
                for rel_path in files:
                    filepath = Path(__file__).parent.parent / rel_path
                    if filepath.exists():
                        h.update(filepath.read_bytes())
        except (json.JSONDecodeError, OSError):
            pass  # If we can't read groups, hash won't match and will trigger regen
    
    return h.hexdigest()[:16]


def extract_stored_hash(codex_path: Path) -> str | None:
    """Extract the stored content hash from the CODEX's ⬡ line."""
    try:
        content = codex_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

    # Match: # ⬡ OMEGA ⬡ CODEX ⬡ <timestamp> ⬡ <hash> ⬡
    # Or legacy: # ⬡ OMEGA ⬡ CODEX ⬡ <timestamp> ⬡
    m = re.search(r"⬡\s*OMEGA\s*⬡\s*CODEX\s*⬡\s*([\dT:.+-]+)\s*⬡\s*([a-f0-9]{16})?\s*⬡", content)
    if not m:
        # Try legacy format without hash
        m = re.search(r"⬡\s*OMEGA\s*⬡\s*CODEX\s*⬡\s*([\dT:.+-]+)\s*⬡", content)
        if m:
            return ""  # Legacy format - no hash stored
    if m and m.group(2):
        return m.group(2)
    return None


def regenerate_codex() -> bool:
    """Run codex_cat.py to regenerate OMEGA_CODEX.md."""
    try:
        result = subprocess.run(
            [sys.executable, str(CODEX_CAT)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=CODEX_CAT.parent.parent
        )
        if result.returncode == 0:
            # Extract summary from stderr
            summary = result.stderr.strip().split("\n")[-1] if result.stderr.strip() else ""
            print(f"✅ OMEGA_CODEX.md regenerated — {summary}")
            return True
        else:
            print(f"❌ Regeneration failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Regeneration timed out after 60s")
        return False
    except FileNotFoundError:
        print(f"❌ codex_cat.py not found at {CODEX_CAT}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Check Codex freshness (content-based)")
    parser.add_argument("--fix", action="store_true",
                        help="Auto-regenerate if stale")
    parser.add_argument("--force", action="store_true",
                        help="Force regeneration regardless")
    args = parser.parse_args()

    # Force regeneration
    if args.force:
        print("♻️  Force-regenerating OMEGA_CODEX.md...")
        ok = regenerate_codex()
        sys.exit(0 if ok else 1)

    # Compute current source hash
    current_hash = compute_source_hash()
    
    # Check existing Codex
    stored_hash = extract_stored_hash(CODEX_PATH)
    
    if stored_hash is None:
        print(f"⚠️  OMEGA_CODEX.md not found or unparseable — needs generation")
        if args.fix:
            print("   → Regenerating...")
            ok = regenerate_codex()
            sys.exit(0 if ok else 1)
        sys.exit(1)
    
    if stored_hash == "":
        # Legacy format without hash - treat as stale
        print(f"⚠️  OMEGA_CODEX.md has legacy format (no content hash) — needs regeneration")
        if args.fix:
            print("   → Regenerating...")
            ok = regenerate_codex()
            sys.exit(0 if ok else 1)
        sys.exit(1)
    
    if stored_hash == current_hash:
        print(f"✅ Codex is fresh (content hash matches)")
        sys.exit(0)
    
    # Stale - content has changed
    print(f"❌ Codex is stale (source content changed)")
    print(f"   Stored hash: {stored_hash}")
    print(f"   Current hash: {current_hash}")
    
    if args.fix:
        print(f"   → Auto-regenerating...")
        ok = regenerate_codex()
        sys.exit(0 if ok else 1)
    
    print(f"   → Run `make codex` or `make check-codex-fix` to regenerate")
    sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()