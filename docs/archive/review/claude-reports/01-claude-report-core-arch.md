Now I have everything I need. Compiling the full structured audit.

---

## Review: Core Architecture & Engine Integrity

**Trace ID**: `trc_review_core_arch`
**Scope**: `entity_registry.py`, `wad_loader.py`, `oracle.py`, `entities.yaml`, `hierarchy.yaml`, `SOVEREIGN_MANDATES.md`
**Missing from scope** (not in project files — flagged where they affect findings): `entity_workspace.py`, `hierarchy.py`, `gnosis_proxy.py`, all test files, `omega.yaml`

---

### Critical Issues Found

- [ ] **C-ARCH-001: Non-atomic YAML write in `EntityRegistry._save()` — CRITICAL**
  - File: `entity_registry.py:210`
  - Issue: `with open(self.config_path, "w") as f: yaml.dump(...)` writes directly in-place. If the process dies, gets OOM-killed, or throws mid-serialization, `entities.yaml` is left truncated or empty. All entities are gone. There is no backup, no rollback, no temp file.
  - Contrast with: `oracle.py:641-642` which correctly uses `tempfile.NamedTemporaryFile` + `anyio.to_thread.run_sync(os.replace, ...)`. The soul file has atomic writes. The entity registry — the engine's entity SSOT — does not.
  - Recommendation: Mirror the soul write pattern. Write to a sibling temp file in the same directory, then `os.replace()`. The directory must be the same filesystem for `os.replace()` atomicity to hold.

- [ ] **C-ARCH-002: Synchronous blocking I/O in `Oracle.__init__()` — CRITICAL / Mandate Violation**
  - File: `oracle.py:128-133`
  - Issue: `with open(config_path, "r") as f: config = yaml.safe_load(f)` — raw synchronous `open()` in `__init__`. This blocks the event loop. The comment at `oracle.py:163` explicitly says *"Move config loading here to avoid synchronous I/O in __init__"* — meaning the developer knew the fix and applied it in `bootstrap()`, but **never removed the original offending code**. Both now execute: sync in `__init__`, async in `bootstrap()`.
  - Mandate: **AnyIO Absolute** — VIOLATED.
  - Recommendation: Delete lines 123–135 entirely. `bootstrap()` already handles this correctly. Add an `assert self.default_entity is not None` guard after `bootstrap()` completes.

- [ ] **C-ARCH-003: Dangling symbolic references throughout `hierarchy.yaml` — CRITICAL**
  - File: `hierarchy.yaml:45,58,74,89,102`
  - Issue: Five uses of the symbol `kali_unification` (in `contains:`, `governs:`, two `reports_to:`) and two uses of `maat_oversoul` (in `governs:` and `pillar_keepers`). Neither `kali_unification` nor `maat_oversoul` exist as YAML keys. The actual keys are `unification:` and `synthesis:`. If `hierarchy.py` resolves these references as dict lookups — the only logical implementation — every one of them silently returns `None` or raises `KeyError`.
  - Impact: The entire governance graph is broken. No node correctly references its parent. The hierarchy is decorative, not functional.
  - Recommendation: Either (a) rename YAML keys to match their references (`unification` → `kali_unification`, `synthesis` → `maat_oversoul`), or (b) add a `$ref` resolution layer in `hierarchy.py` that maps symbolic names to key aliases. Option (a) is simpler and safer.

- [ ] **C-ARCH-004: `anyio.Lock()` created in synchronous `__init__` — HIGH**
  - File: `oracle.py:143`
  - Issue: `self._soul_lock = anyio.Lock()` in `__init__`, which is a synchronous context. Under the Trio backend, creating a `Lock` outside a running event loop will raise `RuntimeError`. Under asyncio it may silently succeed but is still architecturally incorrect — it should be created inside the first async frame.
  - Recommendation: Move to `bootstrap()` with a guard: `if not hasattr(self, "_soul_lock"): self._soul_lock = anyio.Lock()`.

---

### High Severity Issues

