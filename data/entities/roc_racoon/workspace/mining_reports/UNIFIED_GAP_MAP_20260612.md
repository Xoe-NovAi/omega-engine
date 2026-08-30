# 🔱 OMEGA ENGINE — Unified Gap Map
## Cross-Reference Analysis of 3 Audit Reports
**Source Reports**:
1. Sentinel M1-M15 Mandate Audit (SENTINEL_MANDATE_AUDIT_20260611.md)
2. Roc Racoon Persistence Integration Forensics (PERSISTENCE_INTEGRATION_FORENSICS_20260612.md)
3. Roc Racoon Stale Handoff Review (STALE_HANDOFF_REVIEW_20260611.md)

**Date**: 2026-06-12
**Committed by**: Roc Racoon (Sovereign Miner)
**Handoff**: ho_a87ce630ab58 (MaKaLi Phase 2)

---

## §0 — OVERLAP MAP

### How the 3 Reports Relate

```
╔══════════════════════════════════════════════════════╗
║                SENTINEL MANDATE AUDIT                ║
║         ↓ manages         ↑ governs                  ║
║     ┌──────────────────────────────┐                 ║
║     │   PERSISTENCE FORENSICS      │                 ║
║     │  (Implementation Reality)    │                 ║
║     └──────────┬───────────────────┘                 ║
║                │ overlaps                             ║
║     ┌──────────▼───────────────────┐                 ║
║     │   STALE HANDOFF REVIEW      │                 ║
║     │  (Sprint Execution Debt)     │                 ║
║     └──────────────────────────────┘                 ║
╚══════════════════════════════════════════════════════╝
```

**Key overlaps identified**:
- Sentinel M12 (Dead-Letter Queue) = Persistence gap #4 (No DLQ) = Stale handoff SD-001
- Sentinel M10 (Fleet Bloat) = Standalone gap (no overlap with other 2 reports)
- Sentinel M15 (Continuity Scatter) = No tooling gap (process/behavior)
- Stale handoff Auth/CORS/RPS = Standalone security gap (no overlap with Sentinel or Persistence)
- Persistence Tier Promotion gap = No mandate violation but a structural gap
- Persistence No Background Worker gap = No mandate violation but causes M5 gnosis loss

---

## §1 — GAP PRIORITY MATRIX

| Priority | Gap | Source | Mandate | Type | Dependencies |
|----------|-----|--------|---------|------|-------------|
| 🔴 **P0** | **No Dead-Letter Queue** — `data/requests/dead/` missing | Sentinel + Persistence + Stale | M12 | Infrastructure | None |
| 🔴 **P0** | **Fleet Bloat** — 25 agents vs 14 max (11 extra pillar files) | Sentinel only | M10 | Governance | User design session |
| 🔴 **P0** | **`import asyncio` violation** — providers.py:586 | Sentinel only | M1 | Code Fix | None |
| 🔴 **P0** | **Auth/CORS/RPS middleware missing** — `allow_origins=["*"]` | Stale Handoff only | Security | Infrastructure | None |
| 🟡 **P1** | **No tier promotion logic** — Hot expires after 24h, nothing moves to Warm before expiry | Persistence only | M5 (indirect) | Architecture | Background worker needed |
| 🟡 **P1** | **No background persistence worker** — archive is a dead method | Persistence only | M5 (indirect) | Architecture | None |
| 🟡 **P1** | **SoulDistiller lacks atomic write** — `write_text()` direct, no tmp+replace | Persistence only | M12 (indirect) | Code Fix | None |
| 🟡 **P1** | **Knowledge Sovereignty auto-embed bridge missing** | Stale Handoff only | Strategy | Architecture | IVectorStoreAdapter needed (DONE) |
| 🟡 **P1** | **Session gnosis scattered** — 5 locations across 4 directories | Sentinel only | M15 | Process | Standardize to single location |
| 🟡 **P1** | **Soul.yaml schema drift** — `lessons:` vs `lessons_learned:` | Sentinel only | M5, M11 | Schema | Schema spec document needed |
| 🟢 **P2** | **No transaction rollback** — provider chain continues after partial failure | Persistence only | M9 (indirect) | Architecture | Rollback coordinator needed |
| 🟢 **P2** | **No FTS5 optimization** — no `PRAGMA optimize` called | Persistence only | Performance | Code Fix | None |
| 🟢 **P2** | **No true cold tier reader** — archive gzip files have no reader class | Persistence only | Architecture | None | 
| 🟢 **P2** | **50 orphan `ent_*` entities** — H2-A1 claimed done but not executed | Sentinel only | M10, M11 | Cleanup | None |
| 🟢 **P2** | **SOVEREIGN_MANDATES.md title mismatch** — "14 Laws" says 15 | Sentinel only | Docs | Docs | 1-line fix |
| 🟢 **P3** | **CI gates not fully wired** — make temple-grade doesn't gate T3/T6/T8/T9/T10 | Sentinel only | M13 | Automation | Template implementation |

