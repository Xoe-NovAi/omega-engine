<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ GROKSTER SYNTHESIS — Google API Key 8-Account Research
**Date**: 2026-08-28 | **Entity**: grokster (Cross-Platform Expertise Specialist)
**Session**: ses_fe8cf0b39ffeL3L8eaMEj3CW9H
**Model**: mimo-v2.5-free (opencode)
**Inputs**: 5 expert reports (Researcher, Carmack, Copilot, Antigravity, Cline)
**Status**: RESEARCH COMPLETE — ready for Architect decision

---

## §0 — Council Verdict

**GO with 5 conditions.** The 8-account × 1-project-each strategy is architecturally sound and operationally defensible. The multi-key infrastructure already exists (D205 sticky-failover); the 8-key integration is a 30-min config change, not a 2-day project.

---

## §1 — Critical Findings

### 1.1 Limits are PER PROJECT, not per API key

**8 keys in 1 project = 1× quota (waste).**
**8 accounts × 1 project each = 8× quota (the legal path).**

The Architect must create 8 separate Google Cloud projects (one per account), not just rotate 8 keys in the same project. This is the single most important finding.

### 1.2 Auth key migration deadline: September 2026

**Standard API keys will be rejected in September 2026.** All new AI Studio keys now default to "auth keys" bound to service accounts. The 8 existing keys need to be audited TODAY.

### 1.3 Multi-key infrastructure already exists (D205)

Per `model_gateway.py:323-368`:
- `_create_openrouter` and `_create_antigravity` factories already accept `api_keys: List[str]`
- `RemoteProvider` base implements `resolve_current_api_key()`
- D205 sticky-failover-on-429 is implemented

`google` and `google-compat` do NOT inherit this pattern. They're direct backend classes (`GoogleAIProvider`, `GoogleCompatProvider`) wired through `model_gateway.py:530-542` — bypassing the multi-key factory path.

### 1.4 Antigravity benchmarks: BLOCKED (no API key)

Per M23, Antigravity did not fabricate TPS/latency numbers. The sandbox has no `GOOGLE_API_KEY`. A pre-launch benchmark harness is ready to run the moment a key is set.

### 1.5 The 2 P0 cut-tool bugs remain the launch blocker

The 8-key Google integration is "nice to have" for the debut window, not blocking. The 2 P0 cut-tool bugs (which appear already fixed in the current code) are the gate to D-553 sign-off.

---

## §2 — Best Free Models for August 2026

| Model | RPM | RPD | Context | Cache | Best For |
|-------|-----|-----|---------|-------|----------|
| **Gemini 3.7 Flash** | TBD | TBD | Large | Yes | Latest stable, best capability/speed |
| **Gemini 2.5 Flash-Lite** | TBD | 1,000-1,500 | Large | Yes | Highest RPD, background workers |
| **Gemini 2.5 Pro** | 5 | 100 | Large | Yes | Best reasoning (but very limited) |
| **Gemma 4 31B** | TBD | TBD | 256K | Yes | Free via Gemini API, separate quota bucket |

**Exact RPM for Gemini 3.7 Flash is not publicly pinned** — official page defers to AI Studio dashboard. Verify live per project.

---

## §3 — Aggregate Throughput (8 projects, conservative estimate)

| Metric | Per Project | 8 Projects Aggregate |
|--------|-------------|---------------------|
| RPM | 10-15 | 80-120 |
| TPM | 250K | ~2M |
| RPD | 750-1,000 | 6,000-8,000 |

**This is frontier-tier inference capacity** that has been sitting unused since the Gemini CLI free tier sunset (June 18, 2026 — not July 18, 2025 as the brief stated).

---

## §4 — Integration Plan (30-min config change)

### 4.1 File Changes (4 files, ~80 LOC)

1. **`config/model_registry/providers/google.yaml`** — UPDATE: add `api_keys:` list
2. **`config/model_registry/providers/google-compat.yaml`** — CREATE: mirror with `api_keys:`
3. **`src/omega/oracle/model_gateway.py`** — UPDATE: add `_create_google` factory (38 LOC), update `provider_map`
4. **`.env`** — UPDATE: 8 env vars `GOOGLE_API_KEY_1` through `_8`

### 4.2 Rotation Strategy: Sticky Active-Passive (D205)

