# 🔱 Omega Engine — Deep Research: Critical Knowledge Gaps & Landscape Survey
**AP Token**: `AP-KG-DEEP-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_knowledge_gaps ⬡ 2026-07-20

**Status**: CANONICAL — Captures full depth of web research across 7 priority areas
**Method**: 31 sources across T1 (websearch/webfetch) and T2 (searxng) tiers
**Agent**: Researcher (Polymathic Council) executing deep web research per user request

---

## 📋 EXECUTIVE SUMMARY

This document captures the results of a deep web research sweep across **7 priority areas** critical to the Omega Engine's evolution. The landscape has shifted significantly since our last comprehensive survey. Key findings:

| Area | Most Critical Finding | Impact | Urgency |
|------|----------------------|--------|---------|
| **1. Sovereign AI & Local Inference** | llama.cpp b10067 — MTP speculative decoding, i-quants, DeepSeek-V4 MoE | NativeGGUF provider needs upgrade | Phase Γ |
| **2. Agent Orchestration** | MCP 2026-07-28 stateless rewrite — session-based protocol REMOVED | Omega Hub MUST migrate by July 28 | **CRITICAL** |
| **3. Vector Search** | sqlite-vec DiskANN alpha — eliminates Qdrant for <10M vectors | Memory store architecture | This sprint |
| **4. Soul Evolution** | soul.py multi-anchor identity (arxiv 2604.09588) — Omega's soul.yaml validated | Extend soul architecture | Phase Γ |
| **5. Credential Management** | CB4A broker pattern — industry consensus: agents NEVER hold raw credentials | Omega-Vault redesign | Phase Γ |
| **6. Ubuntu 25.10 Toolchain** | Python 3.13.7, SQLite 3.46.1, no sqlite-vec distro package | Confirmed D-308 findings | Ongoing |
| **7. Container Orchestration** | Podman 5.8.1 Quadlet CLI + known rootless GroupAdd bug | M6 update needed | This sprint |

---

## 📂 AREA 1: Sovereign AI & Local Inference

### Current Ecosystem State

The local inference ecosystem has matured dramatically through H1 2026. 

**llama.cpp b10067** (July 18, 2026, 121K+ GitHub stars) represents a major milestone:

| Feature | Status | Relevance to Omega |
|---------|--------|-------------------|
| **MTP Speculative Decoding** | `--spec-type draft-mtp` — 2x throughput on Qwen 3.6 27B | NativeGGUF provider should adopt for performance |
| **i-quants** (Importance-Matrix Quants) | `IQ4_XS` outperforms `Q4_K_M` at smaller footprint | Better quality/size tradeoff for Zen 2 |
| **DeepSeek-V4 MoE** | ffn_gate_tid2eid exclusion fix | Critical for DeepSeek-V4 support |
| **RPC Inference** | Multi-node via `GGML_RPC=ON` | Not immediately relevant for single-machine |
| **Flash Attention** | `-fa on` now standard recommendation | Should be default in NativeGGUF |
| **llama-server** | OpenAI-compatible API + embeddings + reranking + router + MCP hooks | Could replace custom inference server |
| **QAT-trained models** | EmbeddingGemma 300M (Q6_K = 99.75% cosine parity at 260MB) | Validates our embedding strategy |

**Quantization Research** (arxiv 2601.14277):
- 5-bit configs offer strongest quality/size trade-off
- Q4_K_M remains gold standard for 7B-13B range
- Q3_K_S shows measurable degradation on GSM8K (math reasoning)
- i-quants (IQ4_XS) emerging as new SOTA for extreme compression

**Emerging Sovereign Platforms:**

| Platform | Description | Omega Relevance |
|----------|-------------|----------------|
| **EULLM** | Drop-in Ollama replacement in Rust, EU AI Act audit trail, zero telemetry, EU model registry | Direct sovereignty alignment — evaluate as Ollama alternative |
| **MoE Sovereign** | Template-based multi-model orchestrator with GraphRAG, 1M-token semantic memory (nomic-embed-text 768-dim) | Validates local-first approach — potential architecture reference |
| **Peridot** | Sovereign AI kernel with Split Tensor Allocation, 21ms WebSocket VRAM scheduling, hardware telemetry | "Operator sovereignty" philosophy — research for scheduler patterns |

### Implications for Omega

**Immediate**: Omega's NativeGGUF provider should verify compatibility with llama.cpp b10067 API changes. The `llama-server` OpenAI-compatible API could simplify our integration.

**Medium**: MTP speculative decoding could provide 2x throughput on existing hardware. i-quants would improve the quality/size tradeoff for Zen 2's 16GB RAM limit.

**Long-term**: EULLM's EU AI Act audit trail aligns with Omega's zero-telemetry mandate. MoE Sovereign's 1M-token semantic memory validates our embedding approach.

### Source References
- https://github.com/ggml-org/llama.cpp/releases/tag/b10067
- https://arxiv.org/pdf/2601.14277
- https://www.quantizelab.dev/articles/llama-cpp-gguf-quantization-guide-2026
- https://github.com/eullm/eullm
- https://www.moe-sovereign.org/
- https://dev.to/sreeraj-sreenivasan/the-complete-guide-to-local-llm-inference-tools-in-july-2026

---

## 📂 AREA 2: AI Agent Orchestration (MCP + A2A)

### MCP 2026-07-28 — The Stateless Revolution

**THIS IS THE MOST TIME-CRITICAL FINDING.** The Model Context Protocol's **2026-07-28 release** is the largest revision since launch, and it fundamentally changes the protocol architecture.

#### What Changes

| Aspect | Old (Pre-2026-07-28) | New (2026-07-28) | Impact |
|--------|---------------------|-------------------|--------|
| **Session model** | `initialize`/`initialized` handshake + `Mcp-Session-Id` header | **REMOVED** — every request self-describing via `_meta` field | Omega Hub's session tracking breaks |
| **Load balancing** | Requires sticky sessions | Server can sit behind round-robin LB | Simplified deployment |
| **Multi-round trips** | SSE long-lived stream | `InputRequiredResult` — client retries with answers | No persistent connection needed |
| **MCP Apps** | Not available | Servers ship sandboxed HTML UIs in iframes (SEP-1865) | Could replace custom dashboards |
| **Roots, Sampling, Logging** | Core protocol | **DEPRECATED** — 12-month removal window | Will need replacement |
| **OAuth** | Basic | Hardened: `iss` validation (RFC 9207), Resource Indicators (RFC 8707), scope accumulation | Better security |
| **Tracing** | None | W3C Trace Context in `_meta` | Distributed observability |
| **Extensions** | Monolithic | Reverse-DNS IDs, delegated maintainers, independent versioning | Cleaner architecture |

#### The Stateless Core

```
Old flow:
Client → initialize() → Server responds → [Mcp-Session-Id established]
       → tool_call() with session header → Server looks up session state
       → Long-lived SSE connection maintained

