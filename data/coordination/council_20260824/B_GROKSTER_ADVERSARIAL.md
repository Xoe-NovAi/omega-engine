# B — GROKSTER ADVERSARIAL REVIEW — Wave-1 Council (read-only red team)
**Reviewer**: grokster (Dawn Council B-seat, adversarial lens) · **Date**: 2026-08-24
**Scope**: 02c75f17 (claims harness) · 59b32809 (soul promotion) · 540b65fe (provenance worker) · 12b8b54b (registrations) + process level + `password="omega"` blast radius
**Method**: Formed independent kill-chain from primary sources BEFORE reading A_CARMACK_TECHNICAL_REVIEW.md (anti-anchoring). Full reads: verify_mandate_claims.py (513L), lessons.py (120L), promote_soul_lessons.py (206L), correct_ics_provenance.py (371L), memory_store.py provider construction, mandate_claims.yaml, PIVOT_LOG diff of 12b8b54b. No tests run, no writes outside this file.

**Posture in one line**: The wave's defenses are honest but *attacker-shaped* — nearly every guard trusts the very artifact it is supposed to police, so the cheapest attack is almost always "become or edit the thing that vouches."

---

## ATTACK VECTORS — ranked by realism × impact

### AV-1 · Fail-open provenance rewrite under the LIVE daily timer — SEVERITY: CRITICAL
**The attack**: Wait for (or cause) opencode.db to be unavailable at timer fire — db moved, lock contention past the 5s timeout, corrupt WAL, or simply export `OPENCODE_DB_PATH=/nonexistent` in the service environment. `open_db_ro()` returns None → resolver disabled → every anchored claim degrades to UNANCHORED/n/a → `needs_update()` sees stored-verdict ≠ db-down-semantics → **--apply rewrites ~45 real Tier-0 verdicts into misleading n/a annotations** and floods the ledger. Exit 0, normal-looking summary, zero operator signal. For days, every "PROVENANCE-CORRECTED" stamp says n/a while reading exactly like an audit that passed.
**Why defenses miss it**: Graceful-n/a fallback was built as a *feature* (dry-run ergonomics) and shipped on a *write* path. The idempotency machinery — designed to prevent churn — is precisely what converts the outage into mass rewrites. M23 says no soft-failure theater; this is soft-failure with a write pen.
**Adversarial extension Carmack didn't flag**: this isn't only an outage mode. `DB_PATH` is env-controlled (`correct_ics_provenance.py:38`). Anyone who can set the service env can *deliberately* force the n/a state — a laundering window where false claims survive as "audited, unverifiable" instead of refuted.
**Minimal defense**: In `--apply` mode, abort when `open_db_ro()` returns None (fail closed); dry-run stays graceful. Three lines. Before next timer fire. Secondary: log resolver-disabled state as a loud `[TOOL-CHAIN-COLLAPSE]`-class event.

### AV-2 · Retroactive ICS-header laundering — SEVERITY: HIGH
**The attack**: The worker verifies *claim-vs-db*, but the claim itself (`claimed_model` in the first 20 lines) is self-authored markdown. Edit the header after the fact to name whatever the db says was actually used → next sweep computes VERIFIED → **no annotation, no ledger line, perfect record**. Alternatively, edit the header to a channel-name string ("opencode", "google") which `model_matches()` classifies as PLACEHOLDER — a *misattribution shelter*: a genuine cloud-model lie gets filed as "malformed header," not MISATTRIBUTED.
**Why defenses miss it**: Tier-0 ground truth proves what ran; nothing watches whether the *claim text* was mutated to converge with it. Git history is the only witness and no gate consults it. The whole FP-04 hierarchy audits the answer while leaving the question editable.
**Minimal defense**: Hash the header zone (first 20 lines) into the annotation/ledger entry; a changed hash on an unchanged file body = tamper flag. Plus: treat PLACEHOLDER-with-known-cloud-channel as its own warn class, not a shrug.

