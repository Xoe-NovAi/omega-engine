# 🔱 Platform Synchronization Gold Standard
# ⬡ OMEGA ⬡ MAAT ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_platform_sync ⬡ PHASE-II

**AP Token**: `AP-PLATFORM-SYNC-GOLD-v1.0.0`
**Status**: ACTIVE — Canonical Specification
**Date**: 2026-06-11

## §0 Objective
The **Platform Synchronization Gold Standard** defines the required state for the Omega Engine's "Sovereign Alignment." Because the engine is accessed via multiple interfaces (Antigravity, Cline, Gemini CLI, OpenCode), there is a high risk of "instruction drift" where one interface enforces a mandate that another ignores.

The goal of `make platform-sync` is to programmatically verify that the **14 Sovereign Mandates** (defined in `data/coordination/MANDATES_SYNC.md`) are active and consistent across all platforms.

---

## §1 The Synchronization Matrix

A platform is considered **SYNCED** if and only if the following conditions are met:

| Platform | Target File | Sync Criteria | Verification Method |
|----------|--------------|----------------|---------------------|
| **Antigravity** | `data/coordination/ANTIGRAVITY_CUSTOM_INSTRUCTIONS_v4.md` | Contains all 14 mandates in full or summarized form. | Textual overlap / Keyword scan |
| **Cline** | `.clinerules` | Contains all 14 mandates; version marked as v5.0.0. | Textual overlap / Version check |
| **Gemini CLI** | `~/.gemini/policies/auto-saved.toml` | Contains M11 (Soul Integrity) and M7 (Local-First) enforcement. | Key-value pair check |
| **OpenCode** | `.opencode/agents/*.md` | All 14 agents contain the "Hivemind-First Communication" and "Sovereign Mandates" sections. | File-count + Keyword scan |

---

## §2 Verification Logic (The "Gold" Test)

The `make platform-sync` target must execute the following logic:

1. **Load SSoT**: Read `data/coordination/MANDATES_SYNC.md` to extract the current list of 14 mandates and their core keywords.
2. **Scan Targets**: For each platform in the matrix:
    - Read the target configuration file.
    - Perform a "Fuzzy Match" for each mandate's core intent.
    - Check for version markers (e.g., "v5.0.0" in `.clinerules`).
3. **Calculate Alignment Score**:
    - `Alignment % = (Mandates Found / 14) * 100`
4. **Verdict**:
    - **SYNCED**: Alignment = 100% for all platforms.
    - **DRIFTED**: Any platform < 100%.
    - **CRITICAL**: Any platform < 50% or missing a P0 mandate (M1, M2, M7, M8).

---

## §3 Remediation Path

If `make platform-sync` returns **DRIFTED**, the following sequence is triggered:
1. **Identify Gap**: The tool outputs exactly which mandates are missing from which platform.
2. **Update SSoT**: If the drift is intentional (a new mandate was added), update `MANDATES_SYNC.md` first.
3. **Push Sync**: The user must manually (or via a future `make sync-push` tool) update the platform files to match the SSoT.
4. **Re-Verify**: Run `make platform-sync` again.

---

## §4 Sovereign Mandate Alignment (M13)
This verification process is a direct implementation of **Mandate 13 (Temple-Grade Compliance)**. A system that cannot verify its own configuration is not Temple-Grade.

*⬡ OMEGA ⬡ MAAT ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_platform_sync ⬡ PHASE-II*
