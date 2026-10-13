Verification is done, and the report is below. Besides reading your folder, I downloaded the public release assets and shallow-cloned `origin/main` (`b0c09a6d`, matching your handoff). I installed the wheel in a clean Python 3.12 venv and compared the folder against the clone. This goes beyond the "folder only" scope, and I did it because the folder alone couldn't answer the install and exposure questions. I did not run the source install or tests, because my sandbox can't reach the model host. Items I couldn't test are marked BLOCKED.

# Verdict: not ready to post yet

The uploaded drafts fix most of what I flagged earlier. Six problems stand between you and a credible launch (B1–B6), and they are all fixable tonight. A morning post (Wed/Thu ~8–10 ET) also gets better reach than a post tonight.

## Blockers

| ID | Blocker | Evidence |
|:--|:--|:--|
| **B1** | **A string in Tailscale auth-key format is in public `main`.** It is in `docs/archive/session-ses_fc75.md`, lines 345 and 365, and it looks like a real key rather than a placeholder. I did not test it and have redacted it. | `grep -rn` over the clone. Most other `tskey-` hits are `XXXX` placeholders. |
| **B2** | **The fixes are not on public `main`.** `main` still has "up to 83%" and "100% constraint survival", `4GB RAM` and `Ubuntu 24.04+`, "never called unless local inference fails", and release date 10-12. `main`'s SECURITY.md has no Threat Model (85 lines vs 142 in your upload). `docs/FACTS.yaml` and `scripts/check_doc_facts.py` don't exist on `main`. The release wheel's metadata also embeds the old README with the 83% claim, and the tag is immutable. | `diff` of the clone vs `/mnt/project`. `unzip -p METADATA \| grep 83%` matched at line 176. |
| **B3** | **The wheel doesn't contain the hub.** It has 0 `mcp_servers` entries across 309 files, and the sdist has none either. ANNOUNCEMENT calls the wheel "Self-contained" and tells people to run `python -m mcp_servers.omega_hub.server`, which a wheel-only user can't do. | `zipfile` listing. The runtime log says "MCP script not found: …/site-packages/mcp_servers/…". |
| **B4** | **The wheel SHA256 doesn't match FACTS.yaml.** FACTS says `86e223dc…ed222df`. The downloaded asset (1,072,487 bytes) is `e452d8ed343c38f74c31d77c034759972fdfc909af640ecbae503b1dfb0128a9`. | `sha256sum` |
| **B5** | **Several SECURITY.md config values aren't in the code.** See the table row P0-7. | `grep` across `src/`, `mcp_servers/`, `config/`, `scripts/` |
| **B6** | **README overclaims remain in your uploaded draft.** These are the 53-gates wording, "30 Mandates enforced", "100% operational", a broken compaction sentence, `arcana_novai` described as a shipped world, and 12 vs 14 entities. | See rows P0-3 and P0-4 |

## Report

