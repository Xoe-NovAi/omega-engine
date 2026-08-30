<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Kali → @maat — Context Packer v3 Phase 3 Handoff
**AP Token**: `AP-KALI-TO-MAAT-CP-V3-PHASE3-20260808`
⬡ OMEGA ⬡ KALI ⬡ @maat ⬡ N3 ⬡ M4 ⬡ M23

**Date**: 2026-08-08
**From**: `@kali` (via Cline)
**To**: `@maat` (Build Oversoul — N1-N5)
**Priority**: P0
**Task id**: `packer-v3-refactor-20260808-03`

---

## 0. Executive Order

You are authorized to execute **Phase 3** of the Context Packer v3 refactor: **rewire `pack()` onto the v3 contract API**. Do not change Phases 4–5 (curation + regeneration); those remain with Kali/Cline.

**Doctrine (non-negotiable):**
> Curate at config-time. Validate at pack-time. Never silently delete themes to fit a budget.

---

## 1. Current State (as of commit `391c3b72`)

- v3 contract tests: **17 passing** in `tests/contract/test_context_packer_v3.py`
- Legacy v2 tests: **10 passing** in `tests/contract/test_context_packer.py`
- Shared `src/omega/oracle/token_estimator.py` is in place (M23 hard-stop, no soft-fail).
- `packer.py` has additive v3 primitives: `resolve_theme_files`, `validate_pack`, `PackValidationError`, `LITM_ZONE_PRIORITY`, `apply_litm_priority`, `write_pii_vault`.
- Legacy `pack()` method is **untouched** (1158 lines).
- Config hygiene is **complete** for 15 profiles (`tier:`, `tokenizer_encoding:` added; 16 `enhanced_packer` ghost refs removed).
- Poison pack quarantined: `context_packs/sovereign-audit/` → `context_packs/.poison/sovereign-audit-20260808/` (do not restore).

---

## 2. Mission — Phase 3 Only

Rewrite the **runtime `pack()` method** in `.opencode/skills/context-packer/packer.py` so it uses the v3 5-step fail-closed pipeline. Do not touch Phases 4–5.

### 2.1 Must-do

1. Replace the body of `EnhancedContextPacker.pack(profile_name)` with the following ordered steps:
   - `themed = resolve_theme_files(profile, base)`
   - `validate_pack(profile, themed)` — let `PackValidationError` propagate; do not catch and continue
   - apply `apply_litm_priority(bundle)` to each theme bundle, then call `get_ordering_strategy(profile.platform).order(bundles)`
   - write bundles via adapter `write`
   - `write_pii_vault(vault_path, tokens)`
   - Ed25519 sign manifest
2. Wire budgets from `profile.platform`:
   - `per_bundle = profile.platform.token_budget_per_bundle if profile.platform else DEFAULT_PER_BUNDLE`
   - `total = profile.platform.token_budget_total if profile.platform else DEFAULT_TOTAL`
   - `max_slots = profile.max_slots`
3. Delete these v2-only symbols (confirmed safe by handoff §5):
   - `_enforce_token_limits`
   - `_split_bundle_by_tokens`
   - `_trim_to_token_limit`
   - `_consolidate_bundles`
   - `_reorder_bundles_for_litm`
   - `CRITICAL_START_BUNDLES` / `CRITICAL_END_BUNDLES` / `MIDDLE_BUNDLES` keyword sets
   - `MAX_BUNDLE_TOKENS` / `MAX_TOTAL_TOKENS` module constants
4. Keep `_escape_bare_xml_chars`, atomic write helpers, `pii_masker` hard-fail import, `OMEGA_PACKER_DEBUG`/`OMEGA_PACKER_TRACE`.
5. Update the CLI usage string at `packer.py:1301` from `enhanced_packer.py` to `packer.py`.

### 2.2 Must-not

- Do not modify `tests/contract/test_context_packer.py` (legacy v2 tests).
- Do not modify `tests/contract/test_context_packer_v3.py` (specification is locked).
- Do not modify `src/omega/oracle/token_estimator.py` (locked SSOT).
- Do not modify `.opencode/skills/context-packer/platform_adapters.py` (locked contract).
- Do not regenerate `context_packs/` (Phases 4–5 only).
- Do not reintroduce silent-drop logic under any circumstances (M23 hard-stop).

---

## 3. Target Architecture (v3 5-step)

```
packer-config.yaml -> load_config
    |
    v
resolve_theme_files(profile, base) -> Dict[str, List[file_info]]
    |
    v
validate_pack(profile, themed) -> raise PackValidationError on failure
    |
    v
apply_litm_priority(bundle) + get_ordering_strategy(profile.platform).order(bundles)
    |
    v
adapter.write(bundles) -> XML + manifest
    |
    v
write_pii_vault(vault_path, tokens)
    |
    v
Ed25519 sign manifest -> pack_index.json / manifest signature
```

---

## 4. LITM Priority Contract

Map `litm_zone` → `priority` using the **existing** constant in `packer.py`:

```python
LITM_ZONE_PRIORITY = {"start": 3, "middle": 2, "end": 1}
```

Do not invent a second ordering implementation. `platform_adapters.LITMUShapedStrategy` already consumes `bundle["priority"]` as an int.

---

## 5. Error Contract

`PackValidationError` is a `RuntimeError` subclass with `[PACK-FAIL]` prefix. It is **fail-closed**: the packer must not write any output if validation fails. If you believe it should be promoted to an `OmegaError` subclass, raise that as a question in your completion report — do not change it unilaterally.

---

## 6. Verification Gate (Must Pass Before Completion)

```bash
pytest tests/contract/test_context_packer.py tests/contract/test_context_packer_v3.py -q
```

Required: **27 passed** (10 legacy + 17 v3). No failures. No skipping of v3 tests.

---

## 7. Completion Report

When done, write a brief handoff back to Kali at:

```
data/handoff/MAAT_TO_KALI_PACKER_V3_PHASE3_COMPLETE_20260808.md
```

Include:
- Diff stat for `packer.py` only
- Confirmation that 27 contract tests pass
- Any questions for Kali (e.g., `PackValidationError` promotion, legacy CLI backward-compat)
- List of deleted v2 symbols (for changelog)

---

## 8. Key References

| Path | Purpose |
|------|---------|
| `data/handoff/GROK_CLI_TO_KALI_CONTEXT_PACKER_V3_REFACTOR_20260808.md` | Original implementation law |
| `docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md` | SSOT manual (§1–§5) |
| `data/coordination/KALI_CONTEXT_PACKER_V3_PROGRESS_REPORT_20260808.md` | Kali’s review doc (current state) |
| `.opencode/skills/context-packer/packer.py` | Target file |
| `.opencode/skills/context-packer/curate_packs.py` | Curator (do not modify) |
| `src/omega/oracle/token_estimator.py` | Shared estimator (do not modify) |

**M23 Reminder:** If any required tool/library is unavailable during execution, halt and report `[TOOL-CHAIN-COLLAPSE]`. Do not synthesize results or silently fall back.


<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: @maat | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
