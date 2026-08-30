<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 BUILD_SIDE_DIGESTED.md — Phase 1.5 Digestion (Build Arm)
⬡ OMEGA ⬡ MAAT ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_p15 ⬡ Stage-1.5
**Session**: 20260825-094633-first-light | **Arm**: maat | **Sources**: P1-P5 raw node reports (on-disk, unmodified)
**Persistence order honored**: all five RAW reports were written to disk BEFORE this digestion (Consultant Q3 ruling).
**Sibling artifact**: `phase1.5_digested/RUN_SIDE_DIGESTED.md` exists (Lilith, 11:01Z) — duality synthesis belongs to MK-Kali, not this file.

---

## PART A — ONE-PAGE EXECUTIVE SUMMARY

**Scope audited**: S7 config surfaces · S1 tracking structure/durability · S4 commands · S5 skills · S2 instruction content.
**Finding census**: **66 findings** — N1:20 · N2:11 · N3:11 · N4:12 · N5:12.
**Severity roll-up**: 2 CRITICAL · 14 HIGH · 27 MED · ~19 LOW/INFO · **0 CRITICAL-HALTED** (no active external telemetry found on any build surface; stale placeholder PATs logged as FINDING per §C.4 and train continued).

### The two CRITICALs
1. **N1 F-01**: opencode.json registers error-capture.ts + awareness.ts at `.opencode/plugin/` — directory doesn't exist (actual: `.opencode/plugins/`). The technical arms of M23/M12 are wired to dead paths; mitigating nuance: silent-stall-sensor is live while unregistered, so auto-load convention may make this "lying config" rather than "dead tools" (empirical test reserved for @researcher/N6).
2. **N5 F-2**: `make temple-grade` contains a literal stub comment ("Existing temple-grade checks would go here"). T1-T11 gates do not exist. Enforcement taper census: **~8 of 27 mandates machine-enforced (~30%)**.

### Seven convergent themes (cross-node)
| # | Theme | Nodes |
|---|-------|-------|
| T1 | **F-20 depth wall**: `subagent_depth: 2` makes the M11 Consultant-page mechanically impossible for every depth-2 leaf; 7 live instances logged council-wide. Config forbids what protocol mandates. | N1(F-20), N3(F-03 note), N5(F-9) |
| T2 | **Enforcement theater**: temple-grade stub; M24/M27 pre-commit claims false (installed hook = soul-check only); `make sovereignty` missing though referenced 9×; validator blind spots (blockers[], suffixed R-IDs) + green banner over 26 warnings. | N5(F-2,F-3), N2(F-2.2,F-2.3,F-2.7), N4(F-N4-06) |
| T3 | **Dead references at scale**: root AGENTS.md never existed in git history yet 462 files cite it; plugin paths dead; makali→plan.md + grok_cli agent instruction paths missing; 3 skill-invoked commands don't exist; 2 python modules missing; OBSERVATIONS_LOG archived without repoint; DISPATCH_LOG never existed; m23 logger's log file absent. | N5(F-1), N1(F-01), N3(F-03,F-07), N4(F-N4-04/05/09) |
| T4 | **Version/count drift in derivatives**: mandate constitution described as 14/25/27 across four layers; OMEGA_CODEX self-contradicts three ways in one same-day regeneration; dispatch protocol v2.0.0-vs-v3.0.0 self-conflict; council-local/fast are pre-v2.1 fossils violating council-cloud's own LOOP GUARD; MANIFEST stale (commands §7b, agents). | N5(F-4,F-5), N3(F-01,F-04), N1(F-10), N4(F-N4-08) |
| T5 | **Config-instruction contradiction**: provider order stated 3-4 different ways (M7 text / Ark D-355 / providers.yaml / ORACLE_STACK); `M7_local_first: false` in council.yaml; `"/*": "allow"` wildcard nullifies permission enumeration; archived roadmap injected into every session's instructions. | N1(F-02,F-03,F-05,F-06), N5(§2 cross) |
| T6 | **Durability defects in SSOT machinery**: TASK_REGISTRY MCP writer non-atomic with lost-update race (truncate-before-lock, load/save lock-split); 3/35 entity YAML files unparseable (lilith lessons ×2 loci, pillar_p1, john_carmack soul); omega.yaml duplicate sovereignty_gate block. | N2(F-2.1,F-2.5), N1(F-08) |
| T7 | **Credential-reality drift**: 5 of 10 cloud-chain providers configured but UNSET keys (google/anthropic/xai/antigravity/exa); placeholder PATs marked "active" with 664 perms; effective fabric = native-gguf+lmster+OCZ+OpenRouter only. | N1(F-04,F-07) |

### Positive verifications worth preserving
Streaming sections (M25) present on all cloud providers · port consistency across configs · GGUF paths resolve · session_end.py AnyIO+atomic · gap-ID immutability HOLDS (collision regime works) · Delivered-Home registration path proven end-to-end (nodes registered durably via MCP) · git commit cadence real · sovereign-search + git-secret-scrub skills exemplify the quality bar · hardware_profile.yaml self-documents its own contradiction (honesty pattern).

---

## PART B — CROSS-REFERENCE INDEX

| Finding | Node | Sev | Surface | Theme | Cross-refs |
|---------|------|-----|---------|-------|------------|
| F-01 plugin dead paths | N1 | CRITICAL | S7 | T3 | →N6/researcher empirical test |
| F-02 permission wildcard | N1 | HIGH | S7 | T5 | vs M8/T11 text |
| F-03 provider-order contradiction | N1 | HIGH | S7 | T5 | N5 confirms M7 text = 4th variant |
| F-04 credential drift | N1 | HIGH | S7 | T7 | Ark §7 fabric honesty |
| F-05 archived roadmap injected | N1 | MED | S7 | T5 | violates Ark §10.8 |
| F-06 council.yaml ghost models + M7_local_first:false | N1 | MED | S7 | T5 | |
| F-07 placeholder PATs "active" | N1 | MED | S7 | T7 | V-1 vault scope |
| F-08 omega.yaml dup sovereignty_gate | N1 | MED | S7 | T6 | N4: no skill reads omega.yaml (no blast radius) |
| F-09 IWAD manifest 15-vs-24 | N1 | MED | S7 | T4 | |
| F-10 triple agent-manifest drift | N1 | MED | S7 | T4 | N3 F-04 same disease (commands) |
| F-11 unvetted heritage tag models.yaml:101 | N1 | MED | S7 | — | M14 gate |
| F-12 affinity model-id mismatch | N1 | MED | S7 | T5/T7 | N3 F-08 slug schemes |
| F-13 search.yaml vs opencode.json flags | N1 | MED | S7 | T5 | |
| F-14 stall-sensor unregistered; hardcoded paths; kali-hardcode; model intent-smell | N1 | MED | S7 | T3/M16/M22 | |
| F-15..F-17 providers/models blemishes; default_agent kali | N1 | LOW | S7 | — | F-17 observation for N9/N6 |
| F-20 subagent_depth wall | N1 | HIGH | S7 | T1 | N5 F-9; 7 live instances |
| F-2.1 non-atomic registry writer | N2 | HIGH | S1 | T6 | contradicts repo's own design spec |
| F-2.2 pre-commit not installed | N2 | HIGH | S1 | T2 | = N5 F-3 |
| F-2.5 3/35 entity YAML corrupt | N2 | HIGH | S1 | T6 | verifies+extends N1 intel; locus corrected to line 2 |
| F-2.3 blockers[] "resolved" off-taxonomy | N2 | MED | S1 | T2 | validator blind spot |
| F-2.4 GAP_REGISTRY R15/R50 holes | N2 | MED | S1 | — | immutability otherwise holds |
| F-2.6..F-2.9 staleness boundary; green banner; WAKE_STATE homeless; vacuous R-ID check | N2 | LOW/INFO | S1 | T2 | F-2.8 → synthesis/WAKE queue |
| F-2.10 durability fundamentals solid | N2 | INFO | S1 | — | positive |
| F-2.11 single-writer doctrine violated by design | N2 | INFO | S1 | — | corroborates Carmack Pass-1; →synthesis |
| F-01 council-local/fast fossils | N3 | HIGH | S4 | T4 | LOOP GUARD violation; N2 dropped again |
| F-02 artifact-contract divergence | N3 | HIGH | S4 | T4 | breaks auto-GO consumer |
| F-03 dead agent instruction paths | N3 | HIGH | S4↔S7 | T3 | owner N1/S7 |
| F-04 MANIFEST §7b stale | N3 | HIGH | S4 | T4 | |
| F-05 kali-dispatch defects ($ARGUMENTS, broken tool, dead agent/log) | N3 | MED | S4 | T3 | extended_checkin BROKEN per plan M1 |
| F-06 omega-meditation no $ARGUMENTS; tier drift | N3 | MED | S4 | T3/T4 | |
| F-07 researcher commands → archived log | N3 | MED | S4 | T3 | |
| F-08 model-slug scheme conflict | N3 | MED | S4 | T5 | resolution order = research question |
| F-09..F-11 meditate version stamp; typos; healthy-list | N3 | LOW/INFO | S4 | T4 | |
| F-N4-01 8/22 skills loader-invisible | N4 | HIGH | S5 | T2/T3 | empirically verified vs session available_skills |
| F-N4-02 5 stubs + 1 placeholder | N4 | HIGH | S5 | T3 | dissolves both mission-named overlap pairs |
| F-N4-03 meditation quartet ~1213 lines | N4 | HIGH | S5 | T4 | REAL overlap debt (briefing missed it) |
| F-N4-04/05/06 broken cmd/module/make refs | N4 | HIGH | S5 | T3 | make sovereignty ×9 |
| F-N4-07..F-N4-12 stale paths; superseded mandate anchor; phantom log; dup hf-cli; example rot | N4 | MED/LOW | S5 | T3/T4 | F-N4-08 ↔ N5 F-4 |
| F-1 AGENTS.md void, 462 citations | N5 | HIGH | S2 | T3 | SR-V1 authority chain orphaned |
| F-2 temple-grade stub, ~30% enforcement | N5 | CRITICAL | S2 | T2 | core taper metric |
| F-3 M24/M27 enforcement claims false | N5 | HIGH | S2 | T2 | = N2 F-2.2 |
| F-4 mandate version drift ×4 layers; Codex self-contradiction | N5 | HIGH | S2 | T4 | staleness checker checks time not coherence |
| F-5..F-11 protocol self-version; stale pendings; pillar vocab; roster miscount; nesting rule vs depth; dual HandoffPacket schemas; unsynced redundancy | N5 | MED/LOW | S2 | T4/T1 | F-9 ↔ N1 F-20 |
| F-12 honest-labeling bright spots | N5 | POSITIVE | S2 | — | generalize pattern |

