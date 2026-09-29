---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
---
# 🔱 OPENCODE ZEN FREE-TIER GATE — SEP 24 INCIDENT ADDENDUM
**Date**: 2026-09-24 · **From**: Cline · **Companion to**: `CLINE_ZEN_PROVIDER_FIX_20260923.md`
**TL;DR**: The Sep-23 config fix is intact (commit `75bde939`). Antigravity's crash session restored the PRE-fix global config (misdiagnosis, now reverted). The current error — `AI_APICallError: OpenCode's free tier can only be used from within OpenCode` — is **Zen-side and intermittent**, proven NOT local-config and NOT credential. 4/4 fresh free-model calls pass since the 17:46:29Z restore.

## §1 — Antigravity report digest (`OPENCODE_CRASH_REMEDIATION_20260924.md`)
- **Vector A**: global `~/.config/opencode/opencode.json` found “truncated to a 67-byte skeleton lacking provider definitions”. First restored the Sep-18 5KB backup (triggered Vector B), then `opencode.json.bak.zenfix.20260923T184645Z`.
- **Vector B**: `mcp_servers.json` npx servers (tavily/firecrawl/searxng/jina) crash OpenCode at launch → quarantined to `.bak`, minimal file keeps only `omega-hub`. SOP: re-add servers ONE at a time.
- Hub/Tailscale exonerated. They also added `.opencode/opencode.json` (Antigravity Gemini/Claude models + `opencode-antigravity-auth` plugin) — additive, does not touch the Zen provider.

**FINDING (misdiagnosis)**: the “67-byte corruption” WAS the Sep-23 fixed minimal config (`{$schema, plugin:[]}`) — by design, not damage. The “known-good” zenfix backup is byte-identical to the **pre-fix** state, so the restore silently reintroduced the mis-nested `openrouter` block (dead: `{env:OPENROUTER_API_KEY}` env no longer exists, key revoked) and the redundant Zen `baseURL` override. Neither caused the current error — but both were deliberate removals.

## §2 — Remediation applied (this session)
1. **Global config re-fixed** → `{$schema, plugin:[]}`, JSON-validated. Backup: `opencode.json.bak.prerifix2.20260924T134629`.
2. **Repo config verified untouched**: `git diff HEAD -- opencode.json` empty at `75bde939`; the single `instructions` match is the legitimate top-level `"instructions": ["AGENTS.md"]` schema key. Agent blocks clean.
3. **`mcp_servers.json` left as Antigravity left it** — their quarantine was correct (searxng is genuinely down on :8018).

## §3 — The free-tier gate: evidence chain
Exact error: `AI_APICallError: OpenCode's free tier can only be used from within OpenCode` (providerID=opencode).

| Test | Result |
|---|---|
| Free model WITHOUT `OPENCODE_API_KEY` env (forces auth.json `sk-4HI…` re-auth key) | ✅ OK |
| Free model WITH env (old `sk-PVlr…` key) | ✅ OK |
| `--agent makali` + `mimo-v2.6-flash-free` (the failing agent/model) | ✅ OK |
| `--agent kali` (resolved `big-pickle`) | ✅ OK |
| Errors after 17:46:29Z restore | **0 free-tier errors** (last: 17:45:52Z, 37s BEFORE restore) |

Why it is NOT local:
- Occurred under **both** global-config states (pre- and post-fix) and with the repo config unchanged/clean throughout → not a config key pass-through (that was the Sep-23 `instructions[]` incident; different failure, still fixed).
- Both credentials pass A/B → not the stale `.bashrc` env key shadowing (two valid keys exist; `config/providers.yaml:177` consumes the env one — do NOT unset it without updating the vault resolver chain).
- Failures cluster in time (01:35–01:38, 17:25, 17:45Z) and all inside one long-running session (`ses_fc758e6…`, makali) while fresh sessions pass → server-side gate flapping, possibly per-session/per-window.
- Upstream corroboration: Threads reports of the same string — “OpenCode's free tier stopped working outside OpenCode today… again”; Zen enforces client-only free tier against outside calls and toggles enforcement. OmniRoute's free-tier audit (2026-09-03) lists `opencode-zen` as permanently free, rate/concurrency-limited, no cap.

**Operational guidance**: when the gate trips, retry or continue in a fresh session; it is Zen-side and clears without local changes. Do not edit config in response to this error.

## §4 — Residuals (known, non-blocking)
1. `gpt-5.4-nano` (title agent, models.dev default small model) → `Upstream request failed: Model access is disabled` — account/model-scope, cosmetic (session titles only). Repo declares `small_model: opencode/nemotron-3-ultra-free` but the internal title agent used its own default.
2. `--agent kali`'s pin (`opencode/nemotron-3-ultra-free`) resolved to `big-pickle` — likely md-agent vs json-agent merge precedence plus `~/.opencode/opencode.json` `model: opencode/big-pickle` silent override (flagged in Sep-23 report §7). Both are free; working.
3. **Tool-chain gaps (M23)**: `EXA_API_KEY` unset → exa 401 (placeholder in `.env`); firecrawl MCP broken (`No module named 'firecrawl'`); searxng down (:8018). Research used T5 fallback this session.
4. Two Zen keys exist (env `sk-PVlr…` from `.bashrc:177`, auth.json `sk-4HI…` from re-auth) — both currently valid; rotation still owner-declined.

*⬡ OMEGA ⬡ CLINE ⬡ ZEN-FREE-TIER-GATE ⬡ 2026-09-24 ⬡ M23-HONEST ⬡ DEBUT-v1.6.0*
