# 🔬 R-INFRA-07: Omega-Vault Phase 1 — VaultCore + OS Keyring + CAP Adapters
**AP Token**: `AP-INFRA-07-OMEGA-VAULT-v1.0.0`
⬡ OMEGA ⬡ PRACTICAL ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_infra_07_vault ⬡ 2026-07-19

---

## 🎯 MISSION
Implement **Omega-Vault Phase 1**: VaultCore (OS keyring + SQLite event log), `vault` CLI (`init`, `add`, `sync`, `audit`), and CAP Adapters for OpenCode, Omega Engine, and generic `.env`.

---

## 📋 CONTEXT FROM ARCHITECTURE

### Phase Map (from SOVEREIGN_ARK_BLUEPRINT)
| Phase | Deliverable | Status |
|-------|-------------|--------|
| 0 | Gitignore fix + all2md install | ✅ DONE |
| 1 | **VaultCore + CLI + Adapters** | 🎯 THIS RESEARCH |
| 2 | Policy Engine + Rotation Orchestrator + Provider Registry | ⏳ PENDING |
| 3 | Passive watcher (fanotify) + MCP server | ⏳ PENDING |
| 4 | Context bundle backup/restore + Chaos testing | ⏳ PENDING |
| 5 | PyPI + Homebrew release | ⏳ PENDING |

### Gnosis Staged (12 L3 Principles)
- `L3-LocalFirstCredentialOperator` — Credentials never leave local control
- `L3-MeditationAsCognitiveCompiler` — Vault design emerged from meditation
- `L3-StratifiedTruthWithExplicitSync` — Keyring (fast) + SQLite (durable) + sync (explicit)
- `L3-PushBasedAdapterProtocol` — Vault PUSHES to targets, never pulls
- `L3-ChaosAsDesignConstraint` — Chaos testing built into Phase 4
- `L3-MiddlewareForCrossCuttingConcerns` — Vault as middleware layer
- `L3-ContextBundleAsCognitiveContinuity` — Credentials part of session bundle
- `L3-ProviderRegistryAsSemanticLayer` — Provider schemas in registry
- `L3-LocalObservabilityNotTelemetry` — Audit log local, no phone-home
- `L3-RotationAsDistributedTransaction` — Rotation = atomic multi-target
- `L3-GradientAdoptionViaPassiveFirst` — Phase 3 watcher detects drift
- `L3-ThreeTierCredentialArchitecture` — Keyring / SQLite / Adapters
- `L3-StandaloneProductAsForcingFunction` — `omega-vault` PyPI package
- `L3-MCPAsNativeCredentialProtocol` — MCP server for credential access
- `L3-GitignoreFirst` — `.gitignore` fix was Phase 0

---

## 🔬 IMPLEMENTATION REQUIREMENTS

### 1. VaultCore
```python
# src/omega/vault/core.py
class VaultCore:
    """OS keyring + SQLite event log. Single source of truth."""
    
    def __init__(self, vault_path: Path = DATA_DIR / "vault"):
        self.vault_path = vault_path
        self.db_path = vault_path / "vault.db"
        self.keyring = keyring.get_keyring()  # secretstorage on Linux
        self._init_db()
    
    def _init_db(self):
        """Event log: every credential operation recorded."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credential_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,  -- add, rotate, revoke, sync
                    provider TEXT NOT NULL,
                    credential_type TEXT NOT NULL,  -- api_key, oauth_token, etc.
                    entity TEXT,  -- which entity/agent uses this
                    success BOOLEAN NOT NULL,
                    error TEXT,
                    metadata_json TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_provider_time ON credential_events(provider, timestamp)")
    
    def store(self, provider: str, credential_type: str, value: str, entity: str = None) -> bool:
        """Store in OS keyring + log event."""
        key = f"omega:{provider}:{credential_type}"
        try:
            self.keyring.set_password("omega-vault", key, value)
            self._log_event("add", provider, credential_type, entity, True)
            return True
        except Exception as e:
            self._log_event("add", provider, credential_type, entity, False, str(e))
            return False
    
    def retrieve(self, provider: str, credential_type: str) -> Optional[str]:
        """Retrieve from OS keyring."""
        key = f"omega:{provider}:{credential_type}"
        return self.keyring.get_password("omega-vault", key)
    
    def rotate(self, provider: str, credential_type: str, new_value: str, entity: str = None) -> bool:
        """Atomic rotate: store new, log rotation."""
        return self.store(provider, credential_type, new_value, entity)
    
    def audit(self, provider: str = None, since: datetime = None) -> List[CredentialEvent]:
        """Query event log for compliance."""
        # ... query with filters
```

