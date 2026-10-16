#!/usr/bin/env python3
"""
Is the embedding load tax driven by THREAD COUNT and/or DUTY CYCLE?

Motivation (2026-10-14 sweep): core placement of the embedder made no measurable
difference to LLM throughput (0.0% / +1.4% / +0.2%), but continuous embedding load
cost a flat -12% to -13% across 2.6B-7B generators. That points at resource
pressure (threads / bandwidth), not core placement. This measures both knobs:

  X = embedder OMP_NUM_THREADS  (1, 2, 4)   -- restarted per setting
  Y = duty cycle                (100/50/25%) -- paced embed loop

Placement is pinned to E-cores (12-15) throughout, since placement was shown not
to matter. Generator fixed at bench-tlfm25-t6-latest-8 (num_thread 8) because it
iterates fastest (~21 t/s, ~4.7 s per 96-token run).

Duty cycle is enforced by sleep accounting on measured embed call latency, so
"50%" means 50% of wall-clock spent embedding, not a fixed request count.

RESTORES the production embedder (4 threads, 12-15) in a finally block.

Usage: embed_knobs.py
"""
import json, os, signal, statistics, subprocess, sys, threading, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = "http://127.0.0.1:11434"
EMB = "http://127.0.0.1:8090"
MODEL = "bench-tlfm25-t6-latest-8"
MODEL_LABEL = "LFM2.5-2.6B Q4_K_M t8"
PROMPT = ("Explain the difference between a coroutine and a thread "
          "in two sentences.")
RUNS, TOKENS = 5, 96
REPO = "/home/xnai/Documents/Projects/omega-engine-alpha"
PY = "/home/xnai/WanderGround/.venv/bin/python3"
OUT = os.path.join(HERE, "embed_knobs_results.json")


def post(url, payload, timeout=300):
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


def find_embedder():
    out = subprocess.run(["pgrep", "-f", "embedding_server.py"],
                         capture_output=True, text=True).stdout.split()
    return int(out[0]) if out else None


def stop_embedder():
    pid = find_embedder()
    if pid:
        subprocess.run(["kill", str(pid)], capture_output=True)
        time.sleep(3)
        if subprocess.run(["kill", "-0", str(pid)], capture_output=True).returncode == 0:
            subprocess.run(["kill", "-9", str(pid)], capture_output=True)
            time.sleep(2)
    return pid


def start_embedder(threads):
    env = dict(os.environ, OMP_NUM_THREADS=str(threads),
               TRUNCATE_DIM="1024",
               EMB_MODEL_DIR=f"{REPO}/models/embedding/qwen3-0.6b-onnx")
    subprocess.Popen(
        ["taskset", "-c", "12-15", PY, f"{REPO}/scripts/embedding_server.py"],
        env=env, stdout=open(os.path.join(HERE, "knobs_embed.log"), "a"),
        stderr=subprocess.STDOUT, cwd=REPO, start_new_session=True)
    for _ in range(60):
        time.sleep(2)
        try:
            # /health is a GET endpoint. v1 POSTed it -> 405 Method Not Allowed
            # -> start_embedder timed out and raised while the server was healthy.
            with urllib.request.urlopen(EMB + "/health", timeout=5) as r:
                h = json.loads(r.read())
            if h.get("model_loaded"):
                return find_embedder()
        except Exception:
            pass
    raise RuntimeError(f"embedder failed to start at {threads} threads")


class Hammer:
    """Paced embed loop. duty = fraction of wall-clock spent inside /embed."""

    def __init__(self, duty):
        self.duty = duty
        self.stop = threading.Event()
        self.lat, self.n, self.err = [], 0, 0

    def _loop(self):
        while not self.stop.is_set():
            t0 = time.perf_counter()
            try:
                post(EMB + "/embed", {"inputs": ["core-placement duty probe"]},
                     timeout=120)
                self.lat.append((time.perf_counter() - t0) * 1000)
                self.n += 1
            except Exception:
                self.err += 1
            spent = time.perf_counter() - t0
            if self.duty < 1.0:
                target = spent / self.duty
                self.stop.wait(max(0.0, target - spent))

    def start(self):
        self.th = threading.Thread(target=self._loop, daemon=True)
        self.th.start()
        time.sleep(5)          # let load ramp

    def finish(self):
        self.stop.set()
        self.th.join(timeout=10)


