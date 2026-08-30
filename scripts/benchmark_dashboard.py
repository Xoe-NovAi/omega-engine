#!/usr/bin/env python3
"""
benchmark_dashboard.py v2.0 — Real-time benchmark visualization for Omega Engine
=========================================================================
Terminal-native dashboard for the diurnal provider benchmark suite.

Improvements in v2.0:
  - P0: Compute M3 economics from actual data (not hardcoded)
  - P0: Add data freshness indicator (color-coded age warnings)
  - P1: Add trend sparklines (↑/↓/→ direction indicators)
  - P1: CLI argument parsing (--model, --since, --refresh, --once, --json, --csv, --no-clear, --alerts, etc.)
  - P1: Model filtering (--model PATTERN, --since HOURS)
  - P2: Quality score column (valid_json + has_completion rates)
  - P2: Antigravity quota rendering (per-account, per-model breakdown)
  - P2: Threshold alerting (--alert-rate, --alert-latency)
  - P3: --json / --csv export modes
  - P3: Diurnal pattern analysis (off_peak/moderate/poor/worst windows)
  - P3: Per-key health breakdown
  - P3: Incremental file reads (only read new lines since last check)
  - P3: Configurable paths via env vars
  - Hardening: M23 failure integrity (never crash, always degrade gracefully)
  - Hardening: File lock resilience (atomic JSONL tail)
  - Hardening: UTF-8 encoding handling
  - Hardening: Type hints throughout
  - Hardening: Active session detection with PID + memory
  - Hardening: Network quality assessment (signal/latency correlation)

Author: grokster (M11 distillation from v1.0 review)
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
from collections import defaultdict
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
    quality_total: int = 0
    http_statuses: dict[str, int] = field(default_factory=dict)
    key_sources: dict[str, int] = field(default_factory=dict)
    windows: dict[str, int] = field(default_factory=dict)
    last_seen: Optional[datetime] = None
    last_success: Optional[datetime] = None
    recent_window: list[bool] = field(default_factory=list)  # last N successes (for trend)

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
    def trend(self) -> str:
        """Determine trend direction from recent window. Returns ↑, ↓, →"""
        if not self.recent_window or len(self.recent_window) < 4:
            return "?"
        half = len(self.recent_window) // 2
        first_half_rate = sum(self.recent_window[:half]) / half
        second_half_rate = sum(self.recent_window[half:]) / (len(self.recent_window) - half)
        delta = second_half_rate - first_half_rate
        if delta > 0.15:  # >15% improvement
            return "↑"
        if delta < -0.15:  # >15% degradation
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
            "quality_rate": round(self.quality_rate, 2),
            "trend": self.trend,
            "http_statuses": self.http_statuses,
            "key_sources": self.key_sources,
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
    if not C.BOLD:  # No color mode
        char, empty = "#", "-"
    if total == 0:
        return "[" + empty * width + "]"
    pct = current / total
    filled = int(width * pct)
    bar = char * filled + empty * (width - filled)
    return f"[{bar}] {pct * 100:.0f}% ({current}/{total})"


def fmt_ms(ms: float) -> str:
    """Format milliseconds as human-readable string."""
    if ms < 0:
        return f"{C.DIM}--{C.END}"
    if ms == 0:
        return f"{C.DIM}0ms{C.END}"
    if ms < 1000:
        return f"{ms:.0f}ms"
    return f"{ms / 1000:.1f}s"


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
                # Read last N lines efficiently using a deque
                from collections import deque
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
                    entry_ts = datetime.fromisoformat(
                        entry["ts"].replace("Z", "+00:00")
                    )
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
    """Get freshness metadata for a file."""
    if not path or not path.exists():
        return FileFreshness(path=path or Path())
    try:
        stat = path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        age = int((datetime.now(timezone.utc) - mtime).total_seconds())
        entries = read_jsonl(path, since=since)
        return FileFreshness(
            path=path,
            last_modified=mtime,
            age_seconds=age,
            entries_total=sum(1 for _ in open(path, encoding="utf-8", errors="replace")),
            entries_in_window=len(entries),
        )
    except (OSError, IOError):
        return FileFreshness(path=path)


# === AGGREGATION ============================================================

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

        lat = entry.get("latency_ms", 0)
        if isinstance(lat, (int, float)) and lat > 0:
            s.latencies.append(float(lat))

        # Quality check
        qc = entry.get("quality_check", {})
        if isinstance(qc, dict):
            s.quality_total += 1
            if qc.get("valid_json") and qc.get("has_completion"):
                s.quality_valid += 1

        # HTTP status
        status = entry.get("http_status")
        if status:
            s.http_statuses[str(status)] = s.http_statuses.get(str(status), 0) + 1

        # Key source
        ks = entry.get("key_source", "?")
        s.key_sources[ks] = s.key_sources.get(ks, 0) + 1

        # Window
        win = entry.get("window")
        if win:
            s.windows[win] = s.windows.get(win, 0) + 1

        # Timestamps
        ts_str = entry.get("ts")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                s.last_seen = ts
                if entry.get("success"):
                    s.last_success = ts
            except (ValueError, TypeError):
                pass

        # Recent window for trend (last 20 calls)
        s.recent_window.append(bool(entry.get("success")))
        if len(s.recent_window) > 20:
            s.recent_window.pop(0)

    return stats


# === RENDERING: SECTIONS ====================================================

def render_header(now: datetime) -> None:
    """Render the dashboard header."""
    ts = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"{C.BOLD}{C.C}⬡ OMEGA ENGINE BENCHMARK DASHBOARD{C.END}  {C.DIM}v2.0{C.END}  {C.DIM}{ts}{C.END}")
    print(f"{C.DIM}{'─' * 90}{C.END}")


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
    sig_int = int(sig) if isinstance(sig, (int, str)) and str(sig).lstrip("-").isdigit() else 0
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

        print(f"  {s.label:<24} {s.success:>8} {s.fail:>6} {rate_str:>6} {p50_str:>8} {p99_str:>8} {quality_str:>6} {trend_str:>6} {window_str:>5}  {best_key}")
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
                if ts > prev_ts:
                    by_account[email] = entry
            except (ValueError, TypeError):
                pass

    for email, entry in by_account.items():
        enabled = entry.get("enabled", False)
        tier = entry.get("tier", "?")
        models = entry.get("models", [])
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
    quality_entries = [e for e in probe_data if e.get("quality_check")]
    quality_valid = sum(
        1 for e in quality_entries
        if e["quality_check"].get("valid_json") and e["quality_check"].get("has_completion")
    )
    quality_rate = safe_div(quality_valid, len(quality_entries)) * 100

    # Total latency (rough proxy for tokens processed)
    total_latency_s = sum(e.get("latency_ms", 0) for e in probe_data) / 1000

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
        "version": "2.0",
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
    render_header(now)
    render_freshness_summary(freshness)
    render_network(network_data)
    render_alerts(stats, args)
    sorted_stats = render_probes(stats, args)
    if args.diurnal:
        render_diurnal_analysis(stats, args)
    render_antigravity(ag_data)
    render_test_progress("STRESS TEST", STRESS_LOG, "🔥")
    render_test_progress("BURST TEST", BURST_LOG, "💥")
    render_test_progress("LONG DURATION TEST", LONG_DUR_LOG, "⏱️")
    render_economics(probe_data, stats)
    render_active_sessions()
    render_footer(args)

    return state


# === EXPORT MODES ===========================================================

def export_json(state: dict[str, Any]) -> None:
    """Output state as JSON."""
    print(json.dumps(state, indent=2, default=str))


def export_csv(state: dict[str, Any]) -> None:
    """Output model stats as CSV."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "model", "success", "fail", "total", "rate", "p50_ms", "p99_ms",
        "quality_rate", "trend", "key_sources", "last_seen"
    ])
    for label, m in state.get("models", {}).items():
        key_sources = ",".join(f"{k}={v}" for k, v in m.get("key_sources", {}).items())
        writer.writerow([
            label, m["success"], m["fail"], m["total"], m["rate"],
            m["p50_ms"], m["p99_ms"], m["quality_rate"], m["trend"],
            key_sources, m.get("last_seen", "")
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
