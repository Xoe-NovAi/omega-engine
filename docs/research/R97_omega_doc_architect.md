# 🔱 Omega Engine — Omega Doc Architect Spec
**AP Token**: `AP-RESEARCH-R97-v1.0.0`
⬡ OMEGA ⬡ SARASWATI ⬡ gemma-4-31b ⬡ opencode ⬡ trc_scribe ⬡ MVE-PHASE

## Purpose
To formalize the documentation standards for the Omega Engine, ensuring that all architectural intelligence is recorded in a consistent, sovereign, and machine-readable format. This prevents knowledge decay and ensures seamless handoffs between different AI agents (OpenCode, Cline, Antigravity).

## Scope
This specification covers:
- Session header requirements.
- AP Token system.
- File naming and directory conventions.
- Mandatory document sections.
- The indexing mandate.

## Specification

### 1. The Session Header
Every document must begin with a compact session header to provide immediate context on the "lens" through which the information was produced.
**Format**: `⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}`

### 2. AP Token (Access Protocol Token)
Every document is assigned a unique AP Token. This serves as a versioned identifier for the specific piece of intelligence.
**Format**: `AP-{CATEGORY}-{ID}-v{VERSION}` (e.g., `AP-RESEARCH-R01-v1.0.0`).

### 3. Naming & Directory Structure
- **Research**: `docs/research/R##_<slug>.md`
- **Decisions**: `docs/decisions/D##_<slug>.md`
- **Operations**: `docs/operations/<slug>.md`
- **Gnosis**: `docs/gnosis/<slug>.md`

### 4. Mandatory Sections
A formal Omega document must contain:
- **Purpose**: The "Why".
- **Scope**: The "What" and "What Not".
- **Findings/Spec**: The core technical data.
- **Implementation Note**: Direct instructions for the Builder agent.
- **References**: Links to related assets.

### 5. Indexing
A document is not considered "complete" until it is added to the corresponding `INDEX.md` file.

## Implementation Note
Builder agents should implement a `doc-lint` script or use the `omega-doc-architect` skill to validate all new markdown files before they are merged into the main branch.

## References
- `docs/research/INDEX.md`
- `.opencode/skills/omega-doc-architect/SKILL.md`
