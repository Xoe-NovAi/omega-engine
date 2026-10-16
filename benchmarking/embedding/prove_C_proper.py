#!/usr/bin/env python3
"""
prove_C_proper.py — the VALID P-core arm.

Lesson from prove_placement.py: `taskset -p <tgid>` (sched_setaffinity on the
thread-group id) changes ONLY the main thread's mask. The ONNX intra-op pool,
born under 12-15, kept its birth masks — so the sweep's "embed on P-cores" arm
only ever moved the main thread, and most embedding compute stayed on E-cores.
That is why B vs C looked identical: the C arm never existed as designed.

Correct procedure: BIRTH the process under the target mask (taskset at exec),
so every thread inherits it. Then prove union ⊆ {0..11} under sustained hammer,
then measure LLM t/s. Same for a from-birth E arm for symmetry.

Pass criteria:
  ARM C: union of ALL sampled embed-thread CPUs ⊆ {0..11}, zero samples on 12+.
  ARM E: union ⊆ {12..15}, zero samples on 0..11.
Production (12-15, born under mask) is restored at the end.
"""
import json, os, subprocess, sys, threading, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "prove_C_proper.log")
GEN, EMB = "http://127.0.0.1:11434", "http://127.0.0.1:8090"
LFM = "bench-tlfm25-t6-latest-8"
REPO = "/home/xnai/Documents/Projects/omega-engine-alpha"
PY = "/home/xnai/WanderGround/.venv/bin/python3"


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


def kill_embedder():
    out = subprocess.run(["pgrep", "-f", "embedding_server.py"],
                         capture_output=True, text=True).stdout.split()
    me = str(os.getpid())
    for p in out:
        if p == me:
            continue
        try:
            if "prove_" in open(f"/proc/{p}/cmdline").read().replace("\0", " "):
                continue
        except FileNotFoundError:
            continue
        subprocess.run(["kill", p], capture_output=True)
    time.sleep(4)
    # SIGKILL stragglers that are still embedding_server (not this script)
    out = subprocess.run(["pgrep", "-f", "embedding_server.py"],
                         capture_output=True, text=True).stdout.split()
    for p in out:
        if p == me:
            continue
        try:
            if "prove_" in open(f"/proc/{p}/cmdline").read().replace("\0", " "):
                continue
        except FileNotFoundError:
            continue
        subprocess.run(["kill", "-9", p], capture_output=True)
    time.sleep(2)


def start_embedder(mask):
    """Birth the process UNDER the mask: taskset at exec, not after."""
    env = dict(os.environ, OMP_NUM_THREADS="4", TRUNCATE_DIM="1024",
               EMB_MODEL_DIR=f"{REPO}/models/embedding/qwen3-0.6b-onnx")
    subprocess.Popen(
        ["taskset", "-c", mask, PY, f"{REPO}/scripts/embedding_server.py"],
        env=env, stdout=open(os.path.join(HERE, "prove_C_embed.log"), "a"),
        stderr=subprocess.STDOUT, cwd=REPO, start_new_session=True)
    for _ in range(60):
        time.sleep(2)
        try:
            if get(EMB + "/health").get("model_loaded"):
                return find_embedder()
        except Exception:
            pass
    log("FATAL: embedder would not start under mask " + mask)
    sys.exit(2)


def find_embedder():
    out = subprocess.run(["pgrep", "-f", "embedding_server.py"],
                         capture_output=True, text=True).stdout.split()
    me = str(os.getpid())
    for p in out:
        if p == me:
            continue
        try:
            cl = open(f"/proc/{p}/cmdline").read().replace("\0", " ")
            if "embedding_server.py" in cl and "prove_" not in cl:
                return int(p)
        except FileNotFoundError:
            pass
    return None


def thread_cpus(pid):
    out = {}
    try:
        tids = os.listdir(f"/proc/{pid}/task")
    except FileNotFoundError:
        return out
    for tid in tids:
        try:
            st = open(f"/proc/{pid}/task/{tid}/stat").read().split()
            out[int(tid)] = int(st[38])
        except (FileNotFoundError, IndexError, ValueError):
            pass
    return out


def hammer(seconds, stats):
    end = time.perf_counter() + seconds
    while time.perf_counter() < end:
        t0 = time.perf_counter()
        try:
            r = post(EMB + "/embed", {"inputs": ["proper-C hammer"]}, timeout=120)
            stats["ok"] += 1
            stats["ms"].append((time.perf_counter() - t0) * 1000)
            stats["dims"] = r.get("dimensions")
        except Exception as e:
            stats["err"] += 1
            stats["last_err"] = f"{type(e).__name__}: {str(e)[:100]}"


def gen_once():
    r = post(GEN + "/api/generate", {
        "model": LFM, "stream": False,
        "prompt": "Explain the difference between a coroutine and a thread in two sentences.",
        "options": {"num_predict": 96, "temperature": 0, "num_thread": 8}},
        timeout=300)
    ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1)
    return round(ec / (ed / 1e9), 2) if ed else None


def run_arm(label, mask):
    log(f"===== ARM {label}: embedder BORN under {mask} =====")
    kill_embedder()
    pid = start_embedder(mask)
    got = subprocess.run(["taskset", "-pc", str(pid)],
                         capture_output=True, text=True).stdout
    log(f"  pid={pid}, main-thread read-back: {got.split('list:')[-1].strip()}")

    stats = {"ok": 0, "err": 0, "ms": [], "dims": None, "last_err": None}
    h = threading.Thread(target=hammer, args=(40, stats), daemon=True)
    h.start()
    time.sleep(5)
    samples = []
    for i in range(6):
        time.sleep(2)
        s = thread_cpus(pid)
        samples.append(sorted(set(s.values())))
        log(f"  sample {i+1}: embed threads on {sorted(set(s.values()))} "
            f"({len(s)} threads)")
    tps_runs = [gen_once() for _ in range(5)]
    log(f"  LLM decode under load: {tps_runs} t/s")
    h.join(timeout=20)
    mean_ms = sum(stats["ms"]) / len(stats["ms"]) if stats["ms"] else None
    log(f"  hammer: {stats['ok']} ok / {stats['err']} err, "
        f"mean {mean_ms and round(mean_ms,1)} ms, dims={stats['dims']}")
    if stats["ok"] == 0:
        log("  FATAL: zero embeds.")
        sys.exit(3)
    union = sorted({c for s in samples for c in s})
    log(f"  UNION: {union}")
    import statistics
    return {"arm": label, "mask": mask, "union": union, "tps_runs": tps_runs,
            "tps_mean": round(statistics.mean(tps_runs), 2),
            "embeds": stats["ok"], "embed_err": stats["err"]}


def main():
    open(LOG, "w").write("")
    log("PROPER C ARM — birth-mask placement, proven from /proc")
    arms = [run_arm("E", "12-15"), run_arm("C", "0-11")]
    kill_embedder()
    pid = start_embedder("12-15")
    log(f"restored production embedder pid={pid} born under 12-15")

    e, c = arms
    e_ok = all(x <= 11 or True for x in [])  # placeholder replaced below
    e_ok = (not [x for x in e["union"] if x <= 11]) and bool([x for x in e["union"] if x >= 12])
    c_ok = (not [x for x in c["union"] if x >= 12]) and len([x for x in c["union"] if x <= 11]) >= 8
    log("")
    log("PASS CRITERIA + RESULTS:")
    log(f"  ARM E: need union ⊆ E-cores, none on 0-11 | got {e['union']} -> "
        f"{'PASS' if e_ok else 'FAIL'} (LLM {e['tps_mean']} t/s)")
    log(f"  ARM C: need union ⊆ P-cores (>=8 distinct), none on 12+ | got {c['union']} -> "
        f"{'PASS' if c_ok else 'FAIL'} (LLM {c['tps_mean']} t/s)")
    json.dump(arms, open(os.path.join(HERE, "prove_C_proper.json"), "w"), indent=2)
    sys.exit(0 if (e_ok and c_ok) else 4)


if __name__ == "__main__":
    main()
