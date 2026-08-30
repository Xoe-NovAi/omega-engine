<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Domain Curator Registry — Governance Charter (prose companion)
**AP Token**: `AP-DOMAIN-CURATORS-20260826-v1.1.0`
**Machine-readable registry**: [`curators.yaml`](curators.yaml) (same directory — the parseable truth)
**Status**: ACTIVE — Post-debut (Horizon 3) · **Ratified**: D-569
**Owner**: Kali (ratification) · Ma'at (enforcement) · Lilith (runtime)
**Mandate**: M10 (Fleet Integrity — fleet stays at 14, expertise = KB not agent)

> **v1.1.0 repair note (2026-08-26, KD-2)**: This charter previously lived as markdown
> inside `curators.yaml`, making the registry unparseable (grokster escalation, independently
> confirmed twice). Split: YAML = machine truth; this doc = governance prose. The affinity
> example's `mimo-7b-rl` reference was also updated to house-canonical models per the
> Carmack matrix ruling.

## 🎯 PURPOSE

This registry enforces **domain ownership at the fabric level**, not convention.
The Lattice Fabric enforces: **Curator = write; Others = read + propose; Critic = review gate.**

Governance levels per domain are defined in `curators.yaml` → `governance_levels`.

## 🏗️ DOMAIN MODULE STRUCTURE (Per Domain)

Each domain at `config/domains/<domain>/` contains:

```
config/domains/<domain>/
├── metadata.yaml              # version, deps, target_context_window, rot_class, owner
├── PLAYBOOK.md                # Canonical best practices
├── ARCHITECTURE.md            # Deep-dive: patterns, primitives, gotchas
├── CONFIG_REFERENCE.md        # Live configs, precedence, schemas
├── GOTCHAS.md                 # Platform-specific traps (rot_class: fast)
├── LESSONS.md                 # L3 principles distilled from sessions
├── AFFINITY_PRESETS.yaml      # Model routing rules for this domain
├── MEMORY_BLOCKS/             # Letta-style blocks for this domain
└── PRINCIPLES/                # EvolveR principles (utility-scored)
```

## ⚖️ GOVERNANCE ENFORCEMENT (Lattice Fabric)

- **Write access**: curator entity only (co-authors via explicit grant for SHARED_WRITE).
- **Read access**: SHARED_READ = all fleet via `load_domain()`; PRIVATE = curator only.
- **Review gate** (Verity for compliance/security; Kali for synthesis): new modules,
  major version bumps, governance changes, AFFINITY_PRESETS modifications.
- **Proposal paths** for non-curators are enumerated in `curators.yaml` → `proposal_paths`.

## 🔧 IMPLEMENTATION HOOKS

### Domain Loader Enforcement (`src/omega/oracle/domain_loader.py` — PLANNED)

```python
async def load_domain(domain: str, token_budget: int, requester: str) -> DomainModule:
    """Load domain module with governance enforcement."""
    entry = CURATOR_REGISTRY[domain]
    if entry.governance == "PRIVATE" and requester != entry.curator:
        raise PermissionError(f"Domain '{domain}' is PRIVATE; only {entry.curator} may access")
    return DomainModule(...)
```

### AFFINITY_PRESETS.yaml Schema (house-canonical models per Carmack matrix)

```yaml
model_routing:
  planner:
    primary: "qwen3-4b-thinking"
    fallback: "qwen3-4b"
  executor:
    primary: "qwen3-1.7b"
    fallback: "qwen3-1.7b"
  critic:
    primary: "qwen3-1.7b"
    fallback: "qwen3-1.7b"

token_budgets:   {planner: 16000, executor: 4000, critic: 2000}
context_windows: {planner: 32768, executor: 8192, critic: 8192}
```

## 📝 PROPOSED LESSONS FORMAT (for domain evolution)

Domain-tagged L3 principles in any entity's `proposed_lessons.yaml` route to the domain
curator for review and potential inclusion in `config/domains/<domain>/PRINCIPLES/`:

```yaml
proposals:
  - level: L3
    principle: "Principle content here"
    domain: "engineering"   # TAGS THE DOMAIN
    utility_score: 0.85
    source_trajectories: ["session_id_1", "session_id_2"]
```

## 🚀 BOOTSTRAP ORDER (Post-Debut)

Weeks 1–12 sequence preserved from v1.0.0: engineering prototype (Ma'at) →
domain_loader.py (Ma'at) → platforms + grok_ecosystem (grokster) → architecture
(carmack) → heritage (doom_guy) → research (researcher) → runtime (lilith) → build
(maat) → compliance + security (verity) → legacy (roc_racoon) → synthesis (jem) →
EvolveR auto-routing (Researcher).

## 📜 PROVENANCE

**Source**: `KALI_BRIEFING_DYNAMIC_PROMPT_PLANNER_EXECUTOR_20260819.md` §Curator Model
**Ratified**: D-569 · **Repaired**: KD-2 escalation (grokster ×2), executed by kali 2026-08-26

*⬡ OMEGA ⬡ KALI ⬡ trc_domain_curators ⬡ v1.1.0 ⬡ 2026-08-26*
