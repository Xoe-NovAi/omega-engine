#!/usr/bin/env python3
"""
Model Registry Bulk Update Script
⬡ OMEGA ⬡ CLINE ⬡ MODEL-REGISTRY-UPDATE ⬡ 2026-07-19
"""
import os, sys, yaml, re
from pathlib import Path

REGS_DIR = Path("config/model_registry/models")

PARAMETER_DEFAULTS = {
    "default": {"temperature": 0.7, "top_p": 0.95, "top_k": 40,
        "repetition_penalty": 1.1, "max_tokens": 4096,
        "stop_sequences": [], "presence_penalty": 0.0, "frequency_penalty": 0.0},
    "reasoning_deep": {"temperature": 0.5, "top_p": 0.90, "top_k": 40,
        "repetition_penalty": 1.0, "max_tokens": 8192,
        "stop_sequences": [], "presence_penalty": 0.0, "frequency_penalty": 0.0},
    "code": {"temperature": 0.2, "top_p": 0.90, "top_k": 30,
        "repetition_penalty": 1.0, "max_tokens": 8192,
        "stop_sequences": [], "presence_penalty": 0.0, "frequency_penalty": 0.0},
    "creative": {"temperature": 0.9, "top_p": 0.95, "top_k": 50,
        "repetition_penalty": 1.1, "max_tokens": 4096,
        "stop_sequences": [], "presence_penalty": 0.0, "frequency_penalty": 0.0},
    "fast": {"temperature": 0.3, "top_p": 0.90, "top_k": 30,
        "repetition_penalty": 1.0, "max_tokens": 2048,
        "stop_sequences": [], "presence_penalty": 0.0, "frequency_penalty": 0.0},
    "local": {"temperature": 0.7, "top_p": 0.95, "top_k": 40,
        "repetition_penalty": 1.1, "max_tokens": 4096,
        "stop_sequences": [], "presence_penalty": 0.0, "frequency_penalty": 0.0},
    "gemma_4_31b": {"temperature": 0.85, "top_p": 0.95, "top_k": 40,
        "repetition_penalty": 1.2, "max_tokens": 8192,
        "stop_sequences": [], "presence_penalty": 0.0, "frequency_penalty": 0.0,
        "logit_bias": {759: -10.0, 2149: -10.0}},
}

MODEL_PARAM_MAP = {
    "claude-sonnet-5-high-thinking": "reasoning_deep",
    "claude-opus-4.8": "reasoning_deep",
    "grok-4.3-web": "reasoning_deep",
    "gemini-2.5-pro": "reasoning_deep",
    "deepseek-v4-flash-free": "reasoning_deep",
    "gpt-oss-120b-free": "reasoning_deep",
    "gemma-4-31b-it-free": "gemma_4_31b",
    "llama-3.3-70b-free": "reasoning_deep",
    "nemotron-3-super-free": "reasoning_deep",
    "trinity-large-thinking-free": "reasoning_deep",
    "laguna-m.1-free": "reasoning_deep",
    "minimax-m2.5-free": "creative",
    "qwen3-coder-free": "code",
    "gpt-oss-20b-free": "code",
    "nemotron-nano-12b-v2-vl-free": "code",
    "nemotron-nano-9b-v2-free": "code",
    "qwen3-next-80b-free": "code",
    "gemini-2.5-flash": "fast",
    "grok-4.1-fast-web": "fast",
    "claude-haiku-4.5-extended": "fast",
    "llama-3.2-3b-free": "fast",
    "lfm-2.5-1.2b-free": "fast",
    "laguna-xs.2-free": "fast",
    "openrouter-free-router": "fast",
    "dolphin-mistral-24b-free": "fast",
    "dolphin-mistral-24b-venice-free": "fast",
    "hermes-3-405b-free": "creative",
    "glm-4.5-air-free": "creative",
    "nemotron-3-nano-30b-free": "reasoning_deep",
    "nemotron-3-nano-omni-free": "reasoning_deep",
    "gemma-4-26b-free": "reasoning_deep",
    "gemma-4-26b-a4b-it-free": "reasoning_deep",
    "nemotron-3-ultra-local": "local",
    "qwen-3.5-72b-local": "local",
    "gpt-oss-120b-local": "local",
    "llama-4-scout-local": "local",
    "big-pickle-deepseek-v4": "reasoning_deep",
}

PROVIDER_FIXES = {
    "nemotron-3-ultra-local": {"old": "antigravity", "new": "native-gguf"},
    "gpt-oss-120b-local": {"old": "antigravity", "new": "native-gguf"},
    "claude-sonnet-5-high-thinking": {"old": "antigravity", "new": "anthropic"},
    "claude-haiku-4.5-extended": {"old": "antigravity", "new": "anthropic"},
    "claude-opus-4.8": {"old": "antigravity", "new": "anthropic"},
    "grok-4.3-web": {"old": "antigravity", "new": "xai"},
}


