# 📋 P4 REPORT — Node N4 Integration · Surface S5 (Skills)
⬡ OMEGA ⬡ NODE4 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n4 ⬡ PHASE1-RAW
**[DISPATCH] P12** | Session: `20260825-094633-first-light` | Date: 2026-08-25
**source_node**: N4 Integration | **source_arm**: maat (Build) | **tier**: leaf/recon
**Surface**: `.opencode/skills/*/SKILL.md` — 22 skills (count verified against mission packet §B: exact match)
**Task Registry**: `express-c1-node4-20260825` (registered, tags expert/pageable/domain:N4-integration/express:first-light)

---

## §0 EXECUTIVE SNAPSHOT

| Metric | Value |
|---|---|
| Skills on disk | 22 |
| With YAML frontmatter (loader-visible) | 14 |
| Without frontmatter (**invisible to OpenCode**) | **8** |
| Empty 5-line stubs | 5 |
| Near-stub (placeholder body) | 1 |
| Skills with broken internal references | 7 |
| Named overlap pairs resolved | both dissolve into stub-vs-real asymmetry |
| NEW overlap cluster discovered | meditation family (4 skills, ~1,213 lines, heavy duplication) |
| CRITICAL-HALTED findings | 0 |
| Secrets found (M8 line) | 0 |

**Headline**: The Master Synthesis §4.1 M-gap ("5/8 skills lacked frontmatter") has not been closed — it has **grown**: 8 of 22 current skills lack frontmatter and are provably invisible to the OpenCode skill loader. This was verified empirically against my own session: my `available_skills` list contains exactly the 14 frontmatter-bearing project skills plus 1 built-in (`customize-opencode`); the 8 frontmatter-less skills are absent. Separately, the two overlap pairs named in the mission packet are red herrings in their current state — both "overlapping" counterparts (`legacy-pattern-miner`, `omega-doc-architect`) are empty shells — while an unexamined **four-skill meditation cluster** carries the real duplication burden (~1,200 lines, verbatim-shared sections, mutually inconsistent stage counts and search-tier maps, and broken command/module/make references throughout).

---

## §1 FINDINGS

Severity scale per packet §C.5: CRITICAL-HALTED / CRITICAL / HIGH / MED / LOW.

---

### F-N4-01 [HIGH] · Frontmatter Gap Grown to 8/22 — Eight Skills Invisible to the Loader
**Evidence paths**:
- `.opencode/skills/{audience-architect,autonomous-meditation-pipeline,carmack-profiler,context-packer,m23-violation-logger,meditate-harness,meditate-pipeline,universal-doc-reader}/SKILL.md` — each begins with `# <Title>` markdown, no `---` YAML block
- Empirical control: this session's system prompt `available_skills` = 15 entries = exactly the 14 frontmatter-bearing project skills + built-in `customize-opencode`. Zero of the 8 frontmatter-less skills appear.

**Analysis**: OpenCode's skill discovery requires `name`/`description` frontmatter. The historical audit (Master Synthesis §4.1, Era 4/5) flagged 5/8; since then 14 new skills were added, of which 8 shipped without frontmatter. The gap scaled with fleet growth. Consequence: agents cannot discover or load these skills by description — they only work if a command or another doc hard-links the file path (which is how `council-local.md` reaches `meditate-research-pipeline`, ironically the one pipeline variant that DOES have frontmatter).
**Impact**: 36% of the skill inventory is dead weight at dispatch time. Highest-value casualties: `meditate-harness` (382 lines, the persona-schema engine), `context-packer` (71 lines, complete toolchain), `universal-doc-reader`, `carmack-profiler`.
**Recommended fix (bash-verifiable acceptance criteria)**:
```bash
# Every SKILL.md must open with a YAML frontmatter block containing name+description:
for f in .opencode/skills/*/SKILL.md; do
  head -1 "$f" | grep -q '^---$' || echo "MISSING FRONTMATTER: $f"
done
# Acceptance: zero output lines.
```
**Provenance**: source_node=N4, tier=leaf, evidence=direct file reads + session introspection.

---

