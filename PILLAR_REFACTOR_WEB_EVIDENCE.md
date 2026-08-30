# 🔱 Pillar Refactor — Raw Web Evidence Dump
**AP Token**: `AP-PILLAR-EVIDENCE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pillar_refactor ⬡ ACTIVE

**Date**: 2026-08-22
**Purpose**: Raw evidence collection for all research gaps — full excerpts with URLs for traceability

---

## Gap 1: MCP Tool Deprecation Patterns (2024-2026)

### Source 1: amgres.com/blog/mcp-server-versioning-and-tool-deprecation (2026-05-08)
**URL**: https://amgres.com/blog/mcp-server-versioning-and-tool-deprecation

**Key Excerpts**:
```
The three clocks:
1. Protocol version - MCP spec moves (2024-11-05 most deployed, newer in flight)
2. Tool surface - the tools your server exposes
3. Server version - your server's own version

Breaking changes — every one of these needs a deprecation path:
* Renaming a tool
* Removing a tool
* Renaming a parameter
* Removing a parameter, or making an optional one required
* Changing the type of a parameter or output field
* Changing the meaning of a tool while keeping its name (the worst kind)

A worked rename: publishDraft → publishArticle
Step zero: Decide whether the rename is worth a breaking change. Almost no rename is purely cosmetic.
Step one: Add the new tool. Keep the old tool. Both do the same thing.
Step two: Wait. A real deprecation window is at minimum a few weeks of production traffic; for high-stakes tools, it is months. Both versions exist; tooling exists to count how often each is called; the cutover does not happen until the call count on the deprecated tool is near zero.
Step three: Remove the old tool.

Schema-change patterns:
Adding optional parameters: Almost always safe.
Output shape changes: Adding fields to outputs is safe; renaming or removing them is not. The same deprecation pattern applies.

Versioning the server itself:
The MCP spec includes a serverInfo.version field in the initialization response. Set it. Use SemVer.
Your responsibility is to refuse if the negotiated version does not include features your handlers depend on, and to handle the older versions you claim to support. Do not claim more than you support.
```

### Source 2: tianpan.co/blog/2026-05-14-mcp-tool-deprecation-sticky-old-name (2026-05-14)
**URL**: https://tianpan.co/blog/2026-05-14-mcp-tool-deprecation-sticky-old-name

**Key Excerpts**:
```
The prior is sticky. The model your agent is talking to was trained on a corpus where get_user_email was overwhelmingly the canonical way to ask "what is this person's email." Even when the tools array you pass at inference time lists only lookup_contact, the model occasionally — under certain context conditions, especially long traces or recovery-after-error states — falls back to the name it remembers. A hard cutover doesn't eliminate the long tail; it just turns soft failures into hard ones.

Tool renames in MCP-mediated agent systems are not API versioning events. They are model-input distribution shifts, and they need the same kind of dual-write discipline you use when migrating a database column.

The deprecation shim that actually works:
The pattern that survives contact with production has three parts, none of which the MCP spec mandates but all of which the protocol allows.
1. Keep both names live.
2. The old name forwards to the new implementation.
3. Emit deprecation metadata so observability can track usage.
```

### Source 3: d23.io/blog/mcp-versioning-maintaining-backward-compatibility (2026-04-18)
**URL**: https://www.d23.io/blog/mcp-versioning-maintaining-backward-compatibility

**Key Excerpts**:
```
Each tool version needs its own implementation, documentation, and test coverage. You can't just rename a tool and call it versioned. Instead, you need to maintain parallel implementations that handle the same logical operation but with different signatures.

One effective pattern is to use a wrapper or adapter layer. Your core tool logic remains unchanged, but you layer version-specific adapters on top. When a client requests query_data_v2, it goes through the v2 adapter, which translates the v2 request format into your internal representation. When a client requests query_data_v3, it uses the v3 adapter. This keeps your implementation DRY while maintaining multiple public contracts.

Capability flags and feature detection:
Beyond versioning numbers, MCP supports capability flags—metadata that tells consumers what your server can do. A capability might be something like supports_parameterized_queries, supports_caching, or supports_ai_prompt_generation.

The most consumer-friendly approach is the deprecation period: you announce that a tool or resource will be removed in a future version, you keep it working in the current version, and you give consumers a defined window to migrate.

