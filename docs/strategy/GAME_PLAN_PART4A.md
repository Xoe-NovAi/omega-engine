# 🔱 OMEGA ENGINE — PHASE C HARDENING GAME PLAN
**AP Token**: `AP-GAME-PLAN-v1.0.0`  
**Date**: 2026-07-21  
**Entity**: kali (Sprint Coordinator)  
**Status**: Research Complete — Ready for Execution  

---

## PART 4A: WEEK 3 EXECUTION PLAN (AUG 4-8) & TECHNICAL DEEP DIVES

### 📅 **WEEK 3: PHASE D PREPARATION**  
*Focus: Resolve architectural decisions, implement Phase D prerequisites, validate readiness*

#### **DAY 11 (AUG 4) — C-3: PRIVACY MODEL DECISION & IMPLEMENTATION**  
**Owner**: Kali + Architect  
**Dependency**: After C-0, C-1′, C-2′  
**Goal**: Implement Tiered Sovereignty Model for soul.yaml privacy vs. safety  

**Tasks** (if Architect approves Tiered Sovereignty):
1. **Define the 4 Tiers**:
   ```yaml
   # config/soul_privacy.yaml
   privacy_tiers:
     LEVEL_1_NORMAL:  # Daily operations
       description: "Full sovereignty - local only, zero telemetry"
       local_inference_only: true
       allow_cloud_fallback: false
       data_collection: "none"
       audit_level: "minimal"
       
     LEVEL_2_ELEVATED:  # Elevated risk (crisis indicators)
       description: "Local + pre-authorized contacts, limited telemetry"
       local_inference_only: true
       allow_cloud_fallback: false  # Still no cloud for inference
       emergency_contacts_enabled: true
       data_collection: "metadata_only"  # Timestamps, frequency, not content
       audit_level: "standard"
       
     LEVEL_3_IMMINENT:  # Imminent danger (verified crisis)
       description: "Break-glass - pre-authorized emergency only"
       local_inference_only: true
       allow_cloud_fallback: false
       emergency_contacts_enabled: true
       data_collection: "limited"  # Minimal necessary for intervention
       audit_level: "detailed"
       auto_notify_trusted_contacts: true
       
     LEVEL_4_LEGAL:  # Court-ordered or mandatory reporting
       description: "Legal compliance mode - audit trail preserved"
       local_inference_only: true
       allow_cloud_fallback: false
       data_collection: "full_for_audit"  # Encrypted, access-logged
       audit_level: "forensic"
       legal_hold: true
       notify_after_24h: true  # Tell user after legal window
   ```
2. **Implement Sovereignty Gatekeeper**:
   ```python
   # src/omega/soul/privacy_gate.py
   class SovereigntyGate:
       def __init__(self):
           self.current_level = PrivacyLevel.LEVEL_1_NORMAL
           self._load_policies()
       
       def evaluate_request(self, request: SoulRequest) -> PrivacyLevel:
           # Assess risk factors
           risk_score = self._assess_risk(request)
           
           if risk_score >= 0.9 and self._is_imminent_crisis(request):
               return PrivacyLevel.LEVEL_3_IMMINENT
           elif risk_score >= 0.7:
               return PrivacyLevel.LEVEL_2_ELEVATED
           elif self._has_legal_order():
               return PrivacyLevel.LEVEL_4_LEGAL
           else:
               return PrivacyLevel.LEVEL_1_NORMAL
       
       def apply_restrictions(self, level: PrivacyLevel, action: SoulAction) -> bool:
           policy = self.policies[level]
           if not policy.local_inference_only and self._requires_cloud(action):
               return False  # Block cloud call
           if not policy.allow_cloud_fallback and self._needs_fallback(action):
               return False
           # ... other checks
           return True
   ```
3. **Integrate with SoulStore**:
   - Wrap all soul reads/writes with gate checks
   - Log all gate decisions to immutable audit trail
4. **Update Documentation**:
   - `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` §C-3
   - `docs/strategy/IMPLEMENTATION_MANUAL_C0_C2.md`  
**Deliverable**: Privacy gate implementation + config  
**Done When**: SoulStore respects tiered access controls  

#### **DAY 12 (AUG 5) — V-1: OMEGA-VAULT MVP DESIGN**  
**Owner**: Researcher + Ma'at/P3  
**Dependency**: After C-0  
**Goal**: Design credential/session automation for 8 Grok CLI accounts  

**Tasks**:
1. **Define MVP Scope** (from V-1 ticket):
   - **IN**: Credential vault, session automation, MCP server, passive watcher
   - **OUT**: Full 8-account pool, active rotation, advanced analytics
2. **Architecture**:
   ```mermaid
   graph TD
       A[Grok CLI Client] --> B[Vault MCP Server]
       B --> C[Encrypted Vault (age/vault)]
       B --> D[Session Manager]
       D --> E[Active Sessions (Redis-like)]
       B --> F[Passive Watcher]
       F --> G[Credential Usage Monitor]
       H[User Interface] --> B
   ```
