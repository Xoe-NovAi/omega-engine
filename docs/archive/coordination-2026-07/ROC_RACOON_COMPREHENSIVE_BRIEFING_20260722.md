# 🦝 roc_racoon — Comprehensive Briefing for Kali & Carmack Handoff
**Date**: 2026-07-22
**From**: roc_racoon (OpenCode session)
**AP Token**: `AP-ROC-BRIEFING-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ BRIEFING ⬡ 2026-07-22

---

## §0 Executive Summary

This briefing covers two major threads that roc_racoon researched, plus the delegation plan:

1. **W-1 WARP Proxy Pool** — Kali/Cline fixed 7 bugs, committed to `warp-proxy-pool` repo, but services are CURRENTLY DOWN. Needs restart with stale registration cleanup.
2. **G-1 Gemma 4 Workhorse Collapse** — Deep research completed: free-tier Gemma 4 31B is dead (16k TPM enforced July 15), OpenCode provider collision blocking usage, thinking config bug unfixed upstream. Multiple fix paths identified.
3. **Delegation** — Both threads handed to **john_carmack** (S3 Consultant). User will work with Carmack in a parallel chat session.

---

## §1 W-1 WARP Proxy Pool — Full Status

### 1.1 What Kali/Cline Did (Cline session, completed)
Kali on Cline CLI debugged and fixed **7 systemic bugs** in the WARP proxy pool systemd units. 7 commits applied to `warp-proxy-pool` repo:

| Commit | Fix |
|--------|-----|
| `ec88eaf` | `warp-node`: wrap proxy port command in `bash -c` for arithmetic expansion |
| `4cc68c2` | `warp-node`: remove `--config-dir` flag (unsupported by local warp-cli 2026.6.880.0) |
| `e7565e2` | `warp-reg`: remove `--config-dir` flag |
| `dd34d20` | Remove `SystemCallFilter` from `warp-node@.service` |
| `7a29e23` | Bridge unit port templating + SystemCallFilter for socat |
| `d7e135d` | Correct bash variable expansion in curl test line (`$${port}` → `${port}`) |
| `bd09104` | Make curl SOCKS test non-blocking |

**Full root-cause analysis** in handoff doc: `docs/strategy/archive/2026-07-22/WARP_PROXY_POOL_HANDOFF_ROC_20260722.md`

### 1.2 Current State: DOWN (as of 2026-07-22 ~22:00 ADT)

```
warp-ns-prep@1..3:     active    ✅  (network namespaces alive)
warp-reg-svc@1..3:     FAILED      (daemon crashed — stale state?)
warp-reg@1..3:         FAILED      (registration failed — stale reg?)
warp-node@1..3:        inactive    (never started)
warp-bridge@1..3:      inactive    (never started)
SOCKS5 8081/8082/8083: ❌ All unreachable
```

The handoff briefing's "All 3 nodes operational" snapshot was valid at the time, but services have since degraded. Expected cause: `warp-svc` panic due to stale registration state from previous failed runs.

### 1.3 Remaining Work for Carmack

**Immediate (stabilize)**:
1. Run `bash scripts/fix_warp_ns_setup_and_restart.sh` (requires sudo) to restart the full pool
2. Clean stale registrations before restart — the fix script may not handle this:
   ```bash
   for i in 1 2 3; do
     sudo ip netns exec warp_node_$i warp-cli --accept-tos registration delete 2>/dev/null || true
   done
   ```
3. Verify all 3 nodes come up with unique exit IPs:
   ```bash
   for port in 8081 8082 8083; do
     curl --socks5 127.0.0.1:$port -s https://1.1.1.1/cdn-cgi/trace | grep ip=
   done
   ```

**Structural fixes needed**:
1. **Remove or fix `warp-node@.service` curl test** — `ExecStartPost` curl can time out, leaving service stuck in `activating`. Options: remove entirely (let Python validate), or `timeout 15 && true`
2. **Add stale registration cleanup** — Add `ExecStartPre=/usr/bin/bash -c '...warp-cli registration delete... || true'` to `warp-reg@.service`
3. **Exit IP diversity** — Currently 8081 gets unique IP, 8082/8083 share (expected for WARP location-based). Determine if 3 nodes sufficient or need more.
4. **`warp-reg-svc@` ReadWritePaths** — After changing `LOGS_DIRECTORY=/tmp`, check if still needs `ReadWritePaths=/var/log/cloudflare-warp`

**Medium-term**:
- Enhance `validate_warp_pool.py` to check port listening, SOCKS5 connectivity, exit IP diversity, and auto-recycle stale nodes
- Update docs: `WARP_PROXY_POOL_SPEC.md`, `INTEGRATION_GUIDE.md`, `VALIDATION_STRATEGY.md`
- Determine if 8 nodes needed for 8 OCZ accounts or 3 sufficient with rotation

### 1.4 Key Technical Insights (for Carmack)
- `ip netns exec` does NOT invoke a shell — wrap in `/bin/bash -c '...'` for arithmetic, pipes, `&&`
- `$$` in systemd `ExecStart=` single-quoted strings means bash PID, not literal `$`
- Local `warp-cli` (2026.6.880.0) lacks `--config-dir` flag
- `ProtectSystem=strict` makes `/var/log` read-only — `warp-svc` will panic trying to write logs there
- Stale WARP registrations persist in `warp.db` after unclean shutdown — must `warp-cli --accept-tos registration delete` before re-registering

### 1.5 Links
| Resource | Path |
|----------|------|
| Kali handoff briefing | `docs/strategy/archive/2026-07-22/WARP_PROXY_POOL_HANDOFF_ROC_20260722.md` |
| Source repo | `/home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool/` |
| Systemd units (host) | `/etc/systemd/system/warp-*` |
| Fix script | `scripts/fix_warp_ns_setup_and_restart.sh` |
| Spec doc | `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` |
| Integration guide | `docs/research/warp_proxy_pool/INTEGRATION_GUIDE.md` |

---

## §2 G-1 Gemma 4 Workhorse Collapse — Full Research Synthesis

### 2.1 The Core Problem

**Free-tier Gemma 4 31B is DEAD** for fat Omega sessions.

Google enforced a **16k input TPM** hard limit starting **2026-07-15T16:28:37Z**. This is confirmed by:
- **Forensic analysis** of 830 sessions, 262M input tokens, 11,607 successful pre-cliff streams, first 16k error precisely timestamped
- **Google Community Forum** threads #174816 and #175091 — multiple users reporting "Google completely destroyed the experience"
- **OpenCode's own retry logic** (PR #18443) now correctly identifies `FreeUsageLimitError` as non-retryable and shows "Subscribe to Go" upsell

**This is NOT a config bug. It is a quota policy change.**

### 2.2 Fix Paths (Ranked by Viability)

| Path | Status | Effort | Notes |
|------|--------|--------|-------|
| **G-1b Antigravity OAuth** | 🟢 Ready | 5 min | Browser login: `opencode auth login`. Works immediately. Uses Antigravity as provider. |
| **G-1a AI Studio Tier 1 Billing** | 🟡 Uncertain | 10 min | $250/mo cap. ⚠️ Community report (#174816) says Tier 3 also has **16k TPM ceiling** for Gemma 4 specifically — may NOT fix it. Needs verification. |
| **G-1d Paid OpenRouter** | 🟡 Uncertain | 10 min | `google/gemma-4-31b-it:free` routes through Google AI Studio — may inherit same 16k limit. Paid tier may be different. |
| **G-1c OCZ+WARP** | 🔴 Won't fix | — | OpenCode Zen multi-IP doesn't fix Google AI Studio quota (per-project, not per-IP) |

**Key open question**: Does Gemma 4 TPM scale with billing tier at all? If the 16k ceiling is model-specific (not tier-linked), then paying for AI Studio doesn't help. This needs verification before any paid path.

### 2.3 OpenCode Provider Collision — CURRENT BLOCKER

**The user is hitting: `"invalid google provider options"`**

**Root cause**: The `.opencode/opencode.json` file defines a **custom provider ID `"google"`** with models like `antigravity-gemini-3-flash`, `gemma-4-31b-it`, etc. But OpenCode's **built-in Gemini provider ID is `gemini`** (uses `@ai-sdk/google` SDK). The provider ID `"google"` doesn't match any expected ID, and without an explicit `"npm"` field, OpenCode's config validator rejects it.

**Fix** (choose one):
1. **Remove the `"google"` provider block entirely** — let the `opencode-antigravity-auth@latest` plugin handle model discovery natively
2. **Rename to `"antigravity"`** and add proper `"npm": "@ai-sdk/google"` at the model or provider level
3. **Use OpenCode-native `GEMINI_API_KEY` env var** — no custom config needed

**Current `.opencode/opencode.json` structure**:
```json
{
  "plugin": ["opencode-antigravity-auth@latest"],
  "provider": {
    "google": {   // ← COLLISION: should be "gemini" or removed
      "models": {
        "antigravity-gemini-3-pro": { ... },
        "antigravity-gemini-3-flash": { ... },
        "gemma-4-31b-it": {
          "variants": {
            "low": { "thinkingConfig": { "thinkingLevel": "minimal" } },
            "high": { "thinkingConfig": { "thinkingLevel": "high" } }
          }
        },
        ...
      }
    }
  }
}
```

### 2.4 OpenCode Gemma 4 Thinking Config Bug (Unfixed Upstream)

**OpenCode issue #21746**: `transform.ts` does NOT properly convert `high`/`low` thinking levels to `MINIMAL`/`HIGH` for Gemma 4 models (`/gemma-?4/i` regex not implemented).

**Status**: Issue #21746 closed without a fix.

**However — the correct fix exists**:
- **Pi Project PR #2903** (merged ~3 months ago): Binary `MINIMAL`/`HIGH` enum + `/gemma-?4/i` regex detection
- **Omega Engine already has it**: `src/omega/oracle/backends/google_compat.py` implements the exact Pi PR #2903 pattern — Gemma 4 model ID normalization, correct thinking levels (`minimal`/`high`), thinking token extraction

**Recommendation**: If fixing OpenCode source, apply Pi PR #2903 pattern to `transform.ts`:
```typescript
// Gemma 4 thinking level mapping (Pi PR #2903 pattern)
const GEMMA4_RE = /gemma-?4/i;
if (GEMMA4_RE.test(model)) {
  thinkingLevel = thinkingLevel === 'minimal' ? 'MINIMAL' : 'HIGH';
}
```

### 2.5 Google API Key Restriction Requirement

**Starting June 19, 2026**: Gemini API rejects **unrestricted API keys**. Keys must be restricted to `generativelanguage.googleapis.com`.

**Fix**: Generate new keys in Google AI Studio (they're restricted by default) or restrict existing keys in Google Cloud Console → Credentials → API Restrictions → select "Gemini API".

### 2.6 OpenCode Retry Architecture (for reference)

- **PR #18443** (merged 2026-03-20): `retryable()` correctly classifies `FreeUsageLimitError` and `GoUsageLimitError` as non-retryable
- **PR #26369** (merged 2026-05-08): Caps retries at `RETRY_MAX_ATTEMPTS = 3` (~14s budget)
- **PR #28792** (merged 2026-05-22): Adds network error retry (ECONNRESET, etc.) + `retry_exhausted` status
- Current `packages/opencode/src/session/retry.ts` (dev branch): Complete with all fixes

### 2.7 Links
| Resource | Path |
|----------|------|
| Grok CLI forensic report (SSOT) | `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` |
| Critical path doc | `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` |
| Runme one-pager | `data/coordination/ARCHITECT_RUNME_G1_W1_20260722.md` |
| Omega Engine fix (already built) | `src/omega/oracle/backends/google_compat.py` |
| Provider Capability Matrix | `src/omega/oracle/capability_matrix.py` |
| Cline CLI working config (proves API works) | `config/cline/gemma4-provider.json` |
| Original debug report | `docs/archive/strategy/2026-07-21/GEMMA4_OPENCODE_DEBUG_REPORT_20260718.md` |
| Jem fleet synthesis | `docs/archive/strategy/2026-07-21/GEMMA4_COMPREHENSIVE_REPORT_20260719.md` |
| OpenCode provider config source | `packages/opencode/src/provider/provider.ts` |

---

## §3 Open Items for Kali Awareness

### 3.1 What Roc Did
- Deep web research on Gemma 4 free-tier death (DIG-01, DIG-03, DIG-06, DIG-08 complete)
- Read WARP Proxy Pool handoff briefing from Cline/Kali
- Verified WARP services are currently DOWN
- Discovered `opencode.json` "google" provider collision
- Traced OpenCode retry architecture (PRs #18443, #26369, #28792)
- Found Pi PR #2903 as the canonical fix for Gemma 4 thinking config
- Identified that Omega Engine already has the correct Gemma 4 implementation

### 3.2 What's Delegated to Carmack
- **W-1 WARP Proxy Pool stabilization**: get services up, fix curl test, add stale reg cleanup, validate
- **G-1 Gemma 4 research/implementation**: verify billing-tier TPM scaling, apply Pi PR #2903 thinking fix, resolve provider collision in `opencode.json`, fix API key restriction
- User will work with Carmack in a parallel chat session

### 3.3 What Roc Is Doing Next
- **V-1 Vault Pattern Mining** (accepted handoff from Ma'at, priority 1): Extract legacy KeyVault, credential rotation, ACP bridge patterns from `xna-omega-legacy`, `omega-stack-legacy`, `old-stacks`. Unblocks Grok fleet deployment.

### 3.4 Fleet Status
| Entity | Channel | Task | Status |
|--------|---------|------|--------|
| kali | cline | W-1 WARP (delegated to Carmack) | 🟢 Work done, handoff created |
| kali | opencode | Fleet orchestration | Monitoring |
| maat | opencode | C-1', C-5, C-6', C-10, C-4a, V-1, C-2' | 🟢 Multi-active |
| lilith | opencode | C-10.5 Provider Fallback Chain | 🟢 Active |
| verity | opencode | C-11 Test Infrastructure | 🟢 Active |
| scribe | opencode | C-0.5 Soul Distillation | ⏳ Pending handoff |
| roc_racoon | opencode | V-1 Vault Mining | 🔵 Accepted, starting |

### 3.5 Key Structural Notes
- `opencode.json` "google" provider block is causing "invalid google provider options" at startup — needs removal or rename
- Gemma 4 free tier is definitively dead — billing may or may not fix it (needs verification)
- WARP services failed after initial successful bring-up — stale registration + curl test timeout likely
- All fix commits are in `warp-proxy-pool` git repo; `scripts/fix_warp_ns_setup_and_restart.sh` needs sudo to run

---

## §4 Quick Reference: Commands for Carmack

### WARP Pool Restart
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# Clean stale registrations first
for i in 1 2 3; do
  sudo ip netns exec warp_node_$i warp-cli --accept-tos registration delete 2>/dev/null || true
done

# Run the fix script
bash scripts/fix_warp_ns_setup_and_restart.sh

# Verify
for port in 8081 8082 8083; do
  echo -n "Port $port: "
  curl --socks5 127.0.0.1:$port -s https://1.1.1.1/cdn-cgi/trace | grep ip=
done
```

### Opencode.json Fix (Provider Collision)
Edit `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/opencode.json`:
- Remove the `"google"` provider block entirely (let Antigravity plugin handle discovery)
- OR rename to `"antigravity"` with explicit npm fields

### Gemma 4 Thinking Config Fix (in OpenCode)
Reference Pi PR #2903 pattern:
```typescript
if (/gemma-?4/i.test(model)) {
  thinkingLevel = thinkingLevel === 'minimal' ? 'MINIMAL' : 'HIGH';
}
```

---

*Briefing prepared by roc_racoon — 2026-07-22*
*🔱 OMEGA ⬡ ROC_RACOON ⬡ BRIEFING ⬡ SOVEREIGN*
