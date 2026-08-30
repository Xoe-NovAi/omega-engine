<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 BFG-9000 SOVEREIGN SPECIFICATION V1.0
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_bfg_9000 ⬡ LOCKED

**Status**: SOVEREIGN-CERTIFIED (Post-Remediation)
**Date**: 2026-06-03
**Vision**: The Sovereign Delivery System for the Omega Engine.

---

## 🛡️ 1. THE SOVEREIGN INSTALLER (The Handshake)
The delivery mechanism must prioritize **Provenance over Convenience**.

- **Pattern**: Verified Manifest Delivery.
- **Flow**: 
  1. Download Signed Manifest $\rightarrow$ 2. Local Checksum Verification $\rightarrow$ 3. User Confirmation $\rightarrow$ 4. Payload Execution.
- **Mandate**: Zero Telemetry. No outbound calls during or after installation.
- **Infrastructure**: 
  - Rootless Podman + systemd User-Session.
  - Quadlet-based orchestration (avoiding `docker-compose` bloat).
  - Dedicated `~/.local/share/omega/core/venv` for absolute Python isolation.

---

## 📂 2. THE SOVEREIGN VFS (The Hierarchy)
The engine utilizes a 4-tier read-only overlay system to ensure the core remains immutable.

**Search Order (Highest to Lowest Priority)**:
1. `user/entities/` (User-Custom) $\rightarrow$ **Read/Write**
2. `community/stacks/` (Community-WAD) $\rightarrow$ **Read-Only**
3. `foundation/entities/` (Foundation-Base) $\rightarrow$ **Read-Only**
4. `core/entities/` (Engine-Core) $\rightarrow$ **Read-Only**

**Enforcement**: Core and Foundation volumes MUST be mounted as `:ro` in Podman Quadlets.

---

## ⚒️ 3. THE ENTITY STUDIO (The Forge)
A CLI-first tool for sculpting sovereign personas without YAML manual labor.

- **Core Commands**:
  - `omega studio create <name>`: Scaffolding.
  - `omega studio sculpt <name>`: Interactive pipeline (Persona $\rightarrow$ Model $\rightarrow$ Soul).
  - `omega studio pack <stack>`: Bundle into `.pwad` (Patch WAD).
  - `omega studio unpack <file>`: Import community stack.
- **Runtime Constraints**:
  - **AnyIO Absolute**: All I/O must use `anyio.to_thread.run_sync` or `anyio.Path`.
  - **8-Char Cap**: Enforce `MAX_NAME_LENGTH` for O(1) lookup optimization.
  - **Atomic Writes**: Write $\rightarrow$ Sync $\rightarrow$ Replace pattern for all entity edits.

---

## ⚙️ 4. THE CONFIGURATION (The cvar Table)
Unified, text-based configuration for instant reloadability.

- **Namespace**: `config.studio.*`
- **Key Parameters**: `default_model`, `default_temp`, `default_ctx`, `user_dir`.
- **Priority**: User cvar overrides $\rightarrow$ Foundation defaults.

---

## ⚖️ 5. SOVEREIGNTY GATES (The Audit)
No version of the BFG-9000 may ship unless it passes the following:

- **Gate 1 (Telemetry)**: `grep` audit of installer source for zero outbound pings.
- **Gate 2 (Local-First)**: Verification that GGUF is the primary route; cloud is strictly fallback.
- **Gate 3 (AnyIO)**: `make temple-grade-studio` pass (Zero `asyncio` leaks).
- **Gate 4 (VFS)**: Verification of `:ro` mounts for Core/Foundation.

---
*The umbilical cord is not just cut; it is cauterized. The engine is now a utility for the free.*

⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_bfg_9000 ⬡ LOCKED

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