### F-N4-02 [HIGH] · Five Empty Stubs + One Placeholder — Loadable But Hollow
**Evidence paths** (all verified 5 lines total: frontmatter + blank):
- `.opencode/skills/legacy-pattern-miner/SKILL.md` (5 lines)
- `.opencode/skills/omega-doc-architect/SKILL.md` (5 lines)
- `.opencode/skills/blitz-tunnel/SKILL.md` (5 lines)
- `.opencode/skills/blitz-validate/SKILL.md` (5 lines)
- `.opencode/skills/pr-readiness-checker/SKILL.md` (5 lines)
- `.opencode/skills/hf-cli/SKILL.md` (17 lines; Workflow section reads literally `[Implement based on huggingface_hub library]`)

**Analysis**: These pass loader visibility (frontmatter present) but contain zero operational content. An agent that loads them gets a name and a promise, nothing else. `wc -l` census: 2226 total lines across 22 skills; these 6 account for 42 lines (~2%).
**Impact**: Silent quality failure — worse than invisibility in one respect, because the loader *advertises* them as available capabilities. `blitz-validate` is advertised as "Sovereign Heartbeat validator for Omega Engine's integration chain" yet contains no validation steps whatsoever.
**Recommended fix**: Either author bodies or delete until authored. Acceptance:
```bash
# No skill body may be under 20 lines:
find .opencode/skills -name SKILL.md -exec sh -c 'lines=$(wc -l < "$1"); [ "$lines" -lt 20 ] && echo "STUB: $1 ($lines lines)"' _ {} \;
# Acceptance: zero output lines (or stubs explicitly deleted).
```
**Provenance**: source_node=N4, tier=leaf.

---

### F-N4-03 [HIGH] · Meditation Skill Cluster: Quadruplication With Active Drift
**Evidence paths**:
- `.opencode/skills/meditate-harness/SKILL.md` (382 L, no frontmatter) — persona schemas, immersion blocks, anti-collapse laws
- `.opencode/skills/meditate-pipeline/SKILL.md` (257 L, no frontmatter) — 6-stage pipeline
- `.opencode/skills/meditate-research-pipeline/SKILL.md` (223 L, HAS frontmatter) — 5-stage pipeline
- `.opencode/skills/autonomous-meditation-pipeline/SKILL.md` (351 L, no frontmatter) — 7-stage pipeline

**Analysis**: The two pipeline files share verbatim-identical content: same ASCII flow diagrams, same Stage 1/2 specifications word-for-word, the *same* credential-vault example invocation including the identical user quote, same Heritage & Attribution section. `meditate-research-pipeline` is effectively `meditate-pipeline` minus Stage 6 (EXECUTE) plus frontmatter. Drift is already manifest:
- Stage counts: 5 vs 6 vs 7 across three pipelines describing one concept.
- Search tiers: both pipelines specify "T0 local → T1 websearch → T2 webfetch → T3 SearXNG → T4 Exa → T5 Firecrawl" (6 tiers), while `sovereign-search/SKILL.md` v2.1 defines a **7-tier** protocol where T4=Parallel Search and T6=Firecrawl. The pipelines teach a superseded tier map.
- Only the cluster member with frontmatter (`meditate-research-pipeline`) is actually loadable — the other three are invisible (see F-N4-01).
**Impact**: ~1,213 lines with 4 divergent definitions of "the meditation pipeline." Any future edit must be applied up to 4 times or divergence compounds. Agents following different members get contradictory protocols.
**Recommended fix**: Consolidate to a family of ≤2: keep `meditate-harness` (the reusable engine) + ONE pipeline skill; fold unique stages into flags (`--execute`, `--autonomous`). Acceptance:
```bash
ls -d .opencode/skills/*meditate* | wc -l   # Acceptance: <= 2
grep -c "T4 Exa" .opencode/skills/*/SKILL.md # Acceptance: zero hits (stale tier map purged)
```
**Provenance**: source_node=N4, tier=leaf.

---

