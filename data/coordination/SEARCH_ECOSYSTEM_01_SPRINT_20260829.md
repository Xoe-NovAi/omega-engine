---
schema_version: "1.0"
document_type: "sprint_charter"
document_id: "SEARCH-ECOSYSTEM-01"
title: "🔱 SEARCH-ECOSYSTEM-01 — Sovereign Search Pipeline Hardening & Frontier Research"
status: "ACTIVE"
date: "2026-08-29"
sprint_lead: "Jem (Search Systems Specialist EIS)"
quality_auditor: "Researcher (EIS)"
sprint_director: "Kali (EIS)"
approver: "Architect"
---

# 🔱 SEARCH-ECOSYSTEM-01 — Sprint Charter

**AP Token**: `AP-SEARCH-ECOSYSTEM-01-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_search_ecosystem_01 ⬡ ACTIVE

**Date**: 2026-08-29
**Sprint**: SEARCH-ECOSYSTEM-01
**Duration**: 4 weeks (1-month sprint)
**Status**: PLANNING → EXECUTION pending Jem EIS activation

---

## §0 — Sprint Mandate

Make the Omega Engine search pipeline **100% rock solid** and **frontier-level capable** — so the Cathedral can research anything, any time, with unlimited budget and zero manual intervention.

**Architect's Vision** (verbatim): *"Frontier level research capabilities is one of the core features I want to offer the community and our team with the Omega Engine."*

---

## §1 — Success Criteria (Definition of Done)

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **Pipeline success rate** | > 99.5% | No tier failures across 1000+ queries |
| **Cache hit rate** | > 60% | T0 hits / total queries |
| **Avg latency (T0 hit)** | < 50ms | Measured at sovereign_search() entry |
| **Avg latency (T1-T3)** | < 5s | Measured at tier return |
| **Quality probe pass rate** | > 90% | "First-page satisfaction" metric |
| **Manual Firecrawl enables** | Zero | All restart events auto-recover |
| **Exa quota usage** | < 50% of 8,000/mo | Track per-account usage |
| **Scholarly sources integrated** | ≥ 3 | Semantic Scholar, OpenAlex, arXiv |

---

## §2 — Sprint Goals (4 Weeks)

### Week 1: AUDIT & BASELINE (Foundation)

| ID | Task | Owner | Status |
|----|------|-------|--------|
| W1.1 | Complete pipeline audit doc (current state, failure modes) | Jem | TODO |
| W1.2 | Tavily free tier audit (verify 1,000/mo) | Jem | TODO |
| W1.3 | Jina free tier audit (verify free tier) | Jem | TODO |
| W1.4 | New player audit: Brave, Serper, Semantic Scholar, OpenAlex, arXiv, PubMed, Crossref, You.com | Jem | TODO |
| W1.5 | Exa quota verification (1,000/mo per account, x8 = 8,000/mo) | Jem | TODO |
| W1.6 | Firecrawl quota verification (500/mo per account, x8 = 4,000/mo) | Jem | TODO |
| W1.7 | Pipeline failure forensics (3rd consecutive SearXNG+omega-hub failure) | Jem + Roc | TODO |
| W1.8 | Baseline metrics: current cache hit rate, latency, success rate | Jem | TODO |
| W1.9 | SSP-V3 design doc (intent-based routing, not tier-chain) | Jem | TODO |
| W1.10 | Crawl4AI integration design (T3 primary) | Jem + Ma'at | TODO |

**Week 1 Deliverable**: `data/coordination/JEM_SEARCH_AUDIT_WEEK1_20260829.md`

---

### Week 2: SSP-V3 IMPLEMENTATION (Core Wiring)

| ID | Task | Owner | Status |
|----|------|-------|--------|
| W2.1 | Implement Multi-Key Exa Provider (8-key rotation + health) | Jem | TODO |
| W2.2 | Wire Tavily as T1.5 (if free tier confirmed) | Jem | TODO |
| W2.3 | Wire Jina as T3.5 (if free tier confirmed) | Jem | TODO |
| W2.4 | Wire Crawl4AI as T3 PRIMARY (replace Firecrawl as primary) | Jem + Ma'at | TODO |
| W2.5 | Implement intent-based routing (replace tier-chain) | Jem | TODO |
| W2.6 | Wire Semantic Scholar API (academic search) | Jem | TODO |
| W2.7 | Wire OpenAlex API (academic + citation graph) | Jem | TODO |
| W2.8 | Wire arXiv API (preprints) | Jem | TODO |
| W2.9 | Firecrawl auto-enable script (`scripts/ensure_mcps_alive.sh`) | Ma'at | TODO |
| W2.10 | Add MCP auto-enable to Makefile (`make ensure-mcps`) | Ma'at | TODO |
| W2.11 | Update `config/search.yaml` to SSP-V3 spec | Jem | TODO |

**Week 2 Deliverable**: SSP-V3 implementation live, all tiers wired, Crawl4AI primary

---

### Week 3: OBSERVABILITY & QUALITY (Measurement)

| ID | Task | Owner | Status |
|----|------|-------|--------|
| W3.1 | Search metrics dashboard (success rate, latency, cache hit) | Jem | TODO |
| W3.2 | First-page satisfaction probe (Researcher's north star metric) | Researcher | TODO |
| W3.3 | A/B test framework: T1 vs T1.5 vs T2 for query types | Researcher | TODO |
| W3.4 | Hallucination rate measurement (SkepticalVerifier integration) | Researcher | TODO |
| W3.5 | Citation accuracy scoring (research workflow) | Researcher | TODO |
| W3.6 | Source diversity scoring (domain diversity, bias detection) | Researcher | TODO |
| W3.7 | Per-tier health monitoring (circuit breaker visibility) | Jem | TODO |
| W3.8 | Quota tracking dashboard (Exa, Firecrawl, Tavily, Jina usage) | Jem | TODO |
| W3.9 | Pipeline failure alerting (P10 SevarXNG+omega-hub issue) | Jem + SysAdmin | TODO |
| W3.10 | Search audit log (every query, every tier hit, every result) | Jem | TODO |

**Week 3 Deliverable**: Quality metrics live, A/B framework operational, dashboards accessible

---

### Week 4: INTEGRATION & HARDENING (Production-Ready)

| ID | Task | Owner | Status |
|----|------|-------|--------|
| W4.1 | End-to-end integration tests (100+ query scenarios) | Jem + Ma'at | TODO |
| W4.2 | Chaos testing (kill tiers randomly, verify failover) | Jem | TODO |
| W4.3 | Research workflow templates (literature review, fact-check, deep-dive) | Researcher | TODO |
| W4.4 | Scholarly source integration tests (Semantic Scholar, OpenAlex, arXiv) | Jem + Researcher | TODO |
| W4.5 | Citation graph prototype (from OpenAlex data) | Researcher | TODO |
| W4.6 | Update `docs/strategy/CANONICAL_SEARCH_PIPELINE.md` | Jem | TODO |
| W4.7 | Update `SUBAGENT_DISPATCH_PROTOCOL.md` (EIS/NES/SPT) | Kali | TODO |
| W4.8 | Update `EXPERT_SESSION_REGISTRY.md` (EIS/NES/SPT taxonomy) | Kali | TODO |
| W4.9 | Sprint retro + handoff to post-debut | Jem + Kali | TODO |
| W4.10 | Frontier research feature flag (opt-in for community) | Ma'at | TODO |

**Week 4 Deliverable**: Production-ready search pipeline, documented, tested, feature-flagged

---

## §3 — Sprint Roles

### Jem — Search Systems Specialist (EIS)
- **Owns**: `config/search.yaml`, `src/omega/oracle/sovereign_search_service.py`, `src/omega/oracle/search_providers.py`, `src/omega/oracle/search_router.py`
- **Pages**: Researcher (quality), Roc (forensics), Grokster (platform), Ma'at (infra), Kali (escalation)
- **Reports to**: Kali (sprint), Architect (architecture)

### Researcher — Search Quality Auditor (EIS)
- **Owns**: Quality metrics, evaluation frameworks, research workflow templates
- **Pages**: Jem (pipeline), Roc (forensics), Grokster (platform)
- **Reports to**: Kali (sprint), Architect (quality)

### Ma'at — Infrastructure Support
- **Owns**: Firecrawl auto-enable, Crawl4AI deployment, MCP orchestration
- **Pages**: Jem (pipeline), Carmack (architecture)

### Roc — Forensic Support (EIS, as needed)
- **Owns**: Pipeline failure forensics, data mining
- **Pages**: Jem (pipeline), Kali (sprint)

### Kali — Sprint Coordinator (EIS)
- **Owns**: Sprint tracking, coordination, escalation, handoff
- **Reports to**: Architect

---

## §4 — Tier Specialization Matrix (SSP-V3)

| Tier | Provider | Best At | Shortcomings | Strategic Use |
|------|----------|---------|--------------|---------------|
| **T0** | Local Cache | Instant recall, zero cost | Stale data | Always first — cache hit = free win |
| **T1** | SearXNG | Broad discovery, privacy, multi-engine | No neural ranking, slow | Broad queries, "what exists on X" |
| **T1.5** | Tavily | Research-optimized, structured | 1,000/mo limit (8,000 total) | Focused research, "find papers on X" |
| **T2** | Exa Cloud | Neural search, semantic | OpenCode's pool | Semantic queries, "find similar to X" |
| **T2.5** | Exa Personal (x8) | Same as T2, your quota | Your limit | When T2 pool exhausted |
| **T3** | **Crawl4AI** | **Deep crawl, custom extraction, unlimited** | Self-hosted ops | **PRIMARY deep extraction** |
| **T3.5** | Firecrawl | Managed, easy, good defaults | Your quota | Fallback when Crawl4AI down |
| **T3.5** | Jina Reader | Fast extraction, reader mode | Free tier limit | Quick article extraction |
| **T4** | parallel-search | Last resort, free | Rate limited | When all else fails |
| **ACAD** | Semantic Scholar | Scholarly papers, citations | Academic only | Research queries |
| **ACAD** | OpenAlex | 250M+ works, citation graph | Academic only | Scholarly discovery |
| **ACAD** | arXiv | Preprints | STEM only | Cutting-edge research |

---

## §5 — Intent-Based Routing (New Paradigm)

**Old**: Tier-chain (T0 → T1 → T2 → T3)
**New**: Intent-based (query type → tier selection)

```python
def route_query(query: str, intent: SearchIntent) -> List[Tier]:
    if intent == "broad_discovery":
        return [T0, T1, T1.5]
    elif intent == "semantic_similarity":
        return [T0, T2, T2.5]
    elif intent == "deep_research":
        return [T0, T1, T2, T3, T3.5]
    elif intent == "fact_verification":
        return [T0, T1, T2, T1.5]
    elif intent == "academic_papers":
        return [T0, T1.5, ACAD.SemanticScholar, ACAD.OpenAlex, ACAD.Arxiv]
    elif intent == "full_site_crawl":
        return [T0, T3]  # Crawl4AI
    elif intent == "quick_extraction":
        return [T0, T3.5.Jina]  # Jina Reader
