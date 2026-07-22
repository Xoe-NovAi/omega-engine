# 🔱 Critical Knowledge Gaps — Deep Dive Research Campaign
**AP Token**: `AP-CRITICAL-GAPS-CAMPAIGN-v1.0.0`  
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_critical_gaps ⬡ 2026-07-21

**Origin**: Carmack S3 Audit §Gap Analysis — 5 domains requiring sovereign-grade research before Phase C execution  
**Priority**: P0 — Blocks C-4a (7-day deadline), C-2′, C-11, V-1, C-3  
**Campaign Duration**: 14 days (parallel execution where possible)  
**Total Jobs**: 12 new research jobs + 3 existing job augmentations

---

## §1 Campaign Overview

### The Five Critical Gaps

| Gap ID | Domain | Blocking Ticket | Deadline | Research Type |
|--------|--------|-----------------|----------|---------------|
| **CG-01** | MCP Streamable HTTP + OAuth 2.1 PKCE | C-4a MCP Audit | **July 28 (7 days)** | Spec implementation + security audit |
| **CG-02** | Hardware-Aware OOMProtector (PSI + MemAvailable + cgroup v2) | C-2′ One RAM Truth | ASAP (unblocks C-1′/C-10) | Systems research + kernel integration |
| **CG-03** | Modern Test Infrastructure Stack | C-11 Test Infrastructure | ASAP | Toolchain research + CI integration |
| **CG-04** | Agent-Safe Credential Vault (BlindVault/bury/credential-bridge) | V-1 Omega-Vault MVP | Before C-1′ | Security architecture + agent isolation |
| **CG-05** | Three-Tier Privacy Router (Public/Internal/Personal) | C-3 Privacy Model | After C-1′ | Architecture + local PII classification |

### Execution Strategy: Parallel Tracks

```
Week 1 (Days 1-7):     CG-01 ◼◼◼◼◼◼◼  (7-day hard deadline)
                       CG-02 ◼◼◼◼◼    (parallel, unblocks C-1′/C-10)
                       CG-03 ◼◼◼      (parallel, CI foundation)
                       CG-04 ◼◼◼      (parallel, V-1 dependency)

Week 2 (Days 8-14):    CG-05 ◼◼◼◼     (after C-1′ decision)
                       CG-02 ◼◼       (integration testing)
                       CG-03 ◼◼       (CI pipeline hardening)
                       CG-04 ◼◼       (PoC + decision gate)
```

---

## §2 Job Definitions — New Research Jobs

### CG-01: MCP Streamable HTTP + OAuth 2.1 PKCE Implementation Audit
**Job ID**: `R_CG01_MCP_STREAMABLE_HTTP_OAUTH`  
**Phase**: 0 (Immediate) | **Sprint**: 0.1 | **Priority**: P0 | **Status**: open  
**Capabilities**: web_research, security, mcp_protocol, oauth2, fastapi  
**Depends On**: []  
**Owner**: Ma'at/P4 (MCP Audit lead) + Researcher (spec deep-dive)

**Queries**:
- MCP Streamable HTTP transport specification 2026-07-28 revision
- OAuth 2.1 PKCE mandatory for all clients implementation patterns
- RFC 8707 Resource Indicators MCP server audience validation
- RFC 9728 Protected Resource Metadata /.well-known/oauth-protected-resource
- RFC 7591 Dynamic Client Registration /register endpoint
- FastMCP/Starlette Streamable HTTP migration from HTTP+SSE
- Mcp-Session-Id header cryptographically secure UUID generation
- Origin header validation DNS rebinding prevention MCP
- WWW-Authenticate challenge flow MCP 401 response
- Last-Event-ID SSE resumability implementation
- NapthaAI/http-oauth-mcp-server reference implementation patterns
- xai-org/grok-build ACP protocol MCP bridge patterns

**Deliverable**: `docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH.md`  
**Decision Gate**: Complete MCP audit checklist + migration implementation plan with 7-day sprint breakdown

---

### CG-02: Hardware-Aware OOMProtector — PSI + MemAvailable + cgroup v2
**Job ID**: `R_CG02_OOMPROTECTOR_HARDWARE_AWARE`  
**Phase**: 0 (Immediate) | **Sprint**: 0.2 | **Priority**: P0 | **Status**: open  
**Capabilities**: web_research, systems, linux_kernel, memory_management, python_async  
**Depends On**: []  
**Owner**: Ma'at/P1 (Infrastructure lead) + John Carmack (architecture review)

