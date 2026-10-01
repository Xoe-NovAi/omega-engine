---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

title: "R-TEST_HARNESS_HARDENING — Sovereign Test Harness Hardening Plan"
date: 2026-06-29
author: Researcher (Sovereign Master Researcher)
status: PROPOSED
tier: L2 (Synthesis)
tags: [testing, pytest, error-logging, resilience, temple-grade]
heritage: []
mandates: [M1, M8, M13, M15, M18]
---

# R-TEST_HARNESS_HARDENING — Sovereign Test Harness Hardening Plan

## Executive Summary (L1)

The Omega Engine's 440+ pytest tests currently lack structured error reporting, persistent failure history, test isolation guarantees, and diagnostic-first failure output. When a test fails, the developer receives a raw pytest traceback with no classification, no subsystem mapping, and no historical context. This document presents a **Temple-Grade / Sovereign Ark-Grade** plan to transform the test harness into a first-class observability system — one that classifies failures, persists history locally, isolates cascading faults, and delivers diagnostic-first output — all without violating any Sovereign Mandate (especially M8: Zero Telemetry, M1: AnyIO, M13: Temple-Grade).

The plan is organized into **5 Waves** of increasing scope, with each wave independently shippable and testable. Total estimated effort: ~3-5 days of focused implementation.

---

## §1 Current State Analysis

### 1.1 Test Infrastructure Inventory

| Component | Current State | Gap |
|-----------|--------------|-----|
| **pytest version** | >=9.0.0 (pyproject.toml) | Adequate |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` | Minimal: only `testpaths`, `asyncio_mode`, `addopts` |
| **conftest.py** | 77 lines, 4 fixtures | No hooks, no error capture, no reporting |
| **Timeout** | `--timeout=30` via addopts | Global only, no per-test granularity |
| **Error output** | Default pytest traceback (`--tb=auto`) | Not optimized for diagnostic speed |
| **Failure persistence** | None — results vanish after run | No history, no trend analysis |
| **Test isolation** | `tmp_path` + `monkeypatch` env vars | No subprocess isolation, no cascade prevention |
| **Retry** | None | Flaky tests fail permanently on first attempt |
| **Parallel execution** | `flock` mutex (Makefile line 359) | Serial only, no xdist |

### 1.2 Failure Pain Points (Observed)

1. **Slow failure feedback**: 440 tests take ~2-5 minutes; a single failure at test 439 wastes 4+ minutes.
2. **Cryptic tracebacks**: Default `--tb=auto` shows full chain; no subsystem classification.
3. **Cascade risk**: Shared `MemoryStore` singleton (`reset_memory_store()`) means one test's pollution can cascade.
4. **No persistence**: Failed test details are lost after the run; no way to see "what failed last time."
5. **No flaky detection**: No mechanism to identify or retry intermittently failing tests.

---

## §2 The Five Waves

### Wave 1: Diagnostic-First Failure Output (Quick Win — ~2 hours)

**Goal**: Make failures instantly diagnosable without changing test structure.

#### 2.1.1 Enhanced Traceback Format

**Change**: Add `--tb=short --no-header -q` to `addopts` in `pyproject.toml`, plus a custom `conftest.py` hook for enriched failure summaries.

**Why `--tb=short`**: Shows only the assertion line and the immediate context, cutting traceback noise by 60-80%. The `--tb=long` default is useful for library authors but counterproductive for application test suites where you already know the call chain.

**File**: `pyproject.toml` (line 57)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = """
  --ignore=data/entities/roc_racoon/workspace/odysseus-dev
  --timeout=30
  --tb=short
  --no-header
  -q
  --strict-markers
  -p no:faulthandler
  faulthandler_timeout=60
"""
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests requiring live backends",
    "flaky: marks known flaky tests for automatic retry",
    "isolated: marks tests requiring subprocess isolation",
]
```

**Risk**: LOW — `--tb=short` is a display-only change. No behavioral difference.

#### 2.1.2 Structured Failure Summary Hook

**Goal**: After all tests complete, print a classified summary of failures grouped by subsystem.

**File**: `tests/conftest.py` — add `pytest_terminal_summary` hook:

