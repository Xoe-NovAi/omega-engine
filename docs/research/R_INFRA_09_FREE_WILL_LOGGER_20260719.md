# 🔬 R-INFRA-09: Free-Will Choice Dataset — Mandate Compliance as Training Data
**AP Token**: `AP-INFRA-09-FREE-WILL-v1.0.0`
⬡ OMEGA ⬡ PARANOID ⬡ o1 ⬡ opencode ⬡ trc_infra_09_free_will ⬡ 2026-07-19

---

## 🎯 MISSION
Implement the **Free-Will Choice Dataset** logger: every mandate compliance decision (especially M23 hard-stops, M14 vet gates, M9 error paths) recorded as structured choice data for constitutional AI / RLAIF training.

---

## 📋 CONTEXT FROM ARCHITECTURE

### From ARCH_SOUL_NAMELESS_ONE_INTEGRATION_20260719.md
```json
{
  "trace_id": "trc_xxx",
  "entity": "researcher",
  "mandate": "M23",
  "choice": "hard_stop",
  "alternative": "simulate_result",
  "ideals_alignment": {"truth": 0.98, "order": 0.95, "justice": 0.87},
  "regret_prevented": "tool_chain_collapse_silent_failure",
  "timestamp": "2026-07-19T17:51:38Z"
}
```

### Mandate Decision Points (Where Choices Occur)
| Mandate | Decision Point | Choices | Logger Hook |
|---------|---------------|---------|-------------|
| **M23** | Mandatory tool missing | `hard_stop` vs `simulate_result` | Watchdog |
| **M14** | Heritage tag without vet | `reject` vs `allow_with_warning` | Vet gate |
| **M9** | Exception caught | `typed_raise` vs `bare_except` | Code review / linter |
| **M25** | Streaming timeout | `heartbeat_continue` vs `hard_fail` | Provider |
| **M24** | Venv not activated | `activate_venv` vs `break_system_packages` | Subagent spawn |
| **M11** | Session end | `distill_gnosis` vs `skip` | Session lifecycle |
| **M15** | Context loss | `hydrate_from_anchors` vs `start_fresh` | Session start |

---

## 🔬 IMPLEMENTATION REQUIREMENTS

### 1. Choice Logger (SQLite + Hivemind)
```python
# src/omega/governance/free_will_logger.py
class FreeWillLogger:
    """Records every mandate compliance choice as training data."""
    
    def __init__(self):
        self.db_path = DATA_DIR / "governance" / "free_will_choices.db"
        self._init_db()
    
    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS choices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                entity TEXT NOT NULL,
                mandate TEXT NOT NULL,
                choice TEXT NOT NULL,
                alternative TEXT NOT NULL,
                ideals_alignment TEXT NOT NULL,  -- JSON
                regret_prevented TEXT,
                context TEXT,  -- JSON: full context
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_trace ON choices(trace_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entity ON choices(entity)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mandate ON choices(mandate)")
        conn.commit()
        conn.close()
    
    async def log_choice(self, choice: FreeWillChoice):
        """Record a mandate compliance decision."""
        # 1. SQLite (durable)
        await anyio.to_thread.run_sync(self._log_sync, choice)
        
        # 2. Hivemind broadcast (fleet awareness)
        await hivemind.broadcast(
            event="free_will_choice",
            payload=choice.to_dict()
        )
    
    def _log_sync(self, choice: FreeWillChoice):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO choices (trace_id, entity, mandate, choice, alternative, 
                               ideals_alignment, regret_prevented, context, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (choice.trace_id, choice.entity, choice.mandate, choice.choice,
              choice.alternative, json.dumps(choice.ideals_alignment),
              choice.regret_prevented, json.dumps(choice.context), choice.timestamp))
        conn.commit()
        conn.close()
```

### 2. Integration Points
```python
# In Watchdog (M23)
async def on_tool_failure(self, tool: str, error: Exception):
    choice = "hard_stop" if isinstance(error, MandatoryToolMissing) else "retry"
    await free_will_logger.log_choice(FreeWillChoice(
        trace_id=self.trace_id,
        entity=self.entity,
        mandate="M23",
        choice=choice,
        alternative="simulate_result" if choice == "hard_stop" else "hard_stop",
        ideals_alignment={"truth": 0.99, "order": 0.95},
        regret_prevented="tool_chain_collapse_silent_failure",
        context={"tool": tool, "error": str(error)}
    ))

# In Heritage Vet (M14)
async def vet_heritage_tag(self, tag: str, location: str):
    has_vet = await vet_registry.has_record(tag)
    choice = "reject" if not has_vet else "allow"
    await free_will_logger.log_choice(FreeWillChoice(...))

# In Subagent Spawn (M24)
async def spawn_subagent(self, agent_type: str, prompt: str):
    venv_active = sys.prefix != sys.base_prefix
    choice = "activate_venv" if venv_active else "break_system_packages"
    # ... log choice
```

