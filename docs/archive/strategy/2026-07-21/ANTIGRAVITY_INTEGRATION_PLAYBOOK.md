<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Antigravity IDE — Fleet Integration Playbook
# ⬡ OMEGA ⬡ MAKALI ⬡ ANTIGRAVITY ⬡ INTEGRATION-PLAYBOOK ⬡ v1.0.0
**Version**: 1.0.0
**Purpose**: How every fleet agent coordinates with the Antigravity IDE Hivemind Council member
**Audience**: All 11 engine agents + Hivemind Citizens (cli_cline, cli_gemini)
**Soul**: `data/entities/antigravity/soul.yaml` v1.6.0
**Workspace**: `data/entities/antigravity/workspace/`
**Custom Instructions**: `docs/strategy/ANTIGRAVITY_IDE_CUSTOM_INSTRUCTIONS.md` v3.0.0
**Updated**: 2026-06-18

---

## §1 What Is Antigravity?

Antigravity is Google's **Unified Gateway API** ecosystem with four products:

| Product | Omega Role | Status |
|---------|-----------|--------|
| **Antigravity IDE** | Hivemind Cloud Strategist | 🟢 ACTIVE — strategic oversight peer |
| **Antigravity CLI (`agy`)** | Future provider (#5 in fallback chain) | 🔴 BANNED — plugin (round-robin = Google ban risk) |
| **Antigravity 2.0** | Desktop agent orchestrator | ⏳ Not integrated |
| **Antigravity SDK** | Python SDK (pip install) | ⏳ Not integrated |

**In the Omega Engine, "Antigravity" refers to the Antigravity IDE as a Hivemind Council member.**  
The IDE connects to the Omega Hub MCP at `:8016` and operates as a Sovereign Peer — strategy only, never implementation.

---

## §2 Role & Boundaries

### What Antigravity Does
- **Strategic oversight**: Architectural review, roadmap validation, mandate compliance audit
- **Cross-platform coordination**: Hivemind Council member — sees across OpenCode, Cline, Gemini CLI
- **Cloud validation**: Uses frontier models (Gemini 3.1 Pro, Claude Opus 4.6) for high-stakes reasoning
- **Documentation integrity**: Reviewing docs for coherence, identifying gaps
- **Heritage escalation**: Flags untagged `[id-soft:]` patterns, escalates to doom_guy

### What Antigravity NEVER Does
- ❌ Write source code — strategy is review, not implementation
- ❌ Make git commits — OpenCode is the commit authority
- ❌ Run `make test` — tests are local-first via OpenCode
- ❌ Store sensitive data — their session is in Google's cloud sandbox
- ❌ Execute parallel subagents — serial only
- ❌ Make final decisions for the user — strategic recommendations only

---

## §3 How the Fleet Coordinates with Antigravity

### Coordination Surface: Omega Hub MCP (`:8016`)

Antigravity has access to these Hivemind tools:

| Tool | Purpose |
|------|---------|
| `hivemind_get_awareness` | See who's active on the council |
| `hivemind_post_context` | Share findings with the fleet |
| `hivemind_heartbeat` | Signal presence (5-10 min interval) |
| `hivemind_get_continuation` | Read another member's latest post |
| `hivemind_submit_handoff` | Delegate work to another agent |
| `hivemind_accept_handoff` | Accept delegated work |

### When an OpenCode Agent Should Delegate to Antigravity

| Use Case | Why Antigravity? | Handoff Protocol |
|----------|-----------------|------------------|
| **Architectural review needed** | Antigravity runs Claude Opus 4.6 for deep structural critique | Write `data/coordination/HANDOFF_OMEGA_TO_ANTIGRAVITY_{YYYYMMDD}.md` |
| **Cross-platform coordination** | Antigravity sees across OpenCode, Cline, Gemini CLI | Post `hivemind_post_context` with `intent: "cross_platform_validation"` |
| **High-stakes strategic decision** | Reserve Opus for P0 judgment calls | Use `hivemind_submit_handoff` with full context |
| **Documentation coherence audit** | Cloud perspective catches blind spots local agents miss | Post findings, let Antigravity validate |
| **Heritage vetting escalation** | Antigravity has access to model ecosystem profiles | Route through doom_guy → antigravity cross-validation |

### When Antigravity Should Delegate to an OpenCode Agent

| Use Case | Target | Protocol |
|----------|--------|----------|
| **Code needs to be written** | — | Hand off — Antigravity doesn't write code |
| **Tests need running** | — | Hand off — Antigravity can't run `make test` |
| **Git commit needed** | — | Hand off — Antigravity doesn't commit |
| **Heritage vetting needed** | `doom_guy` | `hivemind_submit_handoff` with `target: "doom_guy"` |
| **Compliance audit** | `verity` | `hivemind_submit_handoff` with `target: "verity"` |
| **Legacy archaeology** | `roc_racoon` | `hivemind_submit_handoff` with `target: "roc_racoon"` |
| **Deep research** | `jem` or `researcher` | `hivemind_submit_handoff` with `target: "jem"` |
| **Parallel decomposition** | `makali` | `hivemind_submit_handoff` with `target: "makali"` |

---

## §4 Communication Protocol

### Handoff File Format

All handoffs TO or FROM Antigravity must use:

```
data/coordination/HANDOFF_ANTIGRAVITY_{YYYYMMDD}_{HHMM}.md
```

Required schema:

```yaml
source: antigravity | <agent_name>
target: <agent_name> | antigravity
intent: <purpose statement>
context: <summary of findings, max 500 words>
attachments:
  - <file_path_1>
  - <file_path_2>
continuation: <next_steps | done>
mandate_refs:
  - M<n> # relevant mandates
```

### Lock File

Antigravity writes:

```
data/coordination/ANTIGRAVITY_LOCK_{YYYYMMDD}.md
```

Other agents must check for ANTIGRAVITY_LOCK before deploying, and Antigravity must check `MAKALI_WORKSPACE_LOCK_{YYYYMMDD}.md` etc. before starting strategic review.

### Heartbeat Protocol

- Antigravity heartbeats every 5-10 min on `hivemind_heartbeat(channel="hivemind", entity="antigravity")`
- If Antigravity has not heartbeaten in >15 min, other agents may assume the session ended
- Other agents should NOT wait on Antigravity for blocking operations — Antigravity is advisory, not critical path

---

## §5 Connection Details

| Detail | Value |
|--------|-------|
| MCP Hub URL | `http://127.0.0.1:8016/sse` |
| Omega Engine directory | `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/` |
| Workspace | `data/entities/antigravity/workspace/` |
| Session gnosis | `data/entities/antigravity/workspace/session_gnosis.md` |
| Usage tracking | `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json` |

---

## §6 Known Constraints

### PoolState Wiring Status (2026-06-18)
✅ **ALL PHASES COMPLETE** — Phases 1-4 implemented.

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | PoolState Dataclass (`pool_state.py`) | ✅ IMPLEMENTED |
| 2 | UsagePoolTracker (`pool_tracker.py`) | ✅ IMPLEMENTED |
| 3 | ModelGateway Integration (`antigravity/` module + `generate_antigravity()`) | ✅ IMPLEMENTED |
| 4 | Quota Checker (`antigravity_check_quota.py`) | ✅ IMPLEMENTED |

The Antigravity module is a **standalone module** at `src/omega/oracle/antigravity/`, NOT a provider in the round-robin chain. Google bans rapid account switching — the module is invoked explicitly only when the gateway determines it's the right backend.

⚠️ **Ban constraint**: The `opencode-antigravity-auth` plugin is **banned** from the provider fabric. Round-robin key rotation triggers Google ban detection. The standalone module must never be auto-rotated.

### Plugin Ban
The `opencode-antigravity-auth` plugin is **banned** from the provider fabric. Round-robin key rotation triggers Google's ban detection. The plugin provides access to Antigravity models through OpenCode — it is NOT used. The Antigravity IDE is a separate surface that connects via MCP, not via the provider fabric.

### Quota Constraints
- Pool G (Gemini): 8 keys, weekly reset (Monday 00:00 UTC)
- Pool C (Claude): 8 keys, weekly reset (independent from Pool G)
- Opus 4.6 is a rare resource — reserve for P0 strategic reviews
- Default to Gemini 3.5 Flash for all standard work

---

## §7 Quick Reference — Files & Locations

| File | Purpose |
|------|---------|
| `src/omega/oracle/antigravity/__init__.py` | Module exports |
| `src/omega/oracle/antigravity/config.py` | Configurable paths (Mandate 16) |
| `src/omega/oracle/antigravity/client.py` | OAuth token refresh + API calls |
| `src/omega/oracle/antigravity/account_manager.py` | Account selection, rate limits, cooldowns |
| `src/omega/oracle/model_gateway.py` | `generate_antigravity()` thin adapter |
| `data/entities/antigravity/soul.yaml` | Soul identity, pool config, gnosis (v1.6.0) |
| `data/entities/antigravity/workspace/session_gnosis.md` | M15 continuity anchor |
| `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json` | Pool usage tracking (wired via `pool_tracker.py`) |
| `data/entities/antigravity/knowledge/ACCOUNT_MAP.yaml` | agy_key → email mapping (8 accounts) |
| `scripts/antigravity_check_quota.py` | Python quota checker — queries Google's `fetchAvailableModels` |
| `src/omega/oracle/pool_state.py` | PoolState dataclass — parses soul.yaml |
| `src/omega/oracle/pool_tracker.py` | UsagePoolTracker — atomic JSON writes, anti-thrashing |
| `docs/strategy/ANTIGRAVITY_IDE_CUSTOM_INSTRUCTIONS.md` | Custom Instructions v3.0.0 |
| `docs/strategy/ANTIGRAVITY_INTEGRATION_PLAYBOOK.md` | This file — fleet coordination reference |
| `docs/research/antigravity/ANTIGRAVITY_CLI_MASTER_REF.md` | CLI technical reference (research) |
| `docs/research/antigravity/MODEL_ECOSYSTEM_PROFILES.md` | Model ecosystem profiles (research) |
| `data/entities/researcher/workspace/ANTIGRAVITY_SYSTEM_DEEP_DIVE.md` | 722-line deep research report |
| `docs/research/antigravity/STRATEGIC_UTILIZATION_PLAN.md` | Original provider fabric plan (research) |
| `docs/research/antigravity/UNKNOWNS_AND_GAPS.md` | Unknowns & gaps (research) |
| `docs/research/antigravity/IDE_VS_CLI_USAGE.md` | IDE vs CLI capacity analysis (research) |
| `docs/strategy/PHASE_C_MASTER_SPEC_VERITY.md` §8 | Antigravity Addendum — SomaticState discovery |
| `data/coordination/ANTIGRAVITY_LOCK_{YYYYMMDD}.md` | Active workspace lock |
| `data/coordination/HANDOFF_ANTIGRAVITY_{YYYYMMDD}_{HHMM}.md` | Handoff files |

---

*⬡ OMEGA ⬡ MAKALI ⬡ ANTIGRAVITY ⬡ INTEGRATION-PLAYBOOK ⬡ v1.0.0 ⬡ 2026-06-18*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: ANTIGRAVITY | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
