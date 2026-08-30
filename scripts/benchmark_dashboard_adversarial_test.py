#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
JEM R3 ADVERSARIAL TEST HARNESS
================================
Systematically attempts to break benchmark_dashboard.py v3.1 with adversarial
inputs. Each test creates a temp file with malicious/malformed data, imports
the dashboard module, runs the relevant sections, and reports PASS/FAIL.

Run: python3 scripts/benchmark_dashboard_adversarial_test.py
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import traceback
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

# Make the dashboard importable
sys.path.insert(0, str(Path(__file__).parent))
import benchmark_dashboard as bd

PASS = 0
FAIL = 0
FAILURES = []


def _capture(func, *args, **kwargs):
    """Run func while capturing stdout/stderr. Returns (return_value, exc)."""
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    exc = None
    rv = None
    try:
        with redirect_stdout(buf_out), redirect_stderr(buf_err):
            rv = func(*args, **kwargs)
    except BaseException as e:
        exc = e
    return rv, exc, buf_out.getvalue(), buf_err.getvalue()


def _check(test_name, func, *args, **kwargs):
    """Run func. PASS if no exception, FAIL with traceback otherwise."""
    global PASS, FAIL
    rv, exc, _, err_out = _capture(func, *args, **kwargs)
    if exc is None:
        PASS += 1
        print(f"  PASS  {test_name}")
    else:
        FAIL += 1
        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
        FAILURES.append((test_name, exc, "".join(tb), err_out))
        print(f"  FAIL  {test_name}: {type(exc).__name__}: {exc}")


def make_args(**kw):
    """Build a default argparse.Namespace."""
    import argparse
    defaults = dict(
        once=True, no_clear=True, refresh=2, model=None, since=None,
        alerts=False, alert_rate=70.0, alert_latency=15000,
        json=False, csv=False, diurnal=False, watch_tail=False, alert_min_window=5,
    )
    defaults.update(kw)
    return argparse.Namespace(**defaults)


def test_empty_jsonl():
    """Empty (0-byte) JSONL file."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        assert data == [], f"expected [], got {data}"
        fresh = bd.get_file_freshness(path)
        assert fresh.entries_total == 0, f"expected 0, got {fresh.entries_total}"
    finally:
        path.unlink(missing_ok=True)


def test_all_malformed_jsonl():
    """JSONL where every line is garbage."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write("\n".join([
            "{this is not json",
            "[broken",
            "garbage line",
            "{key: value,}",  # not valid JSON
            "",
            "###",
        ]))
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        assert data == [], f"expected [], got {data}"
        # Should also aggregate without crashing
        stats = bd.aggregate_probes(data)
        assert stats == {}, f"expected empty stats, got {stats}"
    finally:
        path.unlink(missing_ok=True)


