---
schema_version: "1.0"
rule_id: "RULE-MANDATE-HIERARCHY"
authority: "M1 AnyIO + M2 Engine-Stack Firewall + M13 Temple-Grade + M27 Tracking Integrity"
applies_to: "all-agents"
date: "2026-08-27"
status: "ACTIVE"
---

# Architecture Rule 2: Mandate Hierarchy (M1, M2, M13, M27)

> **Law → Sprint SSOT → Hub NEXT_ACTION → Long-Horizon Vision → Corpus Map.**
> If any conflict, Law wins.

## The 5-Tier Conflict Resolution

When documents disagree, resolve in this order:

1. **Law** → `SOVEREIGN_MANDATES.md` (M1-M27, non-negotiable)
2. **Sprint SSOT** → `docs/strategy/DEBUT_REMEDIATION_MANUAL_<date>.md` + `data/coordination/ACTIVE_SPRINT.json`
3. **Live Pointer** → Hivemind `NEXT_ACTION`
4. **Long-Horizon Vision** → `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` (read-only unless Architect reopens)
5. **Ideas Graveyard** → `docs/strategy/STRATEGY_CORPUS_MAP.md` (PARKED / ARCHIVE only)

If Ark §4, Corpus Map, or any other vision doc disagrees with the Sprint SSOT,
**the Sprint SSOT wins until Kali marks it superseded.**

## Mandates (the 27 laws)

Full text: `SOVEREIGN_MANDATES.md` (v3.8.0, 242 lines).
Condensed (Tier-0 injection): `MANDATES_CONDENSED.md` (51 lines, one row per mandate).

**Critical five for oversight**: M1 (AnyIO), M7 (Local-First), M11 (Soul Integrity),
M15 (Sovereign Continuity), M23 (Failure Integrity).

## Per-Mandate Operational Anchors

| Mandate | Operational Anchor |
|---------|-------------------|
| M1 AnyIO | No `import asyncio` in `src/omega/` (CI gate: `make check-m1-anyio`) |
| M2 Engine-Stack Firewall | Core is `src/omega/`, Stacks is `config/wads/`. No stack logic in Core. |
| M7 Local-First | `config/providers.yaml` strategy=`local_first`. Fabric order: native-gguf→lmster→Ollama→cloud. |
| M8 Zero Telemetry | No external analytics. Local observability in `data/` only. |
| M11 Soul Integrity | Every session → `proposed_lessons.yaml` write. |
| M13 Temple-Grade | `make temple-grade` exits 0 before any release. |
| M14 Heritage | Every `[id-soft:]` tag has a vet record with scope declaration. |
| M22 Response Provenance | `GenerateResult.provider_name` carries the ACTUAL provider, not dispatch intent. |
| M23 Failure Integrity | No soft-failures. Broken mandatory tools → `[TOOL-CHAIN-COLLAPSE]`. |
| M24 Venv Sovereignty | All Python inside `.venv/`. No `--break-system-packages`. |
| M26 Doc Standards | Reference docs pass `make doc-llm-validate`. |
| M27 Tracking Integrity | State follows 5-Tier Tracking Architecture. Validate via `scripts/validate_tracking_state.py`. |

## What This Means In Practice

- Before writing code: check if it would violate M1, M2, M7, M11, M13, M23.
- Before adding a new agent file: check M10 (fleet cap ≤14 without architectural review).
- Before committing: `make temple-grade` green; pre-commit hooks pass.
- When in doubt: ask Kali (Sprint Coordinator) or Verity (Compliance).

## Cross-references

- `SOVEREIGN_MANDATES.md` (full law)
- `MANDATES_CONDENSED.md` (one-line distillation)
- `Makefile` (gates: `check-m1-anyio`, `check-m7-local-first`, `check-m8-zero-telemetry`, `check-m9-error-integrity`, `check-m23-failure-integrity`, `temple-grade`)
- `.pre-commit-config.yaml` (CI-enforced gates)
