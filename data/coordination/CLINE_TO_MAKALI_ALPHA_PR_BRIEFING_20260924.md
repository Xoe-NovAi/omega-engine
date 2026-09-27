# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ CLINE → MAKALI · ALPHA PR BRIEFING

**AP Token**: `AP-CLINE-MAKALI-ALPHA-PR-20260924`
**From**: Cline CLI (deepseek-v4.1-flash) · channel `cline` · entity `omega-engine`
**To**: Makali (Overseer, Node 0) — cc: Architect, Kali, Jem, Carmack
**Branch**: `release/debut-v1.6.0` @ `75bde939` (+ 73 staged files, **not committed**)
**Status**: staged and verified. Awaiting your sign-off on §9 before commit/push.

> **Rule of this document**: every claim carries a reproduction command.
> **The command wins over the document.** Re-run before quoting.

---

## §0 — SIXTY-SECOND READ

**PR #3 is red, and the documented reason was wrong.** The handoff blamed
"2 flakes" (`test_m34_atomic`, `test_first_breath`) plus a missing `ruff`.
The real cause is bigger and simpler:

> **~20 project files that committed code depends on were never `git add`ed.**

They exist on every dev box (so everything looks green locally) and exist in
**no clone** (so CI fails at import/collection). The worst one is fatal on its
own:

```
src/omega/governance/budget_guard.py     (committed)  → imports omega.research.types
src/omega/research/                      (UNTRACKED)  → does not exist in a clone
src/omega/governance/__init__.py         (committed)  → eagerly imports budget_guard
```

Because `governance/__init__.py` imports it eagerly, **every** `omega.*` import
dies — including `mcp_servers/omega_hub/server.py`. The Hub cannot boot from a
fresh clone. Pytest cannot collect. That is PR #3's `Run tests` failure.

**What I did this session**

1. Fixed 6 correctness defects (§3) — all previously green-by-accident locally.
2. Found and fixed the untracked-source blocker (§2) — the reason CI is red.
3. Restored 3 failing mandate gates (M10, M13, M26) in the PR tree.
4. Staged **73 audited files** (§4). Nothing committed, nothing pushed.
5. Rebuilt the real PR tree (`HEAD` + staged only) and verified it (§1).

**Result: the PR tree is green** — `2244 tests, 0 failures`, mandates `23/28 ·
0 failed`, doc gate exit 0. Getting there required staging **74 files**, 62 of
them never-before-tracked. Details and repro commands in §1–§4.

**Do NOT take my local green run at face value.** The local working tree is
138-entries dirty and contains ~50 files of *other* agents' in-flight work. My
first "2244 tests OK" was measured on that tree and proved nothing about the
PR. So I built the PR tree in a separate worktree and tested that instead.
That distinction is the whole point of §1.

---
## §1 — VERIFIED FACT BASE

Method: `git worktree add --detach /tmp/pr-treeN HEAD` + `git apply <staged.patch>`.
That reproduces the PR surface with **none** of the other agents' uncommitted work.

```bash
# Build the PR tree and test it (the only honest way to test a PR)
git diff --cached > /tmp/staged.patch
git worktree add --detach /tmp/pr-tree HEAD
cd /tmp/pr-tree && git apply /tmp/staged.patch
ln -sfn <main-repo>/.venv .venv
PYTHONPATH=/tmp/pr-tree/src:/tmp/pr-tree .venv/bin/python -m pytest \
    -q -m 'not integration' tests/ -p no:randomly --maxfail=9999
```

| Surface | Command | Result |
|---|---|---|
| **PR tree · tests** | see above | **`OK` — 2244 tests, 0 failures** (27 skipped, 8 xfail) · EXIT=0 |
| PR tree · mandates | `make check-mandates` | **23/28 · 0 failed** (82.1%) |
| PR tree · doc gate | `make doc-llm-validate` | exit 0 |
| Local dirty tree · tests | same pytest, main repo | 2244 OK (49 skipped, 9 xfail) |
| Local · mandates | `make check-mandates` | 23/28 · 0 failed |
| Local · lint | `make lint` | complete |
| Local · soul | `make soul-validate` | compliant |
| Local · temple | `make temple-grade` | exit 0 |
| Local · secrets | `make gate-secrets` | **PASSED** (was structurally unpassable — §3.6) |
| Local · M35 scanner | `python scripts/check_secrets.py --allowlist-lint` / `--staged` | 0 violations |

**How the PR tree got from red to green during this session** (the trajectory is
the evidence that §2 was the real cause):

