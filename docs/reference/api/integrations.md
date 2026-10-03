# 🔱 Integrations — External API Provider Fleets
**AP Token**: `AP-INTEGRATIONS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Integrations package — Grok CLI fleet management, quota polling, and provider fleet orchestration.
**Tags**: integrations, grok, fleet, quota, orchestrator, providers
**Cross-references**: src/omega/integrations/grok_cli.py, src/omega/integrations/fleet_orchestrator.py, src/omega/integrations/quota_pollers.py, src/omega/vault.py

---

## Overview

The `integrations` package manages **external API provider fleets** with quota-aware routing, credential management, and real-time usage monitoring.

```
┌─────────────────────────────────────────────────────────────┐
│                    Integrations Package                      │
├─────────────────────────────────────────────────────────────┤
│  grok_cli.py         │  Grok CLI fleet (8 accounts)         │
│  fleet_orchestrator.py│  Multi-provider fleet orchestration │
│  quota_pollers.py    │  Real-time quota monitoring          │
│  __init__.py         │  Public exports                      │
└─────────────────────────────────────────────────────────────┘
```

**Supported Providers**:
- **Grok (xAI)** — 8-account fleet via ACP stdio
- **OpenRouter** — Credits-based quota
- **GCP** — Monitoring quotas
- **Exa** — Search rate limits
- **Firecrawl** — Credits-based quota

---

## Grok CLI Integration (grok_cli.py)

**Carmack Mode P0-2** — Minimal working scaffold for `grok agent stdio` (ACP) and `grok -p` (quick prompt).

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  GrokCLIClient          │  Persistent ACP stdio process     │
│  GrokQuickPrompt        │  One-shot `grok -p` wrapper       │
│  GrokFleetManager       │  8-account fleet management       │
└─────────────────────────────────────────────────────────────┘
```

**Account Isolation**: Each account = isolated process via `GROK_HOME=~/.grok-fleet/acct-{N}/`

### Core Classes

#### GrokAccountConfig
```python
@dataclass
class GrokAccountConfig:
    account_id: int              # 1-8
    grok_home: Path              # ~/.grok-fleet/acct-{N}/
    model: str = "grok-3"
    timeout_seconds: float = 60.0
    
    @property
    def env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["GROK_HOME"] = str(self.grok_home)
        return env
```

#### GrokCLIClient
Persistent ACP stdio client for conversation continuity.

```python
config = GrokAccountConfig(account_id=1, grok_home=Path("~/.grok-fleet/acct-1"))
client = GrokCLIClient(config)

await client.start()  # Launches `grok agent stdio`, initializes ACP

response = await client.prompt("Refactor this function", model="grok-3")
# Returns response text

await client.close()  # Clean shutdown
```

**ACP Protocol**: JSON-RPC 2.0 on stdin/stdout
- `initialize` → capabilities negotiation
- `prompt` → inference request
- Background reader task for responses

#### GrokQuickPrompt
Lightweight one-shot wrapper for `grok -p "prompt"`.

```python
quick = GrokQuickPrompt(config)
response = await quick.prompt("Quick question", model="grok-3")
# No conversation continuity — new process each call
```

#### GrokFleetManager
Manages 8-account fleet with quota checking.

```python
fleet = GrokFleetManager(base_grok_home=Path("~/.grok-fleet"))

# Persistent ACP (conversation continuity)
response = await fleet.prompt(account_id=1, text="Continue previous analysis")

# Quick prompt (no continuity)
response = await fleet.quick_prompt(account_id=2, text="One-off question")

# Quota checking
quota = await fleet.check_quota(account_id=1)
# QuotaInfo(credits_remaining=45.0, credits_total=100.0, exhausted=False)

all_quotas = await fleet.check_all_quotas()
# {1: QuotaInfo(...), 2: QuotaInfo(...), ...}

# Find first available account
available = await fleet.find_available_account()
# Returns account_id (1-8) or None

await fleet.close_all()  # Shutdown all persistent connections
```

### QuotaInfo
```python
@dataclass
class QuotaInfo:
    credits_remaining: float
    credits_total: float
    reset_time_unix: Optional[int] = None
    model: str = "grok-3"
    exhausted: bool = False
    
    @property
    def percent_remaining(self) -> float:
        return max(0.0, min(1.0, credits_remaining / credits_total))
```

