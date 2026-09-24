# OpenCode Hosted-Free Model Foundation

**Status:** authoritative foundation for OpenCode hosted-model safety, compaction, agents, and permissions
**Verified:** 2026-09-23 against OpenCode 1.18.32, the published v1/v2 configuration docs, current upstream schema/source, first-party provider terms, and live operator evidence
**Scope:** hosted models; local-model routing remains separate

## Non-negotiable model doctrine

1. **Rotating stealth aliases are dynamic endpoints, not stable checkpoints.** `opencode/big-pickle`, `opencode/space-bunny-free`, and future anonymous aliases may change identity, capacity, output allowance, modalities, availability, or privacy terms without notice.
2. **Never hardcode context, input, output, modality, or identity metadata for any cloud model in durable configuration.** This includes anonymous aliases and named free models whose catalogs, quotas, or provider routing can change.
3. **Select a stable provider/model ID only when the model itself is stable.** A stable alias ID is acceptable; custom `provider.*.models.*.limit` entries are not a substitute for live metadata.
4. **Refresh runtime metadata before operational claims.** Use `opencode models <provider> --verbose --refresh`; provider statements, registry observations, and operator measurements are distinct evidence classes.
5. **Hardcode policy and behavior, not transient capacity.** Alias selection, privacy class, agent role, permission boundary, and whether to prune are valid stable configuration. A copied context number is not.

## Hosted-free evidence classes

### OpenCode Zen

The official Zen page is the policy baseline; the live registry is the availability check. Current free entries include anonymous/stealth aliases and rotating free endpoints.

- **Big Pickle:** officially priced at $0 and therefore free despite lacking a `-free` suffix. During its free period, OpenCode states collected data may be used to improve the model. Treat it as non-private.
- **Space Bunny Free:** officially free and described as a stealth model with
  zero data retention and no model-training use. This is a current provider
  claim, not a permanent alias property. Under the global conservative policy,
  private work still uses paid zero-retention models only; Space Bunny is for
  public/non-sensitive work unless policy is explicitly revalidated. Treat any
  observed context number as dated evidence, never configuration.
- **Other free Zen entries:** free status and privacy vary by endpoint. NVIDIA trial endpoints and contributor-training endpoints require stricter non-private handling.

The public model behind a stealth alias is not identified. Similarities to a named model are not an identity proof.

### Google Gemini API

Google offers genuine free API access to selected Flash and Flash-Lite models. Exact availability, quota buckets, and project-level limits are mutable and must be read from the live pricing/rate-limit surfaces and the signed-in AI Studio project.

The unpaid Gemini API service may use prompts and responses to improve Google products. Restrict this route to public/non-sensitive work. Do not use free Gemini for private, confidential, or proprietary material.

### OpenRouter free models

The `:free` suffix or `openrouter/free` router provides zero-token-cost endpoints, but availability, routing, rate limits, and upstream privacy vary. Account data-policy settings are required controls when selecting upstreams; never assume a zero-price route is private. A free-model pool is operational capacity, not a stable model contract.

## Dynamic model configuration

OpenCode's provider catalog and discovery are authoritative at runtime. For a manually added model, OpenCode may use conservative fallback metadata; those fallbacks are not detected capabilities. Define a custom model entry only when the model is absent from the catalog and authoritative metadata is available, or for a documented capability/variant override.

For every hosted model:

- do not add a durable `limit.context`, `limit.input`, or `limit.output` override;
- do not infer identity from a nickname;
- do not copy a provider page into configuration;
- do not add a custom alias via `modelID` unless the friendly ID is stable and the underlying model mapping is intentional;
- do refresh and inspect runtime metadata during health checks.

## Compaction doctrine

### Installed 1.18.x

OpenCode 1.18.32 uses the v1 compaction surface. Automatic compaction is enabled by default. The relevant controls are:

- `auto` — automatic compaction;
- `prune` — removal of old tool output; current docs default it to `false`;
- `reserved` — explicit safety reserve;
- `tail_turns` — recent turns retained by v1 behavior;
- `preserve_recent_tokens` — recent-token retention bound.

