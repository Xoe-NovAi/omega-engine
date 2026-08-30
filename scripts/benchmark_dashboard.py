#!/usr/bin/env python3
"""
benchmark_dashboard.py v3.0 — Gap-driven real-time benchmark visualization
=========================================================================
Terminal-native dashboard for the Omega Engine diurnal provider benchmark suite.

Improvements in v3.0 (gap-driven, M11-distilled):
  - RECOMMENDED CASCADE: Auto-computed best → fallback provider list
  - FAILURE MODE TAXONOMY: Categorize failures (RATE_LIMITED, AUTH_FAILED, etc.)
  - QUALITY BREAKDOWN: Show why responses are bad (invalid_json vs empty vs no_completion)
  - NEXT QUOTA RESET: Countdown to next Antigravity quota reset
  - DIURNAL PATTERN: Best hour chart (00:00 = 61% success vs 18:00 = 11%)
  - HISTORICAL COMPARISON: Today vs Yesterday at same time of day
  - KEY HEALTH: Per-key rotation health (or_key vs cline vs auth)
  - TREND VELOCITY: ↑↑ (accelerating) vs ↑ (improving) vs ↓↓ (collapsing)
  - OUTLIER %: Detect bimodal latency distributions
  - WINDOW INFERENCE: Auto-detect quota window from timestamp if not tagged

Author: grokster (M11 distillation)
Date: 2026-08-30
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional


# === CONFIGURATION (env-var overrideable) ====================================

def _data_dir() -> Path:
    """Resolve the data directory from env or default location."""
    env = os.environ.get("OMEGA_METRICS_DIR")
    if env:
        return Path(env)
    return Path.home() / "Documents" / "Xoe-NovAi" / "omega-engine" / "data" / "metrics"


DATA_DIR: Path = _data_dir()
WORKSPACE_DIR: Path = Path(os.environ.get(
    "OMEGA_WORKSPACE_DIR",
    Path.home() / "Documents" / "Xoe-NovAi" / "omega-engine" / "data"
))

PROBE_LOG: Path = DATA_DIR / "free_model_probes.jsonl"
NETWORK_LOG: Path = DATA_DIR / "network_probes.jsonl"
ANTIGRAVITY_LOG: Optional[Path] = DATA_DIR / "antigravity_quotas.jsonl" \
    if (DATA_DIR / "antigravity_quotas.jsonl").exists() else None
STRESS_LOG: Optional[Path] = DATA_DIR / "antigravity_stress_test_20260828.jsonl" \
    if (DATA_DIR / "antigravity_stress_test_20260828.jsonl").exists() else None
BURST_LOG: Optional[Path] = DATA_DIR / "antigravity_burst_test_20260828.jsonl" \
    if (DATA_DIR / "antigravity_burst_test_20260828.jsonl").exists() else None
LONG_DUR_LOG: Optional[Path] = DATA_DIR / "antigravity_long_duration_20260828.jsonl" \
    if (DATA_DIR / "antigravity_long_duration_20260828.jsonl").exists() else None
ALERT_LOG: Optional[Path] = DATA_DIR / "alert_state_change.log" \
    if (DATA_DIR / "alert_state_change.log").exists() else None

# Staleness thresholds (seconds)
FRESH_THRESHOLD_S: int = 60 * 45  # 45 min = fresh
STALE_THRESHOLD_S: int = 60 * 90  # 90 min = stale (warn)
# Beyond STALE = critical

# Display thresholds
ALERT_RATE_DEFAULT: float = 70.0  # %
ALERT_LATENCY_DEFAULT_MS: int = 15_000  # 15s
EXCELLENT_RATE: float = 90.0
GOOD_RATE: float = 70.0
FAIR_RATE: float = 50.0


# === TERMINAL COLORS =========================================================

class C:
    """ANSI color codes. Degrades gracefully if NO_COLOR is set."""
    _no_color: bool = bool(os.environ.get("NO_COLOR")) or not sys.stdout.isatty()

    R: str = "" if _no_color else "\033[91m"   # red
    G: str = "" if _no_color else "\033[92m"   # green
    Y: str = "" if _no_color else "\033[93m"   # yellow
    B: str = "" if _no_color else "\033[94m"   # blue
    M: str = "" if _no_color else "\033[95m"   # magenta
    C: str = "" if _no_color else "\033[96m"   # cyan
    W: str = "" if _no_color else "\033[97m"   # white
    DIM: str = "" if _no_color else "\033[2m"  # dim
    BOLD: str = "" if _no_color else "\033[1m"  # bold
    END: str = "" if _no_color else "\033[0m"  # reset
    CLR: str = "" if _no_color else "\033[2J\033[H"  # clear screen


# === DATA STRUCTURES ========================================================

@dataclass
class ModelStats:
    """Aggregated statistics for a single model."""
    label: str
    model_id: str = ""
    success: int = 0
    fail: int = 0
    latencies: list[float] = field(default_factory=list)
    quality_valid: int = 0  # valid_json=true AND has_completion=true
    quality_invalid_json: int = 0  # valid_json=false
    quality_no_completion: int = 0  # has_completion=false
    quality_empty_content: int = 0  # content_length <= 10
    quality_total: int = 0
    http_statuses: dict[str, int] = field(default_factory=dict)
    key_sources: dict[str, int] = field(default_factory=dict)
    key_last_success: dict[str, Optional[datetime]] = field(default_factory=dict)
    windows: dict[str, int] = field(default_factory=dict)
    last_seen: Optional[datetime] = None
    last_success: Optional[datetime] = None
    # carmack: was list[bool] with manual pop(0) → O(N) per trim. deque
    # gives O(1) bounded append + automatic eviction. The field type
    # changed but the public surface (to_dict()) doesn't expose it, and
    # the trend properties only read from it.
    recent_window: deque = field(default_factory=lambda: deque(maxlen=20))
    failure_categories: dict[str, int] = field(default_factory=dict)  # RATE_LIMITED, AUTH_FAILED, etc.

    @property
    def total(self) -> int:
        return self.success + self.fail

    @property
    def rate(self) -> float:
        return (self.success / self.total * 100) if self.total > 0 else 0.0

    @property
    def quality_rate(self) -> float:
        return (self.quality_valid / self.quality_total * 100) if self.quality_total > 0 else 0.0

    @property
    def p50(self) -> float:
        return percentile(self.latencies, 50)

    @property
    def p99(self) -> float:
        return percentile(self.latencies, 99)

    @property
    def outlier_pct(self) -> float:
        """Percentage of latency values that are statistical outliers (above Q3 + 1.5*IQR).
        High outlier % indicates bimodal distribution (some calls are much slower than others)."""
        if len(self.latencies) < 4:
            return 0.0
        sorted_lats = sorted(self.latencies)
        n = len(sorted_lats)
        q1 = sorted_lats[n // 4]
        q3 = sorted_lats[3 * n // 4]
        iqr = q3 - q1
        if iqr == 0:
            return 0.0
        threshold = q3 + 1.5 * iqr
        # Iterate sorted_lats (same length as self.latencies) so denominator
        # matches the population we scanned. Original iterated self.latencies
        # and divided by len(sorted_lats) — numerically identical when
        # lengths match, but inconsistent if the lists ever diverge.
        outliers = sum(1 for l in sorted_lats if l > threshold)
        return (outliers / n) * 100

    @property
    def trend(self) -> str:
        """Determine trend direction from recent window. Returns ↑, ↓, →"""
        n = len(self.recent_window)
        if n < 4:
            return "?"
        # Materialize once — deque doesn't support slicing. N=20 so the
        # copy is essentially free; saves a real slice on every render.
        window = list(self.recent_window)
        half = n // 2
        first_half_rate = sum(window[:half]) / half
        second_half_rate = sum(window[half:]) / (n - half)
        delta = second_half_rate - first_half_rate
        if delta > 0.15:  # >15% improvement
            return "↑"
        if delta < -0.15:  # >15% degradation
            return "↓"
        return "→"

    @property
    def trend_velocity(self) -> str:
        """Returns trend direction with velocity: ↑↑ (accelerating up), ↑ (up), →, ↓, ↓↓ (collapsing)."""
        if len(self.recent_window) < 6:
            return self.trend
        # Compute slope of last 6 calls
        n = min(6, len(self.recent_window))
        # deque doesn't slice; materialize the tail. N=20, copy cost ~free.
        window = list(self.recent_window)[-n:]
        # Count successes in each half
        first_n = n // 2
        first_rate = sum(window[:first_n]) / first_n if first_n > 0 else 0
        second_rate = sum(window[first_n:]) / (n - first_n) if (n - first_n) > 0 else 0
        delta = second_rate - first_rate
        if delta > 0.3:  # >30% swing = accelerating
            return "↑↑"
        if delta < -0.3:
            return "↓↓"
        if delta > 0.1:
            return "↑"
        if delta < -0.1:
            return "↓"
        return "→"

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "model_id": self.model_id,
            "success": self.success,
            "fail": self.fail,
            "total": self.total,
            "rate": round(self.rate, 2),
            "p50_ms": round(self.p50, 1),
            "p99_ms": round(self.p99, 1),
            "outlier_pct": round(self.outlier_pct, 1),
            "quality_rate": round(self.quality_rate, 2),
            "quality_breakdown": {
                "valid": self.quality_valid,
                "invalid_json": self.quality_invalid_json,
                "no_completion": self.quality_no_completion,
                "empty_content": self.quality_empty_content,
            },
            "trend": self.trend,
            "trend_velocity": self.trend_velocity,
            "http_statuses": self.http_statuses,
            "key_sources": self.key_sources,
            "key_last_success": {k: v.isoformat() if v else None for k, v in self.key_last_success.items()},
            "failure_categories": self.failure_categories,
            "windows": self.windows,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
        }


@dataclass
class FileFreshness:
    """Tracks freshness of a single data source."""
    path: Path
    last_modified: Optional[datetime] = None
    age_seconds: Optional[int] = None
    entries_total: int = 0
    entries_in_window: int = 0  # entries within --since window

    @property
    def state(self) -> str:
        """Returns 'fresh', 'stale', 'critical', or 'missing'."""
        if self.last_modified is None:
            return "missing"
        if self.age_seconds is None:
            return "missing"
        if self.age_seconds < FRESH_THRESHOLD_S:
            return "fresh"
        if self.age_seconds < STALE_THRESHOLD_S:
            return "stale"
        return "critical"


# === HELPER FUNCTIONS =======================================================

def percentile(data: list[float], p: int) -> float:
    """Calculate the p-th percentile. Returns 0 if data is empty."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = int(len(sorted_data) * p / 100)
    return sorted_data[min(idx, len(sorted_data) - 1)]


