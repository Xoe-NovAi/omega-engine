# 🔱 Phase 1A Research Report: Google API (Gemini) Free-Tier Rotation Spec
**AP Token**: `AP-PHASE1A-GOOGLE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ gemini-3.1-pro-preview-customtools ⬡ opencode ⬡ trc_phase1a_google ⬡ ACTIVE

**Date**: 2026-07-23
**Scope**: 8 Google API keys across 8 GCP projects (free tier only, zero paid accounts per Architect D-432)
**Sources**: Google AI for Developers rate limits docs (2026-07-20), Yingtu AI analysis (2026-04-25), AI Free API blog (2026-01-27), LaoZhang AI guide (2026-02-02), gcp-seeder npm package (v0.4.0 2026-07-12)

---

## Executive Summary (L1)

Google Gemini API free tier operates on **per-project quotas**, not per-key. Eight API keys require **eight distinct GCP projects**. The `gcp-seeder` CLI automates project provisioning with service accounts. Free tier limits (as of July 2026): **Gemini 3 Flash = 10 RPM / 1,500 RPD / 250k TPM**; **Gemini 3.1 Flash-Lite = 15 RPM / 1,000 RPD / 250k TPM**. Daily quotas reset at **midnight Pacific Time**. Cloud Monitoring API requires a service account with `monitoring.viewer` role for quota telemetry.

---

## Detailed Findings (L2)

### 1. Free Tier Per-Project Quota Limits (2026-07)

| Model | RPM | TPM | RPD | Context Window | Free Tier Status |
|-------|-----|-----|-----|----------------|------------------|
| **Gemini 3 Flash** | 10 | 250,000 | 1,500 | 1M tokens | ✅ Free |
| **Gemini 3.1 Flash-Lite** | 15 | 250,000 | 1,000 | 1M tokens | ✅ Free |
| **Gemini 2.5 Flash** | 10 | 250,000 | 1,500 | 1M tokens | ✅ Free |
| **Gemini 2.5 Pro** | 5 | 150,000 | 50 | 1M tokens | ⚠️ Limited |
| **Gemini 2.0 Flash** | 15 | 1,000,000 | 1,500 | 1M tokens | ✅ Free |
| **Gemma 2 (27B)** | 15 | 1,000,000 | 1,500 | 8K tokens | ✅ Free |

**Critical**: Pro models (2.5 Pro, 3.1 Pro Preview) are **paid-only** as of April 2026. Free tier = Flash/Flash-Lite only.

**Quota Dimensions** (all enforced independently):
- **RPM**: Requests per minute (rolling 60s window)
- **TPM**: Input tokens per minute (rolling 60s window)
- **RPD**: Requests per day (resets **midnight Pacific Time**)

> "Rate limits are applied per project, not per API key. Multiple keys in one project share the same quota pool." — Google AI for Developers, 2026-07-20

### 2. GCP Project Provisioning: `gcp-seeder` Automation

**Tool**: `npx gcp-seeder` (v0.4.0, 2026-07-12, by Comradery64)

**One-liner for 8 projects**:
```bash
for i in {1..8}; do
  npx gcp-seeder --yes \
    --name "omega-gemini-${i}" \
    --preset ai \
    --service-account \
    --output-dir ./credentials/gemini-${i} \
    --ttl 365d
done
```

**What `--preset ai` enables**:
- `generativelanguage.googleapis.com` (Gemini API)
- `aiplatform.googleapis.com` (Vertex AI, optional)
- `cloudresourcemanager.googleapis.com`
- `serviceusage.googleapis.com`
- `iam.googleapis.com`

**Output per project** (`./credentials/gemini-{1..8}/`):
- `service-account.json` — Service account key (for ADC / VaultCore)
- `client_secret.json` — OAuth client (for Antigravity plugin, if needed)
- Project labels: `seeded-by=gcp-seeder`, `seeded-at=<timestamp>`, `expires=<365d>`

**Idempotency**: Re-running with same `--name` reuses existing project + SA (no duplicate keys). Declarative `gcp-seeder.yaml` manifest supported for GitOps.

**MCP Server**: `gcp-seeder` exposes `gcp_seed`, `gcp_audit`, `gcp_sweep`, `gcp_destroy`, `gcp_rotate` as MCP tools for agent-driven lifecycle.

### 3. Service Account for Quota Monitoring (Cloud Monitoring API)

**Minimal IAM Roles**:
```yaml
roles:
  - monitoring.viewer                    # Read metrics, dashboards, alerting policies
  - serviceusage.serviceUsageConsumer    # Enable/disable APIs (for gcp-seeder)
  - resourcemanager.projects.get         # Read project metadata
