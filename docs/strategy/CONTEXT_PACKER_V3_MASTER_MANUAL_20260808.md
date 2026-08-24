# 🔱 Context Packer v3 — Master Refactoring Manual & SSOT
**AP Token**: `AP-PACKER-V3-MASTER-MANUAL-20260808-v2.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_packer_v3_master ⬡ ACTIONABLE

**Date**: 2026-08-08
**Status**: **IMPLEMENTATION SSOT** (Supersedes all prior handoffs, reviews, and syntheses)
**Consolidates**: Carmack Arch Review, Grok CLI Handoff, Researcher Synthesis, Gemini Architectural Insights, **Sonnet 4.6 Code Audit**, **Nemotron 3 Ultra Deep Audit**.

---

## §0. Executive Doctrine

The Context Packer v2 is broken (M23 violation). It silently deletes core engine themes (`mandates`, `oracle_core`, etc.) to fit token budgets due to a flawed split/trim/consolidate pipeline and mismatched keyword priorities. 

**The V3 Doctrine:**
> **Curate at config-time. Validate at pack-time. Never silently delete themes to fit a budget.**

If a pack is over budget, over slots, or missing required files → **`[PACK-FAIL]`** and hard stop. Intelligence lives offline in curation, not in runtime surgery.

---

## §1. Architectural Directives (The "What")

This refactor replaces a 9-phase post-hoc surgical pipeline with a strict 5-phase deterministic pipeline.

### 1.1 Kill the V2 Pipeline
**DELETE** the following methods from `packer.py`:
- `_enforce_token_limits`
- `_split_bundle_by_tokens`
- `_trim_to_token_limit`
- `_consolidate_bundles`
- `_reorder_bundles_for_litm`
- `CRITICAL_START_BUNDLES` / `CRITICAL_END_BUNDLES` / `MIDDLE_BUNDLES` keyword sets.
- `_glob_files` + `_match_pattern` (54 lines) — **REPLACE with `pathspec`** (already installed).
- `INJECTION_PATTERNS` + `INJECTION_REGEXES` — **KEEP** (valid security layer for pre-upload scanning).
- `MAX_BUNDLE_TOKENS` / `MAX_TOTAL_TOKENS` module constants — **REMOVE**; budgets come from `PlatformConfig` only.

### 1.2 The V3 Pipeline (5 Steps)
1. **Resolve**: Expand explicit file lists from config using **`GitIgnoreSpec.from_lines(patterns)`** (handles `**`, negation `!`, edge cases). Returns `Dict[theme_name, List[FileInfo]]`. Note: `pathspec.from_lines('gitwildmatch', ...)` is deprecated in v1.0+ — use `GitIgnoreSpec` for full Git behavior.
2. **Count**: Estimate tokens using **shared `TokenEstimator` utility** (single source of truth for curator + packer). Applies `token_margin_multiplier` from `PlatformConfig`.
3. **Validate (FAIL-CLOSED)**: Check `per_bundle` budget, `total` budget, `max_slots` (including manifest), and `required` themes. Hard fail with `[PACK-FAIL]` + diagnostic file list if violated.
4. **Order**: Use `platform_adapters.py` ordering strategies. **Wire `litm_zone` → priority mapping**: `start=3`, `middle=2`, `end=1` for LITM-U; `start=3` for priority-weighted. PACT framework markers injected into bundle metadata.
5. **Write**: Apply PII masking (concurrent via AnyIO at **file-loop level**), XML escape **before** CDATA wrapping, format adaptation, Ed25519 signature. Write **only `.xml` files** (or to `generated/` subdir) — never delete non-generated files. **XML read-back paths MUST use `defusedxml.ElementTree` for parsing** (security-hardened), but use stdlib `xml.etree.ElementTree.Element`/`SubElement` for element creation (defusedxml does NOT provide these).

### 1.3 Community Library Substitutions (Zero New Dependencies)
All libraries below are **already installed in the venv** — zero `pip install` required.

| Custom Code | Replace With | Location | Status |
|-------------|--------------|----------|--------|
| `_glob_files` + `_match_pattern` (54 lines) | `GitIgnoreSpec.from_lines(patterns)` | `packer.py:1067-1120` | **MANDATORY** |
| Raw `sys.argv` CLI parsing | `typer` (built on `click 8.4.2`) | `packer.py:main()`, new `curate_packs.py` | **MANDATORY** |
| Plain `print()` diagnostic table | `rich.Table` with colour-coded status | `curate_packs.py` output | **MANDATORY** |
| `xml.etree.ElementTree` (if any read-back) | `defusedxml.ElementTree` (parse) + stdlib `Element`/`SubElement` (create) | `_sign_manifest`, future verify | **MANDATORY** |
| Hardcoded `1.3` margin | `PlatformConfig.token_margin_multiplier` | `token_estimator.py`, `PlatformConfig` | **MANDATORY** |
| Module constants `MAX_BUNDLE_TOKENS` | Config-driven budgets only | `packer.py:132-133` | **DELETE** |

### 1.4 Gemini Integration Insights (Crucial Enhancements)
1. **Diagnostic Fail-Closed**: When `curate_packs.py` or `packer.py` fails due to budget overruns, it **MUST** print the top 3-5 largest files in the offending theme. Do not just fail; provide the exact surgical target for the human/agent to fix.
2. **Concurrent PII Masking (M1)**: The fix is at the **file-loop level** in `pack()`, not inside `PIIMasker.detect()` (which already uses `anyio.to_thread.run_sync()`). Wrap the per-file read+mask+render pipeline in `anyio.create_task_group()`.
3. **Platform-Specific Token Margins**: Do NOT hardcode the `1.3x` tiktoken safety margin. Move `token_margin_multiplier` to `PlatformConfig` (e.g., Claude = 1.3, Grok/Gemini = 1.0).
4. **Absolute Output Protection**: Never `rm -rf` an output directory. Write generated bundles strictly as `.xml` or to a `generated/` subdirectory to absolutely guarantee hand-built knowledge files (like `RESEARCH_BRIEF.md`) are never overwritten or deleted.
5. **XML Escaping Order**: Apply `_escape_bare_xml_chars()` **BEFORE** any format adapters wrap content in `<![CDATA[...]]>`. Aggressive escaping will mangle existing CDATA tags if applied too late.

### 1.5 Shared Utilities (Zero-Drift Contract)
**`src/omega/oracle/token_estimator.py`** (or new `token_util.py`) is the **single token estimation function** used by BOTH `curate_packs.py` and `packer.py`. 
- Signature: `estimate_tokens(text: str, model: str = "cl100k_base") -> int`
- Applies `token_margin_multiplier` from `PlatformConfig`.
- **No duplicate logic allowed.** If curator and packer disagree on counts, it's a bug.

### 1.6 `litm_zone` → Priority Mapping (Platform Adapters Contract)
The existing `platform_adapters.py` strategies consume `priority` (int). V3 config uses `litm_zone` (str). The packer **MUST** translate at bundle-assembly time:
```python
LITM_ZONE_PRIORITY = {"start": 3, "middle": 2, "end": 1}
bundle["priority"] = LITM_ZONE_PRIORITY.get(bundle.get("litm_zone", "middle"), 2)
```
This ensures `LITMUShapedStrategy` and `PriorityWeightedStrategy` work unchanged.

### 1.7 Nemotron 3 Ultra Additional Insights (Deep Code Audit)

#### 1.7.1 Injection Scanner — Keep But Harden
The 68-pattern OWASP injection scanner (`packer.py:61-128`) is a **valid security layer** — it scans source files *before upload* to catch prompt injection in context. **Keep it.** But:
- It currently only logs warnings (`print(f"  ⚠️  Injection pattern detected...")`). The manual should specify: **fail the pack** if injection patterns are detected in files marked `required: true`. Optional files can warn.
- The patterns are regex-only. For production hardening, consider `llm-guard` (not installed) or `rebuff` (not installed) later — but regex is acceptable for v3.

#### 1.7.2 PII Vault Persistence — Fix the Location
Current `packer.py:977-992` writes the `pii_vault` to `data/coordination/pii_vaults/{profile}.json` — a global directory. This breaks encapsulation: the vault is decoupled from its pack.
- **Fix**: Write `context_packs/<profile>/pii_vault.json` alongside the manifest and `pack_index.json`. This makes the pack a single, atomic, portable unit.
- The vault must be **excluded from git** — add `context_packs/*/pii_vault.json` to `.gitignore` (the `context_packs/` directory is already gitignored, but the global `data/coordination/pii_vaults/` path is NOT).

#### 1.7.3 File Metadata — SHA256 is Computed But Unused
`_calculate_sha256` runs for every file but the hash is only stored in `FileMetadata` and never used for change detection or cache invalidation.
- **v3 Use Case**: `curate_packs.py --write-lock` should include SHA256 in `theme_lock.json` so the lock file can detect upstream file changes and warn "theme_lock.json is stale — re-run curator".

#### 1.7.4 `_prune_content` — Too Aggressive for Code
`_prune_content` collapses triple newlines and strips trailing whitespace. This is fine for markdown but **corrupts Python** (removes blank lines that are semantically meaningful for readability, strips trailing whitespace that may be intentional in string literals).
- **Fix**: Only apply pruning to `.md`, `.txt`, `.yaml` files. Skip for `.py`, `.json`, `.xml`, `.sh`.

#### 1.7.5 `pathspec` Negation Patterns for Excludes
The current config has `exclude` lists but the glob logic doesn't support negation. `pathspec` natively supports `!` patterns:
```python
# In config, allow:
include:
  - "src/omega/**/*.py"