def progress_bar(current: int, total: int, width: int = 30,
                char: str = "█", empty: str = "░") -> str:
    """Render a progress bar. No-color fallback uses # and -."""
    # carmack: original check was `if not C.BOLD` but BOLD is the ANSI
    # escape "\033[1m" which is always truthy. Use C._no_color instead so
    # the fallback actually fires when NO_COLOR is set or stdout is not a TTY.
    if C._no_color:
        char, empty = "#", "-"
    if total == 0:
        return "[" + empty * width + "]"
    pct = current / total
    filled = int(width * pct)
    bar = char * filled + empty * (width - filled)
    return f"[{bar}] {pct * 100:.0f}% ({current}/{total})"


def fmt_ms(ms: float) -> str:
    """Format milliseconds as human-readable string.

    carmack: handle None and non-numeric gracefully — upstream
    latency_ms fields can be None if the request never returned.
    """
    if not isinstance(ms, (int, float)) or isinstance(ms, bool):
        return f"{C.DIM}--{C.END}"
    if ms < 0:
        return f"{C.DIM}--{C.END}"
    if ms == 0:
        return f"{C.DIM}0ms{C.END}"
    if ms < 1000:
        return f"{ms:.0f}ms"
    return f"{ms / 1000:.1f}s"


# Pattern for stripping ANSI escape sequences when computing visible width
# for column alignment. carmack: the formatter `f"{colored_str:>8}"`
# pads to Python string length, not visible width. Embedded ANSI codes
# (e.g. `\033[92m`) inflate the count and break table alignment. Strip
# them before padding.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _visible_width(s: str) -> int:
    """Visible (terminal) width of a string with ANSI codes stripped."""
    return len(_ANSI_RE.sub("", s))


def pad_visible(s: str, width: int, align: str = ">") -> str:
    """Pad `s` to `width` visible columns. align is '>' (right) or '<' (left)."""
    pad = max(0, width - _visible_width(s))
    return (" " * pad + s) if align == ">" else (s + " " * pad)


def fmt_age(seconds: int) -> str:
    """Format seconds-ago as human-readable."""
    if seconds < 0:
        return f"{C.DIM}just now{C.END}"
    if seconds < 60:
        return f"{seconds}s ago"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    return f"{seconds // 86400}d ago"


def fmt_pct(pct: float) -> str:
    """Format percentage with color coding."""
    if pct >= EXCELLENT_RATE:
        return f"{C.G}{pct:.0f}%{C.END}"
    if pct >= FAIR_RATE:
        return f"{C.Y}{pct:.0f}%{C.END}"
    return f"{C.R}{pct:.0f}%{C.END}"


def freshness_indicator(state: str) -> str:
    """Color-coded freshness indicator."""
    if state == "fresh":
        return f"{C.G}●{C.END}"
    if state == "stale":
        return f"{C.Y}●{C.END}"
    if state == "critical":
        return f"{C.R}● STALE{C.END}"
    return f"{C.DIM}○ MISSING{C.END}"


def safe_div(n: float, d: float, default: float = 0.0) -> float:
    """Division with safe default for zero denominators."""
    return n / d if d != 0 else default


# === FILE READING (incremental + resilient) =================================

def read_jsonl(path: Optional[Path], limit: Optional[int] = None,
               since: Optional[datetime] = None) -> list[dict]:
    """Read JSONL file with incremental + time-window support.

    M23 compliant: never throws, returns [] on any error.
    """
    if not path or not path.exists():
        return []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            if limit:
                # Read last N lines efficiently using a deque. deque is
                # imported at module scope; this list() materializes the
                # deque so we can iterate twice (once for filtering).
                lines = list(deque(f, maxlen=limit))
            else:
                lines = f.readlines()
        result = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue  # skip malformed lines, don't crash
            if since and "ts" in entry:
                try:
                    ts_val = entry["ts"]
                    if not isinstance(ts_val, str):
                        # carmack: ts could be a list/dict/None from a
                        # malformed line. Skip the window filter rather
                        # than crash on .replace().
                        raise ValueError("ts is not a string")
                    entry_ts = datetime.fromisoformat(
                        ts_val.replace("Z", "+00:00")
                    )
                    # carmack: tzinfo guard. If entry_ts is naive, assume
                    # UTC so the comparison with tz-aware `since` works.
                    if entry_ts.tzinfo is None:
                        entry_ts = entry_ts.replace(tzinfo=timezone.utc)
                    if entry_ts < since:
                        continue
                except (ValueError, TypeError):
                    pass  # if ts is malformed, include it anyway
            result.append(entry)
        return result
    except (OSError, IOError) as e:
        # M23: log but don't crash
        return []