```

**Key Metrics to Poll** (via `projects.timeSeries.list`):
| Metric | Description | Use for Rotation |
|--------|-------------|------------------|
| `serviceruntime.googleapis.com/api/request_count` | Total requests | RPD tracking |
| `serviceruntime.googleapis.com/api/request_latencies` | Latency distribution | Health check |
| `serviceruntime.googleapis.com/quota/allocation/usage` | Quota consumption % | **Primary rotation trigger** |
| `serviceruntime.googleapis.com/quota/limit` | Current quota limit | Capacity planning |

**Polling Interval**: 60s (aligns with `quota_refresh_interval_minutes: 15` in Antigravity plugin — but we need tighter for rotation fabric).

**Authentication**: Service account key (`service-account.json`) → ADC → `GOOGLE_APPLICATION_CREDENTIALS` env var.

### 4. Quota Reset Schedule

| Reset Type | Schedule | Timezone | Notes |
|------------|----------|----------|-------|
| **RPD (Daily)** | **Midnight Pacific Time** | PT (UTC-7/UTC-8) | Official contract per Google docs |
| **RPM/TPM (Minute)** | Rolling 60-second window | N/A | No fixed reset; sliding window |
| **Spend-based (Tier 1+)** | Rolling 10-minute window | N/A | Only applies if billing enabled |

> "Requests per day (RPD) quotas reset at midnight Pacific time." — Google AI for Developers Rate Limits, 2026-07-20

**Implication for 8-project fleet**: Stagger project creation times by ~3 hours to distribute daily reset load, or accept synchronized reset at midnight PT.

### 5. Dual Quota: Antigravity OAuth + Gemini CLI

**Antigravity Plugin** (`opencode-antigravity-auth`):
- Uses OAuth refresh tokens stored in `~/.config/opencode/antigravity-accounts.json`
- Each account entry requires `projectId` for Gemini CLI models
- Quota tracked via **Antigravity backend** (separate from direct Gemini API)
- Soft quota threshold: 90% (configurable `soft_quota_threshold_percent`)

**Gemini CLI** (direct API key):
- Uses API key from Google AI Studio
- Quota tracked via **Google Cloud project** (same project as Antigravity if `projectId` matches)
- **Shared quota pool** — Antigravity + Gemini CLI calls draw from same project RPD/RPM

**Rotation Strategy**:
- VaultCore stores **both** OAuth refresh tokens (Antigravity) **and** API keys (Gemini CLI) per project
- Lease protocol: acquire credential → check project quota via Cloud Monitoring → if >90% used, skip to next project
- On 429: mark project cooling down until next reset (midnight PT + buffer)

---

## Actionable Configuration for VaultCore (L3)

### VaultCore Schema Extensions (per-project)

```yaml
# In VaultCore secret for each Google project
provider: "google"
project_id: "omega-gemini-3"
credentials:
  # For Antigravity OAuth plugin
  antigravity_oauth:
    refresh_token: "1//0abc..."
    email: "omega-gemini-3@xoe-nov.ai"
    project_id: "omega-gemini-3"
  # For direct Gemini API / Gemini CLI
  api_key: "AIzaSy..."
  service_account_key: |-
    {
      "type": "service_account",
      "project_id": "omega-gemini-3",
      "private_key_id": "...",
      "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
      "client_email": "quota-monitor@omega-gemini-3.iam.gserviceaccount.com",
      "client_id": "...",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token"
    }
