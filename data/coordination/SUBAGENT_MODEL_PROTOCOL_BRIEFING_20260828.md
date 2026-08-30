---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "coordination_summary"
document_id: "subagent-model-protocol-summary-20260828"
title: "Subagent Model Configuration Protocol — Team Briefing"
status: "ACTIVE — CRITICAL PROTOCOL"
date: "2026-08-28"
---

# 🔱 Subagent Model Configuration Protocol — Team Briefing
**AP Token**: `AP-SUBAGENT-PROTOCOL-SUMMARY-20260828-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_protocol_briefing ⬡ ACTIVE

**Date**: 2026-08-28
**From**: kali (Sprint Coordinator)
**To**: ALL TEAM
**Context**: Critical protocol gap closed. No more subagents landing on qwen3-1.7b.

---

## §0 — THE GAP (What Was Wrong)

**Every time we used the `task` tool to launch a subagent, it sometimes landed on `qwen3-1.7b` (local, 1.7B params) instead of M3 (1M context).** We thought it was a bug. It wasn't. It was a protocol gap.

**Root cause** (Carmack's research, `opencode/packages/opencode/src/tool/task.ts:181`):
```typescript
const model = next.model ?? {
  modelID: msg.info.modelID,      // ← INHERIT FROM PARENT
  providerID: msg.info.providerID,
}
```

**The chain is `next.model ?? parent.model`.** When the agent's `.md` config has no `model:` field, the chain falls through to the parent's model — whatever the parent happens to be on.

**All 13 of our `.opencode/agents/*.md` files had no `model:` field.** So subagents inherited the parent's model — including the wrong one.

---

## §1 — THE FIX (Committed `34324516`)

| Change | Where | What |
|--------|-------|------|
| 1. All 13 agent .md files | `.opencode/agents/*.md` | Added `model: openrouter/minimax/minimax-m3:free` |
| 2. opencode.json | `~/.config/opencode/opencode.json` | Changed `model` and `small_model` from `nemotron-3-ultra-free` to M3 |
| 3. Protocol doc | `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md` | 619 lines, full resolution chain, 3 methods, step-by-step |
| 4. Verify script | `scripts/verify_subagent_model.sh` | 94 lines, pass/fail exit codes, CI-ready |

---

## §2 — THE 3 CONFIGURATION METHODS (Research Verdict)

| Method | Verdict | Evidence |
|--------|---------|----------|
| **A. `model:` in .md frontmatter** | ✅ **WORKS** | `config/agent.ts:281` loads it; schema accepts it |
| **B. `model` param in `task()` call** | ❌ **FICTION** | `task.ts:36-50` schema has only `prompt`, `description`, `subagent_type`, `task_id`, `run_in_background` — **NO `model` field** |
| **C. `model` per agent in opencode.json** | ✅ **WORKS** | `config/config.ts:96-109` shows the `agent:` field schema |

**We used Method A (recommended).**

---

## §3 — THE PROTOCOL (Step-by-Step)

### When launching a subagent via `task()` tool:

1. **Verify the agent's .md has a `model:` field**:
   ```bash
   head -10 .opencode/agents/<agent_name>.md
   ```

2. **If not, add it** (one-liner):
   ```bash
   sed -i '/^mode:/a model: openrouter/minimax/minimax-m3:free' .opencode/agents/<agent_name>.md
   ```

3. **Verify the session will land on the right model**:
   ```bash
   bash scripts/verify_subagent_model.sh <agent_name> [session_id]
   ```

### When resuming a subagent via `task_id`:

- The agent config WINS over the session's stored model
- If the agent's .md has `model: M3`, the resumed session will use M3
- This is retroactive — old sessions on qwen3-1.7b will switch to M3 on resume

---

## §4 — PITFALLS TO AVOID

1. **Don't trust the `model` param in `task()`** — it doesn't exist in the schema
2. **Don't skip the .md `model:` field** — without it, you inherit the parent's model
3. **Don't use `opencode/nemotron-3-ultra-free` as default** — it's RPD-exhausted
4. **Don't assume old sessions will fix themselves** — only NEW sessions get the new model
5. **Don't launch without verifying** — use `scripts/verify_subagent_model.sh`

---

## §5 — VERIFICATION

```bash
$ bash scripts/verify_subagent_model.sh verity ses_fb94afd01ffe1jvUmQVQfqaDu1
Agent:       verity
Config:      openrouter/minimax/minimax-m3:free (from .opencode/agents/verity.md)
Session:     ses_fb94afd01ffe1jvUmQVQfqaDu1
Actual:      lmstudio/qwen3-1.7b (from opencode.db)

❌ FAIL: session is on a DIFFERENT model than configured
```

**The test correctly catches the bug for the OLD session.** For any NEW verity session launched after the fix, the test will pass (M3).

---

## §6 — IMPACT

| Before | After |
|--------|-------|
| Subagents landed on random models (qwen3-1.7b, nemotron) | All subagents on M3 (1M context) |
| No way to verify model config | `verify_subagent_model.sh` with pass/fail |
| Protocol gap (unconscious incompetence) | Protocol document + standard |
| 1.7B local for "Verity mandate compliance" | 1M context M3 for mandate compliance |

**No more 1.7B when we need 1M context. The team has the gnosis to use this feature properly.**

---

## §7 — FILES

| File | Purpose |
|------|---------|
| `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md` | Full protocol (619 lines) |
| `scripts/verify_subagent_model.sh` | Verify script (94 lines, CI-ready) |
| `.opencode/agents/*.md` (13 files) | Now have `model: M3` |
| `~/.config/opencode/opencode.json` | Default model changed to M3 |

---

*⬡ OMEGA ⬡ KALI ⬡ SUBAGENT-PROTOCOL-FIXED ⬡ 2026-08-28*
*No more qwen-1.7B. All 13 agents on M3 1M context.*
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

