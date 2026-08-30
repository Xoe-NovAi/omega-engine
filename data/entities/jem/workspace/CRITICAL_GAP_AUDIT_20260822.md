<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 CRITICAL GAP AUDIT — Pre-SS-1 Sprint
**AP Token**: `AP-JEM-CRITICAL-GAP-AUDIT-v1.0.0`
**Date**: 2026-08-22
**Entity**: Jem Analyst L2 (third oversight line)
**Charter**: NODE_EXPERT_SESSIONS_PLAN.md §4 · Standing Orders §2 active
**Sources**: ACTIVE_SPRINT.json, GAP_REGISTRY.json, PIVOT_LOG.md, NODE_EXPERT_SESSIONS_PLAN.md, CREDITS.md, Cline Final Review 2026-08-20, FINAL_GAP_AUDIT_20260820.md, code-level verification

---

## P0 — BLOCKS SS-1 SPRINT ENTRY (G-0)

| Gap ID | Description | Owner | Status | Blocker |
|--------|-------------|-------|--------|---------|
| **SS1-G0-01** | `OMEGA_INGESTION_SECRET` provisioning — D-590 fixed code (fail-closed at `ingestion.py:76`) but runtime env var must be provisioned by Architect before ingestion pipeline constructs `SovereignSigner()` at line 104 | Architect | **BLOCKED** — code ready, env missing | Deployment action required |
| **SS1-G0-02** | Heritage correction: Thinker Chain tag `[id-soft: quake-1996] Thinker Chain` at `subagent_dispatcher.py:9` must be stripped per M14 (metaphorical use only); CREDITS.md line 18 must be updated to remove or reclassify | doom_guy | **OPEN** — tag present in header | M14 gate: vet record required with scope declaration |
| **SS1-G0-03** | `a2a_transport.py` test skeleton exists (M21 gate) — **FILE DOES NOT EXIST**; only `a2a_bridge.py` + `a2a_auth.py` present in `src/omega/oracle/` | N9 (link) | **MISSING** — no such file | M21 contract test requirement |
| **SS1-G0-04** | `subagent_dispatcher.py` extension spec written (N9 ownership) — charter amendment §4 N9 += "dispatch/protocol-layering map ownership" ratified D-587 but spec not authored | N9 (link) | **OPEN** — charter amended, spec pending | N9 consultable session needed |

---

## P0 — BLOCKS DEBUT (PUBLIC-DEBUT-01)

| Gap ID | Description | Owner | Status | Blocker |
|--------|-------------|-------|--------|---------|
| **DEB-G0-01** | **V-10 AppArmor container hardening** — containers unconfined. `omega-hub.container:14-16` uses `:Z` (SELinux flag) on Ubuntu/AppArmor; no AppArmor profiles defined for any quadlet. Research R47 confirms `:Z` forbidden on Ubuntu | N5 (sentinel) / Ma'at | **OPEN** — config uses wrong flag, no profiles | V-10 GAP in ACTIVE_SPRINT.json notes |
| **DEB-G0-02** | **V-9 IA2 envelope freshness/signature check** — no IA2 implementation in `src/omega/`; `signer.py` in `omega_youtube_research/` only. V-9 requires envelope freshness verification at ingestion | N5 (sentinel) | **MISSING** — no IA2 code in core | V-9 GAP in ACTIVE_SPRINT.json notes |
| **DEB-G0-03** | **D-1 Content persistence + TTL** — not implemented. KALI_DEV_ROADMAP item 45 (8h, @researcher, Phase 3). No ContentCache module in `src/omega/` | Researcher | **BACKLOG** — Phase 3 item | D-1 depends on NL-1 per roadmap |
| **DEB-G0-04** | **D-2 Job board YAML bridge (P0/P1 only)** — not implemented. KALI_DEV_ROADMAP item 46 (6h, @lilith, Phase 3). No job board module in `src/omega/` | Lilith | **BACKLOG** — Phase 3 item | D-2 separate from Identity Phase 0 |
| **DEB-G0-05** | **ZS-1 zswap deployment** — script exists at `scripts/zswap_deploy.sh` but requires sudo; kernel cmdline + sysctl + 16GB NVMe swapfile + systemd cgroup config (MemoryMax=6G) not yet applied | Ma'at (N1) | **SCRIPT READY** — sudo execution pending | Architect sudo required |
| **DEB-G0-06** | **NL-1 NotebookLM ingestion pipeline** (`prepare_notebooklm.py`) — not implemented. R52c spec exists; `notebooklm-py` v0.8.1 adopted (D-571); depends on GN-1/2/3 + V-1 Vault + SDP §10 gate (10 manual runs) | Researcher / N12 | **BLOCKED** — prerequisites unmet | V-1 Vault + SDP gate + GN workstream |

---

## P1 — MANDATE COMPLIANCE GAPS

