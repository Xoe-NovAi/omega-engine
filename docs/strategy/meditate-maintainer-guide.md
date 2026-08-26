# 🔱 Meditate Maintainer's Guide — Change Protocol for the Three-Document Set

**AP Token**: `AP-MEDITATE-MAINTAINER-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_meditate_maintainer ⬡ CANONICAL

**Authority chain**: R53 granite evidence (`docs/research/R53_meditate_granite_foundation_20260826.md`, FROZEN)
→ process spec (`docs/strategy/MEDITATE_DOCUMENTATION_STRATEGY.md`)
→ **this guide** → System Reference (`docs/reference/meditate-system-reference.md`)
→ Invocation Guide (`docs/how-to/meditate-invocation-guide.md`) → live command (`.opencode/commands/meditate.md`).
Never cite tournament drafts or banner-flagged manual lines as rule sources.

---

## §1 Your Job

You maintain a three-document set that describes a five-phase adversarial meditation command.
Your failure mode is not bad writing — it is **partial update**: changing one location while four
tentacles of the same decision keep the old rule alive. Every structural decision in this system
has tentacles. This guide owns the maps.

## §2 The Cascade Principle

Before finalizing any change, answer six questions:

1. What invariant is being changed?
2. Where is it stated **directly**?
3. Where is it **implied** (exemplars, edge-case tables)?
4. Where is it **presupposed** (rules that depend on it)?
5. Which document holds each location?
6. Does the change need a new exemplar, or only updated text?

A change to one location is a change to all. Commit all affected documents in ONE commit.

## §3 Cascade Maps (worked examples — produce equivalents for any new directive)

### Map A — V1-Fix (R53 D1): Voice 1 emits highest-cost domain constraint, not status-quo anchor

| # | Location | Old encoding | Required change |
|---|----------|--------------|-----------------|
| 1 | SR — Behavioral Invariant 3 | "strongest case for status quo" | Rewrite to constraint-emission rule |
| 2 | SR — Worked Example parenthetical | anomaly disclosure of absent anchor | Delete or rewrite: N7-form IS canonical |
| 3 | SR — Edge Cases, 2-entry `--lenses` row | "Voice 1 anchors status quo" | "Voice 1 emits highest-cost constraint; Voice 2 dissents against it by name" |
| 4 | SR — Worked Example Voice 1 slot | preference-attack exemplar | Rebuild per constraint-not-preference template |
| 5 | IG — any Voice 1 description | "status quo defender" | Match new rule |
| 6 | Tournament artifacts / CARMACK_SYNTHESIS | merge recipe D3 old text | Historical — add correction note, do not rewrite history |

### Map B — D4 (rubric restated verbatim at verdict)

Direct: SR verdict schema (rubric field appears in Phase 0 AND Phase 4). Implied: worked-example
verdict block must show verbatim restatement, not paraphrase. Presupposed: rubric quality guidance
(§6 below). Risk if missed: agents paraphrase the rubric mid-run, silently re-adjudicating.

### Map C — D8 (count-first collision semantics)

Direct: SR collision section ("exactly N voices" semantics). Implied: Edge Cases table rows on
panel size; worked example shows count-first header. Presupposed: quota-anchoring discovery
(4 independent corpus runs reported exactly 3 voices when told to avoid exactly-3 collisions).
Risk if missed: panels re-anchor on the number they were told to avoid.

### Map D — D11 (resume semantics, Option B sanctioned conditional read)

Three locations: SR `--durable` flag contract + SR Phase 0 steps + IG flags table. The command's
Phase 0 must contain the conditional-read step or the SR claim is false. Update command and SR in
the same commit.

## §4 Trigger → Response Protocol

| Trigger | Affected documents | Sequence |
|---|---|---|
| Command contract change (field added/modified/removed) | SR (primary) → IG (if user-visible) → this guide's maps | SR first; one commit |
| New flag added | SR Flags + IG Flags table + new cascade map here | Flag mechanics in SR are authoritative definition |
| Lens roster changes (`config/wads/_omega_default/meditate/lenses.yaml`) | SR roster table | SSOT is lenses.yaml; SR table is cached — mark "VERIFY against lenses.yaml" |
| New behavioral invariant discovered | SR Invariants → worked example if touched | Check Voice 1 / collision / verdict blocks |
| New execution record added to corpus | This guide §6 tier assignment | Assign tier within one session of the record |
| Single-run L3 challenges an existing invariant | Flag as tension here | **Two-instance rule below** |

## §5 The Two-Instance Rule

**Never update a behavioral invariant from a single execution record.** One run = anomaly.
Two = signal. Three = pattern (Gick & Holyoak 1983, schema induction). Applies especially to:
collision behavior, Voice 1 output shape, Phase 4 field omissions. Quota anchoring became doctrine
because it appeared in 4 independent runs.

## §6 Corpus Evidence Library

Execution records live under `data/coordination/meditations/records/` (registry:
`MEDITATION_REGISTRY.md`). Tier assignment rules:

- **Tier 1 (teach from directly)**: cleanest demonstrations of current contracts.
  Current: `CONTEXT_PACKER_FIVE_VOICES`, `HIDDEN_GEMS_FIVE_VOICES`.
- **Tier 2 (teach with caveats)**: valuable but containing known-deprecated forms.
  Current: `W1_CANONICAL` (pre-D1 Voice 1), `LOST_VALUE_RECOVERY` (truncation-lie incident),
  `MAKALI_OVERRIDE` (operator override path).
- **Tier 3 (historical only)**: drift evidence, never cite as current form.
  Current: Ma'at-drift set (`maat_drift_*`).

New records: assign a tier within one session. If Tier 1, evaluate whether an SR exemplar
should be refreshed from it.

## §7 Rubric Guidance (what to teach about Phase 0 adjudication)

A good rubric: pre-committed, binary-per-criterion where possible, restated VERBATIM at verdict.
It is NOT: a vibes checklist, a post-hoc justification scaffold, or re-interpretable mid-run.
Rubric design follows question type: factual subjects get verifiability criteria; design subjects
get trade-off-named criteria; strategy subjects get falsifiable-prediction criteria (pairs with
D5 hit/miss accounting).

## §8 Acceptance Criteria You Run

Each document has a test defined in `MEDITATE_DOCUMENTATION_STRATEGY.md` §8:

- **IG**: zero-context agent classifies ≥4/5 gate-test questions correctly and forms a correct
  invocation consulting nothing else.
- **SR**: zero-context agent rebuilds `.opencode/commands/meditate.md` from SR alone with no
  invented rules; output matches phase skeletons verbatim.
- **This guide**: agent given the V1-change scenario finds all six Map-A locations and updates
  in correct sequence (SR → IG → maps).

Run the relevant criterion before any commit that touches structure. Any invented rule found by
the SR test becomes a new cascade-map entry here — that is the gap-closure loop.

## §9 Manual-Sync Checklist (run after ANY structural change)

1. SR invariants consistent with command?
2. SR edge-case table matches command's actual branches?
3. SR flag list matches command flags exactly?
4. Worked example demonstrates every invariant it cites?
5. IG flags table matches SR flags?
6. IG "what you'll see" excerpt matches current phase shapes?
7. All four cascade maps still accurate?
8. Corpus tiers current?
9. `use-meditate.md` banner still points here?
10. Line counts within ceilings (IG ≤80 · SR ≤260 · this guide ≤200)?

## §10 Ownership

| Document | Owner | Change authority |
|---|---|---|
| Invocation Guide | Any agent with ≥1 successful meditation on record | Propose; owner approves |
| System Reference | Kali (primary) or senior agent with Carmack review | Major changes require Architect review |
| Maintainer's Guide (this file) | Kali | Cascade maps peer-reviewed by cascade identifier |

*End — v1.0.0, produced from MEDITATE_DOCUMENTATION_STRATEGY.md §7/§8 during the 2026-08-26 dev sprint.*
