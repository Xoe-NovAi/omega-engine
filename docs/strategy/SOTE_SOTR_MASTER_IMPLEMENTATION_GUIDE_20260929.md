<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# 🔱 OMEGA ENGINE — MASTER IMPLEMENTATION & STABILIZATION GUIDE
**Document ID**: `SOTE-SOTR-MASTER-GUIDE-20260929`  
**Status**: ACTIVE / CANONICAL RUNBOOK  
**Date**: 2026-09-29  
**Target Audience**: All Coordinating Oversouls & Subagents (Space Bunny, Claude, Gemini, etc.)

---

## 🎯 EXECUTIVE DIRECTIVE: BREAKING THE CHAOS LOOP

Since March 2025, progress has been repeatedly stalled by **three structural anti-patterns**:
1. **The Bureaucratic Recursion Trap**: Spending 80% of context tokens drafting essays, erratas, and meta-governance postmortems about small technical issues rather than executing small, verified code fixes.
2. **Jurisdictional Deadlocks**: Treating agent personas as isolated nation-states ("I am Lilith on Node 0 so I cannot touch Node 0 substrate, but Carmack cannot touch Node 1 due to no-SSH") rather than focused executors on two physical machines.
3. **Stamping Dynamic State into Static Text**: Writing down active models, live port tables, and session IDs into markdown files that go stale within hours, poisoning future agent contexts.