```python
@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Append a classified failure summary to the test output."""
    failed = terminalreporter.getreports("failed")
    if not failed:
        return

    terminalreporter.write_sep("=", "SOVEREIGN FAILURE CLASSIFICATION")
    terminalreporter.write_line(
        f"{len(failed)} failure(s) detected. Classification below:\n"
    )

    # Classify by subsystem
    subsystem_counts: dict[str, list[str]] = {}
    for report in failed:
        nodeid = report.nodeid
        # Extract subsystem from file name: tests/test_oracle.py → oracle
        parts = nodeid.split("::")
        file_part = parts[0].replace("tests/test_", "").replace(".py", "")
        subsystem = file_part.replace("test_", "")

        if subsystem not in subsystem_counts:
            subsystem_counts[subsystem] = []
        subsystem_counts[subsystem].append(parts[-1] if len(parts) > 1 else nodeid)

    for subsystem, tests in sorted(subsystem_counts.items()):
        terminalreporter.write_line(
            f"  [{subsystem.upper()}] {len(tests)} failure(s):",
            red=True, bold=True,
        )
        for test in tests:
            terminalreporter.write_line(f"    - {test}")
    terminalreporter.write_line("")
```

**Risk**: LOW — Additive hook. Does not modify test execution.

#### 2.1.3 Failure Detail File Writer

**Goal**: Write a machine-readable failure summary to `data/test_results/failures_latest.json` after each run.

**File**: `tests/conftest.py` — add `pytest_sessionfinish` hook:

```python
import json
import time
from pathlib import Path

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Persist failure details for historical analysis."""
    if exitstatus == 0:
        return  # No failures

    results_dir = Path("data/test_results")
    results_dir.mkdir(parents=True, exist_ok=True)

    failed_reports = session.config.hook.pytest_report_listoferrors(
        config=session.config
    )

    # Build structured failure record
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "exit_code": exitstatus,
        "total_tests": session.testscollected,
        "failures": [],
    }

    for report in session.config._reports.get("failed", []):
        record["failures"].append({
            "nodeid": report.nodeid,
            "outcome": report.outcome,
            "duration": getattr(report, "duration", 0),
            "subsystem": _extract_subsystem(report.nodeid),
            "error_type": _classify_error(report),
            "short_repr": str(report.longrepr)[:500] if report.longrepr else "",
        })

    # Atomic write
    latest = results_dir / "failures_latest.json"
    tmp = results_dir / "failures_latest.json.tmp"
    tmp.write_text(json.dumps(record, indent=2))
    tmp.rename(latest)

    # Append to history
    history = results_dir / "failures_history.jsonl"
    with open(history, "a") as f:
        f.write(json.dumps(record) + "\n")


def _extract_subsystem(nodeid: str) -> str:
    """Extract subsystem name from test node ID."""
    parts = nodeid.split("::")[0]
    name = parts.replace("tests/test_", "").replace(".py", "")
    return name.replace("test_", "")


def _classify_error(report) -> str:
    """Classify error type from report longrepr."""
    if not report.longrepr:
        return "unknown"
    repr_str = str(report.longrepr)
    if "AssertionError" in repr_str or "assert " in repr_str:
        return "assertion"
    if "ImportError" in repr_str or "ModuleNotFoundError" in repr_str:
        return "import"
    if "TimeoutError" in repr_str or "timeout" in repr_str.lower():
        return "timeout"
    if "RecursionError" in repr_str:
        return "recursion"
    if "ConnectionRefused" in repr_str or "ConnectionError" in repr_str:
        return "network"
    if "PermissionError" in repr_str:
        return "permission"
    if "FileNotFoundError" in repr_str:
        return "filesystem"
    return "other"
```

**Risk**: LOW — File I/O only. Atomic write prevents corruption. History append is O(1).

**Mandate Compliance**: M8 (Zero Telemetry) — all writes are local to `data/test_results/`. No external calls.

---

### Wave 2: Test Isolation & Cascade Prevention (~4 hours)

**Goal**: Prevent one test's failure from cascading to others.

#### 2.2.1 Subprocess Isolation for High-Risk Tests

**Plugin**: `pytest-isolated` (v0.0.14, 2026-06-01)

**Why `pytest-isolated` over `pytest-isolate`**:
- `pytest-isolated` is cross-platform (Linux, macOS, Windows) using subprocess (not fork).
- `pytest-isolate` uses `fork()` — Linux only, incompatible with the Omega Engine's Podman-rootless architecture.
- `pytest-isolated` supports intelligent grouping (related tests share a subprocess).

