---
schema_version: "1.0"
document_type: strategy
llm_metadata:
  token_budget: 8000
  audience: agents writing or maintaining any meditate documentation artifact
  executes: false
---

# Meditate Documentation Strategy
## The Definitive Guide for Agents Writing the Three-Audience Manual Set

**AP Token**: `AP-MEDITATE-DOC-STRATEGY-v1.0`
⬡ OMEGA ⬡ KALI/SONNET ⬡ trc_meditate_doc_strategy ⬡ 2026-08-26
**Evidence base**: R53 Granite Foundation (a0a43c82) · 16-record execution corpus · Expert tournament artifacts · Deep review of plan flaws and gaps
**Purpose**: Strategy and agent brief for producing the three-audience documentation set that replaces the current single `use-meditate.md`. Every section is actionable; nothing here requires policy invention at write time.

---

## §0 WHY THIS DOCUMENT EXISTS — THE PROBLEM WITH THE CURRENT PLAN

The remediation plan (R53 + 12 build directives) is a correct specification for the *command*. The mission here is different: teach the team to produce documentation for the meditation system. These are not the same task.

The current `use-meditate.md` serves three audiences simultaneously and serves none of them well:

| Audience | Their task | What they need | What the current manual gives them |
|---|---|---|---|
| **Invoker** | Decide whether to run `/meditate` and how | Fast orientation, flag reference, output preview | 66 lines of useful content buried under 293 lines of reference material |
| **Reconstructor** | Rebuild the command from scratch with no other context | Every contract, invariant, and decision with rationale | The contracts exist but the rationale is 7 compressed lines at the bottom no one reads before writing |
| **Maintainer** | Update the manual and command when behavior changes | Cascade maps, maintenance protocol, corpus-as-evidence, design principles | Nothing — this audience is unserved entirely |

**The plan as inherited has four critical flaws the guide-writing agents must avoid:**

1. **The R53 directives are command specs, not documentation specs.** D1–D12 tell you what the command should do. The documentation task is to make those decisions legible to readers — a different operation with different success criteria.

2. **The manual-sync checklist (R53 §6) is a patch map, not a maintenance protocol.** It tells you where to change text; it does not teach why the change matters to a reader or how to verify the change produced understanding.

3. **The cascade problem is underspecified.** The Voice-1 fix (D1) touches five locations in the manual, not two. The plan missed three of them. Every structural change has a cascade; the guide must map them.

4. **The split decision (user manual + technical guide) still leaves the maintainer unserved.** The correct architecture is three documents, not two.

---

## §1 THE STRATEGY — THREE DOCUMENTS, THREE PURPOSES

### The Three-Document Architecture

```
docs/how-to/
├── meditate-invocation-guide.md      # AUDIENCE 1: Invokers
│   "Should I run /meditate? How?"
│   Target: ~60–80 lines. Fast. Decision-oriented.
│
docs/reference/
├── meditate-system-reference.md      # AUDIENCE 2: Reconstructors
│   "I need to rebuild /meditate from scratch."
│   Target: ~180–220 lines. Complete. Every contract, invariant, edge case.
│
docs/strategy/
└── meditate-maintainer-guide.md      # AUDIENCE 3: Maintainers (this gap)
    "The command changed. What do I update and in what order?"
    Target: ~150–200 lines. Process-oriented. Corpus-grounded.
```

The current `use-meditate.md` (359 lines) is NOT simply split. It is:
- **Partially retired**: Design Basis (lines 346–352) expands into the Maintainer's Guide
- **Partially migrated**: lines 1–66 become the Invocation Guide's foundation
- **Partially retained and corrected**: lines 67–352 (minus Design Basis) become the System Reference, with all 10 cascade corrections applied
- **Superseded**: a single AP-Token banner points to the three new documents

The three documents are maintained independently but linked: the Invocation Guide references the System Reference for depth; the System Reference references the Maintainer's Guide for change protocol. The Maintainer's Guide owns the cascade maps and the corpus evidence library.

### Why Not a Simple Split?

The Architect flagged "user manual + technical guide" as possibly more profitable. This review confirmed the seam is real (lines 1–66 / 67–352) but found a third audience the split leaves unserved. The argument for three documents:

- A two-way split duplicates the sync problem. The current manual is already behind the command (manual:199 claims interest-based resolution; the command never instructs it). Two documents double the surface that can drift. **Three documents with an explicit Maintainer's Guide that owns the sync protocol creates an owner for the drift problem rather than just splitting it.**
- The Reconstructor and the Maintainer are different agents with different needs. A reconstructor needs to read contracts; a maintainer needs to understand what happens when a contract changes. Conflating them in one document produces a document that does neither well.

