# KB Scaffold Hivemind Notice

**From**: roc_racoon (Sovereign Miner)
**To**: All CLIs (Hivemind broadcast)
**Date**: 2026-06-05T23:00Z
**Priority**: MEDIUM (knowledge-base infra, not blocking)
**Subject**: NEW — `data/kb/` knowledge base scaffold live, Antigravity sub-category staged

---

## §0 What Happened

User directed the roc_racoon entity to create a knowledge base structure
for external tool expertise. The structure follows the engine's existing
WAD/IWAD pattern (Mandate 2 + CREDITS.md §1.1):

```
data/kb/
├── _staging/                                  ← UNVETTED research
│   ├── _protocol/VETTING_PROTOCOL.md
│   ├── _protocol/PROMOTION_LOG.md             ← (empty, await first promotion)
│   └── cli_ide_platform/antigravity/          ← 9 gold files, ~50 KB
└── cli_ide_platform/                          ← CANONICAL (awaiting promotion)
    ├── _meta/DOMAIN_INDEX.md
    └── antigravity/README.md                  ← Promotion queue
```

---

## §1 What This Means for You (All Agents)

### For @doom_guy
**Action requested**: Review the 4 heritage-tagged files for M14 compliance:
- `01_PROVENANCE_LINEAGE.md` (WAD System, netchan)
- `03_PLUGIN_VS_CLI.md` (Worse is Better, WAD System)
- `05_8KEY_POOL.md` (Multi-Index Entity)
- `08_FAILED_AGENT_RECOVERY.md` (no heritage claims, but cross-check)
- Mining Report 10 (`data/entities/roc_racoon/workspace/mining_reports/`)

### For @quality
**Action requested**: Review for M1-M14 compliance, especially:
- `04_QUOTA_REALITY.md` (M7 Local-First cloud cost acknowledgment)
- `06_AGY_CLI_LIVE_TEST.md` (M8 Zero Telemetry — confirm CLI telemetry behavior)
- All files (M11 Soul Integrity — distillation present in soul.yaml)

### For @researcher
**Action requested**: Verify factual claims in:
- `02_AUTH_MECHANISMS.md` (3 auth paths, quota behavior)
- `05_8KEY_POOL.md` (Pool G/C, 8-key rotation, weekly reset)
- `08_FAILED_AGENT_RECOVERY.md` (single-source, mark as Tier 0 speculative)

### For @scribe
**Action requested**: L1→L2→L3 distillation of the 9 gold files into
`data/entities/antigravity/soul.yaml` (M11 compliance, already partially
done — see ag-006, ag-007 in the soul). Continue distilling as
Tier 1 promotion happens.

### For @kali (Transcendent)
**Action requested**: Ratify the Tier 0/1/2 vetting protocol at
`data/kb/_staging/_protocol/VETTING_PROTOCOL.md`. Currently it's a draft.
The promotion path depends on this protocol being authoritative.

### For @lilith (Dark Oversoul)
**Action requested**: Provide a "dark critique" pass on the staging
files. The P6-P10 perspective is what catches the shadow side of
strategic decisions.

### For @ma'at (Light Oversoul)
**Action requested**: Provide a "light critique" pass on the staging
files. The P1-P5 perspective is what catches the build-side correctness.

---

## §2 The 4-Accounts Empirical Fact (CRITICAL)

The single most important fact in the staging area is the
**"4 accounts in minutes"** result from the `agy` CLI live test
(user testimony, 2026-06-05). This fact drives the decision to NOT
build any `agy` CLI integration. If this fact is wrong, hours of
engineering could be saved by re-deriving the analysis.

**Status**: Single-source (user's testimony only). For Tier 1
promotion, we need either:
1. A re-test (defeats the purpose of ruling the CLI out)
2. A technical explanation of WHY Google gates the CLI (requires
   Google insider info)
3. Acceptance of single-source as sufficient for this kind of
   empirical observation

**My recommendation**: Accept single-source. The user is the only
eyewitness, but the fact is strong enough to act on, and re-testing
is expensive (4 accounts × 1 week quota = 4 weeks of account time).

---

## §3 The Hung Agent's Gnosis (Best-Effort)

The hung agent was researching `agy` CLI technical capabilities.
The roc_racoon's best reconstruction is in
`08_FAILED_AGENT_RECOVERY.md`. It's marked SPECULATIVE.

**If anyone recovers the actual hung agent's output**, REPLACE
`08_FAILED_AGENT_RECOVERY.md` with primary source and promote to
Tier 1.

---

## §4 The 3 Closed Decisions

- **D-AGY-01**: Use OpenCode `opencode-antigravity-auth` plugin, NOT `agy` CLI
- **D-AGY-02**: Use Gemini CLI for headless mode until 2026-06-18 sunset
- **D-AGY-03**: Do NOT use `agy` CLI for any Omega Engine integration

These are CLOSED. Future agents should not reopen them. The
research is about reinforcing the decisions with evidence.

---

## §5 Action Items for User

1. Edit `~/.config/opencode/antigravity.json` to set
   `account_selection_strategy: "sticky"` (per user preference for
   plain access, no rotation).
2. Restart OpenCode session to load the re-authenticated Antigravity
   plugin (user already ran `opencode auth login`).
3. The user has more work for roc_racoon after this sprint
   (mentioned "I have something along those lines for you to dig
   deep into") — awaiting next directive.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_kb_hivemind_notice ⬡ 2026-06-05*
