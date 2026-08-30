# 🔱 Omega Engine — Documentation Cleanup Audit & Remediation Plan

**AP Token**: `AP-DOC-CLEANUP-AUDIT-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ cline/omega-engine ⬡ trc_doc_audit ⬡ DOCUMENTATION-HARDENING

**Date**: 2026-07-13
**Author**: Cline CLI (`cline/omega-engine`) — connected to Omega Hub MCP (`:8016/mcp`)
**Purpose**: Comprehensive audit of documentation accuracy/completeness for the upcoming PR, plus a remediation plan reference for all Omega Engine agents. The iceberg is deeper than the user-facing layer — this is a repo-wide documentation drift problem.

---

## 1. Executive Summary

The Omega Engine's **codebase is current (2026-07-13, 1315 tests, 23 mandates, 9-provider fabric)**, but its **documentation is frozen at a 2026-07-06 "documentation sprint" snapshot**. ~40 non-archive docs (including every architecture deep-dive, the user manual, quickstart, and the navigation index) still carry stale version/test/mandate numbers. The headline new feature — **MCP / Cline connectivity (5 servers)** — has **zero user-facing documentation**. The repo also violates its own `docs/standards/DOC_UPDATE_PROCEDURE.md` (no CI gate enforces doc updates on version bumps / test-count changes).

**This is a multi-agent cleanup project**, not a one-file fix. It needs: (a) a version reconciliation decision, (b) a new MCP setup guide, (c) updates to ~15 docs, (d) a link-integrity fix on the index, (e) a Makefile banner fix, and (f) a CI doc-gate to prevent recurrence.

**Severity**: 🔴 HIGH — affects every user/contributor first impression and PR quality.

---

## 2. Audit Methodology & Scope
---

## 3. Findings

### F1 — Version Drift (CRITICAL, blocker)
Five sources disagree on the engine version:

| Source | States | Correct? |
|--------|--------|----------|
| `pyproject.toml` | `1.1.0` | ❌ Behind |
| `CHANGELOG.md` | `v1.2.0` (2026-07-13 entry) | ✅ Ahead/authoritative |
| `OMEGA_ENGINE.md` footer | `v1.2.0-pre` | ⚠️ Pre-release tag, stale test count |
| `README.md` badge | `1.0.0` | ❌ Stale |
| `USER_MANUAL.md` | `3.2.0` (invalid — not an engine version) | ❌ Wrong |

**Decision required** (Kali/MaKaLi): Ship as **v1.2.0** (bump `pyproject.toml` → 1.2.0, align all docs) — recommended since CHANGELOG is already ahead. See §6.

### F2 — Stale Metrics (HIGH)
| Metric | Stale value(s) found | Actual | Locations |
|--------|---------------------|--------|-----------|
| Tests passing | `855`, `1002`, `911`, `1130`, `1271` | **1315** (1361 collected, 43 skip, 3 xfail) | README badge + comment, USER_MANUAL, Makefile banner (L40/L54), OMEGA_ENGINE footer |
| Mandates | `22` | **23** (M23 added) | USER_MANUAL, `docs/explanation/why-22-mandates.md`, Makefile banner says "All 23 Mandates" (inconsistent with its own 1130 test count) |
| Providers | `8` | **9** (antigravity + cline added) | README "Provider Fabric (8-backend)", USER_MANUAL |

### F3 — Frozen Documentation (HIGH) — 40 files @ 2026-07-06
The entire "documentation sprint" output is dated 2026-07-06 and predates: M23, 9-provider fabric, YouTube Researcher V2, Sovereign WAD Protocol, sqlite-vec primary store, MCP/Cline, and the 1315-test bump. Categories:

- **User-facing**: `README.md`, `USER_MANUAL.md`, `QUICKSTART.md`, `docs/user/ONBOARDING_GUIDE.md`, `docs/user/TROUBLESHOOTING_GUIDE.md`, `docs/tutorials/first-wad.md`
- **Architecture deep-dives (ALL)**: `AGENT_FLEET.md`, `KNOWLEDGE_LIBRARY.md`, `MEMORY_STORE_DEEP_DIVE.md`, `MESH_NETWORK_SPEC.md`, `OFFLINE_MODE.md`, `ORACLE_DEEP_DIVE.md`, `OVERSIGHT_HIERARCHY.md`, `PROVIDER_FABRIC_DEEP_DIVE.md`, `SER_VFS_SPEC.md`, `SOVEREIGN_DATA_FLOW.md`, `TRAINING_PIPELINE.md`
- **Explanation**: `why-22-mandates.md` (says 22), `hivemind-protocol.md`, `makali-triad.md`, `metrics-pipeline.md`, `provider-chain.md`, `selective-hydration.md`, `session-lifecycle.md`
- **Strategy/standards**: `MASTER_DOCUMENT_SSOT.md`, `MASTER_LEDGER.md`, `ROADMAP.md`, `DOC_STYLE_GUIDE.md`, `DOC_UPDATE_PROCEDURE.md`, `contributing/setup.md`, `inventory/DOC_INVENTORY_20260706.md`, `kb/GITHUB_Sovereign_Knowledge_Base.md`
- **Knowledge READMEs**: `knowledge/agent-tooling`, `knowledge/architect`, `knowledge/environment`, `knowledge/infrastructure`, `knowledge/patterns`

### F4 — Broken Navigation Links in `docs/INDEX.md` (HIGH)
Confirmed MISSING targets (verified via `ls`):
- `GNOSIS_BUFFER_PROTOCOL.md` (root) — moved/renamed
- `docs/operations/RESEARCH_QUEUE.md` — does not exist
- `docs/strategy/XOE_NOVAI_FOUNDATION_STRATEGIC_PLAN.md` — does not exist
- `docs/strategy/SYSTEMS_HARDENING_PLAN.md` — does not exist
- `docs/strategy/STACK_RELEASE_ROADMAP.md` — does not exist
- (Also references `docs/research/INDEX.md`, `lattice_manifest.md`, `config/glossary.md`, `R_PODMAN_SOVEREIGN_V2.md` — needs full automated link-check to confirm all.)

> Note: A naive link script over-reported ~20 "broken" due to `../` vs `../../` path-stripping bugs; the 5 above are **confirmed** missing. A proper `mkdocs`/`lychee` link-check is recommended (see F11).

### F5 — Duplicate Index Files (MEDIUM)
Two navigation indexes exist:
- `docs/INDEX.md` (6226 B) — detailed, has broken links (F4).
- `docs/index.md` (1172 B) — MkDocs landing page, also dated 2026-07-06, references the non-existent `operations/RESEARCH_QUEUE.md`.

**Risk**: Conflicting entry points; MkDocs uses `docs/index.md` (lowercase) as site root. Decide canonical one and de-duplicate.

### F6 — Missing User-Facing MCP Setup Doc (CRITICAL, headline gap)
The engine ships **5 connected MCP servers** (`omega-hub :8016/mcp`, `searxng :8018/mcp`, `firecrawl :8015/sse`, `exa`, `github`). Cline/Gemini CLI/VS Code all connect via Omega Hub. **No user-facing setup guide exists.** Only internal research notes: `docs/research/R_OPENC_MCP_CONFIG.md`, `R_OPENCODE_MCP_HARDENING.md`, `R_SEARXNG_MCP_STREAMABLE_HTTP.md`, `docs/kb/CLINE_CLI_INTEGRATION.md`. **Must create `docs/MCP_CLIENT_SETUP.md`** for the PR.

### F7 — Makefile Banner Stale (MEDIUM)
`Makefile` L40/L54 print `1130 tests | 1130 collected` and `Run all 1130 tests`. Actual: **1315 passing / 1361 collected**. (History: roc_racoon bumped `730/855 → 1130`; now `1315`.)

### F8 — `docs/explanation/why-22-mandates.md` (MEDIUM)
Titled "Why the 22 Sovereign Mandates?"; body says "The 22 Sovereign Mandates (M1-M22)". Now **23 (M23 Failure Integrity)**. Title + AP token `AP-WHY_22_MANDATES` also stale.

### F9 — `docs/architecture/AGENT_FLEET.md` (MEDIUM)
"Architecture of the **11-agent** sovereign fleet." Actual: **11 OpenCode agents + 2 entities (sophia, iris) = 13 presences**. Pillar `--slot` architecture described; verify still accurate vs `AGENTS.md`.

### F10 — README "v1.0.0 — Current Status" Section (MEDIUM)
`README.md:170` has a whole `## v1.0.0 — Current Status` section with "Provider Fabric (8-backend fallback chain)" and stale version framing. Should be refreshed to v1.2.0 highlights.