**Do not write `reserved: 20000`.** Omitting `reserved` preserves the adaptive behavior implemented in 1.18.x. When the selected model exposes an explicit input limit, the reserve defaults to `min(20000, its maximum output)`. When no input limit is exposed, usable context is `context limit - maximum output`; the configured `reserved` value is not consulted on that branch. An explicit `reserved` therefore replaces model-aware behavior only for models with an input limit and is appropriate only for a measured, model-specific experiment.

Recommended hosted-model posture:

```json
{
  "compaction": {
    "auto": true,
    "prune": true
  }
}
```

This intentionally enables automatic pruning but **omits `reserved`**. If pruning is not desired, omit the whole `compaction` block and preserve the built-in defaults. Never include a model-specific reserve merely because a model currently reports a large output allowance.

### Current V2 migration semantics

V2 renames the retained-context field and reserve:

- `preserve_recent_tokens` → `keep.tokens`;
- `reserved` → `buffer`;
- `prune` remains accepted but is reserved in the current V2 core and does not perform V1-style in-place pruning.

V2's omitted `buffer` default is 20,000 tokens. The trigger uses the selected model's live metadata:

```text
estimated tokens >= min(
  input limit - buffer,
  context limit - max(output reserve, buffer)
)
```

Thus, the durable configuration should still **omit `buffer`**. OpenCode applies its default against the current model's input/context/output metadata; writing `buffer: 20000` freezes the value and overrides model-aware behavior. V2 defaults `keep.tokens` to 15,000; increase it only when measured loss of recent detail justifies reducing available post-compaction workspace.

### Compaction limitations

- Compaction is lossy; earlier stored messages remain stored but are not necessarily active model context.
- V2 checkpoint summaries use the active model with tools disabled and a bounded summary output.
- Tool output can be truncated during checkpoint conversion; use explicit durable artifacts, Well records, and gnosis narrative for critical state.
- Provider overflow recovery is a safety net, not a substitute for accurate live model metadata.
- Fixed system instructions and advertised tool schemas can dominate the request and leave no compressible history.

### The CPU Register / RAM / Disk Paradigm (Semantic Write-Through)

**Hosted context is a volatile CPU register. MemPalace is durable RAM/Disk.** Treating context as working memory is a category error. Compaction is cache eviction, not a ceremonial crisis.

**Doctrine:**

- **Context (Register):** Volatile, lossy, bounded by `keep.tokens` and 4K summary bottleneck. Use for immediate computation only.
- **SQLite Continuity Store (RAM/Disk):** Authoritative durable state and event history. All active state — decisions, discoveries, blockers, todos, active-work pointers — is committed here first.
- **MemPalace Projection:** One-way searchable knowledge surface. It is rebuilt from continuity events and is never a second write authority or recovery source.
- **Artifacts / Well (Disk):** Immutable, canonical records. Snapshots, patches, gnosis narrative, constitutional records.

**Operational rules:**

1. **Semantic write-through is mandatory.** After every decision, discovery, task transition, or completed batch, persist state to the local SQLite continuity authority before continuing. Project to MemPalace only after the SQLite commit succeeds.
2. **Compaction is ordinary cache eviction.** No ceremony, no `prepare for compaction` ritual. `gnosis-lock` and `/compact` are fallback/recovery only.
3. **The active-work pointer lives in SQLite.** MemPalace is a one-way searchable projection and is not the recovery source of truth.
4. **Model swap = register swap.** Swapping models (Gemini ↔ Space Bunny ↔ Big Pickle) changes provenance, not entity identity; recovery reads SQLite continuity state.
5. **Chaos recovery is the acceptance test.** Kill the model, discard context, restart via a different adapter, and resume from WAD + SQLite continuity state. The entity must recover mission, todos, decisions, and identity; MemPalace projection may be rebuilt afterward.

## Agent schema and delegation

- Use `prompt`, including `{file:<path>}` for an external prompt.
- `system_prompt`, `inherit_context`, and `allow_background_execution` are not supported v1 agent controls. Unknown agent keys may be routed into provider `options` and must not be treated as OpenCode behavior.
- Background delegation is a Task invocation choice.
- Use `subagent_depth: 1` unless measured nested delegation is required.
- Primary-to-specialist delegation is sufficient for the current architecture.

## Permission doctrine

OpenCode's official v1.18 contract is **last matching rule wins**. Put the broad rule first and specific exceptions last:

```json
{
  "permission": {
    "task": {
      "*": "deny",
      "researcher_humboldt": "allow"
    }
  }
}
```

Putting `*: deny` last overrides preceding allows. Path-pattern behavior can also differ by tool because read and edit historically normalized paths differently; security tests must exercise absolute and worktree-relative paths against the installed release.

V2 changes the top-level names to `permissions`, `shell`, and `subagent`. Do not mix V1 and V2 permission shapes in one generation.

## Required global-config refactor

1. Do not add a `model` pin or any `provider.*.models.*.limit` for hosted models.
2. Remove the paid `gaming-expert` model pin so it inherits the active hosted-free selection unless a paid route is explicitly authorized.
3. Replace `researcher_humboldt.system_prompt` with `prompt: "{file:~/.config/opencode/prompts/researcher_humboldt.md}"` (a string containing the file directive).
4. Remove `inherit_context` and `allow_background_execution` from the active agent definition.
5. Reorder `build.permission.task` broad-first: `*: deny`, then each authorized specialist `allow`.
6. Keep the allowlist restricted to explicitly authorized agents.
7. Remove unsupported MCP fields that disappear during config resolution; remote `max_retries` is not part of the resolved MCP shape.
8. Set `subagent_depth: 1` unless nesting passes a measured task.
9. Add only `compaction.auto` and, if intentionally desired, `compaction.prune`; omit `reserved` in 1.18 and `buffer` in V2.
10. Pin the Antigravity plugin to a reviewed version rather than `@latest` if reproducible startup is required.
11. Rotate any credential exposed by diagnostic output. `opencode debug config` resolves environment substitutions and can print live secrets even when the source file contains placeholders; redirect and sanitize its output.

## Verification procedure

```bash
opencode --version
opencode models opencode --verbose --refresh
opencode models google --verbose --refresh
opencode models openrouter --verbose --refresh
```

After any global or project configuration edit, restart OpenCode; the running session keeps its startup-time configuration.

Verify:

1. no hosted model has a durable custom `limit`, modality, or identity override;
2. no paid model is pinned into a free-only agent;
3. `researcher_humboldt` resolves through `prompt` and `{file:...}`;
4. task permission rules are broad-first and specific-last;
5. `reserved` is absent in 1.18 configuration; `buffer` is absent in future V2 configuration;
6. `prune` is enabled only as an intentional policy choice;
7. provider refresh succeeds without treating a registry mismatch as permission to hardcode a value;
8. diagnostic output is sanitized before storage or sharing.

## Sources

- OpenCode v1 config: https://opencode.ai/docs/config
- OpenCode v1.18.32 compaction source: https://github.com/anomalyco/opencode/blob/v1.18.32/packages/opencode/src/session/compaction.ts
- OpenCode v1.18.32 overflow formula: https://github.com/anomalyco/opencode/blob/v1.18.32/packages/opencode/src/session/overflow.ts
- OpenCode v1 permission implementation: https://github.com/anomalyco/opencode/blob/v1.18.32/packages/opencode/src/permission/index.ts
- OpenCode v2 compaction: https://opencode.ai/v2/docs/compaction
- OpenCode v1→v2 migration: https://opencode.ai/v2/docs/migrate-v1
- OpenCode models: https://opencode.ai/docs/models and https://opencode.ai/v2/docs/models
- OpenCode permissions: https://opencode.ai/docs/permissions
- OpenCode agents: https://opencode.ai/docs/agents
- OpenCode Zen policy: https://opencode.ai/docs/zen
- OpenCode Go: https://opencode.ai/docs/go
- Google Gemini pricing/rate limits/terms: https://ai.google.dev/gemini-api/docs/pricing, https://ai.google.dev/gemini-api/docs/rate-limits, https://ai.google.dev/gemini-api/terms
- OpenRouter free router: https://openrouter.ai/docs/guides/routing/routers/free-router
- OpenRouter privacy/data controls: https://openrouter.ai/docs/guides/privacy

## Implementation status

The global configuration migration is implemented and validated in a fresh OpenCode process. Restart the current TUI to load it. Provider-side credential rotation remains external to this repository. Local-model routing remains a later phase and must not reintroduce host hardcoded context assumptions.
