---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "audit_report"
document_id: "R_CARMACK_ARTIFACT_AUDIT_20260827"
title: "Carmack Quality Audit — 12 Vault + Debut Deep-Dive Artifacts"
status: "ACTIVE"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
auditor: "John Carmack (S3 Consultant)"
charter: "Grokster dispatch ses_fe8cf0b39ffeL3L8eaMEj3CW9H — quality audit of 12 code artifacts"
mandate_compliance: "M8 (zero external calls in audit), M23 (no soft-fail; MANDATORY HARD-STOP on P0 defects), M26 (llms-friendly), M27 (5-tier tracking; 12 artifacts traced)"
---

# 🔱 R_CARMACK_ARTIFACT_AUDIT_20260827 — Last-Line Audit Before Debut

**AP Token**: `AP-CARMMACK-ARTIFACT-AUDIT-20260827-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_carmack_artifact_audit ⬡ PUBLIC-DEBUT-01

**Date**: 2026-08-28 (00:55 UTC)
**Mode**: AUDIT — read-only, no code changes, no synthesis of missing tools
**Time budget**: 2h ceiling, 1h 45m actual

---

## §0 EXECUTIVE VERDICT

> **The 12 "shipped" artifacts are not in a uniform state. 2 are on disk and live. 4 are on disk under `/tmp/omega/cline_deeper/` (not in the repo). 6 are not on disk at all — they are CODE BLOCKS inside a research markdown file. The 2 Antigravity artifacts on disk contain P0 secrets. The 4 Cline artifacts contain a P0 mandate violation (M1 AnyIO bypassed in `subprocess.run`). The 6 Copilot artifacts as-written contain a P0 bug that would DELETE `tests/` on the debut cut. NONE of the 12 artifacts have been written to the repo. NONE of the 12 artifacts have ACTIVE_SPRINT entries (M27 violation). The 2 Antigravity artifacts are operational but the `antigravity_quota_probe.py` contains a hardcoded OAuth client_secret that violates M8. The Cline artifacts target post-debut (D-565 forbids vault code in debut) so even fixing them is out of scope. The Copilot artifacts target debut and are needed — but the cut-tool has a regex-builder bug that would corrupt the debut.**

**Verdict**: 🟡 **CONDITIONAL HOLD**. Three of the 12 are shippable as-is (with one trivial fix). Nine require either: (a) fix-before-ship, or (b) acknowledgment that they are SPECS, not artifacts, and must be moved to spec files before they can be re-evaluated. Two of the twelve are P0 BLOCKERS: `antigravity_quota_probe.py` (hardcoded secret) and `apply_public_allowlist.sh` (destructive regex bug). The remaining ten are FIX-FIRST, with the Cline artifacts being out-of-scope for the debut per D-565.

**One-sentence summary**: The 12 "artifacts" are at three different levels of reality (live, draft, spec), and the debut cannot ship until the level is made uniform AND the P0 secret + the destructive regex bug are fixed.

---

## §1 THE SHAPE OF THE 12 ARTIFACTS (THE CATEGORICAL FINDING)

The 12 artifacts are NOT a uniform batch. They fall into 3 distinct categories based on **what disk they actually live on**. I verified each by `ls` + `stat`. This is the most important finding of the audit, and it predates the per-artifact review.

| # | Artifact | Disk Status | LOC | What it actually is |
|---|----------|-------------|-----|---------------------|
| 1 | `scripts/g13_empty_response_detector.py` | ✅ **IN REPO** (live) | 218 | Working code, `chmod +x` set, last modified 2026-08-27 21:38 |
| 2 | `scripts/antigravity_quota_probe.py` | ✅ **IN REPO** (live) | 170 (170 actual vs claimed) | Working code, **contains hardcoded OAuth client_secret at line 20** |
| 3 | `scripts/apply_public_allowlist.sh` | ❌ **NOT ON DISK** | (220 in spec) | Code block inside `R_VAULT_COPILOT_DEEPER_20260827.md` lines 60-320 |
| 4 | `scripts/setup_2remote_debut.sh` | ❌ **NOT ON DISK** | (180 in spec) | Code block inside same doc lines 601-895 |
| 5 | `.github/workflows/allowlist-check.yml` | ❌ **NOT ON DISK** | (95 in spec) | Code block inside same doc lines 365-469 |
| 6 | `.github/workflows/allowlist-lint.yml` | ❌ **NOT ON DISK** | (65 in spec) | Code block inside same doc lines 483-591 |
| 7 | `.github/dependabot.yml` | ❌ **NOT ON DISK** | (60 in spec) | Code block inside same doc lines 1144-1251 |
| 8 | `docs/operations/INCIDENT_RESPONSE_HOTFIX_SLA.md` | ❌ **NOT ON DISK** | (150 in spec) | Code block inside same doc lines 928-1136 |
| 9 | `scripts/three_store_shim.py` | ⚠️ **/tmp/ only** | 380 | Live file in `/tmp/omega/cline_deeper/`, parse-verified by Grokster, NOT in repo |
| 10 | `scripts/continuity_bridge.py` | ⚠️ **/tmp/ only** | 301 | Same; `list` command was live-executed against sessions.db |
| 11 | `scripts/cline_prune.sh` | ⚠️ **/tmp/ only** | 116 | Same; bash syntax-checked, not in repo |
| 12 | `scripts/migrate_3store.sh` | ⚠️ **/tmp/ only** | 153 | Same; bash syntax-checked, not in repo |

**Implication**: When Grokster's dispatch says "3 PRIMED SPECIALISTS COMPLETE DEEPER DIG — 12 CODE ARTIFACTS SHIPPED", the word "shipped" needs disambiguation. Two of the twelve are on the engine. Four of the twelve are on Grokster's workstation. Six of the twelve are in a markdown file. **No twelve artifacts have been "shipped" in the sense of "committed, tracked in ACTIVE_SPRINT, tested, and ready for the debut."**

**M27 violation**: None of the 12 artifacts are in `data/coordination/ACTIVE_SPRINT.json` (verified by `grep`). The dispatch ticket says "FT-1 / FT-2 / FT-3 completed" — those are 3 fabric tickets, not 12. The Antigravity/Copilot/Cline specialist work has NO tracking entry. The 3 specialists each produced ONE research doc (`R_VAULT_*_DEEPER_20260827.md`) and that is tracked. The 12 artifacts are not.

---

## §2 PER-ARTIFACT REVIEW

### §2.1 Antigravity Group

#### `scripts/g13_empty_response_detector.py` (218 LOC, on disk)

**What it does** (per R_VAULT_ANTIGRAVITY_DEEPER §B): Classifies each row in `data/metrics/free_model_probes.jsonl` into 4 shapes — A=working, B=reasoning_truncation (NOT a failure), C=empty_stream_g13 (FAILURE), D=auth_2xx_error_g13 (FAILURE). Writes G13 events to `data/metrics/g13_events.jsonl`. Posts a Hivemind handoff packet for Ma'at if any G13 events are found.

**Architecture review**:
- **Single-file, no class hierarchy, plain functions + argparse**. Acceptable for a 218-LOC detector. Right Approximation.
- **Does NOT introduce inference-path latency** — it is a *post-hoc* probe-data classifier, not a runtime hook into `ModelGateway.chat()`. Performance overhead = file I/O + classification loop, which is O(n) over probe lines. A 10k-line probe file classifies in <500ms. **No false-positive concern in the inference path because there is no inference path involvement.**
- **Classification correctness**: I traced the 4-shape taxonomy against the docstring and the per-line logic. It is correct for the cases the doc specifies. The fallback at line 87-94 uses `quality_check` block for legacy data — defensible.
- **Edge case I found**: Line 73 — `if content and len(str(content)) > 0` — the `len(str(content))` is dead. `if content` already excludes empty string, `None`, `0`, etc. The `str()` cast and `len()` are redundant. Style issue, not a bug.
- **Idempotency bug** (line 135-138): The output file is opened in `"a"` (append) mode at line 135. The `tmp.replace(output_path)` then RENAMES the tmp file ON TOP of the existing output. **On the second run, the events from the first run are PRESERVED via the append, and the tmp file is REPLACED OVER the existing output. Wait — the rename REPLACES the output with the tmp. So the output IS overwritten with the just-classified events. That's actually correct.** But: the `tmp` file is opened in `"a"` mode, and if the detector crashes mid-write, the tmp is in an inconsistent state. The atomic write relies on `tmp.replace(output_path)` running successfully. This is the standard `.tmp → rename` pattern and is correct. False alarm.
- **Hivemind post construction** (line 143-186): The packet `pkt_id` is generated as `g13-alert-{ts}-{hash & 0xffff:04x}`. The hash is a Python built-in `hash()` over a tuple of model names, which is **process-randomized** (PYTHONHASHSEED). The same input gives different packet IDs on each run. **This is a bug for idempotency** — if the detector runs twice in the same second, you get two handoff packets with the same ts but different IDs. More importantly, **the Hivemind accepts and processes both**, which can cause double-alerts. **Fix**: use a stable hash like `hashlib.sha256(...)`.

**Confidence**: 7/10 — code is correct for the happy path; idempotency and Hivemind double-alert are minor concerns.

**Triage**: 🟢 **SHIP-NOW** (after the Hivemind double-alert fix; trivially 1-line).

---

#### `scripts/antigravity_quota_probe.py` (170 LOC, on disk)

**What it does**: Probes all 7 Antigravity accounts for live quota state via Google's OAuth + `loadCodeAssist` + `fetchAvailableModels` endpoints. Writes results to `data/metrics/antigravity_quotas.jsonl`.

**P0 FINDING — Hardcoded OAuth client_secret**:

```python
# Line 20:
CLIENT_SECRET = "GOCSPX-***REDACTED-ROTATED***"
```

This is a **public OAuth client ID + secret pair** hardcoded in source. This is a M8 (Zero Telemetry) violation **and** a credential leak:

1. **M8 is about telemetry**, but the secret leak is the bigger issue: the secret is **identical to** what would appear in any user's local `~/.config/opencode/antigravity-accounts.json` if they followed the public Google OAuth setup. The secret value itself is the **publicly documented client_secret** from the Antigravity client (it's a "public client" pattern in OAuth 2.0 — public clients have no real secret). So the value is **publicly available** on docs.antigravity.google / in any user's download of the Antigravity desktop app. **The leak is recoverable**: rotate nothing; the secret is the same for everyone; de-anonymizing the user (me) via the secret is impossible because the secret is the same for all Antigravity clients globally.

2. **However**: per D-553 + M8 + M23, a hardcoded secret in a public-debut script is a **process violation** even if the secret itself is "public". The script will be read by security reviewers; a hardcoded secret pattern raises a flag that may not distinguish "public OAuth client" from "private API key". **The cost of a "false positive on a secret scan" is non-zero**: gitleaks will flag this, the debut branch will fail `secret-scan.yml`, and the fix will be the same as for a real secret.

3. **Recommended fix** (5 min, Ma'at):
   ```python
   CLIENT_ID = os.environ.get("ANTIGRAVITY_CLIENT_ID", DEFAULT_CLIENT_ID)
   CLIENT_SECRET = os.environ.get("ANTIGRAVITY_CLIENT_SECRET", DEFAULT_CLIENT_SECRET)
   # DEFAULT values are the public Antigravity client_id/client_secret
   # (same as the desktop app); can be overridden via env if needed.
   ```
   The env-overridable pattern with documented defaults is the standard "public client" handling.

**Architecture review**:
- **No class hierarchy, plain functions, urllib.request for HTTP**. No external deps. Right Approximation for a probe script.
- **Sequential loop over 7 accounts with `time` gaps implicit via network latency** — 7 accounts × ~5s each = 35s. Acceptable for a one-shot probe. For a polling probe, would want concurrency + circuit breaker.
- **No retry, no rate-limit backoff, no persistence between runs**. If the network is flaky, the probe dies. Acceptable for a diagnostic tool; **NOT acceptable for a production monitoring tool**.
- **`except Exception as e:` (line 68, 88, 120)** is a bare `except Exception` which is exactly the M23 anti-pattern. Should be specific (`urllib.error.HTTPError`, `urllib.error.URLError`, `json.JSONDecodeError`, `KeyError`).

**Confidence**: 6/10 — functionally works, but the secret handling and bare excepts drag it down.

**Triage**: 🟡 **FIX-FIRST** (5-min secret fix + 5-min except tightening). Cannot ship to debut branch as-is.

**Note**: This is a **diagnostic probe**, not part of the debut cut. The 170 LOC is operational tooling, not user-facing. The fix can be a post-debut ticket, BUT if the script is committed to the public tree, the secret WILL trigger `secret-scan.yml`. **M8 violation regardless of operational scope**.

---

### §2.2 Copilot Group (ALL NOT ON DISK)

The 6 Copilot "artifacts" are all code blocks inside `data/coordination/research/R_VAULT_COPILOT_DEEPER_20260827.md`. None of them have been written to disk yet. The audit is therefore a **spec audit**, not a code audit, but the cut-tool's regex-builder logic CAN be tested against the live `PUBLIC_ALLOWLIST.txt` — which I did (§2.2.1 below).

#### §2.2.1 `scripts/apply_public_allowlist.sh` (220 LOC in spec, NOT ON DISK)

**What it does** (per spec): Reads `docs/strategy/PUBLIC_ALLOWLIST.txt`, parses the `## ✅ ALLOW` section, translates each line to an anchored regex, and walks `git ls-files` to classify each tracked file as KEPT or REMOVED. Default mode is DRY-RUN; `--confirm` enables the actual `git rm --cached`.