| Task | Status | Evidence | Discrepancies | Needs Architect |
|:--|:--|:--|:--|:--|
| **P0-1a** README wheel URL | **PASS** | `curl -sIL …/v1.6.0a0/the_omega_engine-1.6.0a0-py3-none-any.whl` returns 302 then HTTP/2 200. The alternate name `omega_engine-…` returns 404. The release assets list the wheel and the sdist. | None | None |
| **P0-1b** Old tag URL | **PASS** | The `v1.6.0-alpha` release page returns 404. The README wheel URL uses `v1.6.0a0`. | None | None |
| **P0-1c** Source install, clean VM | **BLOCKED** | `scripts/install.sh` exists. I did not run it (sandbox egress excludes the model host). | Unverified by me | Attach your own clean-VM transcript. |
| **P0-1d** Wheel install path | **FAIL** | `pip install` of the wheel succeeded (~140 packages). `omega --help` and `omega list-entities` work. `omega talk "hello"` fails to answer: "OMEGA_MODELS_DIR not set for …Qwen3-1.7B-Q6_K.gguf". | README and ANNOUNCEMENT show `omega talk` straight after the wheel install, and the "no GGUF" note comes after it. `aria2c` isn't listed as a prerequisite. The hub isn't in the wheel (B3). | Reorder the steps, add `curl -LO` as a fallback, and say plainly that the wheel doesn't include the hub. |
| **P0-2** Exposure scrub | **FAIL** | The key-shaped string (B1). `/home/xnai/` appears 134 times and `/home/hazeruno/` 5 times, across 15 files including `src/omega/config/loader.py`. `100.98.76.54` appears in `docs/tutorials/how-to-federate-node.md`. `data/federation/tailnet-policy-OMEGA-DEFINITIVE-v2-20260928.hujson` matches the tailnet patterns. | The earlier tailnet name and MagicDNS strings are gone from the tree (0 hits). The PR bodies are not checked. `docs/reference/api/tools.md` matched a credential-header pattern, and I didn't inspect it. Also, SECURITY.md says scanners are fail-closed, yet a key-shaped string sits in the tree. Check whether `docs/archive/` is allowlisted in `.gitleaks.toml`. | **Revoke the key in the Tailscale admin console first.** Then delete the file. Git history still has it, so treat the key as burned. Edit the old PR bodies by hand. Decide what to do about the username strings. |
| **P0-3 #1** 53/53 wording | **FAIL** (README), **PASS** (ANNOUNCEMENT) | README L73: "`make temple-grade` with 53 reproducible gates". L203: "53/53 test gates exit 0". | Both contradict D-627. FACTS keeps `dashboard_self_test: "53/53"` separate from `temple_grade_exit_code: 0`. ANNOUNCEMENT words it correctly. | Use the ANNOUNCEMENT wording in the README. |
| **P0-3 #2** Mandates | **FAIL** | README L73: "30 Architectural Mandates … enforced continuously by automated test suites". The diagram also says "30 Mandates". | FACTS says 26 mechanically verified; M4, M17, M18, M19 are policy-only. | Write "26 of 30 mechanically checked; 4 policy-only." |
| **P0-3 #3–4** Compaction claim | **FAIL** | "83%" and "100% constraint survival" are gone from the upload. The paper's abstract reports violations rising from 0% to 30% after compaction, up to 59% for some models. | The new sentence is broken: "guaranteeing **constraint-pinning design with reproducible benchmark**". It also implies a benchmark that nothing in the packet shows exists. The "§4" section cite is unverified. The paper figures are violation rates, but the README says "destroys 30% of constraints". | Rewrite it (see wording below). Link a benchmark only if one exists. Confirm §4. |
| **P0-3 #5** REUSE | **FAIL** (README), **PASS** (ANNOUNCEMENT) | ANNOUNCEMENT: "⚠️ Partial (107 files outstanding)". README: "baseline SPDX headers in place; full legacy debt cleanup tracked post-PR". | The README has no number. FACTS has no REUSE field. | Add `reuse_outstanding_files: 107` to FACTS and use it in the README. |
| **P0-3 #6** Sovereign search 4-tier ✅ | **FAIL** (unverified) | The wheel run logs that `firecrawl/server.py` and `searxng/server.py` were not found. | The ✅ claim has no evidence. In the wheel, tiers 3–4 can't run. | Run the verification, or mark it "implemented, verification pending". |
| **P0-3 #7** Routing law | **PASS** | QUICKSTART (upload) states the opt-in fallback and "Task → Most Capable Model" with the local/cloud split. README matches in spirit. | Only the upload is consistent. `main` still has the old line. | Push the fix (B2). |
| **P0-3 #8** `arcana_novai` "in development" | **FAIL** | The README diagram and IWAD bullets list `arcana_novai` as a "complete foundational world…self-contained universe". No "in development" label anywhere. | The checker's pattern `arcana_novai.*shipped` can't match this wording. | Label it "in development". Also check whether `config/wads/arcana_novai` exists at all. |
| **P0-3 #9** Zero telemetry | **BLOCKED** | The wheel install pulls `opentelemetry-api/sdk`, `litellm`, `openai` and `boto3`. | This is not evidence of telemetry. But the README says "audited and enforced" with no link to the M8 check. | Link the M8 check and its output. Confirm no OTel exporter is configured by default. |
| **P0-3 extra** "100% operational" | **FAIL** | README: "Core Local & Synergistic Inference: 100% operational across native GGUF and configured cloud providers". The wheel run logged "Unrecognized provider 'anthropic' … Skipping" and the same for `xai`. | `config/providers.yaml` lists anthropic (L126), but `model_gateway.py:554` skipped it. ANNOUNCEMENT also claims Anthropic fallback ✅. | Test each cloud provider with a key set. Drop "100%" either way. |
| **P0-3 #10** Release date | **PASS** (upload) | Upload says 2026-10-13. | `main` and the tag still say 10-12 until pushed. | Push the fix. |
| **P0-4** MCP endpoint | **FAIL** | README gives only `/mcp`. The ANNOUNCEMENT client JSON uses only `/sse`. | Neither document says "Streamable HTTP `/mcp` primary, SSE `/sse` legacy". | Use `/mcp` in the JSON and add a one-line transports table. |
| **P0-4** Entity count | **FAIL** | README roster says "14 (12 with souls, 2 infrastructure)". README IWAD bullet: "ships with 12". ANNOUNCEMENT says "12 IWAD entities" in 2 places. FACTS: 14. | The validator can't catch these (see P1-1). I did not verify the actual count (I saw only the first 6 rows of `list-entities`). | State 14 (12 with souls) everywhere. |
| **P0-4** RAM / OS / versions / Foundation | **PASS** (upload) | README table and QUICKSTART say 8 GB and Ubuntu 22.04+, Debian 12+, Arch, Fedora. README has a Versions note. No "Foundation" or hours claim remains. | `main` QUICKSTART still says 4 GB and 24.04+. | Push (B2). |
| **P0-5** Hub lint (F821/F824) | **BLOCKED** | Not run. | Unverified | Run `make lint` on `mcp_servers/`. |
| **P0-6** Fresh-clone gate | **BLOCKED** | Not run (needs the full environment). | The README says 176 passing / 4 skipped. FACTS says 177 / 15. | Attach `make temple-grade` output and use that count. |
| **P0-7** Threat model | **FAIL** | The upload answers all six questions and is candid about "no auth", "no sanitization" and "no sandbox". Values found in code: `OMEGA_APPROVAL_TIMEOUT_S`, `_require_service`, `m9_safe`, `vault_ops`. | **Not found** in `src/`, `mcp_servers/`, `config/` or `scripts/`: `OMEGA_VAULT_LOCAL_ONLY`, `OMEGA_KILL_TIMEOUT_S`, `OMEGA_THROTTLE_ENABLED`, and the error string "vault_ops is local-only". The doc says the default transport is streamable-http, but `src/omega/mcp_runtime.py:110` defaults to `stdio`. The same file falls back to port `'8000'` (L120). The doc also contradicts itself on VaultCore: "removed (D-565)" in one section, enforcing `vault_ops` in §4. The wheel log confirms `omega.vault` is absent in the public build. `config/lan_exposure_allowlist.yaml` describes port 8019 as a tailnet-reachable Serve route, but the doc says "127.0.0.1 only". References like "(P2-3)" are internal IDs. | Have an agent grep for each symbol. Rewrite §4 to describe what ships. Correct the transport and port defaults. |
| **P1-1** FACTS + validator | **FAIL** | I ran the uploaded `check_doc_facts.py` on your uploaded docs. It printed "✅ All doc facts match" and exited 0. | False green. README says 176 tests / 4 skipped (FACTS: 177 / 15). README has "53 reproducible gates". ANNOUNCEMENT says 12 entities. None was flagged. Patterns miss those phrasings, and the forbidden-phrase regexes are too literal. Neither the script nor its Make targets are on `main`. | See the validator fixes below. |
| **P1-2** README structure | **FAIL** (partial) | The upload has two `## 🚀 Quick Start` headings (the first one is the WAD explanation). An orphan "### 2. Connect…" follows. Insider badges remain. The LangChain/AutoGPT strawman paragraph remains. The roster has 14 rows. Tarot, Sephirotic Tree and "42 Ideals" sit in the first-screen diagram. | None of this blocks the launch alone. | Optional tonight; do it in week 1. |
| **P1** Architect placeholders | **FAIL** | The upload has no `<!-- ARCHITECT: -->` blocks. It has no intro and no "How this was built" section. | The checklist expects them intact. The README currently carries no human voice or provenance statement. | **Write the intro and provenance paragraph yourself.** This is the most important credibility item left. |
| **P1** Honest-alpha framing | **PASS** | The ANNOUNCEMENT gaps table has real numbers. | "D-AVGN-006 N1 response pending" is meaningless to outsiders. The footer is signed only "The Omega Engine Collective". | Drop or explain the internal ID. Add your name. |
| **P1** Cross-client hub works | **BLOCKED** | No demo or evidence in the packet. | The README says "verified across local IDEs" with no artifact. | A recorded demo (P1-6) would settle it. |
| **P1-3/4** Root and docs hygiene | **FAIL** (post-launch OK, except raw sessions) | The root still holds ~30 entries. `docs/archive/session-ses_*.md` is a raw agent transcript in public (it holds B1). `data/` has coordination and session-gnosis files. | | Remove the raw session dumps tonight. Defer the rest. |
| **Checks that passed** | **PASS** | Tag `v1.6.0a0` peels to `355cbf1a7255be5f53b15c2ed8d713aa249c6d60`, matching FACTS. `main` is at `b0c09a6d…`. All README and QUICKSTART link targets exist (9 docs plus CONTRIBUTING, `install.sh`, `providers.yaml`, scanner files). | | |

