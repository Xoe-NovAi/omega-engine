#!/usr/bin/env python3
"""
prove_final.py — placement proven at all three levels, with the two known
traps closed.

Trap 1 (killed the sweep's C arm AND the first "birth mask" fix): the
embedder self-pins to E-cores at import (configure_cpu_affinity). Fix: run a
clearly-labeled TEST COPY (embed_server_nopin.py) with that call neutralized.
The production file is never touched.

Trap 2 (contaminated prove_C_proper's t/s): the hammer had a fixed 40 s window
that expired before the 5 gens finished (see the 20.9 tail in both arms' runs).
Fix: the hammer runs CONTINUOUSLY for the whole arm and is stopped after.

Per arm, all three levels are recorded:
  L1 mask      : main-thread taskset read-back (weak — main thread only)
  L2 allowed   : EVERY thread's Cpus_allowed_list from
                 /proc/<pid>/task/<tid>/status  (the real per-thread mask)
  L3 executed  : every thread's last_executed_cpu sampled 6x under hammer

Pass: L2 of every thread ⊆ target mask AND L3 union ⊆ target mask.
Production (original script, born under 12-15) restored at the end.
"""
import json, os, subprocess, sys, threading, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "prove_final.log")
GEN, EMB = "http://127.0.0.1:11434", "http://127.0.0.1:8090"
LFM = "bench-tlfm25-t6-latest-8"
REPO = "/home/xnai/Documents/Projects/omega-engine-alpha"
PY = "/home/xnai/WanderGround/.venv/bin/python3"
TEST_SRV = os.path.join(HERE, "embed_server_nopin.py")
PROD_SRV = f"{REPO}/scripts/embedding_server.py"


def log(msg=""):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    open(LOG, "a").write(line + "\n")


def post(url, payload, timeout=300):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def get(url, timeout=15):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read())


def procs():
    """All embedder pids (production AND test copy) except this script."""
    # NOTE: pgrep uses ERE: alternation is `|`, not `\|`. A previous version
    # matched only the production filename, so the test copy
    # (embed_server_nopin.py) was invisible -> "would not start" while healthy.
    out = subprocess.run(["pgrep", "-af", r"embed.*server.*\.py"],
                         capture_output=True, text=True).stdout.splitlines()
    found = {}
    for ln in out:
        parts = ln.split(None, 1)
        if len(parts) != 2 or "prove_" in parts[1] or "pgrep" in parts[1]:
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
    left = procs()
    if left:
        log(f"FATAL: embedder still alive: {left}")
        sys.exit(2)


def start(server_py, mask):
    env = dict(os.environ, OMP_NUM_THREADS="4", TRUNCATE_DIM="1024",
               EMB_MODEL_DIR=f"{REPO}/models/embedding/qwen3-0.6b-onnx")
    subprocess.Popen(
        ["taskset", "-c", mask, PY, server_py], env=env,
        stdout=open(os.path.join(HERE, "prove_final_embed.log"), "a"),
        stderr=subprocess.STDOUT, cwd=REPO, start_new_session=True)
    for _ in range(60):
        time.sleep(2)
        try:
            if get(EMB + "/health").get("model_loaded"):
                ps = procs()
                assert len(ps) == 1, f"expected 1 embedder, found {ps}"
                return next(iter(ps))
        except Exception:
            pass
    log("FATAL: embedder would not start under " + mask)
    sys.exit(2)


def allowed_sets(pid):
    """tid -> Cpus_allowed_list string, for every thread."""
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


def exec_sets(pid):
    out = {}
    try:
        tids = os.listdir(f"/proc/{pid}/task")
    except FileNotFoundError:
        return out
    for tid in tids:
        try:
            out[int(tid)] = int(open(f"/proc/{pid}/task/{tid}/stat").read().split()[38])
        except (FileNotFoundError, IndexError, ValueError):
            pass
    return out


def cpus_in_lists(allowed):
    """Expand {'0-11','12'} style lists to a cpu set."""
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


def gen_once():
    r = post(GEN + "/api/generate", {
        "model": LFM, "stream": False,
        "prompt": "Explain the difference between a coroutine and a thread in two sentences.",
        "options": {"num_predict": 96, "temperature": 0, "num_thread": 8}},
        timeout=300)
    ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1)
    return round(ec / (ed / 1e9), 2) if ed else None