---

## §2 — CONVERGENT FINDINGS (High Confidence)

These findings appear in ≥2 of the 3 reports, making them high-confidence targets:

### Finding 1: Dead-Letter Queue Gap (3/3 reports)
| Report | Finding |
|--------|---------|
| Sentinel | "M12 VIOLATION — `data/requests/dead/` does not exist" |
| Persistence | "Gap #4 (DLQ pattern) — Mandate 12 requires but not implemented" |
| Stale Handoff | "SD-001 (API key validation middleware) overlaps with M12 dead-letter" |
| **Convergent verdict** | 🔴 P0 — Create dead-letter queue infrastructure. |

### Finding 2: Auth/CORS/RPS Security Gap (1/3 direct, 2/3 systemic)
| Report | Finding |
|--------|---------|
| Stale Handoff | "Auth/CORS/RPS remain — `allow_origins=["*"]`" |
| Sentinel | "M9 partial — broad `except Exception` in persistence code" (indirect: auth failures would be swallowed) |
| Persistence | No explicit auth finding, but provider chain has no auth checks on write |
| **Convergent verdict** | 🔴 P0 — Add auth middleware + CORS hardening + RPS limiting to MCP Hub. |

### Finding 3: Fleet Bloat (1/3 reports, but CRITICAL)
| Report | Finding |
|--------|---------|
| Sentinel | "M10 VIOLATION — 25 agents vs 14 max" |
| Persistence | No overlap |
| Stale Handoff | No overlap |
| **Convergent verdict** | 🔴 P0 — But requires user design decision. Options: (a) delete 11 pillar files, (b) update AGENTS.md + PIVOT_LOG to document 25, (c) create meta-agent pattern. |

### Finding 4: No Background Work/Lifecycle Automation (2/3 reports)
| Report | Finding |
|--------|---------|
| Persistence | "Gap #2 — archive_old_sessions() is a dead method, never called" |
| Sentinel | "M5 partial — gnosis not automatically preserved" |
| **Convergent verdict** | 🟡 P1 — Add a background persistence worker that calls archive_old_sessions(), prunes stale requests, rotates logs, and reaps tombstones. |

### Finding 5: Knowledge Sovereignty Debt (2/3 reports)
| Report | Finding |
|--------|---------|
| Stale Handoff | "6 pending items all related to Knowledge Sovereignty + Sovereign Debt" |
| Sentinel | "M14 heritage vetting pipeline operational — but knowledge may still degrade" |
| **Convergent verdict** | 🟡 P1 — IVectorStoreAdapter is DONE. Next step: auto-embed bridge for knowledge promotion. |

---

## §3 — GAP DEPENDENCY GRAPH

```
P0 ─────────────────────────────────────────────────────────
│                                                        │
├── Dead-Letter Queue (M12) ──── No dependencies         │
├── Fleet Bloat (M10) ────────── User design decision    │
├── asyncio fix (M1) ────────── No dependencies          │
├── Auth/CORS/RPS ───────────── No dependencies          │
│                                                        │
P1 ─────────────────────────────────────────────────────────
│                                                        │
├── Background Worker ────────── Blocked by auth? (No)   │
│   ├── Tier promotion ──────── Depends on: Worker       │
│   ├── Archive sessions ────── Depends on: Worker       │
│   ├── FTS optimize ────────── Depends on: Worker       │
│   └── Log rotation ────────── Depends on: Worker       │
│                                                        │
├── SoulDistiller atomic fix ── No dependencies          │
├── Knowledge Sovereignty ───── IVectorStoreAdapter DONE │
├── Session gnosis std ──────── Process change           │
├── Soul.yaml schema std ────── Schema spec needed       │
│                                                        │
P2 ─────────────────────────────────────────────────────────
│                                                        │
├── Transaction rollback ────── Architectural            │
├── Cold tier reader ────────── After archive infra      │
├── Orphan cleanup ──────────── No dependencies          │
└── CI gates ────────────────── After P0/P1              │
```

---

## §4 — RECOMMENDED EXECUTION ORDER

