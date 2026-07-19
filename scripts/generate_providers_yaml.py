#!/usr/bin/env python3
"""
Generate config/providers.yaml from Model Registry
⬡ OMEGA ⬡ CLINE ⬡ MODEL-REGISTRY ⬡ 2026-07-19

Reads provider configs from config/model_registry/providers/ and
generates the consolidated config/providers.yaml used by ModelGateway.
"""
import sys, os, yaml
sys.path.insert(0, 'src')
from pathlib import Path
from omega.model_registry import ModelRegistry

def main():
    registry = ModelRegistry('config/model_registry')
    registry.load_all()
    registry.build_index()
    
    providers = registry.get_providers()
    
    # Build fallback chain
    fallback_chain = []
    for p in providers:
        fallback_chain.append({
            "provider": p.provider,
            "priority": p.priority,
            "enabled": p.enabled,
            "description": p.description,
        })
    
    output = {
        "version": "1.1.0",
        "generated_at": "2026-07-19",
        "source": "config/model_registry",
        "inference": {
            "fallback_chain": fallback_chain,
            "providers": {}
        }
    }
    
    # Add provider details
    for p in providers:
        provider_config = {
            "priority": p.priority,
            "enabled": p.enabled,
            "description": p.description,
        }
        if p.api_key:
            provider_config["api_key"] = p.api_key
        if p.base_url:
            provider_config["base_url"] = p.base_url
        if p.model_path:
            provider_config["model_path"] = p.model_path
        if p.n_threads:
            provider_config["n_threads"] = p.n_threads
        if p.supported_models:
            provider_config["supported_models"] = p.supported_models
        
        output["inference"]["providers"][p.provider] = provider_config
    
    output_path = Path("config/providers.yaml")
    with open(output_path, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Generated {output_path}")
    print(f"   {len(providers)} providers in fallback chain")
    
    # Validate generated file
    with open(output_path) as f:
        loaded = yaml.safe_load(f)
    chain = loaded.get("inference", {}).get("fallback_chain", [])
    print(f"   Priorities: {[p['priority'] for p in chain]}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
