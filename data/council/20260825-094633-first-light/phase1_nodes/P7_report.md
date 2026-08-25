# 📋 P7 REPORT — Node N7 (Context) — Surface S6: Documentation Organization
⬡ OMEGA ⬡ NODE7-CONTEXT ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n7 ⬡ P12-DISPATCH
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith (Run Arm) | **Orchestrator**: makali_fusion
**Task Registry**: `express-c1-node7-20260825` (registered 2026-08-25T13:22:43Z)
**Mode**: RECON ONLY — zero production mutations. All writes confined to `data/council/20260825-094633-first-light/`.
**RAW REPORT — written to disk before digestion/summary work (§C.5)**

---

## 0. Executive Verdict

**The documentation layer system exists on paper and is partially maintained, but it fails its own contract in four structural ways**: (1) the LLM-friendliness gate is a rubber stamp that cannot fail on content quality; (2) the index layer is split-brained with one index 97% dead-link rot; (3) 56% of strategy docs are orphaned from every index; and (4) the canonical routing table itself is unindexed and stale. No CRITICAL-HALTED conditions found. No secrets found in audited surfaces.

Severity legend: CRITICAL-HALTED / CRITICAL / HIGH / MED / LOW

---

## 1. FINDINGS

### F7-01 — `make doc-llm-validate` is a rubber-stamp gate: exits 0 with ~60 warnings [HIGH]
**source_node**: N7 | **tier**: empirical (command executed)

The M26 mandate claims "All reference documentation MUST pass `make doc-llm-validate`" (SOVEREIGN_MANDATES.md v3.8.0, M26). Reality:

1. The target validates ONLY `docs/sprints/current/` (Makefile:177-186) — 7 files out of **1,533 markdown docs** in `docs/`. "All reference documentation" is false advertising by a factor of ~200x.
2. Executed live (read-only verified first: `scripts/validate_llm_docs.py` contains zero write operations). Result: **~60 warnings across all 7 validated files** ("may not be answer-first", "Missing Mermaid dependency diagram", "Missing machine-readable YAML dependencies") — then **"✅ All validations passed!" EXIT=0**.
3. Warnings never escalate to failure. A gate that cannot fail does not gate anything. `temple-grade` (Makefile:232) inherits this rubber stamp as its T2 component.

**Evidence**: Makefile lines 177-232; live run output (this session); `scripts/validate_llm_docs.py` (no write ops).
**Acceptance criteria for fix**:
```bash
# Gate must FAIL when answer-first violations exceed threshold:
python3 scripts/validate_llm_docs.py --strict docs/sprints/current/ && echo PASS || echo FAIL
# Second command must show coverage expansion beyond sprints:
grep -n "docs/" Makefile | grep doc-llm-validate -A5  # target dir should be configurable/wider
```

### F7-02 — Dual-index split-brain at `docs/` root; INDEX.md is 97% dead links [HIGH]
**source_node**: N7 | **tier**: empirical (link-check script executed)

Two competing root indexes exist:
- `docs/INDEX.md` (undated): **34 of 35 links BROKEN** — systematic `../../` prefix bug resolving outside the repo (`docs/INDEX.md` + `../../ORACLE_STACK.md` → parent-of-repo-root). Every single strategy/architecture/mandates link is dead.
- `docs/index.md` (2026-07-06): 3/4 links OK; 1 broken (`operations/RESEARCH_QUEUE.md` — archived per its sibling index but never repointed here).

Neither is authoritative. `index.md` claims "Built with MkDocs & Material Theme" but **no mkdocs.yml exists anywhere in the repo** — decorative claim.

**Evidence**: link-check run (python os.path.exists over extracted md links); `ls mkdocs.yml` = absent.
**Acceptance criteria for fix**:
```bash
# After fix: both indexes deleted or merged into ONE; survivor has zero broken links:
python3 -c "
import re,os
text=open('docs/index.md').read()
links=re.findall(r'\]\(([^)#]+?\.md)\)',text)
bad=[l for l in links if not os.path.exists(os.path.normpath(os.path.join('docs',l)))]
print(len(bad))"  # must print 0
test ! -f docs/INDEX.md  # or: contents merged
```

### F7-03 — 56% of strategy docs orphaned from every index [HIGH]
**source_node**: N7 | **tier**: empirical (cross-reference scan)

