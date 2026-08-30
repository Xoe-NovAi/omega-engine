# W3 Soul Report — Evidence-Field Schema + Kali Promotion (W1-3)
**Agent**: maat · **Date**: 2026-08-24 · **Sprint**: WAVE-1-DOCTRINE-WIRING
**Ruling basis**: S5/F2 (explicit evidence field day one, warn-only) · Gemini trap-catch #2 (schema BEFORE promotion)

## Research findings
- Surfaces: `proposed_lessons.yaml` = tainted staging (never identity-injected); `approved_lessons.yaml` (entity root) = Vetted-Wisdom surface injected by `entity_workspace.py:408-472` (renders `l.get('lesson', l)`); `soul.yaml` lessons_learned = slug list.
- Single production write path: `SoulStore.write_atomic` (C-1′, 4-layer guarantee). Reused exclusively — structural-debt gate #1 honored.
- `CorePrinciple` already carried an optional `evidence` field (soul_validator.py:222) — the lessons schema now matches that precedent.
- kali staging held exactly 20 proposals: 4 unnamed L1/L2/L3 triplets, 1 combined meditation entry (KALI-INTEGRATION-004), AO-P1..P7.
- M11 auditor safety: requires ≥1 entity with `- id:` staging entries; grokster retains 8 → emptying kali staging stays green.

## What was built
| Component | Path | Notes |
|---|---|---|
| Schema patch | `src/omega/soul/lessons.py` | EvidenceRef (session_id/artifact/quote, ≥1 required, extra=forbid); Lesson (extra=allow, backward compat); validate_lessons() warn-only |
| Promotion script | `scripts/promote_soul_lessons.py` | Pre-flight probe binding → SoulStore-only writes → read-back verification; --dry-run; idempotent no-op when staging empty |
| Tests | `tests/contract/test_soul_lessons.py` | 14 tests: schema units, SoulStore round-trip + .bak recovery, M21 contract on REAL promoted surface |

## Promotion results
- **Promoted**: 20/20 kali proposals → `data/entities/kali/approved_lessons.yaml`
- **Evidence coverage**: 20/20 (100%) — every lesson carries ≥1 structured ref
- **Quote coverage**: 7/20 (reported separately; artifact-path refs satisfy O-Q4 existence+path grade)
- **Staging**: emptied atomically in same run; metadata.last_promotion stamped
- Every evidence artifact path disk-verified pre-write (one abort caught a wrong path: actual file is `VAULT_SYSTEM_OVERHAUL_MASTER_INDEX_20260818.md`)

## Corrections caught before commit
1. Vault master-index path fixed via pre-flight abort — and re-caught after a session-boundary revert silently restored the old string (probe binding in executed path, not narrative)
2. Round-trip test premise corrected: SoulStore .bak recovery triggers on UNREADABLE files, not YAML-invalid content

## Test results
- New suite: 14 PASS (3 promotion-dependent skips pre-execution → all pass post-execution)
- Combined with W1-2 suite: 33/33 green

## Unresolved gaps
- `soul_stage.py` TUI still mock-wired (pre-existing)
- Quote coverage 7/20 — deeper extraction deferred per O-Q4 grade
- Other entities' staged lessons ([TS1] corpus etc.) not promoted this sprint — kali was the mission scope
