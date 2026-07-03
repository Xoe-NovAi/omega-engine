# Holistic Review — Execution Guide
## Companion Document to HOLISTIC_REVIEW_PLAN_V3.md

**Date**: 2026-07-03
**Purpose**: Step-by-step execution instructions for DeepSeek V4 Flash via Cline CLI (1M token context)

---

## Cline Execution Protocol (Mandatory)

This review is executed by **DeepSeek V4 Flash** running under **Cline CLI** (headless agent mode). Cline has read/write access to the filesystem and MCP tools to the Omega Hub server.

### Execution Model
- **File Loading**: Cline reads files via its `read` tool on-demand. Load the files listed in each Phase batch before starting the tracer audit.
- **Output**: Findings are written to `data/review/` as markdown files.
- **Coordination**: Use Hivemind MCP tools to stay visible to the OpenCode fleet.
- **Handoff**: When complete, submit a handoff packet to Kali via `hivemind_submit_handoff()`.

### Hivemind Coordination Steps
Before starting, post context to the Hivemind:
```bash
# Check awareness
omega-hub_hivemind_get_awareness()

# Post presence
omega-hub_hivemind_post_context(
    channel="cline",
    entity="omega-engine",
    model="deepseek-v4-flash",
    task_current="Holistic Review Phase A: Hot Scan",
    focus_chain=["Spatial analysis of oracle.py, model_gateway.py, entity_registry.py"],
    decisions=[],
    continuation="Acknowledge and I will proceed through all 4 phases"
)

# Heartbeat every 5-10 minutes
omega-hub_hivemind_heartbeat(channel="cline", entity="omega-engine")
```

### Result Delivery
When all 4 phases are complete, submit findings back to Kali:
```bash
omega-hub_hivemind_submit_handoff(
    target_channel="opencode",
    target_entity="kali",
    source_channel="cline",
    source_entity="omega-engine",
    task="Holistic Review complete — findings from Phases A-D",
    priority=1,
    context="All 4 phases executed. 3 finding files written to data/review/."
)
```

---

## Pre-Execution Checklist

### 1. Environment Verification
```bash
# Verify all source files exist
find src/omega -name "*.py" | wc -l  # Expected: ~113

# Verify all test files exist
find tests -name "*.py" | wc -l  # Expected: ~66

# Verify key documentation exists
ls -la SOVEREIGN_MANDATES.md CREDITS.md ORACLE_STACK.md

# Verify configuration files exist
ls -la config/omega.yaml config/providers.yaml config/models.yaml
```

### 2. Token Budget Estimation
```bash
# Source files
find src/omega -name "*.py" -exec cat {} + | wc -c  # Characters
# Estimated tokens: characters / 4

# Test files
find tests -name "*.py" -exec cat {} + | wc -c

# Documentation
cat SOVEREIGN_MANDATES.md CREDITS.md ORACLE_STACK.md | wc -c

# Configuration
cat config/omega.yaml config/providers.yaml config/models.yaml | wc -c

# Total estimate: sum all characters / 4
```

### 3. Output Directory Setup
```bash
mkdir -p data/review
```

---

## Phase A: Hot Scan (Critical Path)

### Step 1: Load All Hot Path Files

Read these files via Cline's `read` tool. Load the full content of each — all are well within the 1M context window:

**Source Files**:
1. `src/omega/oracle/oracle.py` (860 lines)
2. `src/omega/oracle/model_gateway.py` (1131 lines)
3. `src/omega/oracle/entity_registry.py`
4. `src/omega/memory_store.py`
5. `src/omega/memory/providers.py`
6. `src/omega/oracle/health_monitor.py`
7. `src/omega/oracle/context_builder.py`
8. `src/omega/oracle/soul_distiller.py`
9. `src/omega/oracle/pii_masker.py`
10. `src/omega/oracle/resource_guard.py`
11. `src/omega/oracle/session_manager.py`