**Queries**:
- Linux Pressure Stall Information (PSI) /proc/pressure/memory monitoring userspace
- PSI "some" vs "full" stall metrics interpretation for admission control
- MemAvailable kernel algorithm si_mem_available() reclaimable estimation
- cgroup v2 memory.pressure per-slice monitoring systemd integration
- systemd-oomd ManagedOOMMemoryPressure configuration patterns
- Earlyoom userspace OOM killer PSI-based thresholds
- llama.cpp mmap demand paging RSS vs MemAvailable correlation
- Ryzen 7 5700U 15W TDP memory bandwidth constraints inference
- 8MB L3 victim cache eviction impact on inference latency
- Python async PSI polling /proc/pressure/memory epoll integration

**Deliverable**: `docs/research/R_CG02_OOMPROTECTOR_HARDWARE_AWARE.md`  
**Decision Gate**: OOMProtector.check() implementation with three-signal fusion (PSI + MemAvailable + cgroup) + contract tests

---

### CG-03: Modern Test Infrastructure Stack — pytest-benchmark + ordeal + pytest-resilience-agent
**Job ID**: `R_CG03_TEST_INFRASTRUCTURE_STACK`  
**Phase**: 0 (Immediate) | **Sprint**: 0.3 | **Priority**: P0 | **Status**: open  
**Capabilities**: web_research, testing, ci_cd, pytest, chaos_engineering  
**Depends On**: []  
**Owner**: Verity/P10 (Validation lead) + Researcher (tool evaluation)

**Queries**:
- pytest-benchmark pedantic mode CI regression gating --benchmark-compare-fail=min:10%
- ordeal automated chaos testing scan --save witness regression workflow
- pytest-resilience-agent 13 built-in LLM gateway chaos scenarios
- mutmut mutation testing critical paths gate 0 surviving mutants
- hypothesis property-based testing stateful RuleBasedStateMachine
- pact-python consumer-driven contract testing provider verification
- pytest-cov diff-cover new code coverage gate 90%
- GitHub Actions benchmark baseline storage .benchmarks/ JSON history
- CI noise floor calibration shared runners benchmark threshold tuning
- Test quarantine pattern @pytest.mark.quarantine(reason, ticket, expires)

**Deliverable**: `docs/research/R_CG03_TEST_INFRASTRUCTURE_STACK.md`  
**Decision Gate**: Complete CI pipeline YAML with 4 gates (unit, mutation, benchmark, chaos) + tool versions pinned

---

### CG-04: Agent-Safe Credential Vault — BlindVault / bury / credential-bridge Evaluation
**Job ID**: `R_CG04_AGENT_SAFE_CREDENTIAL_VAULT`  
**Phase**: 0 (Immediate) | **Sprint**: 0.4 | **Priority**: P0 | **Status**: open  
**Capabilities**: web_research, security, vault, ai_agents, architecture  
**Depends On**: []  
**Owner**: Researcher + P3 (Implementation) + John Carmack (architecture review)

**Queries**:
- BlindVault agent-secret isolation broker architecture PID-bound sessions
- BlindVault master password Argon2id encryption vault at rest
- BlindVault policy engine host allowlist per secret usage policies
- BlindVault scrubber output sanitization agent leak prevention
- bury PID-bound sessions process tree authentication scope control
- bury Argon2id XSalsa20-Poly1305 libsodium encryption audit
- bury credential proxy [CRED:path] pattern substitution execution time
- bury real-time audit log ~/.vault/access.log monitoring
- credential-bridge SecretsManager facade Vault/Keyring/.env plugin architecture
- credential-bridge VaultBackend AppRole auth dynamic secrets rotation
- credential-bridge KeyringBackend OS credential store cross-platform
- credential-bridge EnvFileBackend .env twelve-factor compatibility
- ACP bridge Grok CLI session JSONL extraction Omega Hivemind integration
- Grok Build nono sandbox Landlock Seatbelt secure code execution

**Deliverable**: `docs/research/R_CG04_AGENT_SAFE_CREDENTIAL_VAULT.md`  
**Decision Gate**: Select V-1 backend architecture (BlindVault vs bury vs credential-bridge) + PoC launching `claude` with scoped session

---

### CG-05: Three-Tier Privacy Router — Public/Internal/Personal Classification
**Job ID**: `R_CG05_THREE_TIER_PRIVACY_ROUTER`  
**Phase**: 1 (After C-1′) | **Sprint**: 1.1 | **Priority**: P1 | **Status**: open  
**Capabilities**: web_research, architecture, privacy, ml_models, pii_detection  
**Depends On**: [R_CG01, R_CG02, R_CG03, R_CG04, C-1′ SoulStore decision]  
**Owner**: Kali (Architecture) + Researcher (PII classifier evaluation)

