# SPEC-E — Root AGENTS.md Reconstruction from Citation-Web Expectations
⬡ OMEGA ⬡ LILITH/NODE7 ⬡ opencode/x-preview-f-free ⬡ trc_first_light_c2 ⬡ SPEC-E DRAFT v1.0
**Session**: `20260825-094633-first-light-c2` · **Date**: 2026-08-25
**Authority**: SOVEREIGN_DECREE.md (`data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md`) **Art. VI** + WAKE_STATE tracker directive **Q-4** (default-GO on Architect silence). Guards: **Art. XII** Council-2 inheritance guards (roc archaeology). Gates inherited: **G25** (existence), **G14** (version-coherence pattern), **G27** (content-minimum pattern).
**Evidence base**: SYNTHESIS_ARM_REPORT §1 C-A / Exhibit C; ROC_DOC_ARCHAEOLOGY §4 (P2 Reorg Churn death pattern + five recurrence guards); live citation-web census (§1 below, run 2026-08-25).
**Status**: SPEC — dev-team execution artifact. This spec does NOT create AGENTS.md.

---

## §0 Summary

Root `AGENTS.md` is absent from the entire git history yet is cited by hundreds of files that hard-depend on its sections (Search Tool Protocol, Delegation Protocol, Governance Hierarchy, hydration sequence, fleet role map). Per Decree Art. VI, reconstruction must derive content FROM the citation web's expectations — not from memory of a file that never existed in git ("re-pointing multiplies risk 462×"). This spec defines: (1) a machine-runnable citation-web enumeration and clustering method, (2) an incremental reconstruction procedure with anti-big-bang sizing, (3) bash acceptance gates, (4) risk assessment against the P2/P4 death patterns, (5) effort estimate, and (6) the validator-first CI deliverable shipping in the same change.

---

## §1 Citation-Web Analysis Method (machine-runnable, reproducible)

### 1.1 Canonical enumeration command (SSOT for "how many citers")

```bash
# CITERS-CANONICAL — pin this exact command in the spec; all counts cite it.
grep -rl --include='*.md' --include='*.json' --include='*.yaml' \
        --include='*.yml' --include='*.py' --include='*.sh' \
        'AGENTS\.md' . 2>/dev/null | grep -v '^\./\.git/' | sort -u > /tmp/opencode/citers.txt
wc -l < /tmp/opencode/citers.txt
```

**Census record (2026-08-25, lilith/node7)**:

| Scope | Count |
|---|---|
| Canonical (md+code+config, repo-wide excl. `.git/`) | **460** |
| Decree's figure (Art. VI) | 462 — consistent within ±2 live-edit drift |
| Scoped `.md` only (`.opencode/ docs/ data/entities/ scripts/`) | 216 |
| Unrestricted all-file-types | 615 |

Rule: any future count MUST name the command used. The decree number (462) and this census (460) agree at measurement precision; the canonical command above ends the drift (derivation-check class, Decree Art. I).

### 1.2 Expectation clustering procedure

