# 🔱 Omega Engine — Phase 1a Build Brief
# Overseer → Gemma 4 31B (Builder Mode)

**AP Token**: `AP-BUILDER-BRIEF-PHASE1A-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_builder_handoff ⬡ PHASE-1A
**Recommended Model**: `gemma-4-31b-it` (Google AI Studio — unlimited usage, 262K context)
**Recommended Mode**: `builder` (`.opencode/agents/builder.md`)
**Vision**: NOT required for these tasks (all file-based code changes)
**Estimated Total**: ~250-350 lines changed across 15+ files

---

## §0 How to Use This Brief

### Your Strengths I'm Exploiting

| Strength | Why I'm Pushing You | How to Use It |
|----------|--------------------|---------------|
| **262K context window** | Every task references multiple files simultaneously | Read all files listed in a task at once — don't bounce. You can hold the entire source tree in one window. |
| **Unlimited usage** | No quota management needed | `make test` after EVERY task. If a test fails, fix it immediately in the same session. No deferring. |
| **Instruction-following precision** | These tasks need exact string matches | Read the oldString/newString in each task carefully. Copy line content EXACTLY — whitespace matters. |
| **Vision** | Not needed here, but available | If you hit a bug you can't parse, use `jina_capture_screenshot_url()` on console output and analyze visually. |
| **Reasoning for size** | You punch above your weight on refactoring | The hardest tasks here are the EntityRegistry Iris normalization (Task 2) and oracle.py hardcoded string removals (Task 6). These need architectural thinking — use your reasoning tokens. |

### Your Operating Rules

1. **Read the file before editing** — Every `edit()` call must be preceded by a `read()` of the target file. I read first for you in the brief, but you MUST confirm before editing.
2. **`make test` after every task** — Run `make test` after each commit-worthy change. If tests break, fix before moving on.
3. **`make lint` before final signoff** — One pass at the end only (style-only, defer until all tasks done).
4. **Commit after every P0 task** — `git add -A && git commit -m "Phase 1a: <task description>"`. This creates a checkpoint trail.
5. **Ask about ANY ambiguity** — If a file path is wrong, a line number is off, or a fix seems wrong, stop and ask. Do NOT guess.
6. **You are the Builder, not the Overseer** — Do not redesign architecture. Do not invent new entity names. Do not change test patterns without explicit instruction. Execute the spec.

### Context References (Read These First)

```bash
# All documents are on disk — read them as needed:
ls docs/strategy/OMEGA_IWAD_ARCHITECTURE.md    # Canonical IWAD reference
ls docs/decisions/PIVOT_LOG.md                  # Decision 55 (27 lines from EOF)
```

---

## §1 Priority Queue

> **Execution Strategy**: Run **Tasks 1-5 first** (P0 critical bugs + content creation, fast wins), then **Tasks 6-13** (P1 firewall violations, medium complexity), then **Tasks 14-15** (P2 test updates), then **Tasks W1-W4 in parallel** (web research — these are independent of code changes and can be dispatched after the code tasks), then **Task 16** (final verification).

| Priority | # | Task | Files | Est. | Depends On |
|----------|---|------|-------|------|------------|
| **P0** | 1 | Fix `_load_entities()` soul.yaml filter | `wad_loader.py` | 2 min | — |
| **P0** | 2 | Normalize Iris entity loading in EntityRegistry | `entity_registry.py` | 30 min | — |
| **P0** | 3 | Add `get_all()` method to EntityRegistry | `entity_registry.py` | 2 min | — |
| **P0** | 4 | Remove `duplicate` entity artifact | `config/entities.yaml` | 1 min | — |
| **P0** | 5 | Rename Reference IWAD to Tech Roles (Option A) | `manifest.yaml`, 10 entity files | 45 min | — |
| **P1** | 6 | Replace hardcoded `"Iris"` strings in oracle.py | `oracle.py` | 20 min | Task 2 |
| **P1** | 7 | Fix hardcoded `"arch"` path violations | `oracle.py`, `loop.py` | 10 min | — |
| **P1** | 8 | Fix hardcoded `"sophia"` fallback in soul_updater | `soul_updater.py` | 5 min | — |
| **P1** | 9 | Fix hardcoded `"jem"` path in soul_update_manager | `soul_update_manager.py` | 5 min | — |
| **P1** | 10 | Fix hardcoded `"kali"` special case in hierarchy | `hierarchy.py` | 5 min | — |
| **P1** | 11 | Fix hardcoded entity names in iris/matcher.py | `matcher.py` | 5 min | — |
| **P1** | 12 | Fix hardcoded model names in oracle.py | `oracle.py` | 5 min | — |
| **P1** | 13 | Split hierarchy.yaml: central + per-IWAD | `hierarchy.yaml`, `wad_loader.py` | 45 min | Task 5 |
| **P2** | 14 | Add WAD Loader tests (7 new) | `test_wad_loader.py` | 30 min | Task 1,5 |
| **P2** | 15 | Update test hardcoded entity name references | 5+ test files | 20 min | Tasks 6-12 |
| **Web** | W1 | Doom WAD system deep research | `docs/research/R_DOOM_WAD_DEEP_RESEARCH.md` | 30 min | — |
| **Web** | W2 | Plugin/extension architecture patterns | `docs/research/R_PLUGIN_ARCHITECTURE_PATTERNS.md` | 30 min | — |
| **Web** | W3 | AI engine stack separation patterns | `docs/research/R_AI_ENGINE_STACK_SEPARATION.md` | 30 min | — |
| **Web** | W4 | Container distribution model research | `docs/research/R_CONTAINER_DISTRIBUTION_MODELS.md` | 30 min | — |
| **Final** | 16 | `make lint` + `make test` + git commit | — | 10 min | All above |

> **Web Research Parallelization**: Tasks W1-W4 are 100% independent of each other and of all code changes. You can run all 4 web research tasks in parallel using `task()` subagents — dispatch 4 subagents simultaneously, each handling one domain. Then synthesize the results in a single pass. This is the fastest path: ~30-40 minutes total wall-clock time for all 4 research documents.
>
> **DO NOT SKIP ORDER on code tasks.** Task 2 (Iris normalization) is the hardest — do it right and the rest is cleanup.

---

## §2 Detailed Tasks

---

### TASK 1: Fix `_load_entities()` Filename Filter (P0 — 2 minutes)

**File**: `src/omega/oracle/wad_loader.py`
**Lines**: 113-114
**Bug**: The method scans `**/*.yaml` but then filters to ONLY files named `soul.yaml`. Current entity files are flat `*.yaml` (e.g., `guardian.yaml`). This means WADLoader loads ZERO entities.

**Current code** (lines 111-125):
```python
async def _load_entities(self, entities_dir: Path) -> None:
    yaml_files = await anyio.to_thread.run_sync(
        lambda: list(entities_dir.glob("**/*.yaml"))
    )
    for path in yaml_files:
        if path.name == "soul.yaml":   # <-- BUG: this rejects all flat *.yaml files
            ...