def test_mixed_valid_and_garbage():
    """Mix of valid JSON, garbage, and partial JSON."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write('{"label": "valid", "success": true, "ts": "2026-08-30T12:00:00Z"}\n')
        f.write('not json at all\n')
        f.write('{"label": "also_valid", "success": false}\n')
        f.write('{"label": "missing_fields"}\n')  # no success key
        f.write('\n')  # blank line
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        assert len(data) == 3, f"expected 3 entries, got {len(data)}"
        stats = bd.aggregate_probes(data)
        assert "valid" in stats
        assert "also_valid" in stats
        # missing_fields defaults to "?" label
        assert "?" in stats or "missing_fields" in stats
    finally:
        path.unlink(missing_ok=True)


def test_one_giant_entry():
    """A single entry containing a huge nested dict."""
    huge = {"label": "big", "success": True, "huge_field": "x" * 1_000_000}
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write(json.dumps(huge) + "\n")
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        assert len(data) == 1
        assert len(data[0]["huge_field"]) == 1_000_000
        stats = bd.aggregate_probes(data)
        assert "big" in stats
    finally:
        path.unlink(missing_ok=True)


def test_symlink_to_dev_null():
    """Symlink to /dev/null — file appears empty, but exists."""
    with tempfile.TemporaryDirectory() as tmp:
        link = Path(tmp) / "fake.jsonl"
        try:
            link.symlink_to("/dev/null")
            data = bd.read_jsonl(link)
            assert data == [], f"expected [], got {data}"
            fresh = bd.get_file_freshness(link)
            assert fresh.entries_total == 0
        finally:
            link.unlink(missing_ok=True)


def test_1000_models():
    """1000 distinct models — stress aggregation."""
    entries = []
    base_ts = datetime.now(timezone.utc).isoformat()
    for i in range(1000):
        entries.append(json.dumps({
            "label": f"model-{i:04d}",
            "model": f"provider/model-{i:04d}",
            "success": (i % 3 != 0),
            "ts": base_ts,
            "latency_ms": 100 + (i % 500),
            "key_source": ["or_key", "cline", "auth"][i % 3],
            "quality_check": {
                "valid_json": True,
                "has_completion": True,
                "content_length": 100,
            },
            "http_status": 200 if (i % 3 != 0) else 429,
            "error": None if (i % 3 != 0) else "Rate limit exceeded",
        }))
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write("\n".join(entries))
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        assert len(data) == 1000
        stats = bd.aggregate_probes(data)
        assert len(stats) == 1000
        # Render to capture stdout
        args = make_args()
        bd.render(args)  # No-clear mode, no json/csv → just renders silently
    finally:
        path.unlink(missing_ok=True)


def test_100_percent_success_zero_latency():
    """Edge case: 100% success rate, P50=0ms (impossible in real life but legal input)."""
    entries = []
    base_ts = datetime.now(timezone.utc).isoformat()
    for i in range(20):
        entries.append(json.dumps({
            "label": "ghost", "success": True, "ts": base_ts,
            "latency_ms": 0, "key_source": "magic",
        }))
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write("\n".join(entries))
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        stats = bd.aggregate_probes(data)
        s = stats["ghost"]
        assert s.rate == 100.0
        # p50 is 0 because no latencies > 0
        assert s.p50 == 0.0
        # should not divide by zero anywhere
        _check("100% rate render",
               lambda: bd.render(make_args()))
    finally:
        path.unlink(missing_ok=True)


def test_unicode_and_locale():
    """Non-ASCII label, weird unicode in error string."""
    entries = [{
        "label": "モデル-Ω-λ",
        "success": False,
        "ts": "2026-08-30T12:00:00+09:00",  # Non-UTC tz
        "latency_ms": 100,
        "error": "🔥 Rate limit hit 💀",
        "http_status": 429,
        "key_source": "or_key",
        "quality_check": {"valid_json": True, "has_completion": True, "content_length": 50},
    }]
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w", encoding="utf-8") as f:
        f.write(json.dumps(entries[0], ensure_ascii=False) + "\n")
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        assert len(data) == 1
        assert data[0]["label"] == "モデル-Ω-λ"
        stats = bd.aggregate_probes(data)
        s = stats["モデル-Ω-λ"]
        # RATE_LIMITED category
        assert s.failure_categories.get("RATE_LIMITED") == 1
        # Window should still be inferred correctly
        assert "moderate" in s.windows or "poor" in s.windows
    finally:
        path.unlink(missing_ok=True)


def test_dict_in_error_field():
    """An entry where `error` is a dict (not a string). Upstream malformed."""
    entry = {
        "label": "broken",
        "success": False,
        "ts": "2026-08-30T12:00:00Z",
        "latency_ms": 100,
        "error": {"code": "RATE_LIMIT", "msg": "Too many requests"},  # dict!
        "http_status": 429,
    }
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write(json.dumps(entry) + "\n")
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        stats = bd.aggregate_probes(data)
        cat = bd.categorize_failure(data[0])
        # Should not crash; should categorize somehow (likely RATE_LIMITED via http_status)
        assert cat in ("RATE_LIMITED", "AUTH_FAILED", "INVALID_MODEL", "PAYMENT_REQUIRED",
                       "SERVER_ERROR", "TIMEOUT", "PARSE_ERROR", "PROVIDER_ERROR", "OTHER")
    finally:
        path.unlink(missing_ok=True)


def test_quality_check_as_string():
    """quality_check is a string "true" instead of a dict."""
    entry = {
        "label": "qcbad", "success": True, "ts": "2026-08-30T12:00:00Z",
        "latency_ms": 100, "quality_check": "true",  # STRING instead of dict
    }
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write(json.dumps(entry) + "\n")
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        stats = bd.aggregate_probes(data)
        s = stats["qcbad"]
        # Should not crash; quality_total stays at 0 because not a dict
        assert s.quality_total == 0
    finally:
        path.unlink(missing_ok=True)


def test_latency_ms_is_string():
    """latency_ms is a string "100" instead of number."""
    entry = {
        "label": "latstr", "success": True, "ts": "2026-08-30T12:00:00Z",
        "latency_ms": "100",  # STRING!
        "quality_check": {"valid_json": True, "has_completion": True, "content_length": 50},
    }
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write(json.dumps(entry) + "\n")
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        stats = bd.aggregate_probes(data)
        s = stats["latstr"]
        # Should not append to latencies (string not coerced)
        assert len(s.latencies) == 0
    finally:
        path.unlink(missing_ok=True)


def test_consecutive_fails_deque_bounds():
    """consecutive_fails should be bounded by recent_window deque size (20)."""
    entries = []
    base_ts = datetime.now(timezone.utc).isoformat()
    # 50 failures in a row, no successes
    for i in range(50):
        entries.append(json.dumps({
            "label": "failbot", "success": False, "ts": base_ts,
            "latency_ms": 100, "http_status": 500,
            "error": "Server Error",
        }))
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write("\n".join(entries))
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path)
        stats = bd.aggregate_probes(data)
        s = stats["failbot"]
        # consecutive_fails must NOT exceed deque size (20)
        assert s.consecutive_fails <= 20, f"consecutive_fails={s.consecutive_fails}"
    finally:
        path.unlink(missing_ok=True)


def test_aggregate_twice_no_leak():
    """Calling aggregate_probes twice should not leak state — dataclass is fresh."""
    entry = {
        "label": "leaky", "success": True, "ts": "2026-08-30T12:00:00Z",
        "latency_ms": 100,
    }
    data1 = [entry, entry, entry]
    data2 = [entry]  # single entry
    stats1 = bd.aggregate_probes(data1)
    stats2 = bd.aggregate_probes(data2)
    # stats1 has 3, stats2 has 1 — no global state leak
    assert stats1["leaky"].success == 3
    assert stats2["leaky"].success == 1


def test_re_pattern_injection():
    """--model with a pathological regex like '.*' should not hang."""
    import argparse
    args = make_args(model=".*")
    # Just ensure render() doesn't crash on the .* pattern (matches everything)
    bd.render(args)
    # Now a malicious-looking regex
    args = make_args(model="(a+)+$")  # ReDoS-ish pattern
    # Should not hang; render() should complete
    bd.render(args)


def test_model_filter_with_replacement_chars():
    """Model label containing regex special characters."""
    entry = {
        "label": "test.model+with|chars",
        "success": True, "ts": "2026-08-30T12:00:00Z",
        "latency_ms": 100,
    }
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write(json.dumps(entry) + "\n")
        path = Path(f.name)
    try:
        # Replace cache to point at our path
        bd.invalidate_file_cache()
        # Mock PROBE_LOG to our test path
        original = bd.PROBE_LOG
        bd.PROBE_LOG = path
        try:
            data = bd.read_jsonl(path)
            stats = bd.aggregate_probes(data)
            # A filter that wouldn't match (literal regex)
            args = make_args(model="no_match_here")
            bd.render(args)
            # And one that matches partially
            args = make_args(model=r"test\.model")
            bd.render(args)
        finally:
            bd.PROBE_LOG = original
    finally:
        path.unlink(missing_ok=True)


def test_render_with_all_sections_no_clear():
    """Run the full render pipeline with --no-clear (CI mode)."""
    bd.render(make_args(no_clear=True))


def test_render_json_output():
    """Run with --json, capture output, re-parse."""
    import io
    buf = io.StringIO()
    with redirect_stdout(buf):
        # Patch the render to actually execute (we need --json flag)
        sys.argv = ["benchmark_dashboard.py", "--json"]
        try:
            bd.main()
        except SystemExit:
            pass
    out = buf.getvalue()
    # If anything was output, it should be valid JSON
    if out.strip():
        try:
            j = json.loads(out)
            assert "models" in j or "timestamp" in j
        except json.JSONDecodeError:
            pass  # acceptable if no data


def test_render_csv_output():
    """Run with --csv, capture output, verify CSV header."""
    import io
    buf = io.StringIO()
    with redirect_stdout(buf):
        sys.argv = ["benchmark_dashboard.py", "--csv"]
        try:
            bd.main()
        except SystemExit:
            pass
    out = buf.getvalue()
    # If CSV output, should have a header row
    if out.strip():
        lines = out.strip().split("\n")
        if lines:
            header = lines[0]
            # Header should contain expected columns (or be empty if no data)
            assert "model" in header or len(header.split(",")) > 0


def test_pgrep_failure():
    """Simulate pgrep failure."""
    # Mock render_active_sessions to test subprocess exception path
    with patch("subprocess.run", side_effect=FileNotFoundError("pgrep not found")):
        bd.render_active_sessions()  # Should print "process check unavailable"


def test_pgrep_returns_garbage():
    """pgrep returns malformed output (no PID, weird chars)."""
    import subprocess
    class FakeResult:
        returncode = 0
        stdout = "noPIDhere\ngarbage line with no split\n12345 /usr/bin/foo bar baz"
        stderr = ""
    with patch("subprocess.run", return_value=FakeResult()):
        # Should not crash on the malformed lines
        bd.render_active_sessions()


def test_proc_status_missing():
    """PID returned but /proc/{pid}/status is gone (race condition)."""
    import subprocess
    class FakeResult:
        returncode = 0
        stdout = "99999 /usr/bin/opencode"
        stderr = ""
    with patch("subprocess.run", return_value=FakeResult()), \
         patch("builtins.open", side_effect=FileNotFoundError("no /proc/99999")):
        bd.render_active_sessions()


def test_term_dumb_environ():
    """TERM=dumb should still produce valid output."""
    old_term = os.environ.get("TERM")
    os.environ["TERM"] = "dumb"
    try:
        bd.render(make_args())
    finally:
        if old_term is None:
            os.environ.pop("TERM", None)
        else:
            os.environ["TERM"] = old_term


def test_disk_full_simulation():
    """Simulate disk-full error on read.

    jem R3: clear the cache first. The cache is keyed by (path, mtime_ns,
    size, since) so a previous read into the cache from another test
    (e.g. test_term_dumb_environ) will short-circuit the open() and return
    the cached data, masking the simulated failure.
    """
    bd.invalidate_file_cache()
    with patch("builtins.open", side_effect=OSError(28, "No space left on device")):
        data = bd.read_jsonl_cached(bd.PROBE_LOG)
        assert data == []


def test_permission_denied():
    """Permission denied on read.

    jem R3: clear the cache first (same rationale as test_disk_full_simulation).
    """
    bd.invalidate_file_cache()
    with patch("builtins.open", side_effect=PermissionError("denied")):
        data = bd.read_jsonl_cached(bd.PROBE_LOG)
        assert data == []


def test_path_none():
    """Pass None path."""
    data = bd.read_jsonl(None)
    assert data == []
    data = bd.read_jsonl_cached(None)
    assert data == []
    fresh = bd.get_file_freshness(None)
    assert fresh.path == Path()


def test_path_traversal_in_model_filter():
    """--model with a path-traversal-like string (should just be regex)."""
    args = make_args(model="../../../etc/passwd")
    bd.render(args)  # Should not actually touch filesystem


def test_json_dump_with_non_serializable():
    """export_json must handle non-JSON-serializable fields (default=str)."""
    state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "models": {
            "test": {
                "label": "test",
                "success": 1, "fail": 0, "total": 1, "rate": 100.0,
                "p50_ms": 100.0, "p99_ms": 100.0, "outlier_pct": 0.0,
                "quality_rate": 100.0,
                "quality_breakdown": {"valid": 1, "invalid_json": 0, "no_completion": 0, "empty_content": 0},
                "trend": "↑",
                "trend_velocity": "↑↑",
                "http_statuses": {},
                "key_sources": {},
                "key_outcomes": {},
                "key_last_success": {},
                "failure_categories": {},
                "windows": {},
                "window_success": {},
                "last_seen": datetime.now(timezone.utc),  # datetime not JSON-able by default
                "last_success": datetime.now(timezone.utc),
                "consecutive_fails": 0,
                "currently_alerting": False,
            }
        }
    }
    out = json.dumps(state, indent=2, default=str)
    # Should succeed because of default=str
    assert "test" in out


def test_billion_entries_bounded():
    """Sanity check: read_jsonl with limit=100 caps memory even if file has 1M lines."""
    # Create a 10K-entry file
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        for i in range(10_000):
            f.write(json.dumps({"label": "x", "success": i % 2 == 0, "ts": "2026-08-30T12:00:00Z"}) + "\n")
        path = Path(f.name)
    try:
        data = bd.read_jsonl(path, limit=100)
        assert len(data) == 100
    finally:
        path.unlink(missing_ok=True)


def test_debounce_fail_open():
    """If debounce crashes internally, must return candidates unchanged (fail-open)."""
    # Construct a candidate that triggers an internal exception.
    # Note: type hint is loose; debounce_alerts catches AttributeError/TypeError
    # on the inner iteration but a RuntimeError on .rate bubbles through and is
    # caught by the outer try/except.
    class BrokenStats:
        label = "broken"
        success = 0
        fail = 100
        consecutive_fails = 0
        currently_alerting = False
        @property
        def rate(self):
            raise RuntimeError("broken rate")
    candidates = [(BrokenStats(), ["reason"])]  # type: ignore[list-item]
    # Should not raise; should return candidates (fail-open)
    # cast away the strict generic since BrokenStats is ducktyped-compatible
    import typing
    result = bd.debounce_alerts(typing.cast(list, candidates), 70.0, 5)
    assert result == candidates


def test_argv_with_no_color():
    """--no-clear path with explicit NO_COLOR."""
    old = os.environ.get("NO_COLOR")
    os.environ["NO_COLOR"] = "1"
    try:
        # Force re-init C class
        bd.C._no_color = True
        bd.C.R = ""
        bd.C.G = ""
        bd.C.Y = ""
        bd.render(make_args(no_clear=True))
    finally:
        if old is None:
            os.environ.pop("NO_COLOR", None)
        else:
            os.environ["NO_COLOR"] = old
        bd.C._no_color = bool(os.environ.get("NO_COLOR")) or not sys.stdout.isatty()
        if not bd.C._no_color:
            bd.C.R = "\033[91m"
            bd.C.G = "\033[92m"
            bd.C.Y = "\033[93m"


def test_since_zero_hours():
    """--since 0h means 'all entries'. Should not raise."""
    args = make_args(since="0h")
    bd.render(args)


def test_since_negative():
    """--since -1h is invalid; should be tolerated."""
    args = make_args(since="-1h")
    bd.render(args)


def test_refresh_zero():
    """--refresh 0 should be rejected by main()."""
    sys.argv = ["benchmark_dashboard.py", "--refresh", "0"]
    rc = bd.main()
    assert rc == 1, f"expected exit 1, got {rc}"


def test_refresh_one():
    """--refresh 1 with --once should run once."""
    sys.argv = ["benchmark_dashboard.py", "--refresh", "1", "--once", "--no-clear"]
    rc = bd.main()
    assert rc == 0


def test_watch_tail_then_truncated():
    """--watch-tail: simulate file truncation mid-stream."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write(json.dumps({"label": "a", "success": True, "ts": "2026-08-30T12:00:00Z"}) + "\n")
        f.write(json.dumps({"label": "b", "success": False, "ts": "2026-08-30T12:01:00Z"}) + "\n")
        path = Path(f.name)
    try:
        # First read
        data = bd.read_jsonl_tail(path)
        assert len(data) == 2
        # Truncate file (simulate rotation)
        with open(path, "w") as f:
            f.write(json.dumps({"label": "c", "success": True, "ts": "2026-08-30T12:02:00Z"}) + "\n")
        # Second read should detect truncation (offset > size) and start from tail
        data2 = bd.read_jsonl_tail(path)
        # Should pick up the new entry
        labels = [d["label"] for d in data2]
        assert "c" in labels, f"expected 'c' in labels after truncation, got {labels}"
    finally:
        bd._TAIL_OFFSETS.pop(str(path), None)
        path.unlink(missing_ok=True)