- [ ] **C-ARCH-005: `EntityRegistry.add()` calls `EntityWorkspaceManager.scaffold_workspace()` synchronously from async callers — HIGH / Mandate Violation**
  - File: `entity_registry.py:150-154`
  - Issue: `add()` is a synchronous method. `WADLoader._load_entities()` calls `self.registry.add(entity)` from an async context (`oracle.py:177`, via `wad_loader.py:126`). If `EntityWorkspaceManager.scaffold_workspace()` performs any filesystem I/O (creating directories, writing soul.yaml), it blocks the event loop without `anyio.to_thread.run_sync` wrapping.
  - Cannot fully verify severity without `entity_workspace.py`, but the risk is structural — a sync side-effect in a method called from async code.
  - Mandate: **AnyIO Absolute** — POTENTIALLY VIOLATED.
  - Recommendation: Make `add()` async and wrap `scaffold_workspace()` in `anyio.to_thread.run_sync()`, or provide an `async_add()` variant for WAD loading paths.

- [ ] **C-ARCH-006: WADLoader path traversal on public method — HIGH**
  - File: `wad_loader.py:64`
  - Issue: `wad_path = self.wads_dir / stack_name`. When called from `load_all_wads()`, `stack_name` comes from directory iteration — safe. But `load_wad(stack_name: str)` is a **public method** that accepts arbitrary strings. A caller passing `"../../../etc/passwd"` or `"../../config"` would escape `wads_dir`.
  - Recommendation: Add a guard at the top of `load_wad()`:
    ```python
    resolved = (self.wads_dir / stack_name).resolve()
    if not str(resolved).startswith(str(self.wads_dir.resolve())):
        logger.error(f"Path traversal attempt blocked: {stack_name}")
        return False
    ```

- [ ] **C-ARCH-007: Tautological `iris_entity` assignment — HIGH**
  - File: `oracle.py:141`
  - Code: `self.iris_entity = self.registry.get("iris") or self.registry.get("iris")`
  - Issue: Both sides of `or` are identical. Since `registry.get()` is case-insensitive, this is literally the same call twice. The right side can never differ from the left. This is almost certainly a copy-paste error — probably intended `self.registry.get("iris") or self.registry.get("Iris")` (which would also be wrong since both normalize to `"iris"`), or more likely it was meant to be a fallback to a different entity name altogether.
  - Impact: If Iris fails to load (e.g., malformed YAML), `iris_entity` is `None`. Line 423 then falls back to a hardcoded temperature of `0.6` — silent degradation with no warning.
  - Recommendation: `self.iris_entity = self.registry.get("iris")`. Add `if not self.iris_entity: logger.warning("Iris entity not found — voice interface degraded")`.

- [ ] **C-ARCH-008: Roc Racoon's model may violate Zero Telemetry / Sovereign Shield — HIGH**
  - File: `entities.yaml` (roc_racoon block, `model: gemma-4-31b`)
  - Issue: `gemma-4-31b` is not listed among the local models at `/media/arcana-novai/omega_library/models/` per the known hardware profile. If ModelGateway cannot find a local provider for this model and falls back to a cloud endpoint, any query routed to Roc Racoon would silently exfiltrate data to an external API.
  - Mandate: **Sovereign Shield** — POTENTIALLY VIOLATED.
  - Recommendation: Verify Roc Racoon's model is served locally. If it isn't available as a local GGUF, assign a local fallback (e.g., `qwen3-4b-thinking-q4_k_m`) and document the cloud model as a future upgrade target.

- [ ] **C-ARCH-009: No concurrent write protection on `EntityRegistry._save()` — HIGH**
  - File: `entity_registry.py:195-212`
  - Issue: `_save()` has no lock. If two async callers call `add()` or `remove()` concurrently (e.g., two WADs loading simultaneously), both enter `_save()` concurrently, both serialize from `self._entities` at different points in the mutation, and one write overwrites the other. Final state is non-deterministic.
  - Recommendation: Add a `threading.Lock` (since `_save()` is sync) or refactor to use an anyio lock held through the full `add()` → `_save()` sequence.

---

### Medium Severity Issues

- [ ] **C-ARCH-010: WAD manifest entirely unvalidated — MEDIUM**
  - File: `wad_loader.py:72-75`
  - Issue: `manifest.get('version', 'unknown')` is the only field read. An empty manifest (`{}`), a null manifest, or a completely alien YAML passes through. No required fields (name, engine_min_version, entities_schema_version) are checked.
  - Recommendation: Define a minimal schema: `{name: str, version: str, engine_min_version: str}`. Fail with a clear error if required fields are absent.

