#!/usr/bin/env python3
"""
Abbreviated Screening — GSCA Protocol
Temperature sweep: 0.1, 0.5, 0.7
Context sweep: 4096, 8192
3 prompts × 3 temps × 2 contexts = 18 runs/model

Features:
- Incremental save after EACH run (no data loss on interrupt)
- Auto-resume from existing results file
- Clear progress tracking
"""

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SCREENING_PROMPTS = [
    "Write a Python function to parse JSON with error handling.",
    "Explain the difference between async and threading in Python.",
    "Write a recursive function to flatten a nested dictionary.",
]

TEMPERATURES = [0.1, 0.5, 0.7]
CONTEXTS = [4096, 8192]

REQUEST_TIMEOUT = 300


def log(msg):
    print(msg, flush=True)


def generate(host, model, prompt, temperature=0.1, num_ctx=4096, timeout=REQUEST_TIMEOUT):
    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_thread": 8,
            "num_gpu": 0
        }
    }).encode()
    req = urllib.request.Request(
        f"{host}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        raise RuntimeError(f"HTTP {e.code} :: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"connection error: {e.reason}") from e
    except TimeoutError:
        raise RuntimeError(f"request timed out after {timeout}s")
    return json.loads(raw)


def load_existing_results(output_file):
    """Load existing results if file exists, return (results, completed_runs_set)."""
    if not output_file.exists():
        return [], set()
    try:
        data = json.loads(output_file.read_text())
        results = data.get("results", [])
        completed = {(r["context"], r["temperature"], r["prompt_idx"]) for r in results if r.get("tps") is not None}
        log(f"[RESUME] Found {len(completed)}/18 runs already completed")
        return results, completed
    except Exception as e:
        log(f"[WARN] Could not load existing results: {e}")
        return [], set()


def save_results(output_file, model, results):
    """Save results atomically (write to temp, then rename)."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = output_file.with_suffix(".tmp")
    data = {
        "model": model,
        "protocol": "GSCA abbreviated screening",
        "prompts": SCREENING_PROMPTS,
        "temperatures": TEMPERATURES,
        "contexts": CONTEXTS,
        "results": results,
        "timestamp": time.time()
    }
    temp_file.write_text(json.dumps(data, indent=2))
    temp_file.replace(output_file)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Abbreviated screening per GSCA protocol")
    ap.add_argument("--model", required=True)
    ap.add_argument("--host", default="http://localhost:11434")
    args = ap.parse_args()

    log(f"=== ABBREVIATED SCREENING: {args.model} ===")
    log(f"Prompts: {len(SCREENING_PROMPTS)} | Temps: {TEMPERATURES} | Contexts: {CONTEXTS}")
    log(f"Total runs: {len(SCREENING_PROMPTS) * len(TEMPERATURES) * len(CONTEXTS)}")
    log("")

    # Output file path
    output_dir = Path("benchmarking") / "screening"
    output_file = output_dir / f"{args.model.replace(':', '-')}_screening.json"

    # Load existing results
    results, completed = load_existing_results(output_file)

    run_id = 0
    for ctx in CONTEXTS:
        for temp in TEMPERATURES:
            for i, prompt in enumerate(SCREENING_PROMPTS, 1):
                run_id += 1
                key = (ctx, temp, i)

                # Skip if already completed
                if key in completed:
                    existing = next(r for r in results if (r["context"], r["temperature"], r["prompt_idx"]) == key)
                    log(f"[Run {run_id:2d}/18] ctx={ctx:5d} temp={temp:.1f} prompt={i} — SKIPPED (already done: {existing['tps']:.2f} t/s)")
                    continue

                log(f"[Run {run_id:2d}/18] ctx={ctx:5d} temp={temp:.1f} prompt={i}")
                log(f"  Prompt: {prompt!r}")

                t0 = time.time()
                try:
                    resp = generate(args.host, args.model, prompt, temperature=temp, num_ctx=ctx)
                except Exception as exc:
                    log(f"  ERROR: {exc}")
                    results.append({
                        "run": run_id, "context": ctx, "temperature": temp, "prompt_idx": i,
                        "error": str(exc), "time_s": None, "tokens": None, "tps": None
                    })
                    # Save immediately on error too
                    save_results(output_file, args.model, results)
                    continue

                dt = time.time() - t0
                tok = resp.get("eval_count", 0)
                tps = tok / dt if dt > 0 else 0

                result = {
                    "run": run_id, "context": ctx, "temperature": temp, "prompt_idx": i,
                    "time_s": round(dt, 2), "tokens": tok, "tps": round(tps, 2)
                }
                results.append(result)

                # INCREMENTAL SAVE AFTER EACH RUN
                save_results(output_file, args.model, results)

                log(f"  {dt:.1f}s | {tok} tokens | {tps:.2f} t/s  ✓ SAVED")
                log("")

    # Summary
    log("=== SCREENING SUMMARY ===")
    valid = [r for r in results if r["tps"] is not None]
    if valid:
        for ctx in CONTEXTS:
            for temp in TEMPERATURES:
                subset = [r for r in valid if r["context"] == ctx and r["temperature"] == temp]
                if subset:
                    avg_tps = sum(r["tps"] for r in subset) / len(subset)
                    avg_tok = sum(r["tokens"] for r in subset) / len(subset)
                    log(f"  ctx={ctx:5d} temp={temp:.1f} → avg {avg_tps:.2f} t/s | {avg_tok:.0f} tokens")

    log(f"\nFinal results saved to {output_file}")


if __name__ == "__main__":
    main()