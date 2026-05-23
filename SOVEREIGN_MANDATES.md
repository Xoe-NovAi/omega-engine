# 🔱 Omega Engine — Sovereign Mandates
**Version**: 1.0.0
**Status**: NON-NEGOTIABLE
**Scope**: All Agents, All CLIs, All IDEs

These mandates are the "Constitutional Law" of the Omega Engine. They override any tool-specific defaults or model-suggested patterns.

## 🛡️ The Six Pillars of Sovereign Execution

### 1. AnyIO Absolute
- **Mandate**: All asynchronous code MUST use AnyIO. 
- **Constraint**: Never use `asyncio` directly. 
- **Pattern**: Wrap blocking I/O in `anyio.to_thread.run_sync`.
- **Reason**: Ensures runtime portability and prevents event-loop collisions across the Provider Fabric.

### 2. The Engine-Stack Firewall
- **Mandate**: Maintain absolute separation between the **Omega Engine Core** and **Expansion Stacks (WADs)**.
- **Core**: `src/omega/`, `config/omega.yaml`, `opencode.json`. (The universal runtime).
- **Stacks**: `config/wads/<stack_name>/`. (The specific implementation).
- **Constraint**: Never add stack-specific logic (e.g., a specific entity's trait) to the Core Engine.
- **Reason**: Prevents architectural drift and ensures the engine remains a universal runtime.

### 3. The Iris Constant
- **Mandate**: Iris is the messenger bridge, NOT a Pillar Keeper.
- **Constraint**: Do not assign Iris a Pillar (P1-P10). She is the interface.
- **Reason**: Preserves the cosmological purity of the 10 Pillar Keepers.

### 4. The Sequentiality Mandate
- **Mandate**: Complex architectural changes must follow the "Plan $\rightarrow$ Verify $\rightarrow$ Execute" loop.
- **Constraint**: No "cowboy coding." Every major edit must be preceded by a plan that is verified against the `PIVOT_LOG.md`.
- **Reason**: Prevents the "Restart Cycle" that plagued previous versions of the engine.

### 5. Gnosis Preservation (L1 $\rightarrow$ L2 $\rightarrow$ L3)
- **Mandate**: No intelligence is discarded.
- **Constraint**: Every session must end with a distillation of findings into the entity's `soul.yaml` using the 3-tier abstraction:
    - **L1 (Narrative)**: What happened?
    - **L2 (Insight)**: What does this mean?
    - **L3 (Universal Principle)**: What is the timeless truth?
- **Reason**: Transforms stateless agent interactions into a stateful, evolving sovereign intelligence.

### 6. Podman Sovereignty (keep-id Protocol)
- **Mandate**: All Quadlets that mount host project directories MUST use `UserNS=keep-id` + `User=1000`. The `:U` flag is FORBIDDEN on shared host volumes.
- **Constraint**: Never use `:U` on volume mounts that the host user needs to access. Never use `:Z` or `:z` — they are SELinux flags, and Ubuntu uses AppArmor.
- **Pattern**: See `docs/research/R_PODMAN_SOVEREIGN_V2.md` for the verified Quadlet pattern.
- **Reason**: The `:U` flag destructively chowns host directories to UID 101000, locking the host user out. `UserNS=keep-id` maps host UID 1000 directly into the container — no chown needed.

---
**Failure to adhere to these mandates is a systemic error. If you encounter a conflict between these mandates and a tool's suggestion, the Mandates prevail.**
