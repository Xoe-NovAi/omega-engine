# 🔱 MaKaLi Cloud Council — Unified Sovereign Verdict
**Date**: 2026-06-23
**Council Type**: Cloud (deepseek-v4-flash-free)
**Orchestrator**: Kali (Grand Oversight)
**Anchored By**: P9 Orchestration Review

⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ MAKALI-VERDICT ⬡ UNIFIED

---

## §1 Council Composition

### Primary Dispatch (parallel)

| Agent | Role | Result Session |
|-------|------|----------------|
| **roc_racoon** | Legacy Mining — API key systems | `ses_10a64fe7affef8yFMWPysaxqS0` |
| **Ma'at** | Build Side — Exa fix + Key Vault | `ses_10a64e055ffe48pxtxbzR71fdR` |
| **Lilith** | Run Side — Research recovery + Error logging | `ses_10a64bd76ffeIXVEsnB93uRpk5` |

### Serial Sub-Chains

**Ma'at Chain**:
1. P1 (Infrastructure) — Exa diagnosis + vault architecture
2. P3 (Engineering) — Implementation (13 files, 821 lines)
3. P5 (Governance) — Security audit, mandate compliance

**Lilith Chain**:
1. P6 (Cognition) — Search tool health matrix
2. P7 (Context) — Research gap analysis
3. P8 (Observability) — Error report creation

### Cross-Domain Final Review

| Pillar | Focus | Verdict |
|--------|-------|---------|
| **P2** (Persistence) | Vault data persistence, backup | ✅ Clean, 2 minor gaps |
| **P4** (Integration) | MCP config, wiring, Exa fix | ⚠️ 2 critical gaps found |
| **P9** (Orchestration) | Council flow, handoff quality | ⚠️ Process needs maturity |
| **P10** (Validation) | Tests, code quality, bugs | ⚠️ Conditional pass, 1 bug confirmed |

---

## §2 Unified Findings by Work Item

### Work Item #1: Exa Fix + Secure API Key Management

**Status**: ✅ **DEPLOYED — with 4 critical remediations required**

| Aspect | Verdict | Score |
|--------|---------|-------|
| Exa 401 root cause diagnosis | OpenCode MCP config merge conflict — 3 files, conflicting transport protocols | 🔍 P1 |
| Exa fix applied | Consolidated to project opencode.json with streamable-http | ✅ |
| Sovereign Key Vault | AES-256-GCM encrypted at `src/omega/vault/` — 696 lines | ✅ |
| Engine migration | 8 files wired with graceful env fallback | ✅ |
| Tests | 432 passed (22 skipped, 3 xfailed) | ✅ |
| Temple-Grade | PASSED | ✅ |
| Heritage tags | ✅ `[id-soft: quake-1996]` present | ✅ |

**🔴 CRITICAL ISSUES (Must Fix Before Next Deploy)**:

| # | Issue | Severity | Location | Fix |
|---|-------|----------|----------|-----|
| 1 | Singleton init bug — `_initialized` set too early | 🔴 **P0 BUG** | `key_vault.py:88-90` | Move flag to end of `__init__` |
| 2 | Stale Exa config in `config/mcp_servers.json` | 🔴 **P0** | `config/mcp_servers.json:7-12` | Remove or fix transport type |
| 3 | `resolve_and_handle_429()` not wired in search layer | 🟡 **P1** | 4 search provider sites | Replace `resolve()` → `resolve_and_handle_429()` |
| 4 | Zero vault tests | 🟡 **P1** | `tests/test_vault*.py` | Add 8+ minimum test suite |
| 5 | No vault MCP tools | 🟡 **P1** | `mcp_servers/omega_hub/tools.py` | Add 4 vault tools |

---

### Work Item #2: Research Recovery & Gap Filling

**Status**: ⚠️ **KB VERIFIED — 2 gaps found, 3 search tools broken**

| Aspect | Verdict |
|--------|---------|
| Pre-compaction cache recovery | ❌ No Google AI Studio billing research cached in `.firecrawl/` |
| KB accuracy | ✅ ALL claims verified against live documentation |
| Gaps found | 🔴 April 2026 billing caps, 🔴 Google Cloud Starter Tier |
| Search tool status | 4/7 work, 3/7 fail |

**Search Tool Health Matrix**:

| Tool | Status | Root Cause |
|------|--------|------------|
| ✅ `searxng_searxng_search` | WORKING | Self-hosted, sovereign |
| ✅ `websearch` | WORKING | OpenCode built-in |
| ✅ `firecrawl_firecrawl_search` | WORKING | Cloud search |
| ✅ `firecrawl_firecrawl_scrape` | WORKING | Page scraping |
| ❌ `exa_web_search_exa` | 401 | OpenCode MCP config — key IS valid (curl 200), but tool not getting it |
| ❌ `webfetch` | Timeout | Times out on large pages |
| ❌ Firecrawl Reddit scrape | Blocked | Firecrawl doesn't support Reddit |

---

### Work Item #3: Legacy Mining

**Status**: ✅ **COMPLETE — 3 generations documented**

