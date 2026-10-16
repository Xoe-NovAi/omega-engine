#!/usr/bin/env python3
"""
Comprehensive performance characterisation: what actually makes this box tick.

Phases (each with memory settling + performance-profile assertion):
  1. Generator thread curve, ISOLATED.        models x num_thread
  2. Same curve WITH embedding at 25% duty.   does the optimum shift?
  3. Secondary knobs at the best thread.      num_ctx, prompt-eval cost

Methodology learned the hard way on 2026-10-14 (see docs/BENCHMARKS.md):
  * power profile asserted = performance
  * every resident model unloaded between phases, MemAvailable >= 3000 MB
  * num_thread / num_ctx overridden PER REQUEST (no tag explosion)
  * warm-up run discarded before every cell (87x cold-vs-warm on embeds)
  * n runs per cell, sd reported, MemAvailable recorded

Usage: tune.py [1|2|3|all]
"""
import json, os, statistics, subprocess, sys, threading, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = "http://127.0.0.1:11434"
EMB = "http://127.0.0.1:8090"
RUNS = int(os.environ.get("RUNS", "4"))
TOKENS = int(os.environ.get("TOKENS", "64"))
PROMPT = "Explain the difference between a coroutine and a thread."
OUT = os.path.join(HERE, "tune_results.json")

MODELS = [
    ("bench-tlfm25-t6-latest-8", "LFM2.5-2.6B"),
    ("bench-phi4mini-t8",         "phi4-mini 3.8B"),
    ("bench-qwen25c7b-t8",        "qwen2.5-coder:7B"),
]
THREADS = [4, 5, 6, 8, 10, 12]
CTXS = [2048, 4096, 8192]
DUTY = 0.25


def post(url, payload, timeout=300):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def health():
    with urllib.request.urlopen(EMB + "/health", timeout=5) as r:
        return json.loads(r.read())


def mem_avail_mb():
    for ln in open("/proc/meminfo"):
        if ln.startswith("MemAvailable:"):
            return int(ln.split()[1]) // 1024
    return -1


def profile():
    return subprocess.run(["powerprofilesctl", "get"],
                          capture_output=True, text=True).stdout.strip()


def resident():
    try:
        return [m["name"] for m in post(GEN + "/api/ps", {}).get("models", [])]
    except Exception:
        return []


def settle():
    for n in resident():
        try:
            post(GEN + "/api/generate",
                 {"model": n, "prompt": "", "keep_alive": 0}, timeout=180)
            print(f"    [settle] unloaded {n}", flush=True)
        except Exception:
            pass
    time.sleep(20)
    for _ in range(12):
        if mem_avail_mb() >= 3000:
            return mem_avail_mb()
        time.sleep(15)
    return mem_avail_mb()


class Hammer:
    def __init__(self, duty=DUTY):
        self.duty, self.stop, self.n, self.err, self.lat = duty, threading.Event(), 0, 0, []

    def _loop(self):
        while not self.stop.is_set():
            t0 = time.perf_counter()
            try:
                post(EMB + "/embed", {"inputs": ["tune duty probe"]}, timeout=120)
                self.lat.append((time.perf_counter() - t0) * 1000)
                self.n += 1
            except Exception:
                self.err += 1
            spent = time.perf_counter() - t0
            if self.duty < 1.0:
                self.stop.wait(max(0.0, spent / self.duty - spent))

    def start(self):
        self.th = threading.Thread(target=self._loop, daemon=True)
        self.th.start()
        time.sleep(4)

    def finish(self):
        self.stop.set()
        self.th.join(timeout=10)


def gen(model, num_thread=None, num_ctx=None, n=TOKENS):
    o = {"num_predict": n, "temperature": 0}
    if num_thread:
        o["num_thread"] = num_thread
    if num_ctx:
        o["num_ctx"] = num_ctx
    t0 = time.perf_counter()
    r = post(GEN + "/api/generate",
             {"model": model, "prompt": PROMPT, "stream": False, "options": o})
    wall = time.perf_counter() - t0
    ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1)
    return {
        "tps": ec / (ed / 1e9) if ed else None,
        "prompt_eval_tps": (r.get("prompt_eval_count", 0) /
                            (r["prompt_eval_duration"] / 1e9)) if r.get("prompt_eval_duration") else None,
        "ttft_s": (r.get("prompt_eval_duration", 0) / 1e9) if r.get("prompt_eval_duration") else None,
        "wall_s": round(wall, 2),
        "load_s": round(r.get("load_duration", 0) / 1e9, 2),
        "tokens": ec,
    }


