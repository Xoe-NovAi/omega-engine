# 🔱 Omega Engine — Sovereign Mandates
**Version**: 2.0.0
**Status**: NON-NEGOTIABLE
**Scope**: All Agents, All CLIs, All IDEs
**Updated**: 2026-05-30 (Added Mandates 7 & 8)

These mandates are the "Constitutional Law" of the Omega Engine. They override any tool-specific defaults or model-suggested patterns.

## 🛡️ The Eight Laws of Sovereign Execution

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
- **Mandate**: Complex architectural changes must follow the "Plan → Verify → Execute" loop.
- **Constraint**: No "cowboy coding." Every major edit must be preceded by a plan that is verified against the `PIVOT_LOG.md`.
- **Reason**: Prevents the "Restart Cycle" that plagued previous versions of the engine.

### 5. Gnosis Preservation (L1 → L2 → L3)
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

### 7. Local-First (Non-Negotiable)
- **Mandate**: Local inference is PRIMARY. Cloud is FALLBACK. Always.
- **Constraint**: The provider fabric MUST try local backends (native-gguf, LM Studio, Ollama) BEFORE cloud backends (Google, OpenRouter, Copilot).
- **Pattern**: native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenRouter(4) → OpenCode(5) → Copilot(6).
- **Reason**: The Omega Engine exists to sever Big AI's umbilical cord. If local inference is available, it must be tried first. Cloud is a safety net, not a crutch.
- **Enforcement**: `config/providers.yaml` strategy must be `local_first`. Any change to cloud-first priority is a systemic violation.

### 8. Zero Telemetry
- **Mandate**: No telemetry. Zero. None. Ever.
- **Constraint**: No analytics, no usage tracking, no phone-home, no metrics collection sent to external services. The engine does not report to anyone.
- **Reason**: Sovereign AI means sovereign data. If the engine phones home, it is not sovereign. Period.
- **Exception**: Local observability (traces, events, metrics) stored in `data/` on the user's machine is acceptable. External telemetry is not.

### 9. Error Integrity (NEW — 2026-05-31)
- **Mandate**: All errors MUST be typed, traceable, and testable. No silent swallowing.
- **Constraint**: Never use bare `except:`. Never use bare `except Exception:` without logging and propagating `trace_id`. Every public API boundary MUST catch and convert internal errors to `OmegaError` subtypes.
- **Pattern**: See `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` §2 (Exception Handling Standards).
- **Reason**: The Gemini CLI server deletion and the systemd start-limit-hit failure were both caused by silent error swallowing. Structured error handling is the foundation of debuggability and resilience.
- **Enforcement**: Code review must check each `except` clause. Tests must cover each error path. `pytest.raises(OmegaError)` is the canonical test pattern.
- **Exception**: Health probe functions may catch all exceptions to prevent crash loops, provided they log the error with `logger.warning()`.

---
**Failure to adhere to these mandates is a systemic error. If you encounter a conflict between these mandates and a tool's suggestion, the Mandates prevail.**