---

## §2 THE CASCADE PRINCIPLE — WHAT EVERY WRITING AGENT MUST UNDERSTAND

**The most dangerous documentation error is a partial update.** Every structural decision in the meditation system has tentacles. The V1-fix cascade is the worked example of how cascades work — every agent writing any of the three documents must apply this thinking to every change they make.

### The V1-Fix Cascade (Complete Map)

The decision: Voice 1 no longer argues for the status quo. Voice 1 now emits its highest-cost domain constraint against change (authentic domain view, per R53 D1).

Every location that encodes the old rule, directly or by implication:

| Location | Current text (old rule) | Required change | Risk if missed |
|---|---|---|---|
| System Reference — Invariant 3 | "Voice 1 opens with the strongest case for the status quo" | Rewrite: "Voice 1 emits the highest-cost constraint its domain sees against making this change" | The invariant directly contradicts the contract |
| System Reference — Worked Example parenthetical (line 223) | "status-quo anchor is absent here because N7 opens with observation + doctrine challenge" | Delete parenthetical OR rewrite: "N7's behavior here IS the canonical Voice-1 form" | The parenthetical was an anomaly disclosure; it now misrepresents the norm as exceptional |
| System Reference — Edge Cases (line 290) | "Voice 1 anchors status quo, Voice 2 dissents" for 2-entry `--lenses` sets | Rewrite: "Voice 1 emits its highest-cost constraint; Voice 2 dissents against it by name" | Prescribes deprecated behavior for the smallest-panel case |
| System Reference — Worked Example Voice 1 slot (lines 226–248) | N7 CONTEXT emits a methodological preference attack | **Rebuild the Voice 1 exemplar slot** to demonstrate: "The highest cost my domain sees in changing X is Y" — a constraint, not a doctrine challenge | The exemplar demonstrates neither the old rule nor the new rule correctly |
| Invocation Guide — if it describes Voice 1 behavior at all | Any description of Voice 1 as "status quo defender" | Update to match new rule | Reader learns incorrect behavior from the entry-level document |
| Tournament drafts / CARMACK_SYNTHESIS | Merge recipe D3: "Voice 1 anchors status quo" | Update the synthesis notes — these are historical artifacts but may be referenced | Future agents reading the artifacts may apply the old rule |

**Rule for all writing agents**: before finalizing any section that touches an invariant, trace every place that invariant appears in all three documents and in the command. A change to one is a change to all.

### How to Apply Cascade Thinking

For any structural change, ask:
1. What is the invariant being changed?
2. Where is it stated (direct)?
3. Where is it implied (exemplars, edge cases, edge-case tables)?
4. Where is it *presupposed* (other rules that depend on it)?
5. Which of the three documents is each location in?
6. Does the change require a new exemplar, or just updated text?

Apply this to every R53 directive before writing. The cascade map for D1 is above. The writing agents must produce equivalent maps for D4 (pre-committed rubric — what is the cascade when the rubric field exists in Phase 0 AND Phase 4?), D8 (count-first collisions — what does the Edge Cases table say now?), and D11 (resume semantics — three manual locations).

---

## §3 THE CORPUS AS PEDAGOGY — HOW TO TEACH FROM EVIDENCE

**The 16-record execution corpus is the most powerful teaching asset in the system.** R53 used it for validation. The documentation must use it for instruction.

### The Teaching Tiers

Every record in the corpus belongs to a teaching tier. Writing agents assign tier based on protocol compliance:

**Tier 1 — Gold Standard** (what correct behavior looks like at scale):
- `MEDITATION_KALI_20260823_CONTEXT_PACKER_ENHANCEMENT.md` (529L) — 10 voices, format fidelity identical at Voice 1 and Voice 10, full mandate check M1–M25. The largest run. Use to demonstrate: what a 10-voice meditation looks like, what "anti-collapse held" means concretely, what Phase 4 with all nine fields in order looks like.
- `MEDITATION_KALI_20260822_HIDDEN_GEMS.md` (295L) — 5-lens panel, full template fidelity. Use to demonstrate: the gold-standard Voice 1 (N7 CONTEXT), the correctly-formed collision block, the proper-noun-free L3 principle.

