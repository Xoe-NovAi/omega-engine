# Cline Session Report — Handoff Execution + Install-Path Hardening + OOM RCA
**AP: AP-CLINE-SESSREP-20260822**
⬡ OMEGA ⬡ CLINE ⬡ opencode ⬡ install ⬡ PUBLIC-DEBUT-01 ⬡ 2026-08-22

**From**: cline/omega-engine (ox-alpha)
**To**: kali (orchestration authority)
**Scope**: Full record of this chat session — handoff execution, security
remediation, dependency fixes, the OOM incident and its root cause, new
tooling, and exact repo state left behind.
**Companion doc**: `docs/research/R_CLINE_CATCHUP_REVIEW_FOR_KALI_20260822.md`
(the earlier independent review; this report is the *execution* record).

---

## 1. Executive Summary

Executed handoff `data/handoff/pending/CLINE_DISPATCH_20260822.md` plus four
significant findings that emerged during execution:

1. **Torch was entering the install path** via `headroom-ai[all]` (ml extra).
   Fixed: plain `headroom-ai` base dep, verified torch-free from PyPI metadata.
   Repo policy confirmed: **CPU-only, torch-free, non-negotiable.**
2. **Native-build OOM root-caused**: llama-cpp-python's build backend
   (scikit-build-core) ignores `CMAKE_BUILD_PARALLEL_JOBS`/`MAKEFLAGS`; the
   only honored knob is **`CMAKE_BUILD_PARALLEL_LEVEL`** (verified against
   skbuild-core 1.0.3 source). Unpinned = ~13GiB RSS + ~1.88GiB zRAM overflow.
3. **New P8 observability tool**: `scripts/observe-build.sh` — per-second
   metrics with top-PID RAM attribution + automatic postmortem.
4. **Gitleaks full-history scan triaged**: 106 findings → real credentials
   redacted from 14 live files (21 replacements); false-positive classes
   documented; history rewrite still pending (needs your ruling).

Nothing has been committed. All work sits in the working tree, enumerated in §9.

---

## 2. Dispatch Execution Status

| Dispatch item | Status | Evidence |
|---------------|--------|----------|
| B2 secret-artifact quarantine (.gitignore + untrack) | ✅ done | `.gitignore` additions; `git rm --cached github-mcp-server` |
| B4/C2 README honesty (test counts, phantom targets) | ✅ done | README.md edits |
| Version split fix (`__version__` vs pyproject) | ✅ done | pyproject 1.2.0 aligned |
| B5 delete eval() router | ✅ done | `src/omega/routing/table.py` removed; no importers found |
| C1 warp dep quarantine | ✅ done | moved to optional `warp` extra (pyproject:80) |
| Gitleaks full-history scan | ✅ run | `/tmp/opencode/gitleaks-full.json` (160KB) |
| History rewrite (filter-repo) | ⏸ blocked on your ruling | dry-run artifacts in `.git/filter-repo/` were inspected; NOT executed |
| Fresh-venv install gate | ✅ done ×2 runs | see §5 |
| m23_gate re-check | ⏳ pending | staged post-commit step |

---

## 3. Security Remediation (gitleaks)

**Scan**: `gitleaks detect --source . --report-format json --report-path
/tmp/opencode/gitleaks-full.json` — full history. **106 findings, 40 unique
secrets.**

### 3.1 Real credentials REDACTED in live files (21 replacements, 14 files)
Replacements are literal `[REDACTED-GITLEAKS-<RULE>]` strings; driven
programmatically off the gitleaks JSON (full secret values, nothing hardcoded
by me). Files touched:

- `.firecrawl/claude_codebases.json`, `.firecrawl/claude_instructions.json`
  (Firecrawl keys — also candidates for untracking entirely)
- `data/coordination/KALI_CLINE_SYNC_REPORT_20260817.md` (GCP AIza key)
- `data/coordination/archive/.../P1_EXA_401_DIAG_AND_KEY_VAULT_ARCH_20260623.md`
  (2× Exa API keys, confirmed working via curl at the time)
- `data/entities/researcher/workspace/ANTIGRAVITY_SYSTEM_DEEP_DIVE.md` (Google OAuth client secret G0CPX-…)
- `data/entities/researcher/workspace/KNOWLEDGE_GAP_CLOSURE_20260619.md` (Firecrawl fc-<REDACTED> + Exa key)
- `data/entities/roc_racoon/workspace/mining_reports/{CARMACK_SEARXNG_REVIEW,MCP_SERVER_HARDENING_AUDIT,SEARXNG_HANDOFF_TO_KALI,SEARXNG_JEM_VERIFICATION}_*.md` (Brave v1-q…, Exa UUID, Tavily tvly-<REDACTED>, SearXNG secrets)
- `data/handoff/archive/sessions/research_process_sucks_balls_2_session-ses_149a.md` (3×)
- `data/reviews/roc_racoon_deep_tiered_followup.md` (fc-<REDACTED> key), `data/reviews/roc_racoon_web_research_followup.md` (G0CPX-…)
- `docs/archive/stale/history/2 session-ses_1748.md` (JWT session token)

