<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔐 Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.6.x (alpha) | ✅ |
| < 1.6 | ❌ |

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

Instead, report security issues via:

- **Email**: security@xoe-novai.com (PGP key available on request)
- **GitHub Security Advisories**: Use the "Report a vulnerability" tab in the Security section of this repository

We aim to:
- Acknowledge receipt within **48 hours**
- Provide a preliminary assessment within **7 days**
- Release a fix or mitigation within **30 days** for critical issues

## Scope

This policy covers the Omega Engine core (`src/omega/`), CLI (`omega`), and bundled MCP servers (`mcp_servers/`).

**Out of scope**:
- Third-party dependencies (report upstream)
- Configuration files on your machine
- Local model files (GGUF weights)
- User data directories (`~/omega/data/`)

## Disclosure Timeline

1. **Day 0**: Vulnerability reported
2. **Day 1-2**: Acknowledgment + triage
3. **Day 3-7**: Preliminary assessment + severity classification
4. **Day 7-30**: Fix development + testing
5. **Day 30**: Coordinated disclosure (advisory + patch release)

## Severity Classification

| Severity | CVSS Range | Response |
|----------|------------|----------|
| Critical | 9.0-10.0 | Emergency patch within 7 days |
| High | 7.0-8.9 | Patch within 14 days |
| Medium | 4.0-6.9 | Patch within 30 days |
| Low | 0.1-3.9 | Next scheduled release |

## Security Architecture

The Omega Engine is designed with security as a sovereign mandate:

- **M7 Local-First**: Cloud is opt-in fallback; local inference primary
- **M8 Zero Telemetry**: No external phone-home, no analytics
- **M22 Provenance**: Every response carries provider identity
- **M23 Failure Integrity**: No soft failures; broken tools → hard stop
- **PII Masking**: Cloud backends receive masked observations (M21)
- **Credential Isolation**: VaultCore removed (D-565); python-age for encryption

## Known Security Considerations

| Area | Status | Notes |
|------|--------|-------|
| Local model execution | ✅ | Runs in-process, no sandbox (CPU-only GGUF) |
| Cloud provider fallback | ⚠️ | Opt-in only; PII masking applied |
| MCP server exposure | ⚠️ | Localhost-only by default; no auth on local loopback |
| Model weight verification | ⚠️ | SHA256 checksums on download; no signature verification yet |
| Dependency scanning | ✅ | Gitleaks + dependency audit in CI |

## Threat Model

This section answers the mandatory threat-model questions with actual config values **from the public build**.

### 1. Default Bind Address & Authentication

| Endpoint | Bind | Transport | Auth |
|----------|------|-----------|------|
| MCP Streamable HTTP (hub server) | `127.0.0.1:8016` | `/mcp` | None (localhost only) |
| MCP Legacy SSE (hub server) | `127.0.0.1:8016` | `/sse` | None (localhost only) |
| Exchange | `127.0.0.1:8019` | HTTP | None (localhost only) |

**Hub server config**: `OMEGA_MCP_HOST=127.0.0.1`, `OMEGA_MCP_PORT=8016`, `OMEGA_MCP_TRANSPORT=streamable-http` (default). No authentication on loopback; tailnet exposure controlled by Tailscale ACLs (deny-by-default, explicit grants only).

**Client runtime defaults** (for embedding): `src/omega/mcp_runtime.py` defaults to `stdio` transport with port fallback `8000`. These are **client-side** defaults for embedding the hub; the hub server itself binds `127.0.0.1:8016` with `streamable-http`.

### 2. Handoff-Bus Content Treatment

- **Data vs Instructions**: Handoff packets carry structured task context (JSON), not executable code. The `task` field is a natural-language description; `context` is background metadata.
- **Poisoned Handoff Risk**: A malicious handoff could steer an agent if the receiving agent trusts `task`/`context` uncritically. Mitigation: receiving agents validate via `_require_service()` and entity registry before acting; `m9_safe` decorator wraps all tools with error boundaries.
- **Sanitization**: No automatic sanitization of handoff content. Agents must treat handoff context as untrusted input. Future: schema validation on submit.

### 3. Control Planes (Kill / Escalate / Approve / Throttle)

| Plane | What It Gates | Default | Config |
|-------|---------------|---------|--------|
| **Kill** | Halt runaway session | Enabled | `OMEGA_KILL_TIMEOUT_S` (default 30s) |
| **Escalate** | Promote blocker to higher authority | Enabled | Requires `packet_id` + `to_entity` |
| **Approve** | Gate destructive ops | Enabled (fail-closed) | `OMEGA_APPROVAL_TIMEOUT_S` (default 900s) |
| **Throttle** | Per-entity token/tool limits | Advisory v1 | `OMEGA_THROTTLE_ENABLED=true` |

**Defaults**: Kill/Escalate/Approve active; Throttle advisory. All planes require explicit human decision for Approve; Kill is idempotent.

**Note**: The config symbol `OMEGA_APPROVAL_TIMEOUT_S` is read by the control plane implementation (default 900s). `OMEGA_KILL_TIMEOUT_S` and `OMEGA_THROTTLE_ENABLED` are **not currently implemented** in the public build; they are reserved for future use.

### 4. `vault_ops` Local-Only Enforcement

- **Boundary**: `vault_ops` tool only executes on local VaultCore (python-age encryption). Cloud providers never receive vault credentials.
- **Public build**: VaultCore is **removed from the public build** (D-565). The `vault_ops` tool exists but returns `RuntimeError: VaultCore unavailable` on public cuts. Local-only enforcement is a no-op on public cuts.
- **Internal builds**: `VaultCore` class checks `OMEGA_VAULT_LOCAL_ONLY=true` (default). Any cloud provider attempting vault ops receives `RuntimeError: vault_ops is local-only`.
- **Credential Storage**: python-age encrypted blobs in `~/.config/omega/vault/`. No plaintext keys in memory beyond operation scope.

### 5. Secret Scanners

| Scanner | Runs On | Config |
|---------|---------|--------|
| Gitleaks | PR + Push | `.gitleaks.toml` + `.gitleaksignore` baseline |
| TruffleHog | PR (diff) + Push (full) | `--only-verified` |
| C3 Secret Scan | PR + Push | `scripts/ci_secret_scan.py` (sk/csk/AIza/ghp/xai patterns) |
| M35 VAULT Allowlist | PR (staged files) | `data/secrets-public.toml` |

**Fail-closed**: All scanners must pass; any failure blocks merge/push.

### 6. Known Limits

- **No sandbox** for local GGUF execution (in-process CPU inference).
- **No signature verification** on downloaded model weights (SHA256 only).
- **Loopback auth** absent by design; tailnet is trust boundary.
- **Exchange port 8019**: `config/lan_exposure_allowlist.yaml` describes port 8019 as tailnet-reachable for federation; the hub server itself binds `127.0.0.1:8019` only.
- **Independent human review** pending (P2-3).

---

## Contact

- **Security Team**: security@xoe-novai.com
- **PGP Key**: Available on request
- **Response SLA**: 48 hours acknowledgment

---

*⬡ OMEGA ⬡ SECURITY-POLICY-v1.0.0 ⬡ 2026-09-02*