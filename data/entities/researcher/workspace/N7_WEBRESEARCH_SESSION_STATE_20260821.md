# N7 Web Research — Session State Snapshot (researcher)

**Date**: 2026-08-21
**Status**: DORMANT — mission complete
**Artifact produced**: `data/entities/lilith/workspace/N7_WEB_RESEARCH_20260821.md` (Q-B1..B7 + Source Register + Deep Dive: Model Config Semantics DD-1..3)

## Accomplished

**Q-B verdicts (one-liners)**:
- **Q-B1**: Qwen3-4B = 32K native / 128K YaRN (factor 4.0); Thinking-2507 = **262,144 native**; live 8192 cap is a RAM choice, not a model limit; llama.cpp `-c 0` = GGUF trained ctx; Ollama default 4096 (since Apr 2025); LM Studio has no published universal default.
- **Q-B2**: v1.x honors `{auto, prune, tail_turns, preserve_recent_tokens, reserved}`; `{buffer, keep.tokens}` is V2-product-line-only; trigger = `totalTokens ≥ usable` (usable per `overflow.ts`, reserved default min(20k, maxOutput)).
- **Q-B3**: `OPENCODE_DISABLE_AUTOCOMPACT` is REAL (`flag.ts`), maps to `compaction.auto:false`, disables auto only; provider-overflow bypass bug persisted through v1.17.7 (#16882→#30664→#32385).
- **Q-B4**: `experimental.session.compacting` real in core; payload `{sessionID}` → `{context: string[], prompt?: string}`; `output.prompt` wholesale-replaces; fires pre-summary-generation; experimental/unstable.
- **Q-B5**: SKILL.md frontmatter = only `{name, description, license, compatibility, metadata}`; NO `auto_load`/`always_load`; on-demand via native `skill` tool; per-agent filtering via `permission.skill` patterns.
- **Q-B6**: `toolProfile` does NOT exist upstream — inert stub; official levers are `tools` (deprecated) / `permission`.
- **Q-B7**: AGENTS.md auto-discovery (cwd-up + global + CLAUDE.md fallback) AND `instructions: []` both inject; additive ("combined with your AGENTS.md files").

**Deep Dive (model config)**:
- **DD-1**: `agent.<name>.model` = HARD pin vs TUI `/models` (selection reverts, #13456/#1661) but SOFT vs explicit invocation — chain: `input.model ?? ag.model ?? currentModel(session)` (prompt.ts).
- **DD-2**: `variant` = named reasoning-effort/thinking preset; conditional default (applies ONLY when resolved model == agent's configured model AND variant declared); silently dropped otherwise; levers: `--variant` flag, `variant_cycle` keybind, command config; no env var.
- **DD-3**: No `OPENCODE_MODEL` env var; NO agent-level fallback chains (engine-side responsibility confirmed); `/models` persists as per-agent last-used unless pinned. **Recommendation delivered**: top-level `"model"` key + inheritance, pin only hidden system agents.

## Open Threads

- **PP-1 (variant invocation-time)**: nemotron `high/medium/low` variant support unverified against pinned binary — verify empirically via `opencode models --verbose` on opencode 1.18.19 before spec'ing variants (DD-2 caveat).
- **PP-3 (ctx raise)**: raising `qwen3-4b-thinking` context_length above 8192 is gated on ZS-1 (zswap/RAM headroom); KV estimate ~144 KB/token fp16 at 32K ≈ 4.5 GB (researcher-derived, see Q-B1).
- Hazard D3 (from prior Deep Dig, restated in research doc reconciliation note): pin exact local binary version before trusting compaction key-family targets.

## Wake Pointer

**On wake**: read THIS file first, then `data/entities/lilith/workspace/N7_WEB_RESEARCH_20260821.md` for full citations. Do NOT re-research unless paged by N7 — all primary sources are already registered in the doc's Source Register + Deep-Dive addendum.

*⬡ OMEGA ⬡ researcher ⬡ dormant 2026-08-21*