| Gap ID | Mandate | Description | Owner | Status |
|--------|---------|-------------|-------|--------|
| **MAN-P1-01** | **M17** Cognitive Integrity | Off-by-one in Carmack review: N10 verifier must fix "4→3 PARTIAL" (session_gnosis.md:417). Contract tests at every typed boundary (M21) incomplete for new SS-1 modules | N10 (verifier) | **PARTIAL** — 4→3 noted, fix pending |
| **MAN-P1-02** | **M26** Doc Standards | New SS-1 files (`a2a_transport.py`, `subagent_dispatcher.py` extensions, MCP Agent Card endpoint) must be added to `make doc-llm-validate` pipeline. N12 curator owns doc pipeline integration | N12 (curator) | **OPEN** — SS-1 files not in doc pipeline |
| **MAN-P1-03** | **M11** Soul Integrity | `staged_lessons` sink wired to delegation (SS-1 G2). All Node sessions must feed overseer's `proposed_lessons.yaml` with `[N_XX]` tags per Standing Order 10a | All overseers | **PARTIAL** — Standing Order 10a ratified, wiring pending |
| **MAN-P1-04** | **M14** Heritage | All `[id-soft:]` tags must have vet records with scope declarations in `HERITAGE_VET_LOG.md`. Thinker Chain tag in `subagent_dispatcher.py:9` lacks vet record with scope | doom_guy | **OPEN** — tag present, no vet record |
| **MAN-P1-05** | **M27** Tracking Integrity | GAP_REGISTRY.json must register any new gaps from this audit with distinct prefixes (no R1-R99 reuse). ACTIVE_SPRINT.json statuses must use only canonical states (backlog/ready/in_progress/blocked/completed/superseded/failed) | All agents | **OPEN** — new gaps need registration |

---

## P1 — HERITAGE VALIDATION GAPS (M14)

| Gap ID | Tag | Current State | Required Action | Owner |
|--------|-----|---------------|-----------------|-------|
| **HER-P1-01** | `[id-soft: quake-1996] Thinker Chain` at `subagent_dispatcher.py:9` | Present in header comment as "Heritage: Thinker chain — used for lifecycle tracking metaphor (inspired by Quake 1996)" | **STRIP TAG** — metaphorical use only (M14 classification: METAPHORICAL). Add vet record if legitimate use found elsewhere with scope declaration | doom_guy |
| **HER-P1-02** | `[id-soft: quake-1996] Thinker Chain` in CREDITS.md line 18 | Listed as legitimate pattern | **VERIFY VET RECORD** — check HERITAGE_VET_LOG.md for vet-011 (approved via vet-005/006) covers this usage with scope | doom_guy |
| **HER-P1-03** | `[id-soft: vet-015] ZONEID Pattern` at `subagent_dispatcher.py:8,41,56,70` | Legitimate — vet-015 approved (score 8/10) in HERITAGE_VET_LOG.md | **VERIFIED** — vet record exists with scope | doom_guy |
| **HER-P1-04** | New SS-1 code (`a2a_transport.py`, dispatcher extensions) | Not yet written | **PRE-EMPTIVE** — any new `[id-soft:]` tags must have vet record before merge | doom_guy / N9 |

---

## P1 — SECURITY GAPS

| Gap ID | CVE/Risk | Description | Owner | Status |
|--------|----------|-------------|-------|--------|
| **SEC-P1-01** | **D-590 P0** Hardcoded secret fallback | `ingestion.py:76` `SovereignSigner.__init__` had hardcoded `"omega-sovereign-change-me"` — **FIXED** (D-590): removed default, fail-closed, `OmegaError` raised if unset. Regression test `tests/unit/test_sovereign_signer.py` (4 tests) passing | N5 (sentinel) / N10 (verifier) | ✅ **FIXED & VERIFIED** 2026-08-22 |
| **SEC-P1-02** | **V-9** IA2 envelope freshness | No IA2 envelope freshness/signature verification in core ingestion pipeline. `signer.py` only in `omega_youtube_research/` | N5 (sentinel) | **MISSING** — core implementation needed |
| **SEC-P1-03** | **V-10** AppArmor profiles | No AppArmor profiles for any quadlet. `omega-hub.container` uses `:Z` (SELinux) on Ubuntu/AppArmor. R47 research confirms `:Z` forbidden | N5 (sentinel) / Ma'at | **OPEN** — profiles + correct flags needed |
| **SEC-P1-04** | Secret scanning | Git history scrubbed (Cline report: gitleaks=0 across 699 commits, 843 commits rewritten). PEM exclusions baselined. Cline checkpoints purged | Roc / Kali | ✅ **COMPLETED** 2026-08-22 |

---

## P2 — TECHNICAL DEBT / KNOWN LIMITATIONS

