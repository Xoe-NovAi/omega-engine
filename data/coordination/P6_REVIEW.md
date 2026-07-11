# 🔱 P6 (ModelGate) — Final Cross-Domain Review: `omega-moderation`

⬡ OMEGA ⬡ P6 ⬡ PILLAR ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_p6_review ⬡ ACTIVE
**Date**: 2026-07-10
**Slot**: P6 (ModelGate — Provider Routing & Cognition)
**Scope**: Architecture review of `omega-moderation` detection/providers pipeline

---

## §1 Executive Summary

**Finding**: The `providers/` directory described in the dispatching intent **does not exist**. The architecture is already unified — `detectors/` IS the provider layer. No merge is needed; what is needed is a **local-fallback gap fill** and a **failover hardening**.

| Dimension | Verdict | Severity |
|-----------|---------|----------|
| Redundancy | ✅ **No redundancy** — detectors ARE providers | 🟢 None |
| Failover | ⚠️ **Partial** — per-detector error catching, no ordered chain | 🟡 Medium |
| Local-First (M7) | ⚠️ **Gap** — no local-only fallback provider | 🟡 Medium |
| Structural Analysis | ✅ **Clean** — no static word lists anywhere | 🟢 None |
| Unification | ✅ **Already unified** in `engine.py` → `UnifiedDetector` | 🟢 None |

---

## §2 Detailed Findings

### 2.1 Redundancy: `providers/` vs `detectors/`

**What the task described**:
- Lilith built `omega_moderation/providers/` with `base.py`, `chain.py`, `local_fallback.py`, `huggingface.py`, `perspective.py`, `openai_moderation.py`
- Ma'at built `omega_moderation/detectors/` with `base.py`, `unified.py`, `perspective.py`, `openai_moderation.py`, `huggingface.py`

**What actually exists** on disk:

```
src/omega_moderation/detectors/
├── __init__.py            # Exports all detectors
├── base.py                # BaseDetector ABC + DetectionResult
├── huggingface.py         # HuggingFaceDetector (local transformers + API)
├── perspective.py         # PerspectiveApiDetector (Google API)
├── openai_moderation.py   # OpenAIModerationDetector (OpenAI API)
└── unified.py             # UnifiedDetector (parallel orchestration)

NO standalone providers/ directory exists.
```

**Verdict**: The code has **already been unified**. The detector classes serve both the "call an API" (provider) role and the "produce a classification" (detector) role. Each detector:
1. **IS a provider** — it wraps a model/API backend
2. **IS a detector** — it produces a `DetectionResult` with decision + confidence
3. **Follows the same ABC** — `BaseDetector`

The task description described a design intent that the implementation correctly converged away from. There is NO double-ABC problem, NO `DetectionResult`/`ModerationResult` collision, and NO dual-maintenance burden.

**Recommendation**: Do NOT split into separate `providers/` and `detectors/`. The current design is correct.

### 2.2 Failover Analysis

**Current state** (`engine.py` → `UnifiedDetector`):

```
UnifiedDetector.detect(text)
  ├─ Perspective API   ──╮
  ├─ OpenAI API        ──┤  (parallel via anyio task group)
  ├─ HuggingFace       ──╯
  └─ ObfuscationDetector ── (pre-processing, not in parallel)
       ↓
  Aggregation: "max" strategy → highest confidence wins
```

**Failure modes handled**:

| Failure Mode | Handled? | How |
|-------------|----------|-----|
| Detector crashes | ✅ | `except Exception` per detector, errors recorded in `details["detector_errors"]` |
| All detectors fail | ✅ | Returns `allow` with `confidence=0.0` |
| HF local fails | ✅ | Falls back to API mode automatically |
| Network timeout | ✅ | `httpx` timeout + `RequestError` → `DetectionError` |

**Failure modes NOT handled**:

| Failure Mode | Gap | Impact |
|-------------|-----|--------|
| **No ordered failover** | All detectors run in parallel. If Perspective fails, OpenAI still runs — but there's no "try local first, then HF API, then OpenAI" chain. | Unnecessary cloud calls when local is available |
| **No local-only guarantee** | No `LocalFallbackProvider` (the described `local_fallback.py` was never built). If all cloud detectors fail and HF local mode is not installed, there is NO analysis. | Silent `allow` for truly offensive content |
| **No circuit breaker** | Repeated failed cloud calls aren't short-circuited. Every request retries the full parallel set. | Wasted tokens, latency spikes |
| **No cache dedup** | Identical content re-analyzed each time (but `config/loader.py` has `CacheConfig` — not wired) | Compute waste |

