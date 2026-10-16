#!/usr/bin/env python3
"""
rate_match.py — the placement effect with rate HELD CONSTANT.

The proven-placement run (prove_final.py) showed C worse than E by -14.6%,
but the latency-driven hammer completed 1727 embeds in C vs 1075 in E, so
placement and rate were entangled. Here both arms are driven at IDENTICAL
paced rates, so any remaining gap is placement, not load.

Design (per model: LFM-2.6B t=10, then phi4-mini t=10):
  arms  : E (test copy born 12-15), C (test copy born 0-11)
  rates : idle, 8/s, 16/s, saturated
  order : E-idle, C-idle, E-8, C-8, E-16, C-16, E-sat, C-sat (interleaved:
          drift hits both arms equally)
  per cell: L3 executed-union spot check, 5 gens, embed lat distribution,
            MemAvailable, power profile
  per arm : full L2 (every thread's Cpus_allowed_list) — abort on off-mask

Fail-fast: zero embeds in a hammer cell, any L2 off-mask thread, or embedder
that won't start => abort, never record. Production (original script, born
12-15) restored in a finally block.

Usage: rate_match.py   (runs LFM then phi4-mini; ~20 min total)
"""
import json, os, statistics, subprocess, sys, threading, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "rate_match.log")
OUT = os.path.join(HERE, "rate_match_results.json")
GEN, EMB = "http://127.0.0.1:11434", "http://127.0.0.1:8090"
REPO = "/home/xnai/Documents/Projects/omega-engine-alpha"
PY = "/home/xnai/WanderGround/.venv/bin/python3"
TEST_SRV = os.path.join(HERE, "embed_server_nopin.py")
PROD_SRV = f"{REPO}/scripts/embedding_server.py"
PROMPT = "Explain the difference between a coroutine and a thread in two sentences."

MODELS = [
    ("bench-tlfm25-t6-latest-8", 10, "LFM2.5-2.6B"),
    ("bench-phi4mini-t8", 10, "phi4-mini 3.8B"),
]
RATES = [0, 8, 16, "sat"]
RUNS, TOKENS = 5, 96


def log(msg=""):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    open(LOG, "a").write(line + "\n")


def die(msg):
    log(f"FATAL: {msg}")
    sys.exit(2)


def post(url, payload, timeout=300):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def get(url, timeout=15):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read())


def mem_avail_mb():
    for ln in open("/proc/meminfo"):
        if ln.startswith("MemAvailable:"):
            return int(ln.split()[1]) // 1024
    return -1


def profile():
    return subprocess.run(["powerprofilesctl", "get"],
                          capture_output=True, text=True).stdout.strip()


def procs():
    out = subprocess.run(["pgrep", "-af", r"embed.*server.*\.py"],
                         capture_output=True, text=True).stdout.splitlines()
    found = {}
    for ln in out:
        parts = ln.split(None, 1)
        if len(parts) != 2 or "rate_match" in parts[1] or "pgrep" in parts[1]:
            continue
        found[int(parts[0])] = parts[1]
    return found


def kill_all():
    for p in procs():
        subprocess.run(["kill", str(p)], capture_output=True)
    time.sleep(4)
    for p in procs():
        subprocess.run(["kill", "-9", str(p)], capture_output=True)
    time.sleep(2)
    if procs():
        die(f"embedder still alive: {procs()}")


def start(server_py, mask):
    env = dict(os.environ, OMP_NUM_THREADS="4", TRUNCATE_DIM="1024",
               EMB_MODEL_DIR=f"{REPO}/models/embedding/qwen3-0.6b-onnx")
    subprocess.Popen(
        ["taskset", "-c", mask, PY, server_py], env=env,
        stdout=open(os.path.join(HERE, "rate_match_embed.log"), "a"),
        stderr=subprocess.STDOUT, cwd=REPO, start_new_session=True)
    for _ in range(60):
        time.sleep(2)
        try:
            if get(EMB + "/health").get("model_loaded"):
                ps = procs()
                if len(ps) == 1:
                    return next(iter(ps))
                die(f"expected 1 embedder, found {ps}")
        except Exception:
            pass
    die("embedder would not start under " + mask)


