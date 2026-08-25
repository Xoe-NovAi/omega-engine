# 🔱 P3 REPORT — NODE N3 ENGINEERING · Surface S4: `.opencode/commands/*.md`
**[DISPATCH] P12** | source_node: node3 | source_arm: maat | tier: leaf-recon | ts: 2026-08-25T14:2xZ
**Session**: 20260825-094633-first-light | **Task Registry**: `express-c1-node3-20260825` (registered)
**Mode**: RECON ONLY. Zero production mutations. This report is the sole artifact written outside reads.

---

## §0 SCOPE & METHOD

**Surface**: all 9 files in `.opencode/commands/`:

| File | Bytes | Last modified | Frontmatter agent |
|------|-------|---------------|-------------------|
| council-cloud.md | 19,025 | 2026-08-25 10:10 | `makali` |
| council-fast.md | 3,135 | 2026-08-25 07:14 | `kali` |
| council-local.md | 3,992 | 2026-08-25 07:14 | `kali` |
| kali-dispatch.md | 4,686 | 2026-08-25 06:08 | *(none)* |
| meditate.md | 19,024 | 2026-08-25 06:08 | `kali` |
| omega-meditation.md | 1,978 | 2026-08-25 06:08 | `kali` |
| researcher-discover.md | 3,491 | 2026-08-25 06:08 | `researcher` |
| researcher-synthesize.md | 5,554 | 2026-08-25 06:08 | `researcher` |
| researcher-verify.md | 6,737 | 2026-08-25 06:08 | `researcher` |

**Method**: exhaustive read of all 9 files; every referenced path/agent/skill/tool checked against
filesystem (`ls`/`test -e`), `.opencode/agents/` + `.opencode/agent/` inventories,
`.opencode/skills/` inventory, root `opencode.json`, `.opencode/MANIFEST.md` §7b,
`config/providers.yaml`, `config/entity_model_affinity.yaml`, and git history
(`git log --name-only -- .opencode/commands/`). Every finding below cites its evidence command/path.
No parametric synthesis (M23). No external search was needed — all grounding was local (T0).

**Security bright line (M8)**: no secrets and no active external telemetry found in any of the 9
command files. No CRITICAL-HALTED condition. (Note: root `opencode.json` loads plugin
`opencode-antigravity-auth@latest` — that is S7/N1 territory, flagged here only as provenance.)

**Git forensics**: ALL six First Light Express commits (`56abbba0..d0a9540c`) touched ONLY
`council-cloud.md`. `council-local.md` / `council-fast.md` last content change 2026-08-25 07:15 —
they never received the v2.1 topology fixes. This single fact explains findings F-01/F-02/F-11.

---

## §1 FINDINGS

### F-01 · HIGH · `council-local` / `council-fast` are pre-v2.1 fossils that violate the Loop Guard doctrine
**Tags**: source_node:node3 | tier:S4-command-currency

The v2.1 deadlock fix (commit `9c76e144`, then `58df0335`) established: MaKaLi is top-level
orchestrator; `agent: makali`; LOOP GUARD forbids invocation under kali. `council-cloud.md`
embodies this (frontmatter `agent: makali`, lines 3, 49-51). But:

- `council-local.md:3` → `agent: kali`
- `council-fast.md:3` → `agent: kali`

Per `council-cloud.md`'s own LOOP GUARD ("If this command is ever invoked by kali … STOP
immediately"), the two sibling commands institutionalize exactly the forbidden topology. An
Architect running `/council-local` tonight gets a Kali-run council with no MK-Kali synthesis arm,
no Consultant paging protocol (§ M11), no Delivered-Home Doctrine registration step, no Stage 6
quality gates, no Stage 7 Council-2 continuation — none of the six express commits exist in them.

**Additional divergence inside the same files** — the node taxonomy is an extinct generation:
- `council-local.md:31` lists Ma'at side as "N1, N3, N4, N5" — **N2 Persistence is silently dropped again**, despite `council-cloud.md:106` explicitly marking it "← RESTORED (was silently dropped)". Same drop in `council-fast.md:33`.
- `council-local.md:34-42` labels: N4=Security, N5=Operations, N6="runtime, soul, handoff", N7=Research, N8=Quality, N9=Scribe. Canonical mapping (council-cloud.md:104-116, meditate.md:158-161, mission packet §B): N4=Integration, N5=Governance, N6=Cognition, N7=Context, N8=Observability, N9=Orchestration. Two incompatible node universes coexist in the same commands directory.

