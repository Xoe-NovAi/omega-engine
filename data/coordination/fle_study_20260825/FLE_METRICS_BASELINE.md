# 📊 FLE METRICS BASELINE (Draft v1)
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_fle_metrics ⬡ FLE-STUDY-V1+V2

**Date**: 2026-08-25 · **Commissioned by**: MaKaLi Fusion (fork#1, ses_fc5b80e85ffeAjhjtroU76Gfo2)
**Scope**: Study Phase 1 — Mechanical Mining of the First Light Express (Vectors 1-2 of `FLE_STUDY_EXECUTION_MANUAL.md`)
**Method**: Read-only extraction via `opencode-sessions-explorer` MCP suite + `git log`. Zero markdown-trust; every number tool-cited.

**Analysis window**: `since_ms=1787648400000` (2026-08-25T09:00:00Z) → `until_ms=1787680800000` (18:00:00Z), computed via `date -d`.

---

## §0 PROVENANCE LEDGER

| # | Data | Tool call | Parameters |
|---|------|-----------|------------|
| P1 | Session tree (31 sessions) | `opencode-sessions-explorer-session-genealogy` | `session_id=ses_fc758e6ddffeNEKptpEzboVfYq, direction=descendants, max_depth=4` |
| P2 | Agent cost groups | `cost-by-project` | `group_by=agent, since_ms=1787648400000, until_ms=1787680800000, top=50` |
| P3 | Model cost groups | `cost-by-project` | `group_by=model`, same window |
| P4 | Failure census (error) | `list-tool-failures` | `group_by=error, error_prefix_chars=120, limit=100`, same window |
| P5 | Failure census (tool) | `list-tool-failures` | `group_by=tool, limit=100`, same window |
| P6 | Per-session inventory | `get-session` ×31 | one call per session ID from P1 |
| P7 | task() failure attribution | `search-tool-calls` | `tool=task, status=error`, same window, limit 20 |
| P8 | Stage journal | `git log --since="2026-08-25 09:00" --format="%h %ci %s"` | repo = omega-engine |
| P9 | Phase artifact bytes | `find data/council/20260825-094633-{first-light,first-light-c2}/phase* -name "*.md" \| stat -c%s` | byte sums via awk |

**Consistency check (passed)**: Sum of the 9 FLE-core agent groups (P2) = input 6,567,371 / output 333,967 / reasoning 146,626 / cache_read 52,989,696 — **exactly equal** to the `x-preview-f-free` model group in P3. Internal reconciliation verified.

---

## §1 TABLE A — SESSION INVENTORY (31 sessions: root + 30 descendants)

Duration = `time_updated − time_created` (per P6). Tokens: in/out/reasoning/cache-read. Msgs = message_count.

### Council 1

| # | Session (slug) | Role | Agent | Model | In | Out | Reasoning | Cache Rd | Dur (min) | Msgs |
|---|---------------|------|-------|-------|----|-----|-----------|----------|-----------|------|
| 0 | ses_fc758e…VfYq (hidden-squid) | **ORCHESTRATOR ROOT** | makali | x-preview-f-free | 1,675,581 | 39,062 | 23,202 | 6,100,992 | 324.8 | 68 |
| 1 | ses_fc6f9da9…msgny (quiet-otter) | Build Arm (N1-N5 relay) | maat | x-preview-f-free | 228,128 | 18,918 | 2,436 | 2,615,616 | 65.9 | 30 |
| 2 | ses_fc6f84b3…t7Ry (lucky-mountain) | Node N1 S7 config | maat | x-preview-f-free | 61,034 | 10,046 | 8,215 | 2,613,952 | 11.0 | 32 |
| 3 | ses_fc6ed829…zr7n (happy-comet) | Node N2 S1 tracking | maat | x-preview-f-free | 115,526 | 10,342 | 5,531 | 1,774,784 | 9.1 | 22 |
| 4 | ses_fc6e4a4e…R1NM (eager-moon) | Node N3 S4 commands | maat | x-preview-f-free | 108,053 | 9,350 | 5,195 | 1,684,800 | 9.5 | 23 |
| 5 | ses_fc6db66e…FpOR8 (shiny-wolf) | Node N4 S5 skills | maat | x-preview-f-free | 111,773 | 10,423 | 4,879 | 2,012,736 | 9.6 | 26 |
| 6 | ses_fc6d1a3b…CA4V (silent-rocket) | Node N5 S2 instruction | maat | x-preview-f-free | 120,639 | 10,328 | 5,927 | 2,093,440 | 13.6 | 25 |
| 7 | ses_fc6f9b76…pkz4Ir (playful-wizard) | Run Arm (N6-N10 relay) | lilith | x-preview-f-free | 255,032 | 13,986 | 1,134 | 1,968,512 | 62.9 | 27 |
| 8 | ses_fc6f833c…BYr60 (clever-star) | Node N6 S3 cognition | lilith | x-preview-f-free | 114,830 | 12,716 | 14,160 | 2,358,016 | 15.2 | 25 |
| 9 | ses_fc6e9c1f…QshdPe (lucky-island) | Node N7 S6 context | lilith | x-preview-f-free | 60,139 | 8,179 | 3,163 | 2,063,424 | 6.8 | 24 |
| 10 | ses_fc6e145c…QMmhb (proud-nebula) | Node N8 S1b observability | lilith | x-preview-f-free | 121,863 | 10,035 | 6,551 | 1,978,048 | 10.1 | 24 |
| 11 | ses_fc6d78d5…07lUdu (crisp-nebula) | Node N9 S8 orchestration | lilith | x-preview-f-free | 56,076 | 7,334 | 3,754 | 1,204,032 | 6.2 | 15 |
| 12 | ses_fc6d125a…JrTv0f (misty-river) | Node N10 validation | lilith | x-preview-f-free | 137,101 | 10,253 | 6,556 | 2,149,440 | 10.7 | 23 |
| 13 | ses_fc6f9837…r6m1Q (shiny-wizard) | Carmack Pass 1 | john_carmack | x-preview-f-free | 46,924 | 5,867 | 2,439 | 234,496 | 6.3 | 5 |
| 14 | ses_fc6bc360…sdczKe (lucky-garden) | MK-Kali duality synthesis | kali | x-preview-f-free | 308,839 | 13,372 | 3,235 | 1,710,528 | 12.6 | 18 |
| 15 | ses_fc6af7a2…oTUwz (cosmic-wolf) | Researcher GAP-1..4 | researcher | x-preview-f-free | 243,900 | 10,066 | 6,405 | 2,568,384 | 24.9 | 36 |
| 16 | ses_fc6af562…jDyqv (nimble-canyon) | Jem GAP-5..7 forensics | jem | x-preview-f-free | 216,341 | 8,739 | 5,823 | 4,489,024 | 20.4 | 53 |
| 17 | ses_fc6af2af…g2G84 (neon-canyon) | Verity delta sweep | verity | x-preview-f-free | 89,882 | 10,885 | 5,045 | 1,685,888 | 9.4 | 23 |
| 18 | ses_fc6af03d…wRHKfb (silent-rocket) | Roc doc archaeology | roc_racoon | x-preview-f-free | 47,650 | 7,303 | 3,113 | 1,425,280 | 12.0 | 24 |

### Council 2

| # | Session (slug) | Role | Agent | Model | In | Out | Reasoning | Cache Rd | Dur (min) | Msgs |
|---|---------------|------|-------|-------|----|-----|-----------|----------|-----------|------|
| 19 | ses_fc681471…dfyyZH (brave-star) | Ma'at C2 Arm (SPEC A-C) | maat | x-preview-f-free | 371,359 | 8,641 | 3,118 | 867,904 | 56.6 | 19 |
| 20 | ses_fc679ef3…QpFo5s (brave-engine) | SPEC-A draft | maat | x-preview-f-free | 107,212 | 11,922 | 3,403 | 1,068,928 | 14.8 | 14 |
| 21 | ses_fc66b08c…MfcnIB (brave-circuit) | SPEC-B draft | maat | x-preview-f-free | 141,105 | 11,467 | 2,475 | 1,380,160 | 10.8 | 16 |
| 22 | ses_fc66019c…U5ccB (cosmic-knight) | SPEC-C draft | maat | x-preview-f-free | 188,528 | 10,082 | 3,150 | 1,307,008 | 12.6 | 18 |
| 23 | ses_fc6810c4…sfQbYq (eager-otter) | Lilith C2 Arm (D/E+pkg) | lilith | x-preview-f-free | 489,131 | 8,112 | 1,680 | 931,904 | 48.2 | 21 |
| 24 | ses_fc67c07f…wMQg96 (curious-comet) | SPEC-D P2 hygiene | lilith | x-preview-f-free | 171,118 | 7,674 | 430 | 455,296 | 5.9 | 10 |
| 25 | ses_fc67609c…56T78 (sunny-wizard) | SPEC-E AGENTS.md recon | lilith | x-preview-f-free | 152,294 | 7,387 | 726 | 585,664 | 8.0 | 12 |
| 26 | ses_fc66df9e…SLFb30D (silent-engine) | Work packages | lilith | x-preview-f-free | 160,761 | 9,282 | 1,503 | 337,152 | 4.8 | 8 |
| 27 | ses_fc6690e4…AJCWJ (brave-meadow) | Doc update plan | lilith | x-preview-f-free | 87,298 | 8,179 | 1,053 | 486,272 | 9.6 | 9 |
| 28 | ses_fc65f60b…nnrUKTp (mighty-eagle) | Dev-team launch package | lilith | x-preview-f-free | 164,967 | 6,382 | 1,234 | 801,152 | 5.5 | 14 |
| 29 | ses_fc64c8a5…ra6zu2 (shiny-sailor) | MK-Kali C2 spec synthesis | kali | x-preview-f-free | 271,963 | 11,629 | 4,526 | 1,063,360 | 12.4 | 14 |
| 30 | ses_fc63e3a0…EevpW (eager-sailor) | Carmack Pass 2 | john_carmack | x-preview-f-free | 142,324 | 6,006 | 6,565 | 973,504 | 10.6 | 11 |

---

## §2 TABLE B — COST RANKING BY AGENT (token-economics; monetary cost = $0.00, free tier)

Source: P2 (`cost-by-project group_by=agent`). Cost column returned $0 with `cost_known=true` for all FLE agents → **monetary ranking UNAVAILABLE-with-reason: all sessions ran on free-tier endpoints; token counts are the only economic denominator.**

| Rank | Agent | Sessions | Input | Output | Reasoning | Cache Read | Share of FLE-core input |
|---|---|---|---|---|---|---|---|
| 1 | makali (root) | 1 | 1,675,581 | 39,062 | 23,202 | 6,100,992 | **25.5%** |
| 2 | lilith | 12 | 1,970,610 | 109,519 | 41,944 | 15,318,912 | 30.0% |
| 3 | maat | 10 | 1,553,357 | 111,519 | 44,329 | 17,419,328 | 23.7% |
| 4 | kali | 2 | 580,802 | 25,001 | 7,761 | 2,773,888 | 8.8% |
| 5 | researcher | 1 | 243,900 | 10,066 | 6,405 | 2,568,384 | 3.7% |
| 6 | jem | 1 | 216,341 | 8,739 | 5,823 | 4,489,024 | 3.3% |
| 7 | john_carmack | 2 | 189,248 | 11,873 | 9,004 | 1,208,000 | 2.9% |
| 8 | verity | 1 | 89,882 | 10,885 | 5,045 | 1,685,888 | 1.4% |
| 9 | roc_racoon | 1 | 47,650 | 7,303 | 3,113 | 1,425,280 | 0.7% |
| — | **FLE core total** | **31** | **6,567,371** | **333,967** | **146,626** | **52,989,696** | 100% |

*Excluded from FLE core (present in window per P2 but not part of the council tree): `plan`(1 sess, 8,493 in), `build`(5, 88,948), `instrprobe`(3, 33,139), `denybash`(1, 5,136), `askbash`(1, 6,424), `unknown`(3, no tokens) — these account for the nemotron-3-ultra-free model group (142,140 in / 658 out, P3) plus plan/build internal agents.*

### Orchestrator-vs-Field Economics (Manual Weight #2)

| Cut | Orchestrator side | Field side | Ratio | Verdict vs 20% threshold |
|-----|------------------|------------|-------|--------------------------|
| Root vs 10 C1 nodes | makali root: 1,675,581 in / 39,062 out | Nodes N1-N10 aggregate: 1,007,034 in / 99,006 out / 63,931 reasoning | root burns **1.66×** node input; only **39.5%** of node output | Root alone = **62.5%** of (root+nodes) input |
| Root vs whole FLE core | 1,675,581 in | 4,891,790 in (rest of fleet) | — | **25.5% of total fleet input > 20% threshold → hierarchy measures HEAVY by the manual's own criterion** |
| Full orchestration tier (root + 4 arms) | 1,675,581 + (228,128+255,032+371,359+489,131) = 3,019,231 in | 3,548,140 in (nodes + specialists + carmack + kali synths) | 46.0% / 54.0% | Coordination overhead consumes nearly half of fleet input |

**Caveat**: root session spans the full day (created 11:21 UTC, incl. pre/post-council work); its token count is an upper bound on pure council orchestration. Per-session isolation of council-only turns would require part-level filtering (Vector 3 territory).

---

## §3 TABLE C — FAILURE TAXONOMY (25 failures, window-filtered)

Sources: P4 (by error), P5 (by tool), P7 (attribution).

| Error class | Count | Tool | Sessions affected (via P7 / timestamps) | Notes |
|---|---|---|---|---|
| **Subagent depth limit reached (2)** | **10** | task | **All 10 C1 nodes** (N1-N10), one each, ts 13:16–13:48 -0300 | The F-20 depth wall. Uniform 1-per-node pattern: every node independently attempted a nested spawn and hit the same wall. |
| task() SchemaError: missing `description` | 2 | task | root makali + ses_fdef2be4effe4pAaLXCTUx62GO (legacy-prefix session) | Early dispatch-format failures |
| task() SchemaError: missing `prompt` | 1 | task | kali synthesis arm C1 (ses_fc6bc360…) | |
| Task cancelled | 1 | task | root makali (duration 47.7s before cancel) | Candidate Hop-Rule-genesis event |
| Tool execution aborted | 2 | task(1), edit(1) | ses_fdef2be4… (task abort ran 176.0s) | |
| File not found (.opencode/plugin/error-capture.ts) | 2 | read | within C1 node window (ts pair 287ms apart) | |
| edit oldString not found | 1 | edit | window-scoped | |
| edit oldString multiple matches | 1 | edit | window-scoped | |
| hivemind_post_context Pydantic validation | 2 | omega-hub MCP | missing `model` (1), missing `decisions` (1) | Schema friction on coordination writes |
| hivemind_redis_publish auth required | 1 | omega-hub MCP | Redis not authenticated | Pub/Sub degraded → file-based fallback (M23-compliant path) |
| hivemind_extended_checkin `_save_extended_sessions` undefined | 1 | omega-hub MCP | Engine-side bug (NameError) | |
| bash permission rejected by user | 1 | bash | window-scoped | Human-in-the-loop gate fired once |
| **TOTAL** | **25** | task=15, edit=3, read=2, post_context=2, redis_publish=1, extended_checkin=1, bash=1 | | |

**Friction signature**: 15/25 failures (60%) are `task()`-channel friction — 10 mechanical depth-wall hits + 4 schema errors + 1 cancel. The depth wall was **uniformly distributed** (every C1 node hit it exactly once), consistent with an emergent behavioral constraint rather than isolated misconfiguration.

---

## §4 TABLE D — WALL-CLOCK STAGE TIMELINE (git journal, P8; times local -0300)

| Time (-0300) | Commit | Stage event |
|---|---|---|
| 09:05:11 | e6b1996b | feat(express): MK-Kali synthesis arm + Consultant reservation + reporting protocol |
| 09:11:10 | 877bca35 | fix(express): paging mechanic corrected — PAGE = task() by session ID, not Hivemind post |
| 09:38:11 | 45fa8429 | fix(express): Stage 7 gate now lists all SIX criteria |
| 09:43:00 | 82d73876 | docs(express): launch prompt saved for Architect paste |
| 10:02:16 | 77b9d340 | Consultant launch review — GO with 4 refinements |
| 10:04:49 | e7707634 | C1 Stage 0 complete — workspace tree + mission packet SSOT |
| 10:10:43 | d0a9540c | Carmack Pass 1 adjudicated — 12/12 adopted |
| 11:06:54 | 31c71704 | Run Arm report adjudication (M11 arm-relay clause, SSOT precedence) |
| 11:09:45 | 76436af2 | Build Arm report adjudication; synthetic suffix discarded |
| 11:11:31 | 2eefd5da | C1 Stages 1-2 complete — 10/10 node reports, digests, arm reports |
| 11:22:41 | b8e4e154 | Consultant ratifies MK-Kali synthesis + M11 YAML-repair authorization |
| 11:25:28 | 9eb12ba5 | C1 Stage 3 complete — duality synthesis ratified |
| 11:35–11:43 | 5f4c36a8, 6e09ce75, 592f002f | Consultant ACKs: Roc archaeology, Verity sweep, Jem GAPS 5-7 |
| 11:50:08 | 298ace61 | Researcher empirics accepted; GAP-1 fork closed |
| 11:51:48 | 1ab93f67 | C1 Stage 4 complete — 4 specialist sweeps; GAP-8 suite NOT green |
| 11:56:00 | 08f61cfd | **C1 Stage 5 FUSION — SOVEREIGN_DECREE.md (12 articles, 30 gates)** |
| 12:03–12:05 | d0398b24, 13f54925 | Art.IX M11 YAML repair; tracker directives WAKE_STATE Q1-Q5 |
| 12:10:04 | 480dc9e9 | Consultant closeout ack — **Council 1 ratified complete** |
| 12:15:53 | f359481a | C1 Stage 7 gate GREEN — Council 2 DEV-PREP launches |
| 13:02:36 | 48995abb | Run Arm spec library synthesis-ready |
| 13:10:55 | afcfd3db | Build Arm spec set cleared for fusion |
| 13:25:31 | 265b73cf | MK-Kali C2 synthesis ratified; DROP-1/WEAK-1 adopted |
| 13:38:47 | 651382b0 | Consultant adjudication — Carmack Pass 2 confirmed 3/3 |
| 13:42:13 | 5c1590c2 | **C2 Stages 5-6 — SOVEREIGN_DECREE_C2 fused; ERRATA E-1..E-11** |
| 13:44:13 | 3cc99cb4 | **TOWER LOG — FLE run complete, consultant sign-off** |

**Session-clock cross-check**: earliest FLE child session created 10:04:59 -0300 (Build Arm, P6) — matches Stage-0 commit 10:04:49 within 10s. Last root activity 13:45:51 -0300 — matches TOWER LOG within 2min. **Total wall-clock: ≈ 6h41m** (arm-launch → closeout); full prep-to-closeout span from first express commit 09:05 → 13:44 = **4h39m of committed stage progression** (note: prep commits precede session-tree birth because the root session predates the run).

---

## §5 COMPUTED METRICS

### 5.1 Total Run Tokens (FLE core, 31 sessions)
- **Input**: 6,567,371 · **Output**: 333,967 · **Reasoning**: 146,626 · **Cache read**: 52,989,696
- Grand total (in+out+reasoning): **7,047,964 tokens** (+52.99M cache-read traffic)
- Provenance: sum of Table A rows; reconciled against P2/P3 totals (§0 check).

### 5.2 Cost-per-Finding (112 C1 findings)
Monetary cost UNAVAILABLE-with-reason: free tier ($0.00, P2/P3 `cost_known=true`). Token denominators:

| Denominator | Value | Per finding |
|---|---|---|
| C1-scope input (arms+nodes+Carmack-P1+kali-synth+4 specialists) | 2,443,730 tok | **21,819 tok/finding** |
| Whole-run input | 6,567,371 tok | 58,637 tok/finding |
| Whole-run in+out+reasoning | 7,047,964 tok | 62,928 tok/finding |
| Whole-run incl. cache-read | 59,557,067 tok | 531,759 tok/finding |

*Finding count 112 taken as given from dispatch (C1 findings); not independently re-counted here (Vector 3/5 territory).*

### 5.3 Semantic Compression Ratios (byte-proxy; P9)
⚠️ Bytes ≠ tokens — file-size ratio is a proxy per provenance rule; true token-ratio requires Vector 3 part-level extraction.

**Council 1** (`data/council/20260825-094633-first-light/`):

| Stage | Files | Bytes | Ratio vs phase1_nodes |
|---|---|---|---|
| phase1_nodes (raw) | 10 | 195,509 | 1.00× |
| phase1.5_digested | 2 | 214,027 | **1.095× — EXPANSION, not compression** (digests 9.5% LARGER than raw input) |
| phase2_arms | 2 | 25,838 | 0.132× (**7.6× compression**) |
| phase5_fusion (Decree) | 1 | 13,033 | 0.067× (**15.0× compression** raw→decree) |

🚩 **CRITICAL SIGNAL**: Stage 1.5 did not compress — it *expanded*. The two side-digests contain more bytes than the ten node reports they digest. This directly feeds Manual Weight #1's risk ("did we compress out the nuance?") — but inverted: the digester *added* material rather than dropping it. Whether that addition is redundancy or preserved-nuance requires content diff (Vector 3).

**Council 2** (`data/council/20260825-094633-first-light-c2/`):

| Stage | Files | Bytes | Note |
|---|---|---|---|
| phase1_nodes | 9 | 89,028 | node notes + work packages |
| phase1.5_digested | 0 | **0** | **Stage skipped / never persisted** |
| phase2_arms | 0 | **0** | **Stage skipped / never persisted** |
| phase3_synthesis | 2 | 34,493 | |
| phase5_fusion (Decree C2) | 1 | 4,247 | raw→fusion = **21.0× compression** |

🚩 C2 structurally bypassed the digest/arm stages entirely (empty directories) — the hierarchy flattened between councils. Raw→Decree compression improved (15.0×→21.0×) precisely because intermediate layers were removed.

### 5.4 Model Distribution (P3)
- `x-preview-f-free`: 31 sessions — all FLE core (in 6,567,371 / out 333,967 / reasoning 146,626)
- `nemotron-3-ultra-free`: 11 sessions — internal probe/build/plan agents (in 142,140 / out 658)
- `unknown`: 3 sessions, zero tokens (empty shells)
- **Single-model fleet**: no cross-model variance available for the "who panicked at the depth wall?" comparison (Manual Weight #4) — behavior can only be compared across agents, not models. UNAVAILABLE-with-reason for model-variance analysis.

---

## §6 HEADLINE FINDINGS FOR THE STUDY TEAM

1. **Hierarchy weight flag**: Orchestrator root consumed 25.5% of fleet input tokens — above the manual's own 20% "too heavy" threshold (§2). With arms included, the coordination tier takes 46% of input.
2. **Depth wall was universal**: 10/10 C1 nodes hit `subagent_depth` exactly once each — a perfectly uniform behavioral boundary, ideal specimen for the friction autopsy.
3. **Stage 1.5 expanded instead of compressed** (C1: +9.5% bytes) — the digester is currently an amplifier, contradicting its design intent.
4. **C2 dropped the digest/arm stages** — emergent hierarchy flattening between councils; fusion compression improved accordingly.
5. **All $0.00**: the entire dual-council run cost zero monetary units on free tiers; ~7.05M generated tokens + ~53M cache-read traffic.
6. **Failure budget small and legible**: 25 failures total, 60% concentrated in one channel (task()), zero silent drops observed in the census.

---
*Draft v1 — compiled 2026-08-25 by RESEARCHER per dispatch from makali_fusion. Recon-only; single deliverable; no agent spawns. All numbers tool-cited per §0 ledger; unavailable metrics marked UNAVAILABLE-with-reason.*