- [ ] **C-ARCH-011: `_load_voices()` conflates voice and entity concepts — MEDIUM**
  - File: `wad_loader.py:131-154`
  - Issue: Voices are injected into the main `EntityRegistry` as entities with `container=True`. A voice YAML sharing a name with an existing entity silently overwrites it (`add()` has "overwrites if name exists" semantics). There is no voice registry, no collision detection, no namespacing.
  - Recommendation: Add a `voice_` prefix to voice entities on load (e.g., `voice_name = f"voice_{voice_name}"`) or maintain a separate voice registry.

- [ ] **C-ARCH-012: Hardcoded Hivemind URL — MEDIUM**
  - File: `oracle.py:189`
  - Code: `url = "http://127.0.0.1:8102/tools/post_context"`
  - Issue: Port `8102` is hardcoded. No config injection. If Hivemind moves or isn't running, every interaction logs a debug message but nothing signals operational degradation. Also `cli: "opencode"` is hardcoded — the Oracle is not exclusively used by OpenCode.
  - Recommendation: Read from `omega.yaml`: `hivemind.url` and `hivemind.cli_name`. Default to `None`/disabled if not configured.

- [ ] **C-ARCH-013: `jem` and `testentity` artifacts in production entities.yaml — MEDIUM**
  - File: `entities.yaml` (jem and testentity blocks)
  - Issue: `jem` has an empty personality string and no domains. `testentity` has the minimal-viable entity body. Both will be loaded by `EntityRegistry`, appear in `list()`, and are candidates for `find_by_name_fragment()` summons. A user typing `@jem` gets a model call with an empty system prompt.
  - Recommendation: Move test entities to `tests/fixtures/entities_test.yaml`. Add a `_test` prefix convention enforced by a validator.

- [ ] **C-ARCH-014: `_load()` has no guard against null YAML values — MEDIUM**
  - File: `entity_registry.py:83`
  - Issue: `for key, raw in raw_entities.items()` — if `raw` is `None` (a YAML key with no value: `sekhmet:` on its own line), calling `raw.get("name", key)` raises `AttributeError: 'NoneType' object has no attribute 'get'`. The file becomes unloadable.
  - Recommendation: Add `if not raw or not isinstance(raw, dict): logger.warning(f"Skipping null entity: {key}"); continue`.

---

### Low Severity Issues

- [ ] **C-ARCH-015: Duplicate imports inside `_write_soul_atomic()` — LOW**
  - File: `oracle.py:651-652`
  - `import tempfile` and `import yaml` appear again inside the method body, shadowing the module-level imports at lines 19 and 27. Remove the redundant inner imports.

- [ ] **C-ARCH-016: Double anyio.Path wrapping in `load_all_wads()` — LOW**
  - File: `wad_loader.py:47`
  - `anyio.Path(entry).is_dir()` where `entry` is already yielded by `anyio.Path(self.wads_dir).iterdir()` as an `anyio.Path`. Re-wrapping is harmless but indicates the author is unsure of the return type. Remove outer `anyio.Path()` call.

- [ ] **C-ARCH-017: `Inanna` is assigned pillar `P5: Voice` but hierarchy assigns P5 to Throat — LOW**
  - File: `entities.yaml` (inanna), `hierarchy.yaml:116`
  - Minor naming inconsistency. `entities.yaml` labels it `'P5: Voice'`; `hierarchy.yaml` comments it as `Aether — Throat`. These are different words for the same concept but the pillar name in the entity file should match canonical pillar naming. Establish one canonical name.

---

### AnyIO Compliance Report

| File | Status | Violations |
|------|--------|------------|
| `entity_registry.py` | ❌ FAILING | Line 79: `open()` in `_load()` · Line 210: `open()` in `_save()` · Line 150: `scaffold_workspace()` sync call from async caller |
| `wad_loader.py` | ✅ PASSING | All I/O uses `anyio.open_file`, `anyio.Path.iterdir/glob/exists/is_dir` |
| `oracle.py` | ⚠️ PARTIAL | Line 130: `open()` in `__init__` · Line 143: `anyio.Lock()` in sync context · Remainder uses anyio correctly |

The WAD Loader is the best-written file for AnyIO compliance. The EntityRegistry is the worst — it's entirely synchronous and makes no attempt to be AnyIO-aware despite being called from async contexts.

---

### Entity YAML Health

