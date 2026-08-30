<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 📋 TRACKER & TEAM DOCS UPDATE PLAN
**To Lock In: Holistic Architecture (Gemini Notebook + Docs System + Local Inference + Knowledge Domains + Headroom + zswap + NVMe Swap)**

---

## 🎯 PRIMARY TRACKING DOCS (Must Update)

### 1. `data/coordination/ACTIVE_SPRINT.json` — **Execution SSOT**
**Current**: PUBLIC-DEBUT-01 sprint with CRITICAL-PATH, INST-1, PUB-1, DEL-1, READINESS-REMEDIATION workstreams
**Add New Workstreams**:
```json
{
  "GEMINI-NOTEBOOK": {
    "task": "Free-tier Gemini Notebook domain (3 accounts, 30 DR/mo, notebooklm-py)",
    "owner": "kali",
    "status": "in_progress",
    "subtasks": [
      {"id": "GN-1", "description": "Workspace creation + doc migration", "owner": "kali", "status": "ready"},
      {"id": "GN-2", "description": "Runtime module + sync script", "owner": "maat", "status": "backlog"},
      {"id": "GN-3", "description": "Free-tier fetch pipeline + systemd timer", "owner": "researcher", "status": "backlog"},
      {"id": "GN-4", "description": "NLG-SMOKE single-account test", "owner": "kali", "status": "blocked", "depends_on": ["V-1 Vault", "Pro provisioning"]}
    ]
  },
  "DOCUMENTATION-SYSTEM": {
    "task": "Modular domain documentation system (workspace + runtime + sync)",
    "owner": "kali",
    "status": "ready",
    "subtasks": [
      {"id": "DS-1", "description": "Create DOMAIN_DOCUMENTATION_SYSTEM.md meta-doc", "owner": "kali", "status": "ready"},
      {"id": "DS-2", "description": "Create docs/strategy/domains/ folder structure", "owner": "kali", "status": "ready"},
      {"id": "DS-3", "description": "Migrate gemini-notebook docs to workspace", "owner": "kali", "status": "ready"},
      {"id": "DS-4", "description": "Create config/domains/ runtime modules", "owner": "maat", "status": "backlog"},
      {"id": "DS-5", "description": "Implement sync_domain_docs.py (validated copy)", "owner": "maat", "status": "backlog"}
    ]
  },
  "LOCAL-INFERENCE-OPT": {
    "task": "Tiered hardware local inference (Tier 0/1/2, sequential, q8_0 KV, adaptive context)",
    "owner": "maat",
    "status": "ready",
    "subtasks": [
      {"id": "LI-1", "description": "AdaptiveContextBuffer + SequentialModelLoader classes", "owner": "maat", "status": "ready"},
      {"id": "LI-2", "description": "q8_0 KV cache profiles in providers.yaml", "owner": "maat", "status": "ready"},
      {"id": "LI-3", "description": "Hardware-tier detection (llama-fit-params)", "owner": "maat", "status": "ready"},
      {"id": "LI-4", "description": "Tier 0 model matrix: Qwen3-4B / Qwen3-4B-Thinking / Qwen3-1.7B", "owner": "maat", "status": "ready"},
      {"id": "LI-5", "description": "Startup script: zswap + NVMe swap + THP + pinning + no-mmap + mlock + prompt caching", "owner": "maat", "status": "ready"}
    ]
  },
  "KNOWLEDGE-DOMAINS": {
    "task": "Runtime domain modules + curator model + workspace authoring",
    "owner": "kali",
    "status": "ready",
    "subtasks": [
      {"id": "KD-1", "description": "Domain module schema (metadata.yaml + CONTEXT.md + PROMPTS/)", "owner": "kali", "status": "ready"},
      {"id": "KD-2", "description": "Curator assignments for all 10 domains", "owner": "kali", "status": "ready"},
      {"id": "KD-3", "description": "domain_loader.py (sync, token-budgeted)", "owner": "maat", "status": "backlog"},
      {"id": "KD-4", "description": "gemini-notebook domain module (first)", "owner": "maat", "status": "backlog"}
    ]
  },
  "HEADROOM-INTEGRATION": {
    "task": "Semantic compression middleware for tool outputs + RAG",
    "owner": "maat",
    "status": "ready",
    "subtasks": [
      {"id": "HR-1", "description": "HeadroomMiddleware in src/omega/oracle/middleware/", "owner": "maat", "status": "ready"},
      {"id": "HR-2", "description": "Wire into ModelGateway provider chain", "owner": "maat", "status": "backlog"},
      {"id": "HR-3", "description": "MCP headroom_compress/headroom_retrieve tools", "owner": "maat", "status": "backlog"}
    ]
  },
  "ZSWAP-SUBSYSTEM": {
    "task": "zswap + NVMe swap validated config (16GB NVMe swap, zswap enabled 25% pool lzo_rle zsmalloc, zRAM disabled, swappiness=100, cgroup limits)",
    "owner": "maat",
    "status": "in_progress",
    "subtasks": [
      {"id": "ZS-1", "description": "Deploy zswap sysctl + kernel cmdline (max_pool_percent=25, lzo_rle, zsmalloc, zswap.enabled=1)", "owner": "maat", "status": "ready"},
      {"id": "ZS-2", "description": "Deploy 16GB NVMe swap file + omega.service with cgroup limits (MemoryMax=6G, MemorySwapMax=infinity)", "owner": "maat", "status": "ready"},
      {"id": "ZS-3", "description": "Package as WAD: config/wads/ryzen-5700u-sovereign/", "owner": "maat", "status": "backlog"}
    ]
  }
}
```