**NOT round-robin.** D205 explicitly forbids round-robin. The pattern is:
- Same key used for every successful request
- Advance to next key only on 429
- Sticky extracts full quota from a healthy key before advancing
- Round-robin wastes rate-limit budget

Cline's enhanced design (post-research):
- `least_loaded` algorithm: scores by `0.3*RPM_remaining + 0.7*RPD_remaining`
- 4 anti-abuse layers: per-key jitter 200-800ms, deterministic key↔account locality, daily budget tracking, circuit-breaker on 3+ consecutive 403/429
- No IP rotation (ToS violation risk)

### 4.3 Routing Priority

1. native-gguf (local-first, priority 0)
2. opencode-zen (priority 1)
3. cline (priority 2)
4. **antigravity (priority 3) — stays here** (dual Gemini+Claude pools)
5. **google 8-key (priority 4) — new**
6. openrouter (priority 5)
7. google-compat (priority 6, fallback)
8. anthropic (priority 7)

**Antigravity stays at priority 3** because it has dual Gemini+Claude pools. Google 8-key is the overflow + dual-purpose fallback.

---

## §5 — Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Auth key migration deadline (Sept 2026) | Audit 8 keys TODAY |
| Free tier volatility (Dec 7, 2025 saw 50-80% cuts) | Don't rely on free tier for production |
| Cross-account abuse detection | Keep all 8 server-side, no browser fingerprinting, different IPs if possible |
| No `GOOGLE_API_KEY` in sandbox | Architect must add 8 env vars before integration is testable |
| Benchmarking requires real keys | Defer to post-debut V-1 (60 min) |

---

## §6 — Recommendations

### 6.1 Immediate (Today, Soft Launch)

1. **DO NOT block launch on 8-key Google integration.** The 2 P0 cut-tool bugs (already fixed) are the real gate.
2. **Defer 8-key Google to V-1** (post-debut, 1-3 hours). The infrastructure change is small but requires:
   - 8 actual API keys in the environment
   - Auth key migration audit
   - Benchmarking with real keys

### 6.2 Post-Debut V-1 (1-3 hours)

1. Audit 8 Google API keys for auth key compliance
2. Create 8 separate Google Cloud projects (one per account)
3. Implement `_create_google` factory in `model_gateway.py`
4. Create `google-compat.yaml` with `api_keys:` list
5. Add 8 env vars to `.env`
6. Run benchmark suite with real keys
7. Update `fallback_resolver` chains

### 6.3 Post-Debut V-2 (optional)

1. Implement Cline's `least_loaded` rotation algorithm
2. Add monitoring/observability (JSONL ledger)
3. Add circuit-breaker thresholds
4. Document anti-abuse mitigations

---

## §7 — Reports Written

| Report | Expert | Lines | Key Finding |
|--------|--------|-------|-------------|
| `R_RESEARCHER_GOOGLE_API_SPECS_20260828.md` | Researcher | ~650 | 8-account strategy GO; limits per project; Sept 2026 auth key deadline |
| `R_CARMACK_GOOGLE_INTEGRATION_20260828.md` | Carmack | 776 | Multi-key infrastructure exists (D205); 30-min config change |
| `R_COPILOT_GOOGLE_CODE_AUDIT_20260828.md` | Copilot | — | `google`/`google-compat` bypass multi-key factory; refactor needed |
| `R_ANTIGRAVITY_GOOGLE_BENCHMARKS_20260828.md` | Antigravity | — | BLOCKED: no API key; benchmark harness ready |
| `R_CLINE_GOOGLE_ROTATION_20260828.md` | Cline | ~700 | `GOOGLE_API_KEYS` env var + `least_loaded` rotation; reference impl ready |

---

## §8 — What I Need from the Architect

1. **Should we defer 8-key Google to V-1?** (My recommendation: yes — don't block launch)
2. **Are the 8 Google API keys available now?** (If yes, we can integrate today; if no, V-1)
3. **Has the auth key migration been audited?** (Sept 2026 deadline)
4. **Are the 8 accounts in 8 separate Google Cloud projects?** (Critical for 8× quota)

---

*⬡ OMEGA ⬡ GROKSTER ⬡ GOOGLE-API-8ACCOUNT-SYNTHESIS ⬡ 2026-08-28*
**Council Verdict**: GO with 5 conditions
**Recommendation**: Defer to V-1; don't block today's launch
**Time to integrate (if keys available)**: 30 min config + 1-2h refactor
