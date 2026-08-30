#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
M3 Stress Test 4 — Sustained Load + Errors (combined degradation test)
AP: AP-M3-STRESS-SUSTAINED-v1.0.0
Author: Grokster
Date: 2026-08-28
Mandates: M8, M23, M26, M27

QUESTION
========
Does M3's error recovery degrade with sustained load?
The brief asks: "Does M3's error recovery degrade with sustained load?"

DESIGN
======
3 phases:
  Phase A (turns 1-20): 20 normal turns (baseline warm-up)
  Phase B (turns 21-30): 10 error turns (5 different error types, twice each)
  Phase C (turns 31-50): 20 recovery turns

Compare Phase C's latency/error rate to Phase A's. If Phase C degrades
relative to Phase A, M3 has memory of errors. If Phase C == Phase A,
M3 is stateless across requests (good for the team).
"""
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "minimax/minimax-m3:free"


def get_api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        auth = Path.home() / ".local/share/opencode/auth.json"
        if auth.exists():
            d = json.loads(auth.read_text())
            key = d.get("openrouter", {}).get("key", "")
    return key


def call(payload, headers_extra=None, timeout=30):
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://omega-engine.local/stress-test",
    }
    if headers_extra:
        headers.update(headers_extra)
    req = urllib.request.Request(API_URL, data=json.dumps(payload).encode(), headers=headers)
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, int((time.time() - t0) * 1000), json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, int((time.time() - t0) * 1000), {"error": e.read()[:200].decode(errors='replace')}
    except Exception as e:
        return -1, int((time.time() - t0) * 1000), {"error": str(e)[:200]}


def main() -> int:
    out_path = Path("data/metrics/m3_sustained_load_20260828.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print("=== M3 SUSTAINED LOAD + ERRORS ===")
    print("Phase A: 20 normal (baseline)")
    print("Phase B: 10 errors (5 types × 2)")
    print("Phase C: 20 normal (recovery under sustained load)")
    print()
    results = {"A": [], "B": [], "C": []}
    # Phase A: 20 normal
    for i in range(1, 21):
        s, lat, body = call({
            "model": MODEL,
            "messages": [{"role": "user", "content": f"Phase A turn {i}: 'OK A{i}'"}],
            "max_tokens": 30,
        })
        ok = (s == 200)
        results["A"].append({"turn": i, "status": s, "latency_ms": lat, "ok": ok})
        marker = "✅" if ok else "❌"
        print(f"  A{i:2d} {marker} {lat:>5}ms status={s}")
    # Phase B: 10 errors
    error_payloads = [
        ("invalid_model", {"model": "fake-model", "messages": [{"role": "user", "content": "x"}]}),
        ("missing_messages", {"model": MODEL}),
        ("malformed_messages", {"model": MODEL, "messages": "not-a-list"}),
        ("wrong_auth", {"model": MODEL, "messages": [{"role": "user", "content": "x"}]}, {"Authorization": "Bearer fake"}),
        ("bad_temperature", {"model": MODEL, "messages": [{"role": "user", "content": "x"}], "temperature": 99.0}),
    ]
    for i in range(1, 11):
        entry = error_payloads[(i - 1) % len(error_payloads)]
        # entry is either (kind, payload) or (kind, payload, headers_extra)
        kind = entry[0]
        actual_payload = entry[1]
        headers_extra = entry[2] if len(entry) == 3 else None
        s, lat, body = call(actual_payload, headers_extra=headers_extra)
        ok = (s in (400, 401, 404))  # expected error codes
        results["B"].append({"turn": i, "kind": kind, "status": s, "latency_ms": lat, "expected_error": ok})
        marker = "✅" if ok else "❌"
        print(f"  B{i:2d} {marker} {lat:>5}ms kind={kind:20s} status={s}")
    # Phase C: 20 recovery
    for i in range(1, 21):
        s, lat, body = call({
            "model": MODEL,
            "messages": [{"role": "user", "content": f"Phase C turn {i}: 'OK C{i}'"}],
            "max_tokens": 30,
        })
        ok = (s == 200)
        results["C"].append({"turn": i, "status": s, "latency_ms": lat, "ok": ok})
        marker = "✅" if ok else "❌"
        print(f"  C{i:2d} {marker} {lat:>5}ms status={s}")
    # Analysis
    a_lats = [r["latency_ms"] for r in results["A"] if r["ok"]]
    c_lats = [r["latency_ms"] for r in results["C"] if r["ok"]]
    a_success = sum(1 for r in results["A"] if r["ok"]) / len(results["A"])
    c_success = sum(1 for r in results["C"] if r["ok"]) / len(results["C"])
    print(f"\n=== SUSTAINED-LOAD ANALYSIS ===")
    if a_lats and c_lats:
        a_p50 = statistics.median(a_lats)
        c_p50 = statistics.median(c_lats)
        drift = (c_p50 - a_p50) / a_p50 * 100
        print(f"  Phase A success: {a_success*100:.1f}%, p50={a_p50:.0f}ms")
        print(f"  Phase C success: {c_success*100:.1f}%, p50={c_p50:.0f}ms")
        print(f"  Latency drift: {drift:+.1f}%")
        if drift > 30:
            print(f"  ⚠️  M23 ALERT: Phase C latency > 30% higher than Phase A — possible sustained-load degradation")
        else:
            print(f"  ✅ Phase C latency within 30% of Phase A — no sustained degradation detected")
    out_path.write_text(json.dumps({
        "phase_a": results["A"],
        "phase_b": results["B"],
        "phase_c": results["C"],
        "summary": {
            "a_success_rate": a_success,
            "c_success_rate": c_success,
            "a_p50": statistics.median(a_lats) if a_lats else None,
            "c_p50": statistics.median(c_lats) if c_lats else None,
        }
    }, indent=2))
    print(f"\n  saved → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
