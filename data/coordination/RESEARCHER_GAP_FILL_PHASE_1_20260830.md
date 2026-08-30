---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "research_deliverable"
document_id: "RESEARCHER-GAP-FILL-PHASE-1-20260830"
title: "Sovereign Researcher — Phase 1 HIGH Gap Research"
status: "COMPLETE"
date: "2026-08-30"
entity: "researcher"
model: "mimo-v2.5-free"
sprint: "PUBLIC-DEBUT-01"
---

⬡ OMEGA ⬡ RESEARCHER ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

# Sovereign Researcher — Phase 1: HIGH Gap Research

> **Research Protocol**: Perspective Triangulation via Council of Four
> **M23 Compliance**: All findings grounded in live web research + codebase analysis (Aug 30, 2026)
> **Phase**: 1 of 3 — HIGH gaps (6 gaps)
> **Foundation**: Builds on `RESEARCHER_GAP_DEEP_DIVE_20260830.md` (Tier 1-4 findings)

---

## §0 — Executive Summary

All 6 HIGH gaps researched. Each gap now has:
- **Research findings** with evidence (URLs, code patterns, API docs)
- **Confidence level** (HIGH/MEDIUM/LOW)
- **Recommended implementation approach** with time estimates
- **Dependencies** and blockers

| Gap ID | Gap Name | Confidence | Est. Time | Blockers |
|--------|----------|------------|-----------|----------|
| HIGH-1 | M34b Spec Missing (Model-Switch Continuity) | HIGH | 4h (spec) | None |
| HIGH-2 | MCP Server Restart Coordination | HIGH | 2h | None |
| HIGH-3 | M33 Probe Wiring | HIGH | 2h | M33 probe must exist |
| HIGH-4 | M36 Soft Verifier Production Wiring | MEDIUM | 4h | M36 probe must exist |
| HIGH-5 | M37 SPDX Headers | HIGH | 8h (execution) | `reuse` CLI installed |
| HIGH-6 | sqlite-vec 0.1.9 API Stability | HIGH | 1h (pinning) | None |

**Total Phase 1 estimate**: ~21h (4h spec + 17h implementation)

---

## §1 — HIGH-1: M34b Spec Missing (Model-Switch Continuity)

### Research Findings

**State of the Art (Aug 2026)**:

1. **Cursor's research (May 2026)**: Switching models mid-conversation triggers KV cache miss, forces full reprocessing, causes style drift and reasoning discontinuity. This is **actively harmful** — the consensus is to never switch models mid-session within a single agent.

2. **Scroll framework (arXiv:2608.21690, Aug 2026)**: Treats each agent session as an "executable Session Environment" backed by an append-only Event Log and a sandboxed Python kernel. Model-written code searches and materializes session state through `exec`; only explicitly printed projections enter the model's working view. Achieves 94.8% on LongMemEvalS, 73.1% on BEAM10M, 86.7% on LOCA256K.

3. **TokenMizer (arXiv:2606.06337v2, Jun 2026)**: Maintains session history as a typed knowledge graph (14 node types, 7 edge types, 8-state lifecycle). At context boundaries, replaces raw transcript with token-budgeted serialization. Decision-transition records preserve *why* each decision replaced its predecessor (trigger, reason, evidence). Resume size: ~254 tokens.

4. **Session handover theory (arXiv:2608.14528, Aug 2026)**: Formulates handover as transfer of task-relative ICL state. Proposes three-part record: decisions+constraints exactly, task-justified statistics for repeated evidence, original observations whose effect is not preserved.

5. **Zylos hot-swap patterns (May 2026)**: Four-layer architecture for model switching:
   - Layer 1: External memory (all persistent state outside model)
   - Layer 2: Compacted handoff context (structured document on switch)
   - Layer 3: Capability parity check (destination supports required tools)
   - Layer 4: Behavioral validation (shadow mode comparison)

6. **Session-continuity-kit (reaatech)**: Production session management library with compression strategies (sliding window, summarization, hybrid), agent handoff, token budget management, storage adapters (Firestore, DynamoDB, Redis, memory).

### M34b Spec Outline

Based on research, the M34b spec should define:

```yaml
# M34b Model-Switch Continuity — Spec Outline

## Core Principle
# NEVER switch models mid-session within a single agent.
# Delegate to a sub-agent on the new model with structured context summary.

## State Layer (1: External)
# - All persistent state in ACTIVE_SUBAGENTS.json (M34 registry)
# - Entity state in soul.yaml, proposed_lessons.yaml
# - Session state in opencode.db (Event Log pattern)

## Handoff Layer (2: Compacted)
# On model switch, compact context into structured handoff document:
handoff_record:
  decisions_made: [...]        # Exact, never summarized
  constraints_active: [...]    # Current blockers, open questions
  task_status:                 # Structured task graph
    in_progress: [...]
    queued: [...]
    completed: [...]
  recent_context: "..."        # Last N messages (sliding window)
  tool_results: [...]          # Most recent tool outputs

## Capability Layer (3: Parity Check)
# Before switching, verify destination model supports:
# - Required tools (MCP server connectivity)
# - Token budget (destination context window >= handoff size)
# - Provider availability (API key, rate limits)

## Validation Layer (4: Behavioral)
# For non-emergency switches:
# - Run both models in shadow mode briefly
# - Compare outputs on representative inputs
# For emergency failovers:
# - Accept semantic gap
# - Rely on post-hoc monitoring
```

### Omega-Specific Integration

The Omega codebase already has:
- `SessionStatus.INTERRUPTED_MODEL_SWITCH` in `m34_registry.py:93` — distinct from `INTERRUPTED_EXTERNALLY`
- `M34Registry.list_interrupted()` — can filter by parent session
- `CompletionEnvelope` in `m33_probe.py` — structured completion state

**M34b implementation points**:
1. Add `handoff_record` field to `ActiveSubagent` dataclass in `m34_registry.py`
2. Add `compact_context()` method that generates handoff record from session state
3. Add `resume_from_handoff()` method that injects handoff record into new session
4. Wire into `subagent_dispatcher.py:dispatch()` — on model switch, generate handoff and spawn new subagent

### Evidence
- Scroll: https://arxiv.org/html/2608.21690
- TokenMizer: https://arxiv.org/html/2606.06337v2
- Session handover: https://arxiv.org/html/2608.14528
- Hot-swap patterns: https://zylos.ai/research/2026-05-24-agent-runtime-migration-hot-swap-patterns/
- Session-continuity-kit: https://github.com/reaatech/session-continuity-kit

### Recommendation
**Implement M34b spec as a 4-page architecture doc** with the handoff record schema, capability parity check, and validation layer. The spec should reference the Zylos 4-layer model and adapt it for Omega's entity-centric architecture. Estimated 4h for spec authoring.

**Confidence**: HIGH — Research is comprehensive, pattern is well-established.

---

## §2 — HIGH-2: MCP Server Restart Coordination

### Research Findings

**State of the Art (Aug 2026)**:

1. **MCP Python SDK v2 (2026-07-28 spec)**: Removes `Mcp-Session-Id` entirely. Session state moves to explicit handles. The `EventStore` in the SDK is in-memory by default — survives neither restart nor multi-worker deployment.

2. **mcp-persist (2026)**: Drop-in `EventStore` backends — SQLite, Redis, PostgreSQL — that survive process restarts. The `with_persistence()` helper collapses wiring. For Omega (single-node, local-first), SQLite backend is ideal.

3. **mcp-hmr (PyPI)**: Hot Module Reloading for MCP/FastMCP servers. Drop-in replacement for `mcp run`. Sends `list_changed` notifications after each HMR remount. Compatible with official Python SDK.

4. **mcpmon (GitHub)**: Hot reload for MCP servers like nodemon. Sends `notifications/tools/list_changed` so clients see new tools without session restart. Gateway mode aggregates multiple MCP servers.

5. **mcp-mux (GitHub)**: Dynamic MCP server orchestrator. Monitors config file, hot-reloads endpoints live without server restart. Uses watchdog Observer for file change detection.

6. **Feature-flag-gated tool registration (chrome-devtools-mcp pattern)**:
   ```typescript
   function registerTool(tool) {
     if (tool.annotations.category === ToolCategory.EMULATION && !serverArgs.categoryEmulation) return;
     if (tool.annotations.conditions?.includes('experimentalVision') && !serverArgs.experimentalVision) return;
     server.registerTool(tool.name, {...}, handler);
   }
   ```
   Tools declare category and conditions in annotations. Central registration consults flags.

