# GitHub Copilot — Config Reference (OpenCode Integration + Copilot CLI Flags)

**KB Entry**: grokster/platforms/copilot/CONFIG_REFERENCE
**last_verified**: 2026-08-26 · **rot_class**: fast (flags/versions drift; verify before relying)
**Scope**: House-facing configuration surfaces: OpenCode builtin provider posture, enterprise slot semantics, multi-account isolation, Copilot CLI automation flags, env/config file locations.
**Sources**: R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md §A/§E; docs.github.com CLI install/auth pages; github.blog changelog 2026-07-01 (session limits); opencode issues #20758/#3936.

---

## §1 OpenCode Builtin Provider — Zero-Config NO-OP Posture

- Builtin providers: `github-copilot` + `github-copilot-enterprise` (the ONLY 2 isolation slots).
- Credential already present at `~/.local/share/opencode/auth.json` → **P1a = VERIFIED NO-OP 2026-08-26** (credential confirmed present; raw-gho_ pass-through mode — see ARCHITECTURE §5a). Zero config needed. `expires: 0` is INERT — the builtin loader never reads it (binary-verified); no refresh scheduling, no exchange round-trip, zero `/copilot_internal` rate-limit exposure.
- Auth path: `opencode` TUI → `/connect` → GitHub Copilot → device flow. Officially sanctioned by GitHub (changelog 2026-01-16). Paid plans only for explicit model selection (Free = auto-model-only dead end, #34644).
- OpenCode's `transform.ts` applies special handling for "codex context limits" on the Copilot provider — house V2 recon note; do not strip when editing transforms.

## §2 Enterprise Slot Semantics

**BINARY GROUND TRUTH (2026-08-26, 1.18.23)**: the string `copilot-enterprise` appears **0 times** in the pinned binary, embedded catalog included. There is NO separately compiled `github-copilot-enterprise` provider; enterprise is a MODE of the single `github-copilot` provider — same auth loader, credential gains an `enterpriseUrl` field, models map to `https://copilot-api.<domain>` (legacy `api.githubcopilot.com` fallback when absent). The historical "2 builtin slots" premise is therefore suspect on this binary: whether a `github-copilot-enterprise` key in auth.json resolves to any auth loader at runtime (via fetched models.dev catalog) is exactly what probe L4-a step 0 now tests.

| Aspect | State |
|---|---|
| Intended use | GHE (`*.ghe.com`) via deployment-type prompt in `auth login`/`/connect` (built into binary methods) |
| Separate enterprise provider ID | NOT in binary [HIGH]; may exist only via runtime models.dev fetch [UNVERIFIED] |
| github.com individual token in slot | Redesigned probe L4-a (see RESEARCH_TARGETS) — original design likely dead |
| Known friction | Enterprise client-ID mismatch history (#11554), GHE 404s pre-fix (#3936), compaction 400s (#11105) |

Do NOT build dependencies on slot 2 until L4-a passes.

## §3 Multi-Account Isolation Limits

- Hard ceiling: **2 simultaneous credentials** in stock OpenCode (one per builtin slot) — **PREMISE UNDER AUDIT**: binary 1.18.23 contains no separate enterprise provider (CONFIG_REFERENCE §2); L4-a adjudicates.
- N>2 pattern: external proxy-per-account (e.g., messense/copilot-api-proxy) — each instance holds one account token and exposes a distinct localhost port as a custom OpenAI-compatible provider. Ban-risk acceptance requires Architect sign-off (PLAYBOOK §1).
- Per-model header overrides are possible via opencode.json provider config (pattern from #3936):
```json
{ "provider": { "github-copilot": { "models": { "<model-id>": {
    "headers": { "Editor-Version": "vscode/1.100.0", "Copilot-Integration-Id": "vscode-chat" } } } } } }
```

## §4 Copilot CLI Flags (probe/parity use ONLY — see PLAYBOOK §3)

| Flag / Command | Effect |
|---|---|
| `-p "<prompt>" [-s]` | Headless single-prompt run; pipe-friendly with `-s` |
| `--model=<id>` | Explicit model |
| `--allow-tool` / `--deny-tool` | Selective tool permissions (prefer over blanket) |
| `--allow-all-tools` / `--allow-all` (`--yolo`) | Broad grants — treat as handing over the terminal |
| `--agent <name>` | Named custom agent profile |
| `--no-ask-user` | Non-interactive hard requirement |
| `--max-ai-credits=N` | Session credit fuse (CLI ≥1.0.66; SOFT cap; set ≥30; does not survive resume) |
| `/limits` | Interactive session-limit view/set |
| `--secret-env-vars=VAR,...` | Redact env secrets from shell/MCP/output (`GITHUB_TOKEN`, `COPILOT_GITHUB_TOKEN` redacted by default) |
| `copilot update` | Self-update |
| `copilot login --host <slug>.ghe.com` | GHE auth |

## §5 Env & File Locations

| Item | Path / Var |
|---|---|
| OpenCode credential store | `~/.local/share/opencode/auth.json` |
| Copilot CLI CI auth precedence | `COPILOT_GITHUB_TOKEN` > `GH_TOKEN` > `GITHUB_TOKEN` |
| Copilot CLI config dir | `~/.copilot/` (incl. `lsp-config.json`) |
| Repo-level CLI/LSP config | `.github/lsp.json`, AGENTS.md, Agent Skills |
| Proxy token stores (reference) | messense: `~/.local/share/copilot-api-proxy/github_token` (0600); IT-BAER: `data/github_token.json` |

## §6 Provider Fabric Position

Copilot sits at **priority 6** in the M7 local-first ordering (native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenCode Zen(4) → OpenCode(5) → **Copilot(6)**). Cloud safety net — never primary. Any config change promoting it above local backends is a systemic M7 violation.

**Post-remediation override-safety verdict (2026-08-26)**: the 9 provider overrides deleted in the config remediation (openrouter, cerebras, groq, mistral, together, cloudflare, nvidia-nim, sambanova, siliconflow) were scanned in the pre-remediation backup (`~/.local/share/opencode-backups/20260826-remediation/global-opencode.json`): **0 occurrences of `Editor-Version`, `Copilot-Integration-Id`, or any copilot-relevant string anywhere in the file.** None was load-bearing for Copilot. Deletion is Copilot-SAFE. [VERIFIED — forensic scan]

---
*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