def allowed_map(pid):
    out = {}
    try:
        tids = os.listdir(f"/proc/{pid}/task")
    except FileNotFoundError:
        return out
    for tid in tids:
        try:
            for ln in open(f"/proc/{pid}/task/{tid}/status"):
                if ln.startswith("Cpus_allowed_list:"):
                    out[int(tid)] = ln.split(":", 1)[1].strip()
        except FileNotFoundError:
            pass
    return out


def exec_union(pid):
    s = set()
    try:
        tids = os.listdir(f"/proc/{pid}/task")
    except FileNotFoundError:
        return []
    for tid in tids:
        try:
            s.add(int(open(f"/proc/{pid}/task/{tid}/stat").read().split()[38]))
        except (FileNotFoundError, IndexError, ValueError):
            pass
    return sorted(s)


def expand(allowed):
    s = set()
    for v in allowed.values():
        for part in v.split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-")
                s.update(range(int(a), int(b) + 1))
            elif part:
                s.add(int(part))
    return s


stop_flag = threading.Event()


def hammer_paced(rate, stats):
    """Fixed-rate loop. rate='sat' means back-to-back (no pacing)."""
    interval = None if rate == "sat" else 1.0 / rate
    while not stop_flag.is_set():
        t0 = time.perf_counter()
        try:
            r = post(EMB + "/embed", {"inputs": ["rate-matched hammer"]}, timeout=120)
            stats["ok"] += 1
            stats["ms"].append((time.perf_counter() - t0) * 1000)
            stats["dims"] = r.get("dimensions")
        except Exception as e:
            stats["err"] += 1
            stats["last_err"] = f"{type(e).__name__}: {str(e)[:100]}"
        if interval is not None:
            stop_flag.wait(max(0.0, interval - (time.perf_counter() - t0)))


def gen_once(model, thread):
    r = post(GEN + "/api/generate", {
        "model": model, "stream": False, "prompt": PROMPT,
        "options": {"num_predict": TOKENS, "temperature": 0,
                    "num_thread": thread}}, timeout=300)
    ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1)
    return {"tps": round(ec / (ed / 1e9), 2) if ed else None,
            "load_s": round(r.get("load_duration", 0) / 1e9, 2)}


def settle_llm():
    try:
        for m in post(GEN + "/api/ps", {}, ).get("models", []):
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


def run_cell(model, thread, label, rate, pid):
    # NOTE 2026-10-16: label arrives as "<model-tag> arm-<E|C>"; the arm used
    # to be recovered as label.split()[0], which yields the MODEL tag, not the
    # arm. Every downstream summary then silently matched nothing. Parse it here.
    global stop_flag
    stop_flag = threading.Event()
    stats = {"ok": 0, "err": 0, "ms": [], "dims": None, "last_err": None}
    th = None
    if rate != 0:
        th = threading.Thread(target=hammer_paced, args=(rate, stats), daemon=True)
        th.start()
        time.sleep(5)
    l3 = []
    for _ in range(4):
        time.sleep(2)
        l3.append(exec_union(pid))
    gen_once(model, thread)                      # warm, discarded
    runs = [gen_once(model, thread) for _ in range(RUNS)]
    if th:
        stop_flag.set()
        th.join(timeout=20)
    tps = [r["tps"] for r in runs if r["tps"]]
    if rate != 0 and stats["ok"] == 0:
        die(f"{label} rate={rate}: hammer completed zero embeds.")
    arm = label.rsplit("arm-", 1)[-1] if "arm-" in label else label.split()[0]
    cell = {"model": model, "thread": thread, "arm": arm,
            "rate": rate, "tps_runs": tps,
            "tps_mean": round(statistics.mean(tps), 2),
            "tps_sd": round(statistics.pstdev(tps), 2) if len(tps) > 1 else 0.0,
            "load_s_max": max(r["load_s"] for r in runs),
            "l3_unions": l3,
            "l3_union_all": sorted({c for s in l3 for c in s}),
            "embeds": stats["ok"], "embed_err": stats["err"],
            "embed_lat_mean": round(statistics.mean(stats["ms"]), 1) if stats["ms"] else None,
            "embed_lat_min": round(min(stats["ms"]), 1) if stats["ms"] else None,
            "embed_dims": stats["dims"],
            "mem_available_mb": mem_avail_mb(), "profile": profile()}
    ach = (stats["ok"] / (sum(stats["ms"]) / 1000)) if stats["ms"] else 0
    log(f"  [{label} @ {rate}] LLM {cell['tps_mean']} t/s (sd {cell['tps_sd']}) | "
        f"embeds {stats['ok']} (~{ach:.0f}/s) @ {cell['embed_lat_mean']} ms | "
        f"L3 {cell['l3_union_all']} | mem {cell['mem_available_mb']} MB")
    return cell