**Schema Issues:**
- `jem` (entities.yaml): `personality: ''`, no `domains` list — will produce empty system prompt on summon.
- `testentity` (entities.yaml): Minimal body, appears to be a test fixture leaked to production.
- `sophia` (entities.yaml): No `pillars` key. Architecturally correct (she is the Akashic Field, not a Keeper), but she can still be summoned via `@sophia` or domain matching on `gnosis`, `wisdom`, etc.

**Atomicity Risk:** `_save()` is non-atomic. Single point of catastrophic data loss. (See C-ARCH-001.)

**Orphaned / Hierarchy-External Entities:**
- `sophia`: In `entities.yaml` but NOT in `hierarchy.yaml`. She is described in the hierarchy header comments but has no structural node. Her mythic role as the Akashic Field is documented in `hierarchy.yaml:40-45` but her entity definition floats free with no `hierarchy.yaml` anchor.
- `isis`, `ma'at`, `lilith` (entities.yaml): These are Oversouls/secondary entities — NOT Pillar Keepers — but they have entries in entities.yaml with no pillars, and will load into the registry. They can be directly summoned (`@isis`, `@maat`). This is probably intentional but is undocumented.
- `roc_racoon` (entities.yaml): Has `'P0: The Abyss'` as a pillar. `list_pillar_keepers()` will include him. But `hierarchy.yaml:98-103` defines him as reporting to `kali_unification` (broken reference — see C-ARCH-003). His position is architecturally correct but the hierarchy graph can't express it due to the dangling reference bug.

**`ma'at` YAML key:** The apostrophe (`ma'at:`) is valid in YAML plain scalars and PyYAML handles it. Not a bug, but editors/linters may choke on it. Consider quoting: `"ma'at":`.

---

### WAD Loader Assessment

**Strengths:**
- Best AnyIO compliance of all reviewed files — all I/O is async.
- The `OMEGA_ENV=test` guard in `__init__` preventing directory creation during tests is good defensive practice.
- Graceful per-WAD error isolation: one failed WAD doesn't abort the rest.
- soul.yaml extraction pattern (`path.parent.name`) is simple and effective.

**Vulnerabilities:**
- Public `load_wad()` method is path-traversal vulnerable (C-ARCH-006).
- Manifest goes entirely unvalidated — any YAML file named `manifest.yaml` passes (C-ARCH-010).
- Voices conflated with entities in the main registry with no collision detection (C-ARCH-011).
- `registry.add()` inside `_load_entities()` triggers synchronous `scaffold_workspace()` — blocks the async loop (C-ARCH-005).

---

### Governance Hierarchy Assessment