---

### 2. `data/coordination/HMC_COLLABORATION_HUB.md` — **Team Coordination Center**
**Update Sections**:
- **NEXT_ACTION**: Point to new workstreams (GEMINI-NOTEBOOK, DOCUMENTATION-SYSTEM, LOCAL-INFERENCE-OPT, KNOWLEDGE-DOMAINS, HEADROOM-INTEGRATION, ZRAM-SUBSYSTEM)
- **Add**: Cross-reference to new domain system docs
- **Update**: NOTEBOKLM section to reflect v2.0 free-tier-only direction
- **Add**: Headroom integration status
- **Add**: Knowledge Domains curator assignments table

---

### 3. `data/coordination/GAP_REGISTRY.json` — **Gap Authority**
**Register New Gap Prefixes** (per rules: distinct prefix, never reuse R1-R99):
```json
{
  "GN-1": {"topic": "Gemini Notebook workspace creation", "status": "open", "plan": "gemini_notebook_v2", "prefix": "GN"},
  "GN-2": {"topic": "Gemini Notebook runtime module", "status": "open", "plan": "gemini_notebook_v2", "prefix": "GN"},
  "DS-1": {"topic": "Documentation system meta-doc", "status": "open", "plan": "documentation_system", "prefix": "DS"},
  "LI-1": {"topic": "AdaptiveContextBuffer implementation", "status": "open", "plan": "local_inference_opt", "prefix": "LI"},
  "KD-1": {"topic": "Domain module schema", "status": "open", "plan": "knowledge_domains", "prefix": "KD"},
  "HR-1": {"topic": "HeadroomMiddleware implementation", "status": "open", "plan": "headroom_integration", "prefix": "HR"},
  "ZS-1": {"topic": "zswap sysctl + kernel cmdline deployment", "status": "in_progress", "plan": "zswap_subsystem", "prefix": "ZS"}
}
```

---

### 4. `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` — **Knowledge Gaps SSOT**
**Add New Research Jobs** (extend Phase 1-4 plan):
```markdown
## Phase 5: Gemini Notebook & Documentation System (NEW)

| Job ID | Topic | Priority | Owner | Deliverable |
|--------|-------|----------|-------|-------------|
| R57 | Headroom integration benchmarks (local models) | P1 | researcher | R_HEADROOM_LOCAL_BENCHMARKS.md |
| R58 | Domain module loader performance | P2 | researcher | R_DOMAIN_LOADER_PERF.md |
| R59 | Free-tier Gemini Notebook ToS mitigation validation | P1 | researcher | R_GEMINI_TOS_MITIGATION.md |
| R60 | Adaptive context buffer quality metrics | P2 | researcher | R_ADAPTIVE_CONTEXT_QUALITY.md |
```

---

### 5. `data/coordination/SESSION_ANCHOR.md` — **Session Recovery**
**Update State Section**:
```markdown
**State**: GEMINI NOTEBOOK v2.0 + DOCUMENTATION SYSTEM + LOCAL INFERENCE OPT + KNOWLEDGE DOMAINS + HEADROOM + ZRAM — ALL PLANNED, EXECUTION STARTING

**Active Workstreams** (from ACTIVE_SPRINT.json):
- GEMINI-NOTEBOOK (GN-1..GN-4)
- DOCUMENTATION-SYSTEM (DS-1..DS-5)
- LOCAL-INFERENCE-OPT (LI-1..LI-5)
- KNOWLEDGE-DOMAINS (KD-1..KD-4)
- HEADROOM-INTEGRATION (HR-1..HR-3)
- ZSWAP-SUBSYSTEM (ZS-1..ZS-3)

**Immediate Next Actions**:
1. Deploy zswap sysctl + kernel cmdline + NVMe swap file (ZS-1, ZS-2)
2. Create DOMAIN_DOCUMENTATION_SYSTEM.md (DS-1)
3. Create workspace folder structure (DS-2)
4. Begin AdaptiveContextBuffer + SequentialModelLoader (LI-1)
5. Begin HeadroomMiddleware (HR-1)
```

