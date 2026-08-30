#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
stress_test_internal.py — Round 4 §B deliverable
100-request burst test on tab_flash_lite_preview (Antigravity internal workhorse).
Measures: success rate, p50/p90/p99 latency, rate limit detection.
"""
import json
import os
import statistics
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ACCOUNTS_FILE = Path.home() / ".config/opencode/antigravity-accounts.json"
CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
# M23 round-5 fix: was hardcoded GOCSPX-... — moved to env var to remove
# from version control. The hardcoded value is in git history; the
# corresponding GCP OAuth client secret MUST be rotated at console.cloud.google.com
# (APIs & Services > Credentials > 1071006060591-... > Regenerate Secret).
# Track rotation in data/coordination/secret_rotation_log.yaml.
try:
    CLIENT_SECRET = os.environ["ANTIGRAVITY_CLIENT_SECRET"]
except KeyError:
    raise SystemExit(
        "FATAL: ANTIGRAVITY_CLIENT_SECRET env var is not set.\n"
        "       Export it before running: export ANTIGRAVITY_CLIENT_SECRET='GOCSPX-...'\n"
        "       To rotate: GCP Console > APIs & Services > Credentials > Regenerate Secret.\n"
        "       See data/coordination/secret_rotation_log.yaml for the rotation record."
    )
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Antigravity/1.18.3 Chrome/138.0.7204.235 Electron/37.3.1 Safari/537.36"
ENDPOINTS = [
    "https://cloudcode-pa.googleapis.com",
    "https://daily-cloudcode-pa.sandbox.googleapis.com",
    "https://autopush-cloudcode-pa.sandbox.googleapis.com",
]
OUTPUT_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/antigravity_stress_test_20260828.jsonl"


def refresh_token(refresh_t):
    body = {
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_t, "grant_type": "refresh_token",
    }
    data = urllib.parse.urlencode(body).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call(at, endpoint, project, model, prompt, max_tokens=8):
    body = {
        "project": project, "model": model,
        "request": {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0},
        },
        "userAgent": "antigravity", "requestId": f"stress-{int(time.time()*1000000)}",
    }
    url = f"{endpoint}/v1internal:generateContent"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {at}", "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "Client-Metadata": '{"ideType":"ANTIGRAVITY","platform":"MACOS","pluginType":"GEMINI"}',
        "X-Goog-Api-Client": "google-cloud-sdk vscode_cloudshelleditor/0.1",
    }, method="POST")
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            rdata = json.loads(resp.read().decode("utf-8"))
            elapsed_ms = (time.monotonic() - start) * 1000
            return {"ok": True, "elapsed_ms": elapsed_ms, "body": rdata}
    except urllib.error.HTTPError as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        err = e.read().decode("utf-8", errors="ignore")[:500]
        retry_delay = 0
        try:
            ed = json.loads(err).get("error", {}).get("details", [])
            for d in ed:
                if "retryDelay" in d:
                    retry_delay = float(d["retryDelay"].rstrip("s"))
                    break
        except Exception:
            pass
        return {"ok": False, "elapsed_ms": elapsed_ms, "status": e.code, "retry_delay": retry_delay, "err": err[:200]}
    except Exception as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return {"ok": False, "elapsed_ms": elapsed_ms, "err": str(e)[:200]}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    model = sys.argv[2] if len(sys.argv) > 2 else "tab_flash_lite_preview"
    endpoint_arg = sys.argv[3] if len(sys.argv) > 3 else "production"
    accounts = json.loads(ACCOUNTS_FILE.read_text())["accounts"]
    # Use account 4 (activeIndex) and project quixotic-valve-2mm91 (per prior R3 verification)
    acc = accounts[4]
    tokens = refresh_token(acc["refreshToken"])
    at = tokens["access_token"]
    projects = ["quixotic-valve-2mm91", "master-dominion-wk3xl", "involuted-column-3v1qp"]
    endpoint_map = {"production": ENDPOINTS[0], "daily": ENDPOINTS[1], "autopush": ENDPOINTS[2]}

    print(f"=== Antigravity Stress Test: {n} requests ===")
    print(f"Model: {model}")
    print(f"Endpoint: {endpoint_arg} ({endpoint_map.get(endpoint_arg, endpoint_arg)})")
    print(f"Account: {acc['email']}")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print()

    results = []
    for i in range(n):
        # Rotate across projects to stress multi-project path
        proj = projects[i % len(projects)]
        ep = endpoint_map.get(endpoint_arg, endpoint_arg)
        r = call(at, ep, proj, model, f"P{i % 100}", max_tokens=8)
        results.append({"i": i, "project": proj, **r})
        if (i+1) % 10 == 0 or not r["ok"]:
            elapsed = r.get("elapsed_ms", 0)
            ok_marker = "✅" if r["ok"] else f"❌ {r.get('status','?')}"
            print(f"  [{i+1:3d}/{n}] {ok_marker} {elapsed:6.0f}ms" + (f" retry={r.get('retry_delay',0):.0f}s" if not r["ok"] else ""))
        # Tiny delay to be polite
        time.sleep(0.05)

    # Compute stats
    ok_results = [r for r in results if r["ok"]]
    fail_results = [r for r in results if not r["ok"]]
    latencies = [r["elapsed_ms"] for r in ok_results]

    if latencies:
        latencies_sorted = sorted(latencies)
        p50_idx = len(latencies_sorted) // 2
        p90_idx = min(int(len(latencies_sorted) * 0.9), len(latencies_sorted) - 1)
        p99_idx = min(int(len(latencies_sorted) * 0.99), len(latencies_sorted) - 1)
        p50 = latencies_sorted[p50_idx]
        p90 = latencies_sorted[p90_idx]
        p99 = latencies_sorted[p99_idx]
        mean = statistics.mean(latencies)
        stdev = statistics.stdev(latencies) if len(latencies) > 1 else 0
        min_lat = min(latencies)
        max_lat = max(latencies)
    else:
        p50 = p90 = p99 = mean = stdev = min_lat = max_lat = 0

    print()
    print(f"=== Results: {len(ok_results)}/{n} OK ({len(ok_results)/n*100:.1f}%) ===")
    print(f"Latency (ms): p50={p50:.0f}  p90={p90:.0f}  p99={p99:.0f}  mean={mean:.0f}  stdev={stdev:.0f}  min={min_lat:.0f}  max={max_lat:.0f}")
    print(f"Total wall time: {sum(r.get('elapsed_ms',0) for r in results)/1000:.1f}s")
    if fail_results:
        print(f"Failures: {len(fail_results)}")
        # Categorize
        by_status: dict = {}
        for r in fail_results:
            s = r.get("status", "other")
            by_status.setdefault(s, []).append(r)
        for s, items in by_status.items():
            avg_retry = sum(r.get("retry_delay", 0) for r in items) / len(items) if items else 0
            print(f"  HTTP {s}: {len(items)}  avg_retry={avg_retry:.0f}s")

    # Save to file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model, "endpoint": endpoint_arg, "n": n,
        "success": len(ok_results), "failed": len(fail_results),
        "success_rate": len(ok_results) / n,
        "latency_ms": {
            "p50": round(p50), "p90": round(p90), "p99": round(p99),
            "mean": round(mean), "stdev": round(stdev),
            "min": round(min_lat), "max": round(max_lat),
        },
        "failures_by_status": {str(s): len(items) for s, items in (by_status.items() if fail_results else {})},
    }
    with OUTPUT_FILE.open("w") as f:
        f.write(json.dumps(summary) + "\n")
        for r in results:
            r_clean = {k: v for k, v in r.items() if k != "body"}
            if "body" in r and r.get("ok"):
                r_clean["response_text"] = (r.get("body", {}).get("response", r.get("body", {})).get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", ""))[:50]
            f.write(json.dumps(r_clean, ensure_ascii=False) + "\n")
    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
