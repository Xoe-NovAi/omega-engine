#!/usr/bin/env python3
"""
A/B/C: LFM (num_thread 8) decode under three ONNX-1024d embedding placements.

  A: LLM alone          ONNX embedder idle, pinned 12-15 (E)
  B: LLM + embed on E   hammer -> :8090, pinned 12-15
  C: LLM + embed on P   hammer -> :8090, pinned 0-11

Host: i7-13620H (6P+4E/16T), 16GB single-channel DDR5-5200, CPU-only.
Gen  : Ollama :11434 pinned 0-11, tag bench-tlfm25-t6-latest-8 (num_thread 8).
Emb  : scripts/embedding_server.py (ONNX INT8, 586MB) on :8090, TRUNCATE_DIM=1024,
       num_thread 4. Runs as xnai so affinity is retargetable at runtime.

AFFINITY IS ASSERTED, NOT ASSUMED. v1 of this harness silently produced an
invalid P-core arm because the Ollama processes run as user `ollama` and
`taskset` returned EPERM, which `capture_output=True` discarded. Every arm
below verifies the mask it actually got and aborts on mismatch.

NOTE ON THREAD COUNT: measured peak for this tag family is t=6 (21.2 t/s,
2026-10-07); t=8 measured ~20.5 t/s idle. Operator asked for 8. Do not compare
these rows to the t=6 rows in docs/BENCHMARKS.md without saying which tag.

Usage: emb_bench_onnx.py [all|A|B|C]
"""
import json, os, statistics, subprocess, sys, threading, time, urllib.request

GEN = "http://127.0.0.1:11434"
EMB = "http://127.0.0.1:8090"
# Generator tag. MUST carry an explicit num_thread: the live ollama override.conf
# does NOT set OLLAMA_NUM_THREADS, so unpinned models inherit Ollama's default and
# the three arms stop being comparable. bench-* tags below are pinned to 8.
LFM = os.environ.get("GEN_MODEL", "bench-tlfm25-t6-latest-8")
GEN_LABEL = os.environ.get("GEN_LABEL", LFM)
OUT_SUFFIX = os.environ.get("OUT_SUFFIX", "")
PROMPT = os.environ.get("GEN_PROMPT",
    "Explain the difference between a coroutine and a thread in two sentences.")
RUNS = int(os.environ.get("RUNS", "5"))
TOKENS = int(os.environ.get("TOKENS", "96"))
EMB_PID = int(os.environ.get("EMB_PID", "0"))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, f"emb_bench_onnx_results{OUT_SUFFIX}.json")


def die(msg):
    print(f"FATAL: {msg}", flush=True)
    sys.exit(1)


def post(url, payload, timeout=300):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def aff(pid):
    r = subprocess.run(["taskset", "-pc", str(pid)], capture_output=True, text=True)
    return r.stdout.strip().split("list:")[-1].strip()


def set_aff(pid, cpus, label):
    """Retarget and VERIFY. Raises on EPERM or no-op -- never silent."""
    r = subprocess.run(["taskset", "-pc", cpus, str(pid)],
                       capture_output=True, text=True)
    got = aff(pid)
    if got != cpus:
        die(f"{label}: asked taskset for '{cpus}' but process reports '{got}'.\n"
            f"  taskset stderr: {r.stderr.strip()}\n"
            f"  (EPERM usually means the process runs as another user.)")
    print(f"  [affinity OK] embedder -> {got}", flush=True)


stop = threading.Event()
estats = {"n": 0, "ms": [], "dims": None, "err": 0}


def hammer():
    while not stop.is_set():
        t0 = time.perf_counter()
        try:
            # schema is EmbedRequest.inputs: List[str] -> {"inputs": ["..."]}
            # (v1 sent {"input": "..."} and got 422 on all 572 calls)
            r = post(EMB + "/embed", {
                "inputs": ["benchmark load probe for core-placement measurement"]},
                timeout=120)
            estats["ms"].append((time.perf_counter() - t0) * 1000)
            estats["n"] += 1
            v = r.get("embeddings") or []
            # embeddings is List[List[float]] -> batch size is len(v),
            # the DIMENSION is len(v[0]). v1 read len(v) and saw 1.
            if v and estats["dims"] is None:
                estats["dims"] = len(v[0]) if isinstance(v[0], list) else len(v)
        except Exception:
            estats["err"] += 1
        time.sleep(0.05)


def gen_once():
    t0 = time.perf_counter()
    r = post(GEN + "/api/generate", {
        "model": LFM, "prompt": PROMPT, "stream": False,
        "options": {"num_predict": TOKENS, "temperature": 0}}, timeout=300)
    wall = time.perf_counter() - t0
    n = r.get("eval_count", 0)
    ns = r.get("eval_duration", 1)
    return {"tokens": n, "wall_s": round(wall, 3),
            "eval_tps": round(n / (ns / 1e9), 2) if ns else None,
            "load_s": round(r.get("load_duration", 0) / 1e9, 2),
            "prompt_eval_s": round(r.get("prompt_eval_duration", 0) / 1e9, 3)}