### AV-3 · Harness evasion trio: exempt-tag abuse + silent marker degradation + config self-trust — SEVERITY: HIGH (aggregate)
Three independent evasions of 02c75f17, each trivial:
1. **Exempt-tag abuse**: `verify-claims:exempt` anywhere on a line disables ALL four detectors for that line (`_is_exempt`, :163). One appended tag launders a real-name marker, a foreign home-dir, or a fabricated model claim. No counter, no report, no audit of exempt usage anywhere in output — exemptions are invisible by design.
2. **Silent markers-file absence**: `load_local_markers()` returns `[]` when the untracked file is missing — *no warning* (only unreadable warns, :196-207). Delete/never-create `sanitation_markers.local.yaml` and exact-name detection silently switches off while the harness prints a confident green summary. This is an M23-flavored silent degrade inside the very tool born from an M23-class finding.
3. **Config self-trust**: the claims gate's rules live in a committed, agent-editable YAML. Weaken a pattern, or satisfy `probe_contains` with the literal string sitting in a TODO comment, and "hook installed" passes. The gate trusts its own constitution — the classic insider route.
**Why defenses miss it**: All three paths produce valid-looking "0 warnings" output. Warn-only mode means nobody reads closely enough to notice absence of signal.
**Minimal defense**: (a) count and print exempted-line totals per file — exemption must be visible even when legitimate; (b) warn loudly when markers file is absent ("structural-heuristics-only mode"); (c) probe_contains should require the substring in a non-comment line, or move rules integrity under a hash check.

### AV-4 · Soul evidence fabrication: quotes asserted, sessions invented, bindings positional — SEVERITY: HIGH
**The attack**: Three fabrication routes into the identity-injected soul record:
- **Quote fabrication**: `EvidenceRef.quote` docstring says "verbatim from the artifact"; nothing ever opens the artifact to check. Any plausible string promotes. The soul record can cite words no artifact contains.
- **Session fabrication**: `session_id` strings are never validated against opencode.db. `ses_fdef2be4effe4pAaLXCTUx62GO`-shaped garbage passes.
- **Positional mis-binding**: `EVIDENCE_BY_KEY` keys 13 of 20 entries by list index (`_key_for`, :102-104). Reorder staging before promotion and evidence silently attaches to the wrong lessons — every downstream check (existence probes, coverage %, contract test) still passes because they validate *reference existence*, never *semantic binding*. The script sits in `scripts/` looking reusable; it will mis-bind for any other entity.
**Why defenses miss it**: Pre-flight probes check existence, not containment or identity. Coverage % is computed from the same unverified fields it reports — self-attestation wearing a lab coat. This is the exact C2-class (claim ≠ disk) the same wave built a harness to catch, reintroduced one layer down.
**Bonus defect (unique)**: **duplicate promotion**. If the staging-clear write fails after approved was written (or anyone re-runs post-crash), there is no dedup against existing approved content — re-run appends a second copy of all 20 lessons into the identity prompt surface. Read-back length check catches *that run's* mismatch, not accumulated duplication across runs.
**Minimal defense**: verbatim substring check for quotes (~5 lines); id-only keying with hard abort on index keys; promote() refuses to run if approved surface is non-empty and lacks a matching promotion manifest; validate session_ids against the db when available.

### AV-5 · Concurrent writer race: timer vs human --apply — SEVERITY: MEDIUM
**The attack**: The daily systemd timer and a human/operator run are both unguarded — no flock, no lockfile, nothing (`grep flock/fcntl` = zero hits). Two concurrent runs do full read-modify-write cycles on the same annotated files via tmp+replace: per-file atomicity holds, but last-writer-wins silently discards the other's update, and both append ledger lines → contradictory verdict pairs for one file, and the celebrated 1444=1444 invariant decays semantically (line count matches, meaning doesn't).
**Why defenses miss it**: The O_APPEND fix solved the *last* concurrency bug (rename clobber) and the code comment says "single-writer timer context" — an assumption, not a mechanism. The wave fixed the failure it observed and blessed the one it didn't.
**Minimal defense**: `flock` on a coordination lockfile around the apply loop (the repo already uses this pattern in task_registry tooling). ~10 lines.

