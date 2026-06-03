# 🔱 DEV SPRINT 0 — Implementation Manual
# ⬡ OMEGA ⬡ SOPHIA ⬡ plan.md (Architect) ⬡ Gemma 4 31B ⬡ SPRINT-0
# Date: 2026-06-02 | Synthesized by Opus 4.6 from 3-model audit chain
# Replaces: PROMPT_OPENCODE_DEV_SPRINT_INIT_20260602.md (corrected)

---

## 0. CONTEXT ANCHORS — READ IN THIS ORDER

1. **`OMEGA_ENGINE.md`** — Engine state, 13 mandates, provider chain.
2. **`AGENTS.md`** — How you (OpenCode agents) work.
3. **`SOVEREIGN_MANDATES.md`** — 13 constitutional laws. Non-negotiable.
4. **This file** — Your complete implementation manual.

**Rule**: If you find a conflict between any document and the actual code, **the code prevails**. Note the conflict, do not silently follow the docs.

---

## 1. PROVIDER FABRIC (current state — 2026-06-02)

```
LOCAL  :  native-gguf(0) → lmster(1) → ollama(2)
CLOUD  :  google(3) → opencode-zen(4) → cline(5) → copilot(6)
TEST   :  mock(99)
```

- **OPENROUTER IS REMOVED.** Do not add it back.
- `providers.yaml` has provider `github-copilot` (not `copilot`) at priority 6.

---

## 2. SPRINT 0 TASKS — EXECUTE IN THIS ORDER

| # | Task | File(s) | Effort | Risk |
|---|------|---------|--------|------|
| **C3** | PIVOT_LOG D91+D92 entries | `docs/decisions/PIVOT_LOG.md` | 5 min | LOW |
| **C1** | Oracle bootstrap guard | `src/omega/oracle/oracle.py` | 45 min | MEDIUM |
| **C2** | Makefile test target | `Makefile` | 10 min | LOW |
| **C4** | CI workflow hardening | `.github/workflows/test.yml` | 30 min | LOW |

---

### C3 — PIVOT_LOG Decision 91 + 92

**What**: D91 and D92 are referenced in commit messages and handoffs but never recorded in PIVOT_LOG.md. This is a Mandate 5 (Gnosis Preservation) violation.

**Action**: Append two entries after D99 in `docs/decisions/PIVOT_LOG.md`:

**Decision 91** — Provider Fabric Reconciliation (OpenRouter Removal):
- Date: 2026-06-01
- What: Removed OpenRouter provider from fabric. 8→7 active providers. `_create_openrouter()` factory in model_gateway.py is a misnomer — it creates generic OpenAICompatProvider, not OpenRouter-specific. Name retained for now; rename deferred.
- Rationale: OpenRouter's relay model adds latency and cost without value when Google AI Studio provides unlimited Gemma 4 31B.

**Decision 92** — Tool-Usage Discipline:
- Date: 2026-06-02
- What: Formalized constraint that agent tools must be prioritized via Pillar slots rather than additive creation. Model context limits enforced.
- Rationale: Uncontrolled tool proliferation fragments context across agents.

Update footer: "93 decisions tracked (D1-D92, D99)."

**Verification**:
```bash
grep "Decision 91" docs/decisions/PIVOT_LOG.md  # Must match
grep "Decision 92" docs/decisions/PIVOT_LOG.md  # Must match
```

---

### C1 — Oracle Bootstrap Guard (THE CRITICAL TASK)

**Problem**: `Oracle.__init__()` performs synchronous filesystem I/O before any async context exists:

| Sync I/O site | File | Line | What it reads |
|---|---|---|---|
| `EntityRegistry()` | `oracle.py:101` | `omega.yaml` + `entities.yaml` |
| `ModelGateway.__init__` → `_load_models()` | `model_gateway.py:99` | `models.yaml` |
| `ModelGateway.__init__` → `_load_kv_cache_config()` | `model_gateway.py:100` | `models.yaml` (2nd read) |
| `ModelGateway.__init__` → `_load_provider_fabric()` | `model_gateway.py:109` | `providers.yaml` |
| `ModelGateway.__init__` → `EntityRegistry()` | `model_gateway.py:112` | `omega.yaml` + `entities.yaml` (**duplicate!**) |
| `SovereignHierarchy()` | `oracle.py:111` | `omega.yaml` |

