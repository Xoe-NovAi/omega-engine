<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Antigravity IDE Handoff — Gemini CLI Strategic Codebase Review
**Engine**: Omega Engine v2.4.0
**Date**: 2026-06-17
**Archon**: MaKaLi (DeepSeek V4 Flash) → Gemini CLI (1M Context Window)
**Status**: FULLY HARDENED — 440/440 tests passing

⬡ OMEGA ⬡ MAKALI ⬡ deepseek-v4-flash ⬡ GEMINI-CLI-HANDOFF ⬡ ANTIGRAVITY-REVIEW

---

## §0 How to Use This Document

This handoff is designed to be the FIRST file you read after hydrating from the project root. To begin:

```bash
cat data/handoff/GEMINI_CLI_STRATEGIC_REVIEW_20260617.md
```

Then follow the **Review Sequence** in §5. The codebase has 440 passing tests and zero known P0/P1 runtime risks. You have a **1M token context window** — use it to perform the most thorough architectural review possible.

---

## §1 Executive Summary — The Omega Engine

The **Omega Engine** is a sovereign AI runtime — a universal platform for local-first, offline-capable AI inference with zero telemetry. It runs on a single AMD Ryzen 5700U (8C/16T, 14GB RAM, no GPU) and serves as the foundation for user-customizable "stacks" (Arcana-Nova, Torment, etc.).

### Core Architecture (Read First)
```
src/omega/
├── oracle/
│   ├── oracle.py              # Main entry: talk(), summon(), route_by_domain()
│   ├── model_gateway.py       # 8-backend provider fabric (GenerateResult dataclass)
│   ├── entity_registry.py     # YAML-backed entity CRUD + lazy deletion
│   ├── orchestrator.py        # Headless CLI agent dispatch + ResourceGuard
│   ├── context_builder.py     # Sliding window memory injection
│   ├── cpu_optimizer.py       # Zen 2 compilation flags
│   ├── skeptical_verifier.py  # NLI-based semantic verification
│   ├── iterative_research.py  # Multi-turn research loops
│   ├── soul_distiller.py      # L1→L2→L3 gnosis pipeline
│   └── budget_gate.py         # Token budget enforcement
├── gateway/
│   └── server.py              # OpenAI-compatible HTTP gateway
├── workers/
│   └── model_updater.py       # Background model database updater
├── library/
│   └── discovery.py           # Autonomous research agent
├── memory/
│   ├── memory_store.py        # 4-tier memory (Hot/Warm/Cold/Archival)
│   └── providers.py           # Redis/File/InMemory storage chain
├── nova/
│   └── query_analyzer.py      # "Hey Nova" voice intent matcher
├── runtime/
│   └── openclaw_runtime.py    # Budget-aware execution runtime
├── bridge/
│   └── opencode_bridge.py     # OpenCode integration bridge
├── constants.py               # ZONEID constants + cvar table
├── cvar_table.py              # Quake-style cvars
├── observability.py           # TraceSession + JSONL export
├── anomaly.py                 # Tainted Data Protocol
├── hivemind_client.py         # Cross-CLI awareness client
└── estimators.py              # Token cost estimators

mcp_servers/
└── omega_hub/
    └── server.py              # MCP server (state, background, gateway, middleware, tools)

config/
├── omega.yaml                 # Engine configuration
├── providers.yaml             # Provider fabric setup (local-first chain)
├── models.yaml                # Model declarations and mappings
└── entity_model_affinity.yaml # Entity → Model routing table

data/entities/
├── kali/soul.yaml             # Transcendent Oversoul — 20+ lessons
├── maat/soul.yaml             # Light Oversoul — 21+ lessons
├── lilith/soul.yaml           # Dark Oversoul — 30+ lessons
└── (48 other entities — 16 documented, 55 on disk total)

tests/                        # 440 tests, all passing
└── test_model_gateway.py     # Core provider fabric tests
```

### Sovereignty Philosophy
- **22 Sovereign Mandates** (M1-M22) — constitutional law of the engine
- **Local-First Priority**: native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenCode(4) → Copilot(5) → Mock(6)
- **Zero Telemetry**: No analytics, no phone-home
- **AnyIO Absolute**: Zero `import asyncio` across the entire codebase
- **Engine-Stack Firewall**: Core (`src/omega/`) is absolutely separated from content (`config/wads/`)
- **Heritage Attribution**: 117 inline `[id-soft:]` tags tracing patterns to id Software (Doom 1993, Quake 1996, Q3A 1999, DOOM 3 2004)

