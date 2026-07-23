import os
import time
import json
import psutil
import sys
from llama_cpp import Llama

MODELS_DIR = "/media/arcana-novai/omega_library/models/gguf"
MODELS_TO_TEST = [
    "Qwen3-1.7B-Q6_K.gguf",
    "Qwen3-4B-Instruct-2507-UD-Q4_K_XL.gguf",
    "Phi-4-mini-instruct-Q5_K_M.gguf",
    "Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"
]

PROMPT_TC1 = """You are a JSON data extractor. Extract the following Hivemind broadcast into a JSON object matching this schema:
{
  "agent": "string",
  "timestamp": "string",
  "intent": "status|decision|blocker|handoff_complete",
  "summary": "string",
  "data": {"decision_id": "string", "ticket_id": "string"}
}

Broadcast:
"This is @maat. I have just completed the C-4b MCP migration. All tests are passing. Decision D-436 has been ratified. It's 2026-07-23T15:30Z."

Output ONLY valid JSON."""

PROMPT_TC2 = """Update the following Markdown section with the new broadcast.
Current Markdown:
### @maat — Light Oversoul (P1-P5)
#### Updates
- [2026-07-23T15:00Z] Started C-4b migration.

New Broadcast:
{"agent": "maat", "timestamp": "2026-07-23T15:30Z", "intent": "status", "summary": "C-4b MCP migration complete. Tests passing."}

Output the updated Markdown section ONLY."""

PROMPT_TC3 = """You are a JSON data extractor. Handle this malformed broadcast gracefully by extracting what you can and setting intent to "unknown" if unclear.
Schema: {"agent": "string", "intent": "string", "summary": "string"}

Broadcast:
"system error 0x0000 - core dump - @unknown_agent out of memory"

Output ONLY valid JSON."""

def measure_ram():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024 * 1024)

def run_benchmark():
    results = {}
    
    for model_name in MODELS_TO_TEST:
        model_path = os.path.join(MODELS_DIR, model_name)
        if not os.path.exists(model_path):
            print(f"Skipping {model_name}, not found.", flush=True)
            continue
            
        print(f"--- Benchmarking {model_name} ---", flush=True)
        model_results = {}
        
        start_load = time.time()
        try:
            llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4, verbose=False)
        except Exception as e:
            print(f"Failed to load {model_name}: {e}", flush=True)
            continue
        load_time = time.time() - start_load
        print(f"Loaded in {load_time:.2f}s", flush=True)
        
        print("Running TC1...", flush=True)
        start_tc1 = time.time()
        res_tc1 = llm(PROMPT_TC1, max_tokens=150, stop=["```\n", "}\n\n"])
        tc1_time = time.time() - start_tc1
        tc1_text = res_tc1['choices'][0]['text'].strip()
        
        tc1_valid_json = False
        try:
            clean_text = tc1_text[tc1_text.find('{'):tc1_text.rfind('}')+1]
            parsed = json.loads(clean_text)
            tc1_valid_json = True
            extraction_acc = 100 if parsed.get('agent') == 'maat' else 50
        except:
            extraction_acc = 0
            
        tc1_tps = res_tc1['usage']['completion_tokens'] / tc1_time if tc1_time > 0 else 0
        print(f"TC1 done in {tc1_time:.2f}s", flush=True)
        
        print("Running TC2...", flush=True)
        start_tc2 = time.time()
        res_tc2 = llm(PROMPT_TC2, max_tokens=200)
        tc2_time = time.time() - start_tc2
        tc2_tps = res_tc2['usage']['completion_tokens'] / tc2_time if tc2_time > 0 else 0
        print(f"TC2 done in {tc2_time:.2f}s", flush=True)
        
        print("Running TC3...", flush=True)
        start_tc3 = time.time()
        res_tc3 = llm(PROMPT_TC3, max_tokens=100)
        tc3_time = time.time() - start_tc3
        print(f"TC3 done in {tc3_time:.2f}s", flush=True)
        
        ram_usage = measure_ram()
        
        model_results = {
            "load_time_s": round(load_time, 2),
            "tc1_latency_s": round(tc1_time, 2),
            "tc2_latency_s": round(tc2_time, 2),
            "tc1_tps": round(tc1_tps, 2),
            "tc2_tps": round(tc2_tps, 2),
            "tc1_valid_json": tc1_valid_json,
            "extraction_accuracy": extraction_acc,
            "ram_usage_gb": round(ram_usage, 2)
        }
        
        results[model_name] = model_results
        print(f"Results for {model_name}: {model_results}", flush=True)
        
        del llm
        
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
if __name__ == "__main__":
    run_benchmark()
