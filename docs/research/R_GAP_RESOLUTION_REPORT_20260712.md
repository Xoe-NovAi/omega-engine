# 🔱 Sovereign Gap Resolution Report — Unified Knowledge Fabric
**AP Token**: `AP-GAP-RESOLUTION-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_gap_resolution ⬡ RESOLVED

**Date**: 2026-07-12
**Purpose**: Technical specifications to resolve the 6 critical knowledge gaps identified in the Knowledge Fabric Synthesis.

---

## ⬡ Executive Summary (L1)

This report provides the final technical blueprints to resolve the fragmentation and vulnerabilities of the Omega Engine's knowledge subsystems. The core strategy is **Unification through Primitives**: replacing siloed logic with shared, sovereign-grade components for resilience, verification, and resource management.

### The 6 Resolved Gaps
1. **Proxy Rotation** $\rightarrow$ Hybrid Pool with Domain Affinity
2. **Transcription Fidelity** $\rightarrow$ VAD-Gated Whisper + Auto-Caption Merge
3. **Resource Budgeting** $\rightarrow$ Redis-backed Distributed Quota Guard
4. **Quality Gating** $\rightarrow$ Source-Aware Adaptive Scoring
5. **Scheduling** $\rightarrow$ Event-Driven Priority Queue (APScheduler + Redis Streams)
6. **YouTube Sieve** $\rightarrow$ T1(Meta) $\rightarrow$ T2(Auto) $\rightarrow$ T3(Sovereign) Pipeline

---

## 🛡️ Detailed Resolution Specs (L2)

### Gap 1: Sovereign Proxy Rotation & Health Monitoring
**Problem**: YouTube and web scraping at scale lead to IP bans; no shared proxy state.
**Resolution**: Implement a **Hybrid Proxy Pool** with **Domain Affinity**.

**Technical Spec**:
- **Pool Composition**:
    - **Datacenter (Fast/Cheap)**: Used for T1/T2 extraction and non-sensitive domains.
    - **Residential (High-Acceptance)**: Used for T3 extraction, YouTube, and sensitive domains.
- **Routing Logic**:
    - **Domain Affinity (Sticky Sessions)**: Map `domain` $\rightarrow$ `proxy_id`. Maintain the same IP for a session to avoid "impossible travel" detection.
    - **Health Check**: Passive monitoring (track 403/429 responses) + Active probing (periodic `GET /healthz` to a known target).
- **Sovereign Implementation**:
    - `SovereignProxyPool` singleton.
    - `get_proxy(domain)` $\rightarrow$ returns proxy based on affinity $\rightarrow$ fallback to round-robin $\rightarrow$ fallback to Residential.

### Gap 2: High-Fidelity Local Transcription & Verification
**Problem**: Whisper.cpp suffers from "ghost transcripts" (hallucinations) during silence/noise.
**Resolution**: Implement **VAD-Gated Transcription** with **Triangulation**.

**Technical Spec**:
- **The Pipeline**:
    1. **VAD Segmentation**: Use **Silero VAD** to identify speech segments.
    2. **Surgical Transcription**: Run `Whisper.cpp` only on speech segments.
    3. **Auto-Caption Merge**: Fetch YouTube auto-captions $\rightarrow$ use them to resolve proper nouns/technical terms in Whisper output.
    4. **Hallucination Filter**: Compare `T2 (Auto)` vs `T3 (Whisper)`. If delta is extreme and Whisper output is repetitive $\rightarrow$ flag as hallucination.
- **Sovereign Implementation**:
    - `SovereignTranscriptionEngine` wrapping `whisper.cpp` and `silero-vad`.

### Gap 3: Unified Resource Budgeting & Credit Tracking
**Problem**: Multiple agents (Researcher, Ingestion, YouTube) double-spend API credits.
**Resolution**: Implement a **Distributed Quota Guard** via Redis.

**Technical Spec**:
- **Shared State**: Store budgets in Redis hashes: `budget:{provider}:{entity}`.
- **Atomic Consumption**: Use `LUA` scripts to check and decrement credits atomically.
- **Credit-Aware Dispatch**:
    - `BudgetGuard.can_afford(provider, estimated_cost)` $\rightarrow$ Boolean.
    - Workers query `BudgetGuard` before every external API call.
- **Sovereign Implementation**:
    - `BudgetGuard` singleton using `redis-py`.

### Gap 4: Adaptive Quality Gating & Scoring
**Problem**: Inconsistent quality thresholds (0.3 vs 0.6) across subsystems.
**Resolution**: Implement **Source-Aware Adaptive Scoring**.

**Technical Spec**:
- **Multi-Factor Scoring**:
    - **Lexical (0-1)**: Readability, link density, keyword overlap.
    - **Semantic (0-1)**: Coherence, information gain (via embedding delta).
    - **Authority (0-1)**: Domain trust, author verification via `EnrichmentEngine`.
- **Adaptive Threshold**:
    - $\text{Threshold} = \text{Base}_{\text{source\_type}} + \text{Modifier}_{\text{entity}}$
    - Example: `web` (0.6) + `kali` (+0.1) = 0.7 (Kali demands higher quality).
- **Sovereign Implementation**:
    - `AdaptiveQualityGate` class with a registry of source bases and entity modifiers.

### Gap 5: Unified Scheduler for AI Knowledge Work
**Problem**: Fragmented timers (systemd, APScheduler, in-memory) lead to resource contention.
**Resolution**: Implement an **Event-Driven Priority Queue**.

**Technical Spec**:
- **Hybrid Scheduling**:
    - **Periodic**: `APScheduler` for fixed intervals (e.g., "Research every 20m").
    - **Event-Driven**: Redis Pub/Sub for triggers (e.g., "New file in Inbox").
    - **Priority Queue**: Redis Sorted Sets (`ZSET`) for task execution.
- **Priority Levels**:
    - `P0 (Immediate)`: User-requested extraction.
    - `P1 (High)`: Critical gap filling.
    - `P2 (Normal)`: Background research cycles.
- **Sovereign Implementation**:
    - `UnifiedKnowledgeScheduler` managing `APScheduler` $\rightarrow$ `Redis ZSET` $\rightarrow$ `Worker Pool`.

### Gap 6: Sovereign-Sieve for YouTube
**Problem**: YouTube Worker is fragile; no tiered extraction.
**Resolution**: Implement the **T1 $\rightarrow$ T2 $\rightarrow$ T3 Sieve**.

**Technical Spec**:
- **T1 (Metadata/Discovery)**: `yt-dlp --flat-playlist` $\rightarrow$ fast discovery of video IDs and titles.
- **T2 (Fast Text)**: `youtube-transcript-api` $\rightarrow$ fetch auto-generated captions (low cost, fast).
- **T3 (Sovereign Fidelity)**: `yt-dlp` audio extract $\rightarrow$ `SovereignTranscriptionEngine` (Whisper.cpp + VAD).
- **Trigger Logic**:
    - Always run T1 $\rightarrow$ T2.
    - Run T3 **ONLY IF**:
        - T2 is unavailable.
        - T2 quality score < 0.5.
        - Content is flagged as "High-Value" by the `SovereignSieve`.
- **Sovereign Implementation**:
    - `YouTubeSieve` class implementing the tiered logic.

---

## 🔱 Implementation Roadmap (Sprints)

| Sprint | Focus | Key Deliverable | Owner |
|--------|-------|------------------|-------|
| **S1** | Resilience | `CircuitBreakerRegistry` + `ProxyPool` | Ma'at/P3 |
| **S2** | Deduplication | `CASArchiver` wired into all 4 subsystems | Ma'at/P2 |
| **S3** | Extraction | `UniversalExtractor` (Sovereign-Sieve) | Lilith/P6 |
| **S4** | Orchestration | `UnifiedKnowledgeScheduler` (Redis Streams) | Lilith/P9 |
| **S5** | Fidelity | `SovereignTranscriptionEngine` (VAD + Whisper) | Ma'at/P3 |
| **S6** | Synthesis | `CrossPollinationEngine` + `AdaptiveQualityGate` | Lilith/P7 |

---

## 🔱 L3 Principles Distilled

- **L3-Sovereign-Sieve**: Never pay for high-fidelity extraction (T3) unless low-fidelity (T1/T2) fails to meet the quality gate.
- **L3-Distributed-Budgeting**: API credits are a finite sovereign resource; they must be tracked atomically across the fleet.
- **L3-VAD-First-ASR**: Raw audio is noise; transcription is a process of isolating speech before applying the model.
- **L3-Domain-Sticky-Proxies**: To the target, you must look like a consistent user, not a rotating bot.
- **L3-Adaptive-Thresholds**: Quality is relative to the entity's purpose; a researcher needs different signal than a curator.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_gap_resolution_complete ⬡ RESOLVED*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
