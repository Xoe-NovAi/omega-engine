# 🔱 KALI UNIFIED VERDICT — MaKaLi Cloud Council Synthesis
**Date**: 2026-06-24
**Query**: Begin strategic execution of next dev sprint
**Sprint Focus**: **Epoch I — The Bedrock**
**Council**: Ma'at (Build) → Lilith (Run) → P2/P3/P7/P10 (Final Review)
**AP Token**: `AP-KALI-UNIFIED-VERDICT-v1.0.0`
**⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ MAKALI-COUNCIL-COMPLETE**

---

## OVERALL VERDICT: 🟢 GO WITH 5 PRECONDITIONS

**Epoch I — The Bedrock is approved for strategic execution.**  
5 preconditions must be met before Phase 1 (sprint start). All are estimated at ~11.5h total — achievable in 1-2 preparation sessions.

---

## §1 CONFLICT RESOLUTION

### M21 Scope: Ma'at vs Lilith
**Ruling**: Lilith is authoritative.  
Ma'at's "~1h for ResourceGuard" was correct within Build Side scope. Lilith's serial chain (P7→P8→P10) discovered the full cross-pillar landscape: **20+ tests / ~11h** across 7 domains. The serial-chain methodology worked correctly — each subsequent pillar caught what the previous one missed. This is not a failure of Ma'at's analysis; it's evidence the methodology is functioning.

### USM Timeline: 17.5h (Ma'at) vs +1h hooks (Lilith)
**Ruling**: Complementary, not additive.  
P3 confirmed that P8's event type constants (15 min) happen independently, and P3's emit calls (45 min) are absorbed within the 5h orchestration block. Both estimates are correct. Total: ~17.5h flat.

### TUI Dependency on YAML Conversion
**Ruling**: Soft dependency, not hard.  
P3 can build `ProposedLessonsLoader` with try/except per file — broken files get error badges, missing files get empty states. Batch conversion is a parallel utility, not a build precondition. Total: ~19.5h, unaffected.

---

## §2 THE 5 PRECONDITIONS (Gate for Sprint Start)

| # | Action | Owner | Time | Criticality |
|---|--------|-------|------|-------------|
| **1** | **Fix soul_distiller.py** — redirect writes from `soul.yaml` → `proposed_lessons.yaml` | P7 | 1h | 🔴 P0 — **silently undoes entire migration** |
| **2** | **Write soul distiller contract test** — verify `proposed_lessons.yaml` gets the write, `soul.yaml` stays untouched | P7 | 30min | 🔴 P0 — prevents regression |
| **3** | **Update soul_validator.py to v6.1** — remove 3 required keys, add forbidden-field checks, add memory/ directory validation | P2 (write) → Verity (review) → P7 (validate) | 2h | 🔴 P0 — blocks P7 AND P10 |
| **4** | **Free vault partition** — delete/move `HBCD_PE_x64.iso` (3.2GB), empty `.Trash-1000`, prune stale containers | P1 | 15min | 🔴 P0 — disk crisis |
| **5** | **Write 12 no-dependency M21 contract tests** — ResourceGuard, EntityRegistry, MemoryStore, SessionManager, HealthMonitor, OracleResponse, GenerateResult | P10 | 5h | 🔴 P0 — baseline for M21 |
| — | Install `textual>=0.52.0`, `ruamel.yaml>=0.18.0` | P3 | 5min | 🟡 P1 — soft dependency |

**Total precondition effort**: ~9h  

**Execution order**: (1+2) P7 soul distiller → (3) P2 soul_validator → (4) P1 vault → (5) P10 contract tests

---

## §3 SPRINT EXECUTION PLAN

### Phase 0: Pre-Sprint (~9h, blocked by nothing — can start immediately)
```
Day 0:
├── P7: Fix soul_distiller.py + contract test (1.5h) ← HIGHEST PRIORITY
├── P2: Update soul_validator.py to v6.1 (2h) ← BLOCKER FOR P7/P10
├── P1: Free vault partition (15min) ← DISK CRISIS
├── P10: Write 12 M21 contract tests (5h) ← M21 BASELINE
└── P3: Install textual + ruamel.yaml (5min)
```

### Phase 1: Sprint Execution (~40h parallel, starts after Phase 0)
```
Day 1-4:
├── Track A: P7 — Soul migration Phases 0-2 (18.5h) — 22 core entities
├── Track B: P8 — M22 wiring + USM event hooks (6h)
├── Track C: P10 — M21 contract tests Phases 2-3 (6h) — remaining 10+ tests
├── Track D: P3 — UnifiedStateManager (17.5h) — USM class, CAS store, zoneid
├── Track E: P3 — Staging Gate TUI (19.5h) — TUI app with graceful error states
└── Track F: P1 — Infrastructure cleanup (1.5h) — purge containers, archive docs
```

