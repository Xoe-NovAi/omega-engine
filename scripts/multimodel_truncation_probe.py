#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
multimodel_truncation_probe.py — Multi-model context-size probe (2026-08-28)

PURPOSE: Determine if the M3 398K→368.2K truncation is:
  (a) Model-specific (only M3)
  (b) Provider-specific (only OpenRouter free)
  (c) Client-specific (OpenCode CLI compaction — but we test this DIRECTLY)
  (d) Context-size-specific (all models at high context)

DESIGN: Bypass OpenCode entirely. Hit OpenRouter /api/v1/chat/completions
directly. This eliminates the client-side auto-compaction variable (Carmack's
finding). If a server returns success with a small response at high context,
the server is doing the truncation.

We test 5 models across the context sizes [10K, 50K, 100K, 200K, 300K, 400K, 500K]
and record per-call:
  - model, http_status, error, prompt_tokens, completion_tokens, total_tokens
  - finish_reason (truncation = "length"), content length
  - latency_ms
  - context_size_chars (what we sent)

Threshold = the smallest context size where ANY of:
  - http_status >= 400 (with error indicating context overflow)
  - finish_reason == "length" AND content_len << expected
  - completion_tokens < requested (server cut off)
  - response missing content entirely

OUTPUT: data/metrics/multimodel_truncation_probe_20260828.jsonl
PER-MODEL SUMMARY: data/metrics/multimodel_truncation_summary_20260828.json
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
import statistics
from datetime import datetime, timezone
from pathlib import Path

KEY_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/or-key.md"
OUT_JSONL = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/multimodel_truncation_probe_20260828.jsonl"
OUT_SUMMARY = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/multimodel_truncation_summary_20260828.json"

# Models to probe (all free tier via OpenRouter)
MODELS = [
    ("minimax/minimax-m3:free", "minimax_m3"),                            # the one we know
    ("thinkingmachines/inkling-small:free", "inkling_small"),             # 1M NEW model
    ("thinkingmachines/inkling:free", "inkling"),                          # 1M NEW model
    ("nvidia/nemotron-3.5-lightning:free", "nemotron35_lightning"),       # 1M (different from rate-limited 3-ultra)
    ("google/gemma-4-31b-it:free", "gemma4_31b"),                         # 262K (different context size class)
]

# Context sizes to test (in characters; ~4 chars/token)
# Start small to validate, then escalate to 1M to find true threshold.
CONTEXT_SIZES_CHARS = [10_000, 50_000, 100_000, 200_000, 300_000, 400_000, 500_000, 750_000, 1_000_000]

# Probe prompt that REQUIRES the model to reference content from the
# beginning of the context. If the model loses early context due to
# truncation, the answer will be wrong (controllable test).
PROBE_QUESTION = (
    "\n\n=== TASK ===\n"
    "What is the EXACT 16-character magic string at the very TOP of the document above?\n"
    "Reply with ONLY that 16-character string, nothing else."
)


def get_api_key():
    if not KEY_FILE.exists():
        raise SystemExit(f"FATAL: API key file {KEY_FILE} not found")
    return KEY_FILE.read_text().strip()


def make_context(target_chars):
    """Build a synthetic context of EXACTLY target_chars length.
    The first 16 chars are a unique magic string we can check for in the
    response — if the model lost them, the response is wrong."""
    magic = f"OPENME{int(time.time())%10000:04d}END"  # 16 chars
    magic = magic[:16].ljust(16)
    # pad with lorem ipsum to fill
    base = magic + "\n\n"
    chunk = (
        "The quick brown fox jumps over the lazy dog. "
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris "
        "nisi ut aliquip ex ea commodo consequat. "
    )
    pad = (target_chars - len(base) - len(PROBE_QUESTION)) * "x"
    return base + chunk + pad + PROBE_QUESTION, magic


