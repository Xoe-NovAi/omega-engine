# 🔱 Sprint Hardening — Knowledge Gap Research & Hardening Plan
**AP**: `R-SPRINT-HARDENING-v1.0.0`
**Date**: 2026-07-22
**Scope**: Deep web research across all remaining Phase C/D knowledge gaps
**Model**: mimo-v2.5-free

---

## §1 C-10.5 Provider Fallback Chain — Critical Bug Class Found

### The Bug Class (2026-07-22 GA confirmed)

**Circuit breakers conflating rate-limit 429s with quota-exhausted 429s.**

When an LLM provider returns HTTP 429, the call site can't always tell whether it's:
- A transient **per-minute rate limit** (retry in seconds)
- A **monthly/daily quota** exhausted (retry only after period rolls over, possibly weeks)

A single `unhealthy_until` field picks one TTL and applies to both. Under the wrong choice:
- Quota-exhausted provider retried repeatedly until quota window resets
- Transient rate limit triggers unnecessary multi-hour fallback

**Confirmed in**: SmarterRouter issue #7, OmniRoute issues #1767/#1768/#1804, resilient-llm-router analysis.

### Recommended Implementation

**Three-state model** (from resilient-llm-router):
```
State 1: rate_limit  → cooldown: 60s (or Retry-After header)
State 2: quota       → cooldown: until period rolls over (hours/days)
State 3: circuit     → cooldown: recovery_timeout (60s default)
```

**Key insight**: Classify 429 responses using provider headers and body keywords:
- Rate limit: `x-ratelimit-*` headers, `Retry-After`
- Quota: `"monthly quota"`, `"daily limit"`, `"out of credits"` in body

**Action for C-10.5**:
1. Extend `AsyncCircuitBreaker` with `rate_limit_until` and `quota_until` fields
2. Add 429 classification logic in `record_outcome()`
3. Use `guard()` pattern: check state BEFORE calling provider

---

## §2 C-11 Test Infrastructure — 8 Flaky Test Patterns (Mergify 2026)

### Pattern Catalog

| # | Pattern | Root Cause | Fix |
|---|---------|------------|-----|
| 1 | **Fixture teardown races** | Yield-style fixtures tear down in reverse order; module/session-scoped fixtures stay alive across tests | Make cleanup defensive; scope related fixtures to same lifecycle |
| 2 | **xdist ordering surprises** | Shared state across worker processes (tmp dirs, global counters, Redis keys) | Use `tmp_path` (per-test) or `worker_id` (per-session) for namespacing |
| 3 | **Hypothesis seed non-determinism** | Different example set each run unless seed pinned | Pin seed in CI; treat new Hypothesis failure as real bug, not flake |
| 4 | **Autouse fixture surprises** | Autouse fixtures in parent conftest.py run across entire subtree | Constrain scope; convert to non-autouse where possible |
| 5 | **monkeypatch/mock leakage** | `unittest.mock.patch` as context manager only reverts on exit; exceptions leave stubs behind | Prefer pytest's `monkeypatch` fixture (auto-reverts) |
| 6 | **Async event-loop scope mismatches** | Session-scoped fixtures bind to one loop; tests run on different loops | Match fixture scope to event-loop scope |
| 7 | **Import-time side effects** | Module reads DB connection, opens file, fires thread at import time | Push side effects into fixtures |
| 8 | **pytest-rerunfailures hiding bugs** | `--reruns 3` retries failing tests; real bugs masked by race wins | Do not retry at pytest level; quarantine instead |

### Recommended Test Infrastructure

- **Property-based testing**: Hypothesis with `RuleBasedStateMachine` for stateful systems (circuit breakers, memory stores)
- **Chaos testing**: `ordeal` library for fault injection and property assertions
- **CI profiles**: `dev` (fast), `ci` (balanced), `nightly` (thorough) via `@settings` decorator
- **Database**: Cache `.hypothesis/examples/` as CI artifact