exclude:
  - "!src/omega/**/test_*.py"  # negation = keep test files
```
This is cleaner than separate `exclude` lists. The manual should recommend migrating to `pathspec` negation syntax in v3 config.

#### 1.7.6 `tiktoken` Encoding Selection Per Platform
Currently hardcoded to `cl100k_base` (Claude). Different platforms use different tokenizers:
- Claude: `cl100k_base` (GPT-4/Claude compatible)
- Grok/Gemini: `o200k_base` (GPT-4o) or model-specific
- **Fix**: `PlatformConfig` should include `tokenizer_encoding: str` defaulting to `cl100k_base`. Pass to `TokenEstimator`.

---

## §2. Configuration Schema (v3)

`packer-config.yaml` is the Single Source of Truth. 

```yaml
profiles:
  sovereign-audit:
    description: "Core Engine and Mandates Audit"
    tier: ship                       # NEW: ship | internal | template
    target_platform: "web-claude"
    target_model: "claude-sonnet-5"
    max_slots: 12                    # TOTAL files including manifest
    format: "xml"
    bundle_ordering: "litm-u-shaped"
    token_budget:
      total: 150000
      per_bundle: 15000
    prompt_caching:
      enabled: true
      cache_prefix: ["manifest", "mandates"]
    # NEW: Platform specific token margin (replaces hardcoded 1.3)
    token_margin_multiplier: 1.3
    # NEW: Tokenizer encoding for this platform
    tokenizer_encoding: "cl100k_base"
    themes:
      - name: mandates
        required: true               # PACK-FAIL if missing or over budget
        litm_zone: start             # start | middle | end (Drives PACT ordering)
        files:                       # EXPLICIT LISTS. No fat globs.
          - "SOVEREIGN_MANDATES.md"
          - "OMEGA_ENGINE.md"
      - name: oracle_core
        required: true
        litm_zone: middle
        files:
          - "src/omega/oracle/model_gateway.py"
          - "src/omega/oracle/providers.py"
