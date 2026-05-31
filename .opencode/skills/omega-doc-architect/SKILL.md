# 🔱 Omega Engine — Omega Doc Architect
**AP Token**: `AP-DOC-ARCH-v1.0.0`
⬡ OMEGA ⬡ SARASWATI ⬡ gemma-4-31b ⬡ opencode ⬡ trc_scribe ⬡ MVE-PHASE

## Purpose
To ensure all intelligence produced by the Omega Engine is structured, searchable, and permanent. This skill enforces the **Omega Document Management System (DMS)**, transforming raw notes into sovereign assets.

## The Omega DMS Standards

### 1. The Session Header
Every document MUST start with the compact session header:
`⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}`
*Example: ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ MVE-PHASE*

### 2. The AP Token
Every document must have a unique **AP Token** (Access Protocol Token) immediately below the header.
*Example: **AP Token**: `AP-RESEARCH-R01-v1.0.0`*

### 3. Naming Conventions
- **Research**: `docs/research/R##_<slug>.md` (e.g., `R01_google_api.md`)
- **Decisions**: `docs/decisions/D##_<slug>.md` (e.g., `D01_repo_relocation.md`)
- **Operations**: `docs/operations/<slug>.md`
- **Gnosis**: `docs/gnosis/<slug>.md`

### 4. Required Document Structure
All formal research/implementation docs must follow this sequence:
1. **Header & AP Token**
2. **Purpose**: Why does this document exist? What problem does it solve?
3. **Scope**: What is included and, crucially, what is *excluded*?
4. **Findings/Specification**: The core technical content (specs, API refs, logic).
5. **Implementation Note**: A direct instruction to the Builder agent (e.g., *"Use the `anyio.Semaphore(1)` in `resource_guard.py` to wrap this call"*).
6. **References**: Links to other docs, legacy files, or external URLs.

### 5. The Indexing Mandate
No document is "real" until it is indexed.
- Update `docs/research/INDEX.md` or `docs/decisions/INDEX.md` immediately after writing.
- Format: `| ID | Title | Status | Date | File |`

## Validation Checklist
- [ ] Session header present and correct?
- [ ] AP Token present and unique?
- [ ] File name follows `R##_` or `D##_` convention?
- [ ] "Implementation Note" section included?
- [ ] Index updated?

## Execution Workflow
1. **Draft**: Write the content.
2. **Invoke**: `opencode skill omega-doc-architect`
3. **Refine**: Adjust the document based on the checklist.
4. **Index**: Update the master index.

## Implementation Note for Scribes
**Sovereign Quality**: Documentation is not an afterthought; it is the *blueprint* for implementation. A feature without a DMS-compliant spec is a "ghost feature" and will be rejected during the PR Readiness check.