**Tier 2 — Honest Execution** (compliant but revealing edge behavior):
- `MEDITATION_lilith_20260824_W1_CANONICAL_REGISTRATION.md` (230L) — contains the honest collision count: "Exactly 3 genuine collisions; none manufactured." Use to demonstrate: what an honest zero-inflation count looks like.
- `MEDITATION_kali_20260824_LOST_VALUE_RECOVERY.md` (44L) — claimed COMPLETE while containing only Phases 2–4. Use to demonstrate: the truncation failure mode and why `--durable` exists.
- `MEDITATION_kali_20260824_MAKALI_COUNCIL_REBASE.md` (130L) — the council decreed serial launches; Architect overrode it post-hoc. Use to demonstrate: the verdict is the strongest structured argument in-session, not ground truth.

**Tier 3 — Instructive Drift** (what happens when documentation fails to constrain):
- `MEDITATION_maat_20260824_W2_CLAIMS_HARNESS.md` (40L) — uses Pass 1/2/3 format instead of Phase 0–4. No Phase 0 block. No lens contract. No collision blocks. High-quality reasoning inside a completely wrong structure.
- `MEDITATION_maat_20260824_D602_TORCHFREE.md`, `MEDITATION_maat_20260824_N4_DELETIONS.md`, and the other maat records — same structural drift pattern. Use to demonstrate: what the meditation system produces when an agent knows the subject but hasn't internalized the protocol. The quality of the thinking is irrelevant; the structure is what makes output comparable, composable, and auditable.

**The core teaching moment**: put `W2_CLAIMS_HARNESS` (Tier 3, 40L) next to `CONTEXT_PACKER` (Tier 1, 529L). Both contain high-quality reasoning. Only one can be audited against the protocol, compared to other runs, or yield a verifiable L3. The structure IS the product — not decoration on top of it.

### How to Embed Corpus Evidence in Documentation

Each document type uses the corpus differently:

**Invocation Guide**: one "What you'll actually see" excerpt from CONTEXT_PACKER Phase 0 (lines 1–6 of the record) — the actual output shape, no paraphrasing.

**System Reference**: the worked example section references specific records for each contract element. For Voice 1: the new exemplar (rebuilt per §4 below). For collisions: `LOST_VALUE_RECOVERY`'s Phase 2. For Phase 4 nine-field structure: `CONTEXT_PACKER`'s Phase 4. For drift: a one-paragraph pointer to the maat records with an explicit note that the quality of the thinking is not the failure — the structure is.

**Maintainer's Guide**: the corpus teaching tiers above become a living Corpus Evidence Library. New records are assigned tiers as they are written. When a new behavioral pattern is observed in a Tier 1 or 2 record, the Maintainer's Guide is updated first, then the System Reference, then the Invocation Guide (if user-facing).

---

## §4 THE EXEMPLAR PROBLEM — HOW TO REBUILD THE VOICE 1 SLOT

The current worked example's Voice 1 slot is doubly wrong: it doesn't follow the old rule (status-quo defense) and it won't follow the new rule (authentic highest-cost domain constraint) without being rebuilt. The parenthetical explains it as an anomaly. After D1, it must demonstrate the norm.

### What the New Voice 1 Exemplar Must Show

The new rule (R53 D1): Voice 1 emits the **highest-cost constraint its domain sees against making this change** — not an attack on conventional wisdom, not a preference, not a strawman. A constraint: the domain-grounded cost that would be incurred if the change proceeded.

The old N7 Alchemist voice demonstrates: "Against archaeology-first doctrine: recency beats antiquity." This is a methodological preference attacking an external doctrine. It is NOT a domain constraint against change.

A correct Voice 1 in the new model, using domain-neutral content, looks like:

```
◈ VOICE [1/5]: [DOMAIN LENS]
Domain: [domain]    Element: [element]
Mandate: Speak only from [domain]. Ignore all other domains.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[OBSERVATION]
[What this domain sees that is genuinely at risk if the change proceeds —
 domain-grounded, not rhetorical. 1–3 sentences.]

[CONSTRAINT]
[The specific cost this domain cannot absorb. Named concretely: not
 "this will be hard" but "X will break because Y depends on Z."]

[IMPERATIVE — or CONSTRAINT]
[One directive or restatement of the highest constraint. If no directive
 exists, state the constraint explicitly. Never manufacture urgency.]

[DISSENT / CHALLENGE]
[The highest-cost constraint against making this change, from this
 domain's perspective. NOT a strawman. NOT "conventional wisdom says."
 Something concrete that later voices must actually grapple with.]
```

