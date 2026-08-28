#!/usr/bin/env python3
"""
stress_test_burst.py — Burst test (no delay) to find rate limit threshold
"""
import asyncio
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

# Identical to stress_test_internal.py but uses asyncio + httpx to run N parallel
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
OUTPUT_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/antigravity_burst_test_20260828.jsonl"


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


def call_blocking(at, endpoint, project, model, prompt, max_tokens=8):
    body = {
        "project": project, "model": model,
        "request": {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0},
        },
        "userAgent": "antigravity", "requestId": f"burst-{int(time.time()*1000000)}",
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
        return {"ok": False, "elapsed_ms": elapsed_ms, "status": e.code, "retry_delay": retry_delay}
    except Exception as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return {"ok": False, "elapsed_ms": elapsed_ms, "err": str(e)[:200]}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    concurrency = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    model = sys.argv[3] if len(sys.argv) > 3 else "tab_flash_lite_preview"
    endpoint_arg = sys.argv[4] if len(sys.argv) > 4 else "production"

    accounts = json.loads(ACCOUNTS_FILE.read_text())["accounts"]
    acc = accounts[4]
    tokens = refresh_token(acc["refreshToken"])
    at = tokens["access_token"]
    projects = ["quixotic-valve-2mm91", "master-dominion-wk3xl", "involuted-column-3v1qp"]
    endpoint_map = {"production": ENDPOINTS[0], "daily": ENDPOINTS[1], "autopush": ENDPOINTS[2]}

    print(f"=== Antigravity BURST Test: {n} requests, concurrency={concurrency} ===")
    print(f"Model: {model}")
    print(f"Endpoint: {endpoint_arg}")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print()

    # Use ThreadPoolExecutor for concurrency
    from concurrent.futures import ThreadPoolExecutor, as_completed
    results = []
    start_wall = time.monotonic()

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = []
        for i in range(n):
            proj = projects[i % len(projects)]
            ep = endpoint_map.get(endpoint_arg, endpoint_arg)
            futures.append(ex.submit(call_blocking, at, ep, proj, model, f"B{i % 1000}"))
        for i, f in enumerate(as_completed(futures)):
            r = f.result()
            r["i"] = i
            results.append(r)
            if (i+1) % 5 == 0 or not r["ok"]:
                elapsed = r.get("elapsed_ms", 0)
                ok_marker = "✅" if r["ok"] else f"❌ {r.get('status','?')}"
                retry = f" retry={r.get('retry_delay',0):.0f}s" if not r["ok"] else ""
                print(f"  [{i+1:3d}/{n}] {ok_marker} {elapsed:6.0f}ms{retry}")

    wall_time = time.monotonic() - start_wall
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
    print(f"Wall time: {wall_time:.1f}s ({n/wall_time:.2f} req/s sustained)")
    print(f"Latency (ms): p50={p50:.0f}  p90={p90:.0f}  p99={p99:.0f}  mean={mean:.0f}  stdev={stdev:.0f}  min={min_lat:.0f}  max={max_lat:.0f}")
    if fail_results:
        by_status: dict = {}
        for r in fail_results:
            s = r.get("status", "other")
            by_status.setdefault(s, []).append(r)
        for s, items in by_status.items():
            avg_retry = sum(r.get("retry_delay", 0) for r in items) / len(items) if items else 0
            print(f"  HTTP {s}: {len(items)}  avg_retry={avg_retry:.0f}s")

    # Save
    summary = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model, "endpoint": endpoint_arg, "n": n, "concurrency": concurrency,
        "wall_time_s": round(wall_time, 1), "throughput_rps": round(n / wall_time, 2),
        "success": len(ok_results), "failed": len(fail_results),
        "success_rate": len(ok_results) / n,
        "latency_ms": {
            "p50": round(p50), "p90": round(p90), "p99": round(p99),
            "mean": round(mean), "stdev": round(stdev),
            "min": round(min_lat), "max": round(max_lat),
        },
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w") as f:
        f.write(json.dumps(summary) + "\n")
        for r in sorted(results, key=lambda x: x.get("i", 0)):
            r_clean = {k: v for k, v in r.items() if k != "body"}
            f.write(json.dumps(r_clean, ensure_ascii=False) + "\n")
    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