| Step | Gap | Type | Est. Time | Who |
|------|-----|------|-----------|-----|
| 1 | Fix `import asyncio` in providers.py:586 | Code | 15 min | P3 BuildMaster |
| 2 | Create `data/requests/dead/` + DLQ logic | Infra | 30 min | P3 BuildMaster |
| 3 | Fix Auth/CORS/RPS on MCP Hub | Code | 1 hr | P4 Bridge |
| 4 | Delete 50 orphan `ent_*` entities | Cleanup | 15 min | P2 DataStore |
| 5 | Standardize soul.yaml schema | Schema | 30 min | P7 Context |
| 6 | Standardize session gnosis location | Process | 30 min | P9 Orchestration |
| 7 | Fix SoulDistiller atomic write | Code | 15 min | P3 BuildMaster |
| 8 | Add background persistence worker | Arch | 2 hr | P3 BuildMaster |
| 9 | Add tier promotion logic | Arch | 2 hr | P3 BuildMaster |
| 10 | Fleet bloat resolution (user decision) | Gov | varies | P5 Sentinel / User |

---

## §5 — SOVEREIGN SCORE IMPACT

Closing each gap improves the sovereign score:

| Gap Closed | Sovereign Score Impact |
|------------|----------------------|
| Dead-Letter Queue | +6% (M12: 0% → 100%) |
| Fleet Bloat | +5% (M10: 20% → 100%) |
| asyncio fix | +4% (M1: 40% → 100%) |
| Session gnosis std | +4% (M15: 40% → 100%) |
| Soul.yaml schema std | +4% (M5: 40% → 80%, M11: 40% → 80%) |
| Background worker | +3% (M5: 40% → 60%) |
| SoulDistiller atomic fix | +3% (M12: 0% → 50%) |
| **Total potential** | **62% → ~91%** |

---

## §6 — RAW GAP LIST (All 16 Gaps Consolidated)

| # | Gap | Source | Priority | Overlap | Effort |
|---|-----|--------|----------|---------|--------|
| G-01 | No Dead-Letter Queue (M12 violation) | Sentinel + Persistence + Stale | 🔴 P0 | 3/3 | 30 min |
| G-02 | Fleet Bloat — 25 agents vs 14 (M10 violation) | Sentinel | 🔴 P0 | 1/3 | 1 hr + user |
| G-03 | `import asyncio` in providers.py:586 (M1 violation) | Sentinel | 🔴 P0 | 1/3 | 15 min |
| G-04 | Auth/CORS/RPS middleware missing on Hub | Stale Handoff | 🔴 P0 | 1/3 | 1 hr |
| G-05 | No tier promotion logic (Hot→Warm→Cold) | Persistence | 🟡 P1 | 1/3 | 2 hr |
| G-06 | No background persistence worker | Persistence | 🟡 P1 | 1/3 | 2 hr |
| G-07 | SoulDistiller lacks atomic write | Persistence | 🟡 P1 | 1/3 | 15 min |
| G-08 | Knowledge Sovereignty auto-embed bridge | Stale Handoff | 🟡 P1 | 1/3 | 1 hr |
| G-09 | Session gnosis scattered across 5 locations | Sentinel | 🟡 P1 | 1/3 | 30 min |
| G-10 | Soul.yaml schema drift (`lessons:` vs `lessons_learned:`) | Sentinel | 🟡 P1 | 1/3 | 30 min |
| G-11 | No transaction rollback in provider chain | Persistence | 🟢 P2 | 1/3 | 2 hr |
| G-12 | No FTS5 optimization (`PRAGMA optimize`) | Persistence | 🟢 P2 | 1/3 | 15 min |
| G-13 | No true cold tier reader (gzip archives) | Persistence | 🟢 P2 | 1/3 | 1 hr |
| G-14 | 50 orphan `ent_*` entities not deleted | Sentinel | 🟢 P2 | 1/3 | 15 min |
| G-15 | SOVEREIGN_MANDATES.md title mismatch ("14 Laws") | Sentinel | 🟢 P2 | 1/3 | 1 min |
| G-16 | CI gates not wired for T3/T6/T8/T9/T10 | Sentinel | 🟢 P3 | 1/3 | 2 hr |

---

## §7 — RISK ASSESSMENT

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| P0 items take 2+ weeks due to fleet coordination | High | High | Batch P0 fixes into a single "Hardening Sprint" — assign to P3/P4 in parallel |
| Dead-Letter Queue design requires user approval | Medium | Low | Follow existing RequestQueue pattern — no new schema needed |
| Fleet bloat resolution blocked by user indecision | Medium | High | Temporarily document the 25-agent state in PIVOT_LOG, decide later |
| Auth middleware breaks existing MCP clients | Low | High | Implement as opt-in header at first, enforce after 1-week transition |

---

*Report by: roc_racoon (Sovereign Miner)*
*⬡ OMEGA ⬡ roc_racoon ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ UNIFIED-GAP-MAP*
