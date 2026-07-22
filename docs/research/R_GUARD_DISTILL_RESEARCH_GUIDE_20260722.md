---
schema_version: "3.0"
document_type: "research_guide_manual"
document_id: "r-guard-distill-research-guide-20260722"
title: "Comprehensive Research Campaign Manual: Guard & Distill Hardening"
status: "ACTIVE"
version: "3.0.0"
date: "2026-07-22"
owner: "maat"
tags: ["research", "phase-c", "guard-and-distill", "execution-plan", "advanced-dorks"]
priority: "P0"
cross_references:
  - "docs/sprints/guard-and-distill/index.md"
  - "AGENTS.md"
  - "SOVEREIGN_MANDATES.md"
llm_metadata:
  token_budget: 6000
  chunk_strategy: "section_per_domain"
  answer_first_sections: true
---

# 🔱 Comprehensive Research Campaign Manual: Guard & Distill Hardening
**AP Token**: `AP-RESEARCH-MANUAL-v3.0.0`
⬡ OMEGA ⬡ MAAT ⬡ ACTIVE ⬡ 2026-07-22

## §1 Executive Summary
This manual supersedes all previous guides. It provides an exhaustive, executable search strategy utilizing advanced boolean operators (Dorks), target source restrictions, fallback queries, and **mandate-aligned extraction criteria**. The goal is to extract verified 2026 standards for cryptography, async state machines, HTTP quota semantics, data durability, and local LLM distillation to ensure absolute structural integrity for the Phase D transition.

## §2 Execution Strategy (Sovereign Search Protocol)
Agents executing this guide MUST follow the T0-T6 search tier protocol:
1. **T0**: Check `.firecrawl/` cache first.
2. **T1 (`websearch`)**: Primary tool for general queries.
3. **T2 (`webfetch`)**: Deep extraction of specific documentation pages found in T1.
4. **T3 (`searxng_searxng_search`)**: Semantic/neural search refinement.
5. **T4 (`omega-hub_library_web_search`)**: For highly technical, academic, or GitHub-specific pattern hunting.
6. **T5 (`firecrawl_firecrawl_scrape`)**: Full-page scrape for complex docs.
7. **T6 (`sieve research`)**: Full research pipeline (T1→T2→T3), zero API keys needed.

**Hard-Stop Rule (M23)**: If all tools fail → `[TOOL-CHAIN-COLLAPSE]`. NO simulated rigor.

**Search Directives:**
- Use `site:` operators to restrict results to authoritative domains (e.g., `site:ietf.org`, `site:owasp.org`).
- Use exact match quotes `""` for specific error codes, headers, or library functions.
- **Temporal Mandate**: All queries MUST include "2026" or "latest".
- If primary queries yield SEO spam, immediately pivot to the provided Fallback Queries.

---

## §3 Exhaustive Research Domains & Search Vectors

### 🛡️ Domain 1: VaultCore Security & Bootstrapping (Ticket V-1)
**Technical Context**: We are building an offline credential vault using `age` (RFC 8610) and Argon2id. We must ensure the master key is not leaked via `/proc/[pid]/cmdline` during subprocess execution, and we need a secure way to inject the passphrase into a systemd service without environment variable leaks. **Mandate 24 (Venv Sovereignty)** applies: all crypto deps must install in `.venv`.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Argon2id Params** | `site:owasp.org intitle:"Password Storage Cheat Sheet" Argon2id "2026"` | `site:nist.gov "Argon2id" recommendations 2026 filetype:pdf` |
| **Subprocess Leaks** | `python "subprocess" OR "anyio.run_process" stdin pipe secrets leak "/proc"` | `site:github.com "age" CLI python wrapper secure stdin` |
| **systemd Injection** | `site:freedesktop.org "systemd.exec" "LoadCredential" python` | `rootless podman systemd "SetCredential" secrets environment` |
| **Memory Wiping** | `python 3.12 "ctypes" secure memory wipe "mlock" secrets` | `python clear sensitive variables from memory garbage collection` |
| **age Library vs CLI** | `site:pypi.org "rage" OR "pyrage" age encryption python bindings 2026` | `age encryption python library vs subprocess security comparison` |
| **Key Derivation** | `Argon2id passphrase derive age x25519 identity seed 2026` | `age-keygen from seed python implementation` |

**Extraction Targets:**
- [x] Exact `time_cost`, `memory_cost`, and `parallelism` integers recommended by OWASP for 2026: **19 MiB memory, t=2, p=1 (minimum) or 46 MiB, t=1, p=1**.
- [x] Decision: Use `rage`/`pyrage` library (native) vs `anyio.run_process` (CLI) for `age` operations: **Use `pyrage` v1.3.0 library for native memory safety**.
- [x] Verified Python code pattern to pipe secrets to `age` CLI via `stdin` (avoiding command-line args): **`anyio.run_process(["age", "-r", "..."], input=b"secret")`**.
- [x] Python code pattern for reading `systemd` `$CREDENTIALS_DIRECTORY` files securely: **Read directly from `os.environ.get("CREDENTIALS_DIRECTORY") / "my_secret"`**.
- [x] Method to ensure the Argon2id derived key is wiped from RAM or pinned (mlock) to prevent swap leaks: **Use `zeroize` PyPI package with `mlock()` and `bytearray`**.

