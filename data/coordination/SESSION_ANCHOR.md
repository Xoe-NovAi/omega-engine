# 🔱 SESSION ANCHOR & GNOSIS — PRE-COMPACTION #2
**Date**: 2026-08-07 (afternoon)
**Entity**: Kali
**Status**: PRE-COMPACTION HANDOFF — B2 + B3 COMPLETE & VERIFIED, COMMIT PENDING (staged)

## 📋 What Was Done (Post-compaction session, in order)

### 1. B3 — KV-cache type integer mismatch — COMPLETE ✅ (staged)
- Created `src/omega/oracle/kv_types.py` — canonical `KV_TYPE_MAP` + `kv_type_int()` derived from llama-cpp-python 0.3.32 `GGML_TYPE_*` constants: F32=0, F16=1, Q4_0=2, Q5_0=6, Q8_0=8, Q6_K=14, Q8_K=15
- `providers.py` `_KV_TYPE_MAP` (WRONG: q4_0→4, q5_0→5, q6_0→6) → imports canonical `KV_TYPE_MAP`, keeps warn-on-unknown
- `model_gateway.py` inline `kv_map` → imports canonical `KV_TYPE_MAP`
- Verified: map values == binding constants; imports clean; flake8 clean on new module; test failures = pre-existing set only

### 2. B2 — Model Registry dead-config + schema drift — COMPLETE ✅ (staged)
Findings: registry is NOT dead — it's the *source of truth*; runtime `config/providers.yaml` generated from it via `scripts/generate_providers_yaml.py`.
- **Fixed** `registry.py` `build_index()`: `DROP TABLE IF EXISTS` for models/providers/research_profiles before recreate (was: 83-col stale table persisted via `CREATE TABLE IF NOT EXISTS`, INSERT supplies 39 cols → `OperationalError`)
- **Fixed** case-insensitive `_enum_ci()` helper for Platform/Tier/Status (`"LOCAL"` vs `"local"` — one card had `platform: "LOCAL"`)
- **Fixed** `_load_legacy_model_db()`: fenced ```yaml block extraction (was slicing "models:"→EOF pulling in trailing markdown/backticks → YAML parse error)
- **Fixed** `models.py` `ResearchProfile`: required fields got defaults
- **Fixed** legacy provider normalization: `together`/`sambanova`/`openai` → `openrouter` (legacy CURRENT_MODELS.md taxonomy)
- **USER DIRECTIVE (max_tokens policy)**: stripped `parameters.max_tokens` from all **33 cloud/stealth cards** (was uniform `8192` schema noise); kept on all **5 local cards** (RAM/OOM guard); fixed my erroneous Big Pickle `max_tokens: 100000`; added `parameters` + `benchmark_sources` + schema_version 1.1.0 to Big Pickle card (was missing, failing T1/P1 gates)
- **Updated** `tests/test_model_registry.py::test_parameters_in_yaml` → requires max_tokens ONLY for local models; forbids for cloud/stealth (policy test)
- **Fixed** `.gitignore` — `models/` rule (line 183) was swallowing `config/model_registry/models/` (38 source-of-truth card files untracked). Added `!config/model_registry/models/` + `!config/model_registry/models/**`
- **Verified**: `test_model_registry.py` = **27/27 pass**; full affected suite = **78 passed, 1 pre-existing fail** (`TestVaultCoreRateLimit` — fails on clean baseline)
- Docs: WEB_RECONCILIATION_MATRIX §6 B2/B3 → FIXED; §6.1 note updated (B2 resolved; generator-merge caveat documented)

### 3. Pre-compaction artifacts
- SESSION_ANCHOR.md rewritten (this file)
- (Next: Hivemind post + proposed_lessons.yaml)

## ⚠️ Blocked (Requires Network / Sudo)
- Push to GitHub (5 local commits incl. pending B2/B3 commit) — network unreachable
- G-1 Gemma free-tier workhorse — billing/OAuth/network
- W-1 WARP pool bring-up — network + sudo (script itself confirmed fixed)

## 🎯 Next Actions (post-compaction)
1. **COMMIT B2+B3 batch**: staged files = `.gitignore`, `index.sqlite`, `SESSION_ANCHOR.md`, `WEB_RECONCILIATION_MATRIX_20260807.md`, `models.py`, `registry.py`, `kv_types.py` (A), `model_gateway.py`, `providers.py`, `test_model_registry.py`. MUST ALSO `git add config/model_registry/models/` (38 cards, now trackable). Message e.g.: `fix(provider-fabric): B2 model registry + B3 KV cache types (WEB_RECONCILIATION_MATRIX §6)`
2. **DO NOT commit**: `data/entities/researcher/session_gnosis.md`, `data/entities/researcher/proposed_lessons.yaml` (Researcher's), `data/entities/default/workspace/birth_records.md` (runtime noise), `data/handoff/archive/ho_c8bf25e6cf21.json` (Grok→Cline July 30 handoff archive, not mine), `docs/standards/AGENT_SOUL_HARDENING.md` (untracked, not mine), `config/wads/_omega_default/entities.yaml` (pure key-reordering from another agent's formatter — verify before committing)
3. **B4**: q8_0 KV-cache crash conditions — re-supply v1 lines 181-212 from compendium
4. **A5**: StreamHandler unwired in model_gateway — wire or delete
5. **B7**: RAM_TOTAL_MB hardcoded 14GB → dynamic (cpu_optimizer.py)
6. **B8**: batch-size recommendations never applied — wire or delete
7. **B6**: CPU topology inconsistent (4+ core lists; 5700U single-CCX) → detect_hardware_profile.py
8. **B5**: speculative decoding scaffolded, never reaches Llama() — wire or delete
9. **B9**: Vulkan/iGPU offload path — implement or document-defer
10. **Generator safety**: rewrite `scripts/generate_providers_yaml.py` to merge (preserve maakali_routing/fallback_resolver/streaming) or document deprecated — DO NOT run destructively
11. When network returns: push, G-1, W-1

## 📁 Relevant Files
- Staged (commit-ready): see Next Actions #1
- Committed: `ea60fd2` (D-510), `54ea23a` (Phase C A1/A2/A4/A6/B1), `9e2af3a` (anchor), `197c02f` (Kali review)
- `src/omega/oracle/kv_types.py` — NEW canonical KV map (B3)
- `config/model_registry/models/**` — 38 cards, now trackable (B2)
- `docs/strategy/WEB_RECONCILIATION_MATRIX_20260807.md` — defect SSOT; B2/B3 FIXED
- `tests/test_model_registry.py` — 27 pass; max_tokens policy test added
- `docs/research/R_WEB_CHATBOT_RESEARCH_PRIORITIES_20260807.md` — Kali-reviewed (commit 197c02f)