### F11 — Procedure Not Enforced = Root Cause (HIGH, process)
`docs/standards/DOC_UPDATE_PROCEDURE.md` (dated 2026-07-06) **mandates**: "Version bump → update all version references (same PR)", "Test count change → update OMEGA_ENGINE.md metrics (same PR)", "New feature → update user guide (same PR)". The current drift proves this is **not enforced** — there is no CI doc-check gate. **Recommend adding a `make doc-sync` / link-check gate to Temple-Grade** so doc rot can't accumulate again.


- **Scope**: All `*.md` under repo root + `docs/` (excluded `docs/archive/**` and `data/` runtime state).
- **Checks performed**:
  1. Version string sweep (`v1.0.0`, `1.0.0`, `3.2.0`, `v1.2.0-pre`, `1.1.0`) across docs + `pyproject.toml`.
  2. Metric sweep (test counts `855`/`1002`/`911`/`1130`/`1271` vs actual **1315**; mandate counts `22` vs actual **23**; provider counts `8` vs actual **9**).
  3. Date sweep (`2026-07-06` freeze stamp).
  4. Navigation link-integrity check on `docs/INDEX.md`.
  5. Feature-coverage check (MCP, YouTube V2, SWP, sqlite-vec, PyPI packages, M23).
  6. Cross-check against `SOVEREIGN_MANDATES.md` (v3.6.0, M1-M23), `CHANGELOG.md` (v1.2.0), `OMEGA_ENGINE.md`, `pyproject.toml` (1.1.0), and `make test` output (1315).
