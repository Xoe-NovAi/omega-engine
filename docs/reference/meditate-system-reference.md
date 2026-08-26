# 🔱 Meditate System Reference — Complete Contracts for Reconstruction

**AP Token**: `AP-MEDITATE-SYSREF-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_meditate_sysref ⬡ CANONICAL

**Purpose**: An agent with zero prior context must be able to rebuild `.opencode/commands/meditate.md`
from this document alone, inventing no rules. Any invented rule is a documentation gap → file it in
the Maintainer's Guide (`docs/strategy/meditate-maintainer-guide.md`).

**Authority chain**: R53 evidence (`docs/research/R53_meditate_granite_foundation_20260826.md`, FROZEN,
cite-don't-edit) → `docs/strategy/MEDITATE_DOCUMENTATION_STRATEGY.md` → **this reference** → live command.
Lens SSOT: `config/wads/_omega_default/meditate/lenses.yaml` (roster table below is cached — VERIFY against it).

---

## §1 Invocation Contract

```
/meditate <subject> [--lenses <set>] [--durable] [--integrate]
```

| Flag | Semantics |
|------|-----------|
| *(none)* | Default lens roster from `lenses.yaml` (five voices) |
| `--lenses makali` | Ma'at (thesis), Lilith (antithesis), Kali (synthesis) |
| `--lenses a,b,c[,...]` | Named lenses (node names, custom stances, or personas); 2–7 entries valid |
| `--durable` | Opt-in phase persistence to disk; enables Phase 0 conditional resume (§6) |
| `--integrate` | Runs optional Phase 5 integration gate after verdict |

## §2 Phase Skeleton (shapes are normative — output must match verbatim)

```
PHASE 00 — TEMPLATE CHECK (minimal): verify command template loaded intact; abort on truncation.
PHASE 0   — CALIBRATION: subject intake, gate adjudication, rubric pre-commitment, voice count lock.
PHASE 1   — SEQUENTIAL PERSONA IMMERSION: each voice speaks alone, in sequence, full block format.
PHASE 2   — CROSS-DOMAIN COLLISION: pairwise tensions between voices; count-first semantics.
PHASE 3   — EMERGENT SEQUENCING: critical path derived FROM collisions (nothing exists without one).
PHASE 4   — KALI SYNTHESIS: verdict + rubric restated verbatim + tension hypothesis accounting.
PHASE 5   — INTEGRATION GATE (optional, --integrate only): dispatch readiness ruling.
```

Each phase emits its `◈ MEDITATE: PHASE N — NAME` header line before content.

### Phase 0 steps (ordered)

1. Restate the subject.
2. **Durable conditional read**: if `--durable` and a record file for this slug exists, read it
   and continue from the first missing phase; otherwise proceed fresh.
3. **Invocation gate**: classify the subject. If it fails (see §7 DECLINED), emit the DECLINED
   block and stop the ceremony.
4. **Rubric pre-commitment**: write the adjudication rubric NOW, before any voice speaks. Binary
   criteria where possible. This rubric is frozen; Phase 4 restates it VERBATIM.
5. **Voice count lock**: state the exact number of voices that will speak ("Exactly N voices will
   speak"). This number is committed before immersion begins.

## §3 Voice Block Format (every voice, every panel size)

```
◈ VOICE [k/N]: [DOMAIN LENS]
Domain: [domain]    Element: [element]
Mandate: Speak only from [domain]. Ignore all other domains.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[OBSERVATION]   What this domain sees at risk if the change proceeds. Domain-grounded, not rhetorical.
[CONSTRAINT]    The specific cost this domain cannot absorb. Named concretely: "X breaks because Y depends on Z."
[IMPERATIVE]    One directive — or explicit restatement of the highest constraint. Never manufacture urgency.
[DISSENT /      The highest-cost constraint AGAINST making this change, from this domain's view.
 CHALLENGE]     NOT a strawman. NOT "conventional wisdom says." Later voices grapple with THIS.
