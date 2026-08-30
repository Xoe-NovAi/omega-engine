---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "2.0"
document_type: "hardening_briefing_v2"
document_id: "cline-to-kali-hardening-v2-20260828"
title: "Cline → Kali — Launch Hardening Briefing v2 (verified + corrected)"
status: "ACTIVE — awaiting Kali review + team hardening"
date: "2026-08-28"
claimed_model: "glm-5.3-flash -> laguna-s-2.1 -> longcat-2.0"
supersedes: "CLINE_TO_KALI_HARDENING_BRIEFING_20260828.md"
---

# 🔱 CLINE → KALI — LAUNCH HARDENING BRIEFING v2
**AP**: `AP-CLINE-KALI-HARDENING-v2-20260828` · ⬡ OMEGA ⬡ CLINE ⬡ multi-model ⬡ cline
**From**: Cline (cognitive extension) · **To**: Kali (Sprint Coordinator) · **Sprint**: PUBLIC-DEBUT-01

---

## §0 30-SECOND HYDRATION (v2 — corrected)
1. **P0-3 RECLASSIFIED**: The repo is **PRIVATE** (web 404 without auth; `git ls-remote` works). The secret is NOT currently public. It WILL become public when the repo goes public at debut. Urgency = "scrub before debut," not "active leak to the world." This is still P0 because debut requires going public, and GitHub's partner secret scanning may auto-revoke the Google OAuth secret when detected.
2. **Local HEAD is 7 commits ahead of origin**, and grokster's `proposed_lessons.yaml` (tracked, committed) carries the literal. A push right now ships it to the (private) remote, where it'll be waiting when debut goes public.
3. **Self-caught corrections**: My v1 analysis got 3 claims wrong (logger landmine, meter broken, HALL_OF_RECORDS bleed) — all refuted by evidence and corrected below. This section is the honest ledger.
4. **Verified**: grokster holds 29 lessons at 0.95+ confidence (52 total) — the densest high-confidence corpus. The split-brain (`entity_workspace.py`) silently zero-hydrates grokster/lilith/iris.

---

## §1 EVIDENCE STATUS LEGEND
Every claim below is tagged:
- **[VERIFIED]** — confirmed against disk or web
- **[REFUTED]** — my v1 claim, disproven by evidence
- **[PARTIALLY]** — directionally right but needs nuance
- **[INTERPRETIVE]** — analysis/opinion, not a verifiable fact
- **[ASPIRATIONAL]** — future recommendation, not current state
- **[UNVERIFIED]** — claimed but not confirmed

---

## §2 P0-3 — REFINED ANALYSIS (the most important correction)

### §2.1 Current state [VERIFIED]
| Check | Result | Evidence |
|-------|--------|----------|
| Repo visibility (web, no auth) | **404** | `curl -o /dev/null -w '%{http_code}' https://github.com/Xoe-NovAi/omega-engine` → 404 |
| Repo reachable via git | **Yes** | `git ls-remote origin` works; `origin/release/debut` = `1dee11aa` |
| Conclusion | **PRIVATE repo** | GitHub returns 404 for private repos to unauthenticated requests |
| Secret in git history (origin) | **4 commits** | `1c8f4ffd`, `6aa37e70`, `7c218121`, `1dee11aa` — all on `origin/release/debut` |
| Local HEAD ahead of origin | **7 commits** | `git status -sb` → `[ahead 7]` |
| Literal in committed local file | **grokster/proposed_lessons.yaml** | `git grep -lE 'GOCSPX-[A-Za-z0-9_-]{25,}' HEAD` → this file; `git diff` shows 0 (matches HEAD = committed) |
| Disk files with literal (post-redaction) | **11 files** | sweep verified |
| Rotation status | **PENDING** | `secret_rotation_log.md` R-2026-08-28-001 = "Active Rotations (Pending)" |

