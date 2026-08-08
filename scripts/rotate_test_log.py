#!/usr/bin/env python3
"""
Rotate test-run.log following the established data/logs/ pattern:
- test-run.log          -> current
- test-run.log.1        -> previous (uncompressed)
- test-run.log.2.gz     -> older (compressed)
- test-run.log.3.gz     -> oldest (compressed)
"""

import gzip
import shutil
import sys
from pathlib import Path

LOG_DIR = Path("data/logs")
LOG_BASE = LOG_DIR / "test-run.log"

def rotate_logs():
    """Rotate existing test-run logs."""
    # Remove oldest (test-run.log.3.gz)
    oldest = LOG_BASE.with_suffix(".log.3.gz")
    if oldest.exists():
        oldest.unlink()
        print(f"Removed oldest: {oldest}", file=sys.stderr)

    # Rotate .2.gz -> .3.gz
    log_2gz = LOG_BASE.with_suffix(".log.2.gz")
    if log_2gz.exists():
        shutil.move(str(log_2gz), str(oldest))
        print(f"Rotated: {log_2gz} -> {oldest}", file=sys.stderr)

    # Rotate .1 -> .2.gz (compress)
    log_1 = LOG_BASE.with_suffix(".log.1")
    if log_1.exists():
        with open(log_1, "rb") as f_in:
            with gzip.open(log_2gz, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        log_1.unlink()
        print(f"Compressed & rotated: {log_1} -> {log_2gz}", file=sys.stderr)

    # Rotate current -> .1
    current = LOG_BASE
    if current.exists():
        shutil.move(str(current), str(log_1))
        print(f"Rotated: {current} -> {log_1}", file=sys.stderr)

def write_log(content: str):
    """Write new test-run.log."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_BASE.write_text(content)
    print(f"Wrote new test run log: {LOG_BASE} ({len(content)} chars)", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: rotate_test_log.py <rotate|write>", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    if action == "rotate":
        rotate_logs()
    elif action == "write":
        # Read from stdin to avoid argument length limits
        content = sys.stdin.read()
        write_log(content)
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()