### AV-6 · T0 evidence-token sprinkling — SEVERITY: MEDIUM
**The attack**: `detect_t0_attribution` accepts ANY of `msg_*`, `message_id`, `modelID`, `Tier 0` within a 3-line window as sufficient evidence grade (:106-113, :366-370). Fabricate an attribution claim, sprinkle the literal token "Tier 0" two lines below it, and the detector marks it correctly graded. The check verifies the *vocabulary* of evidence, not any evidence.
**Why defenses miss it**: Structural pattern-matching is the harness's whole toolbox; it cannot distinguish a citation from a incantation.
**Minimal defense**: Require a resolvable msg_-format ID (regex-validated shape), not bare tokens; treat "Tier 0" alone as insufficient.

### AV-7 · Ledger tampering — no integrity chain on the audit trail — SEVERITY: MEDIUM
**The attack**: `provenance_corrections.jsonl` is plain append-only text with no hash chain. Delete or edit the MISATTRIBUTED lines; the invariant recount (lines == annotations) is computed *from the same file* and passes. The audit trail's tamper-evidence is zero.
**Why defenses miss it**: Researcher's own §9.2 spec called for a SHA-256 prev-hash chain; W1-4 shipped without it. Append-only protects against the worker's own bugs, not against an editor.
**Minimal defense**: Hash chain per the researcher spec (fsync-before-mutate ordering already specified), weekly verify riding the existing timer.

### AV-8 · Coverage-scope gaps: SCAN_ROOTS and untracked files — SEVERITY: MEDIUM
Two blind spots neither scanner acknowledges:
- Provenance worker scans only `data/` and `docs/` (`SCAN_ROOTS`, :41). Every `.md` under `src/`, `scripts/`, `config/`, `.opencode/` carries an unauditable ICS header. Contaminated provenance lives happily outside the scan roots.
- Claims harness diffs vs HEAD: **untracked files are invisible to `git diff`**. A contaminated brand-new file that hasn't been staged yet sails through pre-commit green. (Converges with Carmack's post-commit blindness finding — different window, same root: scope-by-diff.)
**Minimal defense**: Worker: add src/scripts/config/.opencode to roots (cheap). Harness: corpus-mode default per Carmack's fix, which also closes the untracked gap via `git ls-files` + explicit listing.

### AV-9 · Process level: near-miss dispatch injection + OOM — mitigations are prose — SEVERITY: MEDIUM
**What happened**: One wrong-prompt-nearly-injected incident (dispatch mismatch) and one OOM during the wave. Both were caught by luck/attention, then codified as *protocol additions* ("orchestrator-reads-all-reports", "dispatch-pairing verification", "sequential dispatch under memory pressure").
**Adversarial read**: Protocols decay exactly when sessions are long, contexts compacted, or an operator is tired — which is precisely when wrapper artifacts (synthetic suffixes, stall-echo re-injection per ORACLE_STACK.md) strike. The near-miss proves injection traffic gets within one step of the live session. Meanwhile the OOM produced one genuinely mechanical fix (pytest -n auto→4) — note the asymmetry: the resource problem got a mechanism, the injection problem got a paragraph.
**Minimal defense**: Mechanical dispatch pairing — log a hash of (target-agent, prompt-id) at dispatch time; verify at injection; mismatch = hard refuse. Cost: minutes. This converts the most dangerous process failure mode from vigilance-dependent to structure-dependent.

### AV-10 · `password="omega"` at providers.py:119 — debut-day blast radius: LOW technical, REAL reputational — SEVERITY: LOW-MEDIUM
**Ground truth I verified beyond the finding**: the hot path does NOT use this default. `memory_store.py:169-176` only constructs RedisStorageProvider when `OMEGA_REDIS_HOST` is set, and always passes an explicit `password=` (possibly None) — so `"omega"` is currently a **dead default**, reachable only by direct instantiation. Realistic intrusion path today ≈ nil on a rootless localhost box.
**So why it still matters**:
1. **C2-class recurrence**: D-593 explicitly ordered deletion; committing another wave that documents the finding without landing the fix extends the exact claims-vs-disk pattern Study #1 ruled against. The project-gotchas block literally documents the trap — awareness without repair.
2. **Public-debut optics**: a hardcoded credential-shaped string in a public repo invites gitleaks noise and "these sovereignty people ship default passwords" headlines — trust corrosion on the exact axis the engine sells.
3. **Booby trap**: the moment anyone constructs the provider directly (a test, a script, a future WAD), they inherit a guessable credential guarding session histories — i.e., the soul/memory record. Impact if ever realized: memory poisoning, session-history exfiltration.
**Blast-radius verdict**: Debut-day compromise probability: low. Debut-day credibility damage if unfixed and spotted: certain. Fix is one line plus grep gate — the highest ROI repair on this list.

