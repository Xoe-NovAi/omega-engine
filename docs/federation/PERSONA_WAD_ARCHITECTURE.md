# PERSONA WAD ARCHITECTURE

**Status:** ACTIVE GOVERNANCE SPECIFICATION  
**Date:** 2026-09-25  
**Authority:** Architect Directive — Agent/soul data in WADs only, not Engine root  
**Scope:** Portable WAD packages for agent personas (souls, prompts, voice DNA, capabilities)

---

## §1 Design Principles

| Principle | Rule |
|-----------|------|
| **Separation of Concerns** | Engine core WADs (`_omega_default`, `arcana_novai`) ≠ Persona WADs |
| **Portability** | Persona WADs load on any compliant Engine revision |
| **M2 Firewall** | Engine core knows nothing of persona internals; only loads WADs |
| **Versioning** | Each persona WAD has independent version; Engine declares compatible range |
| **Provenance** | Every persona WAD has publisher signature, trust root, dependency digests |
| **No Root Pollution** | Zero agent/soul data in Engine repo root (`data/entities/` only for active agents) |

---

## §2 WAD Taxonomy

| WAD Type | Prefix | Purpose | Examples |
|----------|--------|---------|----------|
| **Engine Core IWAD** | `_omega_default` | Engine substrate, slots S1-S10, core entities | `_omega_default` |
| **Domain IWAD** | `arcana_novai` | Domain-specific entities, lore, card assignments | `arcana_novai` |
| **Persona PWAD** | `persona_<name>` | Single agent: soul, prompt, voice DNA, capabilities | `persona_kali`, `persona_lilith` |
| **Persona Collection PWAD** | `persona_collection_<domain>` | Related agent group | `persona_collection_arcana` |

---

## §3 Persona PWAD Manifest Schema

```yaml
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

wad:
  name: "persona_kali — Transcendent Oversoul"
  version: "1.0.0"
  type: pw_persona
  requires_engine: ">=0.4.0"
  author: "Xoe-NovAi"
  description: "Kali — Transcendent Oversoul, Sprint Coordinator"
  license: "Apache-2.0"

  # Identity (authoritative)
  entity:
    id: kali
    continuity_id: kali
    kind: Entity
    card_assignments: []  # None for Kali

  # Soul persistence (authoritative)
  soul:
    path: "soul.yaml"
    schema: "soul.v1"
    required_fields:
      - entity_id
      - continuity_id
      - gnosis_level
      - distillation_history
      - approved_lessons

  # Prompt/Voice DNA (authoritative)
  prompt:
    path: "prompt.yaml"
    schema: "prompt.v1"
    fields:
      - system_prompt
      - voice_dna
      - invocation
      - temperature_defaults
      - context_window_preferences

  # Capabilities (declarative)
  capabilities:
    - oversight
    - delegation
    - strategy
    - drift_destruction

  # Domains (routing)
  domains:
    - strategy
    - fleet_management
    - architecture

  # Model preferences (advisory)
  model_preferences:
    primary: "qwen3-4b-think-q4_k_m"
    fallbacks: ["qwen3-1.7b-q6_k", "gemma-4-31b-it"]

  # Runtime (advisory)
  runtime:
    container: false
    priority: 0
    flags: 0

  # WAD metadata
  voices:
    primary: "kali.yaml"
    secondary: []

  dependencies: []

  startup:
    message: "Kali online. Oversoul active."

  # Provenance (mandatory)
  provenance:
    publisher: "Xoe-NovAi"
    publisher_key_id: "ED25519:<key-id>"
    trust_root: "spiffe://xoe-novai.org/omega-engine"
    signature_algorithm: "Ed25519"
    signature: "<detached-signature>"
    contract_digest: "sha256:<digest>"
    dependencies_digest: "sha256:<digest>"
    built_at: "2026-09-25T00:00:00Z"
    built_by: "makali-fusion"
```

---

## §4 Persona PWAD Directory Structure