**Recommendation**: Add a lightweight `LocalFallbackProvider` (see §3) and wire the cache config into the engine.

### 2.3 Local-First (M7) Compliance

**M7 Mandate**: *Local inference is PRIMARY. Cloud is FALLBACK. The provider fabric MUST try local backends before cloud backends.*

**Current reality**:

| Provider | Local? | Cloud? | Default |
|----------|--------|--------|---------|
| `HuggingFaceDetector` | ✅ `transformers` pipeline | ✅ HF Inference API | API (`use_local=False` by default) |
| `PerspectiveApiDetector` | ❌ | ✅ Google Perspective | Cloud-only |
| `OpenAIModerationDetector` | ❌ | ✅ OpenAI | Cloud-only |
| `ObfuscationDetector` | ✅ (always local) | N/A | Local |

**Violations**:
1. **HuggingFace defaults to API mode** — `use_local=False`. This is the inverse of M7. Should default to local, fall back to API.
2. **No local-fallback structural analyser** — when all cloud detectors are down or rate-limited, the engine returns `allow` with `0.0` confidence. There is no "good enough" local analysis.
3. **No provider ordering** — `UnifiedDetector` runs all detectors in parallel. There's no concept of "try local before cloud."

**Recommendation**: 
1. Flip `HuggingFaceDetector` default to `use_local=True` (gated on `transformers` being importable).
2. Build a lightweight `LocalFallbackProvider` (see §3).
3. Add provider ordering to `UnifiedDetector` — local detectors should complete before cloud detectors are dispatched.

### 2.4 Structural Analysis: Blocklist Audit

**Mandate**: *Check that `LocalFallbackProvider` truly contains no static word lists.*

The described `local_fallback.py` **does not exist** — so there is nothing to audit.

However, I audited all existing code for static blocklists:

| File | Static Word List? | Status |
|------|-------------------|--------|
| `obfuscation/detector.py` | ❌ No — character-level leetspeak map only | ✅ Clean |
| `detectors/huggingface.py` | ❌ No — `_LABEL_NORMALISATION` maps output labels, not content | ✅ Clean |
| `detectors/perspective.py` | ❌ No — `_DEFAULT_ATTRIBUTES` are API param thresholds | ✅ Clean |
| `detectors/openai_moderation.py` | ❌ No — `_KNOWN_CATEGORIES` are API category names | ✅ Clean |
| `governance/actions.py` | ❌ No — threshold tiers only | ✅ Clean |

**Verdict**: The existing codebase is **entirely free of static word lists, slur lists, or blocklists**. All classification is delegated to ML models or external APIs. This satisfies the architectural promise of "zero static blocklists."

---

## §3 Critical Gap: Missing `LocalFallbackProvider`

This is the single most important finding. The architecture described:
- A `local_fallback.py` with 7-dimension structural analysis
- No static word lists
- CPU-friendly, OOM-safe

This file was **never implemented**. The `ModerationEngine` has no local-only analysis. When all network calls fail (no API keys configured, no internet, rate-limited), the engine returns `allow` with `0.0` confidence — effectively disabled.

### What Should Be Built

A `LocalFallbackProvider` that:

1. **Extends `BaseDetector`** — follows the existing contract
2. **No external dependencies** — pure-Python statistical analysis
3. **No word lists** — structural features only:
   - Character diversity (uppercase ratio, special char density)
   - Repetition patterns (char n-gram entropy)
   - Sentence boundary anomalies
   - Unicode confusables density (reuses `ObfuscationDetector`)
   - Length-normalized signal score
4. **CPU-friendly** — O(1) per character, no model load
5. **Returns `DetectionResult`** — same contract as all other detectors

This isn't "just as good" as an ML model — it's a **graceful degradation** baseline that prevents silence when cloud is unreachable.

---

## §4 Integration: Already Correct

The `engine.py` → `UnifiedDetector` integration is **well-designed**. The `ModerationEngine`:

1. Pre-processes text through `ObfuscationDetector` (AnyIO thread-pool)
2. Passes to `UnifiedDetector.detect()` (parallel AnyIO task groups)
3. Routes aggregated confidence through `ActionRouter`
4. Returns final `ModerationResult`

