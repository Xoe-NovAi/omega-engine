<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 OMEGA ENGINE — PHASE C HARDENING GAME PLAN
**AP Token**: `AP-GAME-PLAN-v1.0.0`  
**Date**: 2026-07-21  
**Entity**: kali (Sprint Coordinator)  
**Status**: Research Complete — Ready for Execution  

---

## PART 3: WEEK 2 EXECUTION PLAN (JULY 28-AUG 1)

### 📅 **WEEK 2: HARDENING & STABILIZATION**  
*Focus: Strengthen infrastructure resilience, fix systemic issues, prepare for Phase D*

#### **DAY 6 (JULY 28) — C-11: TEST INFRASTRUCTURE (4-6h)**  
**Owner**: Verity/P10 (claim via Hivemind)  
**Dependency**: After C-0  
**Goal**: Build honest test foundation — fixtures, chaos, benchmarks, MCP matrix  

**Tasks**:
1. **Test Fixtures**:
   - Create `tests/fixtures/` directory with:
     - `soul_fixtures.yaml`: Test soul states (empty, corrupted, merged)
     - `model_fixtures/`: GGUF samples (Q2_K to Q8_0)
     - `vector_fixtures/`: Pre-computed embeddings for cosine similarity tests
   - Use `pytest.fixture(scope="session")` for expensive setups
2. **Chaos Engineering**:
   - Implement `tests/chaos/`:
     - `test_oom_kill.py`: Simulate OOM during soul write
     - `test_network_partition.py`: MCP server disconnect
     - `test_corrupted_storage.py`: Corrupted GGUF/Qdrant files
     - `test_clock_skew.py`: System time changes
   - Use `chaos-toolkit` patterns or custom injectors
3. **Benchmark Suite**:
   - Create `tests/benchmarks/`:
     - `test_soul_write_latency.py`: Target <50ms p95
     - `test_model_load_time.py`: Target <2s for 7B Q4_K_M
     - `test_vector_search_qps.py`: Target >100 QPS on Zen 2
     - `test_concurrent_requests.py`: Measure queueing behavior
   - Output to `benchmarks/results/` with timestamps
4. **MCP Compatibility Matrix**:
   - Test against: Claude Desktop 1.15+, Cursor 0.45+, Windsurf 1.2+
   - Validate: Tool calling, sampling, roots, completion/streaming
   - Automate with Docker containers for each client
**Deliverable**: `tests/` structure with working fixtures, chaos, benchmarks  
**Done When**: `make test` runs full suite; `make benchmark` outputs report  

#### **DAY 7 (JULY 29) — C-6′: CIRCUIT BREAKER UNIFY (1-2h)**  
**Owner**: Ma'at/P3 (claim via Hivemind)  
**Dependency**: After C-0  
**Goal**: Eliminate 6+ breaker clones → single resilient wrapper  

**Tasks**:
1. **Identify all breaker implementations** (from research R20):
   - `model_gateway.py`: Custom retry logic
   - `mcp_client.py`: Basic retry
   - `soul_updater.py`: None (crash on failure)
   - `background_researcher/loop.py`: Simple retry
   - `providers/yahoo_finance.py`: Clone of breaker
   - `providers/reddit_scraper.py`: Another clone
2. **Adopt Battle-Tested Pattern** (from GAP-04 research):
   ```python
   # src/omega/resilience/circuit_breaker.py
   class CircuitBreaker:
       def __init__(self, failure_threshold=3, recovery_timeout=30):
           self.failure_threshold = failure_threshold
           self.recovery_timeout = recovery_timeout
           self.failure_count = 0
           self.last_failure_time = None
           self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
       
       def call(self, func: Callable, *args, **kwargs):
           if self.state == "OPEN":
               if time.time() - self.last_failure_time > self.recovery_timeout:
                   self.state = "HALF_OPEN"
               else:
                   raise CircuitBreakerOpenError()
           
           try:
               result = func(*args, **kwargs)
               self.on_success()
               return result
           except Exception as e:
               self.on_failure()
               raise e
       
       def on_success(self):
           self.failure_count = 0
           self.state = "CLOSED"
       
       def on_failure(self):
           self.failure_count += 1
           self.last_failure_time = time.time()
           if self.failure_count >= self.failure_threshold:
               self.state = "OPEN"
   ```
