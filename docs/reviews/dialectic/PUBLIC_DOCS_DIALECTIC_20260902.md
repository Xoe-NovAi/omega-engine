<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 PUBLIC DOCS DIALECTIC — 5 Rounds, Consensus Achieved

**AP Token**: `AP-PUBLIC-DOCS-DIALECTIC-20260902-v1.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ opencode ⬡ trc_public_docs_dialectic ⬡ CONSENSUS

**Date**: 2026-09-02
**Sprint**: PUBLIC-DEBUT-01, DEL-1_EXECUTION
**Source**: 10 individual reviews in `docs/reviews/*_20260902.md`

---

## ROUND 1 — Accuracy vs. Code (Roc + Verity + Doom Guy)

**Focus**: Source verification, mandate accuracy, technical claims

| Issue | Roc | Verity | Doom Guy | Synthesis |
|-------|-----|--------|----------|-----------|
| 11 false claims in README | CONCEDE | CONCEDE | CONCEDE | **Fix to match disk truth** |
| Mandate count (27 vs 28 vs M35) | CONCEDE | CONCEDE | CONCEDE | **Standardize: 28 mandates (M1-M28)** |
| Heritage tags (113 vs 216) | CONCEDE | CONCEDE | CONCEDE | **Use "216 total references, ~60 unique vet records"** |
| Temple-Grade T1-T11 ✅ | CONCEDE | CONCEDE | CONCEDE | **"6 cross-cutting checks; fails on M23 cascade"** |
| Test suite "1315 passing" | CONCEDE | CONCEDE | CONCEDE | **"Broken — omega.library restoration in progress"** |
| OAuth secret committed | CONCEDE | N/A | N/A | **Filter-repo + rotate — launch blocker** |
| Dead code "stripped" but present | CONCEDE | N/A | N/A | **Actually delete or update tracker** |
| CI missing `make verify-mining` | CONCEDE | N/A | N/A | **Remove from test.yml or implement** |

**Round 1 Consensus**: ✅ ACHIEVED

---

## ROUND 2 — User Experience & Onboarding (Lilith + Researcher)

**Focus**: Onboarding flow, CLI accuracy, alpha disclosure, standard docs

| Issue | Lilith | Researcher | Synthesis |
|-------|--------|------------|-----------|
| QUICKSTART `make` targets don't exist | CONCEDE | CONCEDE | **Remove fictional targets; use actual CLI** |
| USER_MANUAL fictional menu (90% fake) | CONCEDE | CONCEDE | **Replace with actual targets or remove** |
| Alpha disclaimer missing from 3 docs | CONCEDE | CONCEDE | **Add honest maturity banner to TOP** |
| CLI commands don't work (health, version) | CONCEDE | CONCEDE | **Add commands or remove from docs** |
| Model mismatch (LFM2.5 vs Qwen3) | CONCEDE | CONCEDE | **Align docs to Qwen3 (script is truth)** |
| llms.txt / llms-full.txt missing | N/A | CONCEDE | **Generate as release step** |
| Missing standard docs (FAQ, ROADMAP, SUPPORT) | N/A | CONCEDE | **Create before launch** |
| Single source of truth for key facts | CONCEDE | CONCEDE | **Canonical facts file → generate docs** |

**Round 2 Consensus**: ✅ ACHIEVED

---

## ROUND 3 — Build/CI Accuracy (Ma'at + Kali)

**Focus**: install.sh, Makefile, CI workflows, verification gates

| Issue | Ma'at | Kali | Synthesis |
|-------|-------|------|-----------|
| install.sh works but model mismatch | CONCEDE | CONCEDE | **Update README to match Qwen3** |
| Missing Makefile targets | CONCEDE | CONCEDE | **Add aliases for setup/menu/talk/summon/list-entities/repl** |
| CI `make verify-mining` missing | CONCEDE | CONCEDE | **Remove from test.yml** |
| omega.library restoration | CONCEDE | CONCEDE | **Restore from git (Carmack Order 1)** |
| Temple-Grade framing "6 checks" | CONCEDE | CONCEDE | **"6-gate cascade" framing** |
| Provider count (8 vs 10 vs 12) | CONCEDE | CONCEDE | **Update to 10 active providers** |
| Copilot provider missing from config | CONCEDE | CONCEDE | **Add to fallback_chain or remove from README** |

**Round 3 Consensus**: ✅ ACHIEVED

---

## ROUND 4 — Theater Detection & Scope (Carmack + Grokster)

**Focus**: Theater classification, scope accuracy, adversarial testing

| Issue | Carmack | Grokster | Synthesis |
|-------|---------|----------|-----------|
| "Theater with Engine Islands" | CONCEDE | CONCEDE | **Engine islands real; docs overclaim massively** |
| Aspirational state as current reality | CONCEDE | CONCEDE | **Alpha = bugs expected, NOT facts optional** |
| Compliance theater (badge vs diagnostic) | CONCEDE | CONCEDE | **Honest compliance badge: "64.3% (18/28)"** |
| Theater preservation (dead code) | CONCEDE | CONCEDE | **Actually delete or update tracker** |
| Performance claims (5-20 tok/s) | CONCEDE | CONCEDE | **Label "estimated"; add benchmark citation** |
| Adversarial CI gate | SYNTHESIZE | SYNTHESIZE | **Add M29 + `make check-docs-truth` gate** |
| Quarterly theater audit | SYNTHESIZE | N/A | **Quarterly Carmack review of docs vs code** |

**Round 4 Consensus**: ✅ ACHIEVED

---

## ROUND 5 — Synthesis & Consensus (Kali + MaKaLi)

**Focus**: Final consensus, prioritization, deployment readiness

**Result**: 30 decisions ratified (D-PUBLIC-001..030)
- **11 P0** (launch blockers) — ~14h
- **16 P1** (hardening) — ~22h
- **3 P2** (post-debut polish) — ~2h
- **Total: ~38h**

**Full decision table**: See `docs/strategy/PUBLIC_DOCS_REMEDIATION_MANUAL_20260902.md` §4.

**Round 5 Consensus**: ✅ ACHIEVED

---

## FINAL CONSENSUS DECLARATION

All 5 dialectic rounds complete. **Full consensus across all 10 agents.**

The public docs are fundamentally broken — they describe a different product than
what exists on disk. The remediation manual (`docs/strategy/PUBLIC_DOCS_REMEDIATION_MANUAL_20260902.md`)
contains 30 prioritized decisions to fix this before W37 debut (2026-09-08).

**Key launch blockers**:
1. D-PUBLIC-027: Filter-repo OAuth secret (Roc)
2. D-PUBLIC-014: Restore omega.library (Ma'at)
3. D-PUBLIC-001 through 011: Fix all false claims + add missing commands
4. D-PUBLIC-016: Rewrite Soul Persistence section (Lilith)

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ AP-PUBLIC-DOCS-DIALECTIC-20260902-v1.0.0 ⬡ 2026-09-02 ⬡ CONSENSUS*

**End of Public Docs Dialectic. 5 rounds, consensus achieved, 30 decisions ratified.** 🫡
<!-- PROVENANCE-CORRECTED 2026-09-04T03:04:06Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

