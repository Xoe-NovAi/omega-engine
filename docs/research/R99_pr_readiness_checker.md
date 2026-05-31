# 🔱 Omega Engine — PR Readiness Checker Spec
**AP Token**: `AP-RESEARCH-R99-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ gemma-4-31b ⬡ opencode ⬡ trc_guard ⬡ MVE-PHASE

## Purpose
To define the absolute minimum quality bar for any code change entering the Omega Engine codebase. This specification ensures that every PR is technically sound, documented, and sovereign.

## Scope
This spec covers the technical, documentation, and hygiene checklists required for PR approval.

## Specification: The Readiness Checklist

### 1. Technical Bar
- **Tests**: 100% pass rate on `make test`.
- **Lint**: Zero errors on `make lint`.
- **Resources**: All new inference paths must use `ResourceGuard` to prevent OOM on 14GB RAM.
- **Hardware**: Validated for Ryzen 5700U (Local models ≤ 8B).

### 2. Documentation Bar
- **Universal Recording Protocol**: All research used is recorded in `docs/research/` and indexed.
- **Decision Log**: Architectural changes are recorded in `docs/decisions/PIVOT_LOG.md`.
- **DMS Compliance**: All new docs follow the `omega-doc-architect` standards.

### 3. Hygiene Bar
- **Secrets**: No API keys or `.env` files in the commit.
- **Commits**: Atomic commits with standard prefixes (`feat:`, `fix:`, etc.).
- **Handoff**: A clear "Implementation Note" is provided for the reviewer.

## Implementation Note
The `pr-readiness-checker` skill should be integrated as a pre-commit hook or a mandatory step in the agent's task completion workflow. Any `[ ]` in the checklist blocks the PR.

## References
- `.opencode/skills/pr-readiness-checker/SKILL.md`
- `docs/research/R97_omega_doc_architect.md`