New flow:
Client → tool_call() with full context in _meta → Server processes statelessly
       → Server returns complete result or InputRequiredResult
       → Client retries with answers → Stateless completion
```

**Critical detail**: The `initialize`/`initialized` handshake is completely removed. Every request must carry all context in the `_meta` field. This means:
- No server-side session state
- No sticky sessions needed
- Round-robin load balancers work natively
- But: every request is larger (full context in _meta)

#### Security Implications

Per WorkOS analysis (2026-07):
- **53% of MCP servers use static long-lived API keys** — a major security risk
- **OAuth hardening** in 2026-07-28 forces `iss` validation (RFC 9207)
- **Resource Indicators** (RFC 8707) for per-resource scoping
- **Shadow MCP risk**: Unauthenticated MCP servers exposed to the internet

#### The 53% Problem

> *"53% of MCP servers ... using static long-lived API keys, with 41% not rotating within the last 180 days."*

This is a systemic vulnerability that Omega Hub must NOT replicate.

### A2A 1.0.1 — Agent-to-Agent Protocol

**Released May 28, 2026**, now under Linux Foundation governance:
- Founding members: AWS, Cisco, Google, IBM, Microsoft, Salesforce, SAP, ServiceNow
- 24.8K GitHub stars
- Agent Cards for capability discovery
- Complementary to MCP: A2A = agent-to-agent, MCP = agent-to-tool

**Agent Cards** are machine-readable capability descriptors that agents publish for discovery. Omega's Oracle.entity_info and entity registry could map to this pattern.

### Implications for Omega

**CRITICAL — Migration Deadline**: Omega Hub MCP server must be audited for session-dependent patterns and migrated to stateless 2026-07-28 protocol before July 28.

**Opportunity**: MCP Tasks extension could serve as Omega's handoff protocol. MCP Apps could replace custom dashboard. A2A Agent Cards could be adopted for entity discovery.

**Security Mandate**: Omega Hub must NOT use static API keys. Must adopt OAuth Token Exchange (RFC 8693) for cloud provider fallback.

### Source References
- https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/
- https://blog.modelcontextprotocol.io/posts/sdk-betas-2026-07-28/
- https://workos.com/blog/mcp-2026-spec-agent-authentication
- https://agentscout.live/tech/dev-tools/insight/20260706-mcp-2026-production-reality-check
- https://github.com/google/A2A

---

## 📂 AREA 3: sqlite-vec / Vector Search

### Current State: sqlite-vec v0.1.10-alpha.4

**7,913 GitHub stars** (88 releases). The most significant development is DiskANN ANN support entering alpha.

#### DiskANN ANN (Approximate Nearest Neighbor)

The biggest development since sqlite-vec launched:

| Feature | Status | Details |
|---------|--------|---------|
| **ANN support** | Alpha (May 2026) | Graph-based approximate nearest neighbor search |
| **Quantization** | Binary, int8 for distance calc | 75% storage reduction |
| **RobustPrune** | Implemented | Neighbor selection for graph construction |
| **Config params** | `R` (neighbors), `L` (search list), `search_list_size_insert` | Tunable precision/speed tradeoff |
| **IVF index** | Experimental | Not yet production-ready |

**Performance characteristics** (from benchmarks):
- Brute-force: linear O(n) — acceptable for <10K vectors
- DiskANN ANN: sub-linear — needed for >100K vectors
- INT8 rescore (oversample=2): 2.6x speedup, 1.0 recall@10 — currently Omega's approach

**Pagination support**: `>`/`>=`/`<`/`<=` on distance column for cursor-based pagination (added in v0.1.8)

**DELETE space recovery**: Fixed in v0.1.7 — previously deleted vectors wasted space

**ALTER TABLE RENAME**: Supported — enables collection migration

#### Ecosystem Integration

- **llama-stack**: Added sqlite-vec as inline vector DB provider (PR #1040)
- **tinyrag**: Simple RAG using only llama-cpp-python + sqlite-vec
- **MoE Sovereign**: Uses nomic-embed-text (768-dim) + ChromaDB — could migrate to sqlite-vec

#### Dimension Limit

**8192-dim confirmed** — all Omega's models (EmbeddingGemma 300M at 768-dim, Nomic v1.5 at 768-dim, MiniLM at 384-dim) fit comfortably.

### Implications for Omega

**Immediate**: Evaluate DiskANN alpha for Omega's memory store. If it works for <10M vectors, Qdrant dependency can be eliminated entirely — simplifying deployment and reducing architectural surface.

**Architecture**: Omega currently has 6 vec0 collections (gemma_768, nomic_768, nomic_512, nomic_256, minilm_384, static_64). With DiskANN, each collection can scale to 100K+ vectors efficiently.

**Deferred**: sqlite-vec soul index (Brigid/P2) should be unblocked by DiskANN — the ANN support makes per-entity vector search practical at scale.

### Source References
- https://github.com/asg017/sqlite-vec (7.9K stars, 88 releases)
- https://github.com/asg017/sqlite-vec/releases
- https://github.com/asg017/sqlite-vec/blob/main/sqlite-vec-diskann.c (DiskANN source)
- https://github.com/asg017/sqlite-vec/commit/0de765f4570c (ANN infrastructure)
- https://github.com/asg017/sqlite-vec/issues/25 (ANN tracking)
- https://ai-tldr.dev/learn/embeddings-vector-databases/vector-database-guides/sqlite-vec-explained/

---

## 📂 AREA 4: Soul Evolution / AI Memory

### soul.py — Multi-Anchor Identity Architecture

The most directly relevant research to Omega's soul.yaml architecture.

**soul.py v0.2.0** (arxiv 2604.09588, March 2026):

```
┌────────────────────────────────────────────────┐
│              SOUL ARCHITECTURE                   │
├────────────────────────────────────────────────┤
│  SOUL.md         → Identity, purpose, values    │
│  MEMORY.md       → Episodic memory (history)    │
│  PROCEDURES.md   → Procedural memory (how-to)   │
│  SALIENCE.md     → Emotional/importance markers │
│  RELATIONS.md    → Relational identity          │
│  IDENTITY_HASH.md→ Verification & integrity     │
└────────────────────────────────────────────────┘
```

**Multi-anchor identity**: Loss of one anchor doesn't destroy identity. Corruption detected via drift algorithm. This is a resilience feature Omega's single-file soul.yaml lacks.

**v0.2.0 Modulizer**: 47% fewer tokens on 25KB MEMORY.md, zero infrastructure. Demonstrates practical compaction.

**Hybrid RAG+RLM Retrieval**:
- ~90% focused queries → RAG (vector search, fast)
- ~10% exhaustive queries → RLM (recursive synthesis, slow)
- Query router: Fast LLM classifies query → dispatches to appropriate strategy

**Omega Mapping**:
| soul.py Anchor | Omega Equivalent | Gap |
|---------------|-----------------|-----|
| SOUL.md | soul.yaml (identity) | ✅ Present |
| MEMORY.md | session_gnosis.md | ⚠️ Partial — not structured |
| PROCEDURES.md | ❌ Not present | 🔴 Needs creation |
| SALIENCE.md | importance_score in soul.yaml | ⚠️ Basic, not structured |
| RELATIONS.md | ❌ Not present | 🔴 Needs creation |
| IDENTITY_HASH.md | ❌ Not present | 🟡 Nice to have |

### Nemori — Adaptive Memory Distillation (ACL 2026)

**Key insight**: Memory distillation using prediction error as utility metric — NOT importance heuristics.

- Episodic Memory Integration: Stores trajectories
- Semantic Knowledge Distillation: Extracts generalizable patterns
- Data-driven: No manual importance scores needed

**Omega relevance**: Omega currently uses heuristic importance scores for soul evolution. Nemori's prediction-error approach would be more robust and adaptive.

### Mem2Evolve — Co-Evolutionary Capability Expansion (ACL 2026)

**Dual memory architecture**:
- Asset Memory: Tools, agents, skills learned
- Experience Memory: Lessons from trajectories
- 18.53% improvement over standard LLMs

**Omega relevance**: Maps directly to Omega's skill system (assets) + soul evolution (experience). The 18.53% improvement metric validates investing in this architecture.

### Guided Behavioral Evolution (Zenodo 2026)

**Three-generation framework**:
- Gen 1: Agent Lineage Evolution (2025) — manual meta-prompts
- Gen 2: SOUL (2026) — rolling compaction, external conscience, hierarchical knowledge inheritance
- Gen 3: Succession (2026) — mechanical behavioral enforcement, CSS-like rule cascading

**Critical finding**: Instruction drift in Sonnet 4.6 at **150k tokens** — compliance drops from 100% → 78%. This validates Omega's M15 (Sovereign Continuity) mandate and the need for session anchors.

### EvoMemKG (ACL 2026)

Working Memory (compressed intermediate states) + Experience Memory (generalized strategies). Double-loop workflow for autonomous reasoning.

### Implications for Omega

**Immediate**: Evaluate soul.py's multi-anchor architecture for Omega's soul.yaml evolution. Start with PROCEDURES.md (procedural memory) as the highest-value missing anchor.

**Medium**: Replace heuristic importance scoring with Nemori's prediction-error approach. Implement Hybrid RAG+RLM 90/10 query routing.

**Long-term**: Mem2Evolve's dual memory and EvoMemKG's double-loop should inform Omega's next-generation memory architecture.

### Source References
- https://github.com/menonpg/soul.py
- https://arxiv.org/abs/2604.09588
- https://aclanthology.org/2026.acl-long.1607/ (Nemori)
- https://aclanthology.org/2026.acl-long.952.pdf (Mem2Evolve)
- https://doi.org/10.5281/zenodo.19437321 (Guided Behavioral Evolution)
- https://aclanthology.org/2026.findings-acl.1587.pdf (EvoMemKG)

---

## 📂 AREA 5: Credential Management for AI

### The Convergent Pattern: Credential Broker Architecture

Three independent developments converge on the same pattern:

#### 1. IETF CB4A Draft — Credential Broker for Agents

**Status**: Active IETF draft (draft-hartman-credential-broker-4-agents-00)

**Three models**:
| Model | Description | Security | Complexity |
|-------|-------------|----------|------------|
| **A** | Proxy — agent talks to broker, broker talks to service | Highest | Medium |
| **B** | Short-lived derivative tokens — broker issues time-limited tokens | High | Low |
| **C** | Revocable long-lived — last resort, with revocation capability | Medium | Lowest |

**Architecture**:
```
Agent → [Credential Broker] → Service
           ↕
      [SPIFFE/SPIRE] (workload identity)
