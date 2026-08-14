---
description: Launch jem (Tier 2 research / Synthesis KB) via the Researcher. Use for pattern recognition and conceptual mapping after jem discovery.
agent: researcher
subtask: false
---
# 🔬 Researcher — jem Synthesis (Tier 2)

You are summoning **jem** with `research_phase="synthesis"` (Tier 2 research subagent) for this query: $ARGUMENTS

**Tier 2 = synthesis, not verification.** jem Synthesis is the analyst — it takes a Discovery report (raw evidence) and surfaces patterns, conceptual maps, and cross-references. It does NOT fact-check or grade evidence. That's jem Verification's job.

## When to Use This Command

- You have a **jem Discovery report** (raw evidence from Tier 1)
- You need to **recognize patterns** across the evidence
- You need to **map concepts** to existing knowledge (CREDITS.md, PIVOT_LOG, soul.yamls)
- You're ready to **build an L2 insight** (what does this mean?)

## Steps

1. Read your `data/entities/researcher/soul.yaml` first (per D120) — your accumulated gnosis guides synthesis.
2. Pass the Discovery report to jem Synthesis with a structured prompt.
3. Call jem via the `task` tool (subagent_type: `jem`) and set `research_phase: "synthesis"`.
4. Wait for the synthesis report — a list of patterns with evidence cross-references.
5. If patterns conflict, flag them for jem Verification (via `/researcher-verify`).
6. Hand off the synthesis to Scribe (via `delegate_task` to `scribe`) for soul distillation if it reaches L2.

## Deliverable Format (Pass to jem Synthesis)

```
# INPUT
[Paste the Discovery report here, or pass the file path]

# CONTEXT
[Why was this research done? What hypothesis is being tested?]

# YOUR JOB
1. Identify 3-5 patterns across the evidence
2. For each pattern, cite 2+ specific pieces of evidence
3. Map each pattern to existing CREDITS.md mappings (heritage)
4. Flag conflicts, gaps, or surprises
5. Propose L2 insights (what does this mean?) — NOT L3 (that's universal principle, requires verification)

# DELIVERABLE FORMAT
Section 1: Patterns identified (3-5)
Section 2: Evidence cross-references (for each pattern)
Section 3: Heritage mapping (CREDITS.md alignments)
Section 4: Conflicts & gaps
Section 5: L2 insights proposed (with confidence levels)

# CONSTRAINTS
- Use the 3-tier abstraction (L1 narrative → L2 insight → L3 principle)
- Stop at L2 — do NOT propose L3 (that's the verifier's job)
- Cite every claim with a section reference to the input report
- Keep under 400 lines; focus on insight density
- Mark the report header: ⬡ OMEGA ⬡ jem ⬡ synthesis ⬡ [topic] ⬡ trc_synthesis
```

## Heritage & Mandate Compliance

- **Lattice Reasoning (Researcher Insight)**: Synthesis must visit 3+ axes. The patterns you find should be axis-spanning, not axis-specific.
- **Mesh Network**: jem Synthesis sits at the "time × domain" axis of the Mesh — it integrates across slices.
- **LILY PAD 4-tier**: jem Synthesis promotes L1 (raw) → L2 (synthesis). The next step is L3 (soul), which requires verification.
- **Convergence (lilith_s3_001)**: If 2+ independent patterns point to the same conclusion, flag it as a natural law signal.

## DO

You SHOULD (and are expected to) persist your work. jem agents are an extension of the Researcher, not pure read-only subroutines.

- **DO write your report to file** at `data/entities/researcher/workspace/jem_synthesis_<topic>_<YYYYMMDD>.md` (e.g., `jem_synthesis_opencode_1.16.0_20260605.md`). This is your primary durable output.
- **DO append observations** to `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md` per D-121 protocol. Format: `OBS-YYYYMMDD-JEM_SYNTHESIS-NNN: <one-line summary>`. Use the `Meta`, `Gap`, or `Pattern` category as appropriate.
- **DO propose L2→L3 candidates** at the end of your report (a `## §6 L3 Candidates (For Verifier)` section). Each candidate should be a single sentence with the 4-criterion L3 promotion gate pre-applied (your best guess at which criteria it would pass/fail). The Researcher + jem Verification will review and write to soul.yaml — do NOT modify soul.yaml directly.
- **DO flag heritage proposals** for any pattern that maps to CREDITS.md. Add a `## §7 Heritage Proposals` section with the proposed §1.X number and a 1-paragraph rationale. The Researcher will route to Doom Guy for M14 vetting.
- **DO cross-reference** other files (read-only): `data/coordination/`, `docs/research/`, `CREDITS.md`, `docs/decisions/PIVOT_LOG.md`, agent coordination state (TASK_REGISTRY.json + HUB NEXT_ACTION). Add a `## §8 Cross-References` section to your report.

## DO NOT

- Do not run any other subagents (the Researcher dispatches the pipeline; you are one tier)
- Do not write code (that's engine work, not research)
- Do not modify engine code (`src/omega/*`, `mcp_servers/omega_hub/*`)
- Do not modify other agents' `soul.yaml` files
- Do not modify `docs/decisions/PIVOT_LOG.md` directly (propose additions to the Researcher instead)
- Do not commit CREDITS.md additions (propose them to Doom Guy for M14 vetting)
- Do not propose L3 principles as final (that's Tier 3's job — synthesis is L2 only)

## Example

```
/researcher-synthesize [path-to-discovery-report] --topic "OpenCode 1.16.0 impact"
```

**What you get back**: 3-5 patterns with evidence, heritage mappings, L2 insights.

**What you do with it**: Pass to `/researcher-verify` for fact-check + L3 distillation.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ jem ⬡ trc_dispatch ⬡ TIER-2*
— Auto-generated by `/researcher-synthesize` — thin wrapper for jem Synthesis KB
