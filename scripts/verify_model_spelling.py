# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Model Spelling Verifier
# AP: AP-MODEL-VERIFY-v1.0.0
"""
Verifies that all model names used across the engine are consistent and 
defined in the Single Source of Truth (models.yaml).

Prevents 'model name drift' (e.g., 'rocracoon' vs 'roc_racoon').
"""
import yaml
import sys
from pathlib import Path

def verify_models():
    config_dir = Path("config")
    models_path = config_dir / "models.yaml"
    providers_path = config_dir / "providers.yaml"
    
    if not models_path.exists() or not providers_path.exists():
        print("❌ Error: Config files missing.")
        sys.exit(1)
        
    with open(models_path, 'r') as f:
        models_cfg = yaml.safe_load(f)
    with open(providers_path, 'r') as f:
        providers_cfg = yaml.safe_load(f)
        
    # 1. Canonical Local Models (from models.yaml)
    canonical_local = set(models_cfg.get("models", {}).keys())
    
    # 2. Canonical Cloud Models (from providers.yaml)
    canonical_cloud = set()
    for provider in providers_cfg.get("inference", {}).get("fallback_chain", []):
        if "models" in provider:
            canonical_cloud.update(provider["models"])
            
    all_canonical = canonical_local | canonical_cloud
    
    errors = []
    
    # Check Provider Overrides
    for provider in providers_cfg.get("inference", {}).get("fallback_chain", []):
        overrides = provider.get("model_overrides", {})
        for local_name, provider_id in overrides.items():
            if local_name not in canonical_local:
                errors.append(f"Provider {provider['provider']}: local_name '{local_name}' not in models.yaml")
            # We don't strictly check provider_id because it's external to the engine
            
    # Check Agent Roles
    roles = models_cfg.get("agent_roles", {})
    for role, cfg in roles.items():
        model = cfg.get("default_model")
        if model and model not in all_canonical:
            errors.append(f"Role '{role}': default_model '{model}' not in canonical set")
            
    if errors:
        print("❌ Model Spelling Violations Found:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
        
    print("✅ All model names are consistent and canonical.")
    sys.exit(0)

if __name__ == "__main__":
    verify_models()