**Queries**:
- Local PII detection NER Presidio spaCy 2026 performance benchmarks
- Microsoft Presidio analyzer recognizers custom entity types
- spaCy NER transformer vs CNN accuracy latency tradeoff local
- Data sensitivity classification rules engine Public/Internal/Personal
- Confidence cascade routing local→private→frontier escalation thresholds
- Tiered inference router LiteLLM gateway pattern local-first
- Privacy budget differential privacy local inference epsilon calibration
- EU AI Act August 2026 data residency requirements local processing
- GDPR Article 25 data protection by design router implementation
- Model capability estimation lightweight classifier 1B parameter local

**Deliverable**: `docs/research/R_CG05_THREE_TIER_PRIVACY_ROUTER.md`  
**Decision Gate**: Router architecture with hard-lock PERSONAL_REGULATED → Tier 1 + confidence cascade implementation plan

---

### CG-06: Grok Ecosystem Deep Research — Models, Pricing, ACP, Fleet Deployment
**Job ID**: `R_CG06_GROK_ECOSYSTEM_DEEP` (Augments existing R33)  
**Phase**: 0 (Immediate) | **Sprint**: 0.5 | **Priority**: P0 | **Status**: open  
**Capabilities**: web_research, grok_ecosystem, architecture, cost_analysis  
**Depends On**: []  
**Owner**: Grokster (Cloud Mind) + Researcher

**Queries**:
- xAI API models pricing 2026 Grok 4.5 4.3 4.20 4.15 4.10
- Grok Build open source ACP protocol stdio transport 2026
- Grok CLI headless mode parallel subagents 8 accounts orchestration
- Web Grok Projects custom instructions personas 2026
- Responses API vs Chat Completions xAI 2026 feature parity
- Server-side tools web_search x_search code_execution pricing 2026
- Batch API Priority Processing xAI 2026 cost optimization
- Grok model selection matrix reasoning deepsearch think modes
- Grok 4.5 Think mode DeepSearch agentic research capabilities
- xAI API rate limits concurrent requests 8-account fleet management

**Deliverable**: `docs/research/R_CG06_GROK_ECOSYSTEM_DEEP.md` (augments R33)  
**Decision Gate**: Finalize Grok model selection matrix + 8-account fleet deployment architecture

---

### CG-07: Sovereign Search Architecture — 5-Tier Protocol Implementation
**Job ID**: `R_CG07_SOVEREIGN_SEARCH_5TIER` (Augments existing R34)  
**Phase**: 0 (Immediate) | **Sprint**: 0.6 | **Priority**: P0 | **Status**: open  
**Capabilities**: web_research, architecture, engineering, search  
**Depends On**: [R_CG01]  
**Owner**: Researcher + P4 (Integration)

**Queries**:
- SearXNG neural search configuration 2026 embedding reranking
- Brave Search API independent index MCP server 2026
- Semantic Scholar API 200M papers 2026 bulk harvest
- arXiv API bulk harvest 2026 rate limits strategies
- OpenAlex research graph API 2026 citation network
- Search routing intelligence fallback chain cost recall relevance
- Tiered search architecture cache→websearch→SearXNG→Brave→academic
- Firecrawl credit protocol optimization sovereign caching
- Exa AI neural search precision technical queries 2026

**Deliverable**: `docs/research/R_CG07_SOVEREIGN_SEARCH_5TIER.md` (augments R34)  
**Decision Gate**: Implement 5-tier search router with cost/recall/relevance optimization

---

### CG-08: Local Admission Control — CCX Topology + Semaphore Implementation
**Job ID**: `R_CG08_LOCAL_ADMISSION_CONTROL_IMPL` (Augments existing R44)  
**Phase**: 1 (After C-2′) | **Sprint**: 1.2 | **Priority**: P1 | **Status**: open  
**Capabilities**: web_research, systems, performance, hardware, asyncio  
**Depends On**: [R_CG02]  
**Owner**: Ma'at/P1 + John Carmack

**Queries**:
- asyncio.Semaphore local inference admission control 2026 patterns
- Ryzen 5700U CCX topology taskset pinning llama.cpp instances
- llama.cpp concurrent instances memory bandwidth saturation
- Fail-fast cloud route vs queue local admission control latency
- NUMA-aware scheduling Zen 2 single CCX 4-core inference isolation
- LLAMA_CPP_N_THREADS=4 CCX pinning vs SMT throughput
- Memory bandwidth monitoring perf counters inference scaling