**Test Files**:
12. `tests/test_oracle.py`
13. `tests/test_model_gateway.py`
14. `tests/test_contract_m21.py`
15. `tests/test_contract_soul_distiller.py`

### Step 2: Execute Spatial Analysis

For each tracer (T1-T5), trace through the loaded files:

**T1: trace_id**
- Find where `trace_id` is created: `observability.py:new_trace_id()`
- Find where it's passed to `model_gateway.generate()`: `oracle.py:643`
- Find where it's stored: `memory_store.py:add_exchange()` metadata dict
- Find where it's logged: `token_ledger.py:record()`
- Check all 3 entry paths (talk, summon, _respond_as_iris) for consistency

**T2: provider_name**
- Find where `provider_name` is set on `GenerateResult`: `model_gateway.py:895` (success) + `:910` (fallback)
- Find where it's read by oracle: `oracle.py:659`
- Find where it's stored in metadata: `oracle.py:501`
- Check for drift between `get_preferred_backend()` and actual `res.provider_name`

**T3: latency_ms**
- Find where measurement is taken: `model_gateway.py:844`
- Find where it's stored on success: `model_gateway.py:898`
- Find where it's stored on fallback: `model_gateway.py:912`
- Check if fallback path ever has non-zero latency

**T4: error/exception**
- Find all `except:` clauses in loaded files
- Check if they log trace_id
- Check if they use the most specific error type
- Check for bare `except:` or `except Exception:` without logging

**T5: entity_name**
- Find where entity_name is resolved: `entity_registry.py:find_by_domain()`
- Trace through `oracle.py` → `context_builder.py` → `memory_store.py` → `soul_distiller.py`
- Check for case sensitivity issues
- Check for tombstoned entity access

### Step 3: Execute Anomaly Signature Checks

**S1: Counter Non-Reset**
- Find `_interaction_counter` in `oracle.py`
- Check if reset happens before or after `close_session()`
- Check what happens if `close_session()` raises an exception

**S2: Provider Name Drift**
- Compare `get_preferred_backend()` calls vs `res.provider_name` reads
- Find any place where the intended backend is used instead of the actual one

**S5: Silent Async Failures**
- Search for `asyncio.create_task` or `anyio.create_task` in loaded files
- Check if any exist (should be zero after D183 fix)

**S6: Bootstrap Double-Fire**
- Find `_bootstrapped` flag in `oracle.py`
- Check for race condition between check and set
- Check if multiple concurrent calls could both enter `bootstrap()`

**S9: Token Budget Overflow**
- Check `context_builder.py` for token counting logic
- Compare against `config/models.yaml` context window limits
- Check if overflow is handled gracefully

### Step 4: Record Findings

For each finding, record:
- Finding ID (F1, F2, etc.)
- Anomaly signature (S1-S10)
- Dimension (Spatial/Temporal/Causal/Semantic/Model-Level)
- Mandate violated (if applicable)
- Files affected with line numbers
- Description of the issue
- Impact assessment
- Suggested fix
- Severity (Critical/High/Medium/Low)

---

## Phase B: Warm Scan (Support Systems)

### Step 1: Load All Warm Path Files

Read these files via Cline's `read` tool. If the Phase A files are still in context, keep them accessible for cross-referencing.

**Observability Files**:
1. `src/omega/observability/__init__.py`
2. `src/omega/observability/token_ledger.py`
3. `src/omega/observability/metrics_db.py`
4. `src/omega/observability/bleg.py`
5. `src/omega/observability/ufl.py`
6. `src/omega/observability/context.py`

**Memory Files**:
7. `src/omega/memory/__init__.py`
8. `src/omega/memory/providers.py`
9. `src/omega/memory/batch_writer.py`
10. `src/omega/memory/adapters.py`
11. `src/omega/memory/embeddings.py`
12. `src/omega/memory/vector_adapters.py`
13. `src/omega/memory/fts_index.py`

