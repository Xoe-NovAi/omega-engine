# WAD System Quick Reference (Cline, 2026-11-23)

**Internal-only. Do NOT cherry-pick to the public repo.**

## What a WAD is

A WAD ("Where's All Data") is a self-contained content bundle: manifest + entities + souls + voices + hierarchy + (optional) world/ingestion/templates/adapters/meditate. It's the single extension point for all Omega Engine customization. Engine core (`src/omega/`) is invariant; content (`config/wads/`) is variable.

## IWAD vs PWAD

- IWAD (base): type `iwad`, load priority 10, defines foundational entities.
- PWAD (override): type `pwad`, load priority 100+manifest.priority, extends/overrides IWAD.
- Shadow-Stacking: PWAD entity with same canonical name overrides IWAD entity; both layers tracked in `_wad_sources`.
- Name canonicalization: lowercase, strip apostrophes, spaces→underscores (`Ma'at` → `maat`).

## Directory layout

```
config/wads/<name>/
├── manifest.yaml          # required
├── entities/<id>/<id>.yaml + soul.yaml (+ voice_dna.md, card_assignment_*.yaml)
├── voices/<voice_id>.yaml
├── hierarchy.yaml
├── dispatch.yaml          # optional (falls back to IWAD)
├── world/<sector>/<lump>.yaml
├── ingestion/domains.yaml
├── templates/
├── adapters/
└── meditate/lenses.yaml
```

Dual tree: `config/wads/` ≡ `src/omega/config_data/wads/` (must stay byte-identical; lint enforces).

## Soul schemas (3 supported)

- ANAi: `identity:` + `axioms:` + `directives:` + `voice:` (axiom ceiling 20)
- OED v6.1: `entity:` + `identity.values/strengths`
- Researcher: `entity:` + `domain_affinities` + `methodology`

## Taint-Gate (M11)

- `proposed_lessons.yaml` (agent-written, unvetted) is NEVER injected into identity.
- Only `approved_lessons.yaml` (vetted) or promoted soul blocks inject.
- Review/promote via `scripts/soul_promote.py`.

## Soul persistence paths

- Canonical: `data/entities/<name>/memory/` (approved_lessons, proposed_lessons, sessions)
- Fallback: `data/entities/<name>/` (legacy)
- Resolver: `resolve_entity_memory_paths()` in `entity_workspace.py`.

## Key files to review

- `src/omega/oracle/wad_loader.py` — loader (IWAD/PWAD, Shadow-Stacking, unload, switch, upgrade, WADEntitySchema)
- `src/omega/oracle/entity_registry.py` — registry, DEFAULT_ENTITY_MODEL SSOT, batch_add
- `src/omega/oracle/entity_workspace.py` — scaffold, resolve paths, get_soul_prompt, append_session_anchor
- `src/omega/soul_utils.py` — soul context extraction + TTL cache (60s)
- `src/omega/governance/dispatch_registry.py` — WAD-aware cache, IWAD fallback
- `src/omega/governance/config_resolver.py` — WADS_DIR, get_active_iwad, get_active_pwads

## Validation

- `scripts/validate_wad.py` — manifest, entities, voices, hierarchy, souls, cards, world lumps
- `scripts/lint_wad.py` — dup keys, axiom ceiling, voice_dna refs, hierarchy integrity, card refs, dual-tree drift
- `make validate-wads` / `make temple-grade` (53/53)

## Review focus areas for Cline

1. Dual-tree drift between `config/wads/` and `src/omega/config_data/wads/`.
2. Entity name canonicalization consistency across wad_loader, entity_registry, entity_workspace.
3. Taint-Gate enforcement: proposed_lessons never injected; soul_utils reads approved_lessons.
4. No hardcoded model names (should be `opencode/big-pickle` default or blank).
5. AnyIO compliance (no `import asyncio` in `src/omega/`).
6. Engine-Stack Firewall (no stack logic in `src/omega/`).
7. Test coverage: 75 tests pass in omega-engine; check for regressions.

*⬡ OMEGA ⬡ CLINE ⬡ WAD-QUICKREF ⬡ 2026-11-23 ⬡*