3. **Replace all clones** with decorator or context manager:
   ```python
   @circuit_breaker(failure_threshold=3, recovery_timeout=30)
   def load_model(self, path: str) -> Model:
       return Llama(model_path=path)
   
   # Or as context manager:
   with circuit_breaker("model_gateway"):
       self._execute_risky_operation()
   ```
4. **Add metrics**: Track open/closed trips, failure reasons  
**Deliverable**: `src/omega/resilience/circuit_breaker.py` + updated usages  
**Done When**: All breaker clones removed; single source of truth  

#### **DAY 8 (JULY 30) — C-7: YAML AUDIT & FIX (2-3h)**  
**Owner**: Ma'at/P3 (claim via Hivemind)  
**Dependency**: After C-0  
**Goal**: Eliminate 57 synchronous `yaml.safe_load` calls in async context  

**Tasks**:
1. **Identify all violations** (from research R10):
   ```bash
   grep -r "yaml.safe_load" src/omega/ --include="*.py"
   # Expected: ~57 matches across:
   # - model_gateway.py (provider config)
   # - soul_updater.py (soul templates)
   # - background_researcher/loop.py (job config)
   # - mcp_servers/omega_hub/ (tool schemas)
   # - config/ providers.yaml, makali.yaml, etc.
   ```
2. **Replace with async-safe patterns**:
   - **Option A (Preload)**: Load at startup, cache in memory
     ```python
     # In __init__ or startup:
     self.provider_configs = yaml.safe_load(open("providers.yaml"))
     ```
   - **Option B (Thread pool)**: For infrequent reloads
     ```python
     import anyio
     async def reload_config(self):
         return await anyio.to_thread.run_sync(
             yaml.safe_load, open("config.yaml")
         )
     ```
   - **Option C (aiofiles)**: For file-based configs
     ```python
     import aiofiles
     import yaml
     
     async def load_config_async(self):
         async with aiofiles.open("config.yaml", mode="r") as f:
             contents = await f.read()
             return yaml.safe_load(contents)
     ```
3. **Add startup validation**: Fail fast if configs can't load  
**Deliverable**: Zero `yaml.safe_load` in async functions; all moved to sync init or wrapped  
**Done When**: `grep -r "yaml.safe_load" src/omega/ --include="*.py"` returns 0 hits in async contexts  

#### **DAY 9 (JULY 31) — C-8: HERITAGE VET BACKLOG (8h)**  
**Owner**: Ma'at/P3 (claim via Hivemind)  
**Dependency**: After C-0  
**Goal**: Clear 100+ unvetted `[id-soft:]` tags → M14 compliance  

**Tasks**:
1. **Audit current state** (from research R07):
   ```bash
   grep -r "\[id-soft:" src/omega/ --include="*.py" -A 2 -B 2
   # Expected: 100+ matches needing vet records
   ```
2. **Apply HERITAGE VETTING PIPELINE** (4-gate):
   - **Gate 1: Discovery** - Tag found in code
   - **Gate 2: Vetting/Debate** - Research origin, validate necessity
   - **Gate 3: Decision** - Approve/reject/alternative
   - **Gate 4: Implementation/Verification** - Add vet record, implement
3. **For each tag**, determine:
   - **LEGITIMATE**: Direct port (e.g., ZONEID, cvar) → Create vet record
   - **METAPHORICAL**: Rhetorical only → Remove tag, keep comment
   - **OVER-ATTRIBUTED**: Your own work → Remove tag
