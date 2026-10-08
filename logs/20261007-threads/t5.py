import time, json
from llama_cpp import Llama
MODEL="/home/xnai/models/gguf/LFM2.5-2.6B-heretic.Q4_K_M.gguf"
PROMPT="Explain quantum computing in one sentence."
N=64
for t in (5, 5):
    llm=Llama(model_path=MODEL, n_ctx=8192, n_threads=5, n_threads_batch=5, n_batch=1024, n_ubatch=512, flash_attn=True, type_k=8, type_v=8, use_mmap=True, verbose=False)
    list(llm("hi", max_tokens=4, temperature=0.0, stream=True))
    s=time.perf_counter(); first=None; ntok=0
    for chunk in llm(PROMPT, max_tokens=N, temperature=0.1, stream=True):
        tok=chunk["choices"][0].get("text","")
        if tok:
            if first is None: first=time.perf_counter()
            ntok+=1
    e=time.perf_counter()
    ttft=first-s; wall=e-s; dec=ntok/(wall-ttft)
    print(json.dumps({"t":5,"ttft_s":round(ttft,3),"wall_s":round(wall,2),"dec_ts":round(dec,1)}), flush=True)
    del llm
