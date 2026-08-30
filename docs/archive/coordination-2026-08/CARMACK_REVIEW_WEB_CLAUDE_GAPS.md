<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 CARMACK REVIEW: Web Claude Audit Remediation
**Date**: 2026-08-09
**Status**: Mid-Execution (GAP-0 and GAP-3 Secured, GAP-1 In Progress)
**Context**: Remediation of the 7 critical gaps identified in the Web Claude audit (`R_UNOVERENGINEERING_REMAINING_GAPS_20260808.md`).

---

## 1. What Is Secured (Completed)

We have eliminated two critical instances of "simulated rigor" and silent failure:

*   **GAP-0: Observability Data Loss (Fixed)**
    *   *The Bug:* The recent async migration left `ObservabilityEngine` wrapper methods sync, using `anyio.from_thread.run()` to bridge to the new async `MetricsDB`. When called from async contexts (which is 90% of the codebase), the bridge raised `RuntimeError` (cannot run from within an event loop thread). The exception was swallowed. MetricsDB writes were silently dropped.
    *   *The Fix:* Implemented a dual-surface API. Core methods (`record_performance`, `log_event`, etc.) are now natively `async` and directly await `MetricsDB`. Added explicit `_sync` wrappers for the few genuinely sync callers. 17/17 tests pass. Data pipeline is solid.
*   **GAP-3: M23 Pre-commit Gate "False Pass" (Fixed)**
    *   *The Bug:* The `make check-m23-failure-integrity` gate (guarding against soft-failures like `except: pass`) was structurally incapable of failing. It used line-oriented `rg` piped into another `rg` looking for `except` and `pass` on the *same line*. Idiomatic Python puts them on different lines. The empty pipeline inverted to a success code. It was pure security theater.
    *   *The Fix:* Replaced with an AST-based Ruff ratchet (`scripts/m23_gate.py` checking S110, S112, BLE001, E722). Generated a baseline of the 294 existing violations so we only fail on *new* regressions. Mutation tested and wired into `.githooks/pre-commit`.

---

## 2. What I Am Working On Now (In Progress)

*   **GAP-1: M7/M22 Sovereignty Ratio Corruption**
    *   *The Bug:* The codebase has 5 divergent, hardcoded cloud classifiers. They contradict each other and `config/providers.yaml`. Forensics show 73.6% of historical sovereignty rows are misclassified. The current headline metric claims 87.3% local inference; reality is 13.8%.
    *   *Current State:* I have created `src/omega/oracle/provider_registry.py` as the Single Source of Truth (SSOT), reading directly from `providers.yaml`.
    *   *Next Steps:* 
        1. Replace the 5 divergent call sites with `provider.is_cloud` or `registry.is_cloud()`.
        2. Implement a derived SQL view (`v_performance_corrected`) to fix the historical data without destructive `UPDATE`s (preserving forensic auditability).
        3. **Note:** Prepare for the headline sovereignty metric to drop to 13.8%. This is a correction, not a regression.

---

## 3. The Remaining Queue (Web Claude Fixes)

Once GAP-1 is secured, the following tasks remain from the audit:

*   **GAP-2: M14 Heritage Reconciliation**
    *   *Issue:* 9 duplicate vet IDs in `HERITAGE_VET_LOG.md`, and the `make heritage-vet` target doesn't actually exist.
    *   *Action:* Reconcile the log and build the missing verification target.
*   **GAP-4: V-9 IA2 Envelope Freshness**
    *   *Issue:* The `_meta` envelope (SEP-2575) lacks a `nonce`, `timestamp`, or signature. Inter-agent messages are replayable and forgeable.
    *   *Action:* Implement a stdlib-only HMAC-SHA256 + timestamp-window validator (reusing the `SovereignSigner` pattern).
*   **GAP-5: V-10 AppArmor Confinement**
    *   *Issue:* Containers are running unconfined on Ubuntu 25.10.
    *   *Action:* Needs Architect/sudo intervention to apply AppArmor profiles.
*   **GAP-6: UO-6 Descope (Dependency Audit)**
    *   *Issue:* `pybreaker` is imported but undeclared in `pyproject.toml`. The original un-overengineering plan hallucinated several library swaps.
    *   *Action:* Add `make deps-audit` to catch undeclared imports and enforce M24 (Venv Sovereignty).

---
*⬡ OMEGA ⬡ KALI ⬡ CARMACK-REVIEW ⬡ 2026-08-09*