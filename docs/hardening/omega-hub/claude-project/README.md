# 🔱 Omega Hub — Claude.ai Project Setup

This folder contains everything you need to set up the **Hub Architect** in Claude.ai.

## Quick Setup (2 minutes)

### Step 1: Populate the outbox

```bash
bash upload-all.sh
```

This copies all 16 files into `outbox/` with clean, RAG-friendly filenames.

### Step 2: Add Project Knowledge (Claude.ai)

1. Open your Claude.ai project
2. Go to **Project Knowledge**
3. Click **Add files**
4. Select **all 16 files** from `claude-project/outbox/`
5. Wait for upload to complete

### Step 3: Set Custom Instructions (Claude.ai)

1. Go to **Custom Instructions**
2. Open `claude-project/system-prompt.md`
3. **Copy the entire contents**
4. Paste into the Custom Instructions field
5. Save

### Step 4: Start a conversation

Tell the Hub Architect:
> "Review the current state using active-tracker.md and carmack-audit-findings.md, then produce a modularization strategy for Phase 1a."

## File Inventory

| File | Purpose |
|------|---------|
| `system-prompt.md` | ⬡ Custom Instructions (always in context) |
| `hub-system-overview.md` | Engine context, team, 15 mandates |
| `target-module-architecture.md` | Target modules, extraction order |
| `carmack-reconstruction-plan.md` | Carmack's S3 modularization blueprint |
| `carmack-audit-findings.md` | Active + resolved audit findings |
| `phase-0-fixes.md` | What was tactically fixed 2026-06-13 |
| `m9-compliance-analysis.md` | `_safe_call()` error handling spec |
| `sprint-v2-briefing.md` | Parallel sprint architecture |
| `sovereign-gateway-spec.md` | Gateway class + rate limiter |
| `m15-continuity-spec.md` | Startup/shutdown hydration |
| `search-protocol.md` | 5-tier search priority |
| `sovereign-mandates.md` | M1-M15 filtered for Hub work |
| `temple-grade-gates.md` | T1-T11 with Hub-relevant checks |
| `heritage-patterns-in-hub.md` | `[id-soft:]` patterns in the Hub |
| `active-tracker.md` | Current 5-phase task tracker |
| `server-snapshot.py` | Frozen 3,110-line server.py pre-split |
| `mcp-runtime.py` | How the Hub is launched |

## File Selection Rationale

- **All files < 500 lines** (except `server-snapshot.py` which must be full for code reference)
- **Total**: ~5,000 lines across 16 files — well within Claude's RAG capacity
- **RAG-friendly names**: Descriptive, lowercase, hyphenated for best retrieval
- **No noise**: No intra-team notes, no superseded docs, no oversized files

## Troubleshooting

- **"Claude can't find a file"** → Reference it by the name in `outbox/`. The prompt tells Claude the file names.
- **"Out of date"** → Run `upload-all.sh` again after any changes to the project files.
- **"Too many files"** → RAG handles this well. Only 16 files at ~300 avg lines each is light.