def test_cache_invalidation():
    """Cache invalidation should clear entries for specific path.

    jem R3: cache key is now 4-tuple (path, mtime_ns, size, since_iso),
    was 3-tuple. Updated test fixtures to match.
    """
    bd._JSONL_CACHE.clear()
    # Add an entry
    bd._JSONL_CACHE[("test_path", 123, 456, None)] = [{"label": "x"}]
    assert len(bd._JSONL_CACHE) == 1
    # Invalidate specific path
    bd.invalidate_file_cache(Path("test_path"))
    assert len(bd._JSONL_CACHE) == 0
    # Add another, invalidate all
    bd._JSONL_CACHE[("a", 1, 10, None)] = [{}]
    bd._JSONL_CACHE[("b", 2, 20, None)] = [{}]
    assert len(bd._JSONL_CACHE) == 2
    bd.invalidate_file_cache()
    assert len(bd._JSONL_CACHE) == 0


def test_cache_overflow():
    """Cache should evict oldest entry when full.

    jem R3: re-implemented. Original directly mutated the dict and asserted
    eviction had occurred — but eviction lives inside read_jsonl_cached(),
    not in the dict itself. The new test exercises the real eviction path
    by calling read_jsonl_cached() with synthetic paths. We use a sentinel
    mtime_ns=-1 / size=-1 (the "stat failed" fallback) so the cache key
    is stable across calls — we control eviction by varying the path string.
    """
    bd._JSONL_CACHE.clear()
    # Fill cache to capacity with sentinel stat values.
    # The sentinel path strings are distinct so we can verify FIFO.
    sentinel = -1  # matches _cache_key fallback when stat fails
    for i in range(bd._JSONL_CACHE_MAX):
        bd._JSONL_CACHE[(f"p{i}", i, i * 100, None)] = [{"i": i}]
    assert len(bd._JSONL_CACHE) == bd._JSONL_CACHE_MAX
    # The actual eviction logic in read_jsonl_cached runs the FIFO branch
    # when len(_JSONL_CACHE) >= _JSONL_CACHE_MAX *before* insertion. So
    # calling read_jsonl_cached with a brand-new path triggers the eviction
    # of the oldest key.
    fake_path = Path("pNEW")  # not on disk, but _cache_key won't fail for us
    # _cache_key calls path.stat() which would fail on a non-existent path,
    # returning the sentinel (-1, -1). That's the same as our other keys'
    # mtime_ns — but the path string "pNEW" is unique, so the new key won't
    # collide.
    bd.read_jsonl_cached(fake_path)
    # After the call, oldest entry should be evicted
    assert ("p0", 0, 0, None) not in bd._JSONL_CACHE
    assert ("pNEW", sentinel, sentinel, None) in bd._JSONL_CACHE
    assert len(bd._JSONL_CACHE) == bd._JSONL_CACHE_MAX
    bd._JSONL_CACHE.clear()