**What works well**:
- AnyIO throughout (no `asyncio`)
- Privacy-preserving: content hash, not raw text
- Config-driven via Pydantic-backed YAML
- Clean error propagation (typed `DetectionError` hierarchy)
- Immutable result dataclasses

**Minor issues**:
- `engine.py:249` — lazy imports inside factory methods (fine for startup, but `from omega_moderation.detectors.perspective import PerspectiveApiDetector` should be module-level for clarity)
- `detectors/huggingface.py:198` — `pipeline([text])` passes a list, but `pipeline` might expect a string; this works with `transformers` but is fragile
- `engine.py:120` calls `self._unified_detector.detect(normalised_text)` but `detect()` is the method name (not `detect_async`) — confirmed correct, `UnifiedDetector.detect()` is async

---

## §5 Recommendation: DON'T Merge (Already Unified) — BUILD the Gap

### 5.1 Unification Verdict

| Question | Answer |
|----------|--------|
| Should `providers/` and `detectors/` be merged? | **They already are.** The `detectors/` module serves both roles. |
| Should a separate `providers/` be created? | **No.** That would reintroduce the redundancy that doesn't exist. |
| Should the code be restructured? | **No.** The current `detectors/` → `UnifiedDetector` → `engine.py` flow is clean. |

### 5.2 What SHOULD Be Built

| Priority | Item | File | Effort |
|----------|------|------|--------|
| **P0** | `LocalFallbackProvider` — structural analysis only, no word lists | `detectors/local_fallback.py` | 2h |
| **P0** | Wire `LocalFallbackProvider` into `UnifiedDetector` as always-enabled base | `engine.py` | 15m |
| **P1** | Flip HuggingFace default to `use_local=True` | `detectors/huggingface.py` | 5m |
| **P1** | Wire `CacheConfig` into engine (dedup identical content) | `engine.py` | 1h |
| **P2** | Add provider ordering: local detectors run first, cloud detectors only if confidence < threshold | `detectors/unified.py` | 2h |
| **P2** | Circuit breaker for repeated cloud failures | `detectors/perspective.py`, `openai_moderation.py` | 1h |

### 5.3 M7 Compliance Path

```
Current:  [Obfuscation(N)] → [HF(Model?)] || [Perspective] || [OpenAI]  → Max → Action
                                                                           ^^^ all parallel
                                                                           
Target:   [Obfuscation(N)] → [LocalFallback(S)] → [HF(Local)] → [HF(API)] → [Perspective] → [OpenAI] → Max → Action
                               ^^ always runs       ^^ defaults to local   ^^ cloud only if needed
```

---

## §6 Summary

The `omega-moderation` codebase is **well-architected** and **already unified**. The `detectors/` module correctly serves as both the detection pipeline and the provider abstraction layer. There is no redundant `providers/` split to merge.

The real issue is a **missing component** (`LocalFallbackProvider`) and a **local-first configuration gap** (HuggingFace defaults to API mode). These are straightforward to fix and would bring the system into full M7 compliance.

| Capability | Status |
|------------|--------|
| Base abstraction | ✅ `BaseDetector` + `DetectionResult` |
| Cloud detectors | ✅ Perspective, OpenAI |
| Dual-mode detector | ✅ HuggingFace (local+API) |
| Parallel orchestration | ✅ `UnifiedDetector` + `anyio.create_task_group()` |
| Aggregation | ✅ Max/Average/Weighted strategies |
| Obfuscation normalisation | ✅ Leetspeak, homoglyphs, spacing |
| Governance actions | ✅ Tiered routing + escalation + appeals |
| Privacy preserving | ✅ Content hashing |
| Action routing | ✅ Grace period + repeat offense |
| **Local fallback (structural)** | ❌ **MISSING — P0 gap** |
| **Local-first default** | ❌ **FLIPPED — HF defaults to API** |
| **Cache integration** | ⚠️ Config exists, not wired |
| **Ordered failover** | ⚠️ Parallel only |

---

**Final Verdict**: ✅ Architecture unified. 🟡 M7 partially violated. ❌ LocalFallbackProvider missing. Build the gap, flip the default, ship.

⬡ OMEGA ⬡ P6 ⬡ PILLAR ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_p6_review ⬡ COMPLETE