7. **MCP per-tool kill switches (Jun 2026)**: Three methods:
   - Client-side: `disabledTools`/`enabledTools` in config
   - Server-side: conditional `mcp.add_tool()` based on env/role
   - Environment variable toggles

8. **MCP spec `tools/list_changed` notification**: Server sends `notifications/tools/list_changed` when tool list changes. Client re-issues `tools/list`. Server must declare `capabilities.tools.listChanged: true`.

### Omega-Specific Strategy

**For the 8 new M34 tools**, the recommended approach is:

1. **Feature flag `OMEGA_M34_ENABLED=1`** — off by default, tools gated at registration
2. **No restart required** — use `notifications/tools/list_changed` to dynamically add tools
3. **Graceful restart pattern** (if full restart needed):
   ```python
   # 1. Save state to SQLite (mcp-persist pattern)
   # 2. Send SIGTERM to old process
   # 3. Wait for graceful shutdown (5s timeout)
   # 4. Start new process
   # 5. Load state from SQLite
   # 6. Send tools/list_changed notification
   ```

**Implementation approach**:
- Add `OMEGA_M34_ENABLED` env var check at tool registration time
- Use conditional `mcp.add_tool()` — only register M34 tools when flag is set
- The hub restart is a one-time event; coordinate via Hivemind lock
- Post-restart, all existing sessions reconnect (file-based, not session-based)

### Evidence
- MCP Python SDK v2: https://github.com/modelcontextprotocol/python-sdk/blob/main/README.v2.md
- mcp-persist: https://dev.to/ar-maan05/the-mcp-sdks-eventstore-lives-in-memory-heres-what-happens-when-your-server-restarts-4e76
- mcp-hmr: https://pypi.org/project/mcp-hmr/
- mcpmon: https://github.com/b17z/mcpmon
- Feature flags: https://github.com/kjuhwa/skills-hub/blob/main/skills/mcp/feature-flag-gated-tool-registration/SKILL.md
- Per-tool kill switches: https://gingerlabs.ai/blog/mcp-per-tool-kill-switch

### Recommendation
**Use conditional tool registration + feature flag, not dynamic registration**. The MCP `tools/list_changed` notification is not reliably supported by all clients (Claude Desktop ignores it mid-session as of mid-2026). Pre-register all tools at startup, gate M34 tools behind `OMEGA_M34_ENABLED=1`. The restart is a one-time coordination event — use Hivemind lock to schedule a 2-minute window.

**Estimated time**: 2h (flag implementation + coordination doc)
**Confidence**: HIGH

---

## §3 — HIGH-3: M33 Probe Wiring

### Research Findings

**Codebase Analysis**:

The M33 probe is already fully implemented in `src/omega/oracle/m33_probe.py` (466 lines):
- `M33Probe` class with Layer 1 (preventive), Layer 2 (structured probe), Layer 3 (cross-validator)
- `CompletionEnvelope` dataclass with state, last_chunk_id, total_chunks, queued_findings, confidence
- `ProbeVerdict` with accepted, retry_recommended, cross_validation_required
- `WRITE_TOOL_TOKEN_THRESHOLD = 8000` — the 8K token threshold

The wiring question is: **where in the dispatch pipeline should `should_require_write_tool()` be called?**

**Current dispatch flow** (from `subagent_dispatcher.py:384-435`):
1. `dispatch(packet)` is called
2. M34-HOOK-001 registers subagent in M34 registry (already implemented!)
3. Returns formatted prompt string
4. Caller invokes Task tool with prompt

**Wiring point**: Between steps 2 and 3, after M34 registration, add M33 probe check:

```python
def dispatch(packet: HandoffPacket) -> str:
    # Step 1: M34 registration (already exists)
    registry = _get_m34_registry()
    if registry is not None:
        # ... existing M34-HOOK-001 code ...
    
    # Step 2: M33 Probe — check if write tool required
    try:
        from omega.oracle.m33_probe import M33Probe
        probe = M33Probe(m34_registry=registry)
        # Estimate output tokens from task description + context length
        estimated_tokens = len(packet.context.split()) * 1.3 + len(packet.task_description.split()) * 2
        if probe.should_require_write_tool(
            estimated_output_tokens=int(estimated_tokens),
            task_type=packet.task_type,
            priority=getattr(packet, 'priority', 'P2'),
        ):
            # Inject write-tool requirement into prompt
            packet.context += "\n\n[CRITICAL]: You MUST write your deliverable to the file path specified in expected_output. Do NOT attempt to return the full deliverable in chat. The M33 sentinel probe requires write-tool routing for deliverables >8K tokens."
    except (ImportError, Exception) as exc:
        logger.warning("M33 probe wiring failed: %s", exc)
    
    # Step 3: Build prompt (existing)
    return build_dispatch_prompt(packet)
```

