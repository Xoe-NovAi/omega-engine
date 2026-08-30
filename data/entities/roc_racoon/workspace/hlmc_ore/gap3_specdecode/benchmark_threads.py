#!/usr/bin/env python3
"""
Benchmark: native-gguf thread count (4 vs 6 vs 8) on Ryzen 7 5700U.
Measures generation time and peak RSS. Monitors CPU usage via mpstat.
"""
import anyio
import json
import os
import time
import subprocess
import threading
from pathlib import Path

MODEL_PATH = "/media/arcana-novai/omega_library/models/gguf/Qwen3-1.7B-Q6_K.gguf"
N_CTX = 4096
SYSTEM_PROMPT = "You are a helpful assistant. Reply concisely."
USER_QUERY = "Explain the Fast Inverse Square Root algorithm in 3 sentences."
MAX_TOKENS = 128

# Ryzen 7 5700U: 8 physical cores → even logical CPUs (0,2,4,6,8,10,12,14)
# Odd numbers are SMT siblings — avoid them for benchmarking.
PHYSICAL_CORES = [0, 2, 4, 6, 8, 10, 12, 14]

THREAD_CONFIGS = [
    {"n_threads": 4, "n_threads_batch": 4, "cores": PHYSICAL_CORES[:4]},
    {"n_threads": 5, "n_threads_batch": 5, "cores": PHYSICAL_CORES[:5]},
    {"n_threads": 6, "n_threads_batch": 6, "cores": PHYSICAL_CORES[:6]},
    {"n_threads": 8, "n_threads_batch": 8, "cores": PHYSICAL_CORES[:8]},
]

def get_peak_rss_mb():
    """Get peak RSS in MB from /proc/self/status."""
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return 0

def monitor_cpu(interval=0.5, results_list=None, stop_event=None):
    """Sample mpstat every `interval` seconds until stop_event."""
    while not stop_event.is_set():
        try:
            out = subprocess.check_output(
                ["mpstat", "1", "1"],  # 1 CPU, 1 sample
                text=True, timeout=3
            )
            # Parse mpstat output — get idle%
            for line in out.strip().split("\n"):
                if "all" in line and "idle" not in line.lower():
                    parts = line.split()
                    # Find %usr and %sys columns
                    for i, p in enumerate(parts):
                        if p == "all":
                            usr = float(parts[i+1]) if i+1 < len(parts) else 0
                            sys_val = float(parts[i+3]) if i+3 < len(parts) else 0
                            total = 100 - float(parts[i+10]) if i+10 < len(parts) else 0
                            results_list.append({"time": time.monotonic(), "cpu_pct": total, "usr": usr, "sys": sys_val})
                            break
        except Exception:
            pass
        time.sleep(interval)

