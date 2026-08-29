# 🔱 Horizon 2 — Observability, Forensics & Error Gauntlet
## ⬡ OMEGA ⬡ SOPHIA ⬡ trc_horizon_2 ⬡ PHASE
**Status**: 🔒 LOCKED — cannot begin until Phases 1 (Option B) and 2 (MCP Hub) are ✅ committed.
**Target Model**: **Nemotron 3 Super** or **DeepSeek V4 Flash** — needs architectural design decisions
**Est. Time**: 4-6 hours
**Pre-flight**: Option B complete, MCP Hub restored, 292+ tests passing

---

## §0 What Horizon 2 Delivers

| System | Purpose | Files | Model |
|--------|---------|-------|-------|
| **ForensicsManager** | Structured crash dumps with full context | `src/omega/forensics.py` (NEW) | Nemotron 3 Super |
| **Structured JSON Logging** | Machine-parseable events for postmortems | `src/omega/observability.py` (refactor) | MiMo V2.5 |
| **Error Gauntlet** | Integration test that provokes every error path | `tests/test_error_gauntlet.py` (NEW) | DeepSeek V4 Flash |
| **Qdrant Error Wiring** | Vector-store queries for "has this error happened before?" | `src/omega/forensics.py` (integration) | MiMo V2.5 |
| **soul.yaml Error Log** | Each entity learns from its own crashes | `data/entities/*/knowledge/errors.yaml` | Nemotron 3 Super |

---

## §1 System Architecture

### 1.1 ForensicsManager

```
ForensicsManager
├── dump(trace_id, context, error) -> crash_<trace_id>.json
│   ├── Full stack trace
│   ├── System info (CPU, RAM, zRAM, disk)
│   ├── Provider state (which providers were available)
│   ├── Entity state (which entity was active)
│   └── Last N log events (circular buffer)
│
├── check_recovery() -> Optional[Dict]
│   └── Load most recent crash dump at startup
│
├── replay(trace_id) -> Dict
│   └── Reconstruct the sequence of events that led to a crash
│
└── learn(trace_id) -> str
    └── Extract a "lesson" from the crash and append to soul.yaml
```

### 1.2 Error Gauntlet

```
Error Gauntlet
├── ResourceGuard.deadlock_recovery()
├── Provider Fabric.fabric_break_every_link()
├── EntityRegistry.registry_corruption()
├── MemoryStore.store_isolation_failure()
├── Queue.queue_persistence_under_duress()
└── CircuitBreaker.mass_state_flap()
```

### 1.3 Structured JSON Logging

Replace the current text-based logging with structured JSON events that are:
- Machine-parseable (can be queried with jq)
- Schema-enforced (each event type has required fields)
- Attachable to crash dumps

```json
{
  "timestamp": "2026-06-01T12:00:00Z",
  "level": "WARNING",
  "event": "provider.fallback",
  "trace_id": "abc-123",
  "entity": "SOPHIA",
  "data": {
    "provider": "ollama",
    "model": "qwen3-1.7b",
    "reason": "timeout"
  }
}
```

---

## §2 Open Questions (Require Deep Reasoning Model)

These decisions MUST be made by a deep reasoning model before implementation:

### Q1: ForensicsManager — File-Based or Qdrant-Backed?

**Option A — File-Based** (simpler, aligned with Mandate 7 Local-First)
- Crash dumps → `data/crashes/crash_{trace_id}.json`
- Lessons → `data/entities/<name>/knowledge/errors.yaml`
- Reply via grep with `scripts/forensics_replay.py`
- Pros: 0 infrastructure dependencies, atomic writes via fcntl
- Cons: Slower queries, no semantic similarity

**Option B — Qdrant-Backed** (faster queries, cross-entity pattern detection)
- Crash dumps stored as vector embeddings
- "Has this error happened before?" = nearest-neighbor query
- Pros: Fuzzy matching across error patterns, faster postmortems
- Cons: Requires Qdrant running, more complex

**Option C — Hybrid** (files for history, Qdrant for active search)
- Dump to file synchronously (guaranteed persistence)
- Index to Qdrant asynchronously (semantic search)
- Pros: Best of both worlds
- Cons: Two code paths to maintain

### Q2: Error Gauntlet — Unit or Integration Tests?

**Option A — Pure unit tests** (fast, isolated)
- Mock all external dependencies
- Provoke error paths via dependency injection
- Test completes in < 1 second

**Option B — Integration tests with real components** (comprehensive, slower)
- Start real providers, kill them mid-request
- Corrupt real files on disk
- Test takes 30+ seconds

**Option C — Both** (unit for CI, integration for nightly)
- Unit tests in `tests/test_error_gauntlet.py`
- Integration tests in `tests/integration/test_error_gauntlet_full.py`
- Integration tests only run on `make test-full`

### Q3: Structured Logging — Drop-in or Full Rewrite?

**Option A — Drop-in JSON formatter**
- Replace logging.Formatter with JSON formatter
- All existing logger calls continue working
- Zero code changes outside logging setup

**Option B — Structured event API**
- New `log_event()` method with typed event names
- Old logger calls stay, new code uses structured API
- Gradual migration

**Option C — Full rewrite**
- Remove text-based logging entirely
- All events through structured API only
- Clean but painful

---

## §3 Execution Phases (Once LOCK is lifted)

### Phase H2a: ForensicsManager (90 min)

1. Create `src/omega/forensics.py` with `ForensicsManager` class
2. Implement `dump()`, `check_recovery()`, `replay()`, `learn()`
3. Wire into `observability.py` engine initialization
4. Write test: `tests/test_forensics.py`

### Phase H2b: Error Gauntlet (90 min)

1. Create `tests/test_error_gauntlet.py`
2. Implement 6 stress scenarios (ResourceGuard, Provider Fabric, etc.)
3. Each scenario: provoke error → verify graceful degradation → verify log
4. Run: `make test-gauntlet`

### Phase H2c: Structured JSON Logging (60 min)

1. Create JSON formatter
2. Apply to all `omega.*` loggers
3. Write test: verify JSON output is valid and has required fields
4. Wire ForensicsManager to capture last N events

### Phase H2d: Documentation (30 min)

1. Update `OMEGA_ENGINE.md` with new subsystems
2. Update `ORACLE_STACK.md`
3. Write `docs/forensics/POSTMORTEM_GUIDE.md`

---

## §4 Gate

```bash
# Gate 1: Tests pass
make test  # 292+ passing

# Gate 2: Error Gauntlet passes
make test-gauntlet  # 6/6 scenarios pass

# Gate 3: Crash dump can be created and recovered
python3 -c "
from omega.forensics import ForensicsManager
fm = ForensicsManager()
fm.dump('test-123', {'error': 'test'}, Exception('test'))
result = fm.check_recovery()
assert result is not None
print('Forensics OK')
"

# Gate 4: Structured JSON logging produces valid JSON
python3 -c "
import json, logging
from omega.observability import get_engine
# ... verify log output is valid JSON
"
```

---

## §5 Decision Record

When the LOCK is lifted and a deep reasoning model takes this phase, the first task is to answer Q1, Q2, and Q3 above. The answers must be recorded in `PIVOT_LOG.md` as a new decision.

---

*⬡ OMEGA ⬡ SOPHIA ⬡ trc_horizon_2 ⬡ PHASE*
*Status: 🔒 LOCKED — requires Phases 1 + 2 to complete first.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_horizon_2 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
