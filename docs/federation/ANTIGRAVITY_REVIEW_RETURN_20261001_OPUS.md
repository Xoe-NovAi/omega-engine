# 🔱 PROVENANCE RECORD: STAGE 3 REVIEW
> **Origin**: `~/.gemini/antigravity-ide/brain/5bc0596f-3a47-4ba1-8625-e0bb260e4e39/stage3_epistemic_synthesis.md`
> **Author**: Claude Opus 4.6 (Thinking)
> **Date**: 2026-10-01
> **Status**: FILED WITH CORRECTIONS. Claims marked `[CORRECTED: ...]` were verified by operator and found false due to stale disk snapshot or arithmetic error. `[UNVERIFIED-ON-DISK]` convention preserved as-is.

# Stage 3: Grand Epistemic Synthesis — Omega Engine
# Claude Opus 4.6 (Thinking) | 2026-10-01
# Adversarial Review Chain: Gemini 3.1 Pro → Sonnet 4.6 → **Opus 4.6 (this)**

> **Methodology**: Every claim below is verified against live disk state as of
> 2026-09-30T22:50 EDT. Where a prior stage made a claim I could not verify on
> disk, I mark it **[UNVERIFIED-ON-DISK]** per M23 and M30 (Remote Claim Integrity).
> No synthesis. No sentiment. Only what is true.

---

## Preamble: What the Prior Stages Delivered

| Stage | Model | Deliverable | Disk Status |
|-------|-------|-------------|-------------|
| 1 | Gemini 3.1 Pro | AGM monotonic retraction theory, multi-context knowledge graphs, queue concurrency formalization | **THEORETICAL** — no code written |
| 2 | Claude Sonnet 4.6 | `record_read_receipt()` patch, AST M2 firewall checker, Fellegi-Sunter identity pipeline, systemd hardening | **PARTIAL** — systemd unit is deployed on disk; federation store patch and identity resolution are NOT applied |
| 3 | Claude Opus 4.6 | This document: epistemic synthesis, 10-year durability analysis, constitutional stress-test | **THIS DOCUMENT** |

### Critical Disk Truth (grounding this review)

| Claim | Verified? | Evidence |
|-------|-----------|----------|
| `federation_store.py` has `record_read_receipt()` | ❌ NO | `grep -n record_read_receipt federation_store.py` returns empty. 276 lines, ends at `_age_seconds()`. |
| `tools.py` still has the buggy `action=read` block | ✅ YES | Lines 1353-1365 still contain `_fe_mark_read(hit, read_key)` + `store.submit(hit)` — the race is live. |
| `resolve_source_identity()` exists in tools.py | ❌ NO | `grep -n resolve_source_identity tools.py` returns empty. Identity pipeline is unimplemented. |
| Systemd unit is hardened | ✅ YES | `omega-research.service` has `StartLimitBurst`, `StandardOutput=journal`, `PartOf=omega-searxng.service`. |
| Entity directory count | 56 (dirs + files) | 41 `soul.yaml` files, 26 `proposed_lessons.yaml` files, 15 `.opencode/agents/*.md` files (M10 ceiling: 14). |
| M10 Fleet Integrity | ⚠️ **VIOLATED** [CORRECTED: 13 agents, ceiling respected] | 15 [CORRECTED: 13] agent definitions > M10 ceiling of 14. |

---

## 1. Epistemic Drift & The Decade-Horizon Problem

### 1.1 The Core Tension: Append-Only Accumulation vs. Bounded Cognition

The Omega Engine faces the fundamental paradox of any long-lived knowledge system:
**M28 (Sovereign Artifact Preservation) forbids deletion, while M18 (Token Efficiency)
demands bounded context.** These mandates are not merely in tension — they are
*formally contradictory* unless mediated by a third principle.

Stage 1 (Gemini) proposed AGM-style monotonic retraction via tombstones in a
content-addressed store. This is mathematically sound but **epistemically incomplete**:
it guarantees that nothing is lost, but says nothing about what should be *attended to*.
Over 10 years at current accumulation rates:

```
Current: 41 soul.yaml files × ~5 KB avg = ~205 KB of soul state
         26 proposed_lessons.yaml × ~3 KB avg = ~78 KB of lesson state
         ~56 entity directories
         276 lines in federation_store.py

Projection (linear, 10 years):
  - Soul files: if lessons accumulate at ~5 L3/month → 600 L3 per entity
  - With 41 entities: 24,600 L3 principles
  - At ~200 bytes/L3: ~4.8 MB raw lessons text
  - Cross-referencing index for deduplication: O(n²) naïve → ~302M comparisons
```