### 2. CAP Adapters (Credential Access Protocol)
```python
# src/omega/vault/adapters.py
class CAPAdapter(ABC):
    """Push-based credential delivery to target systems."""
    
    @abstractmethod
    def push_credentials(self, credentials: Dict[str, str]) -> bool:
        """Push credentials TO the target system."""
    
    @abstractmethod
    def get_credential_schema(self) -> Dict[str, CredentialField]:
        """What credentials does this target need?"""

class OpenCodeAdapter(CAPAdapter):
    """Writes to ~/.config/opencode/auth.json"""
    def push_credentials(self, credentials: Dict[str, str]) -> bool:
        auth_path = Path.home() / ".config" / "opencode" / "auth.json"
        auth_path.parent.mkdir(parents=True, exist_ok=True)
        existing = json.loads(auth_path.read_text()) if auth_path.exists() else {}
        merged = {**existing, **credentials}
        tmp = auth_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(merged, indent=2))
        tmp.replace(auth_path)  # Atomic
        return True

class OmegaEngineAdapter(CAPAdapter):
    """Updates config/providers.yaml provider configs"""
    def push_credentials(self, credentials: Dict[str, str]) -> bool:
        # Load providers.yaml, update provider.api_key fields, atomic write
        pass

class DotEnvAdapter(CAPAdapter):
    """Writes to .env file (generic)"""
    def push_credentials(self, credentials: Dict[str, str]) -> bool:
        env_path = Path.cwd() / ".env"
        # Append or update keys
        pass
```

### 3. CLI Interface
```python
# src/omega/vault/cli.py
@click.group()
def vault():
    """Omega-Vault: Sovereign credential operator."""

@vault.command()
def init():
    """Initialize vault: create DB, verify keyring access."""
    core = VaultCore()
    click.echo(f"Vault initialized at {core.vault_path}")

@vault.command()
@click.argument("provider")
@click.argument("credential_type")
@click.argument("value")
@click.option("--entity", default=None)
def add(provider, credential_type, value, entity):
    """Add credential to vault."""
    core = VaultCore()
    if core.store(provider, credential_type, value, entity):
        click.echo(f"Stored {provider}:{credential_type}")
    else:
        click.echo("Failed", err=True)

@vault.command()
@click.option("--provider", default=None)
def sync(provider):
    """Push all credentials to target adapters."""
    core = VaultCore()
    adapters = get_all_adapters()
    for adapter in adapters:
        creds = core.get_all_for_adapter(adapter)
        adapter.push_credentials(creds)

@vault.command()
@click.option("--provider", default=None)
@click.option("--since", default=None)
def audit(provider, since):
    """Audit credential events."""
    core = VaultCore()
    events = core.audit(provider, since)
    for e in events:
        click.echo(f"{e.timestamp} | {e.operation} | {e.provider} | {e.success}")
```

