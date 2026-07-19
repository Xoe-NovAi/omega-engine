# 🔱 Headless Subagent Pool Architecture
**AP Token**: `AP-HEADLESS-POOL-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_headless_pool ⬡ ARCHITECTURE

**Date**: 2026-07-19
**Purpose**: Design 24-account CLI agent pool (8 Grok + 8 Copilot + 8 Cline) as unified compute resource with intelligent task routing, credential integration, and cognitive diversity weighting.

---

## 📋 Executive Summary (L1)

The Omega Engine possesses **24 unused CLI accounts** across three platforms — a massive untapped compute resource. This architecture transforms them into a **Headless Subagent Pool** with:
- **Pool Orchestrator** for task dispatch, health monitoring, and rebalancing
- **Omega-Vault Integration** for credential management and rotation
- **Cognitive Diversity Weighting** for result aggregation
- **Hivemind Integration** for task dispatch and result capture
- **Sovereign Search Tier 4** integration (CLI agents as search providers)
- **tmux-based Isolation** (validated by AWS CAO) for session isolation
- **MCP-based Orchestration** (validated by AWS CAO) for agent-to-agent coordination
- **Cross-Provider Profiles** (validated by AWS CAO) for mixed-model workflows

**Key Innovation**: Routing is the highest-leverage optimization (70-80% of inference costs). Modern routing is learned, adaptive, and budget-aware. Cognitive diversity is critical — diversity collapse is a real risk.

**Reference Implementation**: AWS CLI Agent Orchestrator (CAO) — 920★, Apache-2.0, tmux-based multi-agent orchestration for 9+ CLI providers (Claude Code, Codex, Copilot, OpenCode, etc.). Key patterns adopted: tmux isolation, MCP orchestration, cross-provider profiles, fleet coordination.

---

## 1. Pool Composition

| Pool | Accounts | Models | Context | Specialization | Cost Profile |
|------|----------|--------|---------|----------------|--------------|
| **Grok CLI** | 8 | Grok-3, Grok-2, Grok-1.5 | 128K-1M | Web search, reasoning, synthesis | Free tier (xAI) |
| **Copilot CLI** | 8 | GPT-4o, GPT-4o-mini, o1 | 128K | Code gen, implementation, review | GitHub subscription |
| **Cline CLI** | 8 | **DeepSeek V4 Flash (1M)**, MiMo V2.5 (512K), Claude, GPT | 1M/512K | **Deep research (1M ctx)**, large refactors | Free tier (DeepSeek) |

**Total**: 24 accounts, 3 distinct model families, 3 context tiers (128K, 512K, 1M)

---

## 2. Task Routing Matrix

| Task Type | Primary Pool | Fallback | Rationale |
|-----------|-------------|----------|-----------|
| **Deep Research** | Cline (DeepSeek 1M) | Grok | 1M context, free tier, reasoning |
| **Web Search + Synthesis** | Grok | Cline | Native search, reasoning |
| **Code Implementation** | Copilot (GPT-4o) | Cline (MiMo) | Best code gen |
| **Code Review / Audit** | Copilot (o1) | Grok | Reasoning models |
| **Large Refactor (500K+ tokens)** | Cline (DeepSeek 1M) | — | Only 1M context option |
| **Parallel Verification** | All (3-way) | — | Cognitive diversity |

**Routing Principles**:
1. **Context-first**: Match task context size → pool with sufficient context
2. **Capability-second**: Match task type → pool with specialized models
3. **Cost-third**: Prefer free tiers (Grok, DeepSeek) over paid (Copilot)
4. **Diversity**: For verification tasks, dispatch to all 3 pools simultaneously

---

## 3. Pool Orchestrator Design

### 3.1 Component Location
```
src/omega/infra/subagent_pool/
├── __init__.py
├── orchestrator.py          # Main PoolOrchestrator class
├── account_registry.py      # Account health, rate limits, credentials
├── task_router.py           # Routing logic + task decomposition
├── result_aggregator.py     # Cognitive diversity weighting
├── health_monitor.py        # Per-account health checks
├── credential_watcher.py    # Omega-Vault integration
├── tmux_manager.py          # tmux session lifecycle (CAO pattern)
├── mcp_coordinator.py       # MCP-based agent coordination (CAO pattern)
├── profile_manager.py       # Cross-provider agent profiles (CAO pattern)
└── models.py                # Data models
```

### 3.2 Core Interfaces

```python
class PoolOrchestrator:
    """Main entry point for pool operations."""
    
    async def dispatch(
        self, 
        task: PoolTask, 
        routing_hint: RoutingHint = None
    ) -> Future[PoolResult]:
        """Dispatch task to optimal account. Returns future for async collection."""
        ...
    
    async def health_check(self) -> PoolHealthReport:
        """Check all accounts: rate limits, credential validity, responsiveness."""
        ...
    
    async def rebalance(self) -> RebalanceReport:
        """Handle rate limits, failures, redistribute load."""
        ...
    
    async def get_pool_status(self) -> PoolStatus:
        """Real-time status: available accounts, queue depth, throughput."""
        ...

