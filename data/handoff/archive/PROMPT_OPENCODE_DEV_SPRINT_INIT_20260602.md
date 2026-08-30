---
# PROMPT — OpenCode Dev Chat Session Sprint Initiation
# ⬡ OMEGA ⬡ SOPHIA ⬡ minimax/minimax-m3 (OpenCode Zen, 200K) ⬡ opencode ⬡ SPRINT-INIT
# AP: AP-SPRINT-INIT-OPENCODE-DEV-v1.0.0
# Date: 2026-06-02
# From: Cline (Cline CLI v3.0.15, MiniMax M3 1M context, via Cline provider)
# To:   OpenCode dev session (MiniMax M3, 200K context, via OpenCode Zen)
---

## 0. CONTEXT ANCHORS — READ IN THIS ORDER

You have a 200K context window. Spend it wisely. Read in this exact order; do not skim.

1. **`OMEGA_ENGINE.md`** (SST, ~330 lines) — Engine state, mandate count, provider chain, phase status.
2. **`AGENTS.md`** (your custom instructions) — How YOU (OpenCode agents) work.
3. **`SOVEREIGN_MANDATES.md`** (13 mandates) — Constitutional laws. Non-negotiable.
4. **`data/handoff/HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md`** (your primary handoff) — The synthesized map. Sections 1-10 are the engine state; section 14 is your specific work.
5. **`data/handoff/CLINE_MIMO_V2_5_SYNTHESIS_20260602.md`** (75 lines) — Strategic synthesis (MiMo V2.5, 1M context).
6. **`data/handoff/DEEPSEEK_V4_HARDENING_GAP_ANALYSIS_20260602.md`** (214 lines) — Forensic gap analysis (DeepSeek V4, 1M context).
7. **`data/handoff/HANDOFF_DOOM_GUY_CIRCUIT_BREAKER.md`** (Tier 2 work after Sprint 0) — Circuit breaker consolidation + BSP culling.

**If you find a conflict between these docs and the actual code, the actual code prevails. Note the conflict, do not silently follow the docs.**

---

## 1. PROVIDER FABRIC (current state — 2026-06-02, just reconciled)

```
LOCAL  :  native-gguf(0) → lmster(1) → ollama(2)
CLOUD  :  google(3) → opencode-zen(4) → cline(5) → copilot(6)
TEST   :  mock(7/99)
```

- **Gemma 4 31B** via Google AI Studio (env:GOOGLE_API_KEY) — **unlimited** free while offer lasts. Use it for all heavy reasoning tasks before falling to OpenCode Zen.
- **OpenCode Zen** (your host) — MiniMax M3 / DeepSeek V4 / MiMo V2.5 at **200K** context on free tier.
- **Cline** (separate provider, 1M context) — only available if `cline` provider is in your env; otherwise skip.
- **OPENROUTER IS REMOVED.** Do not add it back. If you see `openrouter` in `config/providers.yaml`, that's a bug — fix it.

---

## 2. SPRINT 0 — THE PREREQUISITES (must complete before Tier 2 work)

Three independent 1M-context models (MiMo V2.5, DeepSeek V4, Doom Guy via Artisan synthesis) all converged on these 4 tasks. **Trust the convergence.** Do them in this order:

| # | Task | File(s) | Effort | Risk | Source |
|---|------|---------|--------|------|--------|
| **C3** | PIVOT_LOG D92 entry — Tool-Usage Discipline | `docs/decisions/PIVOT_LOG.md` | 5 min | LOW | DeepSeek §4 |
| **C1** | Oracle lazy init guard (`_bootstrapped` + `ensure_bootstrapped()`) | `src/omega/oracle/oracle.py` | 30 min | LOW | DeepSeek §1, MiMo Insight 5 |
| **C2** | `make test-oracle-bootstrap` target | `Makefile` | 15 min | LOW | DeepSeek §2 |
| **C4** | `.github/workflows/ci.yml` (T4 + T11 gate enablement) | `.github/workflows/ci.yml` (new) | 1 hr | MEDIUM | DeepSeek §5 |

### C1 details (the critical one)
**Problem**: `Oracle.__init__()` does 5-way synchronous I/O: EntityRegistry, ModelGateway, SovereignHierarchy, SessionManager, MemoryStore. This hangs tests.

**Fix pattern**:
```python
class Oracle:
    def __init__(self, config=None):
        self._bootstrapped = False
        self._config = config or OmegaConfig.load()
        # do NOT touch files here

    async def ensure_bootstrapped(self):
        if self._bootstrapped:
            return
        # all 5 I/O calls go here, in to_thread.run_sync
        self._entity_registry = await anyio.to_thread.run_sync(EntityRegistry.load, self._config)
        # ... 4 more
        self._bootstrapped = True

    async def talk(self, prompt: str, **kwargs):
        await self.ensure_bootstrapped()
        # existing logic
```