```

**Fix**: Change the filter to accept ALL `*.yaml` files. Derive entity name from the filename stem (strip `.yaml`). If you want to support BOTH flat files AND nested `entities/<name>/soul.yaml`, check `path.name == "soul.yaml"` OR `path.suffix == ".yaml"` for flat files. Cleanest approach:

```python
# Accept any .yaml file. Extract name from parent dir (if soul.yaml) or filename stem.
if path.name == "soul.yaml":
    entity_name = path.parent.name
elif path.suffix == ".yaml":
    entity_name = path.stem  # e.g., "guardian.yaml" → "guardian"
else:
    continue
```

**Verification**:
- `make test` — all existing WAD tests must still pass
- Manual: `PYTHONPATH=src python3 -c "from omega.oracle.wad_loader import WADLoader; print('OK')"` must succeed

**Commit message**: `Phase 1a: Fix _load_entities() soul.yaml filter — now accepts flat .yaml files`

---

### TASK 2: Normalize Iris Entity Loading in EntityRegistry (P0 — 30 minutes)

**File**: `src/omega/oracle/entity_registry.py`
**Lines**: 270 total
**Scope**: Remove ALL 6 special-case paths for Iris. Iris must be treated as a regular entity.

#### Read this file in full first. It's 270 lines. Your 262K context can handle it.

**The 6 special-case paths** and how to fix each:

**Path #1 — Lines 117-130: Separate load path for Iris**
```python
# CURRENT — Iris loaded from top-level "iris" key
iris_raw = data.get("iris")
if iris_raw:
    iris_entity = Entity(name="Iris", ...)
    self._entities["iris"] = iris_entity

# FIX — Remove this entire block. Iris loads from the entities: dict like everyone else.
```

**Path #2 — Lines 140-142: Iris reordered in entity list**
```python
# CURRENT — Iris filtered out then appended at end
entities = [e for k, e in self._entities.items() if k != "iris"]
if "iris" in self._entities:
    entities.append(self._entities["iris"])

# FIX — Replace with: entities = list(self._entities.values())
```

**Path #3 — Line 162: Iris excluded from workspace scaffolding**
```python
# CURRENT
if entity.name.lower() != "iris":

# FIX — Remove this condition. Iris gets workspace scaffolding like everyone else.
# OR: if iris_entity has container=True, it naturally shouldn't need a workspace.
# Check if the condition is: container entities don't get workspaces.
# If so, change to: if not entity.container:
```

**Path #4 — Line 219: Iris skipped in entity loop during save**
```python
# CURRENT
if key == "iris":
    continue

# FIX — Simply remove this if-block. Iris's data will be in the entities dict.
```

**Path #5 — Lines 223-224: Iris written to separate top-level key**
```python
# CURRENT
if "iris" in self._entities:
    data["iris"] = iris_dict

# FIX — Remove this block. Iris will be in the entities dict, serialized as a regular entity.
```

**Path #6 — Line 117: Top-level `data.get("iris")`**
Same as Path #1. Combined fix.

#### The Unified Fix:

After removal, `config/entities.yaml` must have Iris UNDER the `entities:` key, not at the root. Check the current structure — Iris is currently a root-level key:

```yaml
# config/entities.yaml — CURRENT (bad)
iris:
  name: Iris
  model: qwen3-1.7b
  personality: ''
  role: Voice Interface
  container: true
  port: 8080

# Must become (good):
entities:
  iris:
    name: Iris
    model: qwen3-1.7b
    personality: ''
    role: Voice Interface
    container: true
    port: 8080
```

#### Wait — Critical: Check `config/entities.yaml` Structure First

Read the FIRST 15 lines of `config/entities.yaml`. If Iris is already under `entities:`, then only the code changes are needed. If Iris is a root-level key, then BOTH the YAML AND the code need changing.

**The Entity Dataclass** (lines 27-48) already supports `container: true` and `port:` — no changes needed there.

**Verification**:
- `make test` — all entity_registry tests pass
- Manual: `PYTHONPATH=src python3 -c "from omega.oracle.entity_registry import EntityRegistry; reg = EntityRegistry(); print('iris' in [e.lower() for e in reg.names()])"` → True
- Manual: `PYTHONPATH=src python3 -c "from omega.oracle.entity_registry import EntityRegistry; reg = EntityRegistry(); e = reg.get('iris'); print(e is not None and e.container)"` → True (must still be a container entity)

**Commit message**: `Phase 1a: Normalize Iris entity loading — remove 6 special-case paths in EntityRegistry`

---

### TASK 3: Add `get_all()` Method to EntityRegistry (P0 — 2 minutes)

**File**: `src/omega/oracle/entity_registry.py`

Add a `get_all()` method to the `EntityRegistry` class. Place it near the existing query methods (after `names()` or `count()`).

```python
def get_all(self) -> Dict[str, 'Entity']:
    """Return a copy of the entities dictionary for iteration."""
    return dict(self._entities)
```

This fixes the latent runtime bug in `soul_updater.py:182` where `registry.get_all()` is called but doesn't exist.

**Verification**:
- `make test` — passes
- Manual: `PYTHONPATH=src python3 -c "from omega.oracle.entity_registry import EntityRegistry; reg = EntityRegistry(); all_ents = reg.get_all(); print(len(all_ents))"` → correct count

**Commit**: Combine with Task 2. Both are entity_registry.py changes.

---

### TASK 4: Remove `duplicate` Entity Artifact (P0 — 1 minute)

**File**: `config/entities.yaml`
**Lines**: 513-517
**Bug**: A test artifact entity named "duplicate" with `model: m`, `personality: p`. Minimal fields, no domains.

**Fix**:
```yaml
# Remove these 5 lines:
  duplicate:
    name: Duplicate
    model: m
    personality: p
    container: false