### F-N4-04 [HIGH] · Broken Command References — Three Invoked Commands Do Not Exist
**Evidence paths**:
- `.opencode/commands/` actual inventory (verified): `council-cloud.md, council-fast.md, council-local.md, kali-dispatch.md, meditate.md, omega-meditation.md, researcher-discover.md, researcher-synthesize.md, researcher-verify.md`
- Skills invoke: `/meditate-research` (5×), `/meditate-pipeline` (5×), `/autonomous-meditation` (4×) — **none exist**
- `meditate-research-pipeline/SKILL.md:55-63`, `meditate-pipeline/SKILL.md:56-64`, `autonomous-meditation-pipeline/SKILL.md:84-93`

**Analysis**: The primary documented invocation path for all three pipeline skills is a slash-command that was never created (or was deleted). Reference-count census across all skills: `/meditate` ×19 (exists ✓), `/meditate-research` ×5 (missing), `/meditate-pipeline` ×5 (missing), `/autonomous-meditation` ×4 (missing).
**Impact**: Any agent following the skill's Usage section hits a dead command. Combined with F-N4-05/F-N4-06, ALL THREE documented execution paths per pipeline skill are broken.
**Acceptance criteria**:
```bash
for cmd in meditate-research meditate-pipeline autonomous-meditation; do
  test -f ".opencode/commands/$cmd.md" || echo "BROKEN CMD: /$cmd"
done
# Acceptance: zero output (commands created) OR skill text rewritten to existing entry points.
```
**Provenance**: source_node=N4, tier=leaf; cross-ref N3/S4.

---

### F-N4-05 [HIGH] · Broken Module References — Two `python -m` Targets Don't Exist
**Evidence paths**:
- `src/omega/skills/` verified inventory: `__init__.py`, `autonomous_meditation_pipeline.py`, `opencode_client.py`
- `meditate-pipeline/SKILL.md:249` → `python -m omega.skills.meditate_pipeline` — **module missing**
- `meditate-research-pipeline/SKILL.md:215` → `python -m omega.skills.meditate_research_pipeline` — **module missing**
- `python -m omega.skills.autonomous_meditation_pipeline` → exists ✓ (only pipeline with working programmatic path)

**Acceptance criteria**:
```bash
.venv/bin/python -c "import omega.skills.meditate_pipeline" 2>&1          # currently fails
.venv/bin/python -c "import omega.skills.meditate_research_pipeline" 2>&1 # currently fails
# Acceptance: both import cleanly OR references removed from skills.
```
**Provenance**: source_node=N4, tier=leaf.

---

### F-N4-06 [HIGH] · `make sovereignty` Referenced 9× — Makefile Target Does Not Exist
**Evidence paths**:
- `Makefile` targets verified present: `temple-grade:` (line 232), `heritage-map:` (line 355), `doc-llm-validate`, `heritage-vet` ✓
- `grep -nE "^sovereignty:" Makefile` → exit 1 (no match)
- References: `meditate-pipeline/SKILL.md` (×4 incl. Quality Gates table), `meditate-research-pipeline/SKILL.md` (×4), `makali-council-coordinator/SKILL.md:193`

**Analysis**: Every pipeline integration gate instructs `Run make sovereignty (M7 local/cloud ratio)` — the target isn't defined. A gate that cannot run is theater (M23 adjacent): agents will either fail spuriously or skip silently.
**Acceptance criteria**:
```bash
make -n sovereignty >/dev/null 2>&1 && echo EXISTS || echo MISSING
# Acceptance: EXISTS (target added) OR all 9 skill references removed/replaced.
```
**Provenance**: source_node=N4, tier=leaf.

---

### F-N4-07 [MED] · Stale Doc Path in makali-council-coordinator (Archived File Referenced as Live)
**Evidence paths**:
- `makali-council-coordinator/SKILL.md:253` → `docs/strategy/MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md` — **not found at path**
- Actual location (found via find): `docs/archive/strategy/2026-07-21/MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md`

