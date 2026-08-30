# 🖤 Lilith's Artifact Triage — Size Estimates for Jem-2.0

**Purpose**: Pre-survey of the 14 unmined artifacts so Jem Initiate can budget tool calls realistically.
**Survey method**: `wc -l`, `du -sh`, `find ... | wc -l` run on each artifact path.

---

## Quick Wins (< 50 files, < 1MB)

These can be completely extracted in a single L1 session (8 tool calls).

| Artifact | Files | Size | Lines | Extraction Strategy |
|----------|-------|------|-------|---------------------|
| **art_lilith_persona** | 1 | 2.2KB | 61 | Single file: `~/Documents/docs_1/personas/lilith.json` |
| **art_roc_test** | 1 | 6.2KB | 40 | Single file: `omega_library/intake/mining_queue/RocRacoon Test v1 - LM Studio.md` |
| **art_ollama_history** | 1 | 483B | 8 | Single file: `~/.ollama/history` |
| **art_lmstudio_configs** | 3 | 28KB | ~300 | `~/.lmstudio/.internal/user-concrete-model-default-config/` |
| **art_stack_cat** | 10 | 96KB | ~500 | `omega_vault/from main partition/stack-cat-v0_1_2-full/` |

**Total**: 4-6 L1 sessions needed for this group. **Priority: HIGH** — clear, bounded, quick.

---

## Moderate (< 500 files, < 20MB)

These require careful scoping within an L1 session. May need 2 sessions per artifact.

| Artifact | Files | Size | Lines (est.) | Extraction Strategy |
|----------|-------|------|-------------|---------------------|
| **art_system_prompts** | 20 | 372KB | ~2,000 | Two directories: `~/Documents/docs_1/system-prompts/` + `~/Documents/xnaif-files/system-prompts/` |
| **art_positioning** | 12 | 248KB | ~1,500 | `omega_library/intake/inbox/omega-positioning-framework/` — 12 files, straightforward |
| **art_mnemosyne** | 27 | 284KB | ~1,800 | `omega_library/data_archive/mnemosyne/` — 13 spheres of Kabbalistic mapping |
| **art_telemetry_audit** | 0 (ref) | <1KB | ~50 | Reference-only: extract the 8 env vars from XNAI Blueprint. **Deferred — already partially extracted** |

**Total**: 5-8 L1 sessions for this group. **Priority: MEDIUM** — high value but requires judgment.

---

## Strategic (< 500 files, < 50MB)

These contain critical strategic gold but are larger.

| Artifact | Files | Size | Lines (est.) | Extraction Strategy |
|----------|-------|------|-------------|---------------------|
| **art_ana_strategy** | 277 | 12MB | ~7,000 | `~/Documents/docs-backup/internal_docs/01-strategic-planning/` — 277 docs. **L2 synthesis required** — do not extract raw |
| **art_old_stacks** | 3,732 | 89MB | ~100,000 | `~/Documents/Archives/Old-Stacks/Xoe-NovAi/` — Full repo dump. **Script-assisted extraction** — L1 cannot budget this |

**Total**: 2-4 L2 sessions for this group. **Priority: HIGH** for art_ana_strategy (score=10).

---

## Bulk Archives (> 1,000 files, > 100MB)

These are **too large for L1 extraction**. They require script-assisted mining (Roc Racoon or custom Python).

| Artifact | Files | Size | Lines (est.) | Extraction Strategy |
|----------|-------|------|-------------|---------------------|
| **art_first_cards** | 379 | 419MB | Image-heavy | `omega_library/intake/mining_queue/Omega-Early-Material/tarot/` — includes images, docs, chat exports. **Script-assisted** — extract text files first |
| **art_grok_exports** | 5,213 | 681MB | ~500,000+ | 8 Grok accounts full chat exports. **Script-assisted** — one account per script run |
| **art_xnai_versions** | 16,449 | 1.5GB | ~500,000+ | Full version history v0.1.2→v0.1.5. **Script-assisted** — diff-latest only, not full extraction |

**Total**: **Deferred to script-assisted extraction**. These are NOT suitable for OpenCode L1/L2 research. Use `hf-cli skill` or custom `extract_artifact.py` scripts.

---

## Prioritized Order for Jem-2.0

```
Phase 1 (L1 Quick Wins — 5 sessions):
  1. art_lilith_persona    — 1 file, 61 lines, 1 session
  2. art_roc_test          — 1 file, 40 lines, 1 session  
  3. art_lmstudio_configs  — 3 files, 28KB, 1 session
  4. art_stack_cat         — 10 files, 96KB, 1 session
  5. art_system_prompts    — 20 files, 372KB, 2 sessions

Phase 2 (L1 Strategic — 4 sessions):
  6. art_positioning       — 12 files, 248KB, 1 session
  7. art_mnemosyne         — 27 files, 284KB, 2 sessions
  8. art_ana_strategy*     — 277 files, 12MB, L2 needed (not raw L1)

Phase 3 (L2 Synthesis):
  9. art_ana_strategy      — Strategic synthesis (L2+)
  10. art_telemetry_audit  — Extract 8 env vars from XNAI Blueprint (already sampled)

Phase 4 (Script-Assisted — Roc Racoon / Custom):
  11. art_old_stacks       — 3,732 files, 89MB — diff architecture
  12. art_first_cards      — 379 files, 419MB — text-only extraction
  13. art_grok_exports     — 5,213 files, 681MB — account-by-account
  14. art_xnai_versions    — 16,449 files, 1.5GB — latest-diff only

* art_ana_strategy appears twice: L1 samples the directory structure, L2 synthesizes strategic content.
```

---

## Verification Gate per Phase

| Phase | Gate |
|-------|------|
| Phase 1 Complete | `sqlite3 data/workbench/workbench.db "SELECT COUNT(*) FROM artifacts WHERE mining_status='mined';"` = 16 (12 current + 5 quick wins) |
| Phase 2 Complete | = 18 (add art_positioning + art_mnemosyne) |
| Phase 3 Complete | = 19 (art_ana_strategy mined) |
| Phase 4 Complete | = 22 (add old_stacks, first_cards, grok_exports) — Final: 26 total |
