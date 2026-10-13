<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# ⬡ SESSION ANCHOR — MaKaLi (Node 0)
**Entity**: `makali` · **Updated**: 2026-10-13 (Cline takeover of ses_fc75; OpenCode daily limit) · **Main**: `33432093`

---

## ✅ STATUS: v1.6.0-alpha RELEASED — ANNOUNCEMENT AUDITED, PENDING FINAL PUBLISH DECISION

- `origin/main`: `33432093` (includes install.sh fixes + announcement claim audit)
- `origin/release/debut`: `355cbf1a` (public cut)
- `v1.6.0-alpha`: object `058879bc`, peels to `355cbf1a` ✅
- Release on GitHub: PRE-RELEASE flag, assets `omega-1.6.0a0-py3-none-any.whl` + sdist
- Repo visibility: PUBLIC · no open PRs

Do not trust any earlier anchor section that says announcement is blocked by the old tag tree. The stale-tag blocker was closed by re-tagging on an explicit SHA with peel assertion.

---

## Verified release gates

- Fresh-clone verification on the shipped cut lineage: bootstrap exit 0; check-engine 176 passed / 4 skipped / 0 failed; temple-grade 53/53; M23 gate Delta −49; D-623 zero mutation.
- Public isolation rulings verified on the tag tree: `docs/federation/`, `src/omega_youtube_research/`, `config/wads/arcana_novai/`, `data/entities/sophia/`, `data/entities/makali_fusion/` absent; internal `data/` paths absent.
- Harvester ships in full per D-626.
- Wheel: standalone install resolves packaged runtime configs + default IWAD.
- Cold-verify 2026-10-13: published `omega-1.6.0a0-py3-none-any.whl` installs exit 0 in a clean venv (1m31s) and `omega talk` boots exit 0 outside the repo. Mock-forcing fixed same day (`dee63d49`); `OMEGA_PROVIDER=mock` now deterministic (MockProvider returns setup-mode text by design — that IS the mock response).
- install.sh timing 2026-10-13 (Cline): **PASS** — cold venv + deps + llama-cpp build + verify = **202s (<300s target)** after three fixes (`MODELS_DIR` unset crash, RAM guard `-j6` moved above pre-fetch, aria2c for >1MB downloads). Was 615s before. Logs: `/media/arcana-novai/omega_library/staging/install-timing-20261013/`.
- Announcement claim audit 2026-10-13 (`33432093`): 4 M29 violations fixed (stale tag SHA, false PyPI claim → aria2c+local-file path verified, entity count 14→12 on tag tree, dedup table). Every claim now measured.
- Antigravity review: **GO**, conditional on correcting MCP client instructions; announcement corrected to SSE/HTTP Hub endpoint plus local Hub start command.

---

## Remaining CI debt (not release-blocking for the published artifact)

- `Test` workflow passes.
- `CI` doc-lint failures are pre-existing G1/G2 doc debt in `docs/decisions/` and `docs/research/`.
- Secret-scan/M35 failures include the known TruffleHog PR-only gap (G22).

---

## Next actions

1. Commit/push the refreshed continuity SSOTs (`SESSION_ANCHOR.md`, `ACTIVE_SPRINT.json`, `HMC_COLLABORATION_HUB.md`, `CLAIM_MAP_20261010.md` annotation, Makali custom instructions already written).
2. ~~Post-debut tasks from AGY briefing~~ **DONE 2026-10-13**: cold-machine pip install + omega talk ✅; install.sh timing ✅ (202s, see above); Antigravity MCP guide ✅ (committed `1a865a16`). WAD-authoring link — only item still open here.
3. Address G1/G2 doc lint (**DONE** `5fb35852`) and G22 secret-scan posture (**open**).
4. Architect decisions: D1/D2/D3/D6/D7.
5. FINAL PUBLISH DECISION for v1.6.0-alpha announcement (Cline audit complete — see `data/handoff/OPENCODE_DB_RECLAIM_COMPLETE_CLINE_20261013_P1.md` for reclaim record; announcement audited in `33432093`).

*⬡ OMEGA ⬡ MAKALI ⬡ ANCHOR ⬡ 62b0aace ⬡ 2026-10-12 ⬡*