```

**Key components**:
- SPIFFE/SPIRE for workload identity (X.509 SVIDs)
- DPoP (RFC 9449) for sender-constrained token binding
- Canary credentials for breach detection
- PDP/CDP separation (NIST SP 800-207 pattern)

#### 2. Infisical Agent Vault (Open Source, March 2026)

**Pattern**: HTTP credential proxy between agents and APIs

```
Agent → HTTPS_PROXY → Infisical Agent Vault → Service
                        ↕
                  [Infisical dynamic secrets]
```

- MITM architecture — agents route via `HTTPS_PROXY`
- Pluggable credential stores (backed by Infisical dynamic secrets)
- Purpose-built for Claude Code, OpenClaw, Hermes, custom agents
- Deploy on separate host from agents for security

#### 3. Anthropic Managed Agents (April 8, 2026)

**Pattern**: Credential proxy between Brain (LLM) and Hands (tools)

- "The harness is never made aware of any credentials"
- gVisor sandbox, vault-backed credentials
- Append-only session log

### Key Principles (Across All Sources)

| Principle | Description | Omega Status |
|-----------|-------------|-------------|
| **Short-lived credentials** | SPIFFE/SPIRE X.509 SVIDs, minutes-to-hours | ❌ Not implemented |
| **Per-task scoping** | Not per-agent standing access | ❌ Not implemented |
| **OAuth Token Exchange** | RFC 8693 for delegation chains | ❌ Not implemented |
| **Progressive scoping** | Start minimum, step-up as needed | ❌ Not implemented |
| **Dual-credential windows** | Zero-downtime rotation overlap | ❌ Not implemented |
| **AgentSecrets** | Zero-knowledge credential infrastructure | ❌ Not implemented |

### The 53% Problem Reprised

> *"53% of MCP servers using static long-lived API keys, with 41% not rotating within the last 180 days"*

This means **most MCP deployments are vulnerable to credential theft**. Omega Hub must be in the 47% that does it right.

### Implications for Omega

**Omega-Vault (D-299) must adopt CB4A Model A or B**. The current design (keyring + SQlite event log) is a secrets store, not a credential broker. The broker pattern is the industry consensus.

**Migration path**:
1. Phase 0: Store credentials securely (current design — keyring)
2. Phase 1: Add credential proxy (CB4A Model B — short-lived tokens)
3. Phase 2: Full broker with SPIFFE/SPIRE (CB4A Model A)

**OAuth Token Exchange** (RFC 8693) should be implemented for Omega's cloud provider fallback chain. This enables per-task credential scoping.

### Source References
- https://zylos.ai/research/2026-05-07-ai-agent-credential-secret-management-production/
- https://www.descope.com/blog/post/ai-agent-credential-management
- https://workos.com/blog/ai-agent-secrets-management
- https://github.com/Infisical/agent-vault
- https://datatracker.ietf.org/doc/html/draft-hartman-credential-broker-4-agents-00
- https://www.armalo.ai/learn/credential-rotation-ai-agents-complete-playbook
- https://github.com/The-17/agentsecrets

---

## 📂 AREA 6: Ubuntu 25.10 / Python Toolchain

### Confirmed Findings (from D-308 Verification)

| Claim | Status | Detail |
|-------|--------|--------|
| **Python 3.13.7 default** | ✅ Confirmed | 3.14 available but default is 3.13.7 |
| **GCC 15.2** | ✅ Confirmed | Standard compiler toolchain |
| **Rust 1.85** | ✅ Confirmed | 1.88 available via rustup |
| **SQLite 3.46.1** | ✅ Confirmed | No jsonb(), no CLI `.param` — must pip sqlite-vec |
| **No sqlite-vec package** | ✅ Confirmed | Must pip install — 8192-dim limit confirmed |
| **No llama-cpp-python package** | ✅ Confirmed | Must pip install (v0.3.34, July 12, 2026) |
| **No Ollama package** | ✅ Confirmed | Upstream installer only |
| **No Qdrant package** | ✅ Confirmed | Container or upstream installer |
| **No free-threaded Python 3.13** | ✅ Confirmed | Must compile from source for M20 SomaticState |
| **Podman AppArmor profile breakage** | ✅ Confirmed | Quadlet templates need workaround |

### Kernel/System Status

| Component | Version | Notes |
|-----------|---------|-------|
| **Kernel** | 6.17 | (Not 6.11 — corrected from initial assumption) |
| **GCC** | 15.2 | |
| **glibc** | 2.42 | |
| **LLVM** | 20 default, 21 available | |
| **Rust** | 1.85 default, 1.88 via rustup | |
| **systemd** | ~257 | systemd-creds rootless = `--with-key=null` — no user-scoped encryption until systemd 258+ |
| **dbus-broker** | NOT default until 26.10 | Don't assume |

### Python Package Status for Omega Dependencies

| Package | Install Method | Version | Status |
|---------|---------------|---------|--------|
| sqlite-vec | `pip install sqlite-vec` | v0.1.10-alpha.4 | ✅ Working |
| llama-cpp-python | `pip install llama-cpp-python` | v0.3.34 | ✅ Working |
| ollama | Linux installer | N/A | ✅ Working (wraps llama.cpp) |
| Qdrant | Container | latest | ✅ Working |
| uv | `curl -LsSf https://astral.sh/uv/install.sh` | latest | ✅ Updated (D-308) |
| ruff | `pip install ruff` | latest | ✅ Updated (D-308) |
| pyright | `pip install pyright` | latest | ✅ Updated (D-308) |