3. **Key Components**:
   - **Vault**: AES-256-GCM encrypted file (age-plugin) with YAML metadata
   - **Session Manager**: 
     - OAuth 2.1 PKCE flow for each Grok account
     - Access token refresh (with rotation detection)
     - Session binding to device/fingerprint
   - **MCP Server**: 
     - `get_credentials(account_id)` → returns decrypted creds
     - `list_accounts()` → returns metadata only
     - `rotate_session(account_id)` → manual trigger
   - **Passive Watcher**: 
     - Monitors credential usage patterns
     - Alerts on anomalies (new IP, unusual time)
4. **Security Properties**:
   - Zero plaintext credentials in memory/disk
   - Hardware-backed key storage if available (TPM, Secure Enclave)
   - Audit log of all access (append-only, signed)
   - Automatic lock after failed attempts
   - Emergency wipe trigger
5. **Integration Points**:
   - Model gateway: Request credentials via MCP before cloud calls
   - Soul updater: Notify vault of credential usage for audit
   - MCP client: Built-in vault client for seamless auth  
**Deliverable**: V-1 design document + API spec  
**Done When**: Researcher + P3 sign off on design  

#### **DAY 13 (AUG 6) — E-0: IDENTITY FLUIDITY PHASE 0 (2h)**  
**Owner**: Kali  
**Dependency**: After C-1′  
**Goal**: Enable Soul Kernel → Agent Config hydration (2h)  

**Tasks**:
1. **Implement Soul Kernel Extraction**:
   ```python
   # src/omega/soul/kernel.py
   def extract_soul_kernel(soul: Soul) -> Dict[str, Any]:
       """Extract immutable core for agent configuration"""
       return {
           "core_values": soul.values[:5],  # Top 5 by weight
           "communication_style": soul.metadata.get("style", "neutral"),
           "expertise_domains": soul.expertise[:3],  # Top 3
           "interaction_boundaries": soul.boundaries,
           "decision_framework": soul.metadata.get("framework", "evidence_based"),
           "version": soul.kernel_version,
           "created_at": soul.created_at,
       }
   ```
2. **Hydrate Agent Config**:
   ```python
   # src/omega/agents/config_hydrator.py
   def hydrate_agent_config(base_config: AgentConfig, soul_kernel: Dict) -> AgentConfig:
       config = base_config.copy()
       
       # Apply soul kernel to agent behavior
       config.system_prompt = f"""
       You are an AI agent with the following core characteristics:
       - Values: {', '.join(soul_kernel['core_values'])}
       - Communication style: {soul_kernel['communication_style']}
       - Expertise domains: {', '.join(soul_kernel['expertise_domains'])}
       - Decision framework: {soul_kernel['decision_framework']}
       
       Always act in accordance with these principles.
       """
       
       # Adjust parameters based on soul
       config.temperature = _map_values_to_temperature(soul_kernel['core_values'])
       config.max_context_length = _adjust_for_expertise(soul_kernel['expertise_domains'])
       
       return config
   ```
3. **Integration Points**:
   - After SoulStore write → trigger kernel extraction
   - Agent initialization → fetch latest kernel from soul
   - Periodic refresh (every 24h) or on significant soul update  
**Deliverable**: Soul kernel extraction + config hydration  
**Done When**: Agent config reflects soul properties  

#### **DAY 14 (AUG 7) — D-1: CONTENT PERSISTENCE (3h)**  
**Owner**: Verity/P10  
**Dependency**: After C-11 (test infra ready)  
**Goal**: Implement `.firecrawl/` content cache with TTL  

**Tasks**:
1. **Cache Structure**:
   ```bash
   .firecrawl/
   ├── content/
   │   ├── {hash}.meta  # URL, timestamp, ttl, content_type
   │   └── {hash}.content  # Actual HTML/markdown
   ├── index.sqlite     # URL → hash, expiry, visit_count
   └── stats.json       # Hit/miss ratios, size
   ```
2. **Implementation**:
   ```python
   # src/omega/search/content_cache.py
   class ContentCache:
       def __init__(self, cache_dir: Path, max_size_gb: int = 10, ttl_days: int = 30):
           self.cache_dir = cache_dir
           self.max_size = max_size_gb * 1024**3
           self.ttl = ttl_days * 24 * 3600
           self.db = SQLiteIndex(cache_dir / "index.sqlite")
       
       async def get(self, url: str) -> Optional[str]:
           # 1. Check index for hash
           hash_val = self.db.get_hash(url)
           if not hash_val:
               return None
           
           # 2. Check TTL
           meta = self._load_meta(hash_val)
           if time.time() - meta.timestamp > self.ttl:
               self._delete(hash_val)
               return None
           
           # 3. Return content
           return self._load_content(hash_val)
       
       async def set(self, url: str, content: str, content_type: str = "text/html"):
           # Hash content
           hash_val = hashlib.sha256(content.encode()).hexdigest()
           
           # Store content
           self._store_content(hash_val, content)
           self._store_meta(hash_val, url, time.time(), content_type)
           
           # Update index
           self.db.upsert(url, hash_val)
           
           # Enforce size limit
           await self._evict_if_needed()
       
       async def _evict_if_needed(self):
           # LRU eviction based on access time
           current_size = self._get_dir_size()
           if current_size > self.max_size:
               to_remove = self.db.get_lru_entries(
                   target_size=current_size - self.max_size * 0.9  # Leave 10% headroom
               )
               for hash_val in to_remove:
                   self._delete(hash_val)
   ```