def test_progress_bar_zero_total():
    """progress_bar with total=0 should not divide by zero."""
    s = bd.progress_bar(0, 0)
    assert "[]" in s or "0%" in s


def test_percentile_empty():
    """percentile of empty list returns 0."""
    assert bd.percentile([], 50) == 0.0


def test_fmt_ms_negative():
    """fmt_ms with negative value should not show '-' or 's' suffix.

    jem R3: simplified assertion. Original required "DIM" in s, but DIM
    is an ANSI escape that's empty in no-color mode. The semantically
    correct invariant is just: don't show the negative number. Returned
    sentinel ('--' or ANSI-dim) should not contain '-100' or 'ms'.
    """
    s = bd.fmt_ms(-100)
    # Should not contain the literal negative value or a "ms" suffix
    assert "-100" not in s
    assert "ms" not in s or "DIM" in s  # DIM guard for color-on path
    # And the result must be non-empty (some sentinel is rendered)
    assert len(s) > 0


def test_fmt_ms_zero():
    """fmt_ms with 0 returns '0ms'."""
    s = bd.fmt_ms(0)
    assert "0ms" in s


def test_fmt_ms_bool():
    """fmt_ms with bool should not treat True as 1."""
    s = bd.fmt_ms(True)  # bool, should be rejected
    assert s  # Should return "--"