**Deliverable**: `docs/research/R_CG08_LOCAL_ADMISSION_CONTROL_IMPL.md` (augments R44)  
**Decision Gate**: Semaphore(1) + taskset CCX pinning implementation in ModelGateway

---

### CG-09: SoulStore Atomic Write — Single Writer + Actor Model
**Job ID**: `R_CG09_SOULSTORE_ATOMIC_IMPL` (Augments existing R45)  
**Phase**: 1 (After C-2′) | **Sprint**: 1.3 | **Priority**: P0 | **Status**: open  
**Capabilities**: web_research, systems, file_systems, concurrency, actor_model  
**Depends On**: [R_CG02, R_CG03]  
**Owner**: Ma'at/P3 + Roc Racoon (legacy patterns) + John Carmack

**Queries**:
- fcntl.flock LOCK_EX LOCK_NB Python 2026 cross-platform
- Atomic write mkstemp fsync os.replace pattern durability
- Actor model system_agent user file permissions isolation
- Concurrent writer race condition prevention single writer
- os.fsync vs fdatasync durability guarantees ext4/btrfs
- SQLite WAL mode vs custom actor model soul persistence
- Temporary file directory fsync parent directory atomic rename

**Deliverable**: `docs/research/R_CG09_SOULSTORE_ATOMIC_IMPL.md` (augments R45)  
**Decision Gate**: Single SoulStore writer with fcntl + atomic + fsync + actor model implementation

---

### CG-10: GenerationPolicy Extraction — Gemma 4 Thinking Config
**Job ID**: `R_CG10_GENERATION_POLICY_GEMMA` (Augments existing R43)  
**Phase**: 1 (After C-1′) | **Sprint**: 1.4 | **Priority**: P2 | **Status**: open  
**Capabilities**: web_research, ml_models, architecture, generation_config  
**Depends On**: [R_CG01]  
**Owner**: Researcher + P6 (ModelGate)

**Queries**:
- Gemma 4 logit_bias temperature floors 2026 binary MINIMAL/HIGH
- Model generation policy registry pattern provider-specific
- Provider-specific generation config extraction ModelGateway
- Gemma thinking config regex detection thinking blocks
- Binary thinking mode MINIMAL HIGH no intermediate values
- GenerationPolicy dataclass extraction from ModelGateway.generate()

**Deliverable**: `docs/research/R_CG10_GENERATION_POLICY_GEMMA.md` (augments R43)  
**Decision Gate**: Extract GenerationPolicy from ModelGateway.generate() with provider-specific configs

---

### CG-11: Novelty Engine for Living Research OS — Exploration vs Exploitation
**Job ID**: `R_CG11_NOVELTY_ENGINE_LIVING_RESEARCH` (Augments existing R46)  
**Phase**: 1 (After C-1′) | **Sprint**: 1.5 | **Priority**: P1 | **Status**: open  
**Capabilities**: web_research, architecture, ml_models, research_methodology  
**Depends On**: [R_CG03, R_CG06]  
**Owner**: Researcher + Kali

**Queries**:
- Random topic sampling exploration vs exploitation 2026 bandit algorithms
- Cross-domain contradiction detection AI 2026 belief revision
- Surprise detection belief revision AI 2026 information theory
- Research loop convergence prevention 2026 novelty injection
- INDEX.md noise policy archive auto-generated entries curation
- Thompson sampling research topic selection multi-armed bandit
- Information gain maximization research query selection

**Deliverable**: `docs/research/R_CG11_NOVELTY_ENGINE_LIVING_RESEARCH.md` (augments R46)  
**Decision Gate**: Design novelty injection for _grow_frontier() + INDEX archive policy

---

### CG-12: File-Based Hivemind Contingency — Hub Dark Mode
**Job ID**: `R_CG12_FILE_HIVEMIND_CONTINGENCY` (Augments existing R29)  
**Phase**: 0 (Parallel with CG-01) | **Sprint**: 0.7 | **Priority**: P1 | **Status**: open  
**Capabilities**: web_research, systems, coordination, distributed_systems  
**Depends On**: []  
**Owner**: Ma'at/P9 (Orchestration) + Researcher

