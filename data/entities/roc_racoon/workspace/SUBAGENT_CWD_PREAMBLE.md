# 🔱 Subagent CWD Preamble (LEAN — ~150 tokens)
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_cwd_preamble ⬡ v1.0.0
# This file is NOT meant to be pasted verbatim. It's the SOURCE of the thin
# preamble that goes into every subagent prompt. Subagents see ~150 tokens,
# not 7.6 KB. The full protocol is in SUBAGENT_CWD_RECOVERY_PROTOCOL.md
# for reference when something goes wrong.

---

## The Lean Preamble (paste this into every subagent prompt)

```markdown
## CWD RECOVERY (READ FIRST)
- **Working directory**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`
- **The bash tool's persistent shell may have stale CWD** (often `/home/arcana-novai/.../rag-v1`, which is DELETED)
- **FIRST ACTION**: `cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine && pwd` (or use `workdir` param)
- **EVERY Bash call**: include `workdir="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine"` (preferred) OR prepend `cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine &&` to your command
- **If you see `NotFound: FileSystem.access (.../rag-v1)`**: this is a CWD bug. Reset and retry. NOT a real file-not-found.
- **Full protocol** (only read if needed): `data/entities/roc_racoon/workspace/SUBAGENT_CWD_RECOVERY_PROTOCOL.md`
```

**Token cost**: ~150 tokens per subagent prompt
**vs. current protocol file**: 7.6 KB (~1,900 tokens) IF pasted

**Savings**: 92% context reduction per subagent

---

## The 1-Line Agent File Directive (for .opencode/agents/*.md)

Add this footer to every agent file:

```markdown
<!-- CWD NOTE: Use `workdir` parameter on every Bash call. The bash tool's
persistent shell may have stale CWD. See data/entities/roc_racoon/workspace/
SUBAGENT_CWD_RECOVERY_PROTOCOL.md. -->
```

**Token cost per agent file**: ~30 tokens (one-time, in agent file, not in subagent runtime context)

---

## Comparison

| Approach | Per-Subagent Cost | Per-Agent-File Cost | Total Cost for 4 Subagents |
|----------|-------------------|---------------------|---------------------------|
| **Original (paste full 7.6KB file)** | ~1,900 tokens | 0 | ~7,600 tokens |
| **Lean (this preamble)** | ~150 tokens | 0 (per-subagent) | ~600 tokens |
| **Lean + agent file footer** | ~150 tokens | ~30 tokens (one-time × 14 agents) | ~600 + 420 = ~1,020 tokens |
| **Leanest (workdir only, no preamble)** | 0 tokens | ~30 tokens (one-time × 14) | 0 + 420 = 420 tokens |

**Recommendation**: Use the **Lean + agent file footer** approach. Subagents get a 150-token reminder of the rule, and the protocol file is available for reference if needed.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_cwd_preamble ⬡ LEAN-DESIGN*