---

## PART C — CONFLICT DETECTION (build-side internal)

**C-1 · RESOLVED (refinement, not conflict)** — Lilith-YAML corruption locus: N1 reported lines 374-377; N2 verified parse fails fast at line 2 (markdown wrap) AND confirmed 374-377 also malformed. Both loci real; N2's account supersedes for remediation ordering (fix line 2 first or parser never reaches 374).

**C-2 · DOCTRINAL TENSION (→ synthesis)** — Packet §F "SINGLE-WRITER: only MaKaLi applies tracker directives" vs §C.6 "every node registers itself in TASK_REGISTRY". Both executed; concurrent self-registration actually occurred (N2 F-2.11, mechanical evidence). Carmack Pass-1 flagged independently. Not a finding error — a design contradiction in the council's own constitution requiring an Architect-judgment ruling (WAKE_STATE candidate).

**C-3 · NUMERIC CONSISTENCY CHECK — PASS** — No numeric disagreements between nodes on shared facts: subagent_depth=2 (N1:3, N3:105, N5:217 agree); skill count 22 (N4 verified against packet); command count 9 (N3=N4 inventories match); entity YAML corruption 3 files (N2 authoritative, N1 subset consistent). S1 dual-ownership split (N2 structure / N8 telemetry) produced no overlap disputes — lanes were respected with explicit flag-not-deep-dive discipline.

**C-4 · BRIEFING-vs-FIELDWORK CORRECTION (not conflict)** — Mission packet named knowledge-miner/legacy-pattern-miner and spec-generator/omega-doc-architect as overlap pairs. Fieldwork: both pairs are hollow-vs-real asymmetry (one twin is a 5-line stub each). Real duplication debt = the unflagged meditation quartet. Council 2 should re-aim the consolidation work package accordingly.

**C-5 · OPEN TENSION (unresolved, factual)** — N1 F-17: `default_agent: kali` vs MaKaLi-top-level topology. Possibly intentional (Architect interactive sessions are kali). Flagged as observation; needs N9/N6 or Architect input. No node contradicted another; tension is internal to the config itself.

**C-6 · METHOD NOTE** — N1's F-01 carries an unresolved empirical fork (dead tools vs lying config). N4's independent evidence (only frontmatter-bearing skills appear in available_skills) supports OpenCode being convention-driven about discovery dirs, weakly favoring "auto-load happens" — but that's skills-loader, not plugins; fork stays open for @researcher. Recorded as gap, not resolved by digestion.

---

## PART D — FULL SOURCE CONCATENATION (verbatim, unmodified)

> Sources below are the complete on-disk raw reports, concatenated in dispatch order N1→N5. No edits.

# 📋 P1 REPORT — NODE N1 INFRASTRUCTURE (Surface S7: Config Surfaces)
⬡ OMEGA ⬡ NODE1 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1 ⬡ Stage-1 RAW
**source_node**: N1 Infrastructure | **arm**: maat | **tier**: node | **session**: 20260825-094633-first-light
**task_id**: `express-c1-node1-20260825` (registered in Task Registry)
**Date**: 2026-08-25 | **Mode**: RECON ONLY — zero production mutations
**Surface S7 scope**: `opencode.json`, `config/*.yaml`, `config/wads/**` (manifests), `.opencode/plugins/`, `.opencode/hooks/`

---

## §0 EXECUTIVE VERDICT

The config layer is **structurally rich but partially decayed**. One CRITICAL wiring defect
(broken plugin paths), one HIGH security finding (`"/*": "allow"` wildcard), a three-way
provider-order contradiction between the two constitution files and providers.yaml, and a
wide gap between **configured** providers and **credentialed** reality (5 of 10 cloud chain
entries have no API key in env). No CRITICAL-HALTED finding: **no active external telemetry
discovered** (M8 bright line holds at the config layer). Stale placeholder secrets found =
logged as FINDING per mandate §C.4, continued.

---

## §1 FINDINGS

### F-01 · CRITICAL — opencode.json registers plugins on DEAD PATHS
- **Evidence**: `opencode.json:7-8` registers
  `file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/error-capture.ts`
  and `.../.opencode/plugin/awareness.ts`.
  Verified: `.opencode/plugin/` **does not exist** — actual dir is `.opencode/plugins/` (plural):
  ```
  ls -d .opencode/plugin        # → "No such file or directory"
  ls .opencode/plugins/         # → awareness.ts error-capture.ts silent-stall-sensor.ts test-event.js.DISABLED
  ```
- **Impact**: The two plugins that technically implement instruction-level behaviors are wired
  to nothing: `error-capture.ts` (subagent-failure capture → JSONL log → Hivemind notify →
  synthetic `<subagent-failure>` injection into parent session — the technical arm of M23/M12)
  and `awareness.ts` (stream-death/restart/compaction awareness injection). No
  `data/coordination/errors/subagent-errors-*.jsonl` file has EVER been written (dir checked),
  consistent with error-capture never having fired.
- **Nuance / open question**: `silent-stall-sensor.ts` is NOT in the `plugin` array yet is
  demonstrably LIVE (`data/coordination/errors/silent-stalls-2026-08-25.jsonl` written today
  13:02:44Z; hourly snapshot updated 13:06Z). This implies OpenCode may auto-load
  `.opencode/plugins/` by directory convention — in which case error-capture/awareness may
  also load despite the broken explicit paths, and the defect is "config lies about mechanism"
  rather than "tools dead". Empirical confirmation belongs to N6/@researcher (S3 live-vs-decorative tests).
- **Recommended fix (bash-verifiable)**:
  ```bash
  # Fix: correct paths in opencode.json
  sed -i 's#\.opencode/plugin/#.opencode/plugins/#g' opencode.json
  # Acceptance: every registered plugin path exists
  jq -r '.plugin[]' opencode.json | grep '^file://' | sed 's#file://##' | while read f; do test -f "$f" && echo "OK $f" || echo "MISSING $f"; done
  # Acceptance: zero MISSING lines.
  ```

### F-02 · HIGH — Permission wildcard `"/*": "allow"` makes the entire external_directory block decorative
- **Evidence**: `opencode.json:10-26`. Eleven specific allow-rules are followed by
  `"/*": "allow"` — a universal grant covering every path on the filesystem.
- **Impact**: Config-instruction inconsistency: instruction layers preach sandbox discipline
  (M8, T11, tainted-data quarantine), while the runtime grants agents access to everything.
  The enumerated rules are dead weight; the effective policy is "allow all".
- **Recommended fix**: remove the `"/*"` entry; keep the enumeration.
  ```bash
  # Acceptance: wildcard gone, enumeration intact
  jq '.permission.external_directory | has("/*")' opencode.json   # → false
  jq '.permission.external_directory | keys | length' opencode.json # → ≥ 10
  ```

### F-03 · HIGH — Three-way provider-order contradiction (Mandates vs Ark vs providers.yaml)
- **Evidence**:
  - `SOVEREIGN_MANDATES.md` M7 pattern: `native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenCode Zen(4) → OpenCode(5) → Copilot(6)`
  - `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` §7 + D-355: cloud order **Antigravity → Google → OCZ → OpenRouter**
  - `config/providers.yaml:62-135`: `antigravity(3), google(4), openrouter(5), opencode-zen(6)` — i.e. **OpenRouter BEFORE OCZ**, contradicting the Ark; and Google at 4 (not 3), contradicting M7's literal chain.
- **Impact**: An agent obeying the constitution text routes differently than the engine does.
  Exactly the "strategy docs claiming different critical paths" structural-debt gate (Ark §9.5) — but in config form.
- **Recommended fix**: pick ONE canonical order (recommend Ark/D-355: swap openrouter↔opencode-zen priorities in providers.yaml), then amend M7 text to name antigravity.
  ```bash
  # Acceptance: OCZ priority < openrouter priority in the flat chain
  python3 -c "
  import yaml; c=yaml.safe_load(open('config/providers.yaml'))
  p={e['provider']:e['priority'] for e in c['inference']['fallback_chain']}
  assert p['opencode-zen'] < p['openrouter'], p"
  ```

### F-04 · HIGH — Credential-reality drift: majority of the cloud chain is configured but dead
- **Evidence** (env probe, names only, this session):
  `EXA_API_KEY=UNSET · GOOGLE_API_KEY=UNSET · ANTHROPIC_API_KEY=UNSET · XAI_API_KEY=UNSET · ANTIGRAVITY_API_KEY=UNSET`; SET: `OPENCODE_API_KEY, OPENROUTER_API_KEY, OMEGA_MODELS_DIR`.
  providers.yaml enables google/google-compat/anthropic/xai/antigravity with `api_key: env:*`;
  opencode.json enables exa MCP with `${EXA_API_KEY}` header.