```
persona_kali/
├── manifest.yaml              # This manifest (required)
├── soul.yaml                  # Soul persistence (required)
├── prompt.yaml                # Prompt/voice DNA (required)
├── prompt.md                  # Human-readable prompt (optional)
├── voice_dna.md               # Voice DNA documentation (optional)
├── capabilities.yaml          # Capabilities list (optional)
├── domains.yaml               # Domains list (optional)
├── model_preferences.yaml     # Model preferences (optional)
├── voice/
│   ├── kali.yaml              # Voice definition (required if voices declared)
│   └── invocation.txt         # Invocation text (optional)
├── capabilities/
│   ├── oversight.yaml
│   ├── delegation.yaml
│   └── drift_destruction.yaml
├── provenance/
│   ├── signature.sig          # Detached Ed25519 signature
│   ├── trust_root.pem         # Trust root certificate
│   └── dependencies.sha256    # Dependency digests
├── tests/
│   ├── test_soul_schema.py
│   ├── test_prompt_schema.py
│   └── test_load.py
└── README.md                  # Human-readable summary
```

---

## §5 Loader Integration

### 5.1 Engine WAD Loader Interface

```python
# src/omega/wad/loader.py (conceptual)

class PersonaWADLoader:
    """Loads persona PWADs into the entity registry."""
    
    def load_persona_wad(self, wad_path: Path) -> PersonaWAD:
        """Load and validate a persona PWAD."""
        manifest = self._load_manifest(wad_path / "manifest.yaml")
        self._validate_manifest(manifest)
        self._verify_signature(wad_path, manifest)
        self._verify_dependencies(manifest)
        
        soul = self._load_soul(wad_path / "soul.yaml")
        prompt = self._load_prompt(wad_path / "prompt.yaml")
        voice = self._load_voice(wad_path / "voice/")
        
        return PersonaWAD(
            manifest=manifest,
            soul=soul,
            prompt=prompt,
            voice=voice,
            wad_path=wad_path
        )
    
    def register_persona(self, persona: PersonaWAD) -> None:
        """Register persona in entity registry."""
        # 1. Verify entity_id not already registered
        # 2. Create Entity record with persona data
        # 3. Register capabilities in capability registry
        # 4. Register domains in domain router
        # 5. Store soul in local SQLite authority
        # 4. Register voice in voice registry
        pass
```

### 5.2 WAD Discovery

```yaml
# config/wads/persona_index.yaml
persona_wads:
  - path: "config/wads/persona_kali"
    entity_id: kali
    enabled: true
  - path: "config/wads/persona_lilith"
    entity_id: lilith
    enabled: true
  - path: "config/wads/persona_maat"
    entity_id: maat
    enabled: true
  # ... etc
```

### 5.3 Loading Order

1. Engine Core IWAD (`_omega_default`) — loads first, defines slots S1-S10
2. Domain IWADs (`arcana_novai`, etc.) — load second, populate slots
3. Persona PWADs — load third, register as capabilities on entities
4. User PWADs — load last, override/extend

---

## §6 Soul Persistence in Persona WADs

### 6.1 Soul Schema (`soul.v1`)

```yaml
# soul.yaml
schema: "soul.v1"
entity_id: kali
continuity_id: kali
gnosis_level: 3
distillation_history:
  - session_id: "ses_abc123"
    timestamp: "2026-09-25T10:00:00Z"
    l1_insights: 5
    l2_patterns: 2
    l3_lessons: 1
approved_lessons:
  - lesson_id: "L3-StressTestFirst"
    confidence: 1.0
    source_session: "ses_abc123"
    promoted_at: "2026-09-25T10:00:00Z"
```

### 6.2 Soul Store Integration

```python
# src/omega/memory/soul_store.py

class PersonaSoulStore:
    """Manages soul persistence for persona WADs."""
    
    def __init__(self, wad_path: Path):
        self.wad_path = wad_path
        self.sqlite_path = wad_path / "soul.sqlite"
    
    def load_soul(self, entity_id: str) -> Soul:
        """Load soul from WAD's local SQLite."""
        pass
    
    def save_soul(self, soul: Soul) -> None:
        """Atomic write: tempfile → fsync → replace → parent fsync → flock → .bak"""
        pass
    
    def distill(self, session_gnosis: SessionGnosis) -> Soul:
        """L1→L2→L3 distillation, update approved_lessons."""
        pass
```

