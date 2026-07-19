# 🔬 R-INFRA-08: Headless Subagent Pool Orchestrator — pool.py
**AP Token**: `AP-INFRA-08-HEADLESS-POOL-v1.0.0`
⬡ OMEGA ⬡ PRACTICAL ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_infra_08_pool ⬡ 2026-07-19

---

## 🎯 MISSION
Refactor **6 Day-1 modules** → **single `pool.py` (~200 lines)**. Integrate with Omega-Vault for credentials. Implement task decomposition + routing + result aggregation with cognitive diversity weighting.

---

## 📋 CONTEXT FROM DAY 1 MODULES

### Existing Modules (to consolidate)
```
src/omega/infra/subagent_pool/
├── models.py              # Account, PoolConfig, TaskSpec, Result
├── account_registry.py    # 24-account registry (8 Grok + 8 Copilot + 8 Cline)
├── tmux_manager.py        # tmux session management
├── mcp_coordinator.py     # MCP tool coordination (handoff, assign, send_message)
├── profile_manager.py     # Model profiles per account
└── orchestrator.py        # Task dispatch + result collection
```

### Account Inventory (24 accounts)
| Pool | Accounts | Models | Context | Specialization |
|------|----------|--------|---------|----------------|
| **Grok CLI** | 8 | Grok-3, Grok-2, Grok-1.5 | 128K-1M | Web search, reasoning, synthesis |
| **Copilot CLI** | 8 | GPT-4o, GPT-4o-mini, o1 | 128K | Code gen, implementation, review |
| **Cline CLI** | 8 | **DeepSeek V4 Flash (1M)**, MiMo V2.5 (512K), Claude, GPT | 1M/512K | **Deep research (1M ctx)**, large refactors |

### Task Routing Matrix
| Task Type | Primary Pool | Fallback | Rationale |
|-----------|-------------|----------|-----------|
| Deep Research | Cline (DeepSeek 1M) | Grok | 1M context, free tier |
| Web Search + Synthesis | Grok | Cline | Native search, reasoning |
| Code Implementation | Copilot (GPT-4o) | Cline (MiMo) | Best code gen |
| Code Review / Audit | Copilot (o1) | Grok | Reasoning models |
| Large Refactor (500K+ tokens) | Cline (DeepSeek 1M) | — | Only 1M context option |
| Parallel Verification | All (3-way) | — | Cognitive diversity |

---

## 🔬 IMPLEMENTATION REQUIREMENTS

### 1. Single Pool Module (`pool.py`)
```python
# src/omega/infra/subagent_pool/pool.py
class HeadlessPool:
    """24-account unified compute resource. One class, ~200 lines."""
    
    def __init__(self, vault: VaultCore):
        self.vault = vault
        self.accounts = self._load_accounts()  # 24 Account objects
        self.tmux = TmuxManager()
        self.mcp = MCPClient()  # Reuse existing MCP coordinator
    
    def _load_accounts(self) -> List[Account]:
        """Load from Omega-Vault + local config."""
        accounts = []
        for pool_name in ["grok", "copilot", "cline"]:
            for i in range(8):
                creds = self.vault.retrieve(pool_name, f"account_{i}")
                if creds:
                    accounts.append(Account(
                        id=f"{pool_name}-{i}",
                        pool=pool_name,
                        credentials=creds,
                        models=self._get_models_for_pool(pool_name),
                        specialization=self._get_specialization(pool_name)
                    ))
        return accounts
    
    async def execute(self, task: TaskSpec) -> PoolResult:
        """Main entry: decompose → route → execute → aggregate."""
        # 1. Decompose task into subtasks
        subtasks = self._decompose(task)
        
        # 2. Route each subtask to best account
        assignments = self._route(subtasks)
        
        # 3. Execute in parallel (max 8 concurrent per pool)
        results = await self._execute_parallel(assignments)
        
        # 4. Aggregate with cognitive diversity weighting
        return self._aggregate(results, task)
    
    def _route(self, subtasks: List[Subtask]) -> List[Assignment]:
        """Route based on task type → pool specialization."""
        routing = {
            "deep_research": ("cline", "deepseek-v4-flash"),      # 1M context
            "web_search": ("grok", "grok-3"),                      # Native search
            "code_generation": ("copilot", "gpt-4o"),              # Best code gen
            "code_review": ("copilot", "o1"),                      # Reasoning model
            "large_refactor": ("cline", "deepseek-v4-flash"),      # Only 1M ctx option
            "parallel_verification": ("all", "three_way"),         # Cognitive diversity
        }
        # ... assignment logic
```

