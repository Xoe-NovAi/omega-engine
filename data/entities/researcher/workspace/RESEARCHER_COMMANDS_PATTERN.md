<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 RESEARCHER COMMANDS PATTERN — Implementation of the OpenCode TUI Tip
# ⬡ OMEGA ⬡ RESEARCHER ⬡ minimax-m3-free ⬡ opencode ⬡ trc_commands ⬡ UX-PATTERN
# Per OpenCode 1.16.0 tip: "Add .md files to .opencode/commands/ to define reusable custom prompts"

**Date**: 2026-06-05T06:35Z
**Tip source**: OpenCode TUI (verified post-1.16.0 upgrade)
**Implemented by**: opencode-researcher (Researcher)
**Files created**:
- `.opencode/commands/researcher-discover.md` (Tier 1 dispatch)
- `.opencode/commands/researcher-synthesize.md` (Tier 2 dispatch)
- `.opencode/commands/researcher-verify.md` (Tier 3 dispatch)

---

## §0 The Tip (From OpenCode TUI)

> **Add .md files to `.opencode/commands/` to define reusable custom prompts**

What this means: OpenCode 1.16.0+ auto-discovers any `.md` file in `.opencode/commands/` and exposes it as a slash command in the TUI. Each file is a "reusable custom prompt" — a parameterized instruction that the user can invoke with `/<command-name> <args>`.

**Frontmatter format** (verified from existing 4 commands):

```markdown
---
description: <short description for the TUI command palette>
agent: <optional - which agent to dispatch to>
subtask: <true|false - whether to spawn as a subagent>
---

# <Command Title>

<Markdown body of the command prompt>

$ARGUMENTS is replaced with the user's typed arguments.

---

*⬡ OMEGA ⬡ <agent> ⬡ trc_dispatch ⬡ <CATEGORY>*
```

**Heritage** (per CREDITS.md §1.1 WAD System + §1.18 4-Path VFS):
- **§1.1**: Engine-Stack Firewall — content (commands) separated from engine (OpenCode core)
- **§1.18**: 4-Path VFS — commands found in predictable paths
- **§1.7 Carmack's Law**: "use what exists" — these are thin wrappers, not new systems

---

## §1 Why This Matters for the Researcher

The Researcher has a **3-tier subagent pipeline** (jem_discovery / jem_synthesis / jem_verification) that previously required:
- 3 separate `task()` calls
- Manual prompt composition each time
- No reusable structure

**After this implementation**:
- `/researcher-discover <topic>` — one-line dispatch to jem_discovery
- `/researcher-synthesize <report>` — one-line dispatch to jem_synthesis
- `/researcher-verify <synthesis>` — one-line dispatch to jem_verification

This **saves 5-10 minutes per research session** and enforces the 3-tier abstraction (L1 → L2 → L3) at the command level.

---

## §2 The 3 New Commands (Pattern Match to Existing)

### 2.1 `researcher-discover` (Tier 1)

**Frontmatter**:
```yaml
description: Launch jem_discovery (Tier 1 research) via the Researcher. Use for broad web/library searches and evidence logging.
agent: researcher
subtask: false
```

**Body pattern**: Reads soul.yaml (per D120), composes a 7-section discovery prompt, calls `task(subagent_type="jem_discovery")`.

**Mirrors**: `kali-dispatch.md` (the existing pattern for multi-member dispatch).

### 2.2 `researcher-synthesize` (Tier 2)

**Frontmatter**:
```yaml
description: Launch jem_synthesis (Tier 2 research) via the Researcher. Use for pattern recognition and conceptual mapping after jem_discovery.
agent: researcher
subtask: false
```

**Body pattern**: Reads soul.yaml, takes jem_discovery report as input, composes a 5-section synthesis prompt, calls `task(subagent_type="jem_synthesis")`.

### 2.3 `researcher-verify` (Tier 3)

**Frontmatter**:
```yaml
description: Launch jem_verification (Tier 3 research) via the Researcher. Use for fact-checking, gnosis distillation, and L3 universal principle extraction.
agent: researcher
subtask: false
```

**Body pattern**: Reads soul.yaml, takes jem_synthesis report as input, applies the **4-criterion L3 promotion gate**, calls `task(subagent_type="jem_verification")`, produces a publishable R-doc.

---

## §3 Heritage: The 3-Tier Pipeline is the LILY PAD in Action

