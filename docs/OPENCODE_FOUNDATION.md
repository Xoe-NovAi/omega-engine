# OpenCode Hosted-Free Model Foundation

**Status:** authoritative foundation for OpenCode model selection and compaction
**Verified:** 2026-09-23 against OpenCode 1.18.32, the live OpenCode Zen/Go catalogs, Models.dev, Google's Gemini API documentation, and the current `config.json` schema
**Scope:** hosted foundation only; local-model routing is deliberately deferred

## Non-negotiable model doctrine

1. **Rotating stealth aliases are dynamic endpoints, not stable models.** `opencode/big-pickle`, `opencode/space-bunny-free`, and any future anonymous alias may change underlying checkpoint, context window, output limit, modalities, pricing, or privacy terms without notice.
2. **Never hardcode a rotating alias's context or output limits.** A limit observed on Node 1 is not valid on Node 0, and a Models.dev snapshot may lag the serving alias in either direction.
3. **Select aliases; do not guess their identity.** Use the exact provider/model ID and let OpenCode's live registry supply current metadata.
4. **Refresh before operational claims.** Use `opencode models <provider> --verbose --refresh`; provider claims and operator measurements remain distinct evidence classes.
5. **Hardcode behavior and policy, not transient capacity.** Stable configuration may pin a model alias, agent role, privacy class, permission boundary, and compaction strategy. It must not pin the mutable limits of an anonymous alias.

## Current hosted-free foundation

### OpenCode Zen

The official Zen documentation currently identifies these free entries:

- `big-pickle` — stable free stealth alias; underlying model rotates.
- `space-bunny-free` — anonymous/stealth free alias; zero retention and no training according to OpenCode's privacy table.
- `mimo-v2.6-flash-free`
- `mimo-v2.5-free`
- `ling-3.0-flash-fin-free`
- `nemotron-3-ultra-free`
- `nemotron-3.5-lightning-free`
- `muse-spark-1.3-contributor-free`
- `jev-1.13-free`

The live Zen API can expose transitional or additional IDs not yet present in the documentation table. The documented table is the policy baseline; the live registry is the availability check.

### Big Pickle

`opencode/big-pickle` is permanently authorized as a free stealth-model alias. The absence of a `-free` suffix does **not** make it paid: OpenCode's official pricing table marks input, output, and cached reads free.

Big Pickle's served capacity has changed in place during prior use. Historical Node 1 sessions and registry snapshots have disagreed. Therefore:

- selecting the alias is valid;
- asserting a permanent 1M or 200K window is invalid;
- writing `provider.opencode.models.big-pickle.limit.*` is forbidden unless a deliberate, temporary experiment is explicitly documented and automatically drift-checked.

### Space Bunny Free

`opencode/space-bunny-free` is an anonymous stealth alias. OpenCode does not identify it as DeepSeek V4.1 Flash or any other named checkpoint. Similarities such as 1M context, reasoning, and multimodality are insufficient fingerprinting.

Treat all of the following as hypotheses, not identity claims:

- unmodified DeepSeek V4.1 Flash;
- a fine-tuned or optimized derivative;
- a gateway adapter around a named model;
- a rotating anonymous checkpoint.

The public model launched on 2026-09-23, so there is not yet a mature independent fingerprint or sustained benchmark corpus. Evaluate it empirically before assigning permanent workload status.

### Google Gemini API

Google's official API pricing table confirms genuine free API tiers for:

| Role | Exact OpenCode ID | Context | Output | Free API tier |
|---|---|---:|---:|---|
| Newest capable free Flash | `google/gemini-3.8-flash` | 1,048,576 | 65,536 | Yes |
| Previous-generation fallback | `google/gemini-3.7-flash` | 1,048,576 | 65,536 | Yes |
| Earlier fallback | `google/gemini-3.6-flash` | 1,048,576 | 65,536 | Yes |
| Older capable fallback | `google/gemini-3.5-flash` | 1,048,576 | 65,536 | Yes |
| High-volume economy model | `google/gemini-3.5-flash-lite` | 1,048,576 | 65,536 | Yes |

Selection doctrine:

- use Gemini 3.8 Flash for current public research and high-quality agentic work;
- use Gemini 3.5 Flash-Lite for high-volume extraction/classification;
- keep 3.7/3.6/3.5 available for A/B evidence, not permanent hardcoded roles by default;
- read actual RPM/TPM/RPD quotas from the signed-in Google AI Studio project because Google no longer publishes one universal quota table.

Google's unpaid/free API service may use prompts and responses to improve Google products. Do not send private or confidential material through the free Google API tier.

## Privacy classes

