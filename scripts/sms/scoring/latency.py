"""Latency aggregation helpers."""

from __future__ import annotations

from typing import Iterable


def percentile(values: Iterable[float], p: float) -> float:
    vals = sorted(values)
    if not vals:
        return 0.0
    if len(vals) == 1:
        return vals[0]
    k = (len(vals) - 1) * p / 100.0
    lo, hi = int(k), min(len(vals) - 1, int(k) + 1)
    return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)


def summarize(values: Iterable[float]) -> dict:
    vals = list(values)
    if not vals:
        return {"n": 0, "p50": 0.0, "p95": 0.0, "mean": 0.0, "max": 0.0}
    return {
        "n": len(vals),
        "p50": round(percentile(vals, 50), 3),
        "p95": round(percentile(vals, 95), 3),
        "mean": round(sum(vals) / len(vals), 3),
        "max": round(max(vals), 3),
    }