**Note**: `check_quota()` is a **STUB** — real implementation requires gRPC-web client for `GetGrokCreditsConfig` (deferred to ACP multiplexer, D-435).

### Convenience Function

```python
from omega.integrations.grok_cli import grok_prompt

# One-liner with auto cleanup
response = await grok_prompt("Analyze this code", account_id=1)
```

### Exceptions

| Exception | Cause |
|-----------|-------|
| `GrokCLIError` | Base exception |
| `GrokCLITimeoutError` | Request timeout |
| `GrokCLIQuotaExhaustedError` | Quota exhausted (402 equivalent) |
| `GrokProcessError` | Subprocess failure (exit code, stderr) |

---

## Fleet Orchestrator (fleet_orchestrator.py)

Multi-provider fleet orchestration with quota-aware routing.

### Core Classes

#### ProviderType
```python
class ProviderType(Enum):
    LOCAL = "local"      # Native GGUF, LM Studio, Ollama
    CLOUD = "cloud"      # Grok, OpenRouter, GCP, Exa, Firecrawl
    HYBRID = "hybrid"    # Can route to both
```

#### RouteDecision
```python
class RouteDecision(Enum):
    ROUTE = "route"      # Use this provider
    SKIP = "skip"        # Skip (quota exhausted, rate limited)
    FALLBACK = "fallback" # Use fallback provider
    BLOCK = "block"      # Block all (critical state)
```

#### ProviderFleet
```python
@dataclass
class ProviderFleet:
    provider_name: str
    provider_type: ProviderType
    accounts: List[dict] = []
    quota_poller: Optional[QuotaPoller] = None
    priority: int = 0          # Lower = higher priority
    enabled: bool = True
    last_health_check: float = 0
    health_check_interval: float = 300  # 5 minutes
```

#### RouteRequest / RouteResponse
```python
@dataclass
class RouteRequest:
    query: str
    required_capability: Optional[str] = None
    max_latency_ms: Optional[int] = None
    prefer_local: bool = True
    metadata: dict = {}

@dataclass
class RouteResponse:
    provider: str
    decision: RouteDecision
    account_id: Optional[int] = None
    quota: Optional[QuotaSnapshot] = None
    fallback_provider: Optional[str] = None
    reason: str = ""
    latency_ms: float = 0
    metadata: dict = {}
```

### FleetOrchestrator

```python
orchestrator = FleetOrchestrator()

# Register fleets
orchestrator.register_fleet(
    provider_name="grok",
    provider_type=ProviderType.CLOUD,
    accounts=[{"id": i} for i in range(1, 9)],
    quota_poller=create_quota_poller("grok", api_key="..."),
    priority=3
)

orchestrator.register_fleet(
    provider_name="native-gguf",
    provider_type=ProviderType.LOCAL,
    priority=0  # Highest priority (local-first)
)

# Route request
request = RouteRequest(
    query="Harden container security",
    prefer_local=True,
    max_latency_ms=5000
)
response = await orchestrator.route_request(request)

if response.decision == RouteDecision.ROUTE:
    print(f"Use {response.provider} (account {response.account_id})")
```

**Routing Logic**:
1. Separate local/cloud providers
2. Sort by priority
3. Try local first if `prefer_local=True`
4. Check quota for each → first available wins
5. Circuit breaker on repeated failures

### Circuit Breaker

```python
# Auto-trips on quota exhaustion
# Half-open after 5 minutes for recovery test
# Manual reset after successful use
```

### Health Checks

```python
health = await orchestrator.health_check("grok")
# {"status": "healthy", "quota_status": "active", "remaining": 45, ...}

summary = await orchestrator.get_fleet_summary()
# {"total_fleets": 5, "enabled_fleets": 4, "providers": {...}}
```

### Default Orchestrator Factory

```python
from omega.integrations import create_default_orchestrator

orchestrator = await create_default_orchestrator(
    vault_core=vault,  # For credential retrieval
    config={
        "grok_enabled": True,
        "grok_api_key": "...",
        "openrouter_enabled": True,
        "openrouter_api_key": "..."
    }
)
```

---

## Quota Pollers (quota_pollers.py)

Real-time quota monitoring for each provider.

