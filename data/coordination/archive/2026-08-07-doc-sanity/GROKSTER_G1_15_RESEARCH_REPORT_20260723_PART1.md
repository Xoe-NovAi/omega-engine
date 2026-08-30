<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Gap G1-15: Grok CLI 8-Account Rotation — Comprehensive Research Report

**AP Token**: `AP-GROKSTER-G1-15-20260723`
**Date**: 2026-07-23
**Entity**: grokster (Grok Ecosystem Specialist)
**Handoff**: `ho_00cb63f04efb` (from Kali, priority 2/critical)
**Status**: COMPLETE — All 3 queries + deep MCP/ACP integration research

---

## Executive Summary

This report delivers complete findings for **Gap G1-15: Grok CLI 8-Account Rotation** as assigned by Kali for Phase 1 Parallel Research. The research covers:

1. **Query 1**: `grok cli multiple accounts rotate 2026` — Official + community ecosystem
2. **Query 2**: `grok API key multi account rotation` — xAI Management API + production patterns
3. **Query 3**: `xAI API key rotation multiple accounts 2026` — Billing/quota integration + live sources
4. **Deep Dive**: MCP/ACP integration architecture for Omega Engine 8-account fleet

**Key Finding**: Grok Build **natively supports multi-account** via `grok login`/`logout`, per-model keys, and `auth_provider_command`. Five production-ready community tools implement quota-aware rotation. The xAI Management API provides programmatic key rotation with grace periods. Live quota tracking works today via gRPC-web `GetGrokCreditsConfig`.

---

## PART 1: Query 1 — Grok CLI Multiple Accounts Rotation (2026)

### 1.1 Official xAI Grok Build (xai-org/grok-build)

**Source**: `docs.x.ai/build/cli/headless-scripting`, `docs.x.ai/build/features/mcp-servers`, `xai-org/grok-build` source

#### Authentication Precedence (Official)
```
1. Per-model `api_key` / `env_key` in `~/.grok/config.toml`
2. Active session token (`~/.grok/auth.json` from `grok login`)
3. `XAI_API_KEY` environment variable
```

#### Multi-Account Mechanisms
| Mechanism | Command | Storage | Use Case |
|-----------|---------|---------|----------|
| Browser OAuth | `grok login` | `~/.grok/auth.json` | Interactive |
| Device Code | `grok login --device-auth` | `~/.grok/auth.json` | SSH/CI/Headless |
| Per-Model API Key | `config.toml` `[model.x]` `api_key` | `~/.grok/config.toml` | BYOK / CI |
| Enterprise SSO | `auth_provider_command` | External binary stdout | Corporate proxy |

#### ACP stdio (Agent Client Protocol)
```bash
grok agent stdio
# JSON-RPC 2.0 over stdin/stdout, protocolVersion 1
# Used by: Zed, VS Code extensions, Multica, peer-agents-mcp, custom orchestrators
```

#### MCP Servers
```bash
grok mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path
grok mcp add --transport http linear https://mcp.linear.app/mcp
# Stored in ~/.grok/config.toml or .grok/config.toml (project)
# ${VAR} expansion, OAuth tokens in ~/.grok/mcp_credentials.json
```

---

### 1.2 Community Tools — Production-Ready Multi-Account

#### A. ibi6/grok-switch (Desktop GUI, Tauri/Rust)
**Source**: `github.com/ibi6/grok-switch`, `farion1231/cc-switch#5453`

| Capability | Details |
|------------|---------|
| **Official accounts** | Captures `grok login` sessions → `~/.grok-switch/accounts/<id>/` |
| **One-click switch** | Swaps `~/.grok/auth.json` + `config.toml` atomically |
| **Health checks** | Probes `chat_completions`/`responses`/`messages` before enable |
| **Backups** | Auto-backup before switch; ~30 kept in `~/.grok-switch/backups/` |
| **Import** | Read-only from `~/.cc-switch/cc-switch.db` (Claude Code Switch) |
| **Privacy** | Keys stay under `~/.grok-switch/`; logs mask secrets |

**Architecture**: Manages `gs-*` model sections in `config.toml`; tray icon; light/dark theme

#### B. kenryu42/pi-grok-cli PR #10 (Pi Extension, TypeScript)
**Source**: `github.com/kenryu42/pi-grok-cli/pull/10`, `pi.dev/packages/pi-grok-cli`