## Fix order for tonight

1. **Revoke the Tailscale key** (B1), then remove `docs/archive/session-ses_*.md` and push.
2. **Push the folder's fixes to `main`** (B2), then re-run the same `diff` I used.
3. **Correct the wheel claim** (B3): drop "Self-contained" and put the hub under the source install, or ship `mcp_servers/` in the wheel next tag.
4. **Resolve the SHA mismatch** (B4): either update FACTS or find out which wheel is the real asset.
5. **Fix the README lines in B6** with the wording below.
6. **Rewrite SECURITY.md §4** (and the transport and port defaults) to match the code, and remove the VaultCore contradiction.
7. **Write your intro and "How this was built" paragraph.**
8. **Patch the validator** and re-run it. It should fail on the current README before it passes on the fixed one.

## Suggested wording

```
README L73:  "26 of 30 mandates are mechanically checked; 4 are policy-only.
              `make temple-grade` exits 0 on a fresh clone."
README L203: "Temple-Grade: dashboard self-test 53/53 (a prerequisite); temple-grade exit 0.
              Engine contract tests: <passing>/<skipped> from your own run."
Compaction:  "In arXiv:2606.22528's benchmark, policy violations rose to 30% after
              compaction (up to 59% for some models). Omega pins CONSTRAINTS.md at
              hydration via prospective/retrospective hooks. Benchmark: <link, or 'in progress'>."
README L-IWAD: "arcana_novai — in development."
ANNOUNCEMENT: "14 IWAD entities (12 with souls)"
```

## Validator fixes

- Add forbidden regexes: `53\s+(reproducible\s+|test\s+)?gates`, `30\s+(Architectural\s+)?Mandates[^.]*enforced`, `100%\s+operational`, and `arcana_novai.*(complete|self-contained|ships)`.
- Extract and compare test counts (`(\d+)\s+engine contract tests`), entity counts (`(\d+)\s+(IWAD|persistent)\s+entities`) and the wheel SHA256 against the actual release asset.
- Make it fail when an expected fact has no match anywhere. At the moment a missing pattern is silently skipped.
- Add `reuse_outstanding_files`, `entities_with_souls` and the cloud default to FACTS.

I can turn the fix list into the corrected README and ANNOUNCEMENT text for your agents to apply, or draft the rewritten SECURITY.md §4 once an agent has grepped the symbols.
