#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Fix model cards to have BOTH parameters (sampling) AND architecture (model arch).
"""
import yaml
from pathlib import Path

MODELS_DIR = Path("config/model_registry/models")

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

def fix_model_card(filepath):
    frontmatter, body = load_model_card(filepath)
    
    # Check if parameters has architecture fields (meaning it was overwritten)
    params = frontmatter.get('parameters', {})
    
    # If parameters has architecture fields, move them to architecture and restore sampling params
    if 'total' in params or 'architecture' in params or 'experts' in params:
        # Extract architecture data
        arch_data = {
            "total": params.get("total", "Unknown"),
            "active": params.get("active", "Unknown"),
            "architecture": params.get("architecture", "unknown"),
            "experts": params.get("experts", 0),
            "active_experts": params.get("active_experts", 0),
            "shared_experts": params.get("shared_experts", 0),
            "quantization": params.get("quantization", "Unknown"),
            "training_tokens": params.get("training_tokens", "Unknown"),
            "source": params.get("source", "estimated"),
            "verified": params.get("verified", False),
        }
        if params.get("verified"):
            arch_data["verified_date"] = params.get("verified_date")
        
        # Restore sampling parameters
        sampling_params = {
            "temperature": 0.5,
            "top_p": 0.9,
            "top_k": 40,
            "repetition_penalty": 1.0,
            "max_tokens": 8192,
            "stop_sequences": [],
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0
        }
        
        frontmatter['parameters'] = sampling_params
        frontmatter['architecture'] = arch_data
        save_model_card(filepath, frontmatter, body)
        return True
    return False

def main():
    model_files = list(MODELS_DIR.rglob("*.yaml.md"))
    print(f"Checking {len(model_files)} model cards")
    
    fixed = 0
    for filepath in model_files:
        try:
            if fix_model_card(filepath):
                print(f"  ✅ Fixed: {filepath.name}")
                fixed += 1
        except Exception as e:
            print(f"  ❌ {filepath}: {e}")
    
    print(f"\nFixed {fixed} model cards")

if __name__ == "__main__":
    main()