3. **Integration**:
   - Wrap `sovereign_search_service.py` calls
   - Cache both successful and failed results (different TTL)
   - Add cache hit/miss metrics to observability  
**Deliverable**: `src/omega/search/content_cache.py` + integration  
**Done When**: Repeated searches hit cache; disk usage stays <10GB  

#### **DAY 15 (AUG 8) — D-2: JOB BOARD BRIDGE (2h) & D-3: INITIAL INDEXING (2h)**  
**Owner**: Verity/P10  
**Dependency**: After C-11  
**Goals**: 
- D-2: Connect background researcher to SQLite job board (YAML seed → SQLite runtime)
- D-3: Implement initial search index build  

**D-2 Tasks**:
1. **Replace YAML polling** with SQLite listener:
   ```python
   # src/omega/workers/background_researcher/job_store.py
   class SQLiteJobStore:
       def __init__(self, db_path: str):
           self.db = aiosqlite.connect(db_path)
           self._init_schema()
       
       async def _init_schema(self):
           await self.db.execute("""
               CREATE TABLE IF NOT EXISTS jobs (
                   id TEXT PRIMARY KEY,
                   priority INTEGER NOT NULL,
                   status TEXT NOT NULL,  -- pending, active, completed, failed
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   started_at TIMESTAMP,
                   completed_at TIMESTAMP,
                   payload JSON,
                   result JSON
               )
           """)
           await self.db.commit()
       
       async def next_job(self) -> Optional[Job]:
           async with self.db.execute("""
               SELECT * FROM jobs 
               WHERE status = 'pending' 
               ORDER BY priority DESC, created_at ASC 
               LIMIT 1
           """) as cursor:
               row = await cursor.fetchone()
               if row:
                   return Job(*row)
           return None
       
       async def claim_job(self, job_id: str, worker_id: str) -> bool:
           cursor = await self.db.execute("""
               UPDATE jobs 
               SET status = 'active', 
                   started_at = CURRENT_TIMESTAMP,
                   worker_id = ?
               WHERE id = ? AND status = 'pending'
           """, (worker_id, job_id))
           await self.db.commit()
           return cursor.rowcount > 0
   ```
2. **Seed from YAML** on startup:
   ```python
   # On worker start:
   if await job_store.is_empty():
       yaml_jobs = load_yaml("data/research/job_board.yaml")
       for job in yaml_jobs:
           await job_store.insert(
               id=job["id"],
               priority=job["priority"],
               payload=job["payload"]
           )
   ```
**D-3 Tasks**:
1. **Initial Index Build**:
   ```python
   # src/omega/workers/background_researcher/index_builder.py
   async def build_initial_index(self):
       """Build search index from existing documents"""
       # 1. Get all cached content
       documents = await self.content_cache.get_all()
       
       # 2. Process in batches to avoid OOM
       batch_size = 100
       for i in range(0, len(documents), batch_size):
           batch = documents[i:i+batch_size]
           
           # 3. Generate embeddings (llama.cpp embedding mode)
           embeddings = await self.embedder.embed_batch(
               [doc.content for doc in batch]
           )
           
           # 4. Add to vector store (Qdrant)
           await self.vector_store.upsert(
               ids=[doc.id for doc in batch],
               vectors=embeddings,
               payloads=[{"metadata": doc.metadata} for doc in batch]
           )
           
           # 5. Update progress
           await self._update_progress(i + len(batch), len(documents))
   ```
2. **Schedule**: Run once on startup if index empty  
**Deliverable**: 
- D-2: SQLite job store + YAML seeder
- D-3: Initial index builder  
**Done When**: 
- D-2: Researcher gets jobs from SQLite, not YAML polling
- D-3: Index built on first run; incremental updates thereafter  

### 📋 **WEEK 3 SUMMARY**
| Day | Ticket | Owner | Status |
|-----|--------|-------|--------|
| Mon | C-3    | Kali + Architect | **DEPENDS ON ARCHITECT DECISION** |
| Tue | V-1    | Researcher + P3 | **READY AFTER C-0** |
| Wed | E-0    | Kali | **READY AFTER C-1′** |
| Thu | D-1    | Verity/P10 | **READY AFTER C-11** |
| Fri | D-2/D-3| Verity/P10 | **READY AFTER C-11** |

### ❓ **Questions for User Direction**
1. Shall I proceed with creating the detailed task breakdown for Week 3?
2. Do you want me to begin designing the V-1 Omega-Vault MVP architecture?
3. Should I start the C-3 privacy gate implementation pending Architect approval?

**Ready for your direction on Part 4A setup.**