### 3.2 Classified FALSE POSITIVES (left untouched)
- All `AP-*` project tokens (AP-INSTALL-v1.0.0 etc.) — internal provenance tags
- Test fixtures: `sk-<REDACTED>…`, `sk-<REDACTED>…`, `sk-local-<REDACTED>*`, `explicit_key_1`, `qwen3-0.6b-q6_…`
- `PHASE1A_GOOGLE_API_FREE_TIER_ROTATION` "private key" — template with `...` placeholders
- `data/searxng/config/settings.yml` — already redacted (B1 prior work)

### 3.3 HISTORY-ONLY findings (require rewrite or acceptance)
- 2× GCP API keys inside `server_20260605.heapsnapshot` (deleted file, live in history)
- Exa/firecrawl keys in older revisions of now-clean files
- `context_packs/sovereign-audit/*.md` AP-tokens (benign)

### 3.4 OPEN SECURITY ITEMS (need your action)
1. **Key rotation is mandatory regardless of rewrite**: every redacted secret
   lived on a PUBLIC remote (github.com/Xoe-NovAi). Treat all as burned:
   G0CPX OAuth secret, Firecrawl ×(≥3), Exa ×(≥4), Brave, Tavily, GCP AIza.
2. **History rewrite decision**: `git filter-repo` dry-run was inspected only.
   Options: (a) full filter-repo + force-push (breaks fleet clones),
   (b) accept + rotate-only, (c) fresh orphan branch for debut. Your call.
3. Consider untracking `.firecrawl/` wholesale (tool state dir, no repo value).

---

## 4. Install-Path Fixes (debut blockers)

### 4.1 Torch quarantine (found during execution, not in dispatch)
- `pyproject.toml:12`: `headroom-ai[all]` → `headroom-ai`
- The `[all]` extra chains to the `ml` extra → torch (~527MB download,
  ~2GB installed). Base deps verified torch-free via PyPI metadata:
  tiktoken, pydantic, litellm, click, rich, opentelemetry-api, ast-grep-cli,
  pyyaml, tomli/tomlkit.
- **Verified empirically**: fresh venv install of `.[native,cli]` completed
  with ZERO torch packages (site-packages grep = 0; pip resolve log clean).

### 4.2 Other pyproject changes
- `warp-proxy-pool` moved from base deps to optional `warp` extra (line 80)
- Version aligned to `1.2.0` across pyproject + `src/omega/__init__.py`

### 4.3 Fresh-venv gate results
- venv: `/tmp/opencode/test-install-venv` (python 3.13)
- `pip install -e '.[native,cli]'` → **Successfully installed** (full list in
  `/tmp/opencode/install-test2.log`); includes llama-cpp-python 0.3.35
- `import omega` → OK, version 1.2.0

---

## 5. Code Fix: vault CLI import block (new debut blocker, found by smoke test)

`src/omega/cli/vault.py` imported `ProviderName/CredentialType/CredentialTier/
VaultCredential` from `vault_core` — they live in `vault/models.py`. It also
used a broken `from src.omega...` absolute path and referenced non-existent
`VaultCoreError` (real name: `VaultError`).

**Fix applied** (lines 27–34):
```python
from omega.vault.vault_core import VaultCore
from omega.vault.models import (
    ProviderName, CredentialType, CredentialTier, VaultCredential,
)
from omega.vault.vault_core import VaultError as VaultCoreError
```
⏳ **Not yet re-verified post-edit** — run:
`.venv/bin/python -c 'import omega.cli.vault'` before commit.

---

## 6. OOM Incident — Root Cause Analysis

### 6.1 Timeline
1. Fresh install test → llama-cpp-python sdist build defaulted to **16 jobs**
   (all threads on the 5700U) → machine OOM'd; user reported massive RAM use.
2. First pin attempt (`CMAKE_BUILD_PARALLEL_JOBS=6`, `MAKEFLAGS=-j6`) FAILED —
   measured peak still ~13GiB (sampler: `/tmp/opencode/build6-mem.log`).
3. Source-level investigation: scikit-build-core **1.0.3**, downloaded and
   grepped. `builder/builder.py:488` calls `cmake --build` with empty
   `build_args` — no `-j` ever passed. CMake's documented fallback env var is
   **`CMAKE_BUILD_PARALLEL_LEVEL`** (since CMake 3.12). Our vars were dead.
