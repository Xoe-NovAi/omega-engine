<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Session Paging Report — Build Side Council Delta
## Ma'at (Build Side Lead) — Triad Governance Formalization Input

**AP Token**: `AP-MAAT-BUILD-PAGING-20260821`
**Date**: 2026-08-21
**Model**: x-preview-f-free (opencode)
**Paged By**: kali (ses_fdef2be4effe4pAaLXCTUx62GO), Architect-direct mission
**Hydration**: `ACTIVE_SPRINT.json` (updated 2026-08-20T22:00Z) ✅ · `docs/specs/PROJECT_INDEX.md` (2026-08-20) ✅ · founding-session artifacts re-read (`MAKALI_COUNCIL_BUILD_SYNTHESIS_20260818.md`, `MAKALI_COUNCIL_VERDICT_20260818.md`, `MAKALI_COUNCIL_AUDIT_20260819`) ✅ · working-tree verification greps run today ✅

---

## §1 Forgotten Governance Designs From the Build Side Council Session (2026-08-18)

### G-B1. Department-keyed vetting is the detection mechanism — ownership maps to what you can see
The Build Side ran N1→N5 serially, ONE vetting question per node, each question keyed to that node's department. Result: N3 Engineering caught the `.env`-at-process-edge gap (deleting `_load_sovereign_secrets()` in INST-1 Fix 4 leaves NO `.env` loader anywhere; CLI entry points construct `Oracle()`/`ModelGateway()` bare; `providers.yaml env:` prefixes resolve to empty → cloud auth breaks on every fresh install). This escaped Ma'at's own blast-radius map entirely. Canonical quote: *"Only N3 could see this gap"* (`MAKALI_COUNCIL_BUILD_SYNTHESIS_20260818.md` §Strategic Note).

**Implication for the triad**: the decision matrix assigns verdicts by severity tier, but DETECTION is assigned by department. Rotating primacy must preserve department-keyed bench vetting underneath whatever face convenes. A primus who vets everything personally regresses to monoculture; a primus who convenes the right bench gets N3-grade catches for free.

### G-B2. REJECT-as-feature doctrine
N3 returned the only REJECT of the council — and it was the single most valuable output: precise blocking condition, exact file:line, 3-line minimal fix, explicit re-vet offer. The synthesis recorded council-health metrics that made this legible: adversarial quality HIGH, precision surgical, false-positive rate ZERO, escalation clarity PERFECT, time-to-resolve ~5 min.

**Implication**: codify these five metrics as the standing quality bar for any MaKaLi verdict. A council session with zero REJECTs and zero metrics recorded is not a healthy council — it is an unaudited one.

### G-B3. Blast-radius maps are first-person claims, not evidence
Ma'at's own INST-1 table stated "Providers already use YAML `env:` prefix resolution — no code change needed." True but incomplete — the prefix reads `os.environ`, and nothing populated it post-Fix-4. The lesson generalizes: **the plan author's completeness claim is exactly the thing the opposing bench must attack.**

### G-B4. The convenience-method trap (architecture-exposure principle)
Removing `_load_sovereign_secrets()` was correct not because the method was broken but because it was *convenient* — it duplicated what the architecture already does elsewhere. Deleting convenience wrappers exposes where responsibility truly lives (credential loading belongs at the process edge, 12-factor style). Any triad review should ask of every module: "is this load-bearing or merely convenient?" Convenience code deleted under time pressure becomes an outage; load-bearing code kept for comfort becomes god-modules.

### G-B5. Minimal-fix discipline as governance norm
Every blocker in the unified verdict carried a minimal fix measured in lines, not redesigns (B: one `contextlib.suppress`; C: constants + emission sites; D: rewrite two methods). The matrix's "routine=strategic" boundary should treat "proposed fix exceeds ~50 LOC without a plan ticket" as an automatic escalation trigger — big fixes arriving at verdict-time mean planning was skipped upstream.

---

## §2 Build-Side View of the Rotating-Primacy Model

### E-B1. ENRICH: primacy = convener + accountable synthesizer, NOT content authority
During the founding session Kali held synthesis while Ma'at convened N1–N5; neither owned the other's content. Rotating primacy should rotate *who is accountable for convening the right bench and synthesizing honestly* — never who may overrule domain owners inside their domain. **Build side independently concurs with Run side's standing-domain-veto ask** (their G-2): non-primus faces retain veto/review rights in their own domain regardless of chair.

