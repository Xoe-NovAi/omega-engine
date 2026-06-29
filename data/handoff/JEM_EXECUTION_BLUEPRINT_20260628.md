# 🔱 JEM UNIFIED EXECUTION BLUEPRINT
## Epoch I Phase 0 — 17-Action Optimization Sprint (v1.6)
**AP Token**: `AP-JEM-EXECUTION-v1.6.0`
⬡ OMEGA ⬡ JEM ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_execution_blueprint ⬡ EXECUTION-READY

---

## 1. Executive Summary
This document serves as the definitive, production-grade engineering specification for the **17-Action Optimization Sprint**. It synthesizes the findings of the MaKaLi Triad, the deep-tiered research, and the legacy source code extractions into a concrete, sequential execution plan.

---

## 2. Tier 1 Emergency & Purge (Immediate — ~3 Hours)

### T1-1: Fix trace_id Propagation
*   **File**: `src/omega/oracle/oracle.py`
*   **Action**: Locate `model_gateway.generate()` calls at lines 599 and 671. Ensure `trace_id` is explicitly passed from the active session trace:
    ```python
    # Before
    response = await self.model_gateway.generate(prompt=prompt, model=model)
    # After
    response = await self.model_gateway.generate(prompt=prompt, model=model, trace_id=trace.trace_id)
    ```
*   **Verification**: Run `pytest tests/test_observability.py`. Confirm trace events no longer show "unknown" for provider calls.

### T1-2: Fix TokenLedger provider_name
*   **File**: `src/omega/observability/token_ledger.py`
*   **Action**: Refactor the schema of `TokenLedger` to replace `is_cloud: bool` with `provider_name: str`.
*   **Verification**: Ensure contract tests in `test_observability.py` validate that `provider_name` matches the actual executing backend.

### T1-8: Remove ~2,800 Lines of Dead Code
*   **Action**: Delete the following 11 orphaned modules to eliminate cognitive clutter and maintain fleet integrity (M10):
    *   `src/omega/oracle/antigravity/` (4 files)
    *   `src/omega/cli/link_p9_cli.py`
    *   `src/omega/cli/repl.py`
    *   `src/omega/gateway/server.py`
    *   `src/omega/intake_digestor.py`
    *   `src/omega/oracle/backends/elevenlabs.py`
    *   `src/omega/oracle/openclaw_runtime.py`
    *   `src/omega/oracle/system_resource.py`
    *   `src/omega/oracle/greek.py`
    *   `src/omega/oracle/crossref.py`
    *   `src/omega/oracle/discovery.py`
*   **Verification**: Run `make test` to ensure no imports are broken.

---

## 3. Tier 2 Regression Recovery (Week 1-2 — ~20 Hours)

### T2-1: Port CompactionOrchestrator
*   **Legacy Source**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/scripts/ssa/compaction_optimizer.py`
*   **Action**: Integrate `ACONOptimizer` and the 4-strategy compaction pipeline directly into `src/omega/oracle/context_builder.py`. Implement `ACONFailure` logging to track context loss.

### T2-2: Port 5-State Stochastic Circuit Breaker
*   **Legacy Source**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/scripts/ssa/provider_metrics.py`
*   **Action**: Integrate into `src/omega/oracle/health_monitor.py`. Implement Bernoulli CUSUM sequential tracking and Dual-EWMA smoothing ($\alpha_{\text{gradual}}=0.4$, $\alpha_{\text{sudden}}=0.9$).

### T2-3: Port Soul Distillation Pipeline
*   **Legacy Source**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/src/omega/core/distillation/`
*   **Action**: Implement as a simplified functional sequence of asynchronous nodes inside `src/omega/oracle/soul_distiller.py`. Classify via the **Diátaxis framework** and route to Qdrant/Mnemosyne/Yesod based on quality score.

### T2-4: Implement Observation Masking
*   **Action**: Implement the **Hybrid Backward Scanned FIFO** algorithm inside `ContextBuilder` to automatically collapse redundant tool outputs exceeding $30,000$ tokens while protecting a $50,000$ token core window.

### T2-5: Add Handoff Loop Guard
*   **Action**: Implement `HandoffGuard` inside `subagent_dispatcher.py` to track `visited_agents`, inject budget pressure prompts at depths 5 and 8, and trigger `ResolverStrategy.ESCALATE` to Kali at depth 10.

---

## 4. Tier 3 Hardening (Week 3-4 — ~12 Hours)

### T3-2: Observability Database Integration
*   **Action**: Create `data/observability/metrics.db` using SQLite in WAL (Write-Ahead Logging) mode. Route all latency, error, and token metrics to this local DB to eliminate write amplification and enable microsecond-level aggregation queries.