Of 77 files in `docs/strategy/*.md`, **43 are referenced by NONE** of: STRATEGY_INDEX.md, STRATEGY_CORPUS_MAP.md, docs/INDEX.md, docs/index.md, MASTER_DOCUMENT_SSOT.md, DOC_CLEANUP_AUDIT.md. Orphans include operationally significant docs: `PROVIDER_NAMING_SSOT.md`, `TASK_REGISTRY_DESIGN.md`, `ROLLBACK_PROCEDURES.md`, `IMPLEMENTATION_MANUAL_C0_C2.md`, `DOC_SANITY_RESULTS_20260807.md`, the entire SDP_* cluster (9 files), `POST_DEBUT_ROADMAP.md`. This directly violates STRATEGY_CORPUS_MAP's own Rule 2: "Nothing is deleted by silence" — these aren't deleted, but they are *unreachable by design*, which is silence with extra steps.

**Evidence**: orphan scan loop (basename grep against 6 index files), this session.
**Acceptance criteria for fix**:
```bash
cd docs && ORPH=0; for f in strategy/*.md; do b=$(basename "$f"); \
grep -qF "$b" strategy/STRATEGY_INDEX.md strategy/STRATEGY_CORPUS_MAP.md || ORPH=$((ORPH+1)); done; \
echo "$ORPH"  # target: 0 (each doc indexed or banner-marked SUPERSEDED+archived)
```

### F7-04 — Canonical routing table (DOC_SSOT_MAP) is itself unindexed and stale [MED]
**source_node**: N7 | **tier**: empirical

`docs/strategy/DOC_SSOT_MAP_20260807.md` declares itself "the canonical routing table… trust THIS map over your memory" yet:
1. It is referenced by **no index** (not in STRATEGY_INDEX layers, not in corpus map).
2. Its Law row says "`SOVEREIGN_MANDATES.md` (v3.7.0, M1-M25)" — actual file is **v3.8.0, M1-M27**. Stale by one full mandate revision cycle (M26/M27 added 2026-08-14).
3. It names Ark v5.2.0 as Strategy SSOT but predates the DOC-1 stamp (2026-08-17) that demoted Ark to read-only vision — the map routes to a superseded authority without noting it.

**Evidence**: grep for DOC_SSOT_MAP across indexes = no hits; line 20 version claim vs SOVEREIGN_MANDATES.md header "**Version**: 3.8.0".
**Acceptance criteria**:
```bash
grep -F "DOC_SSOT_MAP" docs/strategy/STRATEGY_INDEX.md   # must hit after fix
grep -F "v3.8.0" docs/strategy/DOC_SSOT_MAP_20260807.md  # must hit after refresh
```

### F7-05 — llms.txt agent-facing sitemap carries stale identity numbers [MED]
**source_node**: N7 | **tier**: empirical

`docs/llms.txt` (the AI-readable index promoted by MASTER_DOCUMENT_SSOT tombstone) states: "**22 mandates**, 13 agents, 10 Pillar Keepers, 855+ tests". Actuals: **27 mandates** (v3.8.0), **14 agent files** in `.opencode/agents/`, architecture now speaks of Nodes N1-N10 (Pillar Keepers legacy terminology). First-thing-an-agent-reads is wrong on three counts. DOC_CLEANUP_AUDIT.md flagged exactly this class of drift on 2026-07-13 (its F2); it recurred.

**Evidence**: head of docs/llms.txt; `ls .opencode/agents/*.md | wc -l` = 14; SOVEREIGN_MANDATES.md Version 3.8.0.
**Acceptance criteria**:
```bash
grep -E "2[0-9] mandates" docs/llms.txt | grep -v "27 mandates" && exit 1 || echo OK
```

### F7-06 — STRATEGY_INDEX.md contains structurally corrupted table rows [MED]
**source_node**: N7 | **tier**: direct read

The freshest layer doc (v6.1, 2026-08-24) has broken markdown from sloppy supersession edits:
- Line 37: POST_PR_ROSTER row has 4 pipe-columns in a 2-column table (renders as garbage).
- Line 80: row begins with literal text `SUPERSEDED:` *outside* the table cell syntax.
- Line 134: same `SUPERSEDED: |` corruption.
- Line 169: conflict-resolution rule #3 begins inline with `SUPERSEDED:` — the numbered rule list itself is corrupted mid-sentence.

