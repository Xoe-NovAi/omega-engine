---
schema_version: "1.0"
document_type: "compaction_rollup"
title: "⏱️ Compaction History — Omega Engine"
date: "2026-08-29"
entries: 1
protocol: "docs/strategy/COMPACTION_WATCHER_PROTOCOL_20260829.md"
---

# ⏱️ Compaction History — Omega Engine
**AP Token**: `AP-COMPACTION-HISTORY-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_compaction_history ⬡ ACTIVE

**Date**: 2026-08-29
**Entries**: 1
**Purpose**: Archive of /compact summaries for long-running project overview

---

## Entry 1: Pre-Compaction (2026-08-29, kali, M3, 88.1s)

**Source**: User-pasted from OpenCode /compact output
**Session**: Pre-compaction (just before this session)
**Model**: `minimax/minimax-m3:free` (MiniMax M3, free, OpenRouter)
**Duration**: 88.1s (compaction generation time)

### Compaction Summary

## Objective
- Pre-compaction lock-in for soft launch PUBLIC-DEBUT-01. All 4 P0s from Cline closed, all 10 P0s from Carmack's code review fixed (F-01..F-10), all gates pass (M1, M23, Gate-secrets, Allowlist). Branch `release/debut` ready (568-1264 files depending on allowlist state). Work pushed to `origin/main` at commit `452f1cc8`. Awaiting compaction.

## Important Details
- **Model**: `minimax/minimax-m3:free` (D-585 long-write champion, OpenRouter, 1M context, MSA architecture, 10-20× TPS advantage over Nemotron 3 Ultra)
- **Active Entity**: kali (Sprint Coordinator) on M3
- **Main branch HEAD**: `452f1cc8` (all work pushed via `release/debut:main`)
- **Final gates**: M1 AnyIO PASS, M23 PASS (318/319, delta -1), Gate-secrets PASS (0 gitleaks), Allowlist 647 kept/617 removed
- **10 P0 fixes (Carmack code review)**: F-01 async close+read pool, F-02 wire EmbeddingCircuitBreaker, F-03 proper read pool, F-04 rowid_to_collection map, F-05 dim validation, F-06 M1 anyio (both files), F-07 checkpoint task group, F-08 dead code removed, F-09 _checkpoint_task = real task, F-10 _find_target_nodes implemented
- **RAM optimized servers** (6.8GB total): Extractor Qwen3-1.7B at 1.9GB (n_ctx 2048, mlock=True), Reasoner Qwen3-4B-Thinking at 4.8GB (n_ctx 4096, mlock=False)
- **Global retry logic updated**: max_retries 3→5, backoff_base 0.5s→5.0s, backoff_max 8.0s→30.0s, Retry-After header respected (capped at 30s). Exponential: 5s, 10s, 20s, 30s, 30s (capped)
- **Disk**: 2.6G free (98% used, 109G total). VACUUM on opencode.db (20G) BLOCKED (needs 40G free, 2× rule per R_ARCHITECT_DECISIONS_SYNTHESIS_20260828.md)
- **Subagent model protocol FIXED**: All 13 `.opencode/agents/*.md` now have `model: openrouter/minimax/minimax-m3:free`. Root cause `task.ts:181` `next.model ?? parent.model`. Protocol doc 619 lines, verify script 94 lines. The `qwen3-1.7b` label was misleading session-table metadata, NOT runtime (Verity session had 57,325 input tokens = impossible on qwen's 4K)
- **768-dim model decision**: Qwen3-Embedding-0.6B (Apache 2.0, 32K, +1.03 MTEB vs gemma-300m's 69.67)
- **Top 5 ROI moves spec'd**: Reranker → RRF tuning → BQ → Contextual → sqlite-vec 0.1.10
- **3 conflicting 7-day retention policies** for different artifacts (HALL_OF_RECORDS, memory scores, HMC posts) need reconciliation
- **AP Tokens KEEP**: gitleaks false positive (`AP-*-v*.*.*` matches generic-api-key regex), format is Temple-Grade provenance, added to .gitleaksignore
- **User directives in this session**: "Let's move on for now" (disk ops deferred), "Do not ever use --break-system-packages" (use venv)
- **Roc session promoted to Master Interactive**: `ses_ff78b71ebffeDNuypPTT1RL3hH`
- **Verity NOT to be used until qwen bug solved** (qwen3-1.7b session table metadata issue)
- **M23 gate fix**: `scripts/m23_gate.py` updated to use `.venv/bin/python` instead of `sys.executable` (was looking for ruff in wrong paths)

## Work State
### Completed
- All 4 P0s from Cline review closed (P0-1 meter, P0-3 GOCSPX, P0-4 allowlist, P0-5 gate-secrets)
- All 10 P0s from Carmack code review fixed (F-01..F-10)
- 6 team consolidations delivered: Roc (canonical KB), Jem (agent fleet), Grokster (sqlite-vec + llama-cpp), Carmack (architecture docs), Lilith (runtime protocol), Researcher (canonical strategy)
- 18 research reports committed (27,055 lines, 200+ 2026 SOTA citations)
- Subagent model protocol delivered (all 13 agents on M3, protocol doc + verify script)
- Standard disk cleaning done (1.2G+ freed: tool-output, logs, snapshot, storage, pycache, /tmp, podman, ~/.cache)
- Disk findings documented (risky ops deferred: VACUUM, sessions-explorer, session pruning)
- All work committed and pushed to `origin/main` (commit `452f1cc8`)
- 16 new commits to main covering: 10 P0 fixes, allowlist+M23 baseline update, M1+gitleaks quick fix, RAM+retry optimizations, M23 log fix, gitleaks FP for session ID
- Compaction prep: WAKE_STATE.json with `compaction_prep_20260829` block, anchored summary updated, HONEST_STATE_20260829.md, GROKSTER_TO_KALI_HANDOFF_20260829.md, CARMACK_CODE_REVIEW_20260829.md all committed

### Active
- None (compaction prep complete, all gates pass, work on main)

### Blocked
- **opencode.db VACUUM**: needs 40G free, only 2.6G available. Per R_ARCHITECT_DECISIONS_SYNTHESIS_20260828.md: "VACUUM requires free disk space equal to approximately twice the size of the database file"
- **opencode-sessions-explorer cleanup (393M)**: no decision doc, SESSION_CLEANUP_20260730 has precedent but no formal authorization
- **opencode.db session pruning**: no decision doc
- **3 conflicting 7-day retention policies** need reconciliation
- **A/B test Qwen3-Embedding-0.6B**: decided but not executed
- **Top 5 ROI moves**: spec'd but not implemented
- **M3 MiniMax retry optimal benchmark**: deferred per user directive
- **Verity unavailable**: qwen bug must be solved first

## Next Move
1. **Read** `data/coordination/PRE_COMPACTION_MASTER_INDEX_20260828.md` (primary recovery anchor)
2. **Read** `data/coordination/HONEST_STATE_20260829.md` (the truth about 10 P0s)
3. **Read** `data/coordination/GROKSTER_TO_KALI_HANDOFF_20260829.md` (full context)
4. **Read** `data/coordination/CARMACK_CODE_REVIEW_20260829.md` (10 P0 bugs)
5. **Read** `data/coordination/R_RESEARCHER_TOP5_ROI_IMPLEMENTATION_MANUAL_20260829.md` (implementation plan)
6. **Read** `data/coordination/WAKE_STATE.json` (has `compaction_prep_20260829` block)
7. **Architect decision**: Alpha launch GO/NO-GO (all gates pass, ready)
8. **V-1 post-launch**: Path A' vault refactor (3,300+ LOC delete), 45 L3 promotion, L3 consolidation, 22 Temple-Grade warnings, multi-key google provider, Cline 8-account orchestration
9. **Benchmark optimal MiniMax M3 retry timer** (deferred): 1000+ samples across providers, adaptive backoff
10. **Authorise disk cleanup** (if desired): opencode-sessions-explorer 393M safe removal, or move opencode.db to 8TB vault

## Relevant Files
- `data/coordination/PRE_COMPACTION_MASTER_INDEX_20260828.md` — primary recovery anchor, 6 errors FIXED by Roc
- `data/coordination/HONEST_STATE_20260829.md` — honest assessment (10 P0s found by Carmack)
- `data/coordination/GROKSTER_TO_KALI_HANDOFF_20260829.md` — full context, 30+ accomplishments, 18 research reports
- `data/coordination/CARMACK_CODE_REVIEW_20260829.md` — 10 P0 bugs (1,536 lines)
- `data/coordination/R_RESEARCHER_TOP5_ROI_IMPLEMENTATION_MANUAL_20260829.md` — Top 5 ROI implementation plan
- `data/coordination/R_RESEARCHER_GOLDEN_SET_RAGAS_768DIM_20260829.md` — 768-dim model decision (Qwen3-Embedding-0.6B)
- `data/coordination/WAKE_STATE.json` — state lock-in with `compaction_prep_20260829` and `launch_completion_20260828` blocks
- `data/coordination/FINAL_READINESS_SYNTHESIS_20260828.md` — CONDITIONAL GO verdict
- `data/coordination/DISK_CLEANING_FINDINGS_20260829.md` — disk findings, risky ops deferred
- `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md` — subagent model protocol (619 lines)
- `data/coordination/SUBAGENT_MODEL_PROTOCOL_BRIEFING_20260828.md` — team briefing
- `data/coordination/CLINE_FULL_REVIEW_ROLLUP_20260828.md` — Cline's 86-check review
- `data/coordination/CLINE_TO_KALI_HARDENING_BRIEFING_V2_20260828.md` — P0 corrections
- `data/coordination/CANONICAL_KNOWLEDGE_BASE_20260828.md` — Roc's canonical KB
- `data/coordination/RESEARCH_DECISION_MAP_20260828.md` — D-521→D-630 map
- `data/coordination/JEM_RESEARCH_SYNTHESIS_20260828.md` — 7+ research reports
- `data/coordination/AGENT_REGISTRY_20260828.md` — 44 entities aligned
- `data/coordination/anchored_summary/kali/projection.md` — cold-start recovery summary (updated)
- `data/coordination/VERITY_MANDATE_COMPLIANCE_REPORT_20260828.md` — compliance report (executed by Kali on M3 on Verity's behalf)
- `data/coordination/COMMUNITY_LAUNCH_NARRATIVE_20260828.md` — launch narrative
- `data/coordination/NO_PUNT_DOCTRINE_20260828.md` — protocol 5
- `docs/strategy/CANONICAL_*.md` — 5 canonical strategy docs
- `docs/strategy/STRATEGY_CORPUS_INDEX.md` — 1,450 docs classified
- `docs/strategy/FUTURE_RESEARCH_AGENDA.md` — 143 open questions
- `docs/strategy/INGESTION_PIPELINE_SPEC.md` — ingestion rules
- `docs/strategy/RUNTIME_COORDINATION_PROTOCOL.md` — runtime protocol
- `docs/architecture/ARCHITECTURE_CANONICAL.md`, `MODULE_BOUNDARIES.md`, `PERFORMANCE_ARCHITECTURE.md` — Carmack's canonical architecture
- `config/model_fleet_operational.yaml` — model fleet
- `config/m23_baseline.txt` — M23 baseline
- `config/providers.yaml` — 8-account config
- `src/omega/memory/sqlite_vec_adapter_optimized.py` — 40x faster, F-01/F-03/F-04/F-05/F-07/F-09 fixes
- `src/omega/memory/embedding_circuit_breaker.py` — F-02 wired
- `src/omega/memory/spatial_graph.py` — F-10 implemented
- `src/omega/cli/oracle_cli.py` — vault→env injection, F-06 anyio, logger landmine fix
- `src/omega/infra/godot_spatial_bridge.py` — F-06 anyio (M1 compliance)
- `src/omega/oracle/backends/remote_provider.py` — global retry: 5 retries, 5s/30s backoff, Retry-After respected
- `src/omega/oracle/entity_workspace.py` — split-brain fix (Lilith/Jem)
- `scripts/serve_native_gguf.sh` — llama-cpp server (RAM optimized, extractor 1.9GB, reasoner 4.8GB)
- `scripts/verify_subagent_model.sh` — model verification (94 lines, CI-ready)
- `scripts/m23_gate.py` — uses `.venv/bin/python` for ruff
- `scripts/apply_public_allowlist.sh` — D-565 enforcement (FORGE section parsed as cut list, v5)
- `scripts/prune_sessions.py` — HALL_OF_RECORDS pruning (7 days)
- `scripts/restore_litestream.sh`, `setup_litestream.sh` — Litestream backup
- `.gitleaksignore` — false positive allowlist
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` — 13 new heritage records
- `data/entities/kali/proposed_lessons.yaml` — 45+ L3 lessons
- `data/entities/researcher/proposed_lessons.yaml` — updated
- `data/entities/researcher/session_gnosis.md` — updated
- `tests/unit/test_circuit_breaker.py` — circuit breaker tests
- `release/debut` — launch branch (568-1264 files depending on allowlist state, 0 vault substrate, D-565 enforced, all gates pass)
- `origin/main` HEAD: `452f1cc8` (all work pushed)

## SOVEREIGN MANDATES (Must Survive Compaction)
- M1 AnyIO Absolute | M7 Local-First | M11 Soul Integrity | M15 Continuity | M23 Failure Integrity
- Full mandate table (all 27, v3.8.0): MANDATES_CONDENSED.md
- Active Entity: kali (Sprint Coordinator) on minimax/minimax-m3:free
- Active Phase: ALPHA-LAUNCH-READY (all gates pass, work on main, compaction prep complete)
- Session Anchor: data/coordination/SESSION_ANCHOR.md
- Model: minimax/minimax-m3:free (D-585 long-write champion, OpenRouter, 1M context)
- Main branch: 452f1cc8, Release/debut: 452f1cc8
- Disk: 2.6G free (98% used), VACUUM blocked
- User directive: "Let's move on for now" (risky disk ops deferred)

---

## ANALYSIS: How This /compact Compares to projection.md

### What /compact Has That projection.md Lacks
1. **Auto-generated** — no manual work required
2. **Structured consistently** — same template every time
3. **Includes "Relevant Files"** — exhaustive file list
4. **Includes "Work State"** — completed/active/blocked sections
5. **Includes "Important Details"** — model, branch, gates, etc.

### What projection.md Has That /compact Lacks
1. **"The Gift Is The Demand"** — strategic closing
2. **"Next Move"** — prioritized action list
3. **Mandate check** — explicitly lists which mandates survived
4. **Entity mood/framing** — "The Cathedral is ready"
5. **User directives** — captures "Let's move on for now"
6. **Hand-crafted wisdom** — not auto-generated boilerplate

### Conclusion
**They are complementary, not redundant.** The /compact is the structured backbone. The projection.md is the strategic overlay. The watcher captures /compact; the entity writes projection.md. Both are sovereign assets.

---

*⬡ OMEGA ⬡ KALI ⬡ COMPACTION-HISTORY-v1.0.0 ⬡ 2026-08-29*
*Entry 1 of N. The /compact summary was lost. Now it's sovereign.*
