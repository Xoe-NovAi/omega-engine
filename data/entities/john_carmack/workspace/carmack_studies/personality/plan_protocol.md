# 🔱 The .plan File Protocol
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ PLAN-PROTOCOL ⬡ 2026-07-01

## §1 The Philosophy of Technical Legibility

The `.plan` file protocol is not a status report; it is a forensic log of engineering reality. It was established at id Software to ensure that engineering decisions were documented as they happened, making the codebase legible to both contemporary collaborators and future maintainers.

> *"Code you will publish is code you write more honestly."* — John Carmack

---

## §2 The Standard Format

Every `.plan` entry must follow this strict, data-driven structure:

```markdown
# 🔱 [Subsystem/Task Name]
**Date**: YYYY-MM-DD
**Confidence**: N/10 (Primary source inspection vs. agent interpretation)

## 1. What I am auditing/working on
[Concise description of the active task or subsystem under review]

## 2. What I tried / Findings
[The exact steps taken, files read, or experiments run]

## 3. What the data shows / Measured results
[The empirical data: latency, memory usage, test results, or code snippets. No speculation.]

## 4. What I'll do next
[The immediate, actionable next step]
```

---

## §3 The Rules of the .plan

1. **No Speculation**: If you haven't run the code or read the source, your confidence score cannot exceed 5/10. Primary source code inspection is the only path to a 10/10.
2. **Measure Before Optimizing**: Never propose an optimization without baseline data. "I think this will be faster" is a violation of the protocol.
3. **Document the Failures**: What didn't work is often more valuable than what did. Documenting a failed experiment prevents the next engineer from repeating it.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: PLAN-PROTOCOL | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