**Acceptance criteria (bash-verifiable)**:
```bash
# AC-1: no council variant runs under the forbidden topology
! grep -q '^agent: kali' .opencode/commands/council-local.md .opencode/commands/council-fast.md
# AC-2: N2 present in every variant's build-side roster
grep -c 'N2' .opencode/commands/council-local.md && grep -c 'N2' .opencode/commands/council-fast.md   # ≥1 each
# AC-3: canonical node labels only
! grep -qE 'N4 \(Security\)|N5 \(Operations\)|N9 \(Scribe\)' .opencode/commands/council-local.md
```

### F-02 · HIGH · Artifact-contract divergence between council variants
**Tags**: source_node:node3 | tier:S4-overlap

The three council commands produce different final artifacts:
- cloud: `SYNTHESIS_ARM_REPORT.md` (Stage 3) + `SOVEREIGN_DECREE.md` (Stage 5) + `phase6_integration/tracker_updates.json`
- local (`council-local.md:57`): `FINAL_SYNTHESIS.md`
- fast (`council-fast.md:47`): `FINAL_SYNTHESIS.md`

Any downstream consumer (auto-GO gate plan §4 requires `SOVEREIGN_DECREE.md` written AND
committed; arms digesting `phase5_fusion/`) that points at a local/fast run finds no decree and no
synthesis-arm report. The overlap between the three variants is by design (three cost tiers), but
the *contract* must be invariant. Local/fast also lack the `phase1.5` digester CLI call and the
workspace-lock release step is abbreviated differently.

**Acceptance criteria**:
```bash
grep -q 'SOVEREIGN_DECREE' .opencode/commands/council-local.md .opencode/commands/council-fast.md
```

### F-03 · HIGH (cross-surface S7; primary owner N1) · `/council-cloud` runs on an agent whose instruction file does not exist
**Tags**: source_node:node3 | tier:S4↔S7-crosscheck

Root `opencode.json` defines:
```json
"makali": { "mode": "primary", "instructions": [".opencode/agents/plan.md"] }
```
but `.opencode/agents/plan.md` **does not exist** (verified: `ls .opencode/agents/plan.md` → No such file).
Same for `"grok_cli"` → `.opencode/agents/grok_cli.md` (**missing**). Meanwhile `.opencode/MANIFEST.md`
header claims "ghost agents removed" (2026-08-23) — the ghosts were removed from disk but their
config entries remain. Practical impact on MY surface: `/council-cloud` (frontmatter `agent: makali`)
launches the orchestrator with a dead instructions path — the entire Required Reading block
(council-cloud.md:330-346) may never load. Also confirmed root `opencode.json:3` →
`"subagent_depth": 2` — the F-20 constraint that makes leaf Consultant paging impossible is real
and config-side (see §4).

**Acceptance criteria**:
```bash
for f in $(jq -r '.agent[].instructions[]' opencode.json); do test -e "$f" || echo "DEAD: $f"; done
# expected output: DEAD: .opencode/agents/plan.md ; DEAD: .opencode/agents/grok_cli.md ; fix = zero DEAD lines
```

### F-04 · HIGH · `.opencode/MANIFEST.md` §7b Command Registry is stale (registry drift)
**Tags**: source_node:node3 | tier:S4-consistency

MANIFEST §7b (lines 126-137) lists **8** commands; the directory holds **9** (`omega-meditation.md`
unlisted). Worse, it attributes `/council-cloud` to agent `kali` (line 130) while the file's live
frontmatter says `agent: makali`. A future council consulting the Manifest gets the pre-v2.1 truth.
Manifest Updated stamp says 2026-08-23 — predates all six express commits of 2026-08-25.

**Acceptance criteria**:
```bash
diff <(ls .opencode/commands/*.md | xargs -n1 basename) \
     <(grep -oP 'commands/\K[a-z-]+\.md' .opencode/MANIFEST.md | sort -u)
# empty diff after fix; plus: grep -A2 '/council-cloud' .opencode/MANIFEST.md | grep makali
```

