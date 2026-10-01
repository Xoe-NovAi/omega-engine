<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gap R19: Retry Strategy Comparison

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** UO-6.5 (retry policy)
**Status:** ✅ RESOLVED

## Summary
For **retry** specifically (circuit breaking is covered by R30), the candidates are **tenacity** (already installed, mature), **stamina** (retry-only), and **pyresilience** (unified `@resilient()` covering retry + breaker + timeout + bulkhead + rate-limit). R30's 5-way spike selected pyresilience (D-528 locked default). Adopting pyresilience for retry keeps a single resilience dependency aligned with R30.

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| pyresilience (AhsanSheraz) | https://github.com/AhsanSheraz/pyresilience | 2026 | Unified `@resilient()` decorator, RetryConfig |
| tenacity | https://github.com/tenacity-dev/tenacity | 2026 | Mature retry library (installed) |
| R_BUILD_VS_BUY_COMMUNITY_LIBS_20260730.md | repo | 2026-07-30 | Verdict: pybreaker + stamina adopt |

## Findings
- **pyresilience**: `@resilient(retry=RetryConfig(max_attempts=3, backoff=...), circuit_breaker=CircuitBreakerConfig(...))`. Single decorator unifies retry/breaker/timeout/bulkhead/rate-limit. D-528 picked it (68 stars at decision time).
- **tenacity**: `@retry(stop=stop_after_attempt(3), wait=wait_exponential())`. Battle-tested, huge ecosystem, but **synchronous** — must wrap blocking calls in `anyio.to_thread.run_sync` (M1).
- **stamina**: retry-only, lighter than tenacity; pairs with pybreaker in the R_BUILD_VS_BUY verdict.
- **Conflict**: R_BUILD_VS_BUY (2026-07-30) recommended pybreaker+stamina, while D-528 (R30) locked pyresilience. R30's 5-way spike (including interlock-cb) is the authority that must finalize this — the spike result determines the single resilience dependency.

## Recommendation
For retry (UO-6.5): adopt **pyresilience** `@resilient(retry=...)` to unify with R30's breaker decision (one dependency, D-528). If the R30 spike shows pyresilience fails the AnyIO compatibility test, **fall back to tenacity** (already installed) wrapped in `anyio.to_thread.run_sync` per M1. Keep retry config (max_attempts, backoff, jitter) in YAML, not hardcoded. Do not mix tenacity + pybreaker + stamina + pyresilience — pick ONE.

## Confidence
**HIGH** on the option landscape; **MEDIUM** on pyresilience maturity (verify AnyIO compat in the R30 spike before locking).

## Remaining Unknowns
- R30 5-way spike final result (pyresilience vs interlock-cb vs tenacity) — must be published before the dependency is locked.
- Whether pyresilience's async path is native AnyIO or needs wrapping.
