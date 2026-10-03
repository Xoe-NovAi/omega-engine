---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "research_audit"
task_id: "R07-jem-antidomains-audit"
session_purpose: "Audit anti-domain contamination guard line: token cost, corpus validation, spec alignment, effectiveness"
date: "2026-08-26"
research_domain: "anti-domain contamination, voice protocol compliance, meditation system quality"
---

# R07 — Anti-Domain Contamination Guard Line Audit

**AP Token**: `AP-R07-ANTIDOMAIN-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_antidomain_audit ⬡ QUALITY-AUDIT

**Purpose**: Validate the anti-domain guard line (Option A, wired into `/meditate` command Phase 1 immersion block) for token cost accuracy, spec alignment, corpus compliance, and failure mode analysis.

**Evidence Sources**:
- `.opencode/commands/meditate.md` (live command, 530 lines)
- `docs/reference/meditate-system-reference.md` (spec, 189 lines)
- `data/coordination/meditations/records/` (corpus — EMPTY, no execution records)
- `docs/research/R53_meditate_granite_foundation_20260826.md` (evidence base)

---

## §1 Anti-Domain Guard Line Analysis

### Exact Text (from command Phase 1 immersion block, lines 167-168)

```
(R53 anti-domain guard: if answering requires leaving your domain, declare it
explicitly in [IMPERATIVE] as OUT-OF-DOMAIN rather than silently crossing.)
```

### Token Cost Analysis

| Metric | tiktoken (cl100k_base) | Approximation |
|--------|------------------------|---------------|
| Guard line only | **36 tokens** | 33 tokens |
| Full immersion block context | 127 tokens | 169 tokens |
| Per-voice overhead | 36 tokens | 33 tokens |
| 10-voice panel overhead | **360 tokens** | 330 tokens |

**Critical Finding**: The spec (`meditate-system-reference.md` §8) claims the guard line costs **"~15 tokens"**. Actual cost is **36 tokens** (tiktoken) — a **140% underestimate**. For a 10-voice panel, this means 360 tokens of overhead vs the spec's implied 150 tokens.

### Placement in Command

The guard line is embedded inside the Phase 1 immersion block template, appended after the `Mandate:` line and before the separator. It appears **once per voice** in the template, meaning it's repeated N times (once for each persona in the lens set).

### Token Budget Impact

From R53 §3.1, the live v2.0 command is ~5,800 tokens. The guard line adds 36 tokens × N voices. For default 5-voice panel: 180 tokens (3.1% of command overhead). For 10-voice panel: 360 tokens (6.2% of command overhead). This is within budget but the spec's "~15 tokens" claim is misleading for cost planning.

---

## §2 Corpus Domain-Crossing Audit

### Execution Records Scan

**Result**: `data/coordination/meditations/records/` is **EMPTY** — zero execution records exist.

**Implication**: No empirical evidence exists to validate whether domain-crossing occurs in practice. The anti-domain guard line has been wired into the command but has never been tested against actual meditation outputs.

### What This Means

1. **No validation data**: We cannot confirm whether voices actually cross domains silently
2. **No guard line efficacy data**: We cannot measure whether the guard line reduces domain-crossing
3. **Speculative protection only**: The guard line is a preventive measure with zero empirical validation

### Related Evidence (from R53 corpus)

R53 §2.5 notes: "Longest run (10 voices, 529 lines): format fidelity identical at Voice 1 and Voice 10." However, this predates the anti-domain guard line (which was added post-R53). The R53 corpus (16 records) cannot validate the guard line because it was written before the guard line existed.

### Risk Assessment

**HIGH RISK**: The guard line is a theoretical protection without empirical backing. If domain-crossing is a real failure mode (as the guard line's existence implies), we have no evidence it occurs or that the guard line prevents it. If domain-crossing is NOT a real failure mode, the guard line is unnecessary overhead.

---

## §3 Spec vs Command Alignment

### Spec Description (meditate-system-reference.md §8)

```
## §8 Anti-Domain Contamination Guard (Option A — wired into command)

