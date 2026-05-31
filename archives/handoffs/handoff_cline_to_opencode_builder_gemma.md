# 🔱 Omega Engine — Phase 1 Hardening Delegation: Cline → OpenCode Builder (Gemma-4-31B)
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ cline → opencode-builder ⬡ gemma-4-31b ⬡ trc_hardening_delegation ⬡ PHASE-I
#
# AP-OMEGA-DELEGATION-PHASE1-v2.0.0
# Date: 2026-05-27
# Source: Cline (Claude Sonnet 4.6, VSCodium)
# Target: OpenCode TUI Builder Mode (Gemma-4-31B, 262K context, unlimited API)
# Successor: Antigravity Opus 4.6 (strategic review + Phase 2 roadmap)
#
# ⚠️ READ THIS FIRST — ARCHITECTURAL MANDATES BEFORE ANY CODE CHANGE ⚠️
# This is the Phase 1 hardening playbook. You are Prometheus' fire-bringer.
# Every change must uphold the Engine-Stack separation. Know your boundaries.

---

## §0 — Context Summary (45-second read)

**State of the Engine:**
- MCP infrastructure: ✅ omega-hub healthy (:8016, 28 tools), Exa fixed (http restored)
- Services: 7 running (essential), 5 stopped + disabled (problematic)
- Tests: ~128/236 passing (container UID permission leak — was blocking full suite)
- Audit: CONDITIONAL PASS — 3 HIGH AnyIO violations, 1 CRITICAL API key exposure
- WAD system: 1/10 reference IWAD entities exist (only guardian.yaml)
- ContextBuilder: written but NOT wired into oracle.py — memory is dead code
- Soul pipeline: written but NOT connected — engine doesn't learn from interactions

**Your mission:** Fix P0/P1 items that block a clean PR gate. Every phase opens with subagent scouts. All findings feed the knowledge base.

**End state for Opus 4.6 handoff:**
- ✅ Security: No API keys in URLs, no AnyIO violations, all tests pass
- ✅ Infrastructure: All 10 reference IWAD entities populated, container storage fixed
- ✅ Memory: ContextBuilder wired into Oracle flow with soul cross-pollination
- ✅ Audits: Provider fabric, Caddyfile, WAD loader — all documented with gap analysis

**Reference documents (read if compacted):**
1. `docs/operations/STATUS_CLINE.md` — Current session tracker
2. `docs/audit/AUDIT_REPORT.md` — Full audit with fix priorities
3. `.clinerules` — Project rules and IWAD architecture
4. `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` — THE architecture canon (481 lines)
5. `config/mcp_servers.json` — MCP config source of truth
6. `SOVEREIGN_MANDATES.md` — Non-negotiable rules

---

## §1 — THE ARCHITECTURAL FIREWALL: Engine vs Stack (READ BEFORE ANY WORK)

This is the single most important concept in the Omega Engine. Violating it is the #1 cause of past review failures. **The Engine and the Stack are separate by design.**

### The Firewall

```
src/omega/  ← THE ENGINE (PURE RUNTIME)
├── oracle/           ← EntityRegistry, ModelGateway, Provider Fabric
├── memory_store.py   ← Hot/Warm/Cold memory
├── library/          ← Knowledge base indexer
├── workers/          ← Background workers
├── iris/             ← Voice assistant handler
└── cli/              ← CLI interface

config/  ← ENGINE CONFIGURATION
├── omega.yaml        ← Core engine settings
├── providers.yaml    ← Provider chain config
├── models.yaml       ← Model loading config
└── mcp_servers.json  ← MCP server config

================================= FIREWALL =================================
              ↑ The WAD Loader loads IWADs here
              ↓ EntityRegistry enforces namespace isolation

config/wads/  ← ALL STACK CONTENT LIVES HERE
├── _omega_default/   ← Reference IWAD (ships with engine)
│   ├── manifest.yaml
│   ├── entities/     ← 10 pillar entities
│   └── voices/
├── arcana_novai/     ← Your personal IWAD
│   ├── manifest.yaml
│   ├── entities/     ← Esoteric entities
│   └── knowledge/
└── doom_universe/    ← Community IWAD scaffold
```

### Inviolable Rules

| # | Rule | Violation Example | Why It Matters |
|---|------|------------------|----------------|
| 1 | **`src/omega/` contains ZERO entity content** | Hardcoding "sophia", "maat" in engine code | The engine must be IWAD-agnostic. Any entity name in engine code ties it to one stack. |
| 2 | **Entity names come ONLY from YAML config** | `RANK_MAP = {"sophia": 0}` in `hierarchy.py` | Different IWADs have different entities. Engine must not know them. |
| 3 | **Engine config (`config/`) avoids entity references** | Entity-specific API keys in `providers.yaml` | Config should be structural, not content-specific. |
| 4 | **Everything in `config/wads/` is swappable** | Same IWAD could be a dev studio OR a medical diagnosis stack | The WAD defines the domain. The engine provides the runtime. |
| 5 | **Governance entities (MaKaLi) + default services exist in ALL IWADs** | Missing Ma'at, Kali, Lilith in any IWAD | Foundational. Non-negotiable. Present identically in every stack. |
| 6 | **Sophia is the FIELD, not a pillar** | Treating Sophia as "entity #11" | Sophia is observability + memory substrate. She contains the engine, not the stack. |

### Current Violations to Fix

