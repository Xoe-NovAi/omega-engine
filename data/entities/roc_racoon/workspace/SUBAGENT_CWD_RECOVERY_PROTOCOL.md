<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SUBAGENT CWD RECOVERY PROTOCOL
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_cwd_recovery ⬡ v1.2.0
# Last Updated: 2026-06-02 (added §0.1 subagent type selection)
# Maintainer: Roc Racoon (Sovereign Miner)
# Status: WORKAROUND, NOT FIX

---

## §0 THE TRUTH (Read First)

**The ONLY true fix is to restart OpenCode with the correct CWD.** This is not a workaround. This is the actual fix.

```bash
# In your terminal, BEFORE restarting OpenCode:
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
# Then restart OpenCode. The bash tool's default CWD will be the project root.
```

Until you do that, the bash tool's default CWD is `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/rag-v1` (which was the working directory when OpenCode was first launched in this session).

**WHY THIS HAPPENS**: The OpenCode bash tool spawns a fresh subshell per call, with the CWD set to whatever OpenCode's "default" was at startup. The `cd` in one call affects only that subshell — it does NOT update the tool's default CWD for future calls. The only way to update the tool's default CWD is to restart OpenCode from a different working directory.

**WORKAROUND** (until restart): the `rag-v1` directory has been recreated as an empty dir so the validation passes. Every bash call uses the `workdir` parameter to specify the correct CWD for that call.

---

## §0.1 Subagent Type Selection (CRITICAL)

Different subagent types have different tool sets. Choose the right one for the task:

| Subagent Type | Tools Available | Use For |
|---------------|----------------|---------|
| `explore` | glob, grep, read, bash, webfetch, websearch (read-only) | **Reconnaissance only** — finding files, searching, reading |
| `general` | ALL tools (read, write, edit, bash, glob, grep, task, webfetch, websearch) | **Any task that needs to write files** |
| `gnosis-analyst` | specialized for research | Research tasks |
| `jem` / `jem_*` | jem pipeline | Research orchestration |
| `quality` | code review | Quality gates |
| `scribe` | gnosis distillation | Soul updates |
| `pillar` | slot-based | Pillar domain work |

**WRONG CHOICE — Common Mistake**:
> Used `explore` for a mining task that needed to write a report. The subagent correctly identified it had no `write` tool and used `bash` with a heredoc as a workaround. This worked, but is fragile (depends on the bash tool's CWD, escaping, etc.).

**RIGHT CHOICE**:
> For any mining/research task that needs to write findings to disk, use `general` or another subagent type that has `write` and `edit` tools.

**Rule of thumb**:
- If the task ends with "return findings to me" → `explore` is fine
- If the task ends with "write a report to X" → use `general`

---

## §1 Workaround (Until OpenCode Restart)

### 1.1 Use `workdir` Parameter on Every Bash Call (PREFERRED)

```python
# CORRECT — workdir parameter
bash(command="ls -la", workdir="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine")

# WRONG — bare command, may fail with NotFound
bash(command="ls -la")
```

The `workdir` parameter tells the bash tool: "validate THIS path, then run the command from this directory." It works regardless of what the tool's default CWD is.

**Cost**: Zero context bloat. The `workdir` parameter is part of the tool call, not the prompt.

### 1.2 Prepend `cd /correct/path &&` (FALLBACK)

If `workdir` is not available:

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine && <your-command>
```

This works because the subshell starts in the tool's default CWD, and `cd` updates the subshell's CWD before the main command runs. But it does NOT update the tool's default CWD for future calls.

---

## §2 What Roc Racoon Did to Mitigate

1. **Recreated `rag-v1` as an empty dir** — so the tool's CWD validation passes. No more `NotFound` errors.
2. **Uses `workdir` on every bash call** — so each call operates from the correct CWD.
3. **Documented the situation** in this file (so future agents understand the workaround).

---

## §3 Common CWD Paths

| Path | Status | Notes |
|------|--------|-------|
| `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine` | ✅ ACTIVE | Current Omega Engine. Always operate from here. |
| `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/rag-v1` | ⚠️ RECREATED (empty) | Was vaporized. Recreated to fix bash tool validation. |
| `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy` | 📚 LEGACY | Read-only mining target. |
| `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy` | 📚 LEGACY | Read-only mining target. |
| `/home/arcana-novai/Documents/Archives/Old-Stacks` | 📚 LEGACY | Read-only mining target. |
| `/home/arcana-novai/archive/foundation-legacy` | 📚 LEGACY | Read-only mining target. |
| `/media/arcana-novai/omega_library/` | 📚 ARCHIVE | Read-only. |
| `/media/arcana-novai/omega_vault/` | 📚 ARCHIVE | Read-only. |

---

## §4 Subagent Prompt Template

When dispatching a subagent, include a thin CWD pointer in the prompt (~50 tokens):

```markdown
## CWD NOTE
- Use `workdir="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine"` on EVERY Bash tool call
- If you must use bare bash, prepend `cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine &&` to your command
- See SUBAGENT_CWD_RECOVERY_PROTOCOL.md for full details if needed
```

**Token cost**: ~50 tokens per subagent prompt. Negligible.

---

## §5 Verification Checklist

Before returning your final report, verify:
- [ ] All bash calls used `workdir` parameter or `cd` prefix
- [ ] No `NotFound: FileSystem.access (.../rag-v1)` errors in your output
- [ ] All file paths in your report are absolute

---

## §6 Long-Term Fix (OpenCode Team Request)

The proper fix is for OpenCode to:
1. Always use a fresh shell with the project root as CWD per call, OR
2. Allow the user to set the default CWD in OpenCode config, OR
3. Reset CWD to the project root at the start of each bash tool call

**Until OpenCode implements one of these, the workaround is the `workdir` parameter on every call.**

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_cwd_recovery ⬡ WORKAROUND-v1.1.0*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