```

Also check `tests/test_wad_loader.py` line 103 for `Duplicate` entity pre-registration — the test creates its OWN `Duplicate` entity programmatically, so the test does NOT depend on the config file. Removing the YAML key is safe.

**Verification**:
- `make test` — all WAD loader tests pass (the test creates its own Duplicate entity)
- `grep "duplicate" config/entities.yaml` → 0 matches after removal

**Commit**: Combine with Tasks 2+3 (config + entity_registry in one commit).

---

### TASK 5: Rename Reference IWAD to Tech Roles (Option A) (P0 — 45 minutes)

**Decision**: The Reference IWAD uses **Tech Role names** per IWAD Architecture doc §5. The manifest.yaml currently lists generic fantasy names (Guardian, Dreamer, etc.). These must be renamed to:

| Pillar | Tech Role | File Name | Description |
|--------|-----------|-----------|-------------|
| P1 | SysAdmin | `sysadmin.yaml` | Infrastructure engineering — containers, networking, systemd |
| P2 | DataStore | `datastore.yaml` | Data pipeline — storage, search, knowledge graphs |
| P3 | BuildMaster | `buildmaster.yaml` | CI/CD — builds, releases, toolchains |
| P4 | Bridge | `bridge.yaml` | API/Protocol — MCP, inter-agent communication |
| P5 | Sentinel | `sentinel.yaml` | Security — boundaries, hardening, permission guards |
| P6 | ModelGate | `modelgate.yaml` | Inference — provider fabric, model orchestration |
| P7 | Context | `context.yaml` | Sessions — memory, context window, continuity |
| P8 | WatchTower | `watchtower.yaml` | Observability — logs, traces, health monitoring |
| P9 | Link | `link.yaml` | Sync — cross-agent coordination, handoff protocol |
| P10 | Verifier | `verifier.yaml` | QA — testing, validation, compliance |

#### Step 5a: Read `guardian.yaml`
Read the existing file at `config/wads/_omega_default/entities/guardian.yaml`. This is your template for all 10 entities.

#### Step 5b: Create 9 new entity files
Create each entity file following the `guardian.yaml` format but with the tech role name and appropriate domain/personality:

```yaml
# Example — sysadmin.yaml (P1)
entity:
  name: SysAdmin
  model: qwen3-1.7b-q6_k
  personality: >
    You are SysAdmin, Pillar 1 of the Omega Engine Reference IWAD.
    Your domain is infrastructure engineering — containers, networking,
    systemd services, storage, and deployment. You ensure the engine
    runs reliably on any hardware...
  domain: [infrastructure, containers, networking, systemd, deployment, storage]
  pillar: "P1: Infrastructure"
```

**IMPORTANT**: The `_load_entities()` fix (Task 1) expects `*.yaml` files named by their entity name in the entities directory. These are flat files, not subdirectories.

#### Step 5c: Update `manifest.yaml`
Rewrite `config/wads/_omega_default/manifest.yaml` to match the tech role names:

```yaml
wad:
  name: "Omega Engine Reference IWAD"
  version: "0.2.0"
  requires_engine: ">=0.4.0"
  author: "Xoe-NovAi Foundation"
  description: "Reference IWAD — a development team of 10 tech specialists."
  type: iwad
  mode: development
  license: "Apache 2.0"
  startup:
    message: "Reference IWAD loaded. Your development team is online."
    theme: "terminal"
  entities:
    - "sysadmin.yaml"      # P1 — Infrastructure
    - "datastore.yaml"     # P2 — Data Pipeline
    - "buildmaster.yaml"   # P3 — CI/CD
    - "bridge.yaml"        # P4 — API/Protocol
    - "sentinel.yaml"      # P5 — Security
    - "modelgate.yaml"     # P6 — Inference
    - "context.yaml"       # P7 — Sessions
    - "watchtower.yaml"    # P8 — Observability
    - "link.yaml"          # P9 — Cross-Agent
    - "verifier.yaml"      # P10 — QA/Testing
  voices:
    primary: "jem.yaml"
  dependencies: []
```

#### Step 5d: Archive old `guardian.yaml`
Rename `guardian.yaml` → `sysadmin.yaml` (since Guardian becomes SysAdmin). Or if they're completely different entities, keep guardian.yaml as an archive file.

**Verification**:
```bash
ls config/wads/_omega_default/entities/  # Should show 10 *.yaml files
cat config/wads/_omega_default/manifest.yaml | grep -c "\.yaml"  # Should match 10
```

**Commit message**: `Phase 1a: Rename Reference IWAD entities to Tech Roles (Option A) — 10 pillar files + manifest`

---

### TASK 6: Replace Hardcoded `"Iris"` Strings in oracle.py (P1 — 20 minutes)

**File**: `src/omega/oracle/oracle.py`
**Lines**: 413, 417, 432, 442, 447

**Dependency**: Task 2 (Iris normalization) must be done FIRST — the oracle.py changes assume Iris is a normal entity accessible via `self.iris_entity`.

**Pattern**: Replace every hardcoded `"Iris"` string with a dynamic lookup.

#### Line 413 — Session manager
```python
# CURRENT
session_id = await self.session_manager.get_session_id("Iris")
# FIX
session_id = await self.session_manager.get_session_id(self.iris_entity.name)
```

#### Line 417 — System prompt
```python
# CURRENT
system_prompt = await self._prepare_system_prompt("Iris", session_id, ...)
# FIX
system_prompt = await self._prepare_system_prompt(self.iris_entity.name, session_id, ...)
```

#### Line 432 — OracleResponse entity
```python
# CURRENT
entity="Iris",
# FIX
entity=self.iris_entity.name,
```

#### Line 442 — Trace log entity
```python
# CURRENT
trace.log("response.delivered", entity="Iris", ...)
# FIX
trace.log("response.delivered", entity=self.iris_entity.name, ...)
```

#### Line 447 — Trace record entity
```python
# CURRENT
entity="Iris",
# FIX
entity=self.iris_entity.name,
```

**IMPORTANT**: Before making changes, read the FULL context around each line. The actual variable names and indentation may differ slightly from this brief. Verify the exact line content against what's on disk.

**Verification**:
- `grep -n '"Iris"' src/omega/oracle/oracle.py` → 0 matches after fix (check case sensitivity)
- `make test` — all oracle tests pass

**Commit message**: `Phase 1a: Replace hardcoded "Iris" strings in oracle.py with dynamic entity lookup`

---

### TASK 7: Fix Hardcoded `"arch"` Path Violations (P1 — 10 minutes)

**File A**: `src/omega/oracle/oracle.py`, line 47
**File B**: `src/omega/workers/background_researcher/loop.py`, line 377
**File C**: `src/omega/oracle/oracle.py`, line 183 (fallback)

#### Fix A — Line 47: DEFAULT_SOUL_PATH hardcodes `"arch"`
```python
# CURRENT
DEFAULT_SOUL_PATH = DATA_DIR / "entities" / "arch" / "soul.yaml"
# FIX
# Make it config-driven. The bootstrap method (line 182-184) already reads 
# config.get("omega", {}).get("entity", {}).get("user", "arch"). 
# Change DEFAULT_SOUL_PATH to accept a parameter or read from config.
```

**Suggested approach**: Convert `DEFAULT_SOUL_PATH` from a module-level constant to a method:
```python
@staticmethod
def _default_soul_path(user_name: str = "arch") -> Path:
    return DATA_DIR / "entities" / user_name / "soul.yaml"