---

### 6. `docs/strategy/STRATEGY_INDEX.md` — **Strategy Hierarchy**
**Add Domain Layer Reference**:
```markdown
## LAYER 2B: DOMAIN SPECIFICATIONS (NEW)
| Document | Domain | Purpose |
|----------|--------|---------|
| `docs/strategy/domains/gemini-notebook/STRATEGY_V2.md` | gemini-notebook | Free-tier Gemini Notebook strategy v2.0 |
| `docs/strategy/domains/<domain>/STRATEGY_V<major>.<minor>.md` | <domain> | Domain strategy SSOT |
| `docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md` | all | Meta-doc: workspace/runtime/sync/curator |
```

**Update Layer 2 (Active Specs)**:
- Add `docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md`
- Add `docs/strategy/domains/gemini-notebook/` reference
- Move `NOTEBOOKLM_BEST_PRACTICES.md` to Layer 3 (superseded)

---

### 7. `docs/strategy/STRATEGY_CORPUS_MAP.md` — **Fine-Grained Preservation**
**Add Domain System Rows**:
```markdown
| Domain System | DOMAIN_DOCUMENTATION_SYSTEM.md | ACTIVE | Meta-doc for workspace/runtime/sync/curator |
| Gemini Notebook v2 | docs/strategy/domains/gemini-notebook/STRATEGY_V2.md | ACTIVE | Free-tier 3-account, notebooklm-py, 30 DR/mo |
| Local Inference Opt | src/omega/research/adaptive_context.py + sequential_loader.py | ACTIVE | Tier 0/1/2, sequential, q8_0 KV, adaptive buffer |
| Headroom Integration | src/omega/oracle/middleware/headroom.py | PLANNED | Semantic compression for tool outputs + RAG |
| Knowledge Domains | config/domains/<domain>/ + docs/strategy/domains/<domain>/ | PLANNED | Runtime modules + workspace authoring + curator |
```

---

### 8. `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` — **Vision SSOT**
**Update §4 Priority Stack** (post-DOC-1):
```markdown
## §4 Priority Stack (Post-Debut)

### IMMEDIATE (Post-Debut Week 1)
- **GN-1..GN-4**: Gemini Notebook domain (free-tier, 3 accounts, 30 DR/mo)
- **DS-1..DS-5**: Documentation system (workspace + runtime + sync)
- **LI-1..LI-5**: Local inference optimization (Tier 0/1/2, sequential, q8_0 KV)
- **KD-1..KD-4**: Knowledge domains (runtime modules + curator model)
- **HR-1..HR-3**: Headroom integration (semantic compression)
- **ZS-1..ZS-3**: zswap + NVMe swap subsystem (validated config deployment)

### POST-DEBUT PHASE B (Week 2-4)
- DEL-1 Week 1 (minus vault CLI)
- Vault overhaul (Path B: embed keyring in ModelGateway)
- Community installer / QUICKSTART / CONTRIBUTING
- NL-1 NotebookLM pipeline (prepare_notebooklm.py)
```

---

### 9. `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` — **Execution SSOT**
**Add Post-Debut Phase** (after PUB-1 allowlist):
```markdown
## POST-DEBUT EXECUTION PHASE (Week 1-4)

### Week 1: Foundation Systems
- [ ] GN-1: Gemini Notebook workspace + doc migration
- [ ] DS-1: DOMAIN_DOCUMENTATION_SYSTEM.md
- [ ] LI-1: AdaptiveContextBuffer + SequentialModelLoader
- [ ] ZS-1: zswap sysctl + kernel cmdline deployment
- [ ] ZS-2: 16GB NVMe swap file + omega.service with MemoryMax=6G

### Week 2: Domain System + Headroom
- [ ] DS-2: docs/strategy/domains/ folder structure
- [ ] DS-3: Migrate gemini-notebook docs
- [ ] KD-1: Domain module schema
- [ ] HR-1: HeadroomMiddleware
- [ ] LI-2: q8_0 KV cache profiles

### Week 3: Runtime Modules + Integration
- [ ] DS-4: config/domains/ runtime modules
- [ ] DS-5: sync_domain_docs.py
- [ ] KD-3: domain_loader.py
- [ ] KD-4: gemini-notebook domain module
- [ ] HR-2: ModelGateway integration
- [ ] LI-3: llama-fit-params hardware detection

### Week 4: Polish + Smoke Test
- [ ] GN-3: Free-tier fetch pipeline + systemd timer
- [ ] GN-4: NLG-SMOKE (blocked on V-1 Vault)
- [ ] HR-3: MCP headroom tools
- [ ] ZS-3: WAD packaging
- [ ] LI-4: Tier 0 model matrix deployment
- [ ] LI-5: Startup script (zswap + NVMe swap + THP + pinning + prompt caching)
```

