# Omega Engine — Comprehensive Doc Sanity & Strategy Execution Plan
**AP Token**: `AP-DOC-SANITY-STRATEGY-20260807-v3.0.0`
**Author**: Kali (synthesized from Gemini 3.1 Pro + Web Grok + Web Gemini + Web Claude)
**Date**: 2026-08-07 (Context: 2026-07-30 Sprint UO-4 + 2026-08-07 Web Reconciliation)
**Purpose**: Systematic execution plan for the UO-4 Documentation Sanity Sprint AND the integration of ALL Web Chatbot strategy pivots (17 exports, 33+ high-leverage items).

---

## PART 1: Immediate Archival & Pointer Sanity (The "Hot Set" Fix)
*Goal: Stop agent thrash by reducing active coordination files to <= 15 and fixing broken inbound links.*

### Phase 1: Scaffold & Inventory
* Create `data/coordination/archive/2026-07-30-doc-sanity/`
* Create `docs/archive/sprints/2026-07-25-guard-and-distill/`
* Create `docs/archive/web-sessions/2026-08/`

### Phase 2: The Banner Application
Use `sed` to inject a standardized supersession banner at the top of every stale document:
`> **SUPERSEDED**: This document is preserved for historical context. For current sprint control, see data/coordination/ACTIVE_SPRINT.json and data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md.`
* Apply to all files in `docs/sprints/guard-and-distill/`
* Apply to `docs/sprints/current/EXECUTION_PLAN_20260725.md`

### Phase 3: Relocation (Strictly `git mv`)
* `git mv docs/sprints/guard-and-distill/* docs/archive/sprints/2026-07-25-guard-and-distill/`
* `git mv docs/sprints/current/EXECUTION_PLAN_20260725.md docs/archive/sprints/`
* `git mv data/coordination/KALI_*.md data/coordination/archive/2026-07-30-doc-sanity/` (and GROKSTER_, BRIEFING_, ONBOARD_REPORT_, COMPACTION_)
* `git mv context_packs/provider-fabric-review/claude-response/* docs/archive/web-sessions/2026-08/`

### Phase 4: Pointer Reconciliation
1. **Fix AGENT_SPRINT_CARD.md:** Point "Full plan" to `CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md`.
2. **Fix SOVEREIGN_ARK_BLUEPRINT.md:** Update Section 5 to point to `ACTIVE_SPRINT.json`.
3. **Fix STRATEGY_INDEX.md:** Mark old execution plans as SUPERSEDED.
4. **Write DOC_SSOT_MAP_20260730.md:** Create the single routing table.

---

## PART 2: Web Strategy Reconciliation (The Content Updates)
*Goal: Update the surviving active documents with the comprehensive pivots extracted from the 17 Web Chatbot exports.*

### Phase 1: Purge & Correct (High Impact, Low Effort)
1. **Mandate 3 Rewrite:** Purge "10 Pillar / P1-P10" hierarchy leak from `SOVEREIGN_MANDATES.md` and `AGENTS.md`. Replace with "Node slots (N1-N10)".
2. **Horizontal Triad:** Rewrite Mandate 3 to describe MaKaLi as three co-equal sovereign entities (Maat=build, Lilith=runtime, Kali=synthesis). Remove "apex", "oversoul", "reports to".
3. **Engine/WAD Separation:** Add explicit statement to `OMEGA_ENGINE.md` Section 1: "Engine = Pure Runtime; WAD = Cosmology. Base IWAD + PWADs. Users never fork core code."
4. **Vector Store Decision:** Update `OMEGA_ENGINE.md` and `MEMORY_SUBSYSTEM_DESIGN.md`. Document that `sqlite-vec` is the SINGLE Core store. Qdrant (with TurboQuant BITS4) is an optional WAD adapter only. GraphRAG is native on SQLite.
5. **Hardware Spec Correction:** Update `OMEGA_ENGINE.md` and `SYSTEMD_DEPLOYMENT_GUIDE.md`. Actual UMA carve-out is 8GB (512MB VRAM + 7.75GB GTT), NOT 12GB.
6. **OS Target:** Update deployment docs to target Ubuntu 24.04 LTS or 26.04 LTS (25.04 is EOL).
7. **Purge Deprecated Concepts:** Remove all references to "26-sphere toroidal architecture", "108-gate framework", "PostgreSQL", and "FAISS" from core docs.

