# Cline — Canonical Operating Playbook (Omega Engine House Practices)

**KB Entry**: grokster/platforms/cline/PLAYBOOK
**last_verified**: 2026-08-26 · **rot_class**: medium (rulings stable; gate/pricing details fast)
**Specialist session**: jem (standing Cline specialist — see EXPERT_SESSIONS.md; Charter in `docs/research/R_CLINE_DIRECT_API_DEEP_MINE_20260826.md`)
**Sources**: `docs/research/R_CLINE_DIRECT_API_DEEP_MINE_20260826.md` (deep-mine, primary), `data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md` (live probe), `docs/research/R_CLINE_COPILOT_PROVIDER_SETUP_20260826.md`, ACTIVE_SPRINT D-557/D-563, docs.cline.bot (free-models, clinepass, cli-reference), cline.bot/tos

---

## §1 House Rulings (corrected framing)

- **D-557** — Cline + DeepSeek V4 Flash = "primary surgical tool" for large-context passes.
  - Caps: 1M context / 384K output — VERIFIED as DeepSeek-native figures (cline/cline discussion #10387); Cline-side enforced cap UNVERIFIED (probe P3/P8).
  - **Gate status CORRECTED 2026-08-26 (supersedes "fluid/pending")**: free-model gating is **OFFICIAL DOCUMENTED POLICY**, not a transient anomaly. docs.cline.bot/getting-started/free-models: *"Free model usage is not supported through the Cline API. Free models are only available in the Cline IDE Extension and CLI."* Backed by ToS §2.2(10)/(11) anti-circumvention. Empirically confirmed by Aug-22 live probe (HTTP 403). **Never wait for the gate to lift; never spoof around it.**
  - **D-557 restoration path (NEW)**: `cline-pass/deepseek-v4-flash` exists on ClinePass ($9.99/mo) and external API use is explicitly sanctioned with official curl examples. Reference pricing $0.44/$1.32 per 1M peak, $0.22/$0.66 off-peak. Whether the 1M-context figure carries to the cline-pass variant is UNVERIFIED (probe P8).
- **D-563** — **1 active Cline instance max**; the ~8-account pool exists for rate-limit resilience, NOT parallelism. ToS §2.2(4) additionally forbids buying/selling/transferring API keys without written consent — every pool key must be tied to a legitimately-held account. VERIFIED (ruling) / REPORTED (ToS reading).
- **Model pairing** — DeepSeek V4 Flash (1M/384K) + MiMo V2.5 (512K claimed). ⚠️ MiMo 512K cap UNVERIFIED — never cite without probe. CLI version reference updated from 3.0.52 to ≥3.0.56-era stores (probe P9 pending for exact stamp).

## §2 Access-Path Decision Tree (which door for which job)

| Need | Path | Status |
|---|---|---|
| Free experimentation | Cline CLI/extension, FREE-tagged models | ✅ sanctioned; training-exposed (ToS §3.2) |
| D-557 workhorse via direct API | ClinePass sub → OpenCode provider block (`cline-pass/*`) | ✅ sanctioned; requires $9.99/mo decision from Architect |
| D-557 workhorse at $0 | `cline` CLI wrapper (agent-loop latency, deep-fallback only) | ✅ sanctioned product surface |
| Raw free-model calls from scripts | NONE — gated by policy | ❌ do not attempt |
| Header-spoofing the client identity | NONE | ❌ PERMANENTLY REJECTED (fragile + ToS breach + M23/M8) |

## §3 Headless Operation (from cli-reference, VERIFIED against docs)

- One-shot: `cline "prompt"` (act mode, auto-approve ON by default — mind this on shared repos).
- Structured output: `cline --json "prompt"` → NDJSON lines `{type: say|ask, text, ts, subtype, reasoning, partial}` — parseable agent-loop stream incl. reasoning field.
- Effort control: `--thinking none|low|medium|high|xhigh` (default medium; note `xhigh`, not OpenAI's `max`). Wire param sent to gateway for non-OpenAI models UNKNOWN (probe P6).
- Session resume: `cline --id <session-id>`; sessions persist in `~/.cline/data/sessions/` (SQLite).
- Background dispatch: `cline -z "task"` → hub daemon (`127.0.0.1:25463`, `CLINE_HUB_ADDRESS`).
- Safety rails: `CLINE_COMMAND_PERMISSIONS='{"allow":[...],"deny":[...],"allowRedirects":false}'`; `CLINE_SANDBOX=1`.
- Auth: `cline auth` (OAuth TUI) or `cline auth -p cline -k "$CLINE_API_KEY" -m <model>`.

## §4 Briefing-Doc Entry Pattern (durable house practice)

- `.clinerules` = HOW-to-work rules; OMEGA_ENGINE.md = WHAT the engine is. Keep the separation.
- Entry point pattern: a briefing doc (`docs/briefings/CLINE_CLI_BRIEFING_*.md`) read first every session (~1% of 1M context), tiered document index Tier-1 SSOTs → Tier-4 deprecated. VERIFIED in house practice.
- Note: `.clinerules` single-file v7.2.0 is legacy-shape — current spec is a DIRECTORY (`.clinerules/*.md|.txt`, optional YAML `paths:` frontmatter). See CONFIG_REFERENCE §1 before editing house rules.

## §5 Sovereign Proxy Identity (durable practice)

Platform instructed to prioritize local files/mandates over training weights; local-first bias;
Cloud-Drift violation concept; M23 hard-stop on tool outages written directly into rules.
VERIFIED house practice. Migration note: when porting to current format, these belong in
always-on rule files (no frontmatter) inside `.clinerules/`.

## §6 Cross-Platform Handoff

- `docs/research/opencode_custom_handoff_to_cline.md` — OpenCode→Cline handoff pattern.
- Cline sessions produce full session-export markdown dumps (see `data/coordination/fle_study_20260825/`) — good forensic artifacts. VERIFIED.
- MCP config path moved: project-level config is now `<project>/.cline/mcp.json` (NOT legacy `cline_mcp_settings.json`). House references to the old name need migration. VERIFIED vs cli-reference layout.

## §7 Cline as Auditor (adversarial cross-platform review)

- `R_CLINE_CATCHUP_REVIEW_FOR_KALI_20260822` demonstrates the fresh-eyes independent-review pattern — Cline re-derived measured facts instead of trusting the manual, and found NEW criticals (B5 23MB tracked binary, B6 M1 enforced by whitelisting violator, B7 truthiness drift).
- Value: use Cline for adversarial cross-platform audits where the OpenCode fleet has blind spots. VERIFIED house result.
- Practical flags for audit runs: `-c <repo>` for cwd, `--auto-approve false` when reviewing untrusted trees, `--retries <n>` to bound loops.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
