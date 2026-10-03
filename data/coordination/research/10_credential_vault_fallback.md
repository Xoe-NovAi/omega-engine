<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Credential Vault & Oracle Fallback — Deep Research
**AP Token**: `AP-VAULT-FALLBACK-20260726`
**Date**: 2026-07-26 | **Priority**: P0
**Researcher**: Sovereign Researcher

---

## Gap 1: Credential Vault (R_CG11)

### Executive Summary

VaultCore has CRUD + lease protocol but encryption is NOT implemented. BlindVault resolver is a stub (returns fake data). `retrieve_credential()` method doesn't exist. Provider fabric uses `.env` file, NOT VaultCore.

### Current State

| Component | Status |
|-----------|--------|
| Core CRUD | ✅ Implemented |
| Lease Protocol | ✅ Implemented |
| CPE Scoring | ✅ Implemented |
| BlindVault Resolver | ⚠️ Stubbed (fake data) |
| Argon2id+age encryption | ❌ Not in vault_core.py |
| retrieve_credential() | ❌ Method doesn't exist |
| Provider fabric uses vault | ❌ Uses .env directly |

### Issues

1. No actual encryption/decryption path — `encrypted_blob` stored but nothing decrypts
2. `retrieve_credential()` referenced in docs but not implemented
3. BlindVault is a stub (line 352: `# TODO`)
4. Provider fabric reads `.env` directly, bypassing vault

### Effort: ~40h

---

## Gap 2: Oracle Fallback Chain (R42)

### Executive Summary

Fallback chain is well-implemented with 3 layers: CascadeRouter → ProviderSelector → ModelGateway.generate(). Circuit breaker integration is mature (5-state FSM, CUSUM). One critical bug: health_score weight=0 in CascadeRouter.

### Current State

| Layer | Component | Status |
|-------|-----------|--------|
| CascadeRouter | Cost/quality/latency scoring | ✅ Implemented |
| ProviderSelector | Fallback to static priority | ✅ Implemented |
| ModelGateway.generate() | Iterated fallback with circuit breaker | ✅ Implemented |
| Circuit Breaker | 5-state FSM, CUSUM, 429 classification | ✅ Implemented |

### Issues

1. **health_score weight=0 in CascadeRouter** — degraded provider can be selected as primary
2. No quality validation on fallback responses
3. No model capability matching on fallback

### Effort: ~43h

---

## Combined Summary

| Gap | Maturity | Key Issue | Effort |
|-----|----------|-----------|--------|
| Vault | 60% | No encryption, BlindVault stubbed | ~40h |
| Fallback | 85% | health_score weight=0 | ~43h |
