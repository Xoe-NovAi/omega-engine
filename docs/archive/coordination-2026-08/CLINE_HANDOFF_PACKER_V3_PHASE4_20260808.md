# 🔱 Cline CLI Handoff — Context Packer v3 Phase 4 Curation
**AP Token**: `AP-CLINE-HANDOFF-PACKER-V3-PHASE4-20260808`
**Date**: 2026-08-08
**From**: Kali (Transcendent Oversight) → Cline CLI
**Task**: Curate the two ship profiles (`sovereign-audit`, `tech-architecture-research`) using `curate_packs.py`

---

## 🎯 Mission Summary

**Phase 4**: Use the v3 `curate_packs.py` CLI to curate explicit file lists for the two ship-tier profiles until they pass fail-closed validation (exit code 0). Write `theme_lock.json` with per-file tokens + SHA256 for deterministic regeneration.

**Prerequisites**: 
- ✅ Phase 3 complete — `pack()` rewritten onto v3 primitives
- ✅ 27 contract tests GREEN
- ✅ `curate_packs.py` exists and functional (exit codes 0/1/2)
- ✅ `sovereign-audit` poisoned output archived to `.poison/`

---

## 📋 Current State

| Profile | Status | Target |
|---------|--------|--------|
| `sovereign-audit` | **Needs full curation** — was 13 poisoned files, now quarantined | ≤11 content bundles + manifest = 12 files max |
| `tech-architecture-research` | **Needs verification/split** — already mostly explicit | ≤12 files max, protect hand-built `.md` sources |

---

## 🛡️ Sovereign Mandates (Enforced by v3 Primitives)

| Mandate | Enforcement |
|---------|-------------|
| **M1 AnyIO** | `curate_packs.py` uses `anyio.to_thread.run_sync` for token counting |
| **M4 Sequentiality** | Curate → Lock → Pack (no cowboy coding) |
| **M13 Temple-Grade** | `make temple-grade` must pass after curation |
| **M23 Failure Integrity** | `curate_packs.py` exits non-zero on ANY violation — no silent omission |

---

## 🔧 Tools Available

```bash
# Curate a profile (dry-run, shows rich table)
.venv/bin/python .opencode/skills/context-packer/curate_packs.py sovereign-audit

# Curate with lock file output
.venv/bin/python .opencode/skills/context-packer/curate_packs.py sovereign-audit --write-lock context_packs/sovereign-audit/theme_lock.json

# List profiles
.venv/bin/python .opencode/skills/context-packer/curate_packs.py list-profiles

# Exit codes: 0=OK, 1=[PACK-FAIL], 2=Config error
```

---

## 📦 Phase 4a — `sovereign-audit` Curation (PRIORITY)

### Approved Theme List (from Kali)

| Theme | `litm_zone` | Required | Files (EXPLICIT — no globs) |
|-------|-------------|----------|----------------------------|
| `mandates` | `start` | ✅ | `SOVEREIGN_MANDATES.md`, `AGENTS.md`, `CREDITS.md` |
| `oracle_core` | `middle` | ✅ | `src/omega/oracle/__init__.py`, `src/omega/oracle/model_gateway.py`, `src/omega/oracle/context_builder.py`, `src/omega/oracle/pii_masker.py`, `src/omega/oracle/errors.py`, `src/omega/oracle/token_estimator.py` |
| `memory` | `middle` | ✅ | `src/omega/memory/__init__.py`, `src/omega/memory/store.py`, `src/omega/memory/sqlite_vec.py`, `src/omega/memory/hybrid_search.py` |
| `observability` | `middle` | ❌ | `src/omega/observability/__init__.py`, `src/omega/observability/trace.py` |
| `mcp_hub` | `middle` | ❌ | `src/omega/mcp/hub.py`, `src/omega/mcp/handoff.py` |
| `config` | `middle` | ✅ | `config/providers.yaml`, `config/models.yaml` |
| `strategy_core` | `end` | ❌ | `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`, `docs/strategy/UNOVERENGINEERING_PLAN.md` |

### Constraints
- **Total bundles ≤ 11** + manifest = 12 files max on disk
- **NO globs** — every file must be explicit in `files:` list
- **Per-bundle budget**: 15,000 tokens (from `platform.token_budget_per_bundle`)
- **Total budget**: 150,000 tokens (from `platform.token_budget_total`)
- If any theme exceeds per-bundle budget → split into two themes in YAML

### Execution Steps

