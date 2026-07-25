# 🔱 OMEGA ENGINE — PHASE C HARDENING GAME PLAN
**AP Token**: `AP-GAME-PLAN-v1.0.0`  
**Date**: 2026-07-21  
**Entity**: kali (Sprint Coordinator)  
**Status**: Research Complete — Ready for Execution  

---

## PART 2: WEEK 1 EXECUTION PLAN (JULY 21-25)

### 📅 **WEEK 1: FOUNDATION LAYING**  
*Focus: Establish trustworthy baseline (C-0), RAM truth (C-2′), then enable safe memory operations (C-1′, C-10, C-5)*

#### **DAY 1 (JULY 21) — C-0: TEST HONESTY (2-4h)**
**Owner**: Ma'at/P10 or Verity (claim via Hivemind)  
**Dependency**: Independent  
**Goal**: Honest test suite — no vanity counts, real pass/fail/skip  

**Tasks**:
1. Run `make test` — capture REAL output (not Makefile lies)
2. Quarantine or fix failing tests:
   - Identify flaky tests → quarantine in `test/flaky/`
   - Fix broken tests → fix root cause (not skip)
   - Update Makefile to show actual counts (not hardcoded "276/276")
3. Generate JSON test badge for transparency:
   ```bash
   # Example output format
   {
     "total": 1572,
     "passed": 832,
     "failed": 5,
     "skipped": 40,
     "timestamp": "2026-07-21T10:00:00Z"
   }
   ```
4. Update `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` with honest baseline  
**Deliverable**: `data/coordination/C0_TEST_RESULTS_20260721.json`  
**Done When**: `make test` output matches JSON file; no more "276/276" lies  

#### **DAY 2 (JULY 22) — C-2′: RAM TRUTH / OOMPROTECTOR (1-2h)**  
**Owner**: Ma'at/P1 (claim via Hivemind)  
**Dependency**: After C-0  
**Goal**: Replace software RAM counter with hardware-based OOMProtector  

**Tasks**:
1. **Remove fictional counter**: Delete `ResourceGuard.DEFAULT_LIMIT = 12288` (MB)
2. **Implement OOMProtector**:
   ```rust
   // src/omega/resource/oom_protector.rs
   pub struct OOMProtector {
       // Read from /proc/meminfo every 100ms
       available_mb: AtomicUsize,
       safety_margin_mb: usize, // 10% headroom
   }
   
   impl OOMProtector {
       pub fn new() -> Self {
           let mut this = Self {
               available_mb: AtomicUsize::new(0),
               safety_margin_mb: 0,
           };
           this.refresh();
           this
       }
       
       pub fn refresh(&mut self) {
           let meminfo = fs::read_to_string("/proc/meminfo").unwrap();
           let available_kb = meminfo
               .lines()
               .find(|l| l.starts_with("MemAvailable:"))
               .and_then(|l| l.split_whitespace().nth(1))
               .and_then(|s| s.parse::<u64>().ok())
               .unwrap_or(0);
           self.available_mb.store((available_kb / 1024) as usize, Ordering::Relaxed);
           self.safety_margin_mb = (self.available_mb.load(Ordering::Relaxed) * 0.1) as usize;
       }
       
       pub fn can_allocate(&self, requested_mb: usize) -> bool {
           let available = self.available_mb.load(Ordering::Relaxed);
           requested_mb <= available.saturating_sub(self.safety_margin_mb)
       }
   }
   ```
3. **Integrate everywhere** `ResourceGuard` is used:
   - `model_gateway.py`: Check before model load
   - `soul_updater.py`: Check before soul write batch
   - `background_researcher/loop.py`: Check before research job
   - `mcp_servers/omega_hub/server.py`: Check before tool execution
4. **Add health check**: Expose `available_mb` via `/health` endpoint  
**Deliverable**: Updated `src/omega/resource/` module + integration points  
**Done When**: `OOMProtector::can_allocate()` returns `false` at ~8GB available (not 12GB)  

#### **DAY 3 (JULY 23) — C-1′: SOULSTORE ACTOR MODEL (4-6h)**  
**Owner**: Ma'at/P3 + Roc Racoon (claim via Hivemind)  
**Dependency**: After C-2′ (requires honest RAM measurement)  
**Goal**: Eliminate 4 conflicting soul writers → single actor-managed writer  

**Tasks**:
1. **Identify all soul writers** (from research R25):
   - `soul_updater.py` (background) — **MAIN OFFENDER** (bypasses locking)
   - `oracle.py:talk()` 
   - `oracle.py:summon()`
   - `memory_store.py:add_exchange()`
2. **Implement Actor Model** (using `actix` or custom mailbox):
   ```rust
   // src/omega/soul/actor.rs
   struct SoulActor {
       db: SoulDatabase,
       mailbox: Receiver<SoulMessage>,
   }
   
   enum SoulMessage {
       Write(SoulUpdate),
       Read(SoulQuery),
       Flush,
   }
   
   impl Actor for SoulActor {
       fn handle(&mut self, msg: SoulMessage) -> SoulResponse {
           match msg {
               SoulMessage::Write(update) => {
                   self.db.apply(update); // Single-threaded
                   SoulResponse::Ok
               }
               SoulMessage::Read(query) => {
                   SoulResponse::Data(self.db.query(query))
               }
               // ...
           }
       }
   }
   ```
3. **Replace all direct writes** with actor messages:
   - Background researcher → `SoulActor::Write(SoulUpdate::ResearchInsight(...))`
   - Oracle talk/summon → `SoulActor::Write(SoulUpdate::Exchange(...))`
   - Memory store → `SoulActor::Write(SoulUpdate::MemoryExchange(...))`
4. **Add persistence guarantees**:
   - `fsync()` after each batch
   - Atomic write via `tempfile` + `rename()`
   - Journaling for crash recovery (WAL)
