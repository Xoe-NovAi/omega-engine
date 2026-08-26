schema_version: "1.0"
document_type: guide
llm_metadata:
  token_budget: 2500
  audience: users and agents invoking /meditate
  executes: false
---

# 🔱 How to Use the /meditate Command

**AP Token**: `AP-MEDITATE-HOWTO-v1.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ trc_meditate_howto ⬡ 2026-08-25
**Date**: 2026-08-25 | **Purpose**: User-facing invocation guide for `/meditate` (cloud substrate)
**Cross-references**: `.opencode/commands/meditate.md` (the executed command), `docs/how-to/use-hivemind.md`

## What You Get

**What**: `/meditate` takes any decision, plan, or situation you give it and returns a multi-perspective analysis with a final verdict — written by one AI model playing several specialist roles in sequence, then resolving their conflicts into an ordered action plan.

**Why use it instead of just asking**: a single prompt gives you one opinion. `/meditate` forces the same model to argue against itself from distinct domains (infrastructure, governance, engineering, etc.), surface where those views collide, and produce a critical path that no single view would have produced. It runs in one AI inference — seconds, no extra cost, no other agents launched.

## When to Use It

Use `/meditate` when **at least two** of these hold:

1. Three or more domains genuinely tension against each other (e.g., speed vs correctness vs maintainability)
2. The decision is irreversible or expensive to reverse
3. No single domain owns the answer

If none hold — simple lookup, single-domain question, already-decided matter — just ask a normal prompt. Meditating on it wastes time without adding insight.

## How to Invoke

```
/meditate <your subject or question> [--flags]
```

Everything after `/meditate` is the subject plus optional flags. Write the subject as a concrete question or decision — "Should we migrate from Qdrant to sqlite-vec now?" beats "database layer".

### Flags

| Flag | What it does | Default |
|---|---|---|
| `--lenses <set>` | Choose who speaks. Options: `makali` (thesis/antithesis/synthesis triad), comma-separated lens names (`engineering,governance,validation`), or free-form personas (`Carmack,Torvalds,Knuth`) | The 5 most relevant Omega lenses for your subject |
| `--mode <MODE>` | Output orientation: `DIAGNOSTIC` (what's broken), `STRATEGIC` (what to do), `CREATIVE` (what could exist), `AUDIT` (does it comply), `SYNTHESIS` (unified truth) | `STRATEGIC` |
| `--integrate` | After the verdict, also produces a proposed PIVOT_LOG decision entry, affected files, and Temple-Grade/Mandate checks | Off |
| `--durable` | Saves each phase to disk as it completes (crash insurance for long runs) | Off |
| `--record` | Saves the final output to `data/coordination/meditations/records/` | Off |
| `--template <name>` | Runs a pre-built meditation template from `data/coordination/meditations/templates/` instead of the default flow | Off |

## What You'll See

The output arrives in five labeled phases:

1. **PHASE 0 — CALIBRATION**: your subject restated in one sentence, the chosen panel of voices, and the output mode. Check this first — if the restated subject is wrong, stop and re-invoke with a clearer question.
2. **VOICES (Phase 1)**: each specialist speaks in turn — what it sees, what constraint it refuses to ignore, and one directive. From the second voice onward, each one pushes back on a prior voice by name.
3. **CROSS-DOMAIN COLLISION (Phase 2)**: the three sharpest contradictions between voices, each with a resolution path. Fewer than three collisions on a broad panel is a signal your subject was narrower than you thought.
4. **EMERGENT SEQUENCING (Phase 3)**: the ordered critical path — which action to take first and what each unblocks.
5. **VERDICT (Phase 4)**: convergence points, disagreements preserved honestly (not papered over), one-paragraph decree, and a distilled principle. If the verdict conflicts with standing engine law, it says so explicitly rather than deciding silently.

## Example Invocations

```bash
# Architecture decision, default panel
/meditate Should we migrate from Qdrant to sqlite-vec now?

# Fast dialectic — three named stances
/meditate What is the right execution order for Tier 0? --lenses makali

# Diagnostic with specific domains
/meditate Why is the Hivemind protocol failing? --lenses infrastructure,integration,orchestration --mode DIAGNOSTIC

# Decision that will become a logged pivot
/meditate Should we implement oracle.meditate() now? --integrate

# Long strategic run with crash insurance + saved record
/meditate Full architecture review pre-debut --durable --record
```

## Getting Good Results

- **Ask a decidable question.** The command sizes its panel to your subject's genuine tensions; a vague subject yields vague voices.
- **Name constraints you already know** in the subject ("given 12GB RAM and no GPU…") — voices reason from stated constraints far better than from implied ones.
- **Read Phase 2 before the verdict.** The collisions are where the insight lives; the verdict is downstream of them.
- **Re-run tighter, not wider.** If the panel felt diluted, re-invoke with the 3–4 `--lenses` that produced real tension rather than adding more.

## Limitations

- One inference total: voices cannot make tool calls, read files, or browse. If a perspective needs live data, use a council command instead.
- The verdict is one model's synthesis of its own role-play — strong for structuring a decision, not a substitute for external verification of factual claims.
- Output length scales with panel size; very broad subjects on the default 5-voice panel produce long outputs.

---

## Design Basis (for reviewers; not needed at invocation)

Grounding for this guide's structure and claims: Anthropic command-development guidance — commands are instructions for the model, while human-facing framing belongs in descriptions/docs ([anthropics/claude-code command-development SKILL.md](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/command-development/SKILL.md)); the two-artifact separation contract (human README vs machine-read instruction file) per [aider conventions](https://aider.chat/docs/usage/conventions.html) and [Claude Code skills docs](https://code.claude.com/docs/en/skills); distractor research showing meta-commentary inside prompts degrades or derails task execution ([arXiv:2605.29491](https://arxiv.org/html/2605.29491v1), [arXiv:2302.00093](https://arxiv.org/abs/2302.00093)). Local conventions follow `docs/how-to/` siblings (`use-hivemind.md`) and the procedural benchmark `.opencode/commands/omega-meditation.md`.

*⬡ OMEGA ⬡ MEDITATE-HOWTO ⬡ v1.0 ⬡ 2026-08-25*