| Feature | Implementation |
|---------|----------------|
| **Independent providers** | `grok-cli`, `grok-cli-2`...`grok-cli-8` (8+ accounts) |
| **Quota cache** | 30min TTL, persisted, 3 concurrent refreshes |
| **Exhaustion rotation** | Triggers on **exact error**: `OpenAI API error (402): 402 "Grok Build usage balance exhausted"` |
| **Cooldown** | 5 minutes per exhausted account (per session) |
| **Quota-ranked fallback** | Ranks by tightest remaining % (monthly/weekly); stale/missing keeps circular order |
| **Dashboard** | `/grok-cli-accounts gui` — browser UI on random `127.0.0.1` port, 15min idle shutdown |
| **Headless login** | Device-code via TUI; browser login via dashboard |

**Key Files**:
- `src/provider/rotation.ts` — rotation logic with early-return pattern
- `src/provider/quotaCache.ts` — centralized billing via `/usage` command (gRPC-web)
- `src/provider/accounts.ts` — serialized mutations, alias-aware registration

#### C. artickc/grok-telegram-bot v2.2.3+ (Telegram Bot, Node.js)
**Source**: `github.com/artickc/grok-telegram-bot`, releases v2.2.2-v2.3.1

| Feature | Implementation |
|---------|----------------|
| **Headless instant rotate** | Stop CLI → swap `~/.grok/auth.json` → restart `grok agent stdio --no-leader` → retry |
| **One-pass rotation** | Cycles through saved accounts **once**; first success wins; stops if all fail |
| **Device auth** | `/reauth` uses `grok login --device-auth` (device code in Telegram) |
| **ACP flags** | `--no-leader` so auth.json swaps take effect; `AUTO_APPROVE_PERMISSIONS=true` |
| **Error classification** | 402 `Payment Required` / `usage balance exhausted` (ACP `[-32603]`) → immediate rotate |
| **Access denial** | 403 `Forbidden` / `Access denied` → bypass retry, mark `⚠️`, rotate |
| **Persistence** | Credentials in git-ignored `data/` dir; real emails from JWT claims |

#### D. djtelicloud/grok-mcp-server (UniGrok, Docker)
**Source**: `github.com/djtelicloud/grok-mcp-server`

| Feature | Details |
|---------|---------|
| **Transport** | Streamable HTTP on `http://localhost:4765/mcp` |
| **Two planes** | 1) Grok Build subscription (flat-rate) 2) xAI API key (metered, adds vision/X search) |
| **Control Center** | `http://localhost:4765/ui/` — live routing, cost, benchmarks |
| **Credentials** | CLI OAuth + API key in Docker volume; never in IDE config |
| **IDE connect** | MCP Streamable HTTP + `X-Client-ID` header |

#### E. Rakeen70210/peer-agents-mcp (MCP Server Wrapper)
**Source**: `github.com/Rakeen70210/peer-agents-mcp`

| Tool | Purpose |
|------|---------|
| `grok_chat` | One-shot prompt → Grok reply |
| `grok_review` | Unified diff → per-dimension code review |
| `grok_consult` | Message history replay for multi-turn |
| `grok_challenge` | Adversarial: find bugs, races, edge cases, security holes |

**Transports**: `headless` (default, `grok --prompt-file`) or `acp` (warm pool, `PEER_AGENTS_GROK_ACP_MAX_CLIENTS=4`, idle recycle 5min)

---

### 1.3 Myth-Busting: Query 1

| Myth | Reality |
|------|---------|
| "Grok CLI doesn't support multiple accounts" | **False** — Official `grok login`/`logout`, per-model keys, `auth_provider_command`, 5 community tools |
| "You need browser for each account switch" | **False** — `--device-auth`, `auth_provider_command`, headless `auth.json` swap all work |
| "No quota-aware rotation exists" | **False** — pi-grok-cli (exhaustion + quota rank), grok2api (QuotaWindow), OmniRoute (live gRPC-web) |
| "Session tokens auto-refresh" | **False** — `grok login` tokens ~7 days; only refresh = re-login. **True for Management API keys** |

---

## PART 2: Query 2 — Grok API Key Multi-Account Rotation

