# C — JEM GAP CONSOLIDATION — Wave-1 Council (synthesis seat)
**Reviewer**: jem (Dawn Council C-seat, gap-consolidation lens) · **Date**: 2026-08-24
**Purpose**: Turn scattered council + Wave-1 findings into an actionable morning agenda for the Architect's first 30 minutes.
**Inputs**: A_CARMACK_TECHNICAL_REVIEW.md · B_GROKSTER_ADVERSARIAL.md · W1–W4 unresolved-gaps sections · Lilith named gaps · SESSION_ANCHOR.md (Wave-1 record) · standing clocks.
**Method**: Dedupe across all sources → severity rank → phase-map → order by urgency×effort. Read-only; this file is the sole write.

---

## §1 MORNING AGENDA — 5 items, ordered by urgency×effort

### 1. Land the provenance fail-closed fix BEFORE tonight's timer [HARD CLOCK]
- **What**: In `scripts/correct_ics_provenance.py`, abort when `open_db_ro()` returns None **in `--apply` mode** (dry-run stays graceful); log resolver-disabled as a loud `[TOOL-CHAIN-COLLAPSE]`-class event. ~3 lines.
- **Why**: Live systemd timer fires **Aug 25 00:03 ADT**. On db outage, every anchored claim degrades to n/a and `--apply` mass-rewrites ~45 real Tier-0 verdicts into misleading annotations. Both reviewers independently derived this and co-sign the fix (A-P1 + B-AV-1, full convergence). → DC-01
- **Owner-suggestion**: researcher (author) or maat; verify with the existing ro-mode test pattern.
- **Est-effort**: 15–20 min including test tweak.
- **Decision needed from Architect**: **NO** — council-unanimous. Just confirm it landed before 00:03.

