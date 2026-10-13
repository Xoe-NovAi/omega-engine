Everything below comes from my external review of the public repo: the README, ANNOUNCEMENT, QUICKSTART, the v1.6.0a0 release page, PR/release snippets surfaced by search, and arXiv:2606.22528. I did not read `src/`, `tests/`, `config/` or most of `docs/`. Per M23, an agent that finds a claim here contradicted by the repo reports the discrepancy and does not "fix" it to match this document. I couldn't make tool calls, so I wrote it inline. Copy it to something like `docs/strategy/DEBUT_POLISH_DIRECTIVE_20261013.md`.

---

# DEBUT POLISH DIRECTIVE: Omega Engine v1.6.0-alpha

**Author:** external advisor review (Claude) for the Architect (Xoe-NovAi)
**Date:** 2026-10-13
**Audience:** all OpenCode agents working on `Xoe-NovAi/omega-engine`
**Decision ID:** *none assigned. Do not invent a D-number (see `CONSTRAINTS.md` provenance). The Architect assigns one if this is ratified.*
**Goal:** make the public landing experience (README, install path, release, docs, repo metadata) accurate, verifiable and credible for a debut targeted at Wed/Thu 14–15 Oct 2026.

## 0. Ground rules for executing agents

| Rule | Meaning here |
|---|---|
| **M23** | Do not synthesize results. If a command or page can't be run or fetched, report `[TOOL-CHAIN-COLLAPSE]` and stop that task. |
| **M24** | All Python via project `.venv`. No `--break-system-packages`. |
| **M28** | Nothing auto-deleted. File moves use `git mv`, are logged in `PIVOT_LOG.md`, and are recoverable. Deletions need a human act. |
| **M13** | No "green" claim without the actual `make temple-grade` exit code attached. |
| **M2** | No Stack content (tarot, pantheons, esoteric material) in `src/omega/`. |
| **Human voice** | The Architect writes the README intro, the "How this was built" paragraph, and all launch posts. Agents leave marked placeholders (`<!-- ARCHITECT: ... -->`) and must not write these in the Architect's voice. |
| **Evidence tags** | Every finding below is tagged `[SEEN]` (observed directly on the live page), `[SNIPPET]` (from a search-index snippet that may be stale) or `[INFERRED]`. Re-verify `[SNIPPET]` and `[INFERRED]` before acting. |

## 1. Priority map

| Tier | Meaning | Deadline |
|---|---|---|
| **P0** | Public inaccuracy, broken install, or exposure | Before any announcement |
| **P1** | Strong credibility and onboarding gains | Before or on launch day |
| **P2** | Follow-through | Weeks 1–2 |

## 2. P0 tasks

### P0-1 Install path integrity

**Problems**
- README Option A downloads from `releases/download/v1.6.0-alpha/…`. That release page returns 404 and the live tag is `v1.6.0a0` `[SEEN]`. An earlier release published 10 Oct (by github-actions) appears to have been replaced `[SNIPPET]`.
- Wheel filename differs by document: `the_omega_engine-1.6.0a0-py3-none-any.whl` (README) vs `omega_engine-1.6.0a0-py3-none-any.whl` (release page) `[SEEN]`.
- README says `pip install the-omega-engine` is pending. Keep that wording until the package is actually live on PyPI.

**Actions**
1. List the actual release assets for `v1.6.0a0` and record their exact filenames.
2. Make README, ANNOUNCEMENT_v1.6.0-alpha.md and QUICKSTART.md use the same tag and filename (feeds P1-1).
3. Reduce the README to **one** recommended install path (source via `./scripts/install.sh`), with the wheel as a clearly labelled alternative.

**Acceptance:** on a clean VM or container (no repo checkout, no prior `.venv`), a person following only the README reaches a working `omega talk "hello"` with no 404s and no undocumented steps. Attach the full terminal transcript.

### P0-2 Exposure scrub (Tailscale and infrastructure identifiers)