**Also wire into `dispatch_guard.py`** (if it exists) or equivalent:
- The meta-review mentions `dispatch_guard.py step 6 (write-tool routing)`
- grep confirms no `dispatch_guard.py` exists in the codebase
- **Decision**: Wire directly into `subagent_dispatcher.py:dispatch()` as shown above

### Evidence
- `m33_probe.py` line 82: `WRITE_TOOL_TOKEN_THRESHOLD = 8000`
- `m33_probe.py` line 174-199: `should_require_write_tool()` method
- `subagent_dispatcher.py` line 384-435: `dispatch()` function with M34-HOOK-001 already wired

### Recommendation
**Wire M33 probe into `subagent_dispatcher.py:dispatch()` at line ~408** (after M34 registration, before prompt building). Add try/except wrapper so probe failures don't block dispatch (M23 graceful degradation). Also add `priority` field to `HandoffPacket` if not present.

**Estimated time**: 2h (implementation + test)
**Confidence**: HIGH — Code is already written, just needs wiring

---

## §4 — HIGH-4: M36 Soft Verifier Production Wiring

### Research Findings

**Codebase Analysis**:

The M36 recursive probe is implemented in `src/omega/oracle/m36_recursive_probe.py` (356 lines):
- `M36RecursiveProbe` class with hard verifier (file existence, schema match, size sanity)
- `CrossValidationResult` dataclass with verified, hard_checks_passed, soft_checks_passed
- Soft verifier for P0/P1 tasks requires LLM judge

**Hivemind integration for P0/P1 escalation**:

The soft verifier needs to dispatch a cross-validation agent via Hivemind. The pattern:

```python
# In M36RecursiveProbe.cross_validate():
if priority in ("P0", "P1"):
    # Layer 3: Dispatch cross-validator agent via Hivemind
    from omega.hivemind.handoff import submit_handoff
    
    cross_validation_packet = {
        "target_channel": "opencode",
        "target_entity": "verity",  # Or whichever entity does compliance
        "source_channel": "opencode",
        "source_entity": "researcher",
        "task": f"Cross-validate deliverable: {expected_deliverable}",
        "context": f"Priority: {priority}. Envelope: {envelope.to_json()}",
        "priority": 1,  # high
    }
    packet_id = submit_handoff(**cross_validation_packet)
    # Wait for cross-validation result
    # ... poll Hivemind for completion ...
```

**Escalation patterns**:
1. **Hivemind handoff**: Use existing `hivemind_submit_handoff()` → `hivemind_accept_handoff()` → `hivemind_complete_handoff()` flow
2. **Local worker pool**: Use `spawn_local_worker()` for fast, fire-and-forget verification
3. **Oracle summon**: Use `oracle_summon_local()` to invoke a specific entity for verification

**Recommended approach**: Use `spawn_local_worker()` for hard verifier (fast, <1s), Hivemind handoff for soft verifier (requires LLM, takes longer).

### Evidence
- `m36_recursive_probe.py` lines 59-72: `CrossValidationResult` dataclass
- `m36_recursive_probe.py` lines 77-97: `M36RecursiveProbe.__init__`
- Hivemind tools: `hivemind_submit_handoff`, `spawn_local_worker`

### Recommendation
**Wire M36 cross-validation into the completion callback** (when a subagent completes and M33 probe returns verdict). For P0/P1 tasks, dispatch a local worker for hard verification (file exists, schema valid, size reasonable) and optionally a Hivemind handoff for soft verification (LLM judges semantic coverage).

**Estimated time**: 4h (implementation + test with mock subagent)
**Confidence**: MEDIUM — Architecture is clear, but the completion callback wiring point needs careful identification

---