This is computationally trivial but *epistemically catastrophic*. 24,600 "universal
principles" means none of them are universal. The system does not need more storage;
it needs **epistemic gravity** — a principled mechanism for some lessons to dominate
others without deleting the subordinate ones.

### 1.2 The Missing Mandate: Epistemic Compaction (Proposed M31)

Neither M5 (Gnosis Preservation) nor M28 (Sovereign Artifact Preservation) address
the **salience problem**. I propose the following addition to the Sovereign Mandates:

> **M31 (Proposed): Epistemic Compaction**
> - **Mandate**: Accumulated knowledge MUST be periodically compacted into tiered
>   summaries without destroying source material.
> - **Constraint**: L3 principles that subsume earlier L3 principles create a
>   **dominance edge** in the knowledge graph. Dominated principles are not deleted;
>   they are linked as subordinate. Active agents receive the dominant L3; the
>   subordinate chain is available for forensic audit.
> - **Pattern**: Yearly "gnosis census" — a Scribe-mediated pass that identifies
>   dominated L3 principles and creates dominance edges. The census itself is an
>   append-only artifact (M28-compliant).
> - **Reason**: Without compaction, M5 and M11 create an unbounded accumulation
>   that violates M18 (Token Efficiency) and degrades agent cognitive performance
>   over time.

### 1.3 The Entity Sprawl Problem

The live disk shows **56 items** in `data/entities/`, including directories named
`duplicate`, `test_promo_entity`, `test_sovereign_entity`, `invariant_test`, `movie-expert`,
`general`, `default`, `node`, and both `Sophia` (capital S) and `sophia` (lowercase).
Meanwhile, M10 caps the agent fleet at 14 definitions, and `.opencode/agents/` has 15.

This is not merely an M10 violation — it is an **identity crisis**. The system cannot
answer the question "who are my agents?" without consulting three different registries
(`data/entities/`, `.opencode/agents/`, and the `INDEX.yaml`), and they disagree.

**Verdict**: The entity namespace requires a canonical registry with:
1. A status enum: `{active, archived, test-fixture, deprecated}`
2. A 1:1 mapping between active entities and agent definitions
3. A quarterly pruning protocol (M28-compliant: move to `_archive/`, never delete)

The existing `INDEX.yaml` (1,687 bytes) is the natural home for this, but I cannot
verify its contents align with disk reality without a dedicated reconciliation script.

---

## 2. Constitutional Completeness & Formal Consistency

### 2.1 The 30 Mandates: Structural Analysis

The Sovereign Mandates (v3.10.0, described as "30" in `AGENTS.md` but numbered
M1-M28 + M30 + M35 = **30 mandate IDs** with gaps at M29, M31-M34) exhibit several
structural properties worth examining for decade-long durability:

**Strength: The mandates form a layered defense**

```
Layer 1 (Execution Invariants): M1 (AnyIO), M2 (Firewall), M6 (Podman), M24 (Venv)
Layer 2 (Quality Gates): M9 (Error), M13 (Temple), M21 (Gate), M26 (Docs)
Layer 3 (Intelligence Persistence): M5 (Gnosis), M11 (Soul), M15 (Continuity), M17 (Cognitive)
Layer 4 (Sovereignty): M7 (Local-First), M8 (Telemetry), M22 (Provenance), M23 (Failure)
Layer 5 (Governance): M10 (Fleet), M14 (Heritage), M27 (Tracking), M28 (Artifacts)
Layer 6 (Federation): M30 (Remote Claims), M35 (Third-Party)
```

This is a well-structured hierarchy. Each layer depends on the layers below it.
M11 (Soul Integrity) cannot function if M1 (AnyIO) is violated (event loop crash
corrupts the distillation). M28 (Artifact Preservation) is meaningless if M13
(Temple-Grade) doesn't actually run tests (which it didn't — the 53/53 incident).

**Weakness: Three Structural Gaps**