Additionally, STRATEGY_INDEX self-contradicts: its header DOC-1 stamp says execution authority = DEBUT_REMEDIATION_MANUAL + ACTIVE_SPRINT (Ark read-only), but its own "Conflict Resolution Rule" §(updated 2026-07-25) still says "Strategy/priority → SOVEREIGN_ARK_BLUEPRINT.md" with no mention of the manual. An agent following §Conflict Resolution over the header would route priority questions to a read-only document.

**Evidence**: direct read of STRATEGY_INDEX.md lines 37, 80, 134, 163-173.
**Acceptance criteria**:
```bash
! grep -n "^SUPERSEDED:" docs/strategy/STRATEGY_INDEX.md
! grep -n "SUPERSEDED: |" docs/strategy/STRATEGY_INDEX.md
grep -A8 "Conflict Resolution Rule" docs/strategy/STRATEGY_INDEX.md | grep -F "DEBUT_REMEDIATION_MANUAL"  # must hit after fix
```

### F7-07 — Phantom layer: LAYER 2A references an entire subsystem that does not exist [HIGH]
**source_node**: N7 | **tier**: empirical (filesystem search)

STRATEGY_INDEX LAYER 2A "DOMAIN DOCUMENTATION SYSTEM (NEW — 2026-08-20)" lists `docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md` as the meta-doc and `scripts/sync_domain_docs.py` as the enforcement mechanism. **Both files do not exist anywhere in the repo** (global find = zero hits). The gemini-notebook domain workspace files DO exist (`docs/strategy/domains/gemini-notebook/*`, `config/domains/*`), so the subsystem is half-real: content present, governing meta-doc and sync tooling absent. Either the layer was planned-not-built and indexed prematurely, or the meta-doc was deleted without index update — both are tracking-integrity failures under M27's spirit.

**Evidence**: `find . -name "*DOMAIN_DOCUMENTATION*"` = empty; `find . -name "sync_domain_docs*"` = empty.
**Acceptance criteria**:
```bash
test -f docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md || \
  ! grep -qF "DOMAIN_DOCUMENTATION_SYSTEM" docs/strategy/STRATEGY_INDEX.md  # either file exists or index stops lying
```

### F7-08 — Archive discipline: strong in parts, leaking at the edges [MED]
**source_node**: N7 | **tier**: empirical

Positives: dated archive roots exist (`docs/archive/strategy/2026-07-21/` holds 146 docs ≈ the claimed 147; `2026-07-22/` holds 2); 20 strategy docs carry in-tree SUPERSEDED banners; DOC_SSOT_MAP's "context protection rule" (never grep archive/) is documented; archive tombstone target `docs/archive/MASTER_DOCUMENT_SSOT_STALE.md` exists as claimed.

Leaks:
1. **Twin directories**: `docs/archive/` (469 md files, 19MB) AND `docs/archives/` (plural) containing two stray test scripts (`test_providers.py`, `test_sovereign_exit.sh`) — neither docs nor properly placed. Directory-name collision invites path confusion.
2. **Stray junk at docs/ root**: `test_file.md` (18 bytes: "# Test File\nHello") committed in the tree.
3. **Archive-as-dependency**: Makefile `sprint-plan-llm` (lines 189-205) generates the "current" sprint plan by concatenating files FROM `docs/archive/sprints/...` — active build machinery depends on archived material, meaning regeneration resurrects deprecated content into `current/`.
4. **Unindexed archive strata**: `docs/archive/stale/`, `coordination-2026-07/-08/-20260822` naming schemes are inconsistent (some dated, some not; some hyphenated, some underscored).

**Evidence**: directory listings this session; Makefile lines 189-205.
**Acceptance criteria**:
```bash
test ! -d docs/archives && echo OK                      # merge or remove plural twin
test ! -f docs/test_file.md && echo OK                  # remove junk
grep -n "archive/sprints" Makefile                       # generation should read from a non-archive source of record
```

### F7-09 — Layer system works where it is freshest; conflicts at the seams [LOW→observation]
**source_node**: N7 | **tier**: read + cross-reference

