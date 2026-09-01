#!/usr/bin/env python3
"""
test_lfm_vs_qwen.py — Empirical comparison: LFM2.5-2.6B vs Qwen3-1.7B
=============================================================================
Runs the same prompt suite against both models and reports:
- Tokens/second (load time + per-prompt)
- Memory footprint
- Output quality (simple heuristic)
- Success rate

Designed for the Architect's 16GB system: loads ONE model at a time.
Default: LFM2.5-2.6B on port 1234. To test Qwen3-1.7B, set --model qwen
(which would also require starting it on port 1236 separately).

Usage:
  # Test LFM only (default, on port 1234)
  python3 scripts/test_lfm_vs_qwen.py

  # Test with custom model on different port
  python3 scripts/test_lfm_vs_qwen.py --model qwen --port 1236

  # Compare both (loads Qwen, runs tests, then loads LFM, runs tests)
  python3 scripts/test_lfm_vs_qwen.py --compare

AP Token: AP-TEST-LFM-QWEN-20260901-v1.0.0
Author: Grokster per Architect directive
"""
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ─── Configuration ───────────────────────────────────────────────────────────
DEFAULT_MODEL = "lfm"  # "lfm" or "qwen"
DEFAULT_PORT = 1234   # LFM is on 1234 (port 1236 for Qwen if separate)
DEFAULT_HOST = "127.0.0.1"
PROMPT_SUITE_PATH = Path("data/coordination/TEST_PROMPTS_LFM_VS_QWEN.json")
RESULTS_PATH = Path("data/metrics/lfm_vs_qwen_results.json")

# Test prompts (fallback if file not found)
FALLBACK_PROMPTS = [
    {
        "name": "extraction_simple",
        "category": "extraction",
        "prompt": "Extract the names of all people mentioned in this text: 'Alice and Bob went to the store. They met Charlie there. Later, Diana joined them for coffee.'",
        "expected_keywords": ["Alice", "Bob", "Charlie", "Diana"],
    },
    {
        "name": "tool_call_basic",
        "category": "tool_use",
        "prompt": "If a user asks 'What's the weather in Paris?', what tool would you call? Respond with just the tool name and parameters in JSON format.",
        "expected_keywords": ["weather", "Paris", "tool"],
    },
    {
        "name": "reasoning_simple",
        "category": "reasoning",
        "prompt": "If all roses are flowers, and some flowers fade quickly, can we conclude that some roses fade quickly? Answer yes or no with one sentence explanation.",
        "expected_keywords": ["no", "some"],
    },
    {
        "name": "code_simple",
        "category": "code",
        "prompt": "Write a Python function that takes a list of integers and returns the sum of all even numbers. Just the function, no explanation.",
        "expected_keywords": ["def", "even", "sum", "return"],
    },
    {
        "name": "instruction_following",
        "category": "instruction_following",
        "prompt": "List exactly 3 fruits. Number them 1, 2, 3. No other text.",
        "expected_keywords": ["1", "2", "3"],
    },
    {
        "name": "summarization",
        "category": "extraction",
        "prompt": "Summarize in one sentence: 'The 2026 market saw a 12% increase in tech stocks driven by AI optimism, while traditional energy declined 3%. Analysts predict continued volatility through Q3.'",
        "expected_keywords": ["tech", "AI", "energy"],
    },
    {
        "name": "agentic_decision",
        "category": "tool_use",
        "prompt": "You are an agent. The user asks: 'Find me a 3-bedroom apartment in Boston under $3000/month.' What is your FIRST action? Respond with one sentence.",
        "expected_keywords": ["search", "filter", "Boston", "apartment"],
    },
    {
        "name": "math_simple",
        "category": "reasoning",
        "prompt": "What is 17 * 23? Show your work in one line, then state the answer.",
        "expected_keywords": ["391", "17", "23"],
    },
]


