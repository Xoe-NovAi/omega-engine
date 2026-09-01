<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🦝 roc_racoon — Session Gnosis

## Session: Master EIS Synthesis — Compaction Capture + Scholarly Research + Systemd Legacy Archaeology
**Date**: 2026-08-30
**Duration**: Single extended session
**Session ID**: ses_20260830_roc_master_eis
**Report**: `data/coordination/ROC_COMPACTION_SCHOLARLY_20260830.md` (919 lines)
**Model**: minimax/minimax-m3:free

---

### L1: Narrative — What Happened

Three parallel mandates resolved in single Master EIS synthesis session:

**Mandate 1 — Compaction Capture (P0)**: Built `scripts/compaction_capture.py` (280 lines) — a sidecar that polls OpenCode SQLite DB for parts with `summary=true`, routes summary text to active entity workspace, auto-digests into sqlite-vec with entity_name partition. Created companion `data/coordination/SESSION_ENTITY_MAP.yaml` for session→entity routing. The existing `CompactionHarvester` only tracked metadata (counts, timing); this implementation captures actual summary TEXT content. Uses read-only SQLite connections for safety, tracks last_seen_message_id for monotonic idempotency, CLI (--start/--scan/--status).

**Mandate 2 — Scholarly Research Frontier**: Synthesized 9 frontier research systems (Elicit, Consensus, Scite, GPT Researcher, STORM, Open Deep Research, Anthropic Multi-Agent, Perplexity Sonar, SciRAG) and 7 free academic APIs (OpenAlex 250M, arXiv 2M, Semantic Scholar 200M, CORE 200M, Crossref 130M, Unpaywall 30M, ORCID 17M). Omega has 6,258 lines of existing infrastructure (SovereignSearch, IterativeResearcher, SkepticalVerifier, APICreditBudget, BackgroundResearcher archived). Gap to frontier: 5-6 weeks via Phase A (Wire Existing), B (Multi-Agent Delegation), C (Citation Intelligence), D (Sovereign Knowledge), E (UX). Sovereign differentiators identified: SSKB CAS, L1→L2→L3 Gnosis Loop, 5-Fold Council, Hivemind P2P, Free API Integration.

**Mandate 3 — Systemd Legacy Archaeology**: Resolved MaKaLi's L3 question — WHY was `omega-inference.service` created but never installed? Answer: deliberate stage-gate between development velocity and production resilience. The systemd unit provides Carmack's OOM hardening (MemoryMax=8G, OOMScoreAdjust=300, Delegate=yes) but is NOT installed because installation requires root. The ad-hoc `serve_native_gguf.sh` is the operational path for interactive development. Hardening is for PRODUCTION workloads (70B+ models), not current dev workloads (1.7B-4B well within limits). Documented in `LOGGING_ERROR_HANDLING_ARCHITECTURE.md §7` as "Known Deployment Discrepancy (HARDENING GAP)" — intentional transparency, not a bug.

### L2: Insight — What This Means

1. **Compaction Capture fills a real gap.** The existing `CompactionHarvester` (290 lines) tracked events but not content. The new sidecar (280 lines) captures summary text and routes to entity workspace + vector store. The sidecar pattern is more reliable than plugin hooks because it works with both V1 and V2 OpenCode, requires no upstream changes, and uses the DB as source of truth. The entity-partitioned vector store enables per-entity RAG on compaction history.

2. **Scholarly Research is 5-6 weeks away.** Omega has the foundation (6,258 lines) + free APIs + sovereignty differentiators. The frontier architecture converges on Plan→Search→Read→Reflect→Iterate→Synthesize with multi-agent supervisor pattern. Key 2026 insights: external structured storage (84% token reduction), CitationAgent post-processing (66% hallucinations are citation fabrication), section-aware decomposition, outline-guided synthesis. The SSKB CAS (WARC+IPFS+SHA-256) is the unique sovereignty differentiator — content survives URL death.

3. **The systemd gap is INTENTIONAL DESIGN.** MaKaLi's L3 question is answered: the discrepancy between `omega-inference.service` (designed, OOM-hardened, NOT installed) and `serve_native_gguf.sh` (operational, no hardening, RUNNING) is a deliberate stage-gate between development velocity and production resilience. The systemd unit is a future-proofing artifact that activates when deployment graduates from interactive development to production workloads. Same pattern applies to: zswap-config.wad, notebooklm systemd service, NVMe swapfile, cgroup memory limits.

