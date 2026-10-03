#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M23 Failure Integrity Gate — AST-based soft-failure detection with ratchet.

Replaces the broken ``rg`` pipeline in ``Makefile:check-m23-failure-integrity``
with a Ruff AST check. Uses a ratchet: fails only on NEW violations
(per-file count increase) vs the baseline in ``config/m23_baseline.txt``.

Also enforces the structural M1 invariant discovered in the Web Claude v3
audit (§3.1 / §4): ``anyio.from_thread.run(...)`` called from inside an
``async def`` body is an event-loop-thread violation — it bridges from the
wrong thread and either deadlocks or raises ``RuntimeError``. This is a
hard invariant (baseline is zero; any occurrence is a new violation).

[M23] No soft-failures: raises PyCompileError if Ruff is absent.
[M8] No telemetry: Ruff is a local static binary, zero runtime dependency.
[M1] AnyIO: AST check flags from_thread.run() reachable inside async def.

AP: AP-M23-GATE-v1.1.0
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

BASELINE_PATH = Path("config/m23_baseline.txt")
RUFF_RULES = ["S110", "S112", "BLE001", "E722"]
SRC_DIR = "src/omega"

# [P2-4] M1 structural invariant: from_thread.run() inside async def.
# Detect as: `anyio.from_thread.run(...)`, `from_thread.run(...)`,
# or bare `from_thread.run(...)` reachable in an async def body.
FROM_THREAD_CALLS = ("from_thread.run", "anyio.from_thread.run")


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def _run_ruff() -> dict[str, int]:
    """Run ruff check, return {relpath: count}. Exits non-zero if ruff missing."""
    venv_python = Path(".venv/bin/python")
    # Fall back to the running interpreter when .venv is absent (CI runners
    # install deps into the active interpreter, not a local .venv).
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    try:
        result = subprocess.run(
            [
                python_exe, "-m", "ruff", "check", SRC_DIR,
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


def _is_from_thread_call(node: ast.AST) -> bool:
    """True if node is a Call to anyio.from_thread.run(...) / from_thread.run(...)."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    # Bare `from_thread.run(...)` — module-level alias
    if isinstance(func, ast.Attribute) and func.attr == "run":
        value = func.value
        # anyio.from_thread.run
        if isinstance(value, ast.Attribute) and value.attr == "from_thread":
            return True
        # from_thread.run (aliased module)
        if isinstance(value, ast.Name) and value.id == "from_thread":
            return True
    # anyio.from_thread.run(...) — direct dotted chain
    if isinstance(func, ast.Attribute):
        head = func.value
        if isinstance(head, ast.Attribute) and head.attr == "from_thread":
            return True
    return False


def _scan_from_thread_in_async() -> dict[str, list[tuple[str, int]]]:
    """AST-scan src/omega for from_thread.run() calls inside async def bodies.

    Returns {relpath: [(function_name, lineno), ...]}. This is the exact bug
    class from the Web Claude v3 audit §3.1 (`_record_perf`) and §4
    (`health_monitor.record_breaker_failure`): calling the blocking bridge
    from the event-loop thread raises RuntimeError or deadlocks.
    """
    found: dict[str, list[tuple[str, int]]] = {}
    root = Path(SRC_DIR)
    for py in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as e:
            _fail(f"{py}: cannot parse ({e})")
        rel = str(py)
        for node in ast.walk(tree):
            if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                # Only scan bodies of async defs (and nested defs inside them
                # still run on the event loop unless to_thread'd — flag both).
                if isinstance(node, ast.AsyncFunctionDef):
                    for sub in ast.walk(node):
                        if _is_from_thread_call(sub):
                            found.setdefault(rel, []).append((node.name, sub.lineno))
    return found


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

    # [P2-4] M1 structural invariant — hard gate, baseline is zero.
    from_thread_hits = _scan_from_thread_in_async()
    if from_thread_hits:
        print("\nM23 FAIL: from_thread.run() inside async def (M1 AnyIO violation):\n")
        for rel, hits in sorted(from_thread_hits.items()):
            for fn, lineno in hits:
                print(f"  {rel}:{lineno} — inside async def {fn}()")
        print(
            "\nFix: replace anyio.from_thread.run(...) with the async-native "
            "pattern (await ...) or wrap sync work in anyio.to_thread.run_sync()."
        )
        sys.exit(1)
    print("  M1 from_thread-in-async scan: clean (0 violations)")


if __name__ == "__main__":
    main()