---

## §3 MCP Streamable HTTP — 2026-07-28 Spec Lock (TODAY)

### Breaking Changes from Previous Spec

1. **GET stream endpoint removed** — no more `GET /sse` for server-initiated messages
2. **Protocol-level sessions removed** — stateless core by default
3. **New required headers**: `Mcp-Method`, `Mcp-Name` (SEP-2243) for load balancer routing
4. **Multi Round-Trip Requests** (SEP-2322): `InputRequiredResult` replaces long-lived SSE streams
5. **Cache hints**: `ttlMs`, `cacheScope` on list/read responses (SEP-2549)
6. **OAuth 2.1**: PKCE-S256 mandatory for ALL clients, including confidential

### Backward Compatibility

- Servers MUST host both old SSE endpoints AND new MCP endpoint during transition
- Clients attempt POST to new endpoint first; fallback to GET /sse on 4xx
- `MCP-Protocol-Version: 2026-07-28` header required on every request

### Action for C-4b

Our MCP Hub currently uses SSE transport. Migration plan:
1. Add Streamable HTTP endpoint alongside existing SSE
2. Implement `Mcp-Method`/`Mcp-Name` header routing
3. Add OAuth 2.1 PKCE-S256 for remote access
4. Keep SSE for backward compatibility during transition

---

## §4 Soul Distillation Pipeline — Compression Spectrum (2026)

### The Experience Compression Spectrum (Level 0-3)

| Level | Name | Compression | Format | Example |
|-------|------|-------------|--------|---------|
| L0 | Raw Trace | 1:1 | Full conversation | Session transcript |
| L1 | Episodic Memory | 5-20x | Time-scoped summary | "2026-07-22: Implemented C-1' SoulStore..." |
| L2 | Procedural Skill | 50-500x | Reusable procedure | "How to write atomic files: tempfile→fsync→replace" |
| L3 | Declarative Rule | 1000x+ | Universal principle | "Factory-Before-Third: extract after 2nd impl, not 3rd" |

### Current State in Omega Engine

- **L1 (proposed_lessons.yaml)**: ✅ Working — manual distillation per session
- **L2 (soul.yaml lessons_learned)**: ✅ Working — written by soul_updater
- **L3 (soul.yaml axioms)**: ❌ Missing — no automated axiom extraction
- **Pipeline automation**: ❌ Missing — all distillation is manual

### Recommended Pipeline (from soul-protocol.py, neon-soul, KMMS)

```
Session End
    ↓
L1 Extraction (narrative) → proposed_lessons.yaml
    ↓
L2 Distillation (insight) → soul.yaml lessons_learned
    ↓
L3 Convergence (universal) → soul.yaml axioms
    ↓
Cross-Pollination → other entities' soul files
```

**Key pattern from neon-soul**: Axioms require N≥3 supporting principles from ≥2 distinct provenance types. This prevents self-reinforcing beliefs.

**Key pattern from KMMS**: 5-tier memory (L0 Redis → L1 Abstract → L2 Core → L3 Examples → L4 Raw) with SUPERSEDES chains preserving history.

---

## §5 E-0 Identity Fluidity — MENTOR Architecture (ACL 2026)

### The Identity Drift Problem

When a single agent serves multiple personas in one session, identity drift occurs:
- Model conflates user-specific states
- Leaks information across roles
- Responses remain fluent but violate role boundaries

**Confirmed in**: ACL 2026 findings, BEAM-SWITCH benchmark.

### MENTOR Solution (Dual-Chain Memory)

```
┌─────────────────────────────────────────┐
│  Global Chain (G)                       │
│  Long-term event logging across session │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼──┐  ┌───▼──┐  ┌───▼──┐
│Role A│  │Role B│  │Role C│
│Chain │  │Chain │  │Chain │
└───┬──┘  └───┬──┘  └───┬──┘
    │          │          │
    └──────────┼──────────┘
               │
┌──────────────▼──────────────────────────┐
│  Knowledge Graph (K)                    │
│  Filters role-admissible information    │
└─────────────────────────────────────────┘
```