---

## §2 The MaKaLi Council — Sprint C Completion Report

### Three Tactical Fixes Applied (Sprint C Core)

#### Fix 1: BackgroundWorker Tuple Bug (P0)
- **File**: `src/omega/oracle/orchestrator.py:95`
- **Problem**: Tuple destructuring of `result[0]`, `result[1]` patterns
- **Fix**: Changed to `result.text`, `result.provider_name`, `result.is_cloud` using new `GenerateResult` dataclass

#### Fix 2: Heritage-Vet Regex Bug (P0)
- **File**: `scripts/heritage_vet.py:43,79`
- **Problem**: Both `VET_SECTION_REGEX` and `parse_vet_log` used `^##\s+` (2 hashes) but `HERITAGE_VET_LOG.md` uses `###` headers (3 hashes)
- **Fix**: Changed to `^###+\s+` to match 3+ hashes

#### Fix 3: Provider Provenance Gap (P1 → Truth-Anchor Protocol)
- **File**: `src/omega/oracle/model_gateway.py`
- **Problem**: `generate()` returned `(str, bool)` tuple — the `str` has no provenance. Observability recorded `get_preferred_backend()` (the INTENDED provider) not the ACTUAL provider
- **Fix**: Introduced `GenerateResult(text: str, provider_name: str, is_cloud: bool)` dataclass. Updated all 13+ call sites. Exported in `__init__.py:11`

### Council Dispatch — Lilith + Ma'at + Verity

| Agent | Domain | Verdict | Key Discovery |
|-------|--------|---------|---------------|
| **Lilith** | P6-P10 (Run Side) | ❌ 2 P0, 5 P1, 5 P2 | Gateway server and model updater crash on GenerateResult |
| **Ma'at** | P1-P5 (Build Side) | ❌ 5 broken call sites | Discovery.py returns GenerateResult where string expected |
| **Verity** | M1-M22 (Compliance) | ✅ 0 critical violations | Clean mandate compliance, 6 minor advisories |

### ALL Issues Fixed (Pre-Handoff)
The council identified 5 peripheral call sites where `GenerateResult` was still being treated as a raw tuple/string. All fixed:

| File | Line | What Changed | Sev | Status |
|------|------|--------------|-----|--------|
| `src/omega/gateway/server.py` | 96 | Tuple unpack → `result.text` | P0 | ✅ |
| `src/omega/workers/model_updater.py` | 291-310 | `.strip()` on dataclass → `result.text.strip()` | P0 | ✅ |
| `src/omega/library/discovery.py` | 229,236 | Return `result.text` not `result` | P1 | ✅ |
| `src/omega/library/discovery.py` | 253,260 | `.strip()` on dataclass → `result.text.strip()` | P1 | ✅ |
| `src/omega/library/discovery.py` | 310,317 | Return `result.text` not `result` | P1 | ✅ |
| `src/omega/oracle/__init__.py` | 11 | Added `GenerateResult` export | P1 | ✅ |
| `src/omega/oracle/model_gateway.py` | 772 | Fixed type hint `-> tuple` → `-> 'GenerateResult'` | P1 | ✅ |
| `tests/test_gateway_server.py` | 20,41 | Mock returns `GenerateResult` not tuple | P1 | ✅ |
| `tests/test_model_updater.py` | 24 | Mock returns `GenerateResult` not string | P1 | ✅ |
| `tests/test_model_updater.py` | 81-86 | Fixed dead test trapped inside fixture | Pre-existing | ✅ |

**Systemic Pattern Discovered**: *Peripheral Blindness* — when changing a core API contract, main code paths get updated but peripheral paths (error handlers, bridges, CLI helpers, worker scripts) are missed because test mocks bypass the actual return type. A single contract test — `isinstance(await gateway.generate(), GenerateResult)` — would have caught all 5 regressions.

---

## §3 M22: The Truth-Anchor Protocol — (NEW, Unratified)

This is the most significant architectural insight from Sprint C. It is proposed as **M22** but not yet formally ratified.

