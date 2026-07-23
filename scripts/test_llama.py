import os
import time
import json
import psutil
from llama_cpp import Llama

MODELS_DIR = "/media/arcana-novai/omega_library/models/gguf"
model_name = "Qwen3-1.7B-Q6_K.gguf"
model_path = os.path.join(MODELS_DIR, model_name)

print(f"Loading {model_name}...")
start = time.time()
llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4, verbose=False)
print(f"Loaded in {time.time() - start:.2f}s")

prompt = "Hello, what is 2+2?"
print("Generating...")
start = time.time()
res = llm(prompt, max_tokens=20)
print(f"Generated in {time.time() - start:.2f}s")
print(res['choices'][0]['text'])