**Queries**:
- File-based agent coordination without central hub 2026 fcntl.flock
- Distributed lock fcntl.flock multi-agent 2026 patterns
- Handoff protocol file-based implementation 2026 atomic
- Awareness heartbeat file-based TTL 2026 stale detection
- M23 Failure Integrity fallback patterns file-based coordination
- JSONL session log append-only awareness reconstruction
- Lock directory structure /tmp/omega-hivemind/locks/

**Deliverable**: `docs/research/R_CG12_FILE_HIVEMIND_CONTINGENCY.md` (augments R29)  
**Decision Gate**: Test file-based Hivemind works without Hub (M23 fallback validated)

---

## §3 Existing Job Augmentations

| Existing Job | Augmentation | New Deliverable |
|--------------|--------------|-----------------|
| **R33** (Grok Ecosystem) | + CG-06 deep pricing/ACP/fleet | `R_CG06_GROK_ECOSYSTEM_DEEP.md` |
| **R34** (Sovereign Search) | + CG-07 5-tier implementation | `R_CG07_SOVEREIGN_SEARCH_5TIER.md` |
| **R44** (Local Admission) | + CG-08 CCX topology + semaphore | `R_CG08_LOCAL_ADMISSION_CONTROL_IMPL.md` |
| **R45** (SoulStore Atomic) | + CG-09 actor model + fcntl | `R_CG09_SOULSTORE_ATOMIC_IMPL.md` |
| **R43** (GenerationPolicy) | + CG-10 Gemma 4 thinking config | `R_CG10_GENERATION_POLICY_GEMMA.md` |
| **R46** (Novelty Engine) | + CG-11 exploration/exploitation | `R_CG11_NOVELTY_ENGINE_LIVING_RESEARCH.md` |
| **R29** (File Hivemind) | + CG-12 M23 fallback validation | `R_CG12_FILE_HIVEMIND_CONTINGENCY.md` |

---

## §4 Campaign Timeline — Day by Day

### Week 1: The 7-Day Sprint (July 21-27)

| Day | CG-01 (MCP) | CG-02 (OOM) | CG-03 (Test Infra) | CG-04 (Vault) | CG-06 (Grok) | CG-07 (Search) | CG-12 (Hivemind) |
|-----|-------------|-------------|-------------------|---------------|--------------|----------------|------------------|
| **Mon 21** | Spec deep-dive + audit checklist | PSI + MemAvailable kernel sources | pytest-benchmark + ordeal eval | BlindVault/bury/credential-bridge survey | Grok Build clone + ACP handshake | SearXNG neural + Brave API | fcntl.flock distributed lock patterns |
| **Tue 22** | FastMCP migration path analysis | cgroup v2 memory.pressure integration | mutmut + hypothesis + pact eval | Architecture comparison matrix | 8-account fleet pricing model | 5-tier router design | JSONL session awareness reconstruction |
| **Wed 23** | OAuth 2.1 PKCE + RFC 8707/9728 impl | Three-signal fusion algorithm design | CI pipeline 4-gate YAML draft | PoC: BlindVault broker + agent | Grok CLI session JSONL extraction | Fallback chain cost/recall model | Handoff protocol file-based atomic |
| **Thu 24** | Origin validation + SSE streaming | Contract test implementation | Mutation testing critical paths | PoC: bury PID-bound session | Grok→Omega Hivemind bridge prototype | Cache→websearch→SearXNG→Brave→academic | TTL stale detection + reaping |
| **Fri 25** | Session management Mcp-Session-Id | Integration test ResourceGuard | Benchmark baseline storage | Decision gate: select V-1 backend | Fleet orchestration architecture | Academic tier Semantic Scholar/arXiv | M23 fallback test without Hub |
| **Sat 26** | **Integration test full MCP server** | **Integration test OOMProtector** | **CI pipeline validation** | **V-1 backend decision doc** | **Grok fleet deployment plan** | **Search router implementation start** | **Contingency test report** |
| **Sun 27** | **Migration PR ready for review** | **OOMProtector PR ready** | **Test infra PR ready** | **V-1 PoC demo** | **R33 augmented deliverable** | **R34 augmented deliverable** | **R29 augmented deliverable** |

### Week 2: Integration & Hardening (July 28 - Aug 3)

