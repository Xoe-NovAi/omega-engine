# 🔱 OmniHub — Cross-Platform Research & Integration Hub

**Part of the Omega Engine Research Knowledge Base**
**AP Token**: `AP-OMNIHUB-v0.1.0`
**Created**: 2026-05-16
**Maintained by**: OVERSIGHT / SOPHIA
**Purpose**: Centralize all cross-platform intelligence (Gemini, NotebookLM, Drive sync, Jem persona, fleet orchestration) and map it back into Omega Engine architecture.

---

## Why OmniHub Exists

This session exposed a fundamental truth: **Omega Engine development is now multi-platform by necessity**. The local-first core is sovereign, but intelligence augmentation from Google's ecosystem, opencode's fleet orchestration, and experimental persona engineering (Jem) each demand dedicated space that doesn't clutter the core roadmap.

OmniHub is that space. It holds the bridges, not the island.

---

## Core Workstreams

| # | Workstream | Status | Primary Owner | Links |
|---|------------|--------|---------------|-------|
| W-1 | DriveSync Daemon — bidirectional local↔Drive sync | 🔲 Not started | OVERSIGHT → BUILDER | `docs/research/omni/drivesync/` |
| W-2 | Dynamic Session Header — model-aware header builder | 🔲 Not started | OVERSIGHT → BUILDER | `R50_session_id_architecture.md` |
| W-3 | NotebookLM ↔ Mnemosyne bridge — cold memory tier | 🔲 Not started | SOPHIA → RESEARCHER | `docs/research/omni/notebooklm/` |
| W-4 | Jem Persona Schema — multi-faceted entity template | 🔲 Not started | SOPHIA → GNOSIS-ANALYST | `docs/research/omni/jem/` |
| W-5 | Fleet Orchestration Blueprint — serial → synthesis → parallel patterns | 🔬 In progress | OVERSIGHT | `docs/research/omni/fleet/` |
| W-6 | Glossary & Nomenclature — definitive term registry | 🔲 Not started | SCRIBE | `docs/research/omni/GLOSSARY.md` |

---

## Research Items

| ID | Title | Urgency | Status | Location |
|----|-------|---------|--------|----------|
| R-OMNIHUB-01 | DriveSync Daemon Spec — rclone + systemd + inotify | 🔴 Critical | 🔲 | `drivesync/SPEC.md` |
| R-OMNIHUB-02 | NotebookLM Import Automation — API wrapper for NotebookLM | 🟡 High | 🔲 | `notebooklm/AUTOMATION_SPEC.md` |
| R-OMNIHUB-03 | Jem Persona Deep Research — character analysis → entity schema | 🟡 High | 🔲 | `jem/PERSONA_ANALYSIS.md` |
| R-OMNIHUB-04 | Dynamic Header Implementation — ModelGateway integration | 🔴 Critical | 🔲 | (in core `src/omega/oracle/`) |
| R-OMNIHUB-05 | Cognitive Load Triage Layer — session-scope manager | 🟢 Strategic | 🔲 | `triage/SPEC.md` |
| R-OMNIHUB-06 | Fleet Orchestration Templates — reusable agent chains | 🟡 High | 🔲 | `fleet/TEMPLATES.md` |

---

## Integration Map

```
OmniHub Intelligence ──> Omega Engine Core
     │                         │
     ├─ DriveSync              ├─ entity_workspace.py (auto-sync entity workspaces to Drive)
     ├─ NotebookLM bridge      ├─ memory_store.py (cold tier reader)
     ├─ Jem persona schema     ├─ config/entities.yaml (new entity definition)
     ├─ Fleet patterns         ├─ orchestrator.py (prebuilt chain templates)
     └─ Glossary               ├─ GLOSSARY.md (project root)
```

---

## Session Gnosis Cross-Ref
- Parent session: `docs/gnosis/session_gnosis.md` (2026-05-16)
- PIVOT_LOG Decision 25
- INDEX.md entry `R-OMNIHUB`

---

## Next Steps (Priority Order)

1. **R-OMNIHUB-01** (DriveSync Daemon) — This is the #1 bottleneck. Spec must be written and implemented before any other OmniHub workstream.
2. **R-OMNIHUB-04** (Dynamic Header) — Quick fix, immediate debugging value.
3. **R-OMNIHUB-03** (Jem Persona) — Deep research deferred until DriveSync is live.
4. **R-OMNIHUB-06** (Fleet Orchestration Templates) — Encapsulate the serial→synthesis→parallel pattern as reusable OpenCode tasks.
5. **R-OMNIHUB-05** (Triage Layer) — Long-term architectural improvement.