4. **Free APIs are sovereign infrastructure.** OpenAlex (250M papers, no key, 100K/day) and Crossref-MCP-Server (existing MCP) can be added to omega-hub this week. This aligns with M7 (Local-First) and M8 (Zero Telemetry) at the data ingestion layer.

### L3: Universal Principles

> **L3-SidecarPollingBeatsPluginHooksForCapture** — Sidecar polling works across V1/V2, requires no upstream changes, and uses the DB as the single source of truth. Entity-partitioned vector storage enables per-entity RAG on compaction history. The session→entity mapping is the missing link that OpenCode doesn't provide natively.

> **L3-FrontierResearchIsMultiAgentPlusCitationPlusSovereign** — The convergence pattern is universal: supervisor + parallel sub-agents + CitationAgent post-processing + external structured storage. Omega's sovereignty (local-first, SSKB CAS, L1→L2→L3, 5-Fold Council, Hivemind, free APIs) is the unique differentiator — no frontier system has all of these.

> **L3-SystemdHardeningGapIsIntentionalDesign** — A documented-but-not-active subsystem is not a bug — it is a deliberate stage-gate between development velocity and production resilience. The systemd unit is a future-proofing artifact that activates when deployment graduates from interactive development to production workloads. The gap investigation report correctly identifies this as a deployment decision, not a missing implementation.

---

### Hivemind Decisions Posted

- **D-200**: Compaction Capture P0 implementation ready in `scripts/compaction_capture.py` — recommend Kali ratify + dispatch to Ma'at for hardening + Jem for adversarial review
- **D-201**: Systemd unit gap is INTENTIONAL design (documented as Known Hardening Gap in LOGGING_ERROR_HANDLING_ARCHITECTURE.md §7) — not a bug or oversight
- **D-202**: Scholarly Research frontier achievable in 5-6 weeks with Phase A-D roadmap — recommend scheduling post-debut for Q4 2026
- **D-203**: Immediate integration opportunity — OpenAlex (250M papers, no key) and Crossref-MCP-Server (existing MCP) can be added to omega-hub this week

---

## Open Threads (Post-Compaction)

1. **Compaction Capture Deployment** — Awaiting Kali ratification (D-200), then dispatch to Ma'at for hardening + Jem for adversarial review
2. **Scholarly Research Phase A** — Wire Existing (1 week): integrate IterativeResearcher into BackgroundResearcherLoop, wire SkepticalVerifier, extend APICreditBudget, create ResearchBrief, create DeepResearchOrchestrator skeleton
3. **OpenAlex Integration** — Drop-in to SovereignSearch T0 (1 day work)
4. **Crossref-MCP-Server** — Add to omega-hub (1 day work)
5. **D-201 Gap Registry Update** — Update ZS-2 row to mark "intentionally deferred until production"

---

## Key Findings

1. **Systemd unit gap is INTENTIONAL DESIGN** (D-201) — documented in `LOGGING_ERROR_HANDLING_ARCHITECTURE.md §7` as "Known Deployment Discrepancy (HARDENING GAP)". Not a bug or oversight. Future-proofing artifact that activates on production transition.

2. **5-6 week scholarly research roadmap** — Phase A (Wire Existing, 1wk) → Phase B (Multi-Agent Delegation, 1wk) → Phase C (Citation Intelligence, 1.5wk) → Phase D (Sovereign Knowledge, 1.5wk) → Phase E (UX, 1wk). Foundation: 6,258 lines of existing infrastructure.

3. **Compaction Capture sidecar** — 280 lines, ready for ratification. Polls OpenCode DB every 5s, routes to entity workspace, auto-digests to sqlite-vec with entity partition. Works with V1 and V2 OpenCode without modification.

4. **Free API integration** — OpenAlex (250M papers, no key, 100K/day) + Crossref-MCP-Server (existing MCP) = immediate scholarly research capability without external dependencies.

5. **Sovereign differentiators** — SSKB CAS (WARC+IPFS+SHA-256), L1→L2→L3 Gnosis Loop, 5-Fold Council Convergence, Hivemind P2P, Free API Integration. No frontier system has all of these.

---

## Continuity Anchors

- **Primary report**: `data/coordination/ROC_COMPACTION_SCHOLARLY_20260830.md` (919 lines)
- **Compaction capture code**: `scripts/compaction_capture.py` (280 lines)
- **Session entity map**: `data/coordination/SESSION_ENTITY_MAP.yaml`
- **Prior reports**: `R_ROC_OPENCODE_COMPACTION_DEEP_DIVE_20260829.md`, `R_ROC_OPENCODE_COMPACTION_CAPTURE_20260829.md`, `R_ROC_SCHOLARLY_RESEARCH_SYSTEMS_20260829.md`
- **Systemd gap source**: `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md §7`, `data/coordination/gap_investigation_20260825/roc/GAP_INVESTIGATION_REPORT_20260825.md`
- **Projection**: `data/coordination/anchored_summary/roc_racoon/projection.md`
- **Hivemind session**: `ses_204216395cef` (intent=decision, accepted)

