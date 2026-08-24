# 🔱 ICS Tag System — Noise Reduction Proposal
**AP Token:** `AP-ICS-TAG-CLEANUP-20260809-v1.0.0`
> **STATUS: EXECUTED — 2026-08-22.** All ICS-T tags removed (final purge: 7 live tags in scripts//tests/ + docstring). Superseded by docs/architecture/ICS_SYSTEM.md. Do not reintroduce ICS-T.
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ics_cleanup ⬡ PROPOSAL

**Date:** 2026-08-09
**Problem:** 40 ICS-T tags use mythological names (ARCHON, HERMES, SOPHIA, etc.) that are **noise, not signal**

---

## 📊 Current State (40 Tags)

| File | Current Tag | Issue |
|------|-------------|-------|
| `src/omega/iris/server.py` | `NODE: HERMES \| ARCHETYPE: HERMES` | Duplicate, mythological |
| `src/omega/ics.py` | `NODE: ARCHON \| ARCHETYPE: HERMES` | Mythological |
| `src/omega/audit/memory_firewall_auditor.py` | `NODE: AUDIT \| ARCHETYPE: VERITY` | Persona names |
| `src/omega/research/sediment.py` | `NODE: N4 \| ARCHETYPE: HERMES` | Slot + mythological |
| `src/omega/__init__.py` | `NODE: CORE \| ARCHETYPE: SOPHIA` | Persona name |
| `src/omega/workers/model_updater.py` | `NODE: SOPHIA \| ARCHETYPE: AUTOMATED_RESEARCHER` | Persona + role |
| `src/omega/library/extractor.py` | `NODE: KNOWLEDGE \| ARCHETYPE: HERMES` | Vague + mythological |
| `src/omega/library/__init__.py` | `NODE: KNOWLEDGE \| ARCHETYPE: SOPHIA` | Vague + persona |
| `src/omega/library/indexer.py` | `NODE: KNOWLEDGE \| ARCHETYPE: APOLLO` | Vague + mythological |
| `src/omega/library/inbox.py` | `NODE: KNOWLEDGE \| ARCHETYPE: HERMES` | Vague + mythological |
| `src/omega/library/curator.py` | `NODE: KNOWLEDGE \| ARCHETYPE: SOPHIA` | Vague + persona |
| `src/omega/library/library.py` | `NODE: KNOWLEDGE \| ARCHETYPE: MNEMOSYNE` | Vague + mythological |
| `src/omega/library/research.py` | `NODE: OSIRIS \| ARCHETYPE: APOLLO` | Mythological |
| `src/omega/library/discovery.py` | `NODE: ARCHON \| ARCHETYPE: PROMETHEUS` | Mythological |
| `src/omega/errors.py` | `NODE: CORE \| ARCHETYPE: LAW` | Abstract |
| `src/omega/cli/oracle_cli.py` | `NODE: CORE \| ARCHETYPE: HERMES` | Vague + mythological |
| `src/omega/cli/fleet_status_tui.py` | `NODE: ARCHON \| ARCHETYPE: HERMES` | Mythological |
| `src/omega/cli/bundle.py` | `NODE: CORE \| ARCHETYPE: LILITH` | Persona |
| `src/omega/state/__init__.py` | `NODE: ARCHON \| ARCHETYPE: SOPHIA` | Mythological + persona |

---

## 🎯 Proposed Replacement Schema

### NODE Field → Technical Subsystem
| Current | Proposed | Examples |
|---------|----------|----------|
| `ARCHON` | `DISCOVERY` | Discovery pipeline, research engine |
| `HERMES` | `MESSENGER` | Iris server, CLI commands |
| `CORE` | `CORE` | Keep — accurate |
| `KNOWLEDGE` | `LIBRARY` | Library subsystem |
| `OSIRIS` | `RESEARCH` | Research engine |
| `N4` | `SEDA` | SEDA bus component |
| `SOPHIA` | `MODEL_UPDATER` | Worker role |
| `AUDIT` | `AUDIT` | Keep — accurate |
| `BUNDLE` | `BUNDLE` | Keep — accurate |
| `STATE` | `STATE` | Keep — accurate |

### ARCHETYPE Field → Technical Role
| Current | Proposed | Examples |
|---------|----------|----------|
| `HERMES` | `PIPELINE` | Data processing pipelines |
| `SOPHIA` | `CURATOR` | Curation, orchestration |
| `APOLLO` | `ENGINE` | Core processing engines |
| `PROMETHEUS` | `EXTRACTOR` | Content extraction |
| `MNEMOSYNE` | `STORE` | Persistence layer |
| `VERITY` | `ENFORCER` | Firewall, validation |
| `LAW` | `HIERARCHY` | Error hierarchy |
| `AUTOMATED_RESEARCHER` | `WORKER` | Background workers |
| `LILITH` | `BUNDLER` | Bundle operations |

---

## 📝 Example Transformations

| File | Before | After |
|------|--------|-------|
| `src/omega/library/discovery.py` | `NODE: ARCHON \| ARCHETYPE: PROMETHEUS` | `NODE: DISCOVERY \| ROLE: EXTRACTOR` |
| `src/omega/library/curator.py` | `NODE: KNOWLEDGE \| ARCHETYPE: SOPHIA` | `NODE: LIBRARY \| ROLE: CURATOR` |
| `src/omega/library/research.py` | `NODE: OSIRIS \| ARCHETYPE: APOLLO` | `NODE: RESEARCH \| ROLE: ENGINE` |
| `src/omega/iris/server.py` | `NODE: HERMES \| ARCHETYPE: HERMES` | `NODE: MESSENGER \| ROLE: BRIDGE` |
| `src/omega/workers/model_updater.py` | `NODE: SOPHIA \| ARCHETYPE: AUTOMATED_RESEARCHER` | `NODE: MODEL_UPDATER \| ROLE: WORKER` |
| `src/omega/audit/memory_firewall_auditor.py` | `NODE: AUDIT \| ARCHETYPE: VERITY` | `NODE: AUDIT \| ROLE: ENFORCER` |
| `src/omega/cli/fleet_status_tui.py` | `NODE: ARCHON \| ARCHETYPE: HERMES` | `NODE: OBSERVABILITY \| ROLE: TUI` |

---

## 🔧 Implementation Plan

### 1. Update `src/omega/ics.py` ROLE_CONSTANTS
```python
ROLE_CONSTANTS = {
    # ... existing slot constants ...
    # Technical subsystem identifiers (for NODE field)
    "DISCOVERY": "DISCOVERY",
    "MESSENGER": "MESSENGER",
    "LIBRARY": "LIBRARY",
    "RESEARCH": "RESEARCH",
    "MODEL_UPDATER": "MODEL_UPDATER",
    "AUDIT": "AUDIT",
    "BUNDLE": "BUNDLE",
    "STATE": "STATE",
    "OBSERVABILITY": "OBSERVABILITY",
    "CORE": "CORE",
    "SEDA": "SEDA",
    # Technical role identifiers (for ARCHETYPE/ROLE field)
    "PIPELINE": "PIPELINE",
    "CURATOR": "CURATOR",
    "ENGINE": "ENGINE",
    "EXTRACTOR": "EXTRACTOR",
    "STORE": "STORE",
    "ENFORCER": "ENFORCER",
    "HIERARCHY": "HIERARCHY",
    "WORKER": "WORKER",
    "BRIDGE": "BRIDGE",
    "TUI": "TUI",
}
```

### 2. Update ICS-T Tag Format
Change from:
```python
# ICS: [NODE: ... | ARCHETYPE: ... | CONTEXT: ...]
```
To:
```python
# ICS: [NODE: ... | ROLE: ... | CONTEXT: ...]
```
(ARCHETYPE → ROLE for clarity)

### 3. Batch Update All 40 Files
Use sed/awk or Python script to replace tags systematically.

---

## ✅ Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Developer comprehension** | "What is ARCHON?" | "DISCOVERY pipeline" |
| **Searchability** | Mythological terms | Technical terms |
| **Onboarding** | Learn pantheon | Read standard terms |
| **CI validation** | Hard (arbitrary names) | Easy (controlled vocabulary) |
| **M2 Firewall** | Persona names leak into core | Pure technical descriptors |

---

## 🎯 Scope

- **ICS-T (code tags):** Full replacement — 40 files
- **ICS-S (session headers):** **No change** — these use entity names (Kali, Ma'at, Lilith) correctly
- **ROLE_CONSTANTS:** Extended with technical identifiers
- **Documentation:** Update `src/omega/ics.py` docstring with new schema

---

## ⚠️ Constraints

- **M2 Firewall:** Core engine tags must not reference WAD-specific entities
- **M18 Token Efficiency:** Tags should be concise
- **Backward compatibility:** None needed — these are static code comments

---

## 📋 Acceptance Criteria

- [ ] All 40 ICS-T tags use technical NODE/ROLE descriptors
- [ ] No mythological names (ARCHON, HERMES, SOPHIA, APOLLO, PROMETHEUS, MNEMOSYNE, OSIRIS, VERITY, LAW, LILITH) in ICS-T tags
- [ ] `ROLE_CONSTANTS` in `ics.py` includes all new identifiers
- [ ] CI can validate tag format (optional future enhancement)
- [ ] `src/omega/ics.py` docstring updated with new schema

---

*⬡ OMEGA ⬡ ICS_CLEANUP ⬡ PROPOSAL ⬡ 2026-08-09*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