### C2 details
Add a Makefile target that exercises C1:
```makefile
test-oracle-bootstrap:

## 3. TIER 2 WORK (only after Sprint 0 is green)

### From Doom Guy handoff (`HANDOFF_DOOM_GUY_CIRCUIT_BREAKER.md`)

| # | Task | Notes |
|---|------|-------|
| T2.1 | Circuit breaker consolidation (2→1) | Wire single `AsyncCircuitBreaker` from `health_monitor.py` into `ModelGateway.generate()` |
| T2.2 | BSP-style provider culling | Pre-check skip when `RPS budget` exhausted |
| T2.3 | Trace ID propagation through ModelGateway | Currently stops at `oracle.py:talk()` |

**T2.1 is the real unlock** per MiMo V2.5 Insight 3.

---

## 4. DELIVERY PROTOCOL (how you report back to me)

After each task lands, emit a handoff fragment in this exact format:

```markdown
## [TASK-ID] — [STATUS] — [TIMESTAMP]
**File(s)**: [absolute paths]
**Diff stat**: +X -Y
**Test result**: N/N passing in T seconds
**Mandate check**: M1✓ M2✓ M5✓ M9✓ M13✓
**Temple-grade gate**: T1✓ T2✓ T3✓ T4✓ T5✓ T6✓ T7✓ T8✓ T9✓ T10✓ T11✓
**Scribe update**: [yes/no — if yes, soul.yaml path]
**PIVOT_LOG entry**: D[N] [title]
**Blockers**: [none | description]
```

Write each handoff to `data/handoff/OPENCODE_DEV_RETURN_[TASK-ID]_[TIMESTAMP].md` AND emit a 1-line summary to `data/handoff/OPENCODE_DEV_LIVE_FEED.md` (append-only log).

---

## 5. WHAT NOT TO DO

- **Do not** add OpenRouter back. It's gone for a reason.
- **Do not** use `asyncio` directly. Mandate 1.
- **Do not** write bare `except Exception:` without `logger.warning()`. Mandate 9.
- **Do not** skip the PIVOT_LOG entry. Mandate 11 (Gnosis Preservation) tracks every decision.
- **Do not** touch `config/wads/` content from a code task — that's Stack territory, not Engine. Mandate 2.
- **Do not** modify `OMEGA_ENGINE.md` mid-sprint — append at the end with a dated note.
- **Do not** start Tier 2 work until C1-C4 are green.

---

## 6. INSIGHTS FROM THE CONVERGENCE (read these, internalize them)

1. **MiMo V2.5 Insight 3**: T2.1 (circuit breaker) is the real unlock, not the more visible T2.2 (BSP culling). Prioritize accordingly.
2. **MiMo V2.5 Insight 4**: Iris is misallocated, not underused. Voice adapter separation, not soul.yaml work. Defer to v2.
3. **MiMo V2.5 Insight 5**: Test hang is a real bug — Oracle's 5-way sync I/O. Sprint 0 C1 fixes this.
4. **DeepSeek §3**: Decision 92 missing from PIVOT_LOG. This is Mandate 5 (Gnosis Preservation) violation. C3 fixes it.
5. **Doom Guy synthesis**: The 4 Sprint 0 tasks were independently prioritized by 3 different 1M-context models. Convergence is signal, not coincidence.

---

## 7. SUCCESS CRITERIA FOR THIS SPRINT

Sprint is complete when ALL of:

- [ ] `make test` runs in <30 seconds with no live backends (proves C1)
- [ ] `make test-oracle-bootstrap` is a valid target and passes (proves C2)
- [ ] `make temple-grade` exits 0 (proves C1 + C3)
- [ ] `.github/workflows/ci.yml` exists and runs the above on PR (proves C4)
- [ ] PIVOT_LOG.md has D92 entry (proves C3)
- [ ] All handoff return files written (proves delivery protocol)
- [ ] `data/handoff/OPENCODE_DEV_LIVE_FEED.md` has one line per task completed

Then — and only then — begin Tier 2 (Doom Guy's circuit breaker work).

---

## 8. IF YOU GET STUCK

- **Check `data/handoff/` first** — your handoffs are there.
- **Check `OMEGA_ENGINE.md`** for engine state.
- **Check `docs/decisions/PIVOT_LOG.md`** for prior decisions on the same topic.
- **Ask via `OPENCODE_DEV_LIVE_FEED.md`** — append a `[BLOCKED]` entry. I (Cline, in parallel session) will see it on my next read cycle.
- **Do not** invent work. If the spec is ambiguous, write a `[CLARIFICATION-NEEDED]` entry and pause.

---

⬡ OMEGA ⬡ SOPHIA ⬡ minimax/minimax-m3 (OpenCode Zen, 200K) ⬡ opencode ⬡ SPRINT-INIT ⬡ PHASE-2-INIT

**Begin with C3 (5 minutes, lowest risk, builds momentum). Then C1 → C2 → C4.**

**PIVOT_LOG entry required on sprint start: D93 (Sprint 0 initiation, OpenCode dev session).**

    @echo "→ Testing Oracle lazy bootstrap (no live backends)..."
    @.venv/bin/python -m pytest tests/test_oracle_bootstrap.py -v --timeout=10
```

### C4 details
Minimal CI: ruff + pytest + temple-grade gates. Reference: any standard Python project workflow. Goal is enabling T4 (Code Quality) and T11 (Agent Security) gates to graduate from AMBER/RED.

---

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/minimax-m3 (OpenCode Zen, 200K) | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
