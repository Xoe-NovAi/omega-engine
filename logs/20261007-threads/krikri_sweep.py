import json, time, gc
from llama_cpp import Llama
MODEL = "/home/xnai/models/gguf/Llama-Krikri-8B-Instruct.Q5_K_M.gguf"
PROMPT = "Explain quantum computing in one sentence."
N = 64
OUT = "/home/xnai/Documents/Projects/omega-engine-alpha/logs/20261007-threads/krikri_sweep.json"
results = []
for t in (4, 5, 6, 8, 10):
    print("=== t=%d ===" % t, flush=True)
    t0 = time.perf_counter()
    llm = Llama(model_path=MODEL, n_ctx=4096, n_threads=t, n_threads_batch=t, n_batch=512, n_ubatch=512, flash_attn=True, type_k=8, type_v=8, use_mmap=True, verbose=False)
    load_s = round(time.perf_counter() - t0, 2)
    list(llm("hi", max_tokens=4, temperature=0.0, stream=True))
    s = time.perf_counter(); first = None; ntok = 0
    for chunk in llm(PROMPT, max_tokens=N, temperature=0.1, stream=True):
        tok = chunk["choices"][0].get("text", "")
        if tok:
            if first is None: first = time.perf_counter()
            ntok += 1
    e = time.perf_counter()
    r = {"t": t, "load_s": load_s, "ttft_s": round(first - s, 3), "wall_s": round(e - s, 2), "ntok": ntok, "dec_ts": round(ntok / (e - first), 1)}
    print(json.dumps(r), flush=True)
    results.append(r)
    del llm; gc.collect()
open(OUT, "w").write(json.dumps(results, indent=1))
print("SAVED %s" % OUT, flush=True)
for r in sorted(results, key=lambda x: -x["dec_ts"]):
    print("t=%2d load=%.1fs TTFT=%.3fs wall=%.1fs dec=%.1f t/s" % (r["t"], r["load_s"], r["ttft_s"], r["wall_s"], r["dec_ts"]), flush=True)
