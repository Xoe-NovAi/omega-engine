#!/usr/bin/env python3
"""Omega Engine Alpha — Ollama benchmark harness with explicit error visibility."""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request

DEFAULT_PROMPTS = [
    "Explain quantum computing in one sentence.",
    "Write a Python function to sort a list.",
    "What are the pros and cons of microservices?",
    "Summarize the history of the internet.",
    "Write a haiku about debugging code.",
]

REQUEST_TIMEOUT = 300  # seconds per request


def log(msg):
    print(msg, flush=True)


def generate(host, model, prompt, timeout=REQUEST_TIMEOUT):
    data = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        f"{host}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        raise RuntimeError(
            f"HTTP {e.code} from {host}/api/generate :: {body}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"connection error to {host}: {e.reason}"
        ) from e
    except TimeoutError:
        raise RuntimeError(f"request timed out after {timeout}s")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"non-JSON response (HTTP {status}): {raw[:300]!r}"
        ) from e


def main():
    ap = argparse.ArgumentParser(description="Benchmark an Ollama model.")
    ap.add_argument("--model", default="phi4-mini")
    ap.add_argument("--prompts", type=int, default=3)
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--warm", action="store_true", help="warm the model first (excluded from stats)")
    ap.add_argument("--verbose", action="store_true", help="print full generate payload")
    args = ap.parse_args()

    log(f"── Benchmarking {args.model} @ {args.host} ──")

    if args.warm:
        log("  [warm] preloading model (excluded from stats)...")
        try:
            generate(args.host, args.model, "hi")
            log("  [warm] ok")
        except Exception as exc:
            log(f"  [warm] WARNING: {exc}")

    total_gen = 0.0
    total_tokens = 0
    measured = 0
    for i, p in enumerate(DEFAULT_PROMPTS[: args.prompts], 1):
        log(f"  → Prompt {i}: {p!r}")
        t0 = time.time()
        try:
            resp = generate(args.host, args.model, p)
        except Exception as exc:
            log(f"  Prompt {i}: ERROR: {exc}")
            continue
        dt = time.time() - t0
        tok = resp.get("eval_count", 0)
        tps = tok / dt if dt > 0 else 0
        total_gen += dt
        total_tokens += tok
        measured += 1
        if args.verbose:
            log(
                f"    payload: tok={tok} pps={resp.get('prompt_eval_count')} "
                f"total={resp.get('total_duration',0)/1e9:.2f}s "
                f"load={resp.get('load_duration',0)/1e9:.2f}s "
                f"eval={resp.get('eval_duration',0)/1e9:.2f}s"
            )
        log(f"  Prompt {i}: {dt:.1f}s | {tok} tokens | {tps:.1f} t/s")

    if measured and total_tokens:
        log("  ────────────────────────────────")
        log(
            f"  Average: {total_gen / measured:.1f}s | {total_tokens / measured:.0f} tokens | "
            f"{total_tokens / total_gen:.1f} t/s"
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n  interrupted by user")
        sys.exit(130)
