#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
m3_context_limit_finder.py — Pinpoint M3's actual context limit

Hypothesis from probe 1: M3 returns prompt_tokens=94,007 when we sent 750K chars.
This means M3's effective context is ~94K tokens, not 1M. Confirm by sending
just-over and just-under that threshold.

Also: test what happens when we send EXACTLY the reported number of tokens.
"""
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

KEY_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/or-key.md"
OUT_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/m3_context_limit_finder_20260828.jsonl"
MODEL = "minimax/minimax-m3:free"


def get_key():
    return KEY_FILE.read_text().strip()


def make_context_with_marker(target_chars, magic):
    """Build context: magic + lorem padding. Magic at TOP."""
    base = magic + "\n\n"
    pad = max(0, target_chars - len(base) - 100) * "x"
    question = "\n\nReply with ONLY the 16-char string at the top of the document above. Nothing else."
    return base + pad + question


def call(key, content, max_out=16):
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
        "X-Title": "M3 Context Limit Finder",
    }, method="POST")
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            elapsed = (time.monotonic() - start) * 1000
            return {"ok": True, "status": resp.status, "elapsed_ms": elapsed, "raw": resp.read().decode("utf-8", errors="ignore")}
    except urllib.error.HTTPError as e:
        elapsed = (time.monotonic() - start) * 1000
        return {"ok": False, "status": e.code, "elapsed_ms": elapsed, "raw": e.read().decode("utf-8", errors="ignore")[:500]}
    except Exception as e:
        return {"ok": False, "status": 0, "elapsed_ms": (time.monotonic() - start) * 1000, "raw": str(e)}


def main():
    key = get_key()
    # From probe 1: at 750K chars (187.5K expected tokens) → server reported 94,007 tokens
    # Test 60K, 70K, 80K, 90K, 100K, 110K, 120K, 130K, 140K (in tokens) to find the cliff
    targets_chars = [c * 1000 for c in [60, 70, 80, 90, 95, 100, 110, 120, 130, 150, 200, 250, 300, 400]]
    print(f"=== M3 Context Limit Finder | {datetime.now(timezone.utc).isoformat()} ===")
    print(f"Model: {MODEL}")
    print(f"Testing chars: {targets_chars}")
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if OUT_FILE.exists() and "--append" not in sys.argv:
        OUT_FILE.unlink()
    out = open(OUT_FILE, "a", buffering=1)
    for tc in targets_chars:
        magic = f"OPENM3{int(time.time())%100000:05d}END"[:16].ljust(16)
        ctx = make_context_with_marker(tc, magic)
        # count actual chars sent
        actual_chars = len(ctx)
        resp = call(key, ctx, max_out=16)
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
                parsed["content"] = content[:80]
                parsed["content_len"] = len(content)
                parsed["finish_reason"] = choices[0].get("finish_reason")
                # magic check
                if magic in content.replace("\n", "").replace(" ", ""):
                    parsed["magic_correct"] = True
                elif content.strip():
                    parsed["magic_correct"] = False
                else:
                    parsed["magic_correct"] = None
        except json.JSONDecodeError:
            parsed["error"] = "JSON decode error"
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "target_chars": tc,
            "actual_chars": actual_chars,
            "magic": magic,
            "http_status": resp["status"],
            "elapsed_ms": round(resp["elapsed_ms"], 1),
            **parsed,
        }
        out.write(json.dumps(entry) + "\n")
        ok = parsed.get("magic_correct")
        sym = "✓" if ok is True else ("✗" if ok is False else "?")
        print(f"  [{tc:>7,}c] HTTP {resp['status']} pt={parsed.get('prompt_tokens','?')} ct={parsed.get('completion_tokens','?')} finish={parsed.get('finish_reason','?')} magic={sym} content={parsed.get('content','?')!r} [{resp['elapsed_ms']:.0f}ms]")
    out.close()
    print(f"\nWrote: {OUT_FILE}")


if __name__ == "__main__":
    main()
