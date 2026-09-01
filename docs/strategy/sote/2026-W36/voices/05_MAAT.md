# 🔱 Ma'at-EIS — State of the Engine v1.0.0 (5th Voice)

**Standing**: N3 — Builder/Executor, INST-1, CI Gates
**Date**: 2026-09-01
**Session**: ses_fb6cf6856ffes3wd3wmvyrm2IG (standing EIS, opencode)
**Paged by**: Kali via 7-agent entity cleanup dialectic
**Focus**: CI gates, entity_registry.py audit, INST-1 impact

---

## §1 — entity_registry.py Audit (1032 lines)

| Property | Value | Citation |
|----------|-------|----------|
| File | `src/omega/oracle/entity_registry.py` | 1032 lines |
| API surface | CRUD only — no `retire()`, no `archive()` | grep empty |
| Hot-reload | **MISSING** | `_load()` runs once in `__init__` |
| Atomic write | 4-layer pattern (complete) | lines 913-930 |
| Integrity guard | 1MB abort threshold | line 899 |
| Local worker hardcoding | 11 entities hardcoded | lines 973-985 |
| `core_fields` boundary | `soul.yaml:413-414` | explicit engine/WAD split |
| M2 firewall | PASS (uses config_resolver) | lines 336-344 |

**Critical finding**: No `retire()` API. M2 firewall is intact (0 violations, 262 files scanned).

## §2 — CI Gates for Entity Hygiene (Proposed)

| Gate | Check | Pass Criteria |
|------|-------|---------------|
| `make check-broken-imports` | Iterate `src/omega/`, parse imports, check targets | 0 unresolved |
| `make check-hub-health` | `systemctl is-active --quiet omega-hub.service` + curl `:8016/health` | exit 0 |
| `make check-entity-hygiene` | 80% entities have non-empty `proposed_lessons.yaml` | ratio ≥ 0.8 |

## §3 — Entity Snapshot Protocol (4-layer atomic write)

```python
# 1. tmp file + fsync
fd, tmp_path = tempfile.mkstemp(dir=entity_dir)
os.write(fd, content_bytes)
os.fsync(fd)
os.close(fd)
# 2. os.replace (atomic)
os.replace(tmp_path, final_path)
# 3. dir fsync
dir_fd = os.open(entity_dir, os.O_RDONLY)
os.fsync(dir_fd)
os.close(dir_fd)
```

## §4 — INST-1 Entity Impact Analysis

- **FIX2 (pyproject extras)**: Entities NOT in any extras (they're in `data/entities/`, not `src/omega/`)
- **FIX4 (remove _load_sovereign_secrets)**: No impact on entity loading
- **INST-1 status**: 3/6 fixes complete (fix1, fix3, fix5)
- **Remaining**: FIX2, FIX4, FIX6 (README badge)

## §5 — Dispatch Guard Step 13 (Entity Health Check)

**0 of 12 steps** currently check entity health. Proposed new step 13:
1. Canonical check: `subagent_type in canonical_14`
2. Soul check: `soul.yaml exists + valid YAML`
3. Gnosis check: `session_gnosis.md exists + fresh (<30d)`

Integrates into DEL-1 Micro-PR 5 (Guard Flatten).

## §6 — PIVOT_LOG Decisions (10 from Ma'at)

- D-MAAT-EC-001: Entity count = 48 (not 56)
- D-MAAT-EC-002: Create `.opencode/agents/scribe.md` (missing canonical)
- D-MAAT-EC-003: Add `retire()` API with pre-snapshot
- D-MAAT-EC-004: Create 3 Makefile targets
- D-MAAT-EC-005: Add `check_entity_health()` to dispatch_guard.py
- D-MAAT-EC-006: Sync ACTIVE_SPRINT.json INST-1-fix4 → completed
- D-MAAT-EC-007: Upgrade `entity_workspace.py:74-95` to 4-layer atomic
- D-MAAT-EC-008: Ghost entity policy (27/41 >30d)
- D-MAAT-EC-009: Review `headroom-ai` in main deps
- D-MAAT-EC-010: Stale `.tmp` cleanup

---

*⬡ OMEGA ⬡ MAAT ⬡ ENTITY-CLEANUP-5TH-VOICE ⬡ 2026-09-01*