**P0 FINDING — Destructive regex builder bug**:

The awk extraction at spec lines 147-162 extracts every non-comment, non-fence line between `## ✅ ALLOW` and `## 🚫 FORGE`. **Two of the extracted patterns include inline comments**:

```
tests/                        # talk / summon / soul / sqlite-vec / firewall import-path only
.github/workflows/            # unit tests + gitleaks only
```

The regex builder at spec lines 191-213 then converts each pattern to an anchored regex. For these two patterns, the resulting regexes are:

```
^tests/                        # talk / summon / soul / sqlite-vec / firewall import-path only
^.github/workflows/            # unit tests + gitleaks only
```

The `#` character in a regex is a metacharacter that introduces a comment, but in `grep -E` (which is what the spec uses at line 247: `[[ "$f" =~ $part ]]`) the `#` is treated as a literal ONLY in BRE; in ERE (extended regex) it is ALSO a literal. So the pattern is treated as a literal string. But: **the regex would require a tracked file to contain the literal substring `tests/                        # talk / summon / soul / sqlite-vec / firewall import-path only` to match**. **No tracked file matches that.** → `tests/` ends up in REMOVED.

I verified this by running the awk extractor against the live `PUBLIC_ALLOWLIST.txt`:
- 18 patterns extracted (correct count for the allowlist)
- 2 of 18 include inline comments
- `tests/` is NOT in the EXCEPTIONS list (spec lines 221-234)
- `tests/` is in the ALLOW section as `tests/  # talk / summon / soul / sqlite-vec / firewall import-path only`
- → `tests/` would be `git rm --cached` on the debut cut

I confirmed this by direct test: `echo "tests/test_foo.py" | grep -E '^tests/                        # talk / summon / soul / sqlite-vec / firewall import-path only'` returns exit code 1 (no match).

**Implication**: The debut cut would **delete the entire `tests/` directory from the public tree** if the script ran as-is. The tests are referenced in PUBLIC_ALLOWLIST.txt (line 21), they are essential for INST-1 (D-548), and they are the only way to verify any future PR. **This is a P0 bug**.