```

---

## §3. Execution Plan (Phased)

### Phase 0: Spec & Workspace (30m)
- [ ] Establish `data/coordination/KALI_WORKSPACE_LOCK_YYYYMMDD.md`.
- [ ] Verify `context_packs/sovereign-audit/` poison pack is quarantined (DO NOT UPLOAD).

### Phase 1: Semantic Contract Tests (1-2h) — *START HERE*
- [ ] Create `tests/fixtures/context_packer/` structure:
  ```
  tests/fixtures/context_packer/
  ├── test-profile.yaml          # Minimal profile: 2 themes, tiny budgets
  ├── theme_a/
  │   ├── file1.py               # ~50 tokens
  │   └── file2.py               # ~50 tokens
  └── theme_b/
      └── file3.md               # ~30 tokens
  ```
- [ ] Create `tests/contract/test_context_packer_v3.py`.
- [ ] Assertions (M21 Gate Integrity — real isinstance, no mocks):
  - `test_over_total_budget_raises` — Packer raises `RuntimeError("[PACK-FAIL] total budget exceeded")`
  - `test_required_theme_missing_raises` — Missing `required: true` theme → `RuntimeError("[PACK-FAIL] required theme missing")`
  - `test_max_slots_includes_manifest` — On-disk file count (bundles + manifest) ≤ `max_slots`
  - `test_litm_zone_ordering` — Bundles ordered: start → middle → end (LITM-U) or by priority (weighted)
  - `test_no_keyword_priority_side_effects` — Theme named `mandates` not special-cased by substring sets
  - `test_token_estimator_shared` — Curator and packer produce identical token counts for same input
  - `test_pathspec_glob_matching` — `pathspec` correctly handles `**` and negation patterns
  - `test_injection_scanner_fails_required` — Injection in required theme → `[PACK-FAIL]`

### Phase 0.5a: Quick Hygiene (Parallel with Phase 1) (1h)
- [ ] Add `tier:` field to all 15 profiles in `packer-config.yaml`.
- [ ] Add `tokenizer_encoding:` to all profiles (Claude = `cl100k_base`, Grok/Gemini = `o200k_base`).
- [ ] Fix 16 ghost references to `enhanced_packer.py` in the config.
- [ ] Update `packer.py` CLI to use `typer` (dynamic profile listing from config, default to `tier: ship`).
- [ ] Archive `provider-fabric-review` output to `context_packs/archive/`.

### Phase 2: The Curator Tool (`curate_packs.py`) (1-2h)
- [ ] Create standalone CLI tool at `.opencode/skills/context-packer/curate_packs.py` using **`typer`**.
- [ ] **CLI Spec**:
  ```bash
  python curate_packs.py <profile_name> [--config PATH] [--write-lock]
  ```
  - `--write-lock`: Outputs `context_packs/<profile>/theme_lock.json` with explicit file lists + token counts + SHA256 for reproducibility.
- [ ] Loads config, expands files using **`pathspec`**, counts tokens (using **shared `TokenEstimator`** + platform margin + `tokenizer_encoding`).
- [ ] Prints diagnostic table using **`rich.Table`**: `Theme | Files | Tokens | Budget | Headroom | Required | Status` (colour-coded: `[green]OK`, `[red]OVER`, `[yellow]WARN`).
- [ ] **If over budget**: Prints top 3 largest files in the failing theme with token counts.
- [ ] Exits non-zero on failure (budget, missing required, missing files, injection in required theme).

### Phase 3: Packer V3 Core Rewrite (2-4h)
- [ ] Implement the 5-step pipeline in `packer.py`.
- [ ] Implement concurrent PII masking via AnyIO at **file-loop level** (`anyio.create_task_group()` per file).
- [ ] Implement safe output writing (only overwrite `.xml` or write to `generated/`).
- [ ] Auto-write `context_packs/<profile>/pack_index.json` on successful pack (schema below).
- [ ] Wire `litm_zone` → `priority` mapping for platform adapters.
- [ ] Write `context_packs/<profile>/pii_vault.json` (reversible token map for detokenization).
- [ ] Use `defusedxml.ElementTree` for XML parsing (security-hardened); stdlib `Element`/`SubElement` for creation.
- [ ] Apply `_prune_content` only to `.md`, `.txt`, `.yaml` — skip code files.
- [ ] Migrate glob logic to `GitIgnoreSpec.from_lines()` (NOT deprecated `gitwildmatch`).

### 1.8 `pack_index.json` Schema (Auto-Written, Per-Profile)
```json
{
  "profile": "sovereign-audit",
  "generated_at": "2026-08-08T10:45:17.134743Z",
  "total_files": 11,
  "total_tokens": 144384,
  "max_slots": 12,
  "bundles": [
    {"theme": "mandates", "file": "mandates.xml", "tokens": 5560, "litm_zone": "start", "required": true},
    {"theme": "oracle_core", "file": "oracle_core.xml", "tokens": 12000, "litm_zone": "middle", "required": true}
  ],
  "manifest": "00_PROJECT_MANIFEST.md",
  "signature": "ed25519:...",
  "public_key": "-----BEGIN PUBLIC KEY-----...",
  "pii_vault": "pii_vault.json"
}
```
**Top-level `context_packs/PACK_INDEX.json`** (optional): Summary aggregator listing all per-profile indexes with timestamps.

### Phase 4: Curate Ship Profiles (2h)
- [ ] `sovereign-audit`: **Explicit theme list (≤11 content bundles + manifest = ≤12 files)**:
  | Theme | litm_zone | required | Files (explicit, NO globs) |
  |-------|-----------|----------|----------------------------|
  | `mandates` | start | yes | `SOVEREIGN_MANDATES.md`, `OMEGA_ENGINE.md`, `AGENTS.md` |
  | `oracle_core` | middle | yes | `model_gateway.py`, `providers.py`, `oom_protector.py`, `admission_controller.py`, `health_monitor.py`, `resource_guard.py` |
  | `memory` | middle | yes | `memory_store.py`, `sqlite_vec_adapter.py`, `vector_adapters.py`, `embeddings.py`, `hybrid_search.py`, `fts_index.py` |
  | `observability` | middle | yes | `metrics_db.py`, `token_ledger.py`, `sovereignty.py`, `observability_reader.py` |
  | `mcp_hub` | middle | yes | `mcp_runtime.py`, `hub.py`, `gateway/__init__.py` |
  | `config` | middle | yes | `providers.yaml`, `models.yaml` |
  | `strategy_core` | end | no | `SOVEREIGN_ARK_BLUEPRINT.md`, `UNOVERENGINEERING_PLAN.md` |
  **Drop**: Full strategy archive, all oracle backends, all tests, all monitoring.
- [ ] `tech-architecture-research`: Ensure hand-built `.md` files are protected. Split themes in YAML if > `per_bundle` budget.

### Phase 5: Regenerate & Verify (1h)
- [ ] Run `packer.py` for both ship profiles.
- [ ] Verify `sovereign-audit` has ≤12 files, all required themes present, no `strategy_partN` spam.
- [ ] Verify `test_context_packer_v3.py` is green.
- [ ] Verify `pii_vault.json` exists and is valid JSON with reversible mappings.
- [ ] Verify `theme_lock.json` includes SHA256 for change detection.

### Phase 6: Closeout
- [ ] Update `SKILL.md` with new v3 flow and `curate_packs.py` usage.
- [ ] Update `session_gnosis.md`.
- [ ] Add `context_packs/*/pii_vault.json` to `.gitignore` (and remove global `data/coordination/pii_vaults/` usage).

---

## §4. Definition of Done (DoD)

### P0 Product (Must Pass)
1. **No Runtime Deletion**: Packer never deletes themes to meet budgets.
2. **Hard Failures**: Budgets and `max_slots` strictly enforced.
3. **Diagnostic Curation**: `curate_packs.py` exits non-zero and identifies exact files causing bloat.
4. **Regenerated Packs**: `sovereign-audit` and `tech-architecture-research` are clean, ≤12 files, and contain all required engine themes.
5. **Safe Output**: Hand-built `.md` files are untouched by the packer.
6. **M21 Contracts**: Semantic tests cover budget/slots/required/ordering and pass.
7. **Community Libraries Used**: `pathspec`, `typer`, `rich`, `defusedxml` replace all custom implementations.
8. **PII Vault Persisted**: `pii_vault.json` written to `context_packs/<profile>/` (not global dir) and excluded from git.
9. **Injection Scanner Hardened**: Required-theme injection → `[PACK-FAIL]`.

### P1 Hygiene
10. **Config Cleaned**: `tier:`, `tokenizer_encoding:` fields implemented, 16 ghost references removed.
11. **CLI Dynamic**: `packer.py` and `curate_packs.py` use `typer` with dynamic profile listing.
12. **Lifecycle**: Per-profile `pack_index.json` auto-written; top-level aggregator optional.
13. **Change Detection**: `theme_lock.json` includes SHA256 for staleness detection.

---

## §5. Mandates Binding This Work
*   **M1 (AnyIO)**: Concurrent PII masking must use `anyio` at file-loop level.
*   **M4 (Sequentiality)**: Plan → Verify → Execute. Red tests first.
*   **M8 (Zero Telemetry/Sovereignty)**: PII masking is a hard gate; vault persisted for reversibility.
*   **M13 (Temple-Grade)**: Contract tests required.
*   **M21 (Gate Integrity)**: Semantic boundary tests, not just vanity type checks.
*   **M23 (Failure Integrity)**: Over budget = `[PACK-FAIL]`. No soft-failure theater.

---

## §6. Knowledge Gaps Resolved (Research Complete)

| Gap | Resolution | Source |
|-----|------------|--------|
| `pathspec` capability for our globs | Verified: `GitIgnoreSpec.from_lines()` handles `**`, negation `!`; `gitwildmatch` deprecated in v1.0+ | Researcher live test |
| `rich.Table` rendering in this env | Verified: works perfectly, colour markup in `add_row()` | Researcher live test |
| `defusedxml` availability | Verified: 0.7.1 installed; **NOT** full drop-in — only parse functions, use stdlib for Element creation | Researcher live test |
| `typer`/`click` availability | Verified: 0.25.1 / 8.4.2 installed | Nemotron live test |
| `pii-shield` primary engine | Verified: 1.1.0 installed, already used by `PIIMasker` (uses `scan_text`, not `detect`) | Researcher live test |
| `tiktoken` encodings available | Verified: `cl100k_base`, `o200k_base` available | Nemotron live test |
| `cryptography` Ed25519 | Verified: 49.0.0 installed, working | Nemotron live test |
| Injection scanner scope | Confirmed: scans source files pre-upload, 68 patterns | Code audit |
| PII vault persistence bug | Confirmed: writes to global `data/coordination/pii_vaults/` (not gitignored) — must move to per-profile dir | Code audit |
| `_prune_content` code corruption | Confirmed: strips trailing whitespace, collapses newlines | Code audit |
| SHA256 unused | Confirmed: computed but never used for change detection | Code audit |

---

*End of Manual. Execute Phase 0 and Phase 1 immediately.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