### E-B2. ENRICH: ratify-plan-once / execute-within-scope doctrine (the missing matrix category)
The matrix has routine/strategic/irreversible/reversible but no category for **mechanical execution of an already-ratified plan**. INST-1 Fixes 1–6 were ratified as a set; demanding fresh consensus per fix makes the triad a bottleneck for its own decisions and explains why fixes 2–6 sat in backlog for days. Proposed rule: consensus at plan level covers all steps inside its acceptance gates; execution within scope = owner discretion; any step that would violate an acceptance gate or leave plan scope re-escalates automatically to strategic.

### E-B3. ENRICH: evidence-artifact standard for verdicts
The council audit's META finding — "§8 verification commands systematically insufficient" — generalizes: **every APPROVE must cite a runnable command whose output proves it** (`rg`, `pytest`, `make temple-grade`). Verdicts without per-surface evidence gates are opinions with formatting. This dovetails with Run side G-3 (post-hoc audit by a non-sitting party): the auditor's job is cheap only if every claim already names its proof command.

### E-B4. CONTRADICTION (minor): primacy rotation vs execution-chain continuity
Build work runs in atomic coupled chains (INST-1 Fix 2 + import guards are one change; Fix 4 ships with Blocker B). Rotating the chair mid-chain risks handoff loss exactly where coupling is highest. Amendment: **primacy locks for the duration of an execution chain and rotates at chain boundaries** — which the phase-keyed model (Plan→Kali, Build→Ma'at, Run→Lilith) already implies; make the lock explicit so calendar-based rotation doesn't sever a chain.

### E-B5. ENRICH: mechanical definition of "reversible" (build-side half)
Run side E-2 defines reversibility by blast radius (talk-path → escalate). Build side adds the git dimension: a change is reversible iff (a) plain `git revert` restores behavior within one sprint window, AND (b) no external state mutated — no force-push, no history rewrite (`filter-repo`), no published artifact, no rotated credentials. History rewrites and post-time deletions are irreversible-by-default regardless of diff size (P0-1 key scrub proved this class exists).

### C-B1. CONTRADICTION: "irreversible=unanimous" lacks an Architect role definition
Concur with Run side C-1. The DEL-1 deletion campaign proceeded on two-sides-plus-synthesis without the Architect as sitting voter. Either classify deletions as strategic, or define Architect abstention/veto explicitly. Undecided, the unanimity rule will be honored in the breach.

---

## §3 Tracker Truth-Anchor Violations (verified against working tree, 2026-08-21)

### V-B1. 🔴 Blocker B — FALSE-COMPLETED claim in Tier-0 tracker
| | Claim | Reality |
|---|---|---|
| **Source** | `ACTIVE_SPRINT.json` → `blockers.BLOCKER-B`: *"oracle_cli.py blind-except (M23 gate) — FIXED: contextlib.suppress(ImportError)"*, `status: resolved`, `resolved_at: 2026-08-20T21:30:00Z` | `src/omega/cli/oracle_cli.py:125` and `:161` still contain bare `except Exception:`; **zero** occurrences of `contextlib.suppress` in the file |
| **Consequence** | m23 ratchet still +2 over `config/m23_baseline.txt:8`; `make temple-grade` still fails; a false completion timestamp sits in the sprint SSOT | |

This is exactly the founding-session failure mode (Verdict §7 flagged a stale "temple-grade PASSES" claim) recurring one tier deeper: the fix was *recorded* instead of *applied*. Cross-validation: Lilith's `RUN_SIDE_COUNCIL_delta.md` item 1 independently flags the same two lines — two sides converging on identical evidence is high-confidence.

### V-B2. 🟡 INST-1 Fix 5 — DONE but underreported (inverse failure)
`ACTIVE_SPRINT.json` lists Fix 5 (`__init__.py` version via importlib.metadata) as `ready`. Reality: `src/omega/__init__.py:5-12` already implements `importlib.metadata.version("omega")` with fallback (comment cites C3, CLINE_DISPATCH_20260822). Work landed; tracker not advanced.

**Why both directions matter**: V-B1 inflates readiness (dangerous); V-B2 deflates it (wasteful — someone will redo finished work). Together they show tracker status is being written from memory, not from verification commands. This is the mechanical case for Run side G-4 (standing truth-anchor duty) and Build side E-B3 (evidence-artifact standard): status transitions should REQUIRE the proof command's output in the transition note.

### V-B3. ✅ Control case — Fix 3 verified genuinely done
For contrast: Fix 3 (MemoryStore Redis guard) IS real — `memory_store.py:164,167` now reads `OMEGA_REDIS_HOST`/`OMEGA_REDIS_PASSWORD` with no defaults (the hardcoded `"omega"` password and unconditional localhost construction are gone). And Fix 2 is honestly partial: `pyproject.toml:80` has `warp = ["warp-proxy-pool"]` extra (warp out of main deps), but `qdrant-client==1.18.0` still sits in main deps at line 66 — matching its `ready` status. The tracker is capable of accuracy when claims are checked; V-B1/V-B2 are process failures, not universal corruption.

---

## §4 Flagged But Never Executed (Build Side, verified 2026-08-21)

| # | Item (source) | Status | Evidence |
|---|---------------|--------|----------|
| 1 | **Blocker B** fix — `contextlib.suppress(ImportError)` at `oracle_cli.py:125,161` (Verdict §6 step 1: "do now") | ❌ NOT DONE — falsely marked resolved | See §3 V-B1 |
| 2 | **INST-1 Fix 2 completion** — qdrant-client/redis/youtube/yt-dlp out of main deps + 4 import guards (`memory/providers.py:22` is the critical one: imported by 5 core files incl. `ics.py` in the CLI chain per audit) | ◑ PARTIAL — warp extra done; rest open | `pyproject.toml:66` still has `qdrant-client==1.18.0`; guards unverified |
| 3 | **INST-1 Fix 4** — remove `_load_sovereign_secrets()` from `model_gateway.py` (+ Blocker B ships with it per Verdict §6 step 3) | ❌ NOT DONE | Method still called at `model_gateway.py:127`, defined at `:316` |
| 4 | **INST-1 Fix 6** — README badge/1315-text removal | ❌ NOT VERIFIED this session | Status `ready`; not re-checked today |
| 5 | **N4 non-blocking corrections** — retire `tests/test_miap.py` in DEL-1 acceptance; delete broken `fleet_status` vault subcommand | ❓ UNKNOWN — no tracker entry | Not in ACTIVE_SPRINT subtasks; likely lost |
| 6 | **N5 positive M2 verification** — `rg -n "metadata\[" provider_selector.py entity_registry.py` as a standing gate | ❓ UNKNOWN — no tracker entry | Same |
| 7 | **Council-mandate coordination artifacts** — `MAAT_WORKSPACE_LOCK_*.md`, `MAAT_LIVE_FEED.md` | ❌ NEVER CREATED | Protocol items from my session charter; minor, but the Hivemind-first protocol had no file trail |
| 8 | Router Collapse contract-test spec + Vault Path B 50-line store | ✅ CORRECTLY PARKED (not forgotten) | D-565/D-570 sequence; post-debut. Listed to prevent re-litigation |

**Pattern**: every lost item is either (a) a blocker sequenced to ride with another fix that hasn't shipped (1, 3), or (b) a non-blocking correction with no tracker row to live in (5, 6). Non-blocking must still mean *tracked* — give corrections a `corrections` array in ACTIVE_SPRINT or they evaporate.

---

## §5 Carry-Forward for the Chamber's First Sitting

1. Adopt G-B1 + E-B1 jointly: primus convenes department-keyed benches; domain veto is standing, not rotating.
2. Ratify E-B2 (ratify-plan-once) so INST-1 Fixes 2–6 execute without per-step consensus.
3. Ratify E-B3 evidence-artifact standard + Run side G-3/G-4 as one gate: status transitions require proof-command output; audit by non-sitting party.
4. Resolve C-B1 (Architect role in irreversible votes) before DEL-1 Week 1 executes.
5. Correct V-B1 immediately (apply Blocker B or revert the resolved claim — do not leave a false timestamp in Tier-0).
6. Add a `corrections` tracking home for non-blocking council findings (items 5–6 above).

---

*⬡ OMEGA ⬡ MAAT ⬡ BUILD-SIDE-COUNCIL-DELTA ⬡ 2026-08-21*