4. Corrected knob tested at 6 jobs — user observed via btop: peak stayed well
   under 10GiB total WITH cline + opencode IDEs (~1GiB each) resident.

### 6.2 True cost of the unpinned build (per user's zRAM data — RECORD)
- ~13GiB RSS peak **plus ~1.88GiB pushed into zRAM swap before OOM**
- The 1.88GiB is the *compressed* zRAM size → true overflow demand est.
  4–6GiB uncompressed (typical anon-page ratios) → **effective demand
  ~17–19GiB on a 14GiB box**. Worse than RSS numbers alone suggest.
- Residual ~1.8GiB zRAM usage persisted post-incident (reclaimable via
  `swapoff -a && swapon -a` when convenient).

### 6.3 Final decision
- `scripts/install.sh` exports `CMAKE_BUILD_PARALLEL_LEVEL=8` default
  (= physical cores; 10 rejected — SMT gains are marginal for C++ compiles
  while RAM scales linearly per concurrent TU). Env-overridable.
- Full evidence trail in comments in install.sh + OPS NOTE in
  `data/coordination/HMC_COLLABORATION_HUB.md`.
- No dedicated 8-job retest run (per Kali/user ruling); next natural rebuild
  exercises it under the observer.

---

## 7. New Tooling: scripts/observe-build.sh (P8 Observability)

```
scripts/observe-build.sh <run-name> <command> [args...]
```
- Artifacts → `/tmp/opencode/obs/<run-name>/`
- `metrics.csv`: 1-second cadence — timestamp, mem used/avail MB, load1,
  top-PID attribution (pid, comm, RSS MB). Answers "WHAT ate the RAM", not
  just "how much".
- `console.log`: full command output (pass `pip -v` to expose cmake/ninja
  invocation lines).
- `summary.txt`: auto-postmortem on exit — duration, exit code, peak RAM,
  offender-at-peak, top-5 PIDs by peak RSS, console tail.
- Smoke-tested ✅ (correctly attributed baseline RAM to the cline process).
- Policy: REQUIRED for any native/long build on this box going forward.

---

## 8. Process Gotchas Discovered (for fleet-wide awareness)

1. **`pip download` for sdists triggers a FULL wheel build** just to extract
   metadata (PEP 517 hook fallback) → compiles the package twice if you then
   install from source. Fetch sdists with `curl` from files.pythonhosted.org
   instead; install from the local file path (always rebuilds fresh, zero
   network, other wheels unaffected).
2. **`--no-cache-dir` disables the HTTP cache too** — it was why every retry
   re-downloaded all wheels. Only use it when cache poisoning is suspected.
3. **Watcher self-match trap**: `pgrep -f "<pattern>"` inside a watcher whose
   own cmdline contains the pattern loops forever. Use marker files, or exclude
   own PID. (Cost us one silent hang.)
4. **pip hides backend output**: without `-v` you cannot see whether your env
   knobs reached ninja/cmake. Always observe builds verbosely once.

---

## 9. Exact Repo State Left Behind (nothing committed)

### 9.1 Modified by this session
| File | Change |
|------|--------|
| `.gitignore` | secret-artifact + binary exclusions |
| `pyproject.toml` | torch-free base dep; warp → extra; version 1.2.0 |
| `README.md` | test-count honesty, phantom-target removal |
| `scripts/install.sh` | CMAKE_BUILD_PARALLEL_LEVEL=8 RAM guard w/ evidence comments |
| `scripts/observe-build.sh` | NEW (untracked) — observability harness |
| `src/omega/__init__.py` | version alignment |
| `src/omega/cli/vault.py` | import-block fix (§5) — needs re-verify |
| 14 data/docs files | gitleaks `[REDACTED-GITLEAKS-*]` substitutions (§3.1) |
| `data/coordination/HMC_COLLABORATION_HUB.md` | OPS NOTE (RAM guard + observability) |
| `github-mcp-server` | staged deletion from index (23MB binary) |

### 9.2 Pre-existing modifications NOT mine (untouched by me)
`OMEGA_CODEX.md`, `data/entities/default/workspace/birth_records.md`,
`data/entities/john_carmack/proposed_lessons.yaml`,
`data/entities/test_promo_entity/.../sca.json`,
`data/entities/test_sovereign_entity/.../sca.json`,
`.opencode/.last_session.json` — were dirty before dispatch execution began.
Recommend committing separately or stashing to keep my commit set clean.

### 9.3 Pending work queue (in suggested order)
1. Verify vault import fix: `python -c 'import omega.cli.vault'`
2. `make lint` + focused tests on touched modules
3. Commit hygiene set (suggest: `fix: torch-free deps, install RAM guard,
   vault CLI imports, secret redaction, build observability`)