### 2.1 xAI Management API (Official)

**Source**: `management-api.x.ai`, `docs.x.ai/build/enterprise`

#### Key Endpoints
| Endpoint | Purpose |
|----------|---------|
| `POST /auth/api-keys` | Create key with ACLs (`api-key:model:*`, `api-key:endpoint:*`), QPS/QPM/TPM limits |
| `POST /auth/api-keys/{id}/rotate` | **Rotate secret** — old key valid for configurable grace period (default 24h, max 7 days) |
| `DELETE /auth/api-keys/{id}` | Revoke key |
| `GET /auth/api-keys/{id}/propagation` | Check cluster propagation |
| `GET /v1/billing/teams/{teamId}/postpaid/invoice/preview` | Billing preview (requires Management Key with `BillingRead`) |

#### Key Architecture
- **Team-scoped keys** (not user-scoped)
- **Management Key** separate from API Key (Settings → Management Keys)
- Keys created at `console.x.ai` → export `XAI_API_KEY`

---

### 2.2 Production Rotation Patterns

#### A. Pollinations (`rotate-genai-xai.sh`)
```bash
# Zero-downtime pattern
1. Create new key via Management API
2. Update SOPS/Secrets with new key
3. Deploy + health-check
4. Delete old key (old key valid until PR merges + deploy passes)
```

#### B. Sim Studio (PR #5574)
```typescript
// Hosted key rotation pool
env: XAI_API_KEY_1, XAI_API_KEY_2, XAI_API_KEY_3
function getRotatingApiKey('xai') // round-robin
// Mirrors OpenAI/Anthropic/Z.ai pattern
```

#### C. Onekey (abhirajadhikary06)
- AES-256 client-side encryption
- Unified platform key → category proxy `/proxy/sdk/openai`
- 10-50+ keys across providers (OpenAI, Anthropic, Groq, Gemini, **xAI**)
- CLI: `Onekey add-key`, `Onekey call <unified_key>`, `Onekey usage`

---

### 2.3 Grok Build Specifics

| Auth Method | Precedence | Rotation |
|-------------|------------|----------|
| `XAI_API_KEY` env | High (beats session) | Management API rotate |
| Per-model `api_key`/`env_key` | Highest | Config deploy |
| `auth_provider_command` | Dynamic | External binary rotation |
| Browser session (`auth.json`) | Low | Re-login only (~7 days) |

---

## PART 3: Query 3 — xAI API Key Rotation + Billing/Quota Integration

### 3.1 Live Quota Sources (Verified Working)

#### 1. gRPC-web (Primary — Works Today)
```bash
POST https://grok.com/grok_api_v2.GrokBuildBilling/GetGrokCreditsConfig
Headers:
  Content-Type: application/grpc-web+proto
  Authorization: Bearer <token from ~/.grok/auth.json>
  X-XAI-Token-Auth: xai-grok-cli
Body: empty protobuf (0 bytes)

Response (proto3, zero fields omitted):
  credit_usage_percent: float
  current_period: { start, end, type: WEEKLY|MONTHLY }
  on_demand_cap: int64
  on_demand_used: int64
  prepaid_balance: int64
  is_unified_billing_user: bool
  history: []
```

**Source**: `xai-org/grok-build/crates/codegen/xai-grok-shell/src/billing.rs`, OmniRoute #6844

#### 2. ACP Extension `x.ai/billing` (When Available)
- Over `grok agent stdio` ACP connection
- Returns: `usedPercent`, `resetsAt`, `onDemandEnabled`
- Falls back to gRPC-web on `-32601 Method not found`

#### 3. xAI Management API Billing
- `GET /v1/billing/teams/{teamId}/postpaid/invoice/preview`
- Requires Management Key with `BillingRead` scope

---

### 3.2 Billing Model (June 2026+)

| Aspect | Detail |
|--------|--------|
| **Pool** | Unified weekly across **all Grok products** (Chat, Imagine, Voice, Build, API) |
| **Metric** | Percentage of pool used (not request/token counts) |
| **Cross-product** | Video generation in Imagine drains Build quota same afternoon |
| **SuperGrok/X Premium+** | Flat-rate Build access |
| **xAI API** | Usage-based: $1/$2 per M tokens (grok-build-0.1) |