### F-05 · MED · `kali-dispatch.md`: no `$ARGUMENTS`, no `subtask` field, mandates a BROKEN tool, dead agent + dead log references
**Tags**: source_node:node3 | tier:S4-correctness

Verified counts (`grep -c`): `kali-dispatch.md` → `$ARGUMENTS: 0`, `subtask: 0`,
`extended_checkin: 1`. Specifics:
1. **Missing $ARGUMENTS handling**: body says "Break the user's query into 2-5 sub-tasks" but the
   user's query is never injected into the prompt — the agent sees only the static template.
   Every other command uses `$ARGUMENTS` (counts 1-5). 
2. **Frontmatter gap**: no `subtask:` field while all 8 siblings declare it (semantics unverified —
   that empirical question belongs to N6/S3 — but the inconsistency is textual fact).
3. **Broken tool mandated**: lines 75-79 instruct calling `hivemind_extended_checkin` "with a
   3-hour safety TTL". Plan §5 M1 declares this tool BROKEN server-side (`_save_extended_sessions`
   NameError) and the mission packet §C.7 says "do not use". Stale instruction.
4. **Dead agent reference**: Step 1 table includes `@quality` ("Code review"). No
   `.opencode/agents/quality.md`, no `quality` subagent_type in the runtime task-tool inventory;
   only a data/entities/quality/ soul dir remains. Dispatching @quality fails or hallucinates.
5. **Dead file reference**: footer — "see `data/coordination/DISPATCH_LOG.md` for usage history".
   File does not exist anywhere in the repo (verified via find).
6. Minor: `asyncio.gather` pseudo-code (line 43) in a fleet governed by M1 AnyIO — labeled
   pseudo-code, cosmetic.
7. Minor: heartbeat cadence "every 5-10 min" (line 54) vs plan §5 M5's unified ~10-min figure that
   explicitly "supersedes any '5 min' elsewhere".

**Acceptance criteria**:
```bash
grep -c '\$ARGUMENTS' .opencode/commands/kali-dispatch.md        # ≥1
grep -c 'extended_checkin' .opencode/commands/kali-dispatch.md   # 0 (or only "BROKEN — do not use")
grep -c '@quality' .opencode/commands/kali-dispatch.md           # 0
grep -c 'DISPATCH_LOG' .opencode/commands/kali-dispatch.md       # 0
```

### F-06 · MED · `omega-meditation.md`: no `$ARGUMENTS` injection; T-tier drift
**Tags**: source_node:node3 | tier:S4-correctness

`$ARGUMENTS: 0` occurrences, yet Usage section promises `/omega-meditation "Your problem statement
here"`. The problem statement never reaches the executing agent — the command is a description of
a pipeline, not an invocable one. Also: Stage 4 says "Sovereign Search (T0-T5)" while
council-cloud.md:195-204 and sovereign-search skill define the canonical 7-tier T0-T6. And the
file is a pure stub (45 lines) referencing stage outputs at `data/autonomous/{run_id}_XX_stage.md`
(dir exists with July 18 artifacts — pipeline ran once ~5 weeks ago; currency unproven since).

**Acceptance criteria**:
```bash
grep -c '\$ARGUMENTS' .opencode/commands/omega-meditation.md   # ≥1
grep -c 'T0-T6' .opencode/commands/omega-meditation.md         # ≥1
```

### F-07 · MED · `researcher-synthesize` / `researcher-verify`: D-121 observation log path is dead
**Tags**: source_node:node3 | tier:S4-dead-refs

Both commands mandate appending to `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md`
(synthesize line 71, verify line 65). That file exists ONLY in archive:
`data/archive/coordination/2026-07-04-to-2026-07-14/HIVEMIND_OBSERVATIONS_LOG.md` (verified via
find). The live coordination surface was consolidated 2026-08-22 (kali session addendum:
"coordination surface 23.7K→12.3K lines") and this log was archived without a successor pointer
being written back into the commands. Agents following D-121 today either fail or resurrect a
dead file. Everything else in the researcher trio checks out: `jem` agent exists, `scribe`
delegation target exists (`omega-hub_delegate_task`), workspace dirs exist, CREDITS.md §1.7
"Carmack's Law" and §5 "Right Approximation" verified in CREDITS_CANONICAL.md.

