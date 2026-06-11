# 🔱 Kali → Roc Racoon — Wave 1.5 Phase 3 Handoff
# ⬡ OMEGA ⬡ KALI ⬡ ROC_RACOON ⬡ HANDOFF ⬡ 2026-06-11

## Your Mission: Inaugural Stale Handoff Review (hi-handoff-5)

### Context
Wave 1.5 is mostly complete. Kali has already dispatched and verified:
- **Phase 1 (P0)**: Sterilization gate ✅ | Workspace locks ✅ | Handoff TTL ✅ | Cold-store hydration ✅
- **Phase 2 (P1)**: Memory MCP tools ✅ | Context hydration tool ✅ | Hivemind metrics ✅

### Your Task
The handoff system at `data/handoff/` has a backlog. You need to scan, analyze, and recommend:

**P0 — Do this first in your session:**

1. **Read `KALI_SPRINT_ORCHESTRATION_20260610.md`** (`data/coordination/`) — see item hi-handoff-5 for full spec
2. **Scan all handoff directories**:
   - `data/handoff/pending/` — 21 packets (anything >24h old → recommend stale)
   - `data/handoff/active/` — 6 packets (anything >48h old → recommend stale)
   - `data/handoff/completed/` — 2 packets (anything >7d old → recommend archive)
   - `data/handoff/stale/` — 0 packets (newly created directory, empty)
3. **For each packet**: read the JSON, extract source/task/age, decide: **archive** (no value), **requeue** (still relevant), or **delete** (duplicate/spam)
4. **Write your report** to `data/entities/roc_racoon/workspace/STALE_HANDOFF_REVIEW_20260611.md`

### Model Choice
Use **Gemma 4 31B** via Google AI Studio for your analysis. It has a 262K context window — more than enough to read all 29 packet files. The TTL reaper (built by P9) needs to run first to auto-categorize expired ones before your review. If the TTL reaper hasn't run yet, you can run it manually by inspecting timestamps.

### Your Handoff Packet
Kali created a pending handoff for you: `data/handoff/pending/ho_8e204750bb25.json`

### Output Format
Return a markdown report with:
- Summary table (totals by status)
- Per-packet table: ID | source | target | created | age | verdict
- Recommended actions list

### When Done
Post to Hivemind: `omega-hub_hivemind_post_context` with cli="roc_racoon", intent="handoff", summary of findings.
Then `hivemind_accept_handoff` (your packet_id) and `hivemind_complete_handoff` when finished.