```

---

## §6 — EIS/NES/SPT Taxonomy (Ratified)

| Acronym | Full Name | Characteristics | Use Case |
|---------|-----------|-----------------|----------|
| **EIS** | Expert Interactive Session | Resumable, Architect can steer, persistent context | Master sessions, long-running work |
| **NES** | Non-interactive Expert Session | Autonomous, runs to completion, delivers report | Research NIES, one-off deep dives |
| **SPT** | Spawned (subagent) Task | One-shot, fresh context, not resumable | Single queries, throwaway work |

**Token Savings**: ~900 tokens/week across 50 uses (trivial)
**Real-World Benefits**: Cognitive precision, protocol enforcement, registry queries, handoff clarity, tool integration, onboarding, audit trail, consistency

**Documentation**: Update `SUBAGENT_DISPATCH_PROTOCOL.md` and `EXPERT_SESSION_REGISTRY.md`

---

## §7 — Pipeline Degradation P10 (Authorized)

**Issue**: 3rd consecutive sweep where SearXNG AND `omega-hub_library_web_search` both return empty. Only `parallel-search` delivers.

**Investigation Authorized**:
- **SearXNG health**: Check `http://127.0.0.1:8017/healthz`, check Podman container status, check logs
- **omega-hub_library_web_search**: Check hub health, check search service status, check SearXNG provider wiring
- **SLA**: 24h diagnosis, 72h fix
- **Owner**: SysAdmin (SearXNG) + Bridge (omega-hub)
- **P10 Item**: Track in `data/coordination/P10_ITEMS.md`