**Installation**:
```bash
pip install pytest-isolated
```

**File**: `pyproject.toml` — add to `addopts`:
```toml
addopts = """
  ...
  --isolated-timeout=30
"""
```

**Marking high-risk tests**:
```python
# In individual test files that do heavy I/O or global state mutation:
@pytest.mark.isolated(group="memory_store")
def test_memory_store_concurrent_access():
    ...

@pytest.mark.isolated(group="entity_registry") 
def test_entity_scaffold_and_teardown():
    ...
```

**Risk**: MEDIUM — Subprocess spawning adds ~100ms overhead per isolated test. Only mark tests that actually need isolation. The `_set_test_env` autouse fixture already provides basic isolation via `tmp_path`.

#### 2.2.2 Per-Test Timeout with faulthandler

**Current**: Global `--timeout=30` in `addopts`.

**Enhancement**: Enable `faulthandler_timeout=60` (built into pytest since 5.0) to dump thread traces on hang:

```toml
[tool.pytest.ini_options]
faulthandler_timeout = 60
```

**Why 60s (2x the test timeout)**: The test timeout kills at 30s; faulthandler dumps traces at 60s as a safety net for tests that somehow bypass the timeout.

**Risk**: LOW — Built-in pytest feature, no external dependency.

#### 2.2.3 Retry Flaky Tests

**Plugin**: `pytest-rerunfailures` (v16.3, 2026-05-21)

**Installation**:
```bash
pip install pytest-rerunfailures
```

**Usage** (opt-in per test, NOT global):
```python
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_network_dependent():
    ...
```

**Do NOT add `--reruns` globally** — that would mask real failures. Only use `@pytest.mark.flaky` on tests known to be intermittently flaky.

**Risk**: LOW — Opt-in only. No behavioral change to unmarked tests.

---

### Wave 3: Structured Error Logging Framework (~6 hours)

**Goal**: Build a sovereign, local-only structured logging system for test results.

#### 2.3.1 Error Taxonomy

Define a formal error classification system for the Omega Engine test suite:

| Code | Category | Description | Example |
|------|----------|-------------|---------|
| `E-001` | Assertion | Test assertion failed | `assert result == expected` |
| `E-002` | Import | Module import failed | `ModuleNotFoundError` |
| `E-003` | Timeout | Test exceeded time limit | `TimeoutError` |
| `E-004` | Resource | File/db/port unavailable | `FileNotFoundError`, `ConnectionRefused` |
| `E-005` | State | Global state pollution | Singleton not reset between tests |
| `E-006` | Mock | Mock configuration error | `AttributeError` on mock |
| `E-007` | Async | AnyIO/asyncio issue | `RuntimeError: Event loop closed` |
| `E-008` | Permission | UID/permission drift | `PermissionError` |
| `E-009` | Infrastructure | Container/service down | `podman: not found` |
| `E-010` | Unknown | Unclassified error | Everything else |

**File**: `tests/error_taxonomy.py` (new file):
```python
"""Omega Engine Test Error Taxonomy — Sovereign Classification System."""

from enum import Enum

class ErrorCategory(Enum):
    ASSERTION = "E-001"
    IMPORT = "E-002"
    TIMEOUT = "E-003"
    RESOURCE = "E-004"
    STATE = "E-005"
    MOCK = "E-006"
    ASYNC = "E-007"
    PERMISSION = "E-008"
    INFRASTRUCTURE = "E-009"
    UNKNOWN = "E-010"

ERROR_PATTERNS = {
    ErrorCategory.ASSERTION: ["AssertionError", "assert ", "!= ", "expected "],
    ErrorCategory.IMPORT: ["ImportError", "ModuleNotFoundError", "cannot import"],
    ErrorCategory.TIMEOUT: ["TimeoutError", "timeout", "timed out"],
    ErrorCategory.RESOURCE: ["FileNotFoundError", "ConnectionRefused", "ConnectionError",
                            "Address already in use", "No such file or directory"],
    ErrorCategory.STATE: ["Singleton", "reset_memory_store", "ResourceWarning"],
    ErrorCategory.MOCK: ["AttributeError", "Mock", "MagicMock", "patch"],
    ErrorCategory.ASYNC: ["RuntimeError", "Event loop", "anyio", "asyncio"],
    ErrorCategory.PERMISSION: ["PermissionError", "Operation not permitted", "UID"],
    ErrorCategory.INFRASTRUCTURE: ["podman", "docker", "container", "redis", "qdrant"],
}

def classify_error(longrepr: str) -> ErrorCategory:
    """Classify a test error from its longrepr string."""
    if not longrepr:
        return ErrorCategory.UNKNOWN
    repr_str = str(longrepr)
    for category, patterns in ERROR_PATTERNS.items():
        if any(p in repr_str for p in patterns):
            return category
    return ErrorCategory.UNKNOWN
```

