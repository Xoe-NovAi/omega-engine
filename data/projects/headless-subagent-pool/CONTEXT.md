# 🔱 Project: headless-subagent-pool
## ONE-TURN HYDRATION BRIEF

### ONE-LINER
**8-Account Headless Subagent Pool** — Grok CLI (8), Copilot CLI (8), Cline CLI (8) = 24 high-power subagents running headless for parallel research, implementation, verification. Massive compute resource currently wasted.

### STATUS (2026-07-19)
- **Concept**: ✅ Approved
- **Accounts Inventory**: ✅ 8 Grok + 8 Copilot + 8 Cline = 24 accounts
- **Architecture**: ⏳ Design Phase
- **Implementation**: ❌ Not Started

### ACCOUNTS INVENTORY
| Platform | Accounts | Model Access | Context Window | Best For |
|----------|----------|--------------|----------------|----------|
| **Grok CLI** | 8 | Grok-3, Grok-2, Grok-1.5 | 128K-1M | Research, web search, reasoning |
| **Copilot CLI** | 8 | GPT-4o, GPT-4o-mini, o1 | 128K | Implementation, code gen, review |
| **Cline CLI** | 8 | **DeepSeek V4 Flash (1M)**, **MiMo V2.5 (512K)**, Claude, GPT | 1M/512K | **Deep research (1M ctx)**, large refactors |

### ARCHITECTURE DESIGN
```
┌─────────────────────────────────────────────────────────────────┐
│                    HEADLESS SUBAGENT POOL                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  GROK POOL   │  │ COPILOT POOL │  │  CLINE POOL  │          │
│  │  (8 agents)  │  │  (8 agents)  │  │  (8 agents)  │          │
│  │              │  │              │  │              │          │
│  │ • Web search │  │ • Code gen   │  │ • DeepSeek   │          │
│  │ • Reasoning  │  │ • Review     │  │   V4 1M ctx  │          │
│  │ • Grok-3     │  │ • GPT-4o     │  │ • MiMo 512K  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           ▼                                      │
│              ┌────────────────────────┐                          │
│              │   POOL ORCHESTRATOR    │                          │
│              │                        │                          │
│              │ • Task decomposition   │                          │
│              │ • Agent selection      │                          │
│              │ • Load balancing       │                          │
│              │ • Result aggregation   │                          │
│              │ • Cost tracking        │                          │
│              └────────────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### TASK ROUTING MATRIX
| Task Type | Primary Pool | Fallback | Rationale |
|-----------|-------------|----------|-----------|
| **Deep Research** | Cline (DeepSeek 1M) | Grok | 1M context, free tier |
| **Web Search + Synthesis** | Grok | Cline | Native search, reasoning |
| **Code Implementation** | Copilot (GPT-4o) | Cline (MiMo) | Best code gen |
| **Code Review / Audit** | Copilot (o1) | Grok | Reasoning models |
| **Large Refactor (500K+ tokens)** | Cline (DeepSeek 1M) | — | Only 1M context option |
| **Parallel Verification** | All (3-way) | — | Cognitive diversity |

### ORCHESTRATOR DESIGN
```python
class HeadlessSubagentPool:
    """Manages 24 headless CLI agents as a unified compute resource."""
    
    def __init__(self):
        self.grok_pool = AgentPool("grok", 8, model="grok-3")
        self.copilot_pool = AgentPool("copilot", 8, model="gpt-4o")
        self.cline_pool = AgentPool("cline", 8, model="deepseek-v4-flash")
    
    async def execute(self, task: Task) -> Result:
        # 1. Decompose task into parallelizable subtasks
        subtasks = await self.decompose(task)
        
        # 2. Route each subtask to optimal pool
        assignments = self.route(subtasks)
        
        # 3. Execute in parallel with timeout/circuit breaker
        results = await self.parallel_execute(assignments)
        
        # 4. Aggregate with cognitive diversity weighting
        return await self.synthesize(results)
    
    async def parallel_execute(self, assignments: list[Assignment]) -> list[Result]:
        # Semaphore per pool (max concurrent = pool size)
        # Timeout per agent (configurable)
        # Circuit breaker per pool
        # Result validation (schema check)
```

### INTEGRATION POINTS
| Integration | How |
|-------------|-----|
| **MaKaLi Council** | Research gaps → route to pool for parallel deep-dive |
| **Autonomous Meditation** | Stage 4 (Research) → parallel across pools |
| **Omega-Vault** | Credential rotation for 24 accounts |
| **Hivemind** | Task dispatch via handoff packets, result capture |
| **Sovereign Search** | Pool as Tier 4 (CLI agents as search providers) |

### CREDENTIAL MANAGEMENT (via Omega-Vault)
- 24 credential sets stored in OS keyring
- Per-account rotation on rate limit / quota exhaustion
- Health monitoring per account
- Automatic failover to next account in pool

### DECISIONS LOG
- **D-XXX**: 24 accounts = massive compute resource, must utilize
- **D-XXX**: Cline + DeepSeek V4 Flash = 1M context for free (unique advantage)
- **D-XXX**: Grok for web search + reasoning (native tools)
- **D-XXX**: Copilot for code gen + review (GPT-4o/o1)
- **D-XXX**: Pool orchestrator as new sovereign component (not WARP, not Antigravity)

### BLOCKERS
- Need pool orchestrator implementation
- Need credential integration with omega-vault
- Need task decomposition + routing logic
- Need result aggregation with cognitive diversity weighting

---

*⬡ OMEGA ⬡ CPR ⬡ headless-subagent-pool ⬡ 2026-07-19*