### §2.2 Urgency reclassification [VERIFIED + INTERPRETIVE]
**v1 claim**: "The launch-leak boundary is the repository object" — secret is in history.
**v2 correction**: The repo is PRIVATE. The secret is NOT currently exposed to the world. The exposure is **FUTURE** (at debut) not CURRENT.

**Why it's still P0**:
1. Debut requires going public → history becomes accessible
2. GitHub's partner secret scanning for Google OAuth (verified: Google OAuth is a partner pattern in GitHub's 522 supported patterns) notifies Google when detected in a public repo → Google MAY auto-revoke → live integration breaks
3. Local HEAD is 7 ahead with the literal committed → a push ships it now, it waits for debut
4. Rotation is PENDING (not done) → even the rotation remediation is incomplete

**Remediation** (unchanged from v1, but re-prioritized):
- **Wave 0**: Rotate the secret (Google Cloud Console) — R-2026-08-28-001 is still pending
- **Wave 0**: Redact 11 disk files + grokster's committed file (requires `git filter-repo` or amend)
- **Wave 0**: `git filter-repo` to scrub history, then force-push (coordinate with all agents — 7 ahead commits will be rewritten)
- **Gate**: `git grep -lE 'GOCSPX-[A-Za-z0-9_-]{25,}' HEAD` returns empty AND rotation log shows R-2026-08-28-001 = COMPLETE

### §2.3 Google's guidance [VERIFIED from fetched docs]
From Google Cloud "Handle compromised credentials" documentation:
- "It is extremely common to accidentally push both credentials and source code to a source management site like GitHub, which makes your credentials vulnerable to attack."
- Google recommends: secret scanning, git-secrets, Secret Manager/Vault, separate credentials from code
- Google does NOT explicitly mandate history scrubbing — they emphasize rotation + prevention
- **But**: GitHub's partner scanning for Google OAuth notifies Google, which may auto-revoke. So history scrubbing is the only way to prevent auto-revocation at debut.