async def run_benchmark(thread_config, run_id):
    """Run a single benchmark with given thread config."""
    from llama_cpp import Llama
    import threading as _threading

    n_threads = thread_config["n_threads"]
    cores = thread_config["cores"]

    print(f"\n{'='*60}")
    print(f"Run {run_id}: n_threads={n_threads}, cores={cores}")
    print(f"{'='*60}")

    # Start CPU monitoring
    cpu_samples = []
    stop_event = _threading.Event()
    monitor_thread = _threading.Thread(target=monitor_cpu, args=(0.5, cpu_samples, stop_event), daemon=True)
    monitor_thread.start()

    # Set CPU affinity
    try:
        os.sched_setaffinity(0, cores)
        print(f"CPU affinity set to: {os.sched_getaffinity(0)}")
    except Exception as e:
        print(f"Could not set affinity: {e}")

    # Load model
    t_load_start = time.monotonic()
    llm = Llama(
        model_path=MODEL_PATH,
        n_threads=n_threads,
        n_threads_batch=n_threads,
        n_ctx=N_CTX,
        n_batch=512,
        n_ubatch=32,
        type_k=8,   # q8_0 key cache
        type_v=1,   # f16 value cache
        use_mmap=True,
        use_mlock=False,
        n_gpu_layers=0,
        verbose=False,
    )
    t_load = time.monotonic() - t_load_start
    print(f"Model loaded in {t_load:.2f}s")

    rss_after_load = get_peak_rss_mb()
    print(f"RSS after load: {rss_after_load:.0f} MB")

    # Run inference
    prompt = f"<|system|>{SYSTEM_PROMPT}</s><|user|>{USER_QUERY}</s><|assistant|>"

    t_gen_start = time.monotonic()
    result = llm(
        prompt=prompt,
        max_tokens=MAX_TOKENS,
        temperature=0.1,
        stop=["</s>", "User:"],
    )
    t_gen = time.monotonic() - t_gen_start

    text = result["choices"][0]["text"].strip()
    usage = result.get("usage", {})
    tokens_generated = usage.get("completion_tokens", 0)

    rss_after_gen = get_peak_rss_mb()

    # Stop monitoring
    stop_event.set()
    monitor_thread.join(timeout=2)

    llm.close()
    del llm

    # Calculate CPU stats
    avg_cpu = sum(s["cpu_pct"] for s in cpu_samples) / len(cpu_samples) if cpu_samples else 0
    max_cpu = max((s["cpu_pct"] for s in cpu_samples), default=0)

    tokens_per_sec = tokens_generated / t_gen if t_gen > 0 else 0

    metrics = {
        "n_threads": n_threads,
        "cores": cores,
        "load_time_s": round(t_load, 2),
        "gen_time_s": round(t_gen, 2),
        "tokens_generated": tokens_generated,
        "tokens_per_sec": round(tokens_per_sec, 1),
        "rss_after_load_mb": round(rss_after_load, 0),
        "rss_after_gen_mb": round(rss_after_gen, 0),
        "avg_cpu_pct": round(avg_cpu, 1),
        "max_cpu_pct": round(max_cpu, 1),
        "output_preview": text[:120],
    }

    print(f"\nResults:")
    print(f"  Tokens: {tokens_generated} | Gen time: {t_gen:.2f}s | Speed: {tokens_per_sec:.1f} tok/s")
    print(f"  RSS: {rss_after_load:.0f} → {rss_after_gen:.0f} MB")
    print(f"  CPU: avg {avg_cpu:.1f}% | peak {max_cpu:.1f}%")

    return metrics

async def main():
    print(f"Model: {MODEL_PATH}")
    print(f"Context: {N_CTX} tokens")
    print(f"Query: {USER_QUERY[:60]}...")
    print(f"Max tokens: {MAX_TOKENS}")

    results = []
    for i, config in enumerate(THREAD_CONFIGS, 1):
        metrics = await run_benchmark(config, i)
        results.append(metrics)

    # Summary table
    print(f"\n{'='*80}")
    print(f"SUMMARY — Ryzen 7 5700U Native-GGUF Thread Benchmark")
    print(f"{'='*80}")
    print(f"{'Threads':>7} | {'Load (s)':>8} | {'Gen (s)':>8} | {'tok/s':>6} | {'RSS (MB)':>8} | {'Avg CPU':>8} | {'Peak CPU':>8}")
    print(f"{'-'*7}-+-{'-'*8}-+-{'-'*8}-+-{'-'*6}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}")
    for r in results:
        print(f"{r['n_threads']:>7} | {r['load_time_s']:>8.2f} | {r['gen_time_s']:>8.2f} | {r['tokens_per_sec']:>6.1f} | {r['rss_after_gen_mb']:>8.0f} | {r['avg_cpu_pct']:>7.1f}% | {r['max_cpu_pct']:>7.1f}%")

    # Save results
    out_path = Path("data/entities/john_carmack/workspace/thread_benchmark_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to: {out_path}")

if __name__ == "__main__":
    anyio.run(main)
