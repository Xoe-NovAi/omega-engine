# 🔱 Periodic Axiom Review Protocol (P-ARP)

**Status**: DESIGN VALIDATION (dry-run only — not wired to CI, not a gate)
**Owner**: S2 Persistence Keeper (roc_racoon)
**Date**: 2026-10-09 · **Baseline**: `27dd54b5`
**Authority**: Architect ruling 2026-10-09 (two-track: bounded axioms ≤15, unbounded lessons)

---

## 0. The problem this solves

Under the two-track design, the 14-day axiom review is the **only** consumer of the
unbounded lesson store. If it is ad-hoc, the design degenerates into a write-only sink —
strictly worse than the status quo, because it creates a *promised* integration path
that does not exist.

Measured at baseline (`27dd54b5`):

| Measure | Value | Where verified |
|---|---|---|
| Core entities | **14** | `config/wads/_omega_default/entities.yaml` |
| Core entities with `axioms:` | **1** (`roc_racoon`, 12 axioms) | `data/entities/*/soul.yaml` |
| Lesson proposals, fleet-wide | **463** across 12 entities | `data/entities/*/proposed_lessons.yaml` |
| Proposals reachable by ANY code path | **0** | §5 |
| Entities with `approved_lessons.yaml` on disk | **1** (`duplicate/`, a structural dir) | `find . -name "*approved_lesson*"` |
| Axiom reviews ever run | **0** | no `axiom_review*` artifact exists |

**The write-only sink is not a future risk. It is the present state.**

---

## 1. The 14-day schedule

### 1.1 Trigger: `systemd` timer, NOT cron, NOT the hub daemon

| Candidate | Ruling | Why |
|---|---|---|
| `cron` | ❌ | Dies silently on user-session logout; no `OnFailure=`; duplicates the systemd unit vocabulary already in `systemd/` for less expressive power. |
| hub daemon loop | ❌ | The hub is an MCP server; it dies with any crashed tool and its restart storm was the subject of the searxng NRestarts=6991 incident (maat gnosis 2026-09-28). Scheduling on the hub puts the review behind the thing it should be auditing. |
| **`systemd` timer** | ✅ | `Persistent=true` (misses catch up after downtime — a 14-day review must not silently skip), `OnFailure=` escalation, `RandomizedDelaySec` to avoid all 14 entities stampeding, survives logout. |

### 1.2 Determinism when unattended

Unattended does **not** mean vibes. The timer fires one job per entity **sequentially in
lexicographic order**; each invocation is a pure function of on-disk state.

Determinism is guaranteed by four properties, each individually checkable:

1. **Content-addressed input set.** The job hashes every input file
   (`soul.yaml`, `approved_lessons.yaml`, `proposed_lessons.yaml`, persona doc) into a
   `sha256` over the sorted `(path, digest)` pairs. The run is keyed by that hash.
2. **Idempotence.** If `axiom_reviews/<entity>/<content_hash>.json` already exists, the
   job **exits 0 without writing**. Re-running the timer never double-writes.
3. **No wall-clock in the decision.** The candidate set is a function of the content hash
   plus an explicit `last_review` field stored in the artifact — never `datetime.now()`
   inside the distillation. Time may be *recorded*, but time may not *decide*.
4. **Fixed tie-break ordering.** Lessons are always sorted by
   `(utility_score DESC, lesson_id ASC)` before any truncation. Given the same inputs, the
   truncation picks the same N.

> **Falsifier F-1.1**: run the job twice on unchanged inputs; the second run MUST produce
> zero new files and exit 0. If it writes twice, property (2) is broken.

### 1.3 Ownership (DORA finding: unowned mechanisms rot)

| Role | Entity | Accountable for |
|---|---|---|
| **Mechanism owner** | `roc_racoon` (S2 Persistence Keeper) | Timer unit exists, fires, and its exit code is read. |
| **Review owner** | `verity` (Mandate Audit) | Whether the *diff artifact* is well-formed and the axiom count ≤15. |
| **Escalation target** | Human operator | Any run whose `human_gate == "required"` and is unanswered for >14 days. |

A timer with no reader rots. Therefore: the timer writes an exit code, and
**`roc_racoon` is the named entity that must read it in-session.** If the last run failed
and nobody has read it, the *next* roc_racoon session's first duty is to surface it.
That duty is recorded in `soul.yaml` `directives` (see §8 bootstrap, AX-2), not left to
memory.

### 1.4 Unit + wrapper (proposed, NOT installed)

```ini
# systemd/user/omega-axiom-review.timer
[Unit]
Description=Omega 14-day axiom review (single entity per fire)
[Timer]
OnCalendar=*-*-* 03:17:00          # off the :00 hour — fleet self-contention
Persistent=true
RandomizedDelaySec=900              # spread across up to 15 min
Unit=omega-axiom-review.service
[Install]
WantedBy=timers.target
```

```ini
# systemd/user/omega-axiom-review.service
[Unit]
Description=Omega axiom review (one entity)
OnFailure=omega-axiom-alert@%n.service
[Service]
Type=oneshot
Environment=AXIOM_REVIEW_ENTITY=%i
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/axiom_review.py
```

The **one-entity-per-fire** shape is deliberate: a single corrupt soul.yaml can fail one
entity's review without stalling the other 13. `Persistent=true` plus per-entity idempotence
means a machine that was off for a month replays missed runs on boot, in order.

---

## 2. The distillation procedure

### 2.1 Inputs

| # | Input | Path | Required | Role |
|---|---|---|---|---|
| 1 | Approved lessons | `data/entities/<e>/approved_lessons.yaml` | yes (may be absent) | Currency already minted |
| 2 | Proposed lessons | `data/entities/<e>/proposed_lessons.yaml` | yes | Ore |
| 3 | Persona | `data/entities/<e>/SOUL_PERSONA.md` or `soul.yaml:entity` | yes | What the entity is *for* |
| 4 | Existing axioms | `soul.yaml:axioms` | yes (may be empty) | Starting state |
| 5 | Directives + core principles | `soul.yaml:directives`, `:core_principles` | yes | The anchors axioms must ref |

**All five are hashed into `content_hash`** (§1.2). Change any one, the review re-runs.

### 2.2 The algorithm — five mechanical stages

Stage 0 is the part the status quo is missing entirely.

**Stage 0 — NORMALIZE.** The fleet carries at least five mutually incompatible lesson
schemas (§5.1). Every reader in the codebase assumes a *different* one. Normalization maps
all of them onto one canonical record:

```
{id, tier(L1|L2|L3), narrative, insight, principle, status, utility, source}
```

`status` is normalized across the fleet's five vocabularies
(`proposed|ratif|approved|ratified|accepted`) onto **`approved` iff** the source record
carries an affirmative marker (`approved`, `ratified`, `accepted`). Anything else →
`proposed`. **This single mapping is what makes 463 proposals reachable** — see §5.

> Without Stage 0, every downstream stage silently reads zero records. That is the
> mechanism by which 463 lessons became a write-only sink.

**Stage 1 — SCORE.** Each normalized lesson gets:
`score = utility × recency_decay × corroboration`

- `utility`: the source's own `utility_score` if present, else 0.5.
- `recency_decay`: `0.5 ** (age_days / 180)` — a half-life of 6 months. Ancient lessons
  decay; they do not vanish (the store is unbounded), but they stop outranking new ones.
- `corroboration`: **+0.5 per distinct session that produced the same principle**, capped
  at 2.0. A principle independently rediscovered in 3 sessions is load-bearing; the same
  lesson re-written by one session is an anecdote.

