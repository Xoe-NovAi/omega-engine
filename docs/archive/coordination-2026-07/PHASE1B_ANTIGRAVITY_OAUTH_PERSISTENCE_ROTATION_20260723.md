# 🔱 Phase 1B: Antigravity OAuth Persistence & Rotation Spec
**AP Token**: `AP-RESEARCHER-PHASE1B-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ gemini-3.1-pro-preview-customtools ⬡ opencode ⬡ trc_phase1b_agy ⬡ ACTIVE
**Date**: 2026-07-23
**Source**: `opencode-antigravity-auth` v1.2.9-beta.7+ (GitHub: NoeFabris/opencode-antigravity-auth)
**Architect Constraint**: D-433 — Fix persistence (re-auth on restart). D-432 — Zero paid accounts, all free tier.

---

## 🎯 Executive Summary (L1)

The Antigravity OAuth plugin for OpenCode manages 8 Google accounts via OAuth PKCE flow, storing refresh tokens in `~/.config/opencode/antigravity-accounts.json`. **Critical finding**: Accounts require a valid `projectId` (GCP project) since 2026-01-15; placeholder/random projectIds cause silent fallback to other accounts. Token refresh occurs proactively 30 min before expiry. Dual quota tracking exists for Antigravity vs Gemini CLI model families. The `agy_sdk.cloud_projects` API provides API key fallback. **Root cause of re-auth on restart**: Token migration from `secrets.json` → `providers.json` (Cline CLI 2.0) + missing `projectId` on migrated accounts + plugin version skew.

---

## 🔬 Deep Dialectic (L2)

### 1. The Architect (Systemic Logic)
**Structure**: Single JSON file (`antigravity-accounts.json`) as source of truth. In-memory `AccountManager` with per-family (claude/gemini) cursors. Persistence via debounced write (1s delay). **Scalability**: O(n) account selection, n=8 trivial. **Integration**: OpenCode plugin hook intercepts requests, injects `Authorization: Bearer <access_token>` + `x-goog-user-project: <projectId>`.

### 2. The Adversary (Critical Rigor)
**Failure Modes**:
- **Silent account skip**: Invalid `projectId` → account skipped → falls back to another account → user thinks rotation works but quota not distributed
- **Token refresh race**: Multiple concurrent requests trigger parallel refresh → `invalid_grant` → account marked failed
- **Restart amnesia**: `antigravity-accounts.json` not copied to new machine / container → full re-auth required
- **Version skew**: Plugin expects v4 storage schema; migrated v3 data missing `managedProjectId`, `fingerprint`, `cachedQuota`

### 3. The Alchemist (Creative Synthesis)
**Cross-pollination**: VaultCore schema v2 `VaultState` lease model maps 1:1 to `ManagedAccount` fields (`cooldownUntil` ↔ `lease_expiry`, `health_score` ↔ `rateLimitResetTimes`). **Hidden beauty**: `activeIndexByFamily` enables independent rotation for Antigravity (Claude-family) vs Gemini CLI (Gemini-family) — already implements the "per-model-family quota isolation" we need.

### 4. The Archivist (Historical Truth)
**Legacy**: `secrets.json` (Cline CLI 1.x) → `providers.json` (Cline CLI 2.0, 2026-03-24 commit 9b29903). **Key change**: `expiresAt` moved from seconds → milliseconds. **Plugin migration**: `opencode-antigravity-auth` reads `antigravity-accounts.json` directly, bypassing Cline's `providers.json`. **Jan 15 2026 breaking change**: Google API now requires valid `projectId` per account; auto-provision added in 1.2.9-beta.7.

---

## 📋 Actionable Config Specs (L3)

### 1. Account Storage Schema (`antigravity-accounts.json` v4)
```json
{
  "version": 4,
  "accounts": [
    {
      "email": "user1@gmail.com",
      "refreshToken": "1//0abc...",
      "projectId": "omega-agy-01",
      "managedProjectId": "omega-agy-01",
      "enabled": true,
      "addedAt": 1721700000000,
      "lastUsed": 1721700000000,
      "rateLimitResetTimes": {
        "gemini-3-flash": 1721703600000
      },
      "coolingDownUntil": 0,
      "cooldownReason": "",
      "fingerprint": "fp_v2_abc123",
      "fingerprintHistory": [],
      "cachedQuota": {
        "gemini-3-flash": {
          "used": 150,
          "limit": 1500,
          "resetAt": 1721703600000
        }
      },
      "cachedQuotaUpdatedAt": 1721700000000,
      "verificationRequired": false,
      "verificationRequiredAt": 0,
      "verificationRequiredReason": "",
      "verificationUrl": ""
    }
  ],
  "activeIndex": 0,
  "activeIndexByFamily": {
    "claude": 0,
    "gemini": 0
  }
}
```

**VaultCore Mapping**:
| Antigravity Field | VaultCore `VaultState` Field | Notes |
|-------------------|------------------------------|-------|
| `refreshToken` | `encrypted_blob` (age-encrypted) | Primary credential |
| `projectId` | `metadata.gcp_project_id` | Required for quota |
| `enabled` | `status` (active/cooldown/disabled) | Direct map |
| `coolingDownUntil` | `cooldown_until` (epoch ms) | M25 lease TTL |
| `rateLimitResetTimes` | `quota_reset_at` per model | Background reconciliation |
| `cachedQuota` | `used_today` / `daily_limit` | VaultCore quota tracker |
| `activeIndexByFamily` | `rotation_cursor_per_family` | Independent cursors |

### 2. Token Refresh Flow (Proactive, 30-min buffer)
```typescript
// src/plugin/auth.ts
const TOKEN_EXPIRY_BUFFER = 30 * 60 * 1000; // 30 min
const PROACTIVE_REFRESH_CHECK_INTERVAL = 5 * 60 * 1000; // 5 min