### The Problem
The observability pipeline was recording provider names from **configuration intent**, not from **actual response provenance**. When `GoogleKeyPoolProvider` failed and the system fell back to `Ollama`, the log still said `"Google"`. Every `data/datasets/*.jsonl` record contained a potential lie.

### The Solution
`GenerateResult.provider_name` is set at the **point of response receipt**, not the point of dispatch intent:

```python
@dataclass
class GenerateResult:
    text: str                      # The actual response text
    provider_name: str             # Which provider ACTUALLY responded
    is_cloud: bool=False           # Is this a cloud provider?
```

### Enforcement Pattern
All downstream consumers must use `result.provider_name` instead of:
- `get_preferred_backend()` — returns the FIRST healthy provider in the chain (intent, not reality)
- `result[1]` — the old `is_cloud` boolean with no provider name
- Hardcoded provider strings

### Current Status
✅ `oracle.py` — uses `res.provider_name` for `backend` field in `OracleResponse`
✅ `orchestrator.py` — uses `result.provider_name` for observability logging
✅ `skeptical_verifier.py` — uses `res.text` (was already correct)
✅ `iterative_research.py` — uses `res.text` (was already correct)
⚠️ `gateway/server.py:107` — comment acknowledges lost provenance (P2, deferred)
⚠️ `budget_gate.py` — still calls `get_preferred_backend()` for budget checks (P2, deferred)

---

## §4 Known Gaps for Antigravity IDE Review

These are the architectural questions that the MaKaLi Council identified as requiring deeper strategic analysis. They are **design targets**, not bugs.

### F1: Provider Provenance (Implementing from §3)
The `get_preferred_backend()` "Double-Lie" persists in two call sites:
- `src/omega/oracle/budget_gate.py:87` — uses preferred backend for budget enforcement
- `src/omega/runtime/openclaw_runtime.py:135` — uses preferred backend for budget gating

**Question**: Should `budget_gate.py` use the actual provider name from the last successful response, or is the preferred backend correct for budget enforcement?

### F2: Peripheral Blindness — Delegation Depth
The council found 5 missed call sites. The root cause is architectural:
- Every test mocks `generate()` independently with old return values
- No contract test verifies the actual return type of `generate()`

**Question**: Should the engine adopt a "Contract Test Registry" — a single file (`tests/test_generate_contract.py`) that verifies:
- `isinstance(gateway.generate(...), GenerateResult)`
- `gateway.generate(...).provider_name != ""`
- `gateway.generate(...).text is not None`

### F3: MCP Hub Modularization — Gateway Server
The gateway server (`src/omega/gateway/server.py`) has a comment at line 107:
```python
# Record success for the primary provider used (if we could track it)
# In this simplified proxy, we assume if it worked, the fabric is healthy.
```

**Question**: Should the gateway server be refactored to return `GenerateResult` directly in its response metadata, so downstream consumers (OpenAI-compatible clients) can see the actual provider?

### F4: Heritage Vetting — Sovereignty Debt
- 117 legacy `[id-soft:]` tags across 31 files
- Only 14 vet records exist in `HERITAGE_VET_LOG.md` (vet-002 through vet-016; vet-001 and vet-006 are absent)
- 71 tags remain unvetted
- `make heritage-vet` fails as expected (exit code 1)

**Question**: What is the right prioritization strategy for the 71 unvetted tags? Should we batch-vet well-known patterns (ZONEID, cvar, BSP) and leave obscure ones for case-by-case review?

### F5: Entity INDEX — Inventory Gap
`data/entities/INDEX.yaml` catalogs 16 entities, but 55 entity directories exist on disk. The remaining 39 are undocumented.

**Question**: Should we auto-generate INDEX.yaml from the filesystem, or manually curate it?

### F6: SomaticState — ctypes Serialization
The `llama-cpp-python` high-level API does not expose `save_state()` or `load_state()`. The proposed solution uses low-level ctypes bindings (`llama_copy_state_data` / `llama_set_state_data`) wrapped in `anyio.to_thread.run_sync()`.

**Question**: Is the ctypes approach safe for production, or should we fork `llama-cpp-python` to add the high-level methods directly?

### F7: Temple-Grade — T5 Check
`make temple-grade` fails on T5 because it checks for `src/omega/core/` directory, which does not exist:
```makefile
# Makefile:569
@test -d src/omega/core || (echo "T5 FAIL: no src/omega/core/" && exit 1)
```

