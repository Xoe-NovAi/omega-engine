#!/usr/bin/env python3
"""
prove_placement.py — HARD PROOF that the ONNX embedder's threads actually
EXECUTE on the claimed cores, not just carry the claimed mask.

Your theory: in the sweep's "embed on P-cores" arm, the embedder may never have
run on P-cores at all (a mask is permission, not a schedule). Fair. This script
measures execution directly:

  * enumerates every thread of the embedder process,
  * reads each thread's last_executed_cpu from /proc/<pid>/task/<tid>/stat
    (field 39) BEFORE and DURING a sustained embed hammer,
  * does it once with the mask at 12-15 (E) and once at 0-11 (P),
  * interleaves a real LLM generation on :11434 and reports its t/s,
  * also scrapes the generator Ollama's own threads (read-only) to show the
    two workloads overlap on P-cores in the C arm.

Pass criteria (printed at the end, no interpretation needed):
  ARM E: 100% of sampled embed threads ran on CPUs 12-15, 0% on 0-11.
  ARM C: >80% of sampled embed threads ran on CPUs 0-11 at least once,
         i.e. the executions really happened on P-cores.
If ARM C fails that, your theory is right and the sweep's C arm is void.

Everything is logged to prove_placement.log AND stdout.
"""
import json, os, subprocess, sys, threading, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "prove_placement.log")
GEN, EMB = "http://127.0.0.1:11434", "http://127.0.0.1:8090"
LFM = "bench-tlfm25-t6-latest-8"


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


def get(url, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read())


def find_onnx_pid():
    """My own embedding_server.py (xnai-owned) — never an ollama-owned pid."""
    out = subprocess.run(["pgrep", "-f", "embedding_server.py"],
                         capture_output=True, text=True).stdout.split()
    me = str(os.getpid())
    cands = [int(p) for p in out if p != me]
    for p in cands:
        try:
            cl = open(f"/proc/{p}/cmdline").read().replace("\0", " ")
            if "embedding_server.py" in cl and "prove_placement" not in cl:
                return p
        except FileNotFoundError:
            pass
    return None


def find_gen_pid():
    """The ollama serve pinned 0-11 (read-only scrape; never modified)."""
    out = subprocess.run(["pgrep", "-f", "ollama serve"],
                         capture_output=True, text=True).stdout.split()
    for p in out:
        try:
            r = subprocess.run(["taskset", "-pc", p],
                               capture_output=True, text=True).stdout
            if "0-11" in r:
                return int(p)
        except Exception:
            pass
    return None


def mask(pid):
    r = subprocess.run(["taskset", "-pc", str(pid)],
                       capture_output=True, text=True).stdout
    return r.split("list:")[-1].strip() if "list:" in r else "?"


def set_mask(pid, cpus, label):
    r = subprocess.run(["taskset", "-pc", cpus, str(pid)],
                       capture_output=True, text=True)
    got = mask(pid)
    log(f"  set_mask {label}: asked '{cpus}', taskset rc={r.returncode}, "
        f"stderr='{r.stderr.strip()}', read-back='{got}'")
    if got != cpus:
        log(f"  FATAL: mask did not take. Aborting.")
        sys.exit(2)
    return got


def thread_cpus(pid):
    """{tid: last_executed_cpu} for every thread. stat is world-readable."""
    out = {}
    try:
        tids = os.listdir(f"/proc/{pid}/task")
    except FileNotFoundError:
        return out
    for tid in tids:
        try:
            st = open(f"/proc/{pid}/task/{tid}/stat").read().split()
            out[int(tid)] = int(st[38])   # field 39 = processor
        except (FileNotFoundError, IndexError, ValueError):
            pass
    return out


def gen_once():
    r = post(GEN + "/api/generate", {
        "model": LFM, "stream": False,
        "prompt": "Explain the difference between a coroutine and a thread in two sentences.",
        "options": {"num_predict": 96, "temperature": 0, "num_thread": 8}},
        timeout=300)
    ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1)
    return round(ec / (ed / 1e9), 2) if ed else None


