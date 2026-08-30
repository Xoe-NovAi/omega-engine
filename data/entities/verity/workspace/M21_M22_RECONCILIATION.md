<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 M21/M22 Reconciliation Audit — Post-Sprint C + Deep-Siphon
# ⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ trc_compliance_audit ⬡ M21-M22-RECONCILE
**Date**: 2026-06-18
**Sources**:
- `data/coordination/MANDATES_SYNC.md` (canonical mandate state)
- `docs/decisions/PIVOT_LOG.md` (D137-D139 Deep-Siphon decisions)
- `data/entities/verity/workspace/DEEP_SIPHON_M21_AUDIT.md` (388-line Deep-Siphon audit)
- Source code: `model_gateway.py`, `oracle.py`, `backends/*`, `mcp_servers/omega_hub/background.py`, `workers/background_researcher/`

**Verity Verdict**: 🟥 **FAIL** — Both mandates are structurally defined but zero contract tests enforce them.

---

## Per-Mandate Status

### M21 — Gate Integrity
**Status**: `🟥 FAIL` (corroborated by both sessions)
**Rationale**: M21 requires "every code path returning a typed result MUST be exercised by at least one test that validates the return type." `GenerateResult` is correctly defined, `ModelGateway.generate()` returns it, and `Oracle.talk()/summon()` consume it — but:
- **Zero `isinstance(result, GenerateResult)` contract tests exist** across the entire test suite
- The closest test (`test_oracle_response_has_all_required_fields` at `test_sovereign_loop.py:224`) checks `OracleResponse` fields, not `GenerateResult`
- The `GenerateResult` fields `latency_ms` and `model_used` have **ZERO** test coverage
- All 7 provider backend mocks return `str` — architecturally correct at the provider boundary, but no test validates the wrapping layer

**Session Assessment**:
| Source | What It Said | Verified? |
|--------|-------------|-----------|
| MaKaLi Sprint C | "Ratified M21 at D-kal-129, fixed GenerateResult dataclass" | ✅ Correct — structural fix applied, no tests |
| Deep-Siphon | "0/24 contract tests exist, 7+ false positives" | ✅ Verified — zero contract tests. "False positives" = tests mock provider.generate() with `str`, not `GenerateResult`. This is DESIGN-LEVEL: providers return `str\|None`, ModelGateway wraps. The false positives exist at the Gateway boundary, not the provider boundary. |

**Gap**: The 24-test plan in DEEP_SIPHON_M21_AUDIT.md is comprehensive but ambitious. It calls for:
- T1 (3 schema tests) — can exist now, no code changes needed
- T2 (9 provider tests) — **requires provider return type change** from `str | None` → `GenerateResult`. This is an architectural redesign of 7 backends.
- T3 (5 pipeline tests) — can exist after code changes
- T4 (4 edge case tests) — can exist after code changes
- T5 (3 provenance tests) — can exist after code changes

**Path to Green**: Minimum viable path:
1. **Phase 1 (immediate, 0 code changes)**: Add 3 schema tests (T1.1-T1.3) asserting `isinstance(result, GenerateResult)` and field types on `ModelGateway.generate()` return. Target: `tests/test_contract_generate_result.py`. **~30 min effort.**
2. **Phase 2 (requires code)**: Provider metadata capture (ICS-F v1.0 fields) + 12 contract tests. This is the full Deep-Siphon Sprint 1+2 work.
3. **Gate-Out**: T1.1-T1.3 must exist and pass **before** any metadata extraction code lands.

---

### M22 — Response Provenance
**Status**: `🟡 CONDITIONAL PASS` (divergent assessments)
**Rationale**: The runtime code correctly propagates `provider_name`:
- `ModelGateway.generate()`: Sets `provider_name=success_provider.name` (line 903) or `"fallback"` (line 910)
- `ModelGateway.generate_antigravity()`: Sets `provider_name="antigravity"` (4 call sites, lines 1198-1246)
- `Oracle.talk()`: Reads `res.provider_name` as `backend` (line 592), propagates to `OracleResponse.backend` and trace logging (lines 595-626)
- `Oracle._route_by_domain()`: Same pattern (lines 662-696)
- `gateway_server.py` (MCP Hub): Logs `provider_name` at line 112

