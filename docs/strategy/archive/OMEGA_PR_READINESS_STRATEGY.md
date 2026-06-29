# 🔱 Omega Engine — PR Readiness & Multi-Provider Orchestration Strategy

**AP Token**: `AP-PR-READINESS-v2.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_strategic ⬡ STRATEGY
**Status**: ACTIVE | **Last Updated**: 2026-05-25 | **Supersedes**: v1.0.0

---

## 🎯 Phase E: PR Readiness & Community Presentation — ✅ Completed (2026-05-25)

The Omega Engine is now **infrastructurally solid and PR-ready** — permission war won, MCP servers consolidated, 259/259 tests green, and the **Engine-Stack Firewall fully enforced**.

To achieve the **fastest time to a viable product PR**, we have pivoted to a **Cloud-First** inference strategy (Decision 56). By prioritizing OpenRouter (priority 0) with automatic model translation, we bypass local compilation blockers (like `llama-cpp-python` CPU builds) while keeping Ollama and LM Studio as robust local fallbacks.

This document outlines the completed work and the final, streamlined path to shipping the PR.

---

## §1 Completed Workstreams (Sprint 1)

All core PR gate requirements have been successfully implemented and verified:

| # | Workstream | Status | Deliverables Completed |
|---|-----------|--------|------------------------|
| **E1** | PR Surface Layer | ✅ COMPLETE | - **README.md**: 3-command quickstart, provider setup table, architecture overview, system requirements, v0.5.0-alpha status table.<br>- **CI/CD** (`.github/workflows/test.yml`): Python 3.12 + 3.13 matrix, `pip install -e .` + test run + flake8 lint.<br>- **.gitignore**: Added `.firecrawl/`, stale artifacts, test debris — untracked files reduced from 215→11. |
| **E2** | OpenCode Modes Consolidation | ✅ COMPLETE | - Hardened all 13 OpenCode agent/mode files.<br>- Updated global and project `opencode.json` to point to `MASTER_LEDGER.md` + `OMEGA_IWAD_ARCHITECTURE.md`. |
| **E3** | Backend Integration | ✅ COMPLETE | - **providers.yaml**: OpenRouter priority 0, Ollama priority 2, LM Studio priority 3, native-gguf priority 98, Mock priority 99.<br>- **Model Translation**: Implemented `_resolve_model_name` in `ModelGateway` to map local GGUF names (e.g., `qwen3-1.7b-q6_k`) to OpenRouter model IDs (e.g., `google/gemma-4-31b-it`).<br>- **MockProvider**: Returns helpful setup instructions instead of debug text. |
| **E4** | Bug Fixes & Hardening | ✅ COMPLETE | - Fixed circular dependencies in `GnosisProxy`.<br>- Fixed `RemoteProvider.generate()` missing `await` on `is_available()`.<br>- Fixed `TriageRouter._load_soul()` to use YAML parser instead of JSON.<br>- Fixed `_display_response()` to handle integer pillars via `str()` conversion.<br>- Fixed all 10 Tech Role entity pillar values from `[1]` → `["1"]` across entities.yaml and all IWAD entity files. |

---

## §2 The Final Path to PR (Remaining Steps)

With the core technical work complete, the remaining steps are purely operational and presentation-focused:

### 1. OpenCode Custom Instructions Optimization (1h) - ✅ COMPLETE
- **Objective**: Reduce token overhead by ~40% by replacing the 12-file instruction list in `opencode.json` with a streamlined 4-file list.
- **Action**: `opencode.json` updated to include only: `SOVEREIGN_MANDATES.md`, `.opencode/MANIFEST.md`, `AGENTS.md`, `docs/gnosis/lattice/lattice_manifest.md`.

### 2. OpenCode Agents Consolidation (2h) - 🔄 IN PROGRESS
- **Objective**: Delete obsolete/experimental agent files to clean the `.opencode/agents/` directory.
- **Action**: Delete the 10 `researcher_*.md` files, `researcher-omnidroid.md`, `gnosis-analyst.md`, `sovereign-expert.md`, `crucible.md`, `scale.md`, and `key.md`. Keep only the core 6 agents (`overseer.md`, `builder.md`, `researcher.md`, `reviewer.md`, `tester.md`, `scribe.md`) and the new MaKaLi/Jem agents.

### 3. End-to-End Smoke Test & Recording (1h) - ✅ COMPLETE
- **Objective**: Verify the entire installation and execution flow on a clean environment.
- **Action**: `omega talk "hello"` executed successfully; output verified. Recording for PR description is pending.

---

## §3 Future Roadmap (Post-PR)

These strategic workstreams are deferred to v0.6.0 and beyond to ensure the immediate PR remains focused and shippable:

### E4 — Antigravity CLI (agy) Migration
- **Focus**: Integrate the new `agy` CLI as a high-priority cloud provider.
- **Challenge**: Manage aggressive quota caps (166-hour reset timer) and model persistence.
- **Strategy**: Default to Flash, reserve Opus for P0 tasks, implement circuit breakers when quota is low.

### E5 — 8× Web Claude Fleet Orchestration
- **Focus**: Deploy 8 parallel Web Claude accounts for deep code review and strategic alignment.
- **Strategy**: Use URL-based context over project sources (pointing to raw GitHub URLs) to bypass context limits and ensure fresh fetches.

### E6 — NotebookLM + Web Gemini Pipeline
- **Focus**: Sync `docs/research/` to Google Drive to enable NotebookLM synthesis (FAQs, study guides, audio overviews) and Web Gemini cross-referencing.

### E7 — Legacy Gnosis Mining
- **Focus**: Re-hydrate SESS-27 fossils, formalize the Individuation Protocol, and map the 10 Pillar Keepers to the "Facets" of the active entity.
