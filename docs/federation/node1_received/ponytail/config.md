# Ponytail Config — LAZY SENIOR DEV

## Status: ✅ REGISTERED, LIVE AFTER RESTART

**Checkout:** `~/Vanguard/ponytail@356918e`
**Registered:** Absolute-path `.mjs` in `~/.config/opencode/opencode.json`

```json
{
  "plugin": ["/home/xnai/Vanguard/ponytail/.opencode/plugins/ponytail.mjs"]
}
```

## Hook-Trust Review: PASSED
**Lifecycle Hooks (2):**
1. `experimental.chat.system.transform` — append-only ruleset injection, honors `/ponytail off`
2. `command.execute.before` — scoped to `/ponytail` mode writes

**Config Hook:** Registers commands + skills directory
**No destructive hooks. No exfiltration paths. No PreToolUse blocks.**

## Commands
- `/ponytail` — mode switch (lite|full|ultra|off)
- `/ponytail-review` — diff over-engineering detection
- `/ponytail-audit` — repo bloat audit
- `/ponytail-debt` — ponytail: comment ledger
- `/ponytail-gain` — impact scoreboard
- `/ponytail-help` — quick reference

## Coexistence
Both gnosis-leash and ponytail append to `output.system` — neither overwrites. Compatible.

## Hook-Trust Review: PASSED
- No destructive hooks
- No exfiltration paths  
- No PreToolUse blocks that could fight our toolset
- Transport shim approach (not env vars) — compatible with our setup
