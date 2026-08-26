# 🔱 R_GAP_CLOSURE_SWEEP_20260826
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_gap_closure ⬡ FINAL PRE-EXECUTION SWEEP

**Mission**: Close every web-researchable open item from the remediation pre-exec review,
the Cline/Copilot setup research, and grokster's KB platforms doc. Last sweep before
remediation execution. Research only.
**Confidence tags**: 🟢 HIGH · 🟡 MEDIUM · 🔴 LOW/UNVERIFIED · **LOCAL** = requires on-machine probe/instrumented session (valid closure verdict per M23)

---

## EXECUTIVE SUMMARY

| Category | Closed (web) | Partial | Requires LOCAL action |
|---|---|---|---|
| A. Forensics residuals (5) | 3 (A1*, A2*, A5-model) | 2 (A3, A4) | gate re-probe, variant smoke, slot login try |
| B. Binary/version (3) | 3 (B6, B7-timeline, B8) | — | — |
| C. KB fills (3) | 3 (C9-arch, C10, C11) | C9-version pin | version pin via `codex --version` if needed |
| **Total** | **9 closed** | **2 partial** | **~5 short local probes** |

*A1/A2 closed to "web-verifiable best evidence"; final confirmation is a 30-second probe.

### 🔴 NEW EXECUTION-DECISION FINDING (D2)
A third-party VS Code extension author states they **validated all model IDs directly
against the Cline API** and found `anthropic/claude-*` models are **NOT available on
api.cline.bot despite being listed in Cline's own docs** — and our ready-to-paste Cline
block (R_CLINE_COPILOT_PROVIDER_SETUP §3.2) includes exactly one. **Action: drop
`anthropic/claude-sonnet-4-6` from the P1 paste block, or verify via `/api/v1/models`
first.** Source: https://marketplace.visualstudio.com/items?itemName=ltmoerdani.cline-copilot-chat 🟡 MEDIUM (single author, but claims direct validation; consistent with the client-gate pattern we probed ourselves).

---

## §A FORENSICS RESIDUALS

### A1 — Cline gate status on deepseek-v4-flash → **CLOSED-WEB (likely lifted); LOCAL confirm**
- Verdict: Evidence now indicates `deepseek/deepseek-v4-flash` works via raw API key:
  the Cline Copilot Chat BYOK extension documents "⭐ **Free model.** `deepseek/deepseek-v4-flash`
  returns 200 OK even at $0 balance" and "All model IDs validated directly against the
  Cline API", listing it in both pay-per-use (`deepseek/deepseek-v4-flash`) and ClinePass
  (`cline-pass/deepseek-v4-flash`) tiers. 🟡 MEDIUM
- Interpretation vs our Aug-22 403: either the gate lifted between Aug 22 and this
  extension's validation, or the extension benefits from a surface exemption. Cannot
  distinguish from web alone. **LOCAL**: 30-second curl re-probe with existing key settles it.
- Sources: https://marketplace.visualstudio.com/items?itemName=ltmoerdani.cline-copilot-chat ;
  https://cline.bot/models/deepseek-v4-flash ("Choose Cline (usage-billing) or ClinePass").
- KB patch: grokster KB cline entry — replace "gate blocks deepseek" with "gate status
  fluid; free tier re-confirmed by third party ~Aug 2026; probe before relying".

### A2 — Cline output cap for v4-flash → **CLOSED 🟡**
- Verdict: **context 1M / max output 384K** for `deepseek/deepseek-v4-flash` (and v4-pro),
  per the validated model table above; MiMo V2.5 = 1M/128K. Replaces our 131072 estimate.
- Residual: cross-check against authenticated `GET api.cline.bot/api/v1/models` at P1
  time (numbers may drift). LOCAL (trivial).
- KB patch: record 1M/384K with source + date.

### A3 — api.cline.bot honors reasoning_effort? → **PARTIAL → LOCAL**
- Verdict: Official Chat Completions reference documents a minimal body (`model`,
  `messages`, `stream`, `tools`) — **no `reasoning_effort` parameter documented**;
  reasoning is described as an OUTPUT property (`delta.reasoning`, `delta.reasoning_details`).
  🟢 HIGH (docs). Meanwhile Cline's own extension code passes `reasoningEffort`/
  `thinkingBudgetTokens` for DeepSeek models over its DeepSeek-direct provider (PR #10401,
  344 unit tests incl. reasoningEffort) — but that's a different upstream (api.deepseek.com),
  not proof the gateway forwards it. 🟢 HIGH (on the distinction).
- Conclusion: web cannot confirm gateway-side honoring. **LOCAL**: one smoke call per
  variant post-P1; if no behavioral delta, drop variants (dead knobs violate M18).
- Sources: https://docs.cline.bot/api/chat-completions ; https://docs.cline.bot/api/models ;
  https://github.com/cline/cline/pull/10401 .
