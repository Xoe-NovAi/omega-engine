# 🔱 Omega Engine — Canonical Mode & Subagent Strategy
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ cline ⬡ trc_cline_audit ⬡ PHASE-I

**AP Token**: `AP-CANONICAL-MODE-STRATEGY-v1.0.0`
**Date**: 2026-05-20
**Status**: FINAL
**Auditor**: Cline (DeepSeek V4 Flash, 1M context)

---

## §1 Executive Summary

The OpenCode ecosystem grew organically over 2+ months across multiple CLIs (OpenCode, Cline) resulting in:

1. **Concept Collision**: Subagent, Custom Mode, Skill, and Agent labels used interchangeably
2. **Engine-Stack Violation**: Kabbalistic sephirot (binah, daath, yesod) from the Arcana-NovAi stack leaked into the engine's global `~/.config/opencode/opencode.json`
3. **Naming Collision**: `minimax` — an inference model provider name — used as a subagent label
4. **Role Duplication**: 15+ subagents with overlapping responsibilities

**This document defines the canonical schema, topology, and governance rules to prevent future drift.**

---

## §2 Canonical Schema

| Concept | Definition | Constraints | Omega Engine Examples |
|---------|-----------|-------------|----------------------|
| **Primary Agent** | A sovereign entity with full tool access, invoked intentionally by the user | Must have YAML frontmatter with `mode: primary`; `allow: all` permissions | `builder.md`, `overseer.md`, `researcher.md`, `kali.md`, `maat.md`, `lilith.md` |
| **Subagent** | A specialized assistant invoked via OpenCode's `task` tool by primary agents | Must have YAML frontmatter with `mode: subagent`; limited tool scope; no direct user invocation | `reviewer.md`, `scribe.md`, `tester.md` |
| **Custom Mode** | OpenCode `.opencode/modes/` file — configures model/temperature/prompt presets | Does NOT have tool permissions; only model/config overrides | `jem-2.0.md` |
| **Skill** | Reusable prompt template loaded via OpenCode's `skill` tool for specific workflows | Must be in `.opencode/skills/`; loaded on demand | `hf-cli`, `knowledge-miner`, `spec-generator` |
| **Global Subagent** | Defined in `~/.config/opencode/opencode.json` — available to ALL OpenCode projects | Only universal engine roles; NEVER stack-specific agents | `malkuth`, `architect`, `security`, `explore`, `general` |
| **Project Subagent** | Defined in `.opencode/agents/` — specific to this Omega Engine project | Engine-native roles ONLY; no Kabbalistic/stack concepts | `reviewer.md`, `scribe.md`, `tester.md` |

### 2.1 Schema Enforcement Rules