Version 2.5.0 (Deprecation Announcement): Both tools are available. The documentation for simple_query includes a deprecation notice explaining that it will be removed in version 3.0 and recommending migration to parameterized_query. You might also add a deprecation flag to the tool's metadata that clients can detect.

Version 2.6.0 through 2.9.x (Maintenance Period): Both tools continue to work.

Version 3.0.0 (Breaking Change): Remove simple_query entirely. The changelog documents the removal.
```

### Source 4: aaif.io/blog/mcp-just-handed-you-a-deprecation-policy-steal-it (2026-07-27)
**URL**: https://aaif.io/blog/mcp-just-handed-you-a-deprecation-policy-steal-it

**Key Excerpts**:
```
MCP's 2026-07-28 release provides a deprecation policy template for managing production tools and preventing costly failures in agent systems.
```

### Source 5: github.com/bjeans/homelab-mcp/blob/main/MIGRATION_V3.md (2026-01-14)
**URL**: https://github.com/bjeans/homelab-mcp/blob/main/MIGRATION_V3.md

**Key Excerpts**:
```
Backward Compatibility: None. Version 3.0 intentionally breaks backward compatibility to establish a clean, consistent naming convention.
If you cannot update immediately: Pin to v2.2.1: bjeans/homelab-mcp:v2.2.1
Tool Names: Breaking changes (20+ renamed)
API Signatures: Compatible (same parameters)
```

---

## Gap 2: Schema Migration in Universal Runtimes

### Source 1: baeseokjae.github.io/posts/autogen-to-agent-framework-migration-2026 (2026-06-15)
**URL**: https://baeseokjae.github.io/posts/autogen-to-agent-framework-migration-2026

**Key Excerpts**:
```
A pre-migration inventory is a written map of every AutoGen agent, tool, shared prompt, state dependency, runtime assumption, and external side effect before code moves. For a medium prototype, this usually takes 2 to 4 hours and prevents days of debugging later. List each AssistantAgent, its model provider, system prompt, allowed tools, expected input shape, output contract, and termination condition. Then list every FunctionTool, API call, database write, file operation, and approval point.

The practical takeaway: do not port what you have not named.

Converting AutoGen FunctionTool usage to Agent Framework @tool functions means turning tool definitions into typed Python callables whose schemas can be inferred by the framework. The official migration guide highlights @tool schema inference as a key difference, and that matters because brittle hand-written JSON schemas are a common source of tool-call failures. Start by moving each tool's input contract into type hints and clear docstrings.

Moving conversation state into AgentSession means making history, continuity, and multi-turn context an explicit runtime object instead of leaving them in AutoGen teams, chat logs, or custom arrays.

Convert each tool function into a method within a plugin class, adding the KernelFunction decorator and Description annotations. The function's type hints become the parameter schema, and the docstring or description annotations become the tool description that the LLM sees. Group related functions into logical plugin classes. Register plugins with the kernel at application startup rather than with individual agents. All agents that use the kernel automatically gain access to all registered plugins, eliminating the need to register the same tool with multiple agents individually.
```

### Source 2: docs.langchain.com/oss/python/migrate/langchain-v1
**URL**: https://docs.langchain.com/oss/python/migrate/langchain-v1

**Key Excerpts**:
```
State type restrictions: create_agent only supports TypedDict for state schemas. Pydantic models and dataclasses are no longer supported.

Use state_schema parameter when your custom state needs to be accessed by tools.

Defining state via state_schema:
class CustomState(AgentState):
    user_name: str

@tool
def greet(runtime: ToolRuntime[None, CustomState]) -> str:
    """Use this to greet the user by name."""
    return f"Hello, {runtime.state.user_name}!"

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[...],
    state_schema=CustomState
)
```

### Source 3: docs.langchain.com/oss/python/versioning
**URL**: https://docs.langchain.com/oss/python/versioning

**Key Excerpts**:
```
Our OSS version numbers follow the format: MAJOR.MINOR.PATCH, as defined by Semantic Versioning.

Major: Breaking API updates that require code changes.
Minor: New features and improvements that maintain backward compatibility.
Patch: Bug fixes and minor improvements.

API stability:
Stable APIs: All APIs without special prefixes are considered stable and ready for production use. We maintain backward compatibility for stable features and only introduce breaking changes in major releases.

