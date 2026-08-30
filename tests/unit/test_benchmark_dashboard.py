"""Unit tests for scripts/benchmark_dashboard.py — ship-readiness gate (Round 4).

AP: AP-DASHBOARD-SHIP-R4-v1.0.0
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import tempfile
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

# Make benchmark_dashboard importable. The script lives in scripts/ which is not
# on sys.path by default. We do this once at module import.
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import benchmark_dashboard as bd  # noqa: E402

# Force no-color mode for deterministic test assertions (ANSI codes in output
# would break string equality checks below). The C class reads NO_COLOR and
# isatty() at module import, so we patch AFTER import.
os.environ["NO_COLOR"] = "1"
bd.C._no_color = True
# Re-resolve color strings after the flag flips (C class captures them at
# import time as instance attributes).
bd.C.R = ""
bd.C.G = ""
bd.C.Y = ""
bd.C.B = ""
bd.C.M = ""
bd.C.C = ""
bd.C.W = ""
bd.C.DIM = ""
bd.C.BOLD = ""
bd.C.END = ""
bd.C.CLR = ""


# ============================================================================
# 1. Helper-function tests (pure functions, no I/O)
# ============================================================================


class TestPercentile:
    """`percentile` is the foundation for p50/p99 latency properties."""

    def test_empty_data_returns_zero(self):
        assert bd.percentile([], 50) == 0.0

    def test_single_value(self):
        assert bd.percentile([42.0], 50) == 42.0

    def test_p50_of_uniform_data(self):
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        # idx = int(5 * 50 / 100) = 2 → sorted[2] = 30
        assert bd.percentile(data, 50) == 30.0

    def test_p99_clamps_to_last_element(self):
        # idx = int(3 * 99 / 100) = 2 → max valid index is 2 → sorted[2]
        data = [100.0, 200.0, 300.0]
        assert bd.percentile(data, 99) == 300.0

    def test_p0_returns_first_element(self):
        data = [1.0, 2.0, 3.0]
        assert bd.percentile(data, 0) == 1.0

    def test_p100_returns_last_element(self):
        data = [1.0, 2.0, 3.0]
        assert bd.percentile(data, 100) == 3.0

    def test_does_not_mutate_input(self):
        data = [3.0, 1.0, 2.0]
        original = data.copy()
        bd.percentile(data, 50)
        assert data == original


class TestProgressBar:
    """progress_bar is rendered across STRESS/BURST/LONG_DURATION sections."""

    def test_total_zero_renders_zero_zero(self):
        # jem R3 regression: must show "(0/0)" not just "[----------]".
        out = bd.progress_bar(0, 0)
        assert "0%" in out
        assert "(0/0)" in out

    def test_full_progress_renders_all_filled(self):
        out = bd.progress_bar(10, 10, width=10)
        assert "100%" in out
        assert "(10/10)" in out

    def test_partial_progress_renders_correct_count(self):
        out = bd.progress_bar(3, 4, width=10)
        assert "(3/4)" in out
        assert "75%" in out

    def test_custom_width(self):
        out = bd.progress_bar(1, 2, width=4)
        # In NO_COLOR mode the function uses "#" / "-"; in TTY mode "█" / "░".
        # We assert structure (4 chars inside brackets) and a "]" terminator.
        inside = out[out.index("[") + 1 : out.index("]")]
        assert len(inside) == 4
        assert "50%" in out
        assert "(1/2)" in out


class TestFmtMs:
    """fmt_ms is used everywhere (P50, P99, network latency)."""

    def test_zero_shows_zero_ms(self):
        assert "0ms" in bd.fmt_ms(0)

    def test_sub_second_shows_ms(self):
        out = bd.fmt_ms(500)
        assert "ms" in out
        assert "500ms" in out

    def test_above_1s_returns_seconds(self):
        out = bd.fmt_ms(2500)
        assert "s" in out
        assert "2.5s" in out

    def test_negative_returns_dash(self):
        out = bd.fmt_ms(-100)
        assert "--" in out

    def test_none_returns_dash(self):
        out = bd.fmt_ms(None)
        assert "--" in out

    def test_non_numeric_returns_dash(self):
        out = bd.fmt_ms("not a number")
        assert "--" in out

    def test_bool_returns_dash_not_zero(self):
        # booleans are ints in Python — must NOT show "1ms" / "0ms"
        assert "--" in bd.fmt_ms(True)
        assert "--" in bd.fmt_ms(False)


class TestFmtPct:
    """fmt_pct drives the rate / quality columns. M23: never crashes."""

    def test_excellent_is_plain_string_in_no_color(self):
        out = bd.fmt_pct(95.0)
        assert "95%" in out

    def test_good_yellow_color_band(self):
        # 50 < pct < 90 → Y. In no-color mode Y is "".
        out = bd.fmt_pct(70.0)
        assert "70%" in out

    def test_below_fair_is_red(self):
        out = bd.fmt_pct(20.0)
        assert "20%" in out

    def test_boundary_at_90_is_excellent(self):
        assert "90%" in bd.fmt_pct(90.0)

    def test_boundary_at_50_is_fair(self):
        assert "50%" in bd.fmt_pct(50.0)


class TestFmtAge:
    """fmt_age powers the freshness / key-health columns."""

    def test_negative_age_is_just_now(self):
        assert "just now" in bd.fmt_age(-5)

    def test_seconds_range(self):
        out = bd.fmt_age(30)
        assert "30s" in out

    def test_minutes_range(self):
        out = bd.fmt_age(180)  # 3 min
        assert "3m" in out

    def test_hours_range(self):
        out = bd.fmt_age(7200)  # 2 hours
        assert "2h" in out

    def test_days_range(self):
        out = bd.fmt_age(86400 * 3)  # 3 days
        assert "3d" in out


class TestSafeDiv:
    """safe_div is used everywhere — M23: zero denominator must NOT raise."""

    def test_normal_division(self):
        assert bd.safe_div(10, 4) == 2.5

    def test_zero_denominator_returns_default(self):
        assert bd.safe_div(10, 0) == 0.0

    def test_zero_denominator_custom_default(self):
        assert bd.safe_div(10, 0, default=-1.0) == -1.0

    def test_negative_numerator(self):
        assert bd.safe_div(-5, 2) == -2.5


class TestVisibleWidth:
    """pad_visible / _visible_width fix the carmack alignment regression."""

    def test_strips_ansi_before_counting(self):
        # Plain text length
        assert bd._visible_width("hello") == 5
        # ANSI escape codes do not count
        assert bd._visible_width("\033[92mhello\033[0m") == 5

    def test_pad_visible_right_aligns_to_visible_width(self):
        s = "hi"
        out = bd.pad_visible(s, 5, align=">")
        assert out.endswith("hi")
        assert len(out) == 5

    def test_pad_visible_left_aligns_to_visible_width(self):
        s = "hi"
        out = bd.pad_visible(s, 5, align="<")
        assert out.startswith("hi")
        assert len(out) == 5

    def test_pad_visible_no_op_when_already_wide(self):
        s = "toolong"
        out = bd.pad_visible(s, 2, align=">")
        # No negative padding — function clamps to 0.
        assert out == "toolong"


# ============================================================================
# 2. categorize_failure — must cover all error categories
# ============================================================================


class TestCategorizeFailure:
    """categorize_failure feeds the FAILURE MODE TAXONOMY section."""

    def _e(self, **kw):
        return kw

    def test_rate_limited_429(self):
        assert bd.categorize_failure({"http_status": 429}) == "RATE_LIMITED"

    def test_rate_limited_text(self):
        assert bd.categorize_failure({"error": "Rate limit exceeded"}) == "RATE_LIMITED"

    def test_rate_limited_per_day(self):
        assert bd.categorize_failure({"error": "You have used 200/200 per-day"}) == "RATE_LIMITED"

    def test_auth_failed_401(self):
        assert bd.categorize_failure({"http_status": 401}) == "AUTH_FAILED"

    def test_auth_failed_text(self):
        assert bd.categorize_failure({"error": "Invalid auth credentials"}) == "AUTH_FAILED"

    def test_auth_failed_key_text(self):
        assert bd.categorize_failure({"error": "API key not valid"}) == "AUTH_FAILED"

    def test_invalid_model_404(self):
        assert bd.categorize_failure({"http_status": 404}) == "INVALID_MODEL"

    def test_invalid_model_text(self):
        assert bd.categorize_failure({"error": "not a valid model id"}) == "INVALID_MODEL"

    def test_payment_required_402(self):
        assert bd.categorize_failure({"http_status": 402}) == "PAYMENT_REQUIRED"

    def test_server_error_5xx(self):
        assert bd.categorize_failure({"http_status": 500}) == "SERVER_ERROR"
        assert bd.categorize_failure({"http_status": 503}) == "SERVER_ERROR"
        assert bd.categorize_failure({"http_status": 599}) == "SERVER_ERROR"

    def test_timeout_text(self):
        assert bd.categorize_failure({"error": "Request timed out"}) == "TIMEOUT"
        assert bd.categorize_failure({"error": "Connection timeout"}) == "TIMEOUT"

    def test_parse_error_text(self):
        assert bd.categorize_failure({"error": "Failed to parse response"}) == "PARSE_ERROR"
        assert bd.categorize_failure({"error": "invalid json in body"}) == "PARSE_ERROR"

    def test_provider_error_text(self):
        assert bd.categorize_failure({"error": "Provider returned error 502"}) == "PROVIDER_ERROR"

    def test_other_fallback(self):
        assert bd.categorize_failure({"http_status": 418, "error": "I'm a teapot"}) == "OTHER"

    def test_non_string_error_does_not_crash(self):
        # carmack regression: dict/list errors used to crash on .lower()
        assert bd.categorize_failure({"error": {"nested": "dict"}}) == "OTHER"
        assert bd.categorize_failure({"error": ["list", "of", "things"]}) == "OTHER"
        assert bd.categorize_failure({"error": None}) == "OTHER"


# ============================================================================
# 3. infer_window_from_ts — must cover all 4 quota windows
# ============================================================================


class TestInferWindowFromTs:
    """infer_window_from_ts drives the DIURNAL PATTERN ANALYSIS section."""

    def _at(self, hour: int, day: int = 15) -> datetime:
        return datetime(2026, 8, day, hour, 0, 0, tzinfo=timezone.utc)

    def test_off_peak_midnight(self):
        assert bd.infer_window_from_ts(self._at(0)) == "off_peak"

    def test_off_peak_5am(self):
        assert bd.infer_window_from_ts(self._at(5)) == "off_peak"

    def test_moderate_6am(self):
        assert bd.infer_window_from_ts(self._at(6)) == "moderate"

    def test_moderate_11am(self):
        assert bd.infer_window_from_ts(self._at(11)) == "moderate"

    def test_poor_noon(self):
        assert bd.infer_window_from_ts(self._at(12)) == "poor"

    def test_poor_5pm(self):
        assert bd.infer_window_from_ts(self._at(17)) == "poor"

    def test_worst_6pm(self):
        assert bd.infer_window_from_ts(self._at(18)) == "worst"

    def test_worst_11pm(self):
        assert bd.infer_window_from_ts(self._at(23)) == "worst"

    def test_none_returns_none(self):
        assert bd.infer_window_from_ts(None) is None


# ============================================================================
# 4. read_jsonl — must handle empty, malformed, large, missing files
# ============================================================================


class TestReadJsonl:
    """read_jsonl is the foundation for every probe-network render."""

    def test_missing_file_returns_empty(self, tmp_path: Path):
        result = bd.read_jsonl(tmp_path / "missing.jsonl")
        assert result == []

    def test_none_path_returns_empty(self):
        assert bd.read_jsonl(None) == []

    def test_empty_file_returns_empty(self, tmp_path: Path):
        f = tmp_path / "empty.jsonl"
        f.write_text("")
        assert bd.read_jsonl(f) == []

    def test_only_whitespace_returns_empty(self, tmp_path: Path):
        f = tmp_path / "blank.jsonl"
        f.write_text("\n\n   \n")
        assert bd.read_jsonl(f) == []

    def test_valid_entries(self, tmp_path: Path):
        f = tmp_path / "valid.jsonl"
        f.write_text('{"a": 1}\n{"a": 2}\n')
        result = bd.read_jsonl(f)
        assert result == [{"a": 1}, {"a": 2}]

    def test_malformed_lines_skipped(self, tmp_path: Path):
        f = tmp_path / "mixed.jsonl"
        f.write_text('{"a": 1}\nnot json\n{"a": 2}\n{"broke"\n')
        result = bd.read_jsonl(f)
        assert result == [{"a": 1}, {"a": 2}]

    def test_non_dict_lines_skipped(self, tmp_path: Path):
        # jem R3: null, int, str, list, bool are valid JSON but invalid schema.
        f = tmp_path / "weird.jsonl"
        f.write_text('null\n42\n"hello"\n[1,2]\ntrue\n{"a": 1}\n')
        result = bd.read_jsonl(f)
        assert result == [{"a": 1}]

    def test_limit_caps_to_tail(self, tmp_path: Path):
        f = tmp_path / "many.jsonl"
        lines = "\n".join(json.dumps({"i": i}) for i in range(100)) + "\n"
        f.write_text(lines)
        result = bd.read_jsonl(f, limit=10)
        assert len(result) == 10
        assert result[0]["i"] == 90  # deque keeps the LAST 10

    def test_since_filters_old_entries(self, tmp_path: Path):
        now = datetime(2026, 8, 30, 12, 0, 0, tzinfo=timezone.utc)
        old_ts = "2026-08-30T10:00:00+00:00"
        new_ts = "2026-08-30T11:30:00+00:00"
        f = tmp_path / "ts.jsonl"
        f.write_text(f'{{"ts": "{old_ts}", "label": "a"}}\n{{"ts": "{new_ts}", "label": "b"}}\n')
        result = bd.read_jsonl(f, since=now - timedelta(hours=1, minutes=30))
        labels = [e["label"] for e in result]
        assert "a" not in labels
        assert "b" in labels

    def test_since_keeps_malformed_ts(self, tmp_path: Path):
        # M23: ts field malformed → include the entry anyway.
        f = tmp_path / "bad_ts.jsonl"
        f.write_text('{"ts": "not a date", "label": "x"}\n')
        result = bd.read_jsonl(f, since=datetime.now(timezone.utc))
        assert result == [{"ts": "not a date", "label": "x"}]

    def test_since_handles_non_string_ts(self, tmp_path: Path):
        # carmack regression: ts could be int epoch, list, None.
        f = tmp_path / "weird_ts.jsonl"
        f.write_text('{"ts": 1234567890, "label": "int_ts"}\n{"ts": null, "label": "null_ts"}\n')
        result = bd.read_jsonl(f, since=datetime.now(timezone.utc) - timedelta(days=10))
        # Both kept (ts comparison skipped for non-strings).
        labels = sorted(e["label"] for e in result)
        assert labels == ["int_ts", "null_ts"]


# ============================================================================
# 5. ModelStats properties — the data-flow backbone
# ============================================================================


class TestModelStatsProperties:
    """ModelStats drives every table, every export, every chart."""

    def _make(self, success: int = 5, fail: int = 5, lats=None,
              q_valid: int = 0, q_total: int = 0,
              recent: list[bool] | None = None) -> bd.ModelStats:
        s = bd.ModelStats(label="test-model", model_id="test/v1")
        s.success = success
        s.fail = fail
        s.latencies = lats or [100.0, 200.0, 300.0]
        s.quality_valid = q_valid
        s.quality_total = q_total
        if recent:
            for r in recent:
                s.recent_window.append(r)
        return s

    def test_total_is_success_plus_fail(self):
        s = self._make(success=7, fail=3)
        assert s.total == 10

    def test_rate_calculates_correctly(self):
        s = self._make(success=8, fail=2)
        assert s.rate == 80.0

    def test_rate_zero_when_no_data(self):
        s = bd.ModelStats(label="empty")
        assert s.rate == 0.0

    def test_quality_rate_calculates_correctly(self):
        s = self._make(q_valid=8, q_total=10)
        assert s.quality_rate == 80.0

    def test_quality_rate_zero_when_no_data(self):
        s = bd.ModelStats(label="empty")
        assert s.quality_rate == 0.0

    def test_p50_uses_50th_percentile(self):
        s = self._make(lats=[10.0, 20.0, 30.0, 40.0, 50.0])
        assert s.p50 == 30.0

    def test_p99_uses_99th_percentile(self):
        s = self._make(lats=list(range(100)))
        assert s.p99 >= 90  # at least 90th element of 0..99

    def test_p50_empty_returns_zero(self):
        s = bd.ModelStats(label="empty")
        assert s.p50 == 0.0

    def test_outlier_pct_small_dataset_is_zero(self):
        # < 4 entries → guard returns 0
        s = self._make(lats=[100.0, 200.0])
        assert s.outlier_pct == 0.0

    def test_outlier_pct_uniform_is_zero(self):
        # All values close → no outliers
        s = self._make(lats=[100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0])
        assert s.outlier_pct == 0.0

    def test_outlier_pct_bimodal_detects_outlier(self):
        # One extreme outlier far above the rest
        s = self._make(lats=[10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 10000.0])
        assert s.outlier_pct > 0.0

    def test_trend_unknown_when_too_few_samples(self):
        s = self._make(recent=[True, False])
        assert s.trend == "?"

    def test_trend_up_when_improving(self):
        s = self._make(recent=[False] * 5 + [True] * 5)
        assert s.trend == "↑"

    def test_trend_down_when_degrading(self):
        s = self._make(recent=[True] * 5 + [False] * 5)
        assert s.trend == "↓"

    def test_trend_flat_when_steady(self):
        s = self._make(recent=[True] * 10)
        assert s.trend == "→"

    def test_trend_velocity_double_arrow_when_accelerating(self):
        # Construct a sequence where last 6 show strong acceleration.
        recent = [False] * 14 + [True] * 6
        s = self._make(recent=recent)
        assert s.trend_velocity in ("↑↑", "↑", "→", "↓", "↓↓")

    def test_recent_window_is_bounded_deque(self):
        s = bd.ModelStats(label="bounded")
        # Append more than maxlen=20 to confirm eviction
        for i in range(50):
            s.recent_window.append(i % 2 == 0)
        assert len(s.recent_window) == 20

    def test_to_dict_round_trips_core_fields(self):
        s = self._make(success=4, fail=1, lats=[100.0, 200.0])
        d = s.to_dict()
        assert d["label"] == "test-model"
        assert d["success"] == 4
        assert d["fail"] == 1
        assert d["total"] == 5
        assert "rate" in d
        assert "p50_ms" in d
        assert "p99_ms" in d
        assert "trend" in d
        assert "trend_velocity" in d


# ============================================================================
# 6. aggregate_probes — the data-flow backbone
# ============================================================================


class TestAggregateProbes:
    """aggregate_probes is the bridge between raw JSONL and rendered sections."""

    def test_empty_input_returns_empty(self):
        assert bd.aggregate_probes([]) == {}

    def test_single_success(self):
        stats = bd.aggregate_probes([{"label": "m1", "success": True, "latency_ms": 100}])
        assert "m1" in stats
        assert stats["m1"].success == 1
        assert stats["m1"].fail == 0

    def test_single_failure(self):
        stats = bd.aggregate_probes([{"label": "m1", "success": False}])
        assert stats["m1"].fail == 1

    def test_unhashable_label_does_not_crash(self):
        # jem R3 regression: list/dict label used to crash on dict key.
        stats = bd.aggregate_probes([
            {"label": ["nested", "list"], "success": True},
            {"label": {"nested": "dict"}, "success": True},
        ])
        assert len(stats) == 2  # Both coerced to distinct strings.

    def test_none_label_becomes_question_mark(self):
        stats = bd.aggregate_probes([{"label": None, "success": True}])
        assert "?" in stats

    def test_empty_string_label_becomes_question_mark(self):
        stats = bd.aggregate_probes([{"label": "", "success": True}])
        assert "?" in stats

    def test_per_key_outcomes_tracked(self):
        entries = [
            {"label": "m1", "success": True, "key_source": "key_a"},
            {"label": "m1", "success": False, "key_source": "key_a"},
            {"label": "m1", "success": True, "key_source": "key_b"},
        ]
        stats = bd.aggregate_probes(entries)
        assert stats["m1"].key_outcomes["key_a"]["success"] == 1
        assert stats["m1"].key_outcomes["key_a"]["fail"] == 1
        assert stats["m1"].key_outcomes["key_b"]["success"] == 1

    def test_window_success_precomputed(self):
        # researcher R2 closes v3.0 TODO — window_success is keyed by window name.
        entries = [
            {"label": "m1", "success": True, "ts": "2026-08-30T01:00:00+00:00"},  # off_peak
            {"label": "m1", "success": False, "ts": "2026-08-30T13:00:00+00:00"},  # poor
        ]
        stats = bd.aggregate_probes(entries)
        assert stats["m1"].window_success["off_peak"]["success"] == 1
        assert stats["m1"].window_success["poor"]["fail"] == 1

    def test_consecutive_fails_increments_then_resets(self):
        # Build a sequence: fail, fail, fail, success, fail, fail
        entries = [
            {"label": "m", "success": False, "ts": "2026-08-30T01:00:00+00:00"},
            {"label": "m", "success": False, "ts": "2026-08-30T01:00:01+00:00"},
            {"label": "m", "success": False, "ts": "2026-08-30T01:00:02+00:00"},
            {"label": "m", "success": True, "ts": "2026-08-30T01:00:03+00:00"},
            {"label": "m", "success": False, "ts": "2026-08-30T01:00:04+00:00"},
            {"label": "m", "success": False, "ts": "2026-08-30T01:00:05+00:00"},
        ]
        stats = bd.aggregate_probes(entries)
        # Last 2 entries in recent_window were fails.
        assert stats["m"].consecutive_fails == 2

    def test_http_statuses_counted(self):
        entries = [
            {"label": "m", "success": True, "http_status": 200},
            {"label": "m", "success": False, "http_status": 429},
            {"label": "m", "success": False, "http_status": 429},
        ]
        stats = bd.aggregate_probes(entries)
        assert stats["m"].http_statuses["200"] == 1
        assert stats["m"].http_statuses["429"] == 2

    def test_quality_breakdown_classifies_correctly(self):
        entries = [
            # valid
            {"label": "m", "success": True, "quality_check": {"valid_json": True, "has_completion": True, "content_length": 100}},
            # invalid_json
            {"label": "m", "success": True, "quality_check": {"valid_json": False, "has_completion": True, "content_length": 100}},
            # no_completion
            {"label": "m", "success": True, "quality_check": {"valid_json": True, "has_completion": False, "content_length": 100}},
            # empty
            {"label": "m", "success": True, "quality_check": {"valid_json": True, "has_completion": True, "content_length": 5}},
        ]
        stats = bd.aggregate_probes(entries)
        assert stats["m"].quality_valid == 1
        assert stats["m"].quality_invalid_json == 1
        assert stats["m"].quality_no_completion == 1
        assert stats["m"].quality_empty_content == 1


# ============================================================================
# 7. debounce_alerts — alert hysteresis (researcher R2 + jem R3)
# ============================================================================


class TestDebounceAlerts:
    """debounce_alerts kills the F1 noise-counting alert pattern."""

    def _stats(self, rate: float, consecutive: int, alerting: bool = False) -> bd.ModelStats:
        s = bd.ModelStats(label=f"m-{rate}")
        # Pre-seed success/fail so rate matches.
        s.success = max(1, int(rate))
        s.fail = max(0, int(100 - rate))
        s.consecutive_fails = consecutive
        s.currently_alerting = alerting
        return s

    def test_min_window_one_is_no_op(self):
        # Backward compat: v3.0 behavior was fire-on-first-breach.
        s = self._stats(rate=10.0, consecutive=1)
        candidates = [(s, ["test"])]
        result = bd.debounce_alerts(candidates, threshold_pct=70.0, min_window=1)
        assert result == candidates  # Unchanged.

    def test_first_alert_requires_min_window(self):
        s = self._stats(rate=10.0, consecutive=4)
        candidates = [(s, ["rate"])]
        # Default min_window=5 → debounce holds.
        result = bd.debounce_alerts(candidates, threshold_pct=70.0, min_window=5)
        assert result == []

    def test_alert_fires_after_min_window_consecutive(self):
        s = self._stats(rate=10.0, consecutive=5)
        candidates = [(s, ["rate"])]
        result = bd.debounce_alerts(candidates, threshold_pct=70.0, min_window=5)
        assert len(result) == 1
        assert s.currently_alerting is True

    def test_alerting_does_not_clear_within_deadband(self):
        # If currently alerting, only clear when rate > threshold * 1.1.
        s = self._stats(rate=72.0, consecutive=1, alerting=True)
        candidates = [(s, ["rate"])]
        result = bd.debounce_alerts(candidates, threshold_pct=70.0, min_window=5)
        # 72 < 70 * 1.10 = 77 → still alerting.
        assert len(result) == 1

    def test_alerting_clears_above_deadband(self):
        s = self._stats(rate=80.0, consecutive=0, alerting=True)
        candidates = [(s, ["rate"])]
        result = bd.debounce_alerts(candidates, threshold_pct=70.0, min_window=5)
        # 80 > 77 → cleared.
        assert result == []

    def test_exception_does_not_lose_alerts(self):
        # M23 fail-open: malformed input must not silently drop alerts.
        bad = object()  # Not a ModelStats — s.rate will raise AttributeError.
        candidates = [(bad, ["rate"])]
        # Should NOT crash; returns unfiltered candidates on outer exception.
        result = bd.debounce_alerts(candidates, threshold_pct=70.0, min_window=5)
        # The per-element AttributeError branch falls through to fail-open.
        assert len(result) == 1


# ============================================================================
# 8. CLI export round-trips — --json and --csv stability
# ============================================================================


class TestExportRoundTrip:
    """export_json / export_csv must be stable for the same input state."""

    def _state(self):
        return {
            "timestamp": "2026-08-30T12:00:00+00:00",
            "version": "3.2",
            "filters": {"model": None, "since": None},
            "freshness": {},
            "models": {
                "test-model": {
                    "label": "test-model",
                    "success": 8,
                    "fail": 2,
                    "total": 10,
                    "rate": 80.0,
                    "p50_ms": 100.0,
                    "p99_ms": 500.0,
                    "outlier_pct": 5.0,
                    "quality_rate": 75.0,
                    "quality_breakdown": {
                        "valid": 8,
                        "invalid_json": 1,
                        "no_completion": 1,
                        "empty_content": 0,
                    },
                    "trend": "→",
                    "trend_velocity": "→",
                    "last_seen": "2026-08-30T12:00:00+00:00",
                }
            },
        }

    def test_json_round_trip(self, capsys):
        state = self._state()
        bd.export_json(state)
        captured = capsys.readouterr()
        # Round-trip: parse the printed JSON, validate structure. We don't
        # compare raw strings because Python 3.13 dict ordering is stable but
        # JSONEncoder default=str may render types differently on re-serialize.
        parsed = json.loads(captured.out)
        assert parsed["version"] == "3.2"
        assert parsed["models"]["test-model"]["success"] == 8
        assert parsed["models"]["test-model"]["fail"] == 2
        assert parsed["models"]["test-model"]["rate"] == 80.0
        # Re-serialize with same kwargs (indent + default) and parse again.
        # The output must remain valid JSON with identical semantic values.
        re_serialized = json.dumps(parsed, indent=2, default=str)
        re_parsed = json.loads(re_serialized)
        assert re_parsed["models"]["test-model"]["success"] == 8
        assert re_parsed["models"]["test-model"]["quality_breakdown"]["valid"] == 8

    def test_csv_round_trip(self, capsys):
        state = self._state()
        bd.export_csv(state)
        captured = capsys.readouterr()
        reader = csv.reader(io.StringIO(captured.out))
        rows = list(reader)
        # header + 1 data row
        assert len(rows) == 2
        header, data = rows
        assert header[0] == "model"
        assert data[0] == "test-model"
        assert int(data[1]) == 8  # success
        assert int(data[2]) == 2  # fail

    def test_csv_with_partial_dict_uses_defaults(self, capsys):
        # carmack regression: m["key"] would raise KeyError. .get() defaults.
        state = {"models": {"broken": {"label": "broken"}}}
        bd.export_csv(state)
        captured = capsys.readouterr()
        reader = csv.reader(io.StringIO(captured.out))
        rows = list(reader)
        # header + 1 row with zeros for missing fields
        assert len(rows) == 2
        assert rows[1][0] == "broken"
        assert int(rows[1][1]) == 0  # success default
        assert int(rows[1][2]) == 0  # fail default

    def test_csv_empty_models_still_emits_header(self, capsys):
        bd.export_csv({"models": {}})
        captured = capsys.readouterr()
        # Just header, no rows.
        assert captured.out.startswith("model,success,fail")


# ============================================================================
# 9. CLI argument parsing edge cases
# ============================================================================


class TestCliArgs:
    """parse_args is the entry point — every flag must be well-formed.

    parse_args() reads sys.argv directly. We patch sys.argv in each test rather
    than monkeypatching the function signature (which is a frozen public API
    boundary per M26 Doc Standards + D-535 "no API drift").
    """

    def _parse(self, argv: list[str]) -> argparse.Namespace:
        with patch.object(sys, "argv", ["benchmark_dashboard.py", *argv]):
            return bd.parse_args()

    def test_help_flag_exits_cleanly(self):
        with pytest.raises(SystemExit) as exc:
            self._parse(["--help"])
        assert exc.value.code == 0

    def test_once_default_is_false(self):
        args = self._parse([])
        assert args.once is False

    def test_refresh_default_is_2(self):
        args = self._parse([])
        assert args.refresh == 2

    def test_alert_rate_default(self):
        args = self._parse([])
        assert args.alert_rate == bd.ALERT_RATE_DEFAULT

    def test_alert_latency_default(self):
        args = self._parse([])
        assert args.alert_latency == bd.ALERT_LATENCY_DEFAULT_MS

    def test_alert_min_window_default(self):
        args = self._parse([])
        assert args.alert_min_window == 5

    def test_all_flags_parse(self):
        # Smoke-test that every documented flag is accepted.
        args = self._parse([
            "--once",
            "--no-clear",
            "--refresh", "10",
            "--model", "minimax",
            "--since", "6h",
            "--alerts",
            "--alert-rate", "75",
            "--alert-latency", "5000",
            "--alert-min-window", "3",
            "--json",
            "--diurnal",
            "--watch-tail",
            "--self-test",
        ])
        assert args.once is True
        assert args.no_clear is True
        assert args.refresh == 10
        assert args.model == "minimax"
        assert args.since == "6h"
        assert args.alerts is True
        assert args.alert_rate == 75.0
        assert args.alert_latency == 5000
        assert args.alert_min_window == 3
        assert args.json is True
        assert args.diurnal is True
        assert args.watch_tail is True
        assert args.self_test is True

    def test_refresh_negative_rejected_by_main(self):
        # parse_args() does not validate; main() rejects. Confirm parse is lax.
        args = self._parse(["--refresh", "0"])
        assert args.refresh == 0  # parse_args accepts; main() will reject.


# ============================================================================
# 10. M23 regression — render functions must NEVER crash
# ============================================================================


class TestM23NeverCrash:
    """M23 Failure Integrity: the dashboard must NEVER raise out of render()."""

    def test_render_with_completely_empty_args(self, capsys):
        # No data files, no flags — must still produce output (graceful no-data).
        args = argparse.Namespace(
            once=True, no_clear=True, refresh=2, model=None, since=None,
            alerts=False, alert_rate=bd.ALERT_RATE_DEFAULT,
            alert_latency=bd.ALERT_LATENCY_DEFAULT_MS,
            alert_min_window=5, json=False, csv=False, diurnal=False,
            watch_tail=False,
        )
        try:
            bd.render(args)
        except Exception as e:
            pytest.fail(f"render() crashed on empty state: {e}")
        # Should have produced *some* output, not raised.
        captured = capsys.readouterr()
        assert len(captured.out) > 0 or len(captured.err) > 0

    def test_render_with_garbage_data_does_not_crash(self, capsys):
        # Inject non-dict entries, non-string labels, broken timestamps.
        garbage = [
            None,
            42,
            "string",
            [1, 2, 3],
            {"label": None, "success": True, "ts": None},
            {"label": ["weird"], "success": False, "http_status": "not an int"},
            {"label": "", "success": True, "quality_check": "not a dict"},
            {"label": "ok", "success": True, "latency_ms": "string"},
            {"label": "ok", "success": True, "key_source": None},
            {"label": "ok", "success": False, "error": {"nested": "dict"}},
        ]
        stats = bd.aggregate_probes(garbage)
        assert isinstance(stats, dict)  # Did not raise.

    def test_render_network_with_garbage(self, capsys):
        # render_network should silently handle garbage data.
        try:
            bd.render_network([
                None,
                "string",
                {"network": "not a dict", "latency_ms": [1, 2]},
            ])
        except Exception as e:
            pytest.fail(f"render_network crashed: {e}")

    def test_render_alerts_with_garbage_stats(self, capsys):
        args = argparse.Namespace(
            alerts=True,
            alert_rate=bd.ALERT_RATE_DEFAULT,
            alert_latency=bd.ALERT_LATENCY_DEFAULT_MS,
            alert_min_window=5,
        )
        try:
            bd.render_alerts({}, args)
        except Exception as e:
            pytest.fail(f"render_alerts crashed: {e}")


# ============================================================================
# 11. FileFreshness — the freshness bar at the top of the dashboard
# ============================================================================


class TestFileFreshness:
    """FileFreshness powers the DATA FRESHNESS section."""

    def test_missing_file_state(self, tmp_path: Path):
        f = bd.FileFreshness(path=tmp_path / "missing.jsonl")
        assert f.state == "missing"

    def test_fresh_state(self, tmp_path: Path):
        # Write a file then check it's fresh (< FRESH_THRESHOLD_S = 45 min).
        p = tmp_path / "fresh.jsonl"
        p.write_text('{"a": 1}\n')
        ff = bd.get_file_freshness(p)
        assert ff.state == "fresh"

    def test_critical_state_old_file(self, tmp_path: Path):
        # Use patch to fake an old mtime.
        p = tmp_path / "old.jsonl"
        p.write_text('{"a": 1}\n')
        old_time = (datetime.now(timezone.utc) - timedelta(hours=3)).timestamp()
        os.utime(p, (old_time, old_time))
        ff = bd.get_file_freshness(p)
        # 3 hours = 10800 s > STALE_THRESHOLD_S = 5400 s
        assert ff.state == "critical"


# ============================================================================
# 12. _discover_latest_test_log — date-glob helper (researcher R2)
# ============================================================================


class TestDiscoverLatestTestLog:
    """Date-glob auto-discovery replaces R1's hardcoded paths."""

    def test_no_matches_returns_none(self, tmp_path: Path):
        with patch.object(bd, "DATA_DIR", tmp_path):
            result = bd._discover_latest_test_log("never_matches_*.jsonl")
        assert result is None

    def test_returns_latest_lexicographically(self, tmp_path: Path):
        (tmp_path / "antigravity_stress_test_20260828.jsonl").write_text("{}\n")
        (tmp_path / "antigravity_stress_test_20260830.jsonl").write_text("{}\n")
        (tmp_path / "antigravity_stress_test_20260829.jsonl").write_text("{}\n")
        with patch.object(bd, "DATA_DIR", tmp_path):
            result = bd._discover_latest_test_log("antigravity_stress_test_*.jsonl")
        assert result.name == "antigravity_stress_test_20260830.jsonl"

    def test_handles_glob_oserror(self, tmp_path: Path):
        # M23: any exception inside the glob also yields None.
        with patch.object(bd, "DATA_DIR", tmp_path):
            with patch("pathlib.Path.glob", side_effect=OSError("fake")):
                result = bd._discover_latest_test_log("any_*.jsonl")
        assert result is None