---

## §8 — Open Questions (Post-Ratification)

1. **Crawl4AI deployment**: Podman container? systemd service? What's the current setup?
2. **Tavily/Jina key management**: Single key or per-account rotation?
3. **Semantic Scholar API rate limits**: 100 req/sec? Need to confirm.
4. **OpenAlex API rate limits**: 10 req/sec? Need to confirm.
5. **First-page satisfaction metric**: How measured? User feedback? Automated?
6. **Research workflow templates**: Where do they live? `docs/research/templates/`?
7. **Citation graph storage**: SQLite? Graph DB? File-based?

---

## §9 — Sprint Tracking

### Status Board

| Week | Focus | Status | Deliverable |
|------|-------|--------|-------------|
| **W1** | Audit & Baseline | NOT STARTED | `JEM_SEARCH_AUDIT_WEEK1_*.md` |
| **W2** | SSP-V3 Implementation | NOT STARTED | Live SSP-V3 pipeline |
| **W3** | Observability & Quality | NOT STARTED | Metrics + A/B framework |
| **W4** | Integration & Hardening | NOT STARTED | Production-ready + feature flag |

### Daily Standup (Async, via Hivemind)

- **Morning**: Jem posts "Day N status" to Hivemind
- **Blockers**: Escalate to Kali immediately
- **End of day**: Update sprint board