**Source**: OmniRoute #6844, xAI Build changelog

---

### 3.3 Verified Rotation Triggers

| Tool | Trigger | Classification |
|------|---------|----------------|
| **pi-grok-cli** | Exact: `OpenAI API error (402): 402 "Grok Build usage balance exhausted"` | Usage limit |
| **grok-telegram-bot** | ACP Internal `[-32603]` wrapping `Payment Required` / `usage balance exhausted` | Usage limit |
| **oh-my-pi** | HTTP 402 + `balance exhausted` wording **OR** 403 `run out of credits` / `personal-team-blocked:spending-limit` | Usage limit |
| **OmniRoute** | Live gRPC-web quota ≥95% **OR** upstream 402 exhaustion error | Reset-aware |

**Source**: `can1357/oh-my-pi#5723`, `#4913`, OmniRoute #7714

---

## PART 4: Omega Engine 8-Account Fleet Architecture

### 4.1 Fleet Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                    OMEGA HMC QUAD-FORGE                         │
│  Kali (oversight) → Grokster (advisory) → Fleet Orchestrator   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │ Account 1│    │ Account 2│ ...│ Account 8│
        │ GROK_HOME│    │ GROK_HOME│    │ GROK_HOME│
        │ ~/.grok- │    │ ~/.grok- │    │ ~/.grok- │
        │ fleet/1  │    │ fleet/2  │    │ fleet/8  │
        └────┬─────┘    └────┬─────┘    └────┬─────┘
             │               │               │
        ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
        │ grok    │     │ grok    │     │ grok    │
        │ agent   │     │ agent   │     │ agent   │
        │ stdio   │     │ stdio   │     │ stdio   │
        │ (ACP)   │     │ (ACP)   │     │ (ACP)   │
        └────┬────┘     └────┬────┘     └────┬─────┘
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                    ┌──────────────────┐
                    │  Fleet Router    │
                    │  (ACP Multiplex) │
                    │  - Quota monitor │
                    │  - Rotation logic│
                    │  - Session mgmt  │
                    └──────────────────┘
```

### 4.2 ACP Handshake Sequence (Per Account — Required)

```typescript
// Per xAI docs: https://docs.x.ai/build/cli/headless-scripting
1. spawn("grok", ["--no-auto-update", "agent", "stdio"], {stdio: ["pipe","pipe","pipe"]})
2. initialize({
    protocolVersion: 1,
    clientCapabilities: {
      fs: {readTextFile: true, writeTextFile: true},
      terminal: true
    }
  })
3. READ init.authMethods → select methodId:
   - "xai.api_key" if XAI_API_KEY set AND offered
   - "cached_token" otherwise
4. authenticate({methodId, _meta: {headless: true}})
5. session/new({cwd, mcpServers: []}) → sessionId
6. session/prompt({sessionId, prompt: [...]}) → stream session/update chunks
```

**Critical**: Multica PR #5285 review confirmed — **must** perform sequential handshake. Fake ACP in tests must reject unadvertised methods and all session ops before successful auth.

---

### 4.3 Quota Monitoring (Per Account)

```bash
# gRPC-web (works today, no ACP dependency)
curl -X POST https://grok.com/grok_api_v2.GrokBuildBilling/GetGrokCreditsConfig \
  -H "Content-Type: application/grpc-web+proto" \
  -H "Authorization: Bearer $(jq -r '."https://accounts.x.ai/sign-in".key' ~/.grok-fleet/N/auth.json)" \
  -H "X-XAI-Token-Auth: xai-grok-cli" \
  --data-binary @empty.protobuf

# Parse: credit_usage_percent, current_period.end, on_demand_cap, prepaid_balance
# Poll interval: 60s (billing data may be cached upstream)
```

---

### 4.4 Rotation Logic (Omega Fleet)

```python
async def rotate_on_exhaustion(account_id: int):
    # 1. Detect exact 402 exhaustion error from ACP stream
    if "Grok Build usage balance exhausted" in error_message:
        # 2. Mark account cooling (5 min, per pi-grok-cli)
        fleet.cooldown(account_id, 300)
        
        # 3. Select next account by quota rank (tightest remaining %)
        next_acct = fleet.select_by_quota_rank(exclude=cooldown_set)
        
        # 4. Swap GROK_HOME, restart ACP process
        await fleet.swap_account(next_acct)
        
        # 5. Replay interrupted prompt on new session
        await fleet.replay_prompt(next_acct, interrupted_prompt)
