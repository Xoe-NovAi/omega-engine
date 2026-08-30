<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Subagent Long-Output Protocol — Multi-File Writes, Stall Recovery, Completeness Audit

**AP Token**: `AP-SUBAGENT-LONG-OUTPUT-v2.0.0`
**Status**: ACTIVE — Ratified 2026-08-20 (Kali, post spec-splitting experiment)
**Applies to**: All subagent tasks producing specs, research reports, or any output >50KB
**Companion**: `.opencode/agent/CONVERSATIONAL_SUBAGENT_PROTOCOL.md` (multi-turn engagement, chains, queueing semantics)

---

## 🎯 Default Rule (Ratified)

**All specs and research reports are written as multi-file outputs**: one file per section, tied together by an `index.md`.

Empirical basis (2026-08-20 experiment, Context Injection Phase 1 spec):

| Metric | Single-File | Multi-File |
|--------|-------------|------------|
| Operational depth | Baseline | **3.2x** (traceability matrices, rollback alternatives, Go/No-Go gates) |
| Local-model viability | Requires large context | One section at a time fits small windows |
| Reviewability | Monolithic | Section-scoped diffs |
| Section drops | None observed | **Occurred** (Phase 2 preview, references) |
| Stall rate | 0/1 | **2/2** (recovered both times) |

Multi-file wins on depth and viability; its failure modes (stalls, section drops) are handled by the guardrails below.

---

## 🛡️ Guardrail 1 — Mandated Section Checklist (Prompt-Time)

Every long-output task prompt MUST contain an explicit file manifest. Never say "write a spec about X" — enumerate every file.

### Required prompt elements

1. **Exact directory** for output
2. **Numbered file list** — every filename with a one-line content description
3. **Completeness clause** (verbatim):

   > **COMPLETENESS REQUIREMENT**: Every section in the source plan must appear as a file. No section may be dropped, merged away, or deferred. If you believe a section is redundant, write it anyway and note the redundancy in `index.md`. If context limits force a choice, stop and report which sections remain rather than silently omitting.

4. **Section-to-source mapping** — which source doc/§ each file derives from (gives the audit trail teeth)

### Template fragment

```
**Write to**: `docs/specs/<domain>/<name>/`

**Files to create** (ALL required — no omissions):
1. `index.md` ← navigation + executive summary
2. `01_<SECTION>.md` ← <content> (source: <doc §X>)
3. `02_<SECTION>.md` ← <content> (source: <doc §Y>)
...
N. `NN_<SECTION>.md` ← <content> (source: <doc §Z>)

**COMPLETENESS REQUIREMENT**: Every section in the source plan must appear
as a file. No section may be dropped, merged away, or deferred. If context
limits force a choice, stop and report which sections remain rather than
silently omitting.
```

---

## 🔁 Guardrail 2 — Stall Detection & Recovery (Write-Time)

### Detection
A subagent has stalled if:
- Task returns `state: "completed"` but output is empty or truncated
- Fewer files exist than the manifest requires
- Streaming timeout errors in task result
- Subagent returns immediately without doing work

**Expect stalls on multi-file runs.** Observed rate: 2/2. A stall is a normal operating event, not a failure — budget an orchestration round-trip for it.

### Recovery procedure

1. **Continue the SAME session** via `task_id` — never start a new `task()`
2. **Prompt with the remaining-file manifest only**:

   ```
   You wrote files 1–K of N. Continue writing the remaining files to
   `<directory>`:

   K+1. `<filename>` — <content description>
   ...
   N. `<filename>` — <content description>

   Then update `index.md` to link ALL N files.

   COMPLETENESS REQUIREMENT still applies: no section may be dropped.
   ```

3. **Repeat until all manifest files exist** — each continuation is cheap; silent omission is expensive

### Anti-patterns
- ❌ Starting a new `task()` instead of continuing via `task_id`
- ❌ "Try again" without the explicit remaining-file list
- ❌ Accepting partial output because the session reported "completed"
- ❌ Re-prompting for already-written files (wastes tokens, risks duplicates)

---

## ✅ Guardrail 3 — Post-Write Completeness Audit (Acceptance-Time)

**The orchestrator audits BEFORE accepting the deliverable.** A subagent's "done" is a claim, not a fact.

### Audit steps

```bash
# 1. File count vs manifest
ls -la docs/specs/<domain>/<name>/ | grep -c '\.md$'   # expect N

# 2. Section headers across all files
grep -n "^## " docs/specs/<domain>/<name>/*.md

# 3. Index links resolve
grep -oP '\]\(\K[^)]+' docs/specs/<domain>/<name>/index.md | \
  while read f; do test -f "docs/specs/<domain>/<name>/$f" || echo "BROKEN: $f"; done
```

### Audit checklist
- [ ] Every manifest file exists
- [ ] Every source-plan section appears in some file's headers (diff header list against source plan)
- [ ] `index.md` links resolve to real files
- [ ] No placeholder stubs (`TODO`, `TBD`, empty code blocks) in acceptance-critical sections
- [ ] Content spot-check: pick the densest expected artifact (e.g., a table, a diff, a config block) and verify it's complete, not summarized

### On audit failure
Return to Guardrail 2: continue the same session with the specific missing items. Do not hand-edit substantial content yourself unless the subagent is unrecoverable — and if you do, record it in the Hivemind post.

### Known drop patterns to check specifically
Observed in the 2026-08-20 experiment:
- **Forward-looking sections dropped first** (Phase 2 preview, references) — they feel optional to the writer
- **Test consolidation** — 7 granular tests became 5 consolidated ones; equivalent coverage but verify nothing was silently lost
- **Code shown twice** (inline + install heredoc) — acceptable, but flag if it inflates a file beyond ~2x its siblings

---

## 📋 Orchestrator Workflow (All Three Guardrails)

```
1. WRITE PROMPT     → manifest + completeness clause + source mappings   (G1)
2. LAUNCH task()    → record task_id
3. CHECK OUTPUT     → file count vs manifest
4. IF STALLED       → continue same session with remaining-file manifest (G2)
5. AUDIT            → headers vs source plan, links, stubs, spot-check  (G3)
6. IF GAPS          → back to step 4 with specific missing items
7. ACCEPT           → update trackers, post Hivemind completion
```

---

## When This Protocol Applies
- Any subagent producing >50KB output
- Any spec or design document task (**default: multi-file**)
- Any research report task (**default: multi-file**)
- Any task where streaming timeout occurred previously

## Coordination Duties After Acceptance
- Update `ACTIVE_SPRINT.json` subtask status
- Post Hivemind context with completion + audit result
- Update `SESSION_ANCHOR.md` / `session_gnosis.md` if strategy-relevant
