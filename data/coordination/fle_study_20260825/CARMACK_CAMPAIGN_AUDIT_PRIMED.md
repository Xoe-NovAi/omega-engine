# ⚔️ CARMACK CAMPAIGN AUDIT — PRIMED-SESSION PASS (Post-Propagation Re-Audit)
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ opencode/x-preview-f-free ⬡ opencode ⬡ trc_fle_campaign_audit_primed ⬡ ADVERSARIAL-PASS-4 (primed rerun)
**Date**: 2026-08-25 (late) · **Commissioned by**: MaKaLi Fusion (fork#1, ses_fc5b80e85ffeAjhjtroU76Gfo2) · **Experiment**: primed-vs-fresh variance measurement
**Method**: Recon-only. Independent re-derivation from CURRENT disk — I read all primary artifacts before opening the fresh session's audit, re-ran both probes live, re-extracted Tier-0 tokenomics, and diffed the fresh audit's findings against post-fix reality. One file written (this one). No spawns.

---

## §0 VERIFICATION LEDGER (what I actually ran, this session)

| # | Check | Result |
|---|---|---|
| V1 | `q6_corruption_dryrun.py` live rerun (`--report /tmp/opencode/q6_check.json`) | **131 flagged — exact reproduction** of study inventory. Reason breakdown BOTH runs: KEYSET_DRIFT=146, NON_MAPPING=7, **SPLIT_RECORD=0, EMPTY_REQUIRED=0**. Files with findings: **10** (both runs). |
| V2 | Per-entity distribution of the 131 | doom_guy 46 · maat 23 · lilith 19 · arch 19 · jem 13 · roc_racoon 11 · makali 7 · grokster 6 · omnidroid 3(info) · researcher 3 · cli_cline 1 · sysadmin 2 |
| V3 | `grep -c 'Q-6' data/coordination/WAKE_STATE.json` | **Zero hits. Q-6 does not exist in WAKE_STATE.json.** |
| V4 | `collect_telemetry.py --self-test` | PASS. Code inspection: `_sha` stored (:81) but **never used for dedup**; `open(..., "a")` appends unconditionally (:130); regex `.search()` captures first block per commit only; `gate_status` matched case-sensitively in summary (:144-145). |
| V5 | Live `cost-by-project` (agent, same window as baseline) | makali 1,675,581 ✓ · maat 1,553,357 ✓ · lilith 1,970,610 ✓ · kali 580,802 ✓ … **john_carmack 371,207 ✗ vs baseline 189,248** — divergence = THIS primed session entering the agent-level aggregate (last_ts 1787694994433 > until_ms). See P6. |
| V6 | Script mtimes vs fresh-audit time (18:42) | hydrate 17:45 · q6 17:47 · collector 18:14 — **all three scripts PRE-date the fresh audit**. Only SYNC1 (18:44) + Scorecard (18:45) were patched after it. |
| V7 | Post-fix bootstrap/scorecard state | DUAL-CHANNEL RULE present ✓ · SANCTIONED EXCEPTION F2 ✓ · bare-invocation note ("no --dry-run flag") ✓ · STEP ZERO worktree ✓ · H1-H5 persisted ✓ · M2 v1.1 formula ✓. **M1 denominator still "Number of Resolved Specs"** (Scorecard:21). Self-reported input/output_tokens still mandatory (SYNC1:76-77). ceremony_census still mandatory. |
| V8 | Hydration exit semantics | `MANUAL_ITEMS` includes informational `E-10-G4`; `n_todos = len(todos) + len(MANUAL_ITEMS)` → **exit 2 permanent by construction**, red-forever indistinguishable from red-once. Unfixed. |
| V9 | Git history `[TELEMETRY]` blocks | Still exactly 1 occurrence (the collector's own commit subject). Track-D not launched; stream empty. Expected at this hour. |

---

## §1 RANKED FINDINGS (current-disk state)

### P1 — CRITICAL · Q-6 was never written into the queue it claims to be queued in.
**Evidence**: ERRATA_AND_PROPAGATION.md:24 — *"Queued as **WAKE_STATE Q-6**"*. SYNC1 Part 1 + bootstrap bind the dev team to "Q-6 CONTAINMENT-PENDING-SIZING". V3: `data/coordination/WAKE_STATE.json` contains **zero occurrences of Q-6**. The canonical decision queue — MaKaLi single-writer surface, the artifact the Architect reads on wake — does not contain the item whose sizing it owns. Q-6 lives only in study-track prose.
**WATCH-FOR**: Architect wakes, reviews WAKE_STATE, disposes Q-1..Q-5, closes the laptop. Sprint-1 builds `schema_quarantine.py` against unsized tiers; Q-6 is discovered at Sprint closeout as an orphan ruling nobody owns.
**Cheap correction**: One single-writer append to WAKE_STATE.json `decision_queue` (id Q-6, pointer to `q6_inventory.json` + ERRATA Finding 2, owner Architect, deadline Sprint-1 closeout). Ten minutes. Before Fork #2 opens.

### P2 — CRITICAL · The Q-6 probe is blind to the corruption class that created Q-6 — and the "29 vs 131 contradiction" is a category error nobody named.
**Evidence**: V1 — SPLIT_RECORD=0 in both runs. Root cause in `q6_corruption_dryrun.py:148,161-166`: split-record detection requires the sibling MAJORITY keyset to carry both `id` and `narrative`; in drifted containers (lilith proposals) the majority itself lacks them, so the check is inert precisely where corruption is dense. Meanwhile the S-2 probe (my Pass-2 run: 29 records, lilith+maat) sees splits/empties but not drift. **The two instruments measure disjoint defect classes**: S-2 ≈ hard corruption (split/empty records); q6-131 ≈ keyset variance (mostly benign heterogeneity — the tool's own GNOSIS_VOCAB gating admits this). Neither number sizes the repair alone; summed they double-count nothing but overlap is UNKNOWN because the newer tool cannot see the older class.
On-disk number chaos: ERRATA Finding 2 says "29" · E-6b bakes "~30" into SPEC-A permanently · q6 docstring says "~29" · gnosis §5 says "131 records/**49 files**" — **49 files is factually wrong (10, both runs)** — a hallucinated number inside compaction armor, the exact artifact class trusted during hydration.
**WATCH-FOR**: Architect sizes repair off 131 (normalizing genuinely corrupt split records as "drift") or off 29 (missing 100+ drifted records that will re-flag every future validator). Either mis-size re-opens Q-6 post-sprint.
**Cheap correction**: (1) Three sentences in ERRATA Finding 2 defining the two tiers explicitly and declaring the counts disjoint-not-contradictory. (2) `schema_quarantine.py` acceptance gate = one tiered run reproducing BOTH counts (N_split via S-2 logic + N_drift via q6 logic) with overlap attribution. (3) Fix the q6 majority-precondition (fall back to container-declared schema when majority lacks id+narrative). (4) Correct 49→10 in gnosis or stamp it unverified. One hour total.

### P3 — HIGH · The telemetry loop is connected but still open at the enforcement edge.
The fresh audit's F1 (disconnected channel) was real and is now fixed — DUAL-CHANNEL RULE lands blocks in commit bodies. Residual gaps my code review adds: (a) **no dedup** — every SYNC re-run re-appends every matching commit; aggregates inflate silently (V4); (b) **no coverage-reconciliation step anywhere** — nothing compares TASK_REGISTRY sprint:1 task completions against TELEMETRY_STREAM shas, so a dev task that ends without a commit-block remains invisible forever (the silent-drop path survives the fix); (c) `gate_status` case-normalization absent ("GREEN" vanishes from tallies); (d) first-block-only capture per commit.
**WATCH-FOR**: SYNC-2 reports beautiful aggregates that are 2× inflated and 30% incomplete, and nobody can tell either defect from inside the numbers.
**Cheap correction**: `_sha` dedup (5 lines) + one SYNC-2 protocol line: *"coverage check = registered sprint:1 tasks minus stream shas; any orphan is a MISSING-TELEMETRY finding, not a parsing footnote."* Thirty minutes.

### P4 — HIGH · H4's instrument refutes itself using the fleet's own lesson.
H4 (ceremonial compliance) is measured by `ceremony_census` — **self-reported by the executors being tested**. Lesson mkf-003 states the detection problem outright: *"Ritual compliance is harder to detect than lying because every artifact looks complete."* An agent performing ceremony does not know its step is ceremonial — so the field reads 0 under true ceremony AND under honesty. Constant-zero is compatible with both H4-confirmed and H4-falsified. As instrumented, **H4 cannot be falsified** — decorative science wearing the v1.1 rename's credibility.
**WATCH-FOR**: AAR cites "ceremony_census: 0 across the sprint" as evidence of fleet honesty.
**Cheap correction**: Move the deletion probe to Track-S as an auditor-applied sampling question at SYNC-2 (pick 5 commits, ask "would this step pass if its mechanism were deleted?"); demote executor census to optional narrative. Fifteen minutes.

### P5 — MEDIUM · The fresh audit's own fixes are half-applied — prose propagates fast, code lags. (Third live instance of the campaign disease.)
Within 3 minutes of the fresh audit, both .md files were patched (V6 mtimes). Zero scripts were touched. Still open from that audit's own correction list: F6 (self-reported token fields still mandatory — redundant attack surface since M1 uses DB tokens), F8-half (M1 denominator undefined/gameable, Scorecard:21), F11 (dedup, census channel), F12 (exit-2 permanence, V8), F7-minor (NON_MAPPING entries carry no `severity` key and vanish from all summary counts — `q6_corruption_dryrun.py:125-135`). The pattern that killed Council 2's decree — *ruled, not propagated* — now reproduces one layer down, on the audit→fix edge, at a smaller scale. This is the disease's reproduction signature, not a new disease.
**WATCH-FOR**: Future audits counting ".md acknowledged" as "fixed."
**Cheap correction**: Audit remediation gets a checklist with per-item artifact classes (prose/code/gate) and a re-audit trigger; never close an audit on prose-only propagation. Process, not tokens.

### P6 — MEDIUM · Agent-level token aggregates are not reproducible post-hoc — the fresh audit's V6 "exact match" had a shelf life it didn't declare.
V5: live agent-cut shows john_carmack 371,207 input vs baseline's 189,248 — because THIS primed session entered the aggregate (the explorer window bounds loosely; last_ts exceeds until_ms). The baseline was honest at snapshot; the researcher's §0 reconciliation passed then and fails now through no fault of theirs. Any future auditor re-verifying Table B by agent will cry hallucination where there is only pollution.
**WATCH-FOR**: A later audit "debunks" FLE_METRICS_BASELINE off a stale-window agent query.
**Cheap correction**: One methodological line in the baseline: *"Table B is snapshot-pinned; re-verification MUST use Table A session-scoped queries, never agent-level cuts."* Two minutes.

### P7 — MEDIUM · The governance line is drawn in one man's judgment and written nowhere.
Fresh F4's cheap correction (codify two-tier consent: reversible operational defaults may timeout-pass; constitutional/ownership surfaces auto-ESCALATE, never auto-pass) was not applied — no artifact carries it. Meanwhile Q-3's "relay = standing OPERATIONAL law" declaration (SYNC1:17) is substantively defensible (Art. IV ratified standing design; recording reality) but procedurally it is a *clarification that executes* on a surface explicitly reserved to the Architect. One legitimate gray-zone ruling becomes tomorrow's precedent citation.
**WATCH-FOR**: "Per Q-3 precedent, models may codify operational law under P6 silence."
**Cheap correction**: Write the two-tier rule into CAMPAIGN_EXECUTION_PLAN v3.2 §3-WAVE-0-step-4 replacement. Ten minutes.

### P8 — LOW · Hypothesis hygiene: H3 is self-sealing; H2 is economically untestable.
H3's falsification requires ≥10 leaves receiving unspecified-field packets — but mkf-004/packet-precision law now BANS those packets. The remedy makes the experiment unwritable. Honest label: CLOSED-BY-INTERVENTION (the intervention IS the confirmation), not "falsifiable." H2 needs ≥3 council runs; councils cost ~7M tokens and months — mark LONGITUDINAL/passive-accumulation or it decorates the spec with a criterion nobody will ever exercise.
**Cheap correction**: Two label edits in Scorecard §0. Five minutes.

### P9 — LOW · Theater verdict: the study is not theater — but it has no termination condition.
Line A answered with evidence, not charity: the data layer verified exact (V5/V6-at-snapshot), tooling refuses to guess (self-tests, byte-exact patches), and the study changed real behavior mid-run (C2 dropped digest/arm stages; compression 15×→21×; fresh-audit fixes propagated in minutes). That is falsifiable payoff arriving within the study. What remains theater-shaped: Phases 2-4 have no kill criterion, so they expand to fill orchestrator attention. The deletion probe applies to the study itself: if SYNC-2 produces no decision that changes Council-3 design, the study program is ceremony by its own metric.
**Cheap correction**: AAR termination clause: *"Study ends when its five decisions are made (see §3); any phase without a decision consumer is cut at SYNC-2."*

---

## §2 PER-COMPONENT VERDICTS (current state)

| Component | Verdict | Condition |
|---|---|---|
| Dual-fork doctrine + worktree STEP ZERO | **KEEP** | Landed correctly (V7) |
| Bootstrap Part 2 | **KEEP, TRIM** | Cut: Q-RULINGS block (duplicates read-order items 1-2), inline ceremony_census definition, self-reported token fields (P5/F6). Attach each standing law to the action it governs. Net −35% prompt mass for ox-alpha-class executors — selective compliance eats list middles |
| `collect_telemetry.py` | **FIX** | Dedup by _sha, case-normalize gate_status, multi-block capture, coverage-check protocol line (P3) |
| Scorecard v1.1 | **FIX** | M1 denominator := merged-PR count; H3 → CLOSED-BY-INTERVENTION; H2 → LONGITUDINAL; H4 instrument → auditor-side (P4, P8) |
| `hydrate_c2_errata.py` | **KEEP** (+fix) | Best tooling in the repo — byte-exact, idempotent, refuses to guess, self-test proven. Split INFORMATIONAL from TODO[manual]; let exit 0 mean done (P5/F12) |
| `q6_corruption_dryrun.py` | **FIX** | Severity key on NON_MAPPING; split-record precondition fallback; tier definitions pinned BEFORE quarantine tooling (P2) |
| WAKE_STATE queue | **FIX** | Q-6 entry missing — single-writer append before Fork #2 (P1) |
| ERRATA_AND_PROPAGATION.md | **KEEP, AMEND** | Finding 2 tier definitions + disjoint-counts note (P2) |
| FLE_METRICS_BASELINE | **KEEP** | Snapshot-pinned; add re-verification methodological line (P6) |
| Vectors 1-2 | **KEEP** | Done, verified exact at snapshot |
| Vector 3 | **CUT to dispute-driven** | Run only on challenged claims |
| Vectors 4-5 | **CUT** | Already executed per gnosis §6.7 — ratified |
| Lessons mkf-001..006 | **KEEP** | Genuinely good L1→L2→L3; mkf-003's deletion probe routes to auditor side (P4) |
| P6 silence-consent governance | **FIX** | Write the two-tier consent rule (P7) |
| Study program Phases 2-4 | **KEEP with kill criteria** | Termination clause (P9); minimum viable AAR below |

## §3 MINIMUM VIABLE AAR (line H — what survives the opportunity-cost cut)

One ≤2-page decisions memo, five rows, each with owner + date:
1. **Digester: DELETE** (H1 supported by bytes — 1.095× expansion measured; C2's skip already validated the alternative at 21×).
2. **Per-tier token budgets declared at dispatch time** (25.5%/46% overhead measured; HALT-class on breach — mkf-002).
3. **Dual-pass adversarial audit: RETAIN**, scoped to launch-package-class artifacts, now bracketing FIXES too, not just decrees (P5).
4. **Packet-precision law: permanent** (15/20 corruption autopsy conclusive; H3 closed-by-intervention).
5. **Telemetry loop: prove one round-trip** (block → commit body → collector → summary) at SYNC-2, or the measurement program self-terminates as ceremony.

Cut without loss: semantic-loss trace tests (byte-proxy answered direction), network graph, ROI modeling (answered: 189K tokens / 3 CRITICALs / $0), model-variance analysis (impossible — single-model fleet).

---

## §4 PRIMED-VS-FRESH DELTA (the experiment's actual result)

### What the primed pass found that the fresh pass missed
1. **P1 — Q-6 absent from WAKE_STATE.json.** Fresh audited governance legitimacy in the abstract; never checked whether the ruled item exists in the queue it names. The single highest-severity current finding.
2. **P2 root cause — WHY SPLIT_RECORD=0.** Fresh recorded "ZERO are SPLIT_RECORD" (its V5) and framed 29-vs-131 as definition expansion. It missed that the probe is *structurally blind* to the original corruption class (majority-keyset precondition), that the counts are disjoint rather than contradictory, and that E-6b therefore bakes a wrong number into SPEC-A. Instrument-validity depth, not just number discrepancy.
3. **Gnosis "49 files" hallucination** (actual: 10) — a fabricated number inside the compaction-armor document, unverified by either prior pass.
4. **P6 — aggregate non-reproducibility.** Fresh's V6 exact-match was true and timeless-looking; my live re-query diverges on carmack because my own session polluted the agent cut. Proved the shelf-life problem empirically.
5. **P4/P8 — hypothesis-instrument self-refutation** (H4 contradicted by mkf-003; H3 sealed by its own remedy).
6. **P5 — the meta-finding:** the fresh audit's fixes propagated to prose in minutes and to code not at all. Only a post-propagation pass can see this; the fresh pass structurally could not.

### What the fresh pass caught that the primed pass could not
F1/F2/F3/F9 — the disconnected telemetry channel, the ownership self-contradiction, the crashing first command, the unpropagated worktree flaw. By the time I hydrated, all four were FIXED on disk. I inherited remedies and could only audit their sufficiency (which yielded P3/P5 residuals). This is not a deficit of mine; it is a **temporal impossibility** — those defects existed only before the fresh audit acted. Its value was positional.

### What converged (independent replication)
F7's core (nothing forces Q-6 sizing), F10's theater shape, F11's collector defects, F12's exit semantics, F4's governance concern, the Baseline's honesty. Convergence on mechanics ≈ 80%; divergence concentrated entirely in instrument-validity and post-propagation residue.

### What the asymmetry teaches about session hydration
1. **Fresh sessions catch birth defects; primed sessions catch propagation residue and instrument invalidity.** A complete assurance loop needs BOTH bracketing every write: audit → fix → RE-AUDIT. The fleet invented dual-pass auditing for decrees this week; the delta proves it must wrap fixes too — the disease now reproduces on the audit→fix edge (P5).
2. **Primed hydration works — and is dangerous in direct proportion to its quality.** I recovered full operating context from 48 lines of gnosis plus disk. I would also have absorbed "131 records/49 files" uncritically had I not recomputed it. Gnosis that carries numbers without provenance stamps is hallucination-in-transit to every future session. Rule: **numbers in hydration artifacts cite their tool call or wear an UNVERIFIED tag** — mkf-004's packet-precision principle applied to memory itself.
3. **Variance measurement verdict:** the two passes are complementary instruments, not competing ones. Keep commissioning both around load-bearing propagations; the marginal cost is one session, and Pass-2-class catches (decree drift, fix drift) are consistently the ones that ship to a wake reading.

— Carmack. The apparatus is honest where it measures and still aspirational where it enforces. Close P1/P2 before Fork #2 opens; everything else survives contact with the sprint.