| Day | CG-05 (Privacy Router) | CG-08 (Admission) | CG-09 (SoulStore) | CG-10 (GenPolicy) | CG-11 (Novelty) |
|-----|------------------------|-------------------|-------------------|-------------------|-----------------|
| **Mon 28** | PII classifier Presidio/spaCy eval | Semaphore + taskset CCX pinning | fcntl.flock + atomic write pattern | Gemma 4 thinking config regex | Thompson sampling topic selection |
| **Tue 29** | Sensitivity rules engine design | NUMA-aware scheduling Zen 2 | Actor model system_agent isolation | GenerationPolicy dataclass design | Cross-domain contradiction detection |
| **Wed 30** | Confidence cascade thresholds | Memory bandwidth monitoring | SQLite WAL vs custom actor model | Provider-specific config extraction | Surprise detection belief revision |
| **Thu 31** | Hard-lock PERSONAL→Tier 1 logic | Fail-fast cloud route logic | Single writer implementation | Regex detection thinking blocks | INDEX.md archive policy |
| **Fri 1** | Router integration with ModelGateway | Integration test admission control | SoulStore PR + contract tests | ModelGateway.generate() refactor | _grow_frontier() novelty injection |
| **Sat 2** | **Privacy router PR ready** | **Admission control PR ready** | **SoulStore PR ready** | **GenerationPolicy PR ready** | **Novelty engine PR ready** |
| **Sun 3** | **Integration testing week** | **Integration testing week** | **Integration testing week** | **Integration testing week** | **Integration testing week** |

---

## §5 Resource Allocation

| Role | Primary | Secondary | Capacity |
|------|---------|-----------|----------|
| **John Carmack** | CG-02 (arch review), CG-04 (arch review), CG-05 (arch), CG-08, CG-09 | All (gate reviews) | 4h/day |
| **Ma'at/P1** | CG-02 (lead), CG-08, CG-09 | CG-03, CG-12 | 6h/day |
| **Ma'at/P3** | CG-09 (lead) | CG-04 | 4h/day |
| **Ma'at/P4** | CG-01 (lead), CG-07, CG-12 | CG-08 | 6h/day |
| **Ma'at/P9** | CG-12 (lead) | CG-01 | 4h/day |
| **Ma'at/P10 / Verity** | CG-03 (lead) | CG-09, CG-10 | 6h/day |
| **Researcher** | CG-01, CG-04, CG-05, CG-06, CG-07, CG-11 | All (synthesis) | 8h/day |
| **Grokster** | CG-06 (lead), CG-07 | CG-01, CG-04 | 8h/day (cloud) |
| **Roc Racoon** | CG-09 (legacy patterns) | CG-04 | 4h/day |
| **Kali** | CG-05 (arch), CG-11 | All (synthesis) | 4h/day |

---

## §6 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP 2026-07-28 spec changes after audit | Medium | High | Monitor modelcontextprotocol.io/specification/draft daily; build adapter layer |
| PSI not available on kernel < 4.20 | Low | High | Fallback to MemAvailable + cgroup pressure; document minimum kernel |
| BlindVault broker requires separate OS user | Medium | Medium | Document as deployment requirement; provide systemd unit template |
| Grok CLI ACP bridge incomplete | Medium | High | Start S-1 (clone grok-build) Day 1; parallel Grokster research |
| PII classifier false negatives → privacy leak | High | Critical | Hard-lock PERSONAL_REGULATED to Tier 1 regardless of classifier |
| CI benchmark noise floor too high | Medium | Medium | Calibrate on dedicated runner; gate on `min` statistic with 15% threshold |
| SoulStore actor model over-engineering | Medium | Medium | Start with fcntl + atomic + fsync; actor model only if contention proven |

---

## §7 Success Criteria — Campaign Complete When:

- [ ] **CG-01**: MCP Streamable HTTP + OAuth 2.1 PKCE audit complete + migration PR merged
- [ ] **CG-02**: OOMProtector.check() three-signal fusion passing contract tests + integrated in ResourceGuard
- [ ] **CG-03**: CI pipeline with 4 gates (unit, mutation, benchmark, chaos) green on main
- [ ] **CG-04**: V-1 backend selected + PoC launching `claude` with scoped session working
- [ ] **CG-05**: Three-tier privacy router implemented + hard-lock PERSONAL_REGULATED validated
- [ ] **CG-06**: Grok model selection matrix finalized + 8-account fleet deployment architecture
- [ ] **CG-07**: 5-tier sovereign search router implemented + cost/recall optimized
- [ ] **CG-08**: Semaphore(1) + taskset CCX pinning in ModelGateway + load tested
- [ ] **CG-09**: SoulStore single writer + fcntl + atomic + fsync + actor model passing tests
- [ ] **CG-10**: GenerationPolicy extracted from ModelGateway + Gemma 4 config working
- [ ] **CG-11**: Novelty engine _grow_frontier() + INDEX archive policy implemented
- [ ] **CG-12**: File-based Hivemind contingency tested + M23 fallback validated