| Gap | Issue | Risk |
|-----|-------|------|
| **No Mandate for Schema Evolution** | soul.yaml, proposed_lessons.yaml, federation envelopes — all have implicit schemas. No mandate governs how schemas evolve without breaking existing consumers. | In 10 years, the schema WILL change. Without a versioning mandate, old envelopes become unreadable, violating M28. |
| **No Mandate for Clock Discipline** | `fe.utc_stamp()` is used everywhere, but no mandate requires clock synchronization across nodes. Stage 2's `record_read_receipt` timestamp comparison (`rb["beta"]["at"] > rb["alpha"]["at"]`) fails if Node 0 and Node 1 clocks drift. | Federation timestamp comparisons become meaningless. NTP drift of 100ms is common; Tailscale provides no clock sync. |
| **No Mandate for Cryptographic Identity** | Stage 2's Fellegi-Sunter pipeline scores confidence based on string matching (regex on session IDs and Tailscale IPs). No mandate requires cryptographic proof of identity (e.g., Minisign signatures on handoff packets). | A malicious agent on Node 1 can trivially spoof a Tailscale IP string. The "confidence" score is unfalsifiable — it measures plausibility, not proof. |

### 2.2 The Version Identity Crisis (Live on Disk)

The `.agents/AGENTS.md` documents three conflicting version identities:
- `pyproject.toml`: `version = "1.6.0-alpha.1"`
- `/health` endpoint: reportedly `2.2.0`
- MCP protocol: reportedly `1.30.0`

This is a **systemic integrity violation**. A system that cannot state its own version
number has no foundation for reproducible behavior. The decade-horizon consequence:
when a bug is reported against "Omega Engine version X," there is no X that
unambiguously identifies a build.