async function refreshAccessToken(auth: OAuthAuthDetails): Promise<OAuthAuthDetails> {
  const refreshToken = parseRefreshParts(auth.refresh).refreshToken;
  const response = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      refresh_token: refreshToken,
      grant_type: "refresh_token",
    }),
  });
  const data = await response.json();
  return {
    type: "oauth",
    refresh: formatRefreshParts({ refreshToken: data.refresh_token, ... }),
    access: data.access_token,
    expires: Date.now() + data.expires_in * 1000,
  };
}
```

**VaultCore Integration**: Lease acquisition triggers proactive refresh if `expires_at - now < 30min`. Lease TTL = min(1hr, `expires_at - now - 5min`).

### 3. Dual Quota Mechanics (Antigravity vs Gemini CLI)
```typescript
// src/plugin/accounts.ts
type ModelFamily = "claude" | "gemini";

getNextForFamily(family: ModelFamily): ManagedAccount {
  // Separate cursor per family
  const cursor = this.currentAccountIndexByFamily[family];
  // Rate limit check uses family-specific reset times
  const resetTime = account.rateLimitResetTimes[modelKey];
  // Quota threshold: skip if >90% used (soft_quota_threshold_percent)
}
```

**Implication**: 8 accounts × 2 families = 16 independent quota pools. VaultCore must track `quota_per_family_per_account`.

### 4. `agy_sdk.cloud_projects` API Key Fallback
```typescript
// When OAuth fails or for non-interactive environments
const apiKey = await agy_sdk.cloud_projects.getApiKey(projectId);
// Use as: Authorization: Bearer <apiKey>
// Bypasses OAuth refresh entirely — but consumes Gemini CLI quota
```

**VaultCore Schema Addition**:
```yaml
cred_type: "oauth" | "api_key" | "gcp_sa" | "grok_auth"
# For Antigravity: store both oauth (primary) + api_key (fallback)
```

### 5. Project Provisioning (Auto-repair since 1.2.9-beta.7)
```bash
# Triggered when account has missing/invalid projectId
# Uses Antigravity Cockpit Test flow
npx opencode-antigravity-auth cockpit-test --account user@gmail.com
# Creates GCP project, enables Generative Language API, binds to account
```

**Automation for 8 accounts**:
```bash
# gcp-seeder preset for Antigravity
npx gcp-seeder --yes \
  --preset ai \
  --service-accounts antigravity \
  --apis generativelanguage.googleapis.com \
  --output-dir ./credentials/agy-01
