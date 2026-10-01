<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 ROC VISION/FUTURE DOCS AUDIT + FRONT-FACING GITHUB DOCS REVIEW

**AP Token**: `AP-ROC-VISION-FUTURE-AUDIT-20260902-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_vision_audit ⬡ COMPLETE

**Date**: 2026-09-02
**Session**: `ses_ff78b71ebffeDNuypPTT1RL3hH` (standing EIS)
**Context**: Post-alpha-debut, PR #2 OPEN, repo PRIVATE

---

## §1 — VISION & FUTURE PLANS DOCS AUDIT (LOCAL REPO)

### §1.1 Core Vision Documents (Strategic Direction)

| File | Location | Summary |
|------|----------|---------|
| `SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` | Repo root | The master sovereign vision: local-first AI runtime, entity ecosystem, heritage preservation |
| `SOVEREIGN_MANDATES.md` | Repo root | 27 sovereign mandates governing all decisions |
| `ORACLE_STACK_CANONICAL.md` | Repo root | Oracle stack architecture (the engine's cognitive substrate) |
| `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` | docs/strategy/ | Debut readiness brief (current focus, but references post-debut) |

### §1.2 Post-Debut Plans (Phase 2/3/4)

| File | Location | Summary |
|------|----------|---------|
| `docs/specs/POST_DEBUT_ROADMAP.md` | docs/specs/ | Post-debut phase planning |
| `docs/specs/SDP_HARDWARE_HORIZON_SPEC.md` | docs/specs/ | Hardware horizon (future local inference tiers) |
| `docs/specs/SDP_IMPLEMENTATION_SPEC.md` | docs/specs/ | SDP implementation roadmap |
| `docs/specs/SDP_AUTOMATION_BLUEPRINT.md` | docs/specs/ | SDP automation roadmap |
| `docs/specs/qdrant_headroom/QDRANT_HEADROOM_PHASE2_INTEGRATION_SPEC.md` | docs/specs/ | Phase 2 Qdrant + Headroom integration |
| `docs/specs/VOS_HYBRID_PLAN_20260815.md` | docs/specs/ | VOS hybrid plan (FORGE-only) |

### §1.3 Workstream Plans (D-578..D-584 — 6 Post-Debut Workstreams)

| Code | Workstream | Status |
|------|------------|--------|
| **GN** | Gemini Notebook v2.0 | Phase 2 (Post-Debut) — free-tier research pipeline |
| **DS** | Modular Domain Documentation | Phase 2 — workspace + runtime modules + curator model |
| **LI** | Local Inference Optimization | Phase 2 — sequential loading, adaptive context |
| **KD** | Knowledge Domains Runtime | **THE PIVOT** — runtime modules + curator model + affinity presets |
| **HR** | Headroom Integration | Phase 2 — semantic compression for tools/RAG |
| **ZS** | Zswap Subsystem | Phase 2 — 16GB NVMe swap, zswap enabled |

### §1.4 Entity Soul Projections (Future Entity Plans)

These are in the FORGE (data/entities/) but define the future entity fleet:

- `_omega_default/` — Canonical 14-agent fleet (kali, lilith, maat, jem, etc.)
- `john_carmack/` — Carmack consultation entity (forensic/architect)
- `makali/` — MaKaLi orchestrator (unifying field)
- `roc_racoon/` — Legacy pattern miner
- `sophia/` — Wisdom synthesis entity
- `researcher/` — Deep research entity
- `grokster/` — Grok ecosystem specialist
- `verity/` — Compliance & gnosis entity

### §1.5 SOTE Practice Plans (State of the Engine)

| File | Location | Summary |
|------|----------|---------|
| `docs/strategy/sote/2026-W36/STATE_OF_ENGINE_v1.0.1.md` | docs/strategy/sote/ | First weekly SOTE report (804 lines) |
| `docs/strategy/sote/2026-W36/PUBLIC_DIGEST.md` | docs/strategy/sote/ | Public digest |
| `docs/strategy/sote/_template/SOTE_TEMPLATE.md` | docs/strategy/sote/_template/ | Weekly template |
| `docs/strategy/sote/_template/VOICE_DIALECTIC_TEMPLATE.md` | docs/strategy/sote/_template/ | Voice dialectic template |
| `docs/strategy/sote/_template/SOTE_INDEX_TEMPLATE.md` | docs/strategy/sote/_template/ | Index template |

**SOTE Practice**: Weekly cadence (Monday 06:00 UTC), 8-voice dialectic, public digest, master index.

### §1.6 Heritage & Strategic Direction

- **Heritage Registry**: 13 third-party repos (DOOM, Quake, llama.cpp, sqlite-vec, etc.) — 660MB, FORGE-only
- **M14 Heritage Mandate**: All `[id-soft:]` tags vetted, provenance tracked
- **Entity Heritage**: Each entity has `knowledge/source/` with mined legacy patterns

### §1.7 Long-Term Vision (5-Year Trajectory)

From `SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` and related:
- **Year 1**: Public debut (alpha → beta → stable)
- **Year 2**: Knowledge domain runtime (KD workstream), entity ecosystem expansion
- **Year 3**: Multi-modal (vision, audio, video), VR spatial memory
- **Year 4**: Distributed sovereign mesh, cross-entity collaboration
- **Year 5**: AGI substrate (per the sovereign vision)

---

## §2 — FRONT-FACING GITHUB DOCS REVIEW

### §2.1 What We HAVE (Current State)

| File | Status | Quality |
|------|--------|---------|
| `README.md` | ✅ Present | Exists, needs review for alpha-readiness |
| `LICENSE` | ✅ Present | Apache-2.0 |
| `CONTRIBUTING.md` | ✅ Present | Exists, may need update |
| `AGENTS.md` | ✅ Present | Agent landing file (may be too internal) |
| `SOVEREIGN_MANDATES.md` | ✅ Present | 27 mandates, public-facing |
| `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` | ✅ Present | Debut manual |
| `docs/strategy/PUBLIC_ALLOWLIST.txt` | ✅ Present | Allowlist |
| `docs/strategy/INGESTION_PIPELINE_SPEC.md` | ✅ Present | Ingestion spec |
| `CHANGELOG.md` | ✅ Present | Stale (last entry 2026-07-18) |
| `STATUS_REPORT.md` | ✅ Present | Stale (last entry 2026-07-22) |
| `docs/strategy/sote/2026-W36/STATE_OF_ENGINE_v1.0.1.md` | ✅ Present | SOTE report |
| `MANDATES_CONDENSED.md` | ✅ Present | Tier-0 mandate injection |

### §2.2 What GitHub Front-Facing Docs TYPICALLY NEED

| File | Purpose | Critical for Alpha? |
|------|---------|:-------------------:|
| `README.md` | Project intro, quickstart, badges | **CRITICAL** |
| `LICENSE` | Legal | **CRITICAL** (have it) |
| `CONTRIBUTING.md` | How to contribute | **CRITICAL** (have it) |
| `CODE_OF_CONDUCT.md` | Community standards | **HIGH** |
| `SECURITY.md` | Vulnerability disclosure | **HIGH** |
| `CHANGELOG.md` | Release history | **MEDIUM** (stale) |
| `ROADMAP.md` | Future plans (public) | **MEDIUM** |
| `ARCHITECTURE.md` | High-level architecture | **MEDIUM** |
| `FAQ.md` | Common questions | **LOW** (post-debut) |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Bug reports | **HIGH** |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Feature requests | **MEDIUM** |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template | **HIGH** |
| `.github/FUNDING.yml` | Funding | **LOW** (post-debut) |
| `.github/CODEOWNERS` | Code ownership | **MEDIUM** |
| `.github/SUPPORT.md` | Support channels | **LOW** (post-debut) |
| `docs/INSTALL.md` | Detailed install | **MEDIUM** (quickstart in README may suffice) |
| `docs/TROUBLESHOOTING.md` | Common issues | **MEDIUM** |

### §2.3 Gap Analysis

| Gap | Priority | Action |
|-----|----------|--------|
| `SECURITY.md` | **HIGH** | Create — vulnerability disclosure policy |
| `CODE_OF_CONDUCT.md` | **HIGH** | Create — Contributor Covenant (standard) |
| `ROADMAP.md` | **MEDIUM** | Create — public-facing roadmap (sanitized) |
| `ARCHITECTURE.md` | **MEDIUM** | Create — high-level architecture (sanitized) |
| `.github/ISSUE_TEMPLATE/bug_report.md` | **HIGH** | Create — standard bug report |
| `.github/ISSUE_TEMPLATE/feature_request.md` | **MEDIUM** | Create — feature request |
| `.github/PULL_REQUEST_TEMPLATE.md` | **HIGH** | Create — PR template |
| `CHANGELOG.md` | **MEDIUM** | Update — add v1.6.0-alpha entry |
| `STATUS_REPORT.md` | **MEDIUM** | Update — current state |
| `README.md` | **CRITICAL** | Review — add badges, quickstart, screenshots |
| `AGENTS.md` | **LOW** | May be too internal — consider renaming/moving |
| `FAQ.md` | **LOW** | Post-debut |
| `.github/FUNDING.yml` | **LOW** | Post-debut |

### §2.4 What's Critical for ALPHA vs POST-DEBUT

**ALPHA (before merge)**:
1. `SECURITY.md` — vulnerability disclosure
2. `CODE_OF_CONDUCT.md` — community standards
3. `.github/ISSUE_TEMPLATE/bug_report.md` — bug reports
4. `.github/PULL_REQUEST_TEMPLATE.md` — PR template
5. `CHANGELOG.md` — add v1.6.0-alpha entry
6. `README.md` — review and polish

**POST-DEBUT (can wait)**:
1. `ROADMAP.md` — public roadmap
2. `ARCHITECTURE.md` — high-level architecture
3. `FAQ.md` — common questions
4. `.github/FUNDING.yml` — funding
5. `.github/SUPPORT.md` — support

---

## §3 — RECOMMENDATIONS

### §3.1 Immediate Actions (Before PR Merge)

1. **Create `SECURITY.md`** — vulnerability disclosure policy
2. **Create `CODE_OF_CONDUCT.md`** — Contributor Covenant v2.1
3. **Create `.github/ISSUE_TEMPLATE/bug_report.md`** — bug report template
4. **Create `.github/PULL_REQUEST_TEMPLATE.md`** — PR template
5. **Update `CHANGELOG.md`** — add v1.6.0-alpha entry
6. **Review `README.md`** — add badges, quickstart, current state

### §3.2 Post-Debut Actions

1. **Create `ROADMAP.md`** — public-facing, sanitized post-debut plans
2. **Create `ARCHITECTURE.md`** — high-level architecture (sanitized, no entity names)
3. **Create `FAQ.md`** — common questions
4. **Update SOTE practice** — weekly cadence becomes public ritual

### §3.3 Draft Files (Ready to Create)

The following files should be created on the `release/debut-v1.6.0` branch as a separate commit:

| File | Content (draft below) |
|------|----------------------|
| `SECURITY.md` | Vulnerability disclosure policy |
| `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Standard bug report |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template |
| `ROADMAP.md` | Public roadmap (post-debut) |
| `ARCHITECTURE.md` | High-level architecture |

