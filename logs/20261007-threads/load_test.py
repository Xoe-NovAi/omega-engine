import time, json, os
from llama_cpp import Llama
MODEL="/home/xnai/models/gguf/LFM2.5-2.6B-heretic.Q4_K_M.gguf"
QWEN="/home/xnai/Downloads/qwen3.5-4B-super-coder.Q4_0.gguf"
PROMPT="Explain quantum computing in one sentence."
N=64
import sys
T=int(sys.argv[1]) if len(sys.argv)>1 else 6
print(f"PIN main={os.sched_getaffinity(0)}", flush=True)
llm=Llama(model_path=MODEL, n_ctx=8192, n_threads=T, n_threads_batch=T, n_batch=1024, n_ubatch=512, flash_attn=True, type_k=8, type_v=8, use_mmap=True, verbose=False)
# check qwen still hammering
list(llm("hi", max_tokens=4, temperature=0.0, stream=True))
runs=[]
for i in range(3):
    s=time.perf_counter(); first=None; ntok=0
    for chunk in llm(PROMPT, max_tokens=N, temperature=0.1, stream=True):
        tok=chunk["choices"][0].get("text","")
        if tok:
            if first is None: first=time.perf_counter()
            ntok+=1
    e=time.perf_counter()
    ttft=first-s; wall=e-s; dec=ntok/(wall-ttft)
    r={"run":i,"t":T,"ttft_s":round(ttft,3),"wall_s":round(wall,2),"dec_ts":round(dec,1)}
    print(json.dumps(r), flush=True); runs.append(r)
with open(f"/tmp/load_t{T}.json","w") as f: json.dump(runs,f,indent=1)