def gen_once():
    t0 = time.perf_counter()
    r = post(GEN + "/api/generate", {
        "model": MODEL, "prompt": PROMPT, "stream": False,
        "options": {"num_predict": TOKENS, "temperature": 0}}, timeout=300)
    wall = time.perf_counter() - t0
    n, ns = r.get("eval_count", 0), r.get("eval_duration", 1)
    return n / (ns / 1e9) if ns else None


def settle():
    for name in [MODEL]:
        try:
            post(GEN + "/api/generate",
                 {"model": name, "prompt": "", "keep_alive": 0}, timeout=120)
        except Exception:
            pass
    time.sleep(20)
    for _ in range(12):
        if mem_avail_mb() >= 3000:
            return mem_avail_mb()
        time.sleep(15)
    return mem_avail_mb()


def measure(duty, baseline):
    h = Hammer(duty)
    if duty > 0:
        h.start()
    post(GEN + "/api/generate", {"model": MODEL, "prompt": PROMPT, "stream": False,
                                 "options": {"num_predict": TOKENS, "temperature": 0}},
         timeout=300)                      # warm, discarded
    runs = [gen_once() for _ in range(RUNS)]
    if duty > 0:
        h.finish()
    if duty > 0 and h.n == 0:
        raise RuntimeError("hammer made zero calls - refusing to record")
    tps = [r for r in runs if r]
    dur = sum(h.lat) / 1000 if h.lat else 0
    return {"duty": duty, "tps_mean": round(statistics.mean(tps), 2),
            "tps_min": round(min(tps), 2), "tps_sd": round(statistics.pstdev(tps), 2),
            "delta_pct": round((statistics.mean(tps) - baseline) / baseline * 100, 1),
            "embed_calls": h.n, "embed_err": h.err,
            "embed_lat_ms": round(statistics.mean(h.lat), 2) if h.lat else None,
            "embed_duty_actual_pct": round(dur / (RUNS * TOKENS / tps[0] / 1000 + dur) * 100, 1)
            if h.lat else 0.0}


def main():
    prof = subprocess.run(["powerprofilesctl", "get"],
                          capture_output=True, text=True).stdout.strip()
    print(f"power profile: {prof}", flush=True)
    if prof != "performance":
        print("WARNING: not performance profile", flush=True)
    results = {}
    try:
        for threads in (1, 2, 4):
            print(f"\n{'='*66}\nEMBEDDER THREADS = {threads}\n{'='*66}", flush=True)
            stop_embedder()
            pid = start_embedder(threads)
            print(f"  embedder pid={pid} aff={subprocess.run(['taskset','-pc',str(pid)],capture_output=True,text=True).stdout.strip()}",
                  flush=True)
            a = settle()
            base = measure(0.0, 1.0)
            base["tps_mean"] = base["tps_mean"]; base.pop("delta_pct", None)
            base["delta_pct"] = 0.0
            print(f"  A idle (baseline)      {base['tps_mean']:6.2f} t/s "
                  f"(sd {base['tps_sd']})  memavail {a} MB", flush=True)
            results[threads] = [base]
            for duty in (1.0, 0.5, 0.25):
                r = measure(duty, base["tps_mean"])
                r["mem_available_mb"] = mem_avail_mb()
                results[threads].append(r)
                print(f"  duty {int(duty*100):3d}%  {r['tps_mean']:6.2f} t/s  "
                      f"{r['delta_pct']:+6.1f}%  embed {r['embed_calls']:4d} calls "
                      f"@ {r['embed_lat_ms']} ms  (actual duty {r['embed_duty_actual_pct']}%)",
                      flush=True)
    finally:
        print("\n[restore] restarting production embedder: 4 threads @ 12-15", flush=True)
        stop_embedder()
        p = start_embedder(4)
        print(f"[restore] pid={p} aff="
              f"{subprocess.run(['taskset','-pc',str(p)],capture_output=True,text=True).stdout.strip()}",
              flush=True)
        results["_meta"] = {"profile": prof, "generator": MODEL_LABEL,
                            "runs": RUNS, "tokens": TOKENS, "date": "2026-10-14"}
        json.dump(results, open(OUT, "w"), indent=2)
        print(f"wrote {OUT}", flush=True)


if __name__ == "__main__":
    main()