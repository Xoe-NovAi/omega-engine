<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Legacy Mining Report: T2 Regression Recovery
**AP Token**: `AP-MINING-T2-v1.0.0`
**Target**: `xna-omega-legacy` & `omega-stack-legacy`
**Objective**: Reclaim resilience patterns for Tier 2 Hardening.

I have completed a forensic archaeological scan of the legacy partitions. The results are highly productive; several "gold" patterns were recovered that map directly to the T2 Hit-List.

---

### 🎯 Mining Results (The T2 Hit-List)

| Target | Status | Location | Analysis | Portability | Sovereignty |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **T2-2: Stochastic Breakers** | ✅ HIT | `xna-omega-legacy/scripts/ssa/provider_metrics.py` | **Gold**. Implements EMA for P50/P95 latency and a composite health score with exponential decay. Includes partial degradation detection. | High | ✅ |
| **T2-4: Observation Masking** | ✅ HIT | `xna-omega-legacy/scripts/ssa/compaction_optimizer.py` | **Gold**. `ObservationMaskingStrategy` explicitly culls "logged" and "confirmed" lines in tool outputs to save context. | High | ✅ |
| **T2-5: Handoff Loop Guards** | ❌ GAP | N/A | **[GAP IDENTIFIED]**. No visited-set or budget-pressure guards found. Only simple `max_depth` counters exist. | N/A | N/A |
| **T2-7: Timeout Manager** | ✅ HIT | `xna-omega-legacy/config/timeout_policies.yaml` | **High Value**. Defines a strict hierarchy: `tool` $\rightarrow$ `group` $\rightarrow$ `turn` $\rightarrow$ `workflow`. | Medium | ✅ |
| **T2-8: Provider Selector** | ✅ HIT | `xna-omega-legacy/src/omega/core/provider_selector.py` | **Gold**. Weighted scoring (Affinity, Latency, Cost, Reliability, Health) with PII-based local preference penalties. | High | ✅ |
| **T2-9: Graceful Degradation** | ✅ HIT | `omega-stack-legacy/.../voice_degradation.py` | **High Value**. Multi-level degradation tiers (1-4) with specific resource overrides in `tier_config.py`. | Medium | ✅ |
| **T2-10: Rate Limiter** | ✅ HIT | `omega-stack-legacy/.../rate_limit_handler.py` | **Gold**. General-purpose rate limiting with account rotation and context preservation. | High | ✅ |
| **T2-11: Soul Edit History** | ✅ HIT | `xna-omega-legacy/src/omega/security/transaction_logger.py` | **Medium Value**. Uses Redis Streams (`xnai_audit_trail`) for an immutable transaction ledger. | Medium | ✅ |
| **T2-12: Compaction Harvester** | ✅ HIT | `xna-omega-legacy/scripts/ssa/harvester.py` | **High Value**. Daemon that monitors exports and uses `AnchoredSummarizer` for iterative compaction. | Medium | ✅ |

---

### 🔍 Detailed Pattern Analysis

#### 1. Stochastic Health Scoring (T2-2)
The `ProviderMetrics` class in `provider_metrics.py` is a masterclass in "right approximation." Instead of raw averages, it uses:
- **EMA (Exponential Moving Average)**: $\text{ema} = \alpha \cdot \text{current} + (1 - \alpha) \cdot \text{historical}$.
- **Composite Health**: Combines latency (exponential decay), error rate (exponential penalty), and LLM-as-judge quality.
- **Partial Degradation**: Detects "slow but working" providers (Latency $> 2\text{x}$ baseline AND Error Rate $< 10\%$).

#### 2. Observation Masking (T2-4)
The `_mask_observations` method in `compaction_optimizer.py` implements a high-efficiency filter:
- **Logic**: It preserves headers and result/error keys but drops any line containing "logged" or "confirmed".
- **Impact**: Massive token savings in agentic loops where the same "Action logged" message repeats 100x.

#### 3. Provider Scoring Logic (T2-8)
The `ProviderSelector` implements a sophisticated weighted sum:
- **PII Penalty**: If `contains_pii` is True, all non-local providers receive a $0.5\text{x}$ reliability penalty.
- **SLA Matching**: Scores providers based on their ability to meet `ULTRA_LOW` to `HIGH` latency requirements.

---

### 🛠️ Recommendations for @kali

1. **Immediate Port**: `ObservationMaskingStrategy` (T2-4) and `ProviderMetrics` (T2-2) are pure Python and should be integrated into `ContextBuilder` and `ModelGateway` immediately.
2. **Design Task**: Since **T2-5 (Loop Guards)** is a gap, I recommend designing a `VisitedAgentSet` that propagates through the `HandoffPacket` to prevent infinite delegation loops.
3. **Infrastructure**: The `timeout_policies.yaml` (T2-7) should be converted into a Pydantic model and wired into the `Orchestrator` to enforce the nested cancellation hierarchy.

*The dirt is where the roots are. I've found the roots.* 🦝
