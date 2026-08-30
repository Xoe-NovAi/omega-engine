#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
m3_truncation_diagnostic.py — Disambiguate the truncation pattern

Two questions:
Q1: Where in the context is the magic when we send 200K chars and get 50K tokens back?
Q2: Does M3 see the WHOLE context, or only a portion?

Test design:
- Magic placed at different positions: [0, 25%, 50%, 75%, 100%]
- All requests send 200,000 chars
- Question ALWAYS at the end: "what's the magic?"
- If model gets full context: all correct
- If model gets first half: position 0/25% correct, 50/75/100% wrong
- If model gets last half: position 50/75/100% correct, 0/25% wrong
- If model gets middle 50%: position 25/50/75% correct
"""
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

KEY_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/or-key.md"
OUT_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/m3_truncation_diagnostic_20260828.jsonl"
MODEL = "minimax/minimax-m3:free"

# Test 200K chars, 5 magic positions, 3 trials each = 15 calls
TOTAL_CHARS = 200_000
N_TRIALS = 3


def get_key():
    return KEY_FILE.read_text().strip()


def build_context(total_chars, magic, position_pct):
    """Place magic at position_pct% of the context (0=top, 100=just before question)."""
    question = "\n\nReply with ONLY the 16-char string at the position I told you. Nothing else. Position was: " + str(position_pct)
    overhead = len(magic) + len(question) + 4  # 4 for newlines
    fill_chars = total_chars - overhead
    if fill_chars < 0:
        raise ValueError("total_chars too small")
    # split fill into two parts: before-magic and after-magic
    split_at = int(fill_chars * position_pct / 100)
    pre = "x" * split_at
    post = "x" * (fill_chars - split_at)
    return f"{magic}\n{pre}\n{post}{question}"


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
        "X-Title": "M3 Truncation Diagnostic",
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
    print(f"=== M3 Truncation Diagnostic | {datetime.now(timezone.utc).isoformat()} ===")
    print(f"Total chars: {TOTAL_CHARS}, positions: [0, 25, 50, 75, 100], trials: {N_TRIALS}")
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if OUT_FILE.exists() and "--append" not in sys.argv:
        OUT_FILE.unlink()
    out = open(OUT_FILE, "a", buffering=1)
    positions = [0, 25, 50, 75, 100]
    results = {}
    for pos in positions:
        results[pos] = []
        for trial in range(N_TRIALS):
            magic = f"M3POS{pos}T{trial}TIME{int(time.time())%10000:04d}"
            magic = magic[:16].ljust(16)
            ctx = build_context(TOTAL_CHARS, magic, pos)
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
                "position_pct": pos,
                "trial": trial,
                "magic": magic,
                "actual_chars": actual_chars,
                "http_status": resp["status"],
                "elapsed_ms": round(resp["elapsed_ms"], 1),
                **parsed,
            }
            out.write(json.dumps(entry) + "\n")
            results[pos].append(entry)
            sym = "✓" if parsed.get("magic_correct") else ("✗" if "magic_correct" in parsed else "?")
            print(f"  pos={pos:>3}% trial={trial} magic={sym} pt={parsed.get('prompt_tokens','?')} ct={parsed.get('completion_tokens','?')} content={parsed.get('content','?')!r} ms={resp['elapsed_ms']:.0f}")
    out.close()
    # Summary
    print("\n=== Summary ===")
    print("Position   | correct/trials | behavior")
    for pos in positions:
        correct = sum(1 for r in results[pos] if r.get("magic_correct"))
        print(f"  {pos:>3}%     |     {correct}/{N_TRIALS}      | {['NEVER','RARELY','SOMETIMES','OFTEN','ALWAYS'][correct]}")
    print(f"\nWrote: {OUT_FILE}")


if __name__ == "__main__":
    main()
