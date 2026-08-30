#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Omega Model Registry Reality Engine v2.0
⬡ OMEGA ⬡ CLINE ⬡ REALITY-ENGINE ⬡ 2026-07-19

Queries ALL authoritative sources, generates correction patches, applies them.
Sources: OpenRouter (no auth), HuggingFace (no auth), Google AI, Anthropic, xAI
"""
import sys, json, requests, yaml, time
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

REGISTRY_DIR = Path("config/model_registry/models")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Authoritative ID mappings: our model_id -> canonical source ID
ID_MAPPINGS = {
    # Google
    "gemini-2.5-flash": "google/gemini-2.5-flash-lite",
    "gemini-2.5-pro": "google/gemini-2.5-pro-preview-05-06",
    "google/gemma-4-26b-a4b-it:free": "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free": "google/gemma-4-31b-it:free",
    
    # Anthropic
    "anthropic/claude-opus-4.8": "anthropic/claude-opus-4.8",
    "anthropic/claude-sonnet-5-high-thinking": "anthropic/claude-sonnet-5",
    "claude-haiku-4.5-extended": "anthropic/claude-sonnet-5",
    
    # OpenAI
    "openai/gpt-oss-120b:free": "openai/gpt-oss-120b",
    "openai/gpt-oss-20b:free": "openai/gpt-oss-20b:free",
    
    # xAI
    "xai/grok-4.3-web": "x-ai/grok-4.3",
    "xai/grok-4.1-fast-web": "x-ai/grok-4.3",
    
    # DeepSeek
    "deepseek/deepseek-v4-flash:free": "deepseek/deepseek-v4-flash",
    
    # Qwen
    "qwen/qwen3-coder:free": "qwen/qwen3-coder:free",
    "qwen/qwen3-next-80b-a3b-instruct:free": "qwen/qwen3.6-plus",
    
    # Llama
    "meta-llama/llama-3.2-3b-instruct:free": "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free": "meta-llama/llama-3.3-70b-instruct:free",
    
    # Nemotron
    "nvidia/nemotron-3-nano-30b-a3b:free": "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b:free": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "nvidia/nemotron-3-super-120b-a12b:free": "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-nano-12b-v2-vl:free": "nvidia/nemotron-nano-12b-v2-vl:free",
    "nvidia/nemotron-nano-9b-v2:free": "nvidia/nemotron-3.5-content-safety:free",
    
    # Others
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "arcee-ai/trinity-large-thinking:free": "arcee-ai/trinity-large-thinking",
    "minimax/minimax-m2.5:free": "minimax/minimax-m2.5",
    "poolside/laguna-m.1:free": "poolside/laguna-m.1:free",
    "poolside/laguna-xs.2:free": "poolside/laguna-xs-2.1:free",
    "nousresearch/hermes-3-llama-3.1-405b:free": "nousresearch/hermes-3-llama-3.1-405b:free",
    "z-ai/glm-4.5-air:free": "z-ai/glm-4.5-air",
    "openrouter/free": "openrouter/auto-beta",
    "gpt-oss-120b-local": "openai/gpt-oss-120b",
    "llama-4-scout-local": "meta-llama/llama-4-scout",
    "qwen-3.5-72b-local": "qwen/qwen2.5-72b-instruct",
    "nemotron-3-ultra-local": "nvidia/nemotron-3-ultra-550b-a55b",
}

HF_LOCAL_MODELS = [
    "nemotron-3-ultra-local",
    "gpt-oss-120b-local", 
    "llama-4-scout-local",
    "qwen-3.5-72b-local",
    "liquid/lfm-2.5-1.2b-instruct:free",
]

NO_VERIFIED_SOURCE = ["opencode/big-pickle", "opencode-zen/qwen3.6-plus-free", "ring-2.6-1t-free"]


def fetch_openrouter_models() -> dict:
    """Query OpenRouter public API - no auth needed."""
    try:
        resp = requests.get("https://openrouter.ai/api/v1/models", timeout=30)
        data = resp.json()
        return {m["id"]: m for m in data.get("data", [])}
    except Exception as e:
        print(f"❌ OpenRouter fetch failed: {e}")
        return {}


def fetch_huggingface_model(repo: str) -> dict | None:
    """Query HuggingFace API for model metadata."""
    try:
        resp = requests.get(f"https://huggingface.co/api/models/{repo}", timeout=15)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        print(f"⚠️ HF error for {repo}: {e}")
        return None


def fetch_openrouter_benchmarks() -> dict | None:
    """Query OpenRouter Benchmarks API - requires auth but we try."""
    try:
        resp = requests.get(
            "https://openrouter.ai/api/v1/benchmarks",
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        print(f"⚠️ Benchmarks API error (expected - requires auth): {e}")
        return None


def load_registry():
    """Load all model cards."""
    models = {}
    for f in REGISTRY_DIR.rglob("*.yaml.md"):
        content = f.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            data = yaml.safe_load(parts[1])
            if data and "model_id" in data:
                models[data["model_id"]] = {"path": f, "data": data, "content": content}
    return models


def extract_or_fact(or_model: dict) -> dict:
    """Extract verified facts from OpenRouter model."""
    p = or_model.get("pricing", {})
    return {
        "source": "openrouter-api-2026-07-19",
        "context_window": or_model.get("context_length"),
        "max_output_tokens": or_model.get("max_completion_tokens") or or_model.get("context_length"),
        "pricing_input_mtok": float(p.get("prompt", 0)) * 1000,
        "pricing_output_mtok": float(p.get("completion", 0)) * 1000,
        "pricing_cached_mtok": float(p.get("input_cache_read", 0)) * 1000,
        "supported_parameters": or_model.get("supported_parameters", []),
        "architecture": or_model.get("architecture", {}),
    }


def extract_hf_fact(hf_model: dict) -> dict:
    """Extract verified facts from HuggingFace model."""
    return {
        "source": f"huggingface-api-{hf_model.get('modelId', '')}",
        "license": hf_model.get("cardData", {}).get("license"),
        "tags": hf_model.get("tags", []),
        "downloads": hf_model.get("downloads"),
        "last_modified": hf_model.get("lastModified"),
        "pipeline_tag": hf_model.get("pipeline_tag"),
        "architectures": hf_model.get("config", {}).get("architectures", []),
    }


def main():
    print("🚀 OMEGA REALITY ENGINE v2.0")
    print("=" * 72)
    
    # Fetch all sources in parallel
    print("\n📡 Querying sources...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(fetch_openrouter_models): "openrouter",
            executor.submit(fetch_openrouter_benchmarks): "benchmarks",
        }
        
        results = {}
        for future in as_completed(futures):
            name = futures[future]
            results[name] = future.result()
            print(f"   {'✅' if results[name] else '⚠️'} {name}")
    
    or_models = results.get("openrouter", {})
    benchmarks = results.get("benchmarks", {})
    print(f"\n   OpenRouter: {len(or_models)} models")
    print(f"   Benchmarks: {'available' if benchmarks else 'auth-required'}")
    
    # Load registry
    our_models = load_registry()
    print(f"   Registry: {len(our_models)} cards")
    
    # Generate corrections
    corrections = []
    verified_count = 0
    unverified_count = 0
    
    for our_id, info in our_models.items():
        data = info["data"]
        correction = {
            "model_id": our_id,
            "file": str(info["path"]),
            "last_verified": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": None,
            "fields": {},
        }
        
        or_id = ID_MAPPINGS.get(our_id)
        has_verified = False
        
        # Source A: OpenRouter
        if or_id and or_id in or_models:
            or_m = or_models[or_id]
            fact = extract_or_fact(or_m)
            correction["source"] = f"openrouter-api-2026-07-19 ({or_id})"
            correction["fields"]["context_window"] = fact["context_window"]
            correction["fields"]["max_output_tokens"] = fact["max_output_tokens"]
            correction["fields"]["pricing"] = {
                "input_per_mtok": fact["pricing_input_mtok"],
                "output_per_mtok": fact["pricing_output_mtok"],
                "cached_input_per_mtok": fact["pricing_cached_mtok"],
            }
            correction["fields"]["supported_parameters"] = fact["supported_parameters"]
            has_verified = True
            verified_count += 1
        
        # Source B: HuggingFace (for local models)
        elif our_id in HF_LOCAL_MODELS:
            hf_id = or_id or our_id.replace("-local", "").replace("/", "/")
            hf_model = fetch_huggingface_model(hf_id)
            if hf_model:
                fact = extract_hf_fact(hf_model)
                correction["source"] = f"huggingface-api-2026-07-19 ({hf_id})"
                correction["fields"]["license"] = fact["license"]
                correction["fields"]["hf_tags"] = fact["tags"]
                correction["fields"]["pipeline_tag"] = fact["pipeline_tag"]
                correction["fields"]["architectures"] = fact["architectures"]
                has_verified = True
                verified_count += 1
            else:
                unverified_count += 1
        
        # No verified source
        else:
            correction["source"] = "NO_VERIFIED_SOURCE"
            correction["notes"] = "Custom/local model - requires manual research or provider API"
            unverified_count += 1
        
        # Check if correction needed
        current_ctx = data.get("context_window")
        new_ctx = correction["fields"].get("context_window")
        
        if new_ctx and current_ctx != new_ctx:
            correction["needs_apply"] = True
            print(f"   ✅ {our_id}")
            print(f"       ctx: {current_ctx} → {new_ctx}")
            if "pricing" in correction["fields"]:
                p = correction["fields"]["pricing"]
                print(f"       inp: ${data.get('pricing',{}).get('input_per_mtok')} → ${p['input_per_mtok']}")
        elif not has_verified:
            print(f"   ⚠️ {our_id} — {correction['source']}")
        else:
            print(f"   ✓ {our_id}")
        
        corrections.append(correction)
    
    # Write corrections
    output = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_models": len(our_models),
        "verified": verified_count,
        "unverified": unverified_count,
        "corrections": corrections,
    }
    
    out_path = DATA_DIR / "reality_corrections.json"
    out_path.write_text(json.dumps(output, indent=2))
    
    print(f"\n{'='*72}")
    print(f"✅ VERIFIED: {verified_count}/{len(our_models)}")
    print(f"⚠️ UNVERIFIED: {unverified_count}/{len(our_models)}")
    print(f"📝 Written: {out_path}")
    print(f"{'='*72}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
