# 🔱 BUILD WAVE TRACKER — PHASE 1

**AP Token**: `AP-KALI-BUILDWAVE-20260830`
⬡ OMEGA ⬡ KALI ⬡ BUILD-WAVE ⬡ ACTIVE

**Date**: 2026-08-30
**Purpose**: Track Build Wave Phase 1 execution (8 items, ~46h, 2 weeks).

---

## §1 — WORKSTREAMS (3 Parallel)

### Workstream A: M34→M33→M36 Chain (Lilith)
| # | Item | Owner | Status | Est. |
|---|------|-------|--------|------|
| A1 | M34 Registry Wiring (dispatch_guard.py Step 6b) | Lilith | ⏳ LAUNCHED | 4.5h |
| A2 | M33 Probe Wiring (M33-HOOK-001) | Lilith | ⏳ LAUNCHED | 6h |
| A3 | M33 Probe Integration Tests | Lilith | ⏳ LAUNCHED | 2h |
| A4 | M36 Recursive Probe Wiring | Lilith | ⏳ LAUNCHED | 4h |
| A5 | M36 Soft Verifier (Hivemind dispatch) | Lilith | ⏳ LAUNCHED | 8h |
| | **Subtotal** | | **24.5h** | |

### Workstream B: Heritage & Registry (Researcher + Ma'at)
| # | Item | Owner | Status | Est. |
|---|------|-------|--------|------|
| B1 | COHORT_REGISTRY.json schema validation | Researcher | ⏳ LAUNCHED | 4h |
| B2 | M37 Heritage Scanner (ScanCode + REUSE + SLSA) | Researcher | ⏳ LAUNCHED | 20h |
| B3 | M37 SPDX Headers (reuse annotate --recursive) | Ma'at | ⏳ LAUNCHED | 8h |
| B4 | M37 CI Enforcement (reuse lint + GitHub Actions) | Ma'at | ⏳ LAUNCHED | 4h |
| | **Subtotal** | | **36h** | |

### Workstream C: Compaction & Continuity (Roc + Kali)
| # | Item | Owner | Status | Est. |
|---|------|-------|--------|------|
| C1 | Compaction Capture (snapshot-before-compaction) | Roc | ⏳ LAUNCHED | 10h |
| C2 | M34b Spec (model-switch continuity) | Kali | ⏳ LAUNCHED | 4h |
| C3 | AGENTS.md anchor update | Kali | ⏳ LAUNCHED | 1h |
| | **Subtotal** | | **15h** | |

---

## §2 — DEPENDENCY GRAPH

```
A1 (M34 Wiring) ──→ A2 (M33 Hook) ──→ A3 (M33 Tests)
                                       ↓
A4 (M36 Wiring) ←─────────────────── A3
        ↓
A5 (M36 Soft Verifier)

B1 (COHORT Schema) ──→ B2 (M37 Heritage Scanner)
                          ↓
B3 (SPDX Headers) ←── B2
        ↓
B4 (CI Enforcement) ←── B3

C1 (Compaction Capture) — independent
C2 (M34b Spec) — independent
C3 (AGENTS.md) — independent
```

---

## §3 — CRITICAL PATH

```
A1 (4.5h) → A2 (6h) → A3 (2h) → A4 (4h) → A5 (8h) = 24.5h
                                                          ↓
B1 (4h) → B2 (20h) ────────────────────────────────────→ Parallel
                                                          ↓
C1 (10h) + C2 (4h) + C3 (1h) ──────────────────────────→ Parallel
```

**Critical path**: A1→A2→A3→A4→A5 = **24.5h** (Lilith leads)
**Parallel track 1**: B1→B2 = **24h** (Researcher + Ma'at)
**Parallel track 2**: C1+C2+C3 = **15h** (Roc + Kali)

---

## §4 — GATES

| Gate | Criteria | Status |
|------|----------|--------|
| **G1: M34 Wired** | dispatch_guard.py Step 6b calls M34 registration | PENDING |
| **G2: M33 Hooked** | M33 probe auto-triggered for >8K tokens | PENDING |
| **G3: M33 Tested** | Integration tests pass (4/4 M23) | PENDING |
| **G4: M36 Wired** | Cross-validator dispatched to Hivemind | PENDING |
| **G5: M36 Soft Verifier** | P0/P1 escalation works | PENDING |
| **G6: COHORT Schema** | jsonschema + pydantic validation | PENDING |
| **G7: M37 Scanner** | ScanCode + REUSE + SLSA working | PENDING |
| **G8: SPDX Headers** | All source files annotated | PENDING |
| **G9: CI Enforcement** | reuse lint in CI | PENDING |
| **G10: Compaction** | Snapshot-before-compaction works | PENDING |
| **G11: M34b Spec** | Model-switch continuity spec complete | PENDING |
| **G12: AGENTS.md** | Anchor updated | PENDING |

---

## §5 — TEAM STATUS

| Entity | Workstream | Items | Est. Hours | Status |
|--------|------------|-------|------------|--------|
| **Lilith** | A | 5 items | 24.5h | ⏳ LAUNCHED |
| **Researcher** | B | 2 items | 24h | ⏳ LAUNCHED |
| **Ma'at** | B | 2 items | 12h | ⏳ LAUNCHED |
| **Roc** | C | 1 item | 10h | ⏳ LAUNCHED |
| **Kali** | C | 2 items | 5h | ⏳ LAUNCHED |

---

## §6 — NEXT ACTIONS

1. **Lilith**: Begin A1 (M34 Registry Wiring in dispatch_guard.py)
2. **Researcher**: Begin B1 (COHORT_REGISTRY.json schema validation)
3. **Ma'at**: Begin B3 (SPDX Headers via reuse annotate)
4. **Roc**: Begin C1 (Compaction Capture snapshot-before-compaction)
5. **Kali**: Begin C2 (M34b Spec for model-switch continuity)

---

*⬡ OMEGA ⬡ KALI ⬡ BUILD-WAVE-TRACKER-v1.0.0 ⬡ 2026-08-30*