```

---

### 4.5 MCP Server Propagation

| Scope | Location | Priority |
|-------|----------|----------|
| Project | `.grok/config.toml` (repo, committed) | Highest for project |
| User | `~/.grok/config.toml` per account | Per-account defaults |
| Enterprise | `/etc/grok/managed_config.toml` | MDM/managed |

**Fleet Orchestrator**: Ensures each account's `GROK_HOME` has required MCP servers via `grok mcp doctor --json` pre-spawn health checks.

---

## PART 5: Complete Myth-Busting Summary

| Myth | Reality | Evidence |
|------|---------|----------|
| "Grok CLI doesn't support multi-account" | False | Official `grok login`/`logout`, per-model keys, `auth_provider_command`, 5 community tools |
| "Need browser for each switch" | False | `--device-auth`, `auth_provider_command`, headless `auth.json` swap |
| "No quota-aware rotation" | False | pi-grok-cli (exhaustion + quota rank), grok2api (QuotaWindow), OmniRoute (live gRPC-web) |
| "API keys auto-rotate" | False (session) / True (Mgmt API) | Session tokens ~7 days, re-login only; Mgmt API rotate endpoint + grace period |
| "ACP = MCP" | False | ACP = client↔agent session protocol; MCP = agent↔tool servers. Grok speaks both. |
| "STDIO MCP from API" | False | xAI API only accepts Streamable HTTP/SSE; STDIO requires wrapper |
| "Free tier includes Build" | False | SuperGrok/X Premium+ required for Grok Build CLI agent |

---

## PART 6: Recommendations for Omega Engine

### Phase 1 (Immediate — Sprint Guard & Distill)

1. **Implement `GrokFleetOrchestrator`** in `src/omega/integrations/grok_fleet.py`
2. **8 isolated directories**: `GROK_HOME=~/.grok-fleet/{1..8}`
3. **Per-account setup**: `grok login --device-auth` → capture `auth.json` → spawn `grok --no-auto-update agent stdio`
4. **ACP multiplexer** with quota monitor (gRPC-web poller, 60s interval)
5. **Rotation logic**: exact 402 exhaustion detection → 5min cooldown → quota-rank fallback → ACP process swap → prompt replay

### Phase 2 (Post V-1 Vault)

- **Omega-Vault integration** for encrypted `auth.json` storage
- **Management API key rotation** via xAI Management API (create→deploy→delete-old)
- **ACP `x.ai/billing` extension** when available (cleaner than gRPC-web)

### Dependencies (Blocking)

| Ticket | Blocks | Status |
|--------|--------|--------|
| **V-1** Omega-Vault MVP | Credential automation | P0 — explicit ticket |
| **C-10.5** Provider Fallback Chain | M7 compliance | P0 — in sprint |
| **C-11** Test Infrastructure | Property tests for rotation | P0 — in sprint |

---

## Sources (Verified)

| Category | Sources |
|----------|---------|
| **Official xAI Docs** | `docs.x.ai/build/cli/headless-scripting`, `build/features/mcp-servers`, `build/settings/reference`, `build/enterprise`, `management-api.x.ai` |
| **xAI Source** | `xai-org/grok-build`: `xai-grok-shell` (billing.rs, acp_session.rs, mcp.rs), `xai-grok-pager` (leader_bridge.rs) |
| **Community Tools** | pi-grok-cli PR #10, grok-telegram-bot v2.2.3+, ibi6/grok-switch, grok2api, grok3-api-free, coding_agent_account_manager |
| **Integrations** | OmniRoute #6844/#7714, Multica #5285, CodexBar grok.md, Pollinations rotate-genai-xai.sh, Sim Studio PR #5574 |
| **MCP/ACP** | `agentclientprotocol.com`, `modelcontextprotocol.io`, mcacp, prefrontalsys/mcacp, peer-agents-mcp |

---

**Report Status**: COMPLETE — Ready for Researcher Phase 1 synthesis merge
**Handoff**: `ho_00cb63f04efb` → completed
**Next**: Researcher integrates into Gap G1-15 deliverable for Fleet Orchestrator implementation