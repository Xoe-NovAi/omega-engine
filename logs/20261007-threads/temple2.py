import json, time, sys, os, subprocess
T = int(sys.argv[1])
TAG = "t%d" % T
from llama_cpp import Llama
LFM = "/home/xnai/models/gguf/LFM2.5-2.6B-heretic.Q4_K_M.gguf"
OUT = "/home/xnai/Documents/Projects/omega-engine-alpha/logs/20261007-threads/temple_loaded_%s.json" % TAG
tele = {"t": T, "loaded": True, "runs": [], "core": []}
llm = Llama(model_path=LFM, n_ctx=8192, n_threads=T, n_threads_batch=T, n_batch=1024, n_ubatch=512, flash_attn=True, type_k=8, type_v=8, use_mmap=True, verbose=False)
list(llm("hi", max_tokens=4, temperature=0.0, stream=True))
for i in range(3):
    mhz = [l.split(":")[1].strip() for l in open("/proc/cpuinfo").read().splitlines() if l.startswith("cpu MHz")]
    tele["core"].append({"run": i, "mhz": mhz})
    s = time.perf_counter(); first = None; ntok = 0
    for chunk in llm("Explain quantum computing in one sentence.", max_tokens=64, temperature=0.1, stream=True):
        tok = chunk["choices"][0].get("text", "")
        if tok:
            if first is None: first = time.perf_counter()
            ntok += 1
    e = time.perf_counter()
    r = {"run": i, "ttft_s": round(first - s, 3), "wall_s": round(e - s, 2), "ntok": ntok, "dec_ts": round(ntok / (e - first), 1)}
    tele["runs"].append(r)
    print(json.dumps(r), flush=True)
open(OUT, "w").write(json.dumps(tele, indent=1))
print("SAVED %s" % OUT, flush=True)