- KB patch: note "reasoning_effort undocumented at gateway; extension uses it only for
  DeepSeek-direct path".

### A4 — github-copilot-enterprise slot accepts github.com login? → **PARTIAL (web says plausible) → LOCAL try**
- Verdict: The builtin Copilot auth plugin's own method prompts include an explicit
  deployment-type select with `GitHub.com` / `GitHub Enterprise` options (source excerpt
  in #5665), i.e., github.com login is a first-class path on BOTH copilot provider ids'
  shared auth machinery. The enterprise-path client-ID bug (#11554) was fixed Feb 2026;
  GHE device-flow failures (#3936) fixed via PR #18103. The cavanaug plugin demonstrates
  github.com tokens stored under the `github-copilot-enterprise` key working end-to-end.
  🟡 MEDIUM overall: no source states verbatim "the builtin enterprise slot accepts a
  github.com account without plugins on 1.18.x". **LOCAL**: attempt `opencode auth login`
  on the enterprise slot; fallback = cavanaug file-plugin (documented working).
- Sources: https://github.com/anomalyco/opencode/issues/5665 ; /issues/11554 ; /issues/3936 ;
  https://github.com/cavanaug/opencode-copilot-vscode .
- KB patch: two-slot multi-account pattern confirmed feasible; document local result.

### A5/U6 — AI-Credits burn characteristics → **CLOSED-WITH-MODEL 🟡 (our rate needs LOCAL instrumented session)**
- Verdict: Since June 1 2026 Copilot metering = GitHub AI Credits, $0.01/credit,
  computed from input+output+cached tokens at per-model rates; premium-request multipliers
  retired. Limits undisclosed; agentic-loop burn is the documented worst case (opencode
  #8030/#8067 synthetic-message misclassification — partially fixed; #15243 architecture
  critique). Expected-cost model for us: `(input_tokens × rate_in + output_tokens ×
  rate_out + cached × rate_cache) / $0.01` per model, using published model rates — but
  OUR loop's token profile requires one instrumented session reading the
  github.com/settings/copilot usage dashboard. LOCAL for calibration only.
- Sources: https://rottenwifi.com/github-copilots-new-limits-and-premium-ai-charges-explained-2025-2026/ ;
  https://github.com/orgs/community/discussions/189990 ; opencode issues above.
- KB patch: replace "premium requests" framing with AI-Credits model + burn caveat.

---

## §B BINARY / VERSION INTELLIGENCE

### B6 — 1.18.20→1.18.23 deltas → **CLOSED 🟢** (official release notes)
What we are frozen ON (all from https://opencode.ai/changelog + releases pages):

| Ver | Date | Execution-relevant changes |
|---|---|---|
| 1.18.20 | Aug 21 | Subagent failures surfaced w/ resumable `task_id`; retries for `finish_reason: network_error` variants; Cerebras `max_completion_tokens` preserved (no extra cap); permission requests answered during `opencode run`; xAI stream-error retries |
| 1.18.21 | Aug 21 | Continue on unknown finish_reason; Vertex multi-region Gemini REP routing |
| 1.18.22 | Aug 24 | **`textVerbosity` no longer sent to OpenAI-compatible providers that don't support it** (directly benefits our custom `cline` openai-compatible block); device-login link fixes; Go pricing msg removal |
| 1.18.23 | Aug 25 | Cloudflare AI Gateway routing fixes; parent-session-ID header fix; **TUI: GitHub auth fix for immutable OIDC subject tokens** |

- Impact assessment: **no provider-loading, variants-handling, compaction, or plugin-API
  breaking changes** in the frozen window → freeze on 1.18.23 is LOW-RISK for the
  remediation; 1.18.22's textVerbosity fix actually improves custom-provider safety. 🟢
- KB patch: record freeze rationale + table.

### B7 — V2 plugin API migration timeline → **CLOSED-WEB 🟢 (answer: no date exists)**
- Verdict: Official V2 migration doc states "**V1 plugins will not work in V2. The V2
  plugin API is still being finalized during beta**, and detailed plugin migration
  guidance will be published when it is ready." No deprecation date for V1 hook families
  on the V1 line; ecosystem projects (oh-my-openagent #6169, opencode-mem #173) confirm
  even large plugin authors are waiting with no timeline. Our V1-family hooks
  (sovereign-compaction.ts, awareness.ts, error-capture.ts, silent-stall-sensor.ts) are
  SAFE on the frozen 1.18.x line; migration is a future project gated on upstream docs.
- Sources: https://opencode.ai/v2/docs/migrate-v1 ; https://opencode.ai/v2/docs/build/plugins
  ("plugin API is beta… publish compatible updates when V2 entrypoints change") ;
  https://github.com/code-yeongyu/oh-my-openagent/issues/6169 .
- KB patch: add "V1 hooks safe through 1.18.x; V2 break is total but unscheduled — do not
  start V2 migration until official guidance publishes".

### B8 — Autoupdate disable that survives updates → **CLOSED 🟢** (carried from pre-exec review §4)
- Two independent mechanisms, both documented: env `OPENCODE_DISABLE_AUTOUPDATE=true`
  (#1793, added by thdxr) AND config key `"autoupdate": false` in GLOBAL config only —
  v2 docs state "Project-level values are ignored". Historical bug where local-config
  `autoupdate:false` was ignored (#3412) fixed via PR #3408. Belt-and-suspenders: set BOTH;
  env var survives any binary replacement by definition. Precedence question dissolved:
  they're additive mechanisms, not competing keys.

---

## §C KB RESEARCH-FIRST FILLS

### C9 — Codex CLI current state → **CLOSED-ARCH 🟢 / version pin LOCAL**
- Architecture: Rust-based CLI is THE maintained Codex CLI (TypeScript legacy). Config =
  `config.toml` (+ `CODEX_HOME` per-project), named `[profiles.NAME]` (experimental),
  top-level `sandbox_mode` + `approval_policy`, `[mcp_servers.*]` registry,
  `sandbox_workspace_write.writable_roots` escape hatch, `rules` for command prefixes.
- Sandbox model: three documented modes — `read-only`, `workspace-write` (default;
  `.git/` and `.codex/` may stay read-only inside it), `danger-full-access`; orthogonal
  `approvals_reviewer` ('user' | 'auto_review').
- AGENTS.md: native primary format, confirmed across sources incl. OpenAI docs references.
- Auth: ChatGPT OAuth or API key (API key recommended for CI).
- Version pin: prior single-source citation was rust-v0.143.0; current latest NOT pinned
  by this sweep → LOCAL `codex --version` if the KB needs the number.
- Sources: https://developers.openai.com/codex/config-basic , /codex/config-advanced ,
  /codex/security (via https://github.com/openai/codex/blob/main/docs/sandbox.md) ;
  https://www.digitalapplied.com/blog/codex-cli-rust-migration-playbook-config-changes-2026 ;
  https://www.digitalapplied.com/blog/codex-cli-deep-dive-config-profiles-sandbox-2026 .
- KB patch: replace single-source version citation with architecture summary above;
  mark version as "pin at next local session".

### C10 — Gemini CLI AGENTS.md support → **CLOSED 🟢 (conflict resolved) + 🔴 NEW D1 finding**
- Resolution: BOTH, with a default. Primary docs: `GEMINI.md` is the default context file
  (hierarchical: global `~/.gemini/GEMINI.md` → workspace/parents → JIT scans);
  AGENTS.md support exists ONLY opt-in via settings:
  `"context": {"fileName": ["AGENTS.md", "CONTEXT.md", "GEMINI.md"]}`. So "GEMINI.md-only"
  sources describe default behavior; "both" sources describe configured behavior. 🟢 HIGH
- 🔴 **D1 (new, material)**: Primary docs banner — "Unpaid tier and Google One users:
  **Gemini CLI will be replaced by Antigravity CLI on June 18th [2026]**" with transition
  blog post. Any KB guidance premised on classic Gemini CLI availability must be annotated
  for the post-transition landscape.
- Sources: https://geminicli.com/docs/cli/gemini-md/ ; https://geminicli.com/docs ;
  transition post linked therein (developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli).
- KB patch: resolve the conflicting claim exactly as above; add Antigravity-CLI transition note.

### C11 — Claude Code hooks count → **CLOSED 🟢 ("25 lifecycle hooks" claim OUTDATED)**
- Verdict: Official hooks reference currently documents ~29–31 events depending on
  version point: third-party trackers count **29 events at v2.1.207** and **31 by Aug 8
  2026** (e.g., `PostToolBatch`, `InstructionsLoaded`, `ConfigChange`, `CwdChanged`,
  `FileChanged`, `WorktreeCreate/Remove`, `TeammateIdle`, `TaskCreated/Completed`,
  `StopFailure`, `PermissionDenied`, `UserPromptExpansion`, `Elicitation*` are all
  post-2025 additions). Five handler types (`command`, `http`, `mcp_tool`, `prompt`,
  `agent`). The KB's single-source "25 lifecycle hooks" is stale — patch to "~29–31 and
  growing; verify against code.claude.com/docs/en/hooks at use time".
- Version-number claim in KB amendment: could not be confirmed/denied from this sweep's
  results without knowing which version the KB cites → treat as LOCAL pin item alongside C9.
- Sources: https://code.claude.com/docs/en/hooks ; https://code.claude.com/docs/en/hooks-guide ;
  https://clockedcode.com/blog/claude-code-hooks (29 @ v2.1.207) ;
  https://blakecrosley.com/blog/claude-code-hooks-explained (31 @ 2026-08-08).

---

## §D NEW UNKNOWNS SURFACED BY THIS SWEEP

| ID | Finding | Materiality |
|---|---|---|
| D1 | **Gemini CLI → Antigravity CLI transition for unpaid tiers (Jun 18 2026)** — classic Gemini CLI guidance ages out | KB platforms doc needs a transition banner; affects any Gemini CLI automation plans |
| D2 | **`anthropic/claude-*` reportedly NOT on api.cline.bot despite official docs listing them** (third-party direct validation) | 🔴 Changes P1 paste block: drop or verify claude-sonnet entry first |
| D3 | 1.18.22 stopped sending `textVerbosity` to non-supporting openai-compatible providers | Positive: reduces risk surface for our custom cline block; note in plan |
| D4 | ClinePass tier exists (`cline-pass/*` model ids, $9.99/mo, 2–5× rate limits) — a separate id namespace on the same endpoint | If fleet hits pay-per-use limits, ClinePass ids are the fallback; add to KB |
| D5 | Copilot PAT auth NOT supported by opencode's copilot provider (OAuth device flow only) — headless automation gap documented in adjacent ecosystems | Relevant to V-1 vault design: Copilot accounts need interactive device-flow bootstrap per account |

---

## FINAL IRREDUCIBLE LOCAL-PROBE LIST

Everything below cannot be closed from the web; each is short and scheduled:

| # | Probe | Settles | Est. |
|---|---|---|---|
| L1 | curl `api.cline.bot/api/v1/chat/completions` w/ existing key, model `deepseek/deepseek-v4-flash` | A1 gate status | 30s |
| L2 | authenticated `GET api.cline.bot/api/v1/models` → dump caps table | A2 cross-check + D2 (claude-* present?) + U3 model list | 1 min |
| L3 | one variant smoke call (`reasoningEffort: high` vs none) on v4-flash | A3 gateway honoring | 2 min |
| L4 | `opencode auth login` on github-copilot-enterprise slot w/ github.com account | A4 second-slot feasibility | 5 min |
| L5 | one instrumented agentic session + usage-dashboard read | A5/U6 our AI-Credit burn rate | 1 session |
| L6 | record `codex --version` (+ Claude Code version if KB cites one) | C9/C11 version pins | 1 min |
| L7 | startup-log check: which plugin resolution wins (file: checkout vs @latest wrapper) | carried U3 from pre-exec review | 2 min |

---

## SOURCE INDEX

Primary:
- https://opencode.ai/changelog ; https://github.com/anomalyco/opencode/releases (v1.18.20–23 notes)
- https://opencode.ai/v2/docs/migrate-v1 ; https://opencode.ai/v2/docs/build/plugins
- https://docs.cline.bot/api/models ; /api/chat-completions ; /api/overview
- https://marketplace.visualstudio.com/items?itemName=ltmoerdani.cline-copilot-chat (validated model table incl. 1M/384K, free-tier 200 OK, claude-* absence claim)
- https://github.com/cline/cline/pull/10401 (DeepSeek reasoningEffort handling in extension)
- https://geminicli.com/docs/cli/gemini-md/ ; https://geminicli.com/docs (context.fileName; Antigravity CLI transition banner)
- https://code.claude.com/docs/en/hooks ; https://code.claude.com/docs/en/hooks-guide
- https://developers.openai.com/codex/config-basic , /codex/security (via https://github.com/openai/codex/blob/main/docs/sandbox.md)

Corroborating:
- https://www.digitalapplied.com/blog/codex-cli-rust-migration-playbook-config-changes-2026 ; …/codex-cli-deep-dive-config-profiles-sandbox-2026
- https://clockedcode.com/blog/claude-code-hooks ; https://blakecrosley.com/blog/claude-code-hooks-explained
- https://github.com/code-yeongyu/oh-my-openagent/issues/6169 ; https://github.com/tickernelz/opencode-mem/issues/173
- https://github.com/anomalyco/opencode/issues/5665 , /issues/11554 , /issues/3936
- https://rottenwifi.com/github-copilots-new-limits-and-premium-ai-charges-explained-2025-2026/
- Carried from prior missions: anomalyco/opencode #22644 #22146 #43829 #30631 #1793 #3412 #34644 #8030 #8067 #15243; NoeFabris/opencode-antigravity-auth #495 #245 #126; docs.cline.bot/api/authentication, /api/sdk-examples; cavanaug/opencode-copilot-vscode; local audit CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md.

Tool-failure note (M23): Exa search remained broken (HTTP 401) this session; all research
via parallel-search/websearch. No claims synthesized without a live source.

---
*⬡ OMEGA ⬡ JEM ⬡ GAP-CLOSURE-SWEEP ⬡ 9-CLOSED / 2-PARTIAL / 7-LOCAL ⬡ 2026-08-26*