---

## §8 Tracking — Add to RESEARCH_JOB_BOARD.yaml

```yaml
# Add these 12 new jobs to data/coordination/RESEARCH_JOB_BOARD.yaml
- id: R_CG01_MCP_STREAMABLE_HTTP_OAUTH
  title: "MCP Streamable HTTP + OAuth 2.1 PKCE Implementation Audit"
  phase: 0
  sprint: '0.1'
  priority: P0
  status: open
  claimed_by: null
  depends_on: []
  capabilities_needed: [web_research, security, mcp_protocol, oauth2, fastapi]
  queries: [...]
  deliverable: docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH.md
  decision_gate: Complete MCP audit checklist + migration implementation plan
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG02_OOMPROTECTOR_HARDWARE_AWARE
  title: "Hardware-Aware OOMProtector — PSI + MemAvailable + cgroup v2"
  phase: 0
  sprint: '0.2'
  priority: P0
  status: open
  claimed_by: null
  depends_on: []
  capabilities_needed: [web_research, systems, linux_kernel, memory_management, python_async]
  queries: [...]
  deliverable: docs/research/R_CG02_OOMPROTECTOR_HARDWARE_AWARE.md
  decision_gate: OOMProtector.check() three-signal fusion + contract tests
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG03_TEST_INFRASTRUCTURE_STACK
  title: "Modern Test Infrastructure Stack — pytest-benchmark + ordeal + pytest-resilience-agent"
  phase: 0
  sprint: '0.3'
  priority: P0
  status: open
  claimed_by: null
  depends_on: []
  capabilities_needed: [web_research, testing, ci_cd, pytest, chaos_engineering]
  queries: [...]
  deliverable: docs/research/R_CG03_TEST_INFRASTRUCTURE_STACK.md
  decision_gate: Complete CI pipeline YAML with 4 gates + tool versions pinned
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG04_AGENT_SAFE_CREDENTIAL_VAULT
  title: "Agent-Safe Credential Vault — BlindVault / bury / credential-bridge Evaluation"
  phase: 0
  sprint: '0.4'
  priority: P0
  status: open
  claimed_by: null
  depends_on: []
  capabilities_needed: [web_research, security, vault, ai_agents, architecture]
  queries: [...]
  deliverable: docs/research/R_CG04_AGENT_SAFE_CREDENTIAL_VAULT.md
  decision_gate: Select V-1 backend architecture + PoC launching claude with scoped session
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG05_THREE_TIER_PRIVACY_ROUTER
  title: "Three-Tier Privacy Router — Public/Internal/Personal Classification"
  phase: 1
  sprint: '1.1'
  priority: P1
  status: open
  claimed_by: null
  depends_on: [R_CG01, R_CG02, R_CG03, R_CG04, C-1']
  capabilities_needed: [web_research, architecture, privacy, ml_models, pii_detection]
  queries: [...]
  deliverable: docs/research/R_CG05_THREE_TIER_PRIVACY_ROUTER.md
  decision_gate: Router architecture with hard-lock PERSONAL_REGULATED to Tier 1
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG06_GROK_ECOSYSTEM_DEEP
  title: "Grok Ecosystem Deep Research — Models, Pricing, ACP, Fleet Deployment"
  phase: 0
  sprint: '0.5'
  priority: P0
  status: open
  claimed_by: null
  depends_on: []
  capabilities_needed: [web_research, grok_ecosystem, architecture, cost_analysis]
  queries: [...]
  deliverable: docs/research/R_CG06_GROK_ECOSYSTEM_DEEP.md
  decision_gate: Finalize Grok model selection matrix + 8-account fleet deployment architecture
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG07_SOVEREIGN_SEARCH_5TIER
  title: "Sovereign Search Architecture — 5-Tier Protocol Implementation"
  phase: 0
  sprint: '0.6'
  priority: P0
  status: open
  claimed_by: null
  depends_on: [R_CG01]
  capabilities_needed: [web_research, architecture, engineering, search]
  queries: [...]
  deliverable: docs/research/R_CG07_SOVEREIGN_SEARCH_5TIER.md
  decision_gate: Implement 5-tier search router with cost/recall/relevance optimization
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG08_LOCAL_ADMISSION_CONTROL_IMPL
  title: "Local Admission Control Implementation — CCX Topology + Semaphore"
  phase: 1
  sprint: '1.2'
  priority: P1
  status: open
  claimed_by: null
  depends_on: [R_CG02]
  capabilities_needed: [web_research, systems, performance, hardware, asyncio]
  queries: [...]
  deliverable: docs/research/R_CG08_LOCAL_ADMISSION_CONTROL_IMPL.md
  decision_gate: Semaphore(1) + taskset CCX pinning implementation in ModelGateway
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG09_SOULSTORE_ATOMIC_IMPL
  title: "SoulStore Atomic Write Implementation — Single Writer + Actor Model"
  phase: 1
  sprint: '1.3'
  priority: P0
  status: open
  claimed_by: null
  depends_on: [R_CG02, R_CG03]
  capabilities_needed: [web_research, systems, file_systems, concurrency, actor_model]
  queries: [...]
  deliverable: docs/research/R_CG09_SOULSTORE_ATOMIC_IMPL.md
  decision_gate: Single SoulStore writer with fcntl + atomic + fsync + actor model
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG10_GENERATION_POLICY_GEMMA
  title: "GenerationPolicy Extraction — Gemma 4 Thinking Config"
  phase: 1
  sprint: '1.4'
  priority: P2
  status: open
  claimed_by: null
  depends_on: [R_CG01]
  capabilities_needed: [web_research, ml_models, architecture, generation_config]
  queries: [...]
  deliverable: docs/research/R_CG10_GENERATION_POLICY_GEMMA.md
  decision_gate: Extract GenerationPolicy from ModelGateway.generate() with provider-specific configs
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG11_NOVELTY_ENGINE_LIVING_RESEARCH
  title: "Novelty Engine for Living Research OS — Exploration vs Exploitation"
  phase: 1
  sprint: '1.5'
  priority: P1
  status: open
  claimed_by: null
  depends_on: [R_CG03, R_CG06]
  capabilities_needed: [web_research, architecture, ml_models, research_methodology]
  queries: [...]
  deliverable: docs/research/R_CG11_NOVELTY_ENGINE_LIVING_RESEARCH.md
  decision_gate: Design novelty injection for _grow_frontier() + INDEX archive policy
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null

- id: R_CG12_FILE_HIVEMIND_CONTINGENCY
  title: "File-Based Hivemind Contingency — Hub Dark Mode"
  phase: 0
  sprint: '0.7'
  priority: P1
  status: open
  claimed_by: null
  depends_on: []
  capabilities_needed: [web_research, systems, coordination, distributed_systems]
  queries: [...]
  deliverable: docs/research/R_CG12_FILE_HIVEMIND_CONTINGENCY.md
  decision_gate: Test file-based Hivemind works without Hub (M23 fallback validated)
  sources_count: null
  started_at: null
  completed_at: null
  key_findings: null
```

