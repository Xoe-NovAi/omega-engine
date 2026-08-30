<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 GROKSTER DEBUT ROI DISCOVERY — 2026-08-25
**AP Token**: `AP-GROKSTER-ROI-DISCOVERY-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_grokster_roi_discovery ⬡ DEEP-DISCOVERY
**Commissioned by**: grokster · **Sprint**: PUBLIC-DEBUT-01 (EXECUTION_MINIMAL, freeze LIFTED)
**Method**: Disk-truth verification (`git`, `ls`, `grep`) against every tracker claim. Per FLE Zero-Trust Documentation Doctrine + precedent warning (ACTIVE_SPRINT previously claimed temple-grade PASS while RED). Every status below is VERIFIED-BY-COMMAND unless marked `[UNVERIFIED]`.

---

## §1 EXECUTIVE SUMMARY

**The single most important finding: the trackers lie in BOTH directions, and the lies point at different tickets.**

1. **Disk is AHEAD of ACTIVE_SPRINT.json** for INST-1: fix2 (pyproject extras split), fix4 (`_load_sovereign_secrets` removed), and PUB-1's allowlist file all EXIST on disk while the tracker still says `ready`/`in_progress`. Ma'at's work landed without tracker sync.
2. **Tracker is AHEAD of disk for P0-1c**: ACTIVE_SPRINT claims gitleaks/trufflehog `completed`; `.pre-commit-config.yaml` contains NO secret-scanning hook and `.github/workflows/` has none either. This is a repeat of the temple-grade-PASSES-while-RED precedent class.
3. **AGENTS.md IS A GHOST** — absent from disk AND git history (RECON C4, independently confirmed). CI-2's acceptance criterion `instructions=["AGENTS.md"]` is **unsatisfiable until AGENTS.md is reconstructed** (WP-E). This makes C4 an unnoticed hard blocker on the entire Context Injection workstream.
4. **CI-1 is DONE on disk** (MANDATES_CONDENSED.md passes its own DEV-01 gate: 27 rows, v3.8.0 marker) but tracker says `ready`.
5. **CI-2 is DRIFTED, not done**: opencode.json compaction uses V1 family (correct per DEV-02 binary pin) but values are tail_turns=3 / preserve=40000 / reserved=10000 (spec: 5/80000/20000); top-level model = `opencode/nemotron-3-ultra-free` (DEV-12 requires `lmstudio/qwen3-4b-thinking`); instructions array lists 5 files including two ARCHIVED strategy docs — directly contradicting the injection-reduction goal.
6. **temple-grade is RED** (M8 regex false-positive at ics.py:197 — RECON C1, dual-agent confirmed). One-line fix. This gates M13 and any debut release claim.
7. **Pre-commit framework is DORMANT** (RECON C3): 20 hooks configured, installed hook is a 6-line soul-check script. `pre-commit install` was never run.
8. **P0-1b residual is LIKELY RESOLVED but nobody closed it**: ancestor commit `0c40b108` (SECURITY_AUDIT blob) no longer exists as an object — a later filter-repo pass ate it. The 13 reachable `csk-` string-deltas are prose in docs about the scrub. Remaining true exposure: unpruned `refs/cline/checkpoints/*` (verified present) — contents `[UNVERIFIED]`, needs one gitleaks pass once wired.
9. **No `release/debut` branch exists. No tags exist.** The publication mechanic (D-553) has not started.
10. **Grokster's assets plug into 6+ live surfaces** (§4), and 5 parts of grokster's own blueprint are now stale (§5) — most notably: the DYNAMIC_PROMPT gaps doc has been moved to `data/coordination/archive/`, mimo-7b assignments are superseded by the Carmack matrix, and the curator registry concept was pre-empted by D-586 Node Expert Sessions + an already-shipped `config/domains/curators.yaml`.

**Calendar-critical path to `release/debut` + tag v0.1.0**: C1 regex fix → C3 pre-commit install (+gitleaks wiring = real P0-1c) → C4 AGENTS.md reconstruction → CI-2 correction → CI-0 behavioral probe → CI-3/4/5 → INST-1-fix6 verification → P0-1d sweep+prune → PUB-1 branch cut. Everything else is post-debut staging.

---
## §2 STRATEGY CORPUS INVENTORY

### 2.1 Commissioned reads — status
| Doc | Read | One-line state |
|---|---|---|
| `docs/specs/PROJECT_INDEX.md` | ✅ | Dated 2026-08-20; ticket table STALE vs disk (says INST fix2/4 `backlog`; disk has them done). Itself needs a refresh stamp. |
| `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 | ✅ | Still the execution SSOT (D-533). Its P0-1b residual note is now stale (blob object gone). |
| `HANDOFF_TO_KALI_FLE_STUDY_20260825.md` | ✅ | FLE SSOT. Standing laws: Hop Rule, M11 Arm-Relay, dual-channel telemetry, exit-code honesty, Zero-Trust Doctrine. Remediation queue: infra_inventory.py (~3h) ⭐, necrotic excision (HMC watcher/scribe/soul_promote/codex), tutorial v2. |
| `teamstudy_20260823/FINAL_SYNTHESIS.md` | ✅ | Protocol validated (12 settlements, 0 objections). Study #2 design changes: A0 premise audit, B-report 8KB cap, round cap 2, cross-agent-discovery stop/go metric. |
| `docs/strategy/ORCHESTRATOR_CHARTER_v1.md` | ✅ | Ratified 2026-08-25. Orchestrator = ROLE not agent; default occupant MaKaLi; Feather Gate; P13 steering (`<!-- KALI: ... -->`); hard limits: no self-audit, no execution capture. |
| `data/coordination/HOLISTIC_ARCHITECTURE_PLAN_20260820.md` | ✅ (TOC+key §§) | 6 systems: GN / DS / LI / KD / HR / ZS. NOTE: System 3 startup script says "zRAM (not zswap)" while System 6 + D-526 say zswap+NVMe — the ZS adjudication split is INSIDE this one doc. |
| `CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` + `phase1_spec/09_SPEC_DEVIATIONS.md` | ✅ | DEV-01..12 remediation trail complete; binary pinned 1.18.19; V1 compaction family primary; model-pin strategy re-mechanized (DEV-12). |
| `data/knowledge/truth_alignment/DATASET_CHARTER.md` | ✅ | TA ledger ACTIVE CAPTURE; schema + Amendment 1 taxonomy; feeds ctxNN + Skeptical Verifier + debut positioning ("auditable AI artifacts"). |
| FLE SOVEREIGN_DECREE.md + SOVEREIGN_DECREE_C2.md | ✅ | C1: root cause = "claims that outlive their mechanisms"; fix class = derivation checks; pairwise binding; temple-grade stub removal; suite NOT green (320 tests, 3 failures). C2: SPEC-A..E ratified; GO×13 work packages; NO-GO×2 blocked on Architect Q-3. |

### 2.2 NEW in data/coordination/ since 2026-08-21 (grokster's last sync)
⚠️ **Mtime caveat**: ~30 files share mtime `Aug 23 17:39` — a bulk backfill/copy reset timestamps; true creation dates vary. Flagged where known.

**Aug 22**:
- `NODE_EXPERT_SESSIONS_PLAN.md` — plan that became D-586 (one agent, many sessions; Nodes = universal KBs)
- `KALI_INDEX_20260822.md` — Kali's corpus index of that date
- `SESSION_REPORT_20260822_STALL_ECHO_AND_STRATEGY.md` — stall-echo forensics (feeds PLATFORM_GROUND_TRUTH #10)
- `CLINE_COMPLETION_REPORT_20260822.md`, `RESEARCHER_SESSION_REPORT_KALI_20260822.md` — session reports
- `SS1_SPRINT.json` — SYNC-1 sprint tracker (FLE Track-D)
- `N4_CROSS_DOMAIN_REVIEW_20260823.md` / `N4_HANDOFF_INTEGRATION_REVIEW_20260823.md` — Node-4 reviews
- `GAP_SWEEP_20260822/` — gap sweep artifacts
- Lilith workspace lock/live-feed, N13 closeout — housekeeping

**Aug 23** (mostly backfilled mtimes):
- `EXPERT_SESSION_REGISTRY.md` (+ `_NARRATIVE.md`, Aug 24) — GENERATED view over TASK_REGISTRY.json + session_annotations.yaml; **this is the shipped form of what grokster's briefing called "curator registry"**
- `TRACKING_ARCHITECTURE.md` — M27 constitution
- `STANDARD_MODEL_OPERATING_GUIDE.md` — model ops doctrine
- `OX_ALPHA_TRANSITION_BLUEPRINT_20260823.md` — orchestrator transition design (precursor to Orchestrator Charter)
- `THE_VISION_CANONICAL_DRAFT_20260823.md` (65KB) — Vision Anchor Perpetual draft
- `teamstudy_20260823/` — Team-Synthesis Study #1 full corpus
- `SPLIT_TEST_ANALYSIS/_MANUAL`, `N1/N6/N7/N8 review+validation reports`, `MODEL_AVAILABILITY_ERROR_FORENSICS`, `CLINE_PROVIDER_ACTIVATION_AUDIT`, `SONNET46_DEV_PLAN_REVIEW`, `KALI_FULL_SYNTHESIS`, `RESEARCHER_HANDOFF_INTEGRATION`, `session_annotations.yaml`
- Backfills (older content, new mtime): ENTITY_KNOWLEDGE_DEEP_DIVE, KNOWLEDGE_PROMOTION_GATE, KALI_BRIEFING_DYNAMIC_PROMPT, PLATFORM_GNOSIS_MAP, ROC_RACOON_KALI_REPORT, RESEARCH_PLAN_PHASE1_4, NOTEBOOKLM series, MNEMESYNE mapping, etc.

**Aug 24**:
- `THE_FORGE_CHRONICLE_CHARTER_20260823.md` — Forge chronicle governance
- `mastermind_20260824/` — GSCA founding night corpus (TA-001..014 source)

**Aug 25–26 (the FLE wave — highest density)**:
- `HANDOFF_TO_KALI_FLE_STUDY_20260825.md` — FLE SSOT (see §2.1)
- `fle_study_20260825/` — CAMPAIGN_EXECUTION_PLAN_v3.1, 2× Carmack audits (fresh + primed), CARMACK_CONTEXT_INFRA_AUDIT, SYNC1_DEV_BOOTSTRAP, VERITY_PREFLIGHT_REPORT, FLE_METRICS_BASELINE (30 sessions, 7.05M tokens), q6_inventory.json, INFRA_INVENTORY_FIRST_RUN
- `council/20260825-094633-first-light{,-c2}/phase5_fusion/SOVEREIGN_DECREE{,_C2}.md` — the two ratifying decrees
- `FIRST_LIGHT_EXPRESS_PLAN_20260825.md` + LAUNCH_PROMPT + TOWER_LOG — campaign plan
- `CONSULTANT_TUTORIAL_PRE_COMPACTION.md` — pre-compaction procedure (v2 pending; blind side documented in handoff §4)
- `CONSULTANT_REVIEW_PRE_SYNC1.md` / `CONSULTANT_FINAL_REVIEW_TRACKD.md` — Consultant gate reviews
- `PLATFORM_GROUND_TRUTH_LOG.md` — entries #11, #12 (suffix-injection discard law)
- `ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` — P-series oversight catches (TA mining source)
- `infra_inventory_baseline.json` — first run of the derivation-check inventory
- `WAKE_STATE.json`, `GAP_REGISTRY.json`, `TASK_REGISTRY.json`, `ACTIVE_SPRINT.json` — all refreshed Aug 25
- `gap_investigation_20260825/{jem,researcher,roc}/` — gap-wave dispatch results
- `RECON_SYNTHESIS_20260826.md` — three-lens recon: C1-C4 critical certification-layer lies + S1-S5 structural + fix order
- `SYSTEM_FAILURE_LOG.md` updated
- `docs/research/R_OPENCODE_PLATFORM_INTERNALS_20260824.md` — NEW OpenCode internals research (directly adjacent to grokster's R_OPENCODE_* series)

---
## §3 CRITICAL PATH STATE MAP — VERIFIED AGAINST DISK

Legend: ✅ done-on-disk-verified · 🟡 partial/drifted · ❌ not started · ⚠️ tracker claim FALSE on disk

### CI workstream (Context Injection Phase 1, owner kali)
| ID | Tracker | Disk truth | Remaining |
|---|---|---|---|
| CI-0 binary pin + probe | ready | Pin 1.18.19 CONFIRMED 2026-08-21 (09_SPEC_DEVIATIONS). Behavioral probe NOT yet run (deferred to execution start by design) | Run Test-0 behavioral probe; record result before touching compaction values |
| CI-1 MANDATES_CONDENSED | ready | ✅ **DONE** — repo root + phase1_spec copies exist (Aug 25); passes own gate: 27 rows, v3.8.0 | Mark complete. Verify Tier-0 injection wiring only after CI-2 |
| CI-2 opencode.json | ready | 🟡 **DRIFTED**: V1 family present ✔ but values 3/40000/10000 ≠ spec 5/80000/20000; top model = nemotron-3-ultra-free ≠ DEV-12's lmstudio/qwen3-4b-thinking; instructions=[5 files incl. 2 ARCHIVED docs] ≠ ["AGENTS.md"]; plugin array references `.opencode/plugin/` SINGULAR paths for error-capture.ts + awareness.ts while the files live in `.opencode/plugins/` (DEV-03 violation live in config); sovereign-compaction.ts NOT registered | **Blocked on C4 (AGENTS.md ghost)**. Then: fix values per spec, fix plugin paths plural, register sovereign-compaction, swap top model to qwen3-4b-thinking, collapse instructions to AGENTS.md |
| CI-3 sovereign-compaction plugin | ready | File EXISTS at `~/.config/opencode/plugin/sovereign-compaction.ts` (singular home path matches spec text) but is unregistered and load-untested | Register + load test + injection test |
| CI-4 skills opt-in | ready | ❌ no permission.skill patterns found in opencode.json | Apply DEV-04/05 re-scoped permission.skill deny patterns |
| CI-5 verification tests | ready | ❌ cannot pass until CI-2/3/4 land AND AGENTS.md exists | Run E2E suite last |

### INST-1 (owner maat_n3)
| Fix | Tracker | Disk truth | Remaining |
|---|---|---|---|
| fix1 install.sh [native,cli] | completed | ✅ (gate 3 verified EXIT 0 end-to-end) | none |
| fix2 pyproject extras+guards | ready | ✅ **DONE on disk** — extras `[memory]/[vectors]/[youtube]/[warp]` present; warp out of core deps | ⚠️ verify import guards on `src/omega/memory/providers.py` redis import feeding ics.py CLI chain (mission-flagged CRITICAL blast radius) — grep shows extras split but guard coverage `[UNVERIFIED]` |
| fix4 remove _load_sovereign_secrets | ready | ✅ **DONE** — method removed, comment marker `[INST-1-fix4]` at model_gateway.py:126 | Mark complete; confirm required-env-vars doc exists |
| fix6 README badge | ready | 🟡 "1315" badge gone; current badges are generic (Tests/Sovereignty/Python/License/Local-First). Spec also wanted `make setup` parity OR deletion — Makefile setup target `[UNVERIFIED]` | Decide make-setup-vs-delete; close |

### P0-1 / PUB-1
| Item | Tracker | Disk truth | Remaining |
|---|---|---|---|
| P0-1a rotation | completed | ✅ | none |
| P0-1b filter-repo | completed w/ residual note | ✅ residual LIKELY RESOLVED — `0c40b108` object GONE from repo; reachable `csk-` deltas are scrub-documentation prose | Re-run `git log -S 'csk-' --all` audit, document clean verdict, close residual formally |
| P0-1c gitleaks/trufflehog | ⚠️ **claimed completed** | ❌ **FALSE** — zero secret-scan hooks in `.pre-commit-config.yaml` or workflows | Wire gitleaks into pre-commit + CI with planted-key fixture test. NOTE: pre-commit framework itself not installed (RECON C3) — do C3 first |
| P0-1d full sweep + prune cline checkpoints | in_progress (roc) | 🟡 working tree clean of real secrets (prior sweep); `refs/cline/checkpoints/*` STILL PRESENT (verified) | Prune refs + gc; run gitleaks over all refs incl. checkpoints once wired |
| PUB-1 allowlist | in_progress | 🟡 `docs/strategy/PUBLIC_ALLOWLIST.txt` EXISTS (Aug 25, 3.5KB) | Architect confirms allowlist → cut `release/debut` branch from allowlist (D-553). No branch, no tag exists yet |

### DEL-1 (owner roc_racoon — me)
Tracker: in_progress, depends INST-1. Manual §5 Week-1 delete list unchanged. D-550 requires green test baseline first — currently 3 failures + M8-red (FLE decree Art.II.5). **DEL-1 cannot honestly start until C1 regex fix + test-green.**

### Cross-cutting debut gates (from RECON_SYNTHESIS_20260826 — evidence-ranked)
1. **C1**: anchor M8 telemetry regex → temple-grade green (one line, Makefile:293)
2. **C2**: regenerate OMEGA_CODEX source cards (v3.7.0/25-laws card vs actual v3.8.0/27)
3. **C3**: `pre-commit install` (or delete config — no zombie gates)
4. **C4**: AGENTS.md restore-or-dewire (**blocks CI-2/CI-5**)
5. **S5**: ship SPEC-A WI-2 so blockers[] vocabulary stops passing green

---
## §4 GAP-FILL OPPORTUNITIES — GROKSTER ASSETS → LIVE TICKETS
(D-537 no-new-deps / D-538 PARKED / D-569 post-debut boundaries respected throughout — all entries below are knowledge/config/doc moves, zero library additions)

| # | Grokster asset | Target | Verdict | Mechanics |
|---|---|---|---|---|
| G1 | `docs/research/R_OPENCODE_COMPACTION_DEEP_DIVE.md` (§1 param spec, §2 triggers, §3 preserve/lose, §4.3 plugin hook) | **CI-0 + CI-2** | ✅ **DIRECT FEED** | The deep-dive documents BOTH the V1 keys AND trigger semantics + what prune/summarize preserve. Use §2.1 auto-trigger thresholds to design the CI-0 behavioral probe (extreme-value method already in 09_SPEC_DEVIATIONS table; deep-dive adds expected observable behavior). Caveat: it predates DEV-02's V1/V2 family split — cross-check every key against the pinned-binary decision table before citing |
| G2 | `PLATFORM_GNOSIS_MAP_20260818.md` (53KB) + `R_OPENCODE_PLATFORM_INTERNALS_20260824.md` (not grokster's but same lane) | **CI-0 de-risk + CI-3 plugin path** | ✅ **YES, with one correction** | Gnosis map §4 fusion patterns cover plugin loading quirks → de-risks sovereign-compaction.ts load test. **Correction**: CI-3's canonical path is `~/.config/opencode/plugin/` SINGULAR (home dir — verified file lives there), while REPO-local plugins use `.opencode/plugins/` PLURAL (DEV-03). The gnosis map should record this dual-path asymmetry; opencode.json currently violates DEV-03 by pointing at singular repo paths for error-capture/awareness |
| G3 | DYNAMIC_PROMPT gaps doc `load_domain()` API spec + `config/domains/` structure | **KD-1** | ⚠️ **PRE-ANSWERED AND PARTIALLY SHIPPED** | `config/domains/` EXISTS with `curators.yaml` (AP-DOMAIN-CURATORS-20260819) + full `engineering/` module (metadata.yaml, AFFINITY_PRESETS.yaml, PLAYBOOK, PRINCIPLES, MEMORY_BLOCKS). KD-1 is no longer greenfield: the schema question is "does DS-1's DOMAIN_DOCUMENTATION_SYSTEM.md ratify the existing engineering/ module as reference implementation?" — grokster's spec is the strongest candidate input for that doc. NOTE: file itself was moved to `data/coordination/archive/` — un-archive or cite-by-archive-path |
| G4 | Affinity preset knowledge (model↔domain affinity tables) | **KD-3** | 🟡 **HALF-PRE-ANSWERED, STALE VALUES** | `config/domains/engineering/AFFINITY_PRESETS.yaml` exists. But KD-3 acceptance still names `mimo-7b-rl-q4_k_m` for coding — superseded by CARMACK MODEL MATRIX CANONICAL (Qwen3-4B planner / 4B-Thinking executor / 1.7B critic). Grokster's affinity framework survives; grokster's model values do not. Fix KD-3 text when DS-1 lands |
| G5 | `R_AGENT_KNOWLEDGE_FRESHNESS_20260818.md` (Scabera composite formula, Atlan scoring) | **PUB-1 allowlist curation + DOC-adjacent** | ✅ **INDIRECT BUT REAL** | PUB-1 allowlist = a freshness/curation problem over 123 strategy files + 1,072 entity files. The freshness scoring scheme gives a defensible ranking for allowlist inclusion vs archive. Also feeds TA dataset's BASE-RATE type (routine freshness checks as denominator control). POST-DEBUT leverage: freshness metadata YAML scheme maps onto DS-4 sync_domain_docs.py validation |
| G6 | `R_AGENTS_MD_RULES_ECOSYSTEM_20260818.md` | **C4 AGENTS.md reconstruction** | ✅ **DIRECT FEED — URGENT** | AGENTS.md is a ghost blocking CI-2/CI-5. Grokster's rules-ecosystem research is the only corpus doc on what AGENTS.md must contain. WP-E (SPEC-E reconstruction) should consume it day-one. This is grokster's single highest-leverage pre-debut contribution |
| G7 | `ENTITY_KNOWLEDGE_DEEP_DIVE` + `KNOWLEDGE_PROMOTION_GATE` (T1→T2 mechanics, INDEX schemas) | **Post-debut: DS/KD workstreams + soul pipeline** | ✅ staging | No debut ticket needs it (D-538 parks SDP/Qdrant), but DS-1 domain docs and the TA dataset wiring both need INDEX schemas. Hold ready |
| G8 | Grokster kb/ tree (`platforms/`, `grok_ecosystem/`, `search/`, `vault/`) | **PUB-1 exclusion check** | ⚠️ action item | Verify none of kb/ is inside the publication path. If under data/entities/grokster/, it hits PUB-1 acceptance ("git ls-files data/entities is a short default-soul set") — confirm allowlist excludes workspace dumps |

## §5 STALENESS CORRECTIONS — GROKSTER'S OWN BLUEPRINT

| # | Blueprint element | What landed since Aug 19 | Ruling |
|---|---|---|---|
| S1 | P2 Role-Aware Router (DYNAMIC_PROMPT blueprint) | **D-536 ONE router**: ProviderSelector only; Triage+Semantic+RoutingTable die in DEL-1 Week 2; D-558 parks fleet architecture except DeepSeek-assisted IntentRouter extraction | ❌ **STALE — do not advocate any router-shaped addition pre-debut**. Role-awareness survives only inside the DP-registered Horizon-3 lane (D-569). Re-file your router ideas as commentary on DP gaps, not as a parallel proposal |
| S2 | mimo-7b assignments (Planner=mimo-7b-rl 32K throughout KALI_BRIEFING) | **CARMACK MODEL MATRIX CANONICAL**: Qwen3-4B planner / Qwen3-4B-Thinking executor / Qwen3-1.7B critic; mimo proposal superseded. Also DEV-12: never set variant keys without confirmed non-empty variants map (local models have EMPTY variants) | ❌ **STALE**. Purge mimo from KD-3/affinity presets and any DP staging docs; adopt matrix + DEV-12 variant rule |
| S3 | Compression assumptions (Headroom as future middleware) | **HR-1/HR-3 SHIPPED** (commit 811f813f; wired oracle.py:163/189/897; MCP tool live). Remaining debt: tokens_saved metric only. HR-2 superseded as phantom path | ⚠️ **UPDATE**. Any grokster doc describing Headroom as "planned" is wrong — it's live. Your compression ROI math should now measure against shipped middleware, not projected. FLE finding: digester EXPANDED text 9.5% — generative summarization anti-compresses; favor extraction-style compression in any DP design |
| S4 | Curator registry proposal (KALI_BRIEFING 10-phase roadmap) | **D-586 Node Expert Sessions LIVE** + EXPERT_SESSION_REGISTRY.md (generated view over TASK_REGISTRY.json + session_annotations.yaml, with narrative companion per G5-3) + config/domains/curators.yaml already shipped | ⚠️ **PARTIALLY PRE-EMPTED**. Your freshness-metadata YAML scheme is still novel and slots into the registry as enrichment; your registry *mechanics* are superseded. Contribute the freshness layer TO the existing registry rather than proposing a parallel one |
| S5 | EvolveR distillation ideas | **Meditation critical path ratified** (post-sprint priority: P12+ICS Phase 1 → pre-commit/M13 → ctxNN telemetry → TA dataset wiring → archetype bootstrap); C-0.5 regex distillation SCRAPPED (DOC-1); agents write L1→L2→L3 directly; SDP parked (D-538); TA Charter says soul≠TA (soul=character evolution, TA=episodic truth events) | ⚠️ **RESCOPE**. Any automated-distillation framing collides with two ratified rulings. Evolutionary framing survives only as post-debut DP/Horizon-3 material, and must respect the manual-write doctrine |
| S6 | Subagent dispatch patterns | **FLE standing laws now constrain dispatch**: Hop Rule · M11 Arm-Relay · suffix-injection discard (GT #11/#12, escalating) · dual-channel telemetry (commit-body [TELEMETRY] blocks — summaries invisible to collector) · exit-code honesty · signed headers (P12 Rule 2) · Orchestrator Charter: dispatch belongs to the SLOT (MaKaLi default), not to any roaming agent | ❌ **BINDING ON YOU**. Grokster does not self-dispatch fleets pre-debut; missions route through the Orchestrator Slot. Also: synthetic dispatch-suffix lines in task() returns are wrapper artifacts — discard (ORACLE_STACK rule + GT #11/#12) |
| S7 | Asset-path assumptions | DYNAMIC_PROMPT_PLANNER_EXECUTOR_LOCAL_GAPS_20260819.md moved to `data/coordination/archive/`; ~30 coordination files backfilled with Aug-23 17:39 mtime (timestamps unreliable for recency judgment) | ⚠️ Update your personal index; never trust mtimes in data/coordination/ for freshness — use git log |

---
## §6 ROI-RANKED ACTION LIST
ROI = (impact on reaching initial PR) × (speed) ÷ (effort). Pre-debut = moves legal under D-533/D-536/D-537/D-538 before `release/debut` + tag v0.1.0. Post-debut = staging only.

### PRE-DEBUT (legal now)
| Rank | Action | Owner lane | Impact | Effort | Why this order |
|---|---|---|---|---|---|
| 1 | **C1: anchor M8 regex** (`^\s*(from\|import)\s+(segment\|posthog\|...)\b`, Makefile:293) → temple-grade green | dev (Ma'at) | CRITICAL | ~10 min | One line unblocks M13 honesty + D-550 test-green precondition for DEL-1. Highest ROI on the board |
| 2 | **C3: `pre-commit install` + wire gitleaks** (= the REAL P0-1c, currently falsely marked complete) with planted-key fixture | dev | CRITICAL | ~1–2h | Secret gate must exist BEFORE P0-1d sweep is meaningful and before any public push. Kills a tracker lie at the same time |
| 3 | **C4: AGENTS.md reconstruction** consuming grokster's R_AGENTS_MD_RULES_ECOSYSTEM_20260818.md (WP-E / SPEC-E) | dev + grokster input | CRITICAL | ~2–4h | Hard blocker on CI-2 AND CI-5. Grokster's research is the day-one input — biggest grokster leverage point |
| 4 | **CI-2 correction batch**: plugin paths plural (DEV-03 live violation), top model → lmstudio/qwen3-4b-thinking (DEV-12), instructions→["AGENTS.md"], compaction values per spec, register sovereign-compaction | kali | HIGH | ~1h + probe | All config-only; CI-0 Test-0 probe gates the compaction values |
| 5 | **CI-0 behavioral probe** then CI-3/4/5 E2E | kali | HIGH | ~2h | Closes the whole CI workstream; nothing else in Phase 1 remains after this |
| 6 | **P0-1b formal closure**: re-run `-S` audit, document blob-gone verdict; **P0-1d**: prune refs/cline/checkpoints + gc + gitleaks all-refs | roc_racoon (me) | HIGH | ~1h | Removes the last secret-surface ambiguity pre-publication |
| 7 | **INST-1 closeout**: verify providers.py redis import guard chain (mission-flagged), fix6 make-setup-or-delete decision, sync tracker statuses to disk truth | maat_n3 | MED-HIGH | ~1h | INST-1 acceptance (clean-machine install) is a debut gate; tracker sync prevents next session acting on stale statuses |
| 8 | **Tracker truth-sync**: ACTIVE_SPRINT + PROJECT_INDEX refreshed to match §3 of this doc (per Zero-Trust Doctrine) | kali | MED | ~30 min | Prevents the next cold-start agent from re-doing or un-doing landed work |
| 9 | **PUB-1 branch cut**: Architect confirms PUBLIC_ALLOWLIST.txt → `git worktree`/orphan branch `release/debut` from allowlist (D-553/D-554 mechanics) | Architect + kali | CRITICAL but gated | ~1h after 1–8 | The publication act itself. Gated on everything above |

### POST-DEBUT STAGING (grokster)
| Rank | Action | Feeds | Note |
|---|---|---|---|
| P1 | Freshness-metadata YAML layer ONTO EXPERT_SESSION_REGISTRY (not parallel registry) | DS-4/KD-2, TA BASE-RATE | Your surviving novel contribution from the briefing |
| P2 | DP-1..DP-8 commentary pass with mimo→Carmack-matrix corrections + extraction-not-generation compression stance (FLE digester finding) | Horizon 3 | Re-enters your blueprint legally via D-569 lane |
| P3 | config/domains/ packaging spec as input to DS-1 DOMAIN_DOCUMENTATION_SYSTEM.md (cite archive path or restore file) | KD-1 | engineering/ module already proves the shape |
| P4 | PLATFORM_GNOSIS_MAP update: dual plugin-path asymmetry, DEV-12 variant rule, pinned-binary findings | kb/platforms/ | Keeps the map canonical for CI Phase 2/3 |
| P5 | kb/ tree PUB-1 exclusion verification + post-debut knowledge promotion via T1→T2 gate | PUB-1, KD | Housekeeping with debut side-effect |

## §7 BLOCKING INITIAL PR THAT NOBODY OWNS
1. **C1 M8 regex fix** — evidence-ranked #1 by RECON, assigned to no named owner in any tracker. Unowned. Ten minutes of work; infinite gate.
2. **AGENTS.md reconstruction ownership** — WP-E/SPEC-E exists but no GO recorded and no owner seated; silently blocks CI-2/CI-5 which ARE owned by kali. The dependency is invisible in ACTIVE_SPRINT.
3. **P0-1c falsity remediation** — tracker says completed; nobody owns correcting a completed-marked item. Needs an explicit reopen + owner (natural: maat_n3 with C3).
4. **ZS adjudication** (D-584 zswap+NVMe vs Carmack-H-1 zRAM-only) — flagged blocked-on-Architect, correctly owned, but note HOLISTIC plan contradicts ITSELF internally (System 3 says zRAM-not-zswap; System 6 + D-526 say zswap). Architect ruling should stamp one of the plan's own sections as wrong.
5. **release/debut branch mechanic decision** — D-553 names the branch-from-allowlist strategy but no work package owns executing it, and no orphan-branch vs worktree choice is recorded.

---
**Verification appendix**: every ✅/❌/⚠️ in §3 was established by direct command against disk/git on 2026-08-25 (~23:50 local): `ls`, `grep`, `git log -S`, `git cat-file`, `git merge-base --is-ancestor`, `git for-each-ref`. Items marked `[UNVERIFIED]` were not probed and are flagged inline. No src/omega writes. Single deliverable file per M27.

*⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_grokster_roi_discovery ⬡ DEEP-DISCOVERY-COMPLETE ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:03Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