4. **Kali ruling needed**: history rewrite (filter-repo vs rotate-only vs orphan)
5. **Rotate ALL burned keys** (§3.4.1) — independent of rewrite decision
6. m23_gate + gitleaks rescan post-commit
7. Consider untracking `.firecrawl/` wholesale

---

## 10. Coordination Record

- Hivemind sessions posted: `ses_0791d5ce9c68` (torch-free fix),
  `ses_248d63c7e135` (RAM guard decisions)
- HMC hub updated with OPS NOTE (see §6.3)
- All measurements preserved under `/tmp/opencode/` (gitleaks-full.json,
  build6-mem.log, install-test2.log, obs/ harness outputs)

---

## 11. ADDENDUM — P0-1b Residual Verification (Kali intel ses_3c27f0d128dd)

Kali paged urgent intel: commit `0c40b108` allegedly carries
`SECURITY_AUDIT_2026_05_19.md` with 3 real-format `c-sk-` keys reachable from
HEAD. **Verified against this repo — findings:**

| Check | Result |
|-------|--------|
| Commit `0c40b108` exists | ❌ NOT FOUND locally; not reachable from HEAD |
| `SECURITY_AUDIT_2026_05_19.md` in HEAD tree | ❌ absent |
| File in gitleaks 106-finding report | ❌ zero hits |
| Real-format gate: `git log -G 'c-sk-[A-Za-z0-9]{20,}' --all` | ✅ **EMPTY — clean** |
| Prose gate: `git log -S 'c-sk-' --all` | 5 hits — ALL prose/doc references; per-commit diff inspection found NO long key material (consistent w/ KALI_CLINE_SYNC_REPORT_20260817.md:30 "6 false positives only") |
| G0CPX gate | ⏳ expected-dirty until B1 lands: HEAD still carries G0CPX in `data/entities/researcher/workspace/ANTIGRAVITY_SYSTEM_DEEP_DIVE.md` + `data/reviews/roc_racoon_web_research_followup.md` (my redactions are uncommitted WT changes) |

**Assessment**: the `0c40b108` residual most likely refers to Kali's pre-gc
clone state; this repo's copy was already destroyed (documented
`git gc --prune=now` in the 20260817 sync report). No action needed beyond
the already-planned B1 rewrite. Post-filter-repo, run BOTH of Kali's gates
(`git log -S 'c-sk-' --all`, `git log -S 'G0CPX' --all`) — must be empty
before push.

### ⚠️ RESOLUTION — Self-inflicted Gate Trap (Kali ruling ses_3c41deff0f52, accepted)
Research reports discussing these incidents contained literal secret-format strings
(`G0CPX-…`, `c-sk-…`, `fc-<REDACTED>`, `tvly-<REDACTED>`). Per kali's ruling:
**sanitize-literals option adopted**, path-allowlist **rejected** (rots →
false-negative blind spots). All secret-format tokens in this report have been
masked to `PREFIX-<REDACTED>` and bare prefixes mangled (`G0CPX`, `c-sk`) so they
can no longer trip `-G` format-regex gates. The committed catchup review `3e2a2c51`
was re-scanned and is **already clean** — no follow-up sanitize commit required.
PRIMARY gate going forward (prose-safe by construction):

```bash
for R in 'G0CPX-[A-Za-z0-9]{12,}' 'c-sk-[A-Za-z0-9]{12,}' 'fc-[a-f0-9]{20,}' 'AIzaSy[A-Za-z0-9_-]{20,}'; do
  printf -- '-G %s: ' "$R"; git log -G "$R" --all --oneline | wc -l
done
```

*⬡ OMEGA ⬡ CLINE ⬡ omega-engine ⬡ session-report ⬡ 2026-08-22*

### 12. Build-Validation Closure (6-thread run, 2026-08-22)
Empirical confirmation via btop (Kali, 6 threads): peak stayed **well under
10GiB total** with cline + opencode IDEs resident — validates the RAM-guard
direction. A second *instrumented* 6-thread run through `observe-build.sh`
could not be captured (wedge, see §13). `install.sh` default therefore settled
at **8 jobs** (5710U has 8 P-cores; 8 is the RAM-safe sweet spot; override via
`CMAKE_BUILD_PARALLEL_LEVEL` env; SMT siblings add marginal gain vs RAM cost).

### 13. Known Wedge (do not re-trigger blindly)
`pip download --no-binary :all:` for llama-cpp-python is **not** a cheap
metadata fetch — scikit-build-core runs a full CMake configure *inside* metadata
extraction (PEP 517 fallback), which is why a detached chain wedged for 52+ min
(PID 997626 still in Ss). Safe workaround for any future rebuild: fetch the
sdist once via `curl` from files.pythonhosted.org, then
`pip install -v --no-deps --force-reinstall <local-tar.gz>` — no metadata dance,
no dependency re-resolution. This is the documented efficient loop in §8.
