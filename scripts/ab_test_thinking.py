#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
A/B Test: Qwen3-1.7B thinking ENABLED vs DISABLED
===================================================
Measures latency, throughput, tok/s, token efficiency, and real-time hardware stats.

Usage:
    source .venv/bin/activate && PYTHONPATH=src python3 scripts/ab_test_thinking.py
    source .venv/bin/activate && PYTHONPATH=src python3 scripts/ab_test_thinking.py --quick
    source .venv/bin/activate && PYTHONPATH=src python3 scripts/ab_test_thinking.py --threads 4
"""
import anyio
import time
import gc
import sys
import json
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from omega.oracle.providers import NativeGGUFProvider
from omega.monitoring import HardwareMonitor

MODEL_PATH = "/media/arcana-novai/omega_library/models/gguf/Qwen3-1.7B-Q6_K.gguf"

PROMPTS = [
    {
        "name": "simple_fact",
        "system": "You are a helpful assistant. Reply concisely.",
        "user": "What is the capital of France?",
    },
    {
        "name": "reasoning",
        "system": "You are a helpful assistant. Reply concisely.",
        "user": "If a train leaves station A at 60 mph and another leaves station B at 40 mph, 200 miles apart, when do they meet?",
    },
    {
        "name": "code",
        "system": "You are a helpful assistant. Reply concisely.",
        "user": "Write a Python function to reverse a linked list.",
    },
]


def parse_response(text: str) -> dict:
    """Parse response, detecting thinking tokens."""
    content = text or ""
    has_think = "<think>" in content
    think_start = content.find("<think>")
    think_end = content.find("</think>")
    if has_think and think_end > think_start:
        think_chars = think_end - (think_start + len("<think>"))
        cleaned = content[think_end + len("</think>"):].strip()
    else:
        think_chars = 0
        cleaned = content
    return {
        "total_chars": len(content),
        "think_chars": think_chars,
        "content_chars": len(cleaned),
        "has_think": has_think,
        "cleaned": cleaned,
    }


async def run_all(
    prompts: list,
    enable_thinking: bool,
    n_threads: int,
    cores: list,
    hw: HardwareMonitor,
) -> list:
    """Run all prompts with hardware monitoring."""
    provider = NativeGGUFProvider("native-gguf", {
        "model_path": MODEL_PATH,
        "n_threads": n_threads,
        "n_threads_batch": min(n_threads, 4),
        "cores": cores,
        "type_k": 8,
        "type_v": 1,
        "n_ctx": 4096,
    })

    results = []
    for p in prompts:
        # Pre-inference hardware snapshot
        hw_before = hw.collect_all()
        
        t0 = time.monotonic()
        try:
            text = await provider.generate(
                model="qwen3-1.7b",
                system_prompt=p["system"],
                user_query=p["user"],
                temperature=0.3,
                max_tokens=512,
            )
            elapsed = time.monotonic() - t0
            parsed = parse_response(text)
            
            # Post-inference hardware snapshot
            hw_after = hw.collect_all()
            hw_delta = HardwareMonitor.diff(hw_before, hw_after)

            tok_s = round(parsed["total_chars"] / 2 / elapsed, 2) if elapsed > 0 else 0
            think_waste = round(
                parsed["think_chars"] / (parsed["total_chars"] or 1) * 100, 1
            )

            results.append({
                "name": p["name"],
                "thinking_enabled": enable_thinking,
                "elapsed_s": round(elapsed, 2),
                "total_chars": parsed["total_chars"],
                "think_chars": parsed["think_chars"],
                "content_chars": parsed["content_chars"],
                "think_waste_pct": think_waste,
                "tokens_per_second": tok_s,
                "has_think": parsed["has_think"],
                "hardware": {
                    "before": {
                        "cpu_avg": hw_before["cpu"]["avg_percent"],
                        "memory_used_mb": hw_before["memory"]["used_mb"],
                        "memory_available_mb": hw_before["memory"]["available_mb"],
                        "oom_risk": hw_before["memory"]["oom_risk"],
                        "memory_pressure": hw_before["memory_pressure"],
                    },
                    "after": {
                        "cpu_avg": hw_after["cpu"]["avg_percent"],
                        "memory_used_mb": hw_after["memory"]["used_mb"],
                        "memory_available_mb": hw_after["memory"]["available_mb"],
                        "oom_risk": hw_after["memory"]["oom_risk"],
                        "memory_pressure": hw_after["memory_pressure"],
                    },
                    "delta": hw_delta,
                },
                "preview": parsed["cleaned"][:120].replace("\n", " "),
            })
        except Exception as e:
            results.append({
                "name": p["name"],
                "thinking_enabled": enable_thinking,
                "error": str(e),
            })

    return results


def print_table(results_on: list, results_off: list):
    """Print comparison table."""
    print("\n" + "=" * 100)
    print(f"{'Prompt':<20} {'Mode':>5} {'Time':>7} {'Total':>7} {'Think':>7} {'Waste':>7} {'Tok/s':>7} {'CPUΔ':>6} {'MemΔ':>7}")
    print("-" * 100)
    for r_on, r_off in zip(results_on, results_off):
        for r, mode in [(r_on, "ON"), (r_off, "OFF")]:
            if "error" in r:
                print(f"{r['name']:<20} {mode:>5} ERROR: {r['error'][:50]}")
            else:
                hw = r.get("hardware", {})
                delta = hw.get("delta", {})
                print(
                    f"{r['name']:<20} {mode:>5} "
                    f"{r.get('elapsed_s', 0):>6.1f}s "
                    f"{r.get('total_chars', 0):>7} "
                    f"{r.get('think_chars', 0):>7} "
                    f"{r.get('think_waste_pct', 0):>6.1f}% "
                    f"{r.get('tokens_per_second', 0):>6.1f} "
                    f"{delta.get('cpu_utilization_delta', 0):>+5.1f}% "
                    f"{delta.get('memory_delta_mb', 0):>+6.0f}MB"
                )
    print("-" * 100)

    # Aggregates
    for label, results in [("Thinking ENABLED", results_on), ("Thinking DISABLED", results_off)]:
        valid = [r for r in results if "error" not in r]
        if not valid:
            print(f"\n{label}: ALL FAILED")
            continue
        avg_t = sum(r["elapsed_s"] for r in valid) / len(valid)
        avg_s = sum(r["tokens_per_second"] for r in valid) / len(valid)
        total_think = sum(r["think_chars"] for r in valid)
        total_content = sum(r["content_chars"] for r in valid)
        total_waste = sum(r["total_chars"] for r in valid)
        total_elapsed = sum(r["elapsed_s"] for r in valid)
        has_any_think = any(r["has_think"] for r in valid)

        print(f"\n{label} (n={len(valid)}):")
        print(f"  Avg time: {avg_t:.1f}s | Avg tok/s: {avg_s:.1f} | Total: {total_elapsed:.1f}s")
        if has_any_think:
            waste_pct = total_think / (total_think + total_content) * 100
            print(f"  Thinking waste: {total_think} chars ({waste_pct:.0f}% of output)")
        else:
            print(f"  Clean output: {total_content} chars (zero thinking tokens)")

        # Hardware summary
        avg_mem_used = sum(r["hardware"]["before"]["memory_used_mb"] for r in valid) / len(valid)
        avg_mem_avail = sum(r["hardware"]["before"]["memory_available_mb"] for r in valid) / len(valid)
        oom_risks = set(r["hardware"]["before"]["oom_risk"]["risk_level"] for r in valid)
        print(f"  Avg mem: {avg_mem_used:.0f}MB used / {avg_mem_avail:.0f}MB avail")
        print(f"  OOM risk: {', '.join(sorted(oom_risks))}")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="A/B Test: Qwen3-1.7B thinking mode")
    parser.add_argument("--quick", action="store_true", help="Skip hardware monitoring, just run prompts")
    parser.add_argument("--threads", type=int, default=8, help="Number of inference threads (default: 8)")
    parser.add_argument("--single-ccx", action="store_true", help="Pin to single CCX (cores 0-3) instead of cross-CCX")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    # Thread topology
    if args.single_ccx:
        n_threads = min(args.threads, 4)
        cores = [0, 2, 4, 6]  # Single CCX (cores 0-3, one SMT thread each)
        topo_label = "SINGLE-CCX (cores 0-3)"
    else:
        n_threads = args.threads
        cores = [0, 2, 4, 6, 8, 10, 12, 14]  # Cross-CCX (all cores)
        topo_label = "CROSS-CCX (cores 0-7)"

    hw = HardwareMonitor() if not args.quick else None

    print("=" * 100)
    print(f"  A/B TEST: Qwen3-1.7B Thinking Mode | Threads: {n_threads} | Topology: {topo_label}")
    if not args.quick:
        print(f"  Initial OOM risk: {hw.get_oom_risk_level()}")
        top_init = hw.collect_all()
        print(f"  Initial memory: {top_init['memory']['used_mb']:.0f}/{top_init['memory']['total_mb']:.0f}MB "
              f"(avail: {top_init['memory']['available_mb']:.0f}MB)")
    print("=" * 100)

    # Phase 1: Thinking ENABLED
    print("\n▶ Phase 1: Thinking ENABLED (default) — loading model...")
    r_on = await run_all(PROMPTS, enable_thinking=True, n_threads=n_threads, cores=cores, hw=hw)
    gc.collect()
    if not args.quick:
        after_p1 = hw.collect_all()
        print(f"  Post-Phase 1 mem: {after_p1['memory']['used_mb']:.0f}MB used / "
              f"{after_p1['memory']['available_mb']:.0f}MB avail")

    # Phase 2: Thinking DISABLED
    print("\n▶ Phase 2: Thinking DISABLED (handler-wrapped) — loading model...")
    r_off = await run_all(PROMPTS, enable_thinking=False, n_threads=n_threads, cores=cores, hw=hw)
    gc.collect()

    if args.json:
        output = {
            "thinking_enabled": r_on,
            "thinking_disabled": r_off,
            "config": {
                "threads": n_threads,
                "topology": topo_label,
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print_table(r_on, r_off)

    # Final
    if not args.quick:
        final = hw.collect_all()
        print(f"\n  Final memory: {final['memory']['used_mb']:.0f}/{final['memory']['total_mb']:.0f}MB "
              f"(avail: {final['memory']['available_mb']:.0f}MB, "
              f"OOM: {final['memory']['oom_risk']['risk_level']})")
        print(f"  Peak memory pressure: {final['memory_pressure']:.3f}")

    print("\n✅ A/B test complete.\n")


if __name__ == "__main__":
    anyio.run(main)
