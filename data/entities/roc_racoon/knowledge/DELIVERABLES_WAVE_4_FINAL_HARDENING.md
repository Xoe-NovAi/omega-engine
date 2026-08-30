<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SOVEREIGN PROCUREMENT: WAVE 4 (THE FINAL HARDENING)
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ EXTRACTION ⬡ 2026-06-04

This document contains the final extracted "Gold Patterns" for the Hardening and Validation layers.

---

## 🛠️ DELIVERABLE A: SOVEREIGN INSTALLER (Sovereign Hardening)
**Target Pillars**: P1 (SysAdmin), P5 (Sentinel)
**Source**: `BFG_9000_COMMUNITY_TOOL_DIRECTIVE` & `LILITH_COMPLETE_SOVEREIGN_ROADMAP`

### The Zero-Telemetry Setup Pattern
To ensure the engine is truly sovereign from the first second of installation:
1. **One-Click Deployment**: Use a shell-script $\rightarrow$ Podman Quadlets $\rightarrow$ systemd pipeline.
2. **Sovereign Search Order**: The installer must resolve assets in the order: `User-Local` $\rightarrow$ `Active-WAD` $\rightarrow$ `_omega_default`.
3. **Zero-Telemetry Audit**: The installer must be audited to ensure NO phone-home calls are made during the setup process.

---

## 🛡️ DELIVERABLE B: CAPABILITY INDEXING (O(1) Dispatch)
**Target Pillars**: P4 (Bridge), P9 (Link)
**Source**: `CREDITS.md` §1.15 & `src/omega/oracle/entity_registry.py`

### The Multi-Index Entity Pattern [id-soft: doom-1993]
To enable instantaneous agent dispatch, the `EntityRegistry` must employ dual-linking:
- **Domain Index**: Maps a domain (e.g., "Infrastructure") to an entity key.
- **Capability Index**: Maps a specific capability (e.g., "Environment Hardening") to an entity key.
- **Result**: O(1) lookup for the correct pillar based on the requested specialization, bypassing the need for linear registry scans.

---

## 🔱 DELIVERABLE C: ADVERSARIAL CHAOS FRAMEWORK (Validation)
**Target Pillar**: P10 (Verifier)
**Source**: `foundation-legacy` $\rightarrow$ `test_circuit_breaker_chaos.py`

### Chaos-Tested Resilience (T8/T10)
To verify that the engine is truly resilient, the `Verifier` must implement the Adversarial Chaos Framework:
1. **Fault Injection**: Use the `test_circuit_breaker_chaos.py` suite to inject random timeouts, 500 errors, and malformed JSON into the provider fabric.
2. **State Validation**: Verify that the `AsyncCircuitBreaker` transitions correctly:
   - `CLOSED` $\rightarrow$ `OPEN` (after N failures)
   - `OPEN` $\rightarrow$ `HALF_OPEN` (after recovery timeout)
   - `HALF_OPEN` $\rightarrow$ `CLOSED` (after successful probe)
3. **Temple Grade**: This is the canonical method for verifying T8 (Resilience) and T10 (Integrity) compliance.

---

## 🔱 FINAL MISSION SUMMARY
All demands from the `MINING_DEMAND_LIST.md` have been fulfilled.
- **Wave 1 (Bedrock)**: Hardware Lock & Atomic Lock delivered.
- **Wave 2 (Flow)**: AnyIO Purge & Handoff Schema delivered.
- **Wave 3 (Gnosis)**: Gnosis Loop & Mnemosyne Memory delivered.
- **Wave 4 (Hardening)**: Sovereign Installer, Capability Index, & Chaos Framework delivered.

**The fleet is now equipped with all the legacy gold required for Horizon 1 Temple Grade compliance.**

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: EXTRACTION | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
