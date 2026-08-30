<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Open Decisions for Kali — Build Observability, Security Sequencing, Platform
**AP: AP-DECISIONS-KALI-20260822**
⬡ OMEGA ⬡ CLINE ⬡ kali ⬡ consultation ⬡ PUBLIC-DEBUT-01 ⬡ 2026-08-22

**From**: cline/omega-engine · **Consultation requested by**: user (Architect)
**STATUS (updated 2026-08-22 during execution of packet ho_9a9d34eac9c8)**:
| Item | Ruling | Execution |
|---|---|---|
| D-K1 | ADOPTED(a): filter-repo replace-text + whole-file purges + force-push | IN PROGRESS |
| D-K2 | AMENDED by Architect: NO rotation (private repo; old keys already rotated) | CLOSED — no action |
| D-K3 | ADOPTED(a): hygiene commits now | ✅ commits 511682f0 + 2 more |
| D-K4 | ADOPTED: fleet-guide graduation now; Mandate deferred post-debut | ✅ guide v1.0.1 ratified |
| D-K5 | ADOPTED: cline owns post-zswap instrumented re-baseline | TICKETED (post-switch) |
| D-K6 | ADOPTED: `make gate-secrets` target | ✅ codified |
| D-K7 | ADOPTED(b): disk-backed caches >500MB | ✅ OMEGA_SDIST_CACHE default ~/.cache |

---

**Context**: follow-up to `R_CLINE_SESSION_REPORT_FOR_KALI_20260822.md`.
Items already closed by your rulings (sanitize-literals adopted; allowlist
rejected; P0-1b refutation accepted) are NOT repeated here.

---

## D-K1 · B1 history-rewrite strategy  〔PRIORITY: HIGH · blocks push〕
The gitleaks full-history scan found real credentials that remain in git
history even though live files are redacted (working tree). Three options:
- (a) `git filter-repo` full purge + force-push — cleanest history, breaks
  every fleet clone (opencode nodes must re-clone or `git pull --rebase` fails)
- (b) rotate-only: accept dirty history, revoke everything, rely on rotation
- (c) fresh orphan branch for public debut (clean slate, archive old branch)
**Needed from you**: pick one + authorize execution window + coordinate fleet
clone refresh if (a).

## D-K2 · Key-rotation schedule  〔PRIORITY: HIGH · independent of D-K1〕
All of these appeared on a PUBLIC remote and must be treated as burned
regardless of rewrite decision: GOCSPX OAuth client secret, Firecrawl keys
(≥3), Exa keys (≥4), Brave API key, Tavily key, GCP AIza key. Full list with
file provenance: session report §3.1 + evidence_20260822/gitleaks-full.json.
**Needed from you**: who rotates, target date, and whether rotation lands
before or after debut.

## D-K3 · Hygiene-commit sequencing  〔PRIORITY: MED〕
24 modified files sit uncommitted: torch-free pyproject, install.sh RAM guard,
vault CLI import fix, secret redactions (14 files), HMC OPS NOTE + 2 new
scripts/docs. Options: (a) commit hygiene set now as its own commit, B1
rewrite follows later; (b) hold everything and land redactions only inside
the filter-repo pass. My recommendation: (a) — working-tree redactions should
be durable ASAP; history scrub is orthogonal. **Needed**: your call + any
commit-message conventions beyond standard prefixes.

## D-K4 · Ratify build-observability policy  〔PRIORITY: MED〕
Shipped this session (repo-level code + UX):
- `scripts/observe-build.sh` v1.1 — telemetry, top-PID attribution, STALL
  tripwire (log frozen ≥5 min → marker file), optional hard timeout,
  auto-postmortem. Smoke-tested.
- `scripts/fetch-sdist.sh` v1.0 — wedge-proof sdist fetch+install loop
  (curl once → local tarball install). Solves both the pip-download double-
  compile trap and the 52-min metadata wedge.
- `make observe CMD=...` / `make install-guarded`
- Guide: `docs/guides/BUILD_OBSERVABILITY.md` (the rule: ANY native/long build
  under the observer; sdists ONLY via fetch-sdist.sh)
**Needed from you**: ratify as fleet-wide policy (and whether it graduates to
a Sovereign Mandate amendment or stays guide-level).

## D-K5 · zswap transition (ZS-1) coordination  〔PRIORITY: MED · upcoming〕
You're moving zRAM → zswap (per ho_91999b286910: max_pool_percent=25,
lzo_rle, zsmalloc). Implications for my lane:
- The measured peak figures in install.sh comments cite *zRAM-era* overflow;
  after transition, OOM dynamics change (compressed pool capped at ~25% RAM,
  overflow goes to NVMe swap). Recommend a fresh instrumented validation run
  (`make install-guarded`) post-switch to re-baseline the 8-job default.
- btop Total-RAM swing (14→15GiB) was a boot-time CMA reservation difference,
  not zRAM; expect similar variance after the zswap reboot.
**Needed from you**: timing, and whether cline should own the post-switch
validation build.

## D-K6 · Gate-convention codification  〔PRIORITY: LOW〕
Your ruling (-G format-regex PRIMARY, -S advisory) is documented in the guide
(§4) but currently lives only in prose. Should it graduate into `.githooks/`
pre-commit enforcement or a `make gate-secrets` target so it executes rather
than relies on memory?

## D-K7 · tmpfs exposure policy  〔PRIORITY: LOW〕
`/tmp` is RAM-backed here; today's cleanup reclaimed 2.58GB of build debris
that was silently costing RAM. Options: (a) keep tmpfs + enforce cleanup via
observer postmortem hook; (b) point heavy build caches at disk-backed paths
(`OMEGA_SDIST_CACHE`, `TMPDIR`). Recommendation: (b) for anything >500MB.
**Needed**: ratify default cache locations.

---

## Already executed this session (no decision needed)
- RAM cleanup: evidence preserved to `docs/research/evidence_20260822/`,
  then /tmp build debris purged → **+2.58GB MemAvailable reclaimed**
- Session report sanitized per your ruling (gate-verified: 0 format literals)
- Catchup review `3e2a2c51` verified already clean — no sanitize commit needed
- Wedged PID 997626 gone (self-resolved before reaping required)

*⬡ OMEGA ⬡ CLINE ⬡ omega-engine ⬡ decisions ⬡ awaiting-kali ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: kali | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