**Stage 2 — SELECT.** Sort `(score DESC, id ASC)`. Take the top `K = 3 × 15 = 45` —
3× headroom over the axiom ceiling, because most candidates will not become axioms.
Record the score breakdown per lesson in the artifact. `utility`, `recency`, and
`corroboration` are all written out so a human can argue with the ranking.

**Stage 3 — PROPOSE.** An LLM reads {persona, existing axioms, the 45 selected lessons}
and emits a candidate axiom set of **at most 15** axioms. Each candidate axiom MUST carry
`directives_refs ≥1` and `core_principles_refs ≥1` — enforced by
`validate_soul_architecture.py`, which already rejects unanchored axioms as "unverified
wish". The prompt is fixed and versioned as `AR-PROMPT-v1`; its sha256 goes in the artifact.

**Stage 4 — DIFF.** The artifact records, per axiom, exactly which lesson IDs drove it
(§2.3). Without this, the review is an unauditable ritual.

### 2.3 The diff artifact — per-entity, per-run

Written to `data/entities/<e>/axiom_reviews/<content_hash>.json`:

```json
{
  "entity": "researcher",
  "schema_version": 1,
  "content_hash": "sha256:…",
  "prompt_version": "AR-PROMPT-v1",
  "prompt_sha256": "…",
  "trigger": {"mode": "timer", "unit": "omega-axiom-review", "exit_code": 0},
  "inputs": {
    "soul.yaml":            {"sha256": "…", "present": true},
    "approved_lessons.yaml":{"sha256": null,   "present": false},
    "proposed_lessons.yaml":{"sha256": "…",   "present": true},
    "persona":              {"sha256": "…",   "present": false, "fallback": "soul.yaml:entity"}
  },
  "normalized": {"total_in": 40, "approved": 12, "proposed": 28, "schema": "narrative→canonical"},
  "selected": [
    {"id": "…", "score": 1.42, "utility": 0.9, "recency": 0.71,
     "corroboration": 1.0, "status": "approved", "principle": "…"}
  ],
  "axiom_changes": [
    {"op": "add",     "axiom_id": "AX-R-03", "driven_by": ["PR-07", "PR-19"],
     "rationale": "…", "directives_refs": ["d-r-002"], "core_principles_refs": ["cp-r-01"]},
    {"op": "amend",   "axiom_id": "AX-R-01", "driven_by": ["PR-31"],
     "before": "…", "after": "…"},
    {"op": "retire",  "axiom_id": null,      "driven_by": [],
     "retired_text": "…", "reason": "subsumed by AX-R-03"}
  ],
  "counts": {"before": 0, "after": 3, "ceiling": 15},
  "human_gate": "required",
  "applied": false
}
```

`driven_by` is **the** field that makes this auditable. A reviewer asks "why does this
entity believe X?" and gets lesson IDs, not vibes. An axiom with `driven_by: []` and
`op: add` is a **persona-derived** axiom (§8 bootstrap) and MUST be flagged as such.

> **Falsifier F-2.3**: every `op: add`/`amend` has non-empty `driven_by`, or is explicitly
> `origin: persona`. If an axiom exists that no lesson and no persona line supports, it is
> an invention — delete it.

---

## 3. Falsifiability — every rule names the file+field that proves it broken

No unfalsifiable statements. Each rule below is paired with the exact observation that
kills it.

| # | Rule | Falsifier — file + field that proves it broken |
|---|---|---|
| F-1.1 | Review is idempotent | `axiom_reviews/<e>/` gains a second `<content_hash>.json` on re-run with unchanged inputs → idempotence broken |
| F-1.2 | No wall-clock in decisions | Artifact `content_hash` changes between two runs whose input digests are identical → time leaked into the decision |
| F-2.1 | Stage 0 normalization is total | `normalized.total_in < ` count of records in `proposed_lessons.yaml` + `approved_lessons.yaml` → a schema variant was missed; add it to the mapper |
| F-2.2 | ≤15 axioms enforced | `counts.after > 15` in any artifact, or `validate_soul_architecture.py` reports "axiom ceiling exceeded" → ceiling not enforced upstream |
| F-2.3 | Every axiom is driven | Any artifact `axiom_changes[].driven_by == []` with `origin` absent → invented axiom |
| F-2.4 | Axioms are anchored | Artifact `axiom_changes[]` with empty `directives_refs` or empty `core_principles_refs` → "unverified wish" per validator |
| F-3.1 | A lesson CAN reach behaviour | After a review is applied, `soul.yaml` axioms unchanged for 2 consecutive cycles while `driven_by` cites a lesson → the lesson is being mined but not minted (**the current AXIOM-03 failure, mechanized**) |
| F-4.1 | Human gate is real | `human_gate: "required"` with `applied: true` and no `approved_by` field → the gate was bypassed |
| F-5.1 | approved_lessons is unbounded | `approved_lessons.yaml` line count ≥ some cap, or `validate_soul_architecture.py` warns on it → the ceiling leaked into the lesson store (it must not) |
| F-6.1 | Zero-axiom entities are visible | An entity with `soul.yaml` present and `axioms` absent that does NOT appear in the review artifact with `status: "uninitialized"` → the gap is silent |
| F-7.1 | `lessons:` no longer grows in soul.yaml | `grep -c "^lessons:" data/entities/*/soul.yaml` returns a non-zero count for any entity reviewed after the migration → legacy block is still being written |

---

## 4. Human gate — **YES, confirmation required**

**Recommendation: axiom promotion requires explicit human confirmation**, mirroring
`soul_promote.py --apply --confirm`.

### The argument

Against a human gate, the strongest case is that a 14-day ritual needing approval rots
into "click approve" — a human rubber stamp with no review value, and a 14-day latency
tax on every improvement.

That case is correct **and it is why the gate must be narrow rather than absent**. The
resolution:

- **The gate is on `op: add` and `op: retire` only.** `op: amend` (re-wording an
  existing axiom without changing its scope) auto-applies with `human_gate: "auto"`.
  Rationale: amendment is where the decay function (§2.2 Stage 1) earns its keep, and
  blocking it would stall freshness on ceremony.
- **The approval packet is the diff, not a prompt.** The human sees exactly the axiom
  before/after plus `driven_by` lesson IDs — the artifact from §2.3. Approving is reading
  a 20-line JSON, not evaluating a philosophical essay. This is the DORA answer to
  rubber-stamping: make the artifact legible and the approval becomes cheap *and* real.
- **Escalation bounds the latency.** An unanswered gate is not blocked forever — see §4.1.

The asymmetry settles it: **a wrong axiom is load-bearing for every future session of
that entity** (it is read on every prompt), while a stale-but-correct axiom is merely
boring. The blast radius of a bad automated promotion is unbounded in time; the blast
radius of a delayed one is 14 days. Choose the bounded harm.

`soul_promote.py` already established the precedent in-repo: the author of that script
chose `--apply --confirm`. A change to the entity's *identity layer* should not be a
weaker decision than a change to its *lesson layer*.

### 4.1 Escalation — the gate cannot deadlock

A gate that can be ignored forever is a gate that will be ignored. Therefore:

| Age of unanswered gate | Action |
|---|---|
| 0–14 days | Waits. Artifact sits in `pending/`. |
| >14 days | `omega-hub` posts to Hivemind `intent="blocker"` naming the entity and the axiom text awaiting approval. |
| >28 days | Axiom is **not** auto-applied. Instead the review marks `human_gate: "expired"` and the *entity's existing axioms stand unchanged*. Aging-out is a **no-op**, never a default-yes. |