quota:
  model: "gemini-3-flash"
  rpm_limit: 10
  tpm_limit: 250000
  rpd_limit: 1500
  reset_time: "00:00 PT"  # midnight Pacific
  current_rpd_used: 0
  current_rpm_used: 0
  last_quota_check: "2026-07-23T14:30:00Z"
  status: "available"  # available | cooling_down | exhausted
rotation:
  strategy: "round_robin_quota_aware"
  soft_threshold_pct: 90
  cooldown_until: null
```

### gcp-seeder Manifest for Fleet (`gcp-seeder.yaml`)

```yaml
version: 1
projects:
  - name: "omega-gemini-1"
    preset: "ai"
    service_account: true
    service_accounts:
      - name: "quota-monitor"
        roles:
          - "roles/monitoring.viewer"
          - "roles/serviceusage.serviceUsageConsumer"
          - "roles/resourcemanager.projects.get"
    ttl: "365d"
    labels:
      fleet: "omega-gemini"
      slot: "1"
  # ... repeat for slots 2-8
```

### Provisioning Script (run once)

```bash
#!/usr/bin/env bash
# provision-gemini-fleet.sh
set -euo pipefail

for i in {1..8}; do
  npx gcp-seeder --yes \
    --name "omega-gemini-${i}" \
    --preset ai \
    --service-account \
    --service-accounts quota-monitor \
    --output-dir "./credentials/gemini-${i}" \
    --ttl 365d \
    --json | jq -r '.projectId' > "./credentials/gemini-${i}/project_id.txt"
done

# Generate API keys in each project via AI Studio (manual step, or use gcloud)
# For each project: https://aistudio.google.com/apikey → Create API key → store in VaultCore
```

---

## Dev Strategy Revisal Recommendations

| Area | Current Assumption | Revised Based on Research |
|------|-------------------|---------------------------|
| **Quota Unit** | Per API key | **Per GCP project** — 8 keys = 8 projects mandatory |
| **Provisioning** | Manual console | **`gcp-seeder` CLI** — automated, idempotent, MCP-exposed |
| **Monitoring** | None / 429-only | **Cloud Monitoring API** via service account — proactive quota % |
| **Reset Timing** | Midnight UTC | **Midnight Pacific Time** — stagger or accept sync |
| **Dual Quota** | Ignored | **Antigravity + Gemini CLI share project quota** — track both |
| **Free Tier Models** | All models | **Flash/Flash-Lite only** — Pro is paid-only since Apr 2026 |

---

## Gaps Requiring Phase 2 Validation

1. **Live quota values**: AI Studio shows live limits per project — need to verify actual RPM/RPD for our specific region/account age
2. **Antigravity projectId auto-provision**: Issue #205 fixed in 1.2.9-beta.7 — validate auto-project-creation on token refresh
3. **Service account key rotation**: `gcp-seeder rotate` command exists — integrate into VaultCore lease expiry
4. **Cross-project billing**: All free tier — no billing account needed, but verify no hidden costs for Cloud Monitoring API calls

---

## References

| Source | Date | Key Data |
|--------|------|----------|
| Google AI for Developers - Rate Limits | 2026-07-20 | Per-project quotas, RPM/TPM/RPD, midnight PT reset |
| Yingtu AI - Gemini API Free Tier | 2026-04-25 | Model-specific limits table, keys share project quota |
| AI Free API - Rate Limits Guide | 2026-01-27 | 50-80% quota reduction Dec 2025, Flash-Lite best throughput |
| LaoZhang AI - Rate Limits Diagnosis | 2026-02-02 | Tier qualification, spend caps, AI Studio live view |
| gcp-seeder npm | 2026-07-12 (v0.4.0) | `--preset ai`, service accounts, MCP server, declarative manifest |
| opencode-antigravity-auth | 2026-01-15 fix | `projectId` mandatory, auto-provision in 1.2.9-beta.7 |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ PHASE1A-COMPLETE ⬡ 2026-07-23*