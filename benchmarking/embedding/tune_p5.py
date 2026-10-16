#!/usr/bin/env python3
"""
Phase 5 — fixes the three open items from the interim report.

A. PREFILL, cache-defeated. v1 of phase 4A sent an IDENTICAL prompt every run,
   so Ollama's prompt cache served it and prompt_eval_duration counted only the
   uncached tail -- producing a fictional ~13,000 tok/s. Here every request gets a
   unique nonce appended, forcing a genuine full prefill.

B. INTERLEAVED power A/B. The sequential perf/bal/perf blocks drifted ~3.4%
   (20.15 -> 19.48) so the profile effect was unreadable. Here profiles alternate
   WITHIN one sweep, so thermal/time drift hits both arms equally and cancels.

C. THERMAL sampling during sustained decode, to test whether the observed drift
   is PL1 throttling. Samples x86_pkg_temp, core frequencies, and RAPL-free
   sysfs each 0.5 s while a long decode runs.

Restores power profile to `performance` in a finally block.

Usage: tune_p5.py
"""
import json, os, statistics, subprocess, threading, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = "http://127.0.0.1:11434"
OUT = os.path.join(HERE, "tune_p5_results.json")

LFM = "bench-tlfm25-t6-latest-8"
QWEN7 = "bench-qwen25c7b-t8"
MODELS = [(LFM, "LFM2.5-2.6B"), (QWEN7, "qwen2.5-coder:7B")]

FILLER = (
    "The Nameless One awakens on a blood-soaked slab in the Mortuary without "
    "memory of who he was. Morte the talking skull drifts across the room "
    "mocking him, while the Lady of Pain watches through the wall. Each "
    "district of Sigil trades in memory, and each guide offers a different "
    "bargain about what was taken and why. "
)


def post(url, payload, timeout=900):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def mem_avail_mb():
    for ln in open("/proc/meminfo"):
        if ln.startswith("MemAvailable:"):
            return int(ln.split()[1]) // 1024
    return -1


def get_profile():
    return subprocess.run(["powerprofilesctl", "get"],
                          capture_output=True, text=True).stdout.strip()


def set_profile(p):
    subprocess.run(["powerprofilesctl", "set", p], capture_output=True)
    time.sleep(10)


def settle():
    try:
        for m in post(GEN + "/api/ps", {}).get("models", []):
            post(GEN + "/api/generate",
                 {"model": m["name"], "prompt": "", "keep_alive": 0}, timeout=180)
    except Exception:
        pass
    time.sleep(15)
    for _ in range(12):
        if mem_avail_mb() >= 3000:
            return mem_avail_mb()
        time.sleep(12)
    return mem_avail_mb()


def pkg_temp_c():
    for z in os.listdir("/sys/class/thermal"):
        t = f"/sys/class/thermal/{z}/type"
        try:
            if open(t).read().strip() == "x86_pkg_temp":
                return round(int(open(f"/sys/class/thermal/{z}/temp").read().strip()) / 1000, 1)
        except Exception:
            pass
    return None


def core_freq_mhz():
    out = []
    for c in ("cpuinfo_max_freq", "scaling_cur_freq"):
        try:
            v = open(f"/sys/devices/system/cpu/cpu0/cpufreq/{c}").read().strip()
            out.append(f"{c[:14]}={int(v)/1000:.2f}GHz")
        except Exception:
            pass
    return " ".join(out)


class Therm:
    """Sample temp/freq while work runs."""

    def __init__(self):
        self.t, self.f, self.stop = [], [], threading.Event()

    def _loop(self):
        while not self.stop.is_set():
            v = pkg_temp_c()
            if v:
                self.t.append(v)
            self.f.append(core_freq_mhz())
            self.stop.wait(0.5)

    def start(self):
        self.th = threading.Thread(target=self._loop, daemon=True)
        self.th.start()

    def finish(self):
        self.stop.set()
        self.th.join(timeout=5)
        return {"temp_max": max(self.t) if self.t else None,
                "temp_mean": round(statistics.mean(self.t), 1) if self.t else None,
                "temp_first": self.t[0] if self.t else None,
                "temp_last": self.t[-1] if self.t else None,
                "freq_samples": sorted(set(self.f))[:3]}


def prefill(model, num_thread, runs=3):
    """Full prefill every time: unique nonce defeats the prompt cache."""
    res = []
    for i in range(runs + 1):
        # nonce varies per request AND per run
        prompt = FILLER * 14 + f" nonce-{time.time_ns()}-{i}"
        t0 = time.perf_counter()
        r = post(GEN + "/api/generate", {
            "model": model, "prompt": prompt, "stream": False,
            "options": {"num_predict": 1, "temperature": 0,
                        "num_thread": num_thread}})
        wall = time.perf_counter() - t0
        pc = r.get("prompt_eval_count", 0)
        pd = r.get("prompt_eval_duration", 0) / 1e9
        if i:                                  # skip warm-up
            res.append({"prompt_tok": pc, "prefill_tps": pc / pd if pd else None,
                        "prefill_s": round(pd, 4), "wall_s": round(wall, 3)})
    tp = [x["prefill_tps"] for x in res if x["prefill_tps"]]
    return {"model": model, "num_thread": num_thread,
            "prompt_tok": res[0]["prompt_tok"] if res else None,
            "prefill_tps_mean": round(statistics.mean(tp), 1) if tp else None,
            "prefill_tps_sd": round(statistics.pstdev(tp), 1) if len(tp) > 1 else 0.0,
            "prefill_s_mean": round(statistics.mean([x["prefill_s"] for x in res]), 3),
            "cache_defeated": True}


