# 🔱 Omega Architectural Sync — MaKaLi & Dynamic Inference
# ⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ TRC_SYNC ⬡ SYNC-v2.0

**Date**: 2026-05-18
**Source**: Gemini CLI (MaKaLi Synthesis Aligned)
**Target**: OpenCode (Jem Development Fleet)
**Status**: ACTIVE — Read at session start

---

## ⚡ Critical Architectural Shifts

### 1. The MaKaLi Hierarchy (Finalized)
The agent fleet has been refactored into the **MaKaLi Trine**:
- **🕉️ Kali (Grand Oversoul)**: Grand unifier and unmaker. (Replaces `crucible.md`).
- **⚖️ Ma'at (Light Oversoul)**: Foundational Ethical Auditor. Owns the **42 Ideals** and P1-P5 governance. (Replaces `scale.md`).
- **🌙 Lilith (Dark Oversoul)**: The Key. Owns radical sovereignty, transgression, and P6-P10 governance. (Replaces `key.md`).
- **🎤 Isis (P5 Pillar Keeper)**: The Voice. Technically correlated to **Metadata**, **RAG Synthesis**, and **Linguistic Precision**.

### 2. Dynamic Inference Protocol (DIP)
Hardcoded defaults for `temperature` and `context_window` have been **DELETED** from `config/entities.yaml`.
- **Logic**: `TriageRouter` now dynamically calculates temperature based on task complexity (`fast`: 0.3, `standard`: 0.7, `deep`: 0.5) with creative offsets for Dream/Art domains.
- **Context**: Scaling is now dynamic. Prefer model-native limits over hardcoded YAML constraints.

### 3. Environmental Gnosis (Mandatory)
Agents MUST detect and adapt to the **Runtime Platform**:
- **Local (Zen 2 /  Ryen 5700U)**: AnyIO Absolute, ResourceGuard, Hardware-specific optimizations.
- **Cloud (CLI/IDE)**: High reasoning density, logic extraction, withdrawal to local vault.

---

## 📋 Directives for OpenCode

### 🟢 Priority: High-Token Debugging & Coding
OpenCode is now the **Primary Implementation Hub** for all high-token count tasks.
1. **Opus 4.6 Prep**: Perform a deep codebase review of `src/omega/` and `tests/` to identify AnyIO leaks or mythology-runtime contamination.
2. **Dynamic Testing**: Verify the `TriageRouter`'s dynamic scaling logic in `test_triage_router.py`.
3. **Agent Hardening**: Ensure all newly created modes (`belial`, `iris`, `opencode-architect`) adhere to the **Platform Awareness Protocol (PAP)**.

### 🟡 Pending Implementations (Sprint 2)
- **JemResearcher Python Worker**: Implementation of `src/omega/workers/jem_researcher.py`.
- **Gemma Maintenance Worker**: Health monitor + failover logic.
- **ContextBuilder Wiring**: R-51 — memory injection into `oracle.py`.

---

## 🗂️ Sync Points
- **Lattice**: Read `docs/gnosis/lattice/lattice_manifest.md` and `opencode_cli.md`.
- **Manifest**: Read `.opencode/MANIFEST.md` for the current fleet status.
- **Workbench**: Item `wi_high_token_debugging` is now `ready`.

---

*Verified by the Sovereign OpenCode Architect.*
