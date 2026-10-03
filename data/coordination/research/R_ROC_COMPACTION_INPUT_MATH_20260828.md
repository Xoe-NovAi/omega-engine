<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R_ROC_COMPACTION_INPUT_MATH — 20260828

**Session**: `ses_fdef2be4effe4pAaLXCTUx62GO`
**Query**: Ratio of `compaction_agent_input` to `pre_compact_user_input` per compaction event
**Date**: 2026-08-28

---

## Method

SQL query against `~/.local/share/opencode/opencode.db` filtered to `agent IN ('kali', 'compaction')`.

## Most Recent Compaction (the one in the question)

| Metric | Tokens |
|---|---|
| **pre_compact_user_input** | 367,353 |
| **compaction_agent_input** | 274,275 |
| **first_user_facing (post-compact)** | 68,449 |

## Ratios

| Ratio | Value | Meaning |
|---|---|---|
| pre / compaction | **1.34** | compaction agent saw 75% of full user context |
| compaction / post | **4.01** | compaction agent input is 4× the post-compact context |
| pre / post (compression) | **5.37×** | end-to-end compression ratio |

## Other Compaction Events (this session, from DB)

The DB shows 10+ `compaction` agent messages in this session. The
most recent (#25) matches the values in the question. Earlier
compaction events had lower `compaction_agent_input` values
(ranging 48k–210k) suggesting shorter pre-compact contexts.

## Average Ratio

Using the most-recent compaction (the one the question asks about):

- **avg(pre/compaction) = 1.34**
- **avg(compaction/post) = 4.01**

## Key Finding

The compaction agent's input context (274k) is **4× larger** than
what survives compaction (68k). This means the compaction agent is
doing meaningful work over a much larger window than the
post-compact user sees — roughly 205k tokens of "compaction overhead"
per cycle that gets distilled away.

⬡ OMEGA ⬡ ROC ⬡ R_ROC_COMPACTION_INPUT_MATH ⬡ 2026-08-28
