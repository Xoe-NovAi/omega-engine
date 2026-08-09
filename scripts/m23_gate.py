#!/usr/bin/env python3
"""M23 Failure Integrity Gate — AST-based soft-failure detection with ratchet.

Replaces the broken ``rg`` pipeline in ``Makefile:check-m23-failure-integrity``
with a Ruff AST check. Uses a ratchet: fails only on NEW violations
(per-file count increase) vs the baseline in ``config/m23_baseline.txt``.

[M23] No soft-failures: raises PyCompileError if Ruff is absent.
[M8] No telemetry: Ruff is a local static binary, zero runtime dependency.

AP: AP-M23-GATE-v1.0.0
"""

import json
import subprocess
import sys
from pathlib import Path

BASELINE_PATH = Path("config/m23_baseline.txt")
RUFF_RULES = ["S110", "S112", "BLE001", "E722"]
SRC_DIR = "src/omega"


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def _run_ruff() -> dict[str, int]:
    """Run ruff check, return {relpath: count}. Exits non-zero if ruff missing."""
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "ruff", "check", SRC_DIR,
                "--select", ",".join(RUFF_RULES),
                "--output-format", "json",
            ],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        _fail(
            "Ruff not found. Install with: .venv/bin/pip install ruff\n"
            "[TOOL-CHAIN-COLLAPSE] M23 gate requires Ruff (M23 Failure Integrity)."
        )

    # ruff exits 1 when violations found (expected), 0 when clean,
    # 2+ on config errors. A non-zero exit with EMPTY stdout means ruff
    # failed to run (e.g. binary not found) — NOT "no violations".
    if result.returncode != 0 and not result.stdout.strip():
        _fail(
            f"Ruff failed to run (exit {result.returncode}): {result.stderr.strip()}\n"
            "[TOOL-CHAIN-COLLAPSE] M23 gate requires a working Ruff install."
        )

    # ruff exits 1 when violations found (expected), 0 when clean
    try:
        violations = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        _fail(f"Ruff output parse failed: {result.stderr}")

    counts: dict[str, int] = {}
    for v in violations:
        path = v.get("filename", "")
        # Normalize absolute paths to repo-relative (src/omega/...)
        if path.startswith("/"):
            # Find the src/omega/ prefix in the absolute path
            idx = path.find("/" + SRC_DIR + "/")
            if idx >= 0:
                path = path[idx + 1:]  # drop leading /
            elif path.endswith(SRC_DIR):
                pass  # keep as-is (shouldn't happen)
        counts[path] = counts.get(path, 0) + 1
    return counts


def _load_baseline() -> dict[str, int]:
    """Load baseline counts from config/m23_baseline.txt."""
    if not BASELINE_PATH.exists():
        _fail(f"Baseline not found at {BASELINE_PATH}. Run 'make m23-baseline' first.")
    baseline: dict[str, int] = {}
    for line in BASELINE_PATH.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        # Format: "  COUNT path/to/file.py"
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        try:
            count = int(parts[0])
        except ValueError:
            continue
        baseline[parts[1]] = count
    return baseline


def main() -> None:
    baseline = _load_baseline()
    current = _run_ruff()

    # Ratchet: fail only on NEW violations (count increase per file)
    new_violations: list[tuple[str, int, int]] = []  # (file, baseline, current)
    for path, cur_count in sorted(current.items()):
        base_count = baseline.get(path, 0)
        if cur_count > base_count:
            new_violations.append((path, base_count, cur_count))

    # Also flag files that have violations but weren't in baseline at all
    # (already covered by base_count=0 above)

    if new_violations:
        print("M23 FAIL: New soft-failure patterns detected (ratchet):\n")
        for path, base, cur in new_violations:
            delta = cur - base
            print(f"  {path}: {base} -> {cur} (+{delta})")
        print(f"\nTotal new violations: {sum(c - b for _, b, c in new_violations)}")
        print("\nFix the violations or update baseline with 'make m23-baseline'.")
        sys.exit(1)

    total = sum(current.values())
    base_total = sum(baseline.values())
    print(f"M23 passed: No new soft-failure patterns.")
    print(f"  Current: {total} | Baseline: {base_total} | Delta: {total - base_total}")


if __name__ == "__main__":
    main()