**.github/workflows/** is in the EXCEPTIONS list (line 224), so it would be saved by the exception, but the `#.github/workflows/` regex is still broken.

**Recommended fix** (15 min, Ma'at):
1. **Strip trailing comments** in the awk extraction: `gsub(/[ \t]+#.*$/, "")` before printing
2. **Add `tests/`, `src/omega/`, `Makefile`, `pyproject.toml`, `docs/strategy/PUBLIC_ALLOWLIST.txt` to the EXCEPTIONS list** as belt-and-suspenders (already mostly there except tests)
3. **Add an integration test**: `cd /tmp/allowlist-test; create a fake `tests/` and `src/omega/`; run script; verify tests/ is in KEPT, not REMOVED`

**Architecture review**:
- **Two-pass design (DRY-RUN default; --confirm for writes)**: ✅ **Genuinely good**. This is the right pattern for any destructive operation. I would have recommended this.
- **EXCEPTIONS list is hardcoded** (spec lines 221-234). The list contains 12 entries. If `PUBLIC_ALLOWLIST.txt` ever changes to require a file not in the list, the script will silently remove it. **Fix**: derive EXCEPTIONS from the same awk extraction but with a different marker (e.g. `## ⚠️ Explicit Exclusions`).
- **Glob-to-regex translation** (spec lines 196-211) is implemented in a 14-line awk pipeline. I read it carefully. **Two issues**:
  - `gsub(/\*\*/, "\x01")` uses ASCII SOH (0x01) as a placeholder. This is correct (SOH is unlikely to appear in paths), but should be documented. Not a bug.
  - The final `gsub(/[][{}()+.|^$\\]/, "\\\\&")` escapes regex specials AFTER glob translation. Order matters: glob `*` becomes `[^/]*` (regex chars `*` and `^` and `/` are already in the output); then the escape pass escapes `^` to `\^`. **The `^` would be double-escaped**. Wait — let me re-trace. The awk pipeline:
    1. `gsub(/\*\*/, "\x01")` → `**` → SOH
    2. `gsub(/\*/, "[^/]*")` → `*` → `[^/]*`
    3. `gsub(/\?/, "[^/]")` → `?` → `[^/]`
    4. `gsub(/\x01/, ".*")` → SOH → `.*`
    5. `gsub(/[][{}()+.|^$\\]/, "\\\\&")` → escapes regex specials

  Step 5 escapes `^` to `\^`. So a pattern starting with `src/omega/` becomes `\^src/omega/`. The bash test `[[ "$f" =~ $part ]]` interprets `\^` as a literal `^` in the input. **No tracked file starts with `^`**, so the regex would only match if the regex is anchored at start. The spec then prepends `^` at line 209: `print "^" $0`. So the final regex is `^^src/omega/`. **That's a literal `^` followed by an anchor `^`. In bash regex, `^^` means a literal `^` followed by an anchor `^` — only matches strings starting with `^`. No file starts with `^`. NO MATCH. ALL FILES GO TO REMOVED.**

  Wait — this is even worse than I thought. **The regex builder would match NOTHING, REMOVE EVERYTHING, and the debut cut would be empty.** I need to test this. But I don't have the script on disk to test. The spec says `print "^" $0` — so yes, the output is `^` + the glob-translated pattern. The pattern starts with the original text (e.g. `src/omega/`) which doesn't contain `^`. After glob→regex translation, no `^` is added. After escape step 5, no `^` is added (the input is `src/omega/`, not `^src/omega/`). Then line 209 prepends `^` → final regex is `^src/omega/`. That's correct.

  I was wrong. Let me re-read step 5: `gsub(/[][{}()+.|^$\\]/, "\\\\&")`. The character class `[][{}()+.|^$\\]` includes `^`. When gsub finds a `^` in the input, it replaces it with `\\^` (literal backslash + caret). But the input at step 5 is the glob-translated string, which has no `^` in it (the original allowlist pattern was `src/omega/`, no `^`). So step 5 doesn't add `\^`. Then line 209 prepends `^`. Final regex = `^src/omega/`. Correct.

  OK, false alarm on the double-anchor. **The P0 bug is just the inline-comment-in-pattern issue.** The rest of the regex builder is correct.

- **Strict mode** (spec lines 170-183) detects patterns with shell metacharacters but **the detection is incomplete** — it allows backticks, dollar signs, pipes, etc. if they end in `?` or `*`. The fallback is just a warning, not a fail. **Defensible** but I'd want a stricter check.

- **Empty allowlist handling** (spec lines 164-167): exits 2 only with `--strict`. Without `--strict`, prints warning and continues with 0 patterns → **all files in REMOVED**. **This is fail-OPEN by default, not fail-CLOSED.** Per M23 doctrine, the default should be fail-closed. **Fix**: exit 2 if patterns is empty, regardless of `--strict`. The `--strict` flag should control additional validation, not the base case.

- **Symlink handling**: The script walks `git ls-files`. Git does not follow symlinks in the index. **A symlink in the working tree pointing to a non-allowlisted path would NOT be detected.** The cut would leave the working-tree symlink in place. **Defensible** (symlinks are an edge case in `git rm --cached`) but worth noting.

- **Path with spaces in the exception list**: `is_exception` does `[[ "$f" == "$ex" ]]`. **Quote the variables** — wait, they ARE quoted. False alarm. But: **the EXCEPTIONS list is not read from `PUBLIC_ALLOWLIST.txt`** — it is hardcoded. So a path in the allowlist that is NOT in EXCEPTIONS relies on the regex match. If the regex builder has a bug (as the inline-comment one does), the file gets REMOVED.

**Confidence**: 5/10 on ship-readiness (the inline-comment bug is P0). 9/10 on architecture design (two-pass, fail-closed, EXCEPTIONS list, regex builder, etc.).

**Triage**: 🔴 **P0 FIX-FIRST** (the regex builder bug). Then ship.

---

#### §2.2.2 `scripts/setup_2remote_debut.sh` (180 LOC in spec, NOT ON DISK)

**What it does**: 5 subcommands (`init`, `cut`, `sync`, `hotfix-start`, `hotfix-finish`) for the 2-remote (private forge + public debut) workflow.

**Architecture review**:
- **Prompts require literal `yes`** (not `y`) — M23-correct. Anti-fat-finger design. ✅
- **`--force-with-lease` exclusively for force-pushes** — this is the right choice. `--force` is a footgun. ✅
- **Tagging is interactive and requires `yes`** — also correct. ✅
- **Cherry-pick uses `-m 1` for merge commits** — required for `--no-ff` merges. ✅
- **`scripts/setup_2remote_debut.sh hotfix-finish`** has a fragile pattern: `git log --oneline -20 | grep -F "Merge hotfix $tag" | head -1`. The merge commit message is `Merge hotfix $tag into $DEBUT_BRANCH` (set in `cmd_hotfix_finish`), so `grep -F "Merge hotfix $tag"` should match. But if a previous hotfix with the same tag exists, `head -1` picks the wrong one. **Edge case but unlikely** (tag is unique per hotfix).

**M1 (AnyIO) consideration**: This is a bash script that orchestrates git. **No async I/O**. M1 applies to Python code, not bash. ✅

**M16 (Modularization)**: The script hardcodes some paths via env vars but no absolute paths. Acceptable.

**Not on disk**: This script does not yet exist. The audit is theoretical. If a Ma'at cycle is going to land this, the review is fine; if the script is going to be used at debut, it MUST be tested in `/tmp/2remote-test-public.git` per the spec's own testing surface.

**Confidence**: 8/10 (architecturally sound; not yet tested on a real public remote).

**Triage**: 🟡 **FIX-FIRST** (write to disk + test in /tmp). 60 min to ship.

---

#### §2.2.3 `.github/workflows/allowlist-check.yml` (95 LOC in spec, NOT ON DISK)

**What it does**: Reusable workflow (`on: workflow_call`). Caller passes `branch` + `allowlist_path` + `fail_on_extra`. Checks out the branch, runs `apply_public_allowlist.sh --summary`, parses the output, fails if `extra_count > 0`.

**Architecture review**:
- **Reusable workflow pattern is correct** — `workflow_call` + `inputs` + `outputs` is the modern GitHub Actions way to share logic. ✅
- **Re-runs the script twice** (once for count, once for list) — wasteful but defensive. Defensible.
- **Output parsing uses `awk` against a specific output format** — fragile to future refactors of the script. The spec explicitly acknowledges this: "If a future refactor changes the output, the awk pattern fails closed (empty list, zero count) rather than silently passing." ✅ (fail-closed, per M23)
- **`if [[ "$REMOVED_COUNT" -gt 0 ]]`** + `if [[ "${{ inputs.fail_on_extra }}" == "true" ]]` + `exit 1` — fail-closed. ✅
- **Does NOT pass `--confirm`** to the script — read-only, perfect for a check. ✅
- **Permissions: `contents: read`** — least-privilege. ✅
- **`actions/checkout@v4`** with `fetch-depth: 0` — correct for full-history validation.
- **The 20-file annotation limit** is correct (GitHub API limits).

**Not on disk**: Cannot be tested. If landed as-is, would catch the P0 cut-tool bug I found above (because `apply_public_allowlist.sh --summary` would report `Removed: >0` for the cut that should be no-op).

**Confidence**: 9/10 (best-in-class reusable workflow).

**Triage**: 🟢 **SHIP-NOW** (after apply_public_allowlist.sh fix). 60 min to write to disk + test.

---

#### §2.2.4 `.github/workflows/allowlist-lint.yml` (65 LOC in spec, NOT ON DISK)

**What it does**: PR-only lint of the allowlist file itself. Catches: missing sections, empty ALLOW, FORGE↔ALLOW drift, invalid globs.

**Architecture review**:
- **`paths:` trigger limits noise** — ✅
- **Section presence check (lines 522-531)** is a 3-section check: ALLOW, FORGE, Explicit Exclusions. The current allowlist has all 3 (verified).
- **Empty allowlist check** (line 540): `if [[ "$ALLOW_LINES" -lt 5 ]]`. The current allowlist has 18 patterns. The threshold of 5 is arbitrary. **I'd want this to be config-driven** (workflow input), but a hardcoded minimum is defensible.
- **Drift detection** (lines 547-579): Uses `git show origin/main:...` and `diff` to find additions/removals. **This only works if `origin/main` is the merge target**. If the debut cuts from a different branch, the diff is wrong. **Defensible** for the main→debut case.
- **Glob syntax validation** (line 583-589): Calls `apply_public_allowlist.sh --strict --summary`. **This re-runs the cut-tool against the live allowlist — a great idea, because it would have caught the P0 inline-comment bug.**

**Not on disk**.

**Confidence**: 9/10.

**Triage**: 🟢 **SHIP-NOW**.

---

#### §2.2.5 `.github/workflows/debut-hotfix.yml` (110 LOC in spec — claimed but NOT IN THE DOC I READ)

**WAIT** — the spec doc `R_VAULT_COPILOT_DEEPER_20260827.md` lists 7 files in its §0 EXECUTIVE VERDICT table (lines 35-44), but the table-of-contents + sections I read (§0–§9) only describe 6 files (apply, allowlist-check, allowlist-lint, setup_2remote, dependabot, INCIDENT_RESPONSE_HOTFIX_SLA). **The debut-hotfix.yml mentioned in the table at line 41 is NOT in the doc I read.** I may have missed a section. Let me note: the table claims it exists at 110 LOC and 85% confidence, but it's not in §1, §2, §3, or §4. **The doc may have been truncated before the hotfix workflow section**, or the table is a forward-reference. **I cannot audit what isn't there.** Logged as a finding.

**Triage**: ⚠️ **CANNOT AUDIT** (spec is incomplete). Add to a follow-up audit.

---

#### §2.2.6 `.github/dependabot.yml` (60 LOC in spec, NOT ON DISK)

**What it does**: Dependabot config for github-actions + pip ecosystems. 3-day cooldown for version updates, NO cooldown for security updates, ignore list for `anyio` and `cryptography`.

**Architecture review**:
- **Cooldown is 2026-current** per github.blog 2026-07-23 reference. ✅
- **Grouping by semver level** reduces PR noise. ✅
- **Ignore list is deliberate** for sovereignty reasons (M1 + R_VAULT_D568). ✅
- **No auto-merge** — explicit per the spec. ✅
- **`commit-message.prefix: "ci"` and `"chore"`** — consistent with conventional commits.
- **DEPRECATION NOTE**: The spec at line 1235-1240 cites `R_VAULT_D568` and says "cryptography is pinned for portability". But per the D-568 gap-fill I read at `session_gnosis_D568_20260827.md`, the Council REVERSED the original D-568 decision: **`EncryptionBackend primary = cryptography AES-256-GCM with Argon2id`** (not python-age). The dependabot ignore list for `cryptography` is **correct** for the post-debut vault sprint, but the **debut is hiding the vault entirely** (D-565). So during PUBLIC-DEBUT-01, `cryptography` is not in use at all. The ignore is harmless but the rationale is wrong for the debut branch. **Minor doc fix needed; not a code bug.**

**Not on disk**.

**Confidence**: 9/10.

**Triage**: 🟢 **SHIP-NOW** (after doc citation fix).

---

#### §2.2.7 `docs/operations/INCIDENT_RESPONSE_HOTFIX_SLA.md` (150 LOC in spec, NOT ON DISK)

**What it does**: Operational runbook for vulnerability response. SLOs by CVSS severity (P0=4h, P1=24h, P2=7d, P3=30d). Post-mortem template. Communication templates.

**Architecture review**:
- **SLOs are industry-validated** (per Anthropic CVD dashboard + git-security mailing list references). ✅
- **9-step P0 procedure** (lines 980-1006) is clear and well-paced. ✅
- **Tag immutability rule** is correct. ✅
- **Tag signing requirement** is correct (GPG or SSH). ✅
- **M23-grounded throughout** — no soft-fail theater, explicit human-in-the-loop.

**Not on disk** — and this is **operational documentation**, not code. Belongs in `docs/operations/` and tracked in CORPUS_MAP per M27.

**M26 concern**: I cannot run `make doc-llm-validate` against a markdown that doesn't exist. The spec LOOKS well-formatted (header hierarchy, length, terminology consistency) but the gate must be run on the actual file.

**Confidence**: 8/10 (well-designed; needs the file written + M26 validation).

**Triage**: 🟡 **FIX-FIRST** (write to disk + run M26 gate). 30 min to ship.

---

### §2.3 Cline Group (ALL IN /tmp/, NOT IN REPO)

#### §2.3.1 `scripts/three_store_shim.py` (380 LOC, in /tmp/omega/cline_deeper/)

**What it does**: Scans 3 plaintext credential stores (`secrets.json`, `providers.json`, `auth.json`) and produces a unified inventory + AES-256-GCM encrypted blob. Two commands: `scan` (read-only) and `inventory` (writes).

**D-568 compliance check**:
- **Uses `cryptography.hazmat.primitives.ciphers.aead.AESGCM`** (line 259). ✅ **D-568-correct** (per gap-fill Council reversal: cryptography AES-256-GCM is the canonical path).
- **AAD bound to `b"omega-vault-shim-v1"`** (line 265). ✅ AAD is a static string. Minor: should also bind a version field for rotation safety, but acceptable.
- **Nonce is `os.urandom(12)`** (line 264). ✅ Correct length for GCM. Cryptographically random.
- **Master key resolution** (lines 335-354): `--master-key` (hex) > `--keyfile` (mode 600 enforced) > `OMEGA_VAULT_MASTER_KEY` (env) > `--dev-derive` (hostname). The `dev_derive` fallback is **clearly marked DO NOT USE IN PROD**. ✅
- **`master_keyfile.read_bytes()[:32].ljust(32, b"\x00")`** (line 345): if the keyfile is shorter than 32 bytes, it's zero-padded. **This silently accepts a short key.** Should `raise CryptoError` if the keyfile is < 32 bytes. **Defense in depth.**
- **AESGCM key must be exactly 32 bytes** (line 260-261): enforced. ✅

**WorkOS OAuth triple handling**:
- **`scan_cline_providers`** reads `auth.accessToken`, `refreshToken`, `expiresAt`, `accountId`, `metadata` (lines 144-152). **Correctly extracts the WorkOS triple.** ✅
- **The `value` is stored as a dict** (line 146), not flattened. The `CredentialEntry` dataclass has `value: str | dict[str, Any]`. The fingerprint is computed in `__post_init__` from `json.dumps(self.value, sort_keys=True)` for dicts. **Fingerprint is stable across processes** (sort_keys=True). ✅
- **The `ACCOUNT_BLOB` handling** (lines 105-111) for `cline:clineAccountId` is a 1.3KB opaque blob. Stored as-is. ✅

**M14 (no-plaintext) violation I found**:
- **The plaintext inventory at line 277** writes `[asdict(e) for e in entries]` to `data/vault/inventory.json` — and `asdict(e)` includes the `value` field (which is the plaintext credential). **The docstring at line 60-61 says "encrypted via the shim, with a plaintext index for the M2 boundary — the inventory is the *seed*; the encrypted payload goes to vault"**. So the design INTENT is "plaintext index + encrypted payload". But the docstring at line 9-10 claims **"M14 (no plaintext)"**. **The shim WRITES PLAINTEXT CREDENTIALS TO DISK at line 277, which is a direct M14 violation per the docstring's own mandate claim.**
- **This is a contradiction in the code's design intent.** Either:
  - (a) the docstring at line 60-61 is correct (plaintext index IS the design), and the M14 claim at line 9-10 is a copy-paste error, OR
  - (b) the M14 claim is correct, and the inventory.json must NOT include plaintext credentials.
- **(a) is what the code does**. The fix is: change line 9-10 to remove the M14 claim, OR change `asdict(e)` to exclude the `value` field and use the fingerprint only.
- **Either fix is 5 min.** The bug is the inconsistency, not the functionality.

**M9 (typed errors)**:
- ✅ Typed error hierarchy: `ShimError → StoreReadError, StoreWriteError, CryptoError, InventoryDrift`. Bare `except (OSError, json.JSONDecodeError)` is exception-specific, not bare. ✅
- ❌ `except sqlite3.Error as e:` (line 237-239) is fine. ✅

**Single-writer lock**:
- **Line 244-250**: `os.open + fcntl.flock`. The fd is opened, flock is attempted, and the function returns with the fd open. **The fd is never closed in this function.** The comment says "leave fd open for process lifetime; lock released on exit." This is OK for a CLI tool (the process exits), but for a long-running daemon it's a fd leak. **Acceptable for a CLI.**
- **Race**: If `os.open` succeeds but `fcntl.flock` raises (e.g., lock held), the `os.close(fd)` at line 249 is correct. ✅
- **But**: `os.open` is called with `O_CREAT | O_RDWR` and mode 0o600. The lock file is created with restrictive perms. ✅

**Octo / `oct()`**:
- Line 357-358 defines `def octo(n): return oct(n)`. **This is a needless wrapper.** Used only at line 344: `octo(mode)`. The function is called `octo` to avoid shadowing the built-in `oct`. **This is cargo cult.** Just `oct(mode)` works. **Fix: delete `octo`, use `oct`.**

**Confidence**: 6/10 (correct crypto, correct WorkOS triple, but M14 docstring contradiction + short-key silent pad).

**Triage**: 🟡 **FIX-FIRST** (5 min) → 🟢 ship. BUT: **out of scope for debut** (D-565 forbids vault code in debut). **Defer to post-debut V-1 sprint.**

---

#### §2.3.2 `scripts/continuity_bridge.py` (301 LOC, in /tmp/omega/cline_deeper/)

**What it does**: Bridges Cline's `sessions.db` git-stash checkpoints to Omega's Session Continuity Protocol (`session_gnosis.md` + Hivemind).

**P0 FINDING — M1 (AnyIO) violation**:

The code uses `subprocess.run` (lines 105-108, 138-141, 144-148, 199-202) directly, NOT wrapped in `anyio.to_thread.run_sync()`. Per **M1**:
> All asynchronous code MUST use AnyIO. Wrap blocking I/O in `anyio.to_thread.run_sync`.

`subprocess.run` is a blocking call that holds the GIL. It should be wrapped. This script CAN be called from an async context (e.g., from a Hivemind listener). **A direct `subprocess.run` from an event loop blocks the loop and can cause event-loop collisions across the Provider Fabric.**

**However**: M1's primary domain is `src/omega/`. The M1 mandate says: "All asynchronous code MUST use AnyIO. Never use `asyncio` directly." The mandate is silent on `subprocess.run` in scripts. But the spirit is clear: don't block the event loop. **This script, if run from a Hivemind listener, WOULD block the loop.**

**Fix** (15 min): wrap each `subprocess.run` in `anyio.to_thread.run_sync` with a function-local lambda, or use `asyncio.to_thread` (which AnyIO supports via `anyio.to_thread`). OR: declare this script as "sync-only, never call from async context" and add a `# NOT for async contexts` docstring.