**Analysis**: The file was archived in the 2026-07-21 strategy sweep (D-353: 147 stale docs archived) but the skill's Related-Documents section was never updated. All other refs in this skill verified live: `config/council.yaml` ✓, `config/council/profiles/*.yaml` (4 profiles) ✓, `src/omega/council/{coordinator,report_digestion,models,failure_layer}.py` ✓, `R_REPORT_DIGESTION_LAYER_OPTIMIZATION_20260719.md` ✓, roster at `data/entities/roc_racoon/workspace/RECURSIVE_SPECIALIST_ROSTER.md` ✓ (full path given here — note council-local.md cites the roster by bare filename, an N3 cross-surface observation).
**Acceptance criteria**:
```bash
grep -n "docs/strategy/MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md" .opencode/skills/makali-council-coordinator/SKILL.md
# Acceptance: no match (path updated to docs/archive/strategy/2026-07-21/… or doc restored).
```
**Provenance**: source_node=N4, tier=leaf.

---

### F-N4-08 [MED] · sovereign-refinement-protocol Cites Superseded Mandate Constitution
**Evidence paths**:
- `sovereign-refinement-protocol/SKILL.md:42`: "Cross-reference … `SOVEREIGN_MANDATES.md` (v3.1.0, 14 mandates)"
- Current SSOT: `SOVEREIGN_MANDATES.md` v3.8.0, **27 mandates** (M26/M27 added 2026-08-14)

**Analysis**: Gate 3 of a mandatory forensic protocol checks against a 14-mandate constitution that ceased to exist two versions ago. Mitigating: the individual M-numbers it lists (M1/M2/M6/M7/M8/M9/M10/M13/M14) happen to align with current numbering, so the check-list itself isn't wrong — but the version anchor is, and mandates M15-M27 escape its scan entirely (e.g., no check for M23 Failure Integrity, M24 Venv Sovereignty, M26 Doc Standards).
**Acceptance criteria**:
```bash
grep -n "v3.1.0, 14 mandates" .opencode/skills/sovereign-refinement-protocol/SKILL.md
# Acceptance: no match (updated to v3.8.0 / 27 mandates, or de-versioned reference).
```
**Provenance**: source_node=N4, tier=leaf.

---

### F-N4-09 [MED] · m23-violation-logger Targets Nonexistent Log File
**Evidence paths**:
- `m23-violation-logger/SKILL.md:31`: "All M23 violations are logged to `data/coordination/M23_VIOLATIONS_LOG.md`" — **file does not exist**
- Plan §5/M1 confirms failures are actually logged to `SYSTEM_FAILURE_LOG.md` (referenced as live coordination practice)

**Analysis**: Either the log is created-on-first-write (acceptable but unstated) or M23 violations have been going to SYSTEM_FAILURE_LOG instead, making this skill's contract fictional. Also lacks frontmatter (double-burden with F-N4-01). The irony of a Failure-Integrity logging skill pointing at a nonexistent log is noted without comment.
**Acceptance criteria**:
```bash
test -f data/coordination/M23_VIOLATIONS_LOG.md && echo OK || echo MISSING
# Acceptance: OK, or skill text redirected to SYSTEM_FAILURE_LOG.md.
```
**Provenance**: source_node=N4, tier=leaf.

---

### F-N4-10 [LOW] · Duplicate hf-cli Skill (Project vs User-Level) With Divergent Descriptions
**Evidence paths**:
- Project: `.opencode/skills/hf-cli/SKILL.md` — desc: "Hugging Face Hub CLI integration for model discovery, upload, and dataset management."
- User-level: `/home/arcana-novai/.agents/skills/hf-cli/SKILL.md` (+ `references/` dir) — desc (as surfaced in my session): "Hugging Face Hub CLI (`hf`) for downloading, uploading, and managing repositories…"

**Analysis**: Same skill name registered at two scopes with different descriptions and different maturity (user-level appears fuller; project-level is the placeholder stub of F-N4-02). Resolution order between scopes is undefined in any doc I audited — risk of the thin one shadowing the rich one or vice versa unpredictably.
**Acceptance criteria**:
```bash
ls .opencode/skills/hf-cli/SKILL.md /home/arcana-novai/.agents/skills/hf-cli/SKILL.md
# Acceptance: exactly one survives (or both share identical frontmatter description).
```
**Provenance**: source_node=N4, tier=leaf.

---