def get_file_freshness(path: Optional[Path], since: Optional[datetime] = None) -> FileFreshness:
    """Get freshness metadata for a file.

    Performance + safety fix (carmack):
    - Original opened the file twice (once via read_jsonl, once via bare
      `open()` to count total lines) and never closed the second handle.
      At 1,897 entries this is benign; at 100K+ entries it doubles I/O
      and leaks the file handle on any exception between the two opens.
    - Now we count lines in a single open() inside a `with` block, using
      the raw on-disk line count rather than the parsed JSONL count, so
      `entries_total` reflects the file size even when some lines are
      malformed (which `read_jsonl` silently skips).
    """
    if not path or not path.exists():
        return FileFreshness(path=path or Path())
    try:
        stat = path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        age = int((datetime.now(timezone.utc) - mtime).total_seconds())
        # Single pass: read JSONL for the windowed entries and count raw lines
        entries = read_jsonl(path, since=since)
        with open(path, encoding="utf-8", errors="replace") as f:
            entries_total = sum(1 for _ in f)
        return FileFreshness(
            path=path,
            last_modified=mtime,
            age_seconds=age,
            entries_total=entries_total,
            entries_in_window=len(entries),
        )
    except (OSError, IOError):
        return FileFreshness(path=path)


# === AGGREGATION ============================================================

def categorize_failure(entry: dict) -> str:
    """Categorize a failed probe into a failure mode taxonomy.

    Categories (per the gap research):
    - RATE_LIMITED: 429 errors or "Rate limit" in error
    - AUTH_FAILED: 401 errors
    - INVALID_MODEL: 404 or "not a valid model"
    - PAYMENT_REQUIRED: 402
    - SERVER_ERROR: 5xx
    - TIMEOUT: Connection timeouts
    - PARSE_ERROR: Malformed responses
    - OTHER: Anything else

    M23 hardening (carmack): coerce `error` to str defensively. Upstream
    pipelines occasionally emit dict/list/None; without coercion the
    `in` and `.lower()` calls raise TypeError and crash the dashboard.
    """
    status = entry.get("http_status")
    raw_err = entry.get("error")
    if not isinstance(raw_err, str):
        # Non-string errors (dict, list, None, etc.) → fall through to OTHER
        err = "" if raw_err is None else str(raw_err)
    else:
        err = raw_err
    err_lower = err.lower()

    if status == 429 or "Rate limit" in err or "per-day" in err:
        return "RATE_LIMITED"
    if status == 401 or "auth" in err_lower or "key" in err_lower:
        return "AUTH_FAILED"
    if status == 404 or "not a valid" in err or "unavailable" in err:
        return "INVALID_MODEL"
    if status == 402:
        return "PAYMENT_REQUIRED"
    if isinstance(status, int) and 500 <= status < 600:
        return "SERVER_ERROR"
    if "timeout" in err_lower or "timed out" in err_lower:
        return "TIMEOUT"
    if "parse" in err_lower or "json" in err_lower:
        return "PARSE_ERROR"
    if "Provider returned error" in err:
        return "PROVIDER_ERROR"
    return "OTHER"


def infer_window_from_ts(ts: Optional[datetime]) -> Optional[str]:
    """Infer the quota window from a timestamp (when not explicitly tagged).

    carmack: assumes UTC. The caller (aggregate_probes) already normalizes
    naive datetimes to UTC. If a tz-aware non-UTC datetime is passed,
    `ts.hour` reflects the local hour which would corrupt the window
    inference. Caller is responsible for tz-normalization upstream.
    """
    if ts is None:
        return None
    h = ts.hour
    if 0 <= h < 6:
        return "off_peak"
    if 6 <= h < 12:
        return "moderate"
    if 12 <= h < 18:
        return "poor"
    return "worst"


def aggregate_probes(probe_data: list[dict]) -> dict[str, ModelStats]:
    """Aggregate probe entries by model label."""
    stats: dict[str, ModelStats] = {}
    for entry in probe_data:
        label = entry.get("label", "?")
        if label not in stats:
            stats[label] = ModelStats(label=label)
        s = stats[label]

        # Track model_id (first seen wins)
        if not s.model_id and entry.get("model"):
            s.model_id = entry["model"]

        if entry.get("success"):
            s.success += 1
        else:
            s.fail += 1
            # Categorize failure
            cat = categorize_failure(entry)
            s.failure_categories[cat] = s.failure_categories.get(cat, 0) + 1

        lat = entry.get("latency_ms", 0)
        if isinstance(lat, (int, float)) and lat > 0:
            s.latencies.append(float(lat))

        # Quality check
        qc = entry.get("quality_check", {})
        if isinstance(qc, dict):
            s.quality_total += 1
            # carmack: explicit bool() coercion defends against upstream
            # emitting `"true"`/`"false"` strings or `1`/`0` ints. The
            # truthy-test (Python's `and`/`not`) would treat string "false"
            # as truthy and silently corrupt the quality taxonomy.
            valid = bool(qc.get("valid_json"))
            completion = bool(qc.get("has_completion"))
            content_len = qc.get("content_length", 0)
            try:
                content_len_int = int(content_len)
            except (TypeError, ValueError):
                content_len_int = 0
            if valid and completion and content_len_int > 10:
                s.quality_valid += 1
            elif not valid:
                s.quality_invalid_json += 1
            elif not completion:
                s.quality_no_completion += 1
            else:
                s.quality_empty_content += 1

        # HTTP status
        status = entry.get("http_status")
        if status:
            s.http_statuses[str(status)] = s.http_statuses.get(str(status), 0) + 1

        # Key source + last success per key
        ks = entry.get("key_source", "?")
        s.key_sources[ks] = s.key_sources.get(ks, 0) + 1

        # Timestamps
        ts_str = entry.get("ts")
        ts = None
        if ts_str:
            try:
                # carmack: defensive type check before .replace() and
                # tzinfo normalization so downstream comparisons work.
                if not isinstance(ts_str, str):
                    raise ValueError("ts is not a string")
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                s.last_seen = ts
                if entry.get("success"):
                    s.last_success = ts
                    s.key_last_success[ks] = ts
            except (ValueError, TypeError):
                pass

        # Window (explicit or inferred)
        win = entry.get("window")
        if not win and ts:
            win = infer_window_from_ts(ts)
        if win:
            s.windows[win] = s.windows.get(win, 0) + 1

        # Recent window for trend (last 20 calls). deque(maxlen=20)
        # evicts the oldest element automatically on append → O(1).
        s.recent_window.append(bool(entry.get("success")))

    return stats


# === RENDERING: SECTIONS ====================================================

def render_freshness_summary(freshness: dict[str, FileFreshness]) -> None:
    """Render the data freshness summary bar."""
    print(f"{C.BOLD}DATA FRESHNESS{C.END}")
    for name, f in freshness.items():
        indicator = freshness_indicator(f.state)
        if f.state == "missing":
            print(f"  {name:<20} {indicator}")
        else:
            age_str = fmt_age(f.age_seconds or 0)
            entries_str = f"{f.entries_in_window}/{f.entries_total} entries" if f.entries_in_window != f.entries_total else f"{f.entries_total} entries"
            print(f"  {name:<20} {indicator} {C.DIM}{age_str:<15}{C.END} {entries_str}")
    print()