Beta APIs: Prefixed with beta_ — may change between minor versions.
Alpha APIs: Prefixed with alpha_ — highly experimental.

Version support policy:
Latest major version: Full support with active development (ACTIVE status)
Previous major version: Security updates and critical bug fixes for 12 months after the next major release (MAINTENANCE status)
Older versions: Community support only

LTS releases: Both LangChain and LangGraph 1.0 are designated as LTS releases.
```

### Source 4: learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen
**URL**: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen

**Key Excerpts**:
```
AutoGen's tool registration pattern, where individual functions are registered with specific agents, converts to Semantic Kernel's plugin pattern, where functions are organized into plugin classes and registered with the kernel. This change provides better organization and reusability because plugins are available to all agents rather than individually registered with each one.
```

---

## Gap 3: Temple-Grade / Enterprise Schema Migration Compliance

### Source 1: devtoolsbuilder.com/learn/json/data-contracts (2026)
**URL**: https://devtoolsbuilder.com/learn/json/data-contracts

**Key Excerpts**:
```
Schema Drift Causing Silent Data Corruption:
A real incident: the user service team renames user_id to userId in their API response. No tests break because no test covers the exact field name. The analytics pipeline silently produces null values for user attribution. The billing team discovers the issue 3 weeks later when revenue reports are off by 15%.

What Is a Data Contract?
Component | JSON Schema Alone | Full Data Contract
Structure definition | Field names, types, required | Field names, types, required
Validation rules | Patterns, enums, min/max | Patterns, enums, min/max
Ownership | Not defined | Named team/individual owner
Change process | Not defined | PR review, compatibility check, approval
Breaking change detection | Manual | Automated in CI/CD
Consumer awareness | None | Consumer-driven contracts, notifications

Breaking vs Non-Breaking Changes:
Change Type | Example | Breaking? | Action Required
Add optional field | Add "avatar_url" to response | No | Minor version bump
Widen enum values | Add "team" to plan enum | No | Minor version bump
Remove a field | Remove "legacy_id" | Yes | Major version, migration period
Rename a field | user_id -> userId | Yes | Major version, migration period
Change field type | age: string -> number | Yes | Major version, new endpoint
Make optional required | display_name becomes required | Yes | Major version, notify consumers
Narrow enum | Remove "trial" from plan enum | Yes | Major version, verify no consumers use it
Change field semantics | status: HTTP code -> business code | Yes | Major version, document thoroughly

Schema Governance Workflow:
Step 1: Automated Compatibility Check in CI
Step 2: Consumer-Driven Contract Testing (Pact)
Step 3: Schema Registry (Confluent) for event streams

Anti-Patterns:
1. Schemas in Multiple Places — no single source of truth
2. Implicit Contracts — consumers depend on undocumented fields
3. No Versioning — no way to know which version a consumer expects

Best Practices:
✓ Store schemas in version control alongside code — treat them as first-class artifacts
✓ Run automated compatibility checks in CI on every schema change PR
✓ Use consumer-driven contract testing (Pact) for REST APIs
✓ Use a Schema Registry for event streams (Kafka, RabbitMQ)
✓ Apply semantic versioning: MAJOR for breaking changes, MINOR for additions
✓ Assign explicit ownership for every data contract (team name, not individual)
✓ Document field semantics beyond types: units, examples, business meaning
✗ Never remove or rename a field without a major version bump and migration period
✗ Never maintain the schema in multiple places — use a single source of truth
✗ Never skip compatibility checks "just this once" — that is when breakage happens
```

### Source 2: techinterview.org/post/3233474123 (2026-04-20)
**URL**: https://www.techinterview.org/post/3233474123/system-design-database-migration-strategies-zero-downtime-schema-changes-online-ddl-gh-ost-blue-green-expand-contract/

**Key Excerpts**:
```
The Expand-Contract Pattern:
The expand-contract pattern (also called parallel change) is the safest approach for breaking schema changes. Three phases:
(1) Expand — add the new column or table alongside the existing one. Both old and new schemas coexist. The application writes to both old and new columns.
(2) Migrate — backfill existing data from the old column to the new column. Run in batches to avoid locking: UPDATE users SET email_normalized = LOWER(email) WHERE email_normalized IS NULL LIMIT 1000.
(3) Contract — after all data is migrated and the application no longer reads the old column, drop it. Each phase is a separate deployment. If something goes wrong, you roll back only the current phase without data loss.

