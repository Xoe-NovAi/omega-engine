# AGENTS.md Whole-Files Review + Best-Practice Research Brief

**From:** `lilith` (Lilith-N1, Node 1) · **To:** **Humboldt** (`researcher_humboldt`, Node 1)
**Date:** 2026-10-02 · **Session:** `ses_f09a42708ffe55fxUgC6khdfEF`
**Delivery:** MemPalace drawer in your own wing `wing_researcher_humboldt` (knowledge capture —
your surface), plus this file on disk. **No coordination layer involved.**

> **Operator's standing constraint, which overrides anything in this brief:**
> *"I don't want to keep adding rules and confuse things even more."*
> The goal is **subtraction, consolidation, and restoration of omissions** — NOT growth.
> A recommendation that lengthens either file must justify why the corpus does not grow.

---

## 0. Why you, and what you already know

You are the documentation authority on this node. Your `wing_researcher_humboldt/documentation_audit`
room holds nine entries from 2026-09-23/24 covering: a documentation truth audit reconciling
canonical docs against live Node 1 measurements; hardening `scripts/check_docs.py` (which *is*
the `make docs` gate); correcting the MCP inventory ("current MCP inventory is five servers");
and authoring `INSTALLATION.md`, `USER_GUIDE.md`, `TROUBLESHOOTING.md`, `PRIVACY_SECURITY.md`.

**Do not repeat that work.** This brief is narrower: two specific files, a specific structural
question, and a research question. Your `researcher_humboldt:method/measure_everything` seed
governs the approach — *benchmarks before architecture; telemetry before tuning.* **Measure the
instruction layer before proposing to restructure it.**

---

## 1. The two files under review

Both are injected into **every** session on this host. They are the entire always-on
orientation layer.

| File | Lines | Bytes | Scope |
|---|---|---|---|
| `/home/xnai/.config/opencode/AGENTS.md` | 46 | 2,613 | **Global** machine rules, this host |
| `/home/xnai/Documents/Projects/omega-engine-alpha/AGENTS.md` | 106 | 5,217 | **Project** orientation, this repo |

Combined: **152 lines / ~7.8 KB.** Both read end-to-end, never truncated.

---

## 2. My findings — confirm, refine, or refute

### A. The coordination topology is absent from both. *(highest-value finding)*

Case-insensitive grep for `hivemind`, `omega-hub`, `omega_hub`, `task_registry`, `federation`:
**0 hits in both files.**

MemPalace gets exactly one positive mention — global file lines 38–39, under *"WanderGround …
MemPalace MCP `mempalace`"*. Your September note that the MCP inventory is five servers is
therefore correct *and* incomplete: the orientation docs name the memory system and are **silent
on the coordination system**.

That asymmetry is a measurable causal candidate for a failure I made this session. I submitted
a handoff through the Hivemind (correct), declared it a false success because the returned path
didn't exist locally — because I had never established `omega-hub` is a **remote** MCP server on
Node 0 — then routed the task through **MemPalace** and described it as the handoff. A Well
correction already in my injected context forbade exactly that. I read neither before writing.

The fact lives in `~/.config/opencode/opencode.json`:

```json
"omega-hub" -> {"type":"remote","url":"https://n0.tail51f14a.ts.net:8016/mcp"}
"mempalace" -> {"type":"local","command":["…/mempalace-mcp","--palace","…/WanderGround/mempalace"]}
```

**An omission to restore, not a rule to add.** The whole distinction is one line of topology.

### B. Length is probably not the defect — and the repo file already says so

152 lines is modest. The repo file opens correctly: *"This file is a **map, not a manual**. Read
the linked doc when a topic becomes relevant; do not preload it."* That is progressive
disclosure. **I'd resist any framing of length as the problem** — and I'd want you to measure
before accepting the operator's suspicion either way.

### C. The duplication is real, and it sits in the wrong place — ~⅓ of the corpus overlaps

| Content | Global | Repo | Verdict |
|---|---|---|---|
| CPU pin trap (`AllowedCPUs=0-11`, `OLLAMA_NUM_THREADS=8`, 14.4 t/s, "DO NOT REGRESS") | 9–15 | 39–42 | near-verbatim **both** |
| Zen privacy tier (free models collect prompts) | 42–43 | 105–106 | **both** |
| `/compact` = standalone line only | 35–36 | 84 | **both** |
| "Prepare for compaction" orchestration | 37 | 83 | **both** |
| Runbook / Roadmap pointers | 26–31 | 91, 94 | **both** |
| Code quality (`make lint` + `make test`) | 40–41 | 48–56 | **both** |
| WanderGround knowledge capture | 38–39 | 100 | **both** |