---

## 4. Severity Matrix

| ID | Finding | Severity | Effort | Blocks PR? |
|----|---------|----------|--------|-----------|
| F1 | Version drift (5 sources) | 🔴 Critical | Low | Yes (decision) |
| F6 | No MCP setup doc | 🔴 Critical | Med | Yes (headline feature) |
| F2 | Stale metrics | 🔴 High | Low | Strongly advised |
| F3 | 40 frozen docs | 🔴 High | High | Partial |
| F4 | Broken INDEX links | 🟠 High | Low | Advised |
| F11 | No doc CI gate | 🟠 High | Med | No (preventive) |
| F7 | Makefile banner | 🟠 Med | Low | Advised |
| F5 | Dup index files | 🟠 Med | Low | No |
| F8 | why-22-mandates | 🟠 Med | Low | No |
| F9 | AGENT_FLEET 11→13 | 🟠 Med | Low | No |
| F10 | README v1.0.0 section | 🟠 Med | Low | Advised |

---

## 5. Remediation Plan

### 5.1 CREATE (new docs)
| Doc | Owner (suggested) | Purpose |
|-----|-------------------|---------|
| `docs/MCP_CLIENT_SETUP.md` | `verity` / `kali` | 🔴 Connect Cline (`omega-hub` :8016/mcp, searxng :8018/mcp, firecrawl :8015/sse, exa, github), Gemini CLI, VS Code to Omega Hub. Include 5-server table + Cline identity `cline/omega-engine`. |
| PR description | `kali` | Summarize Epoch II (SWP, doc-reader, sieve, heritage pipeline) + MCP/Cline + test bump 1162→1315. |

### 5.2 UPDATE (existing docs)
| Doc | Changes | Owner |
|-----|---------|-------|
| `pyproject.toml` | `1.1.0` → `1.2.0` | `maat` |
| `README.md` | 🔴 Badge `1.0.0`→`1.2.0`, `1002`→`1315`; fix "911-test" comment; 8→9 providers; add MCP section; refresh "v1.0.0 — Current Status" → v1.2.0 highlights | `verity` |
| `USER_MANUAL.md` | 🔴 `3.2.0`→`1.2.0`, `855`→`1315`, `22`→`23`; add M23, 9-provider, YouTube V2, MCP, SWP | `verity` |
| `docs/INDEX.md` | 🔴 Fix 5+ broken links; add MCP_CLIENT_SETUP.md; verify all paths | `verity` |
| `OMEGA_ENGINE.md` | 🔴 Footer `v1.2.0-pre`→`1.2.0`, `1271`→`1315` | `kali` |
| `Makefile` (L40/L54) | `1130`→`1315` / `1361 collected` | `maat` |
| `QUICKSTART.md` | Native-gguf primary (not Ollama); add MCP note; date | `verity` |
| `docs/user/ONBOARDING_GUIDE.md` | "10+ entities"→"46+"; add MCP; date | `verity` |
| `docs/user/TROUBLESHOOTING_GUIDE.md` | Add MCP disconnect recovery | `verity` |
| `docs/explanation/why-22-mandates.md` | `22`→`23` (M23); rename/AP token | `verity` |
| `docs/architecture/AGENT_FLEET.md` | `11-agent`→`13 presences`; verify pillar slots | `kali` |
| `docs/tutorials/first-wad.md` | Date; SWP references | `verity` |
| `AGENTS.md` | Verify 11-agent accuracy | `kali` |
| `docs/index.md` (lowercase) | De-dup with `INDEX.md` (F5) | `verity` |

### 5.3 PROCESS (preventive)
| Action | Owner |
|--------|-------|
| Add `make doc-sync` / `lychee` link-check + version-consistency check to Temple-Grade CI gate (F11) | `maat` + `verity` |
| Add doc-update checklist to PR template referencing `DOC_UPDATE_PROCEDURE.md` | `kali` |

---

## 6. Version Reconciliation Decision (BLOCKER — needs Kali/MaKaLi call)