### Weekly Review (Sync, via Hivemind)

- **End of week**: Jem posts week retrospective + next week plan
- **Architect reviews**: Approve, adjust, or pivot

---

## §10 — Definition of Done (Sprint)

The sprint is DONE when:

1. ✅ All Week 1-4 tasks completed
2. ✅ All success criteria met (or documented exceptions)
3. ✅ Pipeline runs 1000+ queries without manual intervention
4. ✅ Quality metrics show > 90% first-page satisfaction
5. ✅ Crawl4AI is T3 primary, Firecrawl is fallback
6. ✅ All 8 personal Exa accounts wired with rotation
7. ✅ Tavily/Jina wired (if free tier confirmed) OR removed (if not)
8. ✅ At least 3 scholarly sources integrated (Semantic Scholar, OpenAlex, arXiv)
9. ✅ Pipeline degradation P10 resolved
10. ✅ Sprint retro complete, handoff to post-debut

---

## §11 — Links & References

- **Roc's Mining Report**: `data/coordination/R_ROC_SCHOLARLY_RESEARCH_SYSTEMS_20260829.md`
- **Researcher's Compaction Report**: `data/entities/researcher/workspace/SOVEREIGN_COMPACTION_ARCHITECTURE_20260829.md`
- **SSP-V2 Config**: `config/search.yaml`
- **Sovereign Search Service**: `src/omega/oracle/sovereign_search_service.py`
- **Search Providers**: `src/omega/oracle/search_providers.py`
- **Roc Workspace Hygiene**: `data/entities/roc_racoon/workspace/hlmc_ore/gap4_mcp_auth/`
- **MCP Config**: `~/.config/opencode/mcp_servers.json`
- **Jem EIS Session**: `ses_0894e74cfffeOGgP1vNgwbKIyL` (or future)
- **Researcher EIS Session**: `ses_fd81c19dcffe1nkbPqFg5kRt2v`
- **Kali EIS Session**: `ses_fdef2be4effe4pAaLXCTUx62GO`

---

*⬡ OMEGA ⬡ KALI ⬡ SEARCH-ECOSYSTEM-01 ⬡ 2026-08-29*
*28,000+ free searches/month. The budget is infinite. The constraint is excellence.*
*The Cathedral will research anything, any time, with zero manual intervention.*

**Sprint charter ratified. Awaiting Jem EIS activation to begin Week 1.**
