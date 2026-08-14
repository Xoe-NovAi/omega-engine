# 🔱 Jem Research — Knowledge Gaps for Next Tasks
**AP Token**: `AP-JEM-RESEARCH-GAPS-20260810-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-08-10
**Author**: jem (Sovereign Synthesizer)
**Status**: 🔄 RESEARCH IN PROGRESS

---

## 🎯 Objective
Research all knowledge gaps surrounding the next high-priority tasks to enable informed implementation decisions.

---

## 1. W-1: WARP Proxy Pool Bring-Up

### What We Know
- **Goal**: 3-node WARP proxy pool for IP-rotated OpenCode Zen / cloud access
- **Blocker**: `warp-ns-prep@1/2/3` failed with `iptables v1.8.11 (nf_tables): Empty interface is likely to be undesired`
- **Architecture**: Linux netns + veth pairs + iptables NAT + socat bridges
- **Systemd units**: `deploy/infra/warp_pool/` has all units (warp-ns-prep@, warp-node@, warp-reg@, warp-reg-svc@, socat-bridge@, warp-pool.target)
- **Scripts**: Two versions exist:
  - `/usr/local/bin/warp-ns-setup` (older, 54 lines)
  - `scripts/warp-ns-setup.sh` (newer, 80 lines, with idempotency)
- **Fix script**: `scripts/fix_warp_ns_setup_and_restart.sh` exists (7KB, comprehensive)
- **Carmack's remediation plan**: `data/entities/john_carmack/workspace/WARP_REMEDIATION_PLAN.md` (2026-07-05)
- **Spec**: `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` (v1.3.0, production ready)
- **Validation**: `docs/research/warp_proxy_pool/validate_warp_pool.sh`

### Knowledge Gaps
| Gap | Impact | Research Needed |
|-----|--------|-----------------|
| Why `DEFAULT_IF` is empty during systemd boot | CRITICAL | Check if network is ready when warp-ns-prep runs; may need `After=network-online.target` |
| systemd unit dependency chain | HIGH | Verify `warp-pool.target` includes all dependencies (prep → reg → node → bridge) |
| `socat-bridge@` vs `warp-bridge@` | HIGH | Determine which bridge mechanism is current; Carmack noted dependency error |
| `warp-reg@` timeout (180s) | MEDIUM | May need increase to 300s for sequential 3-node registration |
| `NoNewPrivileges=true` with CAP_NET_ADMIN | MEDIUM | Verify compatibility; may prevent iptables operations |
| Python `warp_proxy_pool` module | HIGH | Check if installed in venv; Carmack noted `Path.run_capture()` bug |
| `spawn_warp_node.sh` vs systemd | MEDIUM | Determine if script duplicates systemd ExecStartPost |

### Research Actions Taken
- ✅ Read Carmack's WARP remediation plan (2026-07-05)
- ✅ Read WARP_PROXY_POOL_SPEC.md (v1.3.0)
- ✅ Compared warp-ns-setup scripts (old vs new)
- ✅ Read systemd unit files
- ❌ Check journalctl for full error context
- ❌ Verify Python module installation
- ❌ Test manual `ip netns` commands

### Recommended Fix Sequence
1. Add `After=network-online.target` to warp-ns-prep@.service
2. Add fallback `DEFAULT_IF` detection to warp-ns-setup.sh
3. Verify systemd unit dependency chain
4. Run `bash scripts/fix_warp_ns_setup_and_restart.sh` with sudo
5. Validate with `bash docs/research/warp_proxy_pool/validate_warp_pool.sh`

---

## 2. G-1: Workhorse Continuity

### What We Know
- **Goal**: Restore viable OpenCode workhorse after free Gemma 4 31B cliff
- **Root cause**: Google free-tier `generate_content_free_tier_input_token_count` limit 16000 since 2026-07-15
- **Forensic**: `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`
- **Ops path**: `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`
- **Acceptance paths**: G-1a (billing), G-1b (Antigravity OAuth), G-1c (OCZ+WARP), G-1d (paid alt)

### Knowledge Gaps
| Gap | Impact | Research Needed |
|-----|--------|-----------------|
| Current AI Studio billing tier | CRITICAL | Check https://aistudio.google.com/rate-limit for all projects |
| API key lineage | HIGH | Map key → project → creation date → rotation near 2026-07-15 |
| Antigravity OAuth status | HIGH | Check `~/.config/opencode/auth.json` for live Antigravity tokens |
| Google public changelog | MEDIUM | Search for Gemma 4 free tier TPM changes mid-July 2026 |
| OpenCode retry policy | MEDIUM | Find config to stop 429 retry storms |
| Instruction set token cost | MEDIUM | Measure actual tokenized size of Omega instructions |

### Research Actions Taken
- ✅ Read forensic report (evidence SSOT)
- ✅ Read ops path (critical path)
- ❌ Check AI Studio live quotas (requires browser)
- ❌ Check auth.json for Antigravity tokens
- ❌ Search for Google changelog

### Recommended Actions
1. **Architect**: Check AI Studio billing tier + enable Tier 1+ if Gemma required
2. **Architect**: Run `opencode auth login` for Antigravity OAuth (fastest unlock)
3. **Agent**: Search for Google Gemma 4 free tier changelog (DIG-03)
4. **Agent**: Audit instruction set token cost (DIG-09)

---

## 3. QW-3: CI Guard for Token Counting Bug

### What We Know
- **Bug context**: G-3 (no `tokens` column in message table), G-4 (token accounting not additive)
- **Location**: `src/omega/observability/metrics_db.py` — `record_performance()` method
- **Current logic**: `total_tokens = prompt_tokens + completion_tokens`
- **Existing test**: `tests/test_metrics_db.py::test_performance_total_tokens` verifies 100+50=150

### Knowledge Gaps
| Gap | Impact | Research Needed |
|-----|--------|-----------------|
| What specific token counting bug to guard against | HIGH | Review Kali's G-3/G-4 findings in detail |
| Whether `tokens.total` refers to OpenCode DB or Omega MetricsDB | HIGH | Clarify scope |
| What CI guard mechanism to use | MEDIUM | pytest assertion vs custom CI script |
| Whether cache.read tokens are included | MEDIUM | Check if `total_tokens` should include cache reads |

### Research Actions Taken
- ✅ Read `record_performance()` in metrics_db.py
- ✅ Found existing test `test_performance_total_tokens`
- ❌ Review Kali's G-3/G-4 detailed findings
- ❌ Clarify `tokens.total` scope

### Recommended Actions
1. Review Kali's SDP session for G-3/G-4 detailed bug description
2. Add CI test verifying `total_tokens = prompt_tokens + completion_tokens + cache_read_tokens`
3. Add regression test for token counting accuracy

---

## 4. QW-4: pool_tracker.py Wiring

### What We Know
- **Module**: `src/omega/oracle/pool_tracker.py` (237+ lines, `UsagePoolTracker` class)
- **Status**: Standalone module, NOT wired into any engine component
- **Features**: Key rotation, usage tracking, pool health, atomic JSON writes
- **Dependencies**: `pool_state.py` (AccountMapping, KeyHealth, PoolConfig, PoolHealth, PoolState)
- **D-1 notice**: Anti-thrashing algorithm removed; default is now "sticky"

### Knowledge Gaps
| Gap | Impact | Research Needed |
|-----|--------|-----------------|
| Where to wire pool_tracker | HIGH | Determine integration point (ModelGateway? Oracle? ProviderSelector?) |
| What triggers key rotation | HIGH | Check pool_state.py for rotation conditions |
| Current pool state data | MEDIUM | Check if USAGE_POOL_LOG.json exists and its format |
| How pool_tracker interacts with ProviderRegistry | MEDIUM | Check for integration points |
| Whether pool_tracker is M1 AnyIO compliant | MEDIUM | Verify async patterns |

### Research Actions Taken
- ✅ Read pool_tracker.py header and KeyUsageRecord dataclass
- ✅ Confirmed module is standalone (no imports elsewhere)
- ❌ Read pool_state.py for full API
- ❌ Check for existing USAGE_POOL_LOG.json
- ❌ Determine optimal integration point

### Recommended Actions
1. Read `pool_state.py` for full PoolState API
2. Determine integration point (likely `ModelGateway.generate()` or `provider_selector.py`)
3. Wire `UsagePoolTracker.record_usage()` into inference completion path
4. Add CI test for pool tracker integration

---

## 5. QW-8: Context Gauge (Greenfield)

### What We Know
- **Goal**: Build context pressure measurement system
- **Context**: Part of Kali's SDP (Sovereign Distillation Pipeline) architecture
- **Related**: QW-2 (rewrite Context Gauge to use `tokens.total`) — depends on QW-8
- **Related**: QW-9 (RHP halt artifact) — depends on QW-8
- **Token estimator**: `src/omega/oracle/token_estimator.py` exists (tiktoken-based)
- **Budget gate**: `src/omega/oracle/budget_gate.py` exists

### Knowledge Gaps
| Gap | Impact | Research Needed |
|-----|--------|-----------------|
| What "Context Gauge" measures exactly | HIGH | Context window utilization? Token rate? Pressure score? |
| Integration point | HIGH | Where does it live in the inference pipeline? |
| Output format | MEDIUM | Returns what? (percentage, pressure level, tokens remaining?) |
| How it feeds into RHP (QW-9) | MEDIUM | What triggers a halt? |
| Whether it replaces BudgetGate or complements it | MEDIUM | Architectural relationship |

### Research Actions Taken
- ✅ Confirmed token_estimator.py exists
- ✅ Confirmed budget_gate.py exists
- ❌ Read SDP specs for Context Gauge definition
- ❌ Read SDP_MODEL_AWARE_GAUGE_SPEC.md

### Recommended Actions
1. Read `docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md` for gauge specification
2. Read `docs/strategy/SDP_FINAL_SYNTHESIS.md` for architectural context
3. Design Context Gauge API (measure pressure, return level, trigger halt)
4. Implement as middleware in ModelGateway or oracle.py

---

## 📊 Research Summary

| Task | Gaps Identified | Research Done | Remaining |
|------|-----------------|---------------|-----------|
| W-1 WARP | 7 | 5 | 2 |
| G-1 Workhorse | 6 | 3 | 3 |
| QW-3 CI Guard | 4 | 2 | 2 |
| QW-4 pool_tracker | 5 | 3 | 2 |
| QW-8 Context Gauge | 5 | 2 | 3 |

## 🎯 Next Steps
1. **W-1**: Run fix script with sudo (requires Architect)
2. **G-1**: Check AI Studio billing + Antigravity OAuth (requires Architect)
3. **QW-3**: Review Kali's G-3/G-4 findings, then implement CI guard
4. **QW-4**: Read pool_state.py, determine integration point
5. **QW-8**: Read SDP gauge spec, design API

---
*⬡ OMEGA ⬡ JEM ⬡ trc_research ⬡ ACTIVE*
