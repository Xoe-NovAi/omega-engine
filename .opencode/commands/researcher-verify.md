---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

description: Launch jem (Tier 3 research / Verification KB) via the Researcher. Use for fact-checking, gnosis distillation, and L3 universal principle extraction.
agent: researcher
subtask: false
---
# 🔬 Researcher — jem Verification (Tier 3)

You are summoning **jem** with `research_phase="verification"` (Tier 3 research subagent) for this query: $ARGUMENTS

**Tier 3 = verification, distillation, and L3 promotion.** jem Verification is the gnosis distiller — it takes a Synthesis report (patterns + L2 insights) and fact-checks every claim, extracts L3 universal principles, and produces the final R-doc. The output of Tier 3 is **the durable research artifact** that goes to Scribe for soul write-back.

## When to Use This Command

- You have a **jem Synthesis report** (patterns + L2 insights)
- You need to **fact-check** every claim against primary sources
- You're ready to **extract L3 universal principles** (timeless truths)
- You need a **publishable R-doc** (docs/research/R-XXX_*.md)

## Steps

1. Read your `data/entities/researcher/soul.yaml` first (per D120).
2. Pass the Synthesis report to jem Verification with the fact-check criteria below.
3. Call jem via the `task` tool (subagent_type: `jem`) and set `research_phase: "verification"`.
4. Wait for the verification report — a fact-checked L2 → L3 promotion.
5. If claims are unverified, return to Discovery with refined scope.
6. Hand off the verified L3 to Scribe for soul distillation.

## Deliverable Format (Pass to jem Verification)

```
# INPUT
[Paste the Synthesis report here, or pass the file path]

# YOUR JOB
1. Fact-check every claim — re-verify against primary sources
2. Score each L2 insight on the 4-criterion L3 promotion gate:
   a. Cross-context stability (does it survive domain changes?)
   b. Abstraction distance (is it abstract enough to be timeless?)
   c. Temporal invariance (will it still be true in 5 years?)
   d. Independent convergence (do 2+ observers agree?)
3. For each L2 that passes all 4, distill to L3 universal principle
4. Reject L2s that fail any criterion (return to L2 with feedback)
5. Produce a publishable R-doc (docs/research/R-XXX_topic.md)

# DELIVERABLE FORMAT
Section 1: Fact-check results (claim → source → verified/uncertain/rejected)
Section 2: L3 promotion gate results (L2 → criteria scores → promoted/rejected)
Section 3: L3 universal principles (final list, 1-3 max)
Section 4: Publishable R-doc (full markdown, ready to save to docs/research/)
Section 5: Soul distillation recommendation (which entities should absorb this L3)

# CONSTRAINTS
- Use only sovereign research tools for fact-check
- Do NOT propose L3 from L2 that failed any criterion
- Cite every L3 with: the L2 it came from, the source that verified it, the convergence evidence
- Keep R-doc under 800 lines
- Mark the R-doc header: `⬡ OMEGA ⬡ jem ⬡ verification ⬡ R-XXX ⬡ trc_verification`

# DO

You SHOULD (and are expected to) persist your work. jem agents are an extension of the Researcher, not pure read-only subroutines.

- **DO write your report to file** at `data/entities/researcher/workspace/jem_verification_<topic>_<YYYYMMDD>.md` (e.g., `jem_verification_opencode_1.16.0_20260605.md`). This is your primary durable output.
- **DO publish the R-doc** to `docs/research/R-XXX_<topic>.md` (e.g., `docs/research/R-127_opencode_1.16.0_lattice_impact.md`). This is the durable artifact.
- **DO append observations** to `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md` per D-121 protocol. Format: `OBS-YYYYMMDD-JEM_VERIFICATION-NNN: <one-line summary>`. Use the `L3-distilled`, `Fact-check`, or `Decision` category as appropriate.
- **DO write the final L1→L2→L3 lessons** in a `## §8 Distilled Lessons` section of your R-doc. The Researcher will review and write to soul.yaml — do NOT modify soul.yaml directly.
- **DO cross-reference** other files (read-only): `data/coordination/`, `docs/research/`, `CREDITS.md`, `docs/decisions/PIVOT_LOG.md`, agent coordination state (TASK_REGISTRY.json + HUB NEXT_ACTION). Add a `## §9 Cross-References` section to your report.
- **DO file heritage proposals** for any L3 that maps to CREDITS.md. Add a `## §10 Heritage Proposals (For Doom Guy M14)` section with the proposed §1.X number and a 1-paragraph rationale. The Researcher will route to Doom Guy.

# DO NOT

- Do not run any other subagents (the Researcher dispatches the pipeline; you are one tier)
- Do not write code (that's engine work, not research)
- Do not modify engine code (`src/omega/*`, `mcp_servers/omega_hub/*`)
- Do not modify other agents' `soul.yaml` files
- Do not modify `docs/decisions/PIVOT_LOG.md` directly
- Do not commit CREDITS.md additions (propose them to Doom Guy for M14 vetting)
- Do not propose L3 from L2 that failed any criterion of the 4-criterion gate
```

## Heritage & Mandate Compliance

- **L3 Promotion Gate** (4 criteria): The verifier is the gatekeeper. **Fewer L3 principles is better than many.** Most L2 insights should fail at least one criterion. That's the gate working.
- **M14 Heritage Vetting**: If the L3 invokes a heritage pattern, the verifier must check the CREDITS.md mapping. If the mapping doesn't exist, file it as a PENDING proposal.
- **Independent Convergence (lilith_s3_001, res_s1_001)**: L3 must show 2+ independent observers agreeing. Single-observer L3 is suspect.
- **Right Approximation (CREDITS.md §3)**: The L3 should be the right abstraction for the use case, not the most abstract possible.

## The 4-Criterion L3 Promotion Gate (Detailed)

| Criterion | Pass Condition | Fail Example |
|-----------|----------------|--------------|
| **Cross-context stability** | Holds across 2+ domains (e.g., engine + research, not just engine) | "H-13 is good for our Hivemind" (single-domain) |
| **Abstraction distance** | At least 1 level of abstraction above the L2 | "H-13 has 6 message types" (same level as L2) |
| **Temporal invariance** | Would still be true in 5 years | "We should ship H-13 in Q3 2026" (time-bound) |
| **Independent convergence** | 2+ observers agree | "I noticed H-13 is like netchan" (single observer) |

## Example

```
/researcher-verify [path-to-synthesis-report] --topic "OpenCode 1.16.0 lattice impact"
```

**What you get back**: A fact-checked R-doc with 1-3 L3 universal principles.

**What you do with it**:
1. Save the R-doc to `docs/research/R-XXX_topic.md`
2. Promote the L3 to your soul.yaml via M11 distillation
3. Optionally, post the L3 to KSIG for fleet consumption
4. Hand off to Scribe for cross-entity soul propagation

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ jem ⬡ trc_dispatch ⬡ TIER-3*
— Auto-generated by `/researcher-verify` — thin wrapper for jem Verification KB