### Personality Variant Overlay Pattern (Agent Patterns Catalog 2026)

- Base identity (charter, name, tone) stays constant
- Finite labelled variants (teacher, operator, archivist) overlay on top
- Variants are reversible and visible
- Memory, tools, charter shared across all variants
- Variants MUST NOT override base charter

### Action for E-0

1. Implement Dual-Chain Memory: Global Chain (session history) + Role Chains (per-entity working memory)
2. Add Knowledge Graph filtering: only role-admissible information reaches generation
3. Implement Variant Overlay: finite set of register modes per entity
4. Enforce: variants cannot contradict base soul.yaml

---

## §6 C-3 Privacy / Restic Backup — 3-2-1 Rule

### Recommended Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Local Disk  │────▶│  Restic Repo │────▶│  Backblaze B2│
│  (fast first)│     │  (encrypted) │     │  (off-site)  │
└──────────────┘     └──────────────┘     └──────────────┘
       1                    2                    3
```

### Key Patterns

1. **Client-side encryption**: Restic encrypts before upload; passphrase is the single point of failure
2. **Scoped credentials**: Dedicated S3 IAM user with bucket-only permissions
3. **Object lock**: 30-day governance period prevents `restic forget --prune --keep-last 0`
4. **Passphrase rotation**: `restic key add` / `restic key remove` (NOT routine — full re-backup required)
5. **Verification levels**:
   - Daily: `restic check` (metadata only, seconds)
   - Weekly: `restic check --read-data-subset 5%` (sample blobs, minutes)
   - Monthly: `restic check --read-data` (full, hours)

### Omega Engine Specific

- Backup targets: `data/entities/`, `data/coordination/`, `config/`, `proposed_lessons.yaml`
- Exclude: `.venv/`, `node_modules/`, `__pycache__/`, `*.pyc`
- Schedule: Daily backup, weekly verify, monthly full check
- Passphrase: OS keyring (Omega-Vault) + password manager backup

---

## §7 V-1 VaultCore — Credential Rotation Patterns

### From Omega-Vault Deep Research

1. **AES-256-GCM** for at-rest encryption (already implemented in `src/omega/vault/`)
2. **OS keyring** for master key storage (keyring library)
3. **Credential rotation**: 90-day cycle for API keys, 30-day for OAuth tokens
4. **Multi-account support**: Sticky → hybrid → round-robin at 5+ accounts
5. **90% soft threshold**: Rotate before quota exhaustion

### From resilient-llm-router

- **Composite key state**: `(provider, model, credential_alias)` — not just provider
- **Probe daemon**: Low-traffic apps need active probing to detect recovery
- **Auto-detect rate-limit headers**: Parse `x-ratelimit-*`, `Retry-After`, `RateLimit-*`

---

## §8 Synthesis — Hardening Actions (Priority Order)

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| **P0** | Add 429 classification to HealthMonitor (rate-limit vs quota) | 2h | Prevents quota-loop bug class |
| **P0** | MCP Streamable HTTP endpoint (2026-07-28 spec TODAY) | 4h | Spec compliance |
| **P1** | Property-based tests for circuit breakers (Hypothesis) | 3h | C-11 test infra |
| **P1** | Soul distillation pipeline automation (L1→L2→L3) | 4h | M11 compliance |
| **P1** | Restic backup for soul data | 2h | Data durability |
| **P2** | Identity Fluidity Phase 0 (Dual-Chain Memory) | 6h | E-0 foundation |
| **P2** | Credential rotation schedule (Omega-Vault) | 3h | V-1 hardening |
| **P3** | Chaos testing with `ordeal` | 2h | C-11 advanced |

---

*⬡ OMEGA ⬡ MAAT ⬡ R-SPRINT-HARDENING ⬡ 2026-07-22 ⬡*