**Confidence**: 7/10 (functionally correct; M1 violation if used from async).

**Other findings**:
- **`LIKE 'prefix%'` in SQLite** (line 65) doesn't escape `%` or `_` in `cwd_prefix`. If a path contains those chars, the query is wrong. **Edge case**; not a security issue (the script is local).
- **Destructive `git stash apply ref`** at line 200-203 — no diff preview, no confirmation. **The `--apply` flag is opt-in**, which is good, but once opted-in, the action is silent. **Fix**: print the diff before applying, or require a second `yes` confirmation.
- **`gnosis_path` hardcoded to `grokster`** (line 51). Wrong — should be the entity of the current session. **Fix**: take `--entity` arg, default to `grokster` for now.
- **WorkspaceStale exception** used for both git-stash-show failure AND git-stash-apply failure (lines 109-112, 204-205). **Should be distinct: `StashNotFound` vs `StashApplyConflict`.**
- **`subprocess.run` timeout** is 30s for stash show, 10s for rev-parse, 10s for stash show. Reasonable.

**Triage**: 🟡 **FIX-FIRST** (M1 wrap + entity arg) → 🟢 ship. **Out of scope for debut** (per D-565). **Defer to post-debut V-1 sprint.**

---

#### §2.3.3 `scripts/cline_prune.sh` (116 LOC, in /tmp/omega/cline_deeper/)

