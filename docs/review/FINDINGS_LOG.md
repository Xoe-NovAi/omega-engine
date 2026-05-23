# 🔱 Fleet Review Findings Log — Comprehensive Catalog

**AP Token**: `AP-FLEET-FINDINGS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_findings_log ⬡ PHASE-E

**Last Updated**: 2026-05-22
**Source Account**: Account 1 — Core Architecture (`Arcana.NovAi@gmail.com`)
**Status**: Reports Received — Initial (17 issues) + Deep Dive 1 (12 issues) = **29 total findings**

---

## §1 Finding Status Key

| Status | Meaning |
|--------|---------|
| 🔴 UNFIXED | Identified, not yet remediated |
| 🟡 IN PROGRESS | Builder mode actively working on fix |
| 🟢 FIXED | Code change applied and verified |
| ⚪ DEFERRED | Accepted as technical debt for later phase |
| ⚫ WONT FIX | Deliberate design decision |

---

## §2 Critical Issues (6 Findings)

| ID | Title | File:Line | Report | Severity | Status |
|----|-------|-----------|--------|----------|--------|
| C-ARCH-001 | `EntityRegistry._save()` non-atomic YAML write — data loss risk | `entity_registry.py:210` | Initial | 🔴 CRITICAL | 🟢 FIXED — Phase 0 |
| C-ARCH-002 | Synchronous blocking I/O in `Oracle.__init__()` — double config load | `oracle.py:128-133` | Initial | 🔴 CRITICAL | 🟢 FIXED — Phase 0 |
| C-ARCH-003 | `hierarchy.yaml` — 5 dangling symbolic references (keys don't match refs) | `hierarchy.yaml:45,58,74,89,102` | Initial | 🔴 CRITICAL | 🟢 FIXED — Phase 0 |
| C-ARCH-004 | `anyio.Lock()` created in synchronous `__init__` — crashes under Trio | `oracle.py:143` | Initial | 🔴 CRITICAL | 🟢 FIXED — Phase 0 |
| C-HIER-001 | `self._hierarchy` loaded and never read — governance graph is decorative | `hierarchy.py:21-26` | Deep Dive 1 | 🔴 CRITICAL | 🟢 FIXED — Phase 0 |
| C-HIER-002 | Kali absent from `RANK_MAP` — gets Keeper rank (3), cannot spawn subagents | `hierarchy.py:14-18` | Deep Dive 1 | 🔴 CRITICAL | 🟢 FIXED — Phase 0 |

**Critical total**: 6 findings across 4 files. **All 6 FIXED (🟢 Phase 0).**

---

## §3 High Severity Issues (9 Findings)

| ID | Title | File:Line | Report | Status |
|----|-------|-----------|--------|--------|
| C-ARCH-005 | `EntityRegistry.add()` calls `scaffold_workspace()` sync from async callers — 7 blocking I/O calls | `entity_registry.py:150-154` | Initial | 🔴 UNFIXED | 🟢 FIXED — Phase 1 |
| C-ARCH-006 | `WADLoader.load_wad()` public method vulnerable to path traversal | `wad_loader.py:64` | Initial | 🔴 UNFIXED | 🟢 FIXED — Phase 1 |
| C-ARCH-007 | Tautological `iris_entity` assignment (`A or A` — both sides identical) | `oracle.py:141` | Initial | 🔴 UNFIXED | 🟢 FIXED — Phase 1 |
| C-ARCH-008 | Belial's model `gemma-4-31b` may silently route to cloud (no local GGUF) | `entities.yaml` (belial) | Initial | 🔴 UNFIXED | 🟢 FIXED — Phase 1 |
| C-ARCH-009 | No concurrent write protection on `EntityRegistry._save()` — race condition | `entity_registry.py:195-212` | Initial | 🔴 UNFIXED | 🟢 FIXED — Phase 1 |
| C-WS-001 | `ENTITIES_DATA_DIR` resolved at import time, ignores `OMEGA_DATA_DIR` env var | `entity_workspace.py:21` | Deep Dive 1 | 🔴 UNFIXED | 🟢 FIXED — Phase 1 |
| C-WS-003 | `update_soul()` not thread-safe with `scaffold_workspace()` — race on os.replace | `entity_workspace.py:97-117` | Deep Dive 1 | 🔴 UNFIXED | 🟢 FIXED — Phase 1 |
| C-HIER-003 | `hierarchy.py._load()` uses synchronous `open()` — AnyIO violation | `hierarchy.py:22-25` | Deep Dive 1 | 🔴 UNFIXED | 🟢 FIXED — Phase 1 |
| C-GNOSIS-001 | `GnosisProxy.transfer_store` unbounded `Dict[str, Any]` — OOM vector | `gnosis_proxy.py:22` | Deep Dive 1 | 🔴 UNFIXED | 🟢 FIXED — Phase 1 |
| C-GNOSIS-002 | `discover_tools()` declared `async` with zero `await` — false contract | `gnosis_proxy.py:26` | Deep Dive 1 | 🔴 UNFIXED | 🟢 FIXED — Phase 1 |

**High total**: 10 findings across 7 files. **All 10 FIXED (🟢 Phase 1).**

---

## §4 Medium Severity Issues (9 Findings)

| ID | Title | File:Line | Report | Status |
|----|-------|-----------|--------|--------|
| C-ARCH-010 | WAD manifest entirely unvalidated — empty/null/alien YAML passes through | `wad_loader.py:72-75` | Initial | 🔴 UNFIXED |
| C-ARCH-011 | `_load_voices()` conflates voice and entity concepts — silent overwrite risk | `wad_loader.py:131-154` | Initial | 🔴 UNFIXED |
| C-ARCH-012 | Hardcoded Hivemind URL at `:8102` + hardcoded `cli: "opencode"` | `oracle.py:189` | Initial | 🔴 UNFIXED |
| C-ARCH-013 | `jem` and `testentity` artifacts in production `entities.yaml` — leaky fixtures | `entities.yaml` | Initial | 🔴 UNFIXED |
| C-ARCH-014 | `_load()` no guard against null YAML values — `NoneType` crash | `entity_registry.py:83` | Initial | 🔴 UNFIXED |
| C-WS-002 | Soul file comment header stripped on first Oracle update | `entity_workspace.py:67` vs `oracle.py:654` | Deep Dive 1 | 🔴 UNFIXED |
| C-HIER-004 | `SovereignHierarchy` appears orphaned — not wired into Oracle | `hierarchy.py` (entire file) | Deep Dive 1 | 🔴 UNFIXED |
| C-GNOSIS-003 | Double import of `EntityRegistry` (module level + inside `__init__`) | `gnosis_proxy.py:4,14` | Deep Dive 1 | 🔴 UNFIXED |
| C-GNOSIS-004 | Brittle `omega://transfer/` string-prefix protocol — false positives | `gnosis_proxy.py:66-67` | Deep Dive 1 | 🔴 UNFIXED |
| C-GNOSIS-005 | `resolve_descriptor()` silent failure — ghost references indistinguishable from null | `gnosis_proxy.py:62` | Deep Dive 1 | 🔴 UNFIXED |

