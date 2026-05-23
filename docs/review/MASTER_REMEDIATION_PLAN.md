# 🔱 Master Remediation Plan — Fleet Review Findings

**AP Token**: `AP-REMEDIATION-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_remediation ⬡ PHASE-E

**Purpose**: Phased implementation plan for all 29 findings from Account 1.
**Executor**: Gemma 4 31B (Builder mode — `.opencode/agents/builder.md`)
**Overseer**: Overseer mode (`.opencode/agents/overseer.md`) — review gate before status → FIXED
**Test Gate**: `make test` must pass before any fix is considered complete.

---

## Phase 0: ✅ COMPLETE — Critical Blocker Resolution

**Completed**: 2026-05-22 by Builder mode (Gemma 4 31B)
**Result**: 6/6 CRITICAL issues FIXED. `make test`: 236/236 PASSING.

| ID | File | Fix Applied | Verification |
|----|------|-------------|--------------|
| **C-ARCH-001** | `entity_registry.py` | Atomic write via `tempfile.NamedTemporaryFile` + `os.replace()` | ✅ `make test` passes |
| **C-ARCH-002** | `oracle.py:125-135` | Config load moved from sync `__init__` to async `bootstrap()` using `anyio.open_file` | ✅ `make test` passes |
| **C-ARCH-003** | `config/hierarchy.yaml` | 5 dangling keys renamed: `unification`→`kali_unification`, `synthesis`→`maat_oversoul`, `akashic_record`→`sophia`, `pillar_0`→`belial`, `pillar_keepers`→`keepers` | ✅ `make test` passes |
| **C-ARCH-004** | `oracle.py:143` | `self._soul_lock = None` in `__init__`, created as `anyio.Lock()` in `bootstrap()` | ✅ `make test` passes |
| **C-HIER-001** | `hierarchy.py` | Rebuilt `get_rank()` to traverse YAML `reports_to` chain. `get_oversoul()`, `get_dark_mirror()` methods added. Hardcoded `RANK_MAP` replaced with dynamic traversal. | ✅ `make test` passes |
| **C-HIER-002** | `hierarchy.py` | Kali → rank 1, Sophia → rank 0 (now dynamic from YAML). Belial → rank 2 (via `reports_to: kali_unification`). All entities properly ranked by chain depth. | ✅ `make test` passes |

**Phase 0 Gate**: ✅ PASSED — all 6 CRITICAL issues FIXED, `make test` green (236/236).

---

## Phase 1: ✅ COMPLETE — High Severity Resolution

**Completed**: 2026-05-22 by Builder mode (Gemma 4 31B)
**Result**: 10/10 HIGH issues FIXED. `make test`: 239/239 PASSING (+3 new tests).

| ID | File | Fix Applied | Verification |
|----|------|-------------|--------------|
| **C-ARCH-005** | `entity_registry.py` | `add()` → `async def` with `anyio.Lock()`, scaffold via `anyio.to_thread.run_sync` | ✅ 239/239 |
| **C-ARCH-006** | `wad_loader.py:64` | Path traversal guard: resolve + prefix validation | ✅ 239/239 |
| **C-ARCH-007** | `oracle.py:141` | `self.iris_entity = self.registry.get("iris")` — warning log on miss | ✅ 239/239 |
| **C-ARCH-008** | `entities.yaml` (belial) | Belial → `qwen3-4b-thinking-q4_k_m` (verified local GGUF) | ✅ 239/239 |
| **C-ARCH-009** | `entity_registry.py` | `_save()` wrapped in `anyio.Lock()` via `async with self._lock` | ✅ 239/239 |
| **C-WS-001** | `entity_workspace.py:21` | `ENTITIES_DATA_DIR` reads `OMEGA_DATA_DIR` env var | ✅ 239/239 |
| **C-WS-003** | `entity_workspace.py` | Cross-method `threading.Lock` per entity for scaffold/update | ✅ 239/239 |
| **C-HIER-003** | `hierarchy.py` | `async def load()` using `anyio.open_file` | ✅ 239/239 |
| **C-GNOSIS-001** | `gnosis_proxy.py:22` | Bounded transfer_store: MAX 1000 entries, FIFO eviction via deque | ✅ 239/239 |
| **C-GNOSIS-002** | `gnosis_proxy.py:26` | `discover_tools()` → sync function (removed false `async`) | ✅ 239/239 |

**Phase 1 Gate**: ✅ PASSED — all 10 HIGH issues FIXED, `make test` green (239/239).

---

## Phase 2: This Sprint — Medium Severity

---

## Phase 2: This Sprint — Medium Severity

**Goal**: Fix all 9 MEDIUM issues.
**Dependencies**: Phase 1 complete.

| ID | File | Fix Description | Est. Time | Test Strategy |
|----|------|-----------------|-----------|---------------|
| **C-ARCH-010** | `wad_loader.py` | Add YAML validation: schema check, null guard, required fields assertion. | 30 min | `test_wad_manifest_invalid_rejected` — empty/null/malformed YAML all raise clear errors |
| **C-ARCH-011** | `wad_loader.py:131-154` | Separate voice and entity concepts. Voice dir gets its own load path, entity dir its own. No overwriting. | 45 min | `test_voice_entity_no_overwrite` — same name in both dirs, verify both preserved |
| **C-ARCH-012** | `oracle.py:189` | Extract hardcoded URL and CLI name to `omega.yaml` config. Replace with `self.config.get("hivemind_url", ":8102")`. | 10 min | `test_hivemind_url_from_config` — override in test config, verify URL changes |
| **C-ARCH-013** | `entities.yaml` | Remove `jem` and `testentity` from production config. Add to test fixtures if needed. | 10 min | `test_no_fixture_entities_in_production` — grep for jem/testentity in runtime path |
| **C-ARCH-014** | `entity_registry.py:83` | Add null guard: `if data is None: raise ValueError("entities.yaml is empty or malformed")` | 10 min | `test_entity_registry_null_yaml_handling` — load empty YAML, verify clear error |
| **C-WS-002** | `entity_workspace.py:67` + `oracle.py:654` | Coordinate soul file headers. Extract header constant to shared location. Both write paths use same format. | 15 min | `test_soul_header_preserved_across_updates` — scaffold, update, verify header comment intact |
| **C-HIER-004** | `hierarchy.py` | Wire `SovereignHierarchy` into `Oracle.__init__()`. Make it accessible as `self.hierarchy`. | 20 min | `test_oracle_hierarchy_wired` — verify `oracle.hierarchy` returns valid instance |
| **C-GNOSIS-003** | `gnosis_proxy.py:4,14` | Remove duplicate import. Keep module-level import only. | 5 min | `test_no_duplicate_imports` — flake8 or grep for import-in-function patterns |
| **C-GNOSIS-004** | `gnosis_proxy.py:66-67` | Replace string-prefix protocol with typed `DescriptorRef` dataclass. `isinstance` check instead of `startswith`. | 20 min | `test_descriptor_ref_type_safe` — string that starts with omega://transfer/ is NOT hijacked |
| **C-GNOSIS-005** | `gnosis_proxy.py:62` | Replace `dict.get()` with: `raise KeyError(f"Descriptor {descriptor_id} not found")`. Wrap callers in try/except. | 10 min | `test_descriptor_expired_raises_error` — resolve unknown ID, verify KeyError raised |

**Phase 2 Gate**: All 10 MEDIUM issues FIXED, `make test` green. Estimated: **~3 hours**.

---

## Phase 3: Polish — Low Severity

**Goal**: Fix all 3 LOW issues.
**Dependencies**: None.

| ID | File | Fix Description | Est. Time | Test Strategy |
|----|------|-----------------|-----------|---------------|
| **C-ARCH-015** | `oracle.py:651-652` | Remove duplicate imports shadowed inside `_write_soul_atomic()`. Already imported at module level. | 5 min | `test_no_shadowed_imports` — flake8 check |
| **C-ARCH-016** | `wad_loader.py:47` | Remove double `anyio.Path()` wrapping. `Path(a) / b` is already `Path`. | 5 min | `test_wad_loader_path_no_double_wrap` |
| **C-ARCH-017** | `entities.yaml` + `hierarchy.yaml:116` | Fix Inanna pillar name mismatch: "P5: Voice" vs canonical "Throat". | 5 min | `test_pillar_names_consistent` — pillar name matches between entities.yaml and hierarchy.yaml |

**Phase 3 Gate**: All 3 LOW issues FIXED, `make test` green. Estimated: **~30 minutes**.

---

## §1 Builder Execution Order

When running Builder mode (Gemma 4 31B), execute in this strict order:

```
Phase 0 → Phase 1 → Phase 2 → Phase 3
(no skipping phases)
```

### Per-Fix Workflow

For each finding:

1. **Read**: Read the affected file(s) in full context
2. **Plan**: Cross-reference against FINDINGS_LOG.md for the exact issue description
3. **Fix**: Apply the change following Sovereign Mandates (AnyIO Absolute, Engine-Stack Firewall)
4. **Test**: Write/update test(s) that verify the fix
5. **Verify**: `make test` — all existing tests must still pass
6. **Report**: Update FINDINGS_LOG.md status to 🟢 FIXED
7. **Next**: Move to next finding in same phase

### Builder Mode Entry

When launching Builder mode for remediation:

```bash
opencode --mode builder --prompt "Execute MASTER_REMEDIATION_PLAN.md Phase {N}. Starting with {finding ID}."
```

---

## §2 Overseeer Review Gate

Before any finding's status can change from 🟡 IN PROGRESS to 🟢 FIXED:

1. **Overseer reads the diff**: Verify the fix is minimal (doesn't refactor unrelated code)
2. **Overseer runs `make test`**: Verify no regressions
3. **Overseer checks Mandates**: Verify fix doesn't introduce new AnyIO or Firewall violations
4. **Overseer updates FINDINGS_LOG.md**: Change status to FIXED

---

## §3 Estimated Total Effort

| Phase | Findings | Est. Time |
|-------|----------|-----------|
| Phase 0 — Critical | 6 | ✅ ~4 hours (actual) |
| Phase 1 — High | 10 | ✅ ~4 hours (actual) |
| Phase 2 — Medium | 10 | 📋 ~3 hours (estimated) |
| Phase 3 — Low | 3 | 📋 ~30 min (estimated) |
| **TOTAL** | **29** | **16 fixed, 13 remaining (~3.5 hr est.)** |

---

## §4 Future-Proofing: Prevention

Once all findings are fixed, add these to the CI pipeline:

1. **`test_hierarchy_references_valid`** — prevents C-ARCH-003 regression
2. **`test_atomic_writes`** — prevents C-ARCH-001 regression
3. **`test_no_blocking_io_in_async`** — prevents AnyIO mandate regression
4. **`test_no_fixture_entities_in_production`** — prevents C-ARCH-013 regression
5. **flake8 rule**: `TID251` — ban `open()` in async functions (ban `asyncio` imports)

---

*End of MASTER_REMEDIATION_PLAN. Updated: 2026-05-22.*