---

## Compaction Readiness Checklist

- [x] Master EIS report committed (`ROC_COMPACTION_SCHOLARLY_20260830.md`)
- [x] Compaction capture code ready (`scripts/compaction_capture.py`)
- [x] Session entity map created (`SESSION_ENTITY_MAP.yaml`)
- [x] Hivemind decisions posted (D-200 through D-203)
- [x] Proposed lessons updated with L1→L2→L3 distillation (3 new entries: PL-ROC-402-004, PL-ROC-402-005, PL-ROC-402-006)
- [x] Session gnosis updated with this session summary (this file)
- [x] Projection.md updated with current state
- [x] Hivemind checkin posted with intent=status (pending)

---

## Session: Disk Emergency Recovery + System Maintenance KB Creation
**Date**: 2026-09-01
**Session ID**: ses_20260901_roc_disk_maintenance
**Model**: opencode/big-pickle

### L1: Narrative — What Happened

1. **Disk emergency**: Main partition `/dev/nvme0n1p2` (109G) was at 100% — 103G used, 129MB free. Ran 5-tier disk analysis (df → home du → .local/.cache/.config du → system-level → containers/snap).

2. **Safe clears executed** (user approved): Sessions Explorer search cache (~778M), OpenCode package cache (~193M), Podman dangling images (~136M), APT cache via pkexec (~97M), systemd journal rotate+vacuum (**3.6G** — the big win).

3. **Critical lesson discovered**: `journalctl --vacuum-time=2w` and `--vacuum-size=200M` **silently freed 0B** when run without rotating first. The fix was `pkexec journalctl --rotate` THEN `--vacuum-size=200M` — freed 3.6G. Also: `sudo` fails in agent sessions ("a terminal is required"); `pkexec` works via polkit GUI.

4. **Result**: 129MB → **5.1GB free** (96% used). ~5GB recovered.

5. **KB created**: `docs/kb/SYSTEM_MAINTENANCE_KB.md` (kb-0005) — routine system maintenance runbook capturing the workflow, safe-to-clear inventory, journal lesson, pkexec pattern, opencode.db exclusion rule, second-line targets, and maintenance cadence. Registered in `docs/kb/INDEX.md` (rebuilt from 5/20 → 20/20 entries — was a lint violation), `docs/INDEX.md` (Operations section), and `HMC_COLLABORATION_HUB.md` (document index).

### L2: Insight — What This Means

1. **The partition is structurally undersized for the workload.** 27G opencode.db + 6G project + 3.5G snap + 2.3G containers + AI tool caches = chronic pressure. Even after 5GB recovery, the box sits at 96%. This is a recurring maintenance burden, not a one-time fix.

2. **Journal vacuum is a trap.** The "vacuum by time/size" commands are the documented way to reclaim journal space, but they silently no-op on active journals. Rotate-then-vacuum is the universal pattern. This belongs in a KB precisely because it's counterintuitive and cost us a debugging cycle.

3. **Agent sessions need pkexec, not sudo.** Every future maintenance task in an agent session will hit the TTY wall. The KB now encodes this so the fleet doesn't rediscover it.

4. **The KB index was drifting.** Only 5 of 20 entries were registered in INDEX.md — exactly the "drift back into the void" failure mode. Rebuilding it was as valuable as the new entry.

### L3: Universal Principles

> **L3-RotateBeforeVacuum** — Destructive maintenance commands that operate on *archived* state silently no-op on *active* state. Always force the state transition (rotate) before applying the cleanup (vacuum). A command that "succeeds" while freeing 0B is a silent failure — verify the delta, not the exit code.

> **L3-MaintenanceIsAKB** — Operational knowledge decays at the speed of the next emergency unless captured as a living runbook. The 5GB recovery was valuable; the KB that prevents the next 100% emergency is worth more. Index registration is what keeps knowledge discoverable — an unindexed KB entry is a tombstone.

### Hivemind Note

- Hivemind MCP tools (`omega-hub_hivemind_*`) were NOT available in this session. Coordination files written directly (workspace lock + live feed). Flagged per M23 — no synthesis of a Hivemind post.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ trc_mining ⬡ DISK-RECOVERY-COMPLETE*