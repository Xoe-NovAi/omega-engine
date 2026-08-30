#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
m3_throughput_verify.py — Honest throughput measurement at 3M char input

Distinguishes:
  - input_chars_per_sec  = input_chars / elapsed_s  (what the previous report called "throughput")
  - output_tokens_per_sec = completion_tokens / elapsed_s  (TRUE generation throughput)
  - total_tokens_per_sec  = (prompt + completion) / elapsed_s

Also: tests smaller sizes (1K, 100K, 1M) for comparison and reproducibility.
"""
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

KEY_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/or-key.md"
OUT_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/m3_throughput_verify_20260828.jsonl"
MODEL = "minimax/minimax-m3:free"

# Sizes to test — reproduce the 3M claim, plus control points
SIZES = [1_000, 100_000, 1_000_000, 3_000_000]


def get_key():
    return KEY_FILE.read_text().strip()


def build_context(total_chars):
    question = "\n\nReply with the single word: OK"
    overhead = len(question) + 2
    pad = max(0, total_chars - overhead) * "x"
    return pad + question


def call(key, content, max_out=20):
    url = "https://openrouter.ai/api/v1/chat/completions"
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_out,
        "temperature": 0,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://xoe-nov.ai",
        "X-Title": "M3 Throughput Verify",
    }, method="POST")
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            elapsed = (time.monotonic() - start) * 1000
            return {"ok": True, "status": resp.status, "elapsed_ms": elapsed, "raw": resp.read().decode("utf-8", errors="ignore")}
    except urllib.error.HTTPError as e:
        elapsed = (time.monotonic() - start) * 1000
        return {"ok": False, "status": e.code, "elapsed_ms": elapsed, "raw": e.read().decode("utf-8", errors="ignore")[:500]}
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        return {"ok": False, "status": 0, "elapsed_ms": elapsed, "raw": str(e)}


def main():
    key = get_key()
    print(f"=== M3 Throughput Verify (HONEST) | {datetime.now(timezone.utc).isoformat()} ===")
    print(f"Model: {MODEL}")
    print(f"Sizes: {SIZES}")
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if OUT_FILE.exists() and "--append" not in sys.argv:
        OUT_FILE.unlink()
    out = open(OUT_FILE, "a", buffering=1)
    print(f"\n{'Size(c)':>10} {'Sent(k)':>8} {'Pt':>8} {'Ct':>5} {'Latency(s)':>11} {'in_c/s':>12} {'out_tok/s':>11} {'tot_tok/s':>11} {'HTTP':>5} {'finish':>8}")
    print("-" * 110)
    for sz in SIZES:
        ctx = build_context(sz)
        actual_chars = len(ctx)
        resp = call(key, ctx, max_out=20)
        parsed = {}
        try:
            d = json.loads(resp["raw"])
            usage = d.get("usage", {})
            parsed = {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
            }
            choices = d.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                content = msg.get("content", "") or ""
                parsed["content"] = content[:60]
                parsed["finish_reason"] = choices[0].get("finish_reason")
        except json.JSONDecodeError:
            parsed["error"] = "JSON decode"
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "target_chars": sz,
            "actual_chars": actual_chars,
            "http_status": resp["status"],
            "elapsed_ms": round(resp["elapsed_ms"], 1),
            **parsed,
        }
        out.write(json.dumps(entry) + "\n")
        elapsed_s = resp["elapsed_ms"] / 1000.0
        pt = parsed.get("prompt_tokens") or 0
        ct = parsed.get("completion_tokens") or 0
        in_cps = actual_chars / elapsed_s if elapsed_s > 0 else 0
        out_tps = ct / elapsed_s if elapsed_s > 0 else 0
        tot_tps = (pt + ct) / elapsed_s if elapsed_s > 0 else 0
        finish = parsed.get("finish_reason", "?")
        print(f"{sz:>10,} {actual_chars/1000:>7.1f}k {pt:>8,} {ct:>5} {elapsed_s:>11.2f} {in_cps:>12,.0f} {out_tps:>11.2f} {tot_tps:>11.0f} {resp['status']:>5} {finish:>8}")
    out.close()
    print(f"\nWrote: {OUT_FILE}")
    print("\nLEGEND:")
    print("  in_c/s    = input chars per second of wall-clock latency  (what the old report called 'throughput')")
    print("  out_tok/s = output tokens per second  (TRUE generation speed)")
    print("  tot_tok/s = (prompt + completion) tokens per second  (effective token throughput)")


if __name__ == "__main__":
    main()
