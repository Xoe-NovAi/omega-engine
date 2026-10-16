#!/usr/bin/env python3
"""
Phase 4 — the two gaps left by tune.py.

A. PROMPT-EVAL (prefill) throughput. Every sweep so far measured DECODE on a
   ~12-token prompt. Real agent turns carry hundreds of system-prompt + history
   tokens, and docs/BENCHMARKS.md §C already showed WebUI paying 1.69 s of
   prefill for a 155-token prompt. If prefill scales differently with
   num_thread, the whole thread-count recommendation is wrong for agentic use.

B. POWER PROFILE A/B. Every clean measurement so far was `performance`. The only
   balanced-vs-performance comparison in the docs is contaminated (profile
   switched mid-run). Clean A/B: same model, same threads, same cell, one
   profile, memory settled, profile switched ONLY between blocks.

Usage: tune_p4.py
"""
import json, os, statistics, subprocess, sys, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = "http://127.0.0.1:11434"
OUT = os.path.join(HERE, "tune_p4_results.json")

LFM = "bench-tlfm25-t6-latest-8"
QWEN7 = "bench-qwen25c7b-t8"
THREADS = [6, 8, 10, 12]
FILLER = (
    "The Nameless One awakens on a blood-soaked slab in the Mortuary without "
    "memory of who he was. Morte the talking skull drifts across the room "
    "mocking him, while the Lady of Pain watches through the wall. Each "
    "district of Sigil trades in memory, and each guide offers a different "
    "bargain about what was taken and why. "
)


def post(url, payload, timeout=600):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def mem_avail_mb():
    for ln in open("/proc/meminfo"):
        if ln.startswith("MemAvailable:"):
            return int(ln.split()[1]) // 1024
    return -1


def set_profile(p):
    subprocess.run(["powerprofilesctl", "set", p], capture_output=True)
    time.sleep(12)          # let intel_pstate settle before measuring


def get_profile():
    return subprocess.run(["powerprofilesctl", "get"],
                          capture_output=True, text=True).stdout.strip()


def settle():
    try:
        for m in post(GEN + "/api/ps", {}).get("models", []):
            post(GEN + "/api/generate",
                 {"model": m["name"], "prompt": "", "keep_alive": 0}, timeout=180)
            print(f"    [settle] unloaded {m['name']}", flush=True)
    except Exception:
        pass
    time.sleep(20)
    for _ in range(12):
        if mem_avail_mb() >= 3000:
            return mem_avail_mb()
        time.sleep(15)
    return mem_avail_mb()


def prefill(model, num_thread, prompt, runs=3):
    def one():
        t0 = time.perf_counter()
        r = post(GEN + "/api/generate", {
            "model": model, "prompt": prompt, "stream": False,
            "options": {"num_predict": 1, "temperature": 0,
                        "num_thread": num_thread}})
        wall = time.perf_counter() - t0
        pc = r.get("prompt_eval_count", 0)
        pd = r.get("prompt_eval_duration", 0) / 1e9
        return {"prompt_tok": pc, "prefill_tps": pc / pd if pd else None,
                "prefill_s": round(pd, 3), "wall_s": round(wall, 2),
                "load_s": round(r.get("load_duration", 0) / 1e9, 2)}
    one()                                   # warm, discarded
    rs = [one() for _ in range(runs)]
    tp = [x["prefill_tps"] for x in rs if x["prefill_tps"]]
    return {"model": model, "num_thread": num_thread,
            "prompt_tok": rs[0]["prompt_tok"],
            "prefill_tps_mean": round(statistics.mean(tp), 1) if tp else None,
            "prefill_tps_sd": round(statistics.pstdev(tp), 1) if len(tp) > 1 else 0.0,
            "prefill_s_mean": round(statistics.mean([x["prefill_s"] for x in rs]), 3),
            "load_s_max": max(x["load_s"] for x in rs),
            "mem_available_mb": mem_avail_mb(),
            "profile": get_profile()}


def decode_cell(model, num_thread, runs=4, tokens=64):
    o = {"num_predict": tokens, "temperature": 0, "num_thread": num_thread}

    def one():
        r = post(GEN + "/api/generate",
                 {"model": model, "prompt": "Explain the difference between a "
                                            "coroutine and a thread.", "stream": False,
                  "options": o})
        ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1)
        return ec / (ed / 1e9) if ed else None
    one()
    rs = [one() for _ in range(runs)]
    tps = [x for x in rs if x]
    return {"model": model, "num_thread": num_thread,
            "tps_mean": round(statistics.mean(tps), 2),
            "tps_sd": round(statistics.pstdev(tps), 2),
            "mem_available_mb": mem_avail_mb(), "profile": get_profile()}


def main():
    db = json.load(open(OUT)) if os.path.exists(OUT) else {"A_prefill": [], "B_power": []}
    db.setdefault("A_prefill", [])
    db.setdefault("B_power", [])
    prompt = FILLER * 14                       # long, agent-like prefill

    print(f"profile now: {get_profile()}", flush=True)

    # ---- A: prefill vs num_thread -------------------------------------
    for model, label in ((LFM, "LFM2.5-2.6B"), (QWEN7, "qwen2.5-coder:7B")):
        m = settle()
        print(f"\n=== A PREFILL {label}  memavail {m} MB", flush=True)
        for th in THREADS:
            r = prefill(model, th, prompt)
            db["A_prefill"].append(r)
            print(f"  t={th:<3} {r['prefill_tps_mean']:7.1f} tok/s  "
                  f"sd {r['prefill_tps_sd']:.1f}  {r['prompt_tok']} tok in "
                  f"{r['prefill_s_mean']}s", flush=True)
            json.dump(db, open(OUT, "w"), indent=2)

    # ---- B: clean power-profile A/B ----------------------------------
    try:
        for prof in ("performance", "balanced", "performance"):
            set_profile(prof)
            m = settle()
            print(f"\n=== B POWER profile={get_profile()}  memavail {m} MB", flush=True)
            for model, label in ((LFM, "LFM2.5-2.6B"), (QWEN7, "qwen2.5-coder:7B")):
                r = decode_cell(model, 10)
                r["tag"] = label
                db["B_power"].append(r)
                print(f"  {label:<18} {r['tps_mean']:6.2f} t/s  sd {r['tps_sd']:.2f}",
                      flush=True)
                json.dump(db, open(OUT, "w"), indent=2)
    finally:
        set_profile("performance")
        print(f"\n[restore] power profile = {get_profile()}", flush=True)

    db["_meta"] = {"date": "2026-10-14", "threads": THREADS,
                   "prompt_tokens_estimate": len(prompt.split())}
    json.dump(db, open(OUT, "w"), indent=2)
    print(f"wrote {OUT}", flush=True)


if __name__ == "__main__":
    main()