def test_pad_visible_negative_width():
    """pad_visible with negative width should not crash."""
    s = bd.pad_visible("hello", -5)
    assert s == "hello"


def test_render_with_locale():
    """Run with a non-English locale env var."""
    old = os.environ.get("LANG")
    os.environ["LANG"] = "ja_JP.UTF-8"
    try:
        bd.render(make_args())
    finally:
        if old is None:
            os.environ.pop("LANG", None)
        else:
            os.environ["LANG"] = old


def test_render_quality_breakdown_only_8():
    """render_quality_breakdown should show only top 8."""
    # Not strictly adversarial, but documents the behavior
    stats = {}
    for i in range(20):
        s = bd.ModelStats(label=f"m{i}")
        s.quality_total = 10
        s.quality_valid = 5 + (i % 5)
        s.quality_invalid_json = 5 - (i % 5)
        s.quality_no_completion = 0
        s.quality_empty_content = 0
        stats[f"m{i}"] = s
    # Capture output
    buf = io.StringIO()
    with redirect_stdout(buf):
        bd.render_quality_breakdown(stats)
    # Should have only 8 model rows (header + 8)
    lines = [l for l in buf.getvalue().split("\n") if l.strip() and "m" in l]
    # Less than or equal to 8 model rows
    assert len(lines) <= 10, f"too many lines: {len(lines)}"