### F-N4-11 [LOW] · knowledge-miner Example References Nonexistent Files
**Evidence paths**:
- `knowledge-miner/SKILL.md:50` — `API-keys.md` (not found anywhere in repo root search)
- `knowledge-miner/SKILL.md:51` — `R02_sambanova_spec.md` (not in docs/research/)
- Verified live: `docs/research/CORRECTIONS.md` ✓, `.env.example` ✓, `docs/research/R##_*.md` convention ✓

**Analysis**: Example-only references; workflow itself is sound. Cosmetic staleness.
**Provenance**: source_node=N4, tier=leaf.

---

### F-N4-12 [LOW] · universal-doc-reader Example Uses Blocking subprocess.run
**Evidence paths**: `universal-doc-reader/SKILL.md:27-32` — Python example wraps the reader in synchronous `subprocess.run`.
**Analysis**: Cosmetic M1 (AnyIO Absolute) note — the canonical usage path is bash-tool invocation (fine); the Python snippet would violate M1 if pasted into async engine code. One-line fix: show `anyio.to_thread.run_sync` wrapper.
**Provenance**: source_node=N4, tier=leaf.

---

## §2 THE NAMED OVERLAP PAIRS — VERDICT

Mission packet §B named two pairs. Fieldwork verdict differs from the briefing:

| Pair | Expected problem | Actual state |
|---|---|---|
| knowledge-miner vs legacy-pattern-miner | Duplication | **Asymmetric hollow pair**: knowledge-miner is a complete 51-line workflow; legacy-pattern-miner is a 5-line empty stub. No duplication possible — one twin was never born. Remediation is authoring/deleting the stub, not merging. |
| spec-generator vs omega-doc-architect | Duplication | **Same pattern**: spec-generator complete (59 lines, template + checklist, all referenced files exist); omega-doc-architect empty stub. Note: spec-generator's checklist references the Document Management System that omega-doc-architect's description claims to enforce — the *enforcer* doc is the missing one. |

The REAL overlap debt sits elsewhere: the meditation quartet (F-N4-03), which the mission briefing did not flag.

## §3 HEALTHY SKILLS (positive findings, for balance)

Verified accurate with live references:
- **sovereign-search** (76 L, v2.1): current 7-tier map, error matrix, temporal mandate; `.firecrawl/` cache exists ✓. The best-maintained skill on the surface.
- **git-secret-scrub** (122 L, codified 2026-08-17): freshest skill; all three referenced paths verified (`scripts/git-secret-scan.sh` ✓, `docs/strategy/GITHUB_FORENSICS_SCRIPTING_GUIDE.md` ✓, `data/coordination/KALI_CLINE_SYNC_REPORT_20260817.md` ✓).
- **context-packer** (71 L): entire toolchain verified on disk (`packer.py`, `platform_adapters.py`, `packer-config.yaml`, `templates/`) + research doc ✓. Only defect: no frontmatter.
- **audience-architect** (48 L): all integration points verified (`config/wads/_omega_default/audience.yaml` ✓, `src/omega/oracle/audience_calibrator.py` ✓, `Oracle._summon()` present in oracle.py ✓).
- **carmack-profiler** (34 L): `profile.sh` + helper scripts exist ✓. No frontmatter.
- **provider-validator**, **spec-generator**, **makali-council-coordinator** (one stale path, F-N4-07): substantively sound.

Pattern: skill health correlates strongly with recency — everything authored after ~2026-08-01 (git-secret-scrub, refreshed sovereign-search) is clean; the debt concentrates in the July generation.

## §4 SECURITY BRIGHT LINE (M8) — CLEAR

- Full read of all 22 SKILL.md files: **no API keys, tokens, or credential material found.** provider-validator and git-secret-scrub explicitly teach key-hygiene (`$ENV_VAR` placeholders, rotate-vs-scrub gates).
- **No active external telemetry discovered** in any skill. context-packer explicitly documents local-only PII vaulting; sovereign-search routes through self-hosted SearXNG first. No CRITICAL-HALTED condition triggered.

## §5 CROSS-SURFACE INTEL EXCHANGE