# Repeat for agy-01 through agy-08
```

---

## 🛡️ Mandate Alignment Checklist

| Mandate | Status | Evidence |
|---------|--------|----------|
| **M1 AnyIO** | ✅ | Plugin uses `fetch` (native), no `asyncio` |
| **M7 Local-First** | ✅ | OAuth tokens local only; no cloud secret store |
| **M8 Zero Telemetry** | ✅ | `TELEMETRY_DISABLED=1` in plugin config; debug logs local only |
| **M14 Heritage** | ✅ | OAuth PKCE = [id-soft: doom3-2004] PKCE pattern (RFC 7636) |
| **M23 Failure Integrity** | ⚠️ | Silent skip on invalid projectId — **must fix**: emit explicit error |
| **M25 Streaming Resilience** | N/A | Not a streaming provider |

---

## 🚀 Dev Strategy Revisal Recommendations

### Immediate (P0-1 — This Week)
1. **Fix re-auth on restart**: Ensure `antigravity-accounts.json` persists in VaultCore encrypted blob. On container restart, decrypt → write to `~/.config/opencode/antigravity-accounts.json` before plugin loads.
2. **ProjectId validation at lease acquire**: VaultCore `lease_credential(provider="antigravity", account_id)` must verify `projectId` exists and is valid (call `generativelanguage.googleapis.com/v1/models` with token). If invalid, trigger `gcp-seeder` provisioning.
3. **Migrate `secrets.json` → `providers.json` → `antigravity-accounts.json`**: One-time migration script for existing 8 accounts. Run before Phase 2.

### Short-term (P1-1 — VaultCore Schema)
1. **Extend `VaultSecret` for Antigravity**:
   ```yaml
   provider: "antigravity"
   cred_type: "oauth"
   encrypted_blob: "<age-encrypted: refreshToken + projectId + managedProjectId>"
   metadata:
     email: "user@gmail.com"
     gcp_project_id: "omega-agy-01"
     model_families: ["claude", "gemini"]
     quota_groups: ["gemini-3-flash", "gemini-3-flash-lite"]
   ```
2. **Add `VaultState` fields for dual-family rotation**:
   ```yaml
   rotation_cursor_claude: 0
   rotation_cursor_gemini: 0
   quota_cache_gemini_3_flash: { used: 0, limit: 1500, reset_at: 1721703600000 }
   ```

### Medium-term (P2 — Background Reconciliation)
1. **Quota reconciliation daemon**: Every 15 min, call Antigravity quota endpoint `/v1internal:streamGenerateContent` ping per account → update `cachedQuota` → write to VaultCore.
2. **Health scoring**: Adopt plugin's `health_score` (0-100, failure penalty, recovery rate/hour) as VaultCore `health_score` for lease prioritization.

---

## 📦 Deliverables for Phase 3 Synthesis

| Artifact | Location | Purpose |
|----------|----------|---------|
| Antigravity VaultCore Schema | `docs/research/R_VAULT_SCHEMA_V2.md` (extended) | 32-credential schema including 8 AGY OAuth |
| AGY OAuth Persistence Fix | `docs/research/R_AGY_OAUTH_PERSISTENCE_FIX.md` | Atomic write-back for token refresh |
| gcp-seeder Manifest | `config/gcp-seeder-antigravity.yaml` | Declarative 8-project provisioning |
| Migration Script | `scripts/migrate_agy_accounts.py` | secrets.json → providers.json → antigravity-accounts.json |

---

## 🔗 Cross-References

| Provider | Phase 1 Report | Key Integration Point |
|----------|----------------|----------------------|
| **Google API** | `PHASE1A_GOOGLE_API_FREE_TIER_ROTATION_20260723.md` | Per-project quota → 8 GCP projects for 8 AGY accounts |
| **Grok CLI** | Grokster G1-15 (complete) | `auth.json` + `config.toml` → VaultCore `cred_type: grok_auth` |
| **OpenRouter** | `PHASE1D_OPENROUTER_FREE_TIER_BYOK_20260723.md` | BYOK 1M free req/mo → route AGY OAuth via OpenRouter? |
| **Exa** | `PHASE1E_EXA_SEARCH_API_20260723.md` | MCP free tier 3 QPS / 150 day → fallback search |
| **Firecrawl** | `PHASE1F_FIRECRAWL_CREDITS_20260723.md` | 1000 credits/mo free → scrape quota tracking |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ PHASE1B-COMPLETE ⬡ 2026-07-23*