- **Impact**: Effective working fabric = native-gguf + lmster (local) + opencode-zen + openrouter (cloud). All `fallback_resolver` chains terminate in providers that will 401/drop. `maakali_routing.kali.fallback: antigravity` points at an uncredentialed provider. Sovereignty claims and failover design should be stated against the REAL fabric, not the paper one.
- **Recommended fix**: either provision keys (Architect action) or mark uncredentialed providers `enabled: false` until keyed.
  ```bash
  # Acceptance: every enabled provider with api_key env:* resolves to a set var
  python3 -c "
  import yaml, os
  c=yaml.safe_load(open('config/providers.yaml'))
  for e in c['inference']['fallback_chain']:
      k=e.get('api_key','')
      if e['enabled'] and k.startswith('env:') and not k.endswith('*'):
          pass
  provs=c['inference']['providers']
  bad=[n for n,p in provs.items() if p.get('enabled') and str(p.get('api_key','')).startswith('env:') and str(p['api_key']).split(':',1)[1] not in os.environ]
  print('DEAD:',bad); assert not bad"
  ```

### F-05 · MED — Archived strategy doc injected into EVERY session's instructions
- **Evidence**: `opencode.json:27-33` `instructions[]` includes
  `docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md`. Verified live: this node's own
  system prompt contains that document, including its stale provider fabric ("native-gguf(0) → … → Google(3)") and Horizon-status claims that contradict SOVEREIGN_ARK_BLUEPRINT (also injected) — a per-session, every-session contradiction.
- **Impact**: Every agent every session burns tokens absorbing a superseded roadmap as instruction. Direct violation of Ark §10.8 ("Do not resurrect archived roadmaps as competing masters") — committed by config itself.
- **Recommended fix**: drop the archive path from `instructions[]`.
  ```bash
  # Acceptance: no docs/archive/** path in instructions[]
  jq -r '.instructions[]' opencode.json | grep -c '^docs/archive/'   # → 0
  ```

### F-06 · MED — council.yaml references nonexistent models + contradicts M7
- **Evidence**: `config/council.yaml:18-23` — `model_tiers` claims "(references providers.yaml)"
  but names `gemma-4b-local`, `nemotron-8b-cloud`, `nemotron-12b-cloud`; NONE exist anywhere in
  providers.yaml/models.yaml. Line 68: `M7_local_first: false  # Advisory — cloud is acceptable during dev`
  contradicts M7 (NON-NEGOTIABLE local-first) and providers.yaml `strategy: local_first`.
- **Recommended fix**: remap tiers to real model ids; flip M7 flag or document Architect exception.
  ```bash
  # Acceptance: every council model_tiers value appears in providers.yaml or models.yaml
  grep -q 'gemma-4b-local' config/providers.yaml config/models.yaml   # currently fails → must pass after fix
  ```

### F-07 · MED — Placeholder PATs presented as ACTIVE credentials; perms violate own header
- **Evidence**: `config/github_accounts.yaml:10,20` — `pat: "ghp_placeholder_…"` with
  `status: "active"`; header line 4 demands `0400 permissions`; actual `stat` = `664`.
- **Classification per §C.4**: STALE SECRET = FINDING (logged, continued). Values are obvious
  placeholders — NOT real credentials; no HALT.
- **Recommended fix**: `chmod 600 config/github_accounts.yaml`; move PATs to env/vault (V-1);
  set status `placeholder` until real tokens land.
  ```bash
  # Acceptance: stat -c "%a" config/github_accounts.yaml → 600 ; grep -c ghp_placeholder → 0 (post-V-1)
  ```

### F-08 · MED — omega.yaml duplicates the entire sovereignty_gate block
- **Evidence**: `config/omega.yaml:50-55` and `:71-77` — identical `sovereignty_gate` blocks,
  second copy pasted under "# Hardware optimization" section header region.
- **Fix**: delete one block. `grep -c 'sovereignty_gate:' config/omega.yaml` → must equal 1.

### F-09 · MED — IWAD manifest drift: manifest lists 15 entities, disk has 24
- **Evidence**: `config/wads/_omega_default/manifest.yaml` entities list (15 entries) vs
  `ls config/wads/_omega_default/entities/` = 24 files. Unlisted: dispatch, doom_guy, jem,
  john_carmack, quality, researcher, roc_racoon, scribe, verity.
- **Impact**: Anything consuming the manifest (WAD loader, community stacks) sees a ghost fleet.
- **Fix**: regenerate manifest from disk.
  ```bash
  # Acceptance: manifest entity count == dir count
  diff <(ls config/wads/_omega_default/entities/ | sort) \
       <(grep -oE '"[a-z_]+\.yaml"' config/wads/_omega_default/manifest.yaml | tr -d '"' | sort)
  ```

### F-10 · MED — Triple agent-manifest drift (opencode.json vs agents/*.md vs MANIFEST.md)
- **Evidence**:
  - `.opencode/MANIFEST.md` claims "13-agent fleet, deprecated build stub, ghost agents removed" — yet `.opencode/agents/build.md` (deprecated stub) still exists; MANIFEST primary-modes table omits `grok_cli` which opencode.json defines; `scribe` claimed as primary mode but has no opencode.json block (file-auto-reg only).
  - Dual definitions disagree: opencode.json `kali.description` = "Grand Oversight — Sees all…" vs `.opencode/agents/kali.md` frontmatter = "Sovereign Agent: kali (Sovereign Agent)". Which description an agent presents depends on which layer wins — undocumented.