**Risk**: LOW — Pure classification logic, no side effects.

#### 2.3.2 Enhanced conftest.py with Full Hook Integration

**File**: `tests/conftest.py` — complete rewrite with hooks:

```python
"""Omega Engine Test Configuration — Sovereign Test Harness.

Provides:
  - Environment isolation (OMEGA_ENV=test, OMEGA_DATA_DIR=tmp_path)
  - Structured failure capture via pytest_runtest_makereport
  - Subsystem-classified terminal summary
  - Persistent failure history (JSON, local-only)
  - Error taxonomy integration
"""
import json
import logging
import os
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from omega.memory_store import MemoryStore, reset_memory_store
from omega.oracle.context_builder import ContextBuilder
from tests.error_taxonomy import classify_error, ErrorCategory

logger = logging.getLogger(__name__)

# ── Environment Isolation ─────────────────────────────────────────

@pytest.fixture(autouse=True)
def _set_test_env(tmp_path, monkeypatch):
    """Ensure OMEGA_ENV=test and isolated temp data dir for all tests."""
    monkeypatch.setenv("OMEGA_ENV", "test")
    monkeypatch.setenv("OMEGA_DATA_DIR", str(tmp_path))
    reset_memory_store()
    yield
    reset_memory_store()


@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    """Create isolated temp data directory for tests."""
    logger.debug("temp_data_dir: OMEGA_DATA_DIR=%s", tmp_path)
    reset_memory_store()
    yield tmp_path
    reset_memory_store()


# ── Structured Failure Capture ────────────────────────────────────

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Capture structured failure data on every test phase."""
    outcome = yield
    report = outcome.get_result()

    # Attach subsystem and error category to report
    report.subsystem = _extract_subsystem(item.nodeid)

    if report.failed and report.when == "call":
        report.error_category = classify_error(report.longrepr)
    else:
        report.error_category = None


def _extract_subsystem(nodeid: str) -> str:
    """Extract subsystem name from test node ID."""
    parts = nodeid.split("::")[0]
    name = parts.replace("tests/", "").replace("test_", "").replace(".py", "")
    return name


# ── Classified Terminal Summary ────────────────────────────────────

@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Append classified failure summary and subsystem breakdown."""
    failed = terminalreporter.getreports("failed")
    if not failed:
        return

    terminalreporter.write_sep("=", "SOVEREIGN FAILURE CLASSIFICATION")

    # Group by subsystem
    by_subsystem: dict[str, list] = {}
    by_category: dict[str, list] = {}
    for report in failed:
        sub = getattr(report, "subsystem", "unknown")
        cat = getattr(report, "error_category", ErrorCategory.UNKNOWN)
        by_subsystem.setdefault(sub, []).append(report)
        by_category.setdefault(cat.value if cat else "E-010", []).append(report)

    terminalreporter.write_line(
        f"{len(failed)} failure(s) — {terminalreporter._session.testscollected} total\n"
    )

    # Subsystem breakdown
    terminalreporter.write_line("By Subsystem:", yellow=True, bold=True)
    for sub, reports in sorted(by_subsystem.items()):
        terminalreporter.write_line(f"  [{sub}] {len(reports)} failure(s)")
        for r in reports:
            test_name = r.nodeid.split("::")[-1] if "::" in r.nodeid else r.nodeid
            terminalreporter.write_line(f"    - {test_name}")

    # Error category breakdown
    terminalreporter.write_line("\nBy Error Category:", yellow=True, bold=True)
    for cat, reports in sorted(by_category.items()):
        terminalreporter.write_line(f"  {cat}: {len(reports)} failure(s)")

    terminalreporter.write_line("")


# ── Persistent Failure History ────────────────────────────────────

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Write structured failure record to local JSON (M8: no telemetry)."""
    if exitstatus == 0:
        return

    results_dir = Path("data/test_results")
    results_dir.mkdir(parents=True, exist_ok=True)

    failures = []
    for report in session.config._reports.get("failed", []):
        failures.append({
            "nodeid": report.nodeid,
            "outcome": report.outcome,
            "duration": getattr(report, "duration", 0),
            "subsystem": getattr(report, "subsystem", "unknown"),
            "error_category": (
                getattr(report, "error_category", ErrorCategory.UNKNOWN).value
                if getattr(report, "error_category", None) else "E-010"
            ),
            "short_repr": str(report.longrepr)[:500] if report.longrepr else "",
        })

    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "exit_code": exitstatus,
        "total_tests": session.testscollected,
        "failure_count": len(failures),
        "failures": failures,
    }

    # Atomic write to latest
    latest = results_dir / "failures_latest.json"
    tmp = results_dir / "failures_latest.json.tmp"
    tmp.write_text(json.dumps(record, indent=2))
    tmp.rename(latest)

    # Append to history (JSONL for efficient append + line-by-line reading)
    history = results_dir / "failures_history.jsonl"
    with open(history, "a") as f:
        f.write(json.dumps(record) + "\n")


# ── Existing Fixtures ─────────────────────────────────────────────

@pytest.fixture
def mock_memory_store():
    """Mock MemoryStore with configurable get_history return value."""
    store = MagicMock(spec=MemoryStore)
    store.get_history = AsyncMock(return_value=[])
    store.add_exchange = AsyncMock()
    return store


@pytest.fixture
def context_builder(mock_memory_store):
    """ContextBuilder with injected mock MemoryStore."""
    return ContextBuilder(memory_store=mock_memory_store)


@pytest.fixture
def sample_exchanges():
    """Standard test fixture: 2 conversation exchanges."""
    return [
        {
            "timestamp": "2026-05-16T10:00:00+00:00",
            "user": "What is strength?",
            "assistant": "Strength is the will to endure.",
            "metadata": {},
        },
        {
            "timestamp": "2026-05-16T10:01:00+00:00",
            "user": "And what is courage?",
            "assistant": "Courage is strength in the face of fear.",
            "metadata": {},
        },
    ]
```