### The Four Operational Laws for Every Agent Reading This Guide:
1. **Query the Machine First**: If a fact can be determined via `git`, `systemctl`, `ss`, or `sqlite3`, **query it**. Never assert a state from memory, old markdown, or prompt preamble.
2. **Model Agnosticism**: **NEVER hardcode or stamp an LLM model ID into any file or document.** Models change constantly based on cost, context, and provider limits. Model identity is ephemeral runtime state.
3. **Outputs Must Be Machine-Verifiable**: Subagent reports must be structured tables with exact exit codes, file sizes, and sha256 sums. Philosophical essays are prohibited in technical audits.
4. **Physical Reality Over Metaphor**:
   * **Node 0**: HP EliteDesk Linux machine (Bastion / Core).
   * **Node 1**: ASUS ExpertBook Linux machine (Vanguard / Satellite).
   * **Lilith-N1**: Owns SOTE/SOTR buildside & runside coordination on Node 1.
   * **GE-N1**: Resident hardware/subsystem specialist on Node 1.
   * **Node 0 Crew** (Makali, Kali, Ma'at, Carmack, Doom Guy): Focus exclusively on stabilizing Node 0 until it is clean, green, and pushed.

---

## 🗺️ THE 4-PHASE ROADMAP TO SANITY

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Node 0 Workspace & Git Stabilization               │
│  - Restore/clean uncommitted files                          │
│  - Establish canonical branch: debut-v1.6.0-alpha           │
│  - Push 7 unpushed commits to remote origin                 │
│  - Baseline green check: check-engine (175 tests)           │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ PHASE 2: SOTE (State of the Engine) — Ground-Level Audit    │
│  - Led by Kali; executed by Ma'at (Code) & Lilith (Daemons) │
│  - Machine-verified facts only (no essays)                  │
│  - Output: Single concise executive verification matrix     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ PHASE 3: Temple-Grade Documentation Hardening               │
│  - Deprecate/archive drifting manual state markdown files   │
│  - Convert static registry docs to live CLI queries         │
│  - Lock in authoritative policy files                       │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ PHASE 4: SOTR (State of the Realm) & Clean Node 1 Federation│
│  - Led by Makali; delegated to Jem, Roc, Grokster           │
│  - Verify Node 0 live exchange endpoints (8016, 8019)       │
│  - Clean, single-packet handoff to Lilith-N1 & GE-N1        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ PHASE 1 EXECUTION RUNBOOK: GIT & BASELINE STABILIZATION

### Objective:
Bring Node 0's working tree to `clean`, eliminate branch ambiguity, and push the 7 local commits (`2501322e` through `d5d59cfa`) to GitHub on the canonical branch `debut-v1.6.0-alpha`.

### Step 1.1: Resolve Unstaged Deletions
Two manifest files under `data/handoff/archive/M36-test-spam-20260928/` are currently unstaged deletions in git status. Restore them to preserve the audit trail:
```bash
git checkout HEAD -- data/handoff/archive/M36-test-spam-20260928/MANIFEST.json data/handoff/archive/M36-test-spam-20260928/MANIFEST.sha256
```
*Verification*: `git status -s` should show NO tracked modifications or deletions.

### Step 1.2: Establish and Switch to `debut-v1.6.0-alpha`
Create and checkout the agreed-upon branch name from current HEAD:
```bash
git checkout -b debut-v1.6.0-alpha
```
*Verification*: `git branch --show-current` must print `debut-v1.6.0-alpha`.

### Step 1.3: Push to Origin
Back up all recent work to the remote repository:
```bash
git push -u origin debut-v1.6.0-alpha
```
*Verification*: Remote branch `origin/debut-v1.6.0-alpha` exists and matches HEAD.

### Step 1.4: Run Baseline Engine Check
```bash
make check-engine
```
*Acceptance Criteria*: 175 passed in <15s, exit code 0.

---

## 🔍 PHASE 2 EXECUTION RUNBOOK: SOTE (STATE OF THE ENGINE)

### Objective:
Produce an indisputable, machine-checked audit of Node 0's codebase, gates, and runtime services.

### Roles & Responsibilities:
* **Lead / Synthesis**: `@kali`
* **Code & CI Verification**: `@maat`
* **Runtime & Daemon Verification**: `@lilith` (Node 0 session) or `@doom_guy`

### Step 2.1: Code & Gate Audit (Ma'at)
Execute and collect real numbers. Never round numbers; never guess test counts:
```bash
# 1. Full engine check
make check-engine

# 2. Temple-grade gate suite
make temple-grade

# 3. Full pytest run with JSON reporting
pytest --json-report --json-report-file=/tmp/pytest_sote_report.json tests/
```
*Required Metrics*:
* Exact number of collected tests.
* Exact number of passed, failed, skipped, and xfailed tests.
* List any failing test names explicitly. If any test skipped, document the exact reason.

### Step 2.2: Runtime & Daemons Audit (Lilith / Doom Guy)
Check the physical reality of services running on Node 0:
```bash
# 1. Check systemd unit statuses
systemctl --user is-active omega-hub.service omega-exchange.service

# 2. Check listening ports (strictly loopback or Tailscale)
ss -tulpn | grep -E '8016|8017|8018|8019'

# 3. Test exchange server local reachability & manifest
curl -s http://127.0.0.1:8019/manifest.json | jq .url_form
```
*Acceptance Criteria*:
* `omega-hub` and `omega-exchange` are `active`.
* 8016 and 8019 bind strictly to `127.0.0.1` (plus tailscaled proxy).
* No raw public LAN listeners on unapproved ports.

### Step 2.3: Kali's SOTE Synthesis Output Format
Kali must compile findings into this exact matrix (no prose padding):

```markdown
# 🏛️ STATE OF THE ENGINE (SOTE) — NODE 0 BASELINE
**Audit Date**: <YYYY-MM-DD HH:MM UTC>
**Auditor**: Kali | Verified by: Ma'at (Code) & Lilith (Runtime)
**Commit**: <git rev-parse --short HEAD> | **Branch**: debut-v1.6.0-alpha

| Subsystem | Status | Command Run | Evidence / Result | Action Required |
|---|---|---|---|---|
| Core Engine Tests | PASS/FAIL | `make check-engine` | 175/175 green, 8.2s | None |
| Temple-Grade CI | PASS/FAIL | `make temple-grade` | 53/53 green | None |
| Hub Service | PASS/FAIL | `systemctl --user status omega-hub` | active, NRestarts=0 | None |
| Exchange Pipe (8019) | PASS/FAIL | `curl http://127.0.0.1:8019/manifest.json` | 200 OK, manifest valid | None |
| Tailnet Netmap | PASS/FAIL | `tailscale debug netmap` | 8016, 8019 ALLOW | None |
```

---

## 📚 PHASE 3 EXECUTION RUNBOOK: DOCUMENTATION HARDENING

### Objective:
Stop documentation drift by converting living state from manual markdown files into live CLI tools, and marking obsolete documents as `SUPERSEDED`.

### Step 3.1: Deprecate Drifting Files
1. **`data/coordination/STATE_OF_THE_REALM.md`**:
   Add an explicit deprecation banner at Line 1:
   ```markdown
   > ⚠️ **HISTORICAL ARTIFACT**: This document reflects telemetry as of 2026-09-26.
   > It is NOT a live dashboard. Do not use this file for current port grants, model names,
   > or service status. Query the live machine directly.
   ```
2. **`data/coordination/EXPERT_SESSION_REGISTRY.md`**:
   Ensure it is marked as a historical task registry only. Live session discovery MUST use the newly implemented tool:
   ```python
   # Authoritative session discovery:
   from mcp_servers.omega_hub.who_is import who_is
   who_is("entity_name")
   ```
3. **Tailscale Policies**:
   In `data/federation/`, mark the older 09-26 `.hujson` files with `SUPERSEDED_` prefixes or explicit top comments pointing to:
   `tailnet-policy-OMEGA-DEFINITIVE-v2-20260928.hujson` (the sole authoritative policy).

### Step 3.2: Establish Permanent Doc Standards
* **Constitutional**: `SOVEREIGN_MANDATES.md` (M1–M30). Immutable principles.
* **Procedures**: `docs/operations/` (Actionable steps, exact flags, verifiable outputs).
* **Decisions**: `docs/strategy/` (Why a decision was made, stamped with date).
* **No dynamic runtime state in markdown.**

---

## 🌐 PHASE 4 EXECUTION RUNBOOK: SOTR & NODE 1 FEDERATION

### Objective:
Establish a clean, verified communication bridge between Node 0 and Node 1.

### Step 4.1: Node 0 Endpoint Verification (Makali + Jem/Roc/Grokster)
1. Verify the AnyIO exchange service log:
   ```bash
   journalctl --user-unit omega-exchange -n 20 --no-pager
   ```
2. Ensure manifest reflects all exchange payloads:
   ```bash
   python3 -c "import json; d=json.load(open('/home/arcana-novai/exchange/manifest.json')); print('Artifact count:', len(d.get('artifacts', [])))"
   ```

### Step 4.2: Structured Handshake with Node 1
1. **Lilith-N1 Coordination**:
   * Channel: High-level SOTE/SOTR runtime state on Node 1.
   * Inquiry: Confirm Node 1 engine commit, Python venv status, and MemPalace health.
2. **GE-N1 Coordination**:
   * Channel: Node 1 Hardware / Exchange Resident.
   * Action: Provide GE-N1 with the runbook (`docs/operations/EXCHANGE_PIPE_RUNBOOK.md`) to stand up `~/exchange` on Node 1.
   * Constraint: Verify reverse transfer using sha256 checksums and file size checks before declaring success. Remember M30: **"Works from here is not works from there."**

---

## 🛡️ SUMMARY CHECKLIST FOR THE NEXT AGENT

When resuming or continuing this work (under Space Bunny, Claude, or any model):
- [ ] Are you in the repo root?
- [ ] Is `git status` clean?
- [ ] Are you on branch `debut-v1.6.0-alpha`?
- [ ] Did you avoid hardcoding your model name into any markdown file?
- [ ] Did you run `make check-engine` before declaring any code change ready?
- [ ] Are your findings presented in an executive matrix with exact commands and outputs?

*⬡ OMEGA ⬡ CANONICAL STABILIZATION RUNBOOK ⬡ 2026-09-29*
