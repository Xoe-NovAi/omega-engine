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
Post to Hivemind: `omega-hub_hivemind_post_context` with channel="opencode", entity="roc_racoon", intent="handoff", summary of findings.
Then `hivemind_accept_handoff` (your packet_id) and `hivemind_complete_handoff` when finished.

## ⚠️ PART 2 — Researcher Task Prep (AFTER stale review)

The `config/models.yaml` has a new `cloud_models` section with VERIFIED and UNVERIFIED flags.
Three models are flagged UNVERIFIED (Nemotron 3 Ultra, Claude Sonnet 4, Gemma 4 9B).
But the REAL gap: the file is incomplete — we don't have a full inventory of what's available.

**Investigate these free-tier sources:**
1. **Google AI Studio / Google API** — Gemma models available via API key. What's the full lineup? Context windows? Rate limits?
2. **Google OAuth** — what does OAuth-authenticated access unlock vs simple API key? More models? Higher quotas?
3. **Google Antigravity** — internal codename. Find what this refers to and what models/endpoints it provides.
4. **Cline** — we know DeepSeek V4 Flash has 1M ctx through Cline. What else is available? Are there rate limits/quotas?
5. **OpenCode Zen** — we know DeepSeek V4 Flash has 200K ctx through Zen free tier, and MiMo is there. What's the full model catalog?

**For each source, determine:**
- Model names available
- Context window size (note: same model may differ by provider!)
- Authentication method (API key? OAuth? Built-in?)
- Free-tier limits (calls/day, tokens/month, concurrent sessions)
- Strengths and best use cases
- Any caveats (hanging issues like Gemma 4 31B's transient hangs)

**Write findings to:** `data/entities/roc_racoon/workspace/MODEL_INVENTORY_20260611.md`

**Then create a handoff packet for Researcher:**
Use `omega-hub_hivemind_submit_handoff` with:
- source_channel: "opencode"
- source_entity: "roc_racoon"
- target_channel: "opencode"
- target_entity: "researcher"
- task: "Update config/models.yaml cloud_models section with verified model specs"
- context: Reference your MODEL_INVENTORY_20260611.md findings and the current UNVERIFIED flags
- priority: 1