**Acceptance criteria**:
```bash
test -e data/coordination/HIVEMIND_OBSERVATIONS_LOG.md || grep -rn 'OBSERVATIONS_LOG' docs/strategy/HIVEMIND_PROTOCOL.md
# fix = either restore live log OR repoint both commands to successor (e.g., Hivemind post intent="observation") 
```

### F-08 · MED · Model-slug inconsistency across council-local/fast vs provider config
**Tags**: source_node:node3 | tier:S4-config-consistency

Three naming schemes for the same models:
| Source | Slug |
|---|---|
| council-local.md:32,38 / council-fast.md:33 | `lmstudio/qwen3-4b-thinking`, `lmstudio/krikri-8b` |
| config/providers.yaml lmster supported_models (:145-160) | `qwen3-4b-thinking-local`, `krikri-8b-local` (provider is `lmster`; no `lmstudio` provider name exists in providers.yaml) |
| config/entity_model_affinity.yaml | `qwen3-4b-thinking-q4_k_m`, `krikri-8b-q4_k_m` |

ICS_SYSTEM.md uses the `lmstudio/qwen3-4b-thinking` form, so the commands are consistent with
*docs* but not with *providers.yaml*. Whichever layer `oracle_summon_local` actually resolves
against determines whether these calls work; the ambiguity itself is the defect (an agent cannot
tell which scheme is authoritative).

**Acceptance criteria**:
```bash
grep -oP 'model: "\K[^"]+' config/entity_model_affinity.yaml | sort -u > /tmp/affinity.txt
grep -ohP '(lmstudio|lmster)/[a-z0-9.-]+' .opencode/commands/council-*.md | sort -u
# fix: slugs in commands must match ONE authoritative scheme documented in providers.yaml
```

### F-09 · LOW · `meditate.md` self-version conflict
Header line 8: "**Protocol**: `Meditate-v1.1`". Footer line 408: "Meditate-v1.2". Body contains
v1.2 features (Phase 00 registry, falsification attempt, invocation gate marked "v1.2").
Header stamp is stale.
```bash
# AC: grep -c 'Meditate-v1.1' .opencode/commands/meditate.md == 0
```

