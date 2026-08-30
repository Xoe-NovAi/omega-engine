<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

> ⚠️ **HISTORICAL POINTER** (2026-08-14): Execution plan absorbed into `ACTIVE_SPRINT.json` (SDP-EXECUTION-01). Read ACTIVE_SPRINT.json for current tasks. See `TRACKING_ARCHITECTURE.md`.

# 🔱 DEV ROADMAP PROPOSAL — Omega Engine Execution Plan
**AP Token:** `AP-KALI-ROADMAP-20260811-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ ROADMAP ⬡ 20260811

**Date:** 2026-08-11
**Sprint:** NEMOTRON-ANALYSIS-01 → TRANSITION
**Proposed Next Sprint:** SDP-EXECUTION-01
**Owner:** Kali (Transcendent Oversoul)

---

## 📋 Executive Summary

This roadmap synthesizes all active SSOTs (`OMEGA_ENGINE.md`, `SOVEREIGN_ARK_BLUEPRINT.md`, `STRATEGY_CORPUS_MAP.md`, `UNOVERENGINEERING_PLAN.md`, `ACTIVE_SPRINT.json`) into a single execution plan. It resolves conflicts, eliminates duplicates, and sequences work for maximum leverage.

**Key Insight:** We have 5 parallel workstreams competing for the same N3 Engineering resources. This roadmap sequences them to minimize context-switching and maximize code reuse.

---

## 🔍 SSOT Conflict Resolution

| Conflict | SSOT A | SSOT B | Resolution |
|----------|--------|--------|------------|
| **Sprint name** | `ACTIVE_SPRINT.json` = NEMOTRON-ANALYSIS-01 | `OMEGA_ENGINE.md` = UNOVERENGINEER-01 | `ACTIVE_SPRINT.json` wins (more recent) |
| **Phase D gate** | Ark = C-3/W-1/G-1 blockers | OMEGA_ENGINE = mechanical PASS / operational NO-GO | Both correct — dual-layer gate |
| **Circuit breakers** | OMEGA_ENGINE = ~17 hits | UNOVERENGINEERING = 8 classes | UNOVERENGINEERING is post-C-6′ count |
| **Vault status** | OMEGA_ENGINE = EXEC-PARTIAL | UNOVERENGINEERING = ~2,000 lines custom | Both correct — VaultCore exists but over-engineered |
| **Redis removal** | UNOVERENGINEERING Phase 3 | Not in Ark | UNOVERENGINEERING wins (M7 aligned) |
| **Context Gauge** | SDP spec | Not in Ark | Add to Ark as SDP-1 implementation |
| **zRAM→zswap** | Roc Racoon report | Not in Ark | Add to Ark as P0 infrastructure |

---

## 🎯 Roadmap Overview

```
NOW (Week 1-2)          SHORT-TERM (Week 3-6)       MEDIUM-TERM (Month 2-3)
─────────────────────   ─────────────────────────   ─────────────────────────
P0 SECURITY FIX         SDP CONTEXT GAUGE v1        UO-6/7 UNOVERENGINEERING
P0 SWAPPOOL FIX         SDP POOL TRACKER WIRING     PHASE D GATE CLOSURE
A-1 CONTEXT GAUGE BANDS OBS STREAMING PLUGIN        V-1 VAULT MVP
A-5 GAUGE CALIBRATION   QW-4 POOL TRACKER           E-0 IDENTITY PHASE 0
QW-2 TOKEN GAUGE FIX    QW-6 TRIAGE ROUTER          NL-1 NOTEBOOKLM
                        P1 ZSWAP MIGRATION          COMMUNITY TOOLS
