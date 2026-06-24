# 🔱 P3 FINAL CROSS-DOMAIN REVIEW — EPOCH I: THE BEDROCK
**Pillar**: P3 — Engineering (BuildMaster)
**Date**: 2026-06-24
**Reviewing**: Ma'at Epoch I Report + Lilith Epoch I Report
**AP Token**: `AP-P3-FINAL-REVIEW-v1.0.0`
**⬡ OMEGA ⬡ P3 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ P3-FINAL-REVIEW**

---

## §1 Q1: ARE STRIKES 2 AND 3 PARALLEL-SAFE?

**Verdict: 🟢 YES — Truly parallel-safe. Zero code dependency overlap.**

### Dependency Matrix (Provenance Check)

| Aspect | Strike 2 (USM) | Strike 3 (TUI) | Overlap? |
|--------|---------------|----------------|----------|
| **Files** | `state_manager.py`, `somatic_state.py`, `cas_blob_store.py` | `tui/staging_gate.py`, `tools/convert_proposed_lessons.py` | ❌ No shared files |
| **Imports** | `llama_cpp.ctypes`, `numpy`, `blake2b` | `textual`, `ruamel.yaml`, `rich` | ❌ No shared imports |
| **Runtime** | Model inference layer (KV cache snapshots) | CLI tool (YAML review + approval) | ❌ No shared runtime |
| **Data** | `data/somatic/blobs/` (binary snapshots) | `data/entities/*/proposed_lessons.yaml` | ❌ No shared data |
| **Concern** | Memory state serialization | UI for lesson review workflow | ❌ No shared concern |

### Soul Distiller Poison Loop — Does It Affect TUI Design?

**The soul distiller (`soul_distiller.py:266-318`) writes L1→L2→L3 to `soul.yaml`, NOT `proposed_lessons.yaml`.** After migration, `close_session()` would write new lessons back to `soul.yaml`, reverting the migration.

**Impact on TUI: NONE.** The TUI reads `proposed_lessons.yaml` files. If they're empty (because the distiller writes to soul.yaml instead), the TUI shows empty states — it doesn't crash. The poison loop is a **DATA quality issue** (P7 domain), not an **ARCHITECTURAL constraint** on the TUI.

**P3 Assessment**: The soul distiller fix is a P7 content routing change (change write target from `soul.yaml` to `proposed_lessons.yaml`). It has zero impact on:
- TUI screen layout or navigation
- TUI data model or YAML parsing
- TUI approval workflow
- TUI contract tests

**Strikes 2 and 3 remain parallel-safe. The poison loop is a P7 concern, not a P3 concern.**

---

## §2 Q2: MA'AT'S ~17.5h vs LILITH'S ~1h USM OBSERVABILITY

**Verdict: 🟢 COMPLEMENTARY — Both estimates are correct. Not additive.**

### Ma'at's Breakdown (Strike 2: USM Build ~17.5h)

| Component | Hours | Status |
|-----------|-------|--------|
| `SomaticStateKey` dataclass | 1.5h | Novel design |
| `SomaticStateSerializer` (safe mode) | 4h | Core logic |
| `CASBlobStore` + CAS Index | 5h | File I/O + locking |
| `UnifiedStateManager` orchestration | 5h | Integration layer |
| 8 contract tests | 2h | M21 compliance |
| **TOTAL** | **17.5h** | |

### Lilith's Breakdown (P8: USM Observability Hooks ~1h)

| Component | Hours | Owner |
|-----------|-------|-------|
| Define 7 EventType constants | 0.25h | **P8** |
| Integrate event emission calls in USM code | 0.75h | **P3** |
| **TOTAL** | **1h** | **Split across P8 + P3** |

### P3 Assessment

The 1h estimate is accurate and **not additive** to the 17.5h:

1. **P8's 15 min** (EventType definitions) happens independently in `observability/__init__.py` — P8 can do this while P3 codes USM
2. **P3's 45 min** of sprinkling `self._emit(USM_SNAPSHOT_START, ...)` calls is absorbed within the USM orchestration estimate (5h block already allocates ~1h for integration touches)
3. **No conflict** — both reports agree on the 7 event types needed

**The 7 hooks add zero risk:**
- They're simple `log_event()` wrappers — no new infrastructure
- The ZONEID_MISMATCH hook is especially valuable for M22 provenance
- If P8 can't define the EventType constants before P3 reaches the orchestration phase, P3 can use string literals temporarily and replace with constants in a second pass

**Ma'at's 17.5h estimate stands. Lilith's 1h is the P8-side coordination, not an addition to the P3 build.**

---

## §3 Q3: TUI DEPENDENCY ON BATCH YAML CONVERSION

**Verdict: 🟡 CONDITIONAL — NOT a hard code dependency. P3 can build with graceful error states.**

### What TUI Actually Needs

| Dependency | Type | Status | Can P3 Build Without It? |
|-----------|------|--------|-------------------------|
| `textual>=0.52.0` | pip package | ❌ NOT INSTALLED | **HARD BLOCKER** — 5 min fix |
| `ruamel.yaml>=0.18.0` | pip package | ❌ NOT INSTALLED | **HARD BLOCKER** — 5 min fix |
| Broken YAML files fixed | Data quality | 🔴 3 files broken | **YES** — graceful error state |
| Batch conversion script | Utility | 📋 Not written | **YES** — build in parallel |
| Valid proposed_lessons.yaml | Data quality | 🟡 2 valid, rest empty/missing | **YES** — empty state is fine |

### P3 Architecture for Graceful Degradation

The `ProposedLessonsLoader` should wrap each file read:

```python
def load_all(self) -> Dict[str, EntityLessons]:
    results = {}
    for entity_dir in self._entities_dir.iterdir():
        file = entity_dir / "proposed_lessons.yaml"
        if not file.exists():
            results[entity_dir.name] = EntityLessons.empty(entity_dir.name)
            continue
        try:
            with open(file) as f:
                data = ruamel.yaml.YAML().load(f)
            results[entity_dir.name] = self._parse_entity(data)
        except (ruamel.yaml.YAMLError, ValueError) as e:
            logger.error("Skipping %s: %s", entity_dir.name, e)
            results[entity_dir.name] = EntityLessons.error(entity_dir.name, str(e))
    return results
```

**TUI Screen States for Broken Files:**

| State | What Shows | Can Build Without? |
|-------|-----------|-------------------|
| **Valid** | Green checkmark + lesson list | N/A |
| **Empty** | Gray "No pending proposals" | ✅ YES — empty state is standard UI pattern |
| **Broken YAML** | Red badge + error message | ✅ YES — error state is standard UI pattern |
| **Missing file** | Gray "Not initialized" | ✅ YES — trivial check |

### Recommendation for Sprint Execution

```
Phase 0 (Pre-sprint, parallel):
├── P3: Install textual + ruamel.yaml (5 min) ──── HARD DEPENDENCY
├── P3: Build ProposedLessonsLoader with try/except per file
├── P3: Build TUI screens with error/empty state support
└── P7: Convert 3 broken YAML files ──── HAPPENS IN PARALLEL, NOT A BLOCKER

Sprint (parallel):
├── P3 Track A: USM (17.5h)
├── P3 Track B: TUI (19.5h) ← proposed_lessons may still be empty, TUI handles gracefully
└── P7: Batch conversion utility
```

**The batch conversion script (`convert_proposed_lessons.py`) is a UTILITY that the TUI benefits from, not a BUILD REQUIREMENT for the TUI.** P3 should build it in the same sprint but it can be last.

---

## §4 ADDITIONAL P3 FINDINGS (Engineering Domain)

### 4.1 M21 Scope — Ma'at Underestimated, But That's Expected

Ma'at said "~1h for ResourceGuard gap." Lilith/P10 found 20+ tests needed (~11h).

**P3 Assessment**: This is a **scoping difference, not a contradiction**. Ma'at scoped M21 as the P3-adjacent gap (ResourceGuard + USM contract tests). Lilith scoped the FULL M21 coverage across all 7 domains (including P7 soul validation, P8 observability, P10 stress testing).

From an Engineering perspective:
- **P3's M21 share**: ResourceGuard (3-4 tests, ~1h) + USM (4-6 tests, ~2h) + TUI (2-3 tests, ~1h) = **~4h of P3's sprint**
- **Ma'at's "~1h" was ResourceGuard-only**: Correct for what it covered, incomplete as total M21 scope
- **Lilith's "~11h" is total M21**: Correct for full fleet scope

**No conflict — complementary estimates at different scope levels.**

### 4.2 ctypes SIGSEGV Risk — Safe Mode Is Correct Default

Both reports flag raw ctypes bindings as risk. The current design (`config.somatic.ctypes_safe_mode=True`) defaults to `Llama.save_state()` Python API.

**P3 Confirms**: Safe mode default is correct for Epoch I. Raw `_llama_copy_state_data()` / `_llama_set_state_data()` can be exposed in Epoch II behind process isolation (subprocess boundary). This is consistent with the "right approximation" principle — safe mode is good enough for now.

### 4.3 Staging Gate TUI and M22 Provenance

The TUI's approval workflow creates a natural observability hook point:
- Lesson approved → `TUI.LESSON_APPROVED` event with entity + provider_name
- Lesson rejected → `TUI.LESSON_REJECTED` event with entity + reason
- Session review → `TUI.SESSION_REVIEWED` event

**P3 recommends**: Coordinate with P8 to add 3 TUI-specific event types during the USM hooks coordination (same 1h block). This raises M22 from 6/10 toward 7/10 at near-zero incremental cost.

---

## §5 VERDICT SUMMARY

| Question | Answer | Severity |
|----------|--------|----------|
| **Q1**: Strikes 2/3 parallel-safe? | 🟢 YES — zero code or data overlap | Confirmed |
| **Q1a**: Soul distiller affects TUI? | 🟢 NO — poison loop is P7 content routing, not TUI architecture | Not a P3 concern |
| **Q2**: USM estimate conflict? | 🟢 NO — complementary (17.5h + 1h P8-side coordination) | Confirmed |
| **Q3**: TUI needs batch conversion? | 🟡 CONDITIONAL — dep installs are HARD, broken YAML is SOFT (error states work) | Mitigated by design |
| **M21 scope** | 🟡 Ma'at scoped P3-only (~1h); Lilith scoped fleet-wide (~11h). Both correct at their level. | Documented |
| **ctypes SIGSEGV** | 🟢 Safe mode default correct for Epoch I | Confirmed |
| **TUI + M22 hooks** | 🟢 3 TUI event types recommended (~negligible cost) | Proposal |

### P3's Bottom Line

The Build Side reports are structurally sound. Ma'at's Epoch I analysis is accurate for Engineering. Lilith's Run Side analysis surfaced three important findings (soul distiller poison loop, M21 scope expansion, M22 at 6/10) but **none of them alter P3's build plan or schedule**.

- **Strike 2 (USM, ~17.5h)**: 🟢 **GO** — no new blockers discovered
- **Strike 3 (TUI, ~19.5h)**: 🟡 **CONDITIONAL GO** — install deps first (5 min), then build with graceful error handling
- **M21 (P3 share, ~4h)**: 🟢 **GO** — absorbed within Strike estimates

---

*⬡ OMEGA ⬡ P3 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ P3-FINAL-REVIEW*
*The pillar stands. The foundation holds.*