**Problem:** a PR body contains a Tailscale IP, an `omega-hub` MagicDNS hostname and the tailnet name (PR #6 text lists a Tailscale IP and a `ts.net` MagicDNS name for the hub, with a verified MCP handshake over it) `[SNIPPET]`. Similar strings may exist in `docs/federation/` and the ACL policy file `ACL_POLICY_20260922.hujson`.

**Actions**
1. Grep the working tree **and** git history for: `ts.net`, `tail[0-9a-f]{6}`, `100\.[0-9]+\.[0-9]+\.[0-9]+`, `tskey-`, personal emails, usernames, absolute home paths, `/media/` mount paths, and hostnames of N0/N1.
2. Replace working-tree occurrences with placeholders (`<TAILNET>.ts.net`, `100.x.y.z`).
3. List PR/issue/release bodies containing hits. **The Architect edits those by hand** (agents cannot and should not).
4. If any auth key or token appears anywhere in history, stop and report immediately. Rotation is a human decision.
5. Verify `ACL_POLICY_*.hujson` is deny-by-default and that the hub requires authentication on any non-loopback path.

**Acceptance:** zero grep hits in the tree. A written list of PR/history locations for the Architect. A one-paragraph statement of the current hub bind and auth posture, supported by config values (`OMEGA_MCP_HOST=127.0.0.1`, `OMEGA_MCP_PORT=8016`, transport settings).

### P0-3 Claim accuracy (README, ANNOUNCEMENT, release body, QUICKSTART)

Each row is a claim to verify against the repo, then correct the *text* (not the evidence).

| # | Current claim | Why it's at risk | Required wording standard |
|---|---|---|---|
| 1 | "`make temple-grade` with 53 reproducible gates" / "53/53 gates exit 0" | The debut PR itself says 53/53 is the dashboard adversarial self-test, a prerequisite, not the temple-grade verdict, so the number can't be misread (D-627) `[SNIPPET]` | State what 53/53 measures, and separately state the temple-grade exit code. |
| 2 | "30 Architectural Mandates enforced continuously by automated suites" | An earlier release note says 26 mechanically verified, 4 untested (M4, M17, M18, M19) `[SNIPPET]` | "26 of 30 mandates are mechanically checked; 4 are policy-only." Use current numbers from `make check-mandate-compliance`. |
| 3 | "100% constraint survival across compactions" | The paper reports its own mitigation (Constraint Pinning) restoring violations to 0% in its benchmark. Omega's 100% needs Omega's own evidence. | Keep only if P1-5's benchmark produces it. Otherwise: "constraint-pinning design with a reproducible benchmark." |
| 4 | "destroys up to 83% of operational constraints (arXiv:2606.22528)" | The abstract reports 30% violations after compaction, up to 59% for some models, and 38% when the constraint is dropped | Find 83% in the paper body with a section citation, or replace with the abstract's figures. |
| 5 | "REUSE v3.3 compliance ✅ Green" (release table) | The same release lists 107 files of REUSE/SPDX debt `[SEEN]` | "REUSE: partial, 107 files outstanding." |
| 6 | "Sovereign search (SSP-V2, 4-tier) ✅" | `tests/verify_sovereign_search.py` was reverted unexecuted pending an isolated-env run `[SNIPPET]` | Run the verification. If it can't pass, mark "implemented, verification pending." |
| 7 | QUICKSTART: "Cloud providers are never called unless local inference fails." README: "Task → Most Capable Model," routing to frontier models | Contradiction at the heart of the sovereignty story. Sovereignty spec v2.0 describes the Synergy Model: cloud for reasoning/synthesis, local for embeddings, privacy and background work. | One consistent statement of the **default** behavior (read the actual routing default from `config/providers.yaml` and the router config), then describe the opt-in behavior. |
| 8 | `arcana_novai` presented as a shipped IWAD | The Architect states the ANAi WAD is planned, not shipped | Label "in development" or remove from README. Keep the architecture description. |
| 9 | "Zero Telemetry: audited and enforced" | Probably true, since M8 has a check | Link the check (`make check-m8-zero-telemetry`) so the claim is verifiable. |
| 10 | Release date 2026-10-12 | GitHub shows the release published 13 Oct `[SEEN]` | Use the real date. |

**Acceptance:** each row has either a corrected line plus the evidence command and its output, or a note that the claim was verified as-is.

### P0-4 Consistency fixes

| Item | Conflict | Resolution rule |
|---|---|---|
| MCP endpoint | README: `http://127.0.0.1:8016/mcp`. ANNOUNCEMENT and release: `/sse` `[SEEN]` | Document both transports once: Streamable HTTP at `/mcp`, legacy SSE at `/sse`. Show the recommended client config per client. |
| Entity count | README says 12 in prose, 14 in the diagram and roster. The soul audit shows 14 agents, 12 with souls, with a consolidation plan. | One number in README, explained in a footnote with a link. |
| Minimum RAM / OS | README 8 GB min and Ubuntu 22.04+. QUICKSTART 4 GB min and 24.04+ `[SEEN]` | Test the real minimum on the target, then align both documents. |
| Version naming | An older README snapshot shows 1.6.1-alpha; the engine is 1.6.0a0; the hub reports v1.28.1 | Add a short "Versions" note (engine vs hub). |
| Foundation and hours | An older README credited "the Xoe-NovAi Foundation" and ~8,000 hours. The Architect states ~10,000 hours. | Remove "Foundation" unless it's a real legal entity. Hours figure is the Architect's to state. |

### P0-5 Hub code health

19 pre-existing F821/F824 lint hits in `mcp_servers` were noted as follow-up debt `[SNIPPET]`.

**Actions:** run `make lint`. For each F821 (undefined name), decide: real runtime bug, missing import, or false positive (string annotation). Fix real ones, annotate false positives with justification.

**Acceptance:** `make lint` clean for `mcp_servers/`, or each remaining hit documented with a reason. No `# noqa` added without an explanatory comment.

### P0-6 Fresh-clone gate behavior

An earlier README snapshot says M13 requires a Codex less than 24 hours old, refreshed by `make codex` `[SNIPPET]`.

**Actions:** on a clean clone, run `make temple-grade` immediately, then again after simulating a Codex older than 24 hours.

**Acceptance:** documented outcome for both. If the second fails, either document `make codex` as the first step in CONTRIBUTING or fix the gate's staleness behavior. Do not leave this for contributors to discover.

### P0-7 Threat model in SECURITY.md

Add a short section answering exactly these questions with actual config values. Do not guess.

1. Default bind address and any authentication on `/mcp` and `/sse`.
2. How handoff-bus content is treated: data vs. instructions. Can a poisoned handoff steer another agent? What sanitization exists?
3. What Kill / Escalate / Approve / Throttle control planes gate, and their defaults.
4. How `vault_ops` enforces local-only handling.
5. Which secret scanners run (gitleaks, GitGuardian) and where.
6. Known limits (see P2-3 on independent review).

## 3. P1 tasks

### P1-1 Single source of truth for facts (stops doc drift)

**Root cause:** agents regenerate docs and numbers drift. One PR already had to correct model claims, test counts and provider counts in public docs.

**Create `docs/FACTS.yaml`** (fill every `FILL` from the repo itself, never from this document):
```yaml
release_tag: v1.6.0a0
wheel_filename: FILL        # exact asset name from the release
hub:
  host: 127.0.0.1
  port: 8016
  mcp_path: /mcp
  sse_path: /sse
default_local_model: FILL   # e.g. Qwen3-1.7B-Q6_K, from config/models.yaml
embedding:
  model: FILL               # Qwen3-Embedding-0.6B per README
  dimensions: 1024
iwad_default_entities: FILL
mandates:
  total: FILL
  mechanically_verified: FILL
  policy_only: [FILL]
tests:
  engine_contract_passing: FILL
  engine_contract_skipped: FILL
temple_grade:
  exit_code_on_fresh_clone: FILL
  prerequisite_selftest: "FILL/FILL"   # per D-627, label as prerequisite
requirements:
  ram_min_gb: FILL
  python: "3.12+"
  os: FILL
```

**Create `scripts/check_doc_facts.py`** (venv, stdlib + PyYAML) and a Make target `check-doc-facts` that:
- Loads `FACTS.yaml`.
- Scans `README.md`, `QUICKSTART.md`, `ANNOUNCEMENT_*.md`, and `docs/**/*.md` for the facts above and fails on any mismatch.
- Has a **forbidden-phrase list**, failing unless an evidence link sits next to it: `100% constraint survival`, `83%`, `53/53 gates` (without the prerequisite qualifier), `never called unless local`, `REUSE.*Green`.
- Fails loudly on parse errors (M23).

**Wire into CI.** Whatever gate-count or temple-grade chain changes result, take the count from the tooling output, not from typed text.

**Acceptance:** introducing a deliberate mismatch (e.g. wrong port in README) makes `make check-doc-facts` exit non-zero; reverting it exits 0.

### P1-2 README restructure

**Target order** (the Architect writes the intro, the provenance paragraph, and the vision line; agents build everything else):

| # | Section | Notes |
|---|---|---|
| 1 | Title, one-line tagline, 3–4 badges | Keep Python, License, Zero Telemetry, CI. Drop insider badges ("Local-First & Synergy," "Embedding SSOT"). |
| 2 | Hero demo (GIF or short video) | See P1-6 |
| 3 | `<!-- ARCHITECT: why this exists, 4–6 sentences -->` | Placeholder only |
| 4 | Install + first run | Exactly one recommended path (P0-1) |
| 5 | What it does | Three bullets, in this order: cross-client hub (OpenCode, Cline, Cursor, Codex, Gemini CLI) with zero-token coordination; compaction-safe constraints with reproducible benchmark (P1-5); local-first with opt-in cloud (accurate per P0-3 #7) |
| 6 | Status: honest alpha | Works / known gaps table with numbers from `FACTS.yaml` |
| 7 | `<!-- ARCHITECT: how this was built -->` | Placeholder. Skeleton below. |
| 8 | Architecture | One diagram. Keep the DOOM.EXE/WAD analogy, which is distinctive. |
| 9 | Links | QUICKSTART, build-a-WAD guide, hub setup, SECURITY, CONTRIBUTING, docs index |

**Tagline candidates** (Architect picks): "One local MCP server that gives all your AI coding tools shared memory and handoffs." / "A local-first runtime where your AI coding agents share persistent memory, handoffs and constraints that survive context compaction."

**"How this was built" skeleton** (the Architect fills and edits):
```
<!-- ARCHITECT:
- Built entirely by AI agents under my direction (~<HOURS> hours of orchestration); I'm not a programmer.
- What I did: architecture, mandates, acceptance criteria, review.
- What verifies it: <temple-grade result>, <test counts>, <scanners>.
- What hasn't had independent human review: <security-critical paths>.
-->
```

**Also:**
- Reduce the roster table to 4–5 entities with one-line roles, linking the full roster in docs.
- Merge the duplicate Quick Start sections.
- Move the vision statement ("AI not excluded") to the bottom or to `docs/vision.md`.
- Remove the LangChain/AutoGPT comparison. Replace with an honest "How this differs" table against real neighbours. The Architect decides which; likely candidates are an MCP memory server, Letta and mem0. Verify each competitor's current capabilities before writing any claim about it.
- Define each in-house term on first use or link a glossary: IWAD/PWAD, entity, A2A seats, SOTE, M-numbers, D-numbers, control planes.

**Acceptance:** README renders cleanly, passes `check-doc-facts`, all links return 200, and the first screen contains tagline, demo and install.

### P1-3 Root directory declutter

The root has ~30 entries. Target root: `README.md`, `QUICKSTART.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`, `CREDITS.md`, `pyproject.toml`, `Makefile`, `AGENTS.md`, `opencode.json`, plus essential config/license files.

**Candidates to move into `docs/`:** `MANDATES_CONDENSED.md`, `SOVEREIGN_MANDATES.md`, `ORACLE_STACK.md`, `OMEGA_ENGINE.md`, `OMEGA_CODEX.md`.

**Constraints:**
- `MANDATES_CONDENSED.md`, `OMEGA_CODEX.md` and others may be loaded by scripts, hooks or tests (`scripts/load_constraints.py`, `make codex`). Before any move, grep for every reference and update loaders.
- `CONSTRAINTS.md` (under `docs/governance/`) is compaction-immune and loaded from disk at hydration. Do not move it.
- Use `git mv`, log in `PIVOT_LOG.md`, and run the full gate afterward.
- `AGENTS.md` and `.opencode/` stay. They are a feature (mention in README).

**Acceptance:** `make temple-grade` exit code unchanged vs. before the moves; no broken links (`make check-broken-imports`, plus a link check); PIVOT_LOG entry present.

### P1-4 `docs/` as a front door

1. Create `docs/README.md` with a "Start here" list of at most five links: quickstart, hub setup, build-a-WAD, compaction benchmark, security.
2. Move coordination artifacts into `docs/internal/` (same `git mv`/PIVOT_LOG rules). Candidates: council syntheses, SOTE weekly reports, relay logs, entity-state coordination docs, decision-heavy working notes. Public docs currently include items such as Makali/Grokster/Researcher synthesis and dispatch documents.
3. Add `docs/GLOSSARY.md` with one-line definitions of internal terms.
4. Add a short `docs/internal/README.md` explaining that these are working records kept public for transparency.
5. Check `PUBLIC_ALLOWLIST.txt` and any allowlist tooling so the move doesn't re-filter or break the public cut.

**Acceptance:** a first-time visitor clicking "docs" lands on an index that makes sense without knowing any internal term.

### P1-5 Compaction benchmark

**Goal:** back the headline claim with a reproducible, honest number.

**Deliverable:** `make bench-compaction` that:
1. Runs long-horizon scenarios in the spirit of the paper's ConstraintRot (deterministic tool-call grading, with a policy that must survive compaction), using a local model so anyone can reproduce it.
2. Compares: (a) no pinning, (b) Omega's constraint-pinning path (`CONSTRAINTS.md` reload at hydration).
3. Prints a results table plus the raw logs location.
4. Covers the two limits the literature flags: implicit constraints can't be pinned, and operator impersonation in recent context can defeat pinning. Report results for both, even if Omega does not fully pass.

**Honesty rule:** publish whatever the numbers are. If Omega does not reach 100%, change the README to the measured result.

### P1-6 Demo assets

| Asset | Spec |
|---|---|
| Hero demo | 60–90 s: an agent in OpenCode writes a structured handoff; an agent in Cline picks it up and verifies. Use the real hub on `127.0.0.1:8016`. Do not fake output. |
| Screenshots | `omega list-entities`; the hub with two clients connected |
| Social preview | Custom 1280×640 image |

The Architect records or approves the final demo. Agents prepare the script and the exact commands.

### P1-7 Hardware table

Measure and publish (tool outputs attached, not estimated): tokens/s, idle and loaded RAM, and cold-start time for the default model on the reference node (Ryzen 7 5700U, 16 GB). Include the exact command, model file and quantization. Do not publish any number that wasn't measured on that run.

### P1-8 Repository metadata

- **About:** one-line description matching the new tagline, plus docs link.
- **Topics:** `mcp`, `fastmcp`, `local-llm`, `llama-cpp`, `multi-agent`, `agent-memory`, `ai-agents`, `self-hosted`.
- **Issue templates:** bug report requiring OS, Python version, install path used, `omega backends` output, `git rev-parse HEAD`. Feature request. Question.
- **Pull request template:** requires `make temple-grade` exit code.
- **GitHub Discussions:** enable. Create pinned "Welcome: what are you building?" and "Install problems."
- **`good first issue`:** 8–10 genuinely small issues with clear acceptance criteria (doc fixes, link checks, glossary entries, REUSE headers for named files).
- Confirm release assets include checksums.

### P1-9 Build-a-WAD guide

The "swap the world, keep the engine" idea is the project's most distinctive pitch, so make it doable.

1. Write `docs/build-a-wad.md`: a 30-minute path to a working minimal WAD (one entity, `soul.yaml`, `ethics.yaml`, active in `config/omega.yaml` via `omega.entity.active_iwad`).
2. Base it on the existing persona-WAD work (`PERSONA_WAD_ARCHITECTURE.md` defines a portable PWAD manifest schema, directory structure, loader integration and packaging rules) and the `requires_engine` field.
3. Add `config/wads/example_minimal/` (or the correct location after reading the loader) as a tested example.
4. Add a test that loads it, so the guide can't rot.
5. **M2 firewall:** keep all example content under `config/wads/`, none under `src/omega/`.

**Acceptance:** a fresh contributor builds and runs the example WAD following only the guide.

## 4. P2 tasks (weeks 1–2)

| ID | Task | Notes |
|---|---|---|
| P2-1 | Publish to PyPI (`the-omega-engine`), then update `FACTS.yaml` and docs | README says a pending publisher exists. Verify live before changing any claim. |
| P2-2 | Federation spotlight doc | Federation (zero-relay Tailscale, `federation_status`/`federation_diagnose` tools) appears in specs and runbooks but not on the landing page. Write a short public-safe overview *after* P0-2 is complete. |
| P2-3 | Independent human security review | The Architect arranges. Scope: hub auth, handoff bus, `vault_ops`, control planes. Record the result in SECURITY.md. All code is agent-written, so independent review matters more here. |
| P2-4 | Ship `arcana_novai` as its own WAD | When ready, with its own README. This keeps esoteric content out of the main page. |
| P2-5 | Discoverability | Unrelated "Omega Engine" 3D repos and other "Omega MCP Server" projects share the name. Keep tagline and topics keyword-rich. The Architect checks PyPI naming and trademark considerations with a qualified person. |
| P2-6 | REUSE/SPDX debt (107 files) | Work down the list; update `FACTS.yaml` as it shrinks. |
| P2-7 | Close the 4 untested mandates (M4, M17, M18, M19) | Add mechanical checks or document why they stay policy-only. |

## 5. Launch operations (Architect-owned; agents prepare material only)

| When | Action |
|---|---|
| Today (Tue 13 Oct) | P0 tasks; clean-VM install test |
| Wed/Thu ~8–10 am US Eastern | Show HN, posted by the Architect. Cross-post to r/LocalLLaMA with a hardware/local-first angle and to MCP communities, each tailored. |
| First 6 hours | Architect answers comments. Agents triage install-failure reports into issues with reproduction steps. |
| Week 1 | Tag `v1.6.1a0` with community-reported fixes (check version naming per P0-4) |
| Week 2 | Benchmark write-up; PyPI |

**Show HN title (draft):** `Show HN: Omega Engine – one local MCP server that gives Cline, Cursor and Codex shared persistent agents`

**First-comment skeleton** (Architect finalizes in their own voice):
```
<!-- ARCHITECT
Who I am and why I built it (one or two sentences).
What it does today (hub, handoffs, constraints surviving compaction).
Honest alpha: <known gaps, numbers from FACTS.yaml>.
How it was built: <AI-agent authorship statement>.
Looking for: install failures, security review of the handoff bus,
feedback on whether the entity/WAD model is useful or over-engineered.
-->
```
Do not solicit votes or stars. Ask for honest feedback instead.

**Prepared answers for likely hard questions** (draft with evidence, Architect approves):
1. How is this different from Letta, mem0 or an MCP memory server? *(verify current capabilities first)*
2. Why named entities rather than generic roles? What does `soul.yaml` change in behavior?
3. Where is the evidence for constraint survival? *(P1-5)*
4. Can a poisoned handoff steer another agent? *(P0-7)*
5. What does the default local model do well, and when does routing go to cloud? *(P0-3 #7, P1-7)*
6. Is the mandate/gate system a burden on contributors? *(P0-6, CONTRIBUTING)*

## 6. Reporting format back to the Architect

One table, one row per task, no prose padding:

| Task | Status (PASS / FAIL / BLOCKED / N/A) | Evidence (command + exit code + path to output) | Discrepancies found | Needs Architect |
|---|---|---|---|---|

Rules: no PASS without attached evidence. A `[SNIPPET]` or `[INFERRED]` item the repo contradicts is reported as a discrepancy against this document. Do not edit the repo to match this document.

## 7. Appendix: discrepancy register (from the review)

| # | Discrepancy | Locations | Task |
|---|---|---|---|
| 1 | Wheel URL tag `v1.6.0-alpha` vs live tag `v1.6.0a0` | README | P0-1 |
| 2 | Wheel filename `the_omega_engine…` vs `omega_engine…` | README vs release | P0-1 |
| 3 | `/mcp` vs `/sse` | README vs ANNOUNCEMENT/release | P0-4 |
| 4 | REUSE green vs 107-file debt | release table vs known gaps | P0-3 |
| 5 | 12 vs 14 entities | README | P0-4 |
| 6 | Min RAM 8 vs 4 GB; Ubuntu 22.04+ vs 24.04+ | README vs QUICKSTART | P0-4 |
| 7 | Release date 12 vs 13 Oct | ANNOUNCEMENT vs GitHub | P0-3 |
| 8 | "Cloud only on failure" vs "task→most capable model" | QUICKSTART vs README | P0-3 |
| 9 | "83%" not found in the paper abstract | README | P0-3 |
| 10 | "53 gates" vs D-627 clarification | README/ANNOUNCEMENT vs PR | P0-3 |
| 11 | "30 mandates enforced" vs 26/30 | README vs earlier release note | P0-3 |
| 12 | `arcana_novai` presented as shipped | README | P0-3 |
| 13 | Tailnet identifiers in public PR text | PR body, possibly docs | P0-2 |
| 14 | 19 F821/F824 hits in `mcp_servers` | lint | P0-5 |
| 15 | Sovereign search test reverted unexecuted | tests | P0-3 |
| 16 | Version names 1.6.0a0 / 1.6.1-alpha / hub v1.28.1 | multiple | P0-4 |

---

*End of directive. Items tagged `[SNIPPET]` come from search-index excerpts of PR bodies and release notes and may be out of date. Verify against the live repo before acting.*

A note on my previous message: a few of my inline citation anchors there pointed at the wrong snippets. The facts themselves match the sources, and I've re-anchored them correctly in this document.