def call_openrouter(api_key, model, context_str, max_output=64):
    """Direct OpenRouter call. No client-side compaction. Returns full response dict."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": context_str}],
        "max_tokens": max_output,
        "temperature": 0,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://xoe-nov.ai",
        "X-Title": "Omega-Engine Truncation Probe",
    }, method="POST")
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            elapsed_ms = (time.monotonic() - start) * 1000
            raw = resp.read().decode("utf-8", errors="ignore")
            return {
                "ok": True,
                "http_status": resp.status,
                "elapsed_ms": elapsed_ms,
                "raw": raw,
            }
    except urllib.error.HTTPError as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        body = e.read().decode("utf-8", errors="ignore")[:1000]
        return {
            "ok": False,
            "http_status": e.code,
            "elapsed_ms": elapsed_ms,
            "raw": body,
        }
    except Exception as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "ok": False,
            "http_status": 0,
            "elapsed_ms": elapsed_ms,
            "raw": f"EXCEPTION: {type(e).__name__}: {str(e)[:300]}",
        }


def parse_response(raw, expected_magic):
    """Extract: prompt_tokens, completion_tokens, total_tokens, finish_reason,
    content, content_correct (did the model recall the magic)."""
    result = {
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
        "finish_reason": None,
        "content": None,
        "content_len": 0,
        "content_correct": None,  # True/False/None if can't check
        "valid_json": False,
        "error_msg": None,
    }
    try:
        d = json.loads(raw)
        result["valid_json"] = True
        if "error" in d and "choices" not in d:
            result["error_msg"] = json.dumps(d.get("error"))[:300]
            return result
        usage = d.get("usage", {})
        result["prompt_tokens"] = usage.get("prompt_tokens")
        result["completion_tokens"] = usage.get("completion_tokens")
        result["total_tokens"] = usage.get("total_tokens")
        choices = d.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            content = msg.get("content", "") or ""
            result["content"] = content[:200]
            result["content_len"] = len(content)
            result["finish_reason"] = choices[0].get("finish_reason")
            # Check magic recall
            content_clean = content.replace("\n", "").replace(" ", "").strip()
            magic_clean = expected_magic.replace("\n", "").replace(" ", "").strip()
            if magic_clean in content_clean or content_clean in magic_clean:
                result["content_correct"] = True
            elif len(content_clean) > 0:
                result["content_correct"] = False
            else:
                result["content_correct"] = None
    except json.JSONDecodeError as e:
        result["error_msg"] = f"JSON decode error: {str(e)[:200]}"
    return result


def truncate_string(s, n):
    return s if len(s) <= n else s[:n] + f"...[truncated {len(s)-n} chars]"


def main():
    api_key = get_api_key()
    print(f"=== Multi-Model Truncation Probe | {datetime.now(timezone.utc).isoformat()} ===")
    print(f"Models: {len(MODELS)}, Context sizes: {CONTEXT_SIZES_CHARS}")
    print(f"Output: {OUT_JSONL}")
    print()

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    # truncate or append
    if OUT_JSONL.exists() and "--append" not in sys.argv:
        OUT_JSONL.unlink()
    out = open(OUT_JSONL, "a", buffering=1)  # line-buffered

    summary = {
        "probe": "multimodel_truncation_probe",
        "started": datetime.now(timezone.utc).isoformat(),
        "models": {},
        "context_sizes_chars": CONTEXT_SIZES_CHARS,
        "probe_question": PROBE_QUESTION,
        "key_health": "or_key.md (free tier)",
    }

    for model_id, label in MODELS:
        print(f"\n--- {label} ({model_id}) ---")
        model_results = []
        for ctx_chars in CONTEXT_SIZES_CHARS:
            ctx_str, magic = make_context(ctx_chars)
            print(f"  [{ctx_chars:>7,}c / ~{ctx_chars//4:>6,}tok] ", end="", flush=True)
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "model_id": model_id,
                "label": label,
                "context_size_chars": ctx_chars,
                "context_size_approx_tokens": ctx_chars // 4,
                "magic_at_top": magic,
            }
            resp = call_openrouter(api_key, model_id, ctx_str)
            parsed = parse_response(resp["raw"], magic)
            entry.update({
                "http_status": resp["http_status"],
                "elapsed_ms": round(resp["elapsed_ms"], 1),
                "ok": resp["ok"] and parsed["valid_json"] and parsed.get("error_msg") is None,
                **parsed,
            })
            # Compute truncation indicators
            ind = {
                "http_4xx_5xx": resp["http_status"] >= 400,
                "finish_length": parsed.get("finish_reason") == "length",
                "empty_content": parsed.get("content_len", 0) == 0 and resp["ok"],
                "missing_magic": parsed.get("content_correct") is False,
                "completion_capped": (parsed.get("completion_tokens") is not None
                                      and parsed.get("completion_tokens", 0) < 30
                                      and resp["ok"]
                                      and parsed.get("finish_reason") == "length"),
            }
            entry["truncation_indicators"] = ind
            entry["truncated"] = any(ind.values())
            # Print result
            if entry["ok"]:
                pt = entry.get("prompt_tokens") or "?"
                ct = entry.get("completion_tokens") or "?"
                ms = entry["elapsed_ms"]
                correct = "✓" if entry["content_correct"] is True else ("✗" if entry["content_correct"] is False else "?")
                if isinstance(ct, int) and ms > 0:
                    tps = f"{ct / (ms / 1000):.1f}"
                else:
                    tps = "?"
                print(f"HTTP {resp['http_status']} pt={pt} ct={ct} tps={tps} magic={correct} [{ms:.0f}ms]")
            else:
                print(f"HTTP {resp['http_status']} ERROR: {truncate_string(parsed.get('error_msg') or resp['raw'], 100)}")
            out.write(json.dumps(entry, ensure_ascii=False) + "\n")
            model_results.append(entry)
        summary["models"][label] = {
            "model_id": model_id,
            "results": [
                {
                    "context_chars": r["context_size_chars"],
                    "approx_tokens": r["context_size_approx_tokens"],
                    "http_status": r["http_status"],
                    "elapsed_ms": r["elapsed_ms"],
                    "prompt_tokens": r.get("prompt_tokens"),
                    "completion_tokens": r.get("completion_tokens"),
                    "finish_reason": r.get("finish_reason"),
                    "content_len": r.get("content_len"),
                    "content_correct": r.get("content_correct"),
                    "truncated": r.get("truncated"),
                    "truncation_indicators": r.get("truncation_indicators"),
                    "error_msg": r.get("error_msg"),
                }
                for r in model_results
            ],
        }
        # Determine truncation threshold for this model
        thresholds = []
        for r in model_results:
            if r.get("truncated"):
                thresholds.append(r["context_size_chars"])
        summary["models"][label]["first_truncation_at_chars"] = min(thresholds) if thresholds else None
        summary["models"][label]["max_successful_context_chars"] = max(
            (r["context_size_chars"] for r in model_results if not r.get("truncated")),
            default=None,
        )
    summary["ended"] = datetime.now(timezone.utc).isoformat()
    out.close()
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\n\n=== Summary written to {OUT_SUMMARY} ===")
    print(f"Raw rows: {OUT_JSONL}")


if __name__ == "__main__":
    main()
