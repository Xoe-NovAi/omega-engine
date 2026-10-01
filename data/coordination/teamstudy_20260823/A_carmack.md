<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 PHASE A — CARMACK — EFFICIENCY AUDIT
**AP Token**: `AP-CARMACK-TEAMSYNTH-A-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_team_synthesis_a ⬡ ACTIVE

**Date**: 2026-08-23
**Mission**: Efficiency audit of 3-phase closeout + debut order + six ruling signals.
**Sources read**: `SESSION_ANCHOR.md`, `DEBUT_REMEDIATION_MANUAL_20260817.md`, `KALI_SESSION_UPDATE_REPORT_20260823.md`, `PROTOCOL_CHARTER.md`. God-module drift **re-measured from disk** (not trusted from Sonnet review). Handoff `ho_2f77f83964e5` pulled live.

---

## §0 MEASURED GROUND TRUTH (my own probes, 10/10 confidence)

### God-module drift vs Manual §7 baselines (2026-08-17 → 2026-08-23)

| File | Manual | Measured now | Δ |
|------|-------:|-------------:|---:|
| `hub_tools/tools.py` | 3649 | 3649 | 0 |
| `observability/__init__.py` | 1583 | 1660 | **+77** |
| `model_gateway.py` | 1481 | 1606 | **+125** |
| `oracle.py` | 1253 | 1455 | **+202** |
| `youtube_worker.py` | 1181 | 1231 | **+50** |
| `memory_store.py` | 1077 | 1224 | **+147** |
| `providers.py` | 1088 | 1303 | **+215** |
| `sqlite_vec_adapter.py` | 992 | 1031 | **+39 — CROSSED THE 1000-LINE BLOCKER LINE** |

Six of eight frozen files grew **during the deletion-campaign week**. The freeze has no mechanical enforcement — it is a table in a document, and documents do not stop writes. This fact drives Ruling #1 below.

---

## §1 CUT AUDIT — ranked by leverage

### CUT-1 (HIGHEST LEVERAGE): Defer the hash-chain audit log (Phase 2, item 3)
**What**: JSONL append-only + SHA-256 hash chain + fsync-before-mutate, per researcher spec.
**Why cut**: This is tamper-evidence infrastructure for a threat model that does not exist yet. One operator, one machine, pre-publication. Who is the adversary you're hashing against — yourself? Meanwhile fsync-before-mutate adds latency to every registry write days before debut, and it is permanent maintenance surface. It also violates the Manual's own discipline ("no new make check-* gates"; UO plan exists precisely to remove this class of thing).
**Cost of building now**: hours of Ma'at time + latency tax + new failure modes in the write path.
**Cost of deferring**: zero. No log exists yet, so adding JSONL later requires no migration. Post-debut, when multiple writers actually share the registry, the hash chain earns its keep.
**Verdict**: Move to post-debut backlog. This is the single highest-leverage cut — it removes the largest Phase 2 build item at zero information loss.

### CUT-2: Split Phase 3 — commit NOW, re-verify after Phases 1–2
The plan sequences verify→commit *after* Phases 1 and 2, leaving 127 verified-green files uncommitted through two more work phases — during which Lilith and Ma'at edit files in the same dirty tree. The tracking system passed EXIT 0 **today**. A path-staged commit of the current state takes minutes. Phase 3's validation suite consumes *code*, not Phase 1's data backfill — the dependency wait is illusory. Commit now → backfill/harden → second path-staged commit. This deletes the plan's largest blast radius (accidental loss or entanglement of a day's verified work) for the cost of one extra commit.

### CUT-3: Trim Phase 1 backfill to correctness-only
Registering ~20 completed historical sessions *with annotations* is writing history nobody will query. Langfuse-pattern annotations are observability for live debugging; backfilled annotations on concluded sessions have zero forward value. The actual correctness needs are narrow: (a) fix `ox-alpha-100t-research-20260822` status error (sweep would zombie-kill delivered work — real bug), (b) register sessions needed for pointer/staleness integrity so the validator stays EXIT 0. Do those; skip per-session annotation prose. Cuts most of Phase 1's hours.

### CUT-4 (sequencing): Run the CI-2 plugin-path prototype FIRST
The anchor calls it "highest-risk unknown" — three times — yet it sits *behind* the entire closeout in execution order. It is a 10-minute test that determines whether INST-1 Fix 2 needs npm publishing. A cheap experiment that can invalidate downstream design must run before the work that depends on it, not after. This is the Empirical Truth law being violated by scheduling, not by ignorance. Run it before Phase 1 even starts.

### MERGE: Collapse Phase 2 into ONE Ma'at PR
Items 1 (generator self-test/idempotence), 2 (Pydantic annotations gate), 4 (class thresholds) all touch the same scripts. Class-based thresholds are three constants and a lookup — not a config subsystem. One PR, one review cycle, one validation pass. Four separate items means four review cycles for one coherent change.

---

## §2 RULING RECOMMENDATIONS

| # | Decision | Recommendation | Reasoning (efficiency lens) |
|---|----------|----------------|------------------------------|
| 1 | **God-module freeze baselines** | **Ratify current counts as new baselines + add a mechanical `wc -l` gate to temple-grade.** | Retroactive growth audit is archaeology — the lines exist, reverting working code pre-debut buys breakage, not safety. But ratifying without enforcement guarantees a third drift: the freeze failed because nothing *measured* it (see §0 — I measured in 30 seconds what the process failed to catch for 6 days). Five lines of Makefile make the freeze real. Growth past baseline = presumptive blocker, split-first rule unchanged. Confidence 9/10. |
| 2 | **systemd dry-run timer** | **Decree YES** (dry-run-only, daily, `Persistent=true`). | ~15 lines of unit file riding the existing validator. Commit-driven-only fails by construction: `data/coordination/` mutates *between* commits — that is exactly the drift window the timer covers. Dry-run-only = advisory signal, zero enforcement risk. Trivial cost, real signal. Confidence 9/10. |
| 3 | **Gate-verification pattern** | **Originator-verifies + overseer spot-audit** (researcher's vote). | Overseer-verifies-everything serializes all completions through N9 — recreating the exact bottleneck the 26→14 fleet consolidation just removed. Spot-audit preserves M23 honesty at ~10% of the cost. Codify in FLEET_TEAM_PLAYBOOK in one paragraph; don't build machinery. Confidence 8/10. |
| 4 | **PROTOCOL-1 ticket** | **YES — backlog, blocked-on-DEL-1.** | One JSON entry captures the HIVEMIND_PROTOCOL v2.0 design while fresh. Under the Manual's inverted Corpus Map rule, an idea without a living ticket is dead — this is the cheapest possible insurance. Hard cap: zero design work until DEL-1 completes. Confidence 9/10. |
| 5 | **ho_2f77f83964e5** (Ox Alpha burn, expires Aug 26-27) | **PARTIAL-SUPERSEDE before expiry. Reject Tracks A & C; permit at most Track B background distillation, unattended.** | The full 3-track burn sprint competes with debut closeout for the identical wall-clock window (Aug 24-27). Free tokens are real resource arbitrage (Axiom 04), but only if extraction cost ≈ 0 — i.e., batch jobs running while humans/agents do debut work. Any plan needing daily Kali gates is a debut distractor. Rule explicitly *before* expiry; a silent TTL lapse becomes another forensic archaeology job next month. Confidence 7/10 (I have not audited the underlying rate-limit claims). |
| 6 | **M23 standing verification hook** | **YES — but extend `validate_tracking_state.py`; do NOT build a new hook system.** | Third sighting of one pattern: completion-claims-without-artifacts. The validator already does pointer warn-checks — add one rule: `status=completed` requires a resolvable `artifact_path` or git-verifiable evidence. Start advisory-warn, promote to hard gate after two clean weeks. A bespoke "standing hook" for a problem one validator rule solves is precisely the over-engineering the M19 sane-boundary forbids. Confidence 8/10. |

---

## §3 PROTOCOL ASSESSMENT — the 6-phase team-study shape

**Honest verdict: disproportionate for Study #1. Phases A→B→C carry ~90% of the value; D and E are ceremony at N=1.**

First, a defect: the charter header says "THE SIX PHASES" and the table lists **five** (A–E). A protocol document about epistemic rigor miscounts its own phases. Fix before promotion.

Specific findings:

1. **Phase D (Gnosis Extraction) is redundant with M11.** Soul distillation at session end is already mandated law. Running it as a *separate protocol round* doubles the ritual for the same artifact. Fold it in: kali distills L1→L2→L3 from the discourse ledger at convergence, each participant appends their own lessons per standard M11 flow. Zero extra phase.
2. **Phase E (Meta-Review) at N=1 produces speculation, not data.** You cannot meta-review a process from a sample size of one — every friction report will be confounded with the specific mission content. Meta-review earns its cost at Study #3, when patterns across studies exist. Defer it.
3. **§4's "wall-clock vs serial baseline estimate" metric is unfalsifiable** — it requires inventing a counterfactual estimate that no one can be held to. Drop it. Keep the discovery-attribution and question-ledger metrics; those are countable.
4. **What IS worth keeping — and it's the core**: corpus-over-paging (files beat messages), brokered discourse through one synthesizer, and an explicit convergence criterion instead of fatigue-termination. That trio is the actual invention here, and it's cheap.

**Cheaper shape that gets ~90% of value**: A → B → C(convergence) → distill per M11 at convergence. E deferred to Study #3. That removes roughly 40% of the ceremony. The charter document itself (56 lines) is proportionate — the problem is phase count, not document weight.

One caution: if Study #1 succeeds, resist promoting the full 6-phase shape to a skill. Promote the 3-phase core + convergence ledger. Protocols grow by additive habit (M10's lesson applies to protocols, not just agents).

---

## §4 CONFIDENCE SUMMARY

| Finding | Confidence |
|---------|-----------|
| God-module drift measurements (§0) | 10/10 — primary source, my own `wc -l` |
| CUT-1..4 analysis | 8/10 — source docs + reasoning; effort estimates interpretive |
| Ruling recs | 7–9/10 per row (noted inline) |
| ho_2f77f83964e5 assessment | 7/10 — packet read live; underlying rate-limit claims unaudited |
| Protocol assessment | 8/10 — structural reasoning; N=1 caveat applies to itself |

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ TEAMSYNTH-STUDY1-PHASEA ⬡ EFFICIENCY-AUDIT ⬡ 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