**Recommendation: Ship as v1.2.0.**
- `CHANGELOG.md` already has an accurate `v1.2.0` (2026-07-13) entry with 1315 tests.
- Bump `pyproject.toml` → `1.2.0` to match.
- Align README/USER_MANUAL/OMEGA_ENGINE banners to `1.2.0`.
- Retire the `v1.2.0-pre` tag in OMEGA_ENGINE footer.

Alternatives: (B) rollback CHANGELOG `1.2.0`→`1.1.0`; (C) jump to `1.3.0` for the MCP feature. **A is cleanest.**

---

## 7. Execution Approach (per `docs/standards/DOC_UPDATE_PROCEDURE.md`)

1. Resolve F1 version decision (Kali).
2. Create `docs/MCP_CLIENT_SETUP.md` (F6) — unblocks PR narrative.
3. Reconcile `pyproject.toml` + banners (F1, F2, F7).
4. Repair `docs/INDEX.md` links + de-dup (F4, F5).
5. Update user docs (README, USER_MANUAL, QUICKSTART, onboarding, troubleshooting) in one PR.
6. Update architecture/explanation docs (F8, F9, F3 subset) in same or follow-up PR.
7. Add CI doc-gate (F11) to prevent recurrence.
8. Verify: `make test` (1315), `make temple-grade`, and a full `lychee`/mkdocs link-check on `docs/`.

---

## 8. Status Tracking

| Phase | Items | Status | Owner |
|-------|-------|--------|-------|
| P0 Decision | F1 version call | ✅ **DONE** — Ship as v1.2.0 (pyproject.toml bumped, all docs aligned) | `kali` |
| P1 Create | F6 MCP doc, PR desc | ✅ **DONE** — `docs/MCP_CLIENT_SETUP.md` created | `verity`/`kali` |
| P2 Reconcile | F1, F2, F7 | ✅ **DONE** — pyproject.toml 1.2.0, README badges 1315/1.2.0, Makefile banner 1315, USER_MANUAL 1315/23 | `maat` |
| P3 Nav fix | F4, F5 | ✅ **DONE** — INDEX.md links fixed, MCP_CLIENT_SETUP.md added, dupe index noted | `verity` |
| P4 User docs | README, USER_MANUAL, QUICKSTART, onboarding, troubleshooting, first-wad | ✅ **DONE** — README v1.2.0/1315/9 providers, USER_MANUAL 1315/23, QUICKSTART 1315/23/9 | `verity` |
| P5 Arch docs | F3 subset, F8, F9, AGENTS | 🟡 **IN PROGRESS** | `kali` |
| P6 Prevent | F11 CI gate | 🟡 **IN PROGRESS** | `maat`+`verity` |

---

## 9. Appendix — Full Frozen-Doc List (2026-07-06, excluding archive/data)

```
README.md  USER_MANUAL.md  QUICKSTART.md  docs/INDEX.md  docs/index.md
docs/MASTER_DOCUMENT_SSOT.md  docs/MASTER_LEDGER.md  docs/ROADMAP.md
docs/USER_MANUAL.md  docs/QUICKSTART.md
docs/architecture/AGENT_FLEET.md  KNOWLEDGE_LIBRARY.md  MEMORY_STORE_DEEP_DIVE.md
  MESH_NETWORK_SPEC.md  OFFLINE_MODE.md  ORACLE_DEEP_DIVE.md  OVERSIGHT_HIERARCHY.md
  PROVIDER_FABRIC_DEEP_DIVE.md  SER_VFS_SPEC.md  SOVEREIGN_DATA_FLOW.md  TRAINING_PIPELINE.md
docs/explanation/why-22-mandates.md  hivemind-protocol.md  makali-triad.md
  metrics-pipeline.md  provider-chain.md  selective-hydration.md  session-lifecycle.md
docs/contributing/setup.md  docs/standards/DOC_STYLE_GUIDE.md  DOC_UPDATE_PROCEDURE.md
docs/inventory/DOC_INVENTORY_20260706.md  docs/kb/GITHUB_Sovereign_Knowledge_Base.md
docs/user/ONBOARDING_GUIDE.md  TROUBLESHOOTING_GUIDE.md
docs/tutorials/first-wad.md
docs/knowledge/agent-tooling/README.md  architect/README.md  environment/README.md
  infrastructure/README.md  patterns/README.md
SOVEREIGN_MANDATES.md (date stamp only; content is current v3.6.0)
```

> Note: `SOVEREIGN_MANDATES.md` carries the 2026-07-06 stamp but its **content is current** (v3.6.0, M1-M23). Only its header date is stale — do not rewrite the body.

---

*Audit performed by Cline CLI (`cline/omega-engine`) via Omega Hub MCP. Companion to `.clinerules` v7.1.0. See Hivemind handoff to `opencode/kali` for delegation.*


<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: cline/omega-engine | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