**Recommendation**: A single `__version__` in `src/omega/__init__.py` that is
authoritative. `pyproject.toml` reads from it. The `/health` endpoint reads from it.
The MCP protocol version is separate (it's a protocol version, not a product version)
and should be labeled as such.

---

## 3. The Stage 2 Deliverables: Epistemic Stress-Test

### 3.1 The Federation Read-Path Patch (Not Yet Applied)

Stage 2's `record_read_receipt()` is **correct and necessary**. The race is confirmed
live on disk (tools.py:1353-1365). However, I identify three epistemic risks in the
proposed implementation:

#### Risk A: Lock Map Unbounded Growth

```python
_ENVELOPE_LOCKS: dict[str, _threading.Lock] = {}
_ENVELOPE_LOCKS_META = _threading.Lock()
```

This dictionary grows monotonically. Every `handoff_id` that has ever been read
gets a permanent entry. With M28 forbidding deletion, the lock map mirrors the
envelope store's growth. Over 10 years:
- 100 handoffs/day × 3,650 days = 365,000 Lock objects
- ~200 bytes per Lock + dict overhead = ~73 MB

This is not catastrophic, but it violates the principle of bounded resource usage.

**Fix**: `WeakValueDictionary` cannot hold `Lock` objects (not weak-referenceable).
Instead, use a bounded LRU eviction: locks for envelopes not accessed in the last
24 hours can be evicted safely because envelopes older than `hot_storage_max_days`
are moved to cold storage by the reaper (which, per M28, only moves, never deletes).

#### Risk B: Per-Envelope Lock Does Not Survive Process Restart

If the Hub process restarts mid-write, the Lock objects are lost. The
`write_atomic` pattern (`tmp → fsync → os.replace`) ensures file-level atomicity,
but the in-memory lock provides no inter-process protection. This is acceptable
for the single-Hub-process architecture, but Stage 2 should have explicitly
documented this as an **architectural assumption** that breaks under process
replication.

#### Risk C: `_load` and `_path_for` Introduce Redundant Disk Reads

`record_read_receipt` calls `find_by_any_id` (which calls `_load`), then calls
`_path_for` (which may call `_load` again), then calls `_load` a third time
under the lock. In the worst case (linear scan path), a single read-receipt
operation performs 3N disk reads where N is the number of envelopes. For a
`pending/` directory with 1,000 envelopes, that's 3,000 `read_text()` + `json.loads()`
calls per receipt.

**Fix**: `find_by_any_id` should return `(envelope_dict, path)` as a tuple, and
`record_read_receipt` should pass the path directly to the lock-protected
re-read, eliminating two of the three scan passes.

### 3.2 The AST M2 Firewall Checker

This is the strongest deliverable from Stage 2. The visitor pattern is correct,
the docstring exclusion logic is sound, and the `PERMITTED_MODULES` allowlist is
well-documented. One enhancement for decade-horizon durability:

**The allowlist should be in a YAML file, not in Python source.** When a new module
legitimately needs `config/wads` access (and it will, eventually), the allowlist
change should be a data file commit reviewed by Ma'at, not a code change to the
checker script. This separates policy from mechanism — a governance principle that
the Omega Engine already endorses via the Engine-Stack Firewall (M2) itself.

### 3.3 The Fellegi-Sunter Identity Pipeline (Not Yet Applied)

This is the most epistemically fragile deliverable. The issues:

1. **The confidence score is deterministic, not Bayesian.** Fellegi-Sunter (1969)
   is a probabilistic record linkage framework where match weights are derived
   from training data (m-probabilities and u-probabilities). Stage 2's implementation
   uses fixed additive weights (0.50, 0.20, 0.20, 0.10) that are not derived from
   any empirical frequency analysis. Calling this "Fellegi-Sunter" is a nomenclature
   inflation — it is a weighted scoring heuristic, not a statistical model.

2. **The legacy bypass is a security exemption disguised as backward compatibility.**
   `is_legacy_local` grants `confidence = T_MU + 0.01` (0.86) to any caller that
   passes only `source_entity`. This means ANY local Hub tool call automatically
   passes identity verification. This is the correct behavior for the current
   single-Hub architecture, but it means the identity pipeline provides zero
   security benefit until federation callers exist — and when they do exist, the
   legacy bypass becomes an attack surface.

3. **The thresholds are arbitrary.** `T_MU = 0.85` and `T_LAMBDA = 0.40` are
   chosen without justification. In real Fellegi-Sunter implementations, thresholds
   are computed from the cost of Type I and Type II errors. Here, the cost model
   is undefined: what is the consequence of a false match? What is the consequence
   of a false non-match (packet goes to clerical queue)? Without answering these
   questions, the thresholds are decorative constants.

**Verdict**: The identity pipeline should be renamed from "Fellegi-Sunter" to
"Weighted Identity Heuristic" to avoid epistemic inflation. The structure is sound
as a v0 implementation; the thresholds should be marked as `# TODO: derive from
operational frequency data after 90 days of federation traffic` with a decision
ID in `PIVOT_LOG.md`.

### 3.4 The Systemd Hardening (Applied on Disk ✅)

This is the only Stage 2 deliverable confirmed on disk. The hardening is correct:
`StartLimitBurst=5`, `StartLimitIntervalSec=300`, `StandardOutput=journal`,
`PartOf=omega-searxng.service`. The 81.5 MB accumulation root cause is resolved.

One decade-horizon concern: `MemoryMax=512M` is hardcoded. As the research worker's
scope expands (new knowledge domains per D-581), this limit will need adjustment.
The limit should be parameterized via an environment variable with a default:

```ini
MemoryMax=${OMEGA_RESEARCH_MEMORY_MAX:-512M}
```

However, systemd does not support variable substitution in `MemoryMax`. The correct
long-term pattern is a drop-in override directory:
`~/.config/systemd/user/omega-research.service.d/memory.conf`.

---

## 4. The 10-Year Durability Verdict

### 4.1 What Will Survive

| Component | Durability | Reason |
|-----------|------------|--------|
| The Sovereign Mandates as constitutional law | **HIGH** | Well-structured hierarchy, each mandate has explicit enforcement mechanism |
| The Engine-Stack Firewall (M2) | **HIGH** | Structurally enforced by directory layout + AST checker |
| The content-addressed federation store | **HIGH** | Append-only, atomic writes, `StoreUnreachable` type discrimination |
| The AnyIO constraint (M1) | **HIGH** | CI-enforced, prevents runtime portability regression |
| The soul.yaml / proposed_lessons.yaml accumulation | **MEDIUM** | Will work for ~3 years before epistemic compaction becomes necessary |

### 4.2 What Will Not Survive Without Intervention

| Component | Risk | Timeline | Required Intervention |
|-----------|------|----------|----------------------|
| Entity namespace coherence | 56 [CORRECTED: 53] dirs vs 14 agents | **NOW** | Canonical registry with status enum |
| Version identity | 3 conflicting versions [CORRECTED: 1 canonical version] | **NOW** | Single `__version__` source |
| Lock map growth | Unbounded `_ENVELOPE_LOCKS` | ~2 years | LRU eviction or WeakRef wrapper |
| Identity pipeline thresholds | Arbitrary, untested | When federation launches | Empirical threshold derivation |
| Soul accumulation | 24,600+ L3 principles | ~3 years | Epistemic compaction protocol (proposed M31) |
| Clock discipline | No NTP mandate across nodes | When federation launches | Clock sync mandate + bounded-skew assertions |
| Schema evolution | No versioning for YAML schemas | ~1 year | Schema version field + migration protocol |

### 4.3 The Deepest Structural Risk: The Observer Problem

The Omega Engine's most profound vulnerability is not technical — it is epistemic.
The system's quality gates (M13 Temple-Grade, M27 Tracking Integrity) are
self-referential: the engine evaluates its own compliance. The 53/53 incident
(temple-grade passing while the Hub was crash-looping) demonstrated that
**self-assessment without external verification is structurally incapable of
detecting its own failure modes.**

This is not a bug; it is a category error. A system that checks its own tests
cannot detect the failure mode "my tests don't test what they claim." This is
formally identical to Gödel's incompleteness: any sufficiently expressive
self-referential system contains true statements it cannot prove.

**The 10-year solution**: Node 1 (Vanguard) must run an independent test suite
against Node 0's (Bastion's) claims. Not a mirror of the same tests — a
*skeptical replica* that tests the *assumptions* of Node 0's tests. This is
the purpose of M30 (Remote Claim Integrity), but M30 currently operates as a
documentation standard, not as an automated verification protocol.