class AccountRegistry:
    """Manages 24 accounts with health tracking."""
    
    def get_available(self, pool: PoolType, min_context: int) -> List[Account]:
        """Get healthy accounts with sufficient context."""
        ...
    
    def mark_rate_limited(self, account_id: str, retry_after: int):
        """Temporarily remove from available pool."""
        ...
    
    def update_credentials(self, account_id: str, new_creds: Credentials):
        """Called by credential_watcher on rotation."""
        ...
```

### 3.3 tmux Session Management (CAO Pattern)

```python
class TmuxManager:
    """Manages tmux sessions for 24 isolated agent accounts (CAO pattern)."""
    
    async def create_session(self, account: Account, profile: AgentProfile) -> str:
        """Create tmux session with account-specific env vars."""
        # CAO pattern: each agent in isolated tmux session
        # Env var allowlist: HOME, PATH, SHELL, CAO_*, KIRO_*, MISE_*, AWS_*
        # Forward per-account: API keys, OAuth tokens via --env
        ...
    
    async def send_message(self, session_name: str, message: str):
        """Send message to agent via tmux send-keys."""
        ...
    
    async def capture_output(self, session_name: str) -> str:
        """Capture tmux pane output for result collection."""
        ...
    
    async def health_check(self, session_name: str) -> bool:
        """Check if tmux session is responsive."""
        ...
    
    async def terminate_session(self, session_name: str):
        """Clean shutdown via CAO pattern: cao shutdown --session."""
        ...
```

### 3.4 MCP-Based Agent Coordination (CAO Pattern)

```python
class MCPCoordinator:
    """MCP-based agent-to-agent orchestration (CAO pattern)."""
    
    # Orchestration modes from CAO:
    # 1. Handoff — sync, wait for completion, auto-cleanup
    # 2. Assign — async, fire-and-forget with callback
    # 3. Send Message — communicate with existing agent
    
    async def handoff(self, task: PoolTask, target_account: Account) -> PoolResult:
        """Synchronous delegation with result wait."""
        # Creates new tmux session, sends task, waits for completion
        # Auto-deletes worker session on success (scrollback saved)
        ...
    
    async def assign(self, task: PoolTask, target_account: Account) -> str:
        """Asynchronous delegation with callback."""
        # Spawns agent, sends task with callback instructions, returns immediately
        # Worker sends results back via send_message when done
        ...
    
    async def send_message(self, session_id: str, message: str) -> bool:
        """Communicate with existing agent."""
        ...