def main():
    open(LOG, "w").write("")
    if profile() != "performance":
        log(f"WARNING: profile is {profile()}, not performance — recording anyway")
    db = {"cells": []}
    try:
        for model, thread, label in [(m, t, l) for m, t, l in MODELS]:
            log(f"##### {label} (num_thread {thread}) #####")
            m0 = settle_llm()
            log(f"  settled, MemAvailable {m0} MB")
            # interleaved by rate: both arms see the same drift window.
            # L2 (every thread's mask) is verified on EVERY start, not once:
            # birth masks are the whole point, and a single check would leave
            # 7 restarts unverified.
            for rate in RATES:
                for arm in ("E", "C"):
                    kill_all()
                    mask = "12-15" if arm == "E" else "0-11"
                    pid = start(TEST_SRV, mask)
                    am = allowed_map(pid)
                    want = set(range(12, 16)) if arm == "E" else set(range(12))
                    off = [t for t, v in am.items() if expand({0: v}) - want]
                    log(f"  ARM {arm} pid={pid}: {len(am)} threads, "
                        f"L2 union={sorted(expand(am))}, off-mask={len(off)}")
                    if off:
                        die(f"ARM {arm}: {len(off)} threads born off-mask, "
                            f"e.g. {off[:3]}")
                    cell = run_cell(model, thread, f"{label} arm-{arm}", rate, pid)
                    db["cells"].append(cell)
                    json.dump(db, open(OUT, "w"), indent=2)
    finally:
        kill_all()
        pid = start(PROD_SRV, "12-15")
        log(f"restored PRODUCTION embedder pid={pid} (original script, born 12-15)")

    # summary table
    log("\n===== RATE-MATCHED SUMMARY (LLM t/s) =====")
    for model, _, label in MODELS:
        log(f"--- {label} ---")
        base = {}
        for rate in RATES:
            row = {}
            for arm in ("E", "C"):
                cs = [c for c in db["cells"]
                      if c["model"] == model and c["arm"] == arm and c["rate"] == rate]
                if cs:
                    row[arm] = cs[0]
            if row:
                e, c = row.get("E"), row.get("C")
                if e and c:
                    gap = (c["tps_mean"] - e["tps_mean"]) / e["tps_mean"] * 100
                    log(f"  rate={rate!s:>4}: E {e['tps_mean']:6.2f} "
                        f"(n_emb {e['embeds']:4d} @ {e['embed_lat_mean']} ms) | "
                        f"C {c['tps_mean']:6.2f} "
                        f"(n_emb {c['embeds']:4d} @ {c['embed_lat_mean']} ms) | "
                        f"gap {gap:+.1f}%")
    log(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
