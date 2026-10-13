<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# ⬡ SESSION ANCHOR — MaKaLi (Node 0)
**Entity**: `makali` · **Updated**: 2026-10-13 (Cline takeover of ses_fc75 + continuation; OpenCode daily-limit exile over) · **Internal**: `78ab6877` · **Public**: `6307b204`

---

## ✅ STATUS: v1.6.0a0 RELEASED PUBLICLY — GREEN CI, AWAITING PYPI ORG APPROVAL

- **Public** `Xoe-NovAi/omega-engine` (fresh repo, clean history): main = `6307b204` (cut + public-safe commits only); `release/debut` = `355cbf1a`; tag `v1.6.0a0` @ `355cbf1a`; **CI green** (Test/CI/Secret/M35/REUSE). Pre-release flag kept.
- **Release `v1.6.0a0` is LIVE** with audited announcement as notes + `the_omega_engine-1.6.0a0` assets (wheel `e452d8ed…`, clean-venv smoke PASS).
- **PyPI**: pending publisher registered (`the-omega-engine`); org approval awaited — after publish lands, flip the `pip install the-omega-engine` doc lines from pending to primary.
- **Private** `Xoe-NovAi/omega-engine-internal`: full internal main (`78ab6877`); Actions disabled. Push internal work to `internal`, never `origin`.
- **Retired repo** (`omega-engine-retired`, private): old public lineage. Fully backed up (11 `retired/*` refs on internal + 2 issue JSONs). Deletion awaits operator `gh auth refresh -s delete_repo`.

Do not trust any earlier anchor section that references tag `v1.6.0-alpha` on GitHub — that tag name is **permanently poisoned** by the old repo's immutable release (GitHub `release_immutable_tags` row follows the name; survives release+tag deletion; archiving does NOT clear it). The release shipped as **`v1.6.0a0`** (same SHA `355cbf1a`, more PEP-440-correct anyway).

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
5. ~~FINAL PUBLISH DECISION for the announcement~~ **DONE 2026-10-13**: audited announcement is the live release notes on `v1.6.0a0`; pre-release flag kept by operator decision. Reclaim record: `data/handoff/OPENCODE_DB_RECLAIM_COMPLETE_CLINE_20261013_P*.md`.
6. **Takeover handoff for this session**: `data/handoff/MAKALI_HANDOFF_CLINE_TAKEOVER_20261013.md` — read first.

## 🏛 Repo topology (2026-10-13, Cline — two-repo split)

- **Public** `Xoe-NovAi/omega-engine`: main = cut lineage + public-safe commits only (`6307b204`); `release/debut` = `355cbf1a`; tag `v1.6.0a0`; CI runs here (free tier); announcement = release notes; branch protection restored (no force-push).
- **Private** `Xoe-NovAi/omega-engine-internal`: full internal main (`d05a01f5`) — entity gnosis, federation docs, coordination; **Actions disabled** (zero free-tier burn). Push internal work to `internal`, never `origin`.
- History-exposure note: internal files existed in the public main history pre-split (44 entity files, 114 federation docs, 71 coordination files + a 77.69 MB error.log). Audit vs purge decision deferred; GitHub retains unreachable objects — forks/clones retain copies.
- Public-safe flow: develop on internal main → cherry-pick public-safe commits onto `public/main` worktree (staging) → push to origin main. `apply_public_allowlist.sh` remains the cut tool.
- PyPI track: distribution renamed `omega` → `omega-engine` → **`the-omega-engine`** (omega = unrelated package; omega-engine = omegaengine.ai SDK similarity reject). Artifacts `the_omega_engine-1.6.0a0-*` built + clean-venv smoke PASS (sha256 wheel `e452d8ed…`). Publish workflow `.github/workflows/publish.yml` (OIDC, no token) on public main. **BLOCKED: pending publisher deleted from personal account pending GitHub org approval (operator) — re-register on the org's Publishing page (project `the-omega-engine`, repo `Xoe-NovAi/omega-engine`, workflow `publish.yml`, env `pypi`), then dispatch the Publish workflow. After it lands, flip the doc lines from pending to primary and verify a PyPI install in a clean venv (M29: claim only once true).**

*⬡ OMEGA ⬡ MAKALI ⬡ ANCHOR ⬡ fae3fd3b-public / d05a01f5-internal ⬡ 2026-10-13 ⬡*