**MANDATES_SYNC.md claims**: "PARTIAL — gateway_server.py logs provider; background.py workers don't."
- This is a **partially stale assessment**. The `mcp_servers/omega_hub/background.py` file handles awareness pruning, lock reaping, handoff reaping, and metrics — NONE of these functions deal with provider responses. This is infrastructure management, not inference. There is no `provider_name` to propagate.
- The `BackgroundResearcherLoop` (`workers/background_researcher/loop.py`) uses direct HTTP calls (Firecrawl, Jina, Exa, httpx) — it does NOT go through `ModelGateway.generate()`. The `resp.text` references (lines 148, 175, 340) are `httpx.Response.text`, not `GenerateResult.text`.

**Session Assessment**:
| Source | What It Said | Verified? |
|--------|-------------|-----------|
| MaKaLi Sprint C | "Added provider_name field to GenerateResult" | ✅ Correct |
| Deep-Siphon | "No provenance validation tests exist" | ✅ Verified — 0 tests assert `result.provider_name == "expected_provider"` |

**Actual Gap**: The runtime code is CORRECT for the `Oracle.talk/summon()` path. The provenance gap exists at:
1. **Test level**: No test asserts `result.provider_name == "mock"` after generation. This is the critical missing link.
2. **BackgroundResearcher**: Doesn't use `GenerateResult` — uses direct HTTP calls. This is a separate architectural path that doesn't need M22 compliance (it doesn't go through model inference).
3. **Observability logging**: `oracle.py` correctly passes `backend` to `trace.log()` and `trace.record()` — but there's no test that verifies the log entries contain `provider_name`.

**Path to Green**: 
1. Add 3 provenance tests (T5.1-T5.3 from Deep-Siphon spec) asserting `provider_name` matches serving provider
2. No code changes needed for the `Oracle.talk/summon()` path — the wiring is correct
3. The "background.py" gap in MANDATES_SYNC.md should be **clarified** — it refers to background workers that don't exist or don't need M22. Recommend updating MANDATES_SYNC.md to reflect the accurate gap.

---

## Cross-Session Summary

| Session | M21 Action | M22 Action |
|---------|-----------|-----------|
| **MaKaLi Sprint C** | Ratified D-kal-129; fixed `GenerateResult` dataclass with `provider_name` field; updated 6 call sites across 6 files | Added `provider_name` field; wired `oracle.py` to propagate from `GenerateResult.provider_name` → `OracleResponse.backend` → trace logs |
| **Deep-Siphon** | Found 0/24 contract tests exist; identified 7+ tests with false confidence; designed 5-tier test plan (388 lines) | Found 0 provenance validation tests; identified background.py misdocumentation; noted OpenRouter model field gap |
| **RECONCILIATION** | **Synthesis**: Structural code is correct (GenerateResult exists, wired through). Contract test enforcement is **zero**. Deep-Siphon's 24-test plan is comprehensive but 12 of 24 tests (T2) require changing provider return types — scope this correctly. | **Synthesis**: Runtime provenance is correct for the main `oracle.py` path. MANDATES_SYNC.md's "background.py workers" gap is stale/misidentified. Real missing piece: no test asserts `provider_name` correctness. |

---

## Key Findings

### 1. Structural Code is M21/M22 Compliant — Enforcement is Zero
The `GenerateResult` dataclass is correctly defined and wired through `ModelGateway.generate()` → `Oracle.talk/summon()` → `OracleResponse` → trace logs. The runtime code path is clean. What's missing: **any test that verifies the contract is kept**.

### 2. Deep-Siphon's 24-Test Plan is Ambitious — But 12 Tests Require Provider Redesign
- **T1 (3 tests)**: Can be written NOW with zero code changes. Greenest path.
- **T2 (9 tests)**: Requires changing all 7 provider backends to return `GenerateResult` instead of `Optional[str]`. This is architecturally significant — it merges the provider/gateway abstraction boundary. **Recommend challenging this scope**: the `Optional[str]` return type at the provider boundary is intentional. M21 can be satisfied by testing `ModelGateway.generate()` return type, not each backend individually.
- **T3-T5 (12 tests)**: Can be written after metadata capture is implemented.

### 3. MANDATES_SYNC.md M22 Gap is Stale/Misidentified
The document claims "background.py workers don't propagate provider_name." After reading `mcp_servers/omega_hub/background.py` (267 lines) and `workers/background_researcher/` (the actual inference-adjacent background worker), neither file has a gap:
- `mcp_servers/omega_hub/background.py`: Infrastructure management (pruning, reaping, metrics). Has no provider response to propagate.
- `workers/background_researcher/loop.py + search_fleet.py`: Direct HTTP calls to search APIs (Firecrawl, Jina, Exa). Does NOT go through `ModelGateway.generate()`.

**Recommendation**: Update MANDATES_SYNC.md line 108 from "background.py workers don't" to "No provenance validation tests exist (verified: main oracle() path propagates correctly). Background workers don't use ModelGateway — separate architectural path."

### 4. `GenerateResult.latency_ms` and `model_used` Have Zero Coverage
Two `GenerateResult` fields that exist today — `latency_ms` and `model_used` — have no tests anywhere. `latency_ms` is set at lines 900-912 but never read. `model_used` is set at lines 1226, 1237, 1250 but never read.

### 5. The "False Positive" Finding is Nuanced
Deep-Siphon identified 7+ tests as "false positives." These mock `provider.generate()` (individual backend level) with `return_value="string"`. Since individual backends return `Optional[str]` by design, these mocks are **architecturally correct** at their level. The vulnerability is at the `ModelGateway.generate()` boundary — if someone changes its return type, no test catches it. The fix is 3 contract tests on `ModelGateway.generate()`, not changing all backend mocks.

---

## Recommendations

### Priority 1 (This Session — 0 Code Changes)
1. **Create `tests/test_contract_generate_result.py` with 3 schema tests**:
   - `test_generate_result_has_required_fields`: asserts `hasattr(gr, 'text')`, `hasattr(gr, 'provider_name')`, `hasattr(gr, 'is_cloud')`
   - `test_generate_result_types_are_correct`: `isinstance` checks on all fields
   - `test_generate_result_defaults_are_none_or_zero`: verifies optional fields default correctly
   - Test pattern: construct `GenerateResult(text="x", provider_name="m", is_cloud=False)` directly, don't go through pipeline
2. **Add one pipeline contract test** to `test_model_gateway.py`: `isinstance(await gateway.generate(...), GenerateResult)`

### Priority 2 (This Session — Update MANDATES_SYNC.md)
3. **Correct the M22 finding**: Update line 108 from `"background.py workers don't propagate provider_name"` to `"No provenance validation tests exist. Main oracle() path verified correct. Background workers use separate HTTP path (not ModelGateway)."`

### Priority 3 (Next Session — Partner with Deep-Siphon)
4. **Scope T2 provider tests correctly**: Challenge the requirement that all 7 backends return `GenerateResult`. The provider boundary returning `str | None` is intentional. Instead, T2 should test that `ModelGateway.generate()` wraps provider `str` into `GenerateResult` correctly.

5. **Implement remaining contract tests** after Deep-Siphon metadata capture lands:
   - T3: Pipeline propagation tests
   - T4: Edge case tests
   - T5: Provenance tests (assert `provider_name == "mock"`)

### Priority 4 (Low Urgency)
6. **Clarify `GenerateResult.latency_ms` and `model_used`** — either write tests that verify these fields, or deprecate them. Currently they exist but are unused/untested.

---

## Appendix: Violation Records

### M21 Violations (Zero Contract Tests)
| Violation | Location | Severity | Fix |
|-----------|----------|----------|-----|
| No `isinstance(result, GenerateResult)` test | All test files | 🔴 HIGH | Add T1.1-T1.3 contract tests |
| `latency_ms` untested | `GenerateResult` dataclass | 🟡 MED | Add coverage |
| `model_used` untested | `GenerateResult` dataclass | 🟡 MED | Add coverage or deprecate |

### M22 Compliance Map
| Path | Route | Has `provider_name`? | Tested? |
|------|-------|:---:|:---:|
| `ModelGateway.generate()` → success | `success_provider.name` | ✅ | ❌ |
| `ModelGateway.generate()` → fallback | `"fallback"` | ✅ | ❌ |
| `ModelGateway.generate_antigravity()` → success | `"antigravity"` | ✅ | ❌ |
| `ModelGateway.generate_antigravity()` → rate limit | `"antigravity"` | ✅ | ❌ |
| `ModelGateway.generate_antigravity()` → auth error | `"antigravity"` | ✅ | ❌ |
| `Oracle.talk()` → `res.provider_name` | → `OracleResponse.backend` | ✅ | ✅ (functional, not contract) |
| `Oracle._route_by_domain()` → `res.provider_name` | → `OracleResponse.backend` | ✅ | ✅ (functional, not contract) |
| Gateway server proxy_request | Logs `provider_name` | ✅ | ❌ |
| Background workers | N/A (infrastructure) | N/A | N/A |

---

*Audit by: Verity (Unified Compliance + Gnosis)*
*Data sources: MaKaLi Sprint C, Operation Deep-Siphon, source code review*
*End of reconciliation — verdict: 🟥 FAIL (enforceable), but path to 🟢 is well-defined and incremental.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
