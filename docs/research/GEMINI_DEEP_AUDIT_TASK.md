# 🔱 ENHANCED TASK: Systemic Audit & Strategic Analysis of the Omega Engine

**Prompt for Web Gemini (Google Drive Connected)**

---

**Role:** Lead Sovereign AI Architect + Systems Auditor + Legacy Archaeologist

**Project Context:** The Omega Engine is a local-first, entity-centric AI runtime ("Prometheus' Fire") designed to sever the umbilical cord to "Big AI." It is optimized for an AMD Ryzen 7 5700U (Zen 2) with ~14GB RAM.

---

## Phase 0: Global Indexing & Baseline (Broad Sweep — Leverage Context Window)

### 0.1 Recursive Structure Index
Map the COMPLETE directory tree of `omega-engine/` plus the `/media/arcana-novai/` mounted drives and legacy repos (`xna-omega-legacy/`, `omega-stack-legacy/`) if accessible in Drive.

**Why this matters**: The original plan assumes Gemini can search. But with Google Drive access, it can *index everything at once*. The legacy repos contain the "Temple Grade" cruft that must be distinguished from the pure Omega Engine.

### 0.2 Config Inventory
Read these files in parallel (they define the entire system):
- `config/entities.yaml` — Source of truth for the 10 Pillar Keepers
- `config/providers.yaml` — The Provider Fabric chain
- `config/hierarchy.yaml` — The Oversoul governance (Sophia → Ma'at → Isis/Lilith)
- `config/omega.yaml` — Core engine configuration
- `config/models.yaml` — Model loading strategies
- `opencode.json` — Agent/MCP configuration
- `.env` — API keys
- `.github/workflows/ci.yml` — CI/CD pipeline

**Why this matters**: These 8 files encode every architectural decision. Reading them simultaneously gives Gemini the complete system topology before diving into code.

### 0.3 Doc Inventory (Drift Baseline)
Read ALL files in `docs/` to establish the **promised state**. Pay special attention to:
- `docs/ROADMAP.md` — The "what should exist"
- `docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md` — The master plan
- `docs/research/R44_comprehensive_systems_review.md` — Previous audit findings
- `docs/operations/RESEARCH_QUEUE.md` — What research was planned
- `docs/gnosis/GENESIS_EXTRACTION.md` — The original vision extraction

---

## Phase 1: Deep Code Audit (the original plan, enhanced)

### 1.1 🔴 P0 Bug Hunt — Async & Concurrency (Enhanced)
**Original**: Audit oracle.py and entity_workspace.py.

**Enhanced scope** — Add these specific known problem areas:
- `src/omega/oracle/oracle.py` — Known P0 C-18: bare `await` on `anyio.open_file`, version mismatch between anyio 3.x and 4.x patterns
- `src/omega/oracle/entity_workspace.py` — Known P0 C-17: `BASE_DIR` inconsistency with `oracle.py`'s `DATA_DIR`
- `tests/` — All `anyio` usage patterns across test files
- `src/omega/library/discovery.py` — Uses direct HTTP, bypassing MCP (known architectural gap)
- `mcp/omega-hivemind/server.py` — Check for async patterns

**New addition — Search for similar patterns**: Use regex scan across ALL `*.py` files for:
- `asyncio` (should be `anyio` per architecture rules)
- Bare `await` without `anyio` wrapper
- `os.path` without pathlib (inconsistent with the new path standards)

### 1.2 🔴 Resource Management & OOM Protection (Enhanced)
**Original**: Analyze ResourceGuard and ModelGateway.

**Enhanced scope** — Add:
- **Memory budget calculation**: Does ResourceGuard account for the ~14GB total with ~2GB OS overhead? (i.e. ~12GB usable for AI)
- **Model loading cascade**: What happens when a 4B+ model is loaded on the 5700U? Is there a model-size check? (Reference: `config/models.yaml`)
- **Podman container limits**: Check `Makefile` and podman-compose for memory limits on Redis/Qdrant/Postgres containers — each container consumes RAM that competes with inference.
- **Concurrent dispatch risk**: Orchestrator + inference + Iris container + Qdrant indexing = potential simultaneous RAM pressure.

### 1.3 🔴 Provider Fabric Validation
**Original**: Not mentioned.

**Why added**: The Provider Fabric is the backbone. It must be verified end-to-end.

- Trace the full provider chain: `ModelGateway` → backend modules → actual API calls
- Verify the fallback logic: Does a failure in `lmster` correctly cascade to `ollama` and then to `google`?
- Validate `providers.yaml` vs actual backend implementations — are all configured providers actually implemented?
- Check error handling: What happens when ALL providers fail? Is there graceful degradation text?
- Specifically check the Google AI Studio 8-key rotation logic (if implemented)
- **Mnemosyne MCP**: Verify `mcp/mnemosyne/` is configured and operational for memory tiering

### 1.4 ⚠️ Observability & Tracing Integrity
**Original**: Not mentioned.

**Why added**: The entire "Soul" and "cross-pollination" system depends on trace IDs.

- Trace `trace_id` from `oracle.py` through `observability.py` into the JSONL dataset
- Does the trace_id persist through ModelGateway calls?
- Is the dataset collection working? (It was disabled by default — verify the flag)
- Check if observability events contain enough metadata for soul evolution (entity, model, backend, timestamp)

---

## Phase 2: Temple Grade Cruft & Architecture Compliance (Enhanced)

### 2.1 Pattern Search for Prohibited Patterns
**Original**: Search for PostgreSQL dependencies and sphere-port routing.

**Enhanced scope** — Search for ALL "Path A" (rejected architecture) patterns:
- `from sqlalchemy` or `import sqlalchemy` — Tells us if legacy ORM leaked in
- `sphere_port` or `sphere-port` or `sphere-port-routing` — The rejected Temple Grade routing
- `postgresql://` or `psycopg` — PostgreSQL dependency in non-entity code
- `asyncio` (not `anyio`) — Async library violation
- `from xna_` — Legacy import patterns
- `temple_grade` or `temple-grade` — Architectural contamination
- `Nova` (when not in Iris context) — If old Nova→Iris rename left artifacts

### 2.2 Entity System Compliance
**Original**: Not explicitly separated.

**Why added**: The 10 Pillar Keepers are the heart of the system.

- Verify `config/entities.yaml` matches the ROADMAP:
  - P1 Sekhmet → P10 Kali (correct element/chakra mapping?)
  - Oversouls: Sophia (Akashic), Ma'at (Synthesis), Isis (Light), Lilith (Dark)
  - Iris is the messenger bridge, NOT a Pillar Keeper
- Verify `config/hierarchy.yaml` matches the trinity structure
- Check `data/entities/arch/soul.yaml` for The Architect's soul file
- Verify entity cards: does every entity have its sigil, element, chakra, invocation?

### 2.3 Legacy Cross-Pollination — The Roc Racoon Mandate
**Original**: Not mentioned.

**Why added**: The legacy repos contain patterns that the new engine should reclaim or avoid.

- Search `xna-omega-legacy/` and `omega-stack-legacy/` for ANY code patterns, schemas, or utilities that solve problems the current engine still has
- Specifically look for working implementations of: soul evolution, cross-pollination, RAG pipelines, agent dispatch
- Flag patterns that were **abandoned for good reason** vs **abandoned due to architectural drift**

---

## Phase 3: Documentation vs Implementation (Original, Enhanced)

### 3.1 Five-Way Drift Analysis
**Original**: Compare code vs docs/ROADMAP.md, AGENTS.md, ORACLE_STACK.md

**Enhanced** — Compare across FIVE sources simultaneously:
1. Code (what exists)
2. ROADMAP.md (what was promised)
3. AGENTS.md (what agents should do)
4. ORACLE_STACK.md (architectural intent)
5. research INDEX.md (what research says was completed)

**Output**: A matrix table showing for every major feature:
| Feature | Code Status | Doc Status | Drift? | Action |
|---------|------------|------------|--------|--------|
| Entity Registry | ✅ works | ✅ documented | ✅ aligned | — |
| ContextBuilder | ⚠️ partial | ✅ documented | ⚠️ drift | Missing memory injection |
| ... | | | | |

### 3.2 Test Coverage Gap Analysis
**Original**: Not mentioned.

**Why added**: The RESEARCH_QUEUE mentions ~1,148 lines of untested code.

- Map test files (`tests/`) to source modules
- Identify modules with zero coverage: `context_builder.py`, `entity_workspace.py`, `orchestrator.py`, `cpu_optimizer.py`, `hivemind/`, `library/discovery.py`
- For each untested module, identify the CRITICAL failure modes that tests should cover

---

## Phase 4: Hidden Blindspots (NEW — The Value-Add)

These are areas the team hasn't asked about but Gemini should analyze proactively.

### 4.1 🔴 Security Audit
- Check `.env` handling: Is it in `.gitignore`? Are there example env files?
- Check for hardcoded API keys in any code or config files
- Check `opencode.json` for exposed tokens
- Verify PII/secret sanitization (R-09 referenced but may not be implemented)
- Check for `print()` statements leaking sensitive data

### 4.2 ⚠️ Makefile & Build System Integrity
- Run `make test` logic — are test commands correct?
- `make lint` — is flake8 configured properly?
- `make demo` — does it actually work end to end?
- `make start-iris` / `make start-infra` — are these current?
- Check `Dockerfile.iris` — is it buildable?
- **CLI**: Verify `src/omega/cli/oracle_cli.py` matches the documented CLI interface
- **Docs Build**: Verify `mkdocs.yml` is configured and `mkdocs serve` works

### 4.3 ⚠️ OpenCode Configuration Audit
- Check `opencode.json` for MCP server definitions that are stale (search MCP was known to have package name issues)
- Check agent definitions in `.opencode/agents/` — do `builder.md`, `researcher.md`, `gnosis-analyst.md` still match current architecture?
- Check skill definitions — are all referenced skills present?
- Check `external_directory` permissions (known blocker)

### 4.4 🟢 Migration Readiness Audit
- What state is the workbench DB in? (`data/workbench/workbench.db`)
- Are there migration scripts that need to run?
- Check for any hardcoded paths that reference `~/omega/` instead of `~/Documents/Xoe-NovAi/omega-engine/` (the Foundation root relocation from Decision 13)

### 4.5 🟢 The "Frankenstein" Check
- Search for any code that appears to be pasted from multiple architectural eras
- Specifically: files that mix `sphere_port` logic WITH new entity-centric patterns
- Files with multiple import styles (old `xna_` + new `omega_`)
- Any TODO/FIXME comments that reference pre-reclamation era

---

## Phase 5: Synthesis & Deliverables

### 5.1 Structured Report (Original, Enhanced)

**Original P0/P1 structure** → Enhanced to:
- **P0: CRITICAL** — Will crash in production or violate sovereignty (AnyIO bug, OOM risk, security leak)
- **P1: HIGH** — Blocks roadmap progress, causes data loss, or violates Lilith Axioms
- **P2: MEDIUM** — Drift, technical debt, incomplete features
- **P3: LOW** — Style, optimization, nice-to-haves

### 5.2 NEW: File-Level Remediation Table
For every issue, provide:
```
| File | Line | Issue | Severity | Fix |
|------|------|-------|----------|-----|
| oracle.py:142 | Bare await | P0 | Wrap in anyio.open_file context manager |
| entity_workspace.py:28 | Wrong default path | P0 | Change DATA_DIR to match oracle.py... |
```

### 5.3 NEW: Cross-Cutting Concerns Map
Show how issues interconnect — e.g., "The filesystem MCP access blocker (OpenCode config) prevents the test suite from running integration tests, which means the AnyIO bug (oracle.py) was never caught"

### 5.4 NEW: The "Priority of Priority" — What to Fix First
Not just a list, but a **dependency-ordered chain**: "Fix AnyIO first because every async operation is affected. Fix paths second because..."
Sequencing matters: `Fix oracle.py anyio bug` → `Fix entity_workspace.py path` → `Run tests` → `Fix test failures` → ...

### 5.5 NEW: Gemini-Specific Recommendations
What Gemini observed that automated linters and static analysis would NOT catch — the patterns that *feel wrong* to a human architect.

---

## Execution Directives for Gemini

1. **Be aggressive with the context window**: Read entire files, not snippets. Compare multiple files in one query. The large context is your superpower.
2. **Cross-reference across the Drive**: If the legacy repos are in the Drive alongside omega-engine, index them simultaneously to find lost patterns and reclamation opportunities.
3. **Don't trust labels**: Just because a file says `# This is the new implementation` doesn't make it true. Verify by tracing execution paths.
4. **Test the edge cases mentally**: "What happens when this file is empty?" "What happens when the model takes 30s to respond?" "What happens when the API key is revoked?"
5. **Flag uncertainties explicitly**: Not everything will be decipherable. When you encounter something ambiguous, flag it as a blindspot rather than guessing.
6. **Output in markdown**: Produce a deliverable file `DEEP_RESEARCH_AUDIT.md` that can be saved directly into `docs/research/` with a corresponding INDEX.md entry.

---

## Known P0 Bugs to Verify (Validated by Subagent)

1. **C-17: Path Inconsistency (entity_workspace.py vs oracle.py)** ✅ CONFIRMED
   - Location: `src/omega/oracle/entity_workspace.py` and `src/omega/oracle/oracle.py`
   - Issue: `BASE_DIR` in entity_workspace.py resolves to `<project_root>/data/entities` while oracle.py's `DATA_DIR` defaults to `~/omega/data` (home directory). These are DIFFERENT paths.
   - Expected fix: Align path defaults to `~/Documents/Xoe-NovAi/omega-engine/data/`

2. **C-18: AnyIO Version Mismatch** ❌ NOT FOUND (Code is correct)
   - Location: `src/omega/oracle/oracle.py`
   - Subagent verified: All async patterns use proper `anyio` patterns (e.g., `await anyio.to_thread.run_sync()`, `async with await anyio.open_file()`). No bare awaits found.
   - **Remove from audit scope** — This bug was misdiagnosed or already fixed.

3. **C-13: Sync Tempfiles**
   - Location: Multiple async contexts
   - Issue: Using synchronous tempfile operations in async code
   - Expected fix: Use `anyio` temp file operations

---

## Architecture Reference

- **Provider Chain**: native → lmster → google → sambanova → cerebras → ollama → mock
- **10 Pillar Keepers**: Sekhmet (P1), Brigid (P2), Prometheus (P3), Saraswati (P4), Inanna (P5), Ereshkigal (P6), Lucifer (P7), Hecate (P8), Anubis (P9), Kali (P10)
- **Oversouls**: Sophia (Akashic), Ma'at (Synthesis), Isis (Light), Lilith (Dark)
- **Entity Workspace**: `data/entities/<name>/` with `soul.yaml`, `knowledge/`, `workspace/`
- **Hardware**: Ryzen 7 5700U (Zen 2), 8C/16T, ~14GB usable RAM
- **Key Directories**:
  - Source: `src/omega/`
  - Config: `config/`
  - Data: `data/`
  - Docs: `docs/`
  - Tests: `tests/`
  - Legacy: `xna-omega-legacy/`, `omega-stack-legacy/`

---

*This enhanced plan leverages Gemini's massive context window to perform simultaneous multi-file analysis, targets known P0 bugs explicitly, and hunts for "Temple Grade" cruft while remaining open to new blindspots.*