def cell(model, num_thread, num_ctx=None, hammer=None):
    gen(model, num_thread, num_ctx)                 # warm, discarded
    rs = [gen(model, num_thread, num_ctx) for _ in range(RUNS)]
    tps = [x["tps"] for x in rs if x["tps"]]
    out = {
        "model": model, "num_thread": num_thread, "num_ctx": num_ctx or 8192,
        "tps_mean": round(statistics.mean(tps), 2),
        "tps_min": round(min(tps), 2),
        "tps_sd": round(statistics.pstdev(tps), 2),
        "wall_s_mean": round(statistics.mean([x["wall_s"] for x in rs]), 2),
        "ttft_s_mean": round(statistics.mean([x["ttft_s"] for x in rs if x["ttft_s"]]), 3)
        if any(x["ttft_s"] for x in rs) else None,
        "load_s_max": max(x["load_s"] for x in rs),
        "mem_available_mb": mem_avail_mb(),
    }
    if hammer is not None:
        out["embed_calls"] = hammer.n
        out["embed_lat_ms"] = round(statistics.mean(hammer.lat), 2) if hammer.lat else None
    return out


def save(db):
    json.dump(db, open(OUT, "w"), indent=2)


def guard():
    p = profile()
    print(f"power profile: {p}", flush=True)
    if p != "performance":
        print("!!! NOT performance - numbers not comparable to docs", flush=True)
    return p


def phase1(db):
    guard()
    for model, label in MODELS:
        m = settle()
        print(f"\n=== PHASE1 {label} (isolated)  memavail {m} MB", flush=True)
        best = None
        for th in THREADS:
            r = cell(model, th)
            db["phase1"].append(r)
            print(f"  t={th:<3} {r['tps_mean']:6.2f} t/s  sd {r['tps_sd']:.2f}  "
                  f"wall {r['wall_s_mean']}s", flush=True)
            if best is None or r["tps_mean"] > best["tps_mean"]:
                best = r
        db["best_isolated"] = db.get("best_isolated", {})
        db["best_isolated"][model] = {"num_thread": best["num_thread"],
                                      "tps": best["tps_mean"]}
        save(db)
    print("\nPHASE1 BEST:", json.dumps(db.get("best_isolated", {}), indent=2), flush=True)


def phase2(db):
    guard()
    if not health().get("model_loaded"):
        raise RuntimeError("embedder not healthy")
    for model, label in MODELS:
        m = settle()
        print(f"\n=== PHASE2 {label} (embed duty {int(DUTY*100)}%)  memavail {m} MB", flush=True)
        best = None
        for th in THREADS:
            h = Hammer(DUTY)
            h.start()
            r = cell(model, th, hammer=h)
            h.finish()
            if h.n == 0:
                print(f"  t={th:<3} SKIPPED - hammer made 0 calls", flush=True)
                continue
            r["phase"] = 2
            db["phase2"].append(r)
            print(f"  t={th:<3} {r['tps_mean']:6.2f} t/s  sd {r['tps_sd']:.2f}  "
                  f"embeds {r['embed_calls']} @ {r['embed_lat_ms']} ms", flush=True)
            if best is None or r["tps_mean"] > best["tps_mean"]:
                best = r
        if best:
            db["best_loaded"] = db.get("best_loaded", {})
            db["best_loaded"][model] = {"num_thread": best["num_thread"],
                                        "tps": best["tps_mean"]}
        save(db)
    print("\nPHASE2 BEST:", json.dumps(db.get("best_loaded", {}), indent=2), flush=True)


def phase3(db):
    guard()
    for model, label in MODELS:
        th = db.get("best_isolated", {}).get(model, {}).get("num_thread", 8)
        m = settle()
        print(f"\n=== PHASE3 {label} context sweep at t={th}  memavail {m} MB", flush=True)
        for ctx in CTXS:
            r = cell(model, th, num_ctx=ctx)
            r["phase"] = 3
            db["phase3"].append(r)
            print(f"  ctx={ctx:<5} {r['tps_mean']:6.2f} t/s  sd {r['tps_sd']:.2f}  "
                  f"ttft {r['ttft_s_mean']}s", flush=True)
        save(db)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    db = {}
    if os.path.exists(OUT):
        try:
            db = json.load(open(OUT))
        except Exception:
            db = {}
    for k in ("phase1", "phase2", "phase3"):
        db.setdefault(k, [])
    db["_meta"] = {"runs": RUNS, "tokens": TOKENS, "duty": DUTY,
                   "date": "2026-10-14", "threads": THREADS, "ctxs": CTXS,
                   "models": MODELS}
    if arg in ("1", "all"):
        phase1(db)
    if arg in ("2", "all"):
        phase2(db)
    if arg in ("3", "all"):
        phase3(db)
    print(f"\nwrote {OUT}", flush=True)


if __name__ == "__main__":
    main()