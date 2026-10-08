"""Krikri t=4 rerun in performance mode: idle + E-core-loaded."""
import json, subprocess, time
from llama_cpp import Llama

OUT = "/home/xnai/Documents/Projects/omega-engine-alpha/logs/20261007-threads"
KRIKRI = "/home/xnai/models/gguf/Llama-Krikri-8B-Instruct.Q5_K_M.gguf"
PROMPT = "Explain quantum computing in one sentence."
N = 64
T = 4

def bench(label):
    llm = Llama(model_path=KRIKRI, n_ctx=4096, n_threads=T, n_threads_batch=T,
                n_batch=512, n_ubatch=512, flash_attn=True, type_k=8, type_v=8,
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

results = {"governor": "performance", "t": T, "runs": {}}
print("== krikri t=4 idle ==", flush=True)
results["runs"]["krikri_t4_idle"] = bench("idle")
fp = subprocess.Popen(["taskset", "-c", "12-15", "python3", "/tmp/flood_small.py"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(8)
print("== krikri t=4 loaded ==", flush=True)
results["runs"]["krikri_t4_loaded"] = bench("loaded")
fp.terminate(); fp.wait(timeout=15)

out = "%s/perf_krikri_t4.json" % OUT
open(out, "w").write(json.dumps(results, indent=1))
print("SAVED %s" % out, flush=True)
for k, v in results["runs"].items():
    print("%-20s dec=%s" % (k, [r["dec_ts"] for r in v]), flush=True)