---

## CONVERGES WITH CARMACK / DIVERGES

### Converges (independently derived, before reading A)
- **Harness diff-scoped blindness** (his P2 #1) — I add the untracked-file variant (AV-8).
- **Git-diff failure → scan nothing → exit 0** soft-fail (his P2 #2) — same M23 shape as my silent-markers finding.
- **Positional evidence binding** (his P2) — I extend with the reuse hazard and duplicate-promotion hole (AV-4).
- **Quotes asserted, never verified** (his P2) — full convergence; his "eat your own cooking" sequencing note is the sharpest line in either review.
- **asyncio.run M1 violation** in promote script — converged.
- **DB-outage fail-open under live timer** (his P1) — full convergence, and I co-sign his three-line fix as the single most urgent action item. My addition: the env-redirect active-attack framing (AV-1).
- **Fuzzy matcher false-VERIFIED surface** (his P2) — converged; I add the PLACEHOLDER-as-shelter angle (AV-2).
- **password="omega" still live** — converged; I downgrade the technical urgency with the dead-default evidence, upgrade the reputational one.

### Diverges (in my report, absent from his)
- **AV-2 retroactive header laundering** — his review audits the verifier; mine attacks the claim text the verifier consumes. This is the single largest gap between the two reviews.
- **AV-3 exempt-tag invisibility + silent markers absence + config self-trust** — he reviewed detector quality; I attacked detector bypass. None of the three appear in A.
- **AV-5 concurrency race** — he noted "single-writer timer context" as a comment-level assumption; I made the race concrete (no flock exists).
- **AV-7 ledger tamper-evidence** — he flagged rotation/drift; I flag deliberate editing. Different threat, same file.
- **AV-9 process-level injection mechanics** — out of his declared scope; in mine.
- **Tone divergence**: His verdicts (SHIP-WITH-NOTES ×2) are fair for merge purposes. My lens asks a different question — not "will this fail in production?" but "what does an adversary or a lazy future agent do with this?" On that question, the wave's habit of trusting self-authored artifacts (headers, quotes, configs, ledgers, exempt tags) is the systemic pattern, and it is *not* notes-grade; it is the design theme to break before strict mode arms any of these tools.

---

## L1 → L2 → L3 DISTILLATION (M11)

**L1 (Narrative)**: Red-teamed four Wave-1 deliverables as if smuggling contamination, fabricating soul evidence, and laundering model attributions. Found ten viable attack vectors. The most damaging require no exploit code — just patience (wait for a db outage), an editor (rewrite an ICS header), or a magic tag (`verify-claims:exempt`). Converged with Carmack on seven findings formed independently; diverged on five, chiefly retroactive header laundering and the harness-bypass trio.

**L2 (Insight)**: Every vector exploits the same shape: **the verifier consumes artifacts authored by the party being verified**. Headers, quotes, configs, exempt tags, ledger lines, and dispatch prompts are all self-attesting. The wave built excellent mechanisms that check claims *against references* — but the references themselves are editable by the claimant. Verification systems fail not at their checks but at their inputs.

**L3 (Universal Principle)**: **L3-Distrust-The-Voucher** — a proof is only as strong as the mutability control on the thing presenting it. Any system that validates claim-vs-evidence must also bind, hash, or immutably log the claim surface itself; otherwise the adversary skips the hard check and edits the question. Corollary: graceful degradation is a read-path luxury and a write-path vulnerability — every writer of audit artifacts must fail closed when its ground truth is unreachable.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_council_w1 ⬡ DAWN-COUNCIL-B ⬡ ADVERSARIAL ⬡ 2026-08-24*