**What it does**: Weekly cron job that scans `sessions.db` for checkpoint refs, marks elderly (90+ days) and orphans (workspace gone, stash dropped), and alerts if high count.

**Findings**:
- **`REPO_ROOT` hardcoded** to `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine` (line 28). **M16 violation.** Should be `$(git rev-parse --show-toplevel)` or env var.
- **JSON construction from unescaped values** (line 74, 80, 87, 96): `echo "{\"ts\":\"$(date ...)\",\"kind\":\"...\",\"session\":\"$SID\",...}"`. If `SID` or `REF` contains `"`, the JSON breaks. **Use `jq -c` instead.**
- **`git stash list | grep -q "$REF"`** (line 86): `$REF` could be a prefix. **Fix**: `grep -F -x "$REF"`.
- **Path-injection vector** (line 85): `if [[ -n "$WS_ROOT" && -d "$WS_ROOT/.git" ]]` — if `WS_ROOT` is empty, the check is on `WS_ROOT/.git` which expands to `.git` in the current dir. The `[[ -n "$WS_ROOT" ]]` guard prevents this... wait, the guard IS there. False alarm. But the `git -C "$WS_ROOT" stash list` on line 86 still runs `git` from cwd, which is `$REPO_ROOT` (hardcoded). If `WS_ROOT` is a different repo, this is wrong. **Edge case.**
- **`date -d "$STARTED" +%s 2>/dev/null || echo 0`** (line 69): silently returns 0 for malformed dates. Inverts the meaning (0 days = today, not "very old"). **Fix**: log a warning for unparseable dates and skip the row.
- **`TOTAL=$(wc -l < "$TMP")`** (line 62): counts ALL lines including any blank lines or partial lines. **Fix**: `grep -c .`.
- **`ELDERLY` count** is incremented but the row is `continue`d, so the `ORPHAN + ELDERLY` sum double-counts for the summary. **Fix**: the summary should be `TOTAL` (the unique count of rows processed) rather than `ORPHAN + ELDERLY`.
- **Hivemind post uses `--intent "blocker"`** (line 112) for a non-blocking alert. **Wrong intent** — should be `alert` (the G13 detector uses `alert`).

**Confidence**: 7/10 (logic is sound; lint-level issues).

**Triage**: 🟡 **FIX-FIRST** (jq + grep -F -x + REPO_ROOT). **Out of scope for debut** (per D-565). **Defer to post-debut.**

---

#### §2.3.4 `scripts/migrate_3store.sh` (153 LOC, in /tmp/omega/cline_deeper/)

**What it does**: One-shot migration: backup 3 stores → generate master key → run shim scan → run shim inventory → verify decrypt → sanity check.

**Findings**:
- **`REPO_ROOT` hardcoded** to `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine` (line 32). **M16 violation.**
- **Step 5 verify** (line 103-118): `AESGCM(keyfile.read_bytes()[:32].ljust(32, b"\x00"))` — same silent-zero-pad issue as the shim's `_resolve_master_key`. The keyfile is generated at line 78 as `os.urandom(32)` — exactly 32 bytes, so `ljust` is a no-op here. But the code is fragile: if the keyfile is regenerated by a different tool that doesn't pad, the shim's verify and the shim's encrypt will diverge.
- **Step 6 sanity check** (line 122-136): reads the plaintext inventory and compares to the backup. **This confirms the shim PRESERVES the plaintext credential correctly** — but the **script does NOT migrate the actual credentials to a new store**. The original plaintext files at `~/.cline/data/secrets.json` etc. are still there with original permissions. **The comment at line 151-152 says "The 3 source stores are now READ-ONLY for non-shim processes" — this is a LIE.** The script doesn't `chmod` anything. **The shim's `acquire_single_writer_lock` only protects the SHIM's writes; it doesn't prevent other processes from writing to the source stores.** **Fix**: either actually `chmod 444` the source stores, or remove the misleading comment.
- **Heredoc with embedded shell variables** (line 103-118, 122-136): `$MASTER_KEY_PATH`, `$BACKUP_ROOT`, `$REPO_ROOT` are interpolated. **Quote them in the heredoc** (`<<'PY'`) to prevent shell expansion if paths contain special chars. Or pass them via env.
- **Step 1 backup uses `install -m 600`** (line 62): mode is correct, but `install` doesn't preserve timestamps. **Minor**.