@dataclass
class TestResult:
    prompt_name: str
    category: str
    model: str
    success: bool
    latency_ms: float
    tokens_in: int
    tokens_out: int
    tokens_per_sec: float
    output: str
    keywords_found: list[str] = field(default_factory=list)
    keywords_missing: list[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class ModelStats:
    name: str
    port: int
    total_tests: int
    successful_tests: int
    avg_tokens_per_sec: float
    avg_latency_ms: float
    total_tokens_in: int
    total_tokens_out: int
    memory_mb: int
    results: list[TestResult] = field(default_factory=list)


def load_prompts() -> list[dict]:
    """Load test prompts from file or fall back to defaults."""
    if PROMPT_SUITE_PATH.exists():
        try:
            with open(PROMPT_SUITE_PATH) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[WARN] Could not load {PROMPT_SUITE_PATH}: {e}")
            print("[INFO] Using fallback prompt suite")
    return FALLBACK_PROMPTS


def get_memory_usage(port: int) -> int:
    """Get RSS memory in MB for the llama-cpp process on the given port."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", f"python3 -m llama_cpp.server.*--port {port}"],
            capture_output=True, text=True, timeout=5,
        )
        pids = result.stdout.strip().split()
        if not pids:
            return 0
        total = 0
        for pid in pids:
            try:
                with open(f"/proc/{pid}/status") as f:
                    for line in f:
                        if line.startswith("VmRSS:"):
                            total += int(line.split()[1]) // 1024
                            break
            except (OSError, ValueError):
                pass
        return total
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 0


def check_server(host: str, port: int) -> bool:
    """Check if the llama-cpp server is reachable."""
    import urllib.request
    import urllib.error
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/v1/models", timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError, TimeoutError):
        return False


def run_prompt(
    host: str,
    port: int,
    model_name: str,
    prompt_data: dict,
    max_tokens: int = 256,
    temperature: float = 0.1,
) -> TestResult:
    """Send a prompt to the local llama-cpp server and measure the result."""
    import urllib.request
    import urllib.error

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt_data["prompt"]}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    result = TestResult(
        prompt_name=prompt_data["name"],
        category=prompt_data["category"],
        model=model_name,
        success=False,
        latency_ms=0.0,
        tokens_in=0,
        tokens_out=0,
        tokens_per_sec=0.0,
        output="",
    )

    req = urllib.request.Request(
        f"http://{host}:{port}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = (time.perf_counter() - start) * 1000
            result.latency_ms = elapsed

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            result.output = message.get("content", "").strip()
            usage = data.get("usage", {})
            result.tokens_in = usage.get("prompt_tokens", 0)
            result.tokens_out = usage.get("completion_tokens", 0)
            if elapsed > 0 and result.tokens_out > 0:
                result.tokens_per_sec = (result.tokens_out / elapsed) * 1000
            result.success = bool(result.output)

            # Check keywords
            output_lower = result.output.lower()
            result.keywords_found = [
                kw for kw in prompt_data.get("expected_keywords", [])
                if kw.lower() in output_lower
            ]
            result.keywords_missing = [
                kw for kw in prompt_data.get("expected_keywords", [])
                if kw.lower() not in output_lower
            ]
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError) as e:
        result.error = str(e)
        result.success = False

    return result


def run_model_tests(
    model_label: str,
    host: str,
    port: int,
    model_id: str,
    prompts: list[dict],
) -> ModelStats:
    """Run all prompts against a single model and return aggregate stats."""
    print(f"\n{'=' * 70}")
    print(f"  TESTING: {model_label}  (http://{host}:{port})")
    print(f"{'=' * 70}")

    if not check_server(host, port):
        print(f"[ERROR] Server not reachable at http://{host}:{port}/v1/models")
        print(f"[HINT] Start it with: scripts/serve_native_gguf.sh start")
        return ModelStats(
            name=model_label, port=port,
            total_tests=0, successful_tests=0,
            avg_tokens_per_sec=0.0, avg_latency_ms=0.0,
            total_tokens_in=0, total_tokens_out=0, memory_mb=0,
        )

    mem_before = get_memory_usage(port)
    print(f"[OK] Server reachable, RSS before tests: {mem_before} MB")

    results: list[TestResult] = []
    for i, p in enumerate(prompts, 1):
        print(f"\n  [{i}/{len(prompts)}] {p['name']} ({p['category']})")
        r = run_prompt(host, port, model_id, p)
        results.append(r)
        if r.success:
            print(f"    → {r.tokens_per_sec:.1f} tok/s, {r.latency_ms:.0f}ms, "
                  f"{r.tokens_in}→{r.tokens_out} tokens, "
                  f"keywords: {len(r.keywords_found)}/{len(r.keywords_found) + len(r.keywords_missing)}")
        else:
            print(f"    → FAILED: {r.error or 'empty output'}")

    mem_after = get_memory_usage(port)

    total = len(results)
    success = sum(1 for r in results if r.success)
    avg_tps = sum(r.tokens_per_sec for r in results) / total if total else 0
    avg_lat = sum(r.latency_ms for r in results) / total if total else 0
    total_in = sum(r.tokens_in for r in results)
    total_out = sum(r.tokens_out for r in results)

    return ModelStats(
        name=model_label, port=port,
        total_tests=total, successful_tests=success,
        avg_tokens_per_sec=avg_tps,
        avg_latency_ms=avg_lat,
        total_tokens_in=total_in, total_tokens_out=total_out,
        memory_mb=mem_after,
        results=results,
    )


def print_comparison(stats: list[ModelStats]) -> None:
    """Print a side-by-side comparison of the models tested."""
    print(f"\n{'=' * 70}")
    print(f"  COMPARISON SUMMARY")
    print(f"{'=' * 70}\n")
    header = f"{'METRIC':<30}" + "".join(f"{s.name:>18}" for s in stats)
    print(header)
    print("-" * len(header))
    rows = [
        ("Total tests", lambda s: str(s.total_tests)),
        ("Successful tests", lambda s: f"{s.successful_tests} ({s.successful_tests/max(s.total_tests,1)*100:.0f}%)"),
        ("Avg tokens/sec", lambda s: f"{s.avg_tokens_per_sec:.1f}"),
        ("Avg latency (ms)", lambda s: f"{s.avg_latency_ms:.0f}"),
        ("Total input tokens", lambda s: str(s.total_tokens_in)),
        ("Total output tokens", lambda s: str(s.total_tokens_out)),
        ("Memory RSS (MB)", lambda s: str(s.memory_mb)),
    ]
    for label, fn in rows:
        print(f"{label:<30}" + "".join(f"{fn(s):>18}" for s in stats))

    # Per-category breakdown
    print(f"\n  Per-category success rate:")
    categories = sorted({r.category for s in stats for r in s.results})
    for cat in categories:
        row = f"    {cat:<28}"
        for s in stats:
            cat_results = [r for r in s.results if r.category == cat]
            if cat_results:
                succ = sum(1 for r in cat_results if r.success)
                row += f"{succ}/{len(cat_results)} success    ".rjust(18)
            else:
                row += f"{'-':>18}"
        print(row)

    # Verdict
    print(f"\n  VERDICT:")
    if len(stats) >= 2:
        lfm: Optional[ModelStats] = None
        qwen: Optional[ModelStats] = None
        for s in stats:
            if "lfm" in s.name.lower():
                lfm = s
            elif "qwen" in s.name.lower():
                qwen = s
        if lfm and qwen:
            if lfm.avg_tokens_per_sec > qwen.avg_tokens_per_sec * 1.1:
                print(f"    {lfm.name} is faster ({lfm.avg_tokens_per_sec:.1f} vs {qwen.avg_tokens_per_sec:.1f} tok/s)")
            elif qwen.avg_tokens_per_sec > lfm.avg_tokens_per_sec * 1.1:
                print(f"    {qwen.name} is faster ({qwen.avg_tokens_per_sec:.1f} vs {lfm.avg_tokens_per_sec:.1f} tok/s)")
            else:
                print(f"    Speed is comparable (within 10%)")
            if lfm.memory_mb < qwen.memory_mb:
                print(f"    {lfm.name} uses less memory ({lfm.memory_mb} vs {qwen.memory_mb} MB)")


def save_results(stats: list[ModelStats]) -> None:
    """Save raw results to JSON for later analysis."""
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump([asdict(s) for s in stats], f, indent=2, default=str)
    print(f"\n  Raw results saved to: {RESULTS_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare LFM2.5-2.6B and Qwen3-1.7B for Omega Engine.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--model", choices=["lfm", "qwen"], default="lfm",
                        help="Which model to test (default: lfm)")
    parser.add_argument("--port", type=int, default=None,
                        help="Override server port (default: 1234 for lfm, 1236 for qwen)")
    parser.add_argument("--host", default=DEFAULT_HOST,
                        help=f"Server host (default: {DEFAULT_HOST})")
    parser.add_argument("--model-id", default=None,
                        help="Model ID string for the API (default: derived from --model)")
    parser.add_argument("--compare", action="store_true",
                        help="Test both LFM and Qwen sequentially (requires both servers running)")
    args = parser.parse_args()

    prompts = load_prompts()
    print(f"  Loaded {len(prompts)} test prompts")

    stats_list: list[ModelStats] = []

    if args.compare:
        # Test both
        for label, default_port, model_id in [
            ("LFM2.5-2.6B", 1234, "lfm-2.5-2.6b-local"),
            ("Qwen3-1.7B", 1236, "qwen3-1.7b-local"),
        ]:
            port = args.port if args.port else default_port
            stats = run_model_tests(label, args.host, port, model_id, prompts)
            stats_list.append(stats)
    else:
        # Test one
        if args.model == "lfm":
            label = "LFM2.5-2.6B"
            port = args.port if args.port else 1234
            model_id = args.model_id or "lfm-2.5-2.6b-local"
        else:
            label = "Qwen3-1.7B"
            port = args.port if args.port else 1236
            model_id = args.model_id or "qwen3-1.7b-local"
        stats = run_model_tests(label, args.host, port, model_id, prompts)
        stats_list.append(stats)

    print_comparison(stats_list)
    save_results(stats_list)

    # Exit code: 0 if all successful, 1 if any failures
    all_ok = all(s.successful_tests == s.total_tests and s.total_tests > 0 for s in stats_list)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