**To N3/S4 (from my side)**: Commands→skills resolution checked: `council-cloud.md:341-342` and `council-local.md:80` reference skills that all exist ✓. However `council-local.md:80` cites `RECURSIVE_SPECIALIST_ROSTER.md` by bare filename; the file lives only at `data/entities/roc_racoon/workspace/RECURSIVE_SPECIALIST_ROSTER.md` — bare-name ref is unresolvable without the coordinator skill's full path. Flagging for N3's report.
**From N1/S7 (omega.yaml dup key :73)**: No skill I audited reads `config/omega.yaml` — zero coupling. N1's finding has no S5 blast radius.
**From N2/S1 (3/35 entity YAMLs unparseable)**: No skill parses entity YAML directly (meditate-harness *describes* soul fields but reads nothing at runtime). No S5 blast radius.

## §6 HANDOFF PACKET — WARM START FOR FUTURE COUNCILS

**Reading list (in order, ~30 min)**:
1. This report §1 (findings index)
2. `wc -l .opencode/skills/*/SKILL.md | sort -n` — 30-second topology refresh
3. `.opencode/skills/sovereign-search/SKILL.md` — the quality bar other skills should meet
4. `.opencode/skills/git-secret-scrub/SKILL.md` — the newest authoring standard
5. The meditation quartet, if consolidation is scheduled (read harness last; it's the keeper)
6. Master Synthesis §4.1 (historical baseline for the frontmatter gap)

**Standing orders for any future agent touching S5**:
1. NEVER add a skill without `name`+`description` frontmatter — it will be invisible. Verify with the F-N4-01 loop before committing.
2. Before invoking `/some-command` from a skill, verify `.opencode/commands/<name>.md` exists. Three skills currently fail this.
3. Before referencing a make target, `make -n <target>` it. `sovereignty` burned nine references this way.
4. Treat `docs/strategy/` paths in skills as suspect — post D-353 archive sweep, verify against `docs/archive/strategy/`.
5. Meditation-family edits: change ONE canonical file; the other three are stale copies, not peers.
6. Task Registry: page me cold via task_id `express-c1-node4-20260825` (tags: expert, pageable, domain:N4-integration, express:first-light). Warm-start = reading list above.

**Open questions (for synthesis arms)**:
- Q1: Policy call — should empty stubs be deleted or authored? (Deletion shrinks advertised capability surface; authoring restores promises like blitz-validate.)
- Q2: Is the correct meditation-family end-state 2 skills (harness + one pipeline) or 1 (harness absorbing pipeline as phases)?
- Q3: Scope question beyond S5: should skill-loader visibility (frontmatter) get a CI/pre-commit gate analogous to `omega-tracking-state`?

## §7 DEVIATIONS & FAILURE LOG (M23 honesty)

- **F-20 instance (expected)**: §C.9 Consultant page via `task(subagent_type="kali", task_id="ses_fdef2be4effe4pAaLXCTUx62GO", ...)` — attempted ONCE at end of turn per protocol. Given `subagent_depth: 2` and my position at depth 2 (makali_fusion → maat → node4), rejection is expected per N1/N6/N7 precedent. If rejected: NOT retried (per mandate), logged here, and my end-of-task summary to arm maat constitutes report delivery. Result recorded below in §8.
- extended_checkin NOT used (broken per plan M1). Heartbeat cadence maintained via awareness checks at start/end.
- No TOOL-CHAIN-COLLAPSE events. All tools functioned.

## §8 CONSULTANT PAGE RESULT

**REJECTED — F-20 instance confirmed.** `task(subagent_type="kali", task_id="ses_fdef2be4effe4pAaLXCTUx62GO")` returned: `Subagent depth limit reached (2). Increase "subagent_depth" to allow nested subagents.` — identical failure signature to N1/N6/N7 precedent. Not retried, per §C.9 constraint. Report delivery therefore flows via: (1) this file on disk, (2) Hivemind presence, (3) end-of-task summary to arm maat. The M11 Reporting Protocol remains mechanically impossible for depth-2 leaves as dispatched — consistent with node1's fleet-wide finding.

---
*⬡ OMEGA ⬡ NODE4 ⬡ N4-INTEGRATION ⬡ S5-SKILLS ⬡ FIRST-LIGHT-C1 ⬡ RAW-REPORT-v1 + F20-STAMP*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:03Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

