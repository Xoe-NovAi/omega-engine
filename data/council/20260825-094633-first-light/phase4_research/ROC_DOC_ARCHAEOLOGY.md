<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🦝 ROC_DOC_ARCHAEOLOGY — Doc-Organization Evolution Era 0→6
**AP Token**: `AP-ROC-DOC-ARCH-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode/x-preview-f-free ⬡ trc_first_light_c1 ⬡ Stage-4 SPECIALIST
**Session**: 20260825-094633-first-light · Feeds Council 2 (spec drafting)
**Mode**: RECON ONLY. No mutations beyond this file. All conclusions trace to cited paths.

---

## §0 Method & Corpus

Mined physical legacy partitions (not parametric synthesis — M23):

| Era | Corpus | Physical Path |
|-----|--------|---------------|
| 1–2 | ANAi strategy + docs-backup | `/home/arcana-novai/Documents/docs-backup/docs/`, `internal_docs/01-strategic-planning/` |
| 2 | XNAi consolidated (foundation-legacy) | `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/docs/` |
| 4 | omega-stack v5.0 (Old-Stacks dump) | `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/` (`memory_bank/`, `docs/`) |
| 6 | Omega Engine current + git history | `docs/`, `git log --follow -- docs/strategy/STRATEGY_CORPUS_MAP.md` (776 commits; corpus map born in `e899ae2a` "147 stale docs archived") |

Era 0 (tarot genesis) and Era 3 (LM Studio configs) left no formal doc-organization artifacts — chat exports and config snapshots only. That absence is itself a finding: **organization patterns only appear once multi-agent sessions began (Era 4+)**.

---

## §1 Pattern Table (name / era / mechanism / death cause / recurrence guard)

| # | Pattern Name | Era (evidence date) | Mechanism | Death Cause | Recurrence Guard |
|---|--------------|--------------------|-----------|-------------|------------------|
| P1 | **Doc Sediment (flat-root accumulation)** | Era 2 — `foundation-legacy/.../docs/` root had **110+ md files**, `*_dup.md` duplicates, TWO parallel archive dirs (`archive/` + `archived/`) per `docs/design/organization-plan.md` (2026-01-09) | Every session wrote a new file to docs root; nothing ever moved or deleted; duplication tolerated | No intake discipline + no validator. Growth was passive; cleanup required a dedicated human-scale audit that only happened when bloat broke discovery | Hard cap on top-level entries, enforced by CI (count check). NOTE: current `docs/` already has **62 top-level entries** including synonyms (`archive` AND `archives`, `review` AND `reviews`, `ops` AND `operations`, `reference`/`kb`/`knowledge`, stray `test_file.md`) — sediment is re-forming NOW |
| P2 | **Reorg Churn (big-bang plans, serial incompleteness)** | Era 2 — `docs/design/{organization-plan,organization-summary,final-organization-summary,implementation-files-organization-complete}.md`; Era 1/2 — `docs-backup/internal_docs/01-strategic-planning/PHASE-ORGANIZATION-{PLAN,IMPLEMENTATION,MKDOCS-INTEGRATION,DIATACTICS-ENHANCED}.md` (2026-02-17) | A planning session declares a full reorg; writes plan + summary + "complete" marker; next session finds it half-done and writes ANOTHER plan | Single-owner, single-session scope. No enforcement mechanism survived the reorganizer's context. Three separate "organization-complete" markers exist for the SAME tree — completion was declared, not verified | Reorg specs must ship WITH their validator on day one (plan that can't be machine-checked = plan that dies). Ban "complete" status words without a passing check command attached |
| P3 | **Diátaxis-by-Prefix (numbered trees)** | Era 1/5 — `docs-backup/docs/`: `01-start, 02-tutorials, 03-how-to-guides, 03-infrastructure-ops, 03-reference, 04-explanation, 04-phase-4, 05-research, 06-development-log` (+ `_meta/`, `index.json`, `search_index.json`) | Encode read-order/category in directory numeric prefixes (Diátaxis-inspired); mkdocs integration planned alongside | Prefix collisions from insert-without-renumber (TWO `03-`, TWO `04-`). Numbers encode an ordering that doesn't survive organic growth; agents keyed on exact prefixes broke silently. Category taxonomy ALSO drifted (phase-4 mixed into explanation tier) | If prefixing at all: collision must be a CI error, not a cosmetic issue. Better: category dirs WITHOUT order numbers (current `docs/standards/`, `docs/research/` pattern) |
| P4 | **Hand-Curated Master Index SSOT** | Era 4 — `START_HERE.md` + `AI_ASSISTANT_GUIDE.md` + `STACK_STATUS.md` trio (Old-Stacks root); Era 6 v1 — `docs/archive/MASTER_DOCUMENT_SSOT_STALE.md` (2026-06-12, "first consolidated master index", 196+ docs mapped) | One omnibus file maps topic→document; humans/agents trust it as entry point | Manual curation + zero staleness detection. `docs/DOC_CLEANUP_AUDIT.md` (2026-07-13, F1–F3): five sources disagreed on engine VERSION, ~40 docs frozen at one sprint snapshot, index itself stale — the SSOT lied while claiming ✅ LIVE. Killed by UO-4 DOC_SANITY (67 files archived, superseded by routing map) | Every index row must be machine-verifiable (path exists + status field checked by script). Current survivor keeps this property only partially — `DOC_SSOT_MAP_20260807.md` rows are path-checked but status text ("v3.7.0, M1-M25" — mandates now at v3.8.0/M27) is ALREADY drifting again |
| P5 | **Per-Agent Memory Bank (Cline-convention context files)** | Era 4 — `Old-Stacks/Xoe-NovAi/memory_bank/`: `activeContext.md`, `productContext.md`, `techContext.md`, `progress.md`, `teamProtocols.md`, per-agent files (`gemini.md`, `grok.md`, `cline.md`) | Each AI assistant maintained its own structured context dir mirroring project state | Duplicated engine state outside any SSOT; no atomicity; per-agent copies diverged; unreferenced by later eras. Functionally replaced by soul.yaml/proposed_lessons (M11) + `data/coordination/SESSION_ANCHOR.md` (M15) | Never let an agent-owned doc duplicate a tracked-system concern. Agent state lives in entity workspaces; repo truth lives in tracked files with validators |
| P6 | **Junk-Drawer Archive** | Era 4 — `docs/archive/{duplicates,old-versions,historical,sessions,code-review-sessions}/` (unlabeled grab-bags) | Archive = "move it somewhere so root is clean"; no disposition, no date, no reason | Archives became unsearchable second landfill — the bloat moved, not shrank. Discovery required archaeology (literally this assignment) | Archive WITH metadata: dated subdir (`docs/archive/strategy/2026-07-21/` — current pattern ✓), `_STALE`/`_SUPERSEDED` filename suffixes (`MASTER_DOCUMENT_SSOT_STALE.md` ✓), and a routing row pointing old-path→new-path (`DOC_SSOT_MAP` "Archived Path" column ✓) |
| P7 | **Layered SSOT Hierarchy + Routing Map (SURVIVOR)** | Era 6 — precedence chain Mandates → execution SSOT (`DEBUT_REMEDIATION_MANUAL` + `ACTIVE_SPRINT.json`) → Ark → `STRATEGY_CORPUS_MAP.md` (Layer-2, "nothing deleted by silence") → individual specs; plus `DOC_SSOT_MAP_20260807.md` routing table; CI teeth via `make doc-llm-validate` (M26, Makefile:177, gated in temple-grade:232) | Explicit conflict-resolution ORDER between documents; fine-grained preservation index so ideas are parked, never orphaned; supersession banners + disposition-flip tables (Corpus Map §0 DOC-1 Override Table) | Not dead — but degrading at the edges: same synonym-dir sediment as P1 (see #1), status-text drift as P4 (see #4). Survives BECAUSE it is the only pattern with (a) precedence rules, (b) dispositions, (c) a CI gate — the three things every dead pattern lacked | Guard its own weaknesses: naming-collision gate for docs/ dirs; machine-checked status fields in routing maps; periodic re-audit cadence (UO-4 ran once; drift resumed within weeks) |

---

## §2 What Actually Kills Doc Systems (cross-era synthesis)

Ranked by kill-count across eras:
1. **No validator** — every pattern that died had no machine check (P1, P2, P3, P4). Patterns with CI teeth survive (P7).
2. **Single-owner, session-scoped maintenance** — the reorganizer's context ended; the system's upkeep ended with it (P2, P4, P5).
3. **Completion declared, not verified** — three "organization-complete" files for one tree; "✅ LIVE" stamps on frozen content (P2, P4).
4. **Move-without-metadata** — archiving as relocation rather than indexed disposition (P6).
5. **Taxonomy without collision control** — naming schemes that assume a fixed corpus (P1, P3).

## §3 What the Current Layering Repeats vs Fixes

- **REPEATS**: P7's Corpus Map is structurally a P4 master index (one curated omnibus mapping topics→docs). Same failure surface: manual rows, prose status fields, human-only freshness.
- **FIXES**: adds explicit precedence (conflict resolution rule #4 in Corpus Map header), dispositions per row (ACTIVE/PARKED/ARCHIVE/SCRAPPED), supersession banners instead of silent edits, dated archives with routing pointers, and — uniquely — an enforcement gate (M26 `doc-llm-validate`).

---

## §4 FORWARD ANSWER — Dead Pattern Most Likely to Recur in Council 2's Spec Output

**P2 — Reorg Churn, wearing P4's clothes.**

Council 2's mandate is *spec drafting* for documentation organization. The historically dominant failure mode at exactly this juncture is: a well-intentioned spec proposes a NEW canonical structure/index (a fresh master map, a renamed tree, a new numbering) — i.e., a big-bang reorg with hand-curated upkeep — and dies within weeks when its author's session ends, leaving a half-migrated tree plus a stale "complete" marker. Era 2 did this THREE times (`organization-*` series); Era 6's own MASTER_DOCUMENT_SSOT lasted ~5 weeks before DOC_CLEANUP_AUDIT caught it lying.

**Explicit guards Council 2 should write INTO the spec (not as afterthoughts):**
1. **Validator-first clause**: no structural proposal ships without its CI check existing in the same deliverable (`make <gate>` runnable before the reorg starts, not after).
2. **Naming-collision gate**: synonym directories (`archive/archives`, `review/reviews`, `ops/operations`, `guides/how-to/tutorials`) must be a failing check — this is P1 recurrence happening today inside the surviving pattern.
3. **Machine-checkable status fields**: routing-map rows carry statuses a script can verify (path exists, version string matches pyproject/mandate count) — prose "✅ LIVE" is banned (it drifted within ~2 weeks: DOC_SSOT_MAP says M1-M25/v3.7.0; SOVEREIGN_MANDATES.md is now v3.8.0/M27).
4. **Named decay detector**: scheduled re-audit (UO-4 style) with owner; one-shot audits demonstrably don't hold.
5. **Anti-big-bang sizing**: migrations must be incrementally committable with the old and new paths BOTH valid during transition (the DOC_SSOT_MAP "Archived Path" column pattern generalized).

---

## §5 Evidence Index (all paths verified this session)

- Era 2 reorg attempts: `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/docs/design/organization-plan.md` (+ `-summary`, `final-organization-summary`, `implementation-files-organization-complete`)
- Era 1/2 Diátaxis + mkdocs: `/home/arcana-novai/Documents/docs-backup/internal_docs/01-strategic-planning/PHASE-ORGANIZATION-{PLAN,MKDOCS-INTEGRATION}.md` (both 2026-02-17)
- Era 5 numbered tree w/ collisions: `/home/arcana-novai/Documents/docs-backup/docs/` (listing: two `03-*`, two `04-*`)
- Era 4 memory bank: `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/memory_bank/`
- Era 4 junk-drawer archive: `foundation-legacy/.../docs/archive/{duplicates,old-versions,historical,sessions}/`
- Era 6 dead master index: `docs/archive/MASTER_DOCUMENT_SSOT_STALE.md`
- Era 6 drift audit: `docs/DOC_CLEANUP_AUDIT.md` (F1 version drift ×5 sources, F2 stale metrics, F3 40 frozen files, "no CI gate enforces doc updates")
- Era 6 hardened sprint plan: `docs/archive/DOCUMENTATION_NEXT_STEPS_HARDENED_STALE_20260706.md`
- Era 6 survivors: `docs/strategy/STRATEGY_CORPUS_MAP.md` (§0 DOC-1 Override Table), `docs/strategy/DOC_SSOT_MAP_20260807.md`, `Makefile:177` (`doc-llm-validate`), `Makefile:232` (temple-grade gating)
- Current sediment evidence: `ls docs/` = 62 top-level entries incl. `archive`+`archives`, `review`+`reviews`, `ops`+`operations`, `test_file.md`
- Git provenance: `git log --follow -- docs/strategy/STRATEGY_CORPUS_MAP.md` → born/grown in `e899ae2a` ("147 stale docs archived"), stamped through `d3b15b35` (DOC-1 stamps)

*⬡ OMEGA ⬡ ROC_RACOON ⬡ AP-ROC-DOC-ARCH-v1.0.0 ⬡ RECON COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

