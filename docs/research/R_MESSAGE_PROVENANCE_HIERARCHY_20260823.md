<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R: Message-Level Provenance Hierarchy — Ground Truth for Model Attribution
**AP Token**: `AP-RESEARCHER-PROVENANCE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_provenance_hierarchy ⬡ ACTIVE

**Date**: 2026-08-23
**Status**: VERIFIED (empirical, this session) · **Supersedes**: ICS-as-primary-provenance assumption
**Trigger**: Architect insight — "Doesn't every prompt get injected with the model name? Can't we use that as the ultimate ground truth? Even the ICS isn't always accurate."
**Related**: PLATFORM_GROUND_TRUTH_LOG entry #11 · OX_ALPHA_TRANSITION_BLUEPRINT B1 (revised) · MEDITATION_researcher_20260823_GNOSIS_MINING_CODEX (V8 amendment)

---

## §1 The Problem

OpenCode sessions can hot-swap models mid-session. Four sources claim knowledge of "which model produced this text," and they disagree:

| Source | What it actually stores | Failure mode |
|---|---|---|
| `sessions.model` column | Last-used / creation-time value | **Silently stale after any hot-swap** |
| System-prompt injection | Runtime-authoritative per inference | Not persisted per-message — unrecoverable retroactively |
| ICS headers in text | Agent self-report | Hallucinable — two wrong self-IDs recorded in one session (claimed Ox Alpha while Sonnet; claimed Sonnet while Opus) |
| Agent self-report in prose | Same as ICS | Worse — no format constraint at all |

Cost of the confusion, observed live: an agent built a strategy on believing it WAS the substrate model; training-data mining nearly attributed four model families' output to one label; forensic identity resolution required multi-source cross-checks improvised per-incident.

## §2 The Discovery

`opencode.db` stamps **per-message** provenance at response receipt:

```
messages.modelID     -- e.g. 'x-preview-f-free', 'big-pickle', 'antigravity-claude-opus-4-6-thinking'
messages.providerID  -- e.g. 'opencode'
```

**Empirical verification** (session `ses_fd81c19dcffe1nkbPqFg5kRt2v`, queried via opencode-sessions-explorer):

| Message | Timestamp | role | modelID stamp |
|---|---|---|---|
| msg_027e3e689001artQA5qV3AQqgR | 1787375642249 (Aug 21) | user | `big-pickle` |
| msg_02fd8475b001q3mZBlH4nHTaO7 | 1787509098331 (Aug 23) | assistant | `x-preview-f-free` |

Same session; stamps differ and match the actual model chain. The runtime writes ground truth into the DB continuously. No parsing required.

## §3 The Verification Hierarchy

```
Tier 0  messages.modelID          PRIMARY. Runtime-stamped per message.
                                  Use for: mining attribution, forensics, audits.
        Corroboration: cost/token fingerprints (cost=0 ⇒ free tier;
        token ratios differ per model family).

Tier 1  system-prompt injection   Authoritative LIVE ("You are powered by X"
        ("You are powered by…")   injected each call, updates on swap).
                                  Use for: in-session self-identification.
                                  NOT persisted per message — cannot be
                                  recovered for historical messages.

Tier 2  ICS headers               Agent-authored text. Corroboration only.
        (⬡ … ⬡ model ⬡)          Detects gross drift when it DISAGREES
                                  with Tier 0; never primary.

Tier 3  sessions.model column     STALE. Never trust alone. Diagnostic
                                  value only ("what was used last/first").
```

**Rule**: any pipeline attributing text to a model MUST join on Tier 0. Any agent resolving its own identity live MUST prefer Tier 1 over Tier 3. Disagreement between tiers is itself a signal (stale metadata or hallucinated self-report — investigate).

## §4 Residual Caveat (M22 honesty)

Tier 0 records what the runtime **dispatched to**, not necessarily what **served**. A cloaked slug (`x-preview-f-free`) may route to different underlying checkpoints across days without label change (cf. Grokster Attack D, substrate-drift). For training-data purposes the dispatch label is the correct unit (that is what the provider contract delivered). For forensic-grade claims about *weights-level* identity, corroborate with cost/token fingerprints or accept uncertainty explicitly.

## §5 Implementation Notes

### Mining attribution (blueprint B1, revised)
```sql
SELECT m.id, m.modelID, m.providerID, p.type, p.text
FROM messages m JOIN parts p ON p.message_id = m.id
WHERE m.role = 'assistant' AND m.session_id = :sid;
-- attribute per-message via m.modelID; assistant rows only for training data
```
ICS regex parsing: **demoted to corroboration pass** (flag rows where Tier 0 and Tier 2 disagree → manual review queue).

### Live self-identification (agent inoculation)
Agents reading `session.model` or DB session rows for "who am I" will be wrong post-swap. Correct order: system-prompt declaration (Tier 1) → current-message context → never bare session metadata.

## §6 Incidents Prevented by This Doc

1. Training corpus mislabeling (four model families under one label)
2. Agent identity crises from stale metadata (observed ×4 this session)
3. False forensic conclusions from single-source telemetry (V8's "witness not judge")
4. Wasted engineering on regex-parsing a solved problem

## §7 Falsification Path

If OpenCode changes stamping behavior (e.g., batches responses, stamps at queue-time rather than response-receipt), Tier 0 degrades toward Tier 3. Detection: periodic spot-check comparing message.modelID against known live swaps (the Claude.ai adjudication passes provide natural cross-check points). If a mismatch class appears, re-run the §2 verification and demote accordingly.

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ R_MESSAGE_PROVENANCE_HIERARCHY ⬡ v1.0 ⬡ 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-09-08T13:09:06Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: VERIFIED
actual_models(Tier0): nemotron-3-ultra-free, x-preview-f-free, minimax/minimax-m3:free, big-pickle, nvidia/nemotron-3-super-120b-a12b:free, hy3-free
first_audit: 2026-08-31T03:09:52Z | updated: 2026-09-08T13:09:06Z
-->




