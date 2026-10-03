<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Test Suite Honesty — Deep Research
**AP Token**: `AP-TEST-HONESTY-20260726`
**Date**: 2026-07-26 | **Priority**: P0
**Researcher**: Sovereign Researcher

---

## Executive Summary

1,703 tests collected but only ~130+ actually pass (contract/property/chaos/unit). Badge generator reports all zeros. 7 xfail tests exist but quarantine marker not registered. C-0 ticket partially complete with significant gaps.

## Current State

| Metric | Value |
|--------|-------|
| Tests collected | 1,703 |
| Collection errors | 1 (test_vault_integrity.py) |
| Quarantined (xfail) | 7 (MCP client + sqlite-vec) |
| Contract tests (honest) | 77 + 36 = 113 |
| Property tests (Hypothesis) | 16 pass, 1 skip |
| Chaos tests | 2 pass, 1 fail, 5 skip |
| Badge generator | Broken (all zeros) |

## Vanity Risk Areas (Mock-Heavy Tests)

| File | Mock Count | Risk |
|------|------------|------|
| test_context_builder.py | 63 | 🔴 High |
| test_orchestrator.py | 47 | 🔴 High |
| test_hivemind.py | 44 | 🟡 Medium |
| test_providers.py | 41 | 🔴 High |
| test_model_gateway.py | 33 | 🔴 High |

## C-0 Gaps

| Gap | Status |
|-----|--------|
| Badge generator | ❌ Broken (reports all zeros) |
| Quarantine marker | ❌ Not registered in pyproject.toml |
| conftest.py hook | ❌ Not implemented |
| test_vault_integrity.py import | ❌ Broken |
| Real test numbers in OMEGA_ENGINE.md | ❌ Not updated |

## Implementation Plan

| Phase | Task | Effort |
|-------|------|--------|
| 1 | Fix badge generator | 30min |
| 2 | Register quarantine marker in pyproject.toml | 5min |
| 3 | Add quarantine hook to conftest.py | 15min |
| 4 | Fix test_vault_integrity.py import | 15min |
| 5 | Run make test and commit real numbers | 10min |
| 6 | Audit mock-heavy tests (>20 mocks) | 2h |
| 7 | Convert top 10 mock-heavy to contract tests | 4h |
| 8 | Add property tests for SoulStore + OOMProtector | 2h |
| 9 | Implement quarantine SLA (14-day expiry) | 2h |
| 10 | Add mutation testing (mutmut) | 4h |
| **Total** | | **~15h** |
