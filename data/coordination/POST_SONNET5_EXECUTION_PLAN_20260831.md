# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

---
schema_version: "1.0"
document_type: "execution_plan"
document_id: "POST_SONNET5_EXECUTION_PLAN_20260831"
title: "Post-Sonnet 5 Audit — Full Execution Plan to Public Debut"
status: "ACTIVE — Canonical Execution Plan"
date: "2026-08-31"
author: "kali (Transcendent Oversoul / Sprint Coordinator)"
model: "google/gemini-3.7-flash"
sprint: "PUBLIC-DEBUT-01"
classification: "sovereign-internal, execution-authority"
---

# 🔱 POST-SONNET5 EXECUTION PLAN — Full Path to Public Debut

**AP Token**: `AP-KALI-POST-SONNET5-PLAN-v1.0.0`  
⬡ OMEGA ⬡ KALI ⬡ google/gemini-3.7-flash ⬡ opencode ⬡ trc_oversight ⬡ ACTIVE  
**Date**: 2026-08-31  
**Source**: Sonnet 5 Audit Report (`omega_engine_audit_report.md`) + all prior context

---

## §0 — Executive Summary

**Verdict**: **CONDITIONAL-GO** for Public Debut. Two hard conditions must close:
1. **P0-1b Security** — `SECURITY_AUDIT_2026_05_19.md` at ancestor commit `0c40b108` carries 3 real-format keys reachable from HEAD
2. **Theater Strip (Q1)** — Delete ~3,000 lines of control-plane ceremony (M33/M34/M36/cohort/dispatch_guard)

**The Finding That Changes Everything**: The "81/81 tests passing" are tests of the theater, not the engine islands. The entire test suite covers M33/M34/M36/cohort — zero tests cover MemoryStore, SQLiteVecAdapter, SoulStore, OOMProtector, HealthMonitor, native-gguf.

**Net Result**: One PR removes ~3,000 lines and 71 of 81 tests. Replace with ~10 honest tests. Then debut.

---

## §1 — Phase 0: Immediate Prerequisites (This Week)

### 0.1 P0-1b Security — Key Rotation (BLOCKS DEBUT)
**Owner**: Ma'at / Sentinel  
**Effort**: 2-4 hours  
**Action**: 
- Identify the 3 real-format keys in `SECURITY_AUDIT_2026_05_19.md` at commit `0c40b108`
- Rotate/revoke all three
- Verify no keys reachable from HEAD via `git log --all --full-history -- SECURITY_AUDIT_2026_05_19.md`
- Document rotation in `data/coordination/KEY_ROTATION_LOG_20260831.md`

**Gate**: No public push until this closes. Independent of theater strip.

### 0.2 SearXNG Health Fix (BLOCKS SOVEREIGN SEARCH T1)
**Owner**: SysAdmin / Bridge  
**Effort**: 1-2 hours  
**Action**:
- SearXNG on port 8018 is up but returns empty results
- Check SearXNG logs: `docker logs searxng` or `journalctl -u searxng`
- Verify engine configs in `/etc/searxng/settings.yml`
- Test: `curl -s "http://127.0.0.1:8018/search?q=test&format=json"`

**Gate**: Sovereign Search T1 must return results for library ingestion to work.

---

## §2 — Phase 1: Theater Strip PR (DEL-1 Week 1 — Single PR)

**Owner**: Ma'at (lead) + Lilith + Roc  
**Effort**: 8-12 hours total  
**Branch**: `theater-strip-del1` from `release/debut`  
**Rule**: `omega talk "hello"` must exit 0, local, after EVERY step.

### 2.1 Deletion Sequence (Exact Order from Sonnet Q1)