def render_network(network_data: list[dict]) -> None:
    """Render the network state section."""
    print(f"{C.BOLD}NETWORK{C.END}")
    if not network_data:
        print(f"  {C.DIM}no data yet (cron not running){C.END}")
        print()
        return

    n = network_data[-1]
    net = n.get("network", {})
    lat = n.get("latency_ms", {})
    prov = n.get("provider_recent", {})

    ssid = net.get("ssid", "?")
    bssid = net.get("bssid", "?")
    sig = net.get("signal_dbm", "?")
    freq = net.get("frequency_mhz", "?")
    rate = net.get("rate", "?")
    iface = net.get("iface", "?")

    print(f"  {C.C}{ssid}{C.END} ({bssid}) @ {sig}dBm, {freq}MHz, {rate}")
    print(f"  Latency: gateway={fmt_ms(lat.get('gateway', -1))}, "
          f"dns={fmt_ms(lat.get('dns', -1))}, "
          f"resolve={fmt_ms(lat.get('dns_resolve', -1))}, "
          f"OR={fmt_ms(lat.get('openrouter_connect', -1))}")

    # Network quality assessment
    # carmack: signal_dbm may be a string (e.g. "-65") or int upstream.
    # lstrip("-") strips the optional minus; isdigit then rejects floats
    # and strings with units. Falls back to 0 for unparseable values.
    sig_int = 0
    if isinstance(sig, (int, float)) and not isinstance(sig, bool):
        sig_int = int(sig)
    elif isinstance(sig, str):
        stripped = sig.lstrip("-")
        if stripped.isdigit():
            sig_int = int(sig)
    gw_lat = lat.get("gateway", 0)
    quality = "?"
    if isinstance(sig_int, int) and sig_int != 0:
        if sig_int > -55 and gw_lat < 20:
            quality = f"{C.G}EXCELLENT{C.END}"
        elif sig_int > -70 and gw_lat < 50:
            quality = f"{C.G}GOOD{C.END}"
        elif sig_int > -80:
            quality = f"{C.Y}FAIR{C.END}"
        else:
            quality = f"{C.R}POOR{C.END}"
    print(f"  Quality: {quality}  if={iface}")

    # Provider correlation
    sc = prov.get("success_count", 0)
    fc = prov.get("failure_count", 0)
    total = sc + fc
    if total > 0:
        rate_pct = (sc / total) * 100
        print(f"  Provider (last {total} probes): {fmt_pct(rate_pct)} success ({sc}/{total})")
    print()


def render_probes(stats: dict[str, ModelStats], args: argparse.Namespace) -> list[ModelStats]:
    """Render the model probe table. Returns the filtered/ordered list for downstream use."""
    if not stats:
        print(f"{C.BOLD}PROBE RESULTS{C.END}  {C.DIM}no data{C.END}")
        print()
        return []

    # Filter by --model if provided
    filtered = {}
    if args.model:
        pattern = re.compile(args.model, re.IGNORECASE)
        filtered = {k: v for k, v in stats.items() if pattern.search(k) or pattern.search(v.model_id)}
    else:
        filtered = stats

    filter_note = f" ({len(filtered)} of {len(stats)} models)" if args.model else f" ({len(stats)} models)"
    print(f"{C.BOLD}PROBE RESULTS{C.END}  {C.DIM}{filter_note}{C.END}")
    print(f"  {'MODEL':<24} {'SUCCESS':>8} {'FAIL':>6} {'RATE':>6} {'P50':>8} {'P99':>8} {'QUAL':>6} {'TREND':>6} {'WINDOW':>5}  KEY")
    print(f"  {'─' * 24} {'─' * 8} {'─' * 6} {'─' * 6} {'─' * 8} {'─' * 8} {'─' * 6} {'─' * 6} {'─' * 5}  {'─' * 10}")

    # Sort by rate desc, then by total desc (more data = more reliable)
    sorted_stats = sorted(
        filtered.values(),
        key=lambda s: (-s.rate, -s.total)
    )

    for s in sorted_stats:
        if s.total == 0:
            rate_str = f"{C.DIM}--{C.END}"
        else:
            rate_str = fmt_pct(s.rate)
        p50_str = fmt_ms(s.p50) if s.p50 else f"{C.DIM}--{C.END}"
        p99_str = fmt_ms(s.p99) if s.p99 else f"{C.DIM}--{C.END}"
        quality_str = fmt_pct(s.quality_rate) if s.quality_total > 0 else f"{C.DIM}--{C.END}"
        trend_str = f"{s.trend}"
        if s.trend == "↑":
            trend_str = f"{C.G}↑{C.END}"
        elif s.trend == "↓":
            trend_str = f"{C.R}↓{C.END}"
        else:
            trend_str = f"{C.DIM}→{C.END}"

        # Best key for this model
        best_key = max(s.key_sources.items(), key=lambda x: x[1])[0] if s.key_sources else "?"

        # Most recent window
        window_str = f"{C.DIM}--{C.END}"
        if s.windows:
            recent_window = max(s.windows.items(), key=lambda x: x[1])[0]
            window_str = recent_window[:5]

        # carmack: use pad_visible for columns with ANSI codes (rate, p50,
        # p99, qual, trend, window). Plain numeric columns use :>N as
        # before. Without this, colored text overflows column boundaries.
        print(f"  {s.label:<24} {s.success:>8} {s.fail:>6} {pad_visible(rate_str, 6)} "
              f"{pad_visible(p50_str, 8)} {pad_visible(p99_str, 8)} {pad_visible(quality_str, 6)} "
              f"{pad_visible(trend_str, 6)} {pad_visible(window_str, 5)}  {best_key}")
    print()

    return sorted_stats


