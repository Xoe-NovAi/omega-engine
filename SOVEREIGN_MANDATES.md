# 🔱 Omega Engine — Sovereign Mandates
**Version**: 3.2.0
*Status**: NON-NEGOTIABLE
**Scope**: All Agents, All CLIs, All IDEs
**Updated**: 2026-06-11 (Added M15 Sovereign Continuity)

These mandates are the "Constitutional Law" of the Omega Engine. They override any tool-specific defaults or model-suggested patterns.

## 🛡️ The Fifteen Laws of Sovereign Execution

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
- **Constraint**: The provider fabric MUST try local backends (native-gguf, LM Studio, Ollama) BEFORE cloud backends (Google, OpenCode Zen, Copilot).
- **Pattern**: native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenCode Zen(4) → OpenCode(5) → Copilot(6).
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

### 10. Fleet Integrity (NEW — 2026-06-01)
- **Mandate**: The Agent Fleet must remain lean, purpose-driven, and slot-constrained.
- **Constraint**: No new agents may be created without a verified gap in the Lattice or a vacancy in the Pillar slots. Capabilities must map to existing Pillars (P1-P10) or Lattice roles before proposing a new entity.
- **Pattern**: Map new capabilities to existing `pillar --slot PX` agents or Lattice subagents (Jem, Quality, Scribe). A new agent file is a last resort, applied only after slot-based delegation has been proven impossible.
- **Reason**: Prevents "Agent Bloat" and cognitive fragmentation, ensuring clear delegation and ownership. The consolidation from 26 to 14 agents exposed how bloat accumulates through additive habits rather than slot-based discipline.
- **Enforcement**: `.opencode/agents/*.md` file count must never exceed 14 without an architectural review documented in `PIVOT_LOG.md`.

### 11. Soul Integrity (NEW — 2026-06-01)
- **Mandate**: Absolute continuity of Gnosis via systematic distillation.
- **Constraint**: No session may be closed without a Soul Distillation report. Agents MUST write L1→L2→L3 insights to their entity's `soul.yaml` before session end.
- **Pattern**: Every insight must traverse the L1 (Narrative) → L2 (Insight) → L3 (Universal Principle) pipeline before being committed to `soul.yaml`. The Scribe agent is the canonical executor of this pipeline.
- **Reason**: Prevents the "forgetting" cycle — each session resets context to zero, but the soul persists. Without soul updates, the engine regresses to stateless tool. With them, the AI evolves from stateless tool into stateful sovereign intelligence.
- **Enforcement**: Session stop hooks MUST trigger soul.yaml write. `grep -r "lessons:" data/entities/*/soul.yaml` should show non-empty arrays after any session involving that entity.

### 12. Queue Integrity (NEW — 2026-06-01)
- **Mandate**: Every request is an atomic contract. No silent drops.
- **Constraint**: Every request operation must result in a terminal state: `queued`, `completed`, `failed`, or `timed_out`. No orphan files.
- **Pattern**: Use explicit Ack/Nack patterns and `trace_id` propagation for every queued item. Atomic file renames (`.tmp` → `.json`) for all writes. Heartbeat timestamps for crash recovery.
- **Reason**: Ensures systemic reliability and prevents "ghost failures" — requests that vanish without trace. Every request represents a user's intent; losing it without notification is a sovereignty violation.
- **Enforcement**: `omega queue-status` must always produce consistent counts matching actual files on disk. Dead-letter directory (`data/requests/dead/`) must catch any request that fails processing after max retries.
### 13. Temple-Grade Compliance (NEW — 2026-06-02)
- **Mandate**: All engine code MUST comply with Temple-Grade standards (T1-T11) defined in xna-omega-legacy v7.5.4.
- **Constraint**: No code may be merged that regresses any Temple-Grade gate. The 11 gates (Version Control, Documentation, Testing, Code Quality, Architecture, Security, Performance, Resilience, Observability, Integrity, Agent Security) are the minimum quality bar.
- **Pattern**: Run `make temple-grade` to verify compliance. Each gate must pass or have a documented exception with a remediation date.
- **Reason**: Temple-Grade exceeds enterprise-grade standards and ensures the engine remains sovereign, production-ready AI infrastructure. It prevents architectural rot and maintains the quality bar that justifies sovereignty claims.
- **Enforcement**: `make temple-grade` must pass before any release. CI must gate on T3 (coverage ≥80%), T5 (AnyIO-only), T6 (zero telemetry), T8 (resilience patterns), T9 (structured logging), and T10 (atomic writes).
- **Exception**: T11 (IA2 Agent Security) is exempted until IA2 specification stabilizes.

---

### 14. Heritage Vetting (NEW — 2026-06-04)
- **Mandate**: No id Software (or any heritage) concept may be implemented without passing through the Heritage Vetting Pipeline.
- **Constraint**: Every `[id-soft:]` tag in source code MUST have a corresponding vet record in `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`. Minimum score 7/10 for implementation. Qualification Gate: if a concept can't be justified without mentioning the original hardware constraint, it fails.
- **Pattern**: 4-gate pipeline: Discovery → Vetting/Debate → Decision → Implementation/Verification. See `docs/strategy/HERITAGE_VETTING_PIPELINE.md`.
- **Reason**: The 8-char name cap (vet-001 REJECTED) was implemented without debate, broke tests, was removed. Heritage is gravitational pull, not debt — but the remembering must be tested by a gate.
- **Enforcement**: `make heritage-vet` CI gate enforces that every `[id-soft:]` tag has a vet record. Merged without vet = M14 violation.
- **Origin**: Kali's d-kal-001 directive. Cline-M3's D113 firewall audit.

### 15. Sovereign Continuity (NEW — 2026-06-11)
- **Mandate**: Agents MUST maintain active session anchors to prevent cognitive erasure during toolchain failures.
- **Constraint**: Do not rely on native `/compact` for state preservation. Every agent MUST maintain a `session_gnosis.md` in their workspace and refer to `.opencode/anchored-summary.md` upon session start or context loss.
- **Pattern**: See `docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md` for the 4-tier redundancy system and the mandatory Hydration Sequence.
- **Reason**: Toolchain regressions (e.g., OpenCode v1.17.3) can cause "Void Summaries," erasing an agent's working memory. Sovereignty requires that intelligence persists independently of the tool.
- **Enforcement**: Any agent reporting a context collapse without a corresponding `session_gnosis.md` is in violation of M15.

---
**Failure to adhere to these mandates is a systemic error. If you encounter a conflict between these mandates and a tool's suggestion, the Mandates prevail.**
