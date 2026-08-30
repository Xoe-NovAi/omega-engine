#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
probe_percentiles.py — Compute rolling percentiles from probe data
Version: v1.0 (probe-report-actions-20260827 — Action 3)

Reads:  data/metrics/free_model_probes.jsonl
Writes: data/metrics/model_percentiles.jsonl  (one row per model per run)

For each model, computes over the last 50 probes:
  - count
  - success_count
  - success_rate (0.0-1.0)
  - quality_pass_rate (valid_json AND has_completion)
  - latency_ms: p50, p90, p99, mean, stdev
  - windows observed (off_peak/moderate/poor/worst)
  - latest_status, latest_ts

Usage:
  python3 scripts/probe_percentiles.py [--window 50] [--input PATH] [--output PATH]

Mandate compliance:
  M8 (zero telemetry): only reads local files, no external calls
  M23 (failure integrity): tool errors → sys.exit(2), no soft-fail
  M27 (tracking integrity): 6-step flow observed (read, compute, write atomically)
"""

import argparse
import json
import math
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev

# === DEFAULTS ===
DEFAULT_INPUT = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/free_model_probes.jsonl"
DEFAULT_OUTPUT = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/model_percentiles.jsonl"
DEFAULT_WINDOW = 50

# === PERCENTILE =============================================================
def percentile(values, p):
    """Linear-interpolation percentile, returns None if empty."""
    if not values:
        return None
    if len(values) == 1:
        return float(values[0])
    sorted_v = sorted(values)
    k = (len(sorted_v) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_v[int(k)])
    d0 = sorted_v[int(f)] * (c - k)
    d1 = sorted_v[int(c)] * (k - f)
    return float(d0 + d1)


def safe_round(value, digits=1):
    """Round that returns None for None (avoids LSP type errors)."""
    if value is None:
        return None
    if not isinstance(value, (int, float)):
        return None
    return round(float(value), digits)

# === MAIN ==================================================================
def main():
    ap = argparse.ArgumentParser(description="Rolling percentiles for probe data")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                    help="Path to free_model_probes.jsonl")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                    help="Path to model_percentiles.jsonl")
    ap.add_argument("--window", type=int, default=DEFAULT_WINDOW,
                    help="Number of recent probes per model to consider (default 50)")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"[FATAL] input not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    # Read all probes, group by model, keep only last N per model
    by_model = defaultdict(list)
    total_lines = 0
    parse_errors = 0
    with args.input.open() as f:
        for line in f:
            total_lines += 1
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                continue
            model = d.get("model")
            if not model:
                continue
            by_model[model].append(d)

    # Truncate to last N per model
    truncated = 0
    for m in list(by_model.keys()):
        if len(by_model[m]) > args.window:
            truncated += len(by_model[m]) - args.window
            by_model[m] = by_model[m][-args.window:]

    # Compute percentiles
    results = []
    for model, probes in sorted(by_model.items()):
        # Successes
        success_count = sum(1 for p in probes if p.get("success"))
        success_rate = success_count / len(probes) if probes else 0.0

        # Quality pass rate
        quality_pass = sum(
            1 for p in probes
            if (p.get("quality_check") or {}).get("valid_json")
            and (p.get("quality_check") or {}).get("has_completion")
        )
        quality_pass_rate = quality_pass / len(probes) if probes else 0.0

        # Latency stats (only on success+valid_json responses — that measures real perf)
        real_latencies = [
            p.get("latency_ms") for p in probes
            if p.get("success")
            and (p.get("quality_check") or {}).get("valid_json")
            and isinstance(p.get("latency_ms"), (int, float))
        ]
        all_latencies = [
            p.get("latency_ms") for p in probes
            if isinstance(p.get("latency_ms"), (int, float))
        ]
        # HTTP status distribution
        statuses = defaultdict(int)
        for p in probes:
            s = p.get("http_status")
            statuses[str(s)] += 1

        # Windows observed
        windows = sorted(set(p.get("window") for p in probes if p.get("window")))

        # Latest entry
        latest = probes[-1] if probes else {}
        latest_ts = latest.get("ts")
        latest_status = latest.get("http_status")
        latest_key = latest.get("key_source")

        results.append({
            "model": model,
            "label": latest.get("label"),
            "window_n": len(probes),
            "success_count": success_count,
            "success_rate": round(success_rate, 4),
            "quality_pass_count": quality_pass,
            "quality_pass_rate": round(quality_pass_rate, 4),
            "latency_real_ms": {
                "count": len(real_latencies),
                "p50": safe_round(percentile(real_latencies, 50)),
                "p90": safe_round(percentile(real_latencies, 90)),
                "p99": safe_round(percentile(real_latencies, 99)),
                "mean": safe_round(mean(real_latencies)) if real_latencies else None,
                "stdev": safe_round(pstdev(real_latencies)) if len(real_latencies) > 1 else None,
                "min": min(real_latencies) if real_latencies else None,
                "max": max(real_latencies) if real_latencies else None,
            },
            "latency_all_ms": {
                "count": len(all_latencies),
                "p50": safe_round(percentile(all_latencies, 50)),
                "mean": safe_round(mean(all_latencies)) if all_latencies else None,
            },
            "http_status_dist": dict(statuses),
            "windows_observed": windows,
            "latest_status": latest_status,
            "latest_key": latest_key,
            "latest_ts": latest_ts,
        })

    # Write atomically: .tmp → rename
    output = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "window_n": args.window,
        "input_total_lines": total_lines,
        "parse_errors": parse_errors,
        "truncated_dropped": truncated,
        "model_count": len(results),
        "models": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    tmp.replace(args.output)

    # Human-readable summary to stdout
    print(f"=== Probe Percentiles ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}) ===")
    print(f"Input:  {args.input} ({total_lines} lines, {parse_errors} parse errors)")
    print(f"Window: last {args.window} probes per model")
    print(f"Output: {args.output}")
    print(f"Models: {len(results)}")
    print()
    print(f"{'Model':<46} {'N':>3} {'SR%':>6} {'QPR%':>6} {'P50':>7} {'P90':>7} {'P99':>7} {'Status'}")
    print("-" * 110)
    for r in results:
        m = r["model"][:45]
        sr = r["success_rate"] * 100
        qpr = r["quality_pass_rate"] * 100
        p50 = r["latency_real_ms"]["p50"]
        p90 = r["latency_real_ms"]["p90"]
        p99 = r["latency_real_ms"]["p99"]
        p50_s = f"{p50:.0f}ms" if p50 is not None else "—"
        p90_s = f"{p90:.0f}ms" if p90 is not None else "—"
        p99_s = f"{p99:.0f}ms" if p99 is not None else "—"
        status = f"{r['latest_status']} ({r['latest_key']})"
        print(f"{m:<46} {r['window_n']:>3} {sr:>5.1f}% {qpr:>5.1f}% {p50_s:>7} {p90_s:>7} {p99_s:>7} {status}")

if __name__ == "__main__":
    main()