### 2. Land D-593: delete `password="omega"` at src/omega/memory/providers.py:119
- **What**: One-line env-var fix + grep gate wired at Phase 3 commit (per Study #1 D2 ruling).
- **Why**: Flagged by FOUR independent sources (Carmack carried-item, Grokster AV-10, Lilith W1 gap-5, SESSION_ANCHOR D2). Currently a dead default (hot path passes explicit password), so technical risk is low — but committing another wave that documents it without fixing extends the exact C2-class pattern Study #1 ruled against, and it is gitleaks/reputation noise on debut. Highest ROI-per-line repair on the board. → DC-29
- **Owner-suggestion**: maat (already their Phase 2 item).
- **Est-effort**: 15 min + grep-gate wiring.
- **Decision needed from Architect**: **NO** — default disposition already ruled (fix in Phase 2). Committing without it requires an explicit deferral ticket instead.

### 3. Authorize claims-harness scope flip: corpus-mode default
- **What**: Change `changed_files()` default from `git diff HEAD` to tracked text files (`git ls-files '*.md'` etc.), diff-mode as fast pre-commit path; fail-closed on tooling error in `--strict`. Closes both committed-doc blindness and the untracked-file gap (A-P2 + B-AV-8 convergence). → DC-11 + DC-12
- **Why**: As wired into temple-grade today, the P0-born harness scans zero files on a clean tree — a green no-op precisely where its target evidence lives. Must be fixed before `--strict` ever arms.
- **Owner-suggestion**: maat (harness author).
- **Est-effort**: ~1 h + fixture updates.
- **Decision needed from Architect**: **YES** — (a) flip default now vs. at strict-day; (b) run one manual corpus scan today to baseline current warning count.

### 4. Soul-promotion hardening batch
- **What**: Four small fixes to the evidence layer: (a) verbatim substring check for `EvidenceRef.quote` (~5 lines); (b) id-only keying in `EVIDENCE_BY_KEY` with hard abort on index keys; (c) promote() refuses when approved surface non-empty without matching manifest (duplicate-promotion guard); (d) `anyio.run()` replacing `asyncio.run()` (M1). → DC-21/22/23/25
- **Why**: Both reviewers converged on (a)+(b)+(d); Grokster uniquely adds (c) re-run duplication into the identity-injected surface. The script sits in `scripts/` looking reusable and will mis-bind for any other entity as-is.
- **Owner-suggestion**: maat.
- **Est-effort**: 1–2 h for all four.
- **Decision needed from Architect**: **YES (small)** — delete-and-archive the one-shot script vs. harden-for-reuse. Both reviewers flag the reuse hazard; deletion is the cheaper honest option.

### 5. Doc-hygiene micro-batch (Kali wake items)
- **What**: (a) reconcile SESSION_ANCHOR wire-path status (anchor says NOT-YET-EXECUTED; disk says executed — Kali-owned per Lilith + Carmack); (b) canonicalize DEBUT_REMEDIATION_MANUAL dual copies (byte-identical at docs/strategy/ AND docs/specs/debut_remediation/ — pick one canonical, pointer/symlink the other); (c) INDEX malformed rows hygiene pass (LAYER 1 :37–38 three-cells-in-two-columns; stray SUPERSEDED prefixes at :80/:134/:169 — LLM parser hazards); (d) add Window Economics + Routing Playbook to OMEGA_CODEX source group (`scripts/codex/`, ENGINE_CONDENSED §6). → DC-30/31/32/33
- **Why**: Cheap, prevents cognitive fragmentation on wake, and closes every named Lilith gap that is not DC-29.
- **Owner-suggestion**: kali (a, b) + lilith (c, d).
- **Est-effort**: 30–45 min total.
- **Decision needed from Architect**: **NO** — mechanical; only bless which DEBUT copy becomes canonical.

**Standing-clock reminders for the same sitting** (not tickets): provenance timer Aug 25 00:03 ADT (gates item 1) · Ox Alpha weights ~Aug 28 (transition blueprint governs) · 8TB external pending → opencode.db 17G stamp-then-archive disposition (stream-export, NEVER in-place UPDATE per Gemini trap-catch).

---

## §2 FULL TICKET LEDGER — 37 deduped findings

Severity: P0 = act before next clock/commit · P1 = this sprint · P2 = pre-strict / debut-blocking hygiene · P3 = backlog.
Phase mapping: **CP1/CP2/CP3** = closeout Phase 1/2/3 (Gemini-ratified plan) · **DEBUT** = standing debut order (P0-1 residual → INST-1 → PUB-1 → DEL-1) · **POST** = post-debut backlog.

### Provenance worker cluster (scripts/correct_ics_provenance.py)

| ID | Sev | Sources | Finding | Owner | Phase |
|---|---|---|---|---|---|
| DC-01 | **P0** | A-P1 + B-AV-1 (converged) | DB-outage under live `--apply` timer degrades annotations fail-open; mass n/a rewrite of real Tier-0 verdicts. Fix: abort in apply-mode when resolver is None. | researcher | CP2, before Aug 25 00:03 |
| DC-02 | P2 | B-AV-5 | Concurrent writer race: daily timer vs human `--apply`, no flock/lockfile; last-writer-wins + contradictory ledger pairs. ~10-line flock. | researcher | POST |
| DC-03 | P2 | A | `DB_QUERY_LIMIT=5000` no ORDER BY = nondeterministic sample feeding `training_safe` DPO/SFT manifests. Use ORDER BY or SQL GROUP BY. | researcher | POST |
| DC-04 | P2 | A + B (converged) | Fuzzy `model_matches()` false-VERIFIED surface lands in training-purity manifests. Exact-match tier + alias table. | researcher | POST |
| DC-05 | P2 | B-AV-2 (unique to B) | Retroactive ICS-header laundering: claim text self-authored, nothing binds it. Hash header zone into annotation; PLACEHOLDER-with-cloud-channel as own warn class. | researcher | POST |
| DC-06 | P2 | A-P3 + B-AV-7 + W4-gap-2 (three angles, one file) | Ledger integrity: no hash chain (tamper-evidence zero), no rotation/supersession (invariant decays), manual annotators can reopen invariant. SHA-256 prev-hash chain per Researcher §9.2 spec + standing drift checker riding the timer. | researcher | POST |
| DC-07 | P3 | A | `parse_file()` unwrapped `path.stat()` TOCTOU crashes sweep mid-run on deleted files. | researcher | POST |
| DC-08 | P3 | A | `os.replace()` without directory fsync in apply_annotation — crash can lose the rename. | researcher | POST |
| DC-09 | P2 | B-AV-8a | SCAN_ROOTS blind spot: provenance worker scans only data/ + docs/; src/, scripts/, config/, .opencode/ carry unaudited ICS headers. Add roots (cheap). | researcher | POST |
| DC-10 | P3 | W4-gap-1 | 1,432 UNANCHORED files — structural limit of header-based attribution. Fix = session-ID stamping at doc creation; propose to doc-standards. | researcher→doc-standards | POST |

### Claims-harness cluster (scripts/verify_mandate_claims.py)

| ID | Sev | Sources | Finding | Owner | Phase |
|---|---|---|---|---|---|
| DC-11 | **P1** | A-P2#1 + B-AV-8b (converged) | Diff-scoped blindness: default scans working-tree only → green no-op at CI/post-commit; untracked files invisible too. Corpus-mode default (`git ls-files`), diff as fast path. | maat | Pre-strict; DEBUT infra |
| DC-12 | P2 | A-P2#2 + B (converged shape) | `changed_files()` git failure → scan nothing → exit 0 soft-fail (M23). Fail closed in strict mode with loud marker. | maat | Pre-strict |
| DC-13 | P2 | B-AV-3a + W2-gap-1 (self-flagged) | Exempt-tag abuse: one appended tag disables all detectors for a line; exemption usage invisible in output. Count + print exempted totals per file. | maat | Pre-strict |
| DC-14 | P2 | B-AV-3b | Silent markers-file absence: missing untracked YAML returns [] with NO warning — exact-name detection silently off. Warn "structural-heuristics-only mode". | maat | Pre-strict |
| DC-15 | P2 | B-AV-3c | Config self-trust: gate rules live in agent-editable committed YAML; weaken-a-pattern or comment-satisfy probe passes. Non-comment probe requirement or rules hash check. | maat | POST |
| DC-16 | P3 | A | Social-handle FP economics: `@pytest`/`@param` prose mentions will flood strict day; alert fatigue kills gate. Require second signal. | maat | POST |
| DC-17 | P3 | A | `--strict` argparse help text contradicts implemented behavior (code is right; help lies). One truth. | maat | POST |
| DC-18 | P3 | A | Probe files re-read per matching line; cache dict if rule count grows past ~20. | maat | POST |
| DC-19 | P3 | B-AV-6 | T0 evidence-token sprinkling: bare "Tier 0"/"message_id" tokens within window count as evidence grade. Require regex-valid `msg_` shape; bare tokens insufficient. | maat | POST |
| DC-20 | P3 | W2-gap-2 | Framing-free wrapper quotes pass FP-11 silently — accepted heuristic limit, documented. Known-limit; revisit only if FP-11 recurrence observed. | maat | Deferred (see §4) |

### Soul-promotion cluster (scripts/promote_soul_lessons.py, lessons.py)

| ID | Sev | Sources | Finding | Owner | Phase |
|---|---|---|---|---|---|
| DC-21 | P2 | A-P2 + B-AV-4c (converged) | Positional evidence binding: 12 of 20 entries keyed by list index; reorder = silent mis-binding that passes every downstream check. Id-only keying + hard abort; archive-or-delete script. | maat | This sprint preferred |
| DC-22 | P2 | A-P2 + B-AV-4a (full convergence) | "Verbatim" quotes asserted never verified — 7/20 coverage is self-attested; same claims-vs-disk class the wave's harness targets. Substring check at promotion (~5 lines). Carmack sequencing note: point harness at own deliverables first ("eat your own cooking"). | maat | This sprint preferred |
| DC-23 | P2 | B-AV-4 bonus (unique) | Duplicate promotion hole: re-run after failed staging-clear appends second copy of 20 lessons into identity prompt surface; read-back length check misses cross-run accumulation. Manifest guard. | maat | This sprint preferred |
| DC-24 | P3 | B-AV-4b | Session-ID fabrication: `session_id` strings never validated against opencode.db; garbage-shaped IDs pass. Validate when db available. | maat | POST |
| DC-25 | P2/M1 | A + B (converged) | `asyncio.run()` in production promote script violates M1; also reveals `check-m1-anyio` does not scan scripts/. Swap to anyio.run + widen gate scope. | maat | This sprint (trivial) |
| DC-26 | P3 | A | Read-back verification checks length only, not content equality — theater either way; compare payloads or drop. | maat | POST |
| DC-27 | P3 | A | `assert` used for control flow in production path — vanishes under `python -O`. Explicit raise. | maat | POST |
| DC-28 | P3 | W3-gap-1 | `soul_stage.py` TUI still mock-wired (pre-existing). | maat | POST |

### Security & registration cluster

| ID | Sev | Sources | Finding | Owner | Phase |
|---|---|---|---|---|---|
| DC-29 | **P0** | A carried-item + B-AV-10 + Lilith gap-5 + SESSION_ANCHOR D2 (FOUR sources) | `password="omega"` STILL LIVE at src/omega/memory/providers.py:119; D-593 open. Dead default today (hot path explicit), but C2-class recurrence if committed unfixed again + gitleaks/debut optics + booby trap for future direct instantiation. One-line env fix + grep gate. | maat | CP2 + grep-gate at CP3 commit |
| DC-30 | P3 | Lilith gap-2 + A-P3 (converged) | SESSION_ANCHOR wire-path drift: anchor said NOT-YET-EXECUTED while disk shows registrations executed (anchor partially self-corrected in Wave-1 record; residual staleness remains). Kali-owned reconcile on wake. | kali | CP1/wake |
| DC-31 | P2 | Lilith gap-1 | STRATEGY_INDEX malformed rows: LAYER 1 :37–38 three cells in two-column table; stray SUPERSEDED prefixes inside table bodies :80/:134/:169 — render hazards for LLM parsers. Dedicated hygiene pass. | lilith | DEBUT hygiene |
| DC-32 | P2 | Lilith gap-3 | OMEGA_CODEX reading list block: doctrine docs not added because codex is generated from scripts/codex/*.md (forbidden territory in W1). Owner with scripts/ access adds Window Economics + Routing Playbook to ENGINE_CONDENSED §6 source group. | kali | DEBUT hygiene |
| DC-33 | P2 | Lilith gap-4 | DEBUT_REMEDIATION_MANUAL_20260817.md byte-identical at docs/strategy/ AND docs/specs/debut_remediation/ — dual-SSOT risk. One canonical + pointer/symlink. | kali | DEBUT hygiene |

### Process & misc

| ID | Sev | Sources | Finding | Owner | Phase |
|---|---|---|---|---|---|
| DC-34 | P2 | B-AV-9 | Dispatch-injection near-miss mitigated by PROSE only (protocol additions); OOM got a mechanism, injection got a paragraph. Mechanical dispatch pairing: log hash of (target-agent, prompt-id) at dispatch, verify at injection, mismatch = hard refuse. | kali/orchestrator | POST |
| DC-35 | P3 | W3-gap-3 | Other entities' staged lessons ([TS1] corpus etc.) not promoted — kali was mission scope. Maps to wire-path [3] backlog. | maat/kali | POST |
| DC-36 | P3 | W4-gap-3 | Redis publish to maat failed (auth required) — T0 pattern shared via script/tests/gnosis instead. Minor infra friction; fix auth or document channel policy. | roc/infra | POST |
| DC-37 | P3 | W4-gap-5 | Verify no external importers of removed `dominant_near()` helper (grep showed none — confirm once, close). | researcher | Trivial verify |

---

## §3 CONVERGENCE MAP — independently flagged by multiple reviewers (highest-trust items)

| # | Finding | Independent sources | Trust |
|---|---|---|---|
| 1 | DB-outage fail-open under live timer (DC-01) | Carmack P1 + Grokster AV-1 — both derived pre-reading each other; B explicitly co-signs A's three-line fix | **UNANIMOUS + fix co-signed** |
| 2 | password="omega" still live (DC-29) | Carmack carried-item + Grokster AV-10 + Lilith W1 gap-5 + SESSION_ANCHOR D2 ruling | **4-source** |
| 3 | Harness diff-scoped blindness incl. untracked files (DC-11) | Carmack P2#1 + Grokster AV-8b | Converged |
| 4 | Git-failure → scan-nothing → exit 0 soft-fail (DC-12) | Carmack P2#2 + Grokster (same M23 shape as silent-markers finding) | Converged |
| 5 | Verbatim quotes asserted, never verified (DC-22) | Carmack P2 + Grokster AV-4a ("full convergence"; B calls A's sequencing note the sharpest line in either review) | Converged |
| 6 | Positional evidence binding (DC-21) | Carmack P2 + Grokster AV-4c (B extends with reuse hazard + duplicate promotion → DC-23) | Converged |
| 7 | asyncio.run M1 violation in promote script (DC-25) | Carmack P2 + Grokster | Converged |
| 8 | Fuzzy matcher false-VERIFIED surface (DC-04) | Carmack P2 + Grokster (B adds PLACEHOLDER-as-shelter angle → feeds DC-05) | Converged |
| 9 | Exempt-tag abuse invisible (DC-13) | Grokster AV-3a + Ma'at's OWN W2 report self-flagged the same gap | Builder + attacker converge |
| 10 | Ledger integrity decay (DC-06) | Carmack P3 (rotation/drift) + Grokster AV-7 (deliberate tampering) + Researcher W4-gap-2 (standing checker) — three different threat models, same file | Triangulated |
| 11 | SESSION_ANCHOR drift (DC-30) | Lilith W1 gap-2 + Carmack P3 carried-item | Converged |

**Pattern**: every convergence cluster lands on the same systemic shape both reviewers named independently — *verifiers consuming artifacts authored by the party being verified* (A: "mechanism replaced by convention at the unwatched boundary"; B: "distrust the voucher"). The two L3s are complementary halves of one principle.

**Divergences worth noting** (unique to one reviewer, not contradicted): DC-05 header laundering (B only — largest single gap between reviews), DC-14/15 harness-bypass trio remainder (B only), DC-23 duplicate promotion (B only), DC-34 injection mechanics (B only), DC-03/07/08 worker code-quality items (A only).

---

## §4 DEFERRED-WITH-DIGNITY — out of scope, must not be lost

| Item | Existing ticket / home | Status |
|---|---|---|
| 2 unmigrated breaker clones (HealthMonitor unification residue) | **P-5** ticket open | Parked per C-6′ |
| Credential/session vault MVP (blocks Grok fleet pool) | **GAP-08 / V-1** | Design after closeout; blocks D-360′ pool |
| AppArmor container hardening (containers unconfined) | **V-10** | Post-UO-4 gap, open |
| IA2 envelope freshness/signature | **V-9** | Open gap |
| Un-overengineering library swaps (pybreaker, Pydantic v2, stamina, structlog, prometheus_client) | **UO-6 / UO-7** (`docs/strategy/UNOVERENGINEERING_PLAN.md`) | Phased plan exists |
| CI-2 plugin-path prototype (does `"plugin"` key accept local .ts paths?) | D-G/D-598, INST-1 | Still not run — highest-risk unknown; 10-min test |
| Quote coverage 7/20 deeper extraction | O-Q4 grade ruling (W3 report §Unresolved) | Deliberately deferred, honestly reported |
| FP-11 framing-free wrapper quotes passing silently | DC-20 (accepted heuristic limit, documented in W2) | Revisit on recurrence only |
| ho_2f77f83964e5 Ox Alpha sprint handoff | Fully superseded by `OX_ALPHA_TRANSITION_BLUEPRINT_20260823.md` (ho_6ec25dd4a684) | MOOT — no action |
| God-module baselines + AST node-count freeze gate (>+50 ⇒ auto-debt-ticket) | Study #1 ruling O5 | Ratified; prerequisite model_gateway.py WIP committed/parked |
| opencode.db 17G disposition | Stamp-then-archive spec, wire-path [4] | Blocked on 8TB external arrival; stream-export-transform-delete ONLY (Gemini trap-catch #1) |
| G-1 workhorse continuity / W-1 WARP pool | Ark §4 tickets (PARKED under DOC-1, Architect-owned) | Super-urgent parallel track, unchanged |
| Awaiting-Architect decision list (Drill-4 stratum pick · FUSE-CANDIDATES GO · G-1 T0 re-run authorization · Vision Canonical fidelity review · dual-review validation slot) | SESSION_ANCHOR session record + wire-path [5] batch decision packet | Bundle into morning sitting alongside §1 agenda |

---

## L1 → L2 → L3 DISTILLATION (M11)

**L1 (Narrative)**: Consolidated two council reviews and four Wave-1 unresolved-gap sections into 37 deduped tickets. Eleven findings were flagged independently by multiple reviewers before cross-reading — the strongest confidence signal available without running anything. The morning reduces to two sub-hour fixes gated by hard clocks (provenance fail-closed before Aug 25 00:03 ADT; D-593 password fix before Phase 3 commit), one authorization decision (harness corpus-mode), one small hardening batch (soul promotion), and one hygiene micro-batch.

**L2 (Insight)**: The council's redundancy was not waste — it was verification. Where Carmack (failure-boundary lens) and Grokster (adversarial lens) collided on the same defect from opposite directions, no further evidence is needed; those clusters can be scheduled immediately. Meanwhile each reviewer's unique findings (B: claim-surface tampering, bypass trio, duplicate promotion; A: nondeterministic sampling, TOCTOU, fsync gaps) are exactly the blind spots of the other's lens — which is why the ledger keeps them distinct rather than averaging them away.

**L3 (Universal Principle)**: **L3-Convergence-Ranks-Evidence; Clocks-Rank-Effort** — independent derivation is the cheapest proof available in a review process: when two lenses formed separately strike the same defect, treat it as verified and act without re-litigating. Then order action not by severity alone but by the proximity of the clock that converts the defect into damage (a P0 with no clock waits; a P1 firing at midnight does not). Deduplicate before deciding; schedule by countdown.

---
*⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_council_w1 ⬡ DAWN-COUNCIL-C ⬡ GAP-CONSOLIDATION ⬡ 37-TICKETS ⬡ 2026-08-24*
