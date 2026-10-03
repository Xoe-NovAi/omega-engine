<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N2 Vetting Delta — Session Paging Report (Batch 2)
**AP Token**: `AP-N2-VETTING-DELTA-v1.0.0`
⬡ OMEGA ⬡ N2-PERSISTENCE ⬡ opencode ⬡ trc_n2_delta ⬡ PAGED-BACK

**Date**: 2026-08-21
**Origin session**: N2 Persistence vetting of INST-1/DEL-1 (MemoryStore, SQLite-vec, Vault, SoulStore)
**Paged by**: kali (ses_fdef2be4effe4pAaLXCTUx62GO), Architect-direct mission
**Scope of this delta**: Forgotten findings, persistence insights for DEL-1 W1, unexecuted flags
**Hydration source**: ACTIVE_SPRINT.json DEL-1 section only + prior session evidence

## Status
- [x] Header written (this section)
- [x] Hydration from ACTIVE_SPRINT.json DEL-1
- [x] §1 Forgotten vetting findings
- [x] §2 Persistence insights for DEL-1 Week 1
- [x] §3 Unexecuted important items
- [x] Completion confirmation

---

## §1 Forgotten Vetting Findings — Risks Identified, Never Mitigated

**F-1. `_load_sovereign_secrets()` still active (INST-1 FAIL #2, UNRESOLVED).**
Original verdict flagged `model_gateway.py:127` calling `_load_sovereign_secrets()` (def at :316),
dumping `.env` into `os.environ` at Gateway init. Re-verified 2026-08-21: **still present,
still called**. Redis guard (Fix 3) shipped; this sibling fix did not. Every `omega talk`
invocation still pollutes process env from repo-root `.env`. Risk: fresh-clone users inherit
stale/leaked keys silently; violates "load env at process edge" (manual §5 INST-1 step 6).
Status: never executed. Owner was Ma'at/N3.

**F-2. Vault CLI calls non-existent method (`store_credential`).**
`cli/vault.py:95,192` call `vault.store_credential(cred)`; VaultCore only has
`create_credential()`. The default CLI registration is broken at runtime. D-565/D-566 resolve
debut exposure via allowlist exclusion ("zero code changes"), but the broken subcommand remains
registered in the product code path — if `omega vault set` is ever invoked on the debut branch,
it raises AttributeError. Allowlist hides files from GitHub; it does not fix the runtime bug.
Status: never mitigated; masked by allowlist exclusion.

**F-3. MemoryStore → vault adapter write path in hot loop.**
`memory_store.py:557-571`: every `add_exchange()` attempts a shadow-vault update via
adapter registry when registered. If D-568's post-debut "DELETE VaultCore" executes without
auditing this caller, entity memory writes gain a new failure surface (currently caught +
warned, but adds latency + log noise per exchange). Was flagged as CONCERN in original
verdict; no ticket tracks it.

---

## §2 Persistence-Layer Insights for DEL-1 Week 1 Deletions

**I-1. QdrantAdapter deletion is safe for persistence; D-570 changes the calculus, not the risk.**
Original probe: zero instantiations (`rg QdrantAdapter src/omega` → import/export/def only).
`_lazy_qdrant()` means deletion cannot break MemoryStore init — SQLiteVecAdapter is the
constructor default (`memory_store.py:197`) with MemoryVectorAdapter fallback. BUT D-570 now
schedules Qdrant as the POST-DEBUT sqlite-vec replacement via IVectorStoreAdapter swap (QH-4).
Recommendation: delete the class per plan, but preserve `IVectorStoreAdapter` ABC +
`delete_session()` default contract untouched — QH-4's config-toggle migration depends on that
interface remaining stable. Do not let Week 1 cleanup touch the ABC.

**I-2. `search_circuit_breaker.py` redirect must target HealthMonitor.get_breaker() by provider NAME.**
Manual says redirect leftover callers to `HealthMonitor.get_breaker()`. Persistence-relevant
caveat from gateway code: breakers are keyed by `provider.name`, not model_name (T2.2 fix in
`_precheck_provider`). Any mechanical redirect that passes model_name will silently re-create
the always-True breaker bug. Verify redirect call-sites pass provider identity.

**I-3. Week 1 acceptance gate is insufficient for persistence honesty.**
"omega talk still local after each delete" proves inference, not memory. Add one probe:
post-deletion, run a talk with a session_id and confirm `data/memory/entities/<e>/<sid>.json`
still written + FTS row present. Deletion of pool_tracker/pool_state/miap shares no imports
with this path (verified), but the gate should prove it, not assume it.

---

## §3 Flagged Important, Never Executed

**X-1. INST-1 step 6 (`_load_sovereign_secrets` removal) — flagged FAIL in original verdict,
never executed. Re-verified today: still live at model_gateway.py:127,316. This is the single
highest-priority forgotten item; it was an INST-1 acceptance blocker, not advisory.**

**X-2. Vault CLI `store_credential` AttributeError — flagged CONCERN, never fixed. D-565..568
deferred vault work entirely (allowlist exclusion + post-debut CredentialProvider), so the
broken subcommand ships dormant on the debut branch. Acceptable for debut ONLY if `omega vault`
is also absent from demo scripts; otherwise one command breaks the demo.

**X-3. EXTERNAL_STORAGE_PATH hardcode — `memory_store.py:88` hardcodes
`/media/arcana-novai/omega_library/archive/sessions` (M16 portability violation). Flagged in
original read-through, never ticketed. 90-day archival will mkdir this path on ANY machine
running the engine — fails or pollutes foreign filesystems. Should be env-driven like
OMEGA_DATA_DIR. Low debut risk (path only touched by move_to_external_storage), but it is a
known portability landmine in a Keep-List file.

**X-4. Talk-path noise never triaged — observed during original gate run:
"Unrecognized provider 'anthropic'/'xai'" (config/providers.yaml lists providers the fabric
map lacks) + "BatchPersistenceWriter not started — falling back to direct write". Both are
persistence-adjacent honesty issues: the first means config advertises providers that cannot
load; the second means batch durability silently degrades per-process unless start_batch_writer()
is called. Neither has a ticket. Not debut-blocking; both mislead debugging.

---

## Completion Confirmation

File complete: 4 sections (header/status, §1 findings, §2 insights, §3 unexecuted) + this block.
Hydration scope respected: ACTIVE_SPRINT.json DEL-1 + decision strings only; two domain greps
(model_gateway, memory_store) to separate fixed-vs-forgotten. No other files written.

— N2 Persistence, paged-back delta, 2026-08-21

<!-- PROVENANCE-CORRECTED 2026-09-01T03:07:00Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: PLACEHOLDER | header contains unresolved {session_model} literal
actual_models(Tier0): x-preview-f-free, nemotron-3-ultra-free, minimax/minimax-m3:free, mimo-v2.5-free, nvidia/nemotron-3-ultra-550b-a55b:free, hy3-free
first_audit: 2026-08-31T03:09:52Z | updated: 2026-09-01T03:07:00Z
-->






