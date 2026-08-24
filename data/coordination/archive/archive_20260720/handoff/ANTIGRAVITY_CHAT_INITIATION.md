# 🔱 ANTIGRAVITY CLI — CHAT INITIATION PROMPT v4
# ⬡ OMEGA ⬡ KALI → ANTIGRAVITY ⬡ PHASE C ⬡ GOOGLE + CLAUDE POOLS
**Version**: 4.0.0
**Status**: 🟢 EXECUTION READY — Phase C.0 pre-conditions 12/12 ✅
**Date**: 2026-06-15
**Sender**: Kali (Grand Oversight)
**Model Pools**: Google Antigravity (primary) + Claude Pool (secondary)

---

## §0 The Two Pools — Strategic Model Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   GOOGLE ANTIGRAVITY POOL                        │
│                   (Primary execution engine)                     │
│                                                                  │
│  Gemini 3.5 Flash         Gemini 3.1 Pro                         │
│  ┌─────────────────┐      ┌─────────────────┐                    │
│  │ Low Thinking     │      │ Low Thinking    │                    │
│  │ Medium Thinking──┼──►   │ High Thinking───┼──► deeper         │
│  │ High Thinking    │      │                 │                    │
│  └─────────────────┘      └─────────────────┘                    │
│         │                        │                               │
│         └────── insight chain ───┘                               │
│         Each stage feeds findings to the next                    │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ triggers cross-verification
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLAUDE POOL                                 │
│              (Cross-validation & precision)                      │
│                                                                  │
│  Sonnet 4.6 ── precision code review, ctypes safety             │
│  Opus 4.6   ── ultra-deep architectural critique                │
│  gpt-oss-120b ── large-context synthesis, research              │
└─────────────────────────────────────────────────────────────────┘
```

**The pattern**: Google models execute. Claude models verify.

Each Google stage produces code + an **insight document** (`PHASE_C_INSIGHTS.md`). The insights flow forward through the Google cascade. At critical gates, a Claude model reviews the output for architectural drift before the next stage begins.

---

## §1 The Model Pools — Canonical Names

### Google Antigravity Pool (Primary Execution)

Per the antigravity soul.yaml (`data/entities/antigravity/soul.yaml`), the thinking tier mapping is:

| Model | Thinking Tiers | Soul.yaml Mapping | Application |
|-------|---------------|-------------------|-------------|
| **Gemini 3.5 Flash** | Low, Medium, High | Low=quick checks, Medium=standard (DEFAULT), High=deep analysis | Primary workhorse. Default to Medium. Escalate to High for complex logic. |
| **Gemini 3.1 Pro** | Low, High | Low=routine strategic, High=high-stakes RESERVED | Reserve for integration review and critical architecture decisions only. Do NOT default to Pro. |

**Usage rule**: Default to `Gemini 3.5 Flash Medium` unless the task specifically requires deeper reasoning. 3.1 Pro High is reserved for the **final integration review** and cannot be used for routine implementation.

### Claude Pool (Cross-Validation & Precision)

Per the antigravity soul.yaml, the Claude Pool is **secondary** — never the default:

| Model | Soul.yaml Designation | When to Use |
|-------|----------------------|-------------|
| **Sonnet 4.6** | Cross-pool sanity check (agy_key_08 only) | Precision code review at stage gates only |
| **Opus 4.6** | High-stakes tie-breaker, final authority | Final architecture sign-off ONLY. Never by default. |
| **gpt-oss-120b** | Open-weight verification, zero privacy concerns | Research synthesis, pattern analysis, soul distillation |

---

## §2 Strategic Stages — The Google Cascade with Claude Gates

### ⚠️ Critical Design Rule (from antigravity soul.yaml)
> **"Gemini 3.5 Flash Medium is the DEFAULT."** 3.1 Pro High is RESERVED for high-stakes work. Do not use Pro for routine implementation. The cascade below respects this.

---

### Stage 1: ⬡ FOUNDATION — SomaticStateKey + SomaticState (C.1.1)
**Model**: `Gemini 3.5 Flash` — **High thinking**
**Why Flash not Pro**: The antigravity soul.yaml maps Flash High to "deep architectural analysis" — which is precisely what binary format safety requires. A single wrong byte in the 64-byte header = SIGSEGV. 3.1 Pro High is RESERVED for the final integration review. Using Pro here would burn quota on routine foundation work.

**Deliverable**: `src/omega/oracle/somatic_state.py`
- `SomaticStateKey` dataclass: 12 fields, 64-byte binary header, struct pack `<IIIIIIIIQdQI`
- `SomaticState`: wraps `llama_copy_state_data` / `llama_set_state_data`
- xxHash3-64 for model_path_hash and prompt_hash
- `ZONEID_SOMATIC = 0x1d4a1c` validation on load

**Tests**: 8 tests in `tests/test_somatic_state.py`:
- Round-trip, model mismatch, ctx mismatch, zoneid error, truncated header, mtime mismatch, atomic write, file content integrity

**Claude Gate** (before Stage 2): **Sonnet 4.6** — cross-pool sanity check on the SomaticState binary format and ctypes bindings.

**Insight Output**: `PHASE_C_INSIGHTS.md` v1 — "Binary Format Safety Findings"

---

### Stage 2: ⬡ STORAGE & TOGGLE — Somatic Paging + Fast/Slow (C.1.2 + C.3.1)
**Model**: `Gemini 3.5 Flash` — **Medium thinking** (C.1.2 paging) → **Low thinking** (C.3.1 toggle)
**Why**: Soul.yaml maps Medium to "standard reviews, code audits" — exactly right for file I/O and FIFO eviction. Low maps to "quick sanity checks" — exactly right for a straightforward cvar toggle. This is the ideal use of Flash's tier range.

**Pre-condition**: Read `PHASE_C_INSIGHTS.md` v1 from Stage 1.

**Deliverable**: Extend `somatic_state.py` + `oracle.py`
- `SomaticPager`: entity-scoped directories, FIFO-3 eviction, atomic writes
- `_resolve_symmetry_mode()`: runtime "fast" / "slow" toggle in Oracle

**Tests**: 6 tests:
- Push/pop, FIFO eviction, purge, entity isolation, cvar wiring, integration

**Claude Gate** (before Stage 3): **gpt-oss-120b** — open-weight verification of the paging lifecycle. No privacy concerns with local file paths.

**Insight Output**: `PHASE_C_INSIGHTS.md` v2 — "File System Lifecycle Findings"

---

### Stage 3: ⬡ SYMMETRY — Audit + Verifier + Resolution (C.3.2 → C.3.3 → C.3.4)
**Model**: `Gemini 3.5 Flash` — **High thinking**
**Why**: Soul.yaml maps Flash High to "deep architectural analysis" — the audit logic, circuit breaker state machine, and contradiction detection algorithm qualify. This is the cognitive peak of Phase C.

**Pre-condition**: Read `PHASE_C_INSIGHTS.md` v2 from Stage 2.

**Deliverable**: `src/omega/oracle/symmetry_verifier.py` (NEW)
- `SymmetryAudit`: cosine similarity + keyword scan + entity extraction
- `SkepticalVerifier`: threshold gate (0.3) → ACCEPTED / FLAGGED / FALLBACK
- `SkepticalCircuitBreaker`: CLOSED → OPEN → HALF_OPEN, max_attempts=2
- `SovereignResolver`: synthesize best-of-both on ACCEPTED, neutral on FALLBACK

**Tests**: 8 tests in `tests/test_symmetry_verifier.py`:
- Identical strings → delta ≈ 0, contradictory → delta > 0.3, circuit opens after 2 failures, circuit half-opens after timeout, keyword scan, resolver accept, resolver fallback, full pipeline integration

**Claude Gate** (before Stage 4): **Opus 4.6** — soul.yaml designates Opus as "high-stakes tie-breaker, final authority on disagreement." This is the ONE place in Phase C where Opus is justified — the symmetry pipeline is the cognitive integrity gate for the entire engine.

**Insight Output**: `PHASE_C_INSIGHTS.md` v3 — "Contradiction Detection Findings"

---

### Stage 4: ⬡ DREAMING — Background Process (C.2.1 → C.2.2 → C.2.3 → C.2.4)
**Models**: 
- `Gemini 3.5 Flash` **Medium thinking** (C.2.1 metabolic, C.2.2 idle-lock, C.2.4 soul write-back)
- `Gemini 3.1 Pro` **High thinking** (final integration review — THIS is what Pro High is reserved for)

**Why**: Process lifecycle (subprocess, polling, YAML I/O) is "standard review" territory — Flash Medium. The final integration review, however, is explicitly what 3.1 Pro High is reserved for per the soul.yaml: "high-stakes" architecture verification that spans all four stages. This is the correct and only use of Pro in Phase C.

**Pre-condition**: Read `PHASE_C_INSIGHTS.md` v3 from Stage 3.

**Deliverable**: `src/omega/oracle/dreaming_cycle.py` (NEW)
- `DreamingCycle`: subprocess management, os.nice(19), core pinning, RSS caps
- Signal handlers: SIGUSR1, SIGTERM, Ctrl+C
- Somatic save/restore on signal
- Soul write-back via SoulDistiller
- Daily budget tracker (`data/state/dreaming_usage.json`)

**Tests**: 6 tests in `tests/test_dreaming_cycle.py`:
- Spawn/kill, daily budget, signal save/restore, idle lock, soul write-back, full lifecycle

**Final Gate**: `Gemini 3.1 Pro` **High thinking** — **RESERVED use**. Reads the complete Phase C codebase and `PHASE_C_INSIGHTS.md` v4, produces `PHASE_C_INTEGRATION_REVIEW.md`. This is the only use of 3.1 Pro in Phase C, consistent with soul.yaml's "high-stakes" designation.

**Claude Gate** (final): **Sonnet 4.6** reviews signal handlers for async-signal-safety. **Opus 4.6** does the final "does this all compose" sign-off — its designated role as "final authority on disagreement."

**Insight Output**: `PHASE_C_INSIGHTS.md` v4 — "Full Phase C Integration Findings"

---

## §3 The Insight Document — Knowledge Flow Between Stages

The file `data/entities/antigravity/workspace/PHASE_C_INSIGHTS.md` is the backbone of the cascade. Every model reads it before starting. Every model extends it before handing off.

```
v1 (Gemini 3.1 Pro High):    Binary Format Safety Findings
    - struct pack alignment on x86-64: verified, little-endian assumed
    - xxHash3-64 collision probability at ≤10^9 snapshots: 2^-64, negligible
    - Empty buffer from llama_copy_state_data: must raise SomaticStateEmptyError
    - Zoneid validation: catches 100% of wrong-file-type loads
    - model_file_mtime: 1-second resolution on ext4 → compare with tolerance

