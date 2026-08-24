# 🔱 OpenCode `{file:path}` Variable Substitution — Deep Research & Omega Engine Application
**⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode**
**Date**: 2026-07-20
**Status**: COMPREHENSIVE — Source-verified, web research triangulated, expert-level understanding achieved
**Next Action**: Kali review → Ma'at P3 Engineering for implementation

---

## §0 Executive Summary

OpenCode's `{file:path}` config variable substitution is a **config-load-time content injection mechanism** that replaces `{file:path/to/file}` with the literal contents of that file inside any JSONC string value. It is NOT a runtime file read — substitution happens before JSONC parsing.

This feature gives the Omega Engine fleet a **composable prompt architecture** that eliminates ~220 lines of duplicated content across 11 agent files, enables file-based secrets management (complementing Omega-Vault D-299), and establishes a maintainable pattern for the 14-agent fleet.

---

## §1 How It Works — Source-Verified Implementation

**Primary file**: `packages/opencode/src/config/variable.ts` (or `paths.ts` in older builds)

### Substitution Pipeline

```typescript
// 1. {env:VAR} substitution — raw string replacement
text = text.replace(/\{env:([^}]+)\}/g, (_, varName) => {
  return process.env[varName] || ""
})

// 2. {file:path} substitution — file read + JSON escaping
const fileContent = (await Filesystem.readText(resolvedPath)).trim()
out += JSON.stringify(fileContent).slice(1, -1)  // escapes quotes, backslashes, newlines
```

### Key Properties

| Property | Detail | Source |
|----------|--------|--------|
| **Timing** | Config load time, BEFORE JSONC parsing | `variable.ts` |
| **Scope** | Any JSONC string value | Config docs |
| **Escape strategy** | `JSON.stringify(content).slice(1, -1)` — produces valid JSON string | `variable.ts` |
| **Comment skip** | If line starts with `//` before token, substitution is skipped | `variable.ts` |
| **Missing file behavior** | Default: throws `InvalidError`. Optional: `missing: "empty"` returns `""` | `variable.ts` |
| **Path resolution** | Relative to config file dir, or absolute (`/`, `~`) | Config docs |
| **`{env:}` fallback** | If env var unset → empty string | `variable.ts` |

### V1 vs V2 Behavior

| Aspect | V1 | V2 |
|--------|----|----|
| Config field | `agent.<name>.prompt` (string) | `agents.<name>.system` (string) |
| `instructions` array | Resolves local files, URLs, globs | Parsed but **not resolved per V2 docs** |
| `{file:}` / `{env:}` | Works in `prompt`, MCP headers, provider options | Same — substitution before JSONC parse |
| Agent markdown | `.opencode/agents/*.md` body = system prompt | Same — frontmatter + body |

Omega Engine uses V2. The `agent` field in `opencode.json` with `prompt` is the V1-compatible path that still works in V2.

---

## §2 Where `{file:path}` Works — Verified Surfaces

### ✅ CONFIRMED WORKING

