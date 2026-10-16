#!/usr/bin/env python3
"""
Re-run all three generator models under ONE power profile, with memory settling
between runs.

Why this exists (2026-10-14):
  * The phi4-mini run #1 was zRAM-thrashed by the preceding 7B run (arms at
    7.40 t/s vs a documented 13.4) and produced an impossible +65% (embedding
    load appearing to SPEED UP the LLM). Invalid.
  * Run #2 was clean on memory but the operator switched the power profile
    balanced -> performance mid-run, so arm A straddled the switch and cannot
    be differenced against B/C. Invalid for deltas (B-vs-C still valid).
  * The earlier LFM and 7B runs were entirely under `balanced`, so they are not
    comparable to each other or to docs/BENCHMARKS.md performance-profile rows.

This driver pins one profile for the whole sweep, unloads every resident model
between models, and waits for MemAvailable to recover before each run.

Usage: sweep.py
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
GEN_URL = "http://127.0.0.1:11434"
EMB_PID = os.environ.get("EMB_PID", "10463")

MODELS = [
    ("bench-phi4mini-t8",   "_phi4",  "phi4-mini 3.8B Q4_K_M t8"),
    ("bench-qwen25c7b-t8",  "_qwen7b", "qwen2.5-coder:7B Q4_K_M t8"),
    ("bench-tlfm25-t6-latest-8", "_lfm", "LFM2.5-2.6B Q4_K_M t8"),
]
MIN_AVAIL_MB = 3000
SETTLE_S = 25


def api(path, payload, port=11434, timeout=60):
    import urllib.request
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def mem_avail_mb():
    for ln in open("/proc/meminfo"):
        if ln.startswith("MemAvailable:"):
            return int(ln.split()[1]) // 1024
    return -1


def profile():
    try:
        return subprocess.run(["powerprofilesctl", "get"],
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return "?"


def resident(port=11434):
    try:
        return [m["name"] for m in api("/api/ps", {}, port, timeout=15).get("models", [])]
    except Exception:
        return []


def settle(tag):
    """Unload every resident model on both instances, then wait for RAM back."""
    for port in (11434, 11435):
        for name in resident(port):
            try:
                api("/api/generate", {"model": name, "prompt": "",
                                      "keep_alive": 0}, port, timeout=120)
                print(f"  [settle] unloaded {name} from :{port}", flush=True)
            except Exception as e:
                print(f"  [settle] {name} :{port} -> {type(e).__name__}", flush=True)
    time.sleep(SETTLE_S)
    for _ in range(12):
        a = mem_avail_mb()
        if a >= MIN_AVAIL_MB:
            print(f"  [settle] {tag}: MemAvailable {a} MB OK", flush=True)
            return True
        print(f"  [settle] {tag}: MemAvailable {a} MB < {MIN_AVAIL_MB}, waiting",
              flush=True)
        time.sleep(15)
    print(f"  [settle] {tag}: PROCEEDING LOW at {mem_avail_mb()} MB", flush=True)
    return False


def main():
    p0 = profile()
    print(f"power profile at sweep start: {p0}", flush=True)
    if p0 != "performance":
        print(f"WARNING: profile is '{p0}', not 'performance'. "
              f"Set it before trusting these numbers.", flush=True)
    env_base = dict(os.environ, EMB_PID=EMB_PID, RUNS="5", TOKENS="96")

    summary = {}
    for model, suffix, label in MODELS:
        print(f"\n{'#'*70}\n# {label}\n{'#'*70}", flush=True)
        settle(label)
        env = dict(env_base, GEN_MODEL=model, GEN_LABEL=label, OUT_SUFFIX=suffix)
        log = os.path.join(HERE, f"sweep_{suffix.lstrip('_')}_20261014.log")
        r = subprocess.run([sys.executable,
                            os.path.join(HERE, "emb_bench_onnx.py"), "all"],
                           env=env, stdout=open(log, "w"), stderr=subprocess.STDOUT)
        rf = os.path.join(HERE, f"emb_bench_onnx_results{suffix}.json")
        if r.returncode != 0 or not os.path.exists(rf):
            print(f"  !! {label} FAILED rc={r.returncode}; see {log}", flush=True)
            continue
        arms = json.load(open(rf))
        base = arms[0]["eval_tps_mean"]
        print(f"  {'arm':<34}{'t/s':>8}{'delta':>9}  MemAvail", flush=True)
        for a in arms:
            d = (a["eval_tps_mean"] - base) / base * 100
            print(f"  {a['label'][:34]:<34}{a['eval_tps_mean']:>8.2f}{d:>8.1f}%  "
                  f"{a.get('mem_available_mb')} MB", flush=True)
        summary[label] = {
            "profile": profile(),
            "arms": {a["label"]: {"tps": a["eval_tps_mean"],
                                  "sd": a["eval_tps_stdev"],
                                  "mem_avail_mb": a.get("mem_available_mb"),
                                  "embed_lat_ms": a["embed_latency_ms_mean"]}
                     for a in arms}}

    out = os.path.join(HERE, "sweep_summary_20261014.json")
    json.dump(summary, open(out, "w"), indent=2)
    print(f"\nwrote {out}   (profile {profile()})", flush=True)


if __name__ == "__main__":
    main()