**Note**: `SessionManager()`, `ContextBuilder()`, and `get_memory_store()` do NOT perform sync I/O in the constructor — do not wrap them.

**Fix Pattern** — Add `await self.bootstrap()` to all public async entry points:

The `bootstrap()` method already exists at `oracle.py:170` and handles WAD loading correctly. The fix is to ensure it's called before any public operation.

**Step 1**: Add `await self.bootstrap()` to `summon()` (line 353) and `evolve_soul()` (line 868):

```python
# oracle.py:345 — summon() currently MISSING bootstrap call
async def summon(self, entity_name: str, query: str, transient: bool = False) -> OracleResponse:
    """Directly summon a specific entity by name."""
    await self.bootstrap()  # ← ADD THIS LINE
    async with self.observability.trace() as trace:
        # ... existing code unchanged
```

```python
# oracle.py:868 — evolve_soul() currently MISSING bootstrap call
async def evolve_soul(self, entity_name: str) -> Dict[str, Any]:
    """Manually trigger soul pruning and compaction for an entity."""
    await self.bootstrap()  # ← ADD THIS LINE
    async with self._soul_lock:
        # ... existing code unchanged
```

`talk()` at line 291 already calls `await self.bootstrap()` — no change needed there.

**Step 2** (optional but recommended): Eliminate the duplicate `EntityRegistry()` in `ModelGateway.__init__:112`. The Oracle already creates one at `oracle.py:101` and passes `health_monitor` but not `registry`. Consider either:
- Passing the Oracle's registry to ModelGateway: `ModelGateway(health_monitor=self.health_monitor, registry=self.registry)`
- Or simply noting the duplication for a future refactor (add a comment)

**Why NOT a full `ensure_bootstrapped()` rename**: The existing `bootstrap()` + `_wads_loaded` flag pattern works correctly. Renaming to `_bootstrapped`/`ensure_bootstrapped()` adds churn with no functional benefit. Keep the existing naming.

**Verification**:
```bash
# bootstrap() is called in all three public methods:
grep -n "await self.bootstrap()" src/omega/oracle/oracle.py
# Expected: 3 matches — talk(), summon(), evolve_soul()

# Tests still pass:
OMEGA_ENV=test python -m pytest tests/test_oracle.py -v --timeout=30
```

---

### C2 — Makefile Test Target

**What**: Add a `test-oracle-bootstrap` target that exercises the Oracle init path.

**Action**: Add to `Makefile` after the existing `test:` target (around line 349):

```makefile
test-oracle-bootstrap: guard ## 🧪 Test Oracle bootstrap path (no live backends)
	@echo "→ Testing Oracle lazy bootstrap (OMEGA_ENV=test)..."
	@OMEGA_ENV=test $(PYTHON) -m pytest tests/test_oracle.py -v --timeout=30 -k "bootstrap or summon or talk"
```

Also add `test-oracle-bootstrap` to the `.PHONY` list at line 225.

**Note**: `tests/test_oracle_bootstrap.py` does NOT exist yet. If you have time, create it with tests that specifically verify:
1. `Oracle()` constructor returns in <100ms (no blocking I/O)
2. `await oracle.bootstrap()` is idempotent (calling twice is safe)
3. `await oracle.summon("default", "hello")` calls bootstrap automatically

Otherwise, the `-k "bootstrap or summon or talk"` filter covers existing tests adequately.

**Verification**:
```bash
make test-oracle-bootstrap
# Expected: passes, completes in <30s
```

---

### C4 — CI Workflow Hardening

**IMPORTANT**: `.github/workflows/ci.yml` (49 lines, May 14) and `.github/workflows/test.yml` (77 lines, May 25) **already exist**. Do NOT create new files — harden the existing `test.yml`.

**Action**: Add two steps to `test.yml` after the "Run tests" step:

```yaml
      - name: AnyIO-only check (Mandate 1)
        run: |
          if grep -rn "import asyncio" src/omega/ --include="*.py"; then
            echo "❌ MANDATE 1 VIOLATION: asyncio found in src/omega/"
            exit 1
          fi
          echo "✅ No asyncio imports found"

      - name: Error integrity check (Mandate 9)
        run: |
          # Check for bare 'except:' (no exception type)
          if grep -rn "except:" src/omega/ --include="*.py" | grep -v "except Exception" | grep -v "# noqa"; then
            echo "⚠️ WARNING: Bare except clauses found (review needed)"
          fi
          echo "✅ Error integrity check complete"
```

