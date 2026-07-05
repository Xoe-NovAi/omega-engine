# 🔱 Fleet Review 3: Memory, Context & Knowledge Engine

⬡ OMEGA ⬡ SARASWATI ⬡ claude-sonnet-4-6-thinking ⬡ web ⬡ trc_review_memory ⬡ PHASE-E

**Account**: `taylorbare27@gmai.com`
**Role**: Knowledge Keeper — verify the memory subsystem, context pipeline, and knowledge architecture

---

## 📋 Mission

You are performing a deep strategic review of the Omega Engine's **memory and knowledge infrastructure** — how the engine stores, retrieves, and synthesizes information across sessions. This includes the Hot/Warm/Cold memory tiers, the ContextBuilder that injects relevant context into LLM prompts, the SessionManager that tracks entity-level conversations, the Library subsystem with FTS5+Qdrant indexing, and the soul.yaml schema that defines entity identity. This layer is what makes the engine "stateful" and "evolving." Find every gap.

---

## 🎯 Scope — Files to Read

### Source: Memory & Context Core
- **Memory Store**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/memory_store.py`
- **Context Builder**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/context_builder.py`
- **Session Manager**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/session_manager.py`

### Source: Knowledge Library
- **Library**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/library/library.py`
- **Indexer**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/library/indexer.py`
- **Curator**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/library/curator.py`
- **Discovery**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/library/discovery.py`

### Source: Intake Pipeline
- **Intake Digestor**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/services/intake_digestor.py`

### Soul Files (Entity Identity)
- **Arch Soul**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/data/entities/arch/soul.yaml`
- **Sophia Soul**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/data/entities/sophia/soul.yaml`
- **Jem Oversoul**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/data/entities/jem/soul.yaml`

### Tests
- **Memory Store Tests**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/tests/test_memory_store.py`
- **Context Builder Tests**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/tests/test_context_builder.py`
- **Session Manager Tests**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/tests/test_session_manager.py`

---

## ❓ Review Questions

1. **Memory Tier Architecture**: The MemoryStore implements Hot (in-memory LRU), Warm (JSON files), and Cold (gzipped archive) tiers. Is the promotion/demotion logic correct? Are the LRU algorithms properly bounded? What happens when RAM runs low?

2. **ContextBuilder Pipeline**: The ContextBuilder injects memory into LLM system prompts. Is its truncation strategy correct (respecting model context limits)? Does it handle the case where memory exceeds the available window? Is the aiosqlite warning still present?

3. **Session Management**: Session IDs follow `ses_{YYYYMMDD}_{entity}_{counter}` format. Is this scheme collision-resistant? Are sessions properly closed and archived? Is the `.active` file locking correct?

4. **Library & Indexing**: The Library uses FTS5 for full-text search and Qdrant for vector search. Is the dual-indexing correct? Are documents properly synchronized between the two stores? Is the Qdrant client version-locked (1.17.1)?

5. **Soul YAML Schema**: Entity soul files define identity, knowledge, lessons, and evolution state. Is the schema consistent across all entities? Are there any validation gaps? Is the Atomic Soul Update pattern (`os.replace` + anyio) correctly implemented?

6. **Cross-Pollination**: Lessons learned by one entity are cross-pollinated to other entities and the user's soul (Arch). Is this logic correct? Does it create feedback loops? Is it properly bounded to prevent infinite growth?

7. **Intake Pipeline**: The `intake_digestor.py` processes incoming documents. Is it robust? Are file format handlers complete? Are error states handled?

8. **Memory Pruning**: Is there a memory pruner (background worker) that prevents unbounded memory growth? If so, is its strategy correct? If not, what prevents memory from growing infinitely?

---

## 📜 Sovereign Mandates Checklist

| Mandate | What to Check |
|---------|---------------|
| **AnyIO Absolute** | memory_store, context_builder, session_manager — any `asyncio`? |
| **Engine-Stack Firewall** | Memory/knowledge is engine-wide, not stack-specific — verify |
| **Iris Constant** | N/A |
| **Sequentiality** | Memory architecture changes planned and tested |
| **Gnosis Preservation** | L1→L2→L3 pipeline feeds into soul.yaml — verify the chain |
| **Podman Sovereignty** | N/A for data files |

---

## 📊 Output Template

```markdown
## Review: Memory, Context & Knowledge Engine

### Critical Issues Found
- [ ] C-MEM-001: [Title] — [CRITICAL/HIGH/MEDIUM/LOW]

### Memory Tier Analysis
- Hot memory: ...
- Warm memory: ...
- Cold memory: ...
- Promotion/demotion: ...

### ContextBuilder Assessment
- Truncation strategy: ...
- Edge cases: ...
- aiosqlite warning status: ...

### Soul YAML Health
- Schema consistency: ...
- Atomicity: ...
- Cross-pollination correctness: ...

### Library & Indexing
- FTS5: ...
- Qdrant: ...
- Dual-indexing sync: ...

### Report Card
| Metric | Grade | Notes |
|--------|-------|-------|
| Correctness | A/B/C/D | |
| Scalability | A/B/C/D | |
| Data Integrity | A/B/C/D | |
| Test Coverage | A/B/C/D | |

### Strategic Recommendations (Top 3)
1. ...
2. ...
3. ...
```