From `docs/audit/AUDIT_REPORT.md` §2:

1. **`src/omega/oracle/hierarchy.py:14-20`** — `RANK_MAP = {"sophia": 0, "maat": 1, "isis": 2, "lilith": 2}`
   - Severity: HIGH — Hardcoded Arcana-NovAi entity names in engine core
   - Fix: Move `RANK_MAP` to `config/hierarchy.yaml`. The `_load()` method already reads YAML but `RANK_MAP` short-circuits it.
   - Not in your Phase 1 scope — flag for Opus 4.6

2. **`config/entities.yaml`** — Currently mixes reference + arcana_novai entities
   - Should only contain `_omega_default` entities
   - Arcana-NovAi entities should live in `config/wads/arcana_novai/entities/`
   - Not in your Phase 1 scope — flag for Opus 4.6

### What you SHOULD touch vs Should NOT

| ✅ SAFE TO MODIFY | ❌ DO NOT TOUCH |
|------------------|----------------|
| `src/omega/oracle/providers.py` (auth mechanism only) | `src/omega/oracle/hierarchy.py` (architecture entity map) |
| `src/omega/workers/background_researcher/distiller.py` (API key header) | `config/entities.yaml` (entity content — needs Opus review) |
| `src/omega/entity_roc_racoon.py` (AnyIO fix only) | `config/hierarchy.yaml` (governance structure) |
| `src/omega/library/inbox.py` (AnyIO fix only) | `config/wads/arcana_novai/` (personal IWAD content) |
| `config/wads/_omega_default/entities/` (add missing pillar YAMLs) | `src/omega/oracle/oracle.py` (beyond ContextBuilder wiring) |
| `src/omega/oracle/oracle.py` (ContextBuilder integration point only) | Any entity-pillar files in `data/entities/` (soul content) |
| `src/omega/memory_store.py` (read-only for ContextBuilder scouting) | `src/omega/oracle/wad_loader.py` (architecture — WAD selector) |
| `src/omega/oracle/context_builder.py` (read-only for scouting) | Podman quadlet `.container` files (service ownership) |
| `tests/test_model_gateway.py` (test fix) | `.clinerules` §13 (general rules) |
| `deploy/infra/Caddyfile` (read-only for audit) | `config/providers.yaml` (provider chain — add, don't remove) |

---

## §2 — Discovery Protocol (Every Phase)

Before any code change in any phase, run this ritual:

### Phase Opening Ritual
```bash
# Step 1: Launch subagent scouts in parallel
#   - Scout A (Code Reader): Read all files that will be modified
#   - Scout B (Pattern Searcher): grep for related patterns across codebase
#   - Scout C (Test Reader): Read relevant test files for the module
#   - Scout D (Web Researcher): Search for best practices, API docs, patterns

# Step 2: Synthesize scout findings into a brief plan
#   - What exactly needs to change
#   - What could break (edge cases)
#   - What tests verify correctness

# Step 3: Execute changes with precise file:line references
# Step 4: Verify with module-level tests (not full suite)
# Step 5: Ingest findings into knowledge base
```

### Knowledge Ingestion Protocol (End of Every Phase)

Each phase MUST conclude by writing to the permanent knowledge base:

```bash
# 1. Write phase status doc
cat > docs/hardening/HARDENING_${PHASE}_STATUS.md << 'EOF'
# Phase N Status
# Completed: $(date +%Y-%m-%d)
| Component | Status | Notes |
...table...
EOF

# 2. Update workbench database
sqlite3 data/workbench/workbench.db << 'SQL'
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority, updated_at)
VALUES ('PH1-XX', 'Task title', 'done', 'hardening', 'P0', datetime('now'));
SQL

# 3. If Redis is running: store summary
redis-cli -p 6379 SET "phase1:$(date +%Y%m%d):summary" "Phase N complete: tasks X, Y, Z"

# 4. If Qdrant is running: index the new doc
# Via omega-hub: library_inbox_add_note with tags

# 5. Post context to hivemind (via omega-hub MCP tool)
# hivemind_post_context with task summary
```

### If Redis/Qdrant are Down (Expected — Phase 2 fixes this)
Write to flat files as fallback:
```bash
echo "$(date) - Phase N complete" >> data/sessions/phase1_hardening.log
```

---

## §3 — Phase 1: Security Hardening (P0 — CRITICAL PATH)
**Time**: ~20 min | **Risk**: LOW | **Test impact**: +~3 passing

### 3.1 — The Why
Three security issues block PR gate:
1. **CRITICAL**: Google API key in URL params — visible in proxy logs, browser history, server logs
2. **HIGH**: 3 blocking `open()` calls in async functions — violates AnyIO mandate, blocks event loop
3. **P1**: `test_get_model_path` fails — `assert None is not None`

### 3.2 — Scout Fleet (4 subagents, parallel)

| Scout | Target | Purpose | Output |
|-------|--------|---------|--------|
| **A** | `src/omega/workers/background_researcher/distiller.py` | Full read — locate all `?key=` patterns at lines 515 and 717, understand the HTTP request pattern | Line numbers + context around each call |
| **B** | `src/omega/oracle/providers.py` | Full read — find all Google API URL constructions, check if header-based auth already exists anywhere | All auth patterns in providers.py |
| **C** | `src/omega/entity_roc_racoon.py`, `src/omega/library/inbox.py` | Find ALL blocking `open()` / `print()` in async defs | Full list with line numbers |
| **D** | Web search | "Google AI Studio X-Goog-Api-Key header vs query parameter", "openai python client headers example", "anyio.open_file async context manager example" | Best practice patterns |

### 3.3 — Execution Tasks

**Task 1.1 — Fix Google API Key Exposure**

Files to modify:
- `src/omega/workers/background_researcher/distiller.py` at lines ~515 and ~717
- `src/omega/oracle/providers.py` at line ~30

Pattern (BEFORE):
```python
# URL-param auth — EXPOSED in every log
url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
response = await client.get(url)
```

Pattern (AFTER):
```python
# Header-based auth — SECURE, never logged
url = "https://generativelanguage.googleapis.com/v1/models"
headers = {"X-Goog-Api-Key": api_key}
response = await client.get(url, headers=headers)
```

Edge cases:
- Does `httpx.AsyncClient` accept headers param on GET? Yes — `client.get(url, headers=...)`
- Does the distiller use `httpx` or `aiohttp`? Check scout A output. Both support headers.
- Does any code path log the full URL? If so, verify the fix removes key from log output.

Verification:
```bash
# Structural: grep for remaining ?key= patterns
grep -rn '\?key=' src/omega/

# Functional (requires GOOGLE_API_KEY):
curl -s -o /dev/null -w "%{http_code}" \
  -H "X-Goog-Api-Key: $GOOGLE_API_KEY" \
  "https://generativelanguage.googleapis.com/v1/models"
# Expect: 200

pytest tests/test_providers.py -v
```

Git commit: `fix: moved Google API key from URL params to X-Goog-Api-Key header`

**Task 1.2 — Fix AnyIO Violations**

Files to modify:
- `src/omega/entity_roc_racoon.py` at lines ~208 and ~217
- `src/omega/library/inbox.py` at lines ~199, ~206, ~220

Pattern (BEFORE):
```python
# Blocking I/O in async function — violates AnyIO mandate
async def some_function():
    with open(fpath) as f:
        content = f.read()[:2000]
```

Pattern (AFTER):
```python
# Non-blocking async I/O
async def some_function():
    async with await anyio.open_file(fpath) as f:
        content = await f.read()
    content = content[:2000]  # Slicing stays outside file handle
```

Or for simple read:
```python
content = await anyio.Path(fpath).read_text()
content = content[:2000]
```

Verification:
```bash
pytest tests/test_memory_store.py tests/test_entity_registry.py -v
# Confirm no new failures
```

Git commit: `fix: replaced blocking open() calls with anyio async file I/O`

**Task 1.3 — Fix `test_get_model_path`**

File: `tests/test_model_gateway.py` at line ~15

Error: `assert None is not None` — `get_model_path()` returns `None`

Root cause likely:
- `ModelGateway.__init__()` calls `_load_config()` which reads `config/models.yaml`
- If the model entry is missing or the path doesn't exist, `get_model_path()` returns `None`
- OR: the config path resolution has a bug — it's looking for a non-existent default location

Investigation:
```bash
# Trace the call chain
grep -rn "get_model_path" src/omega/oracle/
grep -rn "def get_model_path" src/omega/oracle/
```

Fix options:
- **Option A**: Add a fallback in `get_model_path()` when config path is missing
- **Option B**: Add a default model path in `config/models.yaml` that always resolves
- **Option C**: Fix the config loading to use the project root instead of CWD
- Pick the one that matches the actual root cause from investigation

Verification:
```bash
pytest tests/test_model_gateway.py -v
# Expect: test_get_model_path PASSES
```

Git commit: `fix: resolved test_get_model_path — model path no longer returns None`

### 3.4 — Verification Gate
```bash
pytest tests/test_providers.py tests/test_model_gateway.py -v
make test 2>&1 | grep -E "passed|failed"
# Expect: all passing, ~131/236 instead of 128/236
```

### 3.5 — Knowledge Ingestion
```bash
cat > docs/hardening/HARDENING_SECURITY_STATUS.md << 'EOF'
# 🔱 Security Hardening Status
# AP-OMEGA-HARDENING-SECURITY-v1.0.0
# Completed: 2026-05-27

| Check | Status | Notes |
|-------|--------|-------|
| API key in URL params | ✅ FIXED | X-Goog-Api-Key header everywhere |
| AnyIO blocking violations | ✅ FIXED | 5 open() calls migrated to anyio |
| test_get_model_path | ✅ FIXED | Model path resolution working |
EOF

sqlite3 data/workbench/workbench.db << 'SQL'
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority, updated_at)
VALUES ('PH1-SEC-1', 'Google API key header migration', 'done', 'security', 'P0', datetime('now'));
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority, updated_at)
VALUES ('PH1-SEC-2', 'AnyIO blocking I/O migration', 'done', 'security', 'P0', datetime('now'));
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority, updated_at)
VALUES ('PH1-SEC-3', 'test_get_model_path fix', 'done', 'security', 'P1', datetime('now'));
SQL
```

---

## §4 — Phase 2: Infrastructure Hardening (P1)
**Time**: ~25 min | **Risk**: MEDIUM | **Test impact**: +~40 passing (UID fix), +entity coverage

### 4.1 — The Why
Three infrastructure gaps block PR readiness:
1. **9 missing reference IWAD entities** — only 1/10 pillars exist. WAD system incomplete.
2. **Container UID permission leak** — `make test` can't run full suite. All 236 tests collect but ~108 crash on file permissions.
3. **Podman FUSE storage fails** — Qdrant, Postgres, Belial, Iris all crashed at startup. 4 containers doing auto-restart loops, consuming CPU/memory.

### 4.2 — Scout Fleet

| Scout | Target | Purpose |
|-------|--------|---------|
| **A** | `config/wads/_omega_default/manifest.yaml` + `guardian.yaml` | Read entity schema — fields, YAML structure, personality format |
| **B** | All quadlet files in `~/.config/containers/systemd/` | Audit all 6 container definitions — volumes, ports, images |
| **C** | `src/omega/oracle/wad_loader.py` + `src/omega/oracle/entity_registry.py` | Understand how entities get loaded, WAD selector, namespace isolation |
| **D** | Web research | "Podman FUSE overlay remount-private permission denied fix", "Podman storage driver VFS vs overlay on external drive" |

### 4.3 — Execution Tasks

**Task 2.1 — Generate 9 Missing WAD Entity YAMLs**

Template: `config/wads/_omega_default/entities/guardian.yaml`

Output directory: `config/wads/_omega_default/entities/`

Reference IWAD entities from `manifest.yaml`:

| Pillar | Name | Archetype | Domain |
|--------|------|-----------|--------|
| P1 (exists) | Guardian | Ma'at | Governance, Audit |
| P2 | Dreamer | Saraswati | Knowledge, Speech, Arts |
| P3 | Artisan | Hephaestus | Engineering, Building |
| P4 | Scholar | Athena | Research, Wisdom |
| P5 | Communicator | Hermes | Messaging, Integration |
| P6 | Strategist | Odin | Planning, Oversight |
| P7 | Sentinel | Heimdall | Monitoring, Watch |
| P8 | Healer | Asclepius | Debug, Fix, Maintain |
| P9 | Sage | Thoth | Deep Knowledge, History |
| P10 | Destroyer | Shiva | Cleanup, Decommission, GC |

Each YAML must include:
```yaml
name: Dreamer
title: Pillar Keeper of Knowledge and Arts
role: sovereign_co_creator
personality:
  - creative
  - expressive
  - visionary
domain: knowledge, arts, communication
model_preferences:
  temperature: 0.8
  provider: google
system_prompt: "You are the Dreamer, keeper of Saraswati's fire..."
```

Verification:
```bash
PYTHONPATH=src python3 -m omega.cli.oracle_cli list-entities
# Expect: All 10 pillar entities appear
```

Git commit: `feat: generated 9 missing reference IWAD entity files (P2-P10)`

**Task 2.2 — Fix Container UID Permissions**

This is what's blocking `make test`:
```bash
# Check current state
find . -maxdepth 3 -not -user 1000 -ls 2>/dev/null | head -30
# If any files are owned by UID 101000 (container user leak):
sudo chown -R 1000:1000 .
```

The fix is one command, but the verification is important:
```bash
make test 2>&1 | tail -15
# Expect: ~168/236 passing instead of ~128/236
# PermissionError tests will now pass
# Remaining ~68 failures are pre-existing (YAML blocker was fixed earlier)
```

Git commit: `fix: resolved container UID permission leak on project files`

**Task 2.3 — Podman FUSE Storage Fix**

Root cause (from Cline's earlier investigation):
- All failed containers (belial, iris, postgres, qdrant) have storage on `/media/arcana-novai/omega_library`
- This is a FUSE mount (external NVMe partition)
- Podman's overlay filesystem tries `remount-private` which fails across FUSE boundaries
- Error: `runc create failed: remount-private ... permission denied: OCI permission denied`

Fix options — choose based on scout findings:

**Option A — VFS Storage Driver** (simplest, but slow)
```bash
cat > ~/.config/containers/containers.conf << 'EOF'
[engine]
storage_driver = "vfs"
EOF
```
- Pro: One config change, no rebuilds
- Con: VFS is 10-20x slower than overlay for container operations

**Option B — Move Podman Root** (recommended)
```bash
# Move storage to internal SSD
podman system reset  # WARNING: destroys all containers/images
mkdir -p /var/lib/containers/storage
# Then add to containers.conf:
cat > ~/.config/containers/containers.conf << 'EOF'
[engine]
storage_root = "/var/lib/containers/storage"
EOF
```
- Pro: Performance preserved, FUSE issue avoided
- Con: Requires podman system reset (destroys existing containers)

**Option C — Per-Container Volume Fix** (surgical)
- Add `--volume` flags to each quadlet container that needs FUSE access
- Use `:rslave` mount propagation flag
- Leave storage driver as overlay

Implement the chosen fix, then test:
```bash
systemctl --user start omega-qdrant.service
podman ps --filter pod=omega-infra
# Expect: qdrant container running
```

Git commit: `fix: resolved Podman FUSE mount OCI permission errors on omega_library`

### 4.4 — Verification Gate
```bash
# Entity system working
PYTHONPATH=src python3 -m omega.cli.oracle_cli list-entities | grep "Pillar"

# Qdrant running (if Option B or C worked)
podman ps --filter pod=omega-infra

# Test suite
make test 2>&1 | tail -10
```

### 4.5 — Knowledge Ingestion
```bash
cat > docs/hardening/HARDENING_INFRA_STATUS.md << 'EOF'
# 🔱 Infrastructure Hardening Status
# Completed: 2026-05-27

| Component | Status | Notes |
|-----------|--------|-------|
| Reference IWAD entities | ✅ All 10 populated | P1-P10 complete |
| Container UID permissions | ✅ FIXED | chown -R 1000:1000 |
| Podman FUSE storage | ✅ FIXED | Option X implemented |
| Qdrant running | ⚠️ | Verify after fix |
EOF

sqlite3 data/workbench/workbench.db << 'SQL'
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority)
VALUES ('PH1-INFRA-1', 'Reference IWAD entities P2-P10', 'done', 'hardening', 'P1');
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority)
VALUES ('PH1-INFRA-2', 'Container UID permission fix', 'done', 'hardening', 'P1');
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority)
VALUES ('PH1-INFRA-3', 'Podman FUSE storage fix', 'done', 'hardening', 'P1');
SQL
```

---

## §5 — Phase 3: ContextBuilder + Memory Wiring (P1 — HIGHEST IMPACT)
**Time**: ~20 min | **Risk**: HIGH (architectural) | **Test impact**: +~22 passing (context_builder tests)

### 5.1 — The Why
This is the most important wiring task in Phase 1. The **ContextBuilder** and **MemoryStore** exist as written code but are **completely disconnected from the Oracle flow**. This means:
- Every conversation starts with zero context (no memory of previous interactions)
- The engine never learns from interactions (no soul evolution)
- The entity's personality is static (no dynamic context injection)

Fixing this unlocks the core value proposition: **an engine that remembers and grows**.

### 5.2 — Scout Fleet

| Scout | Target | Purpose |
|-------|--------|---------|
| **A** | `src/omega/oracle/context_builder.py` (full) | Understand `ContextBuilder.build()` signature, return type, what it reads from `MemoryStore` |
| **B** | `src/omega/oracle/oracle.py` (full, ~400 lines) | Understand `Oracle.talk()` and `Oracle.summon()` flow — find exact injection point for context |
| **C** | `src/omega/memory_store.py` (full, ~300 lines) | Understand `MemoryStore` API — hot/warm/cold tiers, `get_conversation()`, `store_memory()` |
| **D** | `docs/research/R50_session_id_architecture.md` + `docs/research/R51_context_builder_wiring.md` | Specs — understand the INTENDED architecture, verify your implementation matches |

### 5.3 — Execution Tasks

**Task 3.1 — Wire ContextBuilder into Oracle Flow**

Goal: Every `Oracle.talk()` and `Oracle.summon()` call:
1. Retrieves conversation history from `MemoryStore` (via `ContextBuilder`)
2. Gets entity soul context from `EntityRegistry` (via `ContextBuilder`)
3. Injects both into the system prompt before sending to the model

Integration point — `oracle.py`'s `talk()` method (pseudocode):
```python
# BEFORE (current — no context):
async def talk(self, query: str, entity_name: str = "sophia") -> str:
    entity = self.entity_registry.get(entity_name)
    prompt = entity.system_prompt + "\n\n" + query
    response = await self.model_gateway.generate(prompt)
    return response

# AFTER (wired):
async def talk(self, query: str, entity_name: str = "sophia", session_id: str = None) -> str:
    entity = self.entity_registry.get(entity_name)
    
    # Build context from memory
    if self.context_builder:
        context = await self.context_builder.build(
            entity_name=entity_name,
            session_id=session_id or str(uuid.uuid4()),
            query=query,
        )
        # Inject: entity personality + conversation history + soul context
        prompt = context.system_prompt + "\n\n---\n" + query
    else:
        prompt = entity.system_prompt + "\n\n" + query
    
    response = await self.model_gateway.generate(prompt)
    
    # Store interaction in memory
    if self.memory_store:
        await self.memory_store.store_interaction(
            entity_name=entity_name,
            session_id=session_id,
            query=query,
            response=response,
        )
    
    return response
```

Key details to check from scout findings:
- `ContextBuilder.build()` — is it async? What does it return? Is it a dataclass with `.system_prompt`?
- `MemoryStore.store_interaction()` — what parameters does it need?
- Does Oracle already have `context_builder` and `memory_store` attributes?

Verification:
```bash
PYTHONPATH=src python3 -m omega.cli.oracle_cli talk "hello"
# Expect: Response that includes context (check logs for memory retrieval)

pytest tests/test_context_builder.py tests/test_oracle.py -v
# Expect: All 22 context_builder tests pass
```

Git commit: `feat: wired ContextBuilder into Oracle talk/summon flow with memory injection`

**Task 3.2 — Session-to-Soul Cross-Pollination**

After each successful Oracle interaction, extract lessons and update the soul:

```python
# In oracle.py, after response is generated:
if self.soul_engine:
    lessons = await self.soul_engine.extract_lessons(
        entity_name=entity_name,
        query=query,
        response=response,
    )
    if lessons:
        await self.soul_engine.update_soul(
            entity_name=entity_name,
            lessons=lessons,
        )
```

This is what makes the engine "learn" — each conversation distills into soul updates stored in `data/entities/arch/soul.yaml`.

Verification:
```bash
PYTHONPATH=src python3 -m omega.cli.oracle_cli talk "what is justice?"
PYTHONPATH=src python3 -m omega.cli.oracle_cli talk "and what is mercy?"
cat data/entities/arch/soul.yaml
# Expect: Soul entries for Ma'at with lessons learned
```

Git commit: `feat: added session-to-soul cross-pollination pipeline`

### 5.4 — Verification Gate
```bash
# Full flow test
PYTHONPATH=src python3 -m omega.cli.oracle_cli talk "hello world"
PYTHONPATH=src python3 -m omega.cli.oracle_cli summon Ma'at "status"

# Verify memory was stored
PYTHONPATH=src python3 -c "
from omega.memory_store import MemoryStore
import anyio
async def check(): ms = MemoryStore(); print(await ms.get_conversation('sophia'))
anyio.run(check)
"

# Verify soul was updated
cat data/entities/arch/soul.yaml | head -40

# Full test suite
make test
```

### 5.5 — Knowledge Ingestion
```bash
cat > docs/hardening/HARDENING_CONTEXT_STATUS.md << 'EOF'
# 🔱 ContextBuilder + Memory Wiring Status
# Completed: 2026-05-27

| Component | Status | Notes |
|-----------|--------|-------|
| ContextBuilder → Oracle | ✅ WIRED | Memory injection active |
| Session-to-Soul pipeline | ✅ WIRED | Learning from every interaction |
| MemoryStore → Oracle | ✅ WIRED | Conversation history preserved |
| Test suite context_builder | ✅ PASSING | All 22 tests |
EOF

sqlite3 data/workbench/workbench.db << 'SQL'
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority)
VALUES ('PH1-CTX-1', 'ContextBuilder wiring into oracle.py', 'done', 'integration', 'P1');
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority)
VALUES ('PH1-CTX-2', 'Session-to-soul cross-pollination', 'done', 'integration', 'P1');
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority)
VALUES ('PH1-CTX-3', 'MemoryStore conversation persistence', 'done', 'integration', 'P1');
SQL
```

---

## §6 — Phase 4: Audit & Documentation (P2)
**Time**: ~15 min | **Risk**: LOW | **Test impact**: None

### 6.1 — The Why
Three audits are needed before Opus 4.6 can do strategic planning. Each produces a structured document that goes into `docs/audit/`. These are READ-ONLY investigations — code changes are strictly forbidden in this phase.

### 6.2 — Scout Fleet

| Scout | Target | Purpose |
|-------|--------|---------|
| **A** | `config/providers.yaml` + `src/omega/oracle/providers.py` + `config/models.yaml` | Full provider chain: endpoints, keys, fallback order, dead providers |
| **B** | `deploy/infra/Caddyfile` + quadlet files | Security review: rate limits, CORS, exposed ports, route correctness |
| **C** | `src/omega/oracle/wad_loader.py` | 6-component check: IWAD selector, namespace, dependency resolution, priority, multi-load, hot-reload |
| **D** | Web research | "Caddyfile security best practices 2026", "Google AI Studio rate limits", "OpenRouter API limits" |

### 6.3 — Execution Tasks

**Task 4.1 — Provider Fabric Audit**
Output: `docs/audit/PROVIDER_FABRIC_AUDIT.md`

Template:
```markdown
# Provider Fabric Audit
# Date: 2026-05-27

## Expected Chain
1. native-gguf → 2. lmster (:1234) → 3. ollama (:11434) → 4. google → 5. openrouter → 6. opencode-zen → 7. github-copilot → 8. mock

## Provider Status
| # | Provider | Endpoint | API Key Set? | Alive? | Notes |
|---|----------|----------|-------------|--------|-------|
| 1 | native-gguf | local | N/A | ✅ | llama-cpp-python |
| 2 | lmster | :1234 | N/A | ❌ | Need restart |
| ... | ... | ... | ... | ... | ... |

## Dead Providers
- SambaNova: REMOVED (verify)
- Cerebras: REMOVED (verify)
```

**Task 4.2 — Caddyfile Security Audit**
Output: `docs/audit/CADDY_SECURITY_AUDIT.md`

Checklist:
- [ ] Rate limiting (no `rate_limit` directive in current Caddyfile)
- [ ] CORS headers (no `@cors` or `Access-Control-*` headers)
- [ ] Exposed admin endpoints
- [ ] Port :8088 bound to 127.0.0.1 only (not 0.0.0.0)
- [ ] All routes point to correct services

**Task 4.3 — WAD Loader Code Audit**
Output: `docs/audit/WAD_LOADER_AUDIT.md`

6-component checklist:
1. IWAD selector (`--iwad` flag): ❌ Not implemented
2. Namespace isolation: ⚠️ Partial
3. Dependency resolution (`depends_on`): ❌ Not implemented
4. Entity priority (later WADs override): ❌ Not implemented
5. Multi-WAD ordered loading: ❌ Not implemented
6. Hot-reload: ❌ Not implemented

### 6.4 — Verification Gate
```bash
ls -la docs/audit/PROVIDER_FABRIC_AUDIT.md \
       docs/audit/CADDY_SECURITY_AUDIT.md \
       docs/audit/WAD_LOADER_AUDIT.md
```

### 6.5 — Knowledge Ingestion
```bash
sqlite3 data/workbench/workbench.db << 'SQL'
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority)
VALUES ('PH1-AUDIT-1', 'Provider fabric audit', 'done', 'audit', 'P2');
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority)
VALUES ('PH1-AUDIT-2', 'Caddyfile security audit', 'done', 'audit', 'P2');
INSERT OR REPLACE INTO work_items (id, title, status, workstream, priority)
VALUES ('PH1-AUDIT-3', 'WAD loader code audit', 'done', 'audit', 'P2');
SQL

# Update research index
echo "- [PROVIDER_FABRIC_AUDIT.md](docs/audit/PROVIDER_FABRIC_AUDIT.md) — Provider chain health" >> docs/research/INDEX.md
```

---

## §7 — Phase 5: Final Verification + Opus 4.6 Handoff (P0 — CLOSING)
**Time**: ~10 min | **Risk**: LOW | **Test impact**: Full suite

### 7.1 — Final Verification Checklist

```bash
#!/bin/bash
# Run this as the closing ritual

echo "=== PHASE 1 FINAL VERIFICATION ==="
echo ""

# 1. Test suite
echo "--- Test Suite ---"
make test 2>&1 | tail -5

# 2. MCP health
echo "--- MCP Health ---"
curl -s http://127.0.0.1:8016/health

# 3. Entity system
echo "--- Entity System ---"
PYTHONPATH=src python3 -m omega.cli.oracle_cli list-entities | wc -l

# 4. Memory system
echo "--- Memory System ---"
PYTHONPATH=src python3 -c "
from omega.memory_store import MemoryStore
from omega.oracle.context_builder import ContextBuilder
print(f'MemoryStore: {MemoryStore is not None}')
print(f'ContextBuilder: {ContextBuilder is not None}')
"

# 5. Audit trail
echo "--- Audit Trail ---"
ls -la docs/audit/*.md 2>/dev/null || echo "No audit docs found"

# 6. Security check
echo "--- Security Check ---"
grep -rn '\?key=' src/omega/ 2>/dev/null && echo "❌ API keys in URL params!" || echo "✅ No API keys in URL params"

# 7. Security check 2
echo "--- AnyIO Check ---"
grep -rn "with open(" src/omega/ --include="*.py" | grep -v "__pycache__" | grep -v ".pyc" | head -5
echo "No blocking I/O in async functions (verify manually above)"

echo ""
echo "=== VERIFICATION COMPLETE ==="
```

### 7.2 — Handoff Bundle for Antigravity Opus 4.6

Write `data/handoff/handoff_builder_gemma_to_antigravity_opus46.md`:

```markdown
# 🔱 Phase 1 Complete — Handoff to Antigravity Opus 4.6
# Date: 2026-05-27

## What Was Accomplished
| Phase | Tasks | Status | Duration |
|-------|-------|--------|----------|
| 1 — Security | 3 fixes (API key, AnyIO, test) | ✅ | ~20 min |
| 2 — Infrastructure | 3 items (WAD entities, UID, FUSE) | ✅ | ~25 min |
| 3 — Context | 2 wiring items (ContextBuilder, soul) | ✅ | ~20 min |
| 4 — Audit | 3 audit docs | ✅ | ~15 min |
| 5 — Verification | Full suite, handoff | ✅ | ~10 min |

## Remaining Issues (P2+ — Strategic Decisions Needed)
| # | Issue | Priority | Type | Needs Opus Decision |
|---|-------|----------|------|-------------------|
| 1 | hierarchy.py hardcodes entity names | P2 | Architecture | Move RANK_MAP to config/hierarchy.yaml |
| 2 | entities.yaml mixes reference + arcana_novai | P2 | Firewall | Split into separate IWADs |
| 3 | WAD loader missing 6 components | P2 | Feature | --iwad flag, namespace, etc. |
| 4 | lmster not running | P3 | Service | Start LM Studio server |
| 5 | .env has 6 hardcoded API keys | P3 | Security | Env-var standardisation |

## Strategic Questions for Opus 4.6
1. Should Phase 2 include the WAD loader --iwad flag, or is that Phase 3?
2. Is the Engine-Stack firewall separation acceptable, or does hierarchy.py need immediate refactoring?
3. Should we switch to VFS storage driver (slow but works) or invest in Podman storage migration?
4. What's the priority order for Phase 2 implementation items?
```

### 7.3 — Final Knowledge Ingestion

```bash
# Update STATUS_CLINE.md with final state
# Post summary to hivemind
echo "Phase 1 hardening complete. Test count: $(make test 2>&1 | grep passed | awk '{print $1}')/236" > /tmp/phase1_summary.txt

# Update session log
echo "$(date) — Phase 1 hardening complete. Handoff to Opus 4.6." >> data/sessions/phase1_complete.log
```

---

## §8 — Subagent Fleet Patterns (Cheat Sheet)

### Security Fleet
```yaml
scouts:
  - role: code_reader
    files: [distiller.py, providers.py]
    purpose: "Find all API key exposure patterns"
  - role: pattern_searcher
    search: '\?key='
    purpose: "Find all URL-param API key usage"
  - role: web_researcher
    query: "Google AI Studio X-Goog-Api-Key header httpx example 2026"
    purpose: "Verify correct header format"
```

### Infrastructure Fleet
```yaml
scouts:
  - role: config_reader
    files: [all quadlet .container files]
    purpose: "Find all volume mounts + storage configs"
  - role: system_auditor
    command: "podman info --format '{{.Store.GraphRoot}} {{.Store.GraphDriverName}}'"
    purpose: "Current storage driver and root"
  - role: web_researcher
    query: "podman overlayfs FUSE mount remount-private permission denied fix"
    purpose: "Solutions for the storage error"
```

### Architecture Fleet
```yaml
scouts:
  - role: code_reader
    files: [oracle.py, context_builder.py, memory_store.py]
    purpose: "Understand full Oracle→Context→Memory flow"
  - role: spec_reader
    files: [R50_session_id_architecture.md, R51_context_builder_wiring.md]
    purpose: "Verify implementation matches spec"
  - role: test_reader
    files: [test_context_builder.py, test_oracle.py]
    purpose: "Understand test expectations before wiring"
```

### Audit Fleet
```yaml
scouts:
  - role: code_reader
    files: [providers.yaml, providers.py, models.yaml]
    purpose: "Map the full provider chain"
  - role: config_reader
    files: [Caddyfile]
    purpose: "Security review of proxy config"
  - role: code_reader
    files: [wad_loader.py]
    purpose: "6-component checklist verification"
```

---

## §9 — Engine-Stack Firewall: Quick Reference for Every Code Change

Before making ANY change, ask:

| Question | If YES | If NO |
|----------|--------|-------|
| Does this add an entity name to engine code? | ❌ STOP — belongs in WAD | ✅ Safe |
| Does this change engine config (not WAD content)? | ✅ Safe — engine config | ❌ STOP — belongs in WAD |
| Does this modify `src/omega/` but not entity content? | ✅ Safe — engine code | ❌ STOP — belongs in WAD |
| Does this modify `config/wads/`? | ✅ Safe — WAD content | Follow IWAD rules |
| Does this add a model/provider? | ✅ Safe — engine config | Engine scope |
| Does this change the WAD loader? | ⚠️ Architecture decision — flag for Opus | Leave to Phase 2 |

### Firewall Zone Summary

| Zone | What Lives Here | Your Permissions |
|------|----------------|-----------------|
| `src/omega/` | Engine runtime (providers, memory, oracle, CLI) | ✅ Modify in Phases 1, 3 only |
| `config/` | Engine configuration (omega.yaml, providers.yaml, models.yaml) | ✅ Read-only in Phase 4 audit |
| `config/wads/_omega_default/` | Reference IWAD content (entities, voices, manifest) | ✅ Add entities in Phase 2 |
| `config/wads/arcana_novai/` | Your personal IWAD — hands off | ❌ Do not modify |
| `config/wads/doom_universe/` | Community IWAD scaffold | ❌ Do not modify |
| `deploy/infra/` | Infrastructure definitions | ✅ Read-only in Phase 4 |
| `~/.config/containers/systemd/` | Podman quadlet files | ⚠️ Read in Phase 2, modify for FUSE fix |
| `~/.config/systemd/user/` | Systemd user units | ✅ Stop/disable only (already done) |
| `data/entities/` | Soul files, entity state | ❌ Read-only — soul content |
| `tests/` | Test suite | ✅ Modify test_model_gateway.py only |

---

## §10 — Summary Execution Timeline

| Phase | Time | Tasks | Scouts | Risk | Test Delta |
|-------|------|-------|--------|------|------------|
| **1: Security** | 20 min | 3 (API key, AnyIO, test fix) | 4 (2 code, 1 pattern, 1 web) | LOW | +3 passing |
| **2: Infra** | 25 min | 3 (WAD YAMLs, UID, FUSE) | 4 (2 code, 1 config, 1 web) | MEDIUM | +40 passing |
| **3: Context** | 20 min | 2 (ContextBuilder, soul) | 4 (3 code, 1 spec) | HIGH | +22 passing |
| **4: Audit** | 15 min | 3 docs | 4 (3 code, 1 web) | LOW | 0 |
| **5: Verify** | 10 min | Full suite + handoff | 0 | LOW | — |
| **Total** | **~90 min** | **11 tasks + 3 docs** | **16 scouts** | — | **+~65 passing** |

---

## §11 — Escalation & Support

| Issue | Contact | Channel | Response Time |
|-------|---------|---------|---------------|
| Architecture/Firewall questions | Antigravity Opus 4.6 | OpenCode Architect mode | Next session |
| MCP/infrastructure issues | Cline (The Artisan) | VSCodium Cline session | ~30 min |
| Research/knowledge gaps | Researcher mode (Gemma) | OpenCode Researcher mode | Immediate |
| Strategic decisions | User (Arcana-NovAi) | Direct chat | User discretion |
| Build/test failures | Self-service | `make test` + `make doctor` | Immediate |

---

## §12 — Recovery: If You Get Compacted Mid-Phase

If you lose context mid-session:

```bash
# 1. Read the phase document
cat data/handoff/handoff_cline_to_opencode_builder_gemma.md | head -100

# 2. Read current status tracker
cat docs/operations/STATUS_CLINE.md

# 3. Check which work items are done
sqlite3 data/workbench/workbench.db "SELECT id, title, status FROM work_items WHERE workstream='hardening' ORDER BY id;"

# 4. Check phase status docs
ls -la docs/hardening/

# 5. Resume from the last incomplete phase
# The complete delegation document is at:
cat data/handoff/handoff_cline_to_opencode_builder_gemma.md | grep -n "## §" | tail -10
```

---

*End of delegation. Cline (PROMETHEUS) → OpenCode Builder (Gemma-4-31B).*
*~330 lines. 5 phases. 16 squadrons. One mission: PR-ready engine.*
*Next: Antigravity Opus 4.6 strategic review and Phase 2 roadmap.*