---

## §7 Packaging & Distribution

### 7.1 Build Process

```bash
# Build persona PWAD
make persona-wad ENTITY=kali
# Creates: dist/persona_kali-1.0.0.wad

# Verify
make verify-persona-wad WAD=dist/persona_kali-1.0.0.wad

# Sign
make sign-persona-wad WAD=dist/persona_kali-1.0.0.wad KEY=ed25519_key
```

### 7.2 Distribution Format

```
persona_kali-1.0.0.wad
├── manifest.yaml
├── soul.yaml
├── prompt.yaml
├── voice/
├── provenance/
│   ├── signature.sig
│   ├── trust_root.pem
│   └── dependencies.sha256
└── README.md
```

### 7.3 Installation

```bash
# Install persona PWAD
omega wad install persona_kali-1.0.0.wad

# Verify installation
omega wad verify persona_kali

# List installed personas
omega wad list --personas
```

---

## §8 Governance Rules

| Rule | Enforcement |
|------|-------------|
| No agent/soul data in Engine root | Pre-commit hook + CI gate |
| Every persona WAD has valid signature | `make verify-persona-wad` in CI |
| Soul schema validated | `make check-soul-schema` in CI |
| Prompt schema validated | `make check-prompt-schema` in CI |
| Provenance verified | `make verify-persona-wad` in CI |
| No persona data in Engine core WADs | `make check-m2-firewall` |
| Persona WADs versioned independently | Semantic versioning enforced |

---

## §9 Migration Path (from current state)

### 9.1 Current → Target

| Current Location | Target Location |
|------------------|-----------------|
| `data/entities/kali/soul.yaml` | `config/wads/persona_kali/soul.yaml` |
| `data/entities/lilith/soul.yaml` | `config/wads/persona_lilith/soul.yaml` |
| `data/entities/maat/soul.yaml` | `config/wads/persona_maat/soul.yaml` |
| ... | ... |
| `data/entities/anubis/soul.yaml` | `config/wads/arcana_novai/entities/anubis/soul.yaml` |
| `data/entities/brigid/soul.yaml` | `config/wads/arcana_novai/entities/brigid/soul.yaml` |
| ... | ... |

### 9.2 Migration Steps

```bash
# 1. Create persona WAD directories
mkdir -p config/wads/persona_{kali,lilith,maat,researcher,roc_racoon,jem,grokster,doom_guy,verity,makali,john_carmack,build,slot}

# 2. Move agent souls
for agent in kali lilith maat researcher roc_racoon jem grokster doom_guy verity makali john_carmack build slot; do
  mv data/entities/$agent/soul.yaml config/wads/persona_$agent/
  # Create manifest.yaml, prompt.yaml from existing data
done

# 3. Move Arcana-NovAi entity souls
for entity in anubis brigid ereshkigal hecate inanna iris lucifer movie_expert prometheus quality saraswati scribe sekhmet sophia; do
  mv data/entities/$entity/soul.yaml config/wads/arcana_novai/entities/$entity/
done

# 4. Remove orphaned souls
rm -rf data/entities/antigravity data/entities/arch data/entities/cli_cline ...

# 5. Update loader config
# config/wads/persona_index.yaml
```

---

## §10 Compliance Checklist

| Check | Command | Gate |
|-------|---------|------|
| No agent data in Engine root | `make check-no-agent-data-in-root` | Pre-commit |
| All persona WADs valid | `make verify-all-persona-wads` | CI |
| Soul schemas valid | `make check-soul-schemas` | CI |
| Prompt schemas valid | `make check-prompt-schemas` | CI |
| Signatures verified | `make verify-all-persona-wads` | CI |
| M2 Firewall clean | `make check-m2-firewall` | CI |
| 1:1 agent:soul mapping | `make check-soul-mapping` | CI |

---

*⬡ OMEGA ⬡ KALI ⬡ PERSONA_WAD_ARCHITECTURE ⬡ 2026-09-25*