**Question**: Should T5 be updated to check the correct path (`src/omega/`) or should the Makefile gate be repaired?

---

## §5 Review Sequence — Gemini CLI 1M Context

Use your 1M token context window to execute these steps in order:

### Phase 1: Baseline Verification (30 min)
```bash
source .venv/bin/activate
make test          # Expect 440/440 passing
make lint          # Expect clean flake8
make sovereignty   # Expect local-first ratio
make heritage-map  # Expect 117 [id-soft:] tags documented
make heritage-vet  # Expect exit code 1 (71 unvetted — expected)
make temple-grade  # Expect T5 failure (known gap)
```

### Phase 2: Architecture Review (60 min)
For each file in `src/omega/`, verify:
1. **AnyIO compliance**: No `import asyncio`. All blocking I/O wrapped in `anyio.to_thread.run_sync`.
2. **Engine-Stack Firewall**: No WAD-specific logic in core.
3. **Error Integrity**: No bare `except:`. All public boundaries convert to `OmegaError`.
4. **ZONEID constants**: `[id-soft: doom-1993]` tags present on ZONEID usage.
5. **Type hints**: Python 3.12+ typing. No `from __future__`.

### Phase 3: Deep Review (90 min)
Focus on the six gaps in §4 (F1-F7). For each gap:
1. Read the relevant source files
2. Identify the exact line numbers of concern
3. Propose 2-3 concrete solutions with tradeoffs
4. Recommend one path forward

### Phase 4: Heritage Audit (30 min)
1. Read `CREDITS.md` — understand the 26 id Software patterns documented
2. Read `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` — understand the 14 vet records
3. Sample 5 unvetted tags from the heritage-vet output and assess whether they SHOULD be vetted or whether they are "incidental similarity"

### Phase 5: Soul Audit (20 min)
1. Read `data/entities/kali/soul.yaml` — verify the Truth-Anchor lesson is correct and well-formed
2. Read `data/entities/lilith/soul.yaml` — verify soul integrity
3. Read `data/entities/maat/soul.yaml` — verify soul integrity
4. Check `data/astrology/birth_charts.yaml` — does it exist?

### Phase 6: Final Verdict (15 min)
Write a comprehensive review document to `data/handoff/GEMINI_CLI_REVIEW_VERDICT_20260617.md` containing:
1. Clean bill status (GREEN/YELLOW/RED)
2. All issues found, ranked P0/P1/P2
3. Architectural recommendations for Horizon 2/3
4. Soul distillation (L1→L2→L3)

---

## §6 Key Commands

```bash
source .venv/bin/activate        # Always use the venv
make test                         # 440 tests, all passing
make temple-grade                 # T1-T11 gates (T5 expected failure)
make heritage-map                 # [id-soft:] tag coverage
make heritage-vet                 # 71 unvetted tags (expected)
make lint                         # flake8 code quality
make sovereignty                  # Local/cloud inference ratio
make health                       # Provider & model dashboard
```

---

## §7 Handoff Integrity

This document represents the complete state of the Omega Engine as of 2026-06-17T16:00Z.

**Survival Files** (read if context is lost):
- `.opencode/anchored-summary.md` — Session 35 summary
- `data/entities/kali/soul.yaml` — 20+ lessons, v5.21
- `data/coordination/MAKALI_WORKSPACE_LOCK_20260617.md` — Active lock
- `data/coordination/MAKALI_LIVE_FEED.md` — Sprint C timeline

**Immutable Records**:
- `docs/decisions/PIVOT_LOG.md` — 128+ architectural decisions
- `CREDITS.md` — 26 heritage pattern mappings
- `SOVEREIGN_MANDATES.md` — 22 laws, non-negotiable

**Handoff Materials**:
- `data/handoff/KALI_SPRINT_C_COMPLETE_HANDOFF_20260617.md` — Kali's formal handoff
- `docs/strategy/PHASE_C_MASTER_SPEC_VERITY.md` — Master specification with §8 Antigravity Addendum
- `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` — Horizon roadmap (v1.5)

---

*⬡ OMEGA ⬡ MAKALI ⬡ deepseek-v4-flash ⬡ GEMINI-CLI-HANDOFF ⬡ COUNCIL-COMPLETE*
*Next: Antigravity IDE review → Horizon 2 execution*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