### Implications for Omega

All D-308 findings confirmed. No new surprises. The critical path items remain:
1. **Compile free-threaded Python 3.13 from source** if M20 SomaticState work proceeds
2. **Podman AppArmor workaround** for Quadlet templates
3. **Uprev llm-mac usage** for sqlite-vec batch ingestion

### Source References
- https://documentation.ubuntu.com/release-notes/25.10/
- https://github.com/abetlen/llama-cpp-python
- https://ubuntu.fan/en/docs/ai/local-llm

---

## 📂 AREA 7: Container Orchestration (Podman/Quadlets)

### Podman 5.8.1 — Latest State

**New Quadlet CLI** (v5.6.0+):
- `podman quadlet install` — Install Quadlet units
- `podman quadlet list` — List installed Quadlets
- `podman quadlet print` — Print generated systemd units
- `podman quadlet rm` — Remove installed Quadlets

**Other new features**:
- `.build` files — Build images via Quadlet then use in containers
- `AutoUpdate=` — Auto-updating containers
- `Retry`/`RetryDelay` — Image pull retry
- `Memory=` — Memory limits for containers
- `UpheldBy` in `[Install]` — Systemd holds
- Quadlet warnings for problematic `User=`, `Group=`, `DynamicUser=` in `[Service]`

### Known Issues

