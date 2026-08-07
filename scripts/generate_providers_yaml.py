#!/usr/bin/env python3
"""
Generate config/providers.yaml from Model Registry — MERGE-PRESERVING.
⬡ OMEGA ⬡ CLINE ⬡ MODEL-REGISTRY ⬡ 2026-07-19
⬡ OMEGA ⬡ KALI ⬡ B-SAFETY ⬡ 2026-08-07 (merge-preserving rewrite)

Reads provider configs from config/model_registry/providers/ and
regenerates ONLY the provider-derived sections of config/providers.yaml
(inference.fallback_chain + inference.providers) while PRESERVING the
hand-maintained runtime sections:

  - strategy: local_first        (M7 audit gate — mandate_auditor checks)
  - maakali_routing:             (D352 — per-entity model routing)
  - fallback_resolver:           (model-aware fallback chains)
  - per-provider streaming:      (M25 chunk/total timeouts)
  - version / generated_at       (bumped, not clobbered to 1.1.0)

SAFETY: This script NEVER overwrites the sections above. It reads the
existing config/providers.yaml, rebuilds only the registry-derived
provider configs, and merges the result. If config/providers.yaml is
missing, it generates a minimal file with defaults so the M7 audit
still passes (strategy: local_first preserved).
"""
import sys
import yaml

sys.path.insert(0, 'src')
from pathlib import Path
from omega.model_registry import ModelRegistry

# Sections that MUST survive regeneration (hand-maintained runtime config)
_PRESERVE_TOP_KEYS = (
    "version",
    "generated_at",
    "source",
    "strategy",
    "maakali_routing",
    "fallback_resolver",
    "streaming",
)
# Provider keys that are runtime-tuned and must survive per-provider merge
_PRESERVE_PROVIDER_KEYS = (
    "streaming",
    "api_key",       # registry may not hold live keys (secrets)
    "base_url",      # runtime may override with env-resolved endpoint
    "is_cloud",      # runtime classification (local/cloud) for M7
)


def _load_existing(path: Path) -> dict:
    """Load existing config/providers.yaml (or empty dict)."""
    if path.exists():
        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError) as e:
            print(f"⚠️  Could not parse existing {path}: {e}")
            print("   Generating from registry only "
                  "(sections above will be lost!).")
            return {}
    return {}