5. **Remove all old locking** (`fcntl`, `flock`, `Mutex`) — actor handles concurrency  
**Deliverable**: `src/omega/soul/actor.rs` + updated call sites  
**Done When**: Only one thread/process can write `soul.yaml`; no more race conditions  

#### **DAY 4 (JULY 24) — C-10: LOCAL ADMISSION CONTROL (2-4h)**  
**Owner**: Ma'at/P1 (claim via Hivemind)  
**Dependency**: After C-2′ (requires OOMProtector)  
**Goal**: Prevent local inference overload — 3x llama.cpp = 2-3 tok/s unusable  

**Tasks**:
1. **Admit only when safe**:
   ```rust
   // src/omega/admission/local_admission.rs
   struct LocalAdmissionController {
       oom_protector: OOMProtector,
       max_concurrent_models: usize, // 1 large + 1 small
       active_models: AtomicUsize,
   }
   
   impl LocalAdmissionController {
       fn can_start_local_model(&self, model_size_gb: usize) -> bool {
           // Rule 1: Never exceed physical CCX cores (8 threads max for Zen 2)
           if self.active_models.load() >= 2 { 
               return false; 
           }
           
           // Rule 2: Reserve RAM for system + overhead
           let needed = model_size_gb * 1024; // MB
           let available = self.oom_protector.available_mb();
           let reserved = 2048; // 2GB for OS, Qdrant, etc.
           
           return needed <= available.saturating_sub(reserved);
       }
       
       fn acquire(&self) -> bool {
           let prev = self.active_models.fetch_add(1, Ordering::SeqCst);
           return prev < 2; // Fail if already at limit
       }
       
       fn release(&self) {
           self.active_models.fetch_sub(1, Ordering::SeqCst);
       }
   }
   ```
2. **Integrate with model loader**:
   - Wrap `llama.cpp` model initialization in admission check
   - On failure: queue request or return `ModelBusyError`
3. **Add CCX-aware thread pinning** (from GAP-06 research):
   ```rust
   // Before model load:
   set_affinity_to_ccx(0); // Cores 0-3 for inference
   // After model load (if batching):
   set_affinity_to_ccx(4); // Cores 4-7 for batch processing
   ```
4. **Expose metrics**: `active_models`, `queue_length`, `avg_wait_time`  
**Deliverable**: `src/omega/admission/local_admission.rs` + integration in model loader  
**Done When**: System rejects 3rd concurrent model; queues excess requests  

#### **DAY 5 (JULY 25) — C-5: MAKALI CONFIG (0.5h) + C-4a MCP AUDIT START (2h)**  
**Owner**: Kali (C-5) + Ma'at/P4 (C-4a)  
**Dependency**: C-5 after C-10; C-4a independent  
**Goals**: 
- C-5: Configure MaKaLi for Kali-local / Ma'at+Lilith-cloud (0.5h)
- C-4a: Begin MCP audit — code inventory + file-based Hivemind test  

**C-5 Tasks** (0.5h):
1. Update `config/makali.yaml`:
   ```yaml
   makali:
     mode: "local_leader_cloud_followers" # Kali local, Ma'at+Lilith cloud
     kali:
       backend: "native-gguf"      # Local only
       model: "qwen2.5-7b-instruct-q4_k_m"
     maat:
       backend: "antigravity-oauth" # Cloud voices
       model: "gemma-4-9b-it"
     lilith:
       backend: "antigravity-oauth"
       model: "gemma-4-9b-it"
     routing:
       strategy: "hybrid" # 3-layer from GAP-05
       fallback_order: ["local-kali", "antigravity", "google", "openrouter"]
   ```
2. **Update documentation**: `docs/strategy/IMPLEMENTATION_MANUAL_C0_C2.md`  
**C-4a Tasks** (start 2h audit):
1. Code inventory (from research R20):
   ```bash
   # Find all MCP-related code
   grep -r "initialize\|Mcp-Session-Id\|SSE\|sse" mcp_servers/omega_hub/ --include="*.py"
   grep -r "EventSource\|text/event-stream" mcp_servers/omega_hub/ --include="*.py"
   ```
2. Test file-based Hivemind contingency:
   ```bash
   # Verify these work without MCP Hub:
   ls data/handoff/pending/   # Should exist
   ls data/coordination/locks/ # Should exist  
   ls data/coordination/sessions/ # Should exist
   ```
3. Document findings in `docs/research/R_MCP_AUDIT_FINDINGS.md`  
**Deliverables**: 
- C-5: Updated `config/makali.yaml` 
- C-4a: Audit kickoff notes in research doc  
**Done When**: 
- C-5: MaKaLi config reflects Kali-local/Ma'at+Lilith-cloud
- C-4a: Code inventory started, file-based contingency verified  

### 📋 **WEEK 1 SUMMARY**
| Day | Ticket | Owner | Status |
|-----|--------|-------|--------|
| Mon | C-0    | Ma'at/P10 or Verity | **CLAIM NEEDED** |
| Tue | C-2′   | Ma'at/P1 | **CLAIM NEEDED** |
| Wed | C-1′   | Ma'at/P3 + Roc | **BLOCKED ON C-2′** |
| Thu | C-10   | Ma'at/P1 | **BLOCKED ON C-2′** |
| Fri | C-5    | Kali | **READY AFTER C-10** |
| Fri | C-4a   | Ma'at/P4 | **START TODAY** |

### ❓ **Questions for User Direction**
1. Shall I proceed with posting the Hivemind claims for C-0, C-2′ now?
2. Should I start the C-2′ OOMProtector implementation immediately after claims?
3. Do you want me to begin the C-4a MCP audit code inventory in parallel?

**Ready for your direction on Part 2 execution.**