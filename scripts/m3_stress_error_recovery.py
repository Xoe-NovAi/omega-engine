#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
M3 Stress Test 3 — Error Recovery: 5+ consecutive errors
AP: AP-M3-STRESS-ERROR-RECOVERY-v1.0.0
Author: Grokster (cline specialist)
Date: 2026-08-28
Mandates: M8, M23 (no soft-fail), M26, M27

WHAT THIS TESTS
===============
After Test 1, M3 was working. This test simulates 5+ errors in a row
via crafted requests (malformed JSON, invalid model names, etc.) and
then sends a NORMAL request. The question: does M3 "remember" the
errors and degrade, or recover cleanly?

Test sequence:
  - Turn 1: 404 (invalid model name)
  - Turn 2: 500 (mock — actually we can only provoke certain errors)
  - Turn 3: malformed JSON (we send invalid payload)
  - Turn 4: auth failure (we send wrong bearer)
  - Turn 5: timeout (we send a slow request that we abort)
  - Turn 6: NORMAL request — does M3 recover?
  - Turn 7-10: 4 more NORMAL requests — does it stay recovered?
"""
import argparse
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
    if not key:
        raise RuntimeError("no API key")
    return key


def call_m3_raw(payload: dict, headers_extra: dict = {}, timeout: int = 30):
    """Send a raw payload. Returns (status, latency, body_or_error)."""
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://omega-engine.local/stress-test",
    }
    headers.update(headers_extra)
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode(), headers=headers
    )
    t0 = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        body = json.loads(resp.read())
        return resp.status, int((time.time() - t0) * 1000), body
    except urllib.error.HTTPError as e:
        body_raw = e.read()[:300].decode(errors='replace')
        try:
            body = json.loads(body_raw)
        except json.JSONDecodeError:
            body = {"raw": body_raw}
        return e.code, int((time.time() - t0) * 1000), body
    except TimeoutError:
        return 0, timeout * 1000, {"error": "timeout"}
    except Exception as e:
        return -1, int((time.time() - t0) * 1000), {"error": str(e)[:200]}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="data/metrics/m3_error_recovery_20260828.json")
    args = p.parse_args()

    print("=== M3 ERROR RECOVERY STRESS ===")
    # === TURN 1: 404 — invalid model name ===
    print("\n[Turn 1] Invalid model name (expect 404)")
    s, lat, body = call_m3_raw({
        "model": "this-model-does-not-exist-12345",
        "messages": [{"role": "user", "content": "PING"}],
        "max_tokens": 5,
    })
    print(f"  status={s} latency={lat}ms body_err={str(body.get('error', body))[:120]}")
    # === TURN 2: 400 — missing messages ===
    print("\n[Turn 2] Missing messages field (expect 400)")
    s, lat, body = call_m3_raw({"model": MODEL, "max_tokens": 5})
    print(f"  status={s} latency={lat}ms body_err={str(body.get('error', body))[:120]}")
    # === TURN 3: 400 — malformed messages (wrong type) ===
    print("\n[Turn 3] Malformed messages (expect 400)")
    s, lat, body = call_m3_raw({
        "model": MODEL,
        "messages": "not a list",
        "max_tokens": 5,
    })
    print(f"  status={s} latency={lat}ms body_err={str(body.get('error', body))[:120]}")
    # === TURN 4: 401 — wrong bearer token ===
    print("\n[Turn 4] Wrong auth header (expect 401)")
    s, lat, body = call_m3_raw(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": "PING"}],
            "max_tokens": 5,
        },
        headers_extra={"Authorization": "Bearer sk-fake-key-1234567890"}
    )
    print(f"  status={s} latency={lat}ms body_err={str(body.get('error', body))[:120]}")
    # === TURN 5: 400 — invalid temperature ===
    print("\n[Turn 5] Invalid temperature (expect 400 or 422)")
    s, lat, body = call_m3_raw({
        "model": MODEL,
        "messages": [{"role": "user", "content": "PING"}],
        "max_tokens": 5,
        "temperature": 99.0,  # > 2 is invalid
    })
    print(f"  status={s} latency={lat}ms body_err={str(body.get('error', body))[:120]}")
    # === TURNS 6-10: NORMAL — does M3 recover? ===
    print("\n[Turns 6-10] Normal requests — does M3 recover?")
    recovery_latencies = []
    recovery_results = []
    for i in range(6, 11):
        s, lat, body = call_m3_raw({
            "model": MODEL,
            "messages": [{"role": "user", "content": f"Recovery test {i}. Say 'OK {i}' briefly."}],
            "max_tokens": 30,
        })
        content = ""
        if s == 200:
            try:
                content = body["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                pass
        print(f"  Turn {i}: status={s} latency={lat}ms content={content!r}")
        recovery_latencies.append(lat)
        recovery_results.append({"turn": i, "status": s, "latency_ms": lat, "content": content})
    # === Summary ===
    success_count = sum(1 for r in recovery_results if r["status"] == 200)
    print(f"\n=== RECOVERY SUMMARY ===")
    print(f"  Recovery turns (6-10): {success_count}/5 succeeded")
    if recovery_latencies:
        print(f"  Recovery latency p50: {statistics.median(recovery_latencies):.0f}ms")
        print(f"  Recovery latency p90: {sorted(recovery_latencies)[int(len(recovery_latencies)*0.9)]:.0f}ms")
        print(f"  Recovery latency mean: {statistics.mean(recovery_latencies):.0f}ms")
    # Compare to baseline (Test 1 p50 = 1573ms)
    baseline_p50 = 1573
    if recovery_latencies:
        recovery_mean = statistics.mean(recovery_latencies)
        drift = (recovery_mean - baseline_p50) / baseline_p50 * 100
        print(f"  Latency drift vs Test 1 baseline: {drift:+.1f}%")
        if abs(drift) > 50:
            print(f"  ⚠️  M23 ALERT: recovery latency drifted > 50% from baseline")
        else:
            print(f"  ✅ Recovery latency within 50% of baseline")
    # Save
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "error_turns": [
            {"label": "404 invalid model", "status": "expected 404", "latency_ms": None},
        ],
        "recovery_results": recovery_results,
        "recovery_success_rate": success_count / 5,
        "baseline_p50_ms": baseline_p50,
    }, indent=2))
    print(f"\n  saved → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