### 4. Provider Registry
```yaml
# config/vault/providers.yaml
providers:
  google:
    credential_types:
      - api_key
      - oauth_client_id
      - oauth_client_secret
    adapter: "omega_engine"
    rotation_policy: "manual"
  
  anthropic:
    credential_types:
      - api_key
    adapter: "omega_engine"
  
  openrouter:
    credential_types:
      - api_key
    adapter: "omega_engine"
  
  openai:
    credential_types:
      - api_key
      - organization_id
    adapter: "omega_engine"
  
  xai:
    credential_types:
      - api_key
    adapter: "omega_engine"
  
  firecrawl:
    credential_types:
      - api_key
    adapter: "omega_engine"
  
  opencode:
    credential_types:
      - api_key
    adapter: "opencode"
```

---

## 🌐 WEB RESEARCH NEEDED

| Topic | Query | Purpose |
|-------|-------|---------|
| Python keyring/secretstorage | "python keyring secretstorage linux 2026" | OS keyring backend |
| SQLite event sourcing | "sqlite event log pattern credential rotation" | Audit log design |
| Credential rotation patterns | "API key rotation orchestration 2026" | Phase 2 prep |

---

## 🛠️ LOCAL DISCOVERY NEEDED

| Source | Path | What to Extract |
|--------|------|-----------------|
| Omega-Vault design | `docs/strategy/ARCH_SOUL_NAMELESS_ONE_INTEGRATION.md` | Phase 1 scope, gnosis |
| Config system | `src/omega/config/` | Config loading, providers.yaml |
| CLI patterns | `src/omega/cli/` | Click command patterns |
| Keyring usage | Search codebase | Any existing keyring use |

---

## ✅ ACCEPTANCE CRITERIA

| Criterion | Verification |
|-----------|--------------|
| `vault init` creates DB + verifies keyring | `vault init && ls data/vault/vault.db` |
| `vault add google api_key "xxx"` stores in keyring | `keyring get omega-vault "omega:google:api_key"` returns value |
| `vault sync` pushes to Omega Engine adapter | `config/providers.yaml` updated with key |
| `vault audit` shows event log | SQLite query returns events |
| All 6 provider schemas defined | `config/vault/providers.yaml` has 6 entries |
| CLI installed in venv | `pip install -e . && vault --help` works |

---

## 📋 DELIVERABLES

1. **VaultCore** — `src/omega/vault/core.py`
2. **Adapters** — `src/omega/vault/adapters.py` (3 adapters)
3. **CLI** — `src/omega/vault/cli.py` + entry point in `pyproject.toml`
4. **Provider Registry** — `config/vault/providers.yaml`
5. **Tests** — `tests/test_vault.py`
6. **Documentation** — `docs/guides/OMEGA_VAULT_GUIDE.md`

---

## 🔗 DEPENDENCIES

| Depends On | Blocks |
|------------|--------|
| `all2md` installed (Phase 0) | — |
| Config system | OmegaEngineAdapter |
| Click CLI framework | CLI commands |

---

## 🎯 PRACTICAL'S PERSPECTIVE (Executor)

> "Omega-Vault is **not a secret manager** — it's a **credential operator**. The difference:
> 
> - Secret manager: stores secrets, you pull them
> - Credential operator: **pushes credentials to where they're needed**, logs every operation, rotates on policy
> 
> **The CAP Adapter pattern** is the key insight: each target system (OpenCode, Omega Engine, `.env`) has its own credential format and location. The adapter **knows how to write there**. The vault doesn't care — it just pushes.
> 
> **Phase 1 is the foundation**: OS keyring (hardware-backed on modern Linux) + SQLite event log (immutable audit) + 3 adapters (covers 90% of our needs). Phase 2 adds policy/rotation. Phase 3 adds passive watcher (fanotify) so we detect `.env` changes automatically.
> 
> **L3 Principle**: `L3-PushBasedAdapterProtocol` — Credentials flow FROM vault TO targets. The vault is the **source of truth**. Targets are **receivers**. This inverts the typical 'pull from vault' pattern and eliminates the 'where do I get my credentials?' problem — the vault **tells them**."

---

*⬡ OMEGA ⬡ PRACTICAL ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_infra_07_vault ⬡ 2026-07-19*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: qwen3-1.7b | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