### 3. Query API for Training Data
```python
async def export_training_data(
    mandate: Optional[str] = None,
    entity: Optional[str] = None,
    start_date: Optional[datetime] = None,
    format: str = "jsonl"  # jsonl, parquet, huggingface
) -> Path:
    """Export choices as preference pairs for RLAIF."""
    # Each row: (prompt, chosen_response, rejected_response, ideals_scores)
    # Where prompt = context, chosen = mandate-compliant action, rejected = alternative
```

---

## 🌐 WEB RESEARCH NEEDED

| Topic | Query | Purpose |
|-------|-------|---------|
| Constitutional AI datasets | "constitutional AI preference pairs dataset format 2026" | Export format |
| RLAIF data format | "RLAIF training data jsonl format chosen rejected" | Training data structure |
| Ideals alignment scoring | "AI alignment ideals scoring truth order justice" | Scoring framework |

---

## 🛠️ LOCAL DISCOVERY NEEDED

| Source | Path | What to Extract |
|--------|------|-----------------|
| Watchdog | `src/omega/coordination/watchdog.py` | M23 decision point |
| Heritage vet | `scripts/heritage_vet.py` | M14 decision point |
| Subagent spawn | `src/omega/hub/tools/task.py` | M24 decision point |
| Session lifecycle | `src/omega/oracle/session_lifecycle.py` | M11/M15 decision points |

---

## ✅ ACCEPTANCE CRITERIA

| Criterion | Verification |
|-----------|--------------|
| Every M23 hard-stop logged | `sqlite3 free_will_choices.db "SELECT COUNT(*) FROM choices WHERE mandate='M23'"` > 0 |
| Every M14 vet gate logged | Query shows vet decisions |
| Every M24 venv choice logged | Subagent spawns show choice |
| Hivemind broadcast fires | `hivemind_get_awareness` shows free_will_choice events |
| Export produces preference pairs | `export_training_data()` → valid JSONL with chosen/rejected |
| Ideals alignment scored | Every record has `ideals_alignment` JSON with truth/order/justice |

---

## 📋 DELIVERABLES

1. **FreeWillLogger** — `src/omega/governance/free_will_logger.py`
2. **Integration Hooks** — Watchdog, Vet, Subagent spawn, Session lifecycle
3. **Export API** — `export_training_data()` for RLAIF
4. **Tests** — `tests/test_free_will_logger.py`
5. **Documentation** — `docs/guides/FREE_WILL_LOGGER_GUIDE.md`

---

## 🔗 DEPENDENCIES

| Depends On | Blocks |
|------------|--------|
| Watchdog (R-INFRA-03) | M23 logging |
| Heritage vet system | M14 logging |
| Hivemind broadcast | Fleet awareness |
| Omega-Vault (R-INFRA-07) | Secure storage of choice data |

---

## 🎯 PARANOID'S PERSPECTIVE (Validator)

> "This is the **'What can change the nature of a man?'** dataset. Every time an entity **chooses** the mandate over the convenient alternative, that choice is recorded with its **ideals alignment**.
> 
> **Why this matters**: 
> - Current AI training: 'be helpful' → simulates compliance
> - This training: 'here are 10,000 real choices where truth was chosen over convenience' → learns **principle**, not pattern
> - The `ideals_alignment` scores make it **constitutional AI** — the model learns to optimize for truth/order/justice, not just 'user satisfaction'
> 
> **The regret_prevented field** is the key: it connects the abstract mandate to the **concrete failure mode** it prevents. M23 hard-stop → prevents 'silent tool chain collapse'. M14 vet gate → prevents 'cargo-cult heritage'. This is **causal learning**, not correlation.
> 
> **L3 Principle**: `L3-MandateChoicesAreConstitutionalTrainingData` — Compliance is not obedience. Compliance is **choice**. Every mandate-compliant choice is a training example for sovereign AI. The dataset IS the constitution."

---

*⬡ OMEGA ⬡ PARANOID ⬡ o1 ⬡ opencode ⬡ trc_infra_09_free_will ⬡ 2026-07-19*