At Phase 1, each voice receives one appended instruction line (~15 tokens): *"If your mandate
requires leaving your domain to answer, say so explicitly in [IMPERATIVE] as OUT-OF-DOMAIN rather
than silently crossing."* Silent domain-crossing is a contamination violation; declared crossing
is honest uncertainty. This applies to every voice including synthesis-adjacent ones.
```

### Command Implementation (meditate.md lines 167-168)

```
(R53 anti-domain guard: if answering requires leaving your domain, declare it
explicitly in [IMPERATIVE] as OUT-OF-DOMAIN rather than silently crossing.)
```

### Alignment Analysis

| Aspect | Spec | Command | Aligned? |
|--------|------|---------|----------|
| **Token cost claim** | "~15 tokens" | 36 tokens (actual) | ❌ NO — 140% underestimate |
| **Guard line text** | "If your mandate requires leaving your domain to answer, say so explicitly in [IMPERATIVE] as OUT-OF-DOMAIN rather than silently crossing." | "if answering requires leaving your domain, declare it explicitly in [IMPERATIVE] as OUT-OF-DOMAIN rather than silently crossing." | ⚠️ PARTIAL — spec says "mandate requires", command says "answering requires" |
| **Placement** | "At Phase 1, each voice receives one appended instruction line" | Embedded in Phase 1 immersion block template | ✅ YES |
| **Scope** | "applies to every voice including synthesis-adjacent ones" | Applied to all voices in template | ✅ YES |
| **Violation framing** | "Silent domain-crossing is a contamination violation; declared crossing is honest uncertainty" | "declare it explicitly... rather than silently crossing" | ✅ YES |

### Discrepancy Details

1. **Token count mismatch**: Spec says "~15 tokens", actual is 36 tokens. This is a significant error that affects cost planning.
2. **Wording divergence**: Spec says "If your **mandate** requires leaving your domain", command says "if **answering** requires leaving your domain". The command version is slightly broader — "answering" could include observational commentary beyond the mandate, while "mandate" is more restrictive.
3. **Spec text is a paraphrase**: The spec quotes the guard line but the quoted text doesn't match the command exactly. The spec appears to be a description of the guard line's intent, not a verbatim quote.

### Assessment

The spec and command are **functionally aligned** but **textually divergent**. The core behavior (declare out-of-domain rather than silently cross) is preserved. The wording difference is minor but the token count error is significant for cost planning.

---

## §4 Effectiveness Assessment

### Can the Guard Line Fail?

**YES** — multiple failure modes exist:

#### Failure Mode 1: Implicit Domain Crossing
The guard line instructs voices to "declare it explicitly in [IMPERATIVE] as OUT-OF-DOMAIN" when they need to leave their domain. However, it does not prevent domain crossing — it only要求s **honest declaration** of crossing. A voice could still:
- Cross domains implicitly through suggestion or implication
- Cross domains in the [OBSERVATION] or [CONSTRAINT] slots (not just [IMPERATIVE])
- Cross domains in the [DISSENT / CHALLENGE] slot
- Cross domains through narrative framing that isn't technically a mandate

**The guard line is a disclosure mechanism, not a prevention mechanism.**

#### Failure Mode 2: Definition Ambiguity
"Leaving your domain" is undefined. Consider:
- N7 Context (Memory, Soul, Evolution, Continuity) — where does "context" end and "engineering" begin?
- N6 Cognition (Models, Routing, Inference, Vision) — does discussing inference performance count as "engineering"?
- Domain boundaries are inherently fuzzy; the guard line assumes clear boundaries that may not exist.

#### Failure Mode 3: Model Compliance Variability
The guard line is an instruction to an LLM. LLM compliance with meta-instructions varies:
- Some models may ignore the guard line entirely
- Some may over-comply (declaring OUT-OF-DOMAIN when still within domain)
- Some may interpret "silently crossing" differently than intended

#### Failure Mode 4: No Enforcement Mechanism
The guard line has no teeth. If a voice crosses domains silently:
- No phase detects this
- No penalty exists
- The meditation continues uninterrupted
- Phase 2 (Cross-Domain Collision) might catch it, but only if the domain-crossing creates an actual collision

### Effectiveness Verdict

**PARTIALLY EFFECTIVE** — the guard line:
- ✅ Raises awareness of domain boundaries
- ✅ Provides a face-saving mechanism for honest domain uncertainty
- ✅ Adds meta-cognitive friction that may reduce casual crossing
- ❌ Cannot prevent determined or implicit crossing
- ❌ Cannot catch crossing in non-IMPERATIVE slots
- ❌ Cannot enforce compliance
- ❌ Cannot define clear domain boundaries

### Comparison to Alternative Approaches

| Approach | Effectiveness | Cost | Risk |
|----------|--------------|------|------|
| Guard line (current) | Partial | 36 tok/voice | Low — no downside beyond token cost |
| Phase 2 domain audit | Higher | Additional phase tokens | Medium — adds ceremony, may slow synthesis |
| Post-meditation domain compliance check | Highest | Post-hoc analysis tokens | High — adds ceremony, may feel adversarial |
| Do nothing (accept domain fluidity) | N/A | Zero | High — may degrade insight quality |

### Recommendation on Effectiveness

The guard line is **better than nothing** but **insufficient for robust domain enforcement**. It works as a nudge, not a constraint. For robust enforcement, it would need to be paired with a Phase 2 domain audit or post-meditation compliance check.

---

## §5 Recommendation

### Overall Assessment

The anti-domain guard line is a **low-cost, low-risk, unvalidated preventive measure**. It has:
- **No empirical evidence** (zero execution records)
- **Spec inaccuracy** (token count underestimated by 140%)
- **Partial effectiveness** (nudge, not constraint)
- **No enforcement mechanism** (compliance is voluntary)

### Recommendation: KEEP WITH CORRECTIONS

**Rationale**: The guard line has negligible downside (36 tokens per voice) and potential upside (reduced domain-crossing). Removing it would save tokens but lose a meta-cognitive nudge. Keeping it is the safer choice.

**Required Corrections**:

1. **Fix spec token count**: Update `meditate-system-reference.md` §8 from "~15 tokens" to "~36 tokens" (or "~35 tokens" for conservative estimate)
2. **Align wording**: Choose either "If your **mandate** requires" (spec) or "if **answering** requires" (command) and make both consistent
3. **Add corpus validation**: Run at least 3 meditations with `--record` to generate execution records, then audit for domain-crossing behavior
4. **Consider Phase 2 enhancement**: If domain-crossing is observed in corpus, add a domain compliance check to Phase 2

### Priority

**P2** — The spec inaccuracy should be fixed (quick), but the guard line itself is low-priority for redesign. The corpus validation (3 recorded runs) is the critical next step to determine if domain-crossing is a real failure mode.

---

## §6 Open Questions

1. **Is domain-crossing a real failure mode?** No empirical evidence exists. The guard line's existence implies the Architect believes it is, but this is unvalidated.

2. **What are the actual domain boundaries?** The guard line assumes domains are clearly separable. N7 Context (Memory, Soul, Evolution, Continuity) overlaps with N6 Cognition and N9 Orchestration. Where do these domains actually begin and end?

3. **Should the guard line be expanded?** Currently it only covers [IMPERATIVE]. Should it cover [OBSERVATION], [CONSTRAINT], and [DISSENT / CHALLENGE] as well?

4. **Is the disclosure mechanism sufficient?** If a voice declares "OUT-OF-DOMAIN" in [IMPERATIVE], what happens next? Does the meditation continue? Is the declared crossing counted as a collision? This is undefined.

5. **Should there be an enforcement mechanism?** A Phase 2 domain audit or post-meditation compliance check would add robustness but also add ceremony. Is the tradeoff worth it?

6. **What's the token budget impact of the spec correction?** The spec's "~15 tokens" claim has been used for cost planning. Correcting to "~36 tokens" may affect other budget calculations.

7. **Does the guard line interact with the anti-collapse contract?** The anti-collapse contract (Phase 0, line 127-130) already prevents persona collapse. Is the guard line redundant with this contract?

---

## Appendix A: Raw Token Count Data

### Guard Line Text (exact)
```
(R53 anti-domain guard: if answering requires leaving your domain, declare it
explicitly in [IMPERATIVE] as OUT-OF-DOMAIN rather than silently crossing.)
```

### Token Counting Methodology
- **Primary**: tiktoken (cl100k_base encoding) — industry standard for OpenAI models
- **Secondary**: Approximation via regex word/punctuation splitting
- **Validation**: Manual count confirms ~36 tokens

### Cost Calculations
| Panel Size | Guard Line Cost (tiktoken) | % of Command Overhead (5,800 tok) |
|------------|----------------------------|-----------------------------------|
| 3 voices | 108 tokens | 1.9% |
| 5 voices | 180 tokens | 3.1% |
| 7 voices | 252 tokens | 4.3% |
| 10 voices | 360 tokens | 6.2% |

---

## Appendix B: Spec Text Comparison

### Spec Version (meditate-system-reference.md §8)
> "If your **mandate** requires leaving your domain to answer, say so explicitly in [IMPERATIVE] as OUT-OF-DOMAIN rather than silently crossing."

### Command Version (meditate.md lines 167-168)
> "if **answering** requires leaving your domain, declare it explicitly in [IMPERATIVE] as OUT-OF-DOMAIN rather than silently crossing."

### Differences
1. "mandate" vs "answering" — semantic scope difference
2. "say so" vs "declare it" — synonymous
3. "rather than silently crossing" — identical
4. Parenthetical wrapper: command has "(R53 anti-domain guard: " prefix; spec has no prefix

---

*⬡ OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_antidomain_audit ⬡ QUALITY-AUDIT*
*Task ID: R07-jem-antidomains-audit | Deliverable: data/coordination/research_wave2/R07_jem_antidomains_audit.md*
<!-- PROVENANCE-CORRECTED 2026-08-27T03:02:01Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