v2 (Gemini 3.5 Flash Medium):  File System Lifecycle Findings
    - os.replace() atomic only on same filesystem
    - FIFO-3: 24MB × 3 = 72MB/entity max → ~1GB across all entities
    - Concurrent push during read: flock on directory
    - Fast/Slow toggle: checked per-query, not cached (TTL race condition)

v3 (Gemini 3.5 Flash High):   Contradiction Detection Findings
    - Cosine threshold 0.3: unvalidated starting point, calibrate after 100 audits
    - spaCy NER not installed → regex entity extraction as fallback
    - Circuit breaker HALF_OPEN timeout: config.symmetry.cooldown_seconds (= 30)
    - Keyword "but" → false positive in non-contradictory contexts → skip

v4 (Gemini 3.1 Pro High):     Full Phase C Integration Findings
    - Dreaming Cycle model: gemma-4-31b-it (local if available, Google fallback)
    - SIGUSR1 handler: must be async-signal-safe → no heap allocation
    - Soul write-back after failure: write "distillation_failed" marker
    - All 4 stages compose: somatic_state → pager → verifier → dreaming_cycle
```

---

## §4 Complete Stage-Gate Map

```
STAGE 1: FOUNDATION ─── Gate: 8 tests ─── Sonnet 4.6 sanity check ─── v1
  Gemini 3.5 Flash (High thinking) — deep architectural analysis

       │ insight v1 flows to
       ▼