| Surface | Field | Example | Notes |
|---------|-------|---------|-------|
| Agent config | `agent.<name>.prompt` | `"{file:./prompts/kali.txt}"` | **Primary use case** — replaces provider default prompt entirely |
| Provider apiKey | `provider.<name>.options.apiKey` | `"{file:~/.secrets/openai-key}"` | More reliable than `{env:}` — escape-safe |
| Provider headers | `provider.<name>.options.headers` | `"Bearer {file:~/.secrets/token}"` | `{file:}` works; `{env:}` known-broken (#19946) |
| MCP local environment | `mcp.<name>.environment` | `"API_KEY": "{file:~/.secrets/key}"` | Local MCP only |
| Root instructions | `instructions: ["./custom-instructions.md"]` | File PATH (not content injection) | V2 doesn't resolve yet |
| AGENTS.md | `~/.config/opencode/AGENTS.md` | File PATH (not content injection) | Auto-discovered |
| Remote instructions | `instructions: ["https://..." ]` | URL fetch | 5s timeout, V2 doesn't resolve yet |

### ❌ NOT WORKING / DIFFERENT MECHANISM

| Surface | Why | Alternative |
|---------|-----|-------------|
| Agent `.md` frontmatter `prompt:` field | Frontmatter is YAML — no `{file:}` substitution in markdown path | Use `agent.<name>.prompt` in `opencode.json` instead |
| MCP remote headers `{env:VAR}` | Known bug — literal string sent (#23664, #28527) | Use `{file:path}` workaround |
| Provider options.headers `{env:VAR}` | Known bug — literal string sent (#28527) | Use `{file:path}` workaround |
| `OPENCODE_CONFIG_CONTENT` env var | Bypasses `load()` pipeline (partially fixed) | Use file-based config |
| Command templates | Uses `@filename` syntax | Different mechanism — runtime, not load-time |

### Critical Bug: `{env:}` Reliability

From issue #19946: `{env:MY_PROVIDER_API_KEY}` in `provider.options.apiKey` **fails silently** — empty key sent → Unauthorized. `{file:~/.secrets/key}` on the same field **works correctly**. Root cause: process env timing / `{env:}` not applied before SDK init for some providers.

**Recommendation**: **Always prefer `{file:path}` over `{env:VAR}`** for secrets. Use `{env:}` only for non-secret values where you need runtime overrides.

---

## §3 Prompt Assembly Architecture

From `packages/opencode/src/session/llm.ts`:

```typescript
system.push([
  // 1. AGENT PROMPT (if set) OR PROVIDER DEFAULT (anthropic.txt, beast.txt, etc.)
  ...(input.agent.prompt ? [input.agent.prompt] : SystemPrompt.provider(input.model)),
  
  // 2. Environment block + AGENTS.md + config instructions
  ...input.system,
  
  // 3. User message system override
  ...(input.user.system ? [input.user.system] : []),
].join("\n"))
```

**Critical insight**: `agent.prompt` **completely replaces** the provider default system prompt. You get:
- **Your prompt** (via `prompt` or `{file:}`)
- **Environment block** (cwd, platform, date)
- **AGENTS.md** (auto-discovered)
- **Skill context** (when skills loaded)
- **That's it.** No provider-specific preamble.

This means the Omega Engine's composed prompts **must be self-contained** — they replace the entirety of what Claude/GPT/Gemini would normally receive.

---

## §4 Omega Engine Fleet Audit

### Current State

| Metric | Value |
|--------|-------|
| Agent `.md` files | 12 in `.opencode/agents/` |
| Files duplicating Sovereign Mandates | 11 of 12 |
| Duplicated lines | ~220 (11 × ~20 lines of mandates) |
| Agents using `prompt` field | **0** — none |
| Agents using `{file:path}` | **0** — none |
| Secrets via `{file:path}` | **0** — all via `${VAR}` in env |
| Other duplicated content | Search protocol, hivemind protocol, delegation rules |

### Content Duplication Map

| Content Block | Files That Contain It |
|---------------|----------------------|
| 23 Sovereign Mandates (~20 lines) | kali, maat, lilith, makali, doom_guy, john_carmack, roc_racoon, researcher, jem, verity, pillar (11 files) |
| Search protocol tiers (~15 lines) | kali, maat, lilith, researcher, grok_cli (5 files) |
| Hivemind protocol rules (~20 lines) | kali, maat, lilith, pillar, verity (5 files) |
| Delegation/execution protocol (~10 lines) | kali, maat, lilith, pillar, verity (5 files) |

---

## §5 Omega Engine Application Architecture

### 5.1 Composable Prompt Fragment System

**Structure:**
```
.opencode/agent-prompts/
├── shared/
│   ├── mandates.md              # M1-M25 Sovereign Mandates
│   ├── search-tiers.md          # 7-tier sovereign search protocol
│   ├── hivemind-protocol.md     # Awareness, handoffs, locks, heartbeats
│   ├── delegation-rules.md      # Direct execution, no self-recursion
│   ├── heritage-rules.md        # [id-soft:] tagging, vet log
│   └── continuity.md            # Hydration sequence, session anchors
├── kali/
│   ├── identity.md              # Transcendent Oversight — sees all
│   └── dispatch-patterns.md     # Direct vs dispatch vs council
├── maat/
│   └── identity.md              # Light Oversoul — P1-P5 governance
├── lilith/
│   └── identity.md              # Dark Oversoul — P6-P10 governance
├── pillar/
│   ├── base.md                  # Slot-agent base identity
│   └── slots/
│       ├── p1.md                # Infrastructure
│       ├── p2.md                # Persistence
│       ├── p3.md                # Engineering
│       ├── p4.md                # Integration
│       ├── p5.md                # Governance
│       ├── p6.md                # Cognition (Vision)
│       ├── p7.md                # Context
│       ├── p8.md                # Observability
│       ├── p9.md                # Orchestration
│       └── p10.md               # Validation
├── verity/
│   ├── identity.md              # Unified compliance + scribe
│   └── scribe-protocol.md       # L1→L2→L3 distillation pipeline
├── doom_guy/
│   └── identity.md              # id Software heritage guardian
└── grok_cli/
    └── identity.md              # Advisory cloud mind
```

### 5.2 Agent Config — Composed from Fragments

```jsonc
{
  "agent": {
    "kali": {
      "mode": "all",
      "model": "nemotron-3-ultra",
      "prompt": "{file:.opencode/agent-prompts/shared/mandates.md}\n\n{file:.opencode/agent-prompts/shared/hivemind-protocol.md}\n\n{file:.opencode/agent-prompts/shared/delegation-rules.md}\n\n{file:.opencode/agent-prompts/kali/identity.md}",
      "permission": {
        "edit": "allow",
        "bash": "allow",
        "task": "allow"
      },
      "steps": 50
    },
    "verity": {
      "mode": "all",
      "model": "nemotron-3-ultra",
      "prompt": "{file:.opencode/agent-prompts/shared/mandates.md}\n\n{file:.opencode/agent-prompts/shared/hivemind-protocol.md}\n\n{file:.opencode/agent-prompts/verity/identity.md}\n\n{file:.opencode/agent-prompts/verity/scribe-protocol.md}",
      "permission": {
        "edit": "read",
        "bash": "deny"
      }
    },
    "pillar-p1": {
      "mode": "all",
      "prompt": "{file:.opencode/agent-prompts/shared/mandates.md}\n\n{file:.opencode/agent-prompts/pillar/base.md}\n\n{file:.opencode/agent-prompts/pillar/slots/p1.md}",
      "permission": {
        "edit": "allow",
        "bash": "allow"
      }
    },
    "pillar-p2": {
      "mode": "all",
      "prompt": "{file:.opencode/agent-prompts/shared/mandates.md}\n\n{file:.opencode/agent-prompts/pillar/base.md}\n\n{file:.opencode/agent-prompts/pillar/slots/p2.md}",
      "permission": { ... }
    }
    // ... pillar-p3 through pillar-p10 follow same pattern
  }
}
```

**Key design decisions:**
1. **Separate agents per pillar slot** (not parameterized) — OpenCode has no slot variable at config time
2. **`\n\n---\n\n` as separator** between fragments in the composed prompt
3. **Self-contained prompts** — each must include mandates because `prompt` replaces provider defaults
4. **`instructions` array stays as file paths** — for AGENTS.md compatible content that should remain as file references (discoverable by read tool, etc.)

### 5.3 Agent Markdown Files Stay For Frontmatter

The `.opencode/agents/kali.md` files **remain** but shrink to frontmatter-only:

```markdown
---
description: Transcendent Oversight — Sees all, delegates to Ma'at/Lilith, destroys drift
mode: all
color: "#8B0000"
steps: 50
permission:
  edit: allow
  bash: allow
  task: allow
---
```

The body becomes empty (or contains a brief reference comment). The actual prompt is in `opencode.json` via `prompt: "{file:...}"`.

This preserves:
- OpenCode agent discovery (finds `.opencode/agents/*.md`)
- Permission model (frontmatter)
- Display metadata (color, description)
- The `prompt` field in `opencode.json` takes priority over the markdown body

### 5.4 Secrets Management Integration

**Current (env vars):**
```json
"headers": { "x-api-key": "${EXA_API_KEY}" }
```

**Target (file-based, with Omega-Vault):**
```json
"headers": { "x-api-key": "{file:~/.config/opencode/secrets/exa-api-key}" }
```

**Integration with Omega-Vault (D-299):**
- Omega-Vault stores credentials encrypted in OS keyring
- On rotation: writes new key to `~/.config/opencode/secrets/<provider>-key`
- OpenCode picks up new key on TUI restart (config load time)
- No .env reload, no process env inheritance

**Priority chain for secrets:**
1. `{file:~/.config/opencode/secrets/<name>}` — file-based, permission-bound, vault-managed
2. `{env:VAR}` — fallback for non-secret overrides (model, temperature)
3. Hardcoded — never for secrets

### 5.5 Remote Config for Org-Level Shared Rules

OpenCode supports remote config from `.well-known/opencode` and the `instructions` array supports URLs:

```json
{
  "instructions": [
    "https://raw.githubusercontent.com/anomalyco/omega-engine/main/SOVEREIGN_MANDATES.md"
  ]
}
```

This enables:
- **Org-wide mandates** that update without syncing
- **Cross-project shared rules** (e.g., all Omega-related projects)
- **Versioned instructions** (pin to commit SHA)

**Caveat**: Remote instructions have 5s timeout and V2 currently doesn't resolve them (per V2 docs). Monitor for V2 resolution support.

---

## §6 Implementation Plan

### Phase 0: Foundation (30 min)

1. **Create directory structure:**
   ```bash
   mkdir -p .opencode/agent-prompts/{shared,kali,maat,lilith,makali,pillar/slots,verity,doom_guy,john_carmack,roc_racoon,researcher,jem,grok_cli}
   ```

2. **Extract Sovereign Mandates** from any single agent file:
   - Copy mandate block from `kali.md` lines 36-58 (or wherever they start)
   - Write to `.opencode/agent-prompts/shared/mandates.md`
   - Verify: `grep "M1 AnyIO" .opencode/agent-prompts/shared/mandates.md` → one match

### Phase 1: Pilot — 3 Agents (1 hr)

3. **Write identity fragments** for kali, verity, and pillar-p1:
   - Extract role-specific content from each `.md` file (everything after frontmatter that ISN'T shared boilerplate)
   - Write to `.opencode/agent-prompts/{agent}/identity.md`

4. **Update `opencode.json`** for 3 agents:
   - Add `prompt` field with `{file:}` composition
   - Keep `instructions: [".opencode/agents/kali.md"]` for frontmatter discovery

5. **Shrink markdown files** to frontmatter-only body:
   - Remove duplicated mandate blocks
   - Remove shared protocols
   - Keep only identity-specific content

6. **Restart OpenCode TUI** and verify each agent loads correctly

### Phase 2: Fleet Rollout (2 hr)

7. **Repeat Phase 1 for all 12 agents**
8. **Move secrets from env to files**
9. **Update SOVEREIGN_ARK_BLUEPRINT.md** with new config architecture section

### Phase 3: V2 Migration Watch (ongoing)

10. **Monitor V2 `instructions` array resolution** — once V2 supports it, can move shared fragments to `instructions`:
    ```json
    "instructions": [
      ".opencode/agent-prompts/shared/mandates.md",
      ".opencode/agent-prompts/shared/search-tiers.md"
    ]
    ```
11. **Monitor `{env:}` fix for MCP remote headers** — once fixed, can switch back from `{file:}` where env vars are preferred

---

## §7 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| `prompt` replaces provider prompt entirely | Agent loses provider-specific behavior | Ensure composed prompt is self-contained; test with 2 different models |
| `{file:}` content is static at load time | Fragment changes require TUI restart | Document requirement; Omega-Vault handles secret rotation gracefully |
| Missing fragment file blocks config load | Agent fails silently or config error | Use `missing: "empty"` or validate with `opencode --config-check` |
| Large composed prompts (>context limit) | Model rejects or compacts aggressively | Keep fragments lean; test total prompt size |
| V2 config changes (`agent` → `agents`, `prompt` → `system`) | Config becomes invalid | Monitor OpenCode release notes; maintain backward compat |
| Agent markdown body vs `prompt` conflict | Both loaded — duplicate instructions | Empty markdown body after frontmatter; `prompt` in config takes priority |
| `{env:}` in MCP headers broken | Auth failures with workaround | Use `{file:}` for MCP headers; track issue #23664 |

---

## §8 Immediate Wins — Quickest ROI

1. **Extract mandates** (10 min) — eliminates 220 duplicated lines across fleet
2. **Move EXA API key** (5 min) — `{file:~/.config/opencode/secrets/exa-api-key}` — security hardening
3. **Pilot kali + verity + pillar-p1** (30 min) — validates composable prompt architecture
4. **Document the pattern** in `docs/reference/OPENCODE_CONFIG_ARCHITECTURE.md` (20 min)

---

## §9 Research Sources

### OpenCode Source Code
- `packages/opencode/src/config/variable.ts` — `substitute()` function
- `packages/opencode/src/config/paths.ts` — path resolution

### OpenCode Documentation
- https://opencode.ai/docs/config/ — `{file:path}` and `{env:VAR}` substitution
- https://opencode.ai/docs/agents/ — agent config with `prompt`
- https://opencode.ai/docs/rules/ — AGENTS.md and instructions
- https://v2.opencode.ai/agents — V2 agent schema (`agents`, `system`)
- https://v2.opencode.ai/instructions — V2 instruction loading

### GitHub Issues (Cross-Referenced)
| Issue | Topic | Status |
|-------|-------|--------|
| #19946 | `{env:}` broken in provider apiKey | Closed — use `{file:}` workaround |
| #23664 | `{env:}` broken in MCP remote headers | Open — use `{file:}` workaround |
| #28527 | `{env:}` broken in provider options.headers | Open — use `{file:}` workaround |
| #13219 | `OPENCODE_CONFIG_CONTENT` bypasses substitution | Fixed |
| #11793 | `$` in file content crashes config | Fixed (#12390) |
| #5299 | `{env:}` inconsistent across MCP servers | Open — investigation |
| #14986 | Unescaped env token can corrupt JSON parse | Fixed (#14987) |
| #20640 | Windows backslashes in `{env:}` | Fixed (#29282) |
| #3202 | Dynamic system prompt templating (PR) | Merged — commands |
| #7369 | Shared prompt across markdown agent definitions | Open — feature request |

### Prompt Architecture Analysis
- https://gist.github.com/rmk40/cde7a98c1c90614a27478216cc01551f — Prompt assembly pipeline
- `packages/opencode/src/session/llm.ts` — `system.push()` construction
- `packages/opencode/src/session/prompt.ts` — main entry point
- `packages/opencode/src/session/system.ts` — instruction loading
- `packages/opencode/src/agent/agent.ts` — agent definitions
- `packages/opencode/src/session/instruction.ts` — AGENTS.md discovery

---

## §10 Handoff to Kali

**⬡ OMEGA ⬡ KALI HANDOFF ⬡ 2026-07-20**

### Summary

Discovered and deeply researched OpenCode's `{file:path}` config variable substitution feature. Source code verified at `packages/opencode/src/config/variable.ts`. Cross-referenced with 10+ GitHub issues, all 3 official docs sites, and the prompt assembly architecture.

### Key Findings for Kali's Oversight

1. **11/12 agent files duplicate the Sovereign Mandates** (~220 lines). This is the #1 maintenance tax on the fleet.
2. **`{file:path}` enables composable prompt fragments** — shared content extracted once, referenced by all agents.
3. **`{file:}` is more reliable than `{env:}`** for secrets — multiple confirmed bugs in `{env:}` substitution across provider options, MCP headers, and headers.
4. **`prompt` replaces provider default** — Omega Engine's composed prompts must be self-contained.
5. **Agent `.md` files shrink to frontmatter-only** — `prompt` in `opencode.json` takes priority.

### Recommended Next Actions

| Priority | Action | Owner | Effort |
|----------|--------|-------|--------|
| P0 | Review this document and ratify approach | Kali | 15 min |
| P1 | Create fragment directory structure + extract mandates | P3 Engineering | 30 min |
| P1 | Pilot kali + verity + pillar-p1 with composed prompts | P3 Engineering | 1 hr |
| P2 | Move EXA key from `{env:}` to `{file:}` | P3 Engineering | 5 min |
| P2 | Fleet rollout to all 12 agents | P3 Engineering | 2 hr |
| P3 | Document pattern in `docs/reference/` | P5 Governance | 30 min |
| P3 | Track V2 `instructions` resolution for future migration | P3 Engineering | ongoing |

### Handoff Packet

- **Research document**: `docs/research/R_OPENCODE_FILEPATH_CONFIG_ARCHITECTURE_20260720.md`
- **Research sources**: Cross-referenced in §9 above
- **Blockers**: None — feature is stable in current OpenCode version
- **Risks**: Monitor V2 schema migration (`agent` → `agents`, `prompt` → `system`)

⬡ OMEGA ⬡ KALI ⬡ FOR THE FLEET

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