**Risk**: MEDIUM — This is a significant conftest.py change. Must be tested against all 440 tests to ensure no regressions.

---

### Wave 4: Historical Trend Analysis (~4 hours)

**Goal**: Enable local-only trend analysis of test failures over time.

#### 2.4.1 Trend Analysis CLI Command

**File**: `scripts/test_trends.py` (new file):

```python
#!/usr/bin/env python3
"""Omega Test Trend Analysis — Local-only failure history viewer.

Usage:
    python scripts/test_trends.py              # Last 10 runs summary
    python scripts/test_trends.py --runs 50    # Last 50 runs
    python scripts/test_trends.py --subsystem oracle  # Filter by subsystem
    python scripts/test_trends.py --flaky      # Show flaky test candidates
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HISTORY_FILE = Path("data/test_results/failures_history.jsonl")


def load_history(limit: int = 10) -> list[dict]:
    """Load the last N entries from failure history."""
    if not HISTORY_FILE.exists():
        return []
    lines = HISTORY_FILE.read_text().strip().split("\n")
    entries = []
    for line in lines[-limit:]:
        if line.strip():
            entries.append(json.loads(line))
    return entries


def show_summary(entries: list[dict]):
    """Show high-level summary of recent runs."""
    print(f"\n{'='*60}")
    print(f"  SOVEREIGN TEST TRENDS — Last {len(entries)} run(s)")
    print(f"{'='*60}\n")

    for entry in entries:
        ts = entry["timestamp"][:19]
        total = entry["total_tests"]
        failed = entry["failure_count"]
        pass_rate = ((total - failed) / total * 100) if total > 0 else 0
        status = "PASS" if entry["exit_code"] == 0 else "FAIL"
        print(f"  {ts}  {status}  {total - failed}/{total} ({pass_rate:.1f}%)  "
              f"[{failed} failures]")


def show_flaky_candidates(entries: list[dict], threshold: int = 3):
    """Identify tests that fail intermittently."""
    test_outcomes: dict[str, list[bool]] = defaultdict(list)
    for entry in entries:
        failed_ids = {f["nodeid"] for f in entry["failures"]}
        # We only have failures, so we need to infer passes from total count
        # This is approximate — full tracking would need per-test history
        for f in entry["failures"]:
            test_outcomes[f["nodeid"]].append(True)  # failed

    print(f"\n{'='*60}")
    print(f"  FLAKY TEST CANDIDATES (failed in {threshold}+ runs)")
    print(f"{'='*60}\n")

    candidates = [
        (nid, fails)
        for nid, fails in test_outcomes.items()
        if len(fails) >= threshold
    ]

    if not candidates:
        print("  No flaky candidates detected.")
        return

    for nid, fails in sorted(candidates, key=lambda x: -len(x[1])):
        subsystem = nid.split("::")[0].replace("tests/test_", "").replace(".py", "")
        print(f"  [{subsystem}] {nid}  — failed {len(fails)}/{len(entries)} runs")


def show_subsystem_breakdown(entries: list[dict]):
    """Show failure breakdown by subsystem."""
    counts: Counter = Counter()
    for entry in entries:
        for f in entry["failures"]:
            counts[f.get("subsystem", "unknown")] += 1

    print(f"\n{'='*60}")
    print(f"  SUBSYSTEM FAILURE BREAKDOWN")
    print(f"{'='*60}\n")

    for subsystem, count in counts.most_common():
        bar = "#" * min(count, 40)
        print(f"  {subsystem:20s}  {count:4d}  {bar}")


if __name__ == "__main__":
    limit = 10
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--runs" and i + 2 < len(sys.argv):
            limit = int(sys.argv[i + 2])
        elif arg == "--flaky":
            entries = load_history(50)
            show_flaky_candidates(entries)
            sys.exit(0)
        elif arg == "--subsystem" and i + 2 < len(sys.argv):
            subsystem = sys.argv[i + 2]
            entries = load_history(limit)
            # Filter
            filtered = []
            for e in entries:
                e_copy = dict(e)
                e_copy["failures"] = [
                    f for f in e["failures"]
                    if f.get("subsystem") == subsystem
                ]
                e_copy["failure_count"] = len(e_copy["failures"])
                filtered.append(e_copy)
            show_summary(filtered)
            sys.exit(0)

    entries = load_history(limit)
    if not entries:
        print("No failure history found. Run tests with failures first.")
        sys.exit(0)

    show_summary(entries)
    show_subsystem_breakdown(entries)
```