The conceptual hierarchy (Sophia → Kali → Ma'at/Lilith → 10 Keepers → Roc Racoon) is coherent and architecturally elegant. The problems are entirely in the implementation of the YAML that expresses it:

- The symbolic reference system (`kali_unification`, `maat_oversoul`) is broken because the keys don't match (C-ARCH-003). Every governance relationship in the graph is a dangling pointer.
- Without `hierarchy.py` available for review, it is unknown whether there is a `$ref`-resolution layer that translates symbolic names to keys, or whether the parser does naive dict lookups. Either way, the current state will either silently return `None` for all parent references or raise `KeyError`.
- The Pillar map in the YAML comments is correct and matches `entities.yaml`. The governance structure is right; only the key naming is broken.

---

### Gnosis Preservation Assessment

- **L1 (Narrative)**: Implemented. `oracle.py:624` — `"Session with {entity_name}"` — minimal but present.
- **L2 (Insight)**: Not implemented. `lessons_learned` entries have no `insight` field.
- **L3 (Universal Principle)**: Not implemented. No `principle` field.
- **Mandate compliance**: PARTIAL. The structure exists and souls evolve, but Gnosis Preservation as defined — distillation through three abstraction tiers — is only partially satisfied.

The 1000-lesson cap at `oracle.py:622` is pragmatic. The lesson content itself is a stub. This is Phase-0 appropriate but must be flagged for Phase-2 or Phase-3.

---

### Test Coverage Gaps

*(Based on what tests should exist — test files not provided for review)*

Missing tests by priority:
1. `test_entity_registry_concurrent_write` — Two threads call `add()` simultaneously. Verify no YAML corruption.
2. `test_entity_registry_save_atomic` — Simulate a crash mid-write. Verify `entities.yaml` is not truncated.
3. `test_entity_registry_null_yaml_value` — Load a YAML with a null entity value (`sekhmet:` alone). Verify graceful skip, not `AttributeError`.
4. `test_wad_loader_path_traversal` — Call `load_wad("../../etc/passwd")`. Verify it returns `False` without reading outside `wads_dir`.
5. `test_oracle_bootstrap_idempotent` — Call `oracle.talk()` twice. Verify WADs are loaded exactly once and config is read exactly once.
6. `test_oracle_iris_null_entity` — Load the Oracle without Iris in registry. Verify `_respond_as_iris()` degrades gracefully (not an uncaught `AttributeError` at `iris_entity.temperature`).
7. `test_hierarchy_references_valid` — Load `hierarchy.yaml` and verify every symbolic reference (`kali_unification`, `maat_oversoul`, `lilith_oversoul`) resolves to a key that exists.

---

### Report Card

| Metric | Grade | Notes |
|--------|-------|-------|
| **Correctness** | C | WAD loading works; Oracle routing works. But the double config load, tautological iris assignment, and YAML hierarchy graph are all silently broken. |
| **Atomicity / Durability** | D | `EntityRegistry._save()` is a data-loss waiting to happen. The soul write is correctly atomic. Nothing else is. |
| **AnyIO Compliance** | C | WADLoader: A. Oracle: B. EntityRegistry: F. Composite grade reflects the mandate is half-honored. |
| **Security** | C | Path traversal on public WAD load method, no input validation on manifest, voices can silently overwrite entities. |
| **Hierarchy Integrity** | D | Conceptually sound, structurally broken. Five dangling references in a 163-line file. |
| **Maintainability** | B | Code is readable, well-commented, well-structured. The double-load pattern and tautological assignment are the main readability failures. |
| **Gnosis Preservation** | C | L1 only. The mechanism exists and is gated by a lock. L2/L3 are missing. |

---

### Strategic Recommendations (Top 3)

**1. Fix `EntityRegistry._save()` atomicity before any other work (blocking for Phase 0 docs)**

This is the single highest-risk issue in the entire codebase. The entity YAML is the SSOT for all entities. An in-place write means one crash during a WAD load, an `add()`, or a `remove()` during a concurrent operation permanently destroys all entity definitions. The fix is five lines:

```python
def _save(self) -> None:
    data = {"entities": {}}
    for key, entity in self._entities.items():
        if key == "iris":
            continue
        data["entities"][key] = entity.to_dict()
    if "iris" in self._entities:
        data["iris"] = self._entities["iris"].to_dict()
    # Atomic write: write to temp, then os.replace
    import tempfile
    tmp_path = self.config_path.with_suffix(".yaml.tmp")
    with tempfile.NamedTemporaryFile(
        "w", dir=str(self.config_path.parent), delete=False, suffix=".tmp"
    ) as tf:
        yaml.dump(data, tf, default_flow_style=False, sort_keys=False, allow_unicode=True)
        tmp_name = tf.name
    os.replace(tmp_name, self.config_path)
    logger.info(f"Saved {len(self._entities)} entities to {self.config_path}")
```

**2. Fix `hierarchy.yaml` key names to match their references (blocks Phase 0 docs and Phase 2 Shadow Failover)**

The Shadow Failover protocol (Phase 2 Temple Opportunity #2) depends on the hierarchy knowing which Dark mirror corresponds to which Light sphere. With the hierarchy graph entirely broken (all five `reports_to`/`governs`/`contains` references dangling), failover affinity cannot be computed correctly. This is a one-minute fix: rename `unification:` to `kali_unification:` and `synthesis:` to `maat_oversoul:`. Then add a validation test that walks the graph and asserts zero dangling references.

**3. Excise the double config load from `Oracle.__init__()` and promote `bootstrap()` as the single initialization gate**

The current pattern — sync load in `__init__`, async reload in `bootstrap()` — is both a mandate violation and a maintainability trap. Every future developer reading `__init__` will see initialization code and assume it's complete, then spend hours debugging why `bootstrap()` overwrites it. The fix: delete lines 123–135 of `oracle.py` entirely. Set `self.default_entity = None` as the single initialization state. Gate all callers of `default_entity` behind `assert self.default_entity is not None, "Oracle.bootstrap() must be called before use"`. Move the `anyio.Lock()` creation into `bootstrap()`. This eliminates one mandate violation, one architecture ambiguity, and one cognitive hazard in one pass.