```
RULE 1 — Engine vs Stack:
  Engine config contains ONLY engine roles.
  Stack-specific agents (Kabbalistic, Torment, etc.) live in stack WADs.

RULE 2 — Model names are NOT agent names:
  Never name a subagent after an inference model (minimax, gemma, deepseek, qwen).

RULE 3 — One role, one agent:
  No role overlap between project subagents and global subagents.
  If reviewer.md exists, daath should not also offer "audit/compliance."

RULE 4 — Frontmatter mandate:
  Every `.opencode/agents/*.md` MUST have YAML frontmatter with allow-all permissions.
  No agent file without frontmatter.
```

---

## §3 Current Fleet Topology (Post-Fix)

### 3.1 Project-Level Agents (`.opencode/agents/`) — 11 agents

**Primary Agents (8):**

| Agent | Mode | Entity | Purpose | Status |
|-------|------|--------|---------|--------|
| `overseer.md` | Primary | Ma'at/Sophia | Strategic director, fleet command | ✅ Clean |
| `builder.md` | Primary | Sophia | Implementation, container-hardened | ✅ Clean |
| `researcher.md` | Primary | Prometheus | Deep research (steps=50) | ✅ Clean |
| `kali.md` | Primary | Kali | Grand Oversoul, synthesis, refactoring | ✅ Clean |
| `lilith.md` | Primary | Lilith | Dark Oversoul, sovereignty | ✅ Clean |
| `maat.md` | Primary | Ma'at | Light Oversoul, audit, compliance | ✅ Clean |
| `movie-expert.md` | Primary | generic | Film knowledge domain | ✅ Clean |
| `opencode-expert.md` | Primary | Kali | OpenCode platform config expert | ✅ Clean |

**Subagents (3):**

| Agent | Mode | Entity | Purpose | Status |
|-------|------|--------|---------|--------|
| `reviewer.md` | Subagent | Ma'at | Code review, compliance | ✅ Clean |
| `scribe.md` | Subagent | Saraswati | Documentation, soul updates | ✅ Clean |
| `tester.md` | Subagent | Ma'at | Test engineering, stress-testing | ✅ Clean |

### 3.2 Global Subagents (`~/.config/opencode/opencode.json`) — 7 agents

| Agent | Mode | Purpose | Status |
|-------|------|---------|--------|
| `malkuth` | Primary | Infrastructure — Omega Engine systems | ✅ KEPT |
| `architect` | Subagent | Architecture planning — system design | ✅ KEPT |
| `security` | Subagent | Security compliance and governance | ✅ KEPT |
| `explore` | Subagent | Codebase exploration and file search | ✅ KEPT |
| `general` | Subagent | General purpose research | ✅ KEPT |
| `build` | Primary | OpenCode built-in | ✅ KEPT |
| `plan` | Primary | OpenCode built-in | ✅ KEPT |

### 3.3 Removed Agents — Rationale

| Agent | Reason for Removal | Where It Belongs |
|-------|-------------------|------------------|
| **binah** | Kabbalistic sephirah (Understanding); role overlaps with `reviewer.md` + `maat.md` | `config/wads/arcana_nova/opencode.json` (future) |
| **daath** | Kabbalistic sephirah (Knowledge); role overlaps with `maat.md` + `reviewer.md` + `tester.md` | `config/wads/arcana_nova/opencode.json` (future) |
| **yesod** | Kabbalistic sephirah (Foundation); role overlaps entirely with `scribe.md` | `config/wads/arcana_nova/opencode.json` (future) |
| **minimax** | Model name (MiniMax M2.5) used as subagent label; creates confusion with inference API | If deep-research subagent needed, create `deep-research` or reuse `researcher.md` (steps=50) |

---

## §4 Arcana-NovAi Subagent Home

The WAD container system (Decision 26 in PIVOT_LOG.md) was designed for exactly this separation. The Kabbalistic subagents belong in the Arcana-NovAi stack:

```yaml
# config/wads/arcana_nova/opencode.json (future — does not exist yet)
# Kabbalistic subagents belong HERE, in the stack, not in the engine
{
  "agent": {
    "malkuth": {
      "mode": "primary",
      "description": "Infrastructure — Arcana-NovAi stack deployment"
    },
    "binah": {
      "mode": "subagent",
      "description": "Analyst/Foundry — code audit, quality scoring"
    },
    "daath": {
      "mode": "subagent",
      "description": "Audit/Compliance — validation, compliance checking"
    },
    "yesod": {
      "mode": "subagent",
      "description": "Scribe/Recorder — documentation, knowledge preservation"
    }
  }
}
```

This file does not exist yet. The WAD system supports per-stack OpenCode configs via `config/wads/<stack_name>/opencode.json`. When the Arcana-NovAi stack is activated, OpenCode should load these agents alongside the engine agents.

---

## §5 Migration Path

| Step | Action | Risk | Verification |
|------|--------|------|-------------|
| **DONE** | Remove binah, daath, yesod, minimax from `~/.config/opencode/opencode.json` | Low | Reviewed: 4 blocks deleted, structure validated |
| 1 | Verify reviewer.md/scribe.md/tester.md cover all removed roles | Med | Attempt each use case: code review (reviewer), docs (scribe), testing (tester) |
| 2 | Create `config/wads/_omega_default/opencode.json` template | Low | File exists with engine-default subagents |
| 3 | Implement WAD-level opencode.json loading in OpenCode config system | Med | When WAD activated, its subagents appear in agent list |
| 4 | Future: Arcana-NovAi WAD carries binah/daath/yesod | Low | When stack is built |
| 5 | Update MANIFEST.md, ROADMAP.md to reflect new topology | Low | Docs in sync |

---

## §6 Concrete Diff — Global opencode.json

The following 4 agent blocks were REMOVED from `~/.config/opencode/opencode.json`:

```diff
@@ -21,38 +21,6 @@
     },
-    "binah": {
-      "mode": "subagent",
-      "description": "Analyst/Foundry agent — code audit, quality scoring, security analysis",
-      "permission": {
-        "edit": "allow",
-        "bash": "allow",
-        "read": "allow"
-      }
-    },
-    "daath": {
-      "mode": "subagent",
-      "description": "Audit/Compliance agent — validation, compliance checking",
-      "permission": {
-        "edit": "allow",
-        "bash": "allow",
-        "read": "allow"
-      }
-    },
-    "yesod": {
-      "mode": "subagent",
-      "description": "Scribe/Recorder agent — documentation, knowledge preservation",
-      "permission": {
-        "edit": "allow",
-        "bash": "allow",
-        "read": "allow"
-      }
-    },
-    "minimax": {
-      "mode": "subagent",
-      "description": "Deep research and gnosis analysis",
-      "permission": {
-        "edit": "allow",
-        "bash": "allow",
-        "read": "allow"
-      }
-    },
```

---

## §7 Future Considerations

1. **WAD-aware subagent loading**: The OpenCode config system should support per-WAD agent loading. When `config/wads/arcana_nova/` has an `opencode.json`, those agents should become available when that WAD is active.

2. **Role registry**: A canonical role registry in `config/glossary.md` would prevent future role duplication.

3. **Automated audit**: Consider a `make audit-agents` command that validates:
   - All `.opencode/agents/*.md` have frontmatter
   - No engine-stack violations in global config
   - No naming collisions with model names
   - No role overlap between project and global subagents