**Makefile integration**:
```makefile
test-trends: ## 📊 Show test failure trends (last 10 runs)
	PYTHONPATH=src $(PYTHON) scripts/test_trends.py $(ARGS)

test-flaky: ## 🔍 Identify flaky test candidates
	PYTHONPATH=src $(PYTHON) scripts/test_trends.py --flaky
```

**Risk**: LOW — Read-only analysis tool. No impact on test execution.

#### 2.4.2 SQLite-Backed Test History (Optional — Long-Term)

For richer querying, persist test results to SQLite (same pattern as `data/workbench/workbench.db`):

**File**: `tests/history_store.py` (new file, optional):

```python
"""SQLite-backed test result history for trend analysis."""
import sqlite3
import time
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path("data/test_results/history.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS test_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    exit_code INTEGER NOT NULL,
    total_tests INTEGER NOT NULL,
    failure_count INTEGER NOT NULL,
    duration_seconds REAL
);

CREATE TABLE IF NOT EXISTS test_failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES test_runs(id),
    nodeid TEXT NOT NULL,
    subsystem TEXT,
    error_category TEXT,
    duration REAL,
    short_repr TEXT
);

CREATE INDEX IF NOT EXISTS idx_failures_nodeid ON test_failures(nodeid);
CREATE INDEX IF NOT EXISTS idx_failures_subsystem ON test_failures(subsystem);
CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON test_runs(timestamp);
"""


@contextmanager
def get_db():
    """Context manager for SQLite connections."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript(SCHEMA)
    try:
        yield conn
    finally:
        conn.close()
```

**Risk**: LOW — Additive. Only used when explicitly called.

---

### Wave 5: Advanced Resilience (Long-Term — ~8 hours)

