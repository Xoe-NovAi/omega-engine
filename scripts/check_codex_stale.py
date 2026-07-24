#!/usr/bin/env python3
"""
Codex staleness checker — gate for Makefile targets.

Returns exit code 0 if Codex is fresh (<24h old or regenerated OK).
Returns exit code 1 if Codex is stale (>24h old) and regeneration failed.
Prints actionable status to stdout.

Usage:
    python3 scripts/check_codex_stale.py          # Check only, exit 1 if stale
    python3 scripts/check_codex_stale.py --fix     # Auto-regenerate if stale
    python3 scripts/check_codex_stale.py --force   # Force regeneration regardless
"""

import argparse
import logging
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

CODEX_PATH = Path(__file__).parent.parent / "OMEGA_CODEX.md"
STALE_THRESHOLD_HOURS = 24


def extract_timestamp(codex_path: Path) -> datetime | None:
    """Extract the UTC timestamp from the Codex's ⬡ line."""
    try:
        content = codex_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

    # Match: # ⬡ OMEGA ⬡ CODEX ⬡ 2026-07-24T15:00:00.000000+00:00 ⬡
    m = re.search(r"⬡\s*CODEX\s*⬡\s*([\dT:.+-]+)\s*⬡", content)
    if not m:
        return None

    try:
        # Handle both offset-aware (+00:00) and offset-naive (Z) timestamps
        ts_str = m.group(1).replace("Z", "+00:00")
        if "+" not in ts_str and ts_str.endswith("+"):
            ts_str = ts_str[:-1] + "+00:00"
        return datetime.fromisoformat(ts_str)
    except (ValueError, IndexError):
        return None


def regenerate_codex() -> bool:
    """Run codex_cat.py to regenerate OMEGA_CODEX.md."""
    import subprocess
    codex_cat = Path(__file__).parent / "codex_cat.py"
    try:
        result = subprocess.run(
            [sys.executable, str(codex_cat)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"❌ Regeneration failed (exit {result.returncode}): {result.stderr.strip()}")
            return False
        # codex_cat.py logs to stderr via logging — print stdout summary
        lines_out = [l for l in result.stdout.strip().split("\n") if "Lines:" in l or "successfully" in l]
        summary = result.stderr.strip().split("\n")[-1] if result.stderr.strip() else ""
        print(f"✅ OMEGA_CODEX.md regenerated — {summary}")
        return True
    except subprocess.TimeoutExpired:
        print("❌ Regeneration timed out after 30s")
        return False
    except FileNotFoundError:
        print(f"❌ codex_cat.py not found at {codex_cat}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Check Codex staleness")
    parser.add_argument("--fix", action="store_true",
                        help="Auto-regenerate if stale")
    parser.add_argument("--force", action="store_true",
                        help="Force regeneration regardless of age")
    args = parser.parse_args()

    # Force regeneration
    if args.force:
        print("♻️  Force-regenerating OMEGA_CODEX.md...")
        ok = regenerate_codex()
        sys.exit(0 if ok else 1)

    # Check existing Codex
    ts = extract_timestamp(CODEX_PATH)

    if ts is None:
        print(f"⚠️  OMEGA_CODEX.md not found or unparseable — needs generation")
        if args.fix:
            print("   → Regenerating...")
            ok = regenerate_codex()
            sys.exit(0 if ok else 1)
        sys.exit(1)

    age = datetime.now(timezone.utc) - ts
    hours_old = age.total_seconds() / 3600

    if hours_old < STALE_THRESHOLD_HOURS:
        print(f"✅ Codex is fresh ({hours_old:.0f}h old, threshold {STALE_THRESHOLD_HOURS}h)")
        sys.exit(0)

    # Stale
    print(f"❌ Codex is stale ({hours_old:.0f}h old, threshold {STALE_THRESHOLD_HOURS}h)")
    print(f"   Generated: {ts.isoformat()}")
    print(f"   Now:       {datetime.now(timezone.utc).isoformat()}")

    if args.fix:
        print(f"   → Auto-regenerating...")
        ok = regenerate_codex()
        sys.exit(0 if ok else 1)

    print(f"   → Run `make codex` or `make check-codex-fix` to regenerate")
    sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