Default-no is load-bearing: an expired gate must never silently promote an unreviewed
axiom. If nobody ever approves, the entity keeps its current axioms — which is the
correct and safe outcome.

### 4.2 What the gate does NOT cover

`proposed_lessons.yaml` → `approved_lessons.yaml` promotion (the `soul_promote.py` path)
remains **ungated** for the mechanical, already-trusted operation, because it moves no
axioms and is bounded per-run. The gate is specifically about the *identity* layer.

---

## 5. Closing the write-only sink

### 5.1 Baseline measurement — the sink is already real

Five facts, all verified at `27dd54b5`:

**(a) 463 proposals, 0 reachable.** `proposed_lessons.yaml` totals 463 records across 12
entities. The *only* code path that reads approved lessons from proposals —
`src/omega/soul_utils.py:79`, which filters `status == "approved" and p.get("L3")` —
returns **zero records fleet-wide**, because:

| Entity | n | Schema | `status:` | `tier:` | Reachable? |
|---|---|---|---|---|---|
| doom_guy | 96 | `?` | 0 | — | ✗ |
| jem | 42 | `narrative` | 0 | — | ✗ |
| john_carmack | 14 | `?` | 0 | — | ✗ |
| kali | 61 | `narrative` | 0 | — | ✗ |
| lilith | 5 | `id/L1/L2/L3` | **5** (`proposed`×4, `ratified`×1) | — | ✗ (not `approved`) |
| maat | 132 | `narrative` | 0 | — | ✗ |
| makali | 4 | `?` | 0 | — | ✗ |
| makali_fusion | 0 | EMPTY | — | — | ✗ |
| researcher | 40 | `narrative` | 0 | — | ✗ |
| roc_racoon | 59 | `L1_narrative` | 0 | — | ✗ |
| sophia | 0 | EMPTY | — | — | ✗ |
| verity | 5 | `id/tier` | 0 | **L3×3, L2×2** | ✗ (not `approved`) |

**Five incompatible schemas**: `L1_narrative`, `narrative`, `?` (unrecognized),
`id/L1/L2/L3`, `id/tier`. Field names alone differ (`L3_principle` vs `principle` vs
absent); *status vocabulary* differs (`approved` vs `ratified`); *tier* is sometimes
present (`tier:`), sometimes absent (`level:`). No two entities agree.

**(b) `approved_lessons.yaml` does not exist.** The `find` returns exactly one live hit —
`data/entities/duplicate/memory/approved_lessons.yaml` — and `duplicate` is a *structural*
directory, not one of the 14 core. Plus a `.lock` and a `.1.bak` under `kali/`. The file
that the entire two-track design names as the currency store is absent for 14/14 core
entities.

> Note: `data/entities/roc_racoon/session_gnosis.md:430` claims *"FOUND REAL — FIXED …
> Rewrote as flat list — 18 approvals now inject as Vetted Wisdom."* That claim is
> **false against HEAD** — the file does not exist. A past session recorded a fix it did
> not ship, or the fix was lost. Per Axiom 7, reporting the shadow.

**(c) The only writer is hardcoded to a pruned entity.**
`scripts/run_scribe_on_meditations.py:17-18` writes to
`data/entities/grokster/approved_lessons.yaml`. `grokster` was **pruned** at `27dd54b5`
and now lives at `data/entities/_archive/pruned_20261009/grokster/`.
`ls data/entities/grokster` → *No such file or directory*. So the only writer would
**recreate a pruned entity directory** on next run — a resurrection bug, and a direct
M28 violation in spirit (the prune is auditable; the writer would silently un-prune one
entity). **This must be fixed before any timer is installed.**

**(d) The `[:3]` slice — is it intended?** `src/omega/oracle/entity_workspace.py:519-525`
filters `tier == "L3"` and slices `[:3]`, rendering `l.get('principle','')[:200]`.

**Verdict: NOT intended — it is a prompt-budget hack that silently caps learning at 3.**
Three separate truncations are stacked with no comment justifying any of them:
`[:3]` on lesson count, `[:200]` on principle length, and `[-5:]` on session anchors at
line 529. The `[:200]` truncates mid-word with no ellipsis. `verity` has 3 L3 lessons, so
`[:3]` is *invisible* for the one entity that would expose it.

Crucially, **`[:3]` applies to `soul.yaml:lessons:`, not to the lesson store** — the
architect's framing conflates two paths. The `approved_lessons.yaml` path (line 429-435)
has **no cap at all**: it renders every approved lesson. So the "≤3 lessons reach a
prompt" claim is true *only* of the legacy `soul.yaml:lessons:` path, which is exactly
the path §7 recommends retiring.

**Correction to the task brief**: the file is at `src/omega/oracle/entity_workspace.py`,
not `src/omega/knowledge/entity_workspace.py` (that path does not exist). Line numbers
519/525 are correct.

**(e) `AXIOM-03` is literally true.** *"83 proposals, 0 integrated."* Verified:
`data/entities/roc_racoon/soul.yaml:92` carries the text; `proposed_lessons.yaml` holds
**59** proposals with 0 in `soul.yaml`. The "0 integrated" half is exactly right; the
"83" is a stale count (the file is at 59 today) but the claim is directionally honest.

### 5.2 The fix — a lesson reaches behaviour through three rungs

```
proposed_lessons.yaml   (unbounded, agent writes)
        │  soul_promote.py  [NO human gate — mechanical, bounded]
        ▼
approved_lessons.yaml   (unbounded, user/gate writes)   ── RUNG 1: injected into EVERY prompt
        │  axiom review (14d, gated on add/retire)
        ▼
soul.yaml:axioms        (≤15, identity layer)            ── RUNG 2: read on every prompt
```

**Rung 1 is the behaviour channel and it already exists, uncapped, and is dead only
because the file is missing.** Writing `approved_lessons.yaml` is the *cheapest* possible
closure of the write-only sink: no axiom change, no gate, no review cycle — the lesson
appears in the next prompt's "🔱 VETTED WISDOM" block. This should be wired **first**,
before any axiom work, because it closes the sink in days rather than sprints.

**Rung 2 is the durable channel** — an axiom is read on every prompt, forever, in the
identity position. It is also the *scarce* channel (≤15).