---

### 10. `docs/strategy/SOVEREIGN_MANDATES.md` — **Law (Verify Compliance)**
**Verify New Architecture Complies**:
- ✅ M1 AnyIO — SequentialModelLoader uses AnyIO
- ✅ M2 Engine-Stack Firewall — Domain modules in `config/domains/` (Stack), Engine in `src/omega/`
- ✅ M7 Local-First — Tier 0/1/2 all local-first, cloud fallback only
- ✅ M8 Zero Telemetry — Headroom local, no cloud calls
- ✅ M13 Temple-Grade — q8_0 KV, sequential loading, hardware detection
- ✅ M16 Modularity — Domain modules are portable, decoupled
- ✅ M23 Failure Integrity — OOM → fallback chain, no soft degradation
- ✅ M24 Venv Sovereignty — All Python in `.venv`

---

### 11. `docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md` — **NEW META-DOC (Create)**
**Full specification** (from holistic plan §2):
- Dual-layer architecture (workspace + runtime)
- Document lifecycle (NEW → ACTIVE → SUPERSEDED → ARCHIVED)
- Naming conventions
- Sync mechanism (validated copy, not symlink)
- Curator model (config flag, not middleware)
- Cross-reference protocol
- Supersession banner standard

---

### 12. `docs/strategy/domains/gemini-notebook/STRATEGY_V2.md` — **Domain Strategy SSOT**
**Create from unified strategy v2.0** (free-tier-only, 3 accounts, notebooklm-py)

---

### 13. `docs/strategy/domains/gemini-notebook/CONTEXT.md` — **Runtime Context**
**Single file** (PLAYBOOK + ARCHITECTURE + GOTCHAS + LESSONS) for runtime loading

---

### 14. `config/domains/gemini-notebook/metadata.yaml` — **Runtime Metadata**
```yaml
version: "2.0"
target_context_window: 16384
rot_class: "research"
owner: "researcher"
cost_model: "free_tier_only"
accounts: 3
dr_per_month: 30
tos_risk: "high_mitigated"
dependencies: []
```

---

### 15. `config/domains/gemini-notebook/PROMPTS/` — **Prompt Templates**
- `planner.txt`
- `executor.txt`
- `critic.txt`

---

### 15. `src/omega/oracle/middleware/headroom.py` — **NEW**
```python
# HeadroomMiddleware replacing deprecated binary version
from headroom import compress, CompressConfig
```

---

### 16. `src/omega/research/adaptive_context.py` — **NEW**
```python
# AdaptiveContextBuffer + SequentialModelLoader
```

---

### 17. `src/omega/research/sequential_loader.py` — **NEW**
```python
# SequentialModelLoader with weight caching
```

---

### 18. `scripts/sync_domain_docs.py` — **NEW**
```python
# Validated copy: workspace → runtime (not symlink)
```

---

### 18. `scripts/startup_optimizations.sh` — **NEW**
```bash
# zswap + NVMe swap + THP + pinning + no-mmap + mlock + prompt caching
```

---

### 19. `config/providers.yaml` — **Update**
- Add q8_0 KV cache profiles per hardware tier
- Add hardware-tier model matrix

---

### 20. `config/domains/` — **Directory Structure**
```
config/domains/
├── gemini-notebook/
│   ├── metadata.yaml
│   ├── CONTEXT.md
│   ├── PROMPTS/
│   └── sources/
└── (other domains...)
```

---

### 21. `docs/strategy/domains/gemini-notebook/` — **Workspace Structure**
```
docs/strategy/domains/gemini-notebook/
├── STRATEGY_V2.md
├── GAP_AUDIT_20260820.md
├── RESEARCH_EXISTENTIAL.md
├── RESEARCH_OPERATIONAL.md
├── RESEARCH_ARBITRATION.md
├── SYNTHESIS_V2.md
├── IMPLEMENTATION_GUIDE.md
└── ARCHIVE/
    ├── BEST_PRACTICES_v1.md
    ├── R52c_INGESTION_v1.md
    ├── R52_EXTERNAL_AI_v1.md
    └── R52_EXECUTION_PLAN_v1.md
```