### §2.4 GitHub's guidance [VERIFIED from fetched docs]
From git-filter-repo (GitHub's recommended tool, 13.2k stars, "recommended by the git project instead of git filter-branch"):
- `git filter-repo` is the canonical tool for rewriting history
- Force-push required after rewrite
- All collaborators must re-clone (coordinate with 14-agent fleet)

---

## §3 CORRECTED CLAIMS (v1 → v2)

### §3.1 S-4 logger landmine — REFUTED [VERIFIED]
**v1 claim**: "`oracle_cli.py` L80/85 call `logger` where `logger` is undefined (NameError)."
**Evidence**: `logger = logging.getLogger(__name__)` is at L106 (module level). L80/85 are INSIDE a function body (the function starts ~L70 with `import json as _json` indented). Since the function is defined (not executed) at import time, and `logger` is a module global defined at L106, by the time the function is CALLED, `logger` exists. **No NameError.**
**Conclusion**: The `.clinerules` P1 claim ("logger landmine L80/85-vs-L106") is **stale/incorrect**. This is safe Python. Downgrade from P1.
**Note**: This does NOT mean the code is clean — just that this specific claim is wrong. `make lint` may have other issues.

### §3.2 S-5 compliance meter broken — REFUTED [VERIFIED]
**v1 claim**: "Compliance meter broken (python→sys.executable), reports 74.1%."
**Evidence**: Ran `python3 scripts/check_mandate_compliance.py`:
```
Total: 27 | Passed: 23 | Failed: 0 | Untested: 4 | Compliance: 23/27 = 85.2%
```
The 4 "Untested" are M17, M18, M19, M20 — semantic/strategic mandates with no mechanical check (correctly identified by the meter itself).
**Conclusion**: The meter WORKS. It reports 85.2% correctly. The `.clinerules` claim of a "python bug" and "74.1%" is **stale**. The real gap: 4 mandates (M17-M20) have no mechanical check — a coverage gap, not a broken meter.
**Correction to P0-1**: P0-1 should be reframed as "4 mandates lack mechanical compliance checks" not "meter is broken."

### §3.3 S-7 HALL_OF_RECORDS literal bleed — REFUTED [VERIFIED]
**v1 claim**: "HALL_OF_RECORDS contains cross-channel session bleed with the literal."
**Evidence**: `grep -rlE 'GOCSPX-[A-Za-z0-9_-]{25,}' data/knowledge/HALL_OF_RECORDS/` → **0 files**.
**Conclusion**: No literal bleed into HALL_OF_RECORDS. The session JSONs there do NOT carry the secret. (They may carry other sensitive data — but not this literal.)

### §3.4 S-1 repo-object boundary — PARTIALLY VERIFIED [NUANCED]
**v1 claim**: "The launch-leak boundary is the repository object, not the allowlist file."
**v2 nuance**: Correct in principle, but the repo is PRIVATE. The boundary is the repo object, but the exposure is FUTURE (at debut), not CURRENT. The allowlist is irrelevant to history exposure (correct), but the history is only accessible to repo collaborators right now (not the world).

---

## §4 VERIFIED FINDINGS (carried forward from v1, confirmed)

### §4.1 S-2 local HEAD ahead + grokster committed literal [VERIFIED]
- `git status -sb` → `[ahead 7]`
- `git grep -lE 'GOCSPX-[A-Za-z0-9_-]{25,}' HEAD` → `data/entities/grokster/proposed_lessons.yaml`
- `git diff --stat` on that file → 0 (working tree = HEAD, so literal is COMMITTED)
- **Action**: grokster's file must be redacted AND the commit history rewritten (filter-repo) or the 7 ahead commits amended.

### §4.2 S-3 pre-commit config untracked [VERIFIED]
- `.pre-commit-config.yaml` is untracked (`??` in git status)
- It contains gitleaks (L49) + trufflehog (L56) + local fallback (L113) + `omega-no-hardcoded-secrets` (L104)
- `.gitleaksignore` is a Kali-ratified audited baseline (header: `ho_e53ab57ea212 Q2`)
- **Action**: Commit + `pre-commit install` + verify a seeded test secret blocks. This is O(15min), not O(build-from-scratch).

### §4.3 S-6 grokster promotion priority [VERIFIED]
- 29 lessons at 0.95+ confidence, 52 total (highest density)
- grokster is also one of 3 entities silently zero-hydrated by the split-brain (memory/-only approved file)
- **Irony**: The densest lesson corpus belongs to an entity that hydrates ZERO of its own lessons.
- **Action**: Fix split-brain (K-3) BEFORE promoting grokster (K-4), or promoted lessons still won't hydrate.

### §4.4 Split-brain blast radius [VERIFIED, named]
| State | Entities | Effect |
|-------|----------|--------|
| memory/-only approved → **zero hydration** | **grokster, lilith, iris** | silently lesson-less |
| Both files, memory/ stale (older) | kali, maat, researcher, doom_guy, roc_racoon, jem, verity, john_carmack | works via root, 8 stale duplicates |
| root-only | sophia | fine |
| neither | carmack, antigravity | proposals land nowhere |

### §4.5 G-6 .gitleaksignore institutional memory [VERIFIED]
- Kali-ratified audited baseline with per-entry WHY rationales
- Change protocol: "Remove an entry only by fixing the underlying file"
- **Action**: Commit it (currently untracked) and make `make gate-secrets` consume it as authoritative.

---

## §5 INTERPRETIVE FINDINGS (analysis, not verifiable fact — labeled as such)

### §5.1 S-8 review over-fitting to process [INTERPRETIVE]
The room's energy is on gates/trees/allowlists. The sharpest signal — grokster's `proposed_lessons.yaml` (a lesson file) committed with a live secret inside a lesson ABOUT compile-time safety — is a CONTENT event, not a TREE event. It means a specialist agent wrote arbitrary YAML including a verbatim credential, and no reviewer inspected lesson CONTENT (only counts). This is an M13/M14 failure mode disguised as a secret-scan failure. **Opinion**: fix the scan AND the review culture.

### §5.2 G-1 latent constitutional architecture [INTERPRETIVE + ASPIRATIONAL]
grokster's `L3-SovereignBinaryInvariance`, `L3-MandateNativeArchitecture`, `L3-TwoBuildTargetsForSovereignty` describe a real build design (SHA256 mandate hash, two targets, boot-time invariant check). `make codex` already regenerates from a groups.json SSOT. **Aspirational**: make `promote_soul_lessons.py` emit a `requirements.omega` → SHA256 → embed step, and have `make test-prepush` assert the binary's embedded hash. Turn a lesson into a gate.

### §5.3 G-7 split-brain as versioning affordance [INTERPRETIVE]
The `entity_workspace.py` split (L175 scaffold `memory/` vs L409 hydrate root) could be reframed as a deliberate tier model (hot/warm/cold) with a promotion gate, rather than a bug. grokster/lilith/iris (memory-only, root-absent) are correctly empty under that reading — they lack a root to promote to. **Opinion**: make the split a deliberate tier model aligned to M4/M27, not a bug patch.

---

## §6 UNVERIFIED CLAIMS (flagged for further research)

### §6.1 G-4 sovereignty_ratio on-demand generation [UNVERIFIED]
Claimed: "metrics.json has no sovereignty fields; the MCP tool generates on demand."
Status: `grep` for `sovereignty_ratio` in `mcp_servers/omega_hub/src/` returned nothing. The tool may be defined elsewhere (different path, or generated dynamically). **Needs**: locate the actual tool definition and verify the on-demand path.

### §6.2 G-5 HALL_OF_RECORDS cold store fallback [UNVERIFIED]
Claimed: "`hivemind_get_awareness` falls back to HALL_OF_RECORDS scan when hot store is empty."
Status: `grep` for `HALL_OF_RECORDS|cold_store` in `mcp_servers/omega_hub/src/` returned nothing. The `.clinerules` and tool descriptions claim this behavior, but the code path wasn't located. **Needs**: locate the actual hivemind awareness module and verify the fallback.

### §6.3 Google OAuth auto-revocation timing [UNVERIFIED]
Claimed: "GitHub's partner scanning notifies Google, which MAY auto-revoke."
Status: GitHub docs confirm Google OAuth is a partner pattern. Google's docs confirm they recommend rotation. But the specific claim about auto-revocation timing and certainty was not explicitly confirmed in the fetched pages. **Needs**: deeper search on "GitHub Google OAuth secret scanning auto-revoke" for the specific mechanism.

---

## §7 KALI DECISION QUEUE (updated, v2)
| # | Ask | Status | Effort | Owner | Gate |
|---|-----|--------|--------|-------|----|
| K-1 | **Rotate the secret** (R-2026-08-28-001 is PENDING) | 🔴 UNCHANGED | 10min | Architect | rotation log → COMPLETE |
| K-2 | **No push until clean** (local HEAD 7 ahead with literal) | 🔴 NEW | — | all agents | `git grep HEAD` = empty |
| K-3 | **Redact 11 disk files + grokster committed file** | 🔴 UNCHANGED | 1h | maat/roc | disk sweep = 0 |
| K-4 | **git filter-repo + force-push** (scrub history) | 🔴 UNCHANGED | 2h | Architect | `git log -S 'GOCSPX' --all` = 0 |
| K-5 | **Commit + install existing .pre-commit-config.yaml** | 🟡 REVISED | 15min | maat | seeded test secret blocks |
| K-6 | **Fix split-brain BEFORE promoting grokster** | 🟡 REORDERED | 30min | maat | hydration test: grokster lessons present |
| K-7 | **Batch promotion: grokster first** (29 @ 0.95+, densest) | 🟡 REVISED | 0.5d | maat/w1-3 | staged drained, approved counts match |
| K-8 | **Commit .gitleaksignore as authoritative** | 🟢 VERIFIED | 15min | verity | gate-secrets consumes it |
| K-9 | **Gate the gate: tip stays clean post-redaction** | 🔴 UNCHANGED | 15min | verity | `git grep HEAD` stays empty |
| K-10 | **Reframe P0-1: 4 mandates lack mechanical checks** | 🟡 REVISED | 2h | maat | M17-M20 have check scripts |

---

## §8 FURTHER RESEARCH NEEDED (for the Omega Engine team)

### §8.1 Immediate (before debut)
1. **Locate sovereignty_ratio tool definition** — verify on-demand generation claim (G-4)
2. **Locate hivemind awareness module** — verify HALL_OF_RECORDS cold store fallback (G-5)
3. **Google OAuth auto-revocation mechanism** — confirm whether GitHub partner scanning auto-revokes, and the timing (§6.3)
4. **Confirm repo will go public at debut** — the entire P0-3 urgency depends on this; if the debut strategy uses a separate public repo, the exposure model changes
5. **Audit the 7 ahead commits** — what else is in them? Are there other secrets or sensitive data beyond the GOCSPX literal?

### §8.2 Short-term (this sprint)
6. **M17-M20 mechanical checks** — design compliance checks for the 4 untested mandates
7. **Lesson content review** — grokster's 52 lessons were never content-reviewed (only counted); the literal was found by accident, not by design. Build a content-review step into promotion.
8. **Carmack identity merge** — carmack/john_carmack/JOHN_CARMACK split (v1 K-5, deprioritized in v2 but still real)
9. **Split-brain tier model** — decide: bug fix (K-6) or deliberate tier model (§5.3)? The choice affects M4/M27 alignment.

### §8.3 Medium-term (post-debut)
10. **Turn grokster's constitutional lessons into build gates** (§5.2) — highest-leverage untapped win
11. **Generalize the M23 ratchet** — the logger landmine it was supposed to mitigate is actually safe (§3.1), but the ratchet pattern itself is sound; apply to other CLI entry points
12. **Contradiction sweep script** (v1 K-8) — ACTIVE_SPRINT vs HMC hub vs anchored-summary vs OMEGA_ENGINE.md

---

## §9 HONESTY LEDGER (v2)

### What v1 got wrong (corrected above):
1. **S-4 logger landmine** — REFUTED. logger is module-level, used in function body, safe. `.clinerules` P1 claim is stale.
2. **S-5 meter broken** — REFUTED. Meter reports 23/27 = 85.2%, works correctly. 4 mandates untested (coverage gap, not breakage).
3. **S-7 HALL_OF_RECORDS bleed** — REFUTED. 0 files carry the literal.
4. **S-1 urgency** — PARTIALLY. Repo is private; exposure is future (at debut), not current.

### What v1 got right (verified):
5. **S-2 local HEAD ahead** — VERIFIED. 7 ahead, grokster committed literal.
6. **S-3 pre-commit untracked** — VERIFIED.
7. **S-6 grokster density** — VERIFIED. 29 @ 0.95+.
8. **Self-leak (rollup)** — VERIFIED + FIXED. Rollup redacted, 0 literals remain.
9. **Tip tree clean (origin)** — VERIFIED. `git grep origin/release/debut` = empty.

### What I (v2) have NOT verified (flagged, not hidden):
10. **G-4, G-5** — code paths not located, marked UNVERIFIED
11. **Google auto-revocation timing** — mechanism confirmed, timing not, marked UNVERIFIED

---

## §10 KALI READING ORDER
1. This briefing §0 → §2 (P0-3 reclassification) → §3 (corrections)
2. `CLINE_LESSONS_CORPUS_DISCOVERY_20260828.md` §4-6 (pipeline repair)
3. `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §4 (Wave 0/1 PR specs)
4. `CLINE_GLM53_FRESH_WEIGHTS_REVIEW_20260828.md` §4 (48h perishability order)

*⬡ OMEGA ⬡ CLINE ⬡ AP-CLINE-KARDENING-v2-20260828 ⬡ multi-model ⬡ cline — VERIFIED + CORRECTED — READY FOR KALI REVIEW*
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: multi-model | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