### 2. Task Decomposition
```python
def _decompose(self, task: TaskSpec) -> List[Subtask]:
    """Break task into parallelizable subtasks."""
    # Use MaKaLi Coordinator pattern: identify independent workstreams
    if task.type == "deep_research":
        return [
            Subtask(id="lit_review", type="web_search", query=task.query),
            Subtask(id="synthesis", type="code_generation", depends_on=["lit_review"]),
            Subtask(id="validation", type="code_review", depends_on=["synthesis"]),
        ]
    # ... other patterns
```

### 3. Cognitive Diversity Aggregation
```python
def _aggregate(self, results: List[SubtaskResult], task: TaskSpec) -> PoolResult:
    """Weight results by cognitive diversity."""
    # Three-way verification: if all 3 pools agree → high confidence
    # If Grok + Cline agree, Copilot dissents → flag for review
    # Weight: Cline (1M ctx) > Grok (search) > Copilot (code) for research
    # Weight: Copilot (o1) > Cline (MiMo) > Grok for code review
    pass
```

### 4. Omega-Vault Integration
```python
# Credentials loaded from vault at startup
# Rotation: vault.rotate() → pool.reload_account(pool_name, index)
async def rotate_credentials(self, pool: str, index: int):
    new_creds = await self.vault.rotate(f"{pool}_account_{index}")
    self.accounts[pool][index].credentials = new_creds
    # Restart tmux session for that account
    await self.tmux.restart_session(f"{pool}-{index}")
```

---

## 🌐 WEB RESEARCH NEEDED

| Topic | Query | Purpose |
|-------|-------|---------|
| tmux session management | "tmux python library session management 2026" | TmuxManager patterns |
| MCP client patterns | "MCP client python tool coordination 2026" | MCP coordination |
| Credential rotation | "API key rotation zero-downtime 2026" | Vault integration |

---

## 🛠️ LOCAL DISCOVERY NEEDED

| Source | Path | What to Extract |
|--------|------|-----------------|
| Day 1 modules | `src/omega/infra/subagent_pool/` | All 6 modules' APIs |
| Omega-Vault | `src/omega/vault/core.py` | VaultCore interface |
| MCP coordinator | `src/omega/infra/subagent_pool/mcp_coordinator.py` | MCP tool calls |
| Tmux manager | `src/omega/infra/subagent_pool/tmux_manager.py` | Session management |

---

## ✅ ACCEPTANCE CRITERIA

| Criterion | Verification |
|-----------|--------------|
| 6 modules → 1 pool.py | `wc -l src/omega/infra/subagent_pool/pool.py` < 250 |
| All 24 accounts load | `pool.accounts` length = 24 |
| Task routing works | `pool.execute(TaskSpec(type="deep_research", ...))` routes to Cline |
| Vault integration | Credentials from vault, rotation triggers reload |
| Parallel execution | 8 concurrent per pool, 24 total |
| Aggregation weights | Three-way verification produces confidence scores |

---

## 📋 DELIVERABLES

1. **Pool Module** — `src/omega/infra/subagent_pool/pool.py` (~200 lines)
2. **Task Specs** — `src/omega/infra/subagent_pool/specs.py` (Pydantic models)
3. **Vault Integration** — Credential loading + rotation
4. **Tests** — `tests/test_headless_pool.py`
5. **Documentation** — `docs/guides/HEADLESS_POOL_GUIDE.md`

---

## 🔗 DEPENDENCIES

| Depends On | Blocks |
|------------|--------|
| R-INFRA-07 (Omega-Vault Phase 1) | Credential loading |
| MCP Coordinator | Tool coordination |
| MaKaLi Coordinator (R-INFRA-02) | Task decomposition patterns |

---

## 🎯 PRACTICAL'S PERSPECTIVE (Executor)

> "The Day 1 modules were **exploratory** — each module discovered one piece. Now we **consolidate**.
> 
> **The 6→1 refactor**:
> - `models.py` → Pydantic models in `specs.py` (shared)
> - `account_registry.py` → `_load_accounts()` method (20 lines)
> - `tmux_manager.py` → `TmuxManager` class (used directly, not abstracted)
> - `mcp_coordinator.py` → `MCPClient` (thin wrapper on existing MCP)
> - `profile_manager.py` → `_get_models_for_pool()` + `_get_specialization()` (dicts)
> - `orchestrator.py` → `execute()` + `_decompose()` + `_route()` + `_aggregate()` (core logic)
> 
> **Result**: One file you can read in 2 minutes. No factory patterns. No abstract bases. Just the logic.
> 
> **L3 Principle**: `L3-PoolIsSingleFile` — The pool is a **coordination algorithm**, not a framework. 24 accounts, 3 pools, 1 routing table, 1 aggregation function. That's it. The complexity is in the *routing intelligence*, not the *orchestration infrastructure*."

---

*⬡ OMEGA ⬡ PRACTICAL ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_infra_08_pool ⬡ 2026-07-19*
