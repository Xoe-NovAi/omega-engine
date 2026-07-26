---
schema_version: "1.0"
document_type: "research_index"
document_id: "research-index-guard-distill"
title: "Research Index: Guard & Distill Sprint"
status: "ACTIVE"
version: "1.0.0"
date: "2026-07-22"
owner: "kali"
tags: ["sprint-plan", "phase-c", "p0-tickets", "llm-friendly", "guard-and-distill", "research-index"]
priority: "P0"
depends_on: []
blocks: []
acceptance_gates:
  - "All 5 research topics have structured metadata"
  - "Each topic maps to implementation files"
  - "Source quality assessment complete"
cross_references:
  - "SOVEREIGN_ARK_BLUEPRINT.md"
  - "FLEET_TEAM_PLAYBOOK.md"
  - "LLM_FRIENDLY_DOCS_BP.md"
llm_metadata:
  token_budget: 6000
  chunk_strategy: "section_per_topic"
  answer_first_sections: true
  self_contained_code: false
---

# 🔱 Research Index: Guard & Distill Sprint
**AP Token**: `AP-RESEARCH-INDEX-GUARD-DISTILL-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research_index ⬡ ACTIVE

**Date**: 2026-07-22
**Sprint**: `guard-and-distill-2026-07-22`
**Status**: ACTIVE

---

## Structured Research Metadata

```yaml
research_topics:
  - topic: "hypothesis_async_fsm"
    tickets: ["C-11"]
    sources:
      - "GitHub hypothesis/hypothesis#4107"
      - "MarkTechPost 2026-04-18: Async stateful testing with Hypothesis"
      - "TechOral 2026-06-14: RuleBasedStateMachine patterns"
      - "oneuptime 2026-01-30: Hypothesis async best practices"
    key_findings:
      - "Use sync wrapper + anyio.run() for async FSM rules"
      - "Register CI profiles: dev (max_examples=20), ci (max_examples=500, deadline=None)"
      - "suppress_health_check=[HealthCheck.too_slow] for stateful tests"
      - "derandomize=True for reproducibility"
    implementation_guidance: "tests/property/test_oom_protector_fsm.py, tests/property/test_soul_store_fsm.py"

  - topic: "restic_b2_object_lock"
    tickets: ["C-3"]
    sources:
      - "byte-guard.net 2026-06-13: Restic 3-2-1 with Backblaze B2"
      - "Backblaze 2026-06-26: Object Lock for ransomware protection"
      - "TechFuelHQ 2026-06-04: Restic backup best practices"
      - "47Network 2026-02-24: Restic + B2 production guide"
    key_findings:
      - "Use S3-compatible API, NOT B2 native backend (error handling issues)"
      - "Endpoint: s3.us-west-002.backblazeb2.com (region-specific)"
      - "Enable Object Lock on bucket creation (Compliance mode recommended)"
      - "Append-only key for server (Read+Write, NO Delete, NO ListBuckets)"
      - "Prune/forget from separate trusted machine with full key"
      - "Retention: 7 daily / 4 weekly / 6 monthly / 1 yearly (max 18 snapshots)"
      - "Systemd timer: OnCalendar=*-*-* 03:00:00 + RandomizedDelaySec=15min"
      - "Healthchecks.io dead-man's switch on backup success"
    implementation_guidance: "scripts/backup_restic.sh, /etc/systemd/system/omega-restic-backup.*"

  - topic: "mcp_streamable_http_2026_07_28"
    tickets: ["C-4a.5"]
    sources:
      - "MCP.Directory blog 2026: Streamable HTTP migration guide"
      - "Zylos Research 2026-03-08: MCP 2025-06-18 spec changes"
      - "AWS Labs issue #72: Stateless transport implementation"
      - "AgentMarketCap 2026-04-06: MCP server patterns"
      - "OpenAI Community 2026-04-02: OAuth 2.1 + PKCE for MCP"
      - "Baeseokjae 2026-05-05: Dynamic client registration"
      - "Upendra Sengar 2026: SEP-2243 stateless transport"
      - "Abhi Panseriya 2026-05-30: MCP caching headers"
    key_findings:
      - "Spec evolution: 2024-11-05 (initial) → 2025-03-26 (Streamable HTTP) → 2025-06-18 (OAuth 2.0 RS) → 2025-11-25 (PKCE mandatory) → 2026-07-28 (Stateless)"
      - "2026-07-28 key changes: No session handshake, no Mcp-Session-Id, Mcp-Method/Mcp-Name headers required, ttlMs/cacheScope caching"
      - "Transport: Single POST /mcp endpoint for JSON-RPC, optional GET /mcp for SSE"
      - "Auth: OAuth 2.1 + PKCE (S256), RFC 9728 Protected Resource Metadata, RFC 8414 AS Metadata, RFC 8707 Resource Indicators"
      - "Discovery: /.well-known/oauth-protected-resource → /.well-known/oauth-authorization-server"
      - "Dynamic Client Reg: RFC 7591"
      - "Migration: Phase 1 dual transport (Aug), Phase 2 OAuth 2.1 RS (Sep), Phase 3 Stateless (Oct)"
      - "ChatGPT connector bug: attempts SSE GET after long idle instead of token refresh — workaround: minimal SSE endpoint returning 405"
    implementation_guidance: "mcp_servers/omega_hub/server.py (Streamable HTTP + OAuth 2.1)"

  - topic: "llm_distillation_pipeline"
    tickets: ["C-0.5"]
    sources:
      - "Stratos (arXiv:2510.15992, AAAI 2026): End-to-end distillation with teacher-student pairing"
      - "Mems (GitHub 2026-03-23): L0-L3 hierarchical memory, L2 async distillation from L1"
      - "RecSys Challenge 2025: Narrative distillation with self-critique, JSON Schema constrained output"
      - "LLM-Distillery: Multi-teacher distillation, offline dataset collection, HDF5 sync"
      - "llm_tools: MapReduce/Refine summarization patterns"
      - "Knowledge Distillation Survey 2026-04-25: Adaptive strategies (Alignment vs Injection)"
    key_findings:
      - "L1 Narrative: Map-Reduce (chunk → parallel summarize → collapse → final reduce for >10 chunks)"
      - "L2 Insight: Refine/iterative condensation (sequential refinement with evidence grounding)"
      - "L3 Axiom: JSON Schema constrained output + LLM-as-Judge self-critique + retrieval-augmented verification"
      - "Quality gates: Narrative coherence, personalization depth, factual correctness metrics"
      - "BLIND STAGING MANDATORY: Write ONLY to proposed_lessons.yaml; promotion requires explicit omega-hub_soul_promote tool call"
      - "Cross-pollination: Suggest relevant L3 axioms to related entities; entity decides adoption"
    implementation_guidance: "src/omega/scribe/__init__.py, src/omega/scribe/distiller.py, tests/contract/test_soul_distiller.py"

  - topic: "quota_aware_routing"
    tickets: ["C-10.5"]
    sources:
      - "TrueFoundry 2026-02-20: Model router cost/quality/latency aware routing"
      - "CallMissed 2026-05-31: Cascade router pattern"
      - "AppScale 2026-05-21: Classifier router for specialist models"
      - "QuotaRouter (Starland9/quotarouter): Priority routing + daily token persistence + streaming + RPM limiting"
      - "DigitalOcean 2026-07-13: x-ratelimit-remaining-* headers for quota tracking"
    key_findings:
      - "QuotaRouter pattern: Priority-based routing with automatic fallback, daily token tracking with persistence, streaming support, RPM limiting"
      - "DigitalOcean quota headers: x-ratelimit-limit-requests, x-ratelimit-limit-tokens-per-day, x-ratelimit-limit-tokens-per-minute, x-ratelimit-remaining-*, x-ratelimit-reset-*"
      - "Cascade router: Try cheapest competent model first, escalate on failure; target <10% escalation rate"
      - "Integration with 429 classification: Filter quota-exhausted providers in select_provider(), score remaining by cost/quality/latency"
      - "Weighted scoring: score = 0.4*(1-cost) + 0.4*quality + 0.2*(1-latency) — tune per Kali Amendment 1"
    implementation_guidance: "src/omega/oracle/model_gateway.py (select_provider), src/omega/oracle/health_monitor.py (has_quota, record_quota_usage)"