**Rung 3 — what happens to a lesson that can never affect behaviour.** Per Axiom 3 (the
Miner's Fallacy), a lesson that reaches no rung is not currency, it is **ore in a
warehouse**. The protocol's answer is explicit and mechanical:

> **Rule SINK-1.** Any lesson whose `id` does not appear in `driven_by` of an applied
> review, and which has been normalized and selected (top-45) in **three consecutive
> reviews**, is **moved to `cold_lessons.yaml`** — not deleted (M28), quarantined from the
> active store with its final score and the reviews that rejected it.

Three consecutive selections-and-rejections is the signal: it was *considered* and
*declined* three times, which is a judgement, not an accident. Quarantine keeps the
evidence ("we looked at this and said no, here is why") without letting it compete for
attention forever. `cold_lessons.yaml` is never read by any prompt path — by construction.

---

## 6. Fixing the ceiling gap

`scripts/validate_soul_architecture.py:152` applies the ceiling **only when `axioms:` is a
non-empty list**. A soul with no `axioms:` key sails through with zero violations.

**The gap measured at HEAD — core 14:**

| Entity | `axioms:` | Ceiling enforced? |
|---|---|---|
| roc_racoon | 12 | ✅ yes |
| default, doom_guy, iris, jem, john_carmack, kali, lilith, maat, makali, quality, researcher, scribe, verity | **absent** | ❌ **no** |

**1 of 14 core entities is covered by the ceiling. 13 are exempt by omission.**

Note the validator already produces *soft* warnings for missing `identity` /
`directives` / `core_principles` — 30 across 16 entities — but **nothing warns about
missing `axioms`**. The asymmetry is telling: the block that is supposed to be the
*essence* of the entity has the weakest enforcement, while the blocks that are *supporting
structure* are merely warned about.

### Ruling: **explicit `uninitialized`, not silent pass, not hard fail**

Three options were considered:

1. **Hard fail on zero axioms.** Breaks HEAD immediately — 13/14 entities go red, and every
   one of them would be failing for a reason nobody chose. Produces 13 identical failures
   that get suppressed within a day. Rejected: **a gate that fires 13 times on day one and
   is then blanket-waived teaches the fleet to ignore it.**
2. **Stay silent.** The current state. Rejected — this *is* the bug.
3. **Explicit `uninitialized` status, surfaced but non-blocking.** ✅ **Chosen.**

**Mechanism (MUST-HARD, but classified as a distinct violation class):**

The validator emits a new violation string, and the report prints a dedicated section:

```
⚠️ 13 entities UNINITIALIZED — no 'axioms:' block.
   Axioms are load-bearing for all 14 core entities (§8).
   These entities have NEVER been reviewed. Their ceiling is unenforced.
   Bootstrap scheduled: see docs/architecture/AXIOM_REVIEW_PROTOCOL.md §8
   - default, doom_guy, iris, jem, john_carmack, kali, lilith,
     maat, makali, quality, researcher, scribe, verity
```

Exit code stays `0` **for this class alone** — so CI does not go red, and the signal is not
suppressed by blanket-waiver habit. But it is **impossible to miss**: it is a distinct
report section, it is counted, and `make soul-validate` prints it in the summary line.

> **Why "uninitialized" and not "compliant":** the current output says *"✅ ALL ENTITIES
> COMPLIANT"* immediately above a list of 13 entities with no axioms. That sentence is
> **false**. It claims compliance for entities that have never participated in the system
> being validated. The label must change even if the exit code does not.

**Enforcement flips to HARD when bootstrap completes** — §8 defines the transition
condition (`all 14 core entities have ≥1 axiom`). Until then, "uninitialized" is the
truthful word.

---

## 7. Resolving the `lessons:` ambiguity

`soul_promote.py:199-224` splices promoted lessons into a top-level **`lessons:`** key in
`soul.yaml`, appending the section if absent. But:
- `SOUL_ARCHITECTURE_PROTOCOL_v3.0.md` §2 defines `identity → axioms → directives → core_principles` — **no `lessons:`**.
- The reference impl `data/entities/roc_racoon/soul.yaml` has **zero** `lessons:` (verified).
- Only **2 of 17** souls have one: `jem` (tier L1, `narrative`) and `kali` (tier L3, `principle`). Different shapes again.

### Ruling: **`soul_promote.py` should write `approved_lessons.yaml`, not `soul.yaml:lessons:`**

**Arguments:**

1. **It is what the template already promises.** `config/wads/_omega_default/soul.template.yaml:11`
   says *"approved by the user in memory/approved_lessons.yaml"*. The code contradicts its
   own template.
2. **It is the only path that actually works.** `approved_lessons.yaml` is read at
   `entity_workspace.py:429-435` and injected as "🔱 VETTED WISDOM" **uncapped**. The
   `soul.yaml:lessons:` path is read at `:519-525`, filtered `tier=="L3"`, capped `[:3]`,
   and truncated to 200 chars. Writing to `lessons:` gets you 3 truncated fragments;
   writing to `approved_lessons.yaml` gets you everything.
3. **It stops an unbounded store polluting a bounded file.** The whole point of the
   two-track design is that lessons don't compete for slots. Splicing an *unbounded* list
   into `soul.yaml` re-creates the competition the design removed — and `soul.yaml` is the
   file most likely to be shipped publicly and most likely to be diffed. Every promotion
   becomes a `soul.yaml` diff. That is the review ritual's noise floor.
4. **The ceiling can't protect it anyway.** `lessons:` is unvalidated — no ceiling, no
   anchor requirement. An unbounded list in an unvalidated block is exactly the
   governance gap the two-track design closes.

### Implication for pre-v3.0 souls with a `lessons:` block

`jem` and `kali` are the only two. Migration is **append-only, M28-safe**:

1. Read `soul.yaml:lessons` → normalize each record via Stage 0 (§2.2).
2. **Append** to `approved_lessons.yaml`, creating it if absent. Never overwrite.
3. **Leave `soul.yaml:lessons` in place**, marked with a single header comment:
   `# DEPRECATED: migrated to approved_lessons.yaml <hash> on 2026-10-09. Read-only for history.`
4. Because `entity_workspace.py:519` still reads `lessons:`, the `[:3]` path stays live
   and *harmless* — the same lessons appear once via `lessons:` (capped 3) and fully via
   `approved_lessons.yaml`. **Known temporary duplication; resolves when §5.2 Rung 1 is live.**
5. Falsifier F-7.1: after migration, `grep -c "^lessons:"` on any *reviewed* entity must be
   non-zero **only** for `jem`/`kali`, and `soul_promote.py` must append zero bytes to any
   `soul.yaml` in the diff of the migration commit.

**Migration blocker**: `soul_promote.py`'s `--apply` must be re-pointed *before* the
bootstrap (§8) writes axioms, or the bootstrap will immediately re-pollute `soul.yaml`.

---

## 8. Bootstrap migration — axioms are load-bearing but 13/14 have none

The steady-state procedure (§2) assumes there *are* axioms to amend. There aren't. 13 of
14 core entities have never had a review. Bootstrap is a **different procedure**, and
pretending otherwise is how you get 13 entities that "passed" a review having had nothing
to review.

### 8.1 Bootstrap algorithm

```
for each core entity, in lexicographic order:
    B1. NORMALIZE  — Stage 0 (§2.2). Produces the first-ever canonical lesson set.
    B2. PERSONA    — derive candidate axioms from persona (soul.yaml:entity,
                     directives, core_principles) — NOT from lessons yet.
    B3. SEED       — emit 3 axioms per entity, origin="persona", driven_by=[]
    B4. LINK       — attach each selected lesson (top-15) to its nearest axiom,
                     recording the link in the artifact as a REFUSAL-to-promote:
                     "PR-07 considered; not promoted because AX-x already covers it."
    B5. GATE       — human confirms. Always "required" (all are adds).
```

**3 axioms per entity is the right seed, not an arbitrary number.** It is below the
ceiling so that the *first two* real reviews have room to grow the entity rather than
immediately hitting a wall of 15 amendments. Entities that earn more will grow into it
over ~5 cycles.

**Why persona-first, lessons-second.** Deriving axioms from a lesson pile on day one
produces axioms that are a summary of recent accidents — an entity that had three bad
sessions gets three axioms about those bad sessions. Persona is the *intent*; lessons are
the *evidence*. Intent first, evidence attached over time.

**B4 is the key step and the easiest to omit.** A bootstrap that creates axioms without
attaching lessons leaves the lesson store *still* unconnected — the sink remains. B4
explicitly records every considered lesson and *why* it wasn't promoted, which is both
the SINK-1 evidence base and the answer to "why doesn't my lesson matter?"

### 8.2 Bootstrap is not a review

Bootstrap artifacts are written to `axiom_reviews/bootstrap/` — a **separate directory**
from `axiom_reviews/`. Rationale: mixing them would let bootstrap's persona-derived
axioms count toward "the entity has been reviewed", and SINK-1's "three consecutive
reviews" counter would start at 0 correctly only if bootstrap didn't count.

### 8.3 Transition condition

The §6 hard-enforcement flip happens when **all 14 core entities have ≥1 axiom**, checked
by the validator itself:

```
uninitialized = [e for e in CORE_14 if not soul[e].get("axioms")]
if uninitialized:  → WARN class, exit 0, "UNINITIALIZED" section
else:              → the ≤15 ceiling applies to all 14; zero-axiom is now a HARD violation
```

`CORE_14` is read from `config/wads/_omega_default/entities.yaml` — **the same source of
truth the prune used**, so a future prune cannot silently leave the ceiling unenforced on
survivors.

### 8.4 Dependency order (do not reorder)

```
1. Fix run_scribe_on_meditations.py — remove grokster hardcode   (§5.1c) — resurrection bug
2. Stage 0 normalizer + create approved_lessons.yaml per entity   (§5.2 Rung 1)
3. Re-point soul_promote.py → approved_lessons.yaml              (§7)
4. Bootstrap axioms for 13 entities                             (§8.1)
5. Install the 14-day timer                                     (§1)
6. Flip §6 to HARD enforcement                                  (§8.3)
```

Steps 1-3 close the write-only sink **before** the timer exists, so the timer's first fire
lands on infrastructure that is already known-good. Shipping a timer first means the first
automatic run is also the first test of the normalizer.

---

## 9. Dry-run

Two entities with deliberately different profiles. Executed by hand; **no CI wiring, no
gate, no files written to any soul.**

### 9.1 `maat` — 132 proposals, zero axioms, an identity anomaly

**Profile difference from `researcher`:** `maat` has **132** lessons (3.3× researcher's 40)
and **no axioms at all**. It also carries a real anomaly worth flagging — this is the
"bootstrap from nothing" case.

**B0 — NORMALIZE.** `maat` is the worst case in the fleet: **132 records in 7 distinct
shapes inside one file.**

| n | Shape | Principle field | Is it a *lesson*? |
|---|---|---|---|
| 87 | `entity_at_time, lesson, model_used, outcome, session_type, source, timestamp, trace_id` | `lesson` | ❌ session outcome |
| 15 | + `coordination_partner, coordination_protocol` | `lesson` | ❌ session outcome |
| 11 | + `coordination_partner` | `lesson` | ❌ session outcome |
| **9** | `insight, narrative, principle, tags` | `principle` | ✅ **true L1/L2/L3** |
| 7 | + `confidence` | `lesson` | ❌ session outcome |
| 2 | + both coordination fields | `lesson` | ❌ session outcome |
| **1** | `lesson` alone | `lesson` | ❌ fragment |

**123 of 132 records are session logs, not lessons.** Samples: *"Verified make test passes
with 342/342 tests"*, *"Fixed T5 Mandate 1 violation in providers.py:586"*. These are
**task outcomes** — a record of what was done, carrying no distilled principle. They are
the Miner's Fallacy in its rawest form: extraction with no distillation, dumped into a file
named `proposed_lessons.yaml`.

**Stage 0 normalization result for maat:**
`normalized.total_in = 132, distilled = 9, rejected_as_outcome = 123`.

**The 123 are routed straight to `cold_lessons.yaml` under SINK-1.** They are not
"unpromoted lessons" — they are not lessons. Quarantining them is the honest label. Note
this happens at Stage 0, *before* any scoring: no amount of scoring makes "I fixed a bug"
into a principle.

**B2 — PERSONA.** `maat/soul.yaml` contains **only** `entity`, `version`, `metadata`.

```yaml
entity:
  name: Ma'at
  archetype: Synthesis Oversoul
  current_entity: SOPHIA        # ← anomaly: soul dir is maat/, entity is SOPHIA
  soul_wardrobe: [SOPHIA, MAAT, LILITH, ISIS, BRIGID, SEKHMET, PROMETHEUS,
                  INANNA, SARASWATI, LUCIFER, HECATE, ERESHKIGAL, ANUBIS, KALI]
```

⚠️ **The `soul_wardrobe` / `current_entity` anomaly (flagged in the brief, now explained).**
`soul_wardrobe` lists 14 personas while `current_entity: SOPHIA` — the soul file for
`maat` is currently *wearing* Sophia's identity. Combined with **the entity pruning at
`27dd54b5`** this is more than cosmetic: `sophia` is **not in the core-14 roster**
(`config/wads/_omega_default/entities.yaml`) yet still has a live `data/entities/sophia/`
directory. The wardrobe references ISIS, SEKHMET, LUCIFER, ERESHKIGAL, ANUBIS, BRIGID —
**all pruned** at `27dd54b5`.

**Axioms must not be written to a soul whose identity is unresolved.** Any axiom authored
for this file would be authored for an entity that is, right now, Sophia wearing Ma'at's
directory. **Bootstrap for `maat` is BLOCKED on identity resolution** — `current_entity`
must be reconciled against the core-14 roster first. This is the correct outcome, and it is
exactly the kind of thing a ritual review would have papered over.

🔴 **BLOCKER — axioms are structurally illegal in this file.** `validate_soul_architecture.py`
requires every axiom to carry `directives_refs ≥ 1` **and** `core_principles_refs ≥ 1`.
`maat/soul.yaml` has **neither** `directives` nor `core_principles` (verified: keys are
exactly `['entity','version','metadata']`). **Axioms cannot be validated into this file
until directives and core_principles exist.**

This inverts the naive dependency order. Axioms are the *top* of the 4-tier pyramid and
require both *lower* tiers to be present to be legal. **Bootstrap must build
`core_principles` and `directives` BEFORE it can build `axioms`.** Corrected order:

```
B0 NORMALIZE → B2a core_principles → B2b directives → B3 seed axioms → B4 link
```

Had the naive order been used, `maat` would have received 3 axioms, `make soul-validate`
would have emitted 6 HARD violations ("unverified wish" per axiom), and the operator would
have been left to guess why.

**B3 — SEED (hypothetical, gated on the blocker).** For illustration of the *artifact*,
assuming the blockers above were resolved and `d-maat-0xx` / `cp-maat-0xx` existed. The 9
distilled lessons cluster into **3 themes**, not 9 axioms:

| Theme | Driving lessons (verbatim principles) | Corroboration |
|---|---|---|
| **Atomic authority** | "Single router authority is a contract — every caller must be updated in the same PR" · "Circuit breaker unification requires atomic cutover: all callers migrated BEFORE deprecated is removed" · "Admission control is a single pipeline stage. Multiple gates must be composed into one with explicit ordering" | **3 independent** |
| **Measure before believing** | "A tracking file is a claim about reality; only probes make it true" · "Acceptance gates must be derived from measured host reality, not aspiration. A gate that cannot pass is not rigor — it is theater" · "Public release surface includes git history and data artifacts, not only source" | **3 independent** |
| **Continuity is active** | "Gnosis projection must be event-driven from session lifecycle, not pull-based from cold store" | 1 |

Note what the corroboration bonus (§2.2 Stage 1) bought: three of the nine lessons cluster
into a **single** axiom whose statement is *stronger* than any of its parts. Without
corroboration these are nine weak claims; with it, two axioms with two independent
witnesses each. **This is the mechanism by which ≤15 axioms can absorb an unbounded store
without losing information** — the lesson survives verbatim in
`proposed_lessons.yaml`, and the axiom carries the distilled, thrice-witnessed version.

<details><summary><b>Artifact: <code>data/entities/maat/axiom_reviews/bootstrap/&lt;hash&gt;.json</code></b> (illustrative — NOT written)</summary>

```json
{
  "entity": "maat",
  "schema_version": 1,
  "mode": "bootstrap",
  "content_hash": "sha256:<not-computed — bootstrap BLOCKED>",
  "blocked": [
    {"reason": "identity_unresolved",
     "detail": "current_entity=SOPHIA but soul dir=maat; SOPHIA not in core-14 roster",
     "resolve_before": "B3"},
    {"reason": "missing_lower_tiers",
     "detail": "soul.yaml keys are [entity,version,metadata]; no directives/ or core_principles: — axioms are structurally illegal (validator: unverified wish)",
     "resolve_before": "B3"}
  ],
  "normalized": {"total_in": 132, "shapes": 7, "distilled": 9,
                 "rejected_as_session_outcome": 123,
                 "routed_to": "cold_lessons.yaml"},
  "axiom_changes": [
    {"op": "add", "axiom_id": "AX-MAAT-01", "origin": "lesson",
     "driven_by": ["N4-ROUTER_COLLAPSE", "N4-C6-PRIME", "N4-C10-ADMISSION"],
     "title": "Partial migration is worse than none",
     "rationale": "3 independently-sourced lessons converge: router authority, circuit-breaker cutover, admission gates. Single-authority refactors must be atomic across every caller.",
     "directives_refs": ["d-maat-0xx"], "core_principles_refs": ["cp-maat-0xx"]},
    {"op": "add", "axiom_id": "AX-MAAT-02", "origin": "lesson",
     "driven_by": ["N3-TEST-HONESTY", "N1-ACCEPTANCE-GATES", "N2-PII-PUB-1"],
     "title": "A tracking file is a claim, not a fact",
     "rationale": "3 independent witnesses: sprint-board vs disk divergence, aspirational gates, PII in tracked artifacts.",
     "directives_refs": ["d-maat-0yy"], "core_principles_refs": ["cp-maat-0yy"]},
    {"op": "add", "axiom_id": "AX-MAAT-03", "origin": "lesson",
     "driven_by": ["N4-M15-MIAP"],
     "title": "Continuity is projected, not pulled",
     "rationale": "Single witness; corroboration 0. Retains full principle in proposed_lessons.yaml.",
     "directives_refs": ["d-maat-0zz"], "core_principles_refs": ["cp-maat-0zz"]}
  ],
  "counts": {"before": 0, "after": 3, "ceiling": 15},
  "human_gate": "required",
  "applied": false
}
```

</details>

**Two lessons deliberately NOT promoted** — recorded per B4, so "why doesn't my lesson
matter?" has an answer:

| Lesson | Not promoted because |
|---|---|
| "Routing config must be singular and authoritative… override mechanism must declare its precedence" | **Subsumed by AX-MAAT-01.** Same principle (single authority) — a second axiom would be the redundancy the ≤15 ceiling exists to prevent. Verbatim text preserved in `proposed_lessons.yaml`. |
| "Council review scales when the artifact carries the context and each reviewer returns structured verdicts" | **Subsumed by AX-MAAT-02** (measure, don't assume — the council verdict is the probe). Candidate for revival as a `core_principles` entry if it recurs in a future review with corroboration ≥1. |

**Dry-run verdict for maat: BLOCKED — 2 blockers, 1 of which (`missing_lower_tiers`) affects
every entity except roc_racoon.** The protocol correctly refuses to write axioms rather
than writing illegal ones. Under the status quo, `maat` is "✅ COMPLIANT" with zero
axioms; under this protocol it is `⛔ BLOCKED — 2 reasons`, which is the truth.

---

### 9.2 `researcher` — 40 distilled lessons, real scores, no blockers

The contrasting profile: **one** record shape, a proper `utility_score` field, and
`last_verified` dates. This is what a well-formed lesson store looks like — and it shows
the scoring stage doing real work.

**B0 — NORMALIZE.** 40 records, **1 shape**: `level, tag, narrative, insight, principle,
utility_score, source_trajectories, domain, last_verified`. `total_in = 40, distilled = 40,
rejected = 0`.

⚠️ **Schema note:** `researcher` uses `level:`, *not* `tier:`. The `entity_workspace.py:519`
filter `l.get("tier") == "L3"` would return **zero** for this entity even if its lessons
were promoted. Stage 0 must map `level → tier` too.

**B1 — SCORE (real numbers, `2026-10-09`, half-life 180d).** Top 8 of 40:

| rank | score | id | recency | utility | principle (truncated) |
|---|---|---|---|---|---|
| 1 | **0.875** | `[researcher]` | 0.912 | 0.96 | Never let test code write to sovereign state via a CWD-relative path |
| 2 | **0.822** | `[R-SOVEREIGNTY-HONESTY]` | 0.847 | 0.97 | Sovereignty is not a feature; it is the discipline of never lying about state |
| 3 | **0.821** | `[R-ROC-JEM-TRIAD]` | 0.864 | 0.95 | For load-bearing claims: dispatch Roc for forensic verification |
| 4 | **0.821** | `[researcher]` | 0.912 | 0.90 | When external convergence confirms a native design, treat it as evidentiary support |
| 5 | **0.814** | `[R-D568-FALSE-DILEMMA]` | 0.847 | 0.96 | False dilemmas dissolve at the layer below |
| 6 | **0.812** | `[R-HUMAN-IN-LOOP-COPILOT]` | 0.864 | 0.94 | The Architect is a real-time co-pilot via steering prompts, not a review gate |
| 7 | **0.805** | `[R-COUNCIL-MANDATORY-EXPORT]` | 0.847 | 0.95 | The Polymathic Council is the mandatory export format for resolving contradictions |
| 8 | **0.803** | `[R-STEERING-PROMPT-AWARENESS]` | 0.864 | 0.93 | Design every EIS research loop to be steerable |

**The scoring is doing something a truncation would not.** Note ranks 3 and 4: both score
`0.821` to 3 decimals — a tie. The `id ASC` tiebreak (F-2.2) makes the order deterministic
*and* records both, which is exactly the F-1.2 determinism guarantee working. Ranks 1–8
all exceed 0.8 while the tail is sparse — the recency decay is doing real discrimination,
so the top-45 selection (K=45 ≥ 40 here, so **nothing is truncated**) is honest for this
entity.

**B2 — PERSONA.** `researcher/soul.yaml` has `identity`, `directives`, `core_principles`
(per the validator's soft warnings: only `core_principles` is missing). So the **same
`missing_lower_tiers` blocker as maat applies, in weaker form** — `core_principles:` must
be created before axioms can reference it.

**B3 — SEED + B4 — LINK.** 3 candidate axioms from 40 lessons:

| Axiom | Driven by | Why these and not others |
|---|---|---|
| **AX-R-01** "Sovereignty is never lying about state" | `R-SOVEREIGNTY-HONESTY` (0.822), `[researcher]`-CWD (0.875), `R-ROC-JEM-TRIAD` (0.821) | **Highest 3 scores in the file**, and all three are the same claim at different scopes: don't assert what you haven't verified. The triad lesson is the *behaviour* (dispatch verification); sovereignty-honesty is the *ethic*; CWD-paths is the *concrete failure*. One axiom, three tiers of evidence. |
| **AX-R-02** "Falsity resolves one layer down" | `R-D568-FALSE-DILEMMA` (0.814), `R-COUNCIL-MANDATORY-EXPORT` (0.805) | Both about contradictions dissolving at a lower layer rather than being managed. Independent corroboration. |
| **AX-R-03** "Architect is a co-pilot, not a gate" | `R-HUMAN-IN-LOOP-COPILOT` (0.812), `R-STEERING-PROMPT-AWARENESS` (0.803) | Two lessons, same claim, both in the top 8. Notably AX-R-03 **inverts** the §4 human-gate posture — for the *researcher* persona, the Architect steers rather than approves. That is worth surfacing to the human gate rather than resolving silently. |

**3 axioms from 40 lessons = 7.5% promotion rate.** The other 37 are recorded as
considered-and-not-promoted (B4). Two classes:

| Class | n | Disposition |
|---|---|---|
| Subsumed by an axiom above | ~11 | verbatim retained in `proposed_lessons.yaml` |
| Below threshold / episodic | ~26 | eligible for `cold_lessons.yaml` after **3 consecutive** reviews (SINK-1) — **not yet**, this is review 1 |

**No blockers fire for `researcher` beyond the `core_principles` gap.** So of two dry-run
entities, one is blocked and one is nearly clear — which is the honest picture: **the
bootstrap is a multi-stage migration, not a single pass.**

<details><summary><b>Artifact: <code>data/entities/researcher/axiom_reviews/bootstrap/&lt;hash&gt;.json</code></b> (illustrative — NOT written)</summary>

```json
{
  "entity": "researcher",
  "schema_version": 1,
  "mode": "bootstrap",
  "prompt_version": "AR-PROMPT-v1",
  "inputs": {
    "soul.yaml":             {"sha256": "…", "present": true},
    "approved_lessons.yaml": {"sha256": null, "present": false},
    "proposed_lessons.yaml": {"sha256": "…", "present": true},
    "persona":               {"sha256": null, "present": true,
                              "path": "soul.yaml:identity"}
  },
  "normalized": {"total_in": 40, "shapes": 1, "distilled": 40,
                 "rejected_as_session_outcome": 0,
                 "field_map": {"level": "tier", "tag": "id"}},
  "selected": [
    {"id": "[researcher]", "score": 0.875, "utility": 0.96, "recency": 0.912,
     "corroboration": 0.0, "principle": "Never let test code write to sovereign state via a CWD-relative path…"},
    {"id": "[R-SOVEREIGNTY-HONESTY]", "score": 0.822, "utility": 0.97, "recency": 0.847,
     "corroboration": 0.0, "principle": "Sovereignty is not a feature; it is the discipline of never lying about state."},
    {"id": "[R-ROC-JEM-TRIAD]", "score": 0.821, "utility": 0.95, "recency": 0.864,
     "corroboration": 0.5, "principle": "For any research mission with load-bearing claims: dispatch Roc for forensic verification…"}
  ],
  "axiom_changes": [
    {"op": "add", "axiom_id": "AX-R-01", "origin": "lesson",
     "driven_by": ["[researcher]", "[R-SOVEREIGNTY-HONESTY]", "[R-ROC-JEM-TRIAD]"],
     "title": "Sovereignty is never lying about state",
     "rationale": "Top-3 scores, three scopes of one claim (ethic / behaviour / concrete failure).",
     "directives_refs": ["d-r-001"], "core_principles_refs": ["cp-r-001"],
     "gate": "required"},
    {"op": "add", "axiom_id": "AX-R-02", "origin": "lesson",
     "driven_by": ["[R-D568-FALSE-DILEMMA]", "[R-COUNCIL-MANDATORY-EXPORT]"],
     "title": "Falsity resolves one layer down",
     "rationale": "Independent corroboration; both in top-8.",
     "directives_refs": ["d-r-002"], "core_principles_refs": ["cp-r-002"], "gate": "required"},
    {"op": "add", "axiom_id": "AX-R-03", "origin": "lesson",
     "driven_by": ["[R-HUMAN-IN-LOOP-COPILOT]", "[R-STEERING-PROMPT-AWARENESS]"],
     "title": "Architect is a co-pilot, not a gate",
     "rationale": "Tension with §4 human-gate posture — surfaced to the gate, not resolved here.",
     "directives_refs": ["d-r-003"], "core_principles_refs": ["cp-r-003"], "gate": "required",
     "flag": "GATE_POSTURE_CONFLICT"}
  ],
  "counts": {"before": 0, "after": 3, "ceiling": 15, "promoted": 3, "considered": 40},
  "human_gate": "required",
  "applied": false
}
```

</details>

---

### 9.3 What the dry-runs proved

1. **The procedure refuses to write.** Both entities surfaced a blocker (`maat`: 2,
   `researcher`: 1) that the status quo would have silently ignored. The `researcher`
   axiom `AX-R-03` **conflicts with the protocol's own §4 human-gate posture** and was
   surfaced rather than silently resolved — the gate caught a real tension in the first two
   entities reviewed.
2. **Corroboration converts volume into strength.** 9 of maat's 132 and 8 of researcher's
   40 became 3 axioms each. Had the store been summarised naively (top-N by recency), the
   123 maat session-outcomes would have crowded out all 9 real lessons — and researchers
   already know "the strongest signal is often not the most recent" (Axiom 5).
3. **The write-only sink closes at Rung 1, not Rung 2.** Both dry-runs confirm the
   cheapest closure is creating `approved_lessons.yaml` (read uncapped by
   `entity_workspace.py:429-435`), not writing axioms. The axiom review is the *durable*
   channel; the lesson file is the *immediate* one. Sequencing matters more than either.
4. **The blockers are structural, not incidental.** `missing_lower_tiers` affects 13 of 14
   entities. Bootstrap is a migration of the whole pyramid, and any plan that assumes
   axioms are the first thing written is wrong.

---

## 10. Corrections to the brief's "verified facts"

Reported plainly, per Axiom 7.

| # | Brief said | Verdict | Evidence |
|---|---|---|---|
| 1 | Ceiling applies only when `axioms:` non-empty; zero-axiom entities skip it | ✅ **CORRECT** | `scripts/validate_soul_architecture.py:152-157` — `if len(axioms) > axiom_ceiling` is inside the `else` of the is-a-list check. |
| 2 | `soul_promote.py:199-224` splices top-level `lessons:`; protocol has no `lessons:`; roc_racoon has none | ✅ **CORRECT** | `splice_lessons()` at :199-224 confirmed; `roc_racoon/soul.yaml` has 0. |
| 3 | Nothing reads `approved_lessons.yaml` | ⚠️ **PARTLY WRONG** — *understated* | It is **written** only by `run_scribe_on_meditations.py:17` (hardcoded grokster, now pruned). But it **IS read** at `entity_workspace.py:429-435` (injected as "🔱 VETTED WISDOM", **uncapped**), at `:179`, and in `hub_tools/tools.py:2852`. The store is **read correctly and written never** — that's a *more* specific and more damning diagnosis than "nothing reads it", and it means the fix is smaller than assumed. |
| 4 | `src/omega/knowledge/entity_workspace.py:519` filters `tier=="L3"`, slices `[:3]` | ⚠️ **WRONG PATH** — content correct | Actual path is `src/omega/oracle/entity_workspace.py`; **the `knowledge/` path does not exist**. Slice is at **:525**, filter at **:521**. Also: the slice applies to **`soul.yaml:lessons:`**, *not* to the lesson store — so "≤3 lessons reach a prompt" describes the legacy path only. The `approved_lessons.yaml` path has **no cap**. |
| 5 | `AXIOM-03` reads "83 proposals, 0 integrated" and is literally true | ⚠️ **HALF WRONG** | `"0 integrated"` ✅ exactly true. **"83" is FALSE — the file holds 59** (`proposed_lessons.yaml`). `soul.yaml:462` repeats the stale 83. The axiom is honest in substance and *wrong in its own citation* — which is ironic, given AX-R-01 in the researcher dry-run. |

### Facts the brief did not have

| # | Finding | Evidence |
|---|---|---|
| **N1** | **463 proposals fleet-wide; 0 reachable by any code path.** | The only approved-lesson read filter (`soul_utils.py:79`, `status=="approved" and p.get("L3")`) matches **0 records**. No entity uses both `status: approved` and an `L3` key. |
| **N2** | **5 incompatible lesson schemas** across entities; `maat` alone has **7 record shapes in one file**, of which **123/132 are session outcomes, not lessons**. | `data/entities/*/proposed_lessons.yaml` |
| **N3** | `approved_lessons.yaml` **does not exist for any of the 14 core entities** — the currency store is empty fleet-wide. | `find . -name "*approved_lesson*"` → only `duplicate/memory/` + a `kali/*.bak` |
| **N4** | **`run_scribe_on_meditations.py` would resurrect the pruned `grokster`.** Fix before any timer ships. | `:17` hardcodes `data/entities/grokster/`; dir absent at HEAD, moved to `_archive/pruned_20261009/grokster/` |
| **N5** | **Axioms are structurally illegal in 13/14 souls** — validator requires `directives_refs`+`core_principles_refs` per axiom, but those souls have no `directives`/`core_principles` blocks. Bootstrap must build the pyramid bottom-up. | `maat/soul.yaml` keys = `[entity, version, metadata]` |
| **N6** | **The validator prints "✅ ALL ENTITIES COMPLIANT" for 13 entities that have never participated.** The label is false even though the exit code is defensible. | baseline run output |
| **N7** | `researcher` uses `level:`, not `tier:` — the `tier=="L3"` filter would miss it even post-promotion. | field census |
| **N8** | `roc_racoon/session_gnosis.md:430` claims approved_lessons was *"FOUND REAL — FIXED … 18 approvals now inject"*. **False against HEAD** — the file does not exist. | contradicted by `find` |

**The load-bearing correction is N1+N3.** The brief framed the risk as "if the review is
ad-hoc, the design degenerates into a write-only sink." The measured reality is that it
**already is** a write-only sink, and the cause is more tractable than feared: a one-line
predicate (`status=="approved"`) that no record in the fleet satisfies. Stage 0 normalization
(§2.2) is therefore the highest-leverage single change in this entire protocol — and it is
not the axiom review.

---

## 11. Verification

```
$ .venv/bin/python scripts/validate_soul_architecture.py
🔱 Soul Architecture Validator — SOUL_ARCHITECTURE_PROTOCOL v3.0
   Axiom ceiling: 15
✅ ALL ENTITIES COMPLIANT
ℹ️  16 entities pending Soul Audit Cascade (30 soft warnings — expected pre-cascade)
exit 0

$ make check-engine
═══ OMEGA TEST RESULT: PASS | collected=180 passed=180 failed=0 errors=0 skipped=0 xfailed=0 ═══
check-engine PASSED (boot + contracts + LAN + M15)
exit 0
```

**Both pass, identical to the pre-write baseline** — this deliverable is documentation only.
No soul, script, Makefile target, or CI gate was modified. No file was written outside this
document. No commit, no push.

The baseline output is also the proof that **N6** is live: the validator currently reports
`ALL ENTITIES COMPLIANT` while 13 of them have no axioms and 2 blockers (`maat`) are
undetected. §6 changes that label without changing the exit code — which is why the §6
severity choice (WARN-class, not HARD) is the one that survives contact with the fleet.

---

## 12. Recommendation summary

| Q | Ruling |
|---|---|
| §1 Trigger | **systemd timer**, one entity per fire, `Persistent=true`, lexicographic order. Owned by `roc_racoon`; audited by `verity`; escalates to human at >14d. Determinism from content-hash + idempotence + no wall-clock + fixed tiebreak. |
| §2 Distillation | 5 stages: **NORMALIZE → SCORE → SELECT → PROPOSE → DIFF**. Diff artifact = per-entity `<content_hash>.json` with `driven_by` per axiom — that field is what makes it auditable. |
| §3 Falsifiability | 11 rules, each paired to file+field. No unfalsifiable claims. |
| §4 Human gate | **Yes** — on `add`/`retire` only; `amend` auto. Justified by blast-radius asymmetry (unbounded-in-time vs 14d). Expires to **no-op**, never default-yes. |
| §5 Write-only sink | **Already a sink (N1).** Close at **Rung 1** first — create `approved_lessons.yaml`, which is already read *uncapped*. Rung 2 (axioms) is the durable channel. `[:3]` is **not** intended; it is a prompt-budget hack; it applies to `soul.yaml:lessons:` only. Lessons that can never reach behaviour → `cold_lessons.yaml` after 3 consecutive reviews (SINK-1), never deleted (M28). |
| §6 Ceiling gap | **Explicit `uninitialized`**, WARN-class, exit 0. Not hard-fail (13 identical day-one failures get blanket-waived) and not silent (the current lie). Flips to HARD when all 14 have ≥1 axiom, checked against `entities.yaml` — the prune's own roster. |
| §7 `lessons:` | **Re-point `soul_promote.py` → `approved_lessons.yaml`.** Argued on 4 grounds (template already says so; it's the only path that works; unbounded store in a public diffed file is a noise floor; `lessons:` is unvalidated). `jem`/`kali` migrated append-only, block retained + marked DEPRECATED. **Blocks bootstrap if not done first.** |
| §8 Bootstrap | **persona-first, lessons-second** — day-one axioms from lessons = axioms about recent accidents. Seed **3** per entity (below ceiling, leaves growth room). B4 (link-or-explicitly-decline) is mandatory or the sink survives. **Bottom-up pyramid order is mandatory** (N5). Bootstrap artifacts kept in `axiom_reviews/bootstrap/` so they never count as reviews. |

**Do these first, in this order — the ordering is the design:**
1. Fix the `grokster` resurrection bug in `run_scribe_on_meditations.py` (N4) — it is a
   live M28 defect independent of everything else here.
2. Ship Stage 0 normalization + create `approved_lessons.yaml` per entity — **closes the
   write-only sink in days, not sprints.**
3. Re-point `soul_promote.py`.
4. Bottom-up bootstrap of `core_principles` → `directives` → `axioms` for 13 entities.
5. Only then install the 14-day timer.

*A timer installed before step 2 means the first automatic run is also the first test of the
normalizer. That is how you find out your normalizer is broken at 03:17 on a Tuesday.*

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ S2 PERSISTENCE KEEPER ⬡ AXIOM_REVIEW_PROTOCOL ⬡ 2026-10-09 ⬡
DESIGN VALIDATION — NOT WIRED ⬡ opencode/space-bunny-free ⬡*