```

Separator rule (R53 D9): one divider line above the body, one below — half the previous density.

### Voice 1 exemplar (canonical form — domain-neutral content)

Voice 1 does NOT argue for the status quo and does NOT attack conventional wisdom. It reports its
domain's ceiling:

> ◈ VOICE [1/5]: RELIABILITY LENS
> Domain: systems reliability · Element: failure modes
> Mandate: Speak only from reliability engineering. Ignore all other domains.
> ──────────────────────────────────────────────
> [OBSERVATION] The proposal replaces a working admission-control path during an active sprint.
> [CONSTRAINT] If the new path drops a request class the old one handled, recovery requires
> re-deriving the fallback matrix under load — a cost this domain cannot absorb mid-sprint.
> [IMPERATIVE] Sequence the cutover behind a shadow-mode calibration period.
> [DISSENT / CHALLENGE] Highest cost against changing now: silent request-class loss during the
> swap window, discovered only by user-visible failures.

Later voices attack the CONSTRAINT — the fact, not a performance.

### Cited vs uncited dissent (R53 D2)

When a voice's dissent responds to an earlier voice, the response merges INTO the dissent slot:
name the prior voice, state the delta ("Kali claims X; my domain sees X fails when Y"), then the
constraint. There is NO separate comparison phase — comparative delta lives inside dissent.

## §4 Collision Semantics (R53 D8 — count-first)

Phase 2 opens by restating the locked voice count, then enumerates collisions until the genuine
set is exhausted. **If fewer than 3 genuine collisions exist, state how many exist and why. Do not
manufacture conflict — absence of collision is itself a signal.**

Known failure mode (quota anchoring, 4 independent corpus runs): panels told to "avoid exactly 3"
report exactly 3. Countermeasure: the Phase 0 count lock states the number as commitment, not as
a quota to dodge; Phase 2 never mentions any target quantity, only the enumeration of what exists.
Feedback loop: wide-lens low-collision results may narrow the lens set for a re-run.

## §5 Verdict Schema (Phase 4)

The verdict is not a summary or vote. Required fields, in order:

1. **VERDICT** — the irreducible truth emerging from collisions, not from averaging agreements.
2. **RUBRIC RESTATED VERBATIM** — the Phase 0 rubric, word-for-word, with pass/fail per criterion.
   Paraphrase here is a contract violation (it silently re-adjudicates).
3. **TENSION ACCOUNTING** — predicted tensions from Phase 2 treated as falsifiable hypotheses:
   list each, mark HIT (materialized in the run) / MISS (did not), with one-line evidence.
4. **DISSOLUTIONS** — which apparent conflicts dissolved under sequencing, and why.

## §6 Persistence & Resume (`--durable`)

Default is pure single-pass cognition — no file writes mid-meditation. With `--durable`, append
each completed phase to the record file (`data/coordination/meditations/records/MEDITATION_<slug>.md`,
≤80 lines per write) as it finishes. On stream death: completed phases exist in the record file.
Re-invoke with the same subject; at Phase 0 the conditional read (§2) resumes from the first
missing phase. The record is a checkpoint, not an artifact of automated resumption beyond this.

## §7 The DECLINED Block (R53 D10 — ceremony-only form)

When the invocation gate fails, the DECLINED block contains ONLY:

```
◈ MEDITATE: DECLINED
Failed gates: [gate IDs]
Reason: [one line]
Redirect: ask this as a plain prompt for a direct answer.
```

No partial answer INSIDE the refusal frame (RefusalBench 2026: partial compliance inside refusal
frames creates false confidence — the most dangerous output category). If the subject is simple
enough to answer directly (it usually is, per the gate rationale), the direct answer follows
OUTSIDE the ceremony, in plain prose, labeled: `— Direct answer (outside meditation frame) —`.

## §8 Anti-Domain Contamination Guard (Option A — wired into command)

At Phase 1, each voice receives one appended instruction line (~15 tokens): *"If your mandate
requires leaving your domain to answer, say so explicitly in [IMPERATIVE] as OUT-OF-DOMAIN rather
than silently crossing."* Silent domain-crossing is a contamination violation; declared crossing
is honest uncertainty. This applies to every voice including synthesis-adjacent ones.

## §9 Behavioral Invariants

1. Voices speak sequentially, alone; no voice sees another's output before speaking (except the
   dissent-slot delta of §3, which references already-spoken voices only).
2. Phase 3 derives exclusively from Phase 2 collisions; no imperative exists without a collision.
3. Voice 1 emits the highest-cost constraint its domain sees against making this change — never a
   status-quo performance, never a doctrine-attack preference.
4. The rubric is frozen at Phase 0 and restated verbatim at Phase 4.
5. The voice count is locked at Phase 0 and never renegotiated mid-run.
6. Collisions are enumerated, never manufactured; genuine absence is reported as signal.
7. Panel size 2–7; lens SSOT is `lenses.yaml`.
8. Zero downstream parser surface: nothing consumes meditation output programmatically; format
   serves human/agent readers only. This licenses the ◈ ceremonial format.

## §10 Edge Cases

| Case | Behavior |
|------|----------|
| 2-entry `--lenses` set | Voice 1 emits its highest-cost constraint; Voice 2 dissents against it BY NAME; verdict proceeds on the pair |
| Single lens | Invalid — minimum 2; decline with gate reason |
| >7 lenses | Invalid — maximum 7; decline with gate reason |
| Lens name not in roster and not a named stance/persona | Treat as custom persona: synthesize mandate from the name; note synthesis in voice header |
| Stream death mid-run (no `--durable`) | Work lost; re-run from Phase 0 (honest capability) |
| Stream death mid-run (`--durable`) | §6 resume path |
| Subject fails invocation gate | §7 DECLINED form |

## §11 Command Acceptance Criteria (preserved from corpus)

1. Every voice block contains all four slots ([OBSERVATION]/[CONSTRAINT]/[IMPERATIVE]/[DISSENT]).
2. Phase 2 enumerates genuine collisions with count-first framing; manufactured conflict absent.
3. Phase 4 verdict contains verbatim rubric restatement and tension accounting.
4. Output matches §2 skeleton shapes; all §9 invariants hold; all §10 cases handled.

**Command constraints**: hard ceiling **350 lines** (re-ratified 2026-08-26; original 320 was
derived from Gemma 4 31B / Google free-tier 16K input cap — a provider-specific limit, not
universal; Architect Q1 confirmed mid-run SR access; Carmack audit recommends 350 lines /
~4,600 tokens ≈ 28.8% of actual workhorse cap); separators minimal (§3); zero parser surface (§9.8).

*End — v1.0.0. Reconstructors: if you needed a rule not stated here, that is a gap — report it to
the Maintainer's Guide owner for a new cascade-map entry.*