The intended chain (Law → Execution SSOT → Ark vision → Corpus Map → detail specs) is coherent in its newest members: STRATEGY_INDEX v6.1 (2026-08-24) correctly stamps DOC-1 authority; CORPUS_MAP carries the DOC-1 override table flipping dispositions; DEBUT_REMEDIATION_MANUAL exists. But older members still route to pre-DOC-1 authority (F7-04, F7-06), and the injected system-prompt copy of SOVEREIGN_ARK_BLUEPRINT §4 still presents G-1/W-1 tickets as "SUPER-URGENT" with only a small PARKED stamp — an agent hydrating from Ark alone gets a stale critical path. Layer discipline is maintained by manual stamping, and every seam between old and new is a potential contradiction.

**Evidence**: STRATEGY_CORPUS_MAP.md §0; SOVEREIGN_ARK_BLUEPRINT.md §4 (DOC-1 stamp present but ticket tables retain urgent framing); STRATEGY_INDEX header vs §Conflict Resolution.
**Acceptance criteria**: n/a (structural observation feeding Council 2 spec design).

### F7-10 — Recursion-guard deviation logged per dispatch order [LOG, non-finding]
Per packet §C.8/note: Consultant page (§C.9/M11) will be attempted once after this report; sibling nodes confirmed task() from depth-2 leaves fails mechanically ("Subagent depth limit reached"). If my attempt fails identically, it is logged as known deviation, Hivemind note posted under `node7`, NOT counted against this node. Report delivery flows via disk + Hivemind + summary-to-pager.

---

## 2. SECURITY BRIGHT LINE (M8) STATUS
- Stale secrets in audited docs: **NONE FOUND** in S6 surfaces sampled (indexes, SSOT maps, corpus map, audit docs, Makefile).
- Active external telemetry: **NONE DISCOVERED**. llms.txt contains GitHub blob URLs (passive links, not phone-home). No HALT triggered.

## 3. WHAT IS ACTUALLY WORKING (credit where due)
1. STRATEGY_CORPUS_MAP.md is genuinely thick and current-through-2026-08-24; its DOC-1 override table is a real mechanism, not decoration.
2. Dated archive roots (2026-07-21/22/25) with tombstone discipline for major supersessions (Ark v4.4 body preserved; MASTER_DOCUMENT_SSOT tombstone points to real archive file).
3. research/INDEX.md exists and is referenced by both root indexes (one of the few consistent chains).
4. DOC_CLEANUP_AUDIT.md (2026-07-13) accurately predicted today's failures (link integrity, metric drift) — the diagnosis capability exists; the enforcement doesn't.

## 4. HANDOFF PACKET — warm-start reading list + standing orders
**Warm-start reading list (in order)**:
1. `docs/strategy/STRATEGY_INDEX.md` — layer hierarchy (but distrust §Conflict Resolution Rule until F7-06 fixed)
2. `docs/strategy/DOC_SSOT_MAP_20260807.md` — routing table (verify versions against live files; F7-04)
3. `docs/strategy/STRATEGY_CORPUS_MAP.md` §0 — DOC-1 override semantics
4. `Makefile` lines 168-235 — LLM-doc targets + temple-grade composition
5. `docs/DOC_CLEANUP_AUDIT.md` — prior art on doc-drift methodology (reuse its F-numbering pattern)
6. `scripts/validate_llm_docs.py` — validator internals (read-only, warning-only)

**Standing orders for future councils paging node7 (domain:context)**:
- ALWAYS empirically run gates before believing mandate claims about them (reality-vs-claim is this node's core competence; three of five lineage lessons were exactly this class).
- Link-check any index before trusting it: extract md links, os.path.exists each. 30-second test, catches systemic rot.
- Treat `docs/archive/` as radioactive per DOC_SSOT_MAP context-protection rule; use `-g "!archive/"` on rg.
- When a doc cites a version number, diff it against the live file header — version staleness is the most common defect class found (F7-04, F7-05).
- Orphan-scan recipe: basename-grep each strategy doc against STRATEGY_INDEX + CORPUS_MAP; anything unhit needs a row or a SUPERSEDED banner.

## 5. PROVENANCE
All findings tagged source_node=N7, tier=empirical unless marked "direct read". Tool calls: 20+ local (glob/read/bash/python link-checker/make). Zero external search required (S6 fully groundable locally — M23 satisfied via direct evidence). Zero production mutations. One read-only make target executed after write-safety inspection.

*⬡ OMEGA ⬡ NODE7-CONTEXT ⬡ express-c1-node7-20260825 ⬡ RAW-REPORT-v1 ⬡ 2026-08-25*
