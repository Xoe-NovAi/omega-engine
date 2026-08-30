# opencode.json — Complete Before/After Diff (Phase 1)

**Target**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json`  
**Authority**: Phase 1 Plan + Carmack Review modifications (Q1.1, Q2.1, Q3.1, Q5.1)  
**ToolProfile stubs**: Document intent for Phase 2 MCP domain split (Q2.1)

> **⚠️ REMEDIATED 2026-08-21** (Architect rulings Q1–Q5; audit trail `09_SPEC_DEVIATIONS.md`):
> ① Plugin registration paths corrected singular→plural (D2). ② Compaction target now
> **V1-keys-primary** with binary-pin gate for the V2 family (D3). ③ `OPENCODE_DISABLE_AUTOCOMPACT`
> documented global-only WITH #32385 bypass caveat (D10, M23 honesty). ④ "8K-16K" context prose
> corrected (D11: base=32K native/128K YaRN, Thinking-2507=256K native; ctx-raise HELD pending
> Architect/ZS-1). ⑤ Live config has 12 agents; this diff models the 6 in CI scope (D4).

---

## Current State (Key Sections)

```json
{
  "instructions": [
    "SOVEREIGN_MANDATES.md",
    "ORACLE_STACK.md",
    "docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md",
    "docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md",
    "CREDITS.md"
  ],
  "compaction": {
    "auto": true,
    "prune": true,
    "tail_turns": 3,
    "preserve_recent_tokens": 40000,
    "reserved": 10000
  },
  "plugin": [
    "opencode-antigravity-auth@latest",
    "opencode-sessions-explorer",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/error-capture.ts",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/awareness.ts"
  ],
  "agent": {
    "kali": { "mode": "all", "temperature": 0.5, "steps": 50 },
    "researcher": { "mode": "all", "temperature": 0.5, "steps": 100 },
    "maat": { "mode": "all", "temperature": 0.5 },
    "lilith": { "mode": "all", "temperature": 0.5 },
    "node": { "mode": "all", "temperature": 0.5 },
    "verity": { "mode": "all", "temperature": 0.5 }
  }
}
```

**Reality notes (2026-08-21)**:
- ⚠️ The two repo plugin entries point at `.opencode/plugin/` (singular) which does NOT exist — files live at `.opencode/plugins/`. Both registrations are dead today (D2). The diff below REPAIRS them.
- ⚠️ Live config defines **12 agents** (makali, jem, doom_guy, roc_racoon, researcher, kali, maat, lilith, verity, node, john_carmack, grok_cli). This diff shows only the 6 within CI scope; the other 6 are intentionally untouched in Phase 1 (D4 — logged as DEV-06).
- ⚠️ Live compaction uses the **V1 key family only** (`tail_turns/preserve_recent_tokens/reserved`). No `buffer`/`keep.tokens` keys exist today.

---

## Target State (Phase 1 — Carmack Modified, Remediated)

### Compaction keys — PIN-GATED (D3 / DEV-02)

**Primary target (V1 family — matches v1.x stable schema & live config):**

```json
"compaction": {
  "auto": true,
  "prune": true,
  "tail_turns": 5,
  "preserve_recent_tokens": 80000,
  "reserved": 20000
}
```

**Conditional alternative (V2 family `{buffer, keep.tokens}`) — ONLY if Test 0 binary pin proves
the running binary consumes V2 keys.** Web evidence (N7_WEB_RESEARCH Q-B2): v1.x honors the V1
family; `buffer`/`keep.tokens` belong to the separate V2 product line, and the V1 schema sets
`additionalProperties: false`, so cross-family keys may trip strict validation. Local binary
strings show both families present (DD-II-2) — hence the pin gate, not an assumption:

```json
"compaction": {
  "auto": true,
  "keep": { "tokens": 20000 },
  "buffer": 50000
}
```

**Pin procedure**: record `opencode --version`; consult decision table in `09_SPEC_DEVIATIONS.md`
§Binary-Pin; apply exactly ONE family; never both (mixed families are unvalidated).

### Full target state (V1-primary variant shown; model strategy per DEV-12)

> **Model strategy (DEV-12, Architect-approved)**: top-level `"model"` = local-first default for
> ALL agents (M7); pins kept ONLY where binding is intentional — `kali` (cloud quality floor,
> Q5.1) and `verity` (hidden cheap-critic subagent). Unpinned agents inherit the global default
> AND gain durable TUI `/models` freedom (#13456 snap-back avoided); CLI `-m` always wins regardless.
> `variant` dropped everywhere — empirically inert on our LM Studio models (see `09` §Variant
> Findings); returns later as invocation-time `--variant` selection per PP-1 if needed.
> Consequence on record: `node`'s effective default moves qwen3-1.7b → qwen3-4b-thinking via
> inheritance (accepted; /models can override interactively).

```json
{
  "model": "lmstudio/qwen3-4b-thinking",
  "instructions": ["AGENTS.md"],
  "plugin": [
    "opencode-antigravity-auth@latest",
    "opencode-sessions-explorer",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/error-capture.ts",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/awareness.ts",
    "file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts"
  ],
  "agent": {
    "kali": {
      "mode": "all",
      "model": "opencode/nemotron-3-ultra-free",
      "temperature": 0.3,
      "steps": 50,
      "toolProfile": "deploy"
    },
    "researcher": {
      "mode": "all",
      "temperature": 0.1,
      "steps": 100,
      "toolProfile": "research"
    },
    "maat": {
      "mode": "all",
      "temperature": 0.2,
      "toolProfile": "dev"
    },
    "lilith": {
      "mode": "all",
      "temperature": 0.3,
      "toolProfile": "run"
    },
    "node": {
      "mode": "all",
      "temperature": 0.1,
      "steps": 20,
      "toolProfile": "debug"
    },
    "verity": {
      "mode": "subagent",
      "model": "lmstudio/qwen3-1.7b",
      "temperature": 0.0,
      "prompt": "{file:.opencode/agents/verity.md}",
      "permission": { "edit": "deny", "bash": "deny", "skill": "deny" },
      "hidden": true,
      "toolProfile": "audit"
    }
  }
}
```

> `toolProfile` remains a **silently-inert stub** (D9): upstream `AgentConfig` has no such key and
> does not set `additionalProperties:false`, so it neither validates-fails nor does anything.
> Kept per Carmack Q2.1 as Phase 2 intent documentation only — claim NO savings from it.

---

## Complete Unified Diff

```diff
--- a/opencode.json
+++ b/opencode.json
@@ -1,53 +1,78 @@
  {
  -  "instructions": [
  -    "SOVEREIGN_MANDATES.md",
  -    "ORACLE_STACK.md",
  -    "docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md",
  -    "docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md",
  -    "CREDITS.md"
  -  ],
  +  "instructions": ["AGENTS.md"],
    "compaction": {
      "auto": true,
      "prune": true,
  -    "tail_turns": 3,
  -    "preserve_recent_tokens": 40000,
  -    "reserved": 10000
  +    "tail_turns": 5,
  +    "preserve_recent_tokens": 80000,
  +    "reserved": 20000
  +    // V2 family {buffer, keep.tokens} ONLY on binary-pin proof — see PIN-GATED section
    },
    "plugin": [
      "opencode-antigravity-auth@latest",
      "opencode-sessions-explorer",
  -    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/error-capture.ts",
  -    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/awareness.ts",
  +    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/error-capture.ts",
  +    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/awareness.ts",
  +    "file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts"
    ],
```

*(Agent-object hunks unchanged from original spec — see "Full target state" above for the
authoritative agent blocks incl. `toolProfile` stubs and verity isolation. JSON has no comments:
the `// V2 family` line above is annotation only — do not paste into opencode.json.)*

---

## Change Rationale (Carmack Review Mapping)

| Change | Carmack Q | Reason |
|--------|-----------|--------|
| `instructions: ["AGENTS.md"]` | Q1.1 | AGENTS.md = guaranteed auto-discovery path; `instructions[]` is ADDITIVE to it, not ignored (web Q-B7: "All instruction files are combined with your AGENTS.md files") — single-entry array keeps the doctrine SSOT unambiguous |
| `compaction` V1 retune (tail_turns 5 / preserve 80000 / reserved 20000) | Q3.1 | More recent turns + larger reserve for 1M-context cloud model; V1 family is what v1.x honors |
| ~~`compaction.buffer/keep.tokens`~~ → pin-gated | Q3.1 | V2-product-line keys; inert (or validation-failing) on v1.x — apply only after binary pin proves consumption (D3/DEV-02) |
| Repair plugin paths singular→plural | — (N7 audit D2) | Existing error-capture/awareness registrations point at nonexistent dir |
| Add sovereign-compaction plugin | Q3.3 | Pre-compaction hook injects mandates/entity/anchor |
| `kali.model: opencode/nemotron-3-ultra-free` | Q5.1 | Orchestration quality floor — cloud justified |
| `kali.model: opencode/nemotron-3-ultra-free` (PIN KEPT) | Q5.1 | Orchestration quality floor — cloud justified; only primary agent with intentional pin |
| ~~per-agent `model` on researcher/maat/lilith/node~~ → **top-level `model: lmstudio/qwen3-4b-thinking`** (DEV-12) | Q5.1 intent, amended mechanism | Local-first default via inheritance; durable TUI `/models` freedom (#13456 snap-back); CLI `-m` remains supreme override. Context truth (D11): base=32K native/128K YaRN; Thinking-2507=256K native; live cap 8192 is a config choice — ctx-raise 8192→32768 DEFERRED, gated on ZS-1 zswap, logged as PP-3 (plan doc §6) |
| `verity.model: lmstudio/qwen3-1.7b` (PIN KEPT) | Q5.2 | Hidden cheap-critic subagent — hard-binding IS the design intent; TUI freedom N/A |
| ~~`variant` on all agents~~ → DROPPED (DEV-12) | Q5.1 amended | Empirically inert: qwen3-4b-thinking/qwen3-1.7b declare EMPTY variant maps (opencode models --verbose, 1.18.19); nemotron HAS low/medium/high → use invocation-time `--variant high` for kali when needed (PP-1) |
| `verity.mode: subagent` + restrictive perms | Q5.2 | Isolation for audit agent; no parent context |
| `verity.hidden: true` | Q5.2 | Prevents accidental @-invocation |
| `toolProfile` stubs on all agents | Q2.1 | Phase 2 intent documentation ONLY — silently inert upstream (D9); no savings claimed |

---

## ToolProfile Values (Phase 2 Intent)

| Agent | toolProfile | Intended MCP Server (Phase 2) |
|-------|-------------|-------------------------------|
| kali | `deploy` | github-hub + hivemind-hub |
| researcher | `research` | research-hub + oracle-hub |
| maat | `dev` | oracle-hub + github-hub |
| lilith | `run` | hivemind-hub + oracle-hub |
| node | `debug` | oracle-hub + hivemind-hub |
| verity | `audit` | oracle-hub (read-only) |

**Note**: `toolProfile` is a config stub — opencode doesn't support it yet. Phase 2 implements domain-scoped MCP servers and wires profiles to `mcp` config per agent.

---

## Environment Variables

Add to shell profile (`.bashrc`, `.zshrc`) or session startup:

```bash
# Disable AUTO-compaction (Architect ruling Q4: SHIP + DOCUMENT)
# ⚠️ SCOPE: process-global — there is NO per-agent variant upstream (web Q-B3:
# flag maps to compaction.auto:false at config load). This also disarms auto-
# compaction for the 1M-context cloud workhorse; manual /compact remains
# available and is the required discipline under this flag.
# ⚠️ KNOWN BYPASS (M23 honesty, #32385): the provider-overflow auto-recovery
# path has historically ignored auto:false / this env var through ≥v1.17.7.
# Treat "fully off" as unreliable until verified on the PINNED binary (Test 0).
export OPENCODE_DISABLE_AUTOCOMPACT=1

# Active entity/phase for compaction plugin
export OMEGA_ENTITY="${OMEGA_ENTITY:-kali}"
export OMEGA_PHASE="${OMEGA_PHASE:-PUBLIC-DEBUT-01}"
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ci_phase1_spec ⬡ 2026-08-20*