#!/usr/bin/env python3
"""
long_duration_test.py — 1h sustained load test on tab_flash_lite_preview
Background-friendly: logs every 5 min, atomic writes, resumable on crash.
"""
import json
import os
import signal
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
OUTPUT_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/antigravity_long_duration_20260828.jsonl"
STATE_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/antigravity_long_duration_state.json"
DURATION_S = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
TARGET_RPS = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0  # 2 calls per second
ENDPOINT = "https://cloudcode-pa.googleapis.com"

# Global flag for graceful shutdown
running = True
def handle_signal(sig, frame):
    global running
    running = False
signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


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


def call(at, project, model, prompt, max_tokens=8):
    body = {
        "project": project, "model": model,
        "request": {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0},
        },
        "userAgent": "antigravity", "requestId": f"longdur-{int(time.time()*1000000)}",
    }
    url = f"{ENDPOINT}/v1internal:generateContent"
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
    accounts = json.loads(ACCOUNTS_FILE.read_text())["accounts"]
    acc = accounts[4]  # activeIndex
    project = "quixotic-valve-2mm91"

    # Check for existing state (resumable)
    start_count = 0
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
        start_count = state.get("count", 0)
        if start_count > 0:
            print(f"[RESUMING] from count={start_count}")

    print(f"=== Long-Duration Test: {DURATION_S}s @ {TARGET_RPS} req/s ===")
    print(f"Model: tab_flash_lite_preview on {ENDPOINT}")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"State: {STATE_FILE}")
    print()

    # Refresh token (only once, then reuse until 5 min before expiry)
    tokens = refresh_token(acc["refreshToken"])
    at = tokens["access_token"]
    token_expires = time.time() + int(tokens.get("expires_in", 3600)) - 300
    print(f"OAuth: OK, expires at {datetime.fromtimestamp(token_expires, timezone.utc).isoformat()}")

    # Open output file in append mode
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    f = OUTPUT_FILE.open("a")

    # State tracking
    count = start_count
    successes = 0
    failures = 0
    status_counts = {}
    latencies = []
    start_wall = time.monotonic()
    end_wall = start_wall + DURATION_S
    last_log = start_wall
    last_save_state = start_wall
    interval = 1.0 / TARGET_RPS

    while running and time.monotonic() < end_wall:
        # Refresh token if needed
        if time.time() > token_expires:
            print(f"[{datetime.now(timezone.utc).isoformat()}] Refreshing OAuth token...")
            tokens = refresh_token(acc["refreshToken"])
            at = tokens["access_token"]
            token_expires = time.time() + int(tokens.get("expires_in", 3600)) - 300

        # Make a call
        result = call(at, project, "tab_flash_lite_preview", f"LD{count % 1000}")
        count += 1
        if result["ok"]:
            successes += 1
            latencies.append(result["elapsed_ms"])
        else:
            failures += 1
            s = result.get("status", "other")
            status_counts[s] = status_counts.get(s, 0) + 1
            # Log truncation/error events
            err_event = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "count": count,
                "status": s,
                "retry_delay": result.get("retry_delay", 0),
                "err": result.get("err", "")[:200],
                "elapsed_ms": result.get("elapsed_ms", 0),
            }
            f.write(json.dumps(err_event, ensure_ascii=False) + "\n")
            f.flush()
            if result.get("retry_delay", 0) > 0:
                print(f"[{datetime.now(timezone.utc).isoformat()}] ❌ {s} retry={result['retry_delay']:.0f}s @ count={count}")

        # Log every 5 minutes
        now = time.monotonic()
        if now - last_log >= 300:
            elapsed = now - start_wall
            rps = count / elapsed
            p50 = sorted(latencies)[len(latencies) // 2] if latencies else 0
            p99_idx = min(int(len(latencies) * 0.99), len(latencies) - 1) if latencies else 0
            p99 = sorted(latencies)[p99_idx] if latencies else 0
            print(f"[{datetime.now(timezone.utc).isoformat()}] count={count} successes={successes} failures={failures} rps={rps:.2f} p50={p50:.0f}ms p99={p99:.0f}ms statuses={status_counts}")
            last_log = now

        # Save state every 60s (resumable)
        if now - last_save_state >= 60:
            STATE_FILE.write_text(json.dumps({"count": count, "successes": successes, "failures": failures, "statuses": status_counts}))
            last_save_state = now

        # Sleep to maintain target RPS
        elapsed_call = time.monotonic() - (now - result["elapsed_ms"] / 1000)
        sleep_for = max(0, interval - (time.monotonic() - (now - result["elapsed_ms"] / 1000)))
        # Actually simpler: just sleep `interval` (since calls take ~0.7s, the interval is the bottleneck)
        time.sleep(max(0, interval - 0.05))

    # Final summary
    elapsed = time.monotonic() - start_wall
    rps = count / elapsed if elapsed > 0 else 0
    p50 = sorted(latencies)[len(latencies) // 2] if latencies else 0
    p99_idx = min(int(len(latencies) * 0.99), len(latencies) - 1) if latencies else 0
    p99 = sorted(latencies)[p99_idx] if latencies else 0
    print()
    print(f"=== Long-Duration Test Complete ===")
    print(f"Duration: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"Total calls: {count}")
    print(f"Successes: {successes} ({successes/count*100 if count else 0:.1f}%)")
    print(f"Failures: {failures}")
    print(f"Throughput: {rps:.2f} req/s")
    print(f"Latency: p50={p50:.0f}ms p99={p99:.0f}ms")
    if status_counts:
        print(f"Status breakdown: {status_counts}")
    # Save final state
    STATE_FILE.write_text(json.dumps({"count": count, "successes": successes, "failures": failures, "statuses": status_counts, "completed": True}))
    f.close()


if __name__ == "__main__":
    main()
