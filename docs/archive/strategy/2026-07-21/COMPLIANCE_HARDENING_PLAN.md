# 🔱 COMPLIANCE HARDENING PLAN
**Document ID**: `docs/strategy/COMPLIANCE_HARDENING_PLAN.md`
**Status**: ACTIVE
**Mandate**: M1-M22 Compliance Enforcement

## 1. M11 (Soul Integrity) 3-Phase Remediation
**Current Status**: CRITICAL FAILURE (1/23 compliance rate).

### Phase 1: The Purge
- Physically correct corrupted soul files on disk.
- Extract bloated session logs.
- Fix YAML errors (e.g., Researcher double-nested entity key).

### Phase 2: The Gates
- Implement strict CI/CD gates to prevent future `soul.yaml` corruption.
- Use `ruamel.yaml` and Pydantic V2 with `model_config = ConfigDict(extra='forbid', strict=True)`.
- Implement the Atomic Cross-Rename Pattern (`.tmp` -> `os.fsync()` -> `.bak` -> `.yaml`).
- Inject mandatory `schema_version: "6.0"` field into the root of `soul.yaml`.

### Phase 3: The Engine
- Update core engine's soul distillation logic to correctly route session data to `memory/sessions.yaml`.
- Preserve `soul.yaml` purity for L3 principles only.

## 2. M21 (Gate Integrity) Remediation
**Current Status**: PARTIAL (4 of 24 contract tests exist).

### Action Plan
- Implement 20 missing contract tests in `test_contract_m21.py`.
- Ensure every code path returning a typed result is exercised by at least one test validating the return type (`isinstance` checks).
- No mock-based tests that mask type mismatches at the core API boundaries.

## 3. M22 (Response Provenance) Remediation
**Current Status**: PARTIAL (`provider_name` flows through `oracle.py` but not captured by `observability.py`).

### Action Plan
- Wire `observability.py` to capture `GenerateResult.provider_name` and `GenerateResult.provider_metadata`.
- Ensure all observability logs record the *actual* provider that generated a response, not the configured intent.
- Implement ICS-F v1.0 schema for raw provider JSON capture.

## 4. M12 (Queue Integrity) Remediation
**Current Status**: PARTIAL-FAIL (32 stale, 8 pending, 0 completed handoffs).

### Action Plan
- Implement handoff automation spec.
- Ensure every request reaches a terminal state (`queued`, `completed`, `failed`, or `timed_out`).
- Implement Dead-letter directory (`data/requests/dead/`) for failed processing.
- Enforce explicit Ack/Nack patterns and `trace_id` propagation for every queued item.
