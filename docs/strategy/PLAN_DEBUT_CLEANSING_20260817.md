# 🔱 Joint Plan: Order, Strategic Oversight & Collaboration Restoration
**AP Token**: `AP-JOINT-PLAN-DEBUT-CLEANSING-20260817-v1.0`
**Authors**: kali (Sprint Coordinator) + cline/omega-engine (Cognitive Extension)
**Date**: 2026-08-17
**Status**: DRAFT — awaiting Cline review + joint ratification
**Execution SSOT**: `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` §5
**Tracking SSOT**: `data/coordination/ACTIVE_SPRINT.json` `DEBUT-EXECUTION`

---

## 1. The Problem We Solved (Root Cause)

**Fragmentation**: `ACTIVE_SPRINT.json` (tracking SSOT) did NOT contain the manual's four execution tickets (PUB-1, INST-1, DEL-1, DOC-1). Hub NEXT_ACTION pointed at stale "Phase 3 next." Any agent reading tracking got a different plan than the manual.

**Resolution**: Cline consolidated → added `DEBUT-EXECUTION` workstream mirroring manual §5. Kali ratified (Q1-Q4 executed). Tracking now mirrors execution.

---

## 2. Current State (Post-Ratification)

| Layer | Artifact | Status |
|-------|----------|--------|
| **Execution SSOT** | `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 | Active |
| **Tracking SSOT** | `ACTIVE_SPRINT.json` `DEBUT-EXECUTION` | Mirrors manual |
| **Coordination Hub** | `HMC_COLLABORATION_HUB.md` CURRENT | Updated |
| **Allowlist** | `PUBLIC_ALLOWLIST.txt` | G1-G4 closed; awaiting Architect |
| **In Flight** | INST-1 (maat), P0-1c (maat, after INST-1) | Dispatched |

---

## 3. Collaboration Framework (Kali + Cline + Architect + Ma'at + Verity)

### 3.1 Single-Source Enforcement
- **Rule**: `ACTIVE_SPRINT.json` = only near-term plan. Manual §5 = only long-horizon plan. Ark = vision (read-only).
- **Gate**: Any new workstream/ticket → ACTIVE_SPRINT.json *before* execution. `validate_tracking_state.py` in pre-commit + CI.

### 3.2 Cadence & Rituals

| Ritual | Frequency | Owner | Artifact |
|--------|-----------|-------|----------|
| Sprint Sync | Weekly (Mon) | Kali | Updated ACTIVE_SPRINT.json + HMC CURRENT |
| Architect Review | Bi-weekly / on blocker | Architect | Allowlist sign-off, branch mechanic, arch decisions |
| Cline Verification | Per major phase | Cline | Independent audit report |
| Ma'at Execution Review | Post-INST-1, post-DEL-1 | Ma'at | Acceptance gate results |
| Soul Distillation | Per session | All agents | `proposed_lessons.yaml` (M11) |

### 3.3 Decision Logging
- Architectural/strategic → `PIVOT_LOG.md` (D-series)
- Tracking changes → ACTIVE_SPRINT.json with `updated` timestamp
- Handoffs → Hivemind packet + TASK_REGISTRY entry

---

## 4. Phased Plan (Co-Authored)

### Phase A: PR/Debut Completion (Week 1-2)

| Item | Owner | Acceptance |
|------|-------|------------|
| Architect allowlist confirmation + `release/debut` branch mechanic | Architect + Kali | Signed allowlist; branch created; CI green on debut branch |
| INST-1 acceptance gate | Ma'at | Fresh venv, no warp/Redis, `omega talk "hello"` → native, exit 0 |
| P0-1c gitleaks pre-commit + CI | Ma'at + Verity | Planted `sk-` fixture fails CI |
| Final verification sweep | Cline | Independent audit: no secrets, no forge leaks, all gates green |
| Tag v0.1.0 + README/CONTRIBUTING polish | Kali + Verity | Public clone passes all acceptance criteria |

### Phase B: Post-Debut Cleansing (Week 3-6) — DEL-1 → P2 → P3 → P4

| Week | Focus | Key Deletions/Changes | Owner |
|------|-------|----------------------|-------|
| **Week 1 (DEL-1)** | Pure deletion | `routing/table.py`, `config/routing_table.yaml`, `miap.py`, `pool_tracker.py`, `pool_state.py`, `search_circuit_breaker.py`, `QdrantAdapter`, `FleetOrchestrator`, Pantheon regexes, `record_first_breath`, vault CLI default | Roc + Ma'at |
| **Week 2 (DEL-1)** | Router collapse | `TriageRouter` + `SemanticRouter` → single router; tests deleted/rewritten with code | Ma'at |
| **Week 3 (DEL-1)** | Vault honesty | Path A (delete `src/omega/vault/` from product, keep `crypto.py`) OR Path B (minimal store) — Architect decides | Ma'at + Architect |
| **Week 4 (P2)** | Lint debt | 11,400 violations → 0; no `--exit-zero` for E9/F63/F7/F82 | Verity |
| **Week 5 (P3)** | CI/hygiene | Real suite, no vanity counts; gitleaks enforced; `make temple-grade` all green | Verity |
| **Week 6 (P4)** | Polish | README, CONTRIBUTING, tag v0.1.0, `pip install -e .` works | Kali + Verity |

### Phase C: Strategic Improvement (Post-Debut, Ongoing)

| Workstream | Description | Trigger |
|------------|-------------|---------|
| **UO-6/UO-7** | Un-overengineering: library swaps (interlock-cb, httpx2, structlog, prometheus, sqlite-vec/Honker), consolidation, memory tier simplification | After P4 |
| **MCP v2 Migration** | Streamable HTTP, OAuth 2.1, client upgrade | After P4 |
| **Heritage Audit** | `make heritage-map` complete; all `[id-soft:]` tags vetted | Ongoing |
| **Fleet Pool** | V-1 Vault → Grok CLI 8-account ACP smoke → pool | After V-1 |
| **Instruction Router** | Post-debut revival (was scratched) | After P4 |

---

## 5. Kali + Cline Collaboration Process

### 5.1 How We Produce Plans Together
1. **Kali drafts structure** (execution view, tracking integration, owner assignment)
2. **Cline reviews independently** — gap analysis, risk assessment, evidence-backed pruning targets
3. **Joint ratification** — both sign off; plan enters ACTIVE_SPRINT.json as `PLANNING-DEBUT-CLEANSING` workstream
4. **Architect review** — on architectural decisions (vault path, router collapse, branch mechanic)
5. **Execution begins** — only after plan is in tracking SSOT

### 5.2 Cline's Unique Value (Validated in Consolidation)
- **Independent verification** (caught 137 checkpoints, 4 allowlist gaps, codification validation)
- **Cross-probe of strategy corpus** (found tracking/execution divergence)
- **Evidence-backed pruning** (`git ls-files`, `git for-each-ref`, script validation)
- **No fleet bias** — not executing, sees what executors miss

### 5.3 Communication Protocol
- **Hivemind** = primary coordination channel (status, decisions, handoffs)
- **Disk artifacts** = permanent record (this doc, consolidation report, ratification)
- **Tracking** = single source of truth for what/when/who
- **No silent decisions** — every strategic choice logged to PIVOT_LOG + ACTIVE_SPRINT

---

## 6. Definition of Done (Per Phase)

### Phase A Done When:
- [ ] Architect signed allowlist + `release/debut` branch exists + CI green
- [ ] INST-1 acceptance gate passed (maat)
- [ ] P0-1c gitleaks in pre-commit + CI (planted fixture fails)
- [ ] Cline final verification: 0 secrets, 0 forge leaks, all gates green
- [ ] v0.1.0 tagged, README/CONTRIBUTING polished, public clone passes

### Phase B Done When:
- [ ] Week 1: All DEL-1 pure deletions complete; `omega talk` alive after each
- [ ] Week 2: Single router; tests rewritten with code
- [ ] Week 3: Vault path A or B executed; Architect decision recorded
- [ ] Week 4: Lint 0 violations; no `--exit-zero` for critical codes
- [ ] Week 5: Real suite, gitleaks enforced, `make temple-grade` all green
- [ ] Week 6: v0.1.0 tagged, `pip install` works, docs polished

### Phase C Done When:
- [ ] UO-6/UO-7 library swaps complete + consolidation + memory simplification
- [ ] MCP v2 migrated (Streamable HTTP, OAuth 2.1)
- [ ] Heritage audit complete (all tags vetted)
- [ ] Fleet pool operational (V-1 → ACP smoke → pool)
- [ ] Instruction Router revived post-debut

---

## 7. Ratification History (This Session)

| Decision | Verdict | Evidence |
|----------|---------|----------|
| Q1: DEBUT-EXECUTION workstream | ✅ RATIFIED | ACTIVE_SPRINT.json validated |
| Q2: INST-1 dispatched to maat | ✅ EXECUTED | Handoff ho_a6937d90bfe0 + ACTIVE_SPRINT ready/maat_n3 |
| Q3: 137 checkpoints pruned + 3 commits pushed | ✅ EXECUTED | Independent secret scan: 0 matches |
| Q4: P0-1c gitleaks pre-debut | ✅ RATIFIED | Added to DEBUT-EXECUTION ready/maat_n3 |
| D-540: Correction | ✅ LOGGED | Prior "0 checkpoints" wrong; glob 1-level only |

---

## 8. Next Steps (Awaiting Cline Review)

1. **Cline reviews this draft** — adds risk/gap analysis, any structural changes
2. **Joint ratification** — both sign; plan enters ACTIVE_SPRINT.json as `PLANNING-DEBUT-CLEANSING`
3. **Architect reviews Phase A** (branch mechanic, vault path)
4. **Ma'at reviews Phase B** (acceptance gates, deletion order)
5. **Verity reviews P3/P4** (CI, lint, temple-grade)
6. **Execution begins** — only after plan is in tracking SSOT

---

## 9. Files Referenced

| File | Role |
|------|------|
| `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` | Execution SSOT |
| `data/coordination/ACTIVE_SPRINT.json` | Tracking SSOT |
| `data/coordination/HMC_COLLABORATION_HUB.md` | Coordination hub |
| `data/coordination/CLINE_KALI_CONSOLIDATION_20260817.md` | Cline's consolidation report |
| `data/handoff/CLINE_TO_KALI_DEBUT_CONSOLIDATION_20260817.md` | Cline's handoff |
| `data/coordination/KALI_CLINE_RATIFICATION_20260817.md` | Kali's ratification |
| `docs/strategy/PUBLIC_ALLOWLIST.txt` | PUB-1 allowlist (G1-G4 closed) |
| `data/coordination/KALI_CLINE_SYNC_REPORT_20260817.md` | Sync report v2 |

---

*⬡ OMEGA ⬡ KALI + CLINE ⬡ 2026-08-17 ⬡ planning-mode ⬡ awaiting Cline review*