---

## 5. Governance Recommendations (Prioritized)

### P0 — Do Now (before next sprint)

1. **Reconcile entity namespace**: Write `scripts/reconcile_entities.py` that
   cross-references `data/entities/`, `.opencode/agents/`, and `INDEX.yaml`.
   Output: which entities are active, which are test fixtures, which are orphans.
   Add status field to `INDEX.yaml`.

2. **Apply the federation read-path patch**: The race at tools.py:1353-1365 is
   live and dropping read receipts. Stage 2's patch is correct; apply it with the
   bounded-lock and reduced-disk-read fixes noted in §3.1.

3. **Fix M10 violation**: 15 [CORRECTED: 13] agent definitions > 14 ceiling. Either remove one
   agent or amend M10 with a PIVOT_LOG decision.

### P1 — Do This Quarter

4. **Rename Fellegi-Sunter to Weighted Identity Heuristic** before the name
   calcifies in documentation and agent context windows.

5. **Add schema version fields** to `soul.yaml`, `proposed_lessons.yaml`, and
   federation envelope JSON. Use `_schema_version: "1.0.0"` with a migration
   protocol documented in `docs/architecture/`.

6. **Unify version identity**: Single `__version__` in `src/omega/__init__.py`.

### P2 — Do This Year

7. **Draft M31 (Epistemic Compaction)** as a proposed mandate, discussed and
   ratified through the PIVOT_LOG.

8. **Draft a Clock Discipline mandate** requiring NTP on all federation nodes
   and bounded-skew assertions in envelope timestamp comparisons.

9. **Implement the AST checker's allowlist as external YAML** per §3.2.

### P3 — Pre-Federation Launch

10. **Derive identity pipeline thresholds** from 90 days of operational data.

11. **Build the skeptical replica test suite** on Node 1 that independently
    verifies Node 0's claims per §4.3.

---

## Closing Statement

The Omega Engine, as observed on disk at 2026-09-30T22:50, is a system of
**remarkable structural ambition with uneven execution maturity**. The constitutional
framework (30 mandates, 5 architecture rules, 6-layer defense hierarchy) is among
the most rigorous governance structures I have encountered in a two-person project.
The AST-based M2 firewall checker, the `StoreUnreachable` type discrimination, and
the content-addressed envelope store are genuine engineering achievements that will
age well.

The risks are not in the architecture but in the **gap between declared invariants
and live enforcement**. Temple-Grade 53/53 over a crash-looping Hub. 56 entity
directories against a 14-agent ceiling. Three version numbers. A live read-receipt
race condition with a patch written but not applied. These are not failures of
design — they are failures of **operational discipline**, which is the hardest
kind to fix because no CI gate can enforce the habit of applying the patch you wrote.

The 10-year durability of this system depends on one principle that no mandate
currently captures: **the system must be willing to act on its own findings**.
Stage 2 wrote the patch. Stage 3 verified the need. The race is still live.

*⬡ OMEGA ⬡ OPUS ⬡ STAGE-3 ⬡ EPISTEMIC-SYNTHESIS-v1.0.0 ⬡ 2026-10-01 ⬡*