---

### 22. `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` — **Update to v2.0**
- Already corrected (9 edits applied)
- Add supersession banner for v1.0
- Update provenance to reference synthesis doc

---

### 23. `data/coordination/PIVOT_LOG.md` — **Register D-Series**
```markdown
## D-578: Gemini Notebook v2.0 Strategy Ratified (2026-08-20)
**Decision**: Free-tier only (3 accounts, 30 DR/mo), notebooklm-py tool, 2-notebook architecture, honor SDP §10 gate, master_token.json auth.

## D-579: Modular Domain Documentation System (2026-08-20)
**Decision**: Dual-layer (workspace + runtime), validated copy sync, curator config flag, domain module schema.

## D-580: Local Inference Tiered Architecture (2026-08-20)
**Decision**: Tier 0/1/2 auto-detected, sequential loading, q8_0 KV, adaptive context buffer, Headroom integration.

## D-581: zswap + NVMe Swap Confirmed — D-526 REAFFIRMED (2026-08-20)
**Decision**: zswap + NVMe swap file architecture — 16GB NVMe swap, zswap enabled (max_pool_percent=25, lzo_rle, zsmalloc), zRAM DISABLED, swappiness=100, cgroup MemoryMin=2G/MemoryHigh=5G/MemoryMax=6G. Reaffirms D-526 (zswap > zRAM). ADR-2026-08-10-001 ACCEPTED (Carmack + Researcher + Jem + LongCat + Nemotron 3 Ultra). D-527 "never both" stays LOCKED.
```

---

### 24. `data/coordination/KALI_DEV_ROADMAP_20260811.md` — **Dev Roadmap**
**Add Post-Debut Phase** with new workstreams

---

### 25. `data/coordination/KALI_OVERSIGHT_PORTFOLIO_20260811.md` — **Oversight Portfolio**
**Add New Workstreams** to portfolio tracking

---

## 📋 EXECUTION ORDER (Lock-In Sequence)

| Phase | Docs to Update | Purpose |
|-------|----------------|---------|
| **0** | `ACTIVE_SPRINT.json`, `HMC_COLLABORATION_HUB.md`, `GAP_REGISTRY.json` | Lock workstreams + gaps + coordination |
| **1** | `SESSION_ANCHOR.md`, `RESEARCH_PLAN_PHASE1_4_20260813.md` | Session recovery + knowledge gaps |
| **2** | `STRATEGY_INDEX.md`, `STRATEGY_CORPUS_MAP.md` | Strategy hierarchy + fine-grained preservation |
| **3** | `SOVEREIGN_ARK_BLUEPRINT.md`, `DEBUT_REMEDIATION_MANUAL_20260817.md` | Vision + execution SSOT |
| **4** | `SOVEREIGN_MANDATES.md` | Verify compliance |
| **5** | Create new docs: `DOMAIN_DOCUMENTATION_SYSTEM.md`, domain workspaces, runtime modules, new engine classes | Implement architecture |
| **6** | `PIVOT_LOG.md`, `KALI_DEV_ROADMAP.md`, `KALI_OVERSIGHT_PORTFOLIO.md` | Decision registry + roadmap + portfolio |

---

## ✅ VALIDATION GATE (Before Implementation)

Run after Phase 0-3 updates:
```bash
# 1. Validate tracking state
.venv/bin/python scripts/validate_tracking_state.py

# 2. Verify ACTIVE_SPRINT.json structure
.venv/bin/python -c "
import json
with open('data/coordination/ACTIVE_SPRINT.json') as f:
    s = json.load(f)
print('Workstreams:', list(s['workstreams'].keys()))
for k, v in s['workstreams'].items():
    print(f'  {k}: {v[\"status\"]} ({len(v.get(\"subtasks\", []))} subtasks)')
"

# 3. Verify GAP_REGISTRY.json new prefixes
.venv/bin/python -c "
import json
with open('data/coordination/GAP_REGISTRY.json') as f:
    g = json.load(f)
new_prefixes = [k for k in g['gaps'] if k.startswith(('GN','DS','LI','KD','HR','ZR'))]
print('New gap prefixes:', new_prefixes)
"

# 4. Verify HMC hub NEXT_ACTION updated
grep -A5 'NEXT_ACTION' data/coordination/HMC_COLLABORATION_HUB.md
```

---

**This locks the entire holistic plan into the sovereign tracking infrastructure. Every workstream has gaps, owners, status, and cross-references.**

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_tracker_plan ⬡ 2026-08-20*