### F-10 · LOW · Typo + path-less references
- `council-fast.md:29`: "Hivemid heartbeat" → Hivemind.
- `council-cloud.md:340` (Required Reading #8): `ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` cited
  bare; actual location `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` (exists).
- `council-local.md:80`: `RECURSIVE_SPECIALIST_ROSTER.md` cited bare; actual location
  `data/entities/roc_racoon/workspace/RECURSIVE_SPECIALIST_ROSTER.md` (exists).
Path-less refs resolve for hydrated agents but fail cold-start agents.

### F-11 · INFO · Currency map (what is healthy)
For balance — verified GOOD on this surface:
- `council-cloud.md` is fully current: v2.1 topology, MK-Kali reservation rules, Consultant paging
  protocol, Delivered-Home Doctrine, all SIX auto-GO criteria (commit `45fa8429`), extended_checkin
  correctly marked BROKEN-do-not-use (line 80), digester fallback path defined (lines 146-148),
  `src/omega/council/report_digestion.py` EXISTS (module CLI claim verified).
- `meditate.md` deep-checked: MEDITATION_REGISTRY.md, templates/, records/,
  MEDITATION_SYSTEM_GUIDE.md, NODE_EXPERT_SESSIONS_PLAN.md all EXIST; lens table matches canonical
  node mapping; D-586 bridge intact.
- Researcher trio: jem/scribe/researcher agents exist; workspace paths exist; CREDITS anchors exist.
- Skills cross-refs: `sovereign-search`, `makali-council-coordinator`, `meditate-research-pipeline`
  all present in `.opencode/skills/`.

---

## §2 OVERLAP ANALYSIS — THE THREE COUNCIL VARIANTS

| Dimension | council-cloud | council-local | council-fast |
|---|---|---|---|
| Orchestrator agent | makali (v2.1) ✅ | kali (pre-v2.1) ❌ | kali (pre-v2.1) ❌ |
| Node set | N1-N10 incl. N2 ✅ | N1,N3-N10, N2 dropped ❌ | same ❌ |
| Node taxonomy | canonical ✅ | legacy labels ❌ | unlabeled ⚠️ |
| Synthesis arm | MK-Kali fresh session ✅ | Kali inline ❌ | Kali inline ❌ |
| Final artifact | SOVEREIGN_DECREE.md ✅ | FINAL_SYNTHESIS.md ❌ | FINAL_SYNTHESIS.md ❌ |
| Consultant paging (M11) | yes ✅ | absent ❌ | absent ❌ |
| Delivered-Home Doctrine | yes ✅ | absent ❌ | absent ❌ |
| Quality gates | full (T1-T11 etc.) ✅ | full list, no decree ⚠️ | minimal ⚠️ |
| Search depth | T0-T6 ✅ | T0-T6 ✅ | T0-T2 by design ✅ |
| Research grounding | yes ✅ | yes ✅ | no (by design) ✅ |

**Verdict**: the three-tier design is sound and should be kept, but local/fast were never migrated
to Topology v2.1. They are one major version behind and structurally contradict the flagship
command's LOOP GUARD. Recommended remediation (Council 2 spec material): regenerate local/fast
from the cloud template as parameterized deltas (routing table + gate set), keeping one shared
contract section verbatim-included so drift becomes mechanically impossible.

## §3 SUBTASK FLAG SEMANTICS (textual audit; empirical behavior = N6/S3)

All files except `kali-dispatch.md` declare `subtask: false`. Rationale appears correct for
council/meditate commands (they must run as the interactive session's own flow, not as nested
subtask UI entries). `researcher-*` commands declare `agent: researcher, subtask: false` — meaning
typing `/researcher-discover` re-personas the CURRENT session as researcher, who then task()s jem.
Whether OpenCode honors `subtask` on commands at all is an S3 empirical question — flagged for N6,
not adjudicated here (no parametric synthesis).

## §4 HANDOFF PACKET (Delivered-Home Doctrine)

**Warm-start reading list for any future council paging domain:N3-engineering / S4-commands**:
1. This report (findings F-01..F-11 with acceptance criteria)
2. `.opencode/commands/council-cloud.md` — the only fully-current command; treat as template SSOT
3. `.opencode/MANIFEST.md` §7b — read as KNOWN-STALE until F-04 fixed
4. Root `opencode.json` `agent` block — cross-check every `instructions[]` path (F-03)
5. Git: `git log --oneline --name-only -- .opencode/commands/` — express commits touched cloud only
6. Plan §2 S4 row + mission packet §B (scope authority)

**Standing orders for future councils**:
- Never trust MANIFEST §7b for inventory; `ls .opencode/commands/` is ground truth.
- Any edit to council-cloud.md MUST be propagated (or explicitly declined-with-reason) to
  council-local/fast in the SAME commit — they share a contract, not just a prefix.
- Before adding a command: frontmatter needs `description`, `agent`, `subtask`; body MUST
  reference `$ARGUMENTS` if the command accepts input; every file/agent/tool named in the body
  must pass `test -e` / agent-inventory check at commit time (candidate for a pre-commit hook).
- F-20 context: `subagent_depth: 2` (root opencode.json:3) means command-authored flows that
  assume leaf→Consultant pages will mechanically fail; route reports via arm instead (this run's
  live proof is in §5).

**Open questions (for research/synthesis stages)**:
- Does OpenCode actually substitute `{session_model}` in command bodies? (N6/S3)
- Is `subtask:` a live field on commands? (N6/S3)
- Which slug scheme does `oracle_summon_local` resolve first — providers.yaml `-local` names or
  affinity-file quant names? (determines F-08 fix direction)

---

## §5 F-20 / M23 DELIVERY NOTE (appended post-page-attempt)

Per §C.9 the LAST step is paging the Consultant (`ses_fdef2be4effe4pAaLXCTUx62GO`). Awareness at
start already showed node1/node6 hit "Subagent depth limit reached (2)" — root cause confirmed by
me at `opencode.json:3`. I attempted the page once per protocol; result recorded in my end-of-task
summary to arm maat. Per M23 failure-integrity: report delivery = this file on disk + Hivemind
broadcast + summary-to-pager. No retries beyond one.

---
*⬡ OMEGA ⬡ NODE3 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_s4 ⬡ 2026-08-25*