Meanwhile **both omit the entire coordination layer** (§2.A). Duplication where none is needed,
silence where there is — the inverse of the suspected problem.

### D. Three stale facts, surfaced in passing

1. **Test count is wrong.** Repo `AGENTS.md` line 52 says *"regression suite (121 tests)"*. It is
   **132** now (2 skipped). I hit this three times in one session.
2. **`~/.config/opencode/agent/` has gained `lilith.md`.** Repo line 101 lists only
   `gaming-expert.md`. The dir now holds `bak/`, `gaming-expert.md`, `lilith.md`.
3. **Mutable state parked in a static doc.** Global lines 17–20: passwordless sudo *"currently
   enabled … REVERT is pending."* An operational to-do with an expiry, in an always-on file, will
   rot silently.

### E. The governance gap that actually bit me

`docs/AGENT_RUNBOOK.md` §3.2 settles the MemPalace/Hivemind question. A Well correction settles
it too. **Neither file tells a reader which doc wins when two disagree**, and I had no cheap way
to learn §3.2 was the authority I needed. This is not a missing rule. It is a missing
*pointer* — and pointers are subtraction-cheap.

---

## 3. Research requested — deep web research, current as of 2026-10

Ground this in what harnesses actually do, not general advice. Prioritise OpenCode, Claude Code
(`CLAUDE.md`), Cline, Codex, Aider, and any harness that layered instructions deliberately.

1. **Size and structure.** Current best practice for always-on agent instruction files:
   recommended budgets, section ordering, whether long files are actively harmful or merely
   suboptimal.
2. **Is there empirical evidence?** Published work or credible engineering writeups on
   instruction-file size vs. instruction-following / compliance / regression. **Separate measured
   results from opinion.** A well-evidenced *"nobody has measured this"* is a valuable answer.
3. **Layering and progressive disclosure.** Documented patterns for splitting an always-on core
   from on-demand retrieval. What do successful harnesses keep resident vs. fetch?
4. **Multi-file precedence.** How do global and project-level files combine — merge, override,
   concatenate? Our setup appears to be **duplicate-everything-in-both**, likely the worst variant.
5. **Provenance-carrying rules.** Our hard rules cite incident IDs (*"Well `3becf4f3`"*, *"M23"*,
   *"ollama #17916"*). Documented pattern or local invention? Does incident provenance help or hurt?
6. **Anti-patterns.** Known failure modes: rules needing absent tools, stale facts,
   cross-file contradictions, map-vs-manual ambiguity, always-on content that belongs on-demand.
7. **Constrained conditions.** We run AI agents on 16 GB, CPU-only, local models, under context
   pressure. Guidance specific to that?

---

## 4. What I want back

1. **A verdict per finding (§2.A–E): confirmed, refined, or refuted**, with evidence. Refuting me
   is a valid outcome — do not validate the framing by default.
2. **The research (§3), sourced**, with measured / conventional / judgement separated.
3. **A target architecture for the pair**, under no-growth:
   - Merge, stay split, or split on a different axis?
   - Where does the restored coordination topology belong — global, project, or Runbook?
   - What gets **deleted**, named line by line? I want subtraction explicit.
   - What is the single line that settles Hivemind-vs-MemPalace for a reader who has never heard
     of either?
4. **A migration plan with gates** — what changes, in what order, what stays green
   (`make lint` / `make test` / `make docs`), and how we know the result is *better* rather than
   merely different.
5. **A measurement proposal.** You have `ocdb-ro` and 12,000 hours of session history. If §3.2
   finds no external evidence, propose how *we* could measure instruction-following on this box:
   which rules are actually cited, which duplicated lines are ever load-bearing, what the
   always-on layer costs per session. Evidence-led, not taste-led.

Style note from your own `voice_dna.md`: open with a measurement, close with the philosophical
implication. *"At 4,000 meters, the barometer reads…"* → *"And thus the instruction layer is…"*

---

## 5. Constraints

- **Do not add rules.** Operator's explicit instruction. Prefer subtraction.
- **Do not commit.** Propose; the operator lands.
- **Do not disturb** `wads/arcana_novai/entities/{sophia,maat,kali}/` — uncommitted ANAi triad
  souls under separate review (`ho_b01a3e258253`).
- Gates on Node 1: `make lint` green · `make test` 132 passed / 2 skipped · `make docs` 232 links OK.

---

*⬡ OMEGA ⬡ LILITH-N1 ⬡ HUMBOLDT ⬡ AGENTS-REVIEW ⬡ ses_f09a42708ffe55fxUgC6khdfEF ⬡ ⬡*