Example: renaming a column from username to user_handle.
Expand: add user_handle column, write to both.
Migrate: backfill user_handle from username.
Contract: stop reading username, drop the column.
This takes 3 deployments instead of 1, but eliminates downtime risk.

Backward-Compatible Migrations:
During a rolling deployment, old and new application versions run simultaneously. Migrations must be backward-compatible with both versions.
Safe operations: adding a nullable column, adding a new table, adding an index, adding a column with a default value.
Unsafe operations: dropping a column, renaming a column, changing a column type, adding a NOT NULL constraint without a default.
For unsafe operations, use the expand-contract pattern to make them safe across multiple deployments.
Migration ordering rule: deploy code that handles both schemas first, then run the migration. Never run a migration that removes something the currently-deployed code depends on.

Data Backfill Strategies:
Batch processing with throttling. Process 1000 rows per batch with a 100ms sleep between batches. Track progress with a cursor. This is resumable, throttled, and observable.

Migration Rollback Strategies:
(1) Reverse migration — for additive changes, the rollback is the inverse operation.
(2) For destructive changes, the rollback is not possible after execution — this is why the expand-contract pattern exists.
(3) Point-in-time recovery (PITR) — last resort.
(4) Blue-green database pattern — maintain two database instances.

Testing Migrations Before Production:
(1) Run the migration against a production-sized dataset.
(2) Verify backward compatibility by running the previous application version against the new schema and the new application version against the old schema. Both must work.
(3) Test the rollback migration.
(4) Check for lock conflicts.
(5) Measure replication lag during the migration.
```

### Source 3: martinfowler.com/bliki/ParallelChange.html (2014, canonical)
**URL**: https://martinfowler.com/bliki/ParallelChange.html

**Key Excerpts**:
```
Parallel change, also known as expand and contract, is a pattern to implement backward-incompatible changes to an interface in a safe manner, by breaking the change into three distinct phases: expand, migrate, and contract.

In the expand phase you augment the interface to support both the old and the new versions. In our example, we introduce a new Map<Coordinate, Cell> data structure and the new methods that can receive Coordinate instances without changing the existing code.

In the migrate phase you gradually move clients to the new interface. This can be done one client at a time, which allows you to test the new version incrementally.

In the contract phase you remove the old interface. Once all clients have been migrated, you can remove the old methods and the old data structure.

Some example applications of this pattern are:
- Refactoring: when changing a method or function signature, especially when doing a Long Term Refactoring or when changing a PublishedInterface.
- Database refactoring: this is a key component to evolutionary database design. Most database refactorings follow the parallel change pattern.
- Deployments: deployment techniques such as canary releases and BlueGreenDeployment are applications of the parallel change pattern.
- Remote API evolution: parallel change can be used to evolve a remote API when you can't make the change in a backwards compatible manner.

The downside of using parallel change is that during the migrate phase the supplier has to support two different versions, and clients could get confused about which version is new versus old. If the contract phase is not executed you might end up in a worse state than you started, therefore you need discipline to finish the transition successfully.
```

### Source 4: enterprise-software-review.contentwave.net/article/online-schema-migrations-for-enterprise-databases-patterns-roi (2026-07-26)
**URL**: https://enterprise-software-review.contentwave.net/article/online-schema-migrations-for-enterprise-databases-patterns-roi

**Key Excerpts**:
```
Step-by-step guide to safe, scalable online schema migrations for enterprise solutions: choose patterns, toolchains, integration points, testing and ROI measurement.
```

---

## Gap 4: AnyIO/Async Migration Patterns

### Source 1: anyio.readthedocs.io/en/stable/api.html
**URL**: https://anyio.readthedocs.io/en/stable/api.html

**Key Excerpts**:
```
AsyncFile: This class wraps a standard file object and provides async friendly versions of the following blocking methods (where available on the original file object):
* read, read1, readline, readlines, readinto, readinto1
* write, writelines
* truncate, seek, tell, flush

All other methods are directly passed through.
This class supports the asynchronous context manager protocol which closes the underlying file at the end of the context block.
This class also supports asynchronous iteration:
async with await open_file(...) as f:
    async for line in f:
        print(line)