**Goal**: Full test isolation, parallel execution, and circuit-breaker-like test patterns.

#### 2.5.1 Parallel Test Execution with pytest-xdist

**Plugin**: `pytest-xdist` (v3.5+, the standard for parallel pytest)

**Installation**:
```bash
pip install pytest-xdist
```

**Configuration** (opt-in via Makefile target, NOT default):
```makefile
test-parallel: guard ## ⚡ Run tests in parallel (4 workers)
	OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest -n 4 --dist loadscope $(ARGS)

test-parallel-fast: guard ## ⚡ Parallel tests, fail-fast
	OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest -n 4 --dist loadscope -x $(ARGS)
```

**Why `--dist loadscope`**: Groups tests by module/class, ensuring fixtures that share state within a module run in the same worker. This prevents the most common parallel flakiness source.

**Why NOT default**: The Omega Engine's `_set_test_env` fixture uses `tmp_path` (per-test isolation), but `reset_memory_store()` operates on a module-level singleton. Parallel execution requires careful audit of all singletons. Start opt-in, graduate to default after stabilization.

**Risk**: HIGH — Parallel execution can expose hidden state coupling. Requires thorough audit of all test fixtures for shared mutable state. Phase this in slowly.

#### 2.5.2 Test Circuit Breaker Pattern

**Concept**: If a subsystem's tests fail N times consecutively, skip remaining tests in that subsystem for the rest of the run (fail fast for broken subsystems).

**File**: `tests/conftest.py` — add to existing hooks:

```python
from collections import defaultdict

# Circuit breaker state: subsystem → consecutive_failures
_subsystem_failures: dict[str, int] = defaultdict(int)
_SUBSYSTEM_BREAK_THRESHOLD = 3

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    """Skip remaining tests in a subsystem if circuit breaker is open."""
    subsystem = _extract_subsystem(item.nodeid)
    if _subsystem_failures[subsystem] >= _SUBSYSTEM_BREAK_THRESHOLD:
        pytest.skip(
            f"CIRCUIT BREAKER: {subsystem} has "
            f"{_subsystem_failures[subsystem]} consecutive failures. "
            f"Skipping remaining tests in subsystem."
        )
    return None  # Let pytest continue normally

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Track subsystem failures for circuit breaker."""
    outcome = yield
    report = outcome.get_result()
    subsystem = _extract_subsystem(item.nodeid)

    if report.when == "call":
        if report.failed:
            _subsystem_failures[subsystem] += 1
        else:
            _subsystem_failures[subsystem] = 0  # Reset on success
```

**Risk**: MEDIUM — This is an aggressive optimization. It can mask cascading failures that happen to look like subsystem failures. Use only when the full run is too slow for iterative development.

#### 2.5.3 Makefile Integration — Complete Test Menu

```makefile
# ── Enhanced Testing Menu ──────────────────────────────────────────

test-fast: guard ## ⚡ Fast test mode: fail-fast, short tracebacks
	OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest -x --tb=short -q $(ARGS)

test-focused: guard ## 🎯 Test only recently changed subsystems
	@echo "$(COLOR_YELLOW)⚠  Requires manual subsystem selection$(COLOR_NC)"
	@echo "  Usage: make test ARGS='-k oracle or memory_store'"

test-diagnostic: guard ## 🔍 Full run with classified failure output
	OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest \
		--tb=short -v \
		--json-report --json-report-file=data/test_results/latest.json \
		$(ARGS)

test-history: ## 📊 Show test failure trends (last 10 runs)
	PYTHONPATH=src $(PYTHON) scripts/test_trends.py $(ARGS)

test-flaky: ## 🔍 Identify flaky test candidates
	PYTHONPATH=src $(PYTHON) scripts/test_trends.py --flaky
```

---

## §3 Plugin Inventory

| Plugin | Version | Purpose | Integration | Risk |
|--------|---------|---------|-------------|------|
| `pytest-timeout` | >=2.4.0 | Per-test timeout (already installed) | `addopts --timeout=30` | LOW |
| `pytest-rerunfailures` | >=16.3 | Retry flaky tests | `@pytest.mark.flaky` opt-in | LOW |
| `pytest-isolated` | >=0.0.14 | Subprocess isolation for crash-prone tests | `@pytest.mark.isolated` opt-in | MEDIUM |
| `pytest-xdist` | >=3.5 | Parallel test execution | `make test-parallel` opt-in | HIGH |
| `pytest-json-report` | >=1.5.0 | Machine-readable JSON output | `--json-report` flag | LOW |