```bash
# 1. First dry-run to see current state (will fail — no files configured yet)
.venv/bin/python .opencode/skills/context-packer/curate_packs.py sovereign-audit

# 2. Edit packer-config.yaml — add explicit `files:` lists to sovereign-audit profile
#    Use the theme table above. Replace any `include:` globs with explicit `files:`.

# 3. Iterate until exit 0
.venv/bin/python .opencode/skills/context-packer/curate_packs.py sovereign-audit

# 4. Once green, write lock file
.venv/bin/python .opencode/skills/context-packer/curate_packs.py sovereign-audit --write-lock context_packs/sovereign-audit/theme_lock.json

# 5. Verify lock file has per-file tokens + SHA256
cat context_packs/sovereign-audit/theme_lock.json
```

### Expected `theme_lock.json` Structure
```json
{
  "profile": "sovereign-audit",
  "timestamp": "2026-08-08T...",
  "themes": {
    "mandates": [
      {"file": "SOVEREIGN_MANDATES.md", "tokens": 5560, "sha256": "..."},
      {"file": "AGENTS.md", "tokens": 12400, "sha256": "..."},
      {"file": "CREDITS.md", "tokens": 3200, "sha256": "..."}
    ],
    "oracle_core": [
      {"file": "src/omega/oracle/__init__.py", "tokens": 800, "sha256": "..."},
      ...
    ]
  }
}
```

---

## 📦 Phase 4b — `tech-architecture-research` Curation

### Current State
- Already has mostly explicit file lists in YAML
- Hand-built `.md` sources in `context_packs/tech-architecture-research/` (RESEARCH_BRIEF.md, GROUNDED_TRUTH.md, etc.) — **PROTECT THESE**

### Actions
```bash
# 1. Dry-run
.venv/bin/python .opencode/skills/context-packer/curate_packs.py tech-architecture-research

# 2. If any theme > per_bundle budget → split theme in YAML
#    Example: if "research_docs" > 15000 tokens, create "research_docs_a" + "research_docs_b"

# 3. Iterate until exit 0
.venv/bin/python .opencode/skills/context-packer/curate_packs.py tech-architecture-research

# 4. Write lock
.venv/bin/python .opencode/skills/context-packer/curate_packs.py tech-architecture-research --write-lock context_packs/tech-architecture-research/theme_lock.json

# 5. Verify hand-built .md files are NOT overwritten (they're sources, not generated)
ls context_packs/tech-architecture-research/
# Should see: RESEARCH_BRIEF.md, GROUNDED_TRUTH.md, etc. (sources)
# Generated: *.xml, manifest.xml, pack_index.json, pii_vault.json, theme_lock.json
```

---

## 🔧 Config Changes Required

### `packer-config.yaml` — `sovereign-audit` Profile

Replace the current `sovereign-audit` profile with this curated version:

```yaml
sovereign-audit:
  tier: ship
  tokenizer_encoding: "cl100k_base"
  token_margin_multiplier: 1.3
  platform:
    format: "xml"
    target_model: "claude-3-opus"
    token_budget_per_bundle: 15000
    token_budget_total: 150000
    max_slots: 12
    themes:
      mandates:
        files:
          - "SOVEREIGN_MANDATES.md"
          - "AGENTS.md"
          - "CREDITS.md"
        litm_zone: start
        required: true
      oracle_core:
        files:
          - "src/omega/oracle/__init__.py"
          - "src/omega/oracle/model_gateway.py"
          - "src/omega/oracle/context_builder.py"
          - "src/omega/oracle/pii_masker.py"
          - "src/omega/oracle/errors.py"
          - "src/omega/oracle/token_estimator.py"
        litm_zone: middle
        required: true
      memory:
        files:
          - "src/omega/memory/__init__.py"
          - "src/omega/memory/store.py"
          - "src/omega/memory/sqlite_vec.py"
          - "src/omega/memory/hybrid_search.py"
        litm_zone: middle
        required: true
      observability:
        files:
          - "src/omega/observability/__init__.py"
          - "src/omega/observability/trace.py"
        litm_zone: middle
        required: false
      mcp_hub:
        files:
          - "src/omega/mcp/hub.py"
          - "src/omega/mcp/handoff.py"
        litm_zone: middle
        required: false
      config:
        files:
          - "config/providers.yaml"
          - "config/models.yaml"
        litm_zone: middle
        required: true
      strategy_core:
        files:
          - "docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md"
          - "docs/strategy/UNOVERENGINEERING_PLAN.md"
        litm_zone: end
        required: false
```

