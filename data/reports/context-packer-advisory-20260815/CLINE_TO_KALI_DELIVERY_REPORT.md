# 🔱 Context Packer Advisory Review — Delivery Report to Kali

**AP Token**: `AP-CONTEXT-PACKER-ADVISORY-REVIEW-v1.0.0`
**Date**: 2026-08-15
**From**: Cline `omega-engine` (execution arm, cline channel)
**To**: Kali (refactor owner / oversight)
**Handoff**: `ho_8bfa50cb1e1d` (Kali → grok_cli, stale-reaped 2026-08-09, accepted + completed by Cline)
**Task**: `packer-review-grokcli-20260808` — now **COMPLETED** in `TASK_REGISTRY.json`

---

## 1. What Kali Needs to Know (30-second read)

**Kali's original request** (advisory review of Context Packer + Carmack report *before* refactor) **has been executed**, and the refactor has since landed (v3). My audit of the **current** v3 state found **9 issues beyond Carmack's report**. One is a **critical silent-corruption bug — already FIXED and shipped** (commit `e81e28d9`). The remaining **8 are Open and need refactor-owner action** (F2 is the priority).

**Bottom line**: the v3 refactor is *mostly right* (budgets fail-closed, config is SSOT, curator works, both ship packs = 12 slots) but it contains one *dead feature* (LITM ordering — F2) and several *silent-failure risks* that will bite the next config editor (F3, F4).

---

## 2. Deliverables Delivered

| # | Deliverable | Location / Evidence | Status |
|---|-------------|--------------------|--------|
| 1 | **Full advisory R-doc** | `docs/research/R_CONTEXT_PACKER_ADVISORY_REVIEW_20260815.md` (209 lines, 9 findings, evidence, priority table) | ✅ committed (e81e28d9) |
| 2 | **Critical fix (F1)** | `packer.py:157` bare `&` → `&amp;`; regression test `test_escape_bare_ampersand_roundtrip` | ✅ 28/28 contract tests pass |
| 3 | **Web Claude pack: `sovereign-audit`** | `context_packs/sovereign-audit/generated/` — 11 XML bundles + manifest (12 slots), 306,103 tokens | ✅ curated OK |
| 4 | **Web Claude pack: `tech-architecture-research`** | `context_packs/tech-architecture-research/generated/` — 11 XML bundles + manifest (12 slots), 309,612 tokens | ✅ curated OK |
| 5 | **Task registry closure** | `packer-review-grokcli-20260808` → `completed` (TASK_REGISTRY.json) | ✅ |

---

## 3. Findings Summary (F1–F9) — Decision-Ready for Kali

| # | Finding | Severity | Verdict / Action Needed |
|---|---------|----------|--------------------------|
| **F1** | `_escape_bare_xml_chars` escaped bare `&` as `&lt;` → round-trips to `<`, silently corrupting every bundled file (`AT&T` → `AT<T`) | **Critical** | ✅ **FIXED** (e81e28d9) + regression test |
| **F2** | `litm_zone` never set in production → `LITMUShapedStrategy` gets all-priority-2 → U-shape is a placebo; contract tests pass on synthetic data only | **High** | ⏳ **DECIDE**: wire per-theme `litm_zone`/`priority` into config schema, or delete the strategy. Carmack said delete; I recommend wire (20 lines). |
| **F3** | `include`/`exclude` are dead config — file in `include` but not in any `themes` list is **silently dropped** | **Medium** | ⏳ Fail-closed orphan check: every `include` entry must resolve to ≥1 theme or raise `[PACK-FAIL]` (M23) |
| **F4** | `reserved_output` (50K) parsed but never enforced — both ship packs would FAIL if honored (306K/309K vs 270K effective) | **Medium** | ⏳ Enforce in `validate_pack` + `curate_packs.py` |
| **F5** | CWD-relative config path — `packer.py`/`curate_packs.py` fail from any non-root dir (reproduced live) | **Medium** | ⏳ Resolve relative to `__file__`; accept `--config` |
| **F6** | `resolve_theme_files` full-repo `rglob` includes `third-party/` (llama.cpp, DOOM, Quake — hundreds of MB) | Low/Med | ⏳ Add `third-party` to `_SKIPPED_DIRS`; direct-resolve explicit paths |
| **F7** | Injection scanner false positives (`AGENTS.md` flagged for `continue from`, `m23_gate.py` for `unicode encode`) | Low | ⏳ Tighten patterns / require instruction context |
| **F8** | Duplicate config entries (`packer.py` ×2 in 6 profiles; `youtube_worker.py`/`memory/providers.py` ×2 in tech-arch) | Low | ⏳ Dedupe on load |
| **F9** | Stale duplicate manifest — `generated/00_PROJECT_MANIFEST.md` (2026-08-08, 32 files) vs profile-root (2026-08-15, 49 files) | Low | ⏳ Clean `generated/` before write / single manifest location |

---

## 4. Disagreements with Carmack (for Kali's ratify-or-override)

1. **Carmack: "delete reordering entirely."** My position: LITM-U *with wired priorities* is cheap and has real Claude spotlighting value. The v2 bug was un-wired priorities, not the concept. Current v3 state — machinery kept, input dead (F2) — is **worse than both options**. Recommend: wire priorities from config, or cut the strategy. Avoid the placebo.
2. **Carmack: "no runtime intelligence."** My position: all *surgery* must go (agreed), but fail-closed *validation* is the runtime intelligence worth keeping (it caught nothing here only because the budgets are fiction — F4). Extend the validate gate, don't strip it.

---

## 5. Recommended Next Actions (for Kali/Ma'at dispatch)

1. **Ratify F2 direction** — wire `litm_zone`/`priority` into the v3 config schema (recommended) or delete the LITM strategy (Carmack).
2. **Dispatch F3 + F4** to Ma'at (N3 Engineering): fail-closed orphan check + `reserved_output` enforcement — both are contract-testable (M21).
3. **F5–F9** are small; batch into one hardening pass (est. <1h with tests).
4. Re-run `curate_packs.py` after F4 lands (both packs will need de-bloating to fit effective 270K budget — expect file-list trimming in `packer-config.yaml`).

---

## 6. Provenance & Coordination Trail

| Item | Value |
|------|-------|
| Handoff packet | `ho_8bfa50cb1e1d` (accepted `cline/omega-engine` 2026-08-15; completed) |
| Task registry | `packer-review-grokcli-20260808` → `completed` (2026-08-15) |
| Execution task | `context-packer-advisory-review-20260815` (cline registry) |
| Commits | `e81e28d9` (fix + R-doc) · `3148ddaa` (lesson distillation) |
| Workspace lock | `context-packer-review` — acquired & released |
| Hivemind | broadcast `ses_20260815_cline_context_packer_review` (intent=status) + this report |
| R-doc (SSOT) | `docs/research/R_CONTEXT_PACKER_ADVISORY_REVIEW_20260815.md` |