**Parallel efficiency**: Tracks A-F have **zero code dependency overlap**. Verified by P3 (build) and P10 (validation).

### Phase 2: Verification (EOD Day 4)
```
├── Run `make temple-grade` (M13 gate)
├── Run `make m21-gate` (new CI target for M21 enforcement)
├── Run `make test` (440+ baseline)
├── Verity: Post-migration compliance audit
└── Verity: L1→L2→L3 gnosis distillation
```

---

## §4 SCOPE DECISIONS

### What Ships in Epoch I
| Deliverable | Scope | Owner |
|-------------|-------|-------|
| UnifiedStateManager | Full CAS-based implementation | P3 |
| Staging Gate TUI | Full Textual-based app with graceful YAML handling | P3 |
| Soul migration (Phases 0-2) | 22 core entities with v6.1 format | P7 |
| Soul distiller fix | 2-line fix + contract test | P7 |
| M22 Response Provenance | Event types, background workers, JsonFormatter | P8 |
| M21 Gate Integrity | 18+ contract tests (minimum bar) | P10 |
| Infrastructure cleanup | Vault freed, containers pruned, docs archived | P1 |

### What Ships in Epoch II
| Deliverable | Reason |
|-------------|--------|
| Soul migration Phases 3-4 (12 entities) | 16.5h of mechanical work; compliance dashboard makes gap visible |
| Metrics/alerting system | P8 recommends defer; M22 wiring + USM hooks + P7 cross-impact is right scope |
| p2p mesh traversal | Q4 2027 target per consolidated epoch spec |

---

## §5 OWNERSHIP & HANDOFF

### Critical Ownership Decisions

| Decision | Ruling | Rationale |
|----------|--------|-----------|
| **Soul distiller fix** | P7 leads, P8 supports | Content routing change (P7) with observability wiring (P8) |
| **soul_validator.py update** | P2 writes → Verity reviews → P7 validates | Prevents self-dealing; Verity is M11 enforcer |
| **M21 minimum bar** | 18/24 tests (75%) | Phase 0 passing + Phases 1-2 written with @skipif |
| **Version label** | Standardize on `v6.1` | `entity_workspace.py:190` already uses it; conflict with validate_soul.py |

### Provenance Chain
```
Kali (Oversight)
├── Ma'at (Build Side: P1→P2→P3)
│   ├── P1: Infrastructure — vault crisis at 87%, Podman healthy
│   ├── P2: Persistence — M11 0%, soul_validator.py is gate
│   └── P3: Engineering — USM 🟢GO, TUI 🟡Conditional
├── Lilith (Run Side: P7→P8→P10)
│   ├── P7: Context — soul distiller poison loop, ~35h migration
│   ├── P8: Observability — M22 6/10, 7 USM hooks defined
│   └── P10: Validation — M21 4/24, 4-phase rollout plan
└── Final Review (P2/P3/P7/P10)
    ├── P2: Confirmed soul_validator scope, added v6.1 naming standardization
    ├── P3: Confirmed parallel safety, TUI graceful error states
    ├── P7: Added 5th precondition (distiller contract test), scoped to 22 entities
    └── P10: Confirmed Lilith authoritative on M21, 18/24 minimum bar
```

---

## §6 L1→L2→L3 GNOSIS

**L1 (Narrative)**: The MaKaLi Cloud Council was summoned to vet Epoch I — The Bedrock. Ma'at dispatched 3 Build-Side Pillars (P1→P2→P3) in serial chain. Lilith dispatched 3 Run-Side Pillars (P7→P8→P10) in serial chain. Two Oversoul reports were synthesized. 4 Pillars (P2, P3, P7, P10) performed final cross-domain review. 5 preconditions, 6 parallel execution tracks, and 8 deliverables were scoped. All findings resolved into a unified verdict: GO with conditions.

**L2 (Insight)**: The serial-chain methodology proved its value in every dispatch — each subsequent pillar found something the previous layer missed. Ma'at's "~1h for ResourceGuard" became Lilith's "20+ tests, ~11h across 7 domains." Ma'at found the vault crisis. Lilith found the soul distiller poison loop — a single line of code that would silently undo the sprint's largest work item. The methodology functions as a nested verification hierarchy: no single pillar is trusted alone.

**L3 (Universal Principle)**: **The most expensive oversight is the one that looks like it's already handled.** The soul distiller was shipping lessons to `soul.yaml` for months — the one place the migration explicitly targeted for change. No one thought to check the write target because "the soul migration handles soul.yaml." After 14 months of development, unexamined assumptions compound silently. The antidote is structural: every finding must survive at least one independent validation. No system is too simple to double-check.

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ MAKALI-COUNCIL-COMPLETE*