def memstat():
    """Available RAM + zRAM used, sampled per arm.

    Added 2026-10-14 after a phi4-mini run returned an impossible +65% (adding
    embedding load appeared to SPEED UP the LLM). Cause: the preceding 7B run
    left 4.68GB resident, phi4 arm A/B ran zRAM-thrashed at 7.40 t/s against a
    documented 13.4, and arm C recovered to 12.23 mid-run. Arms are only
    comparable within a run, and only if this stays high.
    """
    avail = zr = None
    try:
        for ln in open("/proc/meminfo"):
            if ln.startswith("MemAvailable:"):
                avail = int(ln.split()[1]) // 1024
        for ln in open("/sys/block/zram0/mm_stat"):
            zr = int(ln.split()[11]) // 1024
    except Exception:
        pass
    return avail, zr


def run(label, gen_pid, emb_pid, want_mask, use_hammer):
    global stop, estats
    stop = threading.Event()
    estats = {"n": 0, "ms": [], "dims": None, "err": 0}

    print(f"\n{'='*66}\n{label}\n{'='*66}", flush=True)
    a, z = memstat()
    print(f"gen   aff: {aff(gen_pid)}", flush=True)
    print(f"mem       : MemAvailable {a} MB, zRAM used {z} MB", flush=True)
    set_aff(emb_pid, want_mask, label)
    print(f"embed aff: {aff(emb_pid)}", flush=True)

    warm = gen_once()
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
    # A hammer arm that completed zero successful embeds measured NO load.
    # Refuse to record it -- this is exactly how v1 produced a bogus P-core arm.
    if use_hammer and estats["n"] == 0:
        die(f"{label}: hammer made 0 successful /embed calls "
            f"({estats['err']} errors) -- arm is INVALID, refusing to record it.")
    if use_hammer and estats["dims"] not in (None, 1024):
        die(f"{label}: embedder returned {estats['dims']}-d, expected 1024.")
    out = {"gen_model": LFM, "gen_label": GEN_LABEL, "label": label, "gen_affinity": aff(gen_pid), "emb_affinity": aff(emb_pid),
           "embed_mask_requested": want_mask, "mem_available_mb": a,
           "zram_used_mb": z, "warmup": warm, "runs": res,
           "eval_tps_mean": round(statistics.mean(tps), 2),
           "eval_tps_min": round(min(tps), 2), "eval_tps_max": round(max(tps), 2),
           "eval_tps_stdev": round(statistics.pstdev(tps), 2) if len(tps) > 1 else 0.0,
           "embed_calls": estats["n"], "embed_err": estats["err"],
           "embed_dims_observed": estats["dims"],
           "embed_latency_ms_mean": (round(statistics.mean(estats["ms"]), 2)
                                     if estats["ms"] else None),
           "embed_latency_ms_min": round(min(estats["ms"]), 2) if estats["ms"] else None}
    print(json.dumps(out, indent=2), flush=True)
    return out


def main():
    if not EMB_PID or not os.path.exists(f"/proc/{EMB_PID}"):
        die("EMB_PID must be the live embedding_server.py PID (env EMB_PID=N)")
    gen_pid = 2952                                  # :11434, pinned 0-11
    if not os.path.exists(f"/proc/{gen_pid}"):
        die(f"generator pid {gen_pid} not found; update GEN_PID")
    print(f"gen model : {LFM}", flush=True)
    print(f"gen pid={gen_pid}  emb pid={EMB_PID}", flush=True)

    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    results = []
    if which in ("all", "A"):
        results.append(run("A: LLM ALONE (embedder idle @12-15)", gen_pid, EMB_PID, "12-15", False))
    if which in ("all", "B"):
        results.append(run("B: LLM + EMBED ON E-CORES (12-15)", gen_pid, EMB_PID, "12-15", True))
    if which in ("all", "C"):
        try:
            results.append(run("C: LLM + EMBED ON P-CORES (0-11)", gen_pid, EMB_PID, "0-11", True))
        finally:
            set_aff(EMB_PID, "12-15", "restore")
            print("[restored embedder affinity to 12-15]", flush=True)

    prior = []
    if os.path.exists(OUT):
        try:
            prior = json.load(open(OUT))
        except Exception:
            prior = []
    keep = {r["label"] for r in results}
    prior = [p for p in prior if p.get("label") not in keep] + results
    json.dump(prior, open(OUT, "w"), indent=2)
    print(f"\nwrote {OUT}", flush=True)


if __name__ == "__main__":
    main()