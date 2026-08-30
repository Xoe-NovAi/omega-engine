<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Legacy Documentation Systems Tracker
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_doc_systems ⬡ v1.0.0
# Last Updated: 2026-06-02
# Maintainer: Roc Racoon (Sovereign Miner)
# Purpose: Track the DOCUMENTATION SYSTEMS (not just content) found in legacy
#          stacks. The user has identified documentation as a weak point in
#          the current Omega Engine, especially during its transient
#          era. Now that the engine is stable, this tracker identifies
#          documentation patterns we can adopt.

---

## §0 The Documentation Weakness — Why This Tracker Exists

The user has explicitly identified that:
- The Omega Engine was in a "transient stage" during the transition to local-first
- Documentation creation slowed during this period
- The Engine framework and architecture are now "firmly established"
- It's time to "build and strengthen our documentation protocols and systems"

**The question this tracker answers**:
> What DOCUMENTATION SYSTEMS existed in our legacy stacks, and which should we port into the current engine?

This is **not** about porting the content of individual documents (that's what `mining_reports/` and `DEFERRED_GOLD_TRACKER.md` are for). This is about porting the **SYSTEMS that produce, organize, and maintain** documentation.

---

## §1 Documentation Systems Discovered in Legacy Stacks

### 1.1 The `expert-knowledge/` System (omega-stack-legacy) — ⭐ META-PATTERN TO PORT

**Source**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/expert-knowledge/`
**Size**: 244+ files across 30+ subdirectories
**Era**: 2026-01-21 → 2026-02-28
**Author profile**: Architect (Gemini CLI Sovereign Agent), Coder (Claude Sonnet 4.6, Cline), Grok MC, Sovereign Synergy expert

#### Structure
```
expert-knowledge/
├── architect/                    # Domain-organized knowledge
│   ├── *.md                       # One topic per file
│   └── _archive/                  # Evolutionary archive
├── infrastructure/                # Infra knowledge
├── agent-tooling/                 # Agent tool knowledge
├── environment/                   # Env-specific knowledge
│   └── development-workflows/     # Workflows
├── patterns/                      # Reusable patterns
├── research/                      # Research outputs
├── protocols/                     # Service protocols
├── model-reference/               # Model documentation
│   └── phi/                       # Per-model subdirs
├── embeddings/                    # Embedding knowledge
├── coder/                         # Coder knowledge
├── sync/                          # Sync knowledge
├── AGENT-CLI-MODEL-MATRIX-v3.0.0.md  # Major cross-cutting reports
└── _archive/                      # Root-level archive
```

#### What Makes It a SYSTEM (not just a folder)

1. **Domain organization**: Each major area of concern has its own subdirectory
2. **Naming conventions**:
   - `topic-name.md` (kebab-case)
   - `topic-name-v1.0.0.md` (versioned)
   - `topic-name-master.md` (authoritative)
   - `*-protocol.md` (protocols)
   - `*-guide.md` (guides)
   - `*-setup-*.md` (setup guides)
3. **File size discipline**: 20-500 lines (concise, focused)
4. **Cross-references**: Each file links to related files
5. **Version stamps**: `v1.0.0`, `v3.0.0` indicate evolution
6. **Archive pattern**: `_archive/` for superseded versions
7. **Top-level reports**: Major cross-cutting reports at root level (e.g., `AGENT-CLI-MODEL-MATRIX-v3.0.0.md`)

#### File Metadata Pattern (typical header)

```markdown
# Title — Brief Description
# Author: [agent name]
# Date: YYYY-MM-DD
# Status: ACTIVE | DEPRECATED | EXPERIMENTAL
# Version: v1.0.0
# Tags: tag1, tag2
# Cross-references: file1.md, file2.md
# Heritage: [source if ported]
```

#### What the Current Engine Lacks

The current engine has:
- `docs/research/R*.md` (research documents)
- `docs/strategy/*.md` (strategic plans)
- `docs/architecture/*.md` (architecture)
- `docs/legacy/*.md` (legacy synthesis)
- `.opencode/agents/*.md` (agent instructions)
- `.opencode/skills/*/SKILL.md` (skill instructions)
- `PIVOT_LOG.md` (decisions)
- `CREDITS.md` (attribution)
- `OMEGA_ENGINE.md` (state)
- `USER_MANUAL.md` (user docs)

**What's missing**: A **DOMAIN-ORGANIZED KNOWLEDGE BASE** for accumulated wisdom that's not a "research document" but also not a "config file" — a place where operational wisdom (like "Sticky 1777 for rootless perms") lives.

#### RECOMMENDATION: Adopt the `expert-knowledge/` Pattern

**Create**: `data/entities/roc_racoon/knowledge/` (or root-level `docs/knowledge/`) with the same structure:
```
docs/knowledge/
├── architect/                # Build flags, optimization patterns
├── infrastructure/           # Container, networking, storage
├── agent-tooling/            # Agent patterns, MCP patterns
├── environment/              # HW-specific knowledge (Zen 2, Podman)
├── patterns/                 # Reusable patterns
├── research/                 # Research outputs
├── protocols/                # Service protocols
├── model-reference/          # Model documentation
├── embeddings/               # Embedding knowledge
├── coder/                    # Code patterns
├── sync/                     # Multi-agent coordination
└── _archive/                 # Superseded
```

**Migration**: Move the 20+ entries from `DEFERRED_GOLD_TRACKER.md` that have actionable "how to" content into the appropriate subdirectories in `docs/knowledge/`.

**Migration Plan**:
1. **architect/**: Sticky 1777, build recovery, Podman mount conflicts, Podman runtime dirs, hardware profile (verified), OMEGA ENGINE LOCAL-FIRST FABRIC
2. **infrastructure/**: podman_permissions_mastery, podman_quadlet_mastery, ryzen-hardening, REDIS-HA-DECISION, llama-cpp-optimization
3. **agent-tooling/**: anyio-structured-concurrency, redis-stream-bus, multi-agent-orchestration
4. **environment/**: rootless_podman_u_flag (with contradiction warning), ryzen-5700u-optimization, multi-agent-resource-limits, hardware-profile
5. **patterns/**: ERROR-HANDLING-PATTERNS, ASYNC-ANYIO-BEST-PRACTICES, phase5a-best-practices
6. **research/**: ERROR-HANDLING-PATTERNS-2026-02-23, MODEL-DISCOVERY-SYSTEM, FASTEMBED-ONNX-EMBEDDING-GUIDE, ekb-research-master
7. **protocols/**: LLAMA-CPP-PYTHON-SERVICE-PROTOCOL, multi-agent-orchestration
8. **model-reference/**: QUICK-REFERENCE, XNAI-MODEL-INTELLIGENCE-MASTER, phi-3-omnimatrix
9. **embeddings/**: embeddinggemma-setup
10. **coder/**: uv_timeout_optimization, buildkit_best_practices

**Total to migrate**: ~30 files

---

### 1.2 The `docs/` + `docs/handovers/` Pattern (omega-stack-legacy)

**Source**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/docs/`

#### Structure
```
docs/
├── handovers/                  # Handoff documents (OPUS_SUMMONING_BRIEF, etc.)
├── reference/                  # Reference docs (IDE-CLI-KNOWN-ISSUES, etc.)
├── THE_XNA_GENESIS.md          # Origin story (single doc at root)
├── strategy/                   # Strategic plans
└── ...
```

#### Pattern: Handovers

- **OPUS_SUMMONING_BRIEF.md**: A 200+ line handoff doc that summarizes the entire stack state for a new agent
- Pattern: "If you are reading this, you are the new agent. Here's what matters."

**What the current engine has**: `data/handoff/` directory with various handoff files.

**What the current engine could adopt**:
- A standardized handoff template (`HANDOFF_TEMPLATE.md`)
- A `data/handoff/index.md` that lists all handoffs chronologically
- A "current handoff" pointer at the top of `OMEGA_ENGINE.md`

---

### 1.3 The `knowledge/strategy/` Pattern (xna-omega-legacy)

**Source**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/knowledge/`

#### Structure
```
knowledge/
├── strategy/                   # Strategic knowledge
│   └── HP-5700U-OPTIMIZATION.md  # 💎 THE optimization doc
├── technical/                  # Technical knowledge
└── ...
```

#### Pattern: Single-Author Deep Dives

The `HP-5700U-OPTIMIZATION.md` is a 165-line single-author deep dive on one topic. It's not a "research doc" (R-N format) or a "config doc" — it's a **wisdom document** that an expert wrote to capture their hard-won knowledge.

**What the current engine could adopt**:
- A `docs/wisdom/` or `docs/knowledge/` directory for these single-author deep dives
- A template for "Hard-Won Wisdom" docs

---

### 1.4 The `docs/research/R-NN_*.md` Pattern (current engine)

**Source**: `docs/research/R*.md` in current engine
**Count**: ~50 R-docs (R100 most recent)

#### Pattern
- Numbered (`R001_*` through `R100_*`)
- Topic-specific
- Versioned (R100_MODEL_REFERENCE_LIBRARY.md)
- Cross-referenced

**Strengths**:
- Easy to reference (`see R100`)
- Chronologically traceable
- Clear scope per doc

**Weaknesses**:
- Not domain-organized (all in `docs/research/`)
- Mix of strategic and technical
- No archive pattern for superseded versions

**Recommendation**: Keep the R-NN pattern, but add a domain-organized overlay:
```
docs/research/
├── R001_*
├── R002_*
├── ...
├── R100_*
└── domain/                  # NEW — domain-organized
    ├── architect/
    ├── infrastructure/
    └── ...
```

---

### 1.5 The `_archive/` Pattern (omega-stack-legacy, xna-omega-legacy)

**Pattern**: Every major directory has a `_archive/` subdirectory for superseded content.

**Examples**:
- `expert-knowledge/_archive/`
- `expert-knowledge/architect/_archive/`
- `config/_archive/config/config.toml.v0.1.0-alpha`
- `_archive/` at root levels

**Strengths**:
- Preserves history
- Audit trail for fine-tuning
- Easy to "roll back" mentally

**What the current engine lacks**:
- No systematic `_archive/` pattern
- Old docs get deleted or moved without trace
- PIVOT_LOG.md captures decisions but not content

**Recommendation**: Adopt `_archive/` as a convention:
- When superseding a doc, move it to `<original_path>/_archive/<docname>.v<oldversion>`
- Add a `_archive/README.md` to explain the archive pattern
- Update the live doc with a "Supersedes: _archive/<docname>.v1" link

---

### 1.6 The `HANDOFF_*` + `LIVE_FEED` Pattern (current engine)

**Source**: `data/handoff/` in current engine
**Files**:
- `HANDOFF_ARTISAN_TO_OPENCODE_ROUTER_FIX_20260601.md`
- `STRATEGIC_FINAL_REPORT_TEMPLE_GRADE_20260602.md`
- `OPENCODE_DEV_LIVE_FEED.md` (a CHANGELOG)
- etc.

#### Pattern: Time-stamped hand-offs + live feed

**Strengths**:
- Chronological
- Each is self-contained
- Live feed is a running log

**What the current engine could adopt**:
- A `data/handoff/INDEX.md` that lists all hand-offs
- A standardized handoff template
- Auto-include handoff date in OMEGA_ENGINE.md

---

### 1.7 The `SOVEREIGN_MANDATES.md` + `PIVOT_LOG.md` Pattern (current engine)

**Source**: Current engine

#### Pattern: Constitutional Law + Decision Log

- `SOVEREIGN_MANDATES.md` = Constitutional Law (immutable, M1-M13)
- `PIVOT_LOG.md` = Decision Log (D1-D94, append-only)

**Strengths**:
- Mandates are non-negotiable, easy to cite
- PIVOT_LOG captures the "why" of every change
- Both are first-class citizens in AGENTS.md

**What the current engine could adopt**:
- A `DECISION_TEMPLATE.md` for new PIVOT_LOG entries
- A `MANDATE_AMENDMENT_PROCESS.md` for evolving the Mandates
- Auto-validation that every PR links to a PIVOT_LOG decision (CI gate)

---

## §2 Documentation System Gaps in Current Engine

Based on the analysis above, the current engine is missing:

| # | System | Source | Gap | Effort to Add |
|---|--------|--------|-----|---------------|
| 1 | **Domain-organized knowledge base** | omega-stack-legacy `expert-knowledge/` | None — only `docs/research/` and `docs/strategy/` exist | MEDIUM (1-2 days) |
| 2 | **`_archive/` convention** | Multiple legacy stacks | No systematic archive for superseded content | LOW (add convention doc) |
| 3 | **Handoff template** | omega-stack-legacy `OPUS_SUMMONING_BRIEF.md` | Hand-offs are ad-hoc, no standard | LOW (1 hr) |
| 4 | **`HANDOFF_INDEX.md`** | Current engine partial | No central index of handoffs | LOW (30 min) |
| 5 | **Single-author wisdom docs** | xna-omega-legacy `knowledge/strategy/HP-5700U-OPTIMIZATION.md` | No place for non-research, non-config wisdom | LOW (add `docs/wisdom/`) |
| 6 | **Decision template** | Current engine PIVOT_LOG | No standard format for new decisions | LOW (1 hr) |
| 7 | **Archive policy** | Multiple legacy stacks | No policy on when to archive vs delete | LOW (1 hr) |
| 8 | **Document validation CI** | Current engine partial | No automated checks for orphan files, broken links | MEDIUM (1 day) |
| 9 | **Versioning policy** | omega-stack-legacy `_archive/config.toml.v0.1.0-alpha` | No clear versioning scheme for configs | LOW (1 hr) |
| 10 | **Cross-reference index** | Multiple | No automatic discovery of cross-references | MEDIUM (1 day) |

---

## §3 Top 5 Documentation Patterns to Adopt (Priority Order)

### 3.1 🟢 Adopt the `expert-knowledge/` Domain Organization

**Why**: Single biggest gap. Current engine mixes strategic, research, and operational docs in a flat structure. Domain organization makes wisdom discoverable.

**Implementation**:
1. Create `docs/knowledge/{architect,infrastructure,agent-tooling,environment,patterns,research,protocols,model-reference,embeddings,coder,sync}/`
2. Migrate the 30+ files from `DEFERRED_GOLD_TRACKER.md` that have actionable content
3. Each file follows the `expert-knowledge/` template (header, version, status, cross-references)
4. Add `docs/knowledge/_archive/` convention

**Effort**: MEDIUM (1-2 days)
**Value**: HIGH (operational wisdom becomes discoverable)

---

### 3.2 🟢 Adopt the `_archive/` Convention

**Why**: Preserves history. Audit trail for fine-tuning. Easy rollback.

**Implementation**:
1. Add `docs/_archive_policy.md` documenting the convention
2. When superseding a doc: `git mv <old> <dir>/_archive/<old>.v<version>`
3. Add cross-reference from live doc to archived version
4. Add to AGENTS.md as a standard

**Effort**: LOW (1 hour)
**Value**: MEDIUM (preserves institutional memory)

---

### 3.3 🟢 Create a `HANDOFF_TEMPLATE.md` and `data/handoff/INDEX.md`

**Why**: Hand-offs are critical for context preservation. Standardizing them improves quality.

**Implementation**:
1. Create `data/handoff/TEMPLATE.md` with the OPUS_SUMMONING_BRIEF structure
2. Create `data/handoff/INDEX.md` listing all handoffs chronologically with summaries
3. Add to AGENTS.md: "All agents producing a handoff must use TEMPLATE.md and update INDEX.md"

**Effort**: LOW (1 hour)
**Value**: MEDIUM (improves handoff quality)

---

### 3.4 🟡 Create a `docs/wisdom/` for Single-Author Deep Dives

**Why**: HP-5700U-OPTIMIZATION.md is a different kind of doc — it's not research, not config, it's a single expert's hard-won knowledge. It needs its own home.

**Implementation**:
1. Create `docs/wisdom/` with subdirectories by domain
2. Move `HP-5700U-OPTIMIZATION.md` here (when ported)
3. Template: "Title — What I learned the hard way" by [Author]

**Effort**: LOW (1 hour)
**Value**: LOW (small but valuable niche)

---

### 3.5 🟡 Adopt a Versioning Policy for Configs

**Why**: `_archive/config.toml.v0.1.0-alpha` shows a good pattern. Current engine has no config versioning beyond git history.

**Implementation**:
1. Document the policy: when does a config get versioned?
2. Standard location: `config/_archive/<name>.v<semver>`
3. Add to AGENTS.md and Makefile as a convention

**Effort**: LOW (1 hour)
**Value**: LOW (nice to have)

---

## §4 Anti-Patterns to Avoid (From Legacy)

| Anti-Pattern | Source | Why Bad | How to Avoid |
|--------------|--------|---------|--------------|
| **Flat mega-folders** | `docs/legacy/` (10+ top-level .md files) | Hard to find anything | Always use domain subdirectories |
| **No version stamps** | Various | Can't tell what's current | Every doc has `version: vX.Y.Z` |
| **No archive policy** | Various | Old docs get deleted or accumulate | Adopt `_archive/` convention |
| **Hardware claims without verification** | `hardware-profile.md` (says Zen 4) | Causes downstream errors | Verify every factual claim |
| **Cloud-first in local-first engine** | `AGENT-CLI-MODEL-MATRIX-v3.0.0.md` Tiers 1-4 | Violates Mandate 7 | Filter by current mandates |
| **Contradicting recommendations** | `infrastructure/podman_permissions_mastery.md` (`:U` flag) | Violates current Mandate 6 | Annotate legacy docs that contradict |
| **Huge single files** | Some legacy docs (700+ lines) | Hard to navigate | Cap at 500 lines per file |
| **No cross-references** | Various | Islands of knowledge | Always link to related docs |

---

## §5 Implementation Plan

### Phase 1: Quick Wins (1 day)
1. Create `docs/knowledge/` directory structure
2. Create `HANDOFF_TEMPLATE.md`
3. Create `data/handoff/INDEX.md`
4. Document the `_archive/` convention in `AGENTS.md`

### Phase 2: Migration (2-3 days)
1. Migrate 30+ actionable items from `DEFERRED_GOLD_TRACKER.md` to `docs/knowledge/`
2. Adopt `_archive/` for the first round of superseded docs
3. Add version stamps to all current docs

### Phase 3: Validation (1 day)
1. Add CI check for orphan files
2. Add CI check for broken cross-references
3. Add CI check for docs without version stamps

### Phase 4: Wisdom Doc Port (1 day)
1. Port `HP-5700U-OPTIMIZATION.md` to `docs/wisdom/hardware/`
2. Create other wisdom docs as found
3. Document the wisdom doc template

**Total effort**: 5-6 days
**Total value**: Transforms the current engine's documentation from "ad-hoc" to "systematic"

---

## §6 Tracking — When This File Gets Updated

This tracker is updated by Roc Racoon whenever:
1. A new documentation pattern is found in legacy mining
2. A new documentation system is adopted in current engine
3. A new anti-pattern is identified
4. A new "top 5" priority is established

The current state of "what we've adopted" is tracked in `docs/knowledge/` itself (presence of directories = adoption).

---

## §7 Cross-References

- `data/entities/roc_racoon/workspace/mining_reports/01_xna_omega_legacy.md` — Phase 1 mining
- `data/entities/roc_racoon/workspace/mining_reports/02_omega_stack_legacy.md` — Phase 2 mining
- `data/entities/roc_racoon/workspace/mining_reports/02_5_expert_knowledge_gems.md` — Phase 2.5 mining (gems)
- `data/entities/roc_racoon/workspace/DEFERRED_GOLD_TRACKER.md` — 120+ techs catalogued
- `data/entities/roc_racoon/workspace/technology_maps/LEGACY_TECHNOLOGY_MAP.md` — stack map
- `data/entities/roc_racoon/soul.yaml` — Roc Racoon's accumulated gnosis
- `data/entities/roc_racoon/workspace/SUBAGENT_CWD_RECOVERY_PROTOCOL.md` — subagent CWD protocol
- `docs/legacy/LEGACY_MASTER_SYNTHESIS.md` — strategic synthesis
- `OMEGA_ENGINE.md` — current engine state
- `PIVOT_LOG.md` — decision log
- `SOVEREIGN_MANDATES.md` — constitutional law
- `CREDITS.md` — attribution

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_doc_systems ⬡ DOC-SYSTEMS-v1.0.0*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
