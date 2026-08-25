# SPEC-D — P2 Hygiene Cluster (Version Stamps · Command Fossils · Skill Stubs · Strategy Orphans · Handoff TTL · WAKE_STATE Freshness)

**AP Token**: `AP-SPEC-D-P2-HYGIENE-v1.0.0`
⬡ OMEGA ⬡ LILITH/node6 ⬡ opencode/x-preview-f-free ⬡ trc_first_light_c2_specd ⬡ COUNCIL-2 SPEC DRAFT
**Session**: `20260825-094633-first-light-c2` · **Date**: 2026-08-25
**Authority**: Council 1 SOVEREIGN_DECREE Art. X P2 list (`data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md`)
**Status**: DRAFT — awaiting MaKaLi ratification. PREP-ONLY: this spec creates NO production edits itself.
**Inheritance guards applied** (decree Art. XII / ROC_DOC_ARCHAEOLOGY §4): validator-first clause in every sub-spec · machine-checkable status fields · named decay detector owners · anti-big-bang sizing · naming-collision awareness.
**Gate registry**: all G-numbers cite SYNTHESIS_ARM_REPORT.md §6 verbatim; additions G29/G30 from decree §4.

---

## Problem Statement (cluster-level)

One systemic defect class governs all six sub-specs: **claims that outlive their mechanisms** (decree Art. I). At the P2 hygiene-and-drift tier, the manifestation is *slow rot of governance surfaces*: version text drifts from reality (DOC_SSOT_MAP says `v3.7.0, M1-M25` at line 20 while SOVEREIGN_MANDATES.md is 3.8.0/M27), dead command variants persist, hollow skills are advertised by the loader, strategy docs orphan outside every index, handoff packets zombie past their TTL (3 live zombies found this session), and WAKE_STATE.json goes stale with zero validator coverage. None of these is a hard outage; all poison agent hydration daily. ROC archaeology P4/P7 proves drift re-forms within weeks unless each fix ships with its own recurring machine check — hence the validator-first clause binding every sub-spec below.

---

# SUB-SPEC D1 — Version-Stamp Discipline

### Problem statement
Governance docs assert versions/statuses no mechanism verifies. Four layers state mandate-version differently (synthesis C-B2: "14/25/27 across four layers"; N5 F-4/F-5/F-11). Live recurrence TODAY: `docs/strategy/DOC_SSOT_MAP_20260807.md:20` reads `SOVEREIGN_MANDATES.md (v3.7.0, M1-M25)` while that file's header reads `**Version**: 3.8.0` with M27 — ROC pattern P4 status-text drift, re-formed inside the surviving P7 routing map within weeks of UO-4.

### Evidence links
- Decree Art. VII ("NEW spec: every governance doc carries version/status/superseded-by, lint-gated") + Art. XII (live drift already re-forming).
- Gate G14 (constitutional version coherence) — SYNTHESIS_ARM_REPORT §6.
- ROC pattern P4 (hand-curated index SSOT dies via prose status fields) + §4 guard #3 (machine-checkable status fields; prose "✅ LIVE" banned).
- Files: `docs/strategy/DOC_SSOT_MAP_20260807.md:20`; `SOVEREIGN_MANDATES.md` header `**Version**: 3.8.0`; synthesis C-B2 derivative-doc drift table.