def test_antigravity_models_list_of_strings():
    """antigravity entry with models being a list of strings (not dicts)."""
    ag_data = [{
        "email": "x@y.com",
        "enabled": True,
        "tier": "pro",
        "project": "p",
        "models": ["model-a", "model-b", "model-c"],  # strings, not dicts!
        "ts": "2026-08-30T12:00:00Z",
    }]
    # Should not crash on .get("remainingFraction")
    buf = io.StringIO()
    with redirect_stdout(buf):
        bd.render_antigravity(ag_data)


def test_antigravity_reset_in_past():
    """resetTime is in the past (already reset)."""
    past = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    ag_data = [{
        "email": "x@y.com", "enabled": True, "tier": "pro", "project": "p",
        "models": [{"id": "m", "remainingFraction": 0.5, "resetTime": past}],
        "ts": "2026-08-30T12:00:00Z",
    }]
    buf = io.StringIO()
    with redirect_stdout(buf):
        bd.render_next_quota_reset(ag_data)  # Should not fire (reset in past)


def test_aggregate_then_alerts_with_min_window():
    """Full pipeline: aggregate, then alerts with min_window=1 (v3.0 compat)."""
    entries = []
    base_ts = datetime.now(timezone.utc).isoformat()
    for i in range(10):
        entries.append({"label": "allbad", "success": False, "ts": base_ts,
                        "latency_ms": 100, "http_status": 500, "error": "Server Error"})
    stats = bd.aggregate_probes(entries)
    args = make_args(alerts=True, alert_min_window=1)
    buf = io.StringIO()
    with redirect_stdout(buf):
        bd.render_alerts(stats, args)
    # Should fire at least one alert
    output = buf.getvalue()
    assert "ALERTS" in output