```

### 3.5 Cross-Provider Agent Profiles (CAO Pattern)

```python
class ProfileManager:
    """Manages cross-provider agent profiles (CAO pattern)."""
    
    # Profile format: markdown + YAML frontmatter
    # Valid providers: grok_cli, copilot_cli, cline_cli, claude_code, codex, etc.
    
    def create_profile(self, account: Account) -> AgentProfile:
        """Generate profile for specific account."""
        return AgentProfile(
            name=f"{account.pool.value}-{account.id}",
            description=f"{account.pool.value} account {account.id}",
            provider=account.pool.value,  # e.g., "grok_cli"
            role=self._get_role(account),
            allowedTools=self._get_allowed_tools(account),
            model=account.model,
            env_vars=self._get_env_vars(account),  # API keys, OAuth tokens
        )
    
    def _get_role(self, account: Account) -> str:
        """Map account to CAO role."""
        if account.capabilities & {"orchestrate", "delegate"}:
            return "supervisor"
        elif account.capabilities & {"code_gen", "implement"}:
            return "developer"
        elif account.capabilities & {"review", "audit"}:
            return "reviewer"
        return "developer"
    
    def _get_allowed_tools(self, account: Account) -> List[str]:
        """Map capabilities to CAO tool vocabulary."""
        tools = ["@builtin", "@cao-mcp-server"]
        if "code_gen" in account.capabilities:
            tools.extend(["fs_*", "execute_bash"])
        if "web_search" in account.capabilities:
            tools.append("web_fetch")
        if "read_only" in account.capabilities:
            tools = ["fs_read", "fs_list", "@cao-mcp-server"]
        return tools
```

### 3.6 Task Decomposition + Routing Logic

```python
class TaskRouter:
    """Routes tasks to optimal accounts with decomposition."""
    
    async def route(self, task: PoolTask) -> RoutingPlan:
        # 1. Estimate context size from task metadata
        context_estimate = self._estimate_context(task)
        
        # 2. Determine primary pool from routing matrix
        primary_pool = self._select_pool(task.type, context_estimate)
        
        # 3. Select specific account (least loaded, healthy)
        account = await self.registry.get_least_loaded(primary_pool)
        
        # 4. Decompose if parallelizable
        if task.decomposable and context_estimate > 200_000:
            subtasks = self._decompose(task)
            return RoutingPlan(parallel=True, subtasks=subtasks)
        
        return RoutingPlan(parallel=False, account=account)
    
    def _decompose(self, task: PoolTask) -> List[SubTask]:
        """Split large tasks into parallelizable chunks."""
        # Research: split by sub-questions
        # Code: split by files/modules
        # Review: split by severity categories
        ...
```

### 3.7 State Management

```python
@dataclass
class Account:
    id: str                    # e.g., "grok-cli-3"
    pool: PoolType             # GROK | COPILOT | CLINE
    model: str                 # Current model assignment
    context_window: int        # 128K, 512K, 1M
    health: AccountHealth      # HEALTHY | RATE_LIMITED | CREDENTIAL_ERROR | OFFLINE
    rate_limit_remaining: int  # Tokens/minute remaining
    rate_limit_reset: datetime # When limit resets
    last_used: datetime        # For LRU scheduling
    credentials_ref: str       # Omega-Vault reference
    capabilities: Set[str]     # "web_search", "reasoning", "code_gen", etc.
    tmux_session: Optional[str] # Active tmux session name
    mcp_endpoint: Optional[str] # MCP server endpoint for this agent

@dataclass
class PoolTask:
    id: str
    type: TaskType             # DEEP_RESEARCH, CODE_IMPL, etc.
    prompt: str
    context_size_estimate: int
    deadline: Optional[datetime]
    decomposable: bool
    routing_hint: Optional[RoutingHint]
    priority: int              # 0=normal, 1=high, 2=critical
```

---

## 4. Credential Integration (Omega-Vault)

### 4.1 Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    OMEGA-VAULT                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Credential Store (OS keyring + SQLite event log)    │   │
│  │  - 24 entries: grok-cli-1..8, copilot-cli-1..8,     │   │
│  │    cline-cli-1..8                                   │   │
│  │  - Per-account: API key, OAuth tokens, rate limits  │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│          Passive Watcher (fanotify/inotify)                │
│                          ▼                                   │
└──────────────────────────┼──────────────────────────────────┘
                           │
               ┌────────────┴────────────┐
               ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │ Credential      │       │ Pool            │
    │ Watcher         │       │ Orchestrator    │
    │ (subagent_pool) │──────▶│ (credential_    │
    │                 │  push │  watcher)       │
    └─────────────────┘       └─────────────────┘
```

