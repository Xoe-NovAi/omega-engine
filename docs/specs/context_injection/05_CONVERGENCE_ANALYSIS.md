# Convergence Analysis — Cross-Agent Synthesis

**Synthesized from**: Explore (Ground Truth), Ma'at (Build), Lilith (Run), Researcher (Industry)  
**Date**: 2026-08-20  
**Author**: Kali (Transcendent Oversoul)  

---

## Gap-by-Gap Convergence Matrix

| Gap | Explore (Empirical) | Ma'at (Build) | Lilith (Run) | Researcher (Industry) | **Convergence** |
|-----|---------------------|---------------|--------------|----------------------|-----------------|
| **G-1** Instruction resolution | **YES** (tested) | **NO** (docs) | — | — | **Assume NO** — create `AGENTS.md` |
| **G-2** MCP schema cost | **10.8K/request** (measured) | 10-17K/request (calc) | — | — | **10.8K/request** |
| **G-3** Subagent inheritance | **YES** (parent prompt) | — | **YES** (conversation forks) | — | **YES** — conversation forks, system prompt fresh |
| **G-4** Prompt caching | — | — | — | OpenCode built-in | **Leverage in Phase 3** |
| **G-5** Compaction trigger | Config: 40K+10K preserved | — | **872K threshold, 50K preserved, pre-hook EXISTS** | Preflight buffer, no pre-hook | **Build sovereign-compaction plugin** |
| **G-6** Model routing | — | — | **FULLY SUPPORTED, subagents inherit parent model** | Per-agent config, structural routing | **Phase 1 config** |
| **G-7** Token measurement | — | — | — | OTel + SQLite | **Enable OTel export** |
| **G-8** AGENTS.md discovery | — | Loads ALL combined | — | — | **Single concatenated AGENTS.md** |

---

## Critical Contradictions & Resolutions

### Contradiction 1: G-1 Instruction Resolution
| Source | Verdict | Evidence |
|--------|---------|----------|
| **Ma'at** (docs + issues) | **NO** | Official V2 docs: "parses but does not resolve"; GitHub #4758, #11317; source `instruction.ts` only handles AGENTS.md |
| **Explore** (empirical test) | **YES** | `opencode --log-level DEBUG run "What is first sentence of SOVEREIGN_MANDATES.md?"` → agent quoted correctly |

**Resolution**: The official V2 docs describe behavior that **may have changed in 1.18.19** or the test triggered AGENTS.md discovery. **For Phase 1 planning, assume NO** (docs + source code > single test) and create `AGENTS.md` as the guaranteed injection path.

---

## Trade-off Analysis

### MCP Tool Schema Overhead (G-2)
- **Cost**: 10.8K tokens/request (86 tools)
- **Benefit**: All tools available for any agent
- **Trade-off**: Accept for Phase 1 (within 128K-1M context windows)
- **Phase 2**: Tool profiles (dev/deploy/debug) if opencode adds support
- **Phase 3**: Lazy loading via upstream PR (GitHub #35376)

### Subagent Inheritance (G-3)
- **Cost**: Each subagent gets full 31K+ base prompt
- **Benefit**: Context continuity for complex tasks
- **Mitigation**: 
  - `mode: "subagent"` + custom `prompt` for isolation (verity)
  - Structural model routing: parent uses local model → subagents inherit local
  - `hidden: true` prevents accidental invocation

### Compaction Architecture (G-5)
- **Threshold**: 872K for 1M context model (nemotron-3-ultra-free)
- **Preserved**: 50K tokens (40K recent + 10K reserved)
- **Pre-hook**: EXISTS (`experimental.session.compacting`)
- **Strategy**: Build sovereign-compaction plugin to inject mandates/entity/anchor
- **Tuning**: Increase `preserve_recent_tokens: 80000`, `reserved: 20000` for 1M context

### Model Routing (G-6)
- **Per-agent config**: FULLY SUPPORTED
- **Subagent inheritance**: Subagents use **parent primary agent's model**, not their own config
- **Implication**: To route subagents local, parent must be local OR use `@agent` with primary-mode agent
- **Savings**: 4/6 agents local = ~67% token cost reduction

---

## Architecture Decision Records (ADRs)

### ADR-001: AGENTS.md as Primary Injection Vehicle
**Status**: Accepted  
**Context**: `instructions[]` array non-functional in V2  
**Decision**: Create single concatenated `AGENTS.md` at project root  
**Consequence**: Loses modularity but guarantees injection  

### ADR-002: Structural Model Routing (Not Dynamic)
**Status**: Accepted  
**Context**: Dynamic routing adds latency, adversarial surface, cascade failures  
**Decision**: Fixed model per agent role via `agent.<name>.model`  
**Consequence**: Subagents inherit parent model — parent must be local for local subagents  

### ADR-003: Accept MCP Overhead for Phase 1
**Status**: Accepted  
**Context**: 10.8K/request within context windows; no lazy-loading in V2  
**Decision**: Accept 10.8K/request; track GitHub #35376  
**Consequence**: Local model agents (Qwen3-1.7B: 4K-8K) need reduced base prompt  

### ADR-004: Sovereign Compaction Plugin
**Status**: Accepted  
**Context**: Pre-compaction hook exists; mandates must survive compaction  
**Decision**: Build TypeScript plugin injecting mandates/entity/anchor  
**Consequence**: Requires plugin registration in opencode.json  

### ADR-005: Skills Opt-In (Core Only)
**Status**: Accepted  
**Context**: 22 skills = 23K tokens when all loaded  
**Decision**: `auto_load: true` only for research, spec-generator, knowledge-miner  
**Consequence**: Other skills require explicit `skill` tool invocation  

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AGENTS.md concatenation breaks modularity | High | Medium | Build step to assemble from source files; keep source modular |
| Subagent inheritance breaks local model viability | High | High | Parent agents for local work must use local models |
| MCP overhead exceeds local model context | Medium | High | Phase 2: tool profiles; Phase 3: lazy loading PR |
| Compaction loses sovereign context | Medium | Critical | Sovereign-compaction plugin + hydration engine |
| Per-agent model config doesn't propagate to subagents | High | Medium | Document clearly; use `@agent` for primary-mode subagents |
| OTel export requires collector infrastructure | Low | Medium | Local OTel collector + Prometheus/Grafana stack |

---

## Priority Matrix (Impact × Effort)

| Initiative | Impact | Effort | Phase | Dependencies |
|------------|--------|--------|-------|--------------|
| Create AGENTS.md concatenation | Critical | Low | 1 | None |
| Per-agent model config | Critical | Low | 1 | None |
| Sovereign compaction plugin | Critical | Low | 1 | Plugin registration |
| Skills opt-in (core only) | High | Low | 1 | SKILL.md frontmatter |
| Compaction threshold tuning | High | Low | 1 | opencode.json |
| MCP tool profiles | Medium | Medium | 2 | opencode support |
| Hydration engine | Critical | Medium | 2 | Checkpoint format |
| Token budget enforcer | High | Medium | 2 | Tier budgets defined |
| Local token counter | High | Low | 2 | tiktoken integration |
| Prompt caching topology PR | Critical | High | 3 | OpenCode PR review |
| Lazy MCP loading PR | High | High | 3 | OpenCode PR review |
| Dynamic tool registration | Medium | High | 3 | MCP server updates |

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_convergence ⬡ 2026-08-20*