| Step | Target | Files | Tests Removed | Rationale |
|------|--------|-------|---------------|-----------|
| 1 | **Cohort Registry** | `src/omega/oracle/cohort_registry.py`<br>`data/registry/cohort_registry_schema.json`<br>`data/registry/COHORT_REGISTRY.json`<br>`tests/test_cohort_registry.py` | 22 | Zero external callers in provided bundles |
| 2 | **M36 Recursive Probe** | `src/omega/oracle/m36_recursive_probe.py`<br>`tests/test_a4_m36_wiring.py`<br>`tests/test_a5_m36_soft_verifier.py` | 29 | Only caller: `m33_probe.complete_with_validation()` |
| 3 | **M33 Probe** | `src/omega/oracle/m33_probe.py`<br>`tests/test_a2_m33_probe.py`<br>`tests/test_a3_m33_integration.py` | 19 | Only caller: `subagent_dispatcher.dispatch()` |
| 4 | **Subagent Dispatcher — Strip M33 wiring** | `src/omega/oracle/subagent_dispatcher.py` | — | Remove "M33 Probe Wiring" block in `dispatch()`; collapse M34 registration to single thin call; strip `HandoffPacket` Quake fields (`zoneid`, `visited_agents`, `hop_count`, `max_hops`, `resolver_strategy`) |
| 5 | **Dispatch Guard — Flatten to 3 steps** | `scripts/dispatch_guard.py` | — | Keep: Step 1 (specialist routing), Step 9 (secrets scan), Step 6b (M34 registration). Delete: Steps 2-5, 7, 8, 10-12. Delete `dispatch_guard_log.jsonl` writer (M27 dual ledger). |
| 6 | **Fold ACTIVE_SUBAGENTS into TASK_REGISTRY** | `src/omega/oracle/m34_registry.py`<br>`data/registry/ACTIVE_SUBAGENTS.json`<br>`data/registry/TASK_REGISTRY.json` | — | Add optional `liveness` sub-object to `TASK_REGISTRY.json` schema. Delete `ACTIVE_SUBAGENTS.json` and its dedicated registry module. |
| 7 | **Replace 81 theater tests with ~10 honest tests** | New test file(s) | -71 +10 | Test: registration writes entry (3-4), secrets scan catches planted key (2-3), specialist hint fires on keyword (2-3). |

### 2.2 Verification Checklist (After Each Step)
- [ ] `omega talk "hello"` → exits 0, `IS_CLOUD=False`, `PROVIDER_NAME=native-gguf`
- [ ] `make check-m1-anyio` passes
- [ ] `python3 scripts/m23_gate.py` passes
- [ ] `.venv/bin/reuse lint` passes
- [ ] No import errors in `src/omega/`

### 2.3 Test Replacement Target
**New test file**: `tests/test_honest_dispatch.py` (~10 tests)
- M34 registration writes liveness entry
- Secrets scan detects planted API key
- Specialist routing hint fires on keyword
- `HandoffPacket` serializes with only essential fields
- `dispatch_guard.py` runs 3 steps, no `dispatch_guard_log.jsonl`

---

## §3 — Phase 2: Post-Strip Hardening (Week 2)

### 3.1 Library Module Restoration (UNBLOCKS HUB RESTART)
**Owner**: Ma'at / DataStore  
**Effort**: 2-3 hours  
**Action**:
```bash
# Restore from Desktop backup (fastest)
cp -r /home/arcana-novai/Desktop/src/omega/library /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/
```
**Verify**: Hub restart survives; `omega-hub_library_stats` returns data.

### 3.2 Vec0 Double-Prefix Migration
**Owner**: Roc / DataStore  
**Effort**: 1 hour  
**Action**:
```sql
-- In omega_memory.db
ALTER TABLE omega_vec_omega_vec_gemma_768 RENAME TO omega_vec_gemma_768;
-- Or drop and let lazy creation handle it (loses 1,009 vectors)
```
**Verify**: `MemoryStore.search()` returns results for entity queries.

### 3.3 Unify Data Directories
**Owner**: SysAdmin  
**Effort**: 1 hour  
**Action**: Set `OMEGA_DATA_DIR=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data` consistently in systemd unit and all configs.

### 3.4 Wire Vision Model (Qwen3-VL-4B)
**Owner**: ModelGate / Bridge  
**Effort**: 4-6 hours  
**Action**:
- Add vision model entry to `config/providers.yaml` with `multimodal: true`
- Extend `ModelGateway` for multimodal path (image + text → response)
- Add `vision_infer` tool to agent toolsets
- Test: image analysis query via `omega talk` with image attachment

### 3.5 EIS/NES Dashboard
**Owner**: Link / Context  
**Effort**: 4-6 hours  
**Action**:
- Build `omega-hub` endpoint: `/eis-nes/status` showing all sessions with health
- Add `eis-page` / `nes-dispatch` custom commands
- Integrate with `opencode-sessions-explorer` for session discovery

---

## §4 — Phase 3: Knowledge-Centric Pivot (Week 3+)

### 4.1 KD Workstream — The Pivot (Single PR)
**Owner**: Kali (lead) + DataStore + Researcher  
**Effort**: 8-12 hours  
**Deliverables** (from Sonnet Q5):
- `config/domains/<domain>/` — YAML per domain: `name`, `version`, `curator`, `affinity`, `guidance_sets`
- `config/domains/curators.yaml` — flat `domain → curator_model` map
- Affinity presets: research→`qwen3-4b-thinking`, coding→`mimo-7b-rl`, fast→`qwen3-1.7b`
- WAD vs Domain separation: WAD = cosmology (who speaks), Domain = knowledge (what they know)

### 4.2 Library Ingestion Pipeline (Fixed)
**Owner**: Roc / DataStore  
**Effort**: 4-6 hours  
**Action**:
- Modify `scripts/ingestion_pipeline.py` to use `EmbeddingManager` + `SQLiteVecAdapter`
- Write to canonical `omega_memory.db` with entity/domain partitioning
- Ingest: coordination docs (146 in FTS), entity souls (56), research docs, legacy mining
- Target: 500+ vectors in library collections

### 4.3 Agent Recall Integration
**Owner**: Context / ModelGate  
**Effort**: 3-4 hours  
**Action**:
- Extend `MemoryStore.search()` to RRF-fuse library collections
- Add `library_search` tool to agent toolsets
- Test: agent query → hybrid search (memory + library) → results in context

### 4.4 Grok CLI 8-Account Fleet
**Owner**: Grokster / Grok CLI  
**Effort**: 6-12 hours  
**Action**:
- Provision 7 more xAI accounts (manual auth) → `~/.grok-fleet/acct-{1..8}/auth.json`
- Implement real `check_quota()` via gRPC-web `GetGrokCreditsConfig`
- Fix dangling instruction file (`.opencode/agents/grok_cli.md`)
- Wire `find_available_account()` rotation + 402 recovery
- Test: dispatch Grok CLI as subagent via omega-hub MCP

---

## §5 — Phase 4: Public Debut (End Week 3 / Start Week 4)

### 5.1 Final Verification
- [ ] `omega talk "hello"` → local, native-gguf, <5s warm
- [ ] `make temple-grade` exits 0
- [ ] `install.sh` provisions venv + downloads model + runs
- [ ] `proposed_lessons.yaml` persists across sessions
- [ ] No keys in repo history (`git-secret-scrub` clean)
- [ ] `REUSE v3.3` compliant (71,579/71,579)

### 5.2 Release Branch & Tag
```bash
git checkout release/debut
git tag -a v0.1.0-debut -m "Public Debut: local-first AI runtime with soul continuity"
git push origin release/debut --tags
```

### 5.3 Three-Sentence Launch Announcement (from Sonnet Q7)
> *"Omega is a local-first AI runtime: `omega talk` runs entirely on your machine via native GGUF inference, with cloud used only as an explicit, visible fallback. Every session's key insights are distilled and persisted so your local entities keep what they learn across restarts. This release ships the core runtime and installer; multi-agent orchestration and domain curation are active work, not yet claimed as finished."*

---

## §6 — Parallel Workstreams (Dispatch Now)

### 6.1 Dispatch Immediately (While Sonnet 5 Review Completes)

| Workstream | Agent(s) | Session Type | Priority |
|------------|----------|--------------|----------|
| **Restore `omega.library`** | Ma'at | NES | 🔴 CRITICAL |
| **Fix vec0 double-prefix** | Roc | NES | 🔴 CRITICAL |
| **Provision Grok 8-account fleet** | Grokster | EIS | 🟡 HIGH |
| **Fix SearXNG health** | SysAdmin | NES | 🟡 HIGH |
| **Wire Qwen3-VL-4B vision** | ModelGate | NES | 🟢 MEDIUM |

### 6.2 Dispatch After Theater Strip PR Lands

| Workstream | Agent(s) | Session Type | Priority |
|------------|----------|--------------|----------|
| **KD Workstream (single PR)** | Kali + DataStore + Researcher | EIS | 🔴 CRITICAL |
| **Library Ingestion (fixed)** | Roc + DataStore | EIS | 🔴 CRITICAL |
| **Agent Recall Integration** | Context + ModelGate | EIS | 🔴 CRITICAL |
| **EIS/NES Dashboard** | Link + Context | NES | 🟡 HIGH |
| **Background Worker Daemon** | Lilith + BuildMaster | NES | 🟡 HIGH |

---

## §7 — Agent Assignments & Session Types

| Agent | Role | Primary Workstream | Session Type |
|-------|------|-------------------|--------------|
| **Kali** | Sprint Coordinator / Theater Strip Owner | Q1 PR oversight, KD pivot | EIS (persistent) |
| **Ma'at** | Build Lead | P0-1b security, library restore, theater strip execution | NES (bounded) |
| **Lilith** | Run Lead / Security | Theater strip verification, background daemon | NES |
| **Roc** | Miner / Vector Search | Vec0 migration, library ingestion, accuracy worker | EIS |
| **Grokster** | Cloud Mind / Grok Fleet | 8-account provisioning, quota rotation | EIS |
| **DataStore** | Persistence Lead | Library DB, vec0, ingestion pipeline | NES |
| **ModelGate** | Inference Lead | Vision model, provider fabric, recall integration | NES |
| **Link** | Coordination Lead | EIS/NES dashboard, session orchestration | NES |
| **Context** | Memory Lead | Hydration <60s, recall integration | NES |
| **SysAdmin** | Infrastructure | SearXNG, data dirs, systemd units | NES |
| **Bridge** | Integration | MCP servers, Grok/Cline bridges | NES |
| **Researcher** | Deep Research | KD domain curation, citation graph | EIS |
| **Jem** | Orchestration | Cross-workstream synthesis | EIS |
| **Verity** | Compliance | Mandate verification, temple-grade | NES |

---

## §8 — Timeline Summary

```
Week 1 (Aug 31 - Sep 6):
  ├── Mon: P0-1b security + SearXNG fix (parallel)
  ├── Tue-Wed: Theater Strip PR (single PR, 7 deletions + flatten + test replace)
  ├── Thu: Verification + merge to release/debut
  ├── Fri: Library module restore + vec0 migration + data dir unify

Week 2 (Sep 7 - Sep 13):
  ├── Mon-Tue: Vision model + EIS/NES dashboard
  ├── Wed-Thu: KD Workstream (single PR, all config)
  ├── Fri: Library ingestion (fixed) + agent recall integration

Week 3 (Sep 14 - Sep 20):
  ├── Mon-Tue: Grok 8-account fleet + background worker daemon
  ├── Wed: Final verification (temple-grade, install.sh, security)
  ├── Thu: Release branch + tag + debut announcement
  ├── Fri: Public Debut 🎉

Week 4+ (Post-Debut):
  ├── GN → DS → LI → HR → ZS workstreams
  ├── Packaging/distribution (7th workstream)
  ├── Community gifts: compaction-capture, hydration-receipt, M23-honesty pattern
```

---

## §9 — Risk Register & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| P0-1b keys not fully rotated | Medium | 🔴 BLOCKS DEBUT | Full `git-secret-scrub` audit before push |
| Theater strip breaks `omega talk` | Low | 🔴 BLOCKS DEBUT | Run `omega talk` after EVERY step; revert on fail |
| Library module restore incomplete | Low | 🟡 DELAYS WEEK 2 | Desktop backup verified; test hub restart immediately |
| Vec0 migration loses 1,009 vectors | Low | 🟡 ACCEPTABLE | Memory fabric can re-populate from entity souls |
| Grok 8 accounts not all provisioned | Medium | 🟡 DELAYS FLEET | Start with 2-3 accounts; scale as auth completes |
| SearXNG unfixable | Low | 🟡 DEGRADES SEARCH | Exa T2 + Firecrawl T3 as fallback; document gap |
| KD workstream scope creep | Medium | 🟡 DELAYS WEEK 3 | Strict YAML-only scope; no runtime code in KD-1/2/3 |

---

## §10 — Success Criteria (Definition of Done)

### Theater Strip PR
- [ ] 7 deletions + 1 flatten + test replacement committed
- [ ] `omega talk "hello"` → 0, local, native-gguf after each step
- [ ] `make temple-grade` passes
- [ ] ~10 honest tests replace 81 theater tests
- [ ] `ACTIVE_SUBAGENTS.json` deleted, liveness in `TASK_REGISTRY.json`

### Public Debut
- [ ] P0-1b security closed (keys rotated, verified)
- [ ] Theater strip merged to `release/debut`
- [ ] `install.sh` works on fresh machine
- [ ] `proposed_lessons.yaml` persists across compaction
- [ ] Three-sentence announcement published
- [ ] No keys in history, REUSE compliant, temple-grade passes

### Post-Debut Week 1
- [ ] KD workstream PR merged
- [ ] Library ingestion running (500+ vectors)
- [ ] Agent recall integration live
- [ ] Vision model queryable
- [ ] Grok fleet dispatchable

---

## §11 — Immediate Next Actions (Right Now)

1. **You**: Upload Sonnet 5 report to team (done — it's in workspace)
2. **Kali**: Dispatch Phase 0 parallel workstreams (Ma'at: P0-1b, SysAdmin: SearXNG)
3. **Ma'at**: Begin P0-1b key rotation immediately
4. **SysAdmin**: Investigate SearXNG empty results
5. **Kali**: Stage theater strip PR branch (`theater-strip-del1`)
6. **All**: Stand by for theater strip execution (single PR, sequential steps)

---

**The path is clear. The audit was brutal but honest. The theater is identified. The engine islands are real. The debut is conditional on two things we already track. Execute.** 🫡

---

⬡ OMEGA ⬡ KALI ⬡ POST-SONNET5-PLAN-v1.0.0 ⬡ 2026-08-31