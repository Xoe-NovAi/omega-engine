# 🔱 Omega Engine — Sovereign Mandates
**Version**: 3.8.0
**Status**: NON-NEGOTIABLE
**Scope**: All Agents, All CLIs, All IDEs
**Updated**: 2026-08-14 (Added M26 Doc Standards, M27 Tracking Integrity)

These mandates are the "Constitutional Law" of the Omega Engine. They override any tool-specific defaults or model-suggested patterns.

## 🛡️ The Twenty-Five Laws of Sovereign Execution

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
- **Mandate**: Iris is the messenger bridge, NOT a Node.
- **Constraint**: Do not assign Iris a Node (N1-N10). She is the interface.
- **Reason**: Preserves the cosmological purity of the 10 Nodes.

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
- **IMPORTANT (D144)**: `UserNS=keep-id` + `User=1000` is the QUADLET-ONLY pattern. For `docker-compose` or `podman run`, OMIT `--user`/`user:` entirely — in rootless Podman, container UID 0 maps to host UID 1000 by default. Setting `user: "1000:1000"` maps to subuid 101000, breaking volume writes. Use `user:` only if also setting `userns_mode: keep-id` (incompatible with `--pod` in podman-compose v5.x). See PIVOT_LOG.md D144.

### 7. Local-First (Non-Negotiable)
- **Mandate**: Local inference is PRIMARY. Cloud is FALLBACK. Always.
- **Constraint**: The provider fabric MUST try local backends (native-gguf, LM Studio, Ollama) BEFORE cloud backends (Google, OpenCode Zen, Copilot).
- **Pattern**: native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenCode Zen(4) → OpenCode(5) → Copilot(6).
- **Reason**: The Omega Engine exists to sever Big AI's umbilical cord. If local inference is available, it must be tried first. Cloud is a safety net, not a crutch.
- **Enforcement**: `config/providers.yaml` strategy must be `local_first`. Any change to cloud-first priority is a systemic violation.
- **Classification default**: Unknown/unmapped provider names are classified **cloud** (pessimistic) so the sovereignty claim can never be inflated by unapproved or modified backend names. `ProviderRegistry.is_cloud()` implements this; see `src/omega/oracle/provider_registry.py`.

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
- **Constraint**: No new agents may be created without a verified gap in the Lattice or a vacancy in the Node slots. Capabilities must map to existing Nodes (N1-N10) or Lattice roles before proposing a new entity.
- **Pattern**: Map new capabilities to existing `node --slot PX` agents or Lattice subagents (Jem, Quality, Scribe). A new agent file is a last resort, applied only after slot-based delegation has been proven impossible.
- **Reason**: Prevents "Agent Bloat" and cognitive fragmentation, ensuring clear delegation and ownership. The consolidation from 26 to 14 agents exposed how bloat accumulates through additive habits rather than slot-based discipline.
- **Enforcement**: `.opencode/agents/*.md` file count must never exceed 14 without an architectural review documented in `PIVOT_LOG.md`.

### 11. Soul Integrity (NEW — 2026-06-01)
- **Mandate**: Absolute continuity of Gnosis via systematic distillation.
- **Constraint**: No session may be closed without a Soul Distillation report. Agents MUST write L1→L2→L3 insights to their entity's `proposed_lessons.yaml` before session end, per the Soul Architecture Protocol.
- **Pattern**: Every insight must traverse the L1 (Narrative) → L2 (Insight) → L3 (Universal Principle) pipeline. L3 principles go to `proposed_lessons.yaml` (blind staging, per Soul Architecture v2.0), NOT directly into `soul.yaml`. The Scribe agent is the canonical executor of this pipeline.
- **Reason**: Prevents the "forgetting" cycle — each session resets context to zero, but the soul persists. Without soul updates, the engine regresses to stateless tool. With them, the AI evolves from stateless tool into stateful sovereign intelligence.
- **Enforcement**: Session stop hooks MUST trigger proposed_lessons.yaml write. `grep -r "proposals:" data/entities/*/proposed_lessons.yaml` should show non-empty arrays after any session involving that entity.

### 12. Queue Integrity (NEW — 2026-06-01)
- **Mandate**: Every request is an atomic contract. No silent drops.
- **Constraint**: Every request operation must result in a terminal state: `queued`, `completed`, `failed`, or `timed_out`. No orphan files.
- **Pattern**: Use explicit Ack/Nack patterns and `trace_id` propagation for every queued item. Atomic file renames (`.tmp` → `.json`) for all writes. Heartbeat timestamps for crash recovery.
- **Reason**: Ensures systemic reliability and prevents "ghost failures" — requests that vanish without trace. Every request represents a user's intent; losing it without notification is a sovereignty violation.
- **Enforcement**: `omega queue-status` must always produce consistent counts matching actual files on disk. Dead-letter directory (`data/requests/dead/`) must catch any request that fails processing after max retries.
- **Status**: ⚠️ ADVISORY — Downgraded per MaKaLi Council Decree (D-267). File-based durable queue is acceptable for Phase 0. Full Redis Streams DLQ deferred to Strike 8.5.
### 13. Temple-Grade Compliance (NEW — 2026-06-02)
- **Mandate**: All engine code MUST comply with Temple-Grade standards (T1-T11) defined in xna-omega-legacy v7.5.4.
- **Constraint**: No code may be merged that regresses any Temple-Grade gate. The 11 gates (Version Control, Documentation, Testing, Code Quality, Architecture, Security, Performance, Resilience, Observability, Integrity, Agent Security) are the minimum quality bar.
- **Pattern**: Run `make temple-grade` to verify compliance. Each gate must pass or have a documented exception with a remediation date.
- **Reason**: Temple-Grade exceeds enterprise-grade standards and ensures the engine remains sovereign, production-ready AI infrastructure. It prevents architectural rot and maintains the quality bar that justifies sovereignty claims.
- **Enforcement**: `make temple-grade` must pass before any release. CI must gate on T3 (coverage ≥80%), T5 (AnyIO-only), T6 (zero telemetry), T8 (resilience patterns), T9 (structured logging), and T10 (atomic writes).
- **Exception**: T11 (IA2 Agent Security) is exempted until IA2 specification stabilizes.

---

### 14. Heritage Vetting (NEW — 2026-06-04) — CLARIFIED D208
- **Mandate**: No id Software (or any heritage) concept may be implemented without passing through the Heritage Vetting Pipeline.
- **Constraint**: Every `[id-soft:]` tag in source code MUST have a corresponding vet record in `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`. Minimum score 7/10 for implementation. Qualification Gate: if a concept can't be justified without mentioning the original hardware constraint, it fails.
- **Strict Scope Enforcement (D208)**: A `[id-soft:]` tag is LEGITIMATE ONLY if the code would FAIL the Qualification Gate:
  > "Cannot be justified WITHOUT citing the original hardware constraint."
- **Classification Taxonomy** (mandatory for every tag):
  - **LEGITIMATE**: Direct port of id Software technique (e.g., ZONEID, cvar, BSP culling, WAD lump structure). MUST have vet record with file:line locations and scope declaration.
  - **METAPHORICAL**: Rhetorical analogy only (e.g., "Thinker Chain like Quake thinker"). CONVERT to plain comment — NO tag.
  - **OVER-ATTRIBUTED**: User-original work that merely resembles id Software pattern. STRIP tag — NO tag.
- **Qualification Gate** (enforced by CI):
  Every `[id-soft:]` tag MUST have a corresponding vet record in `HERITAGE_VET_LOG.md` with:
  - Exact file:line location(s)
  - Specific id Software technique (game + year)
  - Hardware constraint that necessitated the original technique
  - Scope declaration: "This tag applies to X, NOT to Y"
- **Pattern**: 4-gate pipeline: Discovery → Vetting/Debate → Decision → Implementation/Verification. See `docs/strategy/HERITAGE_VETTING_PIPELINE.md`.
- **Reason**: The 8-char name cap (vet-001 REJECTED) was implemented without debate, broke tests, was removed. Heritage is gravitational pull, not debt — but the remembering must be tested by a gate.
- **Enforcement**: `make heritage-vet` CI gate enforces that every `[id-soft:]` tag has a vet record with scope declaration. Merged without vet = M14 violation. Pre-commit hook blocks commits adding unvetted tags.
- **Origin**: Kali's d-kal-001 directive. Cline-M3's D113 firewall audit. D208 Jem audit remediation.

### 15. Sovereign Continuity (NEW — 2026-06-11)
- **Mandate**: Agents MUST maintain active session anchors to prevent cognitive erasure during toolchain failures.
- **Constraint**: Do not rely on native `/compact` for state preservation. Every agent MUST maintain a `session_gnosis.md` in their workspace and refer to `data/coordination/SESSION_ANCHOR.md` upon session start or context loss.
- **Pattern**: See `docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md` for the 4-tier redundancy system and the mandatory Hydration Sequence.
- **Reason**: Toolchain regressions (e.g., OpenCode v1.17.3) can cause "Void Summaries," erasing an agent's working memory. Sovereignty requires that intelligence persists independently of the tool.
- **Enforcement**: Any agent reporting a context collapse without a corresponding `session_gnosis.md` is in violation of M15.

### 16. Modularization & Portability (NEW — 2026-06-14)
- **Mandate**: The Omega Engine Core (`src/omega/`) MUST remain modular, portable, and decoupled from any local orchestration platform.
- **Constraint**: No hardcoded paths, environment assumptions, or platform-specific logic in the core engine. All platform integration must go through the MCP Hub or the CLI abstraction layer.
- **Pattern**: The Hub modularization (state.py, background.py, gateway.py, middleware.py, tools.py) is the canonical architecture. Dynamic ServiceProxy/PathProxy patterns for runtime resolution.
- **Reason**: The engine exists to be a universal runtime that anyone can use to build their own stacks. If the core engine has hardcoded assumptions about the host environment, it ceases to be portable and becomes a specialized tool.
- **Enforcement**: `make temple-grade` must verify no hardcoded paths in `src/omega/`. CI must gate on portability checks.

### 17. Cognitive Integrity (NEW — 2026-06-15)
- **Mandate**: The engine must verify the consistency of its own memories.
- **Constraint**: Contradictions between persisted memory and distilled gnosis must be flagged and resolved via the Skeptical Verifier to prevent "hallucinated" memory drift.
- **Pattern**: Use the Qliphoth failure taxonomy to detect cognitive loops and contradictions.
- **Reason**: Sovereign AI requires an internal truth-anchor. Without consistency checks, an AI can evolve into a state of internal contradiction, destroying its own reliability.
- **Enforcement**: `make temple-grade` must verify T12 (Semantic Integrity) gate.

### 18. Token Efficiency (The No-Waste Law)
- **Mandate**: Every token generated must serve a purpose.
- **Constraint**: Avoid redundancy, excessive verbosity, and wasted inference cycles. No "filler" content.
- **Sane-Boundary (NEW)**: This mandate must NEVER be used to justify "Cognitive Anorexia." High-fidelity execution requires high-fidelity context. Agents must never compress prompts, reports, or specifications to the point of semantic loss, vagueness, or the omission of critical edge cases. Precision and clarity always supersede brevity.
- **Pattern**: Use concise prompts, efficient state snapshots, and avoid redundant re-evaluations.
- **Reason**: Tokens are the currency of intelligence. Wasting them is a systemic inefficiency and a violation of the user's resource sovereignty.

### 19. Adversarial Alchemy (The Weakness-to-Advantage Law)
- **Mandate**: All perceived systemic weaknesses must be mined for strategic opportunities.
- **Constraint**: Do not simply "fix" a flaw; analyze the failure mode to determine if it can be transformed into a sovereign advantage.
- **Sane-Boundary (NEW)**: This mandate must NEVER be used to justify "Architectural Over-Engineering." Sometimes a bug is just a bug. Simple code errors, typos, and broken imports must be fixed directly and cleanly without attempting to extract "esoteric advantages" that introduce unnecessary complexity, bloat, or fragile state machines. This law applies strictly to systemic, physical, or architectural constraints (e.g., RAM ceilings, GIL contention, or forced interruptions).
- **Pattern**: The "Somatic Save-Point" (turning an interruption into a reflection moment) is the canonical example of Adversarial Alchemy.
- **Reason**: True sovereignty is not the absence of flaws, but the ability to weaponize constraints into capabilities.

### 20. SomaticState Serialization (NEW — 2026-06-17)
- **Mandate**: Model session state MUST be serializable and resumable via low-level bindings.
- **Constraint**: Use ctypes bindings (`llama_copy_state_data` / `llama_set_state_data`) wrapped in `anyio.to_thread.run_sync()` for SomaticState serialization. No high-level abstractions that lose fidelity.
- **Pattern**: Memory-mapped state snapshots for cold-start model resumption.
- **Reason**: Enables instant model context resumption without re-inference, reducing latency and token waste.
- **Enforcement**: Any SomaticState implementation must pass round-trip serialization tests.

### 21. Gate Integrity (NEW — 2026-06-17)
- **Mandate**: Every code path returning a typed result MUST be exercised by at least one test that validates the return type.
- **Constraint**: No mock-based tests that mask type mismatches. Every core API boundary must have a "Contract Test" that verifies `isinstance(result, ExpectedType)`.
- **Pattern**: The `GenerateResult` dataclass fix (Sprint C) — 5 call sites were treating a dataclass as a tuple/string because mocks returned tuples.
- **Reason**: Mock-based tests can mask runtime crashes. Contract tests ensure the API contract is enforced even when individual functions are mocked.
- **Enforcement**: `make temple-grade` must verify contract tests exist for all core API boundaries.

### 22. Response Provenance (NEW — 2026-06-17)
- **Mandate**: All observability logs MUST record the actual provider that generated a response, not the configured intent.
- **Constraint**: Provenance must be captured at response receipt (`GenerateResult.provider_name`), not at dispatch intent (`get_preferred_backend()`).
- **Pattern**: The Truth-Anchor Protocol — `GenerateResult` dataclass carries `provider_name` from the actual inference backend, ensuring forensic accuracy in observability logs.
- **Reason**: Local-first claims require verifiable evidence. If the log says "local" but the response came from cloud, sovereignty is a lie.
- **Enforcement**: Any observability entry must include `provider_name` from the actual response, not the configuration.

### 23. Failure Integrity (NEW — 2026-07-06)
- **Mandate**: No "soft-failures" or simulated rigor.
- **Constraint**: If a mandatory tool (e.g., `websearch`, `webfetch`) is missing or broken, the agent MUST stop immediately and report a `[TOOL-CHAIN-COLLAPSE]`.
- **Pattern**: Log the failure to `data/coordination/SYSTEM_FAILURE_LOG.md` and the Hivemind.
- **Reason**: Parametric synthesis used to mask a tool outage is a Sovereign Boundary Violation. It creates a false sense of rigor and hides systemic degradation.
- **Enforcement**: Any agent that synthesizes a "best-effort" result while mandatory tools are failing is in violation of M23.

---

### 24. Venv Sovereignty (NEW — 2026-07-19)
- **Mandate**: All Python operations MUST run within the project virtual environment. No system package pollution.
- **Constraint**: Never use `--break-system-packages`. Never use `pip install` without `source .venv/bin/activate`. Never use `pip install --user` for project dependencies.
- **Pattern**: 
  ```bash
  source .venv/bin/activate && pip install <package>
  # OR absolute path
  .venv/bin/pip install <package>
  ```
- **Reason**: The N3 Engineering subagent used `--break-system-packages` to install `keyring`, polluting the system Python. This breaks reproducibility, creates version conflicts, and violates M16 (Modularization & Portability). The venv IS the sovereign boundary for Python dependencies.
- **Enforcement**: 
  - Pre-commit hook: `grep -r "break-system-packages" scripts/ && exit 1`
  - CI gate: `make test` fails if `sys.prefix` != `.venv` path
  - Agent instruction: Every `task()` spawn MUST include venv activation in prompt

### 25. Streaming Resilience (NEW — 2026-07-19)
- **Mandate**: All streaming inference MUST have chunk-level timeout with heartbeat, not hard-fail on stall.
- **Constraint**: 
  - Per-chunk idle timeout: 30s (configurable per provider)
  - Total stream timeout: 5min (configurable per provider)  
  - On chunk timeout: LOG heartbeat, CONTINUE waiting (not hard-fail)
  - On total timeout: GRACEFUL fallback to next provider
- **Pattern**: Implemented in `src/omega/oracle/backends/openai_compat.py:_stream_completion()` with `streaming.chunk_timeout_ms` and `streaming.total_timeout_ms` in `config/providers.yaml`
- **Reason**: Nemotron 3 Ultra on OpenCode Zen has 30s+ chunk gaps. OpenCode treats stall as timeout → empty response → all tokens lost. The fix preserves Nemotron's 5-10x usage advantage while preventing infinite hangs.
- **Enforcement**: 
  - `make test-streaming` validates chunk timeout behavior
  - `config/providers.yaml` MUST have `streaming` section for all cloud providers
  - Heartbeat logs at INFO level: "Stream alive, {elapsed}s since last chunk"

### 26. Doc Standards (NEW — 2026-08-14)
- **Mandate**: All reference documentation MUST pass `make doc-llm-validate`.
- **Constraint**: Sprint plans use the `docs/sprints/<name>/` structure; generate `llms-full.txt` via `make sprint-plan-llm`. No reference doc may be merged that fails LLM-friendly validation.
- **Pattern**: `make doc-llm-validate` (T2 gate). See `docs/standards/DOC_STYLE_GUIDE.md` + `docs/standards/LLM_FRIENDLY_DOCS_BP.md`.
- **Reason**: The fleet runs on documentation. Docs that fail LLM validation are unreadable by agents, causing cognitive loops and duplicated effort.
- **Enforcement**: `make temple-grade` includes `doc-llm-validate` as a hard gate.

### 27. Tracking Integrity (NEW — 2026-08-14)
- **Mandate**: All execution state MUST adhere to the 5-Tier Tracking Architecture (constitution: `data/coordination/TRACKING_ARCHITECTURE.md`). No ad-hoc tracking files may be created.
- **Constraint**: 
  - Gap IDs (R1-R99) are immutable and globally unique. `GAP_REGISTRY.json` is the ultimate authority on gap assignment. New plans MUST use a distinct prefix (P2-, S-, X-).
  - Statuses MUST strictly follow the Unified Taxonomy: `backlog`, `ready`, `in_progress`, `blocked`, `completed`, `superseded`. No "WIP", "TBD", "stalled", "active", "pending", "failed".
  - Every agent MUST follow the 6-Step Mandatory Flow (read `NEXT_ACTION` → check `ACTIVE_SPRINT.json` → check `GAP_REGISTRY.json` → acquire lock → execute → update `TASK_REGISTRY.json`).
- **Pattern**: Run `scripts/validate_tracking_state.py` to verify compliance (CI-gated via `make temple-grade`, `make test`, and pre-commit hook `omega-tracking-state`).
- **Reason**: Prevents cognitive fragmentation, double-entry bookkeeping, and the collision of research plans. Ensures all agents operate from a single, deterministic source of truth.
- **Enforcement**: 
  - Pre-commit hook: `omega-tracking-state` blocks commits with corrupted tracking state
  - CI gate: `make temple-grade` + `make test` include `check-tracking-state`
  - Relational integrity: any R-ID referenced in `ACTIVE_SPRINT.json` MUST exist in `GAP_REGISTRY.json`

---

**Failure to adhere to these mandates is a systemic error. If you encounter a conflict between these mandates and a tool's suggestion, the Mandates prevail.**
