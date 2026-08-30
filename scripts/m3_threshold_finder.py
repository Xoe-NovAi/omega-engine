#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
m3_threshold_finder.py — Find M3's actual context cliff

Hypothesis: M3 truncates input server-side to ~25K tokens regardless of what we send.
Test: Send 5K, 10K, 20K, 40K, 60K, 80K, 100K, 150K, 200K, 300K chars
      and plot the relationship between sent_chars and reported prompt_tokens.

Also: place magic at TOP of context (so model can ONLY find it if it sees the start).
"""
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

KEY_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/or-key.md"
OUT_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/m3_threshold_finder_20260828.jsonl"
MODEL = "minimax/minimax-m3:free"

# Test sizes in chars
SIZES = [5_000, 10_000, 20_000, 30_000, 40_000, 50_000, 60_000, 80_000, 100_000, 150_000]


def get_key():
    return KEY_FILE.read_text().strip()


def build_context(total_chars, magic):
    question = f"\n\nReply with ONLY this 16-char string: {magic}"
    overhead = len(magic) + len(question) + 2
    pad = max(0, total_chars - overhead) * "x"
    return magic + "\n" + pad + question


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
        "X-Title": "M3 Threshold Finder",
    }, method="POST")
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return {"ok": True, "status": resp.status, "elapsed_ms": (time.monotonic() - start) * 1000, "raw": resp.read().decode("utf-8", errors="ignore")}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "elapsed_ms": (time.monotonic() - start) * 1000, "raw": e.read().decode("utf-8", errors="ignore")[:500]}
    except Exception as e:
        return {"ok": False, "status": 0, "elapsed_ms": (time.monotonic() - start) * 1000, "raw": str(e)}


def main():
    key = get_key()
    print(f"=== M3 Threshold Finder | {datetime.now(timezone.utc).isoformat()} ===")
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if OUT_FILE.exists() and "--append" not in sys.argv:
        OUT_FILE.unlink()
    out = open(OUT_FILE, "a", buffering=1)
    print(f"{'Size(c)':>9} {'Sent(k)':>7} {'Pt':>6} {'Ratio':>6} {'Correct':>7} {'Magic':<20} {'Content':<30}")
    for sz in SIZES:
        magic = f"M3SZ{sz:06d}T{int(time.time())%1000:03d}"
        magic = magic[:16].ljust(16)
        ctx = build_context(sz, magic)
        actual_chars = len(ctx)
        resp = call(key, ctx, max_out=20)
        parsed = {}
        try:
            d = json.loads(resp["raw"])
            usage = d.get("usage", {})
            parsed = {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
            }
            choices = d.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                content = msg.get("content", "") or ""
                parsed["content"] = content[:50]
                parsed["finish_reason"] = choices[0].get("finish_reason")
                parsed["magic_correct"] = magic.strip() in content.strip()
        except json.JSONDecodeError:
            parsed["error"] = "JSON decode"
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "target_chars": sz,
            "actual_chars": actual_chars,
            "magic": magic,
            "http_status": resp["status"],
            "elapsed_ms": round(resp["elapsed_ms"], 1),
            **parsed,
        }
        out.write(json.dumps(entry) + "\n")
        pt = parsed.get("prompt_tokens") or 0
        ratio = pt / max(1, actual_chars / 4) if pt else 0
        sym = "✓" if parsed.get("magic_correct") else ("✗" if "magic_correct" in parsed else "?")
        cont = parsed.get("content", "?")[:30]
        print(f"{sz:>9,} {actual_chars/1000:>6.1f}k {pt:>6} {ratio:>5.2f} {sym:>7} {magic[:16]!r:<20} {cont!r:<30}")
    out.close()
    print(f"\nWrote: {OUT_FILE}")


if __name__ == "__main__":
    main()