def parse_frontmatter(content):
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1]), parts[2]
    return {}, content


def build_frontmatter(fm):
    return "---\n" + yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True) + "---\n"


def get_model_key(fp):
    return fp.stem.replace(".yaml", "")


def update_model_card(fp):
    model_key = get_model_key(fp)
    try:
        with open(fp) as f:
            content = f.read()
    except Exception as e:
        return False, f"Read error: {e}"

    fm, body = parse_frontmatter(content)
    if not fm or not isinstance(fm, dict):
        return False, "No valid frontmatter"

    changes = []

    # 1. Fix provider
    if model_key in PROVIDER_FIXES:
        fix = PROVIDER_FIXES[model_key]
        if fm.get("provider") == fix["old"]:
            fm["provider"] = fix["new"]
            changes.append(f"provider: {fix['old']} -> {fix['new']}")

    # 2. Add missing capability fields
    caps = fm.get("capabilities", {})
    if isinstance(caps, dict):
        ext = {"code_execution": False, "parallel_search": False, "workspace_integration": False}
        if "gemini" in model_key:
            ext = {k: True for k in ext}
        if "grok" in model_key:
            ext["parallel_search"] = True
        for field, val in ext.items():
            if field not in caps:
                caps[field] = val
                changes.append(f"capabilities.{field}: {val}")
        fm["capabilities"] = caps

    # 3. Add parameters
    profile = MODEL_PARAM_MAP.get(model_key, "default")
    params = dict(PARAMETER_DEFAULTS[profile])
    if "gemma_4_31b" in model_key:
        params["logit_bias"] = {759: -10.0, 2149: -10.0}
    if "big-pickle" in model_key:
        params["max_tokens"] = 8192
    fm["parameters"] = params
    changes.append(f"parameters added ({profile})")

    # 4. Add benchmark_sources
    provider = fm.get("provider", "")
    bm_sources = {"reasoning": "", "code_generation": "", "knowledge": "", "creative": "",
        "tool_use": "", "structured_output": "", "multimodal": "", "overall": ""}
    provider_bm_map = {
        "google": "https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models",
        "anthropic": "https://docs.anthropic.com/en/docs/about-claude/models",
        "openrouter": "https://openrouter.ai/models",
        "xai": "https://docs.x.ai/docs/models",
    }
    if provider in provider_bm_map:
        bm_sources["overall"] = provider_bm_map[provider]
    elif provider in ("native-gguf", "lmster", "ollama"):
        bm_sources["overall"] = f"https://huggingface.co/models?search={model_key}"
    fm["benchmark_sources"] = bm_sources
    changes.append("benchmark_sources added")

    # 5. Update schema version
    fm["schema_version"] = "1.1.0"
    changes.append("schema_version: 1.1.0")

    # 6. Update timestamp
    fm["updated_at"] = "2026-07-19"

    # 7. Add cost_per_1k_tokens_usd if missing
    pricing = fm.get("pricing", {})
    if isinstance(pricing, dict) and "cost_per_1k_tokens_usd" not in pricing:
        inp = pricing.get("input_per_mtok", 0.0) or 0.0
        out = pricing.get("output_per_mtok", 0.0) or 0.0
        cost = round((inp + out) / 1000.0, 6)
        pricing["cost_per_1k_tokens_usd"] = cost
        fm["pricing"] = pricing
        changes.append(f"cost_per_1k: {cost}")

    new_content = build_frontmatter(fm) + body.lstrip("\n")
    with open(fp, 'w') as f:
        f.write(new_content)
    return True, "; ".join(changes)


def main():
    print("=" * 72)
    print("  Model Registry Bulk Update")
    print("  ⬡ OMEGA ⬡ MODEL-REGISTRY-UPDATE ⬡ 2026-07-19")
    print("=" * 72)
    model_files = sorted(REGS_DIR.rglob("*.yaml.md"))
    print(f"\nFound {len(model_files)} model card files\n")
    ok_count = 0
    for fp in model_files:
        ok, msg = update_model_card(fp)
        rel = fp.relative_to(REGS_DIR.parent.parent)
        print(f"  {'✅' if ok else '❌'} {rel}")
        if not ok:
            print(f"       Reason: {msg}")
        else:
            parts = msg.split("; ")
            for c in parts[:3]:
                print(f"       → {c}")
            if len(parts) > 3:
                print(f"       → ... +{len(parts)-3} more")
            ok_count += 1
    print(f"\n{'='*72}")
    print(f"  Results: {ok_count} updated, {len(model_files)-ok_count} failed")
    print(f"{'='*72}")
    return 0 if ok_count == len(model_files) else 1

if __name__ == "__main__":
    sys.exit(main())