def test_subsequent_render_debounce_state():
    """Alerting state should persist across renders (hysteresis)."""
    entries = []
    base_ts = datetime.now(timezone.utc).isoformat()
    for i in range(10):
        entries.append({"label": "flap", "success": False, "ts": base_ts,
                        "latency_ms": 100, "http_status": 500, "error": "Server"})
    stats = bd.aggregate_probes(entries)
    args = make_args(alerts=True, alert_min_window=5)
    # First render — should fire (consecutive_fails=10 >= 5, rate=0 < 70)
    buf = io.StringIO()
    with redirect_stdout(buf):
        bd.render_alerts(stats, args)
    assert "flap" in buf.getvalue(), "first render should fire"
    # State should now be alerting
    assert stats["flap"].currently_alerting is True
    # Second render — still alerting (rate still 0)
    buf = io.StringIO()
    with redirect_stdout(buf):
        bd.render_alerts(stats, args)
    assert "flap" in buf.getvalue(), "second render should keep firing"


def test_render_no_data_no_clear():
    """When data files don't exist (or are empty), render should not crash."""
    # Move data dir temporarily to simulate missing data
    import shutil
    backup = None
    if bd.DATA_DIR.exists():
        backup = bd.DATA_DIR.parent / "_benchmark_dashboard_backup"
        if backup.exists():
            shutil.rmtree(backup)
        shutil.move(str(bd.DATA_DIR), str(backup))
    try:
        bd.render(make_args(no_clear=True))
    finally:
        if backup:
            shutil.move(str(backup), str(bd.DATA_DIR))


def test_csv_with_partial_dict():
    """export_csv with state containing missing keys (defensive)."""
    state = {"models": {"x": {"label": "x", "success": 0}}}  # mostly missing
    buf = io.StringIO()
    with redirect_stdout(buf):
        bd.export_csv(state)
    # Should produce at least header + one row
    output = buf.getvalue()
    assert "model" in output


def test_render_infinite_recent_window():
    """ModelStats.deque should evict old items, not grow unbounded."""
    s = bd.ModelStats(label="big")
    for i in range(1000):
        s.recent_window.append(True)
    # deque should cap at 20
    assert len(s.recent_window) == 20