**A2A and Integration Files**:
14. `src/omega/oracle/a2a_bridge.py`
15. `src/omega/oracle/a2a_auth.py`
16. `src/omega/oracle/wad_loader.py`
17. `src/omega/oracle/handoff.py`
18. `src/omega/oracle/semantic_router.py`
19. `src/omega/oracle/skeptical_verifier.py`
20. `src/omega/oracle/headroom.py`

**Test Files**:
21. `tests/test_hivemind_integration.py`
22. `tests/test_storage_providers.py`

### Step 2: Execute Observability Audit

**Trace ID Coverage**:
- Find all event logging calls in observability files
- Check if every event carries a trace_id
- Find any events that log without trace_id

**Token Ledger Completeness**:
- Find all `record()` calls in token_ledger.py
- Check if they include provider_name, latency_ms, model_used
- Check if they correctly distinguish local vs cloud

**Metrics DB Schema**:
- Check if metrics_db.py schema matches the documented schema
- Check if WAL mode is enabled
- Check if there are any schema migration issues

### Step 3: Execute Memory Provider Audit

**Fallback Chain**:
- Trace the provider chain in memory_store.py
- Check if Redis → File → InMemory fallback works correctly
- Check what happens when all providers fail

**Batch Writer**:
- Check if batch_writer.py handles connection pool exhaustion
- Check if there's a dead-letter mechanism for failed writes
- Check if the 14-day archive / 30-day delete cleanup works

**FTS Index**:
- Check if fts_index.py handles concurrent writes
- Check if the index stays consistent with the underlying data

### Step 4: Execute A2A Audit

**Agent Cards**:
- Check if a2a_bridge.py uses real A2A v1.0 spec
- Check if `draft-schemacommons-aaif-00` has been removed
- Check if Agent Cards are correctly formatted

**Authentication**:
- Check if a2a_auth.py implements SPIFFE/WIMSE
- Check if there are any security vulnerabilities

### Step 5: Record Findings

Same format as Phase A.

---

## Phase C: Cold Scan (Infrastructure & Governance)

### Step 1: Load All Cold Path Files

Read these files via Cline's `read` tool. Load the documentation files last (they are long-form reference material).

**Core Infrastructure**:
1. `src/omega/errors.py`
2. `src/omega/constants.py`
3. `src/omega/cli/oracle_cli.py`
4. `src/omega/cvar_table.py`
5. `src/omega/vault/__init__.py`
6. `src/omega/vault/key_vault.py`
7. `src/omega/vault/crypto.py`

**Orchestration**:
8. `src/omega/orchestration/__init__.py`
9. `src/omega/orchestration/triage_router.py`

**Gateway**:
10. `src/omega/gateway/__init__.py`

**Workers**:
11. `src/omega/workers/background_researcher/` (all files)

**Documentation**:
12. `SOVEREIGN_MANDATES.md`
13. `CREDITS.md`
14. `docs/decisions/PIVOT_LOG.md`

### Step 2: Execute Error Taxonomy Audit

**Error Class Completeness**:
- Load `errors.py` and list all error classes
- For each error class, grep the codebase to see if it's ever raised
- Identify orphaned error classes (defined but never raised)
- Identify untested error classes (raised but never tested)

**Exception Handling Quality**:
- Find all `except:` clauses in loaded files
- Check if they catch the most specific error type
- Check if they log trace_id
- Check if they re-raise or swallow the exception

### Step 3: Execute Heritage Tag Audit

**Tag Extraction**:
- Grep all source files for `[id-soft:]` tags
- Extract tag format: `[id-soft: GAME YEAR] Pattern Name`
- List all tags found

**Tag Cross-Reference**:
- Load `CREDITS.md` and extract all registered patterns
- Cross-reference tags in code against registered patterns
- Identify unregistered tags (tags in code not in CREDITS.md)
- Identify untagged patterns (patterns in CREDITS.md without tags in code)

**Vet Record Verification**:
- Load `HERITAGE_VET_LOG.md`
- Check if every tag has a corresponding vet record
- Check if any vet records reference rejected patterns

### Step 4: Execute Mandate Compliance Audit