### Base Classes

```python
class QuotaStatusLevel(Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"

@dataclass
class QuotaSnapshot:
    provider: str
    status: QuotaStatusLevel
    remaining: float
    total: float
    used: float
    percent_remaining: float
    rate_limit_rpm: Optional[int] = None
    error: Optional[str] = None
```

### Poller Implementations

| Poller | Provider | Auth | Endpoint |
|--------|----------|------|----------|
| `GrokQuotaPoller` | Grok | gRPC-web | `GetGrokCreditsConfig` |
| `OpenRouterQuotaPoller` | OpenRouter | Bearer | `/api/v1/auth/key` |
| `GCPQuotaPoller` | GCP | ADC | Cloud Monitoring API |
| `ExaQuotaPoller` | Exa | Bearer | `/api/usage` |
| `FirecrawlQuotaPoller` | Firecrawl | Bearer | `/api/usage` |

### Factory

```python
from omega.integrations.quota_pollers import create_quota_poller

poller = create_quota_poller("grok", api_key="grok-key-...")
poller = create_quota_poller("openrouter", api_key="or-key-...")
poller = create_quota_poller("gcp", project_id="my-project")
poller = create_quota_poller("exa", api_key="exa-key-...")
poller = create_quota_poller("firecrawl", api_key="fc-key-...")
```

### Usage

```python
poller = create_quota_poller("openrouter", api_key="sk-or-...")

# Poll once
snapshot = await poller.poll(force=True)
print(f"Status: {snapshot.status}, Remaining: {snapshot.remaining}/{snapshot.total}")

# Poll with cache (1 min default)
snapshot = await poller.poll()  # Uses cached if fresh
```

### QuotaPoller Base Class

```python
class QuotaPoller(ABC):
    @abstractmethod
    async def poll(self, force: bool = False) -> QuotaSnapshot:
        """Return current quota snapshot."""
```

---

## Usage Example

```python
from omega.integrations import (
    FleetOrchestrator, create_quota_poller,
    ProviderType, RouteRequest
)
from omega.vault import VaultCore

# Initialize with VaultCore for credentials
vault = VaultCore()
vault._load_sync()

orchestrator = FleetOrchestrator()

# Register local providers (highest priority)
for name in ["native-gguf", "lmster", "ollama"]:
    orchestrator.register_fleet(
        provider_name=name,
        provider_type=ProviderType.LOCAL,
        priority={"native-gguf": 0, "lmster": 1, "ollama": 2}[name]
    )

# Register cloud providers with quota pollers
grok_key = vault.get_credential("grok:api_key")
if grok_key:
    orchestrator.register_fleet(
        provider_name="grok",
        provider_type=ProviderType.CLOUD,
        quota_poller=create_quota_poller("grok", api_key=grok_key),
        priority=3
    )

# Route a request
request = RouteRequest(
    query="Analyze the security implications of this architecture",
    prefer_local=True,
    max_latency_ms=10000
)

response = await orchestrator.route_request(request)

if response.decision == RouteDecision.ROUTE:
    print(f"✅ Routed to {response.provider}")
    # Use provider...
elif response.decision == RouteDecision.FALLBACK:
    print(f"⚠️  Fallback to {response.fallback_provider}")
else:
    print(f"❌ Blocked: {response.reason}")
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | All async via `anyio`; `open_process` for Grok CLI |
| **M7 Local-First** | Local providers priority 0-2; cloud only as fallback |
| **M8 Zero Telemetry** | No external analytics; local quota tracking |
| **M13 Temple-Grade** | Circuit breakers; health checks; structured errors |
| **M22 Response Provenance** | `provider_name` tracked in RouteResponse |
| **M23 Failure Integrity** | Quota exhaustion = hard block; no soft-failures |
| **M24 Venv Sovereignty** | `grok` binary in PATH; Python deps in `.venv` |

---

## Testing

```bash
pytest tests/test_grok_cli.py tests/test_fleet_orchestrator.py tests/test_quota_pollers.py -v
```

Key test scenarios:
- GrokCLIClient ACP protocol
- FleetManager account isolation
- Quota poller implementations
- Routing logic (local-first, quota, circuit breaker)
- Health check accuracy
- Default orchestrator factory

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ INTEGRATIONS-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