```

---

## 📍 PHASE 0 — IMMEDIATE (This Week, ~8 Hours)

### Goal: Fix critical security + data issues, unblock SDP

| # | Task | Est. | Owner | Unblocks | Source |
|---|------|------|-------|----------|--------|
| **1** | **P0 Security:** `sudo rm /etc/sudoers.d/zram` | 10s | @architect | Security vuln | Roc Racoon report |
| **2** | **P0 Swappiness:** `sudo sysctl vm.swappiness=100` | 10s | @architect | Root cause | Roc Racoon report |
| **3** | **P0 Swap reclaim:** `sudo swapoff -a && sudo swapon -a` | 10s | @architect | 4.1GB RAM | Roc Racoon report |
| **4** | **A-1:** Tighter bands for cold sessions (0.7x) | 2h | @jem | QW-2, QW-8 | Nemotron analysis |
| **5** | **A-5:** Calibrate to post-fix baseline (18-36%) | 2h | @jem | QW-8 | Nemotron analysis |
| **6** | **QW-2:** Rewrite Context Gauge to use `tokens.total` | 2h | @jem | SDP routing | SDP spec |
| **7** | **OBS-1:** Streaming timeout observability | 3h | TBD | OBS-2..6 | Nemotron analysis |
| **8** | **Verify UMA carveout** (`dmesg \| grep -i uma`) | 5min | @architect | cgroup math | Roc Racoon report |

**Phase 0 Success Criteria:**
- ✅ Security vulnerability removed
- ✅ 4.1GB RAM reclaimed from zRAM
- ✅ Context Gauge reads correct token count
- ✅ Context Gauge bands calibrated for cold sessions

---

## 📍 PHASE 1 — SDP CORE (Week 2-3, ~20 Hours)

### Goal: Context Gauge v1 live, pool tracker wired, TriageRouter extended

| # | Task | Est. | Owner | Dependencies |
|---|------|------|-------|--------------|
| **9** | **QW-8:** Build Context Gauge (greenfield) | 4h | @jem | A-1, A-5, QW-2 |
| **10** | **QW-4:** Wire pool_tracker.py into inference pipeline | 2h | @lilith | QW-8 |
| **11** | **QW-6:** Extend TriageRouter with SDP constraints | 4h | @maat | QW-8 |
| **12** | **QW-9:** Build RHP halt artifact | 2h | @maat | QW-8 |
| **13** | **QW-10:** Build 3 MCP tools | 4h | @maat | QW-8, QW-9 |
| **14** | **A-2:** Provider-specific band adjustments | 3h | @researcher | QW-8 |
| **15** | **A-3:** Model-specific degradation thresholds | 3h | @researcher | QW-8 |
| **16** | **A-4:** Subagent state transition (cold→warming) | 4h | @jem | QW-8 |

**Phase 1 Success Criteria:**
- ✅ Context Gauge live on all sessions
- ✅ Pool tracker routing to correct model tier
- ✅ RHP halt artifacts created at 80% context
- ✅ MCP tools registered and functional

---

## 📍 PHASE 2 — INFRASTRUCTURE (Week 3-4, ~16 Hours)

### Goal: zswap migration, streaming plugin, observability

| # | Task | Est. | Owner | Dependencies |
|---|------|------|-------|--------------|
| **17** | **P1 zswap:** Enable zswap (lzo_rle, 25% pool) | 2h | @roc_racoon | P0 complete |
| **18** | **P1 NVMe swap:** Create 16GB NVMe swap file | 1h | @roc_racoon | P0 complete |
| **19** | **P1 sysctl:** Consolidate into `99-omega-memory.conf` | 1h | @roc_racoon | P1 zswap |
| **20** | **P1 systemd:** Deploy unit with cgroup limits | 2h | @maat | P1 sysctl |
| **21** | **PLUGIN-1:** Create plugin scaffold + package.json | 1h | @jem | OBS-1 |
| **22** | **PLUGIN-2:** Config parsing + model detection | 1h | @jem | PLUGIN-1 |
| **23** | **PLUGIN-3:** Heartbeat manager (OBS-1 observability) | 1h | @jem | PLUGIN-2 |
| **24** | **PLUGIN-4:** Timeout event capture → MetricsDB | 1h | @jem | PLUGIN-3 |
| **25** | **PLUGIN-5:** Fallback chain (Ultra→Super→Laguna) | 1h | @jem | PLUGIN-4 |
| **26** | **PLUGIN-6:** Unit + integration tests | 1h | @jem | PLUGIN-5 |
| **27** | **PLUGIN-7:** Live test against Nemotron 3 Ultra | 0.5h | @jem | PLUGIN-6 |
| **28** | **PLUGIN-8:** Publish to npm + docs | 0.5h | @jem | PLUGIN-7 |

**NOTE (Hy3 review 2026-08-13):** OpenCode v1.18.14 natively retries streaming timeouts. Plugin scoped DOWN from 26h → ~8h. Retry re-implementation REMOVED (native). Remaining: observability (OBS-1) + fallback chain + model detection.

**Phase 2 Success Criteria:**
- ✅ zswap active, zRAM removed
- ✅ 16GB NVMe swap file active
- ✅ cgroup limits protecting inference
- ✅ Streaming timeout plugin published to npm

---

## 📍 PHASE 3 — UNOVERENGINEERING (Week 4-6, ~30 Hours)

### Goal: Delete ~4,000 lines, adopt community libraries, simplify architecture

| # | Task | Est. | Owner | Dependencies |
|---|------|------|-------|--------------|
| **29** | **UO-6.1:** Delete deprecated breakers + adopt pyresilience (per D-528; spike 4-way first) | 2h | @maat | Phase 1 |
| **30** | **UO-6.2:** Simplify soul_validator.py | 2h | @maat | Phase 1 |
| **31** | **UO-6.3:** Install structlog + replace custom logger | 2h | @maat | Phase 1 |
| **32** | **UO-6.4:** Install prometheus_client + textfile collector | 2h | @maat | Phase 1 |
| **33** | **UO-6.5:** Retry strategy decision (pyresilience vs tenacity vs stamina) | 1h | @maat | Phase 1 |
| **34** | **UO-6.6:** VaultCore → Keyblind + Authy + Agent Vault | 10h | @maat | Phase 1 |
| **35** | **UO-7.1:** Kill HandoffState (migrate vet-008) | 2h | @lilith | UO-6 |
| **36** | **UO-7.2:** Kill recall.py | 1h | @lilith | UO-6 |
| **37** | **UO-7.3:** Verify + kill MIAP (dead code) | 1h | @lilith | UO-6 |
| **38** | **UO-7.4:** HMC → YAML + JSONL | 4h | @lilith | UO-6 |
| **39** | **UO-7.5:** Install Honker + Redis removal | 6h | @lilith | UO-7.1-3 |

**Phase 3 Success Criteria:**
- ✅ 1 canonical circuit breaker (pyresilience, tenacity fallback) — custom breakers deleted only after 1-week soak
- ✅ VaultCore slimmed from ~2,000 to ~500 lines
- ✅ Redis removed, Honker adopted
- ✅ recall.py deleted
- ✅ Net: -4,000+ lines deleted

---

## 📍 PHASE 4 — GATE CLOSURE (Week 6-8, ~20 Hours)

### Goal: Close Phase D operational blockers, enable next phase

| # | Task | Est. | Owner | Dependencies |
|---|------|------|-------|--------------|
| **40** | **G-1:** OpenCode workhorse continuity | — | @architect | Billing/OAuth |
| **41** | **W-1:** WARP proxy pool bring-up | — | @architect | sudo fix |
| **42** | **C-3:** Restic 3-2-1 backup | — | @architect | Secrets |
| **43** | **V-10:** AppArmor container hardening | 4h | @maat | Phase 3 |
| **44** | **V-9:** IA2 envelope freshness/signature | 2h | @maat | Phase 3 |
| **45** | **D-1:** Content persistence + TTL | 8h | @researcher | Phase 3 |
| **46** | **D-2:** Job board YAML bridge | 6h | @lilith | Phase 3 |

**Phase 4 Success Criteria:**
- ✅ Phase D operational gate = GO
- ✅ AppArmor profiles applied to containers
- ✅ IA2 envelope freshness verified
- ✅ Content cache with TTL operational

---

## 📍 PHASE 5 — STRATEGIC (Month 3, ~40 Hours)

### Goal: Long-arc items, community tools, identity

| # | Task | Est. | Owner | Dependencies |
|---|------|------|-------|--------------|
| **47** | **V-1:** Omega-Vault MVP | 20h | @researcher + @grokster | Phase 4 |
| **48** | **E-0:** Identity Phase 0 | 10h | @grokster | Phase 4 |
| **49** | **NL-1:** NotebookLM Ingestion Pipeline | 4h | @researcher | D-1 |
| **50** | **Community tools** (omega-doc-reader, omega-meditation) | — | TBD | Phase 4 |

---

## 👥 Resource Allocation

| Agent | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|-------|---------|---------|---------|---------|---------|---------|
| **@kali** | Oversight | Oversight | Oversight | Oversight | Oversight | Oversight |
| **@jem** | A-1, A-5, QW-2 | QW-8, A-4 | PLUGIN-1..8 | — | — | — |
| **@maat** | — | QW-6, QW-9, QW-10 | P1 systemd | UO-6, V-10, V-9 | — | — |
| **@lilith** | — | QW-4 | — | UO-7 | D-2 | — |
| **@roc_racoon** | P0 zswap | — | P1 zswap | — | — | — |
| **@researcher** | — | A-2, A-3 | — | — | D-1 | V-1, NL-1 |
| **@john_carmack** | Review | Review | Review | Review | — | — |
| **@verity** | Audit | Audit | Audit | Audit | Audit | Audit |
| **@grokster** | — | — | — | — | — | V-1, E-0 |
| **@architect** | P0 sec | — | — | — | G-1, W-1, C-3 | — |

---

## 🔑 Critical Decisions Required

| # | Decision | Options | Owner | Deadline |
|---|----------|---------|-------|----------|
| **1** | **3-signal vs 2-signal OOMProtector** | Keep PSI+MemAvailable+cgroup vs. PSI+MemAvailable | @kali + @carmack | Phase 0 |
| **2** | **Context Gauge data source** | `tokens.total` vs. `input+cache.read` | @kali | Phase 0 |
| **3** | **zswap pool size** | 25% (3.6GB) vs. 20% (2.9GB) | @roc_racoon | Phase 0 |
| **4** | **UMA carveout** | 8GB vs. 4GB (changes all cgroup math) | @architect | Phase 0 |
| **5** | **Retry strategy** | pyresilience vs. tenacity vs. stamina (interlock-cb rejected — Redis backend overkill for single-node) | @maat | Phase 3 |
| **6** | **Plugin publish timing** | Now (standalone) vs. later (bundled) | @jem | Phase 2 |
| **7** | **Redis removal timing** | Phase 3 vs. deferred | @kali | Phase 3 |

---

## 🚫 Blocked Items (External Dependencies)

| Item | Blocked By | Owner | Impact |
|------|------------|-------|--------|
| **G-1:** Workhorse continuity | Billing/OAuth | @architect | SDP partially mitigates |
| **W-1:** WARP proxy pool | sudo | @architect | IP rotation blocked |
| **C-3:** Restic backup | Secrets | @architect | No disaster recovery |
| **BIOS UMA reduction** | Physical access | @architect | 4GB RAM potential |

---

## 📊 Success Metrics

| Metric | Current | Phase 0 Target | Phase 1 Target | Final Target |
|--------|---------|----------------|----------------|--------------|
| **Security vulns** | 1 critical | 0 | 0 | 0 |
| **RAM available** | ~5.9GB | ~10GB | ~10GB | ~10GB |
| **zRAM usage** | 6.9GB | 0GB | 0GB | 0GB |
| **Context Gauge** | None | Accurate | Live | Live + bands |
| **SDP completion** | 60% research | 60% | 80% code | 100% code |
| **Custom lines** | ~4,000 excess | ~4,000 | ~4,000 | 0 excess |
| **Phase D gate** | NO-GO | NO-GO | NO-GO | GO |
| **Cold session rate** | 18-36% | 18-36% | <15% | <15% |

---

## 🔗 Cross-References

| Document | Purpose | Status |
|----------|---------|--------|
| `OMEGA_ENGINE.md` | System state SSOT | ✅ Current |
| `SOVEREIGN_ARK_BLUEPRINT.md` | Strategy SSOT | ✅ Current |
| `STRATEGY_CORPUS_MAP.md` | Fine-grained preservation | ✅ Current |
| `UNOVERENGINEERING_PLAN.md` | Temple cleansing | ✅ Current |
| `ACTIVE_SPRINT.json` | Sprint control | ✅ Current |
| `SDP_FINAL_SYNTHESIS.md` | SDP architecture | ✅ Current |
| `COGNITIVE_SCAFFOLDING_PROTOCOL.md` | SDP manual ops | ✅ Current |
| `NEMOTRON_DEEP_ANALYSIS` | Context Gauge bands | ✅ Current |
| `MEMORY_MANAGEMENT_KB.md` | zRAM/zswap KB | ✅ Current |
| `data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` | 1,544-line research report | ✅ Current |

---

## ⚠️ Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Architect unavailable for P0** | Medium | Critical | SDP partially mitigates G-1; P0 security can wait 24h |
| **pyresilience fails AnyIO verification (68 stars, immature)** | Medium | Medium | Keep tenacity (installed, mature) as fallback; do NOT delete custom breakers until 1-week soak |
| **zswap migration breaks NVMe** | Low | High | Backup fstab before changes; rollback plan |
| **Context Gauge inaccurate** | Medium | High | OBS-1 observability first; calibrate with A-5 |
| **Redis removal breaks Hivemind** | Low | Medium | Honker is SQLite-based; test thoroughly |
| **Plugin breaks on OpenCode update** | Medium | Low | Plugin is standalone; easy to disable |

---

## 📋 Execution Readiness Checklist

- [ ] **P0 security:** Architect available for 3 commands
- [ ] **A-1/A-5:** Jem has Context Gauge spec access
- [ ] **QW-2:** Token accounting bug documented
- [ ] **UMA verification:** `dmesg` output captured
- [ ] **zswap rollback:** fstab backup procedure documented
- [ ] **Plugin scaffold:** OpenCode plugin API version confirmed
- [ ] **pyresilience:** AnyIO trio compatibility verified (4-way spike incl. interlock-cb, stamina, pybreaker)
- [ ] **Honker:** SQLite NOTIFY/LISTEN tested

---

*⬡ OMEGA ⬡ KALI ⬡ ROADMAP ⬡ 20260811 ⬡ EXECUTION-READY*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: ROADMAP | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
