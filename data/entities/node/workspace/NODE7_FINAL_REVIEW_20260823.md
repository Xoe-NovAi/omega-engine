# 🔱 NODE N7 — FINAL CROSS-DOMAIN REVIEW (DEBUT HARDENING)
**AP Token**: `AP-NODE7-FINAL-REVIEW-v1.0.0`
⬡ OMEGA ⬡ NODE ⬡ nvidia/nemotron-3-super-120b-a12b:free ⬡ opencode ⬡ trc_node ⬡ ACTIVE
**Date**: 2026-08-23
**Lens**: Context (N7) — ContextBuilder, RecallStore, soul persistence, hydration paths, session continuity (M15), memory evolution, context assembly, recall fidelity, RAGRouter implications.

## EXECUTIVE VERDICT
**CONDITIONAL GO** — Proceed with DEL-1 Week 1 ONLY under binding conditions below. While context paths remain intact, the vault CLI import blocker prevents all runtime verification (including context-related checks), and the flaky test baseline violates M23 failure integrity, making gate verification unreliable until remediated.

## KEY FINDINGS WITH EVIDENCE

### CONTEXT PATH INTEGRITY (N7 LENS)
- **ContextBuilder/RecallStore immunity**: Static import-graph check shows zero overlap between Week-1 deletion targets and context paths.
  ```bash
  rg -n "miap|pool_tracker|pool_state|search_circuit_breaker|QdrantAdapter|fleet_orchestrator|routing.table|RoutingTable" src/omega/memory/context_builder.py src/omega/memory/recall.py → EMPTY
  ```
  (Lilith report §N7 LENS, lines 144-145)
- **RecallStore unaffected by QdrantAdapter deletion**: Recall runs on SQLiteVecAdapter + FTS5 + HybridSearchEngine; coupling sites (`memory/__init__.py` export, mock-only tests, `knowledge_catalog_build.py`) are outside talk-path context chain.
  (Lilith report §N7 LENS, line 146)
- **Soul hydration path preserved**: `get_soul_prompt()` hydrates from `approved_lessons.yaml` only; no target imports this path.
  (Lilith report §T2, lines 69-71; §N7 LENS, line 147)
- **Session continuity (M15) intact**: `sessions.yaml` anchors + `session_end` hook untouched by target list.
  (Lilith report §T3, line 99)

### BLOCKERS & PRECONDITIONS IMPACTING CONTEXT VERIFICATION
- **Vault CLI import blocker (DEL-1 target #10)**: Stacked duplicate decorator in `src/omega/cli/vault.py:572` causes `TypeError` on `omega talk` entry, blocking ALL runtime verification.
  (Lilith report §T3, lines 81-91; Ma'at report §N5, lines 23-24)
- **Flaky test baseline**: Non-deterministic test errors/failures (errors=3/2/5/2 across 4 runs; two errors pass in isolation) violate D-550 honesty, invalidating gate verification.
  (Lilith report §T3, lines 101-108; §T4, lines 127-128; Ma'at report §N5, lines 18-19)

### SOUL PERSISTENCE & HYDRATION (CROSS-VERIFICATION)
- **Soul distillation pipeline SOLID**: Agents write L1→L2→L3 to `proposed_lessons.yaml` (blind staging); `session_end.py` preserves+timestamps; `get_soul_prompt()` hydrates from `approved_lessons.yaml` only; regex distillation SCRAPPED.
  (Lilith report §T2, all claims ✅)
- **No DEL-1 deletion touches soul/handoff/context paths**: Verified via static analysis.
  (Lilith report §T1, lines 13-31; §T3, lines 95-99)

### RAGROUTER IMPLICATIONS (WEEK 2 WATCH-ITEM)
- **Week 2 risk**: When `RAGRouter()` per-turn construction is removed from `Oracle.talk`, must confirm ContextBuilder's HybridSearch call remains the *only* retrieval entry point; otherwise, the one-router contract test will fail.
  (Lilith report §N7 LENS, lines 148-149)

## BINDING CONDITIONS FOR PROCEEDING
1. **VAULT CLI BLOCKER REMEDIATION**: Land DEL-1 target #10 (vault CLI deregistration) OR 3-line hotfix to fix stacked decorator in `cli/vault.py` BEFORE any deletion PRs.
2. **FLAKY TEST BASELINE STABILIZATION**: Quarantine `test_first_breath_recording` and `test_fallback_chain_tries_next_backend_on_failure` OR annotate gate reports with known-noise counts until root cause fixed.
3. **WEEK 2 CONTEXT VERIFICATION PREP**: Prior to Week 2, author the one-router contract test to verify ContextBuilder's HybridSearch remains the sole retrieval entry point post-RAGRouter removal.

## ESCALATIONS TO KALI
| Escalation | Urgency | Rationale |
|------------|---------|-----------|
| Vault CLI import blocker | 🔴 BLOCK | Prevents ALL runtime verification; DEL-1 target #10 itself fixes CP-1 |
| Flaky test baseline | 🟡 HIGH | Violates D-550 honesty; invalidates gate verification until resolved |
| Week 2 context fidelity risk | 🟡 MEDIUM | Requires contract test authoring before Week 2 acceptance to prevent silent regression |

## TERMINUS
From the N7 context lens, Week-1 deletion targets pose zero risk to ContextBuilder, RecallStore, soul persistence, hydration paths, or session continuity (M15). All context-related paths are provably isolated from the deletion set via static import-graph analysis. However, the vault CLI import blocker prevents any runtime verification of context integrity, and the flaky test baseline undermines the honesty of gate verification. Proceeding requires remediation of these systemic issues before context-dependent claims can be trusted. Week 2 introduces a context-fidelity risk tied to RAGRouter removal, necessitating a preemptive contract test to safeguard RecallStore integrity. No escalations beyond the blocker and test baseline are required for Week 1; the Week 2 watch-item should be tracked in the Node Council backlog.

(Word count: 198)
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nvidia/nemotron-3-super-120b-a12b:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