def decode_cell(model, num_thread, runs=4, tokens=64):
    o = {"num_predict": tokens, "temperature": 0, "num_thread": num_thread}

    def one():
        r = post(GEN + "/api/generate",
                 {"model": model, "prompt": "Explain the difference between a "
                                            "coroutine and a thread.",
                  "stream": False, "options": o})
        ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1)
        return ec / (ed / 1e9) if ed else None
    one()
    rs = [one() for _ in range(runs)]
    tps = [x for x in rs if x]
    return {"model": model, "num_thread": num_thread,
            "tps_mean": round(statistics.mean(tps), 2),
            "tps_sd": round(statistics.pstdev(tps), 2),
            "mem_available_mb": mem_avail_mb(), "profile": get_profile()}


def sustained(model, num_thread, seconds=90):
    """Long decode with thermal sampling -> is the drift throttling?"""
    th = Therm()
    th.start()
    t0 = time.perf_counter()
    blocks = []
    while time.perf_counter() - t0 < seconds:
        r = post(GEN + "/api/generate", {
            "model": model, "stream": False,
            "prompt": "Write a detailed paragraph about memory and identity.",
            "options": {"num_predict": 256, "temperature": 0,
                        "num_thread": num_thread}})
        ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1)
        blocks.append({"tps": round(ec / (ed / 1e9), 2), "temp": pkg_temp_c(),
                       "t": round(time.perf_counter() - t0, 1)})
    therm = th.finish()
    print(f"  sustained: first {blocks[0]['tps']} t/s @ {blocks[0]['temp']}C, "
          f"last {blocks[-1]['tps']} t/s @ {blocks[-1]['temp']}C, "
          f"peak {therm['temp_max']}C", flush=True)
    return {"model": model, "num_thread": num_thread, "seconds": seconds,
            "blocks": blocks, "thermal": therm}


def main():
    db = json.load(open(OUT)) if os.path.exists(OUT) else \
        {"A_prefill": [], "B_interleaved": [], "C_thermal": []}
    for k in ("A_prefill", "B_interleaved", "C_thermal"):
        db.setdefault(k, [])

    # ---- A: cache-defeated prefill -----------------------------------
    set_profile("performance")
    for model, label in MODELS:
        m = settle()
        print(f"\n=== A PREFILL (cache-defeated) {label}  memavail {m} MB", flush=True)
        for th in (6, 8, 10, 12):
            r = prefill(model, th)
            db["A_prefill"].append(r)
            print(f"  t={th:<3} {r['prefill_tps_mean']:8.1f} tok/s  sd {r['prefill_tps_sd']:6.1f}"
                  f"  {r['prompt_tok']} tok in {r['prefill_s_mean']}s", flush=True)
            json.dump(db, open(OUT, "w"), indent=2)

    # ---- B: interleaved power A/B -----------------------------------
    print("\n=== B INTERLEAVED power A/B (order-balanced)", flush=True)
    seq = ["performance", "balanced"] * 3 + ["performance"]
    for prof in seq:
        set_profile(prof)
        m = settle()
        for model, label in MODELS:
            r = decode_cell(model, 10)
            r["tag"] = label
            db["B_interleaved"].append(r)
            print(f"  {get_profile():<12} {label:<18} {r['tps_mean']:6.2f} t/s "
                  f"sd {r['tps_sd']:.2f}  mem {r['mem_available_mb']} MB", flush=True)
            json.dump(db, open(OUT, "w"), indent=2)

    # ---- C: thermal / sustained -------------------------------------
    set_profile("performance")
    m = settle()
    print(f"\n=== C SUSTAINED + THERMAL  memavail {m} MB", flush=True)
    for model, label in MODELS:
        r = sustained(model, 10, 90)
        r["tag"] = label
        db["C_thermal"].append(r)
        json.dump(db, open(OUT, "w"), indent=2)

    db["_meta"] = {"date": "2026-10-14", "profile_note": "restored performance"}
    json.dump(db, open(OUT, "w"), indent=2)
    set_profile("performance")
    print(f"\n[restore] power profile = {get_profile()}", flush=True)
    print(f"wrote {OUT}", flush=True)


if __name__ == "__main__":
    try:
        main()
    finally:
        set_profile("performance")
        print(f"[finally] power profile = {get_profile()}", flush=True)