**Mandate Matrix**:
For each of the 22 mandates (M1-M22), verify compliance:

| Mandate | Check Method | Files to Verify |
|---------|--------------|-----------------|
| M1 | `grep -r "import asyncio" src/omega/` | All source files |
| M2 | `grep -r "from.*wads" src/omega/` | All source files |
| M3 | Check entity_registry.py for Iris in Pillar slots | entity_registry.py |
| M4 | Check PIVOT_LOG.md for plan docs | docs/decisions/PIVOT_LOG.md |
| M5 | Check oracle.py for close_session calls | oracle.py, soul_distiller.py |
| M6 | Check Quadlet files for UserNS=keep-id | deploy/, scripts/setup.sh |
| M7 | Check providers.yaml for local_first strategy | config/providers.yaml, model_gateway.py |
| M8 | `grep -r "telemetry\|analytics\|phone.home"` | All source files |
| M9 | Find all `except:` clauses, check for trace_id | All source files |
| M10 | Check agent count in .opencode/agents/ | .opencode/agents/, hierarchy.py |
| M11 | Check oracle.py for close_session every 5 interactions | oracle.py, soul_distiller.py |
| M12 | Check atomic writes and trace_id propagation | request_queue.py, handoff.py |
| M13 | Run `make temple-grade` | Makefile, CI configs |
| M14 | Check [id-soft:] tags against HERITAGE_VET_LOG.md | All source files, CREDITS.md |
| M15 | Check for session_gnosis.md per entity | data/entities/*/session_gnosis.md |
| M16 | `grep -r "/home\|/media" src/omega/` | All source files |
| M17 | Check skeptical_verifier.py and failure_registry.py | skeptical_verifier.py, failure_registry.py |
| M18 | Check context_builder.py for token efficiency | context_builder.py, headroom.py |
| M19 | Check for Somatic Save-Point pattern | soul_distiller.py |
| M20 | Check state_manager.py for ctypes bindings | state_manager.py, cpu_optimizer.py |
| M21 | Check contract tests for all API boundaries | test_contract_m21.py, test_*.py |
| M22 | Check GenerateResult for provider_name from actual response | token_ledger.py, model_gateway.py, oracle.py |

### Step 5: Execute Configuration Audit

**Provider Config**:
- Check if `config/providers.yaml` strategy is `local_first`
- Check if API keys are in `.env` (not tracked)
- Check if health check timeouts are consistent

**Model Config**:
- Check if `config/models.yaml` is the single source of truth
- Check if model names are hardcoded anywhere in source
- Check if loading strategies are correctly defined

**Entity Config**:
- Check if `config/wads/_omega_default/entities.yaml` has 12 entities
- Check if `config/wads/arcana_novai/entities.yaml` has 11 entities
- Check if there are stale entities (breachentity, default, testentity, quality, scribe)

### Step 6: Record Findings

Same format as Phase A.

---

## Phase D: Synthesis & Reporting

### Step 1: Consolidate All Findings

Load findings from Phases A, B, C and consolidate:

1. Deduplicate findings that appear in multiple phases
2. Group findings by anomaly signature
3. Group findings by dimension
4. Group findings by mandate
5. Group findings by severity

### Step 2: Generate Summary Statistics

```
Total Findings: {N}
  Critical: {N_c}
  High: {N_h}
  Medium: {N_m}
  Low: {N_l}

By Anomaly Signature:
  S1 (Counter Non-Reset): {N}
  S2 (Provider Name Drift): {N}
  S3 (Orphaned Exception Types): {N}
  S4 (Docstring-Return-Type Mismatch): {N}
  S5 (Silent Async Failures): {N}
  S6 (Bootstrap Double-Fire): {N}
  S7 (Tainted Data Bypass): {N}
  S8 (Heritage Tag Rot): {N}
  S9 (Token Budget Overflow): {N}
  S10 (Dead Letter Silence): {N}

By Dimension:
  Spatial: {N}
  Temporal: {N}
  Causal: {N}
  Semantic: {N}
  Model-Level: {N}

By Mandate:
  M1: {N}
  M2: {N}
  ...
  M22: {N}
```

### Step 3: Write Findings Reports

Write three files (Cline: use `write_to_file`):
1. `data/review/FINDINGS_CRITICAL.md` — Critical findings (block release)
2. `data/review/FINDINGS_MAJOR.md` — High findings (fix before next sprint)
3. `data/review/FINDINGS_MINOR.md` — Medium/Low findings (technical debt)

Each file should follow the Finding Template from §Finding Template below. Start each with a summary table of all findings in that file.

### Step 4: Generate Remediation Roadmap

For each critical finding:
1. Identify the fix (code change + test + documentation)
2. Estimate effort (hours)
3. Identify dependencies (does this fix depend on another?)
4. Assign priority (P0, P1, P2)

### Step 5: Post-Execution Validation

```bash
# Run tests to verify no regressions
make test

# Run temple-grade to verify T1-T11 gates
make temple-grade

# Run heritage-map to verify heritage tag coverage
make heritage-map
```

### Step 6: Hivemind Handoff Delivery

After writing all finding files and passing validation, deliver results to the OpenCode fleet:

```bash
# 1. Post completion context
omega-hub_hivemind_post_context(
    channel="cline",
    entity="omega-engine",
    model="deepseek-v4-flash",
    task_current="Holistic Review COMPLETE",
    focus_chain=[
        "Phase A: Hot Scan — Spatial anomalies traced",
        "Phase B: Warm Scan — Support systems audited",
        "Phase C: Cold Scan — Heritage, mandates, config verified",
        "Phase D: Synthesis — Findings consolidated, reports written"
    ],
    decisions=["Holistic Review executed by DeepSeek V4 Flash via Cline CLI"],
    continuation="No handoff required. Finding files in data/review/."
)

# 2. Submit handoff to Kali with finding summary
omega-hub_hivemind_submit_handoff(
    target_channel="opencode",
    target_entity="kali",
    source_channel="cline",
    source_entity="omega-engine",
    task="Holistic Review complete — findings ready for triage",
    priority=1,
    context="All 4 phases executed. Validation passed. See data/review/FINDINGS_*.md"
)

# 3. Final heartbeat
omega-hub_hivemind_heartbeat(channel="cline", entity="omega-engine")
```

---

## Finding Template

Use this template for each finding:

```markdown
## F{n}: {Title}

**Anomaly Signature**: S{n} ({name})
**Dimension**: {Spatial|Temporal|Causal|Semantic|Model-Level}
**Mandate Violated**: M{n} ({name})
**Severity**: {Critical|High|Medium|Low}

**Files Affected**:
- `src/omega/oracle/oracle.py:45-52` (root cause)
- `src/omega/oracle/model_gateway.py:659` (propagation)

**Description**:
{What's wrong and why it matters}

**Evidence**:
```python
# file.py:line
{code snippet showing the issue}
```

**Impact**:
{What happens in production if this is not fixed}

**Suggested Fix**:
{1-2 sentences describing the fix}

**Contract Test Required**: {Yes|No}
{If yes, describe the test that should be added}
```

---

## Post-Review Actions (OpenCode Fleet — Kali Awaiting Handoff)

After the review is complete and the handoff packet has been submitted:

1. **Kali Triage** (Opencode fleet):
   - Kali reads `data/review/FINDINGS_*.md` from the handoff
   - Critical findings → immediate execution sprint
   - High findings → next sprint backlog
   - Medium/Low → technical debt registry

2. **Fixes** (assigned by pillar):
   - Each finding gets a fix, contract test, and commit
   - Run `make test` and `make temple-grade` per fix

3. **Documentation Update**:
   - OMEGA_ENGINE.md and SOVEREIGN_ARK_BLUEPRINT.md updated per findings
   - Any documentation-vs-code drift corrected

4. **Session Close**:
   - Post final summary to Hivemind
   - Release any workspace locks
   - Cline session completes

---

**End of Execution Guide**