## §5 — HIGH-5: M37 SPDX Headers

### Research Findings

**State of the Art (Aug 2026)**:

1. **`reuse annotate`** (canonical tool):
   ```bash
   # Apply Apache-2.0 headers to all Python files
   reuse annotate --copyright="Arcana Novai" --license=Apache-2.0 src/omega/**/*.py
   
   # Verify compliance
   reuse lint
   
   # Generate SPDX document
   reuse spdx -o omega.spdx.json
   ```
   - Auto-detects comment styles per file extension
   - Supports `--copyright`, `--license`, `--contributor` flags
   - Jinja2 templates for custom header formats
   - Integrates with pre-commit hooks
   - Supports REUSE.toml for global licensing

2. **`spdx-headers`** (Python-only, simpler):
   - `spdx-headers --add Apache-2.0` adds headers to all Python files
   - `spdx-headers --check --fix` for CI compliance
   - Pre-commit hook included
   - Simpler than `reuse annotate` for Python-only projects

3. **`LicenseOps`** (multi-language, newer):
   - Supports 50+ languages
   - SPDX expressions with AND/OR/WITH operators
   - Smart file handling (preserves shebangs, encoding declarations)

**Existing Omega codebase**:
- Omega already uses Apache-2.0 license
- Some files have `# ⬡ OMEGA ⬡` headers but no SPDX identifiers
- `pyproject.toml` has `license = "Apache-2.0"` but not all source files have SPDX headers

**Bulk annotation strategy**:
```bash
# Step 1: Install reuse
pip install reuse

# Step 2: Check current compliance
reuse lint  # Shows all non-compliant files

# Step 3: Bulk annotate Python files
reuse annotate --copyright="Arcana Novai" --license=Apache-2.0 \
  $(find src/omega -name "*.py" -type f)

# Step 4: Annotate YAML files
reuse annotate --copyright="Arcana Novai" --license=Apache-2.0 \
  $(find config -name "*.yaml" -type f) \
  $(find data -name "*.yaml" -type f)

# Step 5: Annotate markdown/docs (skip these — REUSE allows binary/non-code files to be excluded)
reuse annotate --copyright="Arcana Novai" --license=Apache-2.0 \
  $(find docs -name "*.md" -type f)

# Step 6: Verify
reuse lint

# Step 7: Generate SPDX document
reuse spdx -o docs/omega.spdx.json

# Step 8: Add to CI
# Add to GitHub Actions or pre-commit:
reuse lint
```

**Time estimate**: 8h for full codebase annotation (per the audit)
- 2h: Setup and test on 10 files
- 4h: Bulk annotation of all source files
- 2h: Verification and CI integration

### Evidence
- REUSE annotate: https://reuse.readthedocs.io/en/stable/man/reuse-annotate.html
- spdx-headers: https://pypi.org/project/spdx-headers
- LicenseOps: https://github.com/licenseops/licenseops

