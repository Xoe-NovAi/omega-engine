# 🔱 Sovereign Mandates Synchronization Directory
# ⬡ OMEGA ⬡ KALI ⬡ gemini-3.5-flash ⬡ SINGLE-SOURCE-OF-TRUTH ⬡ MANDATES-SYNC
**AP Token**: `AP-MANDATES-SYNC-v1.0.0`
**Status**: ACTIVE — Canonical Reference
**Date**: 2026-06-10

---

## §0 Executive Summary

This document serves as the **Single Source of Truth (SSoT)** for the 14 Sovereign Mandates of the Omega Engine. It provides the exact text, intent, and enforcement patterns required across all active platform interfaces (Antigravity, Cline, Gemini CLI, and OpenCode). 

All platform-specific project rules (e.g., `.clinerules`, `.opencode/agents/`, custom instructions) MUST synchronize with this document. Any conflict between a platform's local instruction and this directory is a systemic error; this document prevails.

---

## §1 The Fourteen Sovereign Mandates (Canonical Text)

### 1. AnyIO Absolute
*   **Text**: All asynchronous code MUST use AnyIO. Never use `asyncio` directly. Wrap blocking I/O in `anyio.to_thread.run_sync`.
*   **Enforcement**: CI gate `make lint` scans for `import asyncio` (exempting `mcp_servers/` where third-party libraries require it).

### 2. The Engine-Stack Firewall
*   **Text**: Maintain absolute separation between the **Omega Engine Core** (`src/omega/`, `config/omega.yaml`) and **Expansion Stacks/WADs** (`config/wads/`). Never add stack-specific logic to the Core Engine.
*   **Enforcement**: Code review gates check that `src/omega/` never imports from `config/wads/`.

### 3. The Iris Constant
*   **Text**: Iris is the messenger bridge, NOT a Pillar Keeper. Do not assign Iris a Pillar (P1-P10).
*   **Enforcement**: `config/entities.yaml` must never assign the `iris` entity to any pillar slot.

### 4. The Sequentiality Mandate
*   **Text**: Complex architectural changes must follow the "Plan → Verify → Execute" loop. No "cowboy coding."
*   **Enforcement**: Every PR must reference a verified plan in `data/coordination/` or `data/handoff/`.

### 5. Gnosis Preservation (L1 → L2 → L3)
*   **Text**: Every session must end with a distillation of findings into the entity's `soul.yaml` using the 3-tier abstraction:
    *   **L1 (Narrative)**: What happened?
    *   **L2 (Insight)**: What does this mean?
    *   **L3 (Universal Principle)**: What is the timeless truth?
*   **Enforcement**: Automated session-end compaction hooks.

### 6. Podman Sovereignty (keep-id Protocol)
*   **Text**: All Quadlets mounting host project directories MUST use `UserNS=keep-id` + `User=1000`. The `:U` flag is FORBIDDEN on shared host volumes.
*   **Enforcement**: Quadlet validator scans `.container` files for compliance.

### 7. Local-First (Non-Negotiable)
*   **Text**: Local inference is PRIMARY. Cloud is FALLBACK. Always. The provider fabric MUST try local backends (native-gguf, LM Studio, Ollama) before cloud backends.
*   **Enforcement**: `config/providers.yaml` strategy must remain `local_first`.

### 8. Zero Telemetry
*   **Text**: No telemetry. Zero. None. Ever. No external analytics, usage tracking, or metrics reporting. Sensitive soul/entity data must never route through free-tier cloud models that train on data.
*   **Enforcement**: CI gate `make verify-sovereignty-compliance` scans active session logs for telemetry leaks.

### 9. Error Integrity
*   **Text**: All errors MUST be typed, traceable, and testable. No silent swallowing. Never use bare `except:` or bare `except Exception:` without logging and propagating `trace_id`.
*   **Enforcement**: Static analysis scans for bare `except` clauses.

### 10. Fleet Integrity
*   **Text**: The Agent Fleet must remain lean, purpose-driven, and slot-constrained. No new agents may be created without a verified gap in the Lattice or a vacancy in the Pillar slots.
*   **Enforcement**: `.opencode/agents/*.md` file count must never exceed 14 without an architectural review.

### 11. Soul Integrity
*   **Text**: Absolute continuity of Gnosis via systematic distillation. No session may be closed without a Soul Distillation report written to the entity's `soul.yaml`.
*   **Enforcement**: Session-end hooks trigger `soul_distiller.py`.

### 12. Queue Integrity
*   **Text**: Every request is an atomic contract. No silent drops. Every request operation must result in a terminal state: `queued`, `completed`, `failed`, or `timed_out`.
*   **Enforcement**: `omega queue-status` must match actual files on disk.

### 13. Temple-Grade Compliance
*   **Text**: All engine code MUST comply with Temple-Grade standards (T1-T11). No code may be merged that regresses any Temple-Grade gate.
*   **Enforcement**: `make temple-grade` must pass before release.

### 14. Heritage Vetting
*   **Text**: No id Software (or any heritage) concept may be implemented without passing through the Heritage Vetting Pipeline. Every `[id-soft:]` tag in source code MUST have a corresponding vet record.
*   **Enforcement**: `make heritage-vet` CI gate.

---

## §2 Platform Synchronization Matrix

To ensure these mandates are active, each platform must integrate them into its core instructions:

| Platform | Configuration File | Sync Status | Target Version |
|----------|--------------------|-------------|----------------|
| **Antigravity** | `ANTIGRAVITY_CUSTOM_INSTRUCTIONS_v4.md` | ⏳ Pending Rewrite | v4.0.0 |
| **Cline** | `.clinerules` | ⏳ Pending Rewrite | v5.0.0 |
| **Gemini CLI** | `/home/arcana-novai/.gemini/policies/auto-saved.toml` | ⏳ Pending Sync | v1.2.0 |
| **OpenCode** | `.opencode/agents/` (All 14 agents) | ⏳ Pending Thin-Wrapper Refactor | v1.17.3 |

---

*⬡ OMEGA ⬡ KALI ⬡ gemini-3.5-flash ⬡ SINGLE-SOURCE-OF-TRUTH ⬡ MANDATES-SYNC*