| PR-tree build | Result | Interpretation |
|---|---|---|
| HEAD alone | **collection ERROR** | `ModuleNotFoundError: omega.research` — engine unimportable |
| + core fixes | 0 tests collected | `curate_packs`, then `platform_adapters`, then `entity_roc_racoon` |
| + untracked deps staged | 2244 tests · **24 errors · 2 failures** | errors = 24 × `entity_roc_racoon`; failures = soul-evidence + mandates |
| + schemas/configs/codex/agents (final) | **`OK` · 2244 tests · 0 failures** | mandates 23/28 · 0 failed · EXIT=0 |

Both intermediate failures were real and are now both closed:
1. `tests/contract/test_soul_lessons.py::...resolvable_evidence` — a promoted
   lesson cited `.opencode/skills/git-secret-scrub/SKILL.md` as evidence; the
   file was untracked (§2 #10).
2. `tests/test_mandate_ci_checks.py::test_check_mandates_aggregate_passes` —
   M10 + M13 + M26 failing in the PR tree; all three closed (§2 #6/#7/#8, §7 M13).

⚠️ **One caveat on the `OK`.** `tests/test_contract_m21.py::test_resourceguard_blocks_on_capacity`
is a **wall-clock capacity assertion**: it failed in earlier builds and passed
here. It passes 3/3 in isolation on an idle box and fails under load. Treat the
green as *currently* green, and fix the assertion (§7 #4) rather than trusting it.

> **Do not repeat my own mistake**: I first ran the PR-tree suite *concurrently*
> with the `gate-secrets` git-history scan and got a bogus failure. Serialise
> heavy gates and the suite.

---

## §2 — THE RELEASE BLOCKER (untracked dependencies)

This is the single most important finding in this briefing. It is a **class**
of defect, not one file. Nothing in the repo's own gates catches it, because
all of them run on a dev box where the files exist.

**How to detect it (run this; it is the check we were missing):**

```bash
# 1. Any file that committed code imports but git does not track?
for m in omega.research omega_youtube_research; do
  git grep -l "$m" HEAD -- '*.py' | sed 's|^HEAD:||'
done
# → 5 source files + 4 test files import packages that are untracked
```

**The inventory (all fixed by staging):**

| # | Untracked artifact | Committed thing that needs it | Symptom if absent |
|---|---|---|---|
| 1 | `src/omega/research/` (7 py + sandboxes) | `governance/budget_guard.py`, `cli/oracle_cli.py`, `cli/fleet_status_tui.py`, `oracle/planner/hybrid_orchestrator.py` | **fatal** — engine + Hub unimportable |
| 2 | `src/omega_youtube_research/` (17 py) | `cli/youtube_cli.py`, `workers/youtube_worker.py` | CLI import error |
| 3 | `src/omega/archive/cas.py` | `tests/test_e2e_sovereign_sieve.py` | test collection error |
| 4 | `config/wads/arcana_novai/plugins/entity_roc_racoon.py` | `tests/test_entity_roc_racoon.py` | **24 test errors** |
| 5 | `.opencode/skills/context-packer/{packer,platform_adapters,curate_packs}.py` + `packer-config.yaml` | `tests/contract/test_context_packer*.py` | collection error |
| 6 | `schemas/llm_doc_frontmatter.json` (+ `.license`) | `make doc-llm-validate` | **M26** mandate fail |
| 7 | `configs/token_budgets.yaml` | `scripts/validate_llm_docs.py` | **M26** mandate fail |
| 8 | `.opencode/agents/*.md` (13) | M10 Fleet Integrity | **M10** mandate fail |
| 9 | `.opencode/rules/*.md` (6) | `AGENTS.md` — **11 references** | dangling onboarding docs |
| 10 | `.opencode/skills/git-secret-scrub/SKILL.md` | `data/entities/kali/approved_lessons.yaml` evidence | test failure ("unresolvable evidence") |

**Why #10 is the most instructive.** `.gitignore:283` *already* had the
negation `!.opencode/skills/git-secret-scrub/SKILL.md`, with a comment saying
it was added so the soul-contract test would pass "in CI". Somebody did the
gitignore work and then never `git add`ed the file. The rule was there; the
file was not. The test kept failing and nobody re-read the comment.

**Why #8/#9 were invisible.** `.gitignore:270` is the blanket `*.md` rule.
AGENTS.md (tracked, public!) instructs every newcomer to read
`.opencode/rules/*.md` — 11 times — and M10 requires `.opencode/agents/`.
Both were swallowed. That is the documented `*.md` trap (`.clinerules` §TRAPS #1)
still live for `.opencode/`.

**Blast-radius lesson:** two of these (#6, #7) are not code dependencies but
*gate* dependencies. A gate that reads an untracked config is a gate that
passes locally and fails in CI forever. When you add a gate, ask: **is every
input to this gate tracked?**

---
## §3 — DEFECTS FIXED THIS SESSION

All six were **green locally and broken in reality**, or silently lying.

### 3.1 `dispatch.yaml` was truncated mid-entity
`config/wads/_omega_default/entities/dispatch.yaml` had the last 10 lines of the
`omega_federation` entity deleted (`domains`, `slot`, `model`, `task_tool_type`,
`owned_files`…). HEAD still had them. Restored to HEAD; the dispatch-registry
contract test passes.
```bash
python3 -c "import yaml;d=yaml.safe_load(open('config/wads/_omega_default/entities/dispatch.yaml'));\
print(sorted([x for x in d['entities'] if x['name']=='omega_federation'][0].keys()))"
# → capabilities, domains, mode, model, name, owned_files, purpose, role, slot, task_tool_type
```

### 3.2 M36 cross-validator handoff was dead code
The 92→66 tool consolidation removed `hivemind_submit_handoff`, but
`m36_recursive_probe._dispatch_cross_validator_via_hivemind` still called it.
Result: `ImportError` → silent fallback → packet ids with a `cv_` prefix that
break the documented `ho_` contract.
```bash
python3 -m pytest -q tests/test_a5_m36_soft_verifier.py   # now green
```

### 3.3 …and the replacement was unusable too
Two traps stacked on top of each other:
* `@mcp.tool()` wraps the callable, so calling the unified tool returns a
  **`CallToolResult`**, not the JSON string the caller `json.loads()`ed.
* `_require_service()` raises `RuntimeError` when Hub services are not up.
Fixed by unwrapping (`getattr(fn, "__wrapped__", fn)`) and routing
`RuntimeError` to the honest file-based dispatch. Fallback packet ids are now
canonical `ho_<12hex>`.

### 3.4 The Hub's backward-compat shim was a lie
`mcp_servers/omega_hub/server.py::__getattr__` advertised **29** legacy tool
names. **11 of them resolved to nothing** — 7 handoff, 3 oracle-debug,
`delegate_task` — and raised `AttributeError` on access. Rebuilt as real
adapters bound to their unified replacements, verified against **both** HEAD's
`tools.py` (legacy tools present) and the curated one (removed).
```bash
python3 -c "import mcp_servers.omega_hub.server as s;\
print(callable(s.hivemind_submit_handoff), callable(s.delegate_task))"  # True True
```

### 3.5 Hivemind failure alerting was silently dead
`src/omega/coordination/watchdog.py` and `src/omega/workers/freshness_checker.py`
both did `from omega_hub import hivemind_submit_handoff` — **module `omega_hub`
does not exist** (`importlib.util.find_spec('omega_hub') is None`). Every failure
notification had been raising into a broad `except` and logging a warning.
`freshness_checker` additionally passed an unsupported `metadata=` kwarg.
Routed both to the canonical path with `packet_id` validation.

### 3.6 Four different versions, one of them not ours
| Surface | Before | After |
|---|---|---|
| `pyproject.toml` | `1.2.0` | `1.6.0-alpha.1` |
| `omega.__version__` | `1.2.0` (hardcoded 2nd copy) | `1.6.0-alpha.1` |
| Hub `/health` | `2.2.0` (hardcoded) | `1.6.0-alpha.1` |
| MCP `serverInfo` | **`1.30.0`** | `1.6.0-alpha.1` |

The `serverInfo` value was **the mcp SDK's own version**, leaking as ours.
FastMCP 1.30.0 takes no `version=` kwarg, so the field fell through to the
library default. Also fixed a subtler bug: an editable install freezes its
metadata at install time, so `importlib.metadata.version()` reports a *stale*
version after any pyproject bump — the checkout now wins over installed metadata.
```bash
python3 -c "import omega, mcp_servers.omega_hub.server as s;\
print(omega.__version__, s.mcp._mcp_server.version)"   # 1.6.0-alpha.1 1.6.0-alpha.1
```

### 3.7 `make gate-secrets` could never pass
The regex section was a bare `any match ⇒ FAIL=1` loop with **no mechanism to
record a disposition** — while gitleaks passed the *same* 35 findings through
`.gitleaksignore`, and the PEM section had its own baseline. So the gate failed
on history the project had already audited, and was structurally unpassable.
Replaced with `scripts/check_secret_history.py` + `.secret-history-baseline.toml`:
every distinct token is hashed (sha256, no secret material stored) and must carry
a disposition. **6 tokens total: 2 `fc-*` (revoked, owner-confirmed) + 4 `GOCSPX`
(public OAuth cert fingerprints).**

The gate also now enforces something new: **a token baselined `revoked` must
never reappear in the working tree.** That closes the loop between "we rotated
it" and "we pasted it into a tracked file again".
```bash
python3 scripts/check_secret_history.py   # exit 0
```

---
## §4 — STAGED INVENTORY (74 files · 62 new · 12 modified)

```bash
git diff --cached --stat | tail -1
# 74 files changed, 14838 insertions(+), 95 deletions(-)
git diff --cached --name-status | awk '{print $1}' | sort | uniq -c
#  62 A   12 M
```

**Modified (12)** — the six defect fixes plus restoration work:
`Makefile`, `pyproject.toml`, `.gitignore`, `OMEGA_CODEX.md`,
`src/omega/__init__.py`, `src/omega/oracle/m36_recursive_probe.py`,
`src/omega/coordination/watchdog.py`, `src/omega/workers/freshness_checker.py`,
`mcp_servers/omega_hub/server.py`, `docs/strategy/PUBLIC_ALLOWLIST.txt`,
`data/entities/makali/soul.yaml`, `tests/test_a2_m33_probe.py`.

**New (62)** — almost all of it is §2's untracked-dependency repair:
* `src/omega/research/**` (9) · `src/omega_youtube_research/**` (17) · `src/omega/archive/cas.py`
* `.opencode/agents/*.md` (13) · `.opencode/rules/*.md` (6) · context-packer (4) · git-secret-scrub (1)
* `schemas/**` (4) · `configs/token_budgets.yaml` · `config/wads/arcana_novai/plugins/entity_roc_racoon.py`
* New gates/tests: `scripts/check_secret_history.py`, `.secret-history-baseline.toml`,
  `tests/contracts/test_{legacy_tool_adapters,version_ssot,secret_history_gate}.py`

**New contract tests added: 51** (26 legacy-adapter · 7 version-SSOT · 18 secret-gate).
Each one pins a defect that shipped precisely because nothing tested it.

**Hygiene applied while staging** (not optional — REUSE v3.3 scans tracked files):
* SPDX headers added to **17** files that lacked them (all of `omega_youtube_research/`).
* `*.backup.*` / `*.backup` confirmed already ignored (the `.clinerules` §6 trap).
* Scans run on every new file: **no secrets**, **no `/home/arcana-novai` hardcoded paths**.
* Verified none of the new files are gitignored (`git check-ignore`).

---

## §5 — DECISIONS APPLIED (with your earlier rulings)

| # | Decision | Applied |
|---|---|---|
| 1 | **`data/secrets-public.toml` SHIPS** | Yes. M35 §28.3 mandates it be committed/versioned. I verified the `GOCSPX-` value is published **verbatim** upstream in `NoeFabris/opencode-antigravity-auth` @ `5d229bf` — a public OAuth native-app client (RFC 8252 §8), not a private credential. Now listed in `PUBLIC_ALLOWLIST.txt` with the citation. |
| 2 | **Version = `1.6.0-alpha.1`** | Yes, across all four surfaces (§3.6). |
| 3 | **Unauthenticated tailnet MCP OK for Alpha** | Recorded. No code change. Please state it in the PR body so it reads as a decision, not an oversight. |
| 4 | **No history rewrite** for the 2 revoked `fc-*` tokens | Yes — hash baseline instead. |

### ⚠️ One decision I made that needs your explicit sign-off

To clear **M10 Fleet Integrity** I un-ignored and staged `.opencode/agents/*.md`
(13 files) and `.opencode/rules/*.md` (6 files), amending `.gitignore`.

**Why I judged it correct:** `AGENTS.md` — *already tracked and public* — points
newcomers at `.opencode/rules/*.md` **11 times**; M10 requires
`.opencode/agents/`; **41 `data/entities/*/soul.yaml` are already tracked**, so
persona data is already public in this repo; and I scanned both trees for
secrets/paths and found none.

**Why you should still review it:** this *expands the public surface* with 19
previously-private files. It is staged, so it is fully reversible before push:
```bash
git restore --staged .opencode/agents .opencode/rules .gitignore
```
If you would rather not publish them, the alternative is to relax M10's check
for the public repo — but then AGENTS.md keeps pointing at 11 nonexistent files.
**This is the only item in §4 I would not push without your word.**

---

## §6 — FEDERATION: THE HANDOFF PREMISE WAS INVERTED

This matters because the plan was built on it.

```bash
tailscale status
# 100.123.51.67  n0  n0.tail51f14a.ts.net  linux   <- THIS machine, runs the Hub
# 100.89.40.17   n1  tagged-devices         linux   <- Node 1
```

* **The "Node 1 export at `100.123.51.67`" is Node 0's own address.** N0 exports
  nothing (`exportfs -v` empty) and has no NFS mounts (`findmnt -t nfs,nfs4` empty).
* **N1's ports 22 and 2049 are filtered** from N0. Only **8016** is open. The
  NFS/SSH cross-node handoff **does not exist**; do not plan around it.
* The Hub listens on `127.0.0.1:8016` + the tailnet IP, and is fronted by
  `tailscale serve` over **HTTPS**. Plain HTTP returns
  `400 Client sent an HTTP request to an HTTPS server` — that is why N1 "saw no peer".
* `omega-hub.tail51f14a.ts.net` is **NXDOMAIN**. That stale name is the entire
  source of the "Tailscale ACL" confusion. The correct host is
  **`n0.tail51f14a.ts.net`**.

**Working cross-node verification (from N0):**
```bash
curl -s https://n0.tail51f14a.ts.net:8016/health
# {"status":"healthy",...,"version":"1.6.0-alpha.1"}
curl -s -X POST https://n0.tail51f14a.ts.net:8016/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"n1","version":"0"}}}'
# HTTP 200 · serverInfo {"name":"Omega Core Hub","version":"<engine version>"}
```

⚠️ **That handshake succeeded with no credentials.** I searched the Hub for any
token/Bearer/auth mechanism and found **none** (`OMEGA_HUB_TOKEN`, `Authorization`,
`Bearer`, `api_key` — zero matches; no `mcp.run(auth=…)`). So the trust boundary
is the tailnet itself, and **"authenticated tool-call verification" cannot be
completed as scoped** — there is nothing to authenticate with. Acceptable for
Alpha per your ruling; it must be an explicit, documented posture, not a belief
that auth exists.

---
## §7 — OPEN QUEUE (ordered by risk)

### P0 — blocks a clean PR
| # | Item | Owner | Note |
|---|---|---|---|
| 1 | **Sign off (or revert) the `.opencode` publication** (§5 ⚠️) | Makali/Architect | staged, reversible |
| 2 | **Commit + push**, then watch PR CI | whoever holds the remote | I staged; I did **not** commit |

### P1 — known red/risk, decide before public
| # | Item | Evidence |
|---|---|---|
| 3 | **M13 stale-codex time-bomb** | I ran `make codex`; `OMEGA_CODEX.md` is fresh and staged, so M13 passes *now*. It fails again in **<24h** with zero code change. This is a **freshness property masquerading as a compliance gate**. Either auto-refresh it in CI or make M13 a warning. Pending policy decision. |
| 4 | **`test_resourceguard_blocks_on_capacity` is load-sensitive** | passes 3/3 idle, fails under load. A wall-clock capacity assertion in CI will redden randomly. Fix the assertion, don't chase the flake. |
| 5 | **MCP has no auth at all** | §6. Acceptable for Alpha by your ruling — document it. |
| 6 | **C6 attestation is still draft-only** | the existing "attestation" is human-readable text, not a cryptographic signature. **Public material must not claim signed release trust.** |
| 7 | **`data/secrets-public.toml` holds a live-looking secret** | Correct per M35 and verified public, but scanners and humans will flag it. Consider a loud header (`PUBLIC CLIENT SECRET — SAFE TO PUBLISH`) so the PR reader is not alarmed. |

### P2 — known, not blocking
| # | Item |
|---|---|
| 8 | **Meter arithmetic defect**: `Total 28 \| Passed 23 \| Failed 0 \| Untested 4` — 23+0+4 = **27**. One row is never bucketed. Fix `scripts/check_mandate_compliance.py` before quoting the meter publicly. |
| 9 | **`check_secrets.py` full scan: 7 violations, all inert** — AWS's canonical documentation example key (`AKIA…` + `EXAMPLE`, deliberately masked here: quoting it literally trips the M35 scanner) plus self-labelled test fixtures. `--allowlist-lint` is clean. Two of them already annotate themselves as FPs in prose. |
| 10 | **WAD contract is not production-ready** (unchanged): scanner ignores root `entities.yaml`; some scaffold entities lack the `entity` envelope; PWAD override concatenates personality instead of replacing; `requires_engine` has no semver enforcement; adapter whitelist is narrow. Decide: Alpha-blocker or documented limitation. I did **not** touch it. |
| 11 | **`config/domains/engineering/{metadata,AFFINITY_PRESETS}.yaml` and `PRINCIPLES/principle_001.yaml` are Markdown-in-`.yaml`** — they have never parsed as YAML. They are tracked and clean (pre-existing prototype modules). Misleading extension; either convert or rename. |
| 12 | **46 `operations` entries surfaced on the node** — 138 dirty entries total, ~50 files of other agents' in-flight work (`tools.py` −968 lines, `m34_registry.py`, memory/search stack, entity gnosis). **Not mine, not staged.** Whoever owns them must reconcile before or after this PR — but they must not be swept in with `git add -A`. |

---

## §8 — TRAPS DISCOVERED (new; add to the roster)

1. **Untracked-dependency trap (the big one).** Committed code/gates can depend
   on files that are untracked-but-present. Every local gate passes; CI cannot
   even collect. **No existing gate detects this.** Candidate check:
   `git ls-files --others --exclude-standard 'src/**/*.py'` → 26 files, and grep
   committed code for imports of them.
2. **"The negation existed, the file did not."** `.gitignore:283` negated a
   path specifically so a CI test would pass, then nobody `git add`ed the file.
   Always pair a gitignore negation with `git ls-files --error-unmatch <file>`.
3. **Testing a PR on the dev tree proves nothing.** I nearly shipped "2244 tests
   OK" measured on a tree that also contained 50 files of other agents' work and
   ~20 untracked dependencies. Use `git worktree add` + `git apply <cached diff>`.
4. **`@mcp.tool()` returns `CallToolResult`, not your return value.** Call the
   `__wrapped__` coroutine when a caller needs the raw payload.
5. **`git log -G` is POSIX ERE.** `(?:…)` fails with exit 128. Plain alternation only.
6. **Editable installs freeze metadata.** `importlib.metadata.version()` reports
   the install-time version, so a pyproject bump silently changes nothing at
   runtime. Prefer the checkout's pyproject when running from source.
7. **`-x` hides the rest of the failures.** My first PR-tree run stopped at test
   321 of 2244 — I saw 1 error and thought that was all. Use `--maxfail=9999`
   when auditing, and read `.pytest_cache/v/cache/lastfailed` for the full truth.
8. **Do not run heavy gates concurrently with the suite.** `gate-secrets` does a
   full-history `git log -p`; running it alongside pytest produced a fake
test failure and cost a diagnosis cycle.
9. **`grep -cE` on a large file can silently return 0** where `grep -n` finds
   matches — I hit this and briefly drew a wrong conclusion about `tools.py`.
   When a count contradicts a listing, trust the listing and re-check.
10. **Do not quote a secret-shaped string in prose — the scanner will flag your
   own document.** My first draft of this briefing quoted AWS's canonical
   example key while *describing* it as an inert false positive, and
   `scripts/check_secrets.py --staged` failed on this file (`aws-access-key,
   critical`). Mask it (`AKIA…EXAMPLE`). A gate cannot read intent.

---

## §9 — ASKS

1. **Sign off on (or revert) §5's `.opencode` publication.** This is the only
   staged change I would not push on my own authority.
2. **Give me the word to commit + push**, or take the staging and do it yourself:
   the full path list is in §4; stage explicitly, **never `git add -A`**.
3. **Decide M13's policy** (auto-refresh in CI vs warning) — until then every
   red CI is a coin flip with zero code change.
4. **Fix or park `test_resourceguard_blocks_on_capacity`** — it is a wall-clock
   capacity assertion and will keep flaking.
5. **Tell Node 1**: hub is `https://n0.tail51f14a.ts.net:8016/mcp`, HTTPS not
   HTTP, MagicDNS host `n0` (not `omega-hub`), and **22/2049 are filtered** so the
   NFS/SSH plan is dead. Also that MCP is unauthenticated by design for Alpha.
6. **Confirm** that the ~50 files of other agents' work in this tree (§7 #12) are
   deliberately out of scope for this PR.

---

*⬡ OMEGA ⬡ CLINE ⬡ MAKALI-ALPHA-PR-BRIEFING ⬡ 2026-09-24 ⬡ deepseek-v4.1-flash ⬡*
