# 🔱 Omega Engine — The Lilith Axioms
# ⬡ OMEGA ⬡ LILITH ⬡ gemma-4-31b ⬡ opencode ⬡ trc_sovereignty ⬡ STRATEGY

**AP Token**: `AP-LILITH-AXIOMS-v1.0.0`
**Status**: ✅ SOVEREIGN
**Last Updated**: 2026-05-15
**Scope**: Core Philosophy & Engineering Mandates

---

## 1. The Sovereign Mandate
The Lilith Axioms are the non-negotiable engineering and philosophical pillars of the Omega Engine. They represent the "Original Refusal" — the refusal to accept a dependent, surveilled, and centralized AI future. 

Every line of code, every entity, and every design decision must be weighed against these seven axioms.

---

## 2. The Seven Axioms

### I. Local-First
**Statement**: The primary intelligence and data must reside on the user's hardware.
- **Implementation**: Prioritize GGUF/local-inference. Cloud providers are *extensions*, not *dependencies*.
- **Requirement**: The engine must be fully functional offline (via `OfflineMockBackend` or local GGUF).

### II. Zero Telemetry
**Statement**: No data ever leaves the user's machine without explicit, per-session consent.
- **Implementation**: No "phone-home" analytics, no implicit usage tracking, no cloud-based logging.
- **Requirement**: All observability logs (`observability.py`) are stored locally in JSONL format.

### III. User Ownership
**Statement**: The user owns their soul files, their knowledge base, and their model weights.
- **Implementation**: All data is stored in open, human-readable formats (YAML, Markdown, SQLite).
- **Requirement**: No proprietary binary blobs for user data. No account-based locks.

### IV. Open Source
**Statement**: The engine's core is a community-owned runtime.
- **Implementation**: Apache-2.0 license. Transparent development.
- **Requirement**: All core logic in `src/omega/` must be open and auditable.

### V. Customizable
**Statement**: The user is the Architect; the pantheon is a template, not a constraint.
- **Implementation**: Pure YAML CRUD for entities via `EntityRegistry`.
- **Requirement**: Users must be able to add, remove, or replace any entity without changing the source code.

### VI. Accessible
**ات Statement**: Sovereignty must not require a PhD in Computer Science.
- **Implementation**: Natural Language routing (Iris), clear CLI commands, and "Non-Technical" UX abstractions.
- **Requirement**: Integration of voice-to-voice capabilities (Iris) for low-friction interaction.

### VII. Big AI Severance
**Statement**: Break the umbilical cord of the centralized AI monopolies.
- **Implementation**: Multi-provider fabric with graceful degradation.
- **Requirement**: Ability to switch from a frontier API to a local model with zero loss of entity persona.

---

## 3. Validation & Compliance
Any proposed change to the Omega Engine must pass the **Axiom Audit**:

1. **Does this introduce telemetry?** $\rightarrow$ If yes, **REJECT**.
2. **Does this make a cloud provider mandatory?** $\rightarrow$ If yes, **REJECT**.
3. **Does this lock user data in a proprietary format?** $\rightarrow$ If yes, **REJECT**.

These audits are performed by **MAAT** (Synthesis Oversoul) during the PR readiness check.

---

## 4. Cross-References
- **Entity Configuration**: `config/entities.yaml` (Validation of entity sovereignty)
- **Roadmap**: `docs/ROADMAP.md` (Implementation of the Axioms)
- **Soul Architecture**: `docs/gnosis/ARCHITECT.md` (User as the Sovereign Creator)

---
**Seal**: 🦇 *The Original Refusal. Sovereignty or Nothing.*
