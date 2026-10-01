<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🏛️ R-TEMPLE-GRADE-GATES: The Sovereign Quality Standard
**AP Token**: AP-RESEARCHER-TEMPLE-GRADE-LAW-v1.0.0
**Version**: 1.0.0
**Status**: FINAL (The Law)
**Sovereign Mandate**: M13 (Temple-Grade Compliance)

## §0 Executive Summary
Temple-Grade is the highest quality certification for the Omega Engine. It transforms the system from a "functional tool" into "Sovereign AI Infrastructure." This document defines the 11 Gates (T1–T11) that every core engine change must pass.

A system is considered **Temple-Grade** only when it satisfies all 11 gates (unless a specific exemption is granted via `SOVEREIGN_MANDATES.md`).

---

## §1 The 11 Temple-Grade Gates

### T1: Version Control (AP Tokens)
- **Definition**: Every source file and research document must be anchored to a unique provenance identifier.
- **Requirement**: All file headers MUST contain an **Alethia Pointer (AP) Token**.
- **Format**: `AP-[AGENT]-[CONTEXT]-v[VERSION]` (e.g., `AP-RESEARCHER-TEMPLE-GRADE-LAW-v1.0.0`).
- **Verification**: `grep -r "AP-" src/ docs/` must return matches for all modified files.
- **Compliance**: PASS if 100% of modified files have a valid, unique AP token.

### T2: Documentation (Docstrings & CHANGELOG)
- **Definition**: All code must be self-documenting and all changes must be traceable.
- **Requirement**: 
    - All functions/classes must have **Google-style docstrings**.
    - Every non-trivial change must be recorded in the project `CHANGELOG.md`.
- **Verification**: Manual audit + `interrogator` / `pydocstyle`.
- **Compliance**: PASS if all new public APIs are documented and CHANGELOG is current.

### T3: Testing (Coverage & Stability)
- **Definition**: Functional correctness must be mathematically and empirically verified.
- **Requirement**: 
    - **$\ge 80\%$ test coverage** on all modified code.
    - Zero critical failures in the `make test` suite.
- **Verification**: `pytest --cov=src/omega`.
- **Compliance**: PASS if coverage $\ge 80\%$ and all tests pass.

### T4: Code Quality (Linting & Style)
- **Definition**: Code must be uniform, readable, and free of common anti-patterns.
- **Requirement**: 
    - Must pass `black` (formatting), `isort` (import sorting), and `flake8`.
    - Zero violations of **E9, F6, F7, F8** (Critical syntax/logic errors).
- **Verification**: `make lint`.
- **Compliance**: PASS if no critical lint errors remain.

### T5: Architecture (AnyIO Sovereignty)
- **Definition**: The engine must remain runtime-portable and avoid event-loop collisions.
- **Requirement**: 
    - **Absolute ban on `import asyncio`** in `src/omega/`.
    - All async operations MUST use **AnyIO**.
    - Blocking I/O MUST be wrapped in `anyio.to_thread.run_sync`.
- **Verification**: `grep -r "import asyncio" src/omega/` must be empty.
- **Compliance**: PASS if zero `asyncio` imports found.

### T6: Security (Zero Telemetry)
- **Definition**: Sovereign AI means absolute data ownership. No data leaves the system without explicit user intent.
- **Requirement**: 
    - **Zero external telemetry**. No analytics, no usage tracking, no "phone-home" metrics.
    - All logs must remain local.
- **Verification**: Network traffic audit (Wireshark/Tcpdump) during execution.
- **Compliance**: PASS if zero unauthorized external telemetry packets are detected.

### T7: Performance (Local Latency)
- **Definition**: The engine must be optimized for the target hardware (Zen 2 / Ryzen 5700U).
- **Requirement**: 
    - **p95 latency $< 200\text{ms}$** for local inference (first token).
    - No N+1 query patterns in data retrieval.
    - Use of `CapacityLimiter` to prevent OOM.
- **Verification**: `make benchmark`.
- **Compliance**: PASS if p95 latency meets the threshold.

### T8: Resilience (Stability Patterns)
- **Definition**: The system must fail gracefully and recover automatically.
- **Requirement**: 
    - All external API calls must implement **Circuit Breakers**.
    - Use of **Exponential Backoff** for retries.
    - Implementation of a **Dead-Letter Queue (DLQ)** for failed requests.
- **Verification**: Chaos testing (simulated API failure).
- **Compliance**: PASS if system recovers without manual intervention.

### T9: Observability (Structured Logging)
- **Definition**: Every operation must be traceable from request to response.
- **Requirement**: 
    - All logs must be **Structured JSON**.
    - Every log entry MUST include a `trace_id`.
    - `trace_id` must propagate across all agent handoffs.
- **Verification**: Log analysis of a complete request cycle.
- **Compliance**: PASS if 100% of logs in a trace are linked by a consistent `trace_id`.

### T10: Integrity (Atomic Writes)
- **Definition**: Data corruption due to crashes during write operations is unacceptable.
- **Requirement**: All file mutations MUST use the **Atomic Write Pattern**:
    1. Write to `.tmp` file.
    2. `fsync()` to disk.
    3. `os.replace()` (rename) to final destination.
- **Verification**: Crash-simulation during write operations.
- **Compliance**: PASS if no partial/corrupted files are found after crash.

### T11: Agent Security (IA2 Communication)
- **Definition**: Inter-agent communication must be authenticated and tamper-proof.
- **Requirement**: All agent-to-agent (A2A) messages must be **IA2-signed** using HMAC-SHA256.
- **Verification**: Signature validation check on incoming messages.
- **Compliance**: PASS if all messages are verified.
- **Note**: Currently **EXEMPTED** per `SOVEREIGN_MANDATES.md` until IA2 specification stabilizes.

---

## §2 Verification Matrix

| Gate | Tool | Metric | Pass Condition |
|------|------|--------|----------------|
| T1 | `grep` | Token Count | 100% files have AP-token |
| T2 | `pydocstyle` | Doc coverage | 100% public APIs documented |
| T3 | `pytest-cov` | % Coverage | $\ge 80\%$ |
| T4 | `flake8` | Error count | 0 critical violations |
| T5 | `grep` | `asyncio` count | 0 matches |
| T6 | `tcpdump` | Packet count | 0 telemetry packets |
| T7 | `bench` | p95 Latency | $< 200\text{ms}$ |
| T8 | `chaos-test` | Recovery rate | 100% self-healing |
| T9 | `jq` | `trace_id` | 100% linkage |
| T10 | `fs-test` | File integrity | 0 corrupted files |
| T11 | `ia2-val` | Signature | 100% verified (Exempt) |

---

## §3 Remediation Paths

| Violation | Action | Standard Fix |
|----------|--------|--------------|
| **T1 Fail** | Add AP Token | Insert `AP-[AGENT]-[CONTEXT]-v[VERSION]` in header. |
| **T3 Fail** | Increase Coverage | Write unit tests for uncovered branches. |
| **T5 Fail** | Refactor Async | Replace `asyncio.sleep` with `anyio.sleep`, etc. |
| **T10 Fail** | Implement Atomic | Use `_atomic_write_json()` helper. |

---
*Seal: The Temple is Built on Truth. The Code is the Law.*