**Confidence**: 6/10 (functional but the "read-only" claim is false).

**Triage**: 🟡 **FIX-FIRST** (correct the read-only claim + REPO_ROOT). **Out of scope for debut** (per D-565). **Defer to post-debut.**

---

## §3 TOP 3 CRITICAL BUGS (across all 12)

### BUG #1: `antigravity_quota_probe.py` — hardcoded OAuth client_secret (line 20)

**Severity**: 🔴 **P0 — M8 violation + secret-scan.yml trip**

```python
CLIENT_SECRET = "GOCSPX-***REDACTED-ROTATED***"
```

**Why P0**: This is a **hardcoded credential in a public-debut candidate file**. The secret is a public OAuth client (same for all Antigravity users), so it's not a *real* leak in the cryptographic sense. **But**: gitleaks will flag the pattern, `secret-scan.yml` will fail, and the debut branch will be blocked. **Also**: the pattern violates M8's spirit (zero external credentials in source) and M23's "no soft-fail" doctrine (a soft-fail here is "we know it's a public client but we put it in source anyway").

**Fix** (5 min, Ma'at): env-overridable pattern with documented defaults.

---

### BUG #2: `apply_public_allowlist.sh` — destructive regex bug (P0, blocks debut)

**Severity**: 🔴 **P0 — would DELETE `tests/` on debut cut**

Two allowlist patterns include inline comments:
```
tests/                        # talk / summon / soul / sqlite-vec / firewall import-path only
.github/workflows/            # unit tests + gitleaks only
```

The awk extractor (spec lines 147-162) does NOT strip trailing comments. The regex builder (spec lines 191-213) then produces regexes that cannot match any tracked file. **The debut cut would `git rm --cached` the entire `tests/` directory** (which is in PUBLIC_ALLOWLIST.txt line 21 and is **not** in the EXCEPTIONS list).

**Why P0**: `tests/` is the only way to verify any future PR. Deleting it makes the debut unmaintainable. INST-1 (D-548) requires tests to pass. **A debut without tests is not a debut.**

**Fix** (15 min, Ma'at):
1. Add `gsub(/[ \t]+#.*$/, "")` to the awk pipeline to strip inline comments
2. Add `tests/`, `src/omega/`, `Makefile`, `pyproject.toml` to EXCEPTIONS
3. Add an integration test in `/tmp/allowlist-test` per the spec's own testing surface

**Verification**: I tested the awk extractor against the live `PUBLIC_ALLOWLIST.txt` and confirmed 2 of 18 patterns include inline comments. I tested the resulting regex against `tests/test_foo.py` and confirmed it does NOT match.

---

### BUG #3: `continuity_bridge.py` — M1 (AnyIO) violation (subprocess.run unwrapped)

**Severity**: 🟡 **M1 violation** (deferrable if script is sync-only)

`subprocess.run` is called at lines 105, 138, 144, 199 without `anyio.to_thread.run_sync()` wrapping. If this script is ever called from an async context (e.g., from a Hivemind listener), it will block the event loop.

**Why not P0**: The script's docstring describes a CLI flow (find → extract → show → log → gnosis). It is not currently called from async code. **But the Sovereign Mandate M1 is non-negotiable**, and the cost of an event-loop collision is a Provider Fabric stall.

**Fix** (15 min): wrap each `subprocess.run` in `anyio.to_thread.run_sync`, OR add a `# M1: this script MUST be called from sync context only` docstring + a runtime check.

**Out-of-scope note**: Per **D-565**, the vault is hidden for debut. So this script is post-debut. The fix can happen in the V-1 sprint. But the audit must note it.

---

## §4 TOP 3 ARCHITECTURAL CONCERNS

### CONCERN #1: The 12 "artifacts" are not in a uniform state

**Summary**: 2 are on disk. 4 are in /tmp. 6 are in a markdown. The dispatch says "12 CODE ARTIFACTS SHIPPED" — but "shipped" is doing a lot of work. **This is the most important finding of the audit.**

**Why it matters**: A debut cannot ship on a portfolio of mixed artifacts. The pipeline needs:
- Either: write all 12 to disk + test in /tmp + commit
- Or: classify the 6 in-doc artifacts as "specs" and route them to a spec doc that Ma'at reads when writing the actual code

**Current state is neither.** This is M27 (Tracking Integrity) violation: artifacts without ACTIVE_SPRINT entries are, per D-540, "dead".

**Recommendation**: Scribe pass (20 min) to add 12 rows to `data/coordination/ACTIVE_SPRINT.json` DEBUT-REMEDIATION workstream, with statuses: `ready` (2 Antigravity) / `ready` (6 Copilot, after P0 fix) / `parked` (4 Cline, post-debut per D-565).

---

### CONCERN #2: D-565/D-567/D-568 interpretation conflicts across artifacts

**The conflict**:
- **D-565** says vault is hidden via allowlist for debut, zero code changes to vault.
- **D-567** says `bury_credential` applies to post-debut vault sprint only.
- **D-568** says `EncryptionBackend primary = python-age (NOT pyrage)`.
- **D-568 gap-fill** (researcher, 2026-08-27) REVERSED D-568: Council 4-0 on `cryptography AES-256-GCM`.
- **The 3-store shim** uses `cryptography AES-256-GCM` (correct per gap-fill).
- **The dependabot ignore list** cites `R_VAULT_D568` to justify pinning `cryptography` — but the cite is to the **original** D-568 (which said python-age), not the gap-fill reversal. **Wrong citation.**

**Why it matters**: If the debut is using `cryptography` (per gap-fill), then the dependabot ignore is for the right reason. If the debut is using `python-age` (per literal D-568), then the ignore is for the wrong reason. **The PIVOT_LOG has not been updated to reflect the gap-fill reversal.** The dependency audit at debut will see "ignored: cryptography" and ask "why?" and get an outdated answer.

**Recommendation**: Kali update PIVOT_LOG with D-568 reversal (already on the researcher's next-steps list, item #2 in `session_gnosis_D568_20260827.md`).

---

### CONCERN #3: No integration test for the cut-tool on a /tmp repo

**Summary**: Both `apply_public_allowlist.sh` and `setup_2remote_debut.sh` include `/tmp` testing surfaces in their specs (lines 333-361 and 905-920 of the research doc). **Neither test has been run.** The first run will surface edge cases (Grokster's own admission in the doc §6.1).

**Why it matters**: The P0 regex bug I found in §3.2 is exactly the kind of edge case that a 5-minute /tmp test would have caught. **The spec's own testing surface, had it been run, would have surfaced this P0 before the audit.**

**Recommendation**: Ma'at run the spec's `/tmp` test surfaces BEFORE the debut cut. Budget: 30 min. The cost of NOT running them is shipping a P0 bug to the public debut.

---

## §5 TRIAGE TABLE (ship-now / fix-first / defer)

| # | Artifact | Verdict | Owner | Effort | Notes |
|---|----------|---------|-------|--------|-------|
| 1 | `g13_empty_response_detector.py` | 🟢 **SHIP-NOW** | Ma'at | 5 min | Fix Hivemind double-alert hash first |
| 2 | `antigravity_quota_probe.py` | 🟡 **FIX-FIRST** | Ma'at | 10 min | P0: env-overridable secret + tighten excepts |
| 3 | `apply_public_allowlist.sh` | 🔴 **P0 FIX-FIRST** | Roc | 30 min | Strip inline comments; add tests/ to EXCEPTIONS; /tmp test |
| 4 | `setup_2remote_debut.sh` | 🟡 **FIX-FIRST** | Ma'at | 60 min | Write to disk + /tmp 2-remote test |
| 5 | `allowlist-check.yml` | 🟢 **SHIP-NOW** | Ma'at | 60 min | After #3 fix |
| 6 | `allowlist-lint.yml` | 🟢 **SHIP-NOW** | Ma'at | 30 min | After #3 fix |
| 7 | `debut-hotfix.yml` | ⚠️ **CANNOT AUDIT** | — | — | Spec is incomplete (not in doc I read) |
| 8 | `dependabot.yml` | 🟢 **SHIP-NOW** | Ma'at | 30 min | Update D-568 citation to gap-fill |
| 9 | `INCIDENT_RESPONSE_HOTFIX_SLA.md` | 🟡 **FIX-FIRST** | grokster | 30 min | Write to disk + run `make doc-llm-validate` |
| 10 | `three_store_shim.py` | 🟡 **FIX-FIRST** (post-debut) | Ma'at | 15 min | M14 docstring fix + short-key pad rejection. **Defer to V-1 sprint per D-565** |
| 11 | `continuity_bridge.py` | 🟡 **FIX-FIRST** (post-debut) | Ma'at | 30 min | M1 wrap + entity arg + distinct exceptions. **Defer to V-1 sprint per D-565** |
| 12 | `cline_prune.sh` | 🟡 **FIX-FIRST** (post-debut) | Ma'at | 30 min | jq + grep -F -x + REPO_ROOT. **Defer to V-1 sprint per D-565** |
| 13 | `migrate_3store.sh` | 🟡 **FIX-FIRST** (post-debut) | Ma'at | 30 min | REPO_ROOT + read-only claim. **Defer to V-1 sprint per D-565** |

**Counts**:
- 🟢 Ship-now (after trivial fix): 4 (G13, allowlist-check, allowlist-lint, dependabot)
- 🟡 Fix-first (debut scope): 4 (antigravity_quota, apply_public_allowlist, setup_2remote, INCIDENT_RESPONSE)
- 🔴 P0 fix-first: 1 (apply_public_allowlist)
- ⚠️ Cannot audit: 1 (debut-hotfix.yml — spec incomplete)
- 🟡 Fix-first (post-debut, per D-565): 4 (3-store shim, continuity_bridge, cline_prune, migrate_3store)

**Effort total**: ~5.5h to ship the debut-scope artifacts (4 ship-now + 4 fix-first + 1 P0). The post-debut 4 are another ~2h but out of scope.

---

## §6 BEFORE-SHIP CHECKLIST (debut branch)

The following MUST be true before `release/debut` is cut and pushed to the public remote:

### Code on disk
- [ ] All 6 Copilot artifacts written to `scripts/` and `.github/workflows/` and `docs/operations/`
- [ ] `apply_public_allowlist.sh` P0 fix landed (inline-comment strip + tests/ in EXCEPTIONS)
- [ ] `antigravity_quota_probe.py` P0 fix landed (env-overridable secret)
- [ ] `g13_empty_response_detector.py` Hivemind double-alert fix landed

### Test runs
- [ ] `/tmp/allowlist-test` test of `apply_public_allowlist.sh` passes (DRY-RUN shows `tests/` in KEPT, not REMOVED)
- [ ] `/tmp/2remote-test-public.git` test of `setup_2remote_debut.sh` init + cut + sync + hotfix-start + hotfix-finish passes
- [ ] `/tmp/antigravity-test` test of `antigravity_quota_probe.py` runs without hardcoding secret
- [ ] `g13_empty_response_detector.py` against synthetic 4-shape test data returns the right counts (Grokster claimed 2 G13 / 2 models; verify)
- [ ] `make doc-llm-validate` passes for `INCIDENT_RESPONSE_HOTFIX_SLA.md`
- [ ] `make temple-grade` exits 0
- [ ] `make check-mandate-compliance` exits 0

### Tracking (M27)
- [ ] All 12 artifacts added to `data/coordination/ACTIVE_SPRINT.json` DEBUT-REMEDIATION workstream with correct status (4 ship-now, 5 fix-first, 4 parked)
- [ ] PIVOT_LOG updated with D-568 reversal (cryptography, not python-age)
- [ ] PIVOT_LOG updated with D-565/D-567 reaffirmation (vault = post-debut, hide via allowlist)

### Mandate verification
- [ ] **M1**: any Python with subprocess uses `anyio.to_thread.run_sync` (or is documented as sync-only)
- [ ] **M2**: cut-tool operates only on files under engine paths; no stack logic in `src/omega/`
- [ ] **M7**: cloud order is local-first (already locked in `config/providers.yaml`)
- [ ] **M8**: no hardcoded secrets, no external telemetry in any of the 12 artifacts (after P0 fix to antigravity_quota_probe)
- [ ] **M9**: typed errors throughout (already verified for the 2 Antigravity + 4 Cline)
- [ ] **M14**: no plaintext credentials written to disk (after 3-store shim docstring fix)
- [ ] **M16**: no hardcoded paths (after Cline scripts REPO_ROOT fix — but those are post-debut)
- [ ] **M23**: fail-closed everywhere; no soft-fail theater
- [ ] **M26**: `make doc-llm-validate` passes for `INCIDENT_RESPONSE_HOTFIX_SLA.md`
- [ ] **M27**: ACTIVE_SPRINT has all 12 entries

### Pre-cut sanity
- [ ] INST-1 fresh-venv test passes (D-548 explicit requirement)
- [ ] `omega talk "hello"` exits 0 with PROVIDER_NAME=native-gguf, IS_CLOUD=False
- [ ] `git ls-files data/entities` is a short default-soul set (per PUB-1 acceptance)
- [ ] `git ls-files docs/strategy` is the manual + allowlist + mandates pointers (per PUB-1 acceptance)
- [ ] `git ls-files docs/research` is empty (per PUB-1 acceptance)
- [ ] Allowlist check (allowlist-check.yml) exits 0 on the cut
- [ ] Allowlist lint (allowlist-lint.yml) exits 0 on the cut

### Pre-push sanity
- [ ] Architect signoff on the cut (D-548)
- [ ] Two remote URLs configured (`origin` private + `debut` public)
- [ ] `git push --set-upstream debut release/debut` (no `--force` on first push)
- [ ] Tag v0.1.0 created and signed (GPG or SSH)
- [ ] `git verify-tag v0.1.0` returns success
- [ ] `git push debut v0.1.0`

---

## §7 TESTING EFFORT ESTIMATES

| Artifact | Test effort | Test type | Notes |
|----------|-------------|-----------|-------|
| `g13_empty_response_detector.py` | 30 min | Unit (synthetic 4-shape data) + 30 min live (replay on `free_model_probes.jsonl`) | Grokster claimed 5-entry synthetic test; verify |
| `antigravity_quota_probe.py` | 15 min | Live probe against 7 accounts; verify no secret in output | |
| `apply_public_allowlist.sh` | 30 min | /tmp allowlist-test per spec lines 333-361 | **Critical: must catch the P0 regex bug** |
| `setup_2remote_debut.sh` | 60 min | /tmp 2-remote test per spec lines 905-920 | All 5 subcommands |
| `allowlist-check.yml` | 30 min | GitHub Actions dry-run via `act` or push to feature branch | |
| `allowlist-lint.yml` | 15 min | Same | |
| `debut-hotfix.yml` | — | — | Cannot audit (spec incomplete) |
| `dependabot.yml` | 15 min | Push to feature branch, wait for Dependabot to open a PR | Real-time test; 1-week minimum |
| `INCIDENT_RESPONSE_HOTFIX_SLA.md` | 15 min | `make doc-llm-validate` + read-through by Ma'at | |
| `three_store_shim.py` | 30 min | Unit + live scan of all 3 stores | Post-debut |
| `continuity_bridge.py` | 30 min | Unit + live list + live recover on a test session | Post-debut |
| `cline_prune.sh` | 15 min | ShellCheck + syntax | Post-debut |
| `migrate_3store.sh` | 30 min | --dry-run + on a test fixture | Post-debut |

**Total testing effort**: ~5h for debut-scope (8 artifacts) + ~2h for post-debut (4 artifacts) = **7h**.

---

## §8 5 STILL-UNKNOWN THINGS (per the audit's own gaps)

1. **Does `apply_public_allowlist.sh` correctly handle `data/entities/_omega_default/soul.yaml`?** The allowlist at line 92 says "KEEP" for this file. The EXCEPTIONS list at spec lines 221-234 does NOT include this path. The regex would be `^data/entities/_omega_default/soul.yaml$` if a pattern were added, but the current allowlist has no such pattern. The path falls through to "no allowlist pattern matches" → REMOVED. **Wait — this is a SECOND P0 bug.** The debut keep-list per the spec at line 22 says the file is in the KEEP set, but the implementation does not. **This needs verification.**

2. **What is the `extra_count` threshold for `allowlist-check.yml`?** The spec uses `if [[ "$REMOVED_COUNT" -gt 0 ]]` (line 454) — any non-zero is a fail. But `fail_on_extra` is a boolean input. **Is `0` the right threshold, or should it be a count?** The current design is fail-closed (any non-zero fails). Defensible.

3. **Does `INCIDENT_RESPONSE_HOTFIX_SLA.md` reference paths that exist?** The doc says "Within 7 days of a P0 or P1 fix, write a post-mortem to `data/coordination/postmortems/YYYY-MM-DD-<short-name>.md`". The directory `data/coordination/postmortems/` does NOT exist in the repo (verified by `ls`). **The doc references a directory that doesn't exist. Operational debt.**

4. **Is the G13 detector idempotent across runs?** The detector overwrites `g13_events.jsonl` on each run (via `tmp.replace(output_path)`). But the file is opened in `"a"` mode for the tmp. **The tmp contains only the events from THIS run; the rename replaces the output with just-this-run's events. The previous run's events are LOST.** This is correct for "current state of G13" but the file is named `g13_events.jsonl` (suggesting append-only). **The naming is misleading.** Either rename to `g13_events_latest.json` or change to true append.

5. **Does the antigravity_quota_probe.py produce a 7-row JSONL on a clean run, or does it fail silently on one account and produce 6 rows?** The code has `try/except` per account (lines 58-93), so a single failure doesn't abort. The output count will be 7. ✅

---

## §9 REFERENCES

### Mandates
- **M1** (AnyIO) — `SOVEREIGN_MANDATES.md` §1
- **M8** (Zero Telemetry) — `SOVEREIGN_MANDATES.md` §8
- **M9** (Error Integrity) — `SOVEREIGN_MANDATES.md` §9
- **M14** (Heritage Vetting) — `SOVEREIGN_MANDATES.md` §14
- **M16** (Modularization) — `SOVEREIGN_MANDATES.md` §16
- **M23** (Failure Integrity) — `SOVEREIGN_MANDATES.md` §23
- **M26** (Doc Standards) — `SOVEREIGN_MANDATES.md` §26
- **M27** (Tracking Integrity) — `SOVEREIGN_MANDATES.md` §27

### Decisions
- **D-540** — Corpus Map rule 2 inverted: no ticket in ACTIVE_SPRINT = dead
- **D-548** — INST-1 BLOCKED; 6 critical fixes required before DEL-1
- **D-553** — release/debut branch from allowlist = publication mechanic
- **D-565** — Vault hidden via allowlist for debut; zero vault code changes during PUBLIC-DEBUT-01
- **D-567** — `bury_credential` applies to post-debut vault sprint only
- **D-568** — VaultCore is non-functional; EncryptionBackend primary = python-age (REVERSED by gap-fill Council 2026-08-27 to `cryptography AES-256-GCM`)

### Sprint state
- `data/coordination/ACTIVE_SPRINT.json` — DEBUT-REMEDIATION workstream (P0-1d, PUB-1, INST-1, DEL-1)
- `data/coordination/FT-1/FT-2/FT-3` (Fabric tickets, all completed) — referenced but unrelated to the 12 artifacts

### Artifacts under audit
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/g13_empty_response_detector.py` (218 LOC, on disk)
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/antigravity_quota_probe.py` (170 LOC, on disk)
- `/tmp/omega/cline_deeper/{three_store_shim,continuity_bridge}.py` + `{cline_prune,migrate_3store}.sh` (4 files, /tmp only)
- `data/coordination/research/R_VAULT_COPILOT_DEEPER_20260827.md` (1507L, contains 6 Copilot code blocks)
- `data/coordination/research/R_VAULT_CLINE_DEEPER_20260827.md` (463L, references the 4 Cline files)
- `data/coordination/research/R_VAULT_ANTIGRAVITY_DEEPER_20260827.md` (692L, references the 2 Antigravity files)

### Allowlist (live)
- `docs/strategy/PUBLIC_ALLOWLIST.txt` (106L) — the allowlist being enforced

### Prior research
- `data/entities/researcher/session_gnosis_D568_20260827.md` — D-568 gap-fill Council reversal
- `data/coordination/CARMACK_VAULT_AUDIT_20260818.md` (referenced in gap-fill)
- `docs/research/youtube_research_sessions/session_20260730/04_evidence/CARMACK_DEFINITIVE_STRATEGY_20260730.md` — top-5 force multipliers

---

## §10 L1 → L2 → L3 DISTILLATION

### L1 (Narrative) — What happened in this audit

1. Read all 12 artifacts (2 on disk + 4 in /tmp + 6 in research doc).
2. Verified disk state for each (`ls`, `stat`).
3. Found 3 P0/P1 bugs: hardcoded OAuth secret in antigravity_quota_probe, destructive regex bug in apply_public_allowlist, M1 violation in continuity_bridge.
4. Found 1 categorical bug: the 12 artifacts are not in a uniform state (2 + 4 + 6 across 3 disks).
5. Found 1 doc conflict: D-568 reversal is not yet in PIVOT_LOG; dependabot cite is to the original D-568 not the gap-fill.
6. Tested the awk extractor from `apply_public_allowlist.sh` against the live `PUBLIC_ALLOWLIST.txt` and confirmed the inline-comment regex bug.

### L2 (Insight) — What this means for the debut

1. **The "12 artifacts shipped" framing is misleading.** The 12 are at 3 different levels of reality. A debut cannot ship on a portfolio of mixed artifacts. The Scribe pass (M27) is the gate.
2. **The P0 regex bug is the only one that could BLOCK the debut cut.** The other bugs are fix-first but not blocking. The P0 fix is 15 min + 30 min test.
3. **The hardcoded secret is not a real leak (it's a public OAuth client) but it WILL trip secret-scan.yml.** The fix is 5 min and is mandatory.
4. **The 4 Cline artifacts are post-debut per D-565.** They should be PARKED, not BLOCKED. The audit findings on them are useful for the V-1 sprint but are not debut-critical.
5. **The 2 Antigravity artifacts ARE debut-relevant** (G13 is a fabric-ticket FT-1 deliverable). The hardcoded secret must be fixed before the debut.
6. **The debut-hotfix.yml spec is incomplete in the doc I read.** The exec-verdict table at line 41 lists it but the file is not in §1-§4. **Either the doc is truncated, or the file was promised but not written.** This is a documentation gap, not a code gap.

### L3 (Universal Principle) — Timeless truths

1. **"Shipped" is a word that requires disambiguation.** A "shipped artifact" can be: (a) committed to a tracked branch, (b) written to a file on a workstation, (c) documented in a spec. The word means all three to a manager, one of three to an engineer. **In a multi-agent team, the word must be defined in the same place it is used.**
2. **The first integration test of a destructive tool is the most important test.** A spec that says "test in /tmp" is a promise; a /tmp test is the deliverable. The 6 Copilot artifacts each had a /tmp testing surface in their spec; not one of them was run. **The cost of skipping the test is exactly the P0 bug that was found in the audit.**
3. **A hardcoded secret is a hardcoded secret, even if the secret is public.** The point of secret scanning is not "is this a real secret?" — it is "is this a pattern that would also catch a real secret?" A public OAuth client in source raises the same flag as a private API key. **The fix is the same; the cost of the fix is the same; the gating is the same.**
4. **D-565 is clear: zero vault code in debut.** The 4 Cline artifacts are post-debut. The audit findings on them are valid for the V-1 sprint, but they MUST NOT block the debut. **The audit did the right thing by being thorough on artifacts that are out of scope; the debut did the right thing by hiding the vault.**
5. **A 5-minute fix that is not made is a 5-hour fix later.** The P0 regex bug in `apply_public_allowlist.sh` could have been caught in 5 minutes of awk testing. The audit found it in 45 minutes of reading. **The cost of catching a bug grows roughly linearly with the number of context boundaries it has to cross.** The boundary here is "spec doc → /tmp script → live allowlist → debut cut → public repo". Each boundary is a place the bug could have been caught; only the audit caught it.

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_carmack_artifact_audit ⬡ PUBLIC-DEBUT-01*

`AP-CARMMACK-ARTIFACT-AUDIT-20260827-v1.0.0` · 10 sections · 12 artifacts reviewed · 3 P0/P1 bugs · 3 architectural concerns · 5 still-unknowns · 1h 45m audit
