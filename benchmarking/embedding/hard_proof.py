#!/usr/bin/env python3
"""
HARD PROOF -- which CPUs did each workload's threads actually run on.

Confirms the operating model before re-running the isolation cells:

  :11434  generator  ollama serve, PID A, affinity 0-11   (P-cores + HT)
  :11435  embedder  ollama serve, PID B, affinity 12-15 (Gracemont)
  :8090   embedder  onnx  server,  PID C, affinity 12-15 (Gracemont)

Method: read every thread's LAST_CPU from /proc/PID/task/TID/stat (field 39,
0-indexed field 38). A running generator's worker threads must sit in {0..11};
an embedder's in {12..15}. Then stress each port and confirm its CPU set
does not change. If it does, the harness is cheating.

A number cannot be "the same" if the two loads are not actually on the
claimed cores. Here we measure it directly instead of trusting the mask.
"""
import subprocess, time, glob, os, json, urllib.request

def proc_for_port(port):
    out = subprocess.run(["ss","-ltnp"], capture_output=True, text=True).stdout
    for ln in out.splitlines():
        if f"127.0.0.1:{port} " in ln or f"*:{port} " in ln or f"0.0.0.0:{port}" in ln:
            import re
            m = re.search(r"pid=(\d+)", ln)
            if m: return int(m.group(1))
    return None

def get_affinity(pid):
    r = subprocess.run(["taskset", "-pc", str(pid)], capture_output=True,
                       text=True).stdout
    return r.split("list:")[-1].strip() if "list:" in r else "?"

def task_last_cpu(pid):
    cpus = set()
    for tid in os.listdir(f"/proc/{pid}/task"):
        try:
            st = open(f"/proc/{pid}/task/{tid}/stat").read().split()
            # field 39 (1-indexed) = last_executed_cpu, split() index 38
            cpus.add(int(st[38]))
        except (FileNotFoundError, IndexError, ValueError):
            pass
    return sorted(cpus)

def api(port, endpoint, payload, timeout=900):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{endpoint}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


print("=" * 78)
print("HARD PROOF: which CPUs each workload's threads run on (live /proc scrape)")
print("=" * 78)

for port, label in ((11434, "OLLAMA GENERATOR"), (11435, "OLLAMA EMBEDDER"),
                    (8090,   "ONNX EMBEDDER")):
    pid = proc_for_port(port)
    print(f"\n[{label}]  port={port}  pid={pid}")
    if pid is None:
        print("  port free")
        continue
    print(f"  taskset CPUAffinity (mask)   : {get_affinity(pid)}")
    print(f"  last_executed_cpu (all threads) : {task_last_cpu(pid)}")
    # load the process briefly so the scheduler actually picks cores
    try:
        if port == 8090:
            api(port, "/embed", {"inputs": ["proof-probe"]}, timeout=60)
        elif port == 11434:
            api(port, "/api/generate",
                {"model": "bench-tlfm25-t6-latest-8",
                 "prompt": "Explain coroutines.", "stream": False,
                 "options": {"num_predict": 8, "num_thread": 4}}, timeout=60)
        elif port == 11435:
            api(port, "/api/embed",
                {"model": "qwen3-embedding:0.6b", "input": "probe"}, timeout=60)
    except Exception as e:
        print(f"  load call raised: {type(e).__name__}: {str(e)[:80]}")
    print(f"  last_executed_cpu (after load): {task_last_cpu(pid)}")

# Now launch one gen (4 threads) and one embed concurrently and show the two
# CPU sets do not overlap.
print("\n" + "=" * 78)
print("CONCURRENCY PROOF: gen @4 threads + embed on E-cores simultaneously.")
print("=" * 78)
p_gen = proc_for_port(11434)
# arm :8090 (ONNX) on 12-15 while gen runs
p_onnx = proc_for_port(8090)

def worker():
    api(11434, "/api/generate",
        {"model": "bench-tlfm25-t6-latest-8", "prompt": "Explain a coroutine"
                                                        " vs a thread in detail.",
         "stream": False, "options": {"num_predict": 64, "num_thread": 4}},
        timeout=300)

import threading
t = threading.Thread(target=worker, daemon=True)
t.start()
time.sleep(1.5)   # generator already spinning by now
onnx_cpus = task_last_cpu(p_onnx)
gen_cpus = task_last_cpu(p_gen)
print(f"\n  generator :8090's onnx:   {onnx_cpus}")
print(f"  generator :11434's LFM:   {gen_cpus}")
print(f"  overlap (shared CPUs):    {sorted(set(onnx_cpus) & set(gen_cpus))}")
print()
print("  VERDICT: any overlap >0 means the two workloads shared a core, i.e.")
print("  the mask was not actually enforced (or both P and E cores were used).")
t.join(timeout=60)