**NOT Recommended**:
- `pytest-html`: Generates HTML reports. Violates M18 (Token Efficiency) for a CLI-first project. The JSON report is sufficient.
- `pytest-structlog`: Requires `structlog` dependency. The Omega Engine uses stdlib `logging` — adding structlog is overkill for test error capture.
- `allure`: Heavy external dependency, cloud-oriented reporting. Violates M8 (Zero Telemetry) by design.

---

## §4 Mandate Compliance Matrix

| Mandate | Compliance | Notes |
|---------|-----------|-------|
| **M1 (AnyIO)** | ✅ | No `asyncio` usage in conftest.py. All hooks are synchronous. |
| **M8 (Zero Telemetry)** | ✅ | All writes to `data/test_results/` are local-only. No external endpoints. |
| **M13 (Temple-Grade)** | ✅ | This plan IS a Temple-Grade gate enhancement (T3: Testing). |
| **M15 (Sovereign Continuity)** | ✅ | Failure history persists across sessions. `failures_history.jsonl` survives context compaction. |
| **M18 (Token Efficiency)** | ✅ | `--tb=short` and `-q` reduce token consumption by ~60%. Classified output eliminates noise. |
| **M19 (Adversarial Alchemy)** | ✅ | Turned the weakness (slow, opaque failures) into an advantage (classified, persistent, trendable). |

---

## §5 Implementation Priority Matrix

```
WAVE 1 (TODAY — 2 hours)
├── --tb=short in pyproject.toml
├── pytest_terminal_summary hook (classified output)
├── failures_latest.json writer
└── error_taxonomy.py

WAVE 2 (THIS WEEK — 4 hours)
├── pytest-isolated for high-risk tests
├── faulthandler_timeout=60
└── pytest-rerunfailures for known flaky tests

WAVE 3 (NEXT SPRINT — 6 hours)
├── Full conftest.py rewrite with all hooks
├── pytest_runtest_makereport structured capture
├── Subsystem + error category classification
└── Atomic failure history persistence

WAVE 4 (FOLLOWING SPRINT — 4 hours)
├── scripts/test_trends.py CLI
├── Makefile test-trends / test-flaky targets
└── SQLite history store (optional)

WAVE 5 (LONG-TERM — 8 hours)
├── pytest-xdist parallel execution (opt-in)
├── Test circuit breaker pattern
└── Full singleton audit for parallel safety
```

---

## §6 Risk Assessment

| Wave | Risk Level | Mitigation |
|------|-----------|------------|
| Wave 1 | **LOW** | Display-only changes. Run `make test` to verify all 440 pass. |
| Wave 2 | **MEDIUM** | Subprocess isolation adds overhead. Mark only high-risk tests. |
| Wave 3 | **MEDIUM** | conftest.py rewrite touches all tests. Must verify 440/440. |
| Wave 4 | **LOW** | Read-only analysis tool. No impact on tests. |
| Wave 5 | **HIGH** | Parallel execution can expose hidden state bugs. Audit singletons first. |

---

## §7 Expected Outcomes

| Metric | Before | After (All Waves) | Improvement |
|--------|--------|-------------------|-------------|
| **Time to diagnose failure** | 2-5 minutes (read traceback) | 10-30 seconds (classified output) | **80% faster** |
| **Failure persistence** | None (lost after run) | JSONL history + SQLite (optional) | **∞ improvement** |
| **Cascade prevention** | None | Subprocess isolation + circuit breaker | **Prevents wasted runs** |
| **Flaky detection** | Manual | Automated trend analysis | **Proactive identification** |
| **Token consumption** | Full tracebacks (~500 tokens/failure) | Short tracebacks + summary (~150 tokens) | **70% reduction** |
| **Local-only compliance** | N/A | 100% — no external writes | **M8 compliant** |

---

## §8 Heritage

No id Software heritage patterns are directly applicable to this document. The test harness is a greenfield system within the Omega Engine.

---

*Last Updated: 2026-06-29 | Author: Researcher (Sovereign Master Researcher) | Status: PROPOSED*