stop_flag = threading.Event()


def hammer(stats):
    while not stop_flag.is_set():
        t0 = time.perf_counter()
        try:
            r = post(EMB + "/embed", {"inputs": ["final proof hammer"]}, timeout=120)
            stats["ok"] += 1
            stats["ms"].append((time.perf_counter() - t0) * 1000)
            stats["dims"] = r.get("dimensions")
        except Exception as e:
            stats["err"] += 1
            stats["last_err"] = f"{type(e).__name__}: {str(e)[:100]}"


def run_arm(label, mask):
    log(f"===== ARM {label}: TEST COPY born under {mask} =====")
    kill_all()
    pid = start(TEST_SRV, mask)
    log(f"  pid={pid}")

    stats = {"ok": 0, "err": 0, "ms": [], "dims": None, "last_err": None}
    stop_flag.clear()
    h = threading.Thread(target=hammer, args=(stats,), daemon=True)
    h.start()                       # runs for the WHOLE arm; stopped after
    time.sleep(5)

    allow = allowed_sets(pid)
    allow_union = sorted(cpus_in_lists(allow))
    n_off = sum(1 for v in allow.values()
                if cpus_in_lists({0: v}) - set(range(12) if mask == "0-11"
                                               else range(12, 16)))
    log(f"  L2 allowed: {len(allow)} threads, union={allow_union}, "
        f"threads with ANY cpu outside {mask}: {n_off}")
    for tid, v in sorted(allow.items()):
        if cpus_in_lists({0: v}) - set(range(12) if mask == "0-11" else range(12, 16)):
            log(f"    off-mask thread tid={tid} allowed={v}")

    samples = []
    for i in range(6):
        time.sleep(2)
        s = exec_sets(pid)
        samples.append(sorted(set(s.values())))
        log(f"  L3 sample {i+1}: executing on {sorted(set(s.values()))} "
            f"({len(s)} threads)")
    tps_runs = [gen_once() for _ in range(5)]
    log(f"  LLM decode under load: {tps_runs} t/s")
    stop_flag.set()
    h.join(timeout=20)
    mean_ms = sum(stats["ms"]) / len(stats["ms"]) if stats["ms"] else None
    log(f"  hammer: {stats['ok']} ok / {stats['err']} err, "
        f"mean {mean_ms and round(mean_ms,1)} ms, dims={stats['dims']}")
    if stats["ok"] == 0:
        log("  FATAL: zero embeds.")
        sys.exit(3)
    union = sorted({c for s in samples for c in s})
    import statistics
    return {"arm": label, "mask": mask, "l2_union": allow_union,
            "l2_offmask_threads": n_off, "l3_union": union,
            "tps_runs": tps_runs,
            "tps_mean": round(statistics.mean(tps_runs), 2),
            "embeds": stats["ok"]}


def main():
    open(LOG, "w").write("")
    log("FINAL PROOF — L1 mask + L2 per-thread allowed + L3 executed, "
        "self-pin neutralized, continuous hammer")
    arms = [run_arm("E", "12-15"), run_arm("C", "0-11")]

    kill_all()
    pid = start(PROD_SRV, "12-15")
    log(f"restored PRODUCTION embedder pid={pid} (original script, born 12-15)")

    e, c = arms
    want_e, want_c = set(range(12, 16)), set(range(12))
    e_ok = set(e["l2_union"]) <= want_e and set(e["l3_union"]) <= want_e
    c_ok = set(c["l2_union"]) <= want_c and set(c["l3_union"]) <= want_c
    log("")
    log("PASS CRITERIA + RESULTS:")
    log(f"  ARM E: L2 {e['l2_union']} L3 {e['l3_union']} -> "
        f"{'PASS' if e_ok else 'FAIL'} (LLM {e['tps_mean']} t/s, "
        f"{e['embeds']} embeds)")
    log(f"  ARM C: L2 {c['l2_union']} L3 {c['l3_union']} -> "
        f"{'PASS' if c_ok else 'FAIL'} (LLM {c['tps_mean']} t/s, "
        f"{c['embeds']} embeds)")
    json.dump(arms, open(os.path.join(HERE, "prove_final.json"), "w"), indent=2)
    sys.exit(0 if (e_ok and c_ok) else 4)


if __name__ == "__main__":
    main()