### 4.2 Credential Watcher
```python
class CredentialWatcher:
    """Watches Omega-Vault for credential changes, pushes to pool."""
    
    async def start(self):
        # 1. Initial sync: load all 24 credentials
        await self._initial_sync()
        
        # 2. Watch for changes (fanotify on vault DB + keyring)
        async for event in self.vault.watch():
            if event.type == "credential_rotated":
                await self.orchestrator.registry.update_credentials(
                    event.account_id, event.new_credentials
                )
            elif event.type == "credential_revoked":
                await self.orchestrator.registry.mark_offline(event.account_id)
```

### 4.3 Rotation Strategy
| Pool | Rotation Trigger | Strategy |
|------|------------------|----------|
| Grok CLI | Rate limit (90% threshold) | Sticky → Hybrid → Round-robin |
| Copilot CLI | GitHub quota | Per-account quota tracking |
| Cline CLI | DeepSeek free tier | Per-account, 16k TPM rolling |

### 4.4 tmux Env Var Forwarding (CAO Pattern)
```python
# CAO pattern: forward per-account credentials via tmux env
async def launch_agent(self, account: Account, profile: AgentProfile):
    env_vars = {
        "GROK_API_KEY": account.credentials.api_key,
        "OPENAI_API_KEY": account.credentials.api_key,
        "DEEPSEEK_API_KEY": account.credentials.api_key,
        # CAO allowlist: HOME, PATH, SHELL, CAO_*, KIRO_*, MISE_*, AWS_*
    }
    # Pass via cao launch --env KEY=VALUE (values in request body, not URL)
    await self.tmux_manager.create_session(account, profile, env_vars)
```

---

## 5. Result Aggregation with Cognitive Diversity Weighting

### 5.1 The Diversity Problem
> **Diversity Collapse**: When multiple agents use similar models, they produce correlated errors. Weighting by diversity is essential.

### 5.2 Aggregation Algorithm

```python
class ResultAggregator:
    """Aggregates results from multiple accounts with cognitive diversity weighting."""
    
    async def aggregate(
        self, 
        results: List[AccountResult], 
        task_type: TaskType
    ) -> AggregatedResult:
        
        # 1. Compute capability weights (static per model)
        capability_weights = self._get_capability_weights(results)
        
        # 2. Compute historical accuracy weights (dynamic)
        accuracy_weights = self._get_accuracy_weights(results)
        
        # 3. Compute diversity bonus (penalize correlated outputs)
        diversity_weights = self._compute_diversity_bonus(results)
        
        # 4. Combine: final_weight = capability * accuracy * diversity
        final_weights = {
            r.account_id: c * a * d 
            for (r, c, a, d) in zip(results, capability_weights, accuracy_weights, diversity_weights)
        }
        
        # 5. Weighted synthesis
        synthesis = self._weighted_synthesis(results, final_weights)
        
        # 6. Capture minority dissent
        dissent = self._capture_dissent(results, final_weights)
        
        return AggregatedResult(
            synthesis=synthesis,
            confidence=self._compute_confidence(final_weights),
            minority_dissent=dissent,
            contributing_accounts=list(final_weights.keys())
        )
    
    def _compute_diversity_bonus(self, results: List[AccountResult]) -> Dict[str, float]:
        """Penalize accounts with similar model families."""
        # Embed each result (or use model family as proxy)
        # Compute pairwise similarity
        # Boost weight for unique perspectives
        ...
```

### 5.3 Weighting Factors

| Factor | Source | Weight |
|--------|--------|--------|
| **Model Capability** | Static benchmark scores | 0.4 |
| **Historical Accuracy** | Per-account success rate | 0.3 |
| **Cognitive Diversity** | Model family uniqueness | 0.3 |

---

## 6. Integration Points

### 6.1 MaKaLi Council → Research Gaps
```python
# In MultiAgentCoordinator.run_council()
async def _execute_phase4(self, gaps: List[ResearchGap]):
    for gap in gaps:
        pool_task = PoolTask(
            type=TaskType.DEEP_RESEARCH,
            prompt=gap.question,
            context_size_estimate=gap.context_needed,
            decomposable=True
        )
        future = await self.pool_orchestrator.dispatch(pool_task)
        # Collect asynchronously...
```