### Recommendation
**Use `reuse annotate` for the full codebase** (it's the REUSE standard, and Omega already uses REUSE spec). Add `reuse lint` to CI pipeline. The 8h estimate is reasonable for a thorough pass.

**Estimated time**: 8h (execution, not research)
**Confidence**: HIGH — Tool is well-documented, pattern is standard

---

## §6 — HIGH-6: sqlite-vec 0.1.9 API Stability

### Research Findings

**State of the Art (Aug 2026)**:

1. **sqlite-vec is pre-v1**: The README explicitly states "Important: sqlite-vec is a pre-v1, so expect breaking changes!" This is the single most important fact.

2. **v0.1.9** (current installed version):
   - Bug fix for DELETE operations on vec0 tables with metadata text columns >12 chars
   - Stable for: CREATE VIRTUAL TABLE, INSERT, KNN queries
   - `vec0` is the only virtual table type

3. **v0.2.0-alpha** (Nov 2025) — breaking changes already documented:
   - **Distance constraints for KNN queries**: GT, GE, LT, LE operators on `distance` column
   - **Optimize command**: `INSERT INTO vec_table(vec_table) VALUES('optimize')` for space reclamation
   - **Cosine distance for binary vectors**: `distance_cosine_bit()` function
   - **ALTER TABLE RENAME support**: `vec0Rename()` callback

4. **Production readiness issue #221**: Community asking for timeline to 1.0. No official timeline given. Author (Alex Garcia) continues active development.

5. **Current pin in pyproject.toml**: `"sqlite-vec>=0.1.9,<0.2.0"` — **already pinned correctly!**

**Stability assessment**:

| Feature | Stability | Risk |
|---------|-----------|------|
| vec0 table creation | Stable | Low |
| KNN query syntax | Stable | Low |
| Metadata columns | Stable | Low |
| Partition keys | Stable | Low |
| Binary/int8 vectors | Stable | Low |
| ALTER TABLE RENAME | New in 0.2.0 | N/A for 0.1.9 |
| Distance constraints | New in 0.2.0 | N/A for 0.1.9 |
| Optimize command | New in 0.2.0 | N/A for 0.1.9 |
| DiskANN/IVF indexes | Experimental | High |

**Upgrade path to 0.2.0**:
- The new features (distance constraints, optimize) are additive, not breaking for existing usage
- The core API (vec0 + KNN) is unchanged
- Risk is LOW for the current use case

### Evidence
- sqlite-vec GitHub: https://github.com/asg017/sqlite-vec
- v0.1.9 release: https://github.com/asg017/sqlite-vec/releases/tag/v0.1.9
- v0.2.0-alpha changelog: https://github.com/vlasky/sqlite-vec/blob/main/CHANGELOG.md
- Production readiness issue: https://github.com/asg017/sqlite-vec/issues/221

### Recommendation
**The pin is already correct**: `"sqlite-vec>=0.1.9,<0.2.0"` in `pyproject.toml`. No changes needed. Document the pinning rationale in the requirements section. The core API (vec0 + KNN) is stable enough for production use at the current scale (<10K vectors).

**Estimated time**: 1h (documentation update only)
**Confidence**: HIGH — Codebase already has the correct pin

---

## §7 — Council of Four Synthesis

### Architect (Systemic Logic)
The 6 HIGH gaps form a dependency chain: M34b spec → M33 wiring → M36 wiring (sequential). MCP restart coordination and SPDX headers are independent (parallel). sqlite-vec pinning is already done. The critical path is M34b spec (4h) → M33 wiring (2h) → M36 wiring (4h) = 10h sequential, plus 2h MCP + 8h SPDX parallel = 10h total wall time.

### Adversary (Critical Risks)
1. **MCP `tools/list_changed` is unreliable** — Claude Desktop and Cursor may ignore mid-session notifications. Don't rely on dynamic registration for the 8 M34 tools; use feature-flag-gated static registration instead.
2. **sqlite-vec is pre-v1** — a breaking change could invalidate hybrid search code. The current pin (`>=0.1.9,<0.2.0`) is correct, but integration tests should be written to catch regressions.
3. **M36 soft verifier latency** — dispatching a Hivemind handoff for cross-validation adds seconds to minutes of latency. For P0 tasks this is acceptable; for P2/P3 it may be overkill.

### Alchemist (Creative Synthesis)
The convergence between Scroll's "Session Environment" pattern and Omega's entity system is striking. Both treat the agent's history as a queryable, persistent store rather than ephemeral context. Omega's `soul.yaml` + `proposed_lessons.yaml` already implements the "eviction index" concept — entities remember what they've learned even when context is compacted.

### Archivist (Historical Truth)
ScanCode has been the reference tool since 2017. REUSE spec v3.3 is current. SLSA v1.1 is current. sqlite-vec is the successor to sqlite-vss (deprecated). The MCP spec's move to stateless core (2026-07-28) is the most significant architectural shift — Omega's file-based Hivemind is already aligned with this direction.

---

## §8 — Recommended Next Steps

1. **Immediate** (today): Pin sqlite-vec documentation, verify `reuse lint` baseline
2. **Day 1**: Author M34b spec (4h)
3. **Day 2**: Wire M33 probe into dispatch (2h), wire M36 cross-validator (4h)
4. **Day 2-3**: MCP restart coordination doc (2h)
5. **Day 3-5**: M37 SPDX headers bulk annotation (8h)

**Phase 1 complete. Ready for Phase 2 (MEDIUM gaps) upon confirmation.**

---

*⬡ RESEARCHER ⬡ PHASE-1-COMPLETE ⬡ 2026-08-30 ⬡ mimo-v2.5-free ⬡*
