# 🔱 Web Claude Account Tracker
**AP Token**: `AP-WEB-CLAUDE-ACCOUNT-TRACKER-v1.0.0`
**Date**: 2026-08-08
**Purpose**: Track 8 Web Claude account rotation — quota state, current task, reset window.
**Updated by**: User or OpenCode CLI agent at session start/end.

---

## How to Use

- Accounts are indexed by their **position in the Google login list** (top = 1, bottom = 8)
- Update `Last Used` and `Status` every time you switch accounts
- `Reset ~` is approximate — rolling 5-hour window from last heavy usage
- **Rule**: Never run the same task on two accounts simultaneously

### Status Values
- `FRESH` — not used recently, full quota available
- `IN USE` — currently active session running
- `DRAINED` — quota hit, waiting for reset
- `PARTIAL` — quota hit mid-artifact, continuation needed on next account
- `AVAILABLE` — used earlier, quota likely recovered (>5h ago)

---

## Account State

| # | Google Index | Last Used | Last Task | Artifact | Status | Reset ~ |
|---|-------------|-----------|-----------|---------|--------|---------|
| acct-1 | 1st | 2026-08-07 | Hub modularization review | WCA-001, WCA-002 | AVAILABLE | recovered |
| acct-2 | 2nd | — | — | — | FRESH | — |
| acct-3 | 3rd | — | — | — | FRESH | — |
| acct-4 | 4th | — | — | — | FRESH | — |
| acct-5 | 5th | — | — | — | FRESH | — |
| acct-6 | 6th | — | — | — | FRESH | — |
| acct-7 | 7th | — | — | — | FRESH | — |
| acct-8 | 8th | — | — | — | FRESH | — |

---

## Active Sessions

| Account | Task | Pack Profile | Started | Expected Artifact | Notes |
|---------|------|-------------|---------|------------------|-------|
| — | No active sessions | — | — | — | — |

---

## Rotation Rules

1. **Sequential default**: drain acct-1 → acct-2 → ... → acct-8 → wait for resets
2. **Parallel streams**: assign different packs/tasks to different accounts — never duplicate tasks
3. **Carry-over on quota hit before artifact**:
   - Download partial artifact from current account
   - Move to next FRESH account
   - Upload same pack, paste continuation prompt
4. **Carry-over on quota hit after artifact**:
   - Download complete artifact, mark account DRAINED
   - Move to next account for next task — no carry-over needed
5. **Reset tracking**: mark DRAINED with timestamp; mark AVAILABLE after ~5h

---

## Parallel Stream Assignment (Active)

| Stream | Account | Task | Pack | Status |
|--------|---------|------|------|--------|
| — | — | No parallel streams active | — | — |

---

*Updated: 2026-08-08 by kali (registry initialization)*