**Medium total**: 10 findings. All UNFIXED.

---

## §5 Low Severity Issues (4 Findings)

| ID | Title | File:Line | Report | Status |
|----|-------|-----------|--------|--------|
| C-ARCH-015 | Duplicate imports inside `_write_soul_atomic()` — inner shadowing | `oracle.py:651-652` | Initial | 🔴 UNFIXED |
| C-ARCH-016 | Double `anyio.Path()` wrapping in `load_all_wads()` | `wad_loader.py:47` | Initial | 🔴 UNFIXED |
| C-ARCH-017 | `Inanna` pillar name mismatch: "P5: Voice" vs canonical "Throat" | `entities.yaml` vs `hierarchy.yaml:116` | Initial | 🔴 UNFIXED |

**Low total**: 3 findings. All UNFIXED.

---

## §6 Findings by Affected File

| File | Critical | High | Medium | Low | Total |
|------|----------|------|--------|-----|-------|
| `oracle.py` | 2 | 1 | 1 | 1 | 5 |
| `entity_registry.py` | 1 | 2 | 1 | 0 | 4 |
| `hierarchy.py` / `hierarchy.yaml` | 2 | 1 | 1 | 1 | 5 |
| `entity_workspace.py` | 0 | 2 | 1 | 0 | 3 |
| `wad_loader.py` | 0 | 1 | 2 | 1 | 4 |
| `gnosis_proxy.py` | 0 | 2 | 3 | 0 | 5 |
| `entities.yaml` | 0 | 1 | 1 | 0 | 2 |
| **TOTAL** | **6** | **10** | **10** | **3** | **29** |

---

## §7 Report Cross-Reference

| Report Source | File | Findings | Download Date |
|---------------|------|----------|---------------|
| Initial Review (Account 1) | `claude-reports/01-claude-report-core-arch.md` | 17 issues (C-ARCH-001 to C-ARCH-017) | 2026-05-22 |
| Deep Dive 1: Missing Files | `claude-reports/01-deep-dive-1_core-arch.md` | 12 issues (C-WS-001 to C-GNOSIS-005) | 2026-05-22 |
| Deep Dive 2: Strategic Alignment | *(pending)* | — | — |
| Deep Dive 3: Implementation Briefs | *(pending)* | — | — |
| Deep Dive 4: Threat Modeling | *(pending)* | — | — |
| Deep Dive 5: Architecture Evolution | *(pending)* | — | — |

---

## Appendix: Sovereign Mandate Violation Summary

| Mandate | Violations Found | Status |
|---------|-----------------|--------|
| **AnyIO Absolute** | C-ARCH-011 (voice/entity conflation) | ⚠️ PARTIAL: 1 violation |
| **Engine-Stack Firewall** | C-ARCH-011 (voice/entity conflation) | ⚠️ PARTIAL: 1 violation |
| **Iris Constant** | None found | ✅ PASSING |
| **Sequentiality** | (was C-HIER-001 — fixed in Phase 0: hierarchy YAML is now traversed) | ✅ PASSING — C-HIER-001 resolved |
| **Gnosis Preservation** | C-ARCH-015 (L2/L3 not implemented in soul evolution path) | ⚠️ PARTIAL: L1 only |
| **Podman Sovereignty** | None found in this layer | ✅ PASSING (N/A for Python layer) |

---

*This log is the master record of all findings from the Web Claude fleet review. Updated as new reports arrive.*