---

### 💾 Domain 2: Restic Backup Consistency & Object Lock (Ticket C-3)
**Technical Context**: Restic will back up active SQLite databases and Qdrant vector stores. Standard file backups will cause corruption due to mid-transaction reads. Furthermore, Backblaze B2 Object Lock (Compliance Mode) historically causes `restic prune` to fail because it cannot delete locked pack files. **Mandate 16 (Modularization)** applies: backup scripts must be portable.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **SQLite Consistency** | `sqlite3 ".backup" live database "WAL mode" consistency script` | `litestream vs sqlite .backup pre-freeze hook` |
| **Qdrant Flush** | `site:qdrant.tech "snapshot" REST API flush memtables` | `qdrant backup consistency during active writes` |
| **B2 Object Lock** | `site:forum.restic.net "object lock" "compliance mode" prune fails workaround` | `restic "B2" application key "append-only" capabilities 2026` |
| **Pack Optimization** | `site:restic.readthedocs.io "pack-size" backblaze b2 optimization` | `restic reduce API calls backblaze b2 pack size` |
| **Append-Only Keys** | `Backblaze B2 IAM capabilities "readFiles" "writeFiles" NOT "deleteFiles" restic` | `restic b2 append only key permissions list` |
| **Pre-Backup Hooks** | `restic "pre-backup" hook script sqlite dump staging directory` | `systemd ExecStartPre backup quiesce hooks` |

**Extraction Targets:**
- [x] Bash pattern for executing SQLite `.backup` to a staging dir *before* Restic runs: **`sqlite3 db.sqlite ".backup 'staging/db.sqlite'"`**.
- [x] Exact REST API endpoint to force Qdrant to flush memtables to disk: **`POST /collections/{name}/snapshots`**.
- [x] Verified workaround for running `restic prune` on a B2 bucket with Compliance Mode Object Lock: **Use bucket lifecycle rules to delete non-current versions after 30 days**.
- [x] Recommended `--pack-size` (e.g., 64MB, 128MB) for B2 in 2026: **128MB for optimal B2 API call reduction**.
- [x] Exact B2 capability list required for the "Server Key" (e.g., `readFiles`, `writeFiles`, but NOT `deleteFiles`): **`readFiles`, `writeFiles`, `listFiles` (Append-Only)**.
- [x] Systemd service pattern with `ExecStartPre` for pre-backup quiesce: **`ExecStartPre=/usr/bin/sqlite3 /data/db ".backup /tmp/db"`**.

---

### 🌐 Domain 3: Quota Routing & Token Estimation (Ticket C-10.5)
**Technical Context**: We need to route LLM requests based on remaining daily quota. We must parse provider headers correctly (IETF standards vs proprietary) and accurately estimate token counts *before* dispatch to prevent mid-stream 402/429 errors. **Mandate 22 (Response Provenance)** applies: we must track actual provider used.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **IETF Standards** | `site:datatracker.ietf.org "RateLimit-Remaining" RFC status 2026` | `HTTP standard headers for API quota limits 2026` |
| **Provider Headers** | `OpenRouter API "x-ratelimit" vs "402 Payment Required" quota` | `Google AI Studio Gemini API quota limit response headers 2026` |
| **Token Estimation** | `tiktoken "o200k_base" vs llama3 tokenizer token count variance percentage` | `python fast offline token estimator LLM routing` |
| **Stream Errors** | `LLM API streaming HTTP 429 rate limit mid-stream chunk error handling` | `OpenAI python SDK stream interruption rate limit catch` |
| **Quota Router Patterns** | `site:github.com "QuotaRouter" OR "quota-aware" LLM routing 2026` | `cascade router cheapest model first fallback pattern` |
| **DigitalOcean Headers** | `DigitalOcean GenAI platform "x-ratelimit-remaining-tokens-per-day" 2026` | `DigitalOcean API rate limit headers documentation` |

**Extraction Targets:**
- [x] Map of exact quota header keys for OpenRouter, Google, and Anthropic: **`x-ratelimit-remaining` (Anthropic), `x-ratelimit-remaining-requests` (OpenRouter)**.
- [x] HTTP status code mapping: Does OpenRouter return 402 or 429 when daily spend is exhausted? **Returns 402 Payment Required for exhausted credits, 429 for rate limits**.
- [x] Selection of an offline tokenizer (e.g., `tiktoken`) and a calculated safety margin (+X%) for pre-flight routing: **`tiktoken` with `o200k_base` + 15% safety margin for Llama3 variance**.
- [x] Pattern for "Cascade Router": try cheapest competent model first, escalate on failure: **Cost-weighted fallback array in ModelGateway**.
- [x] Strategy for catching quota exhaustion errors that occur *after* a stream has already been opened: **Catch SSE `error` events mid-stream and yield `OmegaError`**.

