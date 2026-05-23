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

## Phase 2: ✅ COMPLETE — Medium Severity Resolution

**Completed**: 2026-05-23 by Builder mode (Gemma 4 31B)
**Result**: 10/10 MEDIUM issues FIXED. `make test`: 241/241 PASSING (+2 new tests).

| ID | File | Fix Applied | Verification |
|----|------|-------------|--------------|
| **C-ARCH-010** | `wad_loader.py` | YAML null guard + required fields validation (`name`, `version`, `entities`) | ✅ 241/241 |
| **C-ARCH-011** | `wad_loader.py` | `_load_voices()` and `_load_entities()` as separate typed methods — no concept conflation | ✅ 241/241 |
| **C-ARCH-012** | `oracle.py` + `omega.yaml` | Hivemind URL `:8102` and `cli: "opencode"` moved to config | ✅ 241/241 |
| **C-ARCH-013** | `config/entities.yaml` | `jem` and `testentity` fixtures removed from production | ✅ 241/241 |
| **C-ARCH-014** | `entity_registry.py` | Null guard: `if data is None: raise ValueError(...)` | ✅ 241/241 |
| **C-WS-002** | `entity_workspace.py` + `oracle.py` | Soul file header constant shared across write paths | ✅ 241/241 |
| **C-HIER-004** | `hierarchy.py` + `oracle.py` | `self.hierarchy = SovereignHierarchy()` wired into Oracle | ✅ 241/241 |
| **C-GNOSIS-003** | `gnosis_proxy.py` | Duplicate `EntityRegistry` import removed from `__init__` | ✅ 241/241 |
| **C-GNOSIS-004** | `gnosis_proxy.py` | `isinstance(v, DescriptorRef)` replaces brittle `startswith("omega://transfer/")` | ✅ 241/241 |
| **C-GNOSIS-005** | `gnosis_proxy.py` | `raise KeyError(...)` replaces silent `dict.get()` for expired descriptors | ✅ 241/241 |

**Phase 2 Gate**: ✅ PASSED — all 10 MEDIUM issues FIXED, `make test` green (241/241).

---

## Phase 3: ✅ COMPLETE — Low Severity Resolution

**Completed**: 2026-05-23 by Builder mode (Gemma 4 31B)
**Result**: 3/3 LOW issues FIXED. `make test`: 241/241 PASSING.

| ID | File | Fix Applied | Verification |
|----|------|-------------|--------------|
| **C-ARCH-015** | `oracle.py:651-652` | Duplicate `import yaml` and `from pathlib import Path` removed from `_write_soul_atomic()` | ✅ 241/241 |
| **C-ARCH-016** | `wad_loader.py:47` | Double `anyio.Path()` unwrapped — single `Path` expression | ✅ 241/241 |
| **C-ARCH-017** | `entities.yaml` + `hierarchy.yaml` | Inanna pillar: "P5: Throat" harmonized across both files | ✅ 241/241 |

**Phase 3 Gate**: ✅ PASSED — all 3 LOW issues FIXED, `make test` green (241/241).

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
| Phase 2 — Medium | 10 | ✅ ~3 hours (actual) |
| Phase 3 — Low | 3 | ✅ ~30 min (actual) |
| **TOTAL** | **29** | **✅ ALL FIXED (~11.5 hours)** |

---

## §4 Future-Proofing: Prevention

Once all findings are fixed, add these to the CI pipeline:

1. **`test_hierarchy_references_valid`** — prevents C-ARCH-003 regression
2. **`test_atomic_writes`** — prevents C-ARCH-001 regression
3. **`test_no_blocking_io_in_async`** — prevents AnyIO mandate regression
4. **`test_no_fixture_entities_in_production`** — prevents C-ARCH-013 regression
5. **flake8 rule**: `TID251` — ban `open()` in async functions (ban `asyncio` imports)

---

*End of MASTER_REMEDIATION_PLAN. Updated: 2026-05-23. All 29 findings FIXED.*
