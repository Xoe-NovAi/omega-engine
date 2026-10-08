"""Performance-mode rerun: LFM + Krikri, idle + E-core-loaded, t=6.
Writes perf_*.json into logs/20261007-threads/. Spawns/kills its own flood.
"""
import json, subprocess, sys, time, os
from llama_cpp import Llama

OUT = "/home/xnai/Documents/Projects/omega-engine-alpha/logs/20261007-threads"
LFM = "/home/xnai/models/gguf/LFM2.5-2.6B-heretic.Q4_K_M.gguf"
KRIKRI = "/home/xnai/models/gguf/Llama-Krikri-8B-Instruct.Q5_K_M.gguf"
PROMPT = "Explain quantum computing in one sentence."
N = 64
T = 6

def governor():
    try:
        return open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor").read().strip()
    except OSError:
        return "?"

def bench(model_path, n_ctx, n_batch, label):
    llm = Llama(model_path=model_path, n_ctx=n_ctx, n_threads=T, n_threads_batch=T,
                n_batch=n_batch, n_ubatch=512, flash_attn=True, type_k=8, type_v=8,
                use_mmap=True, verbose=False)
    list(llm("hi", max_tokens=4, temperature=0.0, stream=True))
    runs = []
    for i in range(3):
        s = time.perf_counter(); first = None; ntok = 0
        for chunk in llm(PROMPT, max_tokens=N, temperature=0.1, stream=True):
            tok = chunk["choices"][0].get("text", "")
            if tok:
                if first is None: first = time.perf_counter()
                ntok += 1
        e = time.perf_counter()
        r = {"run": i, "ttft_s": round(first - s, 3), "wall_s": round(e - s, 2),
             "ntok": ntok, "dec_ts": round(ntok / (e - first), 1)}
        runs.append(r); print(json.dumps(r), flush=True)
    del llm
    return runs

def flood_start():
    return subprocess.Popen(["taskset", "-c", "12-15", "python3", "/tmp/flood_small.py"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

results = {"governor": governor(), "t": T, "runs": {}}
for name, path, ctx, batch in (("lfm", LFM, 8192, 1024), ("krikri", KRIKRI, 4096, 512)):
    print("== %s idle ==" % name, flush=True)
    results["runs"]["%s_idle" % name] = bench(path, ctx, batch, name)
    fp = flood_start(); time.sleep(8)
    print("== %s loaded ==" % name, flush=True)
    results["runs"]["%s_loaded" % name] = bench(path, ctx, batch, name)
    fp.terminate(); fp.wait(timeout=15); time.sleep(3)

out = "%s/perf_rerun_t%d.json" % (OUT, T)
open(out, "w").write(json.dumps(results, indent=1))
print("SAVED %s" % out, flush=True)
for k, v in results["runs"].items():
    dec = [r["dec_ts"] for r in v]
    print("%-14s dec=%s" % (k, dec), flush=True)