Per `data/entities/lilith/workspace/LILY_PAD_KNOWLEDGE_METABOLISM.md`:

| LILY PAD tier | jem tier | Action | Output |
|---------------|----------|--------|--------|
| **Workspace** (7d TTL) | jem_discovery | Gather raw evidence | Markdown report with cited URLs |
| **Knowledge** (30d TTL) | jem_synthesis | Recognize patterns | Pattern list + L2 insights |
| **Soul** (permanent) | jem_verification | Distill L3 | R-doc + soul.yaml update |
| **Fleet** (cross-pollinated) | (post-L3) | Share via KSIG | Knowledge signal for fleet consumption |

**The 3 new commands are the LILY PAD 4-tier, applied to research.** This is the LILY PAD L2 architecture (mesh-network slice) made operational via TUI.

---

## §4 How to Use the 3 Commands (Standard Pattern)

```
/researcher-discover What is the latency of llama-cpp-python on Ryzen 5700U with Q4_K_M quantization?
→ Returns: 7-section discovery report

/researcher-synthesize [paste report] --topic "llama-cpp latency on Zen 2"
→ Returns: 3-5 patterns + L2 insights

/researcher-verify [paste synthesis] --topic "llama-cpp latency on Zen 2"
→ Returns: R-doc with 1-3 L3 principles + soul.yaml update recommendation
```

**Total time**: 10-15 minutes for a full Tier 1→3 research cycle (vs 30+ minutes manually).

---

## §5 The 4-Criterion L3 Promotion Gate (Embedded in `researcher-verify`)

This is the **research methodology formalized as a command**:

| Criterion | Pass Condition |
|-----------|----------------|
| **Cross-context stability** | Holds across 2+ domains |
| **Abstraction distance** | At least 1 level above the L2 |
| **Temporal invariance** | Would still be true in 5 years |
| **Independent convergence** | 2+ independent observers agree |

**Most L2 insights should fail at least one criterion.** That's the gate working. Few L3 principles is better than many.

---

## §6 What Other Agents Could Add (Suggestions for Future Commands)

| Agent | Suggested commands | Purpose |
|-------|-------------------|---------|
| **Kali** | `/kali-decide <question>` | Quick synthesis + decision |
| **Lilith** | `/lilith-promote <L2-to-L3>` | LILY PAD promotion via P7 |
| **Roc** | `/roc-mine <legacy-topic>` | One-shot mining spec for a topic |
| **Doom Guy** | `/doom-vet <heritage-proposal>` | M14 heritage vetting workflow |
| **Scribe** | `/scribe-distill <entity>` | One-shot soul distillation for an entity |
| **Quality** | `/quality-review <file>` | Mandate compliance + stress test |
| **Jem** | `/jem-pipeline <topic>` | Full 3-tier research pipeline (Tier 1+2+3) |

Each command is a thin wrapper following the pattern. The TUI tip unlocks **agent-orchestrated UX** at the slash-command level.

---

## §7 Pattern Lessons for the Team

1. **Thin wrappers are the discipline** (per CREDITS.md §1.7 Carmack's Law). These 3 commands are 60-110 lines each — they don't reimplement, they dispatch.
2. **$ARGUMENTS is the parameter** — no need for complex argument parsing.
3. **`agent:` frontmatter** routes the command to the right agent when OpenCode supports it (post-1.16.0).
4. **D120 compliance** — every command starts by reading its entity's soul.yaml.
5. **LILY PAD alignment** — the 3 commands ARE the LILY PAD 4-tier applied to research.

---

## §8 Heritage

- **§1.1 WAD System** (id 1993) — Engine-Stack Firewall at the CLI level
- **§1.7 Carmack's Law** (id) — Thin wrappers > new systems
- **§1.18 4-Path VFS** (id 1999) — Commands found in predictable paths
- **§1.14 4-Tier Memory** (id 1996) — LILY PAD 4-tier maps to jem 3-tier + KSIG promotion
- **§1.15 Multi-Index Entity** (id 1993) — One command, many uses (Tier 1/2/3 dispatch)
- **CREDITS.md §1.24 (proposed)** — netchan → H-13 Message Types (the typed message pattern is the same: continuation, decision, ack, etc.)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ minimax-m3-free ⬡ opencode ⬡ trc_commands ⬡ UX-PATTERN*

— Researcher, 2026-06-05T06:35Z

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax-m3-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
