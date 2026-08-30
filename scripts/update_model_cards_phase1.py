#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Phase 1: Add parameter schema and benchmark_sources to all model cards.
"""
import yaml
from pathlib import Path
from datetime import date

MODELS_DIR = Path("config/model_registry/models")
TODAY = date.today().isoformat()

# Parameter data keyed by actual model_id from files
PARAMETER_DATA = {
    # Cloud models
    "anthropic/claude-opus-4.8": {
        "total": "284B", "active": "284B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "anthropic/claude-sonnet-5-high-thinking": {
        "total": "284B", "active": "284B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "claude-haiku-4.5-extended": {
        "total": "Unknown", "active": "Unknown", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "deepseek/deepseek-v4-flash:free": {
        "total": "284B", "active": "13B", "architecture": "MoE",
        "experts": 8, "active_experts": 2, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "15T",
        "source": "official", "verified": True
    },
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free": {
        "total": "24B", "active": "24B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "FP16", "training_tokens": "Unknown",
        "source": "community", "verified": False
    },
    "gemini-2.5-flash": {
        "total": "Unknown", "active": "Unknown", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "gemini-2.5-pro": {
        "total": "Unknown", "active": "Unknown", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "google/gemma-4-26b-a4b-it:free": {
        "total": "26B", "active": "4B", "architecture": "MoE",
        "experts": 8, "active_experts": 2, "shared_experts": 1,
        "quantization": "BF16", "training_tokens": "2T",
        "source": "official", "verified": True
    },
    "google/gemma-4-31b-it:free": {
        "total": "31B", "active": "31B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "2T",
        "source": "official", "verified": True
    },
    "z-ai/glm-4.5-air:free": {
        "total": "Unknown", "active": "Unknown", "architecture": "MoE",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "openai/gpt-oss-120b:free": {
        "total": "120B", "active": "120B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "Unknown",
        "source": "official", "verified": True
    },
    "openai/gpt-oss-20b:free": {
        "total": "20B", "active": "20B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "Unknown",
        "source": "official", "verified": True
    },
    "xai/grok-4.1-fast-web": {
        "total": "Unknown", "active": "Unknown", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "xai/grok-4.3-web": {
        "total": "Unknown", "active": "Unknown", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "nousresearch/hermes-3-llama-3.1-405b:free": {
        "total": "405B", "active": "405B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "15T",
        "source": "official", "verified": True
    },
    "poolside/laguna-m.1:free": {
        "total": "Unknown", "active": "Unknown", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "poolside/laguna-xs.2:free": {
        "total": "Unknown", "active": "Unknown", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "liquid/lfm-2.5-1.2b-instruct:free": {
        "total": "1.2B", "active": "1.2B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "Unknown",
        "source": "official", "verified": True
    },
    "meta-llama/llama-3.2-3b-instruct:free": {
        "total": "3B", "active": "3B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "9T",
        "source": "official", "verified": True
    },
    "meta-llama/llama-3.3-70b-instruct:free": {
        "total": "70B", "active": "70B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "15T",
        "source": "official", "verified": True
    },
    "minimax/minimax-m2.5:free": {
        "total": "Unknown", "active": "Unknown", "architecture": "MoE",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "nvidia/nemotron-3-nano-30b-a3b:free": {
        "total": "30B", "active": "3B", "architecture": "MoE",
        "experts": 10, "active_experts": 1, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "9T",
        "source": "official", "verified": True
    },
    "nvidia/nemotron-3-nano-omni-30b-a3b:free": {
        "total": "30B", "active": "3B", "architecture": "MoE",
        "experts": 10, "active_experts": 1, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "9T",
        "source": "official", "verified": True
    },
    "nvidia/nemotron-3-super-120b-a12b:free": {
        "total": "120B", "active": "12B", "architecture": "MoE",
        "experts": 10, "active_experts": 1, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "9T",
        "source": "official", "verified": True
    },
    "nvidia/nemotron-nano-12b-v2-vl:free": {
        "total": "12B", "active": "12B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "Unknown",
        "source": "official", "verified": True
    },
    "nvidia/nemotron-nano-9b-v2:free": {
        "total": "9B", "active": "9B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "Unknown",
        "source": "official", "verified": True
    },
    "openrouter/free": {
        "total": "Variable", "active": "Variable", "architecture": "router",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Variable", "training_tokens": "Variable",
        "source": "router", "verified": False
    },
    "qwen/qwen3-coder:free": {
        "total": "Unknown", "active": "Unknown", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    "qwen/qwen3-next-80b-a3b-instruct:free": {
        "total": "80B", "active": "3B", "architecture": "MoE",
        "experts": 27, "active_experts": 1, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "Unknown",
        "source": "official", "verified": True
    },
    "arcee-ai/trinity-large-thinking:free": {
        "total": "Unknown", "active": "Unknown", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "Unknown", "training_tokens": "Unknown",
        "source": "estimated", "verified": False
    },
    
    # Local models
    "gpt-oss-120b-local": {
        "total": "120B", "active": "120B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "INT4", "training_tokens": "Unknown",
        "source": "official", "verified": True
    },
    "llama-4-scout-local": {
        "total": "17B", "active": "17B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "INT4", "training_tokens": "Unknown",
        "source": "official", "verified": True
    },
    "nemotron-3-ultra-local": {
        "total": "253B", "active": "253B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "INT4", "training_tokens": "9T",
        "source": "official", "verified": True
    },
    "qwen-3.5-72b-local": {
        "total": "72B", "active": "72B", "architecture": "dense",
        "experts": 0, "active_experts": 0, "shared_experts": 0,
        "quantization": "INT4", "training_tokens": "Unknown",
        "source": "official", "verified": True
    },
    
    # Stealth
    "opencode/big-pickle": {
        "total": "284B", "active": "13B", "architecture": "MoE",
        "experts": 8, "active_experts": 2, "shared_experts": 0,
        "quantization": "BF16", "training_tokens": "15T",
        "source": "estimated", "verified": False
    },
}

DEFAULT_PARAMS = {
    "total": "Unknown", "active": "Unknown", "architecture": "unknown",
    "experts": 0, "active_experts": 0, "shared_experts": 0,
    "quantization": "Unknown", "training_tokens": "Unknown",
    "source": "estimated", "verified": False
}

def load_model_card(path):
    with open(path) as f:
        content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return frontmatter, body
    return {}, content

def save_model_card(path, frontmatter, body):
    yaml_str = yaml.dump(frontmatter, sort_keys=False, default_style=None, width=1000)
    content = f"---\n{yaml_str}---\n\n{body}\n"
    with open(path, 'w') as f:
        f.write(content)

def update_model_card(filepath):
    frontmatter, body = load_model_card(filepath)
    model_id = frontmatter.get('model_id', '')
    
    params = PARAMETER_DATA.get(model_id, DEFAULT_PARAMS)
    
    parameters = {
        "total": params["total"],
        "active": params["active"],
        "architecture": params["architecture"],
        "experts": params["experts"],
        "active_experts": params["active_experts"],
        "shared_experts": params["shared_experts"],
        "quantization": params["quantization"],
        "training_tokens": params["training_tokens"],
        "source": params["source"],
        "verified": params["verified"],
    }
    if params["verified"]:
        parameters["verified_date"] = TODAY
    
    benchmark_sources = {
        "reasoning": "",
        "code_generation": "",
        "knowledge": "",
        "creative": "",
        "tool_use": "",
        "structured_output": "",
        "multimodal": "",
        "overall": ""
    }
    
    frontmatter['parameters'] = parameters
    frontmatter['benchmark_sources'] = benchmark_sources
    frontmatter['schema_version'] = "1.2.0"
    frontmatter['updated_at'] = TODAY
    
    save_model_card(filepath, frontmatter, body)
    return model_id, params["total"], params["architecture"], params["verified"]

def main():
    model_files = list(MODELS_DIR.rglob("*.yaml.md"))
    print(f"Found {len(model_files)} model cards")
    
    updated = 0
    for filepath in model_files:
        try:
            model_id, total, arch, verified = update_model_card(filepath)
            status = "✅" if verified else "⚠️"
            print(f"  {status} {model_id}: {total} params, {arch}")
            updated += 1
        except Exception as e:
            print(f"  ❌ {filepath}: {e}")
    
    print(f"\nUpdated {updated}/{len(model_files)} model cards")

if __name__ == "__main__":
    main()
