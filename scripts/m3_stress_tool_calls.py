#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
M3 Stress Test 2 — Tool Call Volume: 30+ tool calls in a single turn
AP: AP-M3-STRESS-TOOL-CALLS-v1.0.0
Author: Grokster (cline specialist, ses_fe8cf0b39ffeL3L8eaMEj3CW9H)
Date: 2026-08-28
Mandates: M8, M23 (log all tool drops), M26, M27

WHAT THIS TESTS
===============
Single M3 request asking it to make 30+ tool calls.
M3 supports tool_use (per model_registry). This test:
- Asks M3 to emit 30 tool calls in one turn
- Counts actual tool calls in the response
- Counts dropped/skipped tool calls
- Detects any completion_tokens vs request mismatch
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import List

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "minimax/minimax-m3:free"

# A tool definition for M3 to use
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current time in a timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "description": "IANA timezone"}
                },
                "required": ["timezone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression"}
                },
                "required": ["expression"]
            }
        }
    },
]


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


def call_m3(messages, tools=None, max_tokens=4096, timeout=90):
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.0,  # deterministic
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {get_api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://omega-engine.local/stress-test",
            "X-Title": "M3-Stress-Tool-Calls",
        },
    )
    t0 = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        latency = int((time.time() - t0) * 1000)
        body = json.loads(resp.read())
        return {"ok": True, "status": resp.status, "latency_ms": latency, "body": body}
    except urllib.error.HTTPError as e:
        latency = int((time.time() - t0) * 1000)
        return {"ok": False, "status": e.code, "latency_ms": latency, "error": e.read()[:200].decode()}
    except Exception as e:
        latency = int((time.time() - t0) * 1000)
        return {"ok": False, "status": 0, "latency_ms": latency, "error": str(e)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--tool-calls-requested", type=int, default=30)
    p.add_argument("--max-tokens", type=int, default=4096)
    p.add_argument("--output", default="data/metrics/m3_tool_calls_20260828.json")
    args = p.parse_args()

    print(f"=== M3 TOOL-CALL STRESS: requesting {args.tool_calls_requested} calls, max_tokens={args.max_tokens} ===")
    # Build a request that strongly elicits multiple tool calls
    sysprompt = (
        "You are a research coordinator. When asked to gather data, you MUST use the available tools. "
        "Make MANY parallel tool calls — at least 30 distinct calls in a single response. "
        "For weather: query 10 different cities. For time: query 10 timezones. For calculate: run 10 expressions."
    )
    userprompt = (
        f"Gather data for 10 cities (use get_weather), 10 timezones (use get_time), "
        f"and 10 math expressions (use calculate). Make all {args.tool_calls_requested} tool calls "
        "in a SINGLE response — don't summarize first, just call them."
    )
    messages = [
        {"role": "system", "content": sysprompt},
        {"role": "user", "content": userprompt},
    ]
    result = call_m3(messages, tools=TOOLS, max_tokens=args.max_tokens)
    if not result["ok"]:
        print(f"❌ FAIL: status={result['status']} error={result.get('error','')[:200]}")
        return 1
    body = result["body"]
    choice = body.get("choices", [{}])[0]
    msg = choice.get("message", {})
    finish = choice.get("finish_reason")
    tool_calls = msg.get("tool_calls") or []
    content = msg.get("content") or ""
    usage = body.get("usage", {})
    # M23: classify the result
    tool_count = len(tool_calls)
    truncated = (finish == "length") or (tool_count < args.tool_calls_requested)
    dropped = max(0, args.tool_calls_requested - tool_count)
    print(f"\n--- RESULT ---")
    print(f"  http={result['status']}  latency={result['latency_ms']}ms")
    print(f"  finish_reason={finish}")
    print(f"  completion_tokens={usage.get('completion_tokens',0)}")
    print(f"  prompt_tokens={usage.get('prompt_tokens',0)}")
    print(f"  tool_calls_emitted={tool_count}")
    print(f"  tool_calls_requested={args.tool_calls_requested}")
    print(f"  DROPPED={dropped} ({dropped/args.tool_calls_requested*100:.1f}%)")
    if truncated:
        print(f"  ⚠️  M23 TRUNCATION: finish_reason={finish}, tool_count < requested")
    # Per-tool breakdown
    tool_names: dict = {}
    for tc in tool_calls:
        fn = tc.get("function", {}).get("name", "?")
        tool_names[fn] = tool_names.get(fn, 0) + 1
    if tool_names:
        print(f"  per-tool breakdown: {tool_names}")
    # Show first 3 tool call signatures
    print(f"\n  first 3 tool calls:")
    for tc in tool_calls[:3]:
        fn = tc.get("function", {}).get("name", "?")
        args_str = tc.get("function", {}).get("arguments", "")[:80]
        print(f"    {fn}({args_str})")
    # Save
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "tool_calls_requested": args.tool_calls_requested,
        "tool_calls_emitted": tool_count,
        "dropped": dropped,
        "truncated": truncated,
        "finish_reason": finish,
        "completion_tokens": usage.get("completion_tokens"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "latency_ms": result["latency_ms"],
        "per_tool": tool_names,
        "first_three": [{"name": tc.get("function",{}).get("name"),
                         "args": tc.get("function",{}).get("arguments","")[:200]}
                        for tc in tool_calls[:3]],
    }, indent=2))
    print(f"\n  saved → {out_path}")
    if dropped > 0 or truncated:
        print(f"\nM23 ALERT: M3 dropped {dropped}/{args.tool_calls_requested} tool calls")
    return 0


if __name__ == "__main__":
    sys.exit(main())