### 6.2 Autonomous Meditation → Stage 4 Research
```python
# In AutonomousMeditationPipeline.stage_4_research()
async def execute(self, topic: str):
    pool_task = PoolTask(
        type=TaskType.DEEP_RESEARCH,
        prompt=f"Research: {topic}",
        context_size_estimate=500_000,
        decomposable=True
    )
    # Dispatch to all 3 pools for cognitive diversity
    results = await asyncio.gather(*[
        self.pool_orchestrator.dispatch(pool_task, RoutingHint(pool=p))
        for p in [PoolType.GROK, PoolType.COPILOT, PoolType.CLINE]
    ])
    return self.aggregator.aggregate(results)
```

### 6.3 Hivemind Integration
```python
# Task dispatch via Hivemind handoff
async def dispatch_via_hivemind(self, task: PoolTask) -> str:
    packet = await self.hivemind.submit_handoff(
        target_channel="opencode",
        target_entity="researcher",  # or specific pool agent
        source_channel="opencode",
        source_entity="kali",
        task=task.prompt,
        context=json.dumps(task.to_dict()),
        priority=task.priority
    )
    return packet.packet_id
```

### 6.4 Sovereign Search Tier 4
```python
# Pool as search provider
class PoolSearchProvider:
    """CLI agents as Tier 4 search providers."""
    
    async def search(self, query: str, depth: int) -> SearchResults:
        task = PoolTask(
            type=TaskType.DEEP_RESEARCH,
            prompt=f"Search and synthesize: {query}",
            context_size_estimate=100_000
        )
        result = await self.pool_orchestrator.dispatch(task)
        return SearchResults.from_pool_result(result)
```

### 6.5 Fleet Coordination (CAO Pattern)
```python
# Multi-node fleet coordination (CAO fleet pattern)
class FleetCoordinator:
    """Coordinates pool across multiple machines (CAO fleet pattern)."""
    
    # fleet.json registry (git-ignored)
    # {
    #   "port": 9889,
    #   "machines": [
    #     {"name": "pool-node-1", "host": "100.64.0.11", "role": "grok-pool"},
    #     {"name": "pool-node-2", "host": "100.64.0.12", "role": "copilot-pool"},
    #     {"name": "pool-node-3", "host": "100.64.0.13", "role": "cline-pool"}
    #   ]
    # }
    
    async def fan_out_health_check(self) -> FleetHealthReport:
        """Concurrent health checks with per-node isolation."""
        ...
    
    async def launch_on_node(self, node: str, task: PoolTask) -> PoolResult:
        """Proxy launch to specific fleet node."""
        ...
```

---

## 7. MVP Scope (Week 1-2)

| Week | Deliverable | Owner |
|------|-------------|-------|
| **1** | Pool orchestrator skeleton + account registry + health check | Researcher + P1 |
| **1** | Credential integration with Omega-Vault (read-only) | Researcher + P1 |
| **1** | tmux session management (CAO pattern) | Researcher |
| **1** | MCP coordinator (handoff/assign/send_message) | Researcher |
| **2** | Task dispatch + routing matrix + result collection | Researcher |
| **2** | Hivemind handoff integration | Researcher + P9 |
| **2** | Result aggregator with diversity weighting | Researcher |
| **2** | Test: Parallel deep research across 3 pools | Researcher |

### 7.1 Day-by-Day Plan

| Day | Task |
|-----|------|
| 1 | `src/omega/infra/subagent_pool/` module structure + models |
| 2 | `AccountRegistry` + `HealthMonitor` + mock account data |
| 3 | `TmuxManager` + session lifecycle (CAO pattern) |
| 4 | `MCPCoordinator` with handoff/assign/send_message |
| 5 | `ProfileManager` + cross-provider profiles (CAO pattern) |
| 6 | `TaskRouter` with routing matrix + decomposition logic |
| 7 | `CredentialWatcher` + Omega-Vault integration (read) |
| 8 | `PoolOrchestrator.dispatch()` + `health_check()` |
| 9 | `ResultAggregator` with diversity weighting |
| 10 | Hivemind handoff integration |
| 11 | End-to-end test: 3-pool parallel research task |
| 12 | Load test: 10 concurrent tasks |
| 13 | Documentation + integration with MaKaLi Council |

