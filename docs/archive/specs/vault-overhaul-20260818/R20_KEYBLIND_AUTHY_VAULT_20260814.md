# Gap R20: Keyblind / Authy / Agent Vault Verification

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** UO-6.6 (credential management)
**Status:** ✅ RESOLVED

## ⚠️ PLAN CORRECTION
The research plan's Risk Mitigation row *"Keyblind/Authy don't exist → Keep VaultCore"* is **INVALID**. All three tools **exist and are actively maintained** (verified 2026-08-14). The correct conclusion is different: VaultCore should be kept regardless, because the external tools introduce SaaS/network architectures unsuitable for sovereignty.

## Summary
Keyblind, Authy (eric8810), and Infisical's agent-vault are all real, working secret managers for AI agents. However, **VaultCore already exists in this repo** (`src/omega/vault/vault_core.py`) as the local-first single source of truth (OS keyring + SQLite + CLI + lease protocol + audit log). None of the external tools should replace it; at most, a thin MCP adapter can mirror their `resolve_secret` pattern.

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| Keyblind | https://keyblind.dev/ | 2026 | MIT, MCP server, AES-256-GCM, 7 backends, sandbox |
| Authy (eric8810) | https://github.com/eric8810/authy | 2026 | Rust, age X25519, run-only mode, HMAC tokens |
| Infisical agent-vault | https://github.com/Infisical/agent-vault | 2026-04-21 | HTTP proxy broker, MITM credential injection |
| Local: `src/omega/vault/vault_core.py` | repo | 2026 | Existing SSOF credential store |

## Findings
- **Keyblind**: local AES-256-GCM vault, MCP server (16 tools), 7 backends (local/1Password/Bitwarden/AWS/GCP/Azure/env), deterministic HMAC fakes for safe review. Requires a SaaS dashboard for Pro/Team.
- **Authy**: single Rust binary, age-encrypted vault, `authy run` injects secrets as env into subprocesses, **run-only mode** (agent can inject but never read), HMAC-chained audit log.
- **agent-vault**: HTTP forward proxy that injects credentials into outbound requests (MITM architecture); designed to run on a **separate host** from the agent. Strong for multi-agent SaaS but adds a network broker.
- **VaultCore (local)**: already the engine's SSOF — OS keyring + SQLite event log + `vault` CLI, lease protocol (TTL/heartbeat, M25 compliant), file locking, migrated across oracle/library/tools/mcp. No external dependency, fully local (M7).

## Recommendation
**Keep VaultCore** as the engine's credential SSOF — it is local-first, already integrated, and satisfies M7/M11/M25. Do **not** adopt Keyblind/Authy/agent-vault as core dependencies (they pull in external binaries, SaaS tiers, or network MITM brokers that conflict with sovereignty). *Optional* future task: expose VaultCore secrets via a local MCP `resolve_secret` tool (mirroring Keyblind's pattern) if agent-facing secret injection is desired. Update the plan's Risk Mitigation row — the "don't exist" premise is false.

## Confidence
**HIGH** — existence and maturity of all three tools verified via their official sites/GitHub; VaultCore verified in-repo.

## Remaining Unknowns
- If an MCP-based secret-injection adapter is wanted, its design is a separate task (not blocking UO-6.6).