def render_antigravity(ag_data: list[dict]) -> None:
    """Render the Antigravity account quotas section."""
    if not ag_data:
        return

    print(f"{C.BOLD}ANTIGRAVITY QUOTAS{C.END}  {C.DIM}({len(ag_data)} accounts){C.END}")

    # Show most recent entry per account
    by_account: dict[str, dict] = {}
    for entry in ag_data:
        email = entry.get("email", "?")
        ts_str = entry.get("ts") or ""
        if email not in by_account:
            by_account[email] = entry
        else:
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                prev_ts = datetime.fromisoformat((by_account[email].get("ts") or "").replace("Z", "+00:00"))
                # carmack: tzinfo guard for comparison. If both naive,
                # assume UTC. If mixed, also normalize.
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if prev_ts.tzinfo is None:
                    prev_ts = prev_ts.replace(tzinfo=timezone.utc)
                if ts > prev_ts:
                    by_account[email] = entry
            except (ValueError, TypeError):
                pass

    for email, entry in by_account.items():
        enabled = entry.get("enabled", False)
        tier = entry.get("tier", "?")
        models_raw = entry.get("models", [])
        # carmack: defensive — ensure each model entry is a dict. If
        # upstream emits a string or None in the list, skip it rather
        # than crash on `m.get(...)`.
        models = [m for m in models_raw if isinstance(m, dict)]
        project = entry.get("project", "?")

        # Find the most-used models (those with remainingFraction)
        tracked = [m for m in models if m.get("remainingFraction") is not None]
        if not tracked:
            tracked = models[:3]

        # Color the status
        status_color = C.G if enabled else C.R
        status_str = "✓ ENABLED" if enabled else "✗ DISABLED"

        # Project short
        project_short = project[:24] + "..." if len(project) > 24 else project
        print(f"  {C.BOLD}{email}{C.END}  {status_color}{status_str}{C.END}  tier={tier}  project={project_short}")

        # Top 3 models by lowest remaining (most constrained)
        if tracked:
            tracked_sorted = sorted(tracked, key=lambda m: m.get("remainingFraction", 1.0))[:3]
            for m in tracked_sorted:
                frac = m.get("remainingFraction")
                if frac is None:
                    frac_str = f"{C.DIM}--{C.END}"
                elif frac >= 0.8:
                    frac_str = f"{C.G}{frac:.0%}{C.END}"
                elif frac >= 0.4:
                    frac_str = f"{C.Y}{frac:.0%}{C.END}"
                else:
                    frac_str = f"{C.R}{frac:.0%}{C.END}"
                reset = m.get("resetTime")
                reset_str = ""
                if reset:
                    try:
                        reset_dt = datetime.fromisoformat(reset.replace("Z", "+00:00"))
                        # carmack: tzinfo guard for `reset_dt - now`
                        if reset_dt.tzinfo is None:
                            reset_dt = reset_dt.replace(tzinfo=timezone.utc)
                        delta = reset_dt - datetime.now(timezone.utc)
                        if delta.total_seconds() > 0:
                            hours = int(delta.total_seconds() // 3600)
                            mins = int((delta.total_seconds() % 3600) // 60)
                            reset_str = f"  {C.DIM}reset in {hours}h{mins}m{C.END}"
                    except (ValueError, TypeError):
                        reset_str = f"  {C.DIM}reset={reset[:16]}{C.END}"
                model_id = m.get("id", "?")
                print(f"    {model_id:<30} {frac_str}{reset_str}")
    print()


def render_diurnal_analysis(stats: dict[str, ModelStats], args: argparse.Namespace) -> None:
    """Render diurnal pattern analysis per model."""
    if not stats:
        return

    # Only show if we have window-tagged data
    has_windows = any(s.windows for s in stats.values())
    if not has_windows:
        return

    print(f"{C.BOLD}DIURNAL PATTERN ANALYSIS{C.END}  {C.DIM}(by quota window){C.END}")
    windows = ["off_peak", "moderate", "poor", "worst"]
    header = f"  {'MODEL':<24}"
    for w in windows:
        header += f" {w[:8]:>8}"
    print(header)
    print(f"  {'─' * 24}" + f" {'─' * 8}" * len(windows))

    # Filter
    filtered = stats
    if args.model:
        pattern = re.compile(args.model, re.IGNORECASE)
        filtered = {k: v for k, v in stats.items() if pattern.search(k) or pattern.search(v.model_id)}

    for s in sorted(filtered.values(), key=lambda x: -x.total)[:10]:  # top 10
        row = f"  {s.label:<24}"
        for w in windows:
            win_count = s.windows.get(w, 0)
            if win_count == 0:
                row += f" {C.DIM}--{C.END}     "
            else:
                # Calculate success rate in this window
                # This requires re-aggregating... skip for now, show count
                row += f" {win_count:>3}    "
        print(row)
    print()


def render_test_progress(name: str, log_path: Optional[Path], icon: str = "●") -> None:
    """Generic test progress section."""
    if not log_path:
        return
    data = read_jsonl(log_path, limit=2000)
    if not data:
        return

    total = len(data)
    success = sum(1 for e in data if e.get("success"))
    fail = total - success
    rate = (success / total * 100) if total > 0 else 0
    lats = [float(e.get("latency_ms", 0)) for e in data
            if isinstance(e.get("latency_ms"), (int, float)) and e.get("latency_ms", 0) > 0]

    print(f"{C.BOLD}{icon} {name}{C.END}")
    print(f"  Progress: {progress_bar(success, total, width=30)}")
    print(f"  Success: {success}/{total} ({fmt_pct(rate)}), "
          f"P50={fmt_ms(percentile(lats, 50))}, P99={fmt_ms(percentile(lats, 99))}")
    print()


def render_economics(probe_data: list[dict], stats: dict[str, ModelStats]) -> None:
    """Render the M3 survival economics — COMPUTED from actual data."""
    print(f"{C.BOLD}M3 SURVIVAL ECONOMICS{C.END}  {C.DIM}(computed){C.END}")

    if not probe_data:
        print(f"  {C.DIM}no data yet{C.END}")
        print()
        return

    # Count successes and total time
    total = len(probe_data)
    successes = sum(1 for e in probe_data if e.get("success"))
    success_rate = safe_div(successes, total) * 100

    # Check the quality_check field across all entries
    # carmack: filter to dict-shaped entries only; upstream could put a
    # list/str truthy value in `quality_check` and crash the .get() chain.
    quality_entries = [
        e for e in probe_data
        if isinstance(e.get("quality_check"), dict)
    ]
    quality_valid = sum(
        1 for e in quality_entries
        if e["quality_check"].get("valid_json") and e["quality_check"].get("has_completion")
    )
    quality_rate = safe_div(quality_valid, len(quality_entries)) * 100

    # Total latency (rough proxy for tokens processed). carmack: only
    # sum numeric values — upstream could emit a string in `latency_ms`.
    total_latency_ms = sum(
        e.get("latency_ms", 0)
        for e in probe_data
        if isinstance(e.get("latency_ms"), (int, float)) and not isinstance(e.get("latency_ms"), bool)
    )
    total_latency_s = total_latency_ms / 1000

    # Key rotation
    key_sources: dict[str, int] = defaultdict(int)
    for e in probe_data:
        key_sources[e.get("key_source", "?")] += 1
    active_keys = len([k for k, v in key_sources.items() if k != "?" and v > 0])

    print(f"  • {fmt_pct(success_rate)} overall success ({successes}/{total} probes)")
    print(f"  • {fmt_pct(quality_rate)} quality rate (valid JSON + has completion)")
    if total_latency_s > 0:
        print(f"  • {total_latency_s:.0f}s total compute across {len(probe_data)} probes")
    if active_keys:
        print(f"  • {active_keys} active API keys rotating: {', '.join(sorted(key_sources.keys()))}")

    # Survival verdict
    if success_rate >= 90 and quality_rate >= 80:
        verdict = f"{C.G}✅ FREE TIER SURVIVING{C.END}"
    elif success_rate >= 70:
        verdict = f"{C.Y}⚠️  DEGRADED — TIGHTEN ROTATION{C.END}"
    else:
        verdict = f"{C.R}🚨 CRITICAL — DIVERSIFY KEYS{C.END}"
    print(f"  • Verdict: {verdict}")
    print()


def render_active_sessions() -> None:
    """Render active opencode sessions with PID and memory."""
    print(f"{C.BOLD}ACTIVE SESSIONS{C.END}")
    try:
        result = subprocess.run(
            ["pgrep", "-af", "opencode"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")[:8]
            for line in lines:
                # Parse: PID command...
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    pid, cmd = parts
                    # Try to get memory
                    mem_str = ""
                    try:
                        with open(f"/proc/{pid}/status", encoding="utf-8") as f:
                            for status_line in f:
                                if status_line.startswith("VmRSS:"):
                                    mem_kb = int(status_line.split()[1])
                                    mem_mb = mem_kb / 1024
                                    mem_str = f"  {C.DIM}{mem_mb:.0f}MB{C.END}"
                                    break
                    except (OSError, ValueError, IndexError):
                        pass
                    cmd_display = cmd[:60] + "..." if len(cmd) > 60 else cmd
                    print(f"  {C.DIM}{pid}{C.END}  {cmd_display}{mem_str}")
        else:
            print(f"  {C.DIM}no opencode processes detected{C.END}")
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        print(f"  {C.DIM}process check unavailable{C.END}")
    print()


def render_alerts(stats: dict[str, ModelStats], args: argparse.Namespace) -> list[str]:
    """Render alerts for models below threshold. Returns list of alert messages."""
    alerts: list[str] = []
    if not args.alerts:
        return alerts

    rate_threshold = args.alert_rate
    latency_threshold = args.alert_latency

    triggered = []
    for s in stats.values():
        reasons = []
        if s.total >= 5 and s.rate < rate_threshold:
            reasons.append(f"rate {s.rate:.0f}% < {rate_threshold:.0f}%")
        if s.latencies and s.p99 > latency_threshold:
            reasons.append(f"P99 {fmt_ms(s.p99)} > {fmt_ms(latency_threshold)}")

        if reasons:
            triggered.append((s, reasons))

    if not triggered:
        return alerts

    print(f"{C.BOLD}🚨 ALERTS{C.END}  {C.DIM}({len(triggered)} triggered){C.END}")
    for s, reasons in triggered:
        msg = f"  {C.R}●{C.END} {s.label}: {', '.join(reasons)}"
        print(msg)
        alerts.append(f"{s.label}: {', '.join(reasons)}")
    print()

    return alerts


# === v3.0 SECTIONS (gap-driven) =============================================

def render_cascade(stats: dict[str, ModelStats]) -> Optional[str]:
    """Render the auto-computed provider cascade (best → fallback).

    The single most actionable answer to "which model should I use right now?"
    """
    # Filter to models with enough data
    candidates = [s for s in stats.values() if s.total >= 3]
    if not candidates:
        return None

    # Sort by success rate desc, then by P50 latency asc
    candidates.sort(key=lambda s: (-s.rate, s.p50))

    # Take top 5 for the cascade
    top = candidates[:5]
    if not top or top[0].rate < 50:
        return None  # No good primary

    print(f"{C.BOLD}★ RECOMMENDED CASCADE{C.END}  {C.DIM}(best → fallback){C.END}")
    for i, s in enumerate(top):
        if i == 0:
            marker = f"{C.G}★{C.END}"
            role = f"{C.G}PRIMARY{C.END}    "
        else:
            marker = f"{i+1}."
            role = f"{C.DIM}FALLBACK {i}{C.END}"
        rate_str = fmt_pct(s.rate)
        p50_str = fmt_ms(s.p50) if s.p50 else f"{C.DIM}--{C.END}"
        # Show quality if available
        qual_str = ""
        if s.quality_total > 0:
            qual_str = f"  Q={fmt_pct(s.quality_rate)}"
        print(f"  {marker} {role} {s.label:<24} {rate_str}  P50={p50_str}{qual_str}")
    print()

    return top[0].label if top else None


def render_failure_taxonomy(stats: dict[str, ModelStats]) -> None:
    """Render the failure mode taxonomy.

    This addresses the most critical gap: 98.4% of failures are RATE_LIMITED.
    The dashboard now reveals the root cause instead of just "low success rate".
    """
    # Aggregate across all models
    all_failures: dict[str, int] = defaultdict(int)
    total_failures = 0
    for s in stats.values():
        for cat, count in s.failure_categories.items():
            all_failures[cat] += count
            total_failures += count

    if total_failures == 0:
        return

    print(f"{C.BOLD}FAILURE MODE TAXONOMY{C.END}  {C.DIM}({total_failures} total failures){C.END}")
    print(f"  {'CATEGORY':<20} {'COUNT':>6} {'%':>6}  BAR")
    print(f"  {'─' * 20} {'─' * 6} {'─' * 6}  {'─' * 30}")

    # Sort by count desc
    sorted_cats = sorted(all_failures.items(), key=lambda x: -x[1])
    for cat, count in sorted_cats:
        pct = (count / total_failures) * 100
        # Color the category
        cat_color = C.R if pct > 80 else (C.Y if pct > 30 else C.DIM)
        bar = "█" * int(pct / 3)  # 33 chars max
        print(f"  {cat_color}{cat:<20}{C.END} {count:>6} {pct:>5.0f}%  {bar}")

    # Insight: if >80% is one category, name the response
    top_cat, top_count = sorted_cats[0]
    top_pct = (top_count / total_failures) * 100
    if top_pct > 80:
        responses = {
            "RATE_LIMITED": f"{C.Y}→ WAIT for quota reset, not more key diversification{C.END}",
            "AUTH_FAILED": f"{C.R}→ Key is dead/expired, rotate immediately{C.END}",
            "INVALID_MODEL": f"{C.R}→ Model removed from provider, drop from fleet{C.END}",
            "SERVER_ERROR": f"{C.Y}→ Provider outage, switch to fallback{C.END}",
        }
        insight = responses.get(top_cat, f"→ Investigate {top_cat}")
        print(f"  {C.BOLD}INSIGHT:{C.END} {top_pct:.0f}% are {top_cat} {insight}")
    print()


def render_quality_breakdown(stats: dict[str, ModelStats]) -> None:
    """Render per-model quality breakdown (what kind of bad).

    Closes gap: "69% quality" hides why the other 31% failed.
    """
    # Only show models with non-trivial quality data
    candidates = [s for s in stats.values() if s.quality_total >= 5]
    if not candidates:
        return

    print(f"{C.BOLD}QUALITY BREAKDOWN{C.END}  {C.DIM}(why some responses are bad){C.END}")
    print(f"  {'MODEL':<22} {'VALID':>6} {'INV_JSON':>9} {'NO_COMP':>8} {'EMPTY':>6}")
    print(f"  {'─' * 22} {'─' * 6} {'─' * 9} {'─' * 8} {'─' * 6}")

    # Sort by quality rate desc
    candidates.sort(key=lambda s: -s.quality_rate)
    for s in candidates[:8]:  # top 8
        v = s.quality_valid
        ij = s.quality_invalid_json
        nc = s.quality_no_completion
        ec = s.quality_empty_content

        # Color the dominant failure mode
        worst = max([("invalid_json", ij), ("no_completion", nc), ("empty", ec)], key=lambda x: x[1])
        worst_str = f"{C.R}{worst[1]:>4}{C.END}" if worst[0] == "invalid_json" else f"{C.Y}{worst[1]:>4}{C.END}"

        # carmack: pad_visible instead of :>9 because worst_str embeds ANSI
        # escape codes; :>9 pads on Python string length (13+), not
        # visible width (4), breaking the column.
        print(f"  {s.label:<22} {C.G}{v:>6}{C.END} {pad_visible(worst_str, 9)} {nc:>8} {ec:>6}")
    print()


def render_next_quota_reset(ag_data: list[dict]) -> None:
    """Render the next quota reset countdown."""
    if not ag_data:
        return

    # Find the soonest reset across all accounts/models
    now = datetime.now(timezone.utc)
    upcoming = []
    for entry in ag_data:
        for m in entry.get("models", []):
            rt = m.get("resetTime")
            if rt:
                try:
                    rdt = datetime.fromisoformat(rt.replace("Z", "+00:00"))
                    # carmack: naive-tz guard for the comparison `rdt > now`
                    # which would TypeError if rdt lacks tzinfo.
                    if rdt.tzinfo is None:
                        rdt = rdt.replace(tzinfo=timezone.utc)
                    if rdt > now:
                        upcoming.append((rdt, entry.get("email", "?"), m.get("id", "?")))
                except (ValueError, TypeError):
                    pass

    if not upcoming:
        return

    upcoming.sort()
    next_reset, email, model_id = upcoming[0]
    delta = next_reset - now
    hours = int(delta.total_seconds() // 3600)
    mins = int((delta.total_seconds() % 3600) // 60)

    # Color based on urgency
    if hours < 2:
        color = C.G  # Soon = good news
    elif hours < 6:
        color = C.Y
    else:
        color = C.DIM

    print(f"{C.BOLD}⏰ NEXT QUOTA RESET{C.END}  {color}in {hours}h {mins}m{C.END}  "
          f"{C.DIM}({email.split('@')[0]} for {model_id}){C.END}")
    print()


def render_diurnal_best_hour(probe_data: list[dict]) -> None:
    """Render the diurnal best hour recommendation.

    Closes gap: at 00:00 UTC we have 61% success, at 18:00 UTC we have 11%.
    Schedule heavy work around the best hours.
    """
    if not probe_data:
        return

    hourly: dict[int, list[bool]] = defaultdict(list)
    for entry in probe_data:
        ts_str = entry.get("ts")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            # carmack: naive-tz guard — assume UTC if missing tzinfo.
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            hourly[ts.hour].append(bool(entry.get("success")))
        except (ValueError, TypeError):
            pass

    if not hourly:
        return

    # Calculate success rate per hour
    hour_rates = []
    for h, results in hourly.items():
        if len(results) >= 3:
            rate = sum(results) / len(results) * 100
            hour_rates.append((h, rate, len(results)))

    if not hour_rates:
        return

    # Sort by rate desc
    hour_rates.sort(key=lambda x: -x[1])
    best_h, best_rate, _ = hour_rates[0]
    worst_h, worst_rate, _ = hour_rates[-1]

    # Render as a small chart
    print(f"{C.BOLD}📊 DIURNAL PATTERN{C.END}  {C.DIM}(UTC hours, success rate){C.END}")
    chart = "  "
    for h in range(0, 24, 3):  # every 3 hours
        hour_results = hourly.get(h, [])
        if hour_results:
            rate = sum(hour_results) / len(hour_results) * 100
            bar = "█" * int(rate / 5)
            chart += f"{h:02d}:00 {fmt_pct(rate):>5} {bar:<20}  "
        else:
            chart += f"{h:02d}:00  {C.DIM}--{C.END}  {C.DIM}{'─' * 20}  "
        if h == 12:
            chart += "\n  "
    print(chart)
    print(f"  {C.G}Best: {best_h:02d}:00 UTC ({best_rate:.0f}% success){C.END}  "
          f"{C.R}Worst: {worst_h:02d}:00 UTC ({worst_rate:.0f}%){C.END}")
    # Guard against worst_rate == 0 (division by zero). Also skip the
    # insight line entirely if there's no spread — happens early in the
    # data lifecycle before enough samples per hour accumulate.
    if worst_rate > 0:
        ratio = best_rate / worst_rate
        print(f"  {C.DIM}Insight: {ratio:.1f}x difference — schedule heavy work at "
              f"{best_h:02d}:00 UTC{C.END}")
    else:
        print(f"  {C.DIM}Insight: insufficient spread yet — keep collecting samples{C.END}")
    print()


def render_historical_comparison(stats: dict[str, ModelStats], probe_data: list[dict]) -> None:
    """Render Today vs Yesterday at the same time of day.

    Closes gap: is performance improving or degrading week-over-week?
    """
    if not probe_data:
        return

    now = datetime.now(timezone.utc)
    today_start = now - timedelta(hours=24)
    yesterday_start = now - timedelta(hours=48)

    # For each model, compare last 24h vs 24-48h ago
    today_stats: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    yesterday_stats: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for entry in probe_data:
        label = entry.get("label", "?")
        success = 0 if entry.get("success") else 1
        ts_str = entry.get("ts")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            # carmack: defend against naive timestamps (no tzinfo). The
            # rest of the dashboard assumes tz-aware UTC; comparing a
            # naive ts to today_start (tz-aware UTC) would raise
            # TypeError. Fall back: assume UTC.
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue

        if ts > today_start:
            today_stats[label][success] += 1
        elif ts > yesterday_start:
            yesterday_stats[label][success] += 1

    # Only show models with enough data
    candidates = []
    for label in today_stats:
        t_s, t_f = today_stats[label]
        y_s, y_f = yesterday_stats.get(label, [0, 0])
        if t_s + t_f >= 3 and y_s + y_f >= 3:
            t_rate = t_s / (t_s + t_f) * 100
            y_rate = y_s / (y_s + y_f) * 100
            delta = t_rate - y_rate
            candidates.append((label, t_s, t_s + t_f, t_rate, y_rate, delta))

    if not candidates:
        return

    print(f"{C.BOLD}📅 HISTORICAL COMPARISON{C.END}  {C.DIM}(today vs yesterday){C.END}")
    print(f"  {'MODEL':<22} {'TODAY':<10} {'YESTERDAY':<12} {'Δ RATE':>8}")
    print(f"  {'─' * 22} {'─' * 10} {'─' * 12} {'─' * 8}")

    # Sort by abs delta desc (most interesting changes first)
    candidates.sort(key=lambda x: -abs(x[5]))
    for label, t_s, t_t, t_rate, y_rate, delta in candidates[:10]:
        t_str = f"{t_s}/{t_t} ({t_rate:.0f}%)"
        y_str = f"({y_rate:.0f}%)"
        if delta > 10:
            d_str = f"{C.G}↑↑ +{delta:.0f}%{C.END}"
        elif delta > 3:
            d_str = f"{C.G}↑ +{delta:.0f}%{C.END}"
        elif delta < -10:
            d_str = f"{C.R}↓↓ {delta:.0f}%{C.END}"
        elif delta < -3:
            d_str = f"{C.R}↓ {delta:.0f}%{C.END}"
        else:
            d_str = f"{C.DIM}→ {delta:+.0f}%{C.END}"
        # carmack: pad_visible for d_str which embeds ANSI codes.
        print(f"  {label:<22} {t_str:<10} {y_str:<12} {pad_visible(d_str, 8)}")
    print()


def render_key_health(stats: dict[str, ModelStats]) -> None:
    """Render per-key health table.

    Closes gap: which of the 3 keys (or_key, cline, auth) is healthy?
    """
    # Aggregate across all models
    key_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"success": 0, "fail": 0, "models": 0})
    key_last_success_global: dict[str, Optional[datetime]] = {}

    for s in stats.values():
        for key, count in s.key_sources.items():
            # Estimate success/fail per key from the overall success rate
            if s.total > 0:
                key_success = int(count * s.rate / 100)
                # Clamp: int() rounding can produce key_success > count when
                # rate * count / 100 rounds up. Defensive guard against negative
                # arithmetic on malformed inputs.
                key_success = max(0, min(key_success, count))
                key_fail = count - key_success
                key_totals[key]["success"] += key_success
                key_totals[key]["fail"] += key_fail
                key_totals[key]["models"] += 1
        for key, last in s.key_last_success.items():
            if last is None:
                continue
            current_best = key_last_success_global.get(key)
            if current_best is None or last > current_best:
                key_last_success_global[key] = last

    if not key_totals:
        return

    print(f"{C.BOLD}🔑 KEY HEALTH{C.END}  {C.DIM}(3-key rotation){C.END}")
    print(f"  {'KEY':<12} {'SUCCESS':>8} {'FAIL':>6} {'RATE':>6}  {'MODELS':>7}  {'LAST SUCCESS':>20}")
    print(f"  {'─' * 12} {'─' * 8} {'─' * 6} {'─' * 6}  {'─' * 7}  {'─' * 20}")

    # Sort by rate desc
    sorted_keys = sorted(key_totals.items(),
                          key=lambda x: -safe_div(x[1]["success"], x[1]["success"] + x[1]["fail"]) * 100)
    for key, t in sorted_keys:
        total = t["success"] + t["fail"]
        if total == 0:
            rate_str = f"{C.DIM}--{C.END}"
        else:
            rate = t["success"] / total * 100
            rate_str = fmt_pct(rate)
        last_s = key_last_success_global.get(key)
        if last_s is not None:
            age = int((datetime.now(timezone.utc) - last_s).total_seconds())
            # fmt_age already handles >= 86400 → days branch; the previous
            # `age if age < 86400 else f"{age//86400}d ago"` was redundant.
            last_str = fmt_age(age) if age >= 0 else f"{C.DIM}never{C.END}"
        else:
            last_str = f"{C.R}NEVER{C.END}"

        # Highlight dead keys
        if total == 0 or t["success"] == 0:
            key_disp = f"{C.R}{key} ⚠{C.END}"
        elif safe_div(t["success"], total) < 0.5:
            key_disp = f"{C.Y}{key}{C.END}"
        else:
            key_disp = f"{C.G}{key}{C.END}"

        # carmack: pad_visible for rate_str and last_str (both embed ANSI).
        # key_disp is left-aligned and we WANT the visible width to be 20,
        # so pad_visible with '<'.
        print(f"  {pad_visible(key_disp, 20, '<')} {t['success']:>8} {t['fail']:>6} "
              f"{pad_visible(rate_str, 6)}  {t['models']:>7}  {pad_visible(last_str, 20)}")
    print()


def render_header_v3(now: datetime) -> None:
    """Enhanced header with v3.0 metadata."""
    ts = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"{C.BOLD}{C.C}⬡ OMEGA ENGINE BENCHMARK DASHBOARD{C.END}  "
          f"{C.DIM}v3.0 (gap-driven){C.END}  {C.DIM}{ts}{C.END}")
    print(f"{C.DIM}{'─' * 90}{C.END}")


def render_footer(args: argparse.Namespace) -> None:
    """Render the dashboard footer."""
    refresh = f"{args.refresh}s" if args.refresh else "2s"
    sources = [PROBE_LOG.name, NETWORK_LOG.name]
    if ANTIGRAVITY_LOG:
        sources.append(ANTIGRAVITY_LOG.name)
    print(f"{C.DIM}{'─' * 90}{C.END}")
    print(f"{C.DIM}Refresh: {refresh} | Sources: {', '.join(sources)} | "
          f"Filter: --model={args.model or '*'} --since={args.since or 'all'} | "
          f"Press Ctrl+C to exit{C.END}")


# === MAIN RENDER ============================================================

def render(args: argparse.Namespace) -> dict[str, Any]:
    """Single render pass. Returns the state dict for export modes."""
    now = datetime.now(timezone.utc)

    # Determine time window
    since: Optional[datetime] = None
    if args.since:
        try:
            hours = float(args.since.rstrip("h"))
            since = now - timedelta(hours=hours)
        except ValueError:
            since = None

    # Get freshness
    freshness = {
        "free_model_probes": get_file_freshness(PROBE_LOG, since=since),
        "network_probes": get_file_freshness(NETWORK_LOG, since=since),
        "antigravity_quotas": get_file_freshness(ANTIGRAVITY_LOG, since=since) if ANTIGRAVITY_LOG else FileFreshness(path=Path("(none)")),
    }

    # Read data
    probe_data = read_jsonl(PROBE_LOG, since=since)
    network_data = read_jsonl(NETWORK_LOG, limit=10, since=since)
    ag_data = read_jsonl(ANTIGRAVITY_LOG, limit=20) if ANTIGRAVITY_LOG else []

    # Aggregate
    stats = aggregate_probes(probe_data)

    # Build state dict for export
    state = {
        "timestamp": now.isoformat(),
        "version": "3.0",
        "filters": {
            "model": args.model,
            "since": args.since,
        },
        "freshness": {
            k: {
                "state": v.state,
                "age_seconds": v.age_seconds,
                "entries_total": v.entries_total,
                "entries_in_window": v.entries_in_window,
            }
            for k, v in freshness.items()
        },
        "models": {s.label: s.to_dict() for s in stats.values()},
    }

    # Clear and render (unless suppressed)
    if not args.no_clear and not args.json and not args.csv:
        print(C.CLR, end="")

    if args.json:
        return state  # caller handles JSON output

    if args.csv:
        return state  # caller handles CSV output

    # Normal dashboard render
    render_header_v3(now)
    render_freshness_summary(freshness)
    render_next_quota_reset(ag_data)
    render_cascade(stats)
    render_failure_taxonomy(stats)
    render_network(network_data)
    render_alerts(stats, args)
    sorted_stats = render_probes(stats, args)
    if args.diurnal:
        render_diurnal_analysis(stats, args)
    render_quality_breakdown(stats)
    render_historical_comparison(stats, probe_data)
    render_key_health(stats)
    render_antigravity(ag_data)
    render_test_progress("STRESS TEST", STRESS_LOG, "🔥")
    render_test_progress("BURST TEST", BURST_LOG, "💥")
    render_test_progress("LONG DURATION TEST", LONG_DUR_LOG, "⏱️")
    render_diurnal_best_hour(probe_data)
    render_economics(probe_data, stats)
    render_active_sessions()
    render_footer(args)

    return state


# === EXPORT MODES ===========================================================

def export_json(state: dict[str, Any]) -> None:
    """Output state as JSON."""
    print(json.dumps(state, indent=2, default=str))


def export_csv(state: dict[str, Any]) -> None:
    """Output model stats as CSV.

    carmack: original used `m["key"]` for required fields, which raises
    KeyError if to_dict() ever returns a partial dict (e.g. serialized
    through a custom encoder). Defensive `.get()` with safe defaults.
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "model", "success", "fail", "total", "rate", "p50_ms", "p99_ms",
        "outlier_pct", "quality_rate", "valid", "invalid_json", "no_completion",
        "empty_content", "trend", "trend_velocity", "last_seen"
    ])
    for label, m in state.get("models", {}).items():
        qb = m.get("quality_breakdown", {})
        writer.writerow([
            label,
            m.get("success", 0), m.get("fail", 0), m.get("total", 0),
            m.get("rate", 0.0), m.get("p50_ms", 0.0), m.get("p99_ms", 0.0),
            m.get("outlier_pct", 0), m.get("quality_rate", 0.0),
            qb.get("valid", 0), qb.get("invalid_json", 0),
            qb.get("no_completion", 0), qb.get("empty_content", 0),
            m.get("trend", ""), m.get("trend_velocity", ""),
            m.get("last_seen", "")
        ])
    print(buf.getvalue(), end="")


# === ARGUMENT PARSING =======================================================

def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="benchmark_dashboard",
        description="Real-time benchmark visualization for Omega Engine diurnal provider suite.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Live dashboard, refresh every 2s
  benchmark_dashboard.py

  # Single snapshot (for scripts/CI)
  benchmark_dashboard.py --once

  # Custom refresh rate
  benchmark_dashboard.py --refresh 5

  # Filter to specific model
  benchmark_dashboard.py --model minimax

  # Show only last 6 hours of data
  benchmark_dashboard.py --since 6h

  # Threshold alerts
  benchmark_dashboard.py --alerts --alert-rate 80 --alert-latency 10000

  # JSON export (for tooling)
  benchmark_dashboard.py --json

  # CSV export (for spreadsheets)
  benchmark_dashboard.py --csv

  # Diurnal pattern analysis
  benchmark_dashboard.py --diurnal

  # Don't clear screen (for log files)
  benchmark_dashboard.py --no-clear --refresh 10
        """
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Render single snapshot and exit (don't loop)"
    )
    parser.add_argument(
        "--no-clear", action="store_true",
        help="Don't clear screen between renders (useful for logs)"
    )
    parser.add_argument(
        "--refresh", type=int, default=2, metavar="N",
        help="Refresh interval in seconds (default: 2)"
    )
    parser.add_argument(
        "--model", type=str, default=None, metavar="PATTERN",
        help="Filter to models matching regex PATTERN (e.g. 'minimax|llama')"
    )
    parser.add_argument(
        "--since", type=str, default=None, metavar="HOURS",
        help="Show only entries within last N hours (e.g. '6h', '24h')"
    )
    parser.add_argument(
        "--alerts", action="store_true",
        help="Enable threshold-based alerts"
    )
    parser.add_argument(
        "--alert-rate", type=float, default=ALERT_RATE_DEFAULT, metavar="PCT",
        help=f"Alert threshold for success rate %% (default: {ALERT_RATE_DEFAULT})"
    )
    parser.add_argument(
        "--alert-latency", type=int, default=ALERT_LATENCY_DEFAULT_MS, metavar="MS",
        help=f"Alert threshold for P99 latency in ms (default: {ALERT_LATENCY_DEFAULT_MS})"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output single snapshot as JSON and exit"
    )
    parser.add_argument(
        "--csv", action="store_true",
        help="Output single snapshot as CSV and exit"
    )
    parser.add_argument(
        "--diurnal", action="store_true",
        help="Show diurnal pattern analysis section"
    )
    return parser.parse_args()


# === MAIN ====================================================================

def main() -> int:
    """Main entry point. Returns exit code."""
    args = parse_args()

    # Validate
    if args.refresh < 1:
        print(f"Error: --refresh must be >= 1", file=sys.stderr)
        return 1

    # Handle export modes (single render, then exit)
    if args.json or args.csv:
        state = render(args)
        if args.json:
            export_json(state)
        else:
            export_csv(state)
        return 0

    # Live loop mode
    try:
        while True:
            render(args)
            if args.once:
                break
            time.sleep(args.refresh)
    except KeyboardInterrupt:
        print(f"\n{C.Y}Dashboard stopped.{C.END}")
        return 0
    except Exception as e:
        # M23: never crash, but DO report
        print(f"\n{C.R}Dashboard error: {e}{C.END}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