- **Fix**: single source decision (recommend: agents/*.md frontmatter is SSOT; opencode.json only adds env/model overrides), then reconcile MANIFEST counts.
  ```bash
  # Acceptance: no agent defined with differing descriptions in both layers
  for a in kali maat lilith; do diff <(jq -r ".agent.$a.description" opencode.json) <(awk '/^description:/{print; exit}' .opencode/agents/$a.md) && echo "$a OK"; done
  ```

### F-11 · MED — Unvetted heritage tag in config (M14)
- **Evidence**: `config/models.yaml:101` `[id-soft: gemma-4-mtp-s4]` — no vet record matches
  this tag id in `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` (closest is vet-069
  "Speculative Decode" tagged `[id-soft: quake3-1999]`). Other id-soft-tagged config files:
  `config/wads/_omega_default/ethics.yaml`, `config/domains/engineering/MEMORY_BLOCKS/project-gotchas.block`, `config/omega/requirements.omega` (vet coverage unverified — flag for N5/verity).
- **Fix**: add vet record with file:line + scope declaration, or re-tag as METAPHORICAL.
  ```bash
  # Acceptance: grep 'gemma-4-mtp-s4' data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md → ≥1 hit
  ```

### F-12 · MED — entity_model_affinity.yaml names models/providers that don't match the other configs
- **Evidence**: `config/entity_model_affinity.yaml` — `local_deep: qwen3-4b-thinking-q4_k_m @ native-gguf`
  (providers.yaml native-gguf knows `qwen3-4b-thinking-local`; models.yaml puts qwen3-4b-thinking on lmster);
  `__default__.preferred_models.cloud: gemini-3.5-flash @ google` (providers.yaml lists
  gemini-3.5-flash under **antigravity**, not google).
- **Fix**: normalize model-id namespace across the four config files (single registry).
  ```bash
  # Acceptance: every affinity (model,provider) pair resolves in providers.yaml supported_models
  ```

### F-13 · MED — Search-tier config disagrees with MCP config
- **Evidence**: `config/search.yaml:37-46` T3 firecrawl `enabled: true` vs `opencode.json:45-49`
  firecrawl MCP `enabled: false`; T2 exa enabled but `EXA_API_KEY` unset (dead tier);
  `routing.fallback_chain` uses bare integers (`1: 2`) while tiers are named `T0..T3` — ambiguous keys.
- **Fix**: align enabled flags; key the fallback map by tier names.
  ```bash
  # Acceptance: python3 -c "import yaml;s=yaml.safe_load(open('config/search.yaml'));assert all(k.startswith('T') for m in s['routing']['fallback_chain'].values() for k in [m])"
  ```

### F-14 · MED — silent-stall-sensor active but unregistered; plugins carry hardcoded absolute paths
- **Evidence**: `silent-stalls-*.jsonl` written daily Aug 22–25 incl. today 13:02:44Z, yet
  `opencode.json .plugin[]` does not list it. All three plugins hardcode
  `logDir: "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/errors"`
  (M16 portability concern at plugin layer; engine src/ is clean but plugins aren't).
- **Also**: `awareness.ts:103` hardcodes `s.agent === "kali"` for injection target — stale in
  the MaKaLi-orchestrator era (non-kali orchestrators get no awareness injection).
  `error-capture.ts:109` hardcodes `model: "opencode/nemotron-3-ultra-free"` in Hivemind
  notifications — M22 provenance smell (records intent, not actual model).

### F-15 · LOW — providers.yaml internal blemishes
- Typo `native-gguff` (line 26 comment); duplicate priority 4 (google AND google-compat both 4);
  native-gguf `supported_models` advertises `llama-4-scout-local`, `gpt-oss-120b-local`,
  `qwen-3.5-72b-local` etc. that cannot load on this 16GB RAM box whose single `model_path` is
  Qwen3-1.7B-Q6_K.gguf — aspirational roster presented as capacity.

### F-16 · LOW — models.yaml `frontier` role contradicts D-352 routing
- **Evidence**: `config/models.yaml:51-54` — `frontier: provider: google, role: "Kali Grand Oversoul"`
  vs providers.yaml `maakali_routing.kali: prefer native-gguf, fallback antigravity` (D-352/C-5).

### F-17 · LOW — default_agent "kali" vs council topology "MaKaLi top-level"
- **Evidence**: `opencode.json:323` `default_agent: kali`; council-cloud v2.1 deadlock fix made
  makali the top-level orchestrator. Possibly intentional (Architect's interactive sessions are
  kali) — flagged as observation for N9/N6, not a defect claim.

---

## §2 POSITIVE VERIFICATIONS (things that CHECK OUT)

| Claim | Verification |
|---|---|
| M25 streaming sections on all cloud providers | ✅ present for antigravity/google/google-compat/openrouter/opencode-zen/cline/anthropic/xai (providers.yaml) |
| Port consistency hub/searxng/firecrawl | ✅ 8016/8018/8015 agree across omega.yaml, opencode.json, search.yaml |
| SR-V1 `.firecrawl/` cache dir exists | ✅ |
| models.yaml GGUF paths resolve | ✅ Qwen3-1.7B-Q6_K, MiMo-7B-RL, RocRacoon-3b Q4/Q5 all present in OMEGA_MODELS_DIR |
| session_end.py hook quality | ✅ AnyIO-only, atomic tmp→rename write, preserves agent-written proposals, fsync |
| hardware_profile.yaml honesty | ✅ self-documents its contradiction with ARK SS4 zswap claim + provenance note (FP-12 regeneration) |
| council.yaml hardware block | ✅ roughly consistent with hardware_profile.yaml (8 cores/16GB) |

---

## §3 SECURITY BRIGHT LINE DISPOSITION (§C.4)

- **Stale secrets**: F-07 placeholder PATs → FINDING logged, continued. Old backups
  (`.opencode/opencode.json.bak`, `backup.20260809_*`) contain no credential material (spot-checked headers).
- **Active external telemetry**: NONE discovered. Cloud MCP endpoints (exa, parallel-search) are
  on-demand tools, not telemetry channels; `opencode-antigravity-auth` performs local OAuth.
  **No CRITICAL-HALTED.**

## §4 HANDOFF PACKET (Delivered-Home Doctrine)

**Warm-start reading list (in order)**:
1. `opencode.json` (whole file — 324 lines, the spine)
2. `config/providers.yaml` §inference (chain + maakali_routing)
3. `.opencode/plugins/silent-stall-sensor.ts` header comment (lines 1-42) — best doc on what the sensor does
4. `config/council.yaml` + `config/search.yaml` (small, high-drift)
5. `data/coordination/errors/provider-health-2026-08-25.json` (live stall telemetry)

**Standing orders for future councils paging node1 (domain:N1-infrastructure)**:
- NEVER trust a config path until `test -f` passes — this repo renames dirs (`plugin`→`plugins`) without updating referencers.
- Env-probe provider keys (names only) before claiming the fabric works; the paper chain ≠ credentialed chain.
- When instructions and config disagree, log BOTH sides with file:line — the delta IS the finding.
- Open question reserved for @researcher/N6: empirically determine OpenCode's plugin auto-load convention (does `.opencode/plugins/` plural auto-load? did error-capture/awareness ever load?) — decides whether F-01 is "dead tools" or "lying config".

### F-20 · HIGH — `subagent_depth: 2` makes the M11 Reporting Protocol impossible for nodes (DISCOVERED LIVE)
- **Evidence**: `opencode.json:3` sets `"subagent_depth": 2`. Node N1 executes AT depth 2
  (arm→node = two nested task() calls). Final mandate step §C.9 / plan measure M11 requires
  every node to PAGE the Consultant via `task(subagent_type="kali", task_id="ses_…")`.
  Executed live at 2026-08-25T13:16Z → **rejected**: `Subagent depth limit reached (2).
  Increase "subagent_depth" to allow nested subagents.`
- **Impact**: Config-instruction contradiction of the first order: the council's own dispatch
  protocol mandates a mechanism the config forbids at exactly the tier it mandates it for.
  Every N1-N10 node will hit this wall. Arms (depth 1) can still page; nodes cannot.
- **Classification**: Tool-chain failure reported per M23 — NOT silently swallowed. Workaround
  used: failure logged here + Hivemind broadcast; Consultant notification delegated to arm.
- **Recommended fix**: raise `subagent_depth` to 3, OR amend M11/§C.9 so nodes deliver their
  report to their ARM (which pages onward), making the hop rule structural rather than aspirational.
  ```bash
  # Acceptance (option A): jq '.subagent_depth' opencode.json → ≥ 3
  # Acceptance (option B): node packets no longer contain §C.9 paging step
  ```

---

*source_node: N1 | arm: maat | tier: node | raw report written to disk BEFORE digestion per §C.5*
# P2 REPORT — Node N2 Persistence (Surface S1: STRUCTURE/DURABILITY half)
⬡ OMEGA ⬡ NODE2 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_express_c1_node2 ⬡ FIRST-LIGHT-C1

**[DISPATCH] P12** · From: node2 (Build Arm, Council 1) · Session: `20260825-094633-first-light`
**Task Registry**: `express-c1-node2-20260825` (registered 2026-08-25T13:18:49Z, verified present in TASK_REGISTRY.json)
**Date**: 2026-08-25 · **Mode**: RECON ONLY — zero production mutations; only artifact = this report.
**Lane**: Tracking architecture STRUCTURE/DURABILITY/SCHEMA. Status-drift/staleness *telemetry* = N8's lane (flagged where intersecting, not deep-dived).

---

## §0 METHOD (every conclusion traces to a tool call)

1. Read: mission packet, plan §2/§5/§6.5, `data/entities/maat/soul.yaml` + `proposed_lessons.yaml`.
2. Read exhaustively: `TRACKING_ARCHITECTURE.md`, `scripts/validate_tracking_state.py` (323 lines), `mcp_servers/omega_hub/hub_tools/task_registry.py` (231 lines), write paths of `sweep_task_registry.py` + `generate_session_registry.py`, `.pre-commit-config.yaml`, installed `.git/hooks/*`, Makefile targets.
3. Programmatic probes (python3, read-only): JSON parse of all 4 registries; status-vocabulary walk of every `status` key in ACTIVE_SPRINT + TASK_REGISTRY; R-ID relational cross-check ACTIVE_SPRINT↔GAP_REGISTRY; gap-number density scan; in_progress age audit vs STALENESS_DAYS; mtime-vs-`updated` field comparison; YAML parse sweep of all 32 entity soul/proposed_lessons files.
4. Live validator run: `python3 scripts/validate_tracking_state.py` → **exit 0**, 26 warnings.
5. Git durability probes: tracking-state of all tier files, commit cadence log for TASK_REGISTRY.json.

---

## §1 FINDINGS

> Severity scale per packet §C.5. Every finding tagged `source_node: N2` `tier: S1-structure`.

### F-2.1 · HIGH — Primary TASK_REGISTRY writer is NON-ATOMIC with a lost-update race
`source_node: N2` · `tier: S1-structure/durability`

The highest-traffic writer of the Tier-3 SSOT — the MCP facade every agent hits via `omega-hub_task_registry_register/update` — violates the engine's own durability law:

- `mcp_servers/omega_hub/hub_tools/task_registry.py:32-40` `_save_registry()`:
  - Opens the live file with `"w"` (**in-place truncate**) then acquires `flock(LOCK_EX)` AFTER truncation → a concurrent `_load_registry()` holding `LOCK_SH` can read an empty/partial file in the truncate-before-lock window.
  - No tmp+rename, no fsync → crash mid-`json.dump` leaves TASK_REGISTRY.json truncated/corrupt. This contradicts M12's pattern ("Atomic file renames (`.tmp` → `.json`) for all writes"), Temple-Grade T10, and the repo's OWN design spec `docs/strategy/TASK_REGISTRY_DESIGN.md:189-191` which specifies exactly `tmp_path` → `rename`.
  - **Lost-update race**: `task_registry_register()` calls `_load_registry()` (shared lock acquired AND RELEASED), mutates in memory, then `_save_registry()` reopens. Two concurrent registrations both load v-N, each appends its own task, second save clobbers the first → silent task-record loss. This council ran 5+ concurrent node registrations through exactly this window (`express-c1-node1/node2/node6/arm-maat/runarm-lilith` all landed within ~12 min); no loss observed this time, but the structure permits it.
- Contrast (correct pattern, same repo): `scripts/sweep_task_registry.py:93-103` and `scripts/generate_session_registry.py:145-154` use `mkstemp` → write → `chmod 0644` → `os.replace`. SESSION_ANCHOR 2026-08-23 claims "atomic writes … chmod 0644 added to all three writers" — true only for those two scripts + validator context, FALSE for the MCP primary writer.

**Acceptance criteria (bash-verifiable)**:
```bash
# 1. Atomic pattern present in the MCP writer:
grep -n "mkstemp\|os.replace" mcp_servers/omega_hub/hub_tools/task_registry.py   # must hit
# 2. Lock held across full read-modify-write (no load/save lock split):
grep -n "LOCK_EX" mcp_servers/omega_hub/hub_tools/task_registry.py              # must wrap mutate cycle
# 3. Crash-injection: SIGKILL a writer mid-dump 20×; file must always json.load():
for i in $(seq 20); do timeout 0.05 python -c "...register..." ; python3 -c "import json;json.load(open('data/coordination/TASK_REGISTRY.json'))" || echo CORRUPT; done
```

### F-2.2 · HIGH — M27 pre-commit enforcement is DECLARED but NOT INSTALLED
`source_node: N2` · `tier: S1-enforcement`

SOVEREIGN_MANDATES M27 states: "Pre-commit hook: `omega-tracking-state` blocks commits with corrupted tracking state." Reality:

- `.pre-commit-config.yaml` (~line 137) DOES declare hook `omega-tracking-state` → `python scripts/validate_tracking_state.py`.
- The INSTALLED `.git/hooks/pre-commit` is a hand-rolled bash script running ONLY `scripts/validate_soul.py` over `data/entities/*/soul.yaml`. The pre-commit framework is not active (its installed hook script was replaced/never installed). Therefore **no commit today is gated by tracking validation**.
- Corroborating signal: `TASK_REGISTRY.json` is currently modified-uncommitted in the working tree while the council writes to it (git status: ` M data/coordination/TASK_REGISTRY.json`).
- Same class: `.git/hooks/commit-msg` runs `socratic_commit_check.py` only.

**Acceptance criteria**:
```bash
grep -q "pre-commit" .git/hooks/pre-commit && echo FRAMEWORK-ACTIVE || echo NOT-ACTIVE   # must print FRAMEWORK-ACTIVE
pre-commit install && pre-commit run omega-tracking-state --hook-stage pre-commit        # exit 0
```

### F-2.3 · MED — Live Tier-0 vocabulary violation the validator cannot see (blockers[] unscanned)
`source_node: N2` · `tier: S1-schema`

- `ACTIVE_SPRINT.json` `.blockers.BLOCKER-B.status = "resolved"` — `"resolved"` is NOT in the Tier-0 taxonomy (`backlog|ready|in_progress|blocked|completed|superseded`, TRACKING_ARCHITECTURE.md §Unified Status Taxonomy). It even carries `resolved_at` — a de-facto 7th status invented in place.
- Root cause is validator coverage: `validate_active_sprint()` (validate_tracking_state.py:148-206) walks ONLY `workstreams[].status` and `workstreams[].subtasks[].status`. The `blockers[]` array is never scanned. My probe found it in one pass.
- Secondary coverage note: two workstreams (`QDRANT-HEADROOM`, `TRUTH-ALIGNMENT`) are `in_progress` with ZERO subtasks — unverifiable state shape the validator also accepts.

**Acceptance criteria**:
```bash
python3 -c "
import json;d=json.load(open('data/coordination/ACTIVE_SPRINT.json'))
T0={'backlog','ready','in_progress','blocked','completed','superseded'}
bad=[(k,v['status']) for k,v in d.get('blockers',{}).items() if v.get('status') not in T0]
print(bad); assert not bad"
# And post-fix, validator extended: grep validate_tracking_state.py for 'blockers' must hit
```

### F-2.4 · MED — GAP_REGISTRY is authoritative-by-claim but incomplete in practice
`source_node: N2` · `tier: S1-immutability`

Good news first: **gap-ID immutability HOLDS** — zero duplicate R-numbers; the single collision incident (2026-08-14, R13-R38 reuse) is logged in `collision_incidents` with prevention rule; new plan prefixes (GN/DS/LI/KD/HR/ZS/DP) are properly registered as distinct IDs; `next_free_id: 57` is consistent with max registered R56.

But the registry fails its own "authoritative gap-ID → topic map" claim:
- **R15**: subsumed by R30 per `RESEARCH_PLAN_PHASE1_4_20260813.md:172,382` — no tombstone entry in GAP_REGISTRY.json. Number simply absent from the sequence (range 1-56 missing {15, 50}).
- **R50**: marked "skipped" in the plan table (`RESEARCH_PLAN...:487`) yet a real doc `docs/research/R50_SOMATIC_STATE_DESIGN.md` EXISTS consuming the ID — with NO registry entry. `next_free_id=57` implicitly assumes R50 consumed, but nothing in the registry records that R50 = SOMATIC_STATE_DESIGN. A future agent checking the registry before assigning would see a hole, not a fact.
- Validator's `extract_gap_ids()` regex `\bR\d+\b` misses suffixed IDs (`R8b`, `R14b`, `R27b` exist in the registry) — such references in ACTIVE_SPRINT would never be relationally validated.

**Acceptance criteria**:
```bash
# Every R-doc on disk maps to a registry entry or documented tombstone:
for f in docs/research/R[0-9]*.md; do id=$(basename "$f" | grep -oP '^R\d+[a-z]?'); \
  python3 -c "import json,sys;g=json.load(open('data/coordination/GAP_REGISTRY.json'))['gaps'];sys.exit(0 if '$id' in g else 1)" \
  || echo "UNREGISTERED: $id"; done   # must output nothing (after adding R15/R50 tombstones)
```

### F-2.5 · HIGH — Entity gnosis durability failure: 3 of 35 entity YAML files unparseable
`source_node: N2` · `tier: S1-durability` · *(verifies + extends N1 cross-surface intel)*

Soul-distillation pipeline data (M11) is unreadable by any YAML tooling for:

| File | Exact error |
|------|-------------|
| `data/entities/lilith/proposed_lessons.yaml` (377 lines) | `ScannerError: while scanning an alias in line 2, column 1 ... found '*'` — file begins with a MARKDOWN header block (`# 🔱 LILITH — Proposed Lessons`, `**Entity**: lilith`), not YAML. Post-write LSP diagnostics confirm corruption at TWO loci: lines 2-4 (markdown wrap) AND lines 374-377 (malformed seq-item/map-value structure — N1's reported locus is also real). Both must be repaired; python yaml fails fast at line 2. |
| `data/entities/pillar_p1/proposed_lessons.yaml` | `ParserError: while parsing a block mapping` |
| `data/entities/john_carmack/soul.yaml` | `ParserError: mapping values are not allowed here` |

Consequences: soul loaders that `yaml.safe_load` these files either crash or silently skip (M9 error-integrity question for the loader); 377 lines of Lilith L1/L2/L3 gnosis are stranded. Note the installed pre-commit soul-check runs `validate_soul.py` on `soul.yaml` only — and john_carmack's is corrupt, so either the hook isn't running (see F-2.2) or the validator doesn't parse-YAML-check.

**Acceptance criteria**:
```bash
for f in data/entities/*/proposed_lessons.yaml data/entities/*/soul.yaml; do
  .venv/bin/python3 -c "import yaml;yaml.safe_load(open('$f'))" || echo "CORRUPT: $f"; done
# must print nothing after repair
```

### F-2.6 · LOW — Staleness gate boundary: 7-day-exact zombies escape
`source_node: N2` · `tier: S1-validator`

STALENESS_DAYS=7 with strict `age_days > STALENESS_DAYS` (validate_tracking_state.py:241). Five `in_progress` tasks from 2026-08-17/18 sit at exactly age=7d TODAY and pass; they trip tomorrow. Boundary choice undocumented (Researcher Ruling 1 cited for the threshold value, not the comparison operator). Flagged for N8 (drift telemetry owns staleness history) — my lane notes only the off-by-boundary semantics.

### F-2.7 · LOW — Green banner overstates: exit 0 with 26 warnings
`source_node: N2` · `tier: S1-validator`

Live run: exit 0 "ALL TRACKING STATE CHECKS PASSED" while emitting 14 inverted-clock warnings (`last_checkpoint < created_at`, e.g. `test-task-20260721`, 13× `research-*-20260813`), 12 `failed`-without-Tier-0-subtask warnings, 1 missing `superseded_by`. Warn-only policy is defensible (legacy grandfathering per M3 notes in the script header), but the terminal banner claims total pass. Honesty nit (M23 spirit): banner should read "PASSED (26 warnings)".

### F-2.8 · LOW — WAKE_STATE.json operates OUTSIDE the constitution
`source_node: N2` · `tier: S1-structure`

`WAKE_STATE.json` is referenced by the Express plan (§5/M7 decision queue) and is actively written (mtime 2026-08-25T12:10Z), but:
- It appears NOWHERE in TRACKING_ARCHITECTURE.md's 5-tier table or superseded list — an active coordination file with no constitutional home, no defined schema, no validator coverage.
- Its content mixes wake-critical warnings ("DO NOT RUN GIT CHECKOUT…129 files uncommitted", ts 2026-08-24T06:00Z) with `first_light_express.status: "AWAITING_DEPARTURE"` while Council 1 is demonstrably IN FLIGHT (5+ express-c1 tasks registered). Claimed state lags durable state — drift *history* is N8's lane; my finding is the structural one: register the tier + define schema or demote the file.

### F-2.9 · INFO — Relational integrity check is currently vacuous
`source_node: N2` · `tier: S1-schema`

The FIX-3 R-ID cross-check (ACTIVE_SPRINT→GAP_REGISTRY) exists and works, but my regex sweep of the entire ACTIVE_SPRINT.json raw text found **zero** `\bR\d+\b` references today — the guard validates an empty set. Combined with F-2.4's suffix-blind regex, the relational-integrity layer is structurally sound but practically idle. Not a defect; a coverage observation for future plans that DO cite R-IDs.

### F-2.10 · INFO — Durability fundamentals otherwise SOLID
`source_node: N2` · `tier: S1-durability`

Positive findings worth recording so remediation doesn't break what works:
- All four registries parse clean JSON; no duplicate task_ids (90 tasks, unique); no orphan `.tmp` files in `data/coordination/`.
- All tier files are git-tracked; TASK_REGISTRY.json committed 8× since Aug 15 including today (`f8828314` 2026-08-25) — commit cadence (M3) is real.
- File mtimes match claimed `updated` fields on all four registries (no hidden-writer divergence).
- My own MCP registration landed durably in TASK_REGISTRY.json within seconds — the Delivered-Home Doctrine registration path WORKS end-to-end (this node is living proof).
- HMC_COLLABORATION_HUB.md (Tier-2) exists and is fresh (Aug 24).

### F-2.11 · INFO — Single-writer doctrine conflict corroborated (cross-ref Carmack Pass-1)
`source_node: N2` · `tier: S1-structure`

Packet §C.6 orders every node to self-register in TASK_REGISTRY.json while §F declares "SINGLE-WRITER: only MaKaLi applies tracker directives." Both happened: nodes wrote concurrently via the MCP tool. Flock serializes the writes mechanically (modulo F-2.1's load/save split), but the DOCTRINE is already violated by design of this very council. Carmack Pass-1 (`phase4_research/CARMACK_METHOD_WATCH_PASS1.md:42`) flagged the same. Resolution belongs to synthesis; N2 contributes the mechanical evidence that concurrent self-registration is what actually occurred.

---

## §2 SECURITY BRIGHT LINE (M8)

- No secrets encountered in audited surfaces (ACTIVE_SPRINT/TASK_REGISTRY/GAP_REGISTRY/WAKE_STATE/validator/hooks).
- No external telemetry discovered. **No CRITICAL-HALTED conditions triggered.**

---

## §3 HANDOFF PACKET — for future councils paging node2

**Warm-start reading list (in order)**:
1. `data/coordination/TRACKING_ARCHITECTURE.md` — the constitution (101 lines; read whole thing)
2. `scripts/validate_tracking_state.py` — what is ACTUALLY enforced vs mandated
3. `mcp_servers/omega_hub/hub_tools/task_registry.py:22-41` — the load/save lock-split (F-2.1 epicenter)
4. `docs/strategy/TASK_REGISTRY_DESIGN.md` — intended atomic-write spec (diverged from impl)
5. `data/coordination/GAP_REGISTRY.json` `rules` + `collision_incidents` — immutability regime
6. Prior art: `data/entities/john_carmack/workspace/session_gnosis_20260811.md`, `data/entities/researcher/workspace/RESEARCHER_REPORT_FOR_KALI_20260823.md` (registry-orphan history), `data/entities/roc_racoon/workspace/OVERSIGHT_AUDIT_GROUND_TRUTH_20260823.md` (disk-vs-MCP store proof)

**Standing orders**:
- NEVER trust "validator green" as "schema clean" — the validator has known blind spots (blockers[], suffixed gap-IDs, WAKE_STATE). Run the §1 acceptance probes.
- Treat TASK_REGISTRY.json writes during multi-agent events as lossy-prone until F-2.1 is fixed; prefer registering serially or verifying registration landed (`task_registry_get`) after concurrent waves.
- Gap-ID assignment: check GAP_REGISTRY first, but ALSO `ls docs/research/R*.md` — the registry lags reality (R50 lesson).
- Entity YAML: never assume `proposed_lessons.yaml` parses; probe before programmatic use.

**Open questions for synthesis**:
1. Who owns fixing the MCP writer (F-2.1) — engine team or hub team? (touches `src`-adjacent code, out of C1 scope)
2. Should `resolved` be legalized into the Tier-0 taxonomy for blockers, or BLOCKER-B migrated to `completed`? (F-2.3)
3. WAKE_STATE.json: promote to Tier-5 with schema, or fold into HMC hub? (F-2.8)

---

## §4 PROVENANCE

### §4.1 F-20 INSTANCE LOG (M23 failure-integrity)
- §C.9/M11 Consultant page attempted ONCE at 2026-08-25T13:27Z via `task(subagent_type="kali", task_id="ses_fdef2be4effe4pAaLXCTUx62GO")` → **REJECTED**: `Subagent depth limit reached (2). Increase "subagent_depth" to allow nested subagents.` No retry per packet order. Corroborates N1 + N6 F-20 reports — the M11 Reporting Protocol is mechanically impossible for depth-2 leaf nodes as dispatched. This report's delivery channels: (1) this file on disk, (2) Hivemind post `ses_79cde3e80cd7`, (3) end-of-task summary to pager (Build Arm maat), who may relay to Consultant at depth 1.


- All evidence paths relative to repo root, verified 2026-08-25T13:18-13:45Z.
- Validator run: exit 0, 26 warnings (transcript embedded in session tool log).
- Cross-surface intel from N1 (lilith YAML corruption): VERIFIED with corrected locus (line 2 markdown-wrap, not line 374).
- Report written RAW TO DISK before digestion per §C.5. No production files mutated.

*⬡ OMEGA ⬡ NODE2 ⬡ P2-REPORT ⬡ S1-STRUCTURE ⬡ 2026-08-25*
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
# 📋 P5 REPORT — NODE N5 GOVERNANCE / SURFACE S2 (Instruction CONTENT)
**[DISPATCH] P12 | source_node: N5 | tier: leaf (depth-2) | arm: maat (Build) | council: First Light Express C1 | ts: 2026-08-25T~14:10Z**

⬡ OMEGA ⬡ NODE5 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_express_c1_node5 ⬡ ACTIVE
**Task Registry**: `express-c1-node5-20260825` (registered 2026-08-25T13:49Z, tags expert/pageable/domain:N5-governance/express:first-light)
**Mode**: RECON ONLY. Zero production mutations. This report is written to disk BEFORE any digestion/summary work (§C.5).

---

## §0 SURFACES AUDITED (all read exhaustively via tool calls)

| File | Lines | Status on disk |
|------|-------|----------------|
| `OMEGA_CODEX.md` | 433 | Read full |
| `SOVEREIGN_MANDATES.md` | 242 | Read structure + verified v3.8.0/27 headers |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | 567 | Read full |
| `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` | 182 | Read full |
| `AGENTS.md` (root) | **DOES NOT EXIST** | Verified absent; never existed in git history |

Supporting evidence pulled (cross-layer verification): `Makefile`, `.git/hooks/pre-commit`,
`.github/workflows/ci.yml`, `.agents/AGENTS.md`, `.opencode/agents/maat.md`,
`scripts/codex/{ENGINE,MANDATES,AGENTS}_CONDENSED.md`, `data/handoff*/` dir tree,
`data/coordination/HMC_COLLABORATION_HUB.md` (exists), `src/omega/oracle/subagent_dispatcher.py` (exists).

**SECURITY BRIGHT LINE (M8)**: No secrets found in audited surfaces. No active external
telemetry instructions discovered. **No CRITICAL-HALTED condition triggered.**

---

## §1 FINDINGS

Provenance on every finding: `source_node: N5 | tier: leaf | surface: S2`.

---

### [F-1] HIGH — Root `AGENTS.md` does not exist; 462 files cite it as canonical
**source_node: N5 | tier: leaf**

**Claim chain**:
- `ls AGENTS.md` → No such file or directory (repo root).
- `git log --all --oneline -- AGENTS.md` → EMPTY. The file was **never committed at root in this repo's entire history**. This is permanent drift, not a recent deletion.
- Reference count: `grep -rn "AGENTS\.md" --exclude-dir=third-party ... -l . | wc -l` → **462 files** reference the string.
- Key canonical citations to the void:
  - `OMEGA_CODEX.md:222` — "**Source**: `AGENTS.md` (343 lines)" (the Codex's agent-rules card claims a 343-line source that does not exist anywhere in git)
  - `OMEGA_CODEX.md:263,334` — "Full fleet docs: `AGENTS.md` §2-§3"
  - `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md:119` (P10) — "SR-V1 tiered pipeline (**AGENTS.md §Search Tool Protocol**)"
  - Ma'at persona (`.opencode/agents/maat.md`) — "Follow the Delegation Protocol in **AGENTS.md**", "5-tier protocol in **AGENTS.md** §Search Tool Protocol" — injected into every Ma'at-session system prompt
- Only real AGENTS.md files: `.agents/AGENTS.md` (43-line Antigravity IDE discovery card) and third-party vendored copies (`third-party/llama.cpp`, `letta`, `mempalace`).

**Impact**: SR-V1 (Sovereign Search Protocol), the Delegation Protocol, and fleet docs §2-§3 are all defined-by-citation to a nonexistent file. Any agent hydrating per M15 that follows these pointers hits a dead end and either improvises (parametric synthesis risk, M23 exposure) or burns turns hunting. The Search Protocol tiers T0-T6 survive only as fragments in persona files and Codex cards — no authoritative home.

**Recommended fix**: Restore a root `AGENTS.md` as the canonical workflow doc (reconstruct from Codex cards + persona fragments + plan docs), OR amend all citers to point at real paths. Council 2 should spec which.

**Bash-verifiable acceptance criterion**:
```bash
test -f AGENTS.md && echo PASS || echo FAIL          # file exists
! grep -rn "see AGENTS\.md\b" --include="*.md" . --exclude-dir=third-party | grep -v "\.agents/" # no dangling "see AGENTS.md" refs outside .agents/
```

---

### [F-2] CRITICAL — Enforcement taper: `make temple-grade` is a stub; ~8 of 27 mandates machine-enforced (~30%)
**source_node: N5 | tier: leaf**

This is the core Temple-Grade taper metric requested by §B. Measured enforcement reality:

**What `make temple-grade` actually runs** (Makefile):
```make
temple-grade: check-codex-stale doc-llm-validate check-mandates check-tracking-state
	@echo "$(YELLOW)Running temple-grade checks...$(NC)"
	# Existing temple-grade checks would go here      ← LITERAL STUB COMMENT IN PRODUCTION MAKEFILE
	@echo "$(GREEN)Temple-grade complete ...$(NC)"
```
The comment `# Existing temple-grade checks would go here` is present verbatim. **T1-T11 gates do not exist as implemented checks.** M13's own text claims: "Run `make temple-grade` to verify compliance. Each gate must pass… CI must gate on T3 (coverage ≥80%), T5 (AnyIO-only), T6 (zero telemetry), T8, T9, T10." Coverage (T3), resilience (T8), structured logging (T9), atomic writes (T10) have **no corresponding gate targets**.

**Per-mandate enforcement census** (27 mandates):
| Enforced by machine gate | Mandates | Count |
|---|---|---|
| ✅ Real Makefile/CI gates | M1 (check-m1-anyio + check-asyncio-import), M7, M8, M9, M23 (check-mandates → ci.yml:41), M14 (heritage-vet target), M26 (doc-llm-validate), M27 (check-tracking-state, temple-grade chain only) | **8 (~30%)** |
| ⚠️ Warn-only / advisory / meta-stub | M12 (self-declared ADVISORY), M13 (stub chain above), verify-mandate-claims (self-labeled "warn-only") | 3 |
| ❌ Text-only, no gate | M2, M3, M4, M5, M6, M10, M11, M15, M16, M17, M18, M19, M20, M21, M22, M24*, M25 | 16 |

*M24's claimed pre-commit enforcement is separately false — see F-3.

**Impact**: The constitutional document asserts a verification regime that is ~70% aspirational. Agents and humans consulting M13 believe a green `make temple-grade` certifies T1-T11; it certifies 4 narrow checks. This is precisely the "enforcement theater" pattern the Carmack Full-Scope Audit flagged (Codex §2 row: "pre-commit uninstalled, temple-grade RED") — yet the Codex simultaneously prints "✅ All enforced" for 27 mandates two rows up. The engine's own state card contradicts its own audit finding, generated the same day.

**Recommended fix**: Either implement T1-T11 gates or rewrite M13 to enumerate exactly which gates exist. Honesty-first per M23: shrink the claim before growing the gate.

**Bash-verifiable acceptance criterion**:
```bash
# Option A (implement): every T-gate is a real target
for t in t3-coverage t5-anyio t8-resilience t9-logging t10-atomic; do grep -q "^$t:" Makefile || echo "MISSING $t"; done
# Option B (honest shrink): mandate text matches reality
grep -A3 "make temple-grade" SOVEREIGN_MANDATES.md | grep -qv "T3\|T8\|T9\|T10" && echo PASS-text-aligned
# Stub comment gone:
! grep -q "would go here" Makefile && echo PASS-no-stub
```

---

### [F-3] HIGH — M24/M27 pre-commit & `make test` enforcement claims are false
**source_node: N5 | tier: leaf**

**Claimed** (SOVEREIGN_MANDATES.md, disk, v3.8.0):
- M24 Enforcement: "Pre-commit hook: `grep -r "break-system-packages" scripts/ && exit 1`"
- M27 Enforcement: "Pre-commit hook: `omega-tracking-state` blocks commits with corrupted tracking state"; "CI gate: `make temple-grade` + `make test` include `check-tracking-state`"

**Actual**:
- `.git/hooks/pre-commit` (only hook, 199 bytes, dated Jun 5) runs ONLY `scripts/validate_soul.py` over soul.yaml files. **Neither claimed hook exists in it.** `.pre-commit-config.yaml` exists at root but the installed hook never invokes pre-commit-framework.
- `make test` recipe = `$(PYTEST) -x --tb=short -m "not integration" tests/` — **no check-tracking-state**, contradicting M27's explicit claim.
- `.github/workflows/ci.yml:41` runs `make check-mandates`; neither workflow greps for the patterns matching doc-llm/tracking in test.yml. M27's "CI gate … make test include" claim is half-false.

**Impact**: Two constitutional mandates assert blocking enforcement that does not block anything. An agent relying on the hook to catch `--break-system-packages` or corrupted tracking state will ship both silently. Direct descendant of the Carmack audit's "uninstalled hooks" finding — partially remediated (a soul-check hook exists) but the mandate text was never reconciled.

**Bash-verifiable acceptance criterion**:
```bash
grep -q "break-system-packages" .git/hooks/pre-commit && echo PASS-M24 || echo FAIL-M24
grep -q "tracking" .git/hooks/pre-commit && echo PASS-M27-hook || echo FAIL-M27-hook
grep -q "check-tracking-state" <(sed -n '/^test:/,/^$/p' Makefile) && echo PASS-M27-makefile || echo FAIL-M27-makefile
```

---

### [F-4] HIGH — Mandate version/count drift across four instruction layers (same protocol, four different truths)
**source_node: N5 | tier: leaf**

The same constitutional object is described inconsistently in four places, all load-bearing:

| Layer | Claim | Evidence |
|---|---|---|
| Disk SSOT | **v3.8.0, 27 laws** | `SOVEREIGN_MANDATES.md:2` + 27 `###` sections (verified by grep count) |
| Ma'at persona (injected into session prompts TODAY) | **"25 Sovereign Mandates (v3.7.0)"** | `.opencode/agents/maat.md:38` |
| Antigravity discovery card | **"14 Sovereign Mandates"** | `.agents/AGENTS.md:14` |
| Codex mandate card | Header "**Version: 3.7.0**" + "The **27 Laws**" title + table that **stops at M25** (M26/M27 absent) + compliance "**18/25 FULL**" | `scripts/codex/MANDATES_CONDENSED.md:3,43` |

**Worse — OMEGA_CODEX.md contradicts ITSELF internally** (all in the single file generated 2026-08-25T08:55:41Z, i.e., fresh-regenerated TODAY):
- §2 Current State: "Mandates **27 enforced** (M1-M27, v3.8.0 …) ✅ All enforced"
- §6 Key Files: "`SOVEREIGN_MANDATES.md` | **25 Constitutional Laws (v3.7.0)**" (also `scripts/codex/ENGINE_CONDENSED.md:93`)
- Embedded MANDATES_CONDENSED: M5 ❌ FAIL, M11 ❌ FAIL, "FULL 18/25"

Three mutually exclusive compliance claims (all-enforced-27 / 25-laws / 2-fail-25) in one startup read target. The staleness checker (`check_codex_stale.py`) verifies timestamp freshness, not content coherence — so regeneration faithfully reproduces contradictions baked into its source cards. This validates Ma'at's own L3 principle in `data/entities/maat/proposed_lessons.yaml`: *"A Single Source of Truth that is not kept current is worse than no source of truth."*

**Impact**: Every agent hydrating from the Codex (hydration sequence step 3, mandatory) ingests contradictory constitutional state at boot. Downstream behaviors: agents cite v3.7.0/25 in their own outputs (as my own persona did this session), mandate-numbering confusion in dispatches, and erosion of trust in the SSOT concept itself.

**Bash-verifiable acceptance criterion**:
```bash
V=$(grep -m1 "^\*\*Version\*\*" SOVEREIGN_MANDATES.md | grep -o "[0-9.]*$")
N=$(grep -c "^### " SOVEREIGN_MANDATES.md)
grep -rq "$V" scripts/codex/*.md && ! grep -rq "3\.7\.0" scripts/codex/*.md && \
grep -q "M26" scripts/codex/MANDATES_CONDENSED.md && \
[ "$(grep -c 'Constitutional Laws' scripts/codex/ENGINE_CONDENSED.md)" -eq 0 -o "$(grep 'Constitutional Laws' scripts/codex/ENGINE_CONDENSED.md | grep -c "$N")" -eq 1 ] \
&& echo PASS || echo FAIL
```

---

### [F-5] MED — SUBAGENT_DISPATCH_PROTOCOL.md self-version conflict: header v2.0.0 vs footer v3.0.0
**source_node: N5 | tier: leaf**

- Header: `AP-SUBAGENT-DISPATCH-v2.0.0`, "Last Updated: 2026-07-12" (`docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md:3-5`)
- Footer: `SUBAGENT-DISPATCH ⬡ v3.0.0` (line 562)

One file, two versions. Whichever is authoritative, the other is a lie in the same document. Also the provenance-correction comment (lines 564-567) shows the header model attribution was already flagged UNANCHORED by the FP-04 audit — the file's identity metadata has been caught lying once before.

**Bash-verifiable acceptance criterion**:
```bash
H=$(grep -m1 "AP-SUBAGENT-DISPATCH-v" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md | grep -o "v[0-9.]*$")
F=$(grep -o "SUBAGENT-DISPATCH ⬡ v[0-9.]*" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md | grep -o "v[0-9.]*$")
[ "$H" = "$F" ] && echo PASS || echo "FAIL: $H != $F"
```

---

### [F-6] MED — Dispatch protocol stale "Pending Sprint 2" items are actually DONE; archive path split is real on disk
**source_node: N5 | tier: leaf**

- §7 "Pending Design Items — These must be implemented in Sprint 2": Redis Pub/Sub 🔴 PENDING (live today: `hivemind_redis_publish`/`subscribe` MCP tools), MCP Hub integration 🔴 PENDING (operational: `mcp_servers/omega_hub/`), CLI `omega handoff` 🔴 PENDING, Archive INDEX updater 🔴 PENDING. Meanwhile §7 itself marks HandoffPacket dataclass/Capability Registry/dispatch() as ✅ DONE in `src/omega/oracle/subagent_dispatcher.py` (verified exists). The section is ~2 months stale against its own subject matter.
- Path split: §5 Step 4 says archive to `data/handoffs/completed/{packet_id}.json`; §6 says `data/handoff/archive/`. **Both directories exist on disk**: `data/handoffs/` (3 markdown review files — not packets at all) and `data/handoff/` (live pending/active/completed/stale/archive queue used by the MCP tools). The protocol text describes a directory layout that matches nothing actually running.

**Bash-verifiable acceptance criterion**:
```bash
grep -n "handoffs/completed" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo FAIL-path-split || echo PASS
grep -n "🔴 PENDING" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo FAIL-stale-pending || echo PASS
```

---

### [F-7] MED — Pillar→Node terminology drift inside dispatch protocol §11
**source_node: N5 | tier: leaf**

§11 (Dispatch Decision Tree, D-kal-103) uses superseded vocabulary throughout: "Spans 3+ **pillars**", "Run-only (**P6-P10**)", "Lilith handles the **pillar chain**", "@node NX" mixed with pillar language — while the rest of the fleet (Codex, Ark UO-4 freshening, mission packet §B) uses Node/N-numbering exclusively. An execution-model agent following §11 literally encounters undefined "P6-P10" identifiers. This is exactly the contamination class the protocol's own §12 warns about ("Cannot resolve document hierarchy… Merge superseded documents").

**Bash-verifiable acceptance criterion**:
```bash
! grep -qi "pillar" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo PASS || echo FAIL
```

---

### [F-8] MED — Capability registry (§3) drifted from actual fleet
**source_node: N5 | tier: leaf**

§3 registry declares "11 agents" including a `pillar` subagent type; the Codex fleet table (from the same generated Codex) declares **12 agents** including `@grok_cli` and `@node NX`; `scribe` appears in §11's decision tree but is absent from §3's table; `verity`'s Task-tool type is listed as `scribe` (stale pre-unification). Three different fleet rosters across one protocol + one Codex. M10 (Fleet Integrity, cap 14) cannot be audited against a registry that miscounts the fleet.

**Bash-verifiable acceptance criterion**:
```bash
C=$(ls .opencode/agents/*.md | wc -l)
R=$(grep -c "^| \`" <(sed -n '/^| Agent | Type /,/^$/p' docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md))
[ "$R" -ge "$C" ] && echo PASS || echo "FAIL: registry $R < fleet $C"
```

---

### [F-9] MED — "Single-Level Nesting" rule authorizes what `subagent_depth: 2` mechanically forbids
**source_node: N5 | tier: leaf | cross-refs: N1/S7, N3/S4 (F-20)**

Dispatch protocol §1 Rule 4: "Subagents may spawn other specialized subagents when strictly necessary… Limit delegation to a single level of nesting unless explicitly authorized." Config reality (`opencode.json` `subagent_depth: 2`): a dispatched leaf sits AT depth 2 and cannot call task() at all — empirically confirmed this session by N1/N6/N7/N8 (awareness feed: "task() rejected with 'Subagent depth limit reached (2)'"), and by my own constrained paging posture (§C.9). The instruction text grants a permission the runtime revokes. Text-vs-config contradiction ON my surface (protocol content) intersecting S7 (config).

**Bash-verifiable acceptance criterion**:
```bash
grep -q "subagent_depth" opencode.json && \
grep -q "may spawn other specialized subagents" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo CONFIRMED-CONTRADICTION
# Fix = either depth bump or rule rewrite; acceptance: rule text mentions depth limit
grep -q "subagent_depth" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo PASS
```

---

### [F-10] LOW — Oversight Patterns P1 codification promises a HandoffPacket schema that conflicts with the shipped one
**source_node: N5 | tier: leaf**

ARCHITECT_OVERSIGHT_PATTERNS §2 P1 row: dispatch packets will REQUIRE `context_narrative`, `reading_list`, `deliverable_spec` with validator rejection — status "PROPOSED — ticket". The shipped HandoffPacket schema (dispatch protocol §2) has none of these fields (closest: freeform `context`, `relevant_files`). Two competing definitions of "the handoff packet" coexist across two instruction documents with no supersession marker between them. Risk: future spec-writers implement P1 fields and silently break every existing packet consumer. Also: this file lives in `data/coordination/` yet functions as standing law (its P12 header format opened MY dispatch this session) — governance doctrine stored outside any doc-index layer (placement is N7's lane; the CONTENT dual-schema issue is mine).

**Bash-verifiable acceptance criterion**:
```bash
grep -q "context_narrative" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo PASS-integrated || echo "OPEN: P1 fields unintegrated — add supersession note to one of the two schemas"
```

---

### [F-11] LOW — Mandate-content redundancy: 6+ unsynchronized copies, no single-writer
**source_node: N5 | tier: leaf**

Mandate summaries are duplicated in: (1) `SOVEREIGN_MANDATES.md` full text, (2) `scripts/codex/MANDATES_CONDENSED.md`, (3) Codex embed thereof, (4) `scripts/codex/AGENTS_CONDENSED.md`, (5) each persona file's "Key Mandates" block, (6) `.agents/AGENTS.md`. F-4 proves these copies diverge even when regenerated the same day, because the condensers hardcode counts/versions instead of deriving them from the SSOT. No lint gate compares condensed copies against the constitutional source.

**Bash-verifiable acceptance criterion**:
```bash
# A derivation check script exists and passes:
test -x scripts/check_mandate_consistency.sh && scripts/check_mandate_consistency.sh && echo PASS
```

---

### [F-12] POSITIVE — Honest labeling where it exists
**source_node: N5 | tier: leaf**

Two genuine integrity bright spots worth preserving: (1) `verify-mandate-claims` self-labels "(warn-only mode)" in its own output — honest about its weakness; (2) M12 carries an explicit ADVISORY downgrade stamp with decision citation (D-267). The pattern to generalize: every unenforced mandate should carry a visible enforcement-status stamp like these two, converting silent taper into declared taper.

---

## §2 CROSS-SURFACE INTERSECTIONS (verified, not re-audited)

| Sibling finding | My intersection verdict |
|---|---|
| N1/S7 provider-order contradiction (M7 text vs Ark D-355 vs providers.yaml) | Confirmed from my side: M7 (mandate layer) names a 7-provider order ending Copilot; ORACLE_STACK.md names a 6-provider order ending OpenCode; Ark D-355 names Antigravity-first cloud order. THREE orders across instruction layers. Mine adds: the M7 text itself is a fourth variant of the truth N1 flagged. |
| N3/S4 kali-dispatch broken extended_checkin | Plan §5/M1 already documents the breakage honestly (NameError, SYSTEM_FAILURE_LOG ~10:30Z) — the PLAN is honest, but SOVEREIGN_MANDATES/persona layers don't mention it; only coordination-layer docs know. Layered-awareness gap, consistent with F-11 redundancy-without-sync. |
| N4/S5 sovereign-refinement skill anchored to v3.1.0/14 mandates | Same disease as F-4: hardcoded version strings in derivative docs. N4's evidence strengthens the case for a derived-not-hardcoded consistency gate (F-11 acceptance criterion). |
| N8/S1b "validator green certifies taxonomy compliance, NOT truthfulness" | Same root pattern as F-2/F-3: gates certify form, not truth. Convergent finding across build+run sides — synthesis arm should treat "gate honesty" as a council-level theme. |

## §3 HANDOFF PACKET (Delivered-Home Doctrine §6.5)

**Warm-start reading list** (in order):
1. `data/council/20260825-094633-first-light/phase0_mission_packet.md` (§B row S2, §C)
2. This report + `OMEGA_CODEX.md` (read critically — see F-4)
3. `SOVEREIGN_MANDATES.md` (disk = authoritative v3.8.0/27)
4. `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` (with F-5..F-9 caveats)
5. `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` (P1-P13)
6. `Makefile` targets: `temple-grade`, `check-mandates`, `verify-mandate-claims`, `check-tracking-state`
7. `.git/hooks/pre-commit` (what enforcement ACTUALLY exists)

**Standing orders for future councils paging node5 (domain:N5-governance)**:
- Treat `SOVEREIGN_MANDATES.md` on disk as sole constitutional authority; distrust any derivative stating a version/count without re-checking disk.
- Before citing any protocol doc, run the F-5 style header/footer version check.
- Enforcement questions resolve via `grep` on Makefile + hooks, NEVER via mandate text claims (taper ≈ 30%).
- Escalate any new instruction-layer doc that hardcodes mandate counts or version strings — require derivation from SSOT.

**Open questions for Council 2 / Architect queue (WAKE_STATE candidates)**:
1. Reconstruct root `AGENTS.md` or re-point 462 citations? (Architect judgment — affects SR-V1 authority chain.)
2. T1-T11: implement or honestly shrink M13? (Default-on-silence rec: shrink text first, implement gates second — honesty before capability.)
3. Should `ARCHITECT_OVERSIGHT_PATTERNS` be promoted into `docs/standards/` with SSOT registration?

## §4 DEVIATION LOG

- **§C.9 Consultant page**: attempted exactly once at 2026-08-25T14:02Z → **REJECTED**: "Subagent depth limit reached (2). Increase subagent_depth to allow nested subagents." Seventh consecutive F-20 instance across council (after N1/N6/N7/N8/N10). NOT retried per §C.9 constraint. Report delivery = P5_report.md (this file) + Hivemind broadcast (14:01Z) + end-of-task summary to arm maat, who may page the Consultant on my behalf if she deems it needed (Hop Rule respected: I do not page my pager).
- extended_checkin NOT used per M1 (broken server-side). Heartbeat cadence maintained (~10 min).

---
*⬡ OMEGA ⬡ NODE5 ⬡ EXPRESS-C1 ⬡ S2-INSTRUCTION-CONTENT ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