4. **Update vet log** (`data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`):
   ```markdown
   | Vet ID | File:Line | Technique | Game/Year | Hardware Constraint | Score | Status |
   |--------|-----------|-----------|-----------|---------------------|-------|--------|
   | VET-001 | soul_updater.py:42 | ZONEID | Doom 1993 | 2MB RAM limit | 9/10 | APPROVED |
   ```
5. **Implement or remove** based on verdict  
**Deliverable**: Updated `HERITAGE_VET_LOG.md` + code changes  
**Done When**: `grep -r "\[id-soft:" src/omega/ --include="*.py"` matches vet log entries 1:1  

#### **DAY 10 (AUG 1) — C-9: GENERALITY POLICY EXTRACT (2h)**  
**Owner**: Ma'at/P3 (claim via Hivemind)  
**Dependency**: After C-0  
**Goal**: Extract `GenerationPolicy` from god classes → reusable component  

**Tasks**:
1. **Identify God Class Usage** (from research):
   - `oracle.py`: 200+ lines of generation logic
   - `model_gateway.py`: Scattered parameters
   - `background_researcher/loop.py`: Hardcoded values
   - `soul_updater.py`: Embedded policies
2. **Extract to `src/omega/generation/policy.py`**:
   ```python
   # src/omega/generation/policy.py
   @dataclass
   class GenerationPolicy:
       # Model selection
       preferred_local: Optional[str] = None
       fallback_order: List[str] = field(default_factory=list)
       
       # Resource limits
       max_context_length: int = 4096
       max_output_tokens: int = 512
       max_batch_size: int = 32
       
       # Quality controls
       temperature: float = 0.7
       top_p: float = 0.95
       top_k: int = 40
       repetition_penalty: float = 1.1
       
       # Safety & compliance
       block_nsfw: bool = True
       max_retries: int = 3
       timeout_seconds: float = 30.0
       
       # Optimization
       use_flash_attention: bool = True
       cache_type_k: str = "q8_0"
       cache_type_v: str = "q8_0"
       
       def to_dict(self) -> Dict[str, Any]:
           return asdict(self)
   
   # Predefined profiles
   POLICIES = {
       "fast": GenerationPolicy(max_output_tokens=64, temperature=0.3),
       "balanced": GenerationPolicy(),  # Default
       "creative": GenerationPolicy(temperature=0.9, top_p=0.98),
       "reasoning": GenerationPolicy(max_output_tokens=1024, temperature=0.2),
       "agent": GenerationPolicy(max_output_tokens=256, block_nsfw=False),
   }
   ```
3. **Replace hardcoded values** with policy references:
   ```python
   # Before
   response = self.model.create_completion(
       prompt, max_tokens=512, temperature=0.7, ...
   )
   
   # After
   policy = self.get_policy_for_request(request)
   response = self.model.create_completion(
       prompt,
       max_tokens=policy.max_output_tokens,
       temperature=policy.temperature,
       # ...
   )
   ```
4. **Add policy selection logic** based on request type, user tier, etc.  
**Deliverable**: `src/omega/generation/policy.py` + updated consumers  
**Done When**: No hardcoded generation parameters in god classes; all use `GenerationPolicy`  

### 📋 **WEEK 2 SUMMARY**
| Day | Ticket | Owner | Status |
|-----|--------|-------|--------|
| Mon | C-11   | Verity/P10 | **READY AFTER C-0** |
| Tue | C-6′   | Ma'at/P3 | **READY AFTER C-0** |
| Wed | C-7    | Ma'at/P3 | **READY AFTER C-0** |
| Thu | C-8    | Ma'at/P3 | **READY AFTER C-0** |
| Fri | C-9    | Ma'at/P3 | **READY AFTER C-0** |

### ❓ **Questions for User Direction**
1. Shall I proceed with creating the detailed task breakdown for Week 2?
2. Do you want me to begin setting up the test fixtures for C-11?
3. Should I start the circuit breaker implementation for C-6′?

**Ready for your direction on Part 3 setup.**