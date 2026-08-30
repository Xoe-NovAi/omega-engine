<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 CRITICAL: Streaming Timeout Observability Gap
## What We Know, What We Don't Know, and Why It Matters

**AP Token**: `AP-OBSERVABILITY-GAP-v1.0.0`
⬡ OMEGA ⬡ OBSERVABILITY ⬡ CRITICAL ⬡ 2026-0810

**Date**: 2026-08-10
**Severity**: CRITICAL — Cannot trace system behavior
**Author**: jem (Sovereign Synthesizer)

---

## 🚨 The Problem

**We cannot determine why Nemotron 3 Ultra streaming timeouts have stopped.**

This is a **critical observability failure** because:
1. We cannot debug issues when they arise
2. We cannot document the system accurately
3. We cannot make informed infrastructure decisions
4. We cannot trust our own analysis

---

## ✅ What We Know (Facts)

### Streaming Error Timeline

| Date | Nemotron Messages | Streaming Errors | Error Rate |
|------|------------------|------------------|------------|
| 2026-07-21 | 951 | 124 | 13.0% |
| 2026-07-22 | 995 | 127 | 12.8% |
| 2026-07-23 | 1,059 | 85 | 8.0% |
| 2026-07-24 | 997 | 48 | 4.8% |
| 2026-07-25 | 1,002 | 31 | 3.1% |
| 2026-07-30 | 1,601 | 167 | 10.4% |
| 2026-07-31 to 08-06 | — | — | NO DATA |
| 2026-08-07 | 470 | 28 | 6.0% |
| 2026-08-08 | 576 | 5 | 0.9% |
| 2026-08-09 | 526 | 7 | 1.3% |
| 2026-08-10 | 38 | 0 | 0.0% |

### Key Events

| Date | Event |
|------|-------|
| 2026-07-30 | `better-opencode-retries` plugin installed at `/home/arcana-novai/better-opencode-retries/` |
| 2026-07-30 | Streaming errors stopped (same day) |
| 2026-08-09 | Config refactoring (backups created at 11:44 and 12:46) |
| 2026-08-09 | OpenCode binary installed (19:43) |
| 2026-08-10 | `better-opencode-retries` NOT loaded in any config |

### Current State

- **OpenCode version**: 1.18.16 (installed Aug 9 19:43)
- **better-opencode-retries plugin**: EXISTS at `/home/arcana-novai/better-opencode-retries/` but NOT loaded
- **Global config plugins**: `[]` (empty)
- **Project config plugins**: `["opencode-antigravity-auth@latest", "opencode-sessions-explorer", "error-capture.ts", "awareness.ts"]`
- **Streaming errors**: 0 (today)

---

## ❌ What We Don't Know (Gaps)

### Critical Unknowns

1. **What is currently handling the streaming timeout?**
   - The `better-opencode-retries` plugin is NOT loaded
   - No other plugin or config handles streaming timeouts
   - Yet streaming errors have stopped

2. **Was the plugin ever actually loaded?**
   - The plugin exists but is not in any config
   - No evidence of it being loaded in running processes
   - Yet streaming errors stopped on the day it was installed

3. **Did OpenCode update fix the issue?**
   - OpenCode 1.18.16 was installed on Aug 9
   - Streaming errors stopped on Jul 30 (before this version)
   - No changelog available to verify

4. **Did NVIDIA fix the issue on their end?**
   - No way to verify without testing against the API directly
   - The SSE keepalive ping issue may have been resolved

5. **Is there another mechanism we haven't found?**
   - System-level configuration?
   - Network-level fix?
   - Provider-level change?

---

## 🔍 Investigation Steps Taken

| Step | Result |
|------|--------|
| Checked all opencode.json configs | No streaming/timeout settings |
| Checked all plugin directories | `better-opencode-retries` exists but not loaded |
| Checked running processes | No retry/streaming processes found |
| Checked OpenCode version | 1.18.16 (installed Aug 9) |
| Checked OpenCode changelog | No changelog available |
| Checked system logs | No relevant logs |
| Checked OpenCode logs | No log files found |
| Checked /proc for loaded plugins | No plugin files found |

---

## 🎯 Root Cause Hypotheses (Unverified)

| Hypothesis | Evidence For | Evidence Against | Verdict |
|------------|--------------|------------------|---------|
| **Plugin is still active** | Errors stopped when plugin installed | Plugin not in any config | ❌ UNVERIFIED |
| **OpenCode update fixed it** | Binary installed Aug 9 | Errors stopped Jul 30 (before update) | ❌ UNLIKELY |
| **NVIDIA fixed it** | Errors stopped suddenly | No way to verify | ❓ POSSIBLE |
| **Usage pattern changed** | Error rate dropped gradually | User says they're using same models | ❌ UNLIKELY |
| **Unknown mechanism** | We can't find any fix | — | ❓ POSSIBLE |

---

## ⚠️ Why This Matters

### Immediate Risks

1. **We cannot debug streaming issues** if they return
2. **We cannot document the system** accurately
3. **We cannot make informed decisions** about infrastructure
4. **We cannot trust our own analysis**

### Long-term Risks

1. **Technical debt**: Unknown fixes accumulate
2. **Fragility**: System behavior is unpredictable
3. **Onboarding**: New team members cannot understand the system
4. **Compliance**: Cannot prove system behavior for audits

---

## 🛠️ Recommended Actions

### Immediate (Today)

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | **Add streaming timeout observability** to Context Gauge | TBD | P0 |
| 2 | **Document the unknown** in system architecture docs | TBD | P0 |
| 3 | **Create a streaming health check** that logs timeout events | TBD | P0 |

### Short-term (This Week)

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 4 | **Build a plugin detector** that scans all loaded plugins | TBD | P1 |
| 5 | **Add streaming metrics** to MetricsDB | TBD | P1 |
| 6 | **Test streaming timeout** by intentionally triggering it | TBD | P1 |

### Medium-term (This Month)

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 7 | **Build comprehensive observability** into Omega Engine | TBD | P2 |
| 8 | **Document all system behaviors** in architecture docs | TBD | P2 |
| 9 | **Create automated tests** for streaming behavior | TBD | P2 |

---

## 🏁 Conclusion

**We have a critical observability gap.** We cannot determine why streaming timeouts have stopped. This is unacceptable for a sovereign AI system.

**The path forward is:**
1. Acknowledge the gap
2. Build observability into the system
3. Document what we know and don't know
4. Create mechanisms to detect and debug streaming issues

**Until this is resolved, we cannot trust our own analysis of system behavior.**

---

*⬡ OMEGA ⬡ OBSERVABILITY ⬡ CRITICAL ⬡ 2026-08-10*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: CRITICAL | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
