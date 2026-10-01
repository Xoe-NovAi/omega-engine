<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# G1 — CARMACK ORDERING REVIEW — Debut Hardening Plan (REBASED Council)
**AP Token**: `AP-CARMACK-G1-ORDERING-20260824-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_council_rebased ⬡ ORDERING-ARM ⬡ 2026-08-24

**Mode**: Final cross-domain review. Sole write = this file. No subagents. No upward paging.
**Inputs**: E_MAAT_BUILD_ARM.md · F_LILITH_RUN_ARM.md · G2_ROC_LOCALFIRST_REVIEW.md · DEBUT_REMEDIATION_MANUAL §5 · Chair's verified live facts (trusted, not re-derived).
**Prior work**: A_CARMACK_TECHNICAL_REVIEW.md (Wave-1 code, this morning). This review covers the PLAN built on it.

---

## §1 THE EXECUTION DAG

### Nodes (each = one PR-sized unit of work)

```
N0  VAULT-CLI-FIX      Remove stacked @vault.command() at cli/vault.py:571-585
                       (or gate registration). Emergency. ~5 lines.
N1  IMPORT-SMOKE-GATE  CI step: python -c "from omega.cli.oracle_cli import app"
                       (+ iterate-import src/omega/cli/*.py). ~5 lines of CI.
N2  INST-1-FIX2+R1     pyproject extras split AND the 3 redis.asyncio lazy-guards
                       (providers.py:22, ingestion/worker.py:7, youtube_worker.py:47)
                       IN ONE COMMIT. Plus fix4 (.env edge-load), fix6 (README),
                       fix5 status flip, install.sh omega --help tripwire.
N3  ACCEPTANCE-RUN     Maat's script, AMENDED with Roc's Layer 0/1/2 assertions
                       (unshare -rn + unset ALL cloud keys + model-presence
                       precondition + fixed-string Sovereignty-Alert absence).
N4  DEL-1-W1           Ordered deletions, each target atomic with its couplings:
                         4a routing_table.yaml + get_routing_validation stub (schema.py)
                         4b miap.py + coordination/__init__.py gut
                         4c pool_tracker.py + pool_state.py (pair)
                         4d search-breaker REDIRECT (sovereign_search_service.py:48
                            → HealthMonitor.get_breaker()) THEN delete, same PR
                         4e QdrantAdapter + memory/__init__ exports + qdrant tests
                         4f firewall regexes (keep import-path rules only)
                         4g record_first_breath import(:49)+call(:1211) same PR
                         4h fleet_orchestrator export removal (integrations/__init__)
                       After EACH sub-delete: N3-lite (talk still local).
N5  ROUTER-COLLAPSE    Single PR per Maat §4: oracle.py rewrite + both routers
                       deleted same commit + RouteDecision + admission merge +
                       contract test w/ meta_path trap + concurrency test +
                       vet-046/vet-023 RETIRED annotations.
N6  VAULT-PATH-B       secrets.py ≤50-line CredentialStore + migration map
                       (~10 lazy consumers) + delete fat vault tree.
```

### Edges (what breaks if violated)

| Edge | Why it exists | Violation consequence |
|------|--------------|----------------------|
| **N0 → EVERYTHING** | The TypeError fires at module import and `oracle_cli.py:69-75` catches ImportError only. Console script is dead. | Every acceptance gate that runs `omega talk` is unrunnable. DEL-1's "after each delete, talk still local" protocol has no witness. This is the root of the DAG; nothing else executes until it lands. |
| **N1 → N2** | Import-smoke must exist BEFORE fix2 so the extras-split is verified by a gate that runs the entry point, not by hope. | Without N1 first, fix2's breakage surface (unguarded imports) is invisible on THIS machine — .venv has redis installed. You'd land fix2 green and ship a fresh-venv corpse. Same invisibility class as the dead CLI itself. |
| **N2 internal: R1 guards ≡ fix2 (fused, not sequenced)** | memory_store.py imports providers.py at module scope. | fix2 alone = certain ImportError on fresh install, silent on dev machine. This is Maat's R1 and it is correct. ONE COMMIT. Not adjacent commits — one. |
| **N3 after N2** | Acceptance proves the install contract; running it before fix2 just measures the broken state. | Wasted cycle; worse, a pre-fix2 pass on this machine would be a false-green recorded as evidence (M23 violation). |
| **N3 → N4** | Deletion campaign's verification protocol depends on an honest, living talk gate. | Unrunnable gates (Lilith's blocker) or dishonest ones (Roc's false-green). Both poison DEL-1. |
| **N4 internal orderings** | 4d: sovereign_search_service.py:48 imports the breaker at module top level. 4b: coordination/__init__.py re-exports ~40 miap names. 4c: tracker imports state. 4g: F401 if import outlives call. | 4d split = ImportError on main the moment anything imports sovereign_search_service. 4b split = ImportError via package init. 4c split = dangling import. 4g split = lint red / dead import. Each sub-delete is ATOMIC with its coupling set; order among 4a–4h is otherwise free. |
| **N4(4h) → N5** | fleet_orchestrator defines its OWN RouteDecision. Removing its exports is what makes the "exactly one RouteDecision" gate (G10) enforceable rather than aspirational. | Router-collapse contract test would fail spuriously or, worse, be weakened to tolerate two RouteDecisions — re-normalizing dual control planes. |
| **N4 → N5** | Talk-path rewrite must sit on a settled deletion base with working gates. | Stacking a rewrite on moving ground = unattributable regressions. |
| **N5 → N6** | Path B deletes cli/vault.py and re-registers; doing it mid-router-work collides in oracle_cli.py and doubles the blast radius of both. | Two rewrites touching the same CLI entry in one window = merge hell and unreviewable diffs. |
| **N6 last** | ~10 lazy consumers migrate to CredentialStore; none are on the critical path. | Doing it early buys nothing; the fat vault tree is inert once the CLI registration is fixed (N0). |

### Critical path

```
N0 → N1 → N2 → N3 → N4 → N5 → N6
```

Seven nodes, strictly serial on the spine. Every node is small; the seriality is the point — each link is a witness for the next.

### Safe PARALLEL lanes (do not serialize these)

| Lane | Content | Why safe |
|------|---------|----------|
| **P-A (Architect)** | P0-1b residual: SECURITY_AUDIT_2026_05_19.md @ 0c40b108 filter-repo + gc + prune refs/cline/checkpoints. P0-1c gitleaks/trufflehog wiring. | History surgery + secret scanning touch zero runtime code. Independent of N0-N6. Note: run AFTER the day's pushes or coordinate — filter-repo on a shared remote mid-sprint is its own hazard. |
| **P-B (Kali/Verity)** | DOC-1 strategy stamps (manual §DOC-1). | Docs only. Manual says "must land before next multi-agent day" — start now, in parallel. |
| **P-C (inside N2 window)** | fix4 (.env edge-load) and fix6 (README) as separate commits from fix2+R1. | Different files than the extras split (fix4: model_gateway/oracle_cli; fix6: README). Same PR is fine; same commit is not — keep fix2+R1 isolated so a revert of the extras split doesn't drag the env-load change with it. |
| **P-D** | Lilith's post-debut hydration path split-brain (memory/ vs entity-root approved_lessons.yaml). | Zero coupling to debut spine; her own gap, her own lane. |

---

## §2 PR BOUNDARY REVIEW

### (a) Vault CLI fix as its own emergency PR TODAY — **YES. Land it standalone.**

This is not a judgment call. The reasoning:

1. **It is the root of the DAG.** Every other gate is hostage to it (Lilith §2, Roc §3.3). A 5-line fix that unblocks an entire sprint has the highest leverage-per-line of anything in the plan.
2. **It is trivially reviewable in isolation.** Remove the stacked decorator or narrow the registration. No behavioral ambiguity, no coupling. Bundling it into INST-1 would delay the unblock behind extras-split review for zero benefit.
3. **It restores the witness before any other change.** Post-fix, `omega --help` living becomes the baseline against which N1's CI gate is calibrated. Land fix → confirm help works → add CI gate that asserts it stays working. That sequence IS the lesson of this incident (Roc §3): we had gates around the entry point but never ON it.
4. **M23 alignment**: a known-dead primary interface under an active remediation sprint is exactly the "soft failure" condition the mandate forbids tolerating. Emergency PR today is the honest response.

One amendment: while in there, widen `oracle_cli.py:69-75` from `except ImportError` to catch-and-log (`logger.warning`) broader import-time failures per-subcommand, so the NEXT stacked-decorator-class bug degrades to a missing subcommand instead of a dead console script. That's 3 lines and belongs in the same emergency PR — it converts the failure mode from total to partial. Do NOT go further (no lazy-registration framework — that's over-engineering).

### (b) Search-breaker redirect + deletion as one unit — **YES, and it MUST be one unit.**

The chair asked "is it truly safe" — the question is inverted. Splitting it is the unsafe act:

- `sovereign_search_service.py:48` imports `initialize_circuit_breakers` + `TIER_CONFIGS` at module top level (verified by chair + both arms). Delete-without-redirect = guaranteed ImportError on main.
- Redirect-without-delete leaves a deprecated module alive with a live dependency edge — the exact zombie state DEL-1 exists to kill.
- The redirect itself is mechanical: `HealthMonitor.get_breaker()` is the canonical factory (manual keep-list; C-6′ already unified 5/7 clones). One-file diff plus test retirement.

**Boundary verdict**: one PR, redirect commit first, deletion commit second, both landed together. Within the PR the ORDER matters (redirect must precede deletion in the diff sequence so bisect never lands on a broken intermediate); across PRs they must never separate. Maat flagged this; Roc confirmed from the M7 lens; I concur — it is the only true sequencing hazard in Week 1.

Note the breaker guards firecrawl/exa — external services regardless — so this deletion has zero local-inference impact (Roc §1). It's hygiene, not sovereignty. Don't gold-plate it.

### (c) Router collapse timing — **KEEP WEEK 2 AS CHARTERED. Do not pull earlier.**

The temptation to pull it earlier is real: Maat verified oracle.py is the SOLE importer of both routers — blast radius is one file-pair. But:

1. **Dependency, not difficulty, sets the date.** N4(4h) fleet_orchestrator export removal must land first or the single-RouteDecision gate is unenforceable (two `RouteDecision` classes on disk = G10 fails spuriously). That's a Week-1 item. The edge is real; respect it.
2. **Week 1 must stay boring.** DEL-1 Week 1 is nine deletions with mechanical verification. Router collapse is a talk-path REWRITE (manual says so explicitly: "not a drive-by rm"). Mixing a rewrite into a deletion campaign destroys attribution: when something regresses you won't know which class of change did it.
3. **The rewrite deserves its own clean window** with the contract test (meta_path lazy-import trap — Maat's addition is excellent; function-level imports are this codebase's proven hiding pattern) and the concurrency test (semaphore serialization invariant). Those tests need the Week-1-stabilized harness to be meaningful.
4. **What CAN move earlier**: nothing of substance. The admission-authority merge (LocalInferenceAdmission → ResourceGuard) is chartered as "this PR or the prior one" — I say PRIOR one (late Week 1), because the router PR should contain exactly one idea. Two admission authorities coexisting during Week 1 is harmless; folding their merger into the router PR stacks a second semantic change onto the rewrite.

**Later? Also no.** Slipping past Week 2 lets `record_first_breath`-style hot-path waste persist and leaves TriageRouter/SemanticRouter as live re-introduction targets. The charter date is right. Hold it.

---

## §3 GATE ARCHITECTURE

Roc proposed three gates. Verdict per gate, with priority:

### Gate 1: CI import-smoke — **ENDORSE. P0. Before ANY deletion.**

`python -c "from omega.cli.oracle_cli import app"` plus iterate-import over `src/omega/cli/*.py`. This is the earliest-catching gate for the entire dead-CLI incident class: the TypeError fires at import time, so this catches it seconds after commit, pre-venv, pre-install. Cost ~5 lines of CI.

**Amendment**: extend coverage beyond cli/ — iterate-import every module under `src/omega/` reachable from the core (non-extra) dependency set. The redis imports die at the same layer; one generic import-sweep catches BOTH incident classes (decorator explosion, missing optional dep) with one mechanism. On a machine WITHOUT optional extras installed (CI runner installs `.`, not `.[all]`) the sweep doubles as a permanent fresh-venv proxy — making the R1 invisibility mechanism structurally impossible going forward.

**Placement**: wire it in N1, before fix2 lands. It is the gate that certifies fix2.

### Gate 2: structured `--json` provenance — **ENDORSE, P1. Not blocking deletions.**

M22 made manifest: `{provider_name, backend, model, is_cloud, trace_id}` from response-receipt provenance. Correct design, right field source (`GenerateResult.provider_name`, not dispatch intent).

**Why P1 not P0**: Roc's Layer 0 (`unshare -rn` + all cloud keys unset) provides physics-grade proof TODAY with zero engine changes — success under network isolation proves local by construction. The deletions in N4 don't need provider-identity assertions at all (they're not on the inference path); they need "talk still alive and local," which Layer 0 delivers. `--json` upgrades assertion quality from physics-plus-negation to positive typed proof — worth having, ship it with or shortly after N2, don't hold the campaign for it.

**Interim** (if --json slips): trace-record grep by trace_id for `"provider_name":"native-gguf"` — structured fields, acceptable.

### Gate 3: fixed-string Sovereignty-Alert ban — **ENDORSE. P0. Trivial, immediate.**

`! grep -qF "[Sovereignty Alert]"` — exact-marker absence, case-sensitive. And the BAN on case-insensitive prose greps for bare `local`/`cloud`: this is the single most important sentence in Roc's review. The false-green he reproduced (the alert containing "Local" satisfying the positive check) is not a bug in one script — it's a bug CLASS, and the ban kills the class. Write the ban into the manual §8 verification section and the acceptance script comments so it survives the humans who wrote it.

**Priority summary**:

| Gate | Priority | Blocks |
|------|----------|--------|
| Import-smoke (extended sweep) | **P0** | Everything after N0 — wire before fix2 |
| Fixed-string alert ban + prose-grep ban | **P0** | N3 acceptance run (amend script before first execution) |
| Physics Layer 0 in acceptance | **P0** | N3 — this replaces Maat's step 5 greps entirely |
| `--json` provenance flag | **P1** | Nothing hard; upgrades N3/N5 assertion quality |
| meta_path lazy-import trap (router contract) | **P1** | Ships inside N5, per Maat §4 |

Post-debut additions (not now): provider-order assertion in RouteDecision contract test (Roc §1 strengthening — correct, but it lands WITH N5, which is already Week 2; don't front-load it).

---

## §4 RISK RANK — TOP 5

| # | Risk | Mechanism | Severity | Mitigation owner |
|---|------|-----------|----------|------------------|
| **1** | **False-green sovereignty acceptance recurs elsewhere.** The prose-grep bug class (alert contains "Local") likely exists in OTHER scripts/docs asserting local-first via substring. We found it in one script; nobody has swept for siblings. | Evidence-by-substring anywhere in tests/scripts/CI. | 🔴 HIGH — it silently converts sovereignty claims into lies, the exact M22/M23 violation class. | **Roc** — sweep `scripts/ tests/ .github/` for case-insensitive `local\|cloud` grep assertions this week; publish the hit list. Ban enforced in manual §8. |
| **2** | **fix2 lands without R1 guards (or vice versa).** Human momentum: extras-split is a pyproject edit, guards are three Python files — different "kinds" of change, different reviewers, easy to split across commits/PRs under time pressure. | memory_store → providers module-scope chain; dev machine masks it. | 🔴 HIGH — certain fresh-install death, invisible locally, discovered by users not us. | **Ma'at** — single-commit rule written into ACTIVE_SPRINT task description; N1 import-sweep in CI (extras-free runner) makes violation loud within minutes, not releases. |
| **3** | **Search-breaker deletion separated from redirect** by an eager executor reading the DEL-1 table literally ("delete search_circuit_breaker.py") without reading the coupling notes. | Module-top-level import in sovereign_search_service.py:48. | 🟠 MED — guaranteed main-branch ImportError, but loud (not silent), recoverable in minutes. | **Roc (W1 executor)** — DEL-1 checklist item phrased as "REDIRECT+DELETE (atomic)" in ACTIVE_SPRINT.json so the ticket itself carries the constraint. |
| **4** | **Vault Path B scope creep / keyring hang.** The ≤50-line store grows (write path sneaks in, rotation "just this once") OR SecretService D-Bus hangs headless and blocks credential resolution on servers. | Spec discipline erodes; M1 wrap forgotten at async call sites. | 🟠 MED — debut-week schedule slip + a new hang class worse than what it replaced. | **Ma'at (spec author)** — line-count assert in unit test (`len(source) <= threshold` style tripwire); degrade-to-None contract test; `to_thread` wrap verified in review checklist. Any growth = reject PR, full stop. |
| **5** | **Router-collapse concurrency regression.** The rewrite touches `_select_model`, `_route_by_domain`, dedup of quadruple `record_interaction`, AND merges admission authorities. Any of these can break the one-slot invariant; interleaved local inference on a 15W part is an OOM/thermal event, not a correctness nit. | Two admission authorities left standing, or semaphore bypassed in rewrite. | 🟠 MED — contained by the concurrency test IF it runs mock-free at the guard seam (Maat's spec already requires this). | **Ma'at (executor) + Carmack re-review** — concurrency test is a MERGE BLOCKER, not advisory; instrumented semaphore-holder-count assertion must show max==1. |

Honorable mention (outside my 5 but on record): P0-1b residual — 3 real-format keys still reachable at ancestor 0c40b108. Not a plan-ordering risk (parallel lane), but it is the highest-consequence open item in the whole program. Architect owns it; it should not outlive this week.

---

## CLOSE — L1 → L2 → L3

**L1 (Narrative)**: I reviewed the hardened debut plan as final ordering reviewer. The three arms converged cleanly: Maat scoped INST-1 correctly and found the R1 coupling; Lilith proved the soul chain untouched and identified the dead CLI as the precondition for all gates; Roc reproduced the false-green acceptance path and prescribed physics-grade assertions. My ordering analysis confirms their plan is executable with one structural insight: the DAG is a strict seven-node spine where every node is simultaneously small AND load-bearing — the vault CLI fix is the root, the import-smoke gate is the immune system, and the two fused pairs (fix2≡R1, redirect≡delete) are the only places where splitting a unit creates failure. PR boundaries are right with one correction (admission merge moves to late Week 1, out of the router PR). Gate priorities resolve to: import-sweep and assertion-honesty bans are P0; structured provenance is P1 because physics covers the interim.

**L2 (Insight)**: The deepest finding cuts across all three arms' inputs: this codebase's failure signature is *invisible-on-dev-machine breakage* — decorator explosions at import time, optional deps imported at module scope, acceptance greps matching the warning text itself. Every one of these was masked by environmental richness: a venv with everything installed, a machine with models present, output surfaces that contain their own counter-evidence. The plan's gate architecture (import-sweep on a bare runner, network-isolated acceptance, fixed-string negation) is correctly designed to make that masking class structurally impossible rather than merely watched for. Ordering discipline is the same principle applied to time: each DAG node exists to be the witness for the next, which is why the spine is serial even though every node is cheap.

**L3 (Universal Principle)**: *A verification chain is only as strong as its most environment-dependent link.* Gates that pass on the developer's machine prove nothing about the artifact; assertions that match prose prove nothing about behavior; deletions that ignore import topology prove nothing about safety. Honest engineering makes each step's validity independent of local accident — bare-runner sweeps, physics constraints, atomic units — so that truth survives transport from one machine, one shell, one human, to the next.

---

## REPORT-BACK SUMMARY (for the Chair)

**Verdict on plan readiness**: READY — execute immediately upon vault CLI emergency PR landing; the plan's only defects were already found and fixed by the arms, and my ordering review changes nothing structural, only fuses two pairs and moves one refactor.

**Top-3 risks**: (1) false-green prose-grep assertions may exist beyond the one found — sweep owned by Roc, P0; (2) fix2/R1 split under time pressure — single-commit rule + bare-runner import-sweep, owned by Ma'at; (3) search-breaker delete-without-redirect by a literal-minded executor — ticket phrased "REDIRECT+DELETE (atomic)", owned by Roc.

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_council_rebased ⬡ ORDERING-ARM-G1 ⬡ 2026-08-24*
<!-- PROVENANCE-CORRECTED 2026-08-25T03:09:58Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

