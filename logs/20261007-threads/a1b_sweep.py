"""Thread sweep: LFM2.5-230M Q6_K + LFM2.5-350M i1-Q6_K (performance governor)."""
import json, time, gc
from llama_cpp import Llama

OUT = "/home/xnai/Documents/Projects/omega-engine-alpha/logs/20261007-threads/a1b_sweep.json"
MODELS = [("lfm25-8b-a1b", "/home/xnai/models/gguf/LFM2.5-8B-A1B-UD-Q4_K_XL.gguf"),
    ("lfm25-230m", "/home/xnai/models/gguf/LFM2.5-230M-Q6_K.gguf"),
    ("lfm25-350m", "/home/xnai/models/gguf/LFM2.5-350M.i1-Q6_K.gguf"),
]
PROMPT = "Explain quantum computing in one sentence."
N = 64
results = []
for name, path in MODELS:
    for t in (4, 6, 8, 10):
        print("== %s t=%d ==" % (name, t), flush=True)
        t0 = time.perf_counter()
        llm = Llama(model_path=path, n_ctx=4096, n_threads=t, n_threads_batch=t,
                    n_batch=1024, n_ubatch=512, flash_attn=True, type_k=8, type_v=8,
                    use_mmap=True, verbose=False)
        load_s = round(time.perf_counter() - t0, 2)
        list(llm("hi", max_tokens=4, temperature=0.0, stream=True))
        # warm timed run (decode)
        s = time.perf_counter(); first = None; ntok = 0
        for chunk in llm(PROMPT, max_tokens=N, temperature=0.1, stream=True):
            tok = chunk["choices"][0].get("text", "")
            if tok:
                if first is None: first = time.perf_counter()
                ntok += 1
        e = time.perf_counter()
        # prompt-eval probe: 512-token-ish repeated prompt via completion timing
        long_prompt = (PROMPT + " ") * 100
        tp0 = time.perf_counter()
        llm(long_prompt, max_tokens=1, temperature=0.0, stream=False)
        prompt_s = round(time.perf_counter() - tp0, 2)
        r = {"model": name, "t": t, "load_s": load_s,
             "ttft_s": round(first - s, 3), "wall_s": round(e - s, 2), "ntok": ntok,
             "dec_ts": round(ntok / (e - first), 1), "prompt500_s": prompt_s}
        print(json.dumps(r), flush=True)
        results.append(r)
        del llm; gc.collect()
open(OUT, "w").write(json.dumps(results, indent=1))
print("SAVED %s" % OUT, flush=True)
for r in results:
    print("%-11s t=%2d load=%.2fs TTFT=%.3fs dec=%6.1f t/s prompt~500tok=%.2fs"
          % (r["model"], r["t"], r["load_s"], r["ttft_s"], r["dec_ts"], r["prompt500_s"]),
          flush=True)
