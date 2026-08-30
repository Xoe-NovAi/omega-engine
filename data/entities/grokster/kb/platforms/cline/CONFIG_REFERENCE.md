<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Cline — Configuration Reference

**KB Entry**: grokster/platforms/cline/CONFIG_REFERENCE
**last_verified**: 2026-08-26 · **rot_class**: fast (config surfaces evolve per release)
**Sources**: docs.cline.bot/customization/cline-rules, docs.cline.bot/cli/cli-reference, docs.cline.bot/getting-started/clinepass.md, `docs/research/R_CLINE_DIRECT_API_DEEP_MINE_20260826.md`, house `.clinerules` v7.2.0 (legacy)

---

## §1 `.clinerules` — CURRENT SPEC (directory format)

House repo's single-file `.clinerules` v7.2.0 is **legacy-shape**. Current documented surface:

| Aspect | Spec |
|---|---|
| Location | Workspace `.clinerules/` directory; global `~/Documents/Cline/Rules` (Linux/WSL alt: `~/Cline/Rules`); global cross-tool `~/.agents/AGENTS.md` |
| File types | `.md` and `.txt`; numeric prefixes optional; all combined into one rule set |
| Frontmatter | YAML between `---` markers; currently ONE key: `paths:` (glob array) |
| Activation | Conditional rules activate when context (message paths, open tabs, visible files, edited files, pending ops) matches ANY glob |
| `paths: []` | never activates (soft-disable); no frontmatter = always active |
| Invalid YAML | **fail-open** — rule activates with raw frontmatter visible |
| Precedence | workspace > global on conflict; otherwise combined |
| Toggles | per-rule UI toggle; toggle-off beats conditional matching |
| Cross-tool auto-detect | `.cursorrules`, `.windsurfrules`, `AGENTS.md` |

Glob syntax: `*` (no `/`) · `**` recursive · `?` · `[abc]` · `{a,b}`.

```yaml
# .clinerules/frontend.md example
---
paths:
  - "src/components/**"
---
# Frontend Guidelines
- ...
```

No formal version key exists in the spec — house's "v7.2.0" header is a house-side convention.

## §2 MCP Config

- **Current location**: `<project>/.cline/mcp.json`. Manage via `cline mcp` wizard / `cline mcp install`.
- Legacy name `cline_mcp_settings.json` (referenced in house configs) is outdated — migrate on next touch.

## §3 CLI Flags Table (VERIFIED vs cli-reference)

| Flag | Effect |
|---|---|
| `-P, --provider <id>` | provider id (default `cline`) |
| `-m, --model <model-id>` | model for the session |
| `-k, --key <api-key>` | API-key override (beats env vars) |
| `-s, --system <prompt>` | override system prompt |
| `-p, --plan` | plan mode (default act) |
| `-i, --tui` | interactive TUI |
| `--json` | NDJSON output; non-interactive; needs prompt or stdin |
| `--auto-approve <bool>` | tool auto-approval (default TRUE headless; FALSE in ACP) |
| `-t, --timeout <sec>` | task timeout (0 = none) |
| `-c, --cwd <path>` | working directory |
| `--config <path>` | config dir (default `~/.cline/data/settings`) |
| `--data-dir <path>` | isolated state root (default `~/.cline`) |
| `--thinking <level>` | `none\|low\|medium\|high\|xhigh` (default medium) |
| `--retries <count>` | max consecutive mistakes before halting |
| `--hooks-dir <path>` | runtime hook injection dir (default `~/.cline/hooks`) |
| `--acp` | Agent Client Protocol mode |
| `--id <session-id>` | resume session by id |
| `-z, --zen` | dispatch to background hub and exit |
| `-v / -V` | verbose / version |

Commands: `auth` `config` `connect` `mcp` `dev` `doctor` `history|h` `hook` `plugin` `schedule` `hub` `update` `version` `kanban`.

Key env vars: `CLINE_API_KEY`, `CLINE_DATA_DIR`, `CLINE_HUB_ADDRESS`, `CLINE_SESSION_BACKEND_MODE` (`local|hub|remote|auto`), `CLINE_SANDBOX(_DATA_DIR)`, `CLINE_HOOKS_DIR`, `CLINE_COMMAND_PERMISSIONS` (JSON glob policy; deny wins; redirects default-denied), `CLINE_TOOL_APPROVAL_MODE=desktop` + `CLINE_TOOL_APPROVAL_DIR`.

## §4 VS Code Extension Settings Surface

- Settings panel (⚙️): **API Provider** dropdown — `Cline` (usage-billing), `ClinePass`, `OpenAI Compatible`, Anthropic, OpenRouter, Bedrock (3 auth profiles), Gemini, OpenAI (Codex OAuth), Qwen, MiniMax, Z AI, Poolside, +30 more.
- Generic endpoint fields: Base URL + API Key + Model ID + advanced (max output tokens, context window, image support, computer-use flag, per-token prices).
- Free models appear FREE-tagged under both Cline and ClinePass providers.
- Telemetry ON by default; disable in extension settings (ToS §3.6).
- System prompt hardcoded/not user-editable (issue #4301).

## §5 OpenCode Attachment Block (direct-API path)

```jsonc
// project opencode.json → "provider" (merge-safe: "cline" id unused in TUI configs)
"cline": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Cline",
  "options": {
    "baseURL": "https://api.cline.bot/api/v1",
    "apiKey": "{env:CLINE_API_KEY}"
  },
  "models": {
    // ONLY ship models verified against live probes (error-differentiation; no public
    // /models endpoint exists — GOTCHAS G13). Do NOT ship anthropic/* (GOTCHAS G4).
    "cline-pass/deepseek-v4-flash": {
      "name": "DeepSeek V4 Flash (ClinePass)",
      "limit": { "context": 1048576, "output": 393216 }   // 1M/384K per house-validated table; Cline-side enforcement = probe P8
    }
  }
  }
}
```

Plus `.env`: `CLINE_API_KEY=sk_…` (extract once from `~/.cline/data/secrets.json`).
Engine-fabric equivalent (providers.yaml fallback_chain entry): `base_url: https://api.cline.bot/api` + `api_key: env:CLINE_API_KEY` (URL math yields `/api/v1/chat/completions`). VERIFIED boot-clean Aug-22.

⚠️ Re-probe gate + namespace BEFORE pasting any block (PLAYBOOK §1; probes P1/P7). reasoning_effort variants are UNVERIFIED at this gateway — if they render but do nothing, drop them rather than ship dead knobs.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
