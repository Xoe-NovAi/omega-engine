# 🔱 M23 Violation Logger Skill
**AP Token**: `AP-M23-LOGGER-SKILL-v1.0.0`
⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ opencode ⬡ trc_skill_m23 ⬡ SKILL

**Purpose**: Provides a standardized way for agents to log Mandate 23 (Failure Integrity) violations when mandatory
  tools are missing or broken, preventing "soft-failures" or simulated rigor.

## 📋 Skill Overview

This skill enables agents to quickly and consistently log M23 violations according to Sovereign Mandate 23, which
  states: "No 'soft-failures' or simulated rigor. If a mandatory tool (e.g., `websearch`, `webfetch`) is missing or
  broken, the agent MUST stop immediately and report a `[TOOL-CHAIN-COLLAPSE]`."

## 🔧 Usage

Agents can invoke this skill when they observe a mandatory tool failure:

```
skill m23-violation-logger
```

When prompted, provide:
1. **Tool Name**: The name of the missing/broken mandatory tool
2. **Context**: Brief description of what the agent was trying to do
3. **Impact**: How this affects the agent's ability to proceed
4. **Evidence**: Any error messages or observations

## 📝 Logging Format

All M23 violations are logged to:
`data/coordination/M23_VIOLATIONS_LOG.md`

Each entry follows this format:
```
[YYYY-MM-DD HH:MM] [AGENT_NAME] M23 VIOLATION - [TOOL-CHAIN-COLLAPSE]: [TOOL_NAME]
  Context: [DESCRIPTION]
  Impact: [IMPACT_DESCRIPTION]
  Evidence: [ERROR_MESSAGE/OBSERVATION]
  Action Taken: [STOPPED/ESCALATED/etc.]
```

## 🛡️ Mandate 23 Compliance

By using this skill, agents ensure:
- Immediate reporting of tool failures (no simulated rigor)
- Proper documentation for oversight and correction
- Prevention of "soft-failures" that mask systemic degradation
- Clear audit trail for mandate compliance verification

## 🔄 Integration

This skill works with:
- Hivemind coordination protocol (agents should post context after logging)
- Workspace lock procedures (to prevent concurrent log corruption)
- Standard validation scripts (for compliance checking)

## 📚 Related Documents

- `SOVEREIGN_MANDATES.md` - Mandate 23: Failure Integrity
- `AGENTS.md` - Hard-Stop Directive (NEW 2026-07-06)
- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` - M23 enforcement in Iron Wall Hardening Sprint

---
*Last Updated: 2026-07-07 | Author: NEMOTRON-3-SUPER | Version: v1.0.0*