| Class | Examples | Use |
|---|---|---|
| Free + zero retention | Space Bunny Free | Private hosted work, subject to the stealth alias's mutable terms |
| Free + training/retention exception | Big Pickle free period, MiMo free, Ling free | Non-sensitive work only |
| Free + trial logging | Nemotron free endpoints | Non-sensitive evaluation only; no personal/confidential data |
| Contributor training | Muse Spark contributor-free | Only prompts explicitly approved for training |
| Free Google API | Gemini 3.5–3.8 Flash families | Public research only; unpaid-service data-use terms apply |

## Configuration doctrine

### Do not duplicate the live model catalog

OpenCode uses Models.dev plus provider discovery. Manually enumerating every model under `provider.*.models` duplicates mutable metadata and has repeatedly produced stale limits. Only define a provider model entry when deliberately overriding behavior such as a variant, option, timeout, or documented experiment.

### Stable aliases may be selected

A default such as `opencode/space-bunny-free` is acceptable because the **alias ID** is stable. Do not attach hardcoded `limit`, modality, or identity assumptions to that alias.

### Agent model inheritance

- Primary agents use the global model unless they declare their own.
- Subagents inherit the invoking primary agent's model unless they declare their own.
- Only pin a subagent when its role genuinely requires a different provider, privacy class, or capability profile.

### Correct current agent fields

- Use `prompt`, not `system_prompt`.
- Use `{file:<path>}` for an external prompt file.
- `inherit_context`, `allow_background_execution`, and other unknown top-level agent keys are provider pass-through options, not current OpenCode agent controls.
- Background delegation is a Task invocation choice.

### Permission ordering

Insertion order matters and the **last matching rule wins**. Put the broad rule first:

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

Putting `*: deny` last silently overrides preceding allows.

### Delegation depth

Use `subagent_depth: 1` unless nested delegation is an explicit requirement. Primary-to-specialist delegation is sufficient for the current architecture and avoids unnecessary recursion and permission surface.

## Compaction foundation for OpenCode 1.18.x

The current v1 schema supports:

```json
{
  "compaction": {
    "auto": true,
    "prune": true,
    "tail_turns": 2,
    "preserve_recent_tokens": 8000,
    "reserved": 20000
  }
}
```

Hardcode only intentional deviations from adaptive defaults:

```json
{
  "compaction": {
    "auto": true,
    "prune": true
  }
}
```

### Defaults to preserve

- `auto` defaults to true.
- `reserved` defaults to `min(20,000, model maximum output)`.
- `tail_turns` omitted means all recent turns are eligible, bounded by the token budget.
- `preserve_recent_tokens` defaults to 25% of usable context, clamped to 2,000–15,000 tokens.

Hardcoding these values is especially brittle when the active model is a rotating alias whose context metadata changes.

### Trigger semantics

OpenCode computes usable context from the selected model's live metadata:

- when an explicit input limit exists: `input_limit - reserved`;
- otherwise: `context_limit - maximum_output`.

Never calculate or persist trigger points from an alias's historical context number.

### Pruning semantics

`prune: true` protects:

- the two newest user turns;
- approximately the newest 40K tokens of tool output;
- `skill` tool output.

It clears older completed tool outputs only when more than approximately 20K tokens can be reclaimed. This reduces pressure before full summary compaction.

### Well and Gnosis integration

`gnosis-leash.js` injects active Well rules and the populated session narrative through `experimental.session.compacting`. Keep manual gnosis-lock preparation ahead of intentional `/compact`; automatic compaction remains the emergency path.

## Verification procedure

```bash
opencode --version
opencode debug config
opencode models opencode --verbose --refresh
opencode models google --verbose --refresh
```

Verify:

1. the intended alias is active;
2. no custom `limit` override exists for rotating stealth aliases;
3. task permission rules are ordered broad-first, specific-last;
4. agent prompts use `prompt`/`{file:...}`;
5. `compaction.auto` and `compaction.prune` resolve as intended;
6. Node 0 and Node 1 may report different live capacities without configuration drift being misdiagnosed as a bug.

## Sources

- OpenCode Zen: https://opencode.ai/docs/zen/
- OpenCode Go: https://opencode.ai/docs/go/
- OpenCode agents: https://opencode.ai/docs/agents/
- OpenCode config/schema: https://opencode.ai/docs/config/ and https://opencode.ai/config.json
- OpenCode models: https://opencode.ai/docs/models/
- OpenCode permissions: https://opencode.ai/docs/permissions/
- Google Gemini pricing: https://ai.google.dev/gemini-api/docs/pricing
- Google Gemini rate limits: https://ai.google.dev/gemini-api/docs/rate-limits
- Google Gemini terms: https://ai.google.dev/gemini-api/terms

## Deferred work

Implementation of the configuration cleanup is a separate queued ROADMAP item. Local-model routing remains deferred until this hosted foundation is applied and verified.