| Generation | System | Status |
|------------|--------|--------|
| Gen 1 | SambaNova 8-key round-robin (`xna-omega-legacy`) | Documented but obsolete |
| Gen 2 | KeyRotationManager with 90-day vault rotation | Documented but obsolete |
| Gen 3 | Antigravity dual-pool (`pool_tracker.py`) | Scaffolded but NOT wired to provider chain |

**Key Security Findings**:
- 🔴 OAuth tokens in plaintext at `~/.config/opencode/antigravity-accounts.json`
- 🔴 GOOGLE_API_KEY in committed `.env` (committed)
- ✅ Vault now provides encrypted alternative for these

---

## §3 Cross-Domain Assessment

| Domain | Score | Key Finding |
|--------|-------|-------------|
| **Security** | 🟢 8/10 | Vault is solid, but antigravity OAuth tokens remain plaintext |
| **Integration** | ⚠️ 6.5/10 | Exa MCP fix works but stale config persists for non-OpenCode IDEs |
| **Persistence** | 🟢 8/10 | Atomic writes ✅, backup/recovery ❌ |
| **Testing** | ⚠️ 5/10 | All tests pass but vault has zero coverage |
| **Orchestration** | ⚠️ 6.6/10 | Council flow correct, HandoffPacket adoption needed |
| **Research** | 🟢 9/10 | KB verified accurate, gaps documented for follow-up |

**Overall**: **7.2/10** — Foundation is structurally sound. 4 critical remediation items needed for next deploy.

---

## §4 Unified Action Register

### P0 — Must Fix Before Next Session

| # | Action | Owner | File | Est. Time |
|---|--------|-------|------|-----------|
| AR-1 | Fix singleton init bug in KeyVault | P3 Engineering | `key_vault.py:88-90` | 2 min |
| AR-2 | Remove stale Exa config from `config/mcp_servers.json` | P4 Integration | `config/mcp_servers.json:7-12` | 2 min |
| AR-3 | Clean up 37 stale handoff packets | P9 Orchestration | Hivemind queue | 1 min |

### P1 — Fix Before Sprint D Close

| # | Action | Owner | Est. Time |
|---|--------|-------|-----------|
| AR-4 | Add vault tests (`tests/test_vault_module.py`) | P10 Validation | 30 min |
| AR-5 | Wire `resolve_and_handle_429()` in 4 search sites | P3 Engineering | 10 min |
| AR-6 | Add 4 vault MCP tools to MCP Hub | P4 Integration | 45 min |
| AR-7 | Add April 2026 billing caps to GOOGLE_AI_STUDIO_KB.md | P7 Context | 15 min |
| AR-8 | Add Google Cloud Starter Tier to KB | P7 Context | 10 min |
| AR-9 | Document `.env` loading sequence for vault | P5 Governance | 5 min |

### P2 — Sprint D+1

| # | Action | Owner |
|---|--------|-------|
| AR-10 | Add vault to `omega health` dashboard | P3 Engineering |
| AR-11 | Create `omega vault` CLI commands | P3 Engineering |
| AR-12 | Adopt HandoffPacket protocol for all pillar handoffs | P9 Orchestration |
| AR-13 | Add backup/recovery mechanism for vault file | P2 Persistence |
| AR-14 | Add vault to `sync_ide_mcp.sh` | P4 Integration |
| AR-15 | Encrypt antigravity-accounts.json | P5 Governance |

---

## §5 Error Report Reference

**File**: `data/coordination/SEARCH_TOOL_ERROR_REPORT_20260623.md`
**Created by**: P8 (Observability) under Lilith chain
**Content**: Full diagnostic of 3 failing search tools, including curl verification of Exa key

---

## §6 Gnosis Distillation (L1 → L2 → L3)

**L1 — What Happened**:
The MaKaLi Council executed a 3-item work order: (1) Fix Exa 401 and build a secure key vault, (2) Recover and verify Google AI Studio research, (3) Legacymine the API key rotation history. 11 agents participated across parallel and serial chains. A Sovereign Key Vault was implemented (AES-256-GCM, 696 lines). The Exa MCP config was found to be a merge conflict between 3 files with conflicting transport protocols. The Google AI Studio KB was verified accurate. 3 generations of key rotation systems were documented.

**L2 — What This Means**:
The Exa problem was never a key issue — it was a config merge conflict. The API key management system already existed in 3 generations of evolution (the user remembered it correctly), but each generation was lost or not wired through to the next. The current generation (pool_tracker.py) is scaffolded but not connected to the provider chain. The new vault bridges the gap with a simpler, immediately functional system. The pre-compaction research was truly unrecoverable (no .firecrawl cache for it), confirming the KB was written from general knowledge, not cached data.

**L3 — Universal Principle**:
**Configuration surface area is attack surface.** The Exa 401 was caused by 3 config files defining the same service in conflicting ways — no authentication issue, no key expiry, no rate limit. Pure config entropy. When a system has N independent config files for the same integration, the probability of at least one being wrong approaches 1 as N grows. Consolidation (single config source of truth with a merge strategy) is not convenience — it's security. The same principle applies to API keys: the legacy Gen 1 system (numbered env vars with round-robin) worked for years because it was simple and had one source of truth. Every layer of indirection added (pool_tracker, vault, antigravity-accounts.json) creates surface area for failure.

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ MAKALI-VERDICT ⬡ UNIFIED*