---

## 8. Mandate Compliance

| Mandate | Compliance Strategy |
|---------|---------------------|
| **M1 AnyIO** | All async via `anyio`, no `asyncio` |
| **M2 Firewall** | Pool in `src/omega/infra/` — no WAD logic |
| **M7 Local-First** | Prefers free tiers (Grok, DeepSeek) over paid |
| **M9 Error Integrity** | Typed errors per account, no silent failures |
| **M11 Soul Integrity** | Pool decisions → session gnosis |
| **M15 Sovereign Continuity** | Account registry persists across sessions |
| **M18 Token Efficiency** | Routing = 70-80% cost optimization |
| **M23 Failure Integrity** | Rate limit = routing signal, not failure; hard stop on credential loss |

---

## 9. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Account ban (ToS)** | Medium | High | 90% soft threshold, established accounts only |
| **Rate limit exhaustion** | High | Medium | Per-account tracking, proactive rebalancing |
| **Credential rotation failure** | Low | High | Omega-Vault passive watcher + push |
| **Diversity collapse** | Medium | High | Explicit diversity weighting in aggregator |
| **Context window overflow** | Medium | Medium | Pre-flight estimation, decomposition |
| **Hivemind handoff latency** | Low | Medium | Async dispatch, local queue fallback |
| **tmux session leak** | Low | High | CAO shutdown pattern, session cleanup on exit |

---

## 10. Future Extensions

1. **Learned Routing**: Train lightweight router on historical task→account performance
2. **Dynamic Pool Scaling**: Spin up/down CLI instances based on queue depth
3. **Cross-Pool Consensus**: Byzantine fault tolerance for critical decisions
4. **SBOM Integration**: Track model versions per account for reproducibility
5. **Cost Dashboard**: Real-time cost tracking per pool, per task type
6. **CAO Fleet Integration**: Multi-machine pool scaling via CAO fleet pattern

---

## 11. Key Files Reference

| File | Purpose |
|------|---------|
| `docs/strategy/HEADLESS_SUBAGENT_POOL_ARCHITECTURE_20260719.md` | This document |
| `src/omega/infra/subagent_pool/` | Implementation (to be created) |
| `config/omega.yaml` | Pool configuration |
| `data/state/subagent_pool_registry.json` | Persistent account state |
| `docs/strategy/VERSION_CHANGE_WATCHDOG_SPEC_20260719.md` | Watchdog uses pool |
| `docs/strategy/MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md` | Council research gaps → pool |
| `docs/strategy/CONSOLIDATED_RESEARCH_INVENTORY_20260719.md` | Task SUBAGENT-01 |

---

## 12. Reference Implementation: AWS CLI Agent Orchestrator (CAO)

| CAO Component | Our Adoption |
|---------------|--------------|
| **tmux isolation** | ✅ Adopted — each account in isolated tmux session |
| **MCP orchestration** | ✅ Adopted — handoff/assign/send_message primitives |
| **Cross-provider profiles** | ✅ Adopted — provider field in agent profiles |
| **Agent profiles (md + YAML)** | ✅ Adopted — markdown + YAML frontmatter |
| **Tool restrictions (role + allowedTools)** | ✅ Adopted — role-based tool access |
| **Memory system (scopes + auto-injection)** | 🔄 Adapted — Omega memory system |
| **Fleet coordinator** | ✅ Adopted — multi-node pool coordination |
| **tmux env var forwarding** | ✅ Adopted — per-account credential forwarding |
| **Control planes (Web UI, CLI, MCP, plugins)** | 🔄 Adapted — Hivemind + Pool CLI |
| **Agent memory (5 scopes)** | 🔄 Adapted — Omega memory scopes |
| **Web UI dashboard** | 🔄 Future — Pool monitoring dashboard |

**CAO Repository**: `https://github.com/awslabs/cli-agent-orchestrator` (920★, Apache-2.0)
**Key Docs**: `README.md`, `docs/control-planes.md`, `docs/memory.md`, `docs/tmux.md`, `docs/agent-profile.md`, `docs/tool-restrictions.md`, `examples/fleet/`

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_headless_pool ⬡ 2026-07-19*