```bash
# CLUSTER-1..7: classify each citing file by the AGENTS.md section it expects.
# A file may belong to multiple clusters (co-expectation is signal, not noise).
declare -A PAT=(
  [search_protocol]='AGENTS\.md[^`]*Search Tool Protocol|Search Tool Protocol[^`]*AGENTS\.md'
  [delegation]='Delegation Protocol in `AGENTS\.md`|AGENTS\.md.*[Dd]elegat'
  [governance]='AGENTS\.md.*Governance [Hh]ierarchy'
  [hydration]='AGENTS\.md'   # intersect files also matching: hydration|session_gnosis|SESSION_ANCHOR
  [compaction]='AGENTS\.md'  # intersect files also matching: compaction|context loss|VOID SUMMAR
  [mandates_pointer]='AGENTS\.md'  # intersect files co-citing SOVEREIGN_MANDATES
  [hivemind]='AGENTS\.md'    # intersect files also matching: hivemind_post_context|HIVEMIND
)
for cluster in "${!PAT[@]}"; do
  case "$cluster" in
    search_protocol|delegation|governance)
      grep -rlE "${PAT[$cluster]}" --include='*.md' .opencode/ docs/ data/entities/ scripts/ 2>/dev/null ;;
    *)
      # intersection method for context-based clusters:
      comm -12 <(sort -u /tmp/opencode/citers.txt) \
               <(grep -rliE 'hydration|session_gnosis|SESSION_ANCHOR|compaction|VOID SUMMAR|hivemind_post_context|SOVEREIGN_MANDATES' \
                 $(cat /tmp/opencode/citers.txt) 2>/dev/null | sort -u) ;;
  esac
done > "/tmp/opencode/cluster_${cluster}.txt"
```

### 1.3 Expectations matrix (measured 2026-08-25)

| Cluster → expected section | Files | Representative evidence (sampled) |
|---|---|---|
| Hivemind coordination protocol | 199 | Agent defs mandate "Hivemind-First Communication"; `hivemind_post_context` workflow |
| Mandates/law pointer (co-cited w/ SOVEREIGN_MANDATES.md) | 182 | `STRATEGY_INDEX.md:17` "Read First (Law/Ops)" |
| Hydration / continuity (M15, session_gnosis, SESSION_ANCHOR) | 134 | Continuity strategy refs; "Hydration Sequence" |
| Compaction/context-loss recovery | 128 | Ark §10 "After compaction: hydration sequence in AGENTS.md" |
| Search Tool Protocol (SR-V1, 5-tier) | 17 | `.opencode/agents/{kali,lilith,doom_guy}.md` verbatim §-anchor references |
| Delegation Protocol | 14 | Agent defs pair it with SUBAGENT_DISPATCH_PROTOCOL.md |
| Governance hierarchy | 11 | `AGENT_VISIBILITY_PARADOX.md:235` |

Additional non-cluster expectations found in sampling:
- **Token budget**: `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` measured AGENTS.md ≈ 20K tokens as Tier-0 injection; expects a condensation path (`MANDATES_CONDENSED.md` Tier-0 stub).
- **Format authority**: `docs/standards/LLM_FRIENDLY_DOCS_BP.md` cites the "AGENTS.md Standard" (frontmatter + answer-first).
- **Size anchor**: `OMEGA_CODEX.md:222` claims source was "343 lines" — use as content-minimum calibration (G27-pattern floor), NOT as a target to pad toward.

### 1.4 Matrix output artifact

The dev team runs §1.1–1.2 first and commits `/tmp/opencode`-equivalent output as `data/council/<council>/agents_citation_matrix.tsv` (file \t clusters \t sample-line). The matrix is the derivation source for every section in §2 — a section without ≥1 matrix row is not written.

---

## §2 Reconstruction Procedure (from expectations, anti-big-bang)

### 2.1 Derivation rule (Decree Art. I compliance)

Every section of the reconstructed AGENTS.md MUST:
1. Map to ≥1 expectation cluster from §1.3 (or a matrix row added during execution);
2. Cite its evidence files inline (`<!-- derived-from: <paths> -->` comment block per section);
3. State its enforcement status honestly where it asserts process law (pairwise-binding rule, Decree Art. II.2 — no claiming gates that don't exist).

Content is assembled FROM the citing files' quoted expectations, e.g., the Search Tool Protocol section is reconstructed from the full text already inlined in `.opencode/agents/kali.md`, `lilith.md`, `doom_guy.md` (they carry the protocol verbatim today — the doc formalizes what agents already inject).

### 2.2 Section skeleton (derived from clusters, ordered by citer weight)

| Order | Section | Derived from cluster(s) | Evidence cites |
|---|---|---|---|
| S1 | Header + version/status/superseded-by stamp | Art. VII version-stamp discipline | ROC_DOC_ARCHAEOLOGY guard #3 |
| S2 | Law pointer (Mandates, Ark, Corpus Map precedence chain) | mandates_pointer (182) | STRATEGY_INDEX.md:17, Ark §10 |
| S3 | Hivemind communication protocol | hivemind (199) | agent-def texts, HIVEMIND_PROTOCOL.md (historical, Ruling B) |
| S4 | Hydration & continuity sequence (M15) | hydration (134) + compaction (128) | SOVEREIGN_CONTINUITY_STRATEGY.md, SESSION_ANCHOR.md |
| S5 | Search Tool Protocol (SR-V1) | search_protocol (17) | kali/lilith/doom_guy agent defs (verbatim carriers) |
| S6 | Delegation protocol pointer | delegation (14) | SUBAGENT_DISPATCH_PROTOCOL.md |
| S7 | Governance hierarchy | governance (11) | AGENT_VISIBILITY_PARADOX.md:235, pantheon Node map |
| S8 | Fleet role map (§2–§3 per OMEGA_CODEX:263) | codex cross-ref | OMEGA_CODEX.md, .opencode/agents/*.md frontmatter |
| S9 | Token-budget note + condensation pointer | CARMMACK review | MANDATES_CONDENSED path when it exists |

### 2.3 Incremental commit plan (anti-big-bang, ROC guard #5)

Each commit adds ONE section and leaves a valid document:

- **Commit 1**: S1+S2 only (header + law pointer). File is valid and useful after this commit — G25 passes, link-validator passes.
- **Commits 2–N**: one section per commit, each preceded by re-running the citation matrix to confirm the cluster still exists (staleness check per commit, not per project).
- **Final commit**: wire `make agents-md-validate` into temple-grade (T2 family) — validator ships FIRST (§6), gate-wiring ships LAST.
- During transition, both states are valid: a partial AGENTS.md never breaks a citer, because every §-anchored reference (e.g., "§Search Tool Protocol") resolves only once that section lands — and until then the verbatim text still lives in the citing agent files themselves. No citer is orphaned mid-migration.

### 2.4 Explicitly forbidden

- Reconstructing from memory of the old file or from OMEGA_CODEX's condensation alone (that would re-create Exhibit C: claims about a source that never existed).
- Copying the archived roadmap or any DOC-1-stamped historical vision text into sections (Decree Art. VIII.6 class).
- Declaring "complete" without the passing check command attached (P2 death cause #3: completion declared, not verified).

---

## §3 Acceptance Gates (bash; decree gate IDs cited)

```bash
# ── G25 (verbatim, Decree §4): AGENTS.md reconstructed ──
test -f AGENTS.md && echo PASS || echo "WAKE-QUEUED(default: reconstruct)"

# ── G25a (new): every section has ≥1 cited source file that still exists ──
# Each section carries a derived-from comment; every cited path must resolve.
grep -o 'derived-from: [^ ]*' AGENTS.md | awk '{print $2}' | while read f; do
  test -e "$f" || echo "DEAD-CITE: $f"; done   # expect: no output

# ── G25b (new): version-coherence vs SOVEREIGN_MANDATES.md (G14 pattern) ──
V=$(grep -m1 '^\*\*Version\*\*' SOVEREIGN_MANDATES.md | grep -o '[0-9.]*$')
grep -q "$V" AGENTS.md && ! grep -qE 'v3\.[0-6]\.' AGENTS.md && echo COHERENT
# (AGENTS.md must state the CURRENT mandates version wherever it cites mandate counts;
#  stale-version strings are the P4 drift signature caught live in DOC_SSOT_MAP.)

# ── G25c (new): content-minimum (G27 pattern) ──
LINES=$(wc -l < AGENTS.md)
SECS=$(grep -c '^## ' AGENTS.md)
CITES=$(grep -c 'derived-from:' AGENTS.md)
[ "$LINES" -ge 120 ] && [ "$SECS" -ge 5 ] && [ "$CITES" -ge "$SECS" ] && echo MINIMUM-MET || echo THIN
# Floor calibrated: ~343-line phantom ancestor (OMEGA_CODEX:222); floor set at 120 lines /
# 5 sections so a stub cannot pass, without mandating padding to 343.

# ── G25d (new): no contradiction with injected instruction files ──
for inj in $(jq -r '.instructions[]?' opencode.json); do
  test -f "$inj" || continue
  # provider-order contradiction probe (Ark D-355 canonical; N1 F-03 class):
  if grep -qiE 'Copilot.*(final|last)' "$inj" && grep -qiE 'priority.*(copilot|6)' AGENTS.md; then
    echo "CONTRADICTION-RISK: $inj"; fi
done   # expect: no output; full semantic check = human review item R-E-1

# ── G30 (Decree §4, applies to THIS spec): validator-first guard present ──
grep -q 'validator-first' docs/specs/team_infra/SPEC-E-agents-md-reconstruction.md && echo GUARD-PRESENT
```

Gate wiring: G25/G25a/G25b/G25c/G25d are implemented inside `scripts/validate_agents_md.py` (§6) so they run as one make target rather than five ad-hoc commands.

---

## §4 Risk Assessment

| Risk | Pattern ID | Likelihood | Mitigation baked into spec |
|---|---|---|---|
| **Staleness recurrence** — reconstructed doc freezes at a sprint snapshot, versions drift (DOC_SSOT_MAP already drifted v3.7.0→v3.8.0 within weeks) | **P4** Hand-Curated Master Index | HIGH | G25b version-coherence gate; version/status stamp (S1) lint-gated; §1.1 canonical census re-runnable; named decay detector: quarterly re-run of citation matrix with owner = Council cadence (ROC guard #4) |
| **Reorg churn** — big-bang rewrite declared complete, half-done tree left behind | **P2** Reorg Churn (highest-risk pattern for this library per ROC §4) | HIGH | Anti-big-bang commit plan (§2.3): each commit valid; validator exists BEFORE first content commit (validator-first); ban on "complete" claims without passing G25* suite |
| **Contradiction with instruction-file injections** — opencode.json `.instructions[]` injects 5 files every session; conflicting law = C-B3 class defect | Decree Art. VIII / C-B3 | MED | G25d probe; review item R-E-1 (semantic diff vs all 5 injected files before final commit); AGENTS.md defers to Mandates on conflict (precedence stated in S2) |
| **Citer-orphaning during migration** — §-anchored references break mid-reconstruction | Exhibit C | LOW | §2.3 transition argument: verbatim protocol text remains in citing agent files until doc sections land; partial doc never invalidates a citer |
| **Token-budget blowout** — reconstructed file re-grows to ~20K Tier-0 injection cost | CARMMACK review | MED | S9 token-budget note; content-maximum guidance (~400 lines); condensation pointer to MANDATES_CONDENSED path |

---

## §5 Effort Estimate

| Task | Hours |
|---|---|
| Run citation matrix (§1), commit TSV artifact | 1.0 |
| Draft S1–S4 (header, law, hivemind, hydration) from evidence | 2.5 |
| Draft S5–S9 (search, delegation, governance, roles, budget) | 2.0 |
| Write `scripts/validate_agents_md.py` implementing G25a–d | 2.0 |
| Makefile target + temple-grade wiring + pre-commit registration | 1.0 |
| Semantic review vs injected instructions (R-E-1) + gate dry-run | 1.5 |
| **Total** | **≈10 h** (range 8–12 h) |

Sequencing note: validator script (task 4) lands BEFORE first content commit (task 2), per validator-first.

---

## §6 Validator-First Clause (Decree Art. XII)

**validator-first**: this spec ships its CI check in the same deliverable. No AGENTS.md content commit may precede the existence of `scripts/validate_agents_md.py` and the Makefile target below.

```makefile
# Makefile addition (ships with the validator script, before any content):
agents-md-validate:
	.venv/bin/python scripts/validate_agents_md.py --gates G25,G25a,G25b,G25c,G25d
temple-grade: agents-md-validate ## T2-family gate wiring (Makefile:232 pattern)
```

Validator behavior (`scripts/validate_agents_md.py`):
- Implements G25a–G25d exactly as specified in §3; exits non-zero on any failure (no warn-only theater — M23).
- Pre-content mode: `--gates G25` alone (existence check) passes trivially before reconstruction begins, proving the harness itself runs.
- Registered in `.pre-commit-config.yaml` alongside `omega-tracking-state` so drift is caught at commit time, not audit time (Art. II.4 pattern).

Self-verification (Decree §6): every directive herein maps to a gate — G25 (existence), G25a (dead cites), G25b (version coherence), G25c (content minimum), G25d (injection contradiction), G30 (this spec carries its guard). None is claim-without-mechanism.

---

## §7 Provenance & Lineage

| Input | Used for |
|---|---|
| SOVEREIGN_DECREE.md Art. VI, XII, §4 G25/G30, §5 Q-4 | Mission authority, default-GO, guard clauses |
| SYNTHESIS_ARM_REPORT.md §1 C-A, Exhibit C; §6 G14/G25/G27 patterns | Void evidence, gate patterns |
| ROC_DOC_ARCHAEOLOGY.md §1 P2/P4, §2, §4 five guards | Death-pattern analysis, risk section |
| Live census (commands in §1, run 2026-08-25 by lilith/node7) | Citer counts, cluster sizes, sampled expectations |
| Working notes | `data/council/20260825-094633-first-light-c2/phase1_nodes/N7_notes.md` |

*⬡ OMEGA ⬡ LILITH/NODE7 ⬡ SPEC-E v1.0 ⬡ PREP-ONLY ⬡ validator-first ⬡ 2026-08-25*