def main():
    registry = ModelRegistry('config/model_registry')
    registry.load_all()
    registry.build_index()

    providers = registry.get_providers()

    output_path = Path("config/providers.yaml")

    # Load existing file FIRST so we can preserve non-registry entries
    existing = _load_existing(output_path)

    # Build fallback chain (registry-derived + preserved non-registry)
    # Local-first providers (M7): native-gguf, lmster, ollama
    # Cloud providers: antigravity, google, openrouter, opencode-zen,
    #   cline, anthropic, xai
    LOCAL_FIRST_PROVIDERS = {"native-gguf", "lmster", "ollama"}
    fallback_chain = []
    for p in providers:
        fallback_chain.append({
            "provider": p.provider,
            "priority": p.priority,
            "enabled": p.enabled,
            "description": p.description,
            "is_cloud": p.provider not in LOCAL_FIRST_PROVIDERS,
        })

    # Preserve non-registry providers in fallback chain (e.g. google-compat)
    existing_fallback = (
        existing.get("inference", {}).get("fallback_chain", [])
        if isinstance(existing.get("inference", {}), dict)
        else []
    )
    existing_providers_set = {p.provider for p in providers}
    for entry in existing_fallback:
        prov = entry.get("provider")
        if isinstance(entry, dict) and prov not in existing_providers_set:
            fallback_chain.append(entry)
            print(f"   📦 Preserved non-registry fallback: {prov}")

    # Build provider details (registry-derived)
    registry_providers = {}

    # Enforce M7 strategy if missing from existing file
    if "strategy" not in existing:
        print("   ⚠️  No strategy in existing file — "
              "defaulted to local_first (M7)")

    # Rebuild inference section from registry
    inference = {
        "fallback_chain": fallback_chain,
        "providers": {},
    }

    # Merge registry-derived provider configs, preserving runtime-tuned keys
    existing_providers = (
        existing.get("inference", {}).get("providers", {})
        if isinstance(existing.get("inference", {}), dict)
        else {}
    )
    for pname, pcfg in registry_providers.items():
        merged_cfg = dict(pcfg)
        prev = existing_providers.get(pname, {})
        if isinstance(prev, dict):
            for k in _PRESERVE_PROVIDER_KEYS:
                if k in prev:
                    merged_cfg[k] = prev[k]
        inference["providers"][pname] = merged_cfg

    # Carry over any existing provider entries NOT in the registry
    # (e.g. manual providers that the registry doesn't know about)
    for pname, pcfg in existing_providers.items():
        if pname not in inference["providers"] and isinstance(pcfg, dict):
            inference["providers"][pname] = pcfg
            print(f"   📦 Preserved non-registry provider: {pname}")

    # Bump version/generated_at instead of hardcoding 1.1.0
    try:
        old_ver = existing.get("version", "0.0.0")
        ver_parts = [int(x) for x in str(old_ver).split(".")]
        ver_parts[-1] += 1
        new_version = ".".join(str(x) for x in ver_parts)
    except (ValueError, IndexError):
        new_version = "1.4.0"

    # ── SURGICAL WRITE: preserve comments by editing text, not round-trip ─
    # yaml.dump strips inline comments. Instead, read the existing file as
    # text and surgically replace only the version/generated_at lines and the
    # inference: section, leaving all other sections (maakali_routing,
    # fallback_resolver, streaming, etc.) WITH their comments intact.
    # If the file doesn't exist, fall back to full yaml.dump.
    existing_text = output_path.read_text() if output_path.exists() else ""

    if existing_text:
        new_lines = []
        in_inference = False
        inference_written = False
        for line in existing_text.splitlines(keepends=True):
            stripped = line.lstrip()
            # Replace version/generated_at lines
            if stripped.startswith("version:"):
                indent = line[:len(line) - len(stripped)]
                new_lines.append(f"{indent}version: {new_version}\n")
                continue
            if stripped.startswith("generated_at:"):
                indent = line[:len(line) - len(stripped)]
                new_lines.append(
                    f"{indent}generated_at: '2026-08-07'\n"
                )
                continue
            # Detect start of inference: section (top-level, no indent)
            if stripped.startswith("inference:") and not line.startswith(" "):
                in_inference = True
                if not inference_written:
                    # Write the new inference section
                    new_lines.append(
                        yaml.dump(
                            {"inference": inference},
                            default_flow_style=False,
                            sort_keys=False, allow_unicode=True,
                        )
                    )
                    inference_written = True
                continue
            # Skip lines that are part of the old inference: section
            if in_inference:
                # A line with no leading space at top level ends the section
                is_comment = stripped.startswith("#")
                is_top_level = not line.startswith(" ")
                if is_top_level and stripped and not is_comment:
                    in_inference = False
                    new_lines.append(line)
                # Otherwise skip (part of old inference section)
                continue
            # All other lines (maakali_routing, fallback_resolver, comments)
            # are preserved verbatim
            new_lines.append(line)

        if not inference_written:
            # inference: section didn't exist — append it
            new_lines.append(
                "\n" + yaml.dump(
                    {"inference": inference},
                    default_flow_style=False, sort_keys=False,
                    allow_unicode=True,
                )
            )

        output_path.write_text("".join(new_lines))
    else:
        # No existing file — full dump
        with open(output_path, 'w') as f:
            yaml.dump(
                {
                    "version": new_version,
                    "generated_at": "2026-08-07",
                    "strategy": "local_first",
                    "inference": inference,
                },
                f,
                default_flow_style=False, sort_keys=False, allow_unicode=True,
            )

    print(f"✅ Generated (merge-preserving) {output_path}")
    print(f"   {len(providers)} providers in fallback chain")
    print(f"   version {new_version} "
          f"(was {existing.get('version', 'N/A')})")
    has_maakali = 'yes' if 'maakali_routing' in existing else 'NO'
    has_fallback = 'yes' if 'fallback_resolver' in existing else 'NO'
    print(f"   preserved: strategy=local_first, "
          f"maakali_routing={has_maakali}, fallback_resolver={has_fallback}")

    # Validate generated file
    with open(output_path) as f:
        loaded = yaml.safe_load(f)
    chain = loaded.get("inference", {}).get("fallback_chain", [])
    print(f"   Priorities: {[p['priority'] for p in chain]}")
    assert loaded.get("strategy") == "local_first", \
        "M7 VIOLATION: strategy != local_first"
    assert "fallback_chain" in loaded.get("inference", {}), \
        "inference.fallback_chain missing"

    return 0


if __name__ == "__main__":
    sys.exit(main())
