<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Context Pack Creation Guide — Web Claude / Claude.ai Projects

**AP Token**: `AP-CTX-PACK-GUIDE-v1.0.0`
**Date**: 2026-08-10
**Author**: @john_carmack
**Purpose**: How to create, manage, and use context packs for Web Claude / Claude.ai project audits.

---

## The Core Mental Model

A Claude.ai project has **three separate input channels**:

| Channel | What It Is | How It's Set | Persistence |
|---------|-----------|--------------|-------------|
| **Project Knowledge Pack** | Files uploaded to the project | User uploads via UI | **FIXED until user uploads more** |
| **System Prompt** | Custom Instructions | User pastes into Settings → Custom Instructions | Persistent across sessions |
| **Chat Prompt** | The message sent to start/continue a session | User sends as chat message | One-shot per message |

**Critical rule**: The pack is a **snapshot**. It does NOT update automatically. If you reference a file that isn't in the pack, **it does not exist in Claude's world** unless you upload it or paste its contents into the chat prompt.

---

## Lesson 1: The Pack Is Fixed

**Mistake made**: Saying "now in the pack" or "P3-unblocked files (now in pack)" when the files were NOT uploaded.

**Reality**: The sovereign-audit pack was uploaded once (2026-08-09, 39 files, 217K tokens). It has not changed. Any file created locally (P3 prompts, concatenated files, supplemental docs) does NOT exist in Claude's world until explicitly uploaded.

**Rule**: Never say a file is "in the pack" unless you personally uploaded it via the Claude.ai UI.

---

## Lesson 2: Three Channels, Three Strategies

### Strategy A — Project Knowledge Pack (Best for large, stable files)
- Upload files via the Claude.ai project UI
- Available to all sessions in that project
- **Limitation**: Fixed snapshot — must re-upload to update
- **Best for**: Source code, configs, manifests, large reference docs

### Strategy B — System Prompt / Custom Instructions (Best for role + constraints)
- Paste into Settings → Project → Custom Instructions
- Persistent across all sessions
- **Limitation**: Counts against context window; keep concise (~100-150 lines)
- **Best for**: Role definition, mandate constraints, output format, rules

### Strategy C — Chat Prompt (Best for task-specific instructions + small files)
- Sent as the message to start/continue a session
- **Advantage**: Can include file contents directly (paste or attach)
- **Best for**: Investigation questions, task scope, small file contents (<500 lines)

### Strategy D — Concatenated Files (Best for multiple small files not in pack)
- Combine multiple files into ONE file with clear `=== FILE N: path ===` separators
- Upload as a single project file
- **Advantage**: One upload, multiple files, Claude can parse separators
- **Best for**: 3-10 files that are each <500 lines

---

## Lesson 3: Verification-by-Comparison Strategy

When you've already done work (P0/P1/P2 fixes) and want Claude to verify:

1. **Do NOT ask Claude to "verify our fixes"** — it doesn't have the post-fix code
2. **DO ask Claude to audit the pre-fix source** — it has the original pack
3. **Compare findings against your fix list** — the delta is your verification

This turns Claude's limitation (fixed pack) into a feature: it documents what was wrong, you confirm what you fixed.

---

## Lesson 4: Accurate Wording in System Prompts

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| "post-P2 snapshot" | "P2 audit source — original pre-fix codebase" |
| "now in pack" | "NOT in pack (upload or paste to provide)" |
| "current state" | "original audit source" |
| "verify our fixes" | "audit the source code in this pack" |

---

## Lesson 5: What to Provide for a P3+ Deepening

When the original pack lacks files needed for the next audit phase:

1. **Identify the gap**: Which files are referenced but not in the pack?
2. **Create a concatenated file**: Combine them with `=== FILE N: path ===` separators
3. **Upload to project files**: Give it a clear name like `P3_UNBLOCKED_FILES.md`
4. **Update the system prompt**: Reference the uploaded file by name
5. **Update the chat prompt**: Tell Claude where to find the files

---

## Lesson 6: Token Budget Awareness

- System prompt: ~100-150 lines max (persistent cost per session)
- Chat prompt: ~150-200 lines (one-shot cost)
- Pack: ~250K tokens (fixed cost)
- **Total**: Keep system + chat under ~500 lines to leave room for pack + output

---

## Lesson 7: The 5-Element Formula for Recommendations

Every recommendation in audit reports MUST use:

```
[Role] + [Scope] + [Focus] + [Format] + [Severity]
```

Example: `[Senior Architect] + [model_gateway.py generate()] + [fallback chain] + [derive from providers.yaml] + [HIGH]`

---

## Checklist for Creating a New Audit Pack

- [ ] Identify the files needed for the audit
- [ ] Check which files are already in the project pack
- [ ] For files NOT in the pack: create a concatenated file with separators
- [ ] Write the system prompt (role + constraints + rules + output format)
- [ ] Write the chat prompt (investigations + questions + deliverables)
- [ ] Write supplemental context (scope map, known gaps, remediation history)
- [ ] Verify all three documents say accurate things about what's in/out of the pack
- [ ] Upload concatenated file + supplemental context to project files
- [ ] Paste system prompt into Custom Instructions
- [ ] Send chat prompt as the audit request

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ CTX-PACK-GUIDE-v1.0.0 ⬡ 2026-08-10*