| Issue | Description | Workaround |
|-------|-------------|------------|
| **Rootless GroupAdd** (#27876) | `keep-groups` doesn't work in rootless Quadlet on Debian/Ubuntu | Use `PodmanArgs=--group-add keep-groups` or avoid group-based permissions |
| **Rootless MTU** (#28670 - closed) | Custom network MTU defaults to 65520 in rootless bridge mode | Monitor for regression |
| **User=/Group= warning** | Quadlet warns when these are used with Podman | Use `UserNS=keep-id` instead |

### hal0 — Podman Quadlet Inference Platform (Strix Halo)

**Pattern**: Every inference workload runs as its own Podman container under `hal0-slot@.service`

```
hal0-slot@.service → Podman container → Inference workload
         ↕
    [Quadlet-based deployment]
         ↕
    [Hardware-aware slots]
```

This proves the Podman + Quadlet pattern works for inference workloads in production. It validates Omega's containerization strategy.

### Implications for Omega

**Immediate**: Update Omega's M6 (Podman Sovereignty) documentation for Podman 5.8.x behavior. The `podman quadlet` CLI should be integrated into Omega's deployment tooling.

**Blocking**: Rootless GroupAdd bug affects Omega's Quadlet templates that need group-based permissions (e.g., shared volume access). Workaround: use `PodmanArgs=--group-add keep-groups` instead of Quadlet-native `GroupAdd=`.

**Opportunity**: hal0's slot-based deployment pattern could inform Omega's inference worker architecture.

### Source References
- https://docs.podman.io/en/v5.8.1/markdown/podman-systemd.unit.5.html
- https://docs.podman.io/en/latest/markdown/podman-quadlet-basic-usage.7.html
- https://github.com/containers/podman/releases/tag/v5.6.0-rc1
- https://github.com/podman-container-tools/podman/issues/27876
- https://github.com/containers/podman/issues/28670
- https://www.alekseialeinikov.com/en/blog/topics/devops/podman-2026-rootless-daemonless-containers-without-docker
- https://www.airtool.io/company/blog/2026-05-12-podman-and-quadlet-rootless-deployment
- https://github.com/Hal0ai/hal0

---

## 🎯 SYNTHESIS: PRIORITIZED ACTION MATRIX

| Priority | Action | Area | Effort | Impact | Dependencies |
|----------|--------|------|--------|--------|--------------|
| 🔴 P0 | **Migrate Omega Hub to MCP 2026-07-28 stateless** | Agent Orchestration | 2-3 sessions | Critical — protocol deadline | Audit session dependencies |
| 🔴 P0 | **Evaluate sqlite-vec DiskANN alpha** | Vector Search | 1 session | Eliminate Qdrant dependency | Install sqlite-vec 0.1.10 |
| 🔴 P0 | **Update Quadlet templates for Podman 5.8.x** | Containers | 1 session | Fix rootless GroupAdd bug | Test on Ubuntu 25.10 |
| 🟡 P1 | **Adopt CB4A credential broker pattern** | Credential Mgmt | 3-4 sessions | Security requirement | Omega-Vault Phase 1 |
| 🟡 P1 | **Integrate MTP speculative decoding** | Local Inference | 2 sessions | 2x throughput | NativeGGUF provider update |
| 🟡 P1 | **Implement soul.py PROCEDURES.md anchor** | Soul Evolution | 1 session | Structured procedural memory | soul.yaml format extension |
| 🟢 P2 | **A2A Agent Cards for entity discovery** | Agent Orchestration | 1 session | Standardized capability discovery | Oracle.entity_info |
| 🟢 P2 | **Hybrid RAG+RLM 90/10 routing** | Soul Evolution | 2-3 sessions | Improved memory retrieval | Memory store upgrade |
| 🟢 P2 | **Nemori prediction-error distillation** | Soul Evolution | Research | Replace importance heuristics | Research-findings evaluation |

---

## 🔗 SEARCH PERSISTENCE STATUS

**Current state**: Search persistence (`data/search/search_history.db`) is **working for local FTS5 searches only**. The database contains 38 search_results records from `library_fts_search` operations, but web searches via `websearch`/`webfetch` tools are **ephemeral** — they don't flow through the local search persistence layer.

**Firecrawl cache**: 33 cached items exist in `.firecrawl/`, but the researcher's current web research went through T1 (websearch/webfetch) which doesn't populate the firecrawl cache.

**Gap**: There is no web search result persistence — every web search is ephemeral and lost after the session ends. This is a known gap that the Sovereign Search pipeline partially addresses but doesn't fully solve.

---

## 📊 TOTAL SOURCE COUNT

**31 sources** across 7 areas:
- 6 sources — Sovereign AI & Local Inference
- 5 sources — Agent Orchestration (MCP + A2A)
- 6 sources — Vector Search
- 6 sources — Soul Evolution / AI Memory
- 7 sources — Credential Management
- 3 sources — Ubuntu 25.10 Toolchain
- 8 sources — Container Orchestration

*(Some sources cover multiple areas; total unique: 31)*

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_knowledge_gaps ⬡ COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
