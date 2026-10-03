<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ENGINE_CLEANSING_delta — Session Paging Report
**AP Token**: `AP-PAGING-ENGINE-CLEANSING-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_session_paging ⬡ 2026-08-22

**Source session**: "Kali - Engine Cleansing and Hardening" (Aug 8–12, ~44M tokens)
**Mined files**: `docs/sprints/hygiene-20260808/EXECUTION_MANUAL.md`, `docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md`, `data/entities/kali/{,workspace/}session_gnosis.md`, PIVOT_LOG archive D-512..D-520.
**Cross-checked against**: `data/coordination/ACTIVE_SPRINT.json` (PUBLIC-DEBUT-01) + live repo state (greps, git log, systemd).
**Method**: every era claim re-verified against current tree; no transcript reliance.

---
## §A — Projects: completed, forgotten, or stalled

**VETALA / OMEGA-SIEVE: CLOSED.** Removed in `3efe923f` (dead-code) + `6e1d574a` (exclusion cleanup).
Verified today: zero refs in src/tests/scripts/Makefile; `packages/omega-sieve/` gone;
`docs/reference/api/omega_sieve.md` gone. No residual debt.

**CONTEXT PACKER V3: IMPLEMENTED, THEN PARKED — STATUS AMBIGUOUS.**
Shipped in era (`9c6c35f`: contract tests, curator CLI, shared TokenEstimator; V2 pipeline
methods verified deleted; per-profile `context_packs/*/pii_vault.json` live; Phase4/5
completion doc archived). BUT ACTIVE_SPRINT scope-cut notes list "Context Packer" under
POST-DEBUT items — risk a future agent re-plans already-shipped work.
Residual debt: global `data/coordination/pii_vaults/sovereign-audit.json` still exists
(V3 manual Phase 6 said remove usage; file IS gitignored — low risk, cosmetic).

**HYGIENE §8 AGENTS.md dedup (deferred "Sprint 2"): MOOT.** Root AGENTS.md no longer
exists; `.agents/AGENTS.md` is 43 lines with 0 duplicate sections. Resolved by
replacement/move, not the planned surgical edit. No action needed.

**HYGIENE §9 Future Decisions — 4 of 5 NEVER RESOLVED, NO TICKETS:**
1. omega-meditation PyPI publish — still local-editable only (deliberate deferral, OK).
2. pyproject name `omega` still collides with Caltech's PyPI package — unresolved if ever publishing.
3. `RE_IDSOFT_EMPTY` regex property test — flagged in manual Fix C ("requires a test");
   `tests/test_ark_optimizer.py` does NOT exist today. Never written, never ticketed.
4. GROK_CLI_TO_KALI_CONTEXT_PACKER_V3_REFACTOR handoff file — still untracked at
   data/handoff/, commit-or-delete decision never made.

**F821 remediation (adjacent, Aug 15 gnosis)**: handoff ho_4e14cee4057a → Roc; plan docs
exist at docs/sprints/f821-remediation/; completion NOT verifiable from current trackers.
## §B — Hardening wins that are LOAD-BEARING today (all re-verified live)

| Win | Decision/Commit | Verified today |
|-----|-----------------|----------------|
| Vetala/sieve dead-code removal | `3efe923f` | 0 refs anywhere |
| sqlite-vec [id-soft:]→[heritage:] | D-512 / `1d9dfc17` | 0 mis-tags in src/ |
| PyPI fiction killed (honesty) | D-513 / `93bdd836` | STATUS_REPORT+OMEGA_ENGINE honest |
| ark_optimizer service fix + make targets | D-514 / `485c205d` | timer ACTIVE, next fire 00:28 ADT tonight; targets in .PHONY |
| omega_pantheon→omega_nodes rename fix | D-515 | KeyError regression closed |
| Rotating test-run log (test-honest chain) | D-516 | wired into Makefile chain |
| ObservabilityEngine async refactor (P0 data-loss fix) | D-517 | silent MetricsDB-drop path eliminated |
| M23 pre-commit AST Ruff ratchet | D-518 | replaced structurally-broken rg pipeline |
| ProviderRegistry SSOT (73.6% misclassification fix) | D-520 | now CITED in SOVEREIGN_MANDATES M7 enforcement |

These nine are the era's surviving skeleton. D-517 and D-520 are the two deepest —
both fixed silent-failure classes that would still be producing wrong data today.
## §C — Flagged important, then VANISHED from all later plans

1. **Carmack L3 principle (hygiene manual §10)** — "Fix the mechanism, don't kill the
   tool; delete the lie, don't build a verifier." Absent from later doctrine docs;
   worth re-canonicalizing in a standards doc.
2. **ark_optimizer §2 "New-Plan Integration Gaps" (4 items)** — explicitly out of scope
   in era ("verdict remains 🟡 DEGRADED until addressed in future sprint"); never
   resurfaced in any later sprint. Status unknown.
3. **RE_IDSOFT_EMPTY property test** — see §A.3. Flagged mandatory-adjacent, no ticket.
4. **pii_vaults global-dir removal** — Phase 6 closeout item, incomplete (§A residual).
5. **Context Packer "DONE not pending" fact** — ACTIVE_SPRINT POST-DEBUT listing could
   trigger redundant re-planning of shipped work (§A).
6. **D-516 duplicate entry** in PIVOT_LOG archive (same decision twice) — minor
   integrity blemish in the frozen archive; note only.

## §D — Verdict

Era knowledge survived well in files: 9/9 major hardening wins load-bearing, vetala/
sieve fully closed, V3 packer shipped. Gaps are small and ticketable: 4 unresolved §9
decisions, ark_optimizer degraded-verdict items, Context Packer status ambiguity.
File complete.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