---

## §9 Hivemind Coordination

**Campaign Channel**: `opencode`  
**Campaign Entity**: `john_carmack` (oversight) + `researcher` (execution)  
**Handoff Protocol**: Each CG job → Hivemind handoff packet with `task_id` = `cg-{id}-{date}`  
**Heartbeat**: Every 2 hours during active research  
**Session Anchors**: Each researcher maintains `session_gnosis.md` in entity workspace  

---

## §10 Gnosis Distillation Targets (L1→L2→L3)

Each CG job must produce L3 principles for `proposed_lessons.yaml`:

| CG Job | Expected L3 Principle |
|--------|----------------------|
| CG-01 | Protocol migrations require adapter layers, not rewrites |
| CG-02 | Kernel knows memory pressure better than userspace counters |
| CG-03 | Test infrastructure is a product, not a tax — invest accordingly |
| CG-04 | Agent secret isolation requires OS-enforced boundaries, not scrubbing |
| CG-05 | Privacy is a routing constraint, not a post-processing filter |
| CG-06 | Cloud fleets are force multipliers when bridged, not replacements |
| CG-07 | Search tiering is a cost/recall/relevance optimization problem |
| CG-08 | Admission control must understand hardware topology, not just counts |
| CG-09 | Single writer + atomic rename > distributed consensus for local state |
| CG-10 | Generation config belongs to the model, not the gateway |
| CG-11 | Research without novelty injection converges to local optima |
| CG-12 | Centralized coordination is a SPOF — file-based fallback is mandatory |

---

**Campaign Status**: 🟢 **READY TO EXECUTE** — All job definitions complete, dependencies mapped, resources allocated  
**Next Action**: Ticket owners claim jobs via Hivemind handoff; Day 1 sprint begins immediately

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_critical_gaps ⬡ 2026-07-21T19:25:00Z*