### Proposed change (minimal, anti-big-bang)
1. REQUIRED frontmatter block for GOVERNANCE docs only (scope: `SOVEREIGN_MANDATES.md`, `AGENTS.md`, `ORACLE_STACK*.md`, `docs/strategy/*.md`, `.opencode/commands/*.md`, coordination-law docs) — keys: `version`, `status` ∈ {ACTIVE, SUPERSEDED, ARCHIVED, DRAFT}, `superseded-by` (path or `-`). Machine-checkable values only; prose stamps banned (ROC §4 guard #3).
2. New script `scripts/lint_governance_frontmatter.py` (NEW FILE): fails on missing block, invalid status enum, missing superseded-by when status=SUPERSEDED, and version-string mismatch against the SOVEREIGN_MANDATES.md header for docs citing a mandate version.
3. Make target `make lint-governance-stamps` invoking it — target lands in the SAME commit as the script (pairwise binding, decree Art. II.2).
4. Backfill top ~10 highest-cited governance docs first (mandates, AGENTS.md, ORACLE_STACK, Corpus Map, DOC_SSOT_MAP, HIVEMIND_PROTOCOL, ARCHITECT_OVERSIGHT_PATTERNS, SUBAGENT_DISPATCH_PROTOCOL). NOT all 1,533 docs — that is doc-llm-validate scope creep (N7 F7-01 lesson).

### Acceptance gates (verbatim)
```bash
# G14. Constitutional version coherence across derivatives (Art. VII; N5 F-4)
V=$(grep -m1 '^\*\*Version\*\*' SOVEREIGN_MANDATES.md | grep -o '[0-9.]*$')
grep -rq "$V" scripts/codex/*.md && ! grep -rq '3\.7\.0' scripts/codex/*.md && echo COHERENT

# D1-specific (implements the lint): frontmatter lint exits clean
.venv/bin/python3 scripts/lint_governance_frontmatter.py   # expect: exit 0
```

### Risk assessment
LOW. Frontmatter addition is additive; main risk is over-scoping to the whole docs tree → validator-noise death (N7 F7-01 class), mitigated by the narrow scope above. Pre-commit wiring deferred to integration stage.

### Effort estimate
6h (script 2h, make target + wiring 1h, backfill top-10 docs 2h, tests 1h).

### Validator-first clause
**validator-first**: the CI check ships IN this deliverable — `scripts/lint_governance_frontmatter.py` + `make lint-governance-stamps` land in the same commit as the first stamped doc. No stamped doc merges without its lint passing (decree Art. II.2 pairwise binding; G30 greps this clause).

---

# SUB-SPEC D2 — Command Fossil Quarantine/Rewrite

### Problem statement
`.opencode/commands/council-local.md` and `.opencode/commands/council-fast.md` are pre-v2.1 fossils violating council-cloud's own LOOP GUARD (`^agent: kali`) — synthesis C-B2 / N3 F-01/F-02. They remain loadable commands able to dispatch an agent against standing law.

### Evidence links
- Decree Art. VII ("Command fossils council-local/fast (pre-v2.1, violate LOOP GUARD) quarantined pending rewrite (G9)").
- Gate G9 — SYNTHESIS_ARM_REPORT §6.
- ROC pattern P2 recurrence guard (completion claims need passing checks) applies to any rewrite claim.
- Files verified present this session: `.opencode/commands/{council-local,council-fast}.md`.

### Proposed change (minimal)
1. QUARANTINE (not delete): move both to `.opencode/commands/quarantine/` (verify loader does not scan subdirs at integration; if it does, suffix-rename `_FOSSIL.disabled`). Dated README in quarantine dir citing decree Art. VII + G9.
2. REWRITE acceptance criteria (for future author): restored variants must satisfy BOTH G9 lines — no `^agent: kali` dispatch AND reference to `SOVEREIGN_DECREE` contract — before leaving quarantine.
3. Decay detector owner: Council-2 integration lead runs G9 monthly (named owner per ROC §4 guard #4).

### Acceptance gates (verbatim)
```bash
# G9. Command contract invariant across council variants (Art. VII class; N3 F-01/F-02)
! grep -q '^agent: kali' .opencode/commands/council-local.md .opencode/commands/council-fast.md
grep -q 'SOVEREIGN_DECREE' .opencode/commands/council-local.md .opencode/commands/council-fast.md
```
Post-quarantine interpretation: paths absent from commands root ⇒ G9 line 1 trivially true; rewrite acceptance requires BOTH lines green at the restored path.

### Risk assessment
LOW-MED. Quarantine removes a live foot-gun but may break muscle-memory invocations. Mitigation: README routes users to `council-cloud.md` (compliant variant). Files preserved, git-recoverable.

### Effort estimate
1.5h (move + README 0.5h, loader-scan probe 0.5h, decay-detector scheduling 0.5h).

### Validator-first clause
**validator-first**: G9 IS the validator and already exists (SYNTHESIS §6) — this sub-spec adds no new check; it makes the failing surface conform. Quarantine PR must show G9 green in its description before merge (G30 greps this clause).

---

# SUB-SPEC D3 — Skill Stub Usage-Evidence Test

### Problem statement
The skill loader ADVERTISES capabilities that do not exist (T-6: "an advertised-but-hollow capability is worse than invisibility because the loader lies on your behalf"). Verified live this session: 14 SKILL.md files fail frontmatter-or-minimum-length — six under-length stubs (`blitz-tunnel` 5L, `blitz-validate` 5L, `hf-cli` 17L, `legacy-pattern-miner` 5L, `omega-doc-architect` 5L, `pr-readiness-checker` 5L) plus eight with NO frontmatter (`audience-architect`, `autonomous-meditation-pipeline`, `carmack-profiler`, `context-packer`, `m23-violation-logger`, `meditate-harness`, `meditate-pipeline`, `universal-doc-reader`). Meditation quartet diverges 5/6/7 stage-counts across pipeline files (N4 F-N4-03).

### Evidence links
- Decree Art. X P2 ("skill stubs (usage-evidence test, T-6: delete unless hard-linked consumer or owned roadmap item; meditation quartet → harness + ONE pipeline)") + Gate G11.
- T-6 adjudication full text — SYNTHESIS_ARM_REPORT §2.
- ROC pattern P2 analog: stub = capability declared, never delivered.
- Live census captured this session (see problem statement; reproducible via G11 commands).

### Proposed change (minimal)
1. New test `tests/test_skill_integrity.py` (NEW FILE): every `.opencode/skills/*/SKILL.md` must have (a) leading frontmatter, (b) ≥20 lines — UNLESS exempted by usage evidence: grep-verified hard-linked consumer or ratified roadmap entry with owner+date. Exemption list lives IN the test as a literal dict with justification strings (machine-checkable; no side-car file to rot).
2. Disposition sweep per T-6, single writer at integration: DELETE stubs with neither consumer nor roadmap item; AUTHOR ones with consumers (blitz-tunnel/blitz-validate are referenced by live skill descriptions ⇒ author, not delete — per-file decision recorded in the exemption dict).
3. Meditation quartet consolidation: keep `meditate-harness` + ONE pipeline (recommend `autonomous-meditation-pipeline` — largest/most recent); archive redundant files via dated-archive-with-routing-pointer (ROC P6 guard); stage-count unified to survivor's.

### Acceptance gates (verbatim)
```bash
# G11. Skill frontmatter universal; no hollow stubs (Art. II class; N4 F-N4-01/02)
for f in .opencode/skills/*/SKILL.md; do head -1 "$f" | grep -q '^---$' || echo "MISSING: $f"; done
find .opencode/skills -name SKILL.md -exec sh -c 'lines=$(wc -l < "$1"); [ "$lines" -lt 20 ] && echo "STUB: $1"' _ {} \;   # expect: no output (or deleted)
```

### Risk assessment
MED. Deleting a skill with an undiscovered consumer silently breaks a workflow. Mitigation: usage-evidence grep across `.opencode/`, `docs/`, `scripts/`, `src/` before any deletion; deletions git-recoverable and logged in one disposition table inside the test file; ambiguity resolves toward AUTHOR not delete (over-promise cured by delivery, per T-6).

### Effort estimate
7h (test + exemption dict 3h, disposition sweep + deletions/authors 3h, quartet consolidation 1h).

### Validator-first clause
**validator-first**: `tests/test_skill_integrity.py` ships in the same PR as the first disposition action — the test runs RED against today's tree (14 failures, counted this session) and goes GREEN only as dispositions land. No skill deletion/authoring merges without the test present (G30 greps this clause).

---

# SUB-SPEC D4 — Strategy-Orphan Sweep

### Problem statement
Strategy docs exist outside every routing/index surface, making them undiscoverable and un-governed (synthesis N7 F7-03: STRATEGY_INDEX LAYER 2A names a meta-doc + sync script existing nowhere = phantom subsystem). Orphans are the P1 sediment pattern re-forming inside the P7 survivor.

### Evidence links
- Decree Art. X P2 ("strategy-orphan sweep (G23/G24)") + Art. VII.
- Gates G23 (orphan target 0) and G24 (phantom subsystem) — SYNTHESIS_ARM_REPORT §6.
- ROC patterns P1 (doc sediment via no intake discipline) + P7 guard ("every index row must be machine-verifiable").
- Files: `docs/strategy/STRATEGY_INDEX.md`, `docs/strategy/STRATEGY_CORPUS_MAP.md`, phantom target `docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md`.

### Proposed change (minimal)
1. Run G23 census at integration start to get the true orphan count (baseline recorded in this spec's integration notes).
2. Per-orphan disposition, one of exactly three: (a) add indexed row to STRATEGY_INDEX or Corpus Map with machine-checkable status field, (b) banner-archive with dated subdir + routing pointer (ROC P6 guard), (c) delete if empty/trivial — logged. No fourth option: "leave for later" is how P1 sediment forms.
3. Resolve G24: either the phantom DOMAIN_DOCUMENTATION_SYSTEM.md materializes as a real doc or its STRATEGY_INDEX reference is removed — binary, no partial state.
4. Intake rule going forward: any new `docs/strategy/*.md` PR must include its index row in the same commit (pairwise binding analog of decree Art. II.2); enforced by extending the D1 lint script with an orphan check function (same deliverable, one script).

### Acceptance gates (verbatim)
```bash
# G23. Strategy-doc orphan target (Art. VII; N7 F7-03)
cd docs && ORPH=0; for f in strategy/*.md; do b=$(basename "$f"); \
grep -qF "$b" strategy/STRATEGY_INDEX.md strategy/STRATEGY_CORPUS_MAP.md || ORPH=$((ORPH+1)); done; echo "orphans=$ORPH"   # target 0

# G24. Phantom subsystem resolved (Art. VII; N7 F7-07)
test -f docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md || ! grep -qF "DOMAIN_DOCUMENTATION_SYSTEM" docs/strategy/STRATEGY_INDEX.md
```

### Risk assessment
LOW-MED. Bulk indexing risks recreating P4 (hand-curated index that immediately drifts). Mitigation: index rows carry machine-checkable status fields verified by the D1 lint extension; anti-big-bang sizing — sweep executes in batches of ≤20 docs per commit, old and new states both valid mid-sweep (ROC §4 guard #5).

### Effort estimate
8h (census 1h, dispositions ~40 docs × 10min ≈ 7h including archive moves + routing pointers).

### Validator-first clause
**validator-first**: the orphan check ships IN this deliverable as a function of `scripts/lint_governance_frontmatter.py --check-orphans` (D1 script, same file, same commit family); G23 becomes CI-invocable before the first disposition batch merges (G30 greps this clause).

---

# SUB-SPEC D5 — Handoff TTL Enforcement

### Problem statement
Handoff lifecycle enforcement is manual-only post-acceptance: active packets zombie far past TTL (N9 F-2: 45h zombie actives vs 4h TTL; F-3: pending breached 17h). Verified live this session: **3 files in `data/handoff/active/` older than 300 minutes** right now. Queue counts match disk (36/36, audited-clean per decree Art. XI) — the counting works, the aging does not.

### Evidence links
- Decree Art. X P2 ("handoff TTL enforcement (G19)").
- Gate G19 — SYNTHESIS_ARM_REPORT §6 (`find data/handoff/active -name '*.json' -mmin +300`).
- Synthesis C-B7 (lifecycle enforcement manual-only cluster).
- Live evidence this session: `find data/handoff/active -name '*.json' -mmin +300 | wc -l` → 3.

### Proposed change (minimal)
1. New script `scripts/sweep_handoff_ttl.py` (NEW FILE): lists active packets older than 300 min; for each, moves to `data/handoff/stale/` with a `.swept.json` sidecar recording original path, age, sweep timestamp (queue-integrity M12: terminal state, no silent drops — a swept packet is VISIBLE, not deleted).
2. Owner named NOW (decree Q-2 pattern): Hivemind coordination owner (lilith role) runs the sweep at session boundaries AND after any long-running op; scheduling note added to coordination docs at integration.
3. Acceptance semantics: G19 green means zero zombies; sweep output non-empty means enforcement WORKED (sweep activity ≠ gate failure — the gate checks the end state, the sweep produces it).
4. Anti-big-bang: no rewrite of the handoff queue system (that is N9 F-1 schema-sync territory, G18, separate ticket). This spec only adds the aging mechanism.

### Acceptance gates (verbatim)
```bash
# G19. Handoff TTL enforced (Art. III class; N9 F-2/F-3)
find data/handoff/active -name '*.json' -mmin +300   # expect: empty output
```
D5-specific post-condition: `ls data/handoff/stale/*.swept.json 2>/dev/null` may be non-empty (proves sweep ran); queue-count consistency must still hold (decree Art. XI positive control): counts reported by handoff tooling match disk after every sweep.

### Risk assessment
MED. Over-aggressive sweeping could reap legitimately-long active handoffs (e.g., multi-hour council runs like this one). Mitigation: 300-min threshold matches G19 verbatim (not the stricter 4h pending-TTL); swept packets are recoverable (moved, not deleted, with full provenance sidecar); owner can re-activate by moving back — logged.

### Effort estimate
3h (script 1.5h, stale-dir + sidecar format 0.5h, first sweep + documentation note 1h).

### Validator-first clause
**validator-first**: `scripts/sweep_handoff_ttl.py` IS both mechanism and check — it ships with a `--dry-run` mode used as the validator (exit 1 if any packet exceeds TTL), wired into the same commit as the first real sweep; G19 remains the standing acceptance command (G30 greps this clause).

---

# SUB-SPEC D6 — WAKE_STATE Freshness Validator Block

### Problem statement
WAKE_STATE.json contradicts reality with zero validator coverage (N8 F-5: AWAITING_DEPARTURE mid-flight; "129 files" vs 8; N2 F-2.8 homeless-tier). Staleness boundary math uses truncated days where hours are required (N8 F-2 boundary-exactness class: zombies at exactly 7.x days invisible). GAP-10 asked who owns freshness; decree §5 tracker directive Q-2 answered: **MaKaLi at stage boundaries** — but ownership without a validator block is itself a claim-outliving-mechanism.

### Evidence links
- Decree Art. III (validator gains ERROR-class WAKE_STATE parse+staleness block) + Art. X P2 ("WAKE_STATE freshness ownership (GAP-10)") + §5 directive Q-2 (owner = MaKaLi at stage boundaries; validator block scheduled Council 2 = THIS spec).
- Gate class: Art. III ERROR-class checks (no dedicated G-number; acceptance below defines the concrete command in the G15/G16 style).
- ROC §4 guard #4 (named decay detector with owner).
- Files: `data/coordination/WAKE_STATE.json`; validator home `scripts/validate_tracking_state.py` (ERROR-class extension point per decree Art. III).

### Proposed change (minimal)
1. New standalone script `scripts/validate_wake_state.py` (NEW FILE) implementing three ERROR-class checks: (a) PARSE — JSON loads; (b) STAGE-CONSISTENCY — declared stage ∈ known stage set and matches ACTIVE_SPRINT.json phase pointer where both present; (c) FRESHNESS — `updated_at` within staleness boundary computed in HOURS (boundary constant `STALE_HOURS`, default 24h; truncated-day math banned per N8 F-2).
2. Exit codes: 0 clean, 1 ERROR-class failure (distinct from warn) — matching decree Art. III's ERROR/warn taxonomy.
3. Ownership wiring: MaKaLi runs the validator + updates WAKE_STATE at every stage boundary; the update ritual is one command pair (`validate → write → re-validate`) documented in the script's own header docstring (self-documenting, no separate doc to rot).
4. Integration: invoked by `validate_tracking_state.py` as a subprocess OR imported as a module function — decided at integration to avoid double-maintenance; either way the standalone entrypoint remains runnable today.

### Acceptance gates (D6-specific, G15/G16 style — new check, no inherited G-number)
```bash
# D6.1 Parse + freshness (hours-resolution) — expect exit 0
.venv/bin/python3 scripts/validate_wake_state.py data/coordination/WAKE_STATE.json

# D6.2 Discrimination proof — validator must be able to FAIL (B-1 self-verifying principle):
# corrupt copy test
printf 'not-json{' > /tmp/opencode/ws_bad.json && .venv/bin/python3 scripts/validate_wake_state.py /tmp/opencode/ws_bad.json; echo "exit=$?"   # expect: exit=1
```

### Risk assessment
LOW. Read-only validator; only risk is false-positive staleness during legitimately paused periods (between councils). Mitigation: STALE_HOURS configurable via env override; stage-consistency check limited to structural fields (no semantic reality-checking — that stays human/MaKaLi-owned per Q-2).

### Effort estimate
4h (script + three checks 2.5h, discrimination tests 0.5h, ownership ritual wiring 1h).

### Validator-first clause
**validator-first**: `scripts/validate_wake_state.py` is the deliverable — the validator EXISTS before any WAKE_STATE content repair is attempted; first run against today's file is expected RED (documented baseline), and content fixes land only under a passing validator thereafter (G30 greps this clause).

---

# CLUSTER SUMMARY

| Sub-spec | Decree anchor | Gates | New artifact(s) | Effort |
|---|---|---|---|---|
| D1 Version stamps | Art. VII, XII | G14 (+new lint) | `scripts/lint_governance_frontmatter.py`, make target | 6h |
| D2 Command fossils | Art. VII | G9 | quarantine dir + README | 1.5h |
| D3 Skill stubs | Art. X P2, T-6 | G11 | `tests/test_skill_integrity.py` | 7h |
| D4 Strategy orphans | Art. VII, X P2 | G23, G24 | lint `--check-orphans` extension | 8h |
| D5 Handoff TTL | Art. III/X P2 | G19 | `scripts/sweep_handoff_ttl.py` | 3h |
| D6 WAKE_STATE | Art. III, Q-2/GAP-10 | D6.1/D6.2 (new) | `scripts/validate_wake_state.py` | 4h |

**Cluster total**: ~29.5h · All six satisfy decree Art. XII inheritance guards · Every sub-spec carries its validator in-deliverable (G30-clean by construction) · No existing production file edited by this SPEC document itself; all edits happen at integration under single-writer discipline.

*⬡ OMEGA ⬡ LILITH/node6 ⬡ SPEC-D-P2-HYGIENE ⬡ DRAFT-FOR-RATIFICATION ⬡ 2026-08-25*