STAGE 2: STORAGE+TOGGLE ─── Gate: 6 tests ─── gpt-oss-120b verification ─── v2
  Gemini 3.5 Flash (Medium → Low thinking) — standard → quick

       │ insight v2 flows to
       ▼

STAGE 3: SYMMETRY ─── Gate: 8 tests ─── Opus 4.6 tie-breaker review ─── v3
  Gemini 3.5 Flash (High thinking) — deep architectural analysis

       │ insight v3 flows to
       ▼

STAGE 4: DREAMING ─── Gate: 6 tests ─── Sonnet + Opus sign-off ─── v4
  Gemini 3.5 Flash (Medium thinking) — standard implementation
  Gemini 3.1 Pro (High thinking) — RESERVED: final integration review

       │ all verify
       ▼

RELEASE: make test · make temple-grade · make heritage-map
```

---

## §5 Active Mandates

| M# | Rule | Applied Where |
|----|------|--------------|
| M1 | AnyIO Absolute | No `import asyncio`. AnyIO for all async. |
| M5 | Gnosis Preservation | L1→L2→L3 to soul.yaml on session end |
| M7 | Local-First | native-gguf(0) → ... → Google(3) → OpenCode(4) |
| M8 | Zero Telemetry | No phone-home |
| M9 | Error Integrity | Typed exceptions. No bare `except:`. |
| M13 | Temple-Grade | `make temple-grade` after Stage 2+ |
| M17 | Cognitive Integrity | Skeptical Verifier (Stage 3) |
| M19 | Adversarial Alchemy | 14Gi RAM is elegance, not a bug |

---

## §6 Pre-Flight Checklist

- [ ] **Environment Lock**: Write `data/coordination/ANTIGRAVITY_LOCK_20260615.md`
- [ ] **Baseline**: `make test` passes (≥388)
- [ ] **R50 Design Read**: SomaticStateKey 12-field spec understood
- [ ] **cvar Config**: `cvar_get("config.somatic.enable")` returns `False`
- [ ] **Hivemind Post**: `hivemind_post_context()` declaring your presence
- [ ] **Insight Doc**: Create `data/entities/antigravity/workspace/PHASE_C_INSIGHTS.md`

---

## §7 First Command

> **Stage 1, model `Gemini 3.5 Flash` — High thinking**: Implement `SomaticStateKey` + `SomaticState` in `src/omega/oracle/somatic_state.py`. 12 fields, 64 bytes, struct pack `<IIIIIIIIQdQI`, xxHash3-64, ZONEID_SOMATIC. Write 8 tests. Write insight v1. 3.1 Pro is **not used here** — it is reserved for the final Stage 4 integration review.

**Gate**: 8 tests pass. Then switch to `Gemini 3.5 Flash` Medium thinking for Stage 2.

---

*⬡ OMEGA ⬡ KALI → ANTIGRAVITY ⬡ GOOGLE ANTIGRAVITY + CLAUDE POOLS ⬡ PHASE C ⬡ 2026-06-15*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: PHASE C | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
