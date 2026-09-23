# Session Narrative: session-2026-09-23T18-44-21Z

**Timestamp:** 2026-09-23T18:44:21Z
**Reason:** Hosted free-model aliases and OpenCode compaction foundation researched; hardcoded rotating-model limits rejected
**Host:** XNAi-Asus
**Agent:** build (channel: opencode)
**Phase:** phase-3

---

## Session Summary

Deep first-party research established the hosted OpenCode foundation and
rejected a recurring failure mode: treating rotating stealth aliases as stable
models with permanent context windows. The operator clarified that Big Pickle
can expose 1M behavior on Node 1 while Node 0 behaves as if constrained near
200K; both are valid observations of the same mutable alias. The session also
verified OpenCode 1.18.32's current agent, permission, and compaction schema,
and established that Google's Gemini 3.5–3.8 Flash families have genuine free
API tiers, with 3.8 Flash the current capable default.

## Key Decisions

1. **Never hardcode mutable stealth-alias capacity.** Big Pickle and Space Bunny
   are dynamic endpoints. Hardcoded context/output limits are invalid even when
   locally measured; pin the stable alias ID and refresh runtime metadata.
2. **Big Pickle is permanently authorized as free.** The absence of `-free` in
   its alias is irrelevant to its official $0 pricing.
3. **Space Bunny identity remains unknown.** It is an anonymous zero-retention
   stealth alias. It is not confirmed to be DeepSeek V4.1 Flash; similarity is
   not fingerprinting, and self-report is not evidence.
4. **Google 3.8 Flash is the first-principles free default.** Gemini 3.5, 3.6,
   3.7, and 3.8 Flash all have free API tiers, so choosing 3.5 without a
   measured reason was unjustified. Use 3.8 for current public research and 3.5
   Flash-Lite for high-volume utility work.
5. **Free privacy tiers are not one privacy class.** Space Bunny is zero
   retention; Big Pickle/MiMo/Ling/NVIDIA/Muse contributor free tiers carry
   collection/training caveats; Google free API data may improve Google products.
6. **Use adaptive v1 compaction.** Hardcode `auto: true` and intentional
   `prune: true`; omit mutable/model-specific `reserved`, `tail_turns`, and
   `preserve_recent_tokens` defaults.
7. **Schema beats historical templates.** Current agents use `prompt` with
   `{file:...}`; unknown keys become provider pass-through. Task permissions
   are last-match-wins, so broad deny must precede specific allows.
8. **Local model routing is deferred.** This session closes the hosted cloud
   foundation only; local-model work remains a later phase.

## Code Changes

- Added `docs/OPENCODE_FOUNDATION.md` as the authoritative hosted-free model,
  dynamic-alias, privacy, agent-schema, permission-ordering, and compaction guide.
- Updated `docs/ROADMAP.md` with queued item P3.3a.5 and explicit finish gates.
- Corrected active doctrine in `docs/HARDWARE.md`, `docs/ARCHITECTURE.md`,
  `docs/AGENT_RUNBOOK.md`, `docs/WANDERGROUND_SPEC.md`,
  `docs/NODE1_TO_NODE0_README.md`, and `docs/SYSTEM_GUIDE.md`.
- Replaced the runbook's obsolete master config template containing removed MCP
  fields, unauthorized agents, pass-through-only agent keys, and an invalid
  task allowlist.
- Added rotating-alias guidance to `docs/models/README.md`.
- Researched but did **not** mutate the active global OpenCode configuration;
  implementation is queued under P3.3a.5.
- Validation: `make test` 54/54 and `make docs` passed. `make lint` passes for
  the committed tree; unrelated untracked `scripts/embedding_server.py` has a
  bare `asyncio` import and was preserved byte-for-byte outside the committed
  lint scope.

## Blockers & Open Questions

- Native `question` tool was unavailable in this runtime; the operator's direct
  instructions supplied the current Decision/Pattern/Gnosis reflection.
- Space Bunny was released on 2026-09-23; no mature independent fingerprint or
  benchmark corpus exists yet.
- Node-specific live registry metadata can lag or diverge from the served alias;
  any capacity claim must carry node/date/evidence provenance.
- P3.3a.5 active config migration remains queued and requires an OpenCode restart
  after editing global config.
- Untracked `scripts/embedding_server.py` currently fails a full working-tree
  lint because it imports `asyncio`; it was not altered or committed in this
  research-only session.

## Next Session Priorities

1. Execute P3.3a.5: clean the global config without hardcoding rotating aliases.
2. Replace Humboldt's pass-through fields with `prompt: {file:...}`.
3. Correct task permission ordering and retain only authorized agents.
4. Remove unsupported active MCP keys and set `subagent_depth: 1`.
5. Apply adaptive v1 compaction with `prune: true`.
6. Run `opencode debug config`, provider registry refreshes, `make lint`,
   `make test`, and `make docs`; restart OpenCode and verify all hosted paths.
7. Run controlled Space Bunny vs Big Pickle vs Gemini 3.8 evaluations before
   permanent workload promotion.
8. Only after the hosted foundation, begin the local-model layer.

## Gnosis Gained

- **Dynamic alias doctrine:** an alias can be stable while its model and limits
  mutate. Stable routing ID ≠ stable model identity ≠ stable capacity.
- **Node divergence is evidence, not contradiction:** the same alias may expose
  1M on one node and 200K-like behavior on another; hardcoding either number is
  wrong.
- **Naming is not pricing:** Big Pickle is free despite lacking `-free`.
- **Privacy is a matrix:** zero-retention free, free-with-training, trial-logged,
  contributor-trained, and free-unpaid-service are distinct classes.
- **First-principles model choice:** when equal-cost models exist, prefer the
  latest generation absent contrary measurements; Gemini 3.8 supersedes an
  unjustified 3.5 default.
- **Schema validation prevents false confidence:** pass-through `options` can
  make invalid agent fields look accepted while failing to control behavior.
- **Last match wins:** task permission ordering is a mechanical security boundary.
- **Compaction should adapt to the selected model:** reserve and recent-tail
  defaults are safer than global constants when model capacity changes.
- **Do the research yourself:** provider names, suffixes, registry snapshots,
  and community guesses are not substitutes for first-party evidence and direct
  operator measurement.

---
*Prepared during full pre-compaction orchestration on 2026-09-23.*