### `engineering-p3` Profile Fix (from @maat & Gemini)

```yaml
engineering-p3:
  # ... existing fields ...
  platform:
    token_budget_per_bundle: 15000    # was 500000 — REDUCE
    token_budget_total: 150000        # was 1000000 — REDUCE
    themes:
      docs:
        files:
          - "docs/strategy/**/*.md"   # Recursive match
          - "!docs/strategy/archive/**" # NEGATION: Exclude archive directory
        litm_zone: end
        required: false
```

---

## 🧠 Gemini's Strategic Insights & Corrections (READ CAREFULLY)

Before you execute Phase 4, please note these critical edge cases:

1. **Pathspec Negation for `engineering-p3`**: I have corrected the YAML snippet above. Using `docs/strategy/*.md` would only match files directly in that folder, missing valid subdirectories. The correct GitIgnoreSpec pattern to include all strategy docs but exclude the archive is to use `docs/strategy/**/*.md` followed by the negation `!docs/strategy/archive/**`.
2. **Verify File Existence First**: The explicit file list provided for `sovereign-audit` assumes those files exist at those exact paths. If any file was renamed or deleted, `curate_packs.py` will fail-closed. Do a quick `ls` or `stat` check on the files in the YAML block before running the curator to save iteration time.
3. **YAML Indentation Safety**: `packer-config.yaml` is 835 lines long. When replacing the `sovereign-audit` block, be extremely careful with indentation. Using a quick Python script with `ruamel.yaml` or `PyYAML` to update the config is often safer than `sed`/`awk` or manual text replacement.
4. **Directory Creation**: Before running `curate_packs.py --write-lock context_packs/sovereign-audit/theme_lock.json`, ensure the `context_packs/sovereign-audit/` directory actually exists (since we moved the old one to `.poison/`). If it doesn't, the file write will crash.
5. **Theme Splitting Strategy**: If `tech-architecture-research` has a theme exceeding 15,000 tokens, split it logically in the YAML. For example, if `research_docs` is 25,000 tokens, create `research_docs_part1` and `research_docs_part2`, distributing the files array between them.

---

## ✅ Acceptance Criteria (Phase 4 Complete When)

| Check | Command | Expected |
|-------|---------|----------|
| `sovereign-audit` curates green | `curate_packs.py sovereign-audit` | Exit 0, rich table shows all themes ≤ budget |
| `tech-architecture-research` curates green | `curate_packs.py tech-architecture-research` | Exit 0 |
| Both have `theme_lock.json` | `cat context_packs/*/theme_lock.json` | Per-file tokens + SHA256 |
| Total bundles ≤ 11 each | `jq '.themes | length' theme_lock.json` | ≤ 11 |
| Contract tests still green | `pytest tests/contract/test_context_packer*.py -q` | 27 passed |
| No hand-built `.md` overwritten | `ls context_packs/tech-architecture-research/*.md` | Sources intact |

---

## 🚫 Do NOT Do

- ❌ Run `packer.py` regeneration yet (Phase 5)
- ❌ Upload to Web Claude
- ❌ Modify `curate_packs.py`, `token_estimator.py`, `platform_adapters.py`
- ❌ Use globs in `files:` lists — must be explicit
- ❌ Delete or modify `context_packs/.poison/`

---

## 📝 Completion Report

When both profiles curate green, write:

**File**: `data/handoff/CLINE_TO_KALI_PACKER_V3_PHASE4_COMPLETE_20260808.md`

**Contents**:
- Which profiles curated
- `theme_lock.json` paths
- Any theme splits performed
- Contract test status
- Ready for Phase 5

---

## 🐝 Hivemind (Optional)

If you want to broadcast progress:
```bash
# Post context to Omega Hub
# intent: "status" or "handoff"
```

---

## 📞 Escalation

If blocked:
- **Config/schema questions** → Check `docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md`
- **Mandate interpretation** → `SOVEREIGN_MANDATES.md`
- **Tool chain failure** → Report `[TOOL-CHAIN-COLLAPSE]` per M23

---

*⬡ OMEGA ⬡ KALI → CLINE ⬡ PACKER-V3-PHASE4 ⬡ 2026-08-08*

**The curator is the gatekeeper. No pack regenerates until `curate_packs.py` exits 0 with a valid `theme_lock.json`.**