```

---

## Cross-Reference Index

| Topic | Primary Ticket | Related Tickets | Implementation Files |
|-------|----------------|-----------------|---------------------|
| Hypothesis Async FSM | C-11 | — | tests/property/test_oom_protector_fsm.py, tests/property/test_soul_store_fsm.py |
| Restic + B2 Object Lock | C-3 | V-1 (credentials) | scripts/backup_restic.sh, systemd units |
| MCP Streamable HTTP 2026-07-28 | C-4a.5 | — | mcp_servers/omega_hub/server.py |
| LLM Distillation Pipeline | C-0.5 | C-10.5 (provider selection) | src/omega/scribe/, tests/contract/test_soul_distiller.py |
| Quota-Aware Routing | C-10.5 | C-6' (unified breakers) | src/omega/oracle/model_gateway.py, health_monitor.py |

---

## Source Quality Assessment

| Source | Recency | Authority | Relevance | Notes |
|--------|---------|-----------|-----------|-------|
| GitHub hypothesis#4107 | 2026 | Primary (project repo) | High | Direct async FSM discussion |
| MarkTechPost 2026-04-18 | 2026-04 | Technical blog | High | Practical async patterns |
| byte-guard.net 2026-06-13 | 2026-06 | Practitioner blog | High | Production restic+B2 guide |
| Backblaze 2026-06-26 | 2026-06 | Vendor docs | High | Object Lock specification |
| MCP.Directory 2026 | 2026 | Community hub | High | Migration timeline |
| Zylos 2026-03-08 | 2026-03 | Research blog | Medium | Spec change analysis |
| Stratos AAAI 2026 | 2026 | Peer-reviewed | High | Distillation architecture |
| Mems 2026-03-23 | 2026-03 | GitHub project | High | Hierarchical memory |
| QuotaRouter GitHub | 2026 | Open source | High | Working implementation |
| DigitalOcean 2026-07-13 | 2026-07 | Vendor docs | High | Quota header spec |

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-INDEX-GUARD-DISTILL ⬡ v1.0.0 ⬡ 2026-07-22*