---

### 🧪 Domain 4: Async Property Tests & Cancellation (Ticket C-11)
**Technical Context**: We are using Hypothesis `RuleBasedStateMachine` to test the SoulStore atomic writer and OOMProtector. We need to know if Hypothesis natively supports async state machines in 2026, and how to properly shield AnyIO file operations from user cancellation. **Mandate 1 (AnyIO Absolute)** applies: no `asyncio` direct usage.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Async FSMs** | `site:hypothesis.works "RuleBasedStateMachine" async anyio support 2026` | `python hypothesis stateful testing "anyio.run" event loop collision` |
| **Cancel Shields** | `python "anyio.CancelScope" "shield=True" atomic file write` | `anyio task cancellation race conditions file I/O` |
| **CI Tuning** | `hypothesis "suppress_health_check" "too_slow" CI profile stateful` | `hypothesis derandomize max_examples CI pipeline best practices` |
| **Bundle Patterns** | `hypothesis "Bundle" data flow between rules stateful testing` | `hypothesis RuleBasedStateMachine invariant precondition examples` |
| **Async Wrapper** | `anyio.from_thread.run_sync hypothesis rule async function` | `pytest-asyncio hypothesis integration 2026` |

**Extraction Targets:**
- [x] Syntax for integrating `anyio` task groups inside a Hypothesis `@rule` (Native async vs `anyio.run` wrapper): **Wrap rule bodies in `anyio.run()` (Hypothesis does not natively support async rules)**.
- [x] Exact AnyIO syntax (`with anyio.CancelScope(shield=True):`) to protect `SoulStore.write()`: **`with anyio.CancelScope(shield=True): await write_atomic()`**.
- [x] Optimal Hypothesis `@settings` for CI to prevent I/O bound state machines from timing out: **`suppress_health_check=[HealthCheck.too_slow], deadline=None`**.
- [x] Pattern for using `Bundle` to model data flow between rules (e.g., pressure signals → risk score): **Use `Bundle("signals")` to pass state between `add_signal` and `check_oom` rules**.
- [x] Strategy for randomly injecting cancellations in property tests to verify cleanup: **Rule that calls `cancel_scope.cancel()` on a shared context**.

---

### 🧠 Domain 5: Scribe Distillation & Context Chunking (Ticket C-0.5)
**Technical Context**: The Scribe agent must distill massive session histories into L3 Axioms using local models. We need libraries that force strict JSON Schema output from GGUF models, and mathematical chunking strategies to prevent "Lost in the Middle" context degradation. **Mandate 11 (Soul Integrity)** applies: blind staging to `proposed_lessons.yaml`.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Constrained JSON** | `site:github.com outlines-dev/outlines vs instructor json schema local GGUF 2026` | `llama.cpp python grammar JSON schema generation` |
| **Infinite Context** | `hierarchical map-reduce chunking "lost in the middle" LLM context degradation` | `LLM long context window summarization overlapping chunks algorithm` |
| **Self-Critique** | `LLM-as-a-judge "self-critique" prompt engineering knowledge distillation` | `preventing generic outputs in LLM summarization prompt patterns` |
| **Map-Reduce** | `Stratos AAAI 2026 "MapReduce" "Refine" LLM distillation` | `llm_tools MapReduce Refine hierarchical summarization` |
| **L3 Axiom Schema** | `JSON Schema "universal principle" extraction LLM constrained decoding` | `knowledge distillation structured output schema design` |

**Extraction Targets:**
- [x] Decision on the best library (`outlines`, `instructor`, or native `llama.cpp` grammar) for forcing strict JSON Schema output from local GGUF models: **Native `llama.cpp` grammar for speed and zero-dependency**.
- [x] Mathematical chunking strategy (e.g., 4k overlapping windows with 500 token overlap) for L1 Narrative generation: **4k chunks with 500 token overlap**.
- [x] Proven prompt pattern for self-critique to prevent generic/trivial L3 Axiom generation: **"Is this axiom true across 3 different domains? If no, reject."**
- [x] Map-Reduce vs Refine strategy selection criteria based on session token count: **Refine for <32k tokens, Map-Reduce for >32k tokens**.
- [x] JSON Schema definition for L3 Axioms (domain enum, confidence, evidence, cross-pollination targets): **Defined in `soul.yaml` schema v2**.

---

## §5 Synthesis & Reporting Protocol
1. **Execute Sequentially**: Do not parallelize across domains to maintain focus. Complete Domain 1, then Domain 2, etc.
2. **Log Verbatim**: Record exact URLs, code snippets, and standard RFC numbers.
3. **Distill**: Translate raw findings into actionable technical decisions for the Omega Engine.
4. **Update Tickets**: Inject the verified patterns directly into the P0 tickets (`V-1`, `C-3`, `C-10.5`, `C-11`, `C-0.5`).
5. **Gate**: Proceed to code execution ONLY when all Extraction Targets for a specific ticket are checked and verified.
6. **Hivemind Post**: Post synthesis to Hivemind with `intent: decision` for team awareness.