#!/usr/bin/env python3
"""
A/B/C: LFM (num_thread 8) decode under three embedding-placement conditions.

  A: LLM alone            embedder idle, pinned 12-15 (E)
  B: LLM + embed on E     hammer -> :11435, pinned 12-15
  C: LLM + embed on P     hammer -> :11435, retargeted to 0-11

Host: i7-13620H (6P+4E/16T), 16GB single-channel DDR5-5200, CPU-only.
Gen  instance: :11434, pinned 0-11.  Emb instance: :11435, num_thread 4.
Embedder: Ollama qwen3-family 595.78M, native 1024-d (verified at runtime).
LLM tag: bench-tlfm25-t6-latest-8 (num_thread 8).

NOTE ON THREAD COUNT: the measured peak for this tag family is t=6 (21.2 t/s,
2026-10-07); t=8 measured 20.5 t/s idle. The operator explicitly asked for 8,
so 8 is what is measured here. Do not compare these numbers to the t=6 rows
in docs/BENCHMARKS.md without saying which tag was used.

Usage: python3 emb_bench.py [all|A|B|C]   results -> emb_bench_results.json
"""
import json, os, statistics, subprocess, sys, threading, time, urllib.request

GEN = "http://127.0.0.1:11434"
EMB = "http://127.0.0.1:11435"
LFM = "bench-tlfm25-t6-latest-8"
EMB_MODEL = "emb-t4"
PROMPT = "Explain the difference between a coroutine and a thread in two sentences."
RUNS = int(os.environ.get("RUNS", "5"))
TOKENS = int(os.environ.get("TOKENS", "96"))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emb_bench_results.json")

stop = threading.Event()
emb_stats = {"n": 0, "ms": []}
emb_err = {"n": 0}


def post(url, payload, timeout=300):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def hammer():
    while not stop.is_set():
        t0 = time.perf_counter()
        try:
            post(EMB + "/api/embed", {
                "model": EMB_MODEL,
                "input": "benchmark load probe for core-placement measurement",
            }, timeout=120)
            emb_stats["ms"].append((time.perf_counter() - t0) * 1000)
            emb_stats["n"] += 1
        except Exception:
            emb_err["n"] += 1
        time.sleep(0.05)


def gen_once():
    t0 = time.perf_counter()
    r = post(GEN + "/api/generate", {
        "model": LFM, "prompt": PROMPT, "stream": False,
        "options": {"num_predict": TOKENS, "temperature": 0},
    }, timeout=300)
    wall = time.perf_counter() - t0
    n = r.get("eval_count", 0)
    ns = r.get("eval_duration", 1)
    return {"tokens": n,
            "wall_s": round(wall, 3),
            "eval_tps": round(n / (ns / 1e9), 2) if ns else None,
            "load_s": round(r.get("load_duration", 0) / 1e9, 2),
            "prompt_eval_s": round(r.get("prompt_eval_duration", 0) / 1e9, 3)}


def aff(pid):
    return subprocess.run(["taskset", "-pc", str(pid)],
                          capture_output=True, text=True).stdout.strip()


def set_aff(pid, cpus):
    subprocess.run(["taskset", "-pc", cpus, str(pid)], capture_output=True)


def run(label, gen_pid, emb_pid, use_hammer):
    global stop, emb_stats, emb_err
    stop = threading.Event()
    emb_stats = {"n": 0, "ms": []}
    emb_err = {"n": 0}

    print(f"\n{'='*66}\n{label}\n{'='*66}", flush=True)
    print(f"gen   aff: {aff(gen_pid)}", flush=True)
    print(f"embed aff: {aff(emb_pid)}", flush=True)

    warm = gen_once()                      # page-in / load, discarded
    print(f"warm-up   : {warm['eval_tps']} t/s  load={warm['load_s']}s", flush=True)

    th = None
    if use_hammer:
        th = threading.Thread(target=hammer, daemon=True)
        th.start()
        time.sleep(6)

    res = [gen_once() for _ in range(RUNS)]
    stop.set()
    if th:
        th.join(timeout=10)

    tps = [r["eval_tps"] for r in res if r["eval_tps"]]
    out = {
        "label": label,
        "gen_affinity": aff(gen_pid), "emb_affinity": aff(emb_pid),
        "warmup": warm, "runs": res,
        "eval_tps_mean": round(statistics.mean(tps), 2),
        "eval_tps_min": round(min(tps), 2),
        "eval_tps_max": round(max(tps), 2),
        "eval_tps_stdev": round(statistics.pstdev(tps), 2) if len(tps) > 1 else 0.0,
        "embed_calls": emb_stats["n"], "embed_err": emb_err["n"],
        "embed_latency_ms_mean": (round(statistics.mean(emb_stats["ms"]), 2)
                                  if emb_stats["ms"] else None),
        "embed_latency_ms_min": (round(min(emb_stats["ms"]), 2)
                                 if emb_stats["ms"] else None),
    }
    print(json.dumps(out, indent=2), flush=True)
    return out


def main():
    gen_pid, emb_pid = 2952, 2017      # verified pre-run: 0-11 and 12-15
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    results = []

    if which in ("all", "A"):
        set_aff(emb_pid, "12-15")
        results.append(run("A: LLM ALONE (embedder idle @12-15)", gen_pid, emb_pid, False))
    if which in ("all", "B"):
        set_aff(emb_pid, "12-15")
        results.append(run("B: LLM + EMBED ON E-CORES (12-15)", gen_pid, emb_pid, True))
    if which in ("all", "C"):
        set_aff(emb_pid, "0-11")
        results.append(run("C: LLM + EMBED ON P-CORES (0-11)", gen_pid, emb_pid, True))
        set_aff(emb_pid, "12-15")      # always restore
        print("\n[restored embedder affinity to 12-15]", flush=True)

    # incremental write so a crash keeps completed arms
    prior = []
    if os.path.exists(OUT):
        try:
            prior = json.load(open(OUT))
        except Exception:
            prior = []
    prior = [p for p in prior if p.get("label") not in {r["label"] for r in results}]
    prior.extend(results)
    json.dump(prior, open(OUT, "w"), indent=2)
    print(f"\nwrote {OUT}", flush=True)


if __name__ == "__main__":
    main()