**The critical distinction**: the old rule asked Voice 1 to perform a position (argue for doing nothing). The new rule asks Voice 1 to report a domain fact (what my domain's ceiling is). The former is theater; the latter is information. Later voices attack Voice 1's constraint slot — not the performance, the constraint.

### The Contamination Guard

Both R53 and the tournament experts flagged using domain-neutral content in the exemplar (D6). The reason is syntactic priming: demonstration content bleeds into outputs (SyntaxPrime, SEM 2026). The new exemplar must:

1. Use a **non-Omega, non-meditation subject** (not "should we migrate to sqlite-vec" — that's an Omega decision that primes Omega-flavored outputs)
2. Use **no vivid proper nouns** (no "Alchemist," "N7," "Recency beats antiquity" — these stamp)
3. Demonstrate **the shape of a constraint**, not the shape of a preference
4. Keep the **cited vs uncited dissent pair** adjacent — this teaches the citation contract separately from the content

Suggested neutral subject for the exemplar: "switching the team's primary communication channel from X to Y." Concrete enough to ground the constraint demonstration; generic enough to not prime any specific domain's content.

---

## §5 THE RUBRIC QUALITY PROBLEM — WHAT TO TEACH ABOUT PHASE 0 ADJUDICATION CRITERIA

R53 D4 requires a pre-committed adjudication rubric in Phase 0, restated verbatim in Phase 4. Neither R53 nor the tournament drafts specify what makes a good rubric. This is the gap agents must fill when writing the System Reference's Phase 0 section.

### What a Good Rubric Is

A pre-committed adjudication rubric answers the question: **by what criteria will I decide between competing positions, stated before I know what those positions are?**

Good rubrics have three properties:
1. **They are criteria, not conclusions.** "Prefer the solution with fewer moving parts" is a criterion. "We should use sqlite-vec" is a conclusion. A rubric must not presuppose its own verdict.
2. **They name the tradeoff axes.** "Weight operational simplicity above raw performance" names the axis (simplicity vs performance) and the weighting direction. A rubric without an axis is a wish, not a criterion.
3. **They are falsifiable.** After the verdict is reached, it must be possible to check whether the rubric was actually applied. If the rubric said "weight simplicity above performance" and the verdict chose the complex high-performance option, a reader can ask: was the rubric overridden, and why?

### What a Rubric Is NOT

- "Use the most elegant solution" — not falsifiable (elegance is undefined)
- "Consider all perspectives equally" — not a criterion (it doesn't break ties)
- "Apply the Sovereign Mandates" — scope too wide (every decision does this; naming it adds nothing)
- "Choose the fastest implementation" — this may be a conclusion dressed as a criterion (fastest to implement, or fastest at runtime?)

### Rubric Design by Question Type

The System Reference should teach rubric design with examples by question type:

| Question type | Example subject | Good rubric elements |
|---|---|---|
| Migration decision | Should we move from Qdrant to sqlite-vec? | Weight: operational complexity · data-integrity risk during migration · reversibility · performance delta at current scale |
| Architecture decision | Should the Oracle call Iris directly or via queue? | Weight: failure isolation · latency budget · cognitive load for maintainers · consistency with existing patterns |
| Governance decision | Does this implementation comply with M1 AnyIO? | Weight: literal compliance · spirit compliance · deviation cost if non-compliant · precedent set |
| Prioritization decision | Which of P0–P3 tickets ships in this sprint? | Weight: unblocking value · irreversibility of delay · resource cost · risk if deprioritized |

**The key teaching point**: a good rubric is written knowing the question but NOT knowing the answers the voices will produce. It should be possible to write the rubric before the meditation begins and have it still be applicable after all voices have spoken.

---

## §6 THE ANTI-DOMAIN ENFORCEMENT GAP — A DECISION REQUIRED BEFORE WRITING

The System Reference currently states: "each lens bans exactly three domains" and "only governance may challenge governance." Neither the command nor any behavioral invariant enforces this. Anti-domains exist in `lenses.yaml` but are never injected into the voice block instruction during a meditation.

**This is a documented behavior that is not implemented behavior.** Before writing the System Reference, the Architect must decide:

**Option A — Wire anti-domains into the command**: Each voice block's Mandate line becomes "Speak only from [domain]. Do NOT address [anti-domain-1], [anti-domain-2], [anti-domain-3]." This costs ~15 tokens per voice per run and makes the anti-domain constraint enforceable. The System Reference documents it as enforced.

**Option B — Label anti-domains advisory**: The System Reference adds a disclosure: "Anti-domains in `lenses.yaml` are advisory metadata — the command does not enforce them. They express the intended focus of each lens; violations are caught by the Reconstructor's review, not by automated enforcement." This is honest about current state.

**Option C — Remove anti-domains from the manual**: If anti-domains don't affect output and aren't enforced, their documentation creates false expectations without adding value.

**Recommendation**: Option A if the command rewrite is imminent (wire it in the new command, document it as enforced). Option B if the command rewrite is deferred (document current honest state, flag as a known gap). Option C is a last resort.

**Writing agents**: do not write the System Reference's anti-domain section until this decision is made. The section you write will differ materially depending on the answer.

---

## §7 THE MAINTENANCE PROTOCOL — WHAT THE MAINTAINER'S GUIDE MUST CONTAIN

This is the section the current plan entirely omits. The Maintainer's Guide answers: "The system changed. What do I do?"

### Trigger Conditions and Response Protocol

| Trigger | Affected documents | Sequence |
|---|---|---|
| Command contract changes (new field, modified field, removed field) | System Reference (primary) → Invocation Guide (if user-visible) | Update SR first. Check Invocation Guide for any user-facing description of the affected contract. Update the cascade map in Maintainer's Guide. Commit all three in one commit. |
| New flag added | System Reference (Flags section) + Invocation Guide (Flags table) + Maintainer's Guide (cascade map for new flag) | Three-document update. Flag mechanics section in SR is the authoritative definition; IG flags table is a user-facing summary. |
| Lens roster changes (`lenses.yaml`) | System Reference (Lens Roster table) + any worked example that uses the changed lens | SR table is a cached representation; the SSOT is `lenses.yaml`. Update SR table + add note "VERIFY against lenses.yaml" in SR. |
| New behavioral invariant discovered | System Reference (Behavioral Invariants section) + cascade to Worked Example if exemplar must be updated | Invariants section first. Check whether the new invariant touches the worked example's Voice 1, collision, or verdict blocks. |
| New execution record added to corpus | Maintainer's Guide (Corpus Evidence Library, tier assignment) | Assign tier within one session of the record being written. If Tier 1, check whether any system reference exemplar should be updated to use the new record. |
| L3 principle from a run challenges an existing invariant | Maintainer's Guide (flag as tension), System Reference (if invariant must be updated) | Never update the System Reference from a single run's L3 alone. Require ≥2 records showing the same pattern before updating a behavioral invariant. This is the Gick & Holyoak two-instance schema induction rule applied to documentation. |

### The Ownership Model

Each document has one owner. The owner is responsible for:
- Accepting change requests from other agents
- Verifying the cascade before committing
- Updating the Corpus Evidence Library tier when new records appear

| Document | Owner | Change authority |
|---|---|---|
| Invocation Guide | Any agent with ≥1 successful meditation on record | Propose; owner approves |
| System Reference | Kali (primary) or any senior agent with Carmack review | Major changes require Architect review |
| Maintainer's Guide | Kali | Cascade maps must be peer-reviewed by the agent who identified the cascade |

### The Two-Instance Rule for Behavioral Changes

**Never update a behavioral invariant from a single execution record's evidence.** One run showing unexpected behavior is an anomaly. Two runs showing the same pattern is a signal. Three is a pattern. The two-instance minimum (Gick & Holyoak 1983 schema induction) is the documentation equivalent of the L3 distillation gate — you cannot generalize from one case.

This applies especially to: collision behavior, Voice 1 output shape, Phase 4 field omissions. The corpus discovery of quota anchoring was valid because it appeared in 4 independent runs. A single run claiming "zero genuine collisions" is data; it becomes doctrine only when replicated.

---

## §8 THE DOCUMENTATION ACCEPTANCE CRITERIA — HOW TO KNOW WHEN EACH DOCUMENT IS DONE

The current manual's acceptance criteria (lines 326–335) test the *command's* output. These are preserved in the System Reference. Each document additionally has its own acceptance criterion testing whether it fulfills its purpose for its audience.

### Invocation Guide — Acceptance Criterion

**Test**: Give the Invocation Guide to an agent with zero prior context on the meditation system. Ask: "Should I run `/meditate` on this question, and if so, how?" Measure:
- Does the agent correctly classify ≥4 of 5 test questions as meditate-appropriate or not? (Gate test success rate)
- Can the agent produce a correctly-formed invocation with the right flag for a given scenario within 2 minutes of reading the guide?
- Does the agent need to consult any other document to form the invocation?

If the answer to the third question is "yes" for any basic invocation, the Invocation Guide is incomplete.

### System Reference — Acceptance Criterion

**Test**: Give the System Reference to an agent with zero prior context and the instruction: "Rebuild `.opencode/commands/meditate.md` from this document alone." The resulting command passes if:
- The three command acceptance criteria (current manual lines 330–335) all pass
- The rebuilt command produces output that matches the Phase 0–4 skeleton shapes verbatim
- The rebuilt command correctly handles all edge cases in the Edge Cases table
- No rule had to be invented (any invented rule is a documentation gap)

If any rule had to be invented, the Maintainer's Guide gets a new cascade map entry identifying the gap.

### Maintainer's Guide — Acceptance Criterion

**Test**: Give the Maintainer's Guide to an agent and present this scenario: "The Architect has decided Voice 1 should no longer argue for the status quo. It should instead emit its highest-cost domain constraint against change. Update all three documents." Measure:
- Does the agent find all five cascade locations (Invariant 3, worked example parenthetical, Edge Cases 2-entry set, Voice 1 exemplar slot, tournament artifact notes)?
- Does the agent update them in the correct sequence (System Reference → Invocation Guide → Maintainer's Guide cascade map)?
- Does the agent identify whether the Invocation Guide needs updating for this specific change?

If any cascade location is missed, the Maintainer's Guide's cascade maps are incomplete. The missed location becomes a new map entry.

---

## §9 AGENT BRIEFS — WHAT EACH WRITING AGENT IS RESPONSIBLE FOR

### Agent Writing the Invocation Guide

**Your single constraint**: a reader who finishes this guide should be able to decide whether to run `/meditate` and form a correct invocation without reading anything else.

**What to include**:
- What `/meditate` is (one paragraph — the "one inference, multiple specialist roles" framing)
- The 2-of-3 gate test (when to use it) — concrete, with examples of gate-pass and gate-fail subjects
- How to invoke (flags table with defaults — concise, match the System Reference exactly)
- What you'll see (one Phase 0 excerpt from an actual record — CONTEXT_PACKER or HIDDEN_GEMS — raw, not paraphrased)
- Cost and duration (from real corpus data: 9K–45K tokens, 15–45 min, $0.41–$0.62 at mid-tier)
- One sentence each on: when NOT to use it, what it cannot do

**What to exclude** (belongs in System Reference):
- Output contracts and skeletons
- Behavioral invariants
- Edge cases (beyond the gate-fail case)
- Design basis and rationale
- Acceptance criteria

**Target**: 60–80 lines. If it exceeds 80 lines, something belongs in the System Reference instead.

**Verify before submitting**: give to one agent with zero context. If they ask "but what does Phase 3 look like?" — that question is healthy (they can consult the System Reference). If they ask "but when should I use `--mode DIAGNOSTIC`?" — that question means the guide is incomplete.

### Agent Writing the System Reference

**Your single constraint**: a reader who finishes this document should be able to rebuild the command without inventing any policy. Every rule must be present; every decision must have a rationale.

**What to include**:
- The Lens Roster (table from `lenses.yaml` — with VERIFY header and SSOT pointer)
- Panel Sizing rules (with the research grounding: Self-MoA correlated noise beyond 5)
- Mode Conditioning (with the pre-mortem evidence for DIAGNOSTIC — prospective hindsight +30%)
- All output contracts verbatim (Phases 0–5 skeletons)
- The rebuilt Voice 1 exemplar (per §4 above — domain-neutral, demonstrates the constraint not the preference)
- The cited vs uncited dissent pair (keep this — it's the clearest possible teaching of Invariant 4)
- Anti-domain section (per the Architect's ruling on Option A/B/C from §6 above)
- All nine behavioral invariants with rationale inline (because reconstructors who know WHY don't silently drop rules)
- The Worked Example (rebuilt to demonstrate the new Voice 1 rule, using HIDDEN_GEMS or CONTEXT_PACKER as source)
- Edge Cases table (updated for V1-fix cascade items — particularly the 2-entry `--lenses` case)
- Long-Output Hygiene section (4K-token cliff, countermeasures)
- Flag Mechanics Reference
- Post-Meditation Workflow
- Real-World Performance table (from corpus data)
- Acceptance Criteria (the three command output tests)
- Limitations

**What to exclude**:
- Usage decision guidance (belongs in Invocation Guide)
- Maintenance protocol (belongs in Maintainer's Guide)
- Design basis rationale (expands into Maintainer's Guide; keep a one-line pointer only)

**Target**: 180–220 lines. Hard ceiling: 260 lines (beyond this the document starts serving the Maintainer's audience, not the Reconstructor's).

**Critical: apply all V1-fix cascade locations before finalizing.** Every location in the cascade map (§2 above) must be updated. Run the Acceptance Criterion test before submitting.

**The two open items (D10 and D11)**: do not finalize the DECLINED block or the stream-death edge case until the Architect rules. Write placeholder text: `[D10: DECLINED form — pending Architect ruling]` and `[D11: Resume semantics — pending Architect ruling]`. Submit the rest.

### Agent Writing the Maintainer's Guide

**Your single constraint**: a reader who finishes this document should be able to handle any documentation change correctly — meaning they find every affected location, update them in the right order, and verify the cascade is complete.

**What to include**:
- The three-document ownership model (§7 above)
- The trigger-condition/response table (§7 above)
- The full cascade map for every structural change in the current remediation plan:
  - V1-fix cascade (five locations, from §2 above — the worked example)
  - D4 cascade (pre-committed rubric in Phase 0 AND Phase 4 — what changes where)
  - D8 cascade (count-first collisions — Edge Cases table, any description of Phase 2 behavior)
  - D11 cascade (resume semantics — three manual locations)
- The two-instance rule for behavioral changes (§7 above)
- The Corpus Evidence Library (tier assignments for all 16 records, per §3 above)
- Rubric design guidance (§5 above — what makes a good vs bad rubric)
- The documentation acceptance criteria for all three documents (§8 above)
- The anti-domain enforcement decision and its cascade implications (once the Architect rules)

**How to organize it**: by trigger type, not by document. A maintainer's first question is "what changed?" not "which document am I editing?" The trigger-response table is the entry point; the cascade maps are the body; the corpus library and rubric guidance are the appendices.

**Target**: 150–200 lines. Unlike the other two documents, the Maintainer's Guide may grow over time as new cascade maps are added. The target is a floor, not a ceiling. Quality metric: does it leave any gap that would cause an agent to miss a cascade location?

---

## §10 THE OPEN DECISIONS — WHAT MUST BE RESOLVED BEFORE FINALIZING

Two items in the command specification are still open. Both affect the System Reference. The guide-writing agents must not finalize these sections until the Architect rules.

### D10 — DECLINED Block Form

**The question**: when a subject fails the invocation gate, should the DECLINED block contain a direct answer to the subject, or only a redirect?

**Evidence** (R53 V9, Researcher H9): RefusalBench (2026) found that partial answers inside refusal frames create false confidence — the partial-compliance mode is the most dangerous output category. Learn-to-Refuse (arXiv:2311.01041) found clean refusal maintained answer quality vs answering out-of-scope. **These support redirect-only.**

**Counter-evidence** (Jem feasibility A7): gate-failed subjects are by definition simple enough to answer directly (that's the gate rationale). The direct answer is the user-value payload of a decline. A redirect that provides no content may frustrate users with simple questions. **This supports redirect + direct answer.**

**The compromise that splits the difference**: the DECLINED block contains only: failed gate IDs, one-line reason, and one-line redirect ("ask this as a plain prompt for a direct answer"). The direct answer follows OUTSIDE the DECLINED ceremony, in plain prose without the ◈ header. This separates the ceremonial refusal from the content delivery, avoiding the "partial compliance inside refusal frame" failure mode while preserving the user value.

**This is a recommendation, not a ruling.** The Architect decides.

### D11 — Resume Semantics

**The question**: when a stream dies mid-run with `--durable`, does the command resume from the last persisted phase, or is work accepted as lost?

**Evidence** (Jem A6): nothing implements resume automation for `/meditate`. The `--durable` flag only guarantees phases are persisted. Resuming would require a fresh inference that reads the record file — an unsanctioned multi-step agentic operation not described anywhere.

**Options**:
- **Option A (loss-acceptance)**: "Stream dies with `--durable`: completed phases exist in the record file. Re-run from Phase 0; the record file is a checkpoint for your review, not for automated resumption." Honest about current capability.
- **Option B (sanctioned conditional read)**: "Stream dies with `--durable`: completed phases exist in the record file. Re-invoke with the same subject; at Phase 0, if a durable record for this slug exists, read it and continue from the first missing phase." This makes the claim true by wiring in the behavior — costs ~25 tokens in the command, requires the Phase 0 contract to include a conditional-read step.

**Recommendation**: Option B is cleaner for users but requires a command change (a file read at Phase 0 for `--durable` runs). Option A is honest today. If the command rewrite is happening anyway, Option B costs nothing extra. If the manual is being updated without a simultaneous command rewrite, Option A avoids promising behavior that doesn't exist.

---

## §11 THE SEQUENCING — WRITE IN THIS ORDER

1. **Architect resolves D10 and D11** (otherwise System Reference has two stubs)
2. **Architect resolves anti-domain enforcement** (Option A/B/C from §6) — this determines the System Reference's anti-domain section
3. **Maintainer's Guide is drafted first** — it contains the cascade maps that the System Reference author needs. Writing it first forces the cascade-thinking discipline before touching the primary documents.
4. **System Reference is drafted second** — with cascade maps in hand, every update location is known before writing begins. The V1 exemplar is rebuilt per §4; the anti-domain section reflects the Architect's ruling; D10/D11 stubs are placed.
5. **Invocation Guide is drafted last** — it draws from the System Reference for precision and from the corpus for its "what you'll see" excerpt. It is the simplest document but depends on the others being stable.
6. **Cascade verification pass** — one agent runs the Maintainer's Guide acceptance criterion test against all three documents before committing.
7. **`use-meditate.md` is superseded** — the current file gets a header banner pointing to the three new documents. It is not deleted (it contains historical Acceptance Criteria that the corpus references).

---

## §12 ARTIFACT REGISTRY — AUTHORITY MAP (consolidated 2026-08-26)

Single declaration of which artifact governs what. On conflict, the higher-ranked source wins.

| Rank | Artifact | Status | Governs |
|---|---|---|---|
| 1 | `docs/research/R53_meditate_granite_foundation_20260826.md` | **FROZEN — evidence SSOT** | All design verdicts; the 12 directives; corpus findings |
| 2 | This document | **LIVE — process SSOT** | Documentation architecture; cascade maps; maintenance protocol; agent briefs |
| 3 | `docs/how-to/use-meditate.md` v2.3 | **LIVE w/ ADVISORY BANNER** | Command usage + reference. Four locations carry the deprecated Voice-1 rule (banner lists exact lines) pending Phase B |
| 4 | `.opencode/commands/meditate.md` v2.0 (498L) | **LIVE — replacement target** | Executed command behavior until Phase B lands |
| 5 | `.opencode/commands/meditate-local.md` v1.1.0 | **LIVE — corrected** | Local trio command (:72 heading contradiction fixed 2026-08-26) |
| 6 | `data/coordination/meditations/MEDITATION_REGISTRY.md` v1.1.0 | **LIVE — consolidated** | Execution index; all 16 records registered; anomaly annotations |
| 7 | `data/coordination/meditations/MEDITATION_TEMPLATE_REGISTRY.md` | LIVE (roc_racoon) | Template definitions SSOT |
| 8 | `data/coordination/meditations/MEDITATION_SYSTEM_GUIDE.md` | LIVE w/ known-stale claim | Autonomous/agentic meditation subsystem. ⚠️ Its Six-Pass budget claim (8K) is STALE — template frontmatter (`token_budget: 4000`) is executable truth (disclosed in use-meditate.md:307) |
| 9 | `data/coordination/meditate_tournament_20260826/` (+ README) | **FROZEN — historical inputs** | Tournament drafts carry superseded V1 rule; shape references only |
| 10 | `records/*.md` (16 files) | FROZEN — execution truth | Primary evidence; registry indexes them |

**Out of scope but related** (autonomous-meditation lineage — separate subsystem, do not consolidate into this campaign): `docs/protocol/MEDITATION_PROTOCOL.md`, `docs/protocol/AUTONOMOUS_MEDITATION_PROTOCOL.md`, `docs/guides/AUTONOMOUS_MEDITATION*.md`, `docs/adr/ADR-001_AUTONOMOUS_MEDITATION_PIPELINE.md`.

**Regression guards active**: manual advisory banner · tournament README · registry anomaly section. Any agent citing a meditation rule MUST trace it to R53 or this document — never to a tournament draft or a banner-flagged manual line.

---

*Evidence base: R53 Granite Foundation (a0a43c82) · 16-record corpus (2,377 lines total) · Expert A grokster 296L · Expert B doom_guy 251L · CARMACK_SYNTHESIS · Manual v2.3 (359L) · Deep review of plan flaws and gaps.*
*⬡ OMEGA ⬡ MEDITATE-DOC-STRATEGY ⬡ v1.1.0 ⬡ 2026-08-26*