```

Then update line 182 to: `soul_path = self._default_soul_path(user_name)`

#### Fix B — Line 377: Hardcoded "arch" exclusion
```python
# CURRENT
if entity_dir.is_dir() and entity_dir.name != "arch":
# FIX
if entity_dir.is_dir() and entity_dir.name != "arch":
```
**Note**: Change the hardcoded `"arch"` to read from config. The challenge here is that `loop.py` may not have access to `config/omega.yaml`. If not, use `"arch"` as a default fallback but document that it should be config-driven:

```python
import yaml
_OMEGA_CONFIG_PATH = Path("config/omega.yaml")
_USER_ENTITY = "arch"
try:
    with open(_OMEGA_CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
        _USER_ENTITY = cfg.get("omega", {}).get("entity", {}).get("user", "arch")
except Exception:
    pass
# Then: if entity_dir.is_dir() and entity_dir.name != _USER_ENTITY:
```

Or, simpler: pass `user_entity` as a parameter to the relevant method.

#### Fix C — Line 183: Fallback `"arch"` in config lookup
```python
# CURRENT
user_name = self.config.get("omega", {}).get("entity", {}).get("user", "arch")
# FIX
# This is ALREADY config-driven. The "arch" fallback is acceptable.
# BUT: the fallback should be None or "default", not a specific user name.
# Change to: ...get("user", None)
# And when None, print a warning and skip soul operations gracefully.
```

**Verification**:
- `make test` — all oracle.py and loop.py tests pass
- Manual: verify `omega talk "hello"` creates correct soul path

**Commit message**: `Phase 1a: Fix hardcoded "arch" path violations in oracle.py and loop.py`

---

### TASK 8: Fix Hardcoded `"sophia"` Fallback in soul_updater (P1 — 5 minutes)

**File**: `src/omega/workers/background_researcher/soul_updater.py`
**Line**: 192

```python
# CURRENT
best_match = "sophia"
# FIX
# This is the fallback when no domain match is found. Use the engine's default entity
# from config instead of hardcoding "sophia":
from omega.oracle.entity_registry import EntityRegistry
_registry = EntityRegistry()
default_entity = _registry.get("default")
best_match = default_entity.name if default_entity else "sophia"
```

**Verification**:
- `make test` — soul_updater tests pass
- The config `entities.yaml` has a `default:` entity with `name: default`

**Commit message**: `Phase 1a: Fix hardcoded "sophia" fallback in soul_updater.py`

---

### TASK 9: Fix Hardcoded `"jem"` Path in soul_update_manager (P1 — 5 minutes)

**File**: `src/omega/workers/background_researcher/soul_update_manager.py`
**Line**: 12

```python
# CURRENT
self.base_soul_dir = ... / "data" / "entities" / "jem" / "souls"
# FIX
# Read the IWAD-aware entity directory from config. Or use a config-driven approach:
_ENTITY_DIR = Path("data/entities")
# In context of the active IWAD, the soul dir should be derived.
# Simplest fix: accept entity_name as a constructor parameter.
```

**Actual fix**: Change the hardcoded path to accept a parameter:
```python
def __init__(self, base_dir: Path, entity_name: str = "jem"):
    self.base_soul_dir = base_dir / "data" / "entities" / entity_name / "souls"
```

**Verification**:
- `make test` — soul_update_manager tests pass
- Check callers to ensure they pass `entity_name="jem"` (backward compatibility)

**Commit message**: `Phase 1a: Fix hardcoded "jem" path in soul_update_manager.py`

---

### TASK 10: Fix Hardcoded `"kali"` Special Case in hierarchy.py (P1 — 5 minutes)

**File**: `src/omega/oracle/hierarchy.py`
**Lines**: 59-60

```python
# CURRENT
elif name == "kali" and "kali_unification" in hierarchy_data:
    lookup_name = "kali_unification"
# FIX
# Remove the hardcoded "kali" check. Instead, look up the name in hierarchy_data
# and find its governance entry dynamically. If not found as a direct key, 
# search the keepers list for a matching keeper name.
```

**Suggested fix**:
```python
# Replace the hardcoded elif with a dynamic lookup:
if name in hierarchy_data:
    lookup_name = name
elif f"{name.lower()}_unification" in hierarchy_data:
    lookup_name = f"{name.lower()}_unification"
else:
    # Search keepers for a matching keeper
    keepers = hierarchy_data.get("keepers", {})
    for pillar, keeper_info in keepers.items():
        if isinstance(keeper_info, dict) and keeper_info.get("keeper", "").lower() == name.lower():
            lookup_name = keeper_info["keeper"]
            break
    else:
        # Fall back to a default oversoul
        lookup_name = self._find_oversoul_for_entity(name, hierarchy_data)
```

**Verification**:
- `make test` — all hierarchy tests pass
- Manual: `PYTHONPATH=src python3 -c "from omega.oracle.hierarchy import SovereignHierarchy; h = SovereignHierarchy(); print(h.get_rank('kali'))"` → same result as before

**Commit message**: `Phase 1a: Fix hardcoded "kali" special case in hierarchy.py — dynamic lookup`

---

### TASK 11: Fix Hardcoded Entity Names in iris/matcher.py (P1 — 5 minutes)

**File**: `src/omega/iris/matcher.py`
**Lines**: 79-83

```python
# CURRENT
return (
    "I can help you connect with the 10 Pillar Keepers. Try:\n"
    "  'summon Sekhmet' — for grounding and strength\n"
    "  'ask Hecate about crossroads' — for wisdom at thresholds\n"
    "  '@Lilith show my shadow' — for shadow work\n"
)
# FIX
# Replace with a generic, IWAD-agnostic help message:
return (
    "I can help you connect with the active IWAD's pillars. Try:\n"
    "  'summon <entity name>' — to invoke a specific keeper\n"
    "  'list entities' — to see who's available\n"
    "  'help' — for more commands\n"
)
```

**Verification**:
- `make test` — iris tests pass
- Manual: `omega talk "help"` — no arcana_novai-specific names in response

**Commit message**: `Phase 1a: Fix hardcoded entity names in iris/matcher.py help text`

---

### TASK 12: Fix Hardcoded Model Names in oracle.py (P1 — 5 minutes)

**File**: `src/omega/oracle/oracle.py`
**Lines**: ~421, 437, 448, 628 (model name strings)

```python
# Search for these patterns:
grep -n '"qwen3-1.7b"' src/omega/oracle/oracle.py
grep -n '"qwen3-4b-thinking-q4_k_m"' src/omega/oracle/oracle.py
```

**Fix**: Replace hardcoded model name strings with `self.config["models"]` lookup or entity-level model retrieval. The entity registry already has model assignments — use those instead of hardcoding model names in the Oracle.

For each occurrence:
```python
# CURRENT
model_name = "qwen3-1.7b"
# FIX
model_name = self.config.get("models", {}).get("default", "qwen3-1.7b")
```

**Verification**:
- `make test` — all oracle tests pass
- `grep -n '"qwen3-1.7b"' src/omega/oracle/oracle.py` → 0 matches after fix

**Commit message**: `Phase 1a: Replace hardcoded model names in oracle.py with config-driven lookup`

---

### TASK 13: Split hierarchy.yaml: Central + Per-IWAD (P1 — 45 minutes)

**Reference**: L4 subagent report §D (Hierarchy Migration Plan)

**Background**: The current `config/hierarchy.yaml` mixes **structural governance** (Ma'at governs light, Lilith governs dark) with **content-specific entity names** (sekhmet, brigid, etc.). The structure must be split.

#### Step 13a: Create Central Foundation Hierarchy
Read `config/hierarchy.yaml` fully. Create a new version that contains ONLY the oversoul structure:

```yaml
# config/hierarchy.yaml — NEW: central foundation only
hierarchy:
  sophia:
    name: Sophia
    role: "Containing field — observability, memory, knowledge"
    contains: [kali_unification, maat_oversoul, lilith_oversoul]

  kali_unification:
    name: Kali
    role: "Grand Oversoul — MaKaLi trine synthesis"
    governs: [maat_oversoul, lilith_oversoul]

  maat_oversoul:
    name: Ma'at
    role: "Light Oversoul — governs manifestation pillars (P1-P5)"
    reports_to: kali_unification

  lilith_oversoul:
    name: Lilith
    role: "Dark Oversoul — governs sovereign pillars (P6-P10)"
    reports_to: kali_unification

  isis_oversoul:
    name: Isis
    role: "Healer within the Light"
    reports_to: kali_unification

  roc_racoon:
    keeper: roc_racoon
    pillar: "P0: Archivist"
    reports_to: kali_unification
```

**Remove from central**: The `governs_keepers` lists, the `keepers` block, and any arcana_novai-specific entity names.

#### Step 13b: Create Reference IWAD Hierarchy
Create `config/wads/_omega_default/hierarchy.yaml`:

```yaml
# config/wads/_omega_default/hierarchy.yaml
hierarchy:
  maat_oversoul:
    governs_keepers: [sysadmin, datastore, buildmaster, bridge, sentinel]

  lilith_oversoul:
    governs_keepers: [modelgate, context, watchtower, link, verifier]

  keepers:
    P1: { keeper: sysadmin, oversoul: maat_oversoul }
    P2: { keeper: datastore, oversoul: maat_oversoul }
    P3: { keeper: buildmaster, oversoul: maat_oversoul }
    P4: { keeper: bridge, oversoul: maat_oversoul }
    P5: { keeper: sentinel, oversoul: maat_oversoul }
    P6: { keeper: modelgate, oversoul: lilith_oversoul }
    P7: { keeper: context, oversoul: lilith_oversoul }
    P8: { keeper: watchtower, oversoul: lilith_oversoul }
    P9: { keeper: link, oversoul: lilith_oversoul }
    P10: { keeper: verifier, oversoul: lilith_oversoul }
```

#### Step 13c: WAD Loader Integration
Add hierarchy loading to `wad_loader.py`. After loading entities and voices from a WAD, also check for `hierarchy.yaml` in the WAD directory and merge it:

```python
# In load_wad(), after _load_entities() and _load_voices():
hierarchy_path = wad_dir / "hierarchy.yaml"
if hierarchy_path.exists():
    await self._load_hierarchy(hierarchy_path)

async def _load_hierarchy(self, hierarchy_path: Path) -> None:
    """Load and merge a per-IWAD hierarchy file."""
    # Read hierarchy.yaml
    # Merge its keeper mappings into the central hierarchy
    # Handle override conflicts (WAD hierarchy wins for its pillar mappings)
```

**Verification**:
- `make test` — all hierarchy tests pass
- `python3 -c "from omega.oracle.hierarchy import SovereignHierarchy; h = SovereignHierarchy(); print(h.get_rank('sysadmin'))"` → works (after WAD loaded)
- `python3 -c "from omega.oracle.hierarchy import SovereignHierarchy; h = SovereignHierarchy(); print(h.get_rank('sekhmet'))"` → still works if arcana_novai WAD loaded

**Commit message**: `Phase 1a: Split hierarchy.yaml into central foundation + per-IWAD hierarchy files`

---

### TASK 14: Add WAD Loader Tests (P2 — 30 minutes)

**File**: `tests/test_wad_loader.py`
**Current**: 6 tests (121 lines)
**Need**: +7 new tests

Add these tests to the existing file:

1. `test_load_entity_from_wad` — Create temp WAD with one entity file, verify entity is registered with correct fields
2. `test_load_voices_from_wad` — Create temp WAD with one voice file, verify voice entity created
3. `test_load_all_wads_mixed_results` — Create 3 WADs (1 valid, 1 missing manifest, 1 empty), verify success dict has mixed results
4. `test_wad_namespace_isolation` — Create 2 WADs with same-named entity, verify source tracking
5. `test_wad_no_entities_dir` — WAD with no `entities/` directory, verify graceful handling
6. `test_wad_startup_message` — WAD with `startup.message` in manifest, verify it's accessible
7. `test_wad_hierarchy_merge` — Create WAD with `hierarchy.yaml`, verify keeper mappings merge correctly

Use the existing `wad_env` fixture pattern. Add a `conftest.py`-level fixture if needed for new temp directories.

**IMPORTANT**: Do NOT change the test's `entities_dir` structure to use nested `soul.yaml`. The test should use flat `*.yaml` files matching the Task 1 fix.

**Verification**:
- `make test` — all 13 WAD tests pass
- `pytest tests/test_wad_loader.py -v` — all 13 named tests pass

**Commit message**: `Phase 1a: Add 7 new WAD Loader tests — entity loading, voices, multi-WAD, namespace, hierarchy`

---

### TASK 15: Update Test Hardcoded Entity Name References (P2 — 20 minutes)

**Scope**: 5+ test files with 39+ hardcoded entity name references.

**Files** (from L1 report):
- `tests/test_session_manager.py` — "sophia" → dynamic entity lookup
- `tests/test_memory_store.py` — "sophia" → dynamic entity lookup  
- `tests/test_sovereign_loop.py` — "sophia" → dynamic entity lookup
- `tests/test_hierarchy.py` — "sekhmet", "brigid" etc. → use IWAD-aware hierarchy
- `tests/test_iris.py` — "lilith" → dynamic entity lookup

**General approach**: For each test that hardcodes a specific entity name:
1. If the test is testing a general mechanism (not an entity-specific feature), use a test-scoped entity or the `default` entity
2. If the test is testing hierarchy behavior, use `hierarchy_data` fixture values
3. If the test is testing session management, use `default` entity
4. Create a `_test_entity_name` fixture or constant if multiple tests use the same name

**Example fix** (`tests/test_session_manager.py`):
```python
# CURRENT
session_id = await session_manager.get_session_id("sophia")
# FIX
session_id = await session_manager.get_session_id("default")
```

**Example fix** (`tests/test_hierarchy.py`):
```python
# CURRENT
rank = await hierarchy.get_rank("sekhmet")
# FIX  
# Use the default hierarchy names or IWAD-aware names:
rank = await hierarchy.get_rank("sysadmin")  # Reference IWAD name
```

**Verification**:
- `make test` — ALL 251 tests pass
- No regressions: `pytest tests/ -v --tb=short`

**Commit message**: `Phase 1a: Update test hardcoded entity names for IWAD awareness`

---

### TASK W1: Doom WAD System Deep Research (Web — 30 minutes)

**Why Gemma**: This is a **deep web research task** requiring multi-source extraction, comparison, and synthesis. Your unlimited usage means no API quotas to manage. Your 262K context means you can download and read entire wiki pages, GitHub discussions, and source port documentation in a single session. Use Firecrawl for bulk extraction.

**Mission**: Validate the IWAD architecture against id Software's ACTUAL implementation to identify blind spots and learn from 30 years of WAD ecosystem evolution.

**Tools Available**: `websearch`, `webfetch`, `skill firecrawl-search`, `skill firecrawl-scrape`, `skill firecrawl-map`, `skill firecrawl-crawl`

**Research Questions** (answer all in a single synthesized research document):

| # | Question | Why It Matters |
|---|----------|----------------|
| 1 | How did vanilla Doom handle WAD namespace collisions? (Two WADs define same sprite/lump) | Our EntityRegistry currently skips duplicates silently. Should we warn? Error? Override by priority? |
| 2 | How did DEHACKED/BEX layer modifications on top of vanilla WADs? | PWADs need to modify IWAD behavior. DEHACKED is the canonical precedent. |
| 3 | How did source ports (ZDoom, GZDoom, Eternity Engine) handle multi-WAD loading with priority? | Our `load_all_wads()` uses filesystem order. Source ports have advanced priority systems. |
| 4 | What was id Software's actual "IWAD vs PWAD" distinction — enforced or convention? | Verifies our IWAD/PWAD distinction is historically accurate |
| 5 | Did Doom have a concept of "dependency resolution" between WADs? | Our `dependencies: []` field exists but is unused. Should it be? |
| 6 | How did the community handle WAD distribution, versioning, and compatibility? | Informs our future XOE distribution model (Phase 4) |

**Research Sources** (find and crawl these):
- doomwiki.org — WAD, IWAD, PWAD, DEHACKED, BEX articles
- ZDoom/GZDoom wiki — Command-line WAD loading, priority ordering
- GitHub: `coelckers/gzdoom` — Source code for WAD loading
- Eternity Engine docs — Multi-WAD merge logic
- Any archived id Software developer commentary on the WAD system

**Output Format** — Write to `docs/research/R_DOOM_WAD_DEEP_RESEARCH.md`:
```markdown
# R-DOOM-WAD: Doom WAD System Deep Research
**Date**: 2026-05-25
**Researcher**: Gemma 4 31B

## Executive Summary
[3-4 sentences on key findings relevant to Omega Engine]

## Question 1: Namespace Collisions
Finding: ...
Source: [URL]
Omega Engine Implication: ...

## Question 2: DEHACKED/BEX Layering
...

## Consolidated Recommendations for IWAD Architecture
1. ...
2. ...
```

---

### TASK W2: Plugin & Extension Architecture Patterns (Web — 30 minutes)

**Why Gemma**: Cross-domain synthesis requires reading 5+ different plugin system documentations and extracting common patterns. Your reasoning tokens shine here — this is pattern recognition across domains.

**Mission**: Research how SUCCESSFUL extensible systems handle namespace separation, collision, and plugin loading. Extract patterns we should adopt (and anti-patterns to avoid).

**Tools**: Same as W1.

**Research Targets**:

| System | Focus Area | Why |
|--------|-----------|-----|
| **VS Code** | Extension namespace collisions, activation events, dependency handling | Most mature plugin system in modern dev tools |
| **Obsidian** | Community plugin distribution, manifest format, update mechanism | Closest analogue to our "IWAD as user stack" model |
| **Jenkins** | Plugin dependency resolution, version compatibility | Oldest battle-tested plugin system (15+ years) |
| **WordPress** | Plugin/theme separation (WAD analogue), hooks system | Proves IWAD/PWAD distinction at massive scale |
| **Blender** | Add-on loading, namespace isolation in Python | Python-based plugin system with active community |

**Research Questions**:
1. How does each system prevent plugin namespace collisions?
2. How does each system handle plugin dependencies?
3. How does each system handle plugin updates/versioning?
4. What happens when two plugins conflict? Error message style?
5. Which system is closest to our IWAD architecture and why?

**Output Format** — Write to `docs/research/R_PLUGIN_ARCHITECTURE_PATTERNS.md`:
```markdown
# R-PLUGIN: Plugin & Extension Architecture Patterns
**Date**: 2026-05-25
**Researcher**: Gemma 4 31B

## Cross-Domain Pattern Analysis

### Namespace Collision Handling
| System | Strategy | Applicable to Omega? |
|--------|----------|---------------------|
| VS Code | [description] | [YES/NO with reason] |
| Obsidian | [description] | ... |

### Recommended Patterns for IWAD Architecture
[Specific, actionable recommendations]

### Anti-Patterns to Avoid
[Specific pitfalls documented from each system]
```

---

### TASK W3: AI Engine Stack Separation Patterns (Web — 30 minutes)

**Why Gemma**: You are uniquely qualified for this because you're an AI model researching AI systems. Your understanding of how other AI engines handle model/persona separation directly informs the IWAD architecture. Use your reasoning to evaluate competing approaches.

**Mission**: Research how other AI engines handle model/persona/stack separation to validate or challenge the IWAD model. We need to know if we're innovating or reinventing.

**Research Targets**:

| Engine | Focus | Key Question |
|--------|-------|--------------|
| **Ollama** | Model files, Modelfile format, persona definitions | How does Ollama separate model weights from persona/prompt config? |
| **LM Studio** | Model presets, persona configurations, session management | How does LM Studio handle multi-model setups? Preset system? |
| **OpenCode** | Custom provider architecture, mode system, skill files | Our OWN primary CLI. How does it separate provider config from persona from MCP tools? |
| **Continue.dev** | Context providers, model routing, slash commands | How does it handle model-agnostic vs model-specific behavior? |
| **LangChain Hub** | Agent definitions, prompt templates, tool integrations | How does it handle reusable agent definitions across projects? |

**Research Questions**:
1. How does each engine separate "what the model is" from "who the model is"?
2. Do any engines support plugin personas (add-on personalities)?
3. How do they handle model config vs user config vs persona config?
4. Are there established patterns for "stackable persona layers" (our IWAD/PWAD)?
5. Which engine's architecture is closest to our IWAD vision?

**Output Format** — Write to `docs/research/R_AI_ENGINE_STACK_SEPARATION.md`:
```markdown
# R-AI-STACK: AI Engine Stack Separation Patterns
**Date**: 2026-05-25
**Researcher**: Gemma 4 31B

## Engine-by-Engine Analysis

### Ollama
Model/Persona separation: ...
Relevant to IWAD: ...
Sources: [URLs]

### [Engine 2]
...

## Comparative Table
| Feature | Ollama | LM Studio | OpenCode | Continue | LangChain |
|---------|--------|-----------|----------|----------|-----------|
| Persona separation | ... | ... | ... | ... | ... |
| Plugin system | ... | ... | ... | ... | ... |
| Closest to IWAD? | ... | ... | ... | ... | ... |

## Recommendations
[Validate or challenge each IWAD assumption based on evidence]
```

---

### TASK W4: Container Distribution Model Research (Web — 30 minutes)

**Why Gemma**: This feeds Phase 4 (Omegaverse) but needs research NOW so we don't design the IWAD system in a way that makes distribution impossible later. Your unlimited context can hold all 5 distribution models simultaneously for comparison.

**Mission**: Research how open-source projects handle community package distribution to inform the Omegaverse's IWAD distribution model.

**Research Targets**:

| System | Focus | Why for Omegaverse |
|--------|-------|-------------------|
| **npm** | Package name collisions, registry architecture, namespace (scoped packages) | Our IWAD naming system — should we use `@user/stackname` pattern? |
| **Docker Hub** | Image namespacing, tags, versioning, official vs community images | Our XOE container distribution model |
| **Flatpak/Flathub** | Sandboxed app distribution, runtime dependencies, update mechanism | Our "one install, local-first" deployment model |
| **Snap Store** | Automatic updates, confinement model, channel system | Our P2P update mechanism |
| **PyPI** | Package naming, dependency resolution, yanking/policy | Our community IWAD upload model |

**Research Questions**:
1. How does npm handle package name collisions? (scoped packages `@user/package`)
2. How does Docker Hub handle namespace/registry architecture? (Docker ID → repositories → tags)
3. What signing/verification models do these systems use?
4. What "lessons learned" from Docker Hub's security issues apply to IWAD distribution?
5. What license/legal model should community IWADs follow?
6. How does Flatpak handle multiple versions of the same app?

**Output Format** — Write to `docs/research/R_CONTAINER_DISTRIBUTION_MODELS.md`:
```markdown
# R-DISTRIBUTION: Container Distribution Model Research
**Date**: 2026-05-25
**Researcher**: Gemma 4 31B

## Distribution Model Comparison

### Registry Architecture
| System | Registry Type | Namespace Model | Our Takeaway |
|--------|--------------|-----------------|--------------|
| npm | [type] | [namespace] | [applicability] |
| Docker | [type] | [namespace] | ... |

### Security & Signing
[What we must implement before Phase 4]

### Recommended Omegaverse Distribution Architecture
[Concrete proposal based on research]
```

---

### TASK 16: Final Lint + Test + Commit (Final — 10 minutes)

```bash
make lint
# Fix any style issues (should be minimal since all changes are targeted)
make test  # Must be 251/251 passing
git add -A
git commit -m "Phase 1a: IWAD Foundation — entity normalization, hierarchy split, WAD fixes, tests"
```

---

## §3 Files Changed Summary

| File | Task(s) | Lines Changed | Risk |
|------|---------|---------------|------|
| `src/omega/oracle/wad_loader.py` | 1, 13 | +15/-3 | Low — isolated method fix |
| `src/omega/oracle/entity_registry.py` | 2, 3 | +10/-25 | HIGH — Iris normalization core |
| `config/entities.yaml` | 2, 4 | +0/-5 | Low — Iris key move + duplicate removal |
| `config/wads/_omega_default/manifest.yaml` | 5 | Full rewrite | Medium — new IWAD identity |
| `config/wads/_omega_default/entities/*.yaml` | 5 | 9 new + 1 updated | Medium — template-based |
| `config/wads/_omega_default/hierarchy.yaml` | 13 | New file | Medium — new IWAD content |
| `config/hierarchy.yaml` | 13 | Major rewrite | HIGH — central hierarchy split |
| `src/omega/oracle/oracle.py` | 6, 7, 12 | +15/-15 | HIGH — Iris string replacement |
| `src/omega/workers/background_researcher/loop.py` | 7 | +3/-1 | Low |
| `src/omega/workers/background_researcher/soul_updater.py` | 8 | +5/-1 | Low |
| `src/omega/workers/background_researcher/soul_update_manager.py` | 9 | +3/-1 | Low |
| `src/omega/oracle/hierarchy.py` | 10 | +15/-2 | Medium — dynamic Kali lookup |
| `src/omega/iris/matcher.py` | 11 | +3/-3 | Low — cosmetic text |
| `tests/test_wad_loader.py` | 14 | +80/-0 | Low — new tests |
| `tests/test_session_manager.py` | 15 | +5/-5 | Low |
| `tests/test_memory_store.py` | 15 | +3/-3 | Low |
| `tests/test_sovereign_loop.py` | 15 | +3/-3 | Low |
| `tests/test_hierarchy.py` | 15 | +10/-10 | Low |
| `tests/test_iris.py` | 15 | +1/-1 | Low |
| **Output:** `docs/research/R_DOOM_WAD_DEEP_RESEARCH.md` | W1 | New file | — |
| **Output:** `docs/research/R_PLUGIN_ARCHITECTURE_PATTERNS.md` | W2 | New file | — |
| **Output:** `docs/research/R_AI_ENGINE_STACK_SEPARATION.md` | W3 | New file | — |
| **Output:** `docs/research/R_CONTAINER_DISTRIBUTION_MODELS.md` | W4 | New file | — |

---

## §4 Verification Gates

| Gate | Command | Expected | Run After |
|------|---------|----------|-----------|
| **G1** | `make test` | 251/251 passing | Every commit |
| **G2** | `grep -rn '"Iris"' src/omega/oracle/oracle.py` | 0 matches | Task 6 |
| **G3** | `grep -rn 'duplicate' config/entities.yaml` | 0 matches | Task 4 |
| **G4** | `ls config/wads/_omega_default/entities/*.yaml \| wc -l` | 10 files | Task 5 |
| **G5** | `grep -rn '"sophia"' src/omega/workers/background_researcher/soul_updater.py` | 0 matches for fallback | Task 8 |
| **G6** | `make lint` | Clean | Final |
| **G7** | `cat docs/research/R_DOOM_WAD_DEEP_RESEARCH.md \| head -5` | File exists with content | Task W1 |
| **G8** | `cat docs/research/R_PLUGIN_ARCHITECTURE_PATTERNS.md \| head -5` | File exists with content | Task W2 |
| **G9** | `cat docs/research/R_AI_ENGINE_STACK_SEPARATION.md \| head -5` | File exists with content | Task W3 |
| **G10** | `cat docs/research/R_CONTAINER_DISTRIBUTION_MODELS.md \| head -5` | File exists with content | Task W4 |
| **G11** | `docs/research/INDEX.md` updated with 4 new entries | 4 new rows | Web tasks |

---

## §5 Rollback Protocol

If a commit breaks the test suite and you cannot fix it in 5 minutes:

```bash
git reset --hard HEAD~1  # Undo last commit
# READ the test output carefully, fix the bug, recommit
```

Do NOT push broken state. The Overseer reviews after you.

---

## §6 Post-Web-Research: INDEX.md Update

After writing the 4 web research documents, update `docs/research/INDEX.md` with 4 new entries. The existing table format is:

```markdown
| R-??? | ... | 🔴 Critical | ✅ | [filename](filename) | 2026-05-25 |
```

Add these rows (in alphabetical order by ID):

| ID | Title | Status | File |
|----|-------|--------|------|
| R-AI-STACK | AI Engine Stack Separation Patterns | ✅ | R_AI_ENGINE_STACK_SEPARATION.md |
| R-CONTAINER-DIST | Container Distribution Model Research | ✅ | R_CONTAINER_DISTRIBUTION_MODELS.md |
| R-DOOM-WAD | Doom WAD System Deep Research | ✅ | R_DOOM_WAD_DEEP_RESEARCH.md |
| R-PLUGIN-PATTERNS | Plugin & Extension Architecture Patterns | ✅ | R_PLUGIN_ARCHITECTURE_PATTERNS.md |

Urgency: all 🟡 High (foundational research for IWAD architecture validation).

---

*The fire is forged. Build the pillars.*