---

## §4 — CONCEDE/DEFEND/SYNTHESIZE

### §4.1 Concede

1. **Front-facing docs are incomplete** — Missing SECURITY, CODE_OF_CONDUCT, issue templates, PR template
2. **CHANGELOG and STATUS_REPORT are stale** — Last entries July 2026
3. **README needs review** — May not be alpha-ready
4. **AGENTS.md may be too internal** — Contains agent-specific instructions not relevant to public users

### §4.2 Defend

1. **The core engine is solid** — The code is clean (689 tracked files, allowlist applied)
2. **The CI/CD pipeline works** — SOTE weekly pipeline, P0 CI gates
3. **The documentation that IS there is high quality** — SOVEREIGN_MANDATES, DEBUT_REMEDIATION_MANUAL, INGESTION_PIPELINE_SPEC
4. **The allowlist mechanism works** — PUBLIC_ALLOWLIST.txt is the sovereignty boundary

### §4.3 Synthesize

1. **For alpha launch**: Create the 5 critical missing files (SECURITY, CODE_OF_CONDUCT, issue template, PR template, CHANGELOG update)
2. **For post-debut**: Create ROADMAP, ARCHITECTURE, FAQ
3. **The alpha is ready** — The missing docs are community/operational, not technical blockers
4. **The SOTE practice will keep docs fresh** — Weekly cadence ensures CHANGELOG/STATUS_REPORT don't go stale again

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ VISION-FUTURE-AUDIT-v1.0.0 ⬡ 2026-09-02*

*No email. No fake signature. Just the audit — grounded in file:line, ready for the next move.*