| Gap ID | Component | Description | Impact | Owner |
|--------|-----------|-------------|--------|-------|
| **TECH-P2-01** | N3 AGPL ruling | Kerykeion (AGPL-3.0) → pyswisseph-direct migration needed for arcana_novai WAD compliance | Legal risk if AGPL code ships in community stacks | N3 (buildmaster) |
| **TECH-P2-02** | N4 Tarotoo license | Tarotoo dataset: MIT license claimed but CC BY inconsistency in source attribution | License compliance risk for N13 arcana external source | N4 (bridge) |
| **TECH-P2-03** | Tier-0 executor model gap | `Qwen2.5-Coder-7B` (5GB) NOT on disk — C7 blocker. Nearest `gemma4-coding-Q4_K_M` (6.9GB) exceeds budget. Matrix rebuild or download required | LI-4 blocked; Tier 0 matrix incomplete | Ma'at / N6 |
| **TECH-P2-04** | zRAM/zswap decision reversal | D-526 (zswap > zRAM, RATIFIED) contradicted by all 2026-08-20 plans mandating zRAM-only. Cline review C-RAM: formal supersession of D-526 required | Config drift at deployment | Architect / Ma'at |
| **TECH-P2-05** | CONTEXT_WINDOW_OPTIMIZATION_RESEARCH CUT content | Carmack CUT items (SWA, LLMLingua-2, gpt-oss-20B, Nemotron-3-Nano) still present in doc marked "COMPLETE" | Misleading docs; supersession banner needed | Researcher |
| **TECH-P2-06** | Memory math contradiction | HOLISTIC_PLAN: weight cache 6.3GB vs models sum 8.6GB; code sketch uses mmap but Carmack FIX-2 mandates `--no-mmap --mlock` | Implementation wrong if followed | Ma'at |
| **TECH-P2-07** | NotebookLM workstream duplication | ACTIVE_SPRINT has `NOTEBKLM-STRATEGY` (stale 8-acct frame) + `NOTEBKLM-GAP-RESEARCH` + proposed `GEMINI-NOTEBOOK` = 3 overlapping trackers | Tracking fragmentation | Kali |
| **TECH-P2-08** | Domain schema conflict | `curators.yaml` (14 domains, D-569) vs proposed `metadata.yaml` schema for `gemini-notebook` — dual definition risk, `gemini-notebook` not in curators.yaml | Domain system inconsistency | Kali / N12 |
| **TECH-P2-09** | R58 Local IPC benchmarks | p99 < 3ms, >10k req/s target for local IPC — not yet measured | N11 evaluator scope | N11 |
| **TECH-P2-10** | R56 Chaos harness | ReliabilityBench/Maestro alignment for chaos testing — not started | Reliability validation gap | Researcher |
| **TECH-P2-11** | R57 AMD memory distillation | AMD-specific memory optimization research — not started | Local inference optimization | Researcher |
| **TECH-P2-12** | R55 IETF EAT/ACT | Entity Attestation Token / Attestation Claims Token — deferred, triggers registered | Standards compliance | Researcher |

---

## SOURCE REGISTER (Evidence Trace)

| Source | Type | Key Evidence |
|--------|------|--------------|
| `data/coordination/ACTIVE_SPRINT.json` | Primary | Sprint state, workstreams, gates, blockers, decisions_locked |
| `data/coordination/GAP_REGISTRY.json` | Primary | All gap IDs R1-R56, DP-1..8, GN/DS/LI/KD/HR/ZS prefixes, collision rules |
| `docs/decisions/PIVOT_LOG.md` | Primary | D-521 through D-592 decisions, supersessions, ratifications |
| `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` | Primary | N1-N13 charters, standing orders, amendments, session registry |
| `data/coordination/FINAL_GAP_AUDIT_20260820.md` | Primary | 57 gaps (54 unique) across 8 categories |
| `data/coordination/CLINE_FINAL_REVIEW_20260820.md` | Primary | C1-C3 critical conflicts, H1-H4 high conflicts, C7-C19 new issues, C-RAM zRAM/zswap reversal |
| `data/coordination/CLINE_COMPLETION_REPORT_20260822.md` | Primary | Secret scrub complete, gitleaks=0, filter-repo stats |
| `src/omega/oracle/ingestion.py` | Code | Line 76-82: OMEGA_INGESTION_SECRET fail-closed (D-590 fix) |
| `src/omega/oracle/subagent_dispatcher.py` | Code | Line 9: Thinker Chain heritage tag (M14 violation — metaphorical) |
| `src/omega/oracle/a2a_bridge.py` + `a2a_auth.py` | Code | A2A implementation exists; `a2a_transport.py` missing |
| `config/containers/omega-hub.container` | Config | Lines 14-16: `:Z` flag on Ubuntu/AppArmor (V-10 violation) |
| `scripts/zswap_deploy.sh` | Code | ZS-1 deployment script ready, sudo pending |
| `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | Primary | Vet records vet-001 through vet-017; vet-011 covers Thinker Chain via vet-005/006 |
| `CREDITS.md` | Primary | Heritage registry; Thinker Chain listed line 18 |
| `tests/unit/test_sovereign_signer.py` | Test | 4 tests passing for D-590 regression |
| `data/coordination/KALI_DEV_ROADMAP_20260811.md` | Primary | D-1 (item 45), D-2 (item 46), V-10 (item 43) roadmap entries |

---

*⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_critical_gap_audit ⬡ 2026-08-22*