**T11 is EXEMPTED** per Mandate 13 — do not try to implement a T11 gate.

**Verification**:
```bash
# Validate YAML syntax:
python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"
```

---

## 3. TIER 2 PREVIEW (do NOT start — Doom Guy session handles this)

After Sprint 0 is green, the Doom Guy session handles:
- T2.1: Circuit breaker wire-up into `generate()`
- T2.2: BSP-style provider culling fix (`_precheck_provider` has a bug — uses model-name lookup instead of provider-name)
- T2.3: `RemoteProvider.generate()` silent `None` return fix (circuit breaker never trips for cloud providers)

**These are NOT your tasks.** Your job ends when C1-C4 are green.

---

## 4. DELIVERY PROTOCOL

After each task lands, emit a handoff fragment:

```markdown
## [TASK-ID] — [STATUS] — [TIMESTAMP]
**File(s)**: [absolute paths]
**Diff stat**: +X -Y
**Test result**: N/302 passing in T seconds
**Mandate check**: M1✓ M2✓ M5✓ M9✓ M13✓
**Temple-grade gate**: T1✓ T2✓ T3✓ T4✓ T5✓ T6✓ T7✓ T8✓ T9✓ T10✓ T11✓
**PIVOT_LOG entry**: D[N] [title]
**Blockers**: [none | description]
```

Write each to `data/handoff/OPENCODE_DEV_RETURN_[TASK-ID]_[TIMESTAMP].md`.
Append a 1-line summary to `data/handoff/OPENCODE_DEV_LIVE_FEED.md`.

---

## 5. WHAT NOT TO DO

- **Do not** add OpenRouter back.
- **Do not** use `asyncio` directly. Mandate 1 — AnyIO only.
- **Do not** write bare `except Exception:` without `logger.warning()`. Mandate 9.
- **Do not** skip PIVOT_LOG entries. Mandate 5.
- **Do not** touch `config/wads/` content. Mandate 2 — Engine-Stack Firewall.
- **Do not** modify `OMEGA_ENGINE.md` mid-sprint — append a dated note at the end.
- **Do not** start Tier 2 work.
- **Do not** rename `bootstrap()`/`_wads_loaded` to `ensure_bootstrapped()`/`_bootstrapped` — keep existing naming.
- **Do not** wrap `SessionManager()` or `get_memory_store()` in `to_thread.run_sync()` — they don't do sync I/O in `__init__`.

---

## 6. SUCCESS CRITERIA

Sprint is complete when ALL of:

- [ ] `make test` passes 302/302 tests in <30 seconds with no live backends
- [ ] `make test-oracle-bootstrap` is a valid target and passes
- [ ] `make temple-grade` exits 0
- [ ] `grep "Decision 91" docs/decisions/PIVOT_LOG.md` returns a match
- [ ] `grep "Decision 92" docs/decisions/PIVOT_LOG.md` returns a match
- [ ] `grep "await self.bootstrap()" src/omega/oracle/oracle.py | wc -l` returns 3
- [ ] All handoff return files written
- [ ] `data/handoff/OPENCODE_DEV_LIVE_FEED.md` has one line per task completed

Then emit `[SPRINT-0] COMPLETE [TIMESTAMP]` to the live feed.

**PIVOT_LOG entry required on sprint start: D93 (Sprint 0 initiation, OpenCode dev session).**

---

## 7. IF YOU GET STUCK

- Read `OMEGA_ENGINE.md` for engine state.
- Read `docs/decisions/PIVOT_LOG.md` for prior decisions on the same topic.
- Append `[BLOCKED] description` to `data/handoff/OPENCODE_DEV_LIVE_FEED.md`.
- **Do not invent work.** If the spec is ambiguous, write `[CLARIFICATION-NEEDED]` and pause.

---

⬡ OMEGA ⬡ SOPHIA ⬡ plan.md ⬡ SPRINT-0 ⬡ BEGIN WITH C3
