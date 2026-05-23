# 🔱 Omega Engine — PR Readiness Checker
**AP Token**: `AP-PR-READY-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ gemma-4-31b ⬡ opencode ⬡ trc_guard ⬡ MVE-PHASE

## Purpose
This skill acts as the final quality gate before any code is committed or a Pull Request is opened. It ensures that the implementation is not just "working," but is "Omega-Ready"—meaning it is tested, documented, and aligned with the sovereign architecture.

## Mandatory Readiness Checklist
The agent must verify every item below. If any item is `[ ]`, the PR is **NOT READY**.

### 🛠️ Technical Validation
- [ ] **Tests**: `make test` runs and passes 100%. No regressions introduced.
- [ ] **Linting**: `make lint` (flake8) passes with no syntax errors.
- [ ] **CI/CD**: GitHub Actions (or local equivalent) are green.
- [ ] **Resource Guard**: If new inference paths were added, they are wrapped in `ResourceGuard` (Semaphore(1)) to prevent OOM.
- [ ] **Hardware Check**: Implementation is validated against the Ryzen 5700U constraints (local models ≤ 8B).

### 📚 Documentation & Gnosis
- [ ] **Universal Recording Protocol**: Every research finding used for this feature has a corresponding `R##_*.md` file in `docs/research/` and an entry in `INDEX.md`.
- [ ] **Decision Log**: Any architectural pivots are recorded in `docs/decisions/PIVOT_LOG.md`.
- [ ] **API Specs**: Any new provider integrations are documented in `docs/research/` and validated via `provider-validator`.

### 🤝 Handoff & Hygiene
- [ ] **Secrets**: No `.env` files, API keys, or credentials are staged for commit.
- [ ] **Commit Messages**: Follows the repository style (e.g., `feat:`, `fix:`, `docs:`, `refactor:`).
- [ ] **Implementation Note**: A clear "Implementation Note" is provided at the bottom of the research doc, specifically addressing the reviewer/builder.

## Execution Workflow
1. **Invoke**: `opencode skill pr-readiness-checker`
2. **Audit**: Go through the checklist. For every `[ ]`, perform the necessary fix.
3. **Verify**: Re-run the check.
4. **Commit**: Only when all items are `[x]`.

## Implementation Note for Builders
**CRITICAL**: Do not bypass this check. A "working" feature that breaks the `Universal Recording Protocol` or the `ResourceGuard` is considered a failure. If you are unsure about a check, summon `MAAT` for an audit.