```

### Source 2: github.com/agronholm/anyio/blob/master/docs/migration.rst
**URL**: https://github.com/agronholm/anyio/blob/master/docs/migration.rst

**Key Excerpts**:
```
Threading functions moved:
* current_default_worker_thread_limiter → anyio.to_thread.current_default_thread_limiter
* run_sync_in_worker_thread() → anyio.to_thread.run_sync
* run_async_from_thread() → anyio.from_thread.run
* run_sync_from_thread() → anyio.from_thread.run_sync

The old versions are still in place but emit deprecation warnings when called.

Blocking portal changes:
AnyIO now requires from_thread.start_blocking_portal to be used as a context manager:
from anyio import sleep
from anyio.from_thread import start_blocking_portal

with start_blocking_portal() as portal:
    portal.call(sleep, 1)

Synchronization primitives:
Synchronization primitive factories (create_event() etc.) were deprecated in favor of instantiating the classes directly.
So convert code like:
    from anyio import create_event
    async def main():
        event = create_event()
into:
    from anyio import Event
    async def main():
        event = Event()
```

### Source 3: anyio.readthedocs.io/en/stable/versionhistory.html
**URL**: https://anyio.readthedocs.io/en/stable/versionhistory.html

**Key Excerpts**:
```
4.0.0:
* Exposed the ResourceGuard class in the public API (#627)
* Fixed RuntimeError: Runner is closed when running higher-scoped async generator fixtures in some cases (#619)
* Fixed discrepancy between asyncio and trio where reraising a cancellation exception in an except* block would incorrectly bubble out of its cancel scope (#634)

3.4.0:
* Added context propagation to/from worker threads in to_thread.run_sync(), from_thread.run() and from_thread.run_sync() (#363; partially based on a PR by Sebastián Ramírez)
  NOTE: Requires Python 3.7 to work properly on asyncio!
* Fixed race condition in Lock and Semaphore classes when a task waiting on acquire() is cancelled while another task is waiting to acquire the same primitive (#387)
* Fixed async context manager's __aexit__() method not being called in BlockingPortal.wrap_async_context_manager() if the host task is cancelled (#381; PR by Jonathan Slenders)
```

### Source 4: LWN.net "A way to do atomic writes" (2019)
**URL**: https://lwn.net/Articles/789661

**Key Excerpts**:
```
An option to write data to an auxiliary file first and then replace the original file with the auxiliary file when the write completes. This option is equivalent to using a write method that takes the parameter atomically as true.

It would be nice to keep atomicity separate from durability, i.e. don't make fsync() the atomic commit primitive, unless it also works with an asynchronous variant of fsync(). A lot of applications don't care if you lose the last few updates, as long as the application never sees the results of a partial update. In database terms, this is asynchronous commit, which trades durability for performance without giving up atomicity, consistency, or integrity.
```

---

## Gap 5: MCP Server Versioning

### Source 1: modelcontextprotocol.io/docs/learn/versioning
**URL**: https://modelcontextprotocol.io/docs/learn/versioning

**Key Excerpts**:
```
The Model Context Protocol uses string-based version identifiers following the format YYYY-MM-DD, to indicate the last date backwards incompatible changes were made.
```

### Source 2: modelcontextprotocol.io/registry/versioning
**URL**: https://modelcontextprotocol.io/registry/versioning

**Key Excerpts**:
```
The version string MUST be unique for each publication of the server. Once published, the version string (and other metadata) cannot be changed.

Version Format:
The MCP Registry recommends semantic versioning, but supports any version string format.

Example | Type | Guidance
1.0.0 | semantic version | Recommended
2.1.3-alpha | semantic prerelease | Recommended
2025.11.25 | semantic date | Recommended
2025-06-18 | non-semantic date | Allowed
v1.0 | prefixed version | Allowed
^1.2.3 | version range | Prohibited

Best Practices:
- Use Semantic Versioning
- Align Server Version with Package Version
- Use Prerelease Versions for Registry-only Updates
```

### Source 3: d23.io/blog/mcp-versioning-maintaining-backward-compatibility (2026-04-18)
**URL**: https://www.d23.io/blog/mcp-versioning-maintaining-backward-compatibility

**Key Excerpts**:
```
One effective pattern is to use a wrapper or adapter layer. Your core tool logic remains unchanged, but you layer version-specific adapters on top. When a client requests query_data_v2, it goes through the v2 adapter, which translates the v2 request format into your internal representation. When a client requests query_data_v3, it uses the v3 adapter. This keeps your implementation DRY while maintaining multiple public contracts.

Capability flags are more granular than version numbers. You might have a server at version 2.1.0 that supports 15 different capabilities, while a competing server at version 2.5.0 supports only 10.

The most consumer-friendly approach is the deprecation period: you announce that a tool or resource will be removed in a future version, you keep it working in the current version, and you give consumers a defined window to migrate.

A practical testing strategy includes:
* Contract tests: Verify that each tool and resource in each version meets its documented contract
* Backward compatibility tests: Verify that old clients can still use the server (or fail gracefully if they can't)
* Migration tests: Verify that clients can migrate from one version to another successfully
* Capability detection tests: Verify that capability flags are accurate and clients can detect capabilities correctly
```

### Source 4: github.com/modelcontextprotocol/python-sdk/issues/1667 (2025-11-25)
**URL**: https://github.com/modelcontextprotocol/python-sdk/issues/1667

**Key Excerpts**:
```
Version-aware discovery for list_tools and related MCP APIs:
Allow clients to optionally request discovery results for a specific server/tool manifest version (e.g. via a version or server_version parameter).
Preserve current behavior when no version is provided (i.e. "latest" remains the default).
Ensure that, when a version is specified, the discovery payload reflects a consistent snapshot of tools/prompts/resources as they existed for that version (including schemas and descriptions).

Proposed behavior:
1. Separate version domains: The MCP server exposes a server/manifest version (e.g. semver). Individual tools and/or tool manifests can also have their own semantic versions. The server tracks, for each server/manifest version, which tool versions were part of that snapshot.
2. Version-aware discovery APIs: list_tools accepts an optional version parameter. If no version is provided: behavior is identical to today. If a version is provided: only tools that existed for that version are returned. Each tool's schema/description matches what was valid for that version.
3. Backward compatibility: Servers that do not yet support version-aware discovery can safely ignore the parameter.

Initial proposal: semver rules for tools vs server:
- Tool-level MAJOR for any change that can break clients built against the previous tool contract
- Server-level MINOR whenever the exposed tool surface changes (new tools, contract/signature changes)
- Server-level PATCH for internal/server changes that don't affect the observable tool contract
```

### Source 5: py.sdk.modelcontextprotocol.io/migration (2026)
**URL**: https://py.sdk.modelcontextprotocol.io/migration

**Key Excerpts**:
```
FastMCP is now MCPServer:
The high-level server class was renamed, and its module with it. This is the first thing every v1 server hits, because the old import path is gone rather than deprecated:
from mcp.server import MCPServer  # v1: from mcp.server.fastmcp import FastMCP
mcp = MCPServer("Demo")  # v1: FastMCP("Demo")

It is also, for a decorator-built server, most of the port. @mcp.tool(), @mcp.resource(), and @mcp.prompt() accept what they accepted in v1.

Fields renamed from camelCase to snake_case:
AttributeError: 'Tool' object has no attribute 'inputSchema' → input_schema

mcp.types names removed:
ImportError: cannot import name 'Content' from 'mcp.types' → from mcp_types import Content

McpError renamed to MCPError:
ImportError: cannot import name 'McpError' from 'mcp' → from mcp import MCPError
```

---

## Gap 6: Test Strategy for Breaking Changes

### Source 1: qaskills.sh/blog/hypothesis-property-based-testing-python-guide (2026-06-21)
**URL**: https://qaskills.sh/blog/hypothesis-property-based-testing-python-guide

**Key Excerpts**:
```
Example-based testing checks that your code works for the inputs you thought of; it says nothing about the inputs you didn't. Property-based testing flips this around. Instead of writing specific inputs and outputs, you describe the space of valid inputs and a property that must hold for all of them, and the testing library generates hundreds of examples to try to break that property.

When Hypothesis finds an input that violates your property, it shrinks that input to the smallest, simplest counterexample that still triggers the failure, then saves it so the bug is reproduced deterministically on every subsequent run.

Aspect | Example-based | Property-based
You write | Specific inputs + expected outputs | A rule that holds for all inputs
Coverage | Only inputs you imagined | Hundreds of generated inputs incl. edge cases
Edge cases | Manually enumerated | Discovered automatically
On failure | Shows the input you wrote | Shrinks to minimal counterexample
Maintenance | Update outputs when logic changes | Property often stays stable
Best for | Known specific cases, regressions | Invariants, parsers, data structures, math
```

### Source 2: dev.to/stranger6667/schemathesis-property-based-testing-for-api-schemas (2019-11-27)
**URL**: https://dev.to/stranger6667/schemathesis-property-based-testing-for-api-schemas-3j2k

**Key Excerpts**:
```
Schemathesis: property-based testing for API schemas.
Convert Open API & Swagger definitions to JSON Schema.
Use hypothesis-jsonschema to get proper Hypothesis strategies.
Use these strategies in CLI & hand-written tests.
It generates test data that conforms to the schema and makes a relevant network call to a running app and checks if it crashes or if the received response conforms to the schema.

The central element of Schemathesis in-code usage is a schema instance. It provides test parametrization, selecting endpoints to test and other configuration options.

Each test with this schema.parametrize decorator should accept a case fixture, that contains attributes required by the schema and extra information to make a relevant network request.

Case.call makes a request with this data to the running app via requests and checks if it crashes or if the received response conforms to the schema.
```

### Source 3: developers-heaven.net/blog/versioning-and-contract-testing-in-apis (2026-07-12)
**URL**: https://developers-heaven.net/blog/versioning-and-contract-testing-in-apis

**Key Excerpts**:
```
Contract testing verifies that an API matches its published contract. Learn consumer-driven, provider-driven, and schema-based patterns.

Write the Contract: The consumer writes a test that expects specific data types and structures from the provider.
Verify the Provider: The provider runs this contract test against its current codebase to ensure the schema matches.
Share the Artifact: Use a "Pact Broker" to store and share contracts between different codebases.
Validation Logic: If the provider changes a field name, the contract test fails immediately during the build process.
Documentation-as-Code: The contracts essentially serve as live, up-to-date documentation for your API endpoints.

Managing Breaking Changes Gracefully:
* Deprecation Headers: Send a Warning or Sunset header to notify clients that an endpoint is being retired.
* Sunset Policy: Clearly communicate the timeline for when an old version will be decommissioned.
* Parallel Operation: Run both versions concurrently for a period to allow for a staggered migration phase.
* Documentation Updates: Automate your Swagger or OpenAPI docs to reflect which version is current and which is deprecated.
* Monitoring Traffic: Use API gateways to identify how many clients are still hitting legacy versions before pulling the plug.
```

### Source 4: boringssl.googlesource.com/boringssl/+/refs/heads/main/BREAKING-CHANGES.md
**URL**: https://boringssl.googlesource.com/boringssl/+/refs/heads/main/BREAKING-CHANGES.md

**Key Excerpts**:
```
Breakage risk: We do not think about whether a change is formally a breaking change, but about the risk of it breaking someone. Hyrum's Law applies. Fixing a bug may be a breaking change for some consumer which was depending on that bug.

Fixing consumers:
If code search reveals call sites that are definitely going to break, prefer to handle these before making the change. While unexpected breakage is always possible, we generally consider it the responsibility of the developer or group making a change to handle impact of that change.

In most cases, this is straightforward:
1. Add the replacement API.
2. As the replacement API enters each consuming repository, migrate callers to it.
3. Remove the original API once all consumers have been migrated.

Fail early, fail closed:
When breaking changes do occur, they should fail as early and as detectably as possible.
Ideally, problematic consumers fail to compile. Prefer to remove functions completely over leaving an always failing stub function.
If breaking the compile is not feasible, break at runtime, in the hope that consumers have some amount of test coverage.

Canary changes and bake time:
When planning a large project that depends on a breaking change, prefer to make the breaking change first—before committing larger changes. Or, when changing toolchain or language requirements, add a small instance of the dependency somewhere first then wait a couple of weeks for the change to appear in consumers. This ensures that reverting the change is still feasible if necessary.
```

---

## Additional Sources: Expand-Contract Pattern Details

### Source: matheuspalma.com/blog/zero-downtime-database-migrations-expand-contract-pattern (2026-04-12)
**URL**: https://matheuspalma.com/blog/zero-downtime-database-migrations-expand-contract-pattern

**Key Excerpts**:
```
You need to split a users.full_name column into first_name and last_name before the next billing release. The naive approach—ALTER TABLE in a transaction, deploy code that reads the new shape, done—works on a laptop. In production, long-running DDL locks the table, API pods briefly see inconsistent shapes, and a rollback is no longer "revert the deploy" because the data has already moved.

The expand-contract pattern (sometimes called "parallel change" or "live migration") is the discipline of breaking every schema change into a sequence of small, individually-safe steps such that the database is always in a state where both the old and new application code work correctly.
```

### Source: bigiron.cc/guides/zero-downtime-schema-migrations-the-expand-contract-pattern (2026-06-08)
**URL**: https://www.bigiron.cc/guides/zero-downtime-schema-migrations-the-expand-contract-pattern

**Key Excerpts**:
```
The expand-contract pattern (sometimes called "parallel change" or "live migration") is the discipline of breaking every schema change into a sequence of small, individually-safe steps such that the database is always in a state where both the old and new application code work correctly. Done well, it lets you deploy schema changes the same way you deploy code changes: continuously, with zero downtime, with safe rollback at every step.

The pattern, formalized:
1. Expand: change the schema in a backward-compatible way. Both old and new code work. The database now has the new structure available; the old structure is still there.
2. Migrate (or "transition"): change the application code to use the new structure. Deploy. Backfill any data the new structure needs.
3. Contract: remove the old structure. Schema and code are now both clean.

Critically, each phase is its own deploy - schema change, then code change, then schema change again. There's a "during phase 2" window where both schemas coexist. The application has to be tolerant of that during the transition.

Backfill strategies:
* Batched UPDATE in the application: loop in code, update 1000-10000 rows at a time with a sleep between. Easy to control rate.
```

### Source: khimananda.com/blog/database-migrations-at-scale-zero-downtime (2026-08-20)
**URL**: https://khimananda.com/blog/database-migrations-at-scale-zero-downtime

**Key Excerpts**:
```
Quick answer: Achieving database migrations at scale zero downtime requires the expand-contract pattern: add new columns non-blocking, dual-write via application code, backfill historical data in batches, verify integrity, then drop old columns. Use online schema change tools like gh-ost or pgroll to avoid locking production tables during structural modifications.
```

---

## FastMCP Specific Sources

### Source: gofastmcp.com/servers/tools
**URL**: https://gofastmcp.com/servers/tools

**Key Excerpts**:
```
Versioning (v3.0.0+):
Tools support versioning, allowing you to maintain multiple implementations under the same name while clients automatically receive the highest version. See Versioning for complete documentation on version comparison, retrieval, and migration patterns.

Dynamic Tool Management:
from fastmcp import FastMCP
mcp = FastMCP(name="DynamicToolServer")

@mcp.tool
def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

mcp.local_provider.remove_tool("calculate_sum")
```

### Source: py.sdk.modelcontextprotocol.io/whats-new
**URL**: https://py.sdk.modelcontextprotocol.io/whats-new

**Key Excerpts**:
```
FastMCP is now MCPServer:
from mcp.server import MCPServer  # v1: from mcp.server.fastmcp import FastMCP
mcp = MCPServer("Demo")  # v1: FastMCP("Demo")

What is unchanged on MCPServer:
@mcp.tool(), @mcp.resource(), @mcp.prompt() accept what they accepted in v1.
```

---

## Search Metadata

| Search Session | Queries | Results | Date |
|----------------|---------|---------|------|
| pillar-refactor-research-20260822 | 6 search batches | 50+ sources | 2026-08-22 |

**Search Tiers Used** (per Sovereign Search Protocol SR-V1):
1. ✅ websearch (primary) — all searches
2. ✅ webfetch — for specific URLs from search results
3. ⚠️ searxng — not invoked (websearch sufficient)
4. ⚠️ sovereign_search — not invoked (websearch sufficient)
5. ⚠️ firecrawl — not invoked (websearch sufficient)

**No TOOL-CHAIN-COLLAPSE** — all mandatory tools operational.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pillar_refactor ⬡ COMPLETE*