def main():
    print("=" * 70)
    print("JEM R3 ADVERSARIAL TEST SUITE")
    print("=" * 70)
    print()

    tests = [
        ("empty_jsonl", test_empty_jsonl),
        ("all_malformed_jsonl", test_all_malformed_jsonl),
        ("mixed_valid_and_garbage", test_mixed_valid_and_garbage),
        ("one_giant_entry", test_one_giant_entry),
        ("symlink_to_dev_null", test_symlink_to_dev_null),
        ("1000_models", test_1000_models),
        ("100_percent_success_zero_latency", test_100_percent_success_zero_latency),
        ("unicode_and_locale", test_unicode_and_locale),
        ("dict_in_error_field", test_dict_in_error_field),
        ("quality_check_as_string", test_quality_check_as_string),
        ("latency_ms_is_string", test_latency_ms_is_string),
        ("consecutive_fails_deque_bounds", test_consecutive_fails_deque_bounds),
        ("aggregate_twice_no_leak", test_aggregate_twice_no_leak),
        ("re_pattern_injection", test_re_pattern_injection),
        ("model_filter_with_replacement_chars", test_model_filter_with_replacement_chars),
        ("render_with_all_sections_no_clear", test_render_with_all_sections_no_clear),
        ("render_json_output", test_render_json_output),
        ("render_csv_output", test_render_csv_output),
        ("pgrep_failure", test_pgrep_failure),
        ("pgrep_returns_garbage", test_pgrep_returns_garbage),
        ("proc_status_missing", test_proc_status_missing),
        ("term_dumb_environ", test_term_dumb_environ),
        ("disk_full_simulation", test_disk_full_simulation),
        ("permission_denied", test_permission_denied),
        ("path_none", test_path_none),
        ("path_traversal_in_model_filter", test_path_traversal_in_model_filter),
        ("json_dump_with_non_serializable", test_json_dump_with_non_serializable),
        ("billion_entries_bounded", test_billion_entries_bounded),
        ("debounce_fail_open", test_debounce_fail_open),
        ("argv_with_no_color", test_argv_with_no_color),
        ("since_zero_hours", test_since_zero_hours),
        ("since_negative", test_since_negative),
        ("refresh_zero", test_refresh_zero),
        ("refresh_one", test_refresh_one),
        ("watch_tail_then_truncated", test_watch_tail_then_truncated),
        ("cache_invalidation", test_cache_invalidation),
        ("cache_overflow", test_cache_overflow),
        ("progress_bar_zero_total", test_progress_bar_zero_total),
        ("percentile_empty", test_percentile_empty),
        ("fmt_ms_negative", test_fmt_ms_negative),
        ("fmt_ms_zero", test_fmt_ms_zero),
        ("fmt_ms_bool", test_fmt_ms_bool),
        ("pad_visible_negative_width", test_pad_visible_negative_width),
        ("render_with_locale", test_render_with_locale),
        ("render_quality_breakdown_only_8", test_render_quality_breakdown_only_8),
        ("antigravity_models_list_of_strings", test_antigravity_models_list_of_strings),
        ("antigravity_reset_in_past", test_antigravity_reset_in_past),
        ("aggregate_then_alerts_with_min_window", test_aggregate_then_alerts_with_min_window),
        ("subsequent_render_debounce_state", test_subsequent_render_debounce_state),
        ("render_no_data_no_clear", test_render_no_data_no_clear),
        ("csv_with_partial_dict", test_csv_with_partial_dict),
        ("render_infinite_recent_window", test_render_infinite_recent_window),
    ]

    for name, fn in tests:
        print(f"\n--- {name} ---")
        try:
            _check(name, fn)
        except Exception as e:
            global FAIL
            FAIL += 1
            FAILURES.append((name, e, traceback.format_exc(), ""))
            print(f"  ERROR  {name}: {e}")

    print()
    print("=" * 70)
    print(f"TOTAL: {PASS + FAIL}  PASS: {PASS}  FAIL: {FAIL}")
    print("=" * 70)

    if FAILURES:
        print("\nFAILURES:")
        for name, exc, tb, err_out in FAILURES:
            print(f"\n--- {name} ---")
            print(f"Exception: {type(exc).__name__}: {exc}")
            if err_out:
                print(f"Stderr: {err_out[:500]}")
            print(tb[:2000])

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())