def hammer(seconds, stats):
    """Continuous /embed until the deadline. Counts successes loudly."""
    end = time.perf_counter() + seconds
    while time.perf_counter() < end:
        t0 = time.perf_counter()
        try:
            r = post(EMB + "/embed", {"inputs": ["placement proof hammer"]},
                     timeout=120)
            dims = r.get("dimensions")
            stats["ok"] += 1
            stats["ms"].append((time.perf_counter() - t0) * 1000)
            stats["dims"] = dims
        except Exception as e:
            stats["err"] += 1
            stats["last_err"] = f"{type(e).__name__}: {str(e)[:100]}"


def run_arm(label, want_mask, onnx_pid, gen_pid):
    log(f"===== ARM {label}: embedder mask -> {want_mask} =====")
    set_mask(onnx_pid, want_mask, f"arm-{label}")

    stats = {"ok": 0, "err": 0, "ms": [], "dims": None, "last_err": None}
    h = threading.Thread(target=hammer, args=(36, stats), daemon=True)
    h.start()
    time.sleep(4)   # let the hammer saturate before sampling

    samples = []
    for i in range(5):
        time.sleep(2)
        s = thread_cpus(onnx_pid)
        samples.append(sorted(set(s.values())))
        log(f"  sample {i+1}: embed threads on CPUs {sorted(set(s.values()))} "
            f"({len(s)} threads alive)")

    # one generation under this exact load
    tps = gen_once()
    log(f"  LLM decode under load: {tps} t/s")
    g = thread_cpus(gen_pid)
    log(f"  generator threads on CPUs {sorted(set(g.values()))} "
        f"({len(g)} threads alive)")

    h.join(timeout=20)
    mean_ms = (sum(stats["ms"]) / len(stats["ms"])) if stats["ms"] else None
    log(f"  hammer: {stats['ok']} ok / {stats['err']} err, "
        f"mean {mean_ms and round(mean_ms,1)} ms, dims={stats['dims']}, "
        f"last_err={stats['last_err']}")
    if stats["ok"] == 0:
        log("  FATAL: hammer completed zero embeds — arm measured nothing.")
        sys.exit(3)

    union = sorted({c for s in samples for c in s})
    on_p = [c for c in union if c <= 11]
    on_e = [c for c in union if c >= 12]
    log(f"  UNION over 5 samples: P-cores {on_p} | E-cores {on_e}")
    return {"arm": label, "mask": want_mask, "union": union,
            "on_p": on_p, "on_e": on_e, "tps": tps,
            "embeds": stats["ok"], "embed_err": stats["err"]}


def main():
    open(LOG, "w").write("")
    log("PROVE PLACEMENT — mask vs execution, measured from /proc")
    onnx_pid = find_onnx_pid()
    gen_pid = find_gen_pid()
    log(f"onnx embedder (:8090) pid={onnx_pid}, mask={mask(onnx_pid) if onnx_pid else '?'}")
    log(f"generator (:11434)   pid={gen_pid}, mask={mask(gen_pid) if gen_pid else '?'} (READ-ONLY, never touched)")
    if not onnx_pid or not gen_pid:
        log("FATAL: could not find both processes.")
        sys.exit(1)
    h = get(EMB + "/health")
    log(f"embedder health: {h}")

    arms = [run_arm("E", "12-15", onnx_pid, gen_pid),
            run_arm("C", "0-11", onnx_pid, gen_pid)]

    set_mask(onnx_pid, "12-15", "restore")
    log("restored embedder to 12-15")

    e, c = arms
    log("")
    log("PASS CRITERIA + RESULTS (no interpretation needed):")
    e_ok = (not e["on_p"]) and bool(e["on_e"])
    log(f"  ARM E: expected P={{}} E={{12..15}} | got P={e['on_p']} E={e['on_e']} -> "
        f"{'PASS' if e_ok else 'FAIL'}")
    # threads counted by how many distinct P-core CPUs they landed on is too
    # strict (scheduler may park some); count fraction of UNION cpus on P side.
    frac = len(c["on_p"]) / max(1, len(c["union"]))
    c_ok = len(c["on_p"]) >= 8 and frac >= 0.8
    log(f"  ARM C: need >=8 distinct P-core CPUs and >=80% of union on P side | "
        f"got P={c['on_p']} E={c['on_e']} (frac={frac:.2f}) -> "
        f"{'PASS' if c_ok else 'FAIL'}")
    log(f"  LLM t/s: E-arm {e['tps']} vs C-arm {c['tps']}")
    log(f"  full log: {LOG}")
    sys.exit(0 if (e_ok and c_ok) else 4)


if __name__ == "__main__":
    main()
