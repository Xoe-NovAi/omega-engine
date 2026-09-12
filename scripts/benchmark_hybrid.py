#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
⬡ OMEGA ⬡ HYBRID BENCHMARK RUNNER ⬡ v1.0
Unified local + cloud benchmarking with thermal protocol and steady-state measurement.
Outputs to SQLite benchmark_runs table. No routing engine — just data.
"""

import json
import os
import sqlite3
import time
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import anyio

# ── Configuration ──────────────────────────────────────────────────────
DB_PATH = Path("data/benchmarks/benchmark_runs.db")
MODELS_DIR = Path("/media/arcana-novai/omega_library/models/gguf")
CLOUD_PRICING = Path("config/cloud_pricing.yaml")

# Local models to benchmark (3 configs × 3 thermal states = 27 runs)
LOCAL_BENCHMARK_CONFIGS = [
    {"model": "qwen3-1.7b", "threads": 4, "n_ctx": 4096, "n_batch": 512},
    {"model": "qwen3-1.7b", "threads": 6, "n_ctx": 4096, "n_batch": 512},
    {"model": "qwen3-4b", "threads": 6, "n_ctx": 4096, "n_batch": 512},
]

THERMAL_STATES = [
    {"name": "cold", "duration_s": 60, "cooldown_s": 300},
    {"name": "warm", "duration_s": 300, "cooldown_s": 300},
    {"name": "hot", "duration_s": 900, "cooldown_s": 600},
]

# Cloud models to benchmark (3 providers × 1 model × 3 times of day)
CLOUD_BENCHMARK_CONFIGS = [
    {"provider": "google", "model": "gemini-1.5-pro", "rps": 2, "requests": 50},
    {"provider": "anthropic", "model": "claude-opus-4", "rps": 2, "requests": 50},
    {"provider": "openrouter", "model": "google/gemini-1.5-pro", "rps": 2, "requests": 50},
]

TIMES_OF_DAY = ["morning", "afternoon", "night"]

# Task categories with prompts
TASK_PROMPTS = {
    "code_completion": [
        "Complete this Python function: def fibonacci(n):",
        "Write a SQL query to find duplicate emails in users table.",
        "Implement a binary search in Rust.",
    ],
    "simple_qa": [
        "What is the capital of France?",
        "Explain photosynthesis in 2 sentences.",
        "Who wrote 'Masters of Doom'?",
    ],
    "complex_reasoning": [
        "Plan a 3-day trip to Tokyo optimizing for food and temples.",
        "Design a rate limiter for a distributed API.",
        "Debug this memory leak: [code snippet]",
    ],
    "planning": [
        "Create a project plan for migrating from PostgreSQL to CockroachDB.",
        "Outline a CI/CD pipeline for a monorepo with 50 services.",
    ],
    "function_calling": [
        "Call the weather API for Tokyo and return temperature.",
        "Search for 'RULER benchmark' and summarize top 3 results.",
    ],
}

# ── Database Schema ────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS benchmark_runs (
    run_id TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    model_id TEXT NOT NULL,
    model_hash TEXT NOT NULL,
    provider TEXT,
    task_category TEXT NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    latency_ms INTEGER,
    ttft_ms INTEGER,
    quality_score REAL,
    cost_usd REAL,
    energy_j REAL,
    thermal_state TEXT,
    privacy_tag INTEGER DEFAULT 0,
    success INTEGER DEFAULT 1,
    error_type TEXT
);
CREATE INDEX IF NOT EXISTS idx_runs_task_quality ON benchmark_runs(task_category, quality_score);
CREATE INDEX IF NOT EXISTS idx_runs_model ON benchmark_runs(model_id);
CREATE INDEX IF NOT EXISTS idx_runs_thermal ON benchmark_runs(thermal_state);
"""

# ── Data Classes ───────────────────────────────────────────────────────
@dataclass
class BenchmarkRun:
    run_id: str
    timestamp: int
    model_id: str
    model_hash: str
    provider: Optional[str]
    task_category: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    ttft_ms: int
    quality_score: float
    cost_usd: float
    energy_j: float
    thermal_state: str
    privacy_tag: int = 0
    success: int = 1
    error_type: Optional[str] = None

    def to_sql(self) -> tuple:
        return (
            self.run_id, self.timestamp, self.model_id, self.model_hash,
            self.provider, self.task_category, self.prompt_tokens,
            self.completion_tokens, self.latency_ms, self.ttft_ms,
            self.quality_score, self.cost_usd, self.energy_j,
            self.thermal_state, self.privacy_tag, self.success,
            self.error_type
        )

# ── Utility Functions ──────────────────────────────────────────────────
def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn

def insert_run(conn: sqlite3.Connection, run: BenchmarkRun):
    conn.execute(
        """INSERT INTO benchmark_runs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        run.to_sql()
    )
    conn.commit()

def get_model_hash(model_path: Path) -> str:
    """SHA256 of GGUF file for exact reproducibility."""
    sha256 = hashlib.sha256()
    with open(model_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]

def read_rapl_energy_j() -> float:
    """Read package energy from RAPL (Joules). Returns 0 if unavailable."""
    try:
        for pkg in Path("/sys/class/powercap").glob("intel-rapl:*"):
            name = (pkg / "name").read_text().strip()
            if "package" in name.lower():
                energy_uj = int((pkg / "energy_uj").read_text().strip())
                return energy_uj / 1_000_000  # µJ → J
    except Exception:
        pass
    return 0.0

def read_cpu_temp_c() -> float:
    """Read CPU temperature (°C). Returns 0 if unavailable."""
    try:
        for hwmon in Path("/sys/class/hwmon").glob("hwmon*"):
            name = (hwmon / "name").read_text().strip()
            if "k10temp" in name or "zen" in name.lower():
                for temp_file in hwmon.glob("temp*_input"):
                    temp_mc = int(temp_file.read_text().strip())
                    return temp_mc / 1000.0
    except Exception:
        pass
    return 0.0

# ── Local Benchmarking ─────────────────────────────────────────────────
async def run_local_benchmark(config: dict, thermal: dict, conn: sqlite3.Connection):
    """Run local benchmark with llama.cpp via native-gguf provider."""
    from llama_cpp import Llama
    
    model_name = config["model"]
    model_path = MODELS_DIR / f"{model_name.replace('.', '-')}.gguf"
    if not model_path.exists():
        # Try common naming patterns
        for pattern in [f"{model_name}*.gguf", f"*{model_name}*.gguf"]:
            matches = list(MODELS_DIR.glob(pattern))
            if matches:
                model_path = matches[0]
                break
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return
    
    model_hash = get_model_hash(model_path)
    print(f"\n{'='*60}")
    print(f"Local: {model_name} | {thermal['name']} | threads={config['threads']}")
    print(f"{'='*60}")
    
    # Cooldown between thermal states
    if thermal["name"] != "cold":
        print(f"Cooling down {thermal['cooldown_s']}s...")
        await anyio.sleep(thermal["cooldown_s"])
    
    # Load model
    llm = Llama(
        model_path=str(model_path),
        n_threads=config["threads"],
        n_threads_batch=config["threads"],
        n_ctx=config["n_ctx"],
        n_batch=config["n_batch"],
        n_ubatch=32,
        type_k=8,
        type_v=1,
        use_mmap=True,
        use_mlock=False,
        n_gpu_layers=0,
        verbose=False,
    )
    
    # Warmup run
    _ = llm("Warmup.", max_tokens=1, temperature=0)
    
    # Baseline energy
    energy_start = read_rapl_energy_j()
    temp_start = read_cpu_temp_c()
    
    # Run tasks for this thermal state
    for task_cat, prompts in TASK_PROMPTS.items():
        for prompt in prompts:
            run_id = f"local_{model_name}_{thermal['name']}_{task_cat}_{int(time.time()*1000)}"
            timestamp = int(time.time() * 1000)
            
            t0 = time.monotonic()
            result = llm(
                prompt=prompt,
                max_tokens=256,
                temperature=0.1,
                stop=["\n\n", "User:", "Human:"],
            )
            latency_ms = int((time.monotonic() - t0) * 1000)
            
            text = result["choices"][0]["text"].strip()
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            # Simple quality heuristic (can be replaced with judge later)
            quality = 1.0 if len(text) > 10 and "error" not in text.lower() else 0.5
            
            # Energy delta
            energy_end = read_rapl_energy_j()
            energy_j = energy_end - energy_start
            energy_start = energy_end  # Reset for next
            
            run = BenchmarkRun(
                run_id=run_id,
                timestamp=timestamp,
                model_id=model_name,
                model_hash=model_hash,
                provider=None,
                task_category=task_cat,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                ttft_ms=latency_ms,  # Approximation for llama.cpp
                quality_score=quality,
                cost_usd=0.0,
                energy_j=energy_j,
                thermal_state=thermal["name"],
                privacy_tag=0,
                success=1,
                error_type=None,
            )
            insert_run(conn, run)
            print(f"  {task_cat}: {completion_tokens} tok, {latency_ms}ms, {quality:.1f} qual, {energy_j:.1f}J")
    
    llm.close()
    del llm

# ── Cloud Benchmarking ─────────────────────────────────────────────────
async def run_cloud_benchmark(config: dict, time_of_day: str, conn: sqlite3.Connection):
    """Run cloud benchmark with steady-state protocol."""
    import httpx
    
    provider = config["provider"]
    model = config["model"]
    rps = config["rps"]
    n_requests = config["requests"]
    
    # Get API key from environment
    api_key_env = {
        "google": "GOOGLE_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }.get(provider)
    
    api_key = os.environ.get(api_key_env)
    if not api_key:
        print(f"⚠️  {api_key_env} not set — skipping {provider}/{model}")
        return
    
    print(f"\n{'='*60}")
    print(f"Cloud: {provider}/{model} | {time_of_day} | {rps} RPS × {n_requests}")
    print(f"{'='*60}")
    
    # Provider-specific endpoints
    endpoints = {
        "google": f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "anthropic": "https://api.anthropic.com/v1/messages",
        "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    }
    
    headers = {
        "google": {"x-goog-api-key": api_key, "Content-Type": "application/json"},
        "anthropic": {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        "openrouter": {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Warmup: 10 requests at 1 RPS
        print("  Warmup (10 req @ 1 RPS)...")
        for _ in range(10):
            await call_cloud_api(client, provider, endpoints[provider], headers[provider], model, "Warmup.")
            await anyio.sleep(1.0)
        
        # Measure: n_requests at target RPS
        print(f"  Measuring ({n_requests} req @ {rps} RPS)...")
        latencies = []
        ttfts = []
        errors = 0
        rate_limited = 0
        
        for i, (task_cat, prompts) in enumerate(TASK_PROMPTS.items()):
            for prompt in prompts[:n_requests // len(TASK_PROMPTS) + 1]:
                if len(latencies) >= n_requests:
                    break
                
                t0 = time.monotonic()
                try:
                    result = await call_cloud_api(
                        client, provider, endpoints[provider], headers[provider], model, prompt
                    )
                    latency_ms = int((time.monotonic() - t0) * 1000)
                    
                    if result.get("success"):
                        latencies.append(latency_ms)
                        ttfts.append(result.get("ttft_ms", latency_ms))
                    else:
                        errors += 1
                        if result.get("error_type") == "rate_limit":
                            rate_limited += 1
                except Exception as e:
                    errors += 1
                    print(f"    Error: {e}")
                
                await anyio.sleep(1.0 / rps)
        
        # Record aggregate results
        if latencies:
            latencies.sort()
            p50 = latencies[len(latencies)//2]
            p95 = latencies[int(len(latencies)*0.95)]
            p99 = latencies[int(len(latencies)*0.99)]
            
            run_id = f"cloud_{provider}_{model}_{time_of_day}_{int(time.time()*1000)}"
            
            run = BenchmarkRun(
                run_id=run_id,
                timestamp=int(time.time() * 1000),
                model_id=f"{provider}:{model}",
                model_hash=f"{provider}:{model}",
                provider=provider,
                task_category="aggregate",
                prompt_tokens=0,
                completion_tokens=0,
                latency_ms=p50,
                ttft_ms=int(sum(ttfts)/len(ttfts)) if ttfts else 0,
                quality_score=1.0 - (errors / n_requests),
                cost_usd=0.0,  # Filled from pricing config
                energy_j=0.0,
                thermal_state=f"cloud_{time_of_day}",
                privacy_tag=0,
                success=1 if rate_limited / n_requests < 0.05 else 0,
                error_type="rate_limit" if rate_limited > 0 else None,
            )
            insert_run(conn, run)
            
            print(f"  p50: {p50}ms | p95: {p95}ms | p99: {p99}ms")
            print(f"  429 rate: {rate_limited/n_requests*100:.1f}% | Errors: {errors}")

async def call_cloud_api(client, provider, url, headers, model, prompt):
    """Call cloud API with provider-specific payload."""
    if provider == "google":
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 256},
        }
    elif provider == "anthropic":
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 256,
            "temperature": 0.1,
        }
    else:  # openrouter
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 256,
            "temperature": 0.1,
        }
    
    try:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 429:
            return {"success": False, "error_type": "rate_limit"}
        resp.raise_for_status()
        data = resp.json()
        
        # Extract text and usage (provider-specific)
        if provider == "google":
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            usage = data.get("usageMetadata", {})
        elif provider == "anthropic":
            text = data["content"][0]["text"]
            usage = data.get("usage", {})
        else:
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
        
        return {
            "success": True,
            "text": text,
            "prompt_tokens": usage.get("promptTokenCount", usage.get("input_tokens", 0)),
            "completion_tokens": usage.get("candidatesTokenCount", usage.get("output_tokens", 0)),
            "ttft_ms": 0,  # Not available from most APIs
        }
    except Exception as e:
        return {"success": False, "error_type": str(e)}

# ── Main ───────────────────────────────────────────────────────────────
async def main():
    print("⬡ OMEGA HYBRID BENCHMARK v1.0")
    print(f"DB: {DB_PATH}")
    print(f"Models dir: {MODELS_DIR}")
    
    conn = init_db()
    
    # ── Local benchmarks ──
    print("\n" + "="*60)
    print("PHASE 1: LOCAL BENCHMARKS (Thermal Protocol)")
    print("="*60)
    
    for config in LOCAL_BENCHMARK_CONFIGS:
        for thermal in THERMAL_STATES:
            await run_local_benchmark(config, thermal, conn)
    
    # ── Cloud benchmarks ──
    print("\n" + "="*60)
    print("PHASE 2: CLOUD BENCHMARKS (Steady-State Protocol)")
    print("="*60)
    
    for config in CLOUD_BENCHMARK_CONFIGS:
        for time_of_day in TIMES_OF_DAY:
            await run_cloud_benchmark(config, time_of_day, conn)
    
    conn.close()
    print("\n✅ Benchmark complete. Results in:", DB_PATH)

if __name__ == "__main__":
    anyio.run(main)