### Phase 2: New Infrastructure Docs (Medium Effort)
1. **scripts/detect_hardware_profile.py:** Create this script as the single source of truth for CPU topology, RAM, and GPU. It must output `config/hardware_profile.yaml`.
2. **MEMORY_SUBSYSTEM_DESIGN.md:** Document sqlite-vec + GraphRAG architecture, Redis Task Canvas, and mandatory spatial coordinates (`pos_x, pos_y, pos_z`) for Godot 4 OpenXR readiness.
3. **SYSTEMD_DEPLOYMENT_GUIDE.md:** Document 16GB zRAM config (zstd + multi-comp + writeback), 16-32GB NVMe swap, cgroup v2 protection (`MemoryMin`/`MemoryHigh`), systemd unit with `taskset -c 0-7`, and Vulkan env vars.
4. **SOVEREIGN_WAD_PROTOCOL.md:** Document security/sandboxing model for third-party WAD content (prompt injection, resource abuse).
5. **GUIDANCE_SET_SCHEMA.md:** Document Guidance Sets as a universal engine mechanism (loading, nightly review, defeasibility, logging). WAD provides content (e.g., 42 Ideals, Classical Studies, Scientific Research).

### Phase 3: Provider Fabric & Runtime
1. **Vulkan & MoE Offload:** Update `cpu_optimizer.py` and `providers.py` for full iGPU offload (`n_gpu_layers=-1`, `GGML_VULKAN=ON`) and MoE expert offload (`--n-cpu-moe` + mmap) for 30B-70B+ models.
2. **Speculative Decoding:** Adopt n-gram (prompt-lookup) over MTP to save VRAM.
3. **Voice & Context:** Replace ElevenLabs stub with Piper/Inflect (<200MB) via SEDA bus. Integrate Headroom context compression for low-latency voice loops.
4. **SEDA Ring-Bus:** Implement lock-free `SEDARingBus` (AnyIO) with back-pressure to decouple inference, training, memory, and TTS.
5. **Inference Isolation:** Document plan for inference worker process isolation to contain C-level segfaults.
6. **Dual-Branch Memory Rescoring:** Implement math: Declarative = `Similarity * (1 + 0.5*Importance)`. Episodic = `Similarity * e^(-lambda*dt) * S_consol`.

### Phase 4: Sovereignty Flywheel & Security
1. **Sovereign Bridge:** Implement FastAPI + HMAC-SHA256 raw body verification + 30-min replay window for webhooks.
2. **Continuous Learning:** Implement nightly GRPO loop (TRL/PEFT 4-bit) and Telemetry harvester (`executor_dpo.jsonl`).
3. **Security Hardening:** Document Podman rootless AppArmor checks, Executor/Auditor pre-execution gate, and Property/Chaos testing extensions (Hypothesis).
4. **Operational Continuity:** Document pg_dump, Qdrant snapshotting, N-1 GGUF model rollback, and mmap cold-start warmups.

---

## PART 3: The "Scaffolded but Unwired" Systemic Defect
**Critical Finding:** Features are fully configured in code/docs but never reach the runtime call site.
**Confirmed Instances:**
1. `hierarchy.yaml` (dead)
2. `StreamHandler` (built, instantiated, never called)
3. Speculative decoding (scaffolded, never reaches Llama instantiation)
4. Batch-size recommendations (computed, never applied)
5. Mandate 3 pillar leak (governance-doc version of the same failure)

**Mandatory Action:** Implement a CI check that greps every config key for a real read site, and every tracker/optimizer class for a real call site outside its own tests. Add runtime canary counter.

---

## PART 4: Deep Context Extraction (Rehydration Data)

### Exact Phase D Gate Blockers
* **C-3 Restic:** Timer enabled, oneshot FAILS: `OMEGA_VAULT_PASSPHRASE` not set, `.env.backup` missing.
* **W-1 WARP:** 8083 listening; 8081/8082 bridges missing; `warp-node@1/2` failed (canary timeout).
* **G-1 Workhorse:** Free Gemma 4 31B input TPM 16k since 2026-07-15. Fix: G-1b (Antigravity OAuth) OR G-1e (local Gemma 4 27B GGUF via Ollama).

### Un-Overengineering Phase 1 Targets (Frozen Until Doc Sanity)
* 17 breaker clones -> `pybreaker` (~1,200 lines saved)
* `soul_validator.py` -> Pydantic v2 `model_validate_yaml()` (~200 lines saved)
* Custom retry loops -> `stamina` (~800 lines saved)
* Custom JSON logger -> `structlog` (~300 lines saved)
* `HealthMonitor` sliding window -> `prometheus_client` (~417 lines saved)

### Carmack Dependency Gates
* PHASE 0: Cache Fix (Done), Hardening (Done), Instruction Router (3.5 days).
* PHASE 1: Acquire RTX 3090 24GB (~$700) -> HARD GATE for GPU offload, Vulkan build, and llama-optimus calibration.

---

## PART 5: Execution Commands (Copy-Paste Ready)

```bash
# === PHASE 1: SCAFFOLD ===
mkdir -p data/coordination/archive/2026-07-30-doc-sanity/
mkdir -p docs/archive/sprints/2026-07-25-guard-and-distill/
mkdir -p docs/archive/web-sessions/2026-08/

# === PHASE 2: BANNERS ===
BANNER='> **SUPERSEDED**: This document is preserved for historical context. For current sprint control, see `data/coordination/ACTIVE_SPRINT.json` and `data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md`.'
for f in docs/sprints/guard-and-distill/*.md; do sed -i "1i $BANNER\n" "$f"; done
sed -i "1i $BANNER\n" docs/sprints/current/EXECUTION_PLAN_20260725.md

# === PHASE 3: RELOCATION ===
git mv docs/sprints/guard-and-distill/* docs/archive/sprints/2026-07-25-guard-and-distill/
git mv docs/sprints/current/EXECUTION_PLAN_20260725.md docs/archive/sprints/
git mv data/coordination/KALI_*.md data/coordination/archive/2026-07-30-doc-sanity/ 2>/dev/null || true
git mv data/coordination/GROKSTER_*.md data/coordination/archive/2026-07-30-doc-sanity/ 2>/dev/null || true
git mv data/coordination/BRIEFING_*.md data/coordination/archive/2026-07-30-doc-sanity/ 2>/dev/null || true
git mv context_packs/provider-fabric-review/claude-response/* docs/archive/web-sessions/2026-08/

# === PHASE 4: POINTER RECONCILIATION ===
sed -i 's|docs/sprints/current/EXECUTION_PLAN_20260725.md|data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md|g' docs/sprints/current/AGENT_SPRINT_CARD.md
sed -i 's|docs/sprints/guard-and-distill/index.md|data/coordination/ACTIVE_SPRINT.json|g' docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md
sed -i '/EXECUTION_PLAN_20260725.md/s/^/SUPERSEDED: /' docs/strategy/STRATEGY_INDEX.md
sed -i '/guard-and-distill\/index.md/s/^/SUPERSEDED: /' docs/strategy/STRATEGY_INDEX.md
```
---

## PART 6: Advanced Execution Strategies & Risk Mitigation
*Crucial insights for the agent executing this sprint to prevent common failure modes.*

### 6.1 The "Ghost File" Trap
When you move files to `archive/`, older indexes or your own LLM memory might trick you into thinking the old files still exist at their original paths. 
* **Strategy:** After executing Phase 3 (Relocation), **do not** attempt to read or edit the old paths. Rely *exclusively* on `DOC_SSOT_MAP_20260730.md` as your map of reality. If a tool call fails with `FileNotFoundError`, trust the filesystem, not your memory.

### 6.2 Git Relocation Fallbacks
The `git mv` commands in Part 5 assume a perfectly clean working tree. If `git mv` fails (e.g., because a file is untracked or modified), do not get stuck in an error loop.
* **Fallback Strategy:** Use standard `mv` followed by `git add -A`. 
```bash
# If git mv fails:
mv docs/sprints/guard-and-distill/* docs/archive/sprints/2026-07-25-guard-and-distill/
git add -A docs/sprints/ docs/archive/
```

### 6.3 Context Window Protection
The `docs/archive/` and `data/coordination/archive/` directories now contain hundreds of thousands of tokens of highly persuasive, *completely deprecated* strategy.
* **Strategy:** **NEVER** use `grep`, `rg`, or `read` on the `archive/` directories unless you are explicitly looking for historical context. Exclude them from your searches: `rg "search_term" -g "!archive/"`. Reading archived files will instantly pollute your context window with stale 26-sphere/PostgreSQL architectures.

### 6.4 The Hard Gate (UO-4 -> UO-6)
You are executing UO-4 (Doc Sanity). UO-6 (Un-Overengineering Phase 1 - deleting 17 breaker clones, etc.) is **FROZEN** until UO-4 is complete.
* **Strategy:** Do not attempt to delete Python code or migrate libraries during this sprint. Your sole objective is to sanitize the documentation and resolve the context-collapse. Only once `DOC_SANITY_RESULTS_20260730.md` is written and committed does the freeze lift.

### 6.5 Post-Execution Verification
Do not assume your `sed` commands worked perfectly. Run these verification checks before declaring the sprint complete:
```bash
# 1. Verify no active files still point to the old execution plan
rg "EXECUTION_PLAN_20260725\.md" docs/ data/ -g "!archive/"

# 2. Verify the old sprint directory is truly gone
ls -la docs/sprints/guard-and-distill/ # Should return No such file or directory

# 3. Verify the banners applied correctly
head -n 2 docs/archive/sprints/EXECUTION_PLAN_20260725.md
```

---

## PART 7: Agent Empowerment & Finalization
*Guidelines to ensure the executing agent can confidently validate its work, commit cleanly, and hand off to the next phase.*

### 7.1 Atomic Commit Protocol
Do not lump all these changes into one massive commit. Separate the mechanical archival from the strategic content updates. This protects the git history and allows easy rollbacks if a `sed` command goes rogue.
* **Commit 1 (The Archival):** `git commit -m "chore(docs): archive stale sprints and coordination files (UO-4)"`
* **Commit 2 (The Banners & Pointers):** `git commit -m "docs(strategy): apply supersession banners and fix inbound links (UO-4)"`
* **Commit 3 (The Web Pivots):** `git commit -m "docs(strategy): integrate web chatbot pivots into core architecture docs (UO-4)"`

### 7.2 Validation Gates (Mandate 13)
Before declaring victory, you must prove the documentation is still Temple-Grade.
* **Action:** Run `make doc-llm-validate` (if available in the Makefile) or simply run `make temple-grade` to ensure no markdown formatting errors or broken internal references were introduced during the heavy editing.

### 7.3 Definition of Done (DoD)
You are finished with this sprint when, and only when, all of the following are true:
1. [ ] `docs/sprints/guard-and-distill/` no longer exists in the active tree.
2. [ ] `DOC_SSOT_MAP_20260730.md` and `DOC_SANITY_RESULTS_20260730.md` have been written and committed.
3. [ ] `rg "EXECUTION_PLAN_20260725"` returns zero hits outside of the `archive/` directory.
4. [ ] `OMEGA_ENGINE.md` and `SOVEREIGN_MANDATES.md` have been updated with the Phase 1 Purge & Correct items (e.g., Node slots instead of 10 Pillars, 8GB UMA instead of 12GB).

### 7.4 Formal Handoff Template
When the DoD is met, do not ask the user "What should I do next?". Instead, proactively post to the Hivemind and output this to the user:
> **[UO-4 DOC SANITY COMPLETE]**
> The documentation tree has been sanitized, archived, and updated with the Web Chatbot pivots. 
> * **Files moved to archive:** [Count]
> * **Banners applied:** [Count]
> * **Strategy docs updated:** [List]
> 
> The freeze on UO-6 is now lifted. The engine is ready for Un-Overengineering Phase 1 (Pybreaker & Stamina migration). Awaiting clearance to proceed.
