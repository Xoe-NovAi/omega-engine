<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 GitHub Integration Protocol
# ⬡ OMEGA ⬡ KALI ⬡ GNOSIS ⬡ v1.0.0

This document defines the sovereign standards for interacting with GitHub as an extension of the Omega Engine's memory and coordination layer.

## 1. Commit Message Format
All commits must follow the Conventional Commits specification with an added Entity Attribution trailer.

**Format**: `<type>(<scope>): <description>`
**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `ci`, `chore`

**Attribution Trailer**:
Every commit must end with:
`Sovereign-Entity: @<entity_name>`

**Example**:
`feat(oracle): implement local-first routing`
`Sovereign-Entity: @kali`

## 2. Heritage Tag Protocol
When implementing patterns derived from id Software, the `[id-soft:]` tag must be used in the code.
When creating a GitHub Issue for a heritage concept:
- Label: `heritage`
- Title: `Heritage Vet: <Concept Name>`
- Body: Must include the vet record from `HERITAGE_VET_LOG.md`.

## 3. Temple-Grade Checklist
No PR may be merged into `main` without passing the Temple-Grade gates.
The PR description MUST include the following checklist:
- [ ] T1: AP tokens in all file headers
- [ ] T3: Tests passing (`make test`)
- [ ] T4: Linting passed (`make lint`)
- [ ] T5: AnyIO-only architecture
- [ ] T6: Zero external telemetry
- [ ] T10: Atomic writes implemented

## 4. Entity Attribution
All significant architectural changes must be attributed to the entity that designed them.
This is handled via the `github_add_entity_attribution` tool, which creates a linked attribution issue for the commit.

## 5. Branch Naming Conventions
- `feat/<entity>-<feature-name>`
- `fix/<entity>-<bug-id>`
- `docs/<entity>-<doc-name>`

## 6. Account Rotation
To manage API quotas, the engine rotates between multiple GitHub accounts.
- Primary: `xoe-nova-ai` (System/Kali)
- Governance: `arcana-novai` (Ma'at)
Rotation is handled by `github_tools.py` based on the entity performing the action.

## 7. PR Template
The standard PR template is enforced via `.github/pull_request_template.md`. It requires:
1. Summary of changes.
2. Link to the PIVOT decision (if applicable).
3. Temple-Grade checklist.
4. Entity attribution.

## 8. Merge Strategy
- **Squash and Merge**: Preferred for feature branches to keep `main` history clean.
- **Rebase and Merge**: Used for small fixes.
- **Merge Commit**: Only for large architectural milestones.

## 9. PR Review Protocol
- Every PR requires at least one approval from a Pillar Keeper (P1-P10).
- Verity (@verity) must audit all changes for Mandate compliance.

## 10. CI Failure Protocol
If a CI gate fails:
1. The agent responsible is notified via Hivemind.
2. The agent must fix the violation and push a new commit.
3. The PR is blocked from merging until `make temple-grade` returns GREEN.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: GNOSIS | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
