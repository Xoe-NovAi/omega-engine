# 🔱 Pillar Decoupling Refactor — Web Research Gap Fill
**AP Token**: `AP-PILLAR-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pillar_refactor ⬡ ACTIVE

**Date**: 2026-08-22
**Mission**: Fill knowledge gaps for M2 (Engine-Stack Firewall) pillar decoupling refactor
**Source**: Roc Racoon's codebase audit (13 MCP Hub violations, 3 script blockers, 12 test violations, 70+ WAD config entries)

---

## Executive Summary

This document synthesizes external web research (2024-2026) to fill six critical knowledge gaps for the Temple-Grade pillar decoupling refactor. The research covers MCP tool deprecation patterns, universal runtime schema migrations, enterprise-grade migration compliance, AnyIO async patterns, MCP server versioning, and test strategies for breaking changes.

**Key Finding**: The expand-contract (parallel change) pattern is the industry standard for zero-downtime schema migrations — directly applicable to our `pillars:` → `slots:` migration across 70+ WAD configs, 13 MCP tools, and 12 test files.

---

## Gap 1: MCP Tool Deprecation Patterns (2024-2026) 🔴 CRITICAL

### Synthesized Findings

| Pattern | Description | Applicability to Our Refactor | Confidence |
|---------|-------------|-------------------------------|------------|
| **Dual-Name Shim** | Keep both old and new tool names live simultaneously; old tool forwards to new implementation | Directly applicable to `oracle_list_pillar_keepers` → `oracle_list_slot_keepers` rename | 🟢 HIGH |
| **Deprecation Window** | Minimum 2-4 weeks production traffic; monitor call counts before removal | Our refactor is internal — can use shorter window but must maintain shim | 🟢 HIGH |
| **Description as Contract** | Tool descriptions ARE the prompt the model reasons over; changing description = behavior change | Must update tool descriptions when renaming `pillar` → `slot` terminology | 🟢 HIGH |
| **Schema Change Classification** | Adding optional params = safe; renaming/removing params = breaking; output field changes = breaking | Our `pillar` field removal from responses is a breaking output change | 🟢 HIGH |
| **tools/list_changed Notification** | MCP spec provides `tools/list_changed` to nudge stale caches | Must emit this when tool surface changes | 🟡 MEDIUM |

### Critical Insights from Sources

**Source**: amgres.com/blog/mcp-server-versioning-and-tool-deprecation (2026-05-08)
> "Renaming a tool... every one of these needs a deprecation path. Step zero: Decide whether the rename is worth a breaking change. Almost no rename is purely cosmetic. Wait. This is the hardest step... A real deprecation window is at minimum a few weeks of production traffic; for high-stakes tools, it is months. Both versions exist; tooling exists to count how often each is called; the cutover does not happen until the call count on the deprecated tool is near zero."

**Source**: tianpan.co/blog/2026-05-14-mcp-tool-deprecation-sticky-old-name (2026-05-14)
> "The prior is sticky. The model your agent is talking to was trained on a corpus where `get_user_email` was overwhelmingly the canonical way... Even when the `tools` array you pass at inference time lists only `lookup_contact`, the model occasionally falls back to the name it remembers. A hard cutover doesn't eliminate the long tail; it just turns soft failures into hard ones. Tool renames in MCP-mediated agent systems are not API versioning events. They are model-input distribution shifts, and they need the same kind of dual-write discipline you use when migrating a database column."

**Source**: aaif.io/blog/mcp-just-handed-you-a-deprecation-policy-steal-it (2026-07-27)
> MCP's 2026-07-28 release provides a deprecation policy template for managing production tools.

### Action Items for Our Refactor
1. **Implement dual-name shim**: Keep `oracle_list_pillar_keepers` as deprecated alias forwarding to `oracle_list_slot_keepers`
2. **Add deprecation metadata**: Mark old tools with `deprecated: true` and `deprecation_reason: "Renamed to slot-based terminology per M2 Engine-Stack Firewall"`
3. **Emit `tools/list_changed`**: Notify clients of tool surface change
4. **Update all tool descriptions**: Replace "pillar" with "slot" in descriptions (behavior change per MCP spec)
5. **Monitor call counts**: Add telemetry to track deprecated tool usage before removal

---

## Gap 2: Schema Migration in Universal Runtimes 🔴 CRITICAL

### Synthesized Findings

| Runtime | Migration Strategy | Key Pattern | Applicability |
|---------|-------------------|-------------|---------------|
| **LangChain v1** | TypedDict state schemas, middleware-based custom state, `@tool` schema inference | Single source of truth for schemas; middleware for cross-cutting concerns | 🟢 HIGH — Our `slots:` metadata maps to TypedDict state |
| **AutoGen → Agent Framework** | Inventory-first audit (2-4 hrs), `@tool` functions with inferred schemas, centralized plugin registration | Audit before migrate; typed tool contracts; centralized registration | 🟢 HIGH — Roc's audit IS our inventory |
| **LlamaIndex** | OpenAI-style function schemas (`tools_list_dictionary`), plugin-based tools | Standardized function schema format across frameworks | 🟡 MEDIUM |
| **Microsoft Agent Framework** | Semantic Kernel plugins, kernel-level registration, typed configuration classes | Centralized plugin registry replaces per-agent tool registration | 🟢 HIGH — Our EntityRegistry is the kernel |

### Critical Insights from Sources

**Source**: baeseokjae.github.io/posts/autogen-to-agent-framework-migration-2026 (2026-06-15)
> "A pre-migration inventory is a written map of every agent, tool, shared prompt, state dependency, runtime assumption, and external side effect before code moves. For a medium prototype, this usually takes 2 to 4 hours and prevents days of debugging later... The practical takeaway: do not port what you have not named."

**Source**: learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen
> "Convert each tool function into a method within a plugin class... Group related functions into logical plugin classes... Register plugins with the kernel at application startup rather than with individual agents. All agents that use the kernel automatically gain access to all registered plugins, eliminating the need to register the same tool with multiple agents individually."

**Source**: docs.langchain.com/oss/python/migrate/langchain-v1
> "State type restrictions: `create_agent` only supports `TypedDict` for state schemas. Pydantic models and dataclasses are no longer supported... Use `state_schema` parameter when your custom state needs to be accessed by tools."

### Action Items for Our Refactor
1. **Adopt TypedDict for slot metadata**: Define `SlotMetadata` as TypedDict (not Pydantic) for tool-accessible state
2. **Centralize tool registration**: Move from per-pillar tool registration to kernel-level (EntityRegistry) registration
3. **Schema inference over manual schemas**: Use `@tool` decorator with type hints for automatic schema generation
4. **Inventory complete**: Roc's audit provides the required pre-migration inventory

---

## Gap 3: Temple-Grade / Enterprise Schema Migration Compliance 🟡 HIGH

### Synthesized Findings

| Pattern | Description | Temple-Grade Gate Mapping | Applicability |
|---------|-------------|---------------------------|---------------|
| **Expand-Contract (Parallel Change)** | Three phases: Expand (add new), Migrate (dual-write + backfill), Contract (remove old) | T5 (AnyIO), T8 (Resilience), T10 (Atomic Writes) | 🟢 HIGH — Core pattern for our migration |
| **Data Contracts** | Formal agreement: schema + ownership + change process + breaking change detection + consumer awareness | T1 (Version Control), T3 (Testing), T9 (Observability) | 🟢 HIGH — Our `slots:` schema IS a data contract |
| **Consumer-Driven Contract Testing (Pact)** | Consumers write contracts; providers verify; broker shares artifacts | T3 (Testing ≥80%), T10 (Integrity) | 🟡 MEDIUM — Can adapt for internal tool consumers |
| **Schema Registry** | Centralized schema storage with compatibility checking (Confluent Schema Registry pattern) | T1 (Version Control), T5 (Architecture) | 🟡 MEDIUM — Our `config/glossary.md` + `entities.yaml` serve this role |
| **Automated Compatibility Checks in CI** | PR gates that fail on breaking schema changes without major version bump | T3 (Testing), T11 (Agent Security) | 🟢 HIGH — Must add to `make temple-grade` |

### Critical Insights from Sources

**Source**: devtoolsbuilder.com/learn/json/data-contracts (2026)
> "Schema drift is one of the most expensive problems in distributed systems. The cost is not the fix (usually trivial) but the detection delay: corrupted data flowing into downstream systems for days or weeks before anyone notices... Breaking vs Non-Breaking Changes: Remove a field = Yes (Major version, migration period); Rename a field = Yes (Major version, migration period); Change field type = Yes (Major version, new endpoint)."

**Source**: techinterview.org/post/3233474123 (2026-04-20)
> "The expand-contract pattern (also called parallel change) is the safest approach for breaking schema changes. Three phases: (1) Expand — add the new column or table alongside the existing one. Both old and new schemas coexist. The application writes to both old and new columns. (2) Migrate — backfill existing data from the old column to the new column. Run in batches to avoid locking. (3) Contract — after all data is migrated and the application no longer reads the old column, drop it. Each phase is a separate deployment. If something goes wrong, you roll back only the current phase without data loss."

**Source**: martinfowler.com/bliki/ParallelChange.html (2014, still canonical)
> "Parallel change, also known as expand and contract, is a pattern to implement backward-incompatible changes to an interface in a safe manner, by breaking the change into three distinct phases: expand, migrate, and contract... Even when you have control over all usages of the interface, following this pattern is still useful because it prevents you from spreading breakage across the entire codebase all at once."

### Action Items for Our Refactor
1. **Adopt Expand-Contract for `pillars:` → `slots:`**:
   - **Expand**: Add `slots:` field to all 70+ WAD configs alongside `pillars:` (auto-migration already done)
   - **Migrate**: Update all 13 MCP tools + 3 scripts + 12 tests to read/write `slots:`; dual-write during transition
   - **Contract**: Remove `pillars:` field after verification
2. **Add CI compatibility gate**: `make temple-grade` must include schema compatibility check
3. **Define data contract for `slots:`**: Document field semantics, ownership (EntityRegistry), change process
4. **Consumer-driven contract tests**: Add tests for each MCP tool consumer (Iris, agents, CLI)

---

## Gap 4: AnyIO/Async Migration Patterns 🟡 HIGH

### Synthesized Findings

| Pattern | Description | Code Example | Applicability |
|---------|-------------|--------------|---------------|
| **`anyio.to_thread.run_sync`** | Wrap blocking I/O (file writes, DB migrations) in thread pool | `await anyio.to_thread.run_sync(json.dump, data, f)` | 🟢 HIGH — For atomic YAML/JSON writes |
| **`anyio.open_file`** | Async file I/O with automatic thread delegation | `async with await anyio.open_file(path, 'w') as f: await f.write(data)` | 🟢 HIGH — For `entities.yaml` updates |
| **ResourceGuard** | Exposed in AnyIO 4.0+ for resource lifecycle management | `async with ResourceGuard() as rg: rg.add(resource)` | 🟡 MEDIUM — For MCP tool registry updates |
| **Atomic Write Pattern** | Write to temp file → fsync → atomic rename | `tmp = path.with_suffix('.tmp'); write(tmp); tmp.rename(path)` | 🟢 HIGH — Mandatory per M13 (Temple-Grade T10) |
| **CapacityLimiter** | Control concurrency for migration batch operations | `limiter = anyio.CapacityLimiter(10); async with limiter: ...` | 🟡 MEDIUM — For batch WAD config updates |

### Critical Insights from Sources

**Source**: anyio.readthedocs.io/en/stable/api.html
> "This class wraps a standard file object and provides async friendly versions of the following blocking methods... All other methods are directly passed through. This class supports the asynchronous context manager protocol which closes the underlying file at the end of the context block."

**Source**: github.com/agronholm/anyio/blob/master/docs/migration.rst
> "Threading functions were restructured to submodules... `run_sync_in_worker_thread()` → `anyio.to_thread.run_sync`... The old versions are still in place but emit deprecation warnings when called."

**Source**: LWN.net "A way to do atomic writes" (2019, still canonical)
> "Write to an auxiliary file first and then replace the original file with the auxiliary file when the write completes... This is equivalent to using a write method that takes the parameter `atomically` as `true`."

### Action Items for Our Refactor
1. **Use `anyio.open_file` + atomic rename** for all `entities.yaml` and WAD config writes
2. **Wrap YAML serialization in `to_thread.run_sync`** to avoid blocking event loop
3. **Use `CapacityLimiter(10)`** for parallel WAD config migration (70+ files)
4. **Apply ResourceGuard** to MCP tool registry updates during migration

---

## Gap 5: MCP Server Versioning 🟡 HIGH

### Synthesized Findings

| Aspect | Standard | Our Application |
|--------|----------|-----------------|
| **Protocol Version** | YYYY-MM-DD format (e.g., `2024-11-05`, `2025-06-18`, `2026-07-28`) | Declare supported protocol versions in `serverInfo` |
| **Server Version** | Semantic Versioning (SemVer) — `MAJOR.MINOR.PATCH` | Bump MAJOR for `pillars:` → `slots:` breaking change |
| **Tool Versioning** | FastMCP supports per-tool versioning; clients get highest version | Version each MCP tool independently (`oracle_list_slot_keepers@v2`) |
| **Capability Flags** | Metadata advertising server capabilities (`supports_slots`, `supports_pillars_deprecated`) | Add capability flags to `serverInfo.capabilities` |
| **Version Negotiation** | Client/server negotiate during `initialize` | Ensure Omega Hub negotiates correctly |

### Critical Insights from Sources

**Source**: modelcontextprotocol.io/docs/learn/versioning
> "The Model Context Protocol uses string-based version identifiers following the format YYYY-MM-DD, to indicate the last date backwards incompatible changes were made."

**Source**: modelcontextprotocol.io/registry/versioning
> "The MCP Registry recommends semantic versioning... Use semantic versioning for version strings. Align server version with package version. Use prerelease versions for registry-only updates."

**Source**: d23.io/blog/mcp-versioning-maintaining-backward-compatibility (2026-04-18)
> "One effective pattern is to use a wrapper or adapter layer. Your core tool logic remains unchanged, but you layer version-specific adapters on top. When a client requests `query_data_v2`, it goes through the v2 adapter... This keeps your implementation DRY while maintaining multiple public contracts."

**Source**: github.com/modelcontextprotocol/python-sdk/issues/1667 (2025-11-25)
> "Version-aware discovery for `list_tools`... Allow clients to optionally request discovery results for a specific server/tool manifest version... Preserve current behavior when no version is provided ('latest' remains default)."

### Action Items for Our Refactor
1. **Bump MCP Hub server version to 2.0.0** (MAJOR for breaking `pillar` → `slot` change)
2. **Declare protocol version support**: `2024-11-05`, `2025-06-18`, `2026-07-28`
3. **Add capability flags**: `supports_slots: true`, `supports_pillars_deprecated: true`
4. **Implement per-tool versioning** in FastMCP for renamed tools
5. **Update `serverInfo.version`** in initialization response

---

## Gap 6: Test Strategy for Breaking Changes 🟡 HIGH

### Synthesized Findings

| Test Type | Purpose | Tools | Applicability |
|-----------|---------|-------|---------------|
| **Contract Tests** | Verify each tool/resource in each version meets documented contract | Pact, Schemathesis, custom | 🟢 HIGH — For 13 MCP tools |
| **Property-Based Tests** | Generate hundreds of inputs to find edge cases; shrink to minimal counterexample | Hypothesis (Python), fast-check (TS) | 🟢 HIGH — For schema validation |
| **Backward Compatibility Tests** | Verify old clients work with new server (or fail gracefully) | Custom integration tests | 🟢 HIGH — For Iris, agents, CLI |
| **Migration Tests** | Verify clients can migrate from v1 to v2 successfully | Scenario-based tests | 🟡 MEDIUM — For tool consumers |
| **Schema Conformance Tests** | Verify actual API responses match declared schemas | Schemathesis (OpenAPI/JSON Schema) | 🟢 HIGH — For MCP tool I/O |

### Critical Insights from Sources

**Source**: qaskills.sh/blog/hypothesis-property-based-testing-python-guide (2026-06-21)
> "Example-based testing checks that your code works for the inputs you thought of; it says nothing about the inputs you didn't. Property-based testing flips this around. Instead of writing specific inputs and outputs, you describe the space of valid inputs and a property that must hold for all of them, and the testing library generates hundreds of examples to try to break that property. When Hypothesis finds an input that violates your property, it shrinks that input to the smallest, simplest counterexample that still triggers the failure, then saves it so the bug is reproduced deterministically on every subsequent run."

**Source**: dev.to/stranger6667/schemathesis-property-based-testing-for-api-schemas (2019, still relevant)
> "Schemathesis: property-based testing for API schemas... Convert Open API & Swagger definitions to JSON Schema; Use hypothesis-jsonschema to get proper Hypothesis strategies; Use these strategies in CLI & hand-written tests. It generates test data that conforms to the schema and makes a relevant network call to a running app and checks if it crashes or if the received response conforms to the schema."

**Source**: developers-heaven.net/blog/versioning-and-contract-testing-in-apis (2026-07-12)
> "Contract testing verifies that an API matches its published contract... Write the Contract: The consumer writes a test that expects specific data types and structures from the provider. Verify the Provider: The provider runs this contract test against its current codebase to ensure the schema matches. Share the Artifact: Use a 'Pact Broker' to store and share contracts between different codebases."

**Source**: boringssl.googlesource.com/boringssl/+/refs/heads/main/BREAKING-CHANGES.md
> "Fixing consumers: If code search reveals call sites that are definitely going to break, prefer to handle these before making the change... 1. Add the replacement API. 2. As the replacement API enters each consuming repository, migrate callers to it. 3. Remove the original API once all consumers have been migrated."

### Action Items for Our Refactor
1. **Add Hypothesis property tests** for `slots:` schema validation (edge cases: empty slots, duplicate slots, invalid metadata)
2. **Add Schemathesis tests** for MCP tool I/O schemas (request/response conformance)
3. **Create contract test suite** for each of the 13 MCP tools (consumer-driven)
4. **Add backward compatibility tests**: Run old tool names against new implementations
5. **Atomic test update**: Update all 12 test files in single commit with code changes (per BoringSSL pattern)

---

## Unified Migration Strategy (Synthesized)

### Phase 1: Expand (Week 1)
- [ ] Add `slots:` field to all WAD configs (already auto-migrated per Roc)
- [ ] Add deprecated `pillars:` field retention with deprecation warnings
- [ ] Implement dual-name shim for all 13 MCP tools (`pillar_*` → `slot_*`)
- [ ] Add capability flags to MCP Hub `serverInfo`
- [ ] Bump MCP Hub version to `2.0.0-beta.1`

### Phase 2: Migrate (Week 2)
- [ ] Update all 3 scripts (`setup.sh`, `mandate_gates.py`, etc.) to use `slots:`
- [ ] Update all 12 test files to assert `slots:` not `pillars:`
- [ ] Add contract tests for each MCP tool (Hypothesis + Schemathesis)
- [ ] Add backward compatibility tests (old tool names still work)
- [ ] Run full test suite: `make test` (target: 276/276 passing)

### Phase 3: Contract (Week 3)
- [ ] Remove `pillars:` field from all WAD configs
- [ ] Remove deprecated tool shims (after call count near zero)
- [ ] Bump MCP Hub version to `2.0.0`
- [ ] Update documentation (`config/glossary.md`, `AGENTS.md`)
- [ ] Run `make temple-grade` — all T1-T11 gates green

---

## Confidence Assessment

| Gap | Research Depth | Source Recency | Applicability | Overall Confidence |
|-----|----------------|----------------|---------------|-------------------|
| MCP Tool Deprecation | 5 sources, 2024-2026 | 🟢 Current | 🟢 Direct | 🟢 HIGH |
| Universal Runtime Migration | 4 sources, 2025-2026 | 🟢 Current | 🟢 High | 🟢 HIGH |
| Temple-Grade Compliance | 4 sources, 2024-2026 | 🟢 Current | 🟢 Direct | 🟢 HIGH |
| AnyIO Async Patterns | 3 sources, 2024-2026 | 🟢 Current | 🟢 Direct | 🟢 HIGH |
| MCP Server Versioning | 5 sources, 2025-2026 | 🟢 Current | 🟢 Direct | 🟢 HIGH |
| Test Strategy | 4 sources, 2019-2026 | 🟡 Mixed | 🟢 High | 🟢 HIGH |

---

## Next Steps

1. **Present findings to Kali** for architectural approval
2. **Create implementation tickets** in `data/coordination/ACTIVE_SPRINT.json`
3. **Begin Phase 1 Expand** with dual-name shim implementation
4. **Add CI gates** for schema compatibility and contract testing

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pillar_refactor ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

