<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# SDP Knowledge Gap Research Report

**AP Token:** `AP-RESEARCHER-SDP-GAPS-20260809-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ longcat-2.0-free ⬡ opencode ⬡ trc_sdp_gaps ⬡ COMPLETE

**Date:** 2026-08-09
**Status:** ACTIVE — Bedrock evidence base for SDP implementation
**Mandate Bindings:** M7 (Local-First), M18 (Token Efficiency), M19 (Adversarial Alchemy), M22 (Provenance), M23 (Failure Integrity)
**Supersedes:** Nothing. **Extends:** `COGNITIVE_SCAFFOLDING_PROTOCOL.md`, `SDP_FORMAL_ROUTING_SPEC.md`, `SDP_IMPLEMENTATION_SPEC.md`, `SDP_FAILURE_MODE_ANALYSIS.md`

---

## 0. Executive Summary (L1)

Five gaps blocked SDP implementation. All five are now closed with evidence. The headline findings, in order of how much they change the design:

| # | Gap | Headline Finding | Design Impact |
|---|-----|------------------|---------------|
| 1 | Scaffold matrix | **Context window claims in `providers.yaml` are wrong for the two most important models.** Nemotron 3 Ultra is 260K as served (not 1M); Laguna S 2.1 is the genuine 1M scaffold and outperforms Nemotron on every agentic coding benchmark despite being 4.7× smaller. | Rebuild the matrix around *served* windows. Demote Nemotron 3 Ultra from "big scaffold" to "instruction-following specialist." |
| 2 | Attestation | Full cryptographic attestation is **overkill and unimplementable** here (it defends against a hostile gateway; our threat is a *lazy or confused* scaffold). The real threat is silent non-retrieval — "retrieval that never ran" — not forgery. | Ship **content-addressed evidence manifests** (SHA-256 of every artifact + a deterministic replay check). ~120 LOC. Reject LLM-judge groundedness for Phase 2 handoff. |
| 3 | Dialectic schema | Existing `finetune_*.jsonl` schema is a strict subset of what's needed. A **one-row-per-session envelope with a `turns[]` array** covers single, council, and ensemble modes without three schemas. | One schema, five modes, migration is additive (existing rows map to `mode:"single"`). |
| 4 | Ensemble routing | **Ensembles are net-negative on retrieval/factual tasks and positive only on reasoning tasks with genuinely heterogeneous models.** Voting captures 80–90% of debate's gain at 30–40% of cost. Single-agent with equal token budget beats multi-agent on multi-hop reasoning. | Ensemble is the **exception, not the default**. Gate it behind an explicit trigger list. Prefer parallel voting over debate rounds. Never ensemble Phase 1. |
| 5 | Local executor | Hard cliff at **~3B for structured output**. Llama 3.1 8B Q8 hits 95.7% schema compliance; Llama 3.2 3B collapses to 47.8–56.5% JSON parse. Our own qwen3-1.7b bench: quality 0.65, factuality 0.954, 45 tok/s, 1.03 GB peak. Constrained decoding fixes syntax but **imposes a "constraint tax" on semantic accuracy in sub-3B models**. | Qwen3-1.7B is a *classifier and gauge*, not an executor. Promote an 8B-class model for Phase 3 edits, or make edits deterministic (patch application, not patch authoring). |

**The single most important correction:** the SDP's Phase 3 assumption — "local models are mechanical executors" — is only safe if the *mechanism* is deterministic. A 1.7B model cannot reliably author a multi-file refactor. It can reliably *apply* a pre-authored, machine-checkable patch. Phase 2's output format must therefore change: the AGY model must emit **executable artifacts (unified diffs, exact commands)**, not prose instructions that a small model must interpret.

---

## 1. Scaffold Model Selection Matrix

### 1.1 The Context Window Correction (CRITICAL)

`config/providers.yaml` and `SDP_MODEL_AWARE_GAUGE_SPEC.md` both assert **Nemotron 3 Ultra = 1,000,000 tokens**. This is the *architectural* claim from NVIDIA's model card. The **served** window measured by Artificial Analysis is **260K**.

| Model | Claimed (our config) | Verified served | Source |
|---|---|---|---|
| Nemotron 3 Ultra 550B-A55B | 1,000,000 | **260,000** | Artificial Analysis model page (Aug 2026) |
| Nemotron 3 Ultra (NVIDIA card) | 1M (RULER-validated) | 1M *self-hosted only* | research.nvidia.com/labs/nemotron |
| Longcat 2.0 | 1,000,000 | 1M (release, Jun 2026) | longcatai.org/benchmarks |
| Laguna S 2.1 118B-A8B | not in config | **1,048,576** | poolside.ai blog, HF card (21 Jul 2026) |
| Nemotron 3 Super 120B-A12B | 1M / 262K | **262,144 on OpenRouter free** | our own model card notes the discrepancy |
| Laguna M.1 / XS.2 | 262,144 (config) | **131,072** | our own model card body contradicts its own frontmatter |

> **M23 finding:** `config/model_registry/models/cloud/laguna-m.1-free.yaml.md` has `context_window: 262144` in frontmatter and "128K context / 131,072" in the body. Two of our own SSOT files disagree. This must be reconciled before the Context Gauge ships, or the gauge will mis-fire (FM-02 class).

**Why this matters for SDP:** the gauge computes `tokens_to_compaction` from `context_window`. A 4× overstatement means the agent believes it has 700K of headroom when it has 40K. That is a guaranteed Scenario A "Redzone Race" (FM-09) — the exact failure the SDP was built to prevent.

### 1.2 Verified Benchmark Evidence

Agentic-coding benchmarks, all as of 21 Jul 2026, pass@1 averaged over 4 attempts (source: Poolside official card, cross-checked against Artificial Analysis and VentureBeat):

| Model | Params | Terminal-Bench 2.1 | SWE-Bench Multilingual | SWE-Bench Pro | SWE Atlas |
|---|---|---|---|---|---|
| **Laguna S 2.1** | 118B-A8B | 70.2% | **78.5%** (best) | 59.4% | **46.2%** (best) |
| **Longcat 2.0** | — | **70.8%** | 77.3% | 59.5% | — |
| Nemotron 3 Ultra | 550B-A55B | 56.4% | — | — | — |
| Nemotron 3 Super | 120B-A12B | 38.6% | — | — | — |
| Laguna XS 2.1 | 33B-A3B | 33.4% | — | — | — |
| DeepSeek-V4-Pro-Max | 1.6T-A49B | 64.0% | — | — | — |
| Kimi K3 | 2.8T-A50B | 88.3% | — | — | — |

Longcat 2.0 additional (official, Jun 2026): RWSearch 78.8, BrowseComp **79.9**, FORTE 73.2, MMLU 89.71, IFEval 89.65, MATH500 96.40, HumanEval+ 88.41.

Nemotron 3 Ultra profile (BenchLM, 7 Aug 2026): overall #155/216, score 44.4/100 — but **strongest category is Instruction Following at #4**, weakest is **Agentic at #121**. Artificial Analysis: Intelligence #20/101 (index 38), Speed **#11/101 at 119.4 tok/s**, price $0.60in/$2.75out.

> **The Adversary speaks:** Nemotron 3 Ultra's aggregate rank (#155) looks damning, but that number is built from only 19 of 381 displayable benchmark slots and is labeled "Estimated." Do not use the aggregate. Use the *category* rows — IF #4 and Agentic #121 — which tell a coherent and actionable story: **it obeys precisely and reasons adequately, but should not drive an agent loop.** That is exactly a scaffold profile, not an executor profile.

### 1.3 The Matrix: Model × Task Type

Task types per `SDP_FORMAL_ROUTING_SPEC.md` §1.1 (`architecture, compliance, refactoring, research, synthesis`). Scaffold role only — Phase 1.

| Task Type | Primary | Rationale (evidence) | Fallback | Avoid |
|---|---|---|---|---|
| **architecture** | **Longcat 2.0** | 1M verified served window; BrowseComp 79.9 + FORTE 73.2 = best at assembling wide, heterogeneous evidence. Architecture scaffolding is a breadth problem. | Laguna S 2.1 (1M) | Nemotron 3 Super (262K free cap truncates wide reads) |
| **compliance** | **Nemotron 3 Ultra** | Instruction Following **#4** — compliance scaffolding is literally "apply this checklist to these files without improvising." Its Agentic weakness is irrelevant when it makes few tool calls. | Longcat 2.0 (IFEval 89.65) | Laguna S 2.1 (overthinks straightforward problems — vendor-admitted) |
| **refactoring** | **Laguna S 2.1** | SWE-Bench Multilingual 78.5 (outright best), SWE Atlas 46.2 (codebase QnA — the exact "understand this repo" scaffold task). 1M window holds a whole subsystem. | Longcat 2.0 (SWE-Bench Pro 59.5) | Nemotron 3 Super (T-Bench 38.6) |
| **research** | **Longcat 2.0** | RWSearch 78.8 + BrowseComp 79.9 are search-agent benchmarks — no other candidate publishes these. Directly measures the scaffold's actual job. | DeepSeek V4 Flash (1M, MIT) | Laguna XS.2 (131K) |
| **synthesis** | **MiniMax M2.5** | Our model card: "exceptional for long-form synthesis." 204.8K is sufficient — synthesis scaffolding consumes a *distilled* corpus, not a raw one. | Trinity Large Thinking (262K, explicit thinking) | Nemotron 3 Ultra (260K served, but Agentic #121) |

**Selection constraints applied:** all primaries are free-tier or daily-refresh (per SDP Phase 1 definition); none are AGY weekly-pool models; all exceed 200K served context.

### 1.4 Edge Cases & Caveats

1. **Laguna S 2.1's vendor-admitted defects** (poolside.ai, 21 Jul 2026): "overfits to some third-party agent harnesses, **mangles nested JSON in tool calls**, and occasionally overthinks straightforward problems." → **Never use Laguna S 2.1 for a scaffold phase that must emit structured JSON to the next stage.** Use it for prose-context assembly; convert to JSON with a different model or deterministic code.
2. **OpenRouter free-tier truncation is the dominant real constraint.** Nemotron 3 Super is 1M on NVIDIA and 262K on OpenRouter free. Qwen3 Coder is 256K native / 1M YaRN / 262K on OpenRouter free. The gauge must key on `(model, provider)` — **not model alone.** This is a schema change to `models.yaml`.
3. **Daily quota reset is 00:00 UTC** for OpenRouter free tier (all our cloud model cards). Scaffold scheduling should prefer post-reset hours for large jobs.
4. **Message count, not just token count, drives OpenCode compaction** (per `COGNITIVE_SCAFFOLDING_PROTOCOL.md` §2 rule 1). A high-benchmark model that makes many tool calls is a *worse* scaffold than a mediocre one that makes few. This is why Nemotron 3 Ultra's Agentic #121 is tolerable — we *want* low agency in Phase 1.
5. **Speed matters more than intelligence in Phase 1.** Nemotron 3 Ultra at 119.4 tok/s (#11/101) is a genuine scaffold advantage; scaffolding is throughput-bound, not quality-bound.

### 1.5 Actionable Config Changes

```yaml
# config/models.yaml — REQUIRED schema extension
# Context window must be keyed by (model, provider), not model alone.
models:
  nemotron-3-ultra:
    providers:
      opencode-zen:   { context_window: 260000,  verified: "artificialanalysis-2026-08" }
      self-hosted:    { context_window: 1000000, verified: "nvidia-ruler-2026-06" }
    tier: 3
    task_affinity: [compliance]        # IF #4
    task_antiaffinity: [refactoring]   # Agentic #121
    tokens_per_sec: 119.4
  laguna-s-2.1:
    providers:
      openrouter:     { context_window: 1048576, verified: "poolside-2026-07-21" }
    tier: 4
    task_affinity: [refactoring, architecture]
    emits_reliable_json: false         # vendor-admitted nested-JSON defect
  longcat-2.0:
    providers:
      opencode-zen:   { context_window: 1000000, verified: "longcatai-2026-06" }
    tier: 4
    task_affinity: [research, architecture]
```

**Immediate M23 remediation:** reconcile `laguna-m.1-free.yaml.md` frontmatter (262144) against its body (131072) before the gauge ships.

---

## 2. Context Attestation Protocol

### 2.1 Threat Model — What Can Actually Go Wrong

The mission brief framed the risk as "Scaffold could fabricate, misread, or inject bias." The literature says the *dominant* production failure is subtler and worse.

Giskard's 2026 production review states it plainly:

> "An LLM judge can score an answer as 'grounded' while the retrieval trace is empty. Invented citations pass judges surprisingly often when nobody inspects `sources`, `context`, or `tool_calls`... Tools that treat hallucination detection as answer-only scoring will miss agentic failures where the final string looks fine but **the database was never queried**."

That is the SDP's precise exposure. Phase 2 receives a beautifully-written context document. It has no way to know whether Phase 1 actually read the files.

**Threat enumeration, ranked by likelihood × impact:**

| ID | Threat | Likelihood | Impact | Detectable by |
|---|---|---|---|---|
| **T1** | **Silent non-retrieval** — scaffold answers from parametric memory, never reads the file | **HIGH** | **CRITICAL** | Deterministic check only (was the tool called?) |
| **T2** | **Staleness** — file read, then changed before Phase 2 consumes context | MEDIUM | HIGH | Content hash comparison |
| **T3** | **Partial read** — scaffold reads 200 of 2000 lines, presents as complete | HIGH | HIGH | Byte-range + size manifest |
| **T4** | **Paraphrase drift** — scaffold summarizes and loses the decisive detail | HIGH | MEDIUM | Verbatim quote requirement |
| **T5** | **Invention** — scaffold fabricates a file path, function name, or line | MEDIUM | CRITICAL | Path existence + hash check |
| **T6** | **Scope expansion** — scaffold extrapolates beyond evidence (Openlayer taxonomy) | MEDIUM | MEDIUM | Claim-to-source binding |
| **T7** | **Contradiction** — scaffold states the opposite of source | LOW | CRITICAL | Groundedness scoring |
| **T8** | Hostile gateway substitutes model/route | VERY LOW | HIGH | Cryptographic attestation (out of scope) |

Openlayer's Feb 2026 groundedness taxonomy maps to T4–T7 exactly: *invention, contradiction, partial hallucination, scope expansion*. Note their warning: **"Partial hallucination blends real and invented content... These mixed outputs pass casual review because most content appears correct."**

### 2.2 What NOT to Build

The 2026 literature offers a fully cryptographic answer — arXiv:2606.22560, *Evidence-Bound Gateway-Path Provenance for Third-Party LLM Inference* (Wang & Tian, 21 Jun 2026) — with AEAD, sequence checks, signed stream evidence, and attested evidence keys. It is rigorous and it is **the wrong tool for us**.

Its own threat table concedes the boundary:

| Threat | Covered by that paper? |
|---|---|
| Gateway route/model substitution | **Yes** |
| Gateway stream tampering | **Yes** |
| **RAG corpus, webpage, tool, or model is poisoned** | **No** |
| **LLM provider returns malicious text** | **No** |

Every threat we actually face (T1–T7) falls in its **uncovered** column. It defends the *transport*; our risk is in the *content*. **Rejected — with the note that if we ever route through an untrusted aggregator, T8 becomes live and this paper becomes the reference.**

Equally rejected: **LLM-as-judge groundedness as the Phase 2 gate.** It reaches only ~80% agreement with humans (Openlayer/Encord), costs an inference call, and — per Giskard — *scores empty retrieval as grounded*. It cannot detect T1, our highest-ranked threat. It is acceptable as advisory telemetry; it is unacceptable as a gate.

> **The Architect's ruling:** Giskard documents the correct ordering — **"deterministic retrieval checks (`FnCheck`) before `Groundedness` judges."** We adopt that ordering as law. Deterministic first. Judges never alone.

### 2.3 The Protocol: Content-Addressed Evidence Manifest (CAEM)

**Design principle:** the scaffold cannot be trusted to *report* what it read, but the *harness* can record it. Attestation is produced by the tool layer, not by the model.

**Trust anchor:** the MCP tool wrapper. Every `read`, `grep`, `bash`, and `webfetch` call is intercepted and hashed at the point of execution. The model never writes the manifest and cannot forge it.

#### 2.3.1 Manifest Schema

```json
{
  "manifest_version": "1.0",
  "manifest_id": "caem_20260809_204500_a1b2c3",
  "session_id": "ses_...",
  "scaffold_model": "longcat-2.0-free",
  "scaffold_provider": "opencode-zen",
  "created_at": "2026-08-09T20:45:00.000Z",
  "closed_at": "2026-08-09T21:10:32.000Z",
  "evidence": [
    {
      "ref": "E1",
      "kind": "file",
      "uri": "src/omega/oracle/model_gateway.py",
      "sha256": "9f2b...c41d",
      "bytes_total": 48213,
      "bytes_read": 48213,
      "read_complete": true,
      "lines_total": 1204,
      "line_range": [1, 1204],
      "mtime": "2026-08-08T14:22:10Z",
      "tool_call_id": "prt_...",
      "ts": "2026-08-09T20:45:12.000Z"
    },
    {
      "ref": "E2",
      "kind": "command",
      "uri": "bash:make test",
      "argv_sha256": "3d81...9a02",
      "exit_code": 0,
      "stdout_sha256": "77ab...10ff",
      "stdout_bytes": 8123,
      "stdout_excerpt": "349 passed, 99 skipped",
      "ts": "2026-08-09T20:47:03.000Z"
    },
    {
      "ref": "E3",
      "kind": "web",
      "uri": "https://poolside.ai/blog/introducing-laguna-s-2-1",
      "content_sha256": "5c19...ee73",
      "fetched_at": "2026-08-09T20:52:44.000Z",
      "http_status": 200
    }
  ],
  "coverage": {
    "files_referenced_in_context": 12,
    "files_in_manifest": 12,
    "unbacked_references": [],
    "partial_reads": 0
  },
  "attestation": {
    "manifest_sha256": "e0d4...77b1",
    "replay_verified": true,
    "verified_at": "2026-08-09T21:10:35.000Z",
    "verifier": "deterministic",
    "drift": []
  }
}
```

**Storage:** `data/coordination/attestation/caem_{session_id}_{ts}.json` (atomic `.tmp` → `fsync` → rename, per FM-04).

#### 2.3.2 The Four Checks (all deterministic, zero inference)

| Check | Detects | Implementation | Failure action |
|---|---|---|---|
| **C-A: Existence** | T5 (invention) | Every `uri` in `evidence[]` must resolve on disk / have returned HTTP 200 | HARD FAIL — manifest invalid |
| **C-B: Freshness** | T2 (staleness) | Re-hash every `kind:"file"` at manifest close; compare to recorded `sha256` | HARD FAIL if drift, list changed files |
| **C-C: Completeness** | T3 (partial read) | `bytes_read == bytes_total` → `read_complete: true`. Any `false` is surfaced. | WARN + flag to Phase 2 |
| **C-D: Coverage** | T1 (silent non-retrieval) | Regex-extract every `path/like/this.py` from the context document; every extracted path must appear in `evidence[]` | HARD FAIL — list `unbacked_references` |

**C-D is the load-bearing check.** It is the only one that catches T1, and it is pure string matching — no model, no judge, no cost.

#### 2.3.3 What Phase 2 Actually Receives

The AGY model receives a **prepended attestation header**, budget-capped at <400 tokens (per M18 and the gauge injection precedent of <200 chars):

```
[CONTEXT ATTESTATION — caem_20260809_204500_a1b2c3]
Scaffold: longcat-2.0-free @ opencode-zen | 12 files, 3 commands, 1 web source
Integrity: VERIFIED (12/12 files hash-stable, 0 partial reads, 0 unbacked references)
Coverage: 12/12 referenced paths backed by evidence
Verbatim-quote requirement: ENFORCED for E1, E4, E7
Caveats: none
→ You may reason over this context as attested. Any claim you make about a file
   not in the evidence list is unsupported; flag it rather than assert it.
```

Degraded variant, when checks fail:

```
[CONTEXT ATTESTATION — caem_... ]
Integrity: DEGRADED
  - UNBACKED (C-D): context references `src/omega/rag/router.py` — never read
  - PARTIAL (C-C): `model_gateway.py` read 400/1204 lines
  - DRIFT (C-B): `providers.yaml` changed after read (sha mismatch)
→ Treat the three items above as UNVERIFIED. Do not produce a plan that
   depends on them. Request re-scaffold or scope down.
```

This is the entire trust mechanism: **the frontier model is told precisely what it may and may not rely on**, in a header it cannot be talked out of, produced by code the scaffold cannot reach.

### 2.4 Anti-Paraphrase: The Verbatim Anchor

Deterministic checks cannot catch T4 (paraphrase drift) or T7 (contradiction) — those need the source text. Mitigation without inference:

**Rule:** For any evidence item the scaffold *characterizes* rather than *reproduces*, the scaffold must emit at least one verbatim quote ≥40 chars, tagged `[E{n}:L{start}-{end}]`. The harness then does an exact substring match of that quote against the hashed source.

- Match → quote is genuine, characterization has an anchor.
- No match → **HARD FAIL**, `fabricated_quote` event.

This is `grep -F`. It costs nothing and it catches the single most dangerous class: confident, plausible, wrong.

### 2.5 Integration Points

| Where | Change | Effort |
|---|---|---|
| MCP tool wrapper (`src/omega/hub/tools.py`) | Intercept read/grep/bash/webfetch; append evidence rows | ~60 LOC |
| New `src/omega/oracle/attestation.py` | `CAEM` dataclass, C-A..C-D verifiers, atomic writer | ~120 LOC |
| `ModelGateway.generate()` middleware | Prepend attestation header on Phase-2 (AGY) calls only | ~20 LOC |
| `metrics_db.py` | New `attestation_events` table (mirrors `vault_audit` pattern) | ~15 LOC |
| `SDP_FAILURE_MODE_ANALYSIS.md` | Add FM-11 (unbacked reference), FM-12 (fabricated quote), FM-13 (hash drift) | doc |

**Total: ~215 LOC, zero inference cost, zero external dependency.** Contrast with cryptographic attestation (weeks, new infra) or LLM-judge gating (an inference call per handoff, 80% accuracy, blind to T1).

### 2.6 Deliberately Deferred

- **Cryptographic signing** of the manifest — only needed if the manifest crosses a trust boundary. Today it doesn't; it stays on one disk. Revisit if SDP goes multi-machine.
- **Groundedness scoring** (Giskard OSS `Groundedness`, Patronus Lynx, Galileo Chunk Attribution) — worth adding as **advisory telemetry** in Phase 2+ to catch T6/T7, logged and never gating. Openlayer's guidance: threshold >0.85 for critical domains.
- **RAG triad metrics** (context relevance / groundedness / answer relevance) — a natural later addition to the dialectic log for offline analysis.

---

## 3. Dialectic Session Schema

### 3.1 Design Constraints

The schema must capture four distinct interaction shapes with **one** structure:

| Mode | Shape | Example |
|---|---|---|
| `single` | 1 model, 1 turn | Ordinary `talk()` call |
| `sequential` | Model A → Model B reads A's output → refines | The SDP's core pattern (M19 sequential dialectic) |
| `council` | N models in parallel, then 1 synthesizer | MaKaLi (Kali + Ma'at + Lilith) |
| `ensemble` | N models independently on same input, then aggregate | Voting for high-stakes routing |
| `pipeline` | Phase 1 → Phase 2 → Phase 3 with role changes | Full SDP run |

**Existing schema** (`data/datasets/finetune_*.jsonl`) is:

```json
{"trace_id","session_id","timestamp","messages":[...],"metadata":{"entity","model","backend","confidence","latency_ms","rating"}}
```

This is a strict subset — it is exactly `mode:"single"` with one turn. **Migration is therefore additive, not breaking.**

### 3.2 The Schema — One Row Per Session

Each line of `dialectic_sessions.jsonl` is one complete session. Rationale: a dialectic is only meaningful as a whole (who reviewed whom, who changed their mind), and one-row-per-turn would require joins to reconstruct — hostile to both `jq` and training-data loaders.

```jsonc
{
  // ── IDENTITY ─────────────────────────────────────────────
  "schema_version": "1.0",
  "dialectic_id": "dlg_20260809_204500_a1b2c3",
  "session_id": "ses_...",              // OpenCode session (joins to opencode.db)
  "trace_id": "trc_...",                // joins to metrics_db.performance
  "parent_dialectic_id": null,          // for nested/recursive dialectics
  "created_at": "2026-08-09T20:45:00Z",
  "closed_at": "2026-08-09T21:12:00Z",

  // ── CLASSIFICATION ───────────────────────────────────────
  "mode": "sequential",                 // single|sequential|council|ensemble|pipeline
  "problem_type": "architecture",       // matches SDP_FORMAL_ROUTING_SPEC §1.1
  "sdp_phase": "synthesize",            // scaffold|synthesize|execute|null
  "problem_statement": "Should the Context Gauge key on model or (model,provider)?",
  "tags": ["sdp", "context-gauge", "M23"],

  // ── PROVENANCE (M22) ─────────────────────────────────────
  "attestation": {
    "manifest_id": "caem_20260809_204500_a1b2c3",
    "integrity": "VERIFIED",            // VERIFIED|DEGRADED|ABSENT
    "unbacked_references": 0
  },

  // ── THE DIALECTIC ────────────────────────────────────────
  "turns": [
    {
      "turn": 1,
      "role": "proposer",               // proposer|critic|synthesizer|executor|verifier
      "entity": "researcher",
      "model": "longcat-2.0-free",
      "provider": "opencode-zen",
      "is_cloud": true,
      "is_agy": false,
      "account_id": null,
      "reviews_turns": [],              // ← THE KEY FIELD: which turns this turn read
      "input_tokens": 48200,
      "output_tokens": 3100,
      "latency_ms": 18400,
      "cost_usd": 0.0,
      "position": "Key on model alone; provider variance is noise.",
      "reasoning_summary": "Simpler schema, fewer config permutations.",
      "confidence": 0.62,
      "artifacts": ["docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md"],
      "content_ref": "prt_...",         // pointer to full text; body NOT inlined
      "content_sha256": "aa19...4f2b"
    },
    {
      "turn": 2,
      "role": "critic",
      "entity": "researcher",
      "model": "gemini-3.1-pro",
      "provider": "antigravity",
      "is_cloud": true,
      "is_agy": true,
      "account_id": "account-1",
      "reviews_turns": [1],             // ← Model B explicitly reviewed turn 1
      "input_tokens": 51300,
      "output_tokens": 4200,
      "latency_ms": 31000,
      "cost_usd": 0.0,
      "position": "Key on (model,provider). OpenRouter truncates Nemotron 1M→262K.",
      "reasoning_summary": "Counter-example from providers.yaml free-tier caps.",
      "confidence": 0.94,
      "critique": {
        "target_turn": 1,
        "verdict": "refuted",           // agreed|refined|refuted|orthogonal
        "grounds": ["factual_error", "missing_evidence"],
        "specific_objection": "Nemotron 3 Super is 1M on NVIDIA, 262K on OpenRouter free — same model id, 4x window delta."
      },
      "content_ref": "prt_...",
      "content_sha256": "c73d...91a0"
    }
  ],

  // ── OUTCOME ──────────────────────────────────────────────
  "resolution": {
    "converged": true,
    "rounds": 2,
    "final_position": "Key on (model, provider) tuple.",
    "decided_by": "turn_2",
    "dissent": [],                      // turns whose position was not adopted
    "position_changes": [
      {"turn": 1, "changed_by": 2, "from": "model-only", "to": "model+provider"}
    ],
    "value_added_by_dialectic": true,   // ← did turn 2+ change the outcome?
    "would_single_model_suffice": false // ← THE TRAINING LABEL
  },

  // ── ECONOMICS ────────────────────────────────────────────
  "economics": {
    "total_input_tokens": 99500,
    "total_output_tokens": 7300,
    "total_cost_usd": 0.0,
    "agy_pool_consumed": {"account-1": 55500},
    "wall_clock_ms": 49400,
    "single_model_baseline_tokens": 51300,   // cost had we used only the best model
    "ensemble_overhead_ratio": 2.08
  },

  // ── HUMAN SIGNAL (sparse, high value) ────────────────────
  "human_feedback": {
    "rating": null,                     // -1|0|1
    "preferred_turn": null,
    "notes": null
  }
}
```

### 3.3 Field-by-Field Rationale

| Field | Why it exists | What it trains |
|---|---|---|
| `mode` | Distinguishes the five shapes without five schemas | Router: which mode for which problem |
| `turns[].reviews_turns` | **The field that makes this a dialectic log** and not a chat log. Encodes the DAG of who-read-whom. | Critic model: learns the review relation |
| `turns[].role` | Separates proposer from critic from synthesizer | Role-conditioned fine-tuning |
| `turns[].critique.verdict` | 4-way label (agreed/refined/refuted/orthogonal) | Critic model: primary supervision label |
| `turns[].confidence` | Self-reported, pre-outcome | Calibration analysis: is confidence predictive? |
| `resolution.value_added_by_dialectic` | Boolean: did turn 2+ change anything? | **Ensemble router: the exact target variable** |
| `resolution.would_single_model_suffice` | Retrospective judgment | **The single most valuable label in the schema** |
| `economics.ensemble_overhead_ratio` | Cost of the dialectic vs single call | Cost-aware routing policy |
| `attestation.integrity` | Ties dialectic quality to context quality | Confound control: bad outcome ≠ bad model if context was DEGRADED |
| `content_ref` + `content_sha256` | Body stays in opencode.db; log stays small and verifiable | Prevents multi-GB JSONL (the compaction-part problem) |

> **Design decision — bodies are NOT inlined.** OpenCode parts can reach hundreds of MB. Storing `content_ref` (a `prt_` id) plus a hash keeps `dialectic_sessions.jsonl` grep-able and diffable, while the full text remains retrievable and tamper-evident. This mirrors the externalized-output pattern already used by the sessions-explorer plugin.

### 3.4 Example Rows (abbreviated)

**Mode `single`** — the migration target for existing `finetune_*.jsonl`:
```json
{"schema_version":"1.0","dialectic_id":"dlg_...","mode":"single","problem_type":"research","turns":[{"turn":1,"role":"proposer","model":"qwen3-1.7b","provider":"native-gguf","is_cloud":false,"reviews_turns":[],"confidence":0.5}],"resolution":{"converged":true,"rounds":1,"value_added_by_dialectic":false,"would_single_model_suffice":true}}
```

**Mode `council`** — MaKaLi (parallel, then synthesis):
```json
{"mode":"council","problem_type":"compliance","turns":[
 {"turn":1,"role":"proposer","entity":"maat","model":"gemini-3.5-flash","provider":"antigravity","reviews_turns":[]},
 {"turn":2,"role":"proposer","entity":"lilith","model":"gemini-3.5-flash","provider":"antigravity","reviews_turns":[]},
 {"turn":3,"role":"synthesizer","entity":"kali","model":"qwen3-1.7b","provider":"native-gguf","reviews_turns":[1,2],
  "critique":{"target_turn":2,"verdict":"refined","grounds":["scope_expansion"]}}],
 "resolution":{"converged":true,"rounds":1,"decided_by":"turn_3","value_added_by_dialectic":true}}
```
Note turns 1 and 2 have `reviews_turns: []` — parallel, independent. Only the synthesizer reviews. This is structurally distinct from `sequential` and the schema captures it natively.

**Mode `ensemble`** — independent voting:
```json
{"mode":"ensemble","problem_type":"architecture","turns":[
 {"turn":1,"role":"proposer","model":"gemini-3.1-pro","account_id":"account-1","reviews_turns":[],"position":"A","confidence":0.88},
 {"turn":2,"role":"proposer","model":"claude-opus-4.6","account_id":"account-2","reviews_turns":[],"position":"A","confidence":0.91},
 {"turn":3,"role":"proposer","model":"claude-sonnet-4.6","account_id":"account-1","reviews_turns":[],"position":"B","confidence":0.71}],
 "resolution":{"converged":false,"final_position":"A","decided_by":"majority_vote","dissent":[3],
  "value_added_by_dialectic":false,"would_single_model_suffice":true},
 "economics":{"ensemble_overhead_ratio":3.0}}
```
This row is a **negative training example**: 3× cost, unanimous-enough outcome, `would_single_model_suffice: true`. Rows like this are what teach the router to *not* ensemble.

### 3.5 Training Data Pipeline

Three downstream models, three different projections of the same log:

| Target model | Input projection | Label | Minimum rows |
|---|---|---|---|
| **Router** (when to ensemble) | `problem_type`, `sdp_phase`, context size, `attestation.integrity` | `resolution.value_added_by_dialectic` | ~500 (binary, tabular — a gradient-boosted tree suffices; no LLM needed) |
| **Critic** (find the flaw) | turn *N* content + prior turns it reviews | `critique.verdict` + `grounds` | ~2,000 |
| **Synthesizer** (resolve dissent) | all turns | `resolution.final_position` | ~1,000 |

**Bootstrapping path:** the router is trainable first and cheapest — it is a tabular binary classifier over ~10 features. At 500 rows it beats a hand-written heuristic. The critic and synthesizer need LLM fine-tuning and should wait for volume.

**Pipeline stages:**
1. **Emit** — `src/omega/oracle/dialectic_logger.py` appends on session close (atomic, per M12/FM-04).
2. **Validate** — JSON Schema check in CI; malformed rows quarantined to `dialectic_sessions.rejected.jsonl` (never silently dropped — M12).
3. **Enrich** — nightly job back-fills `would_single_model_suffice` by replaying the problem against the single best model and diffing outcomes.
4. **Project** — `scripts/export_training_data.py --target router|critic|synthesizer`.
5. **Prune** — dedupe on `problem_statement` embedding (per C-MEM-005/006 gnosis-hygiene mandate); discard rows where `attestation.integrity == "DEGRADED"` from training sets (confounded).

### 3.6 Migration Path

```
Step 1  Freeze finetune_*.jsonl (stop new writes; keep files).
Step 2  scripts/migrate_finetune_to_dialectic.py — mechanical map:
          trace_id→trace_id, session_id→session_id, metadata.model→turns[0].model,
          metadata.confidence→turns[0].confidence, metadata.rating→human_feedback.rating,
          mode:"single", reviews_turns:[], would_single_model_suffice:true
Step 3  Dual-write for 2 weeks (both formats) to validate parity.
Step 4  Cut over. finetune_*.jsonl becomes read-only archive.
```

**No data is lost and no field is dropped** — every existing key has a destination. This satisfies M5 (Gnosis Preservation).

### 3.7 Storage & Indexing

- **Path:** `data/dialectics/dialectic_sessions.jsonl` (append-only), rotated monthly to `data/dialectics/archive/YYYY-MM.jsonl`.
- **Index:** mirror key fields into `metrics_db.py` as a `dialectic_index` table (`dialectic_id, mode, problem_type, converged, value_added, total_cost_usd, ts`) so the Hub can query without scanning JSONL — consistent with the **FTS5-first mandate (C-MEM-004)**: never linear-scan for discovery.

---

## 4. Ensemble Routing Strategy

### 4.1 The Evidence Is Mostly Negative

This is the gap where the research most sharply contradicts intuition. The mission asked "when should the SDP route to 2-3 AGY models vs just 1?" The honest 2026 answer is: **rarely, and only under conditions we can enumerate precisely.**

**Finding 1 — Debate can make things worse.**
*Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate* (arXiv:2509.05396): multi-agent debate "can sometimes degrade performance, leading to worse final answers than those generated by a single agent acting alone. These failures are **not rare edge cases**, but arise systematically in settings where agents amplify each other's errors — agreeing reflexively rather than challenging flawed reasoning." On CommonSenseQA, "**debate always harms performance**." Critically: "even when groups include more 'strong' models than 'weak' ones, the process of debate does not always yield performance gains."

**Finding 2 — Sycophancy is not fixable by prompting.**
Same paper: adding an explicit correctness payoff to the prompt "does not significantly reduce the likelihood that LLM agents flip their answers from correct to incorrect. In fact... the number of correct→incorrect transitions actually **increases**." So the naive mitigation ("just tell them to be rigorous") is empirically refuted.

**Finding 3 — Tyranny of the majority.**
Estornell & Liu (via the same survey): if the majority give the same answer *regardless of correctness*, minority agents conform — an echo chamber. Extended to heterogeneous settings: "even when the majority consists of stronger models, introducing a weaker model can **diminish overall performance**."

**Finding 4 — The ICLR 2025 verdict.**
*Multi-LLM-Agents Debate — Performance, Efficiency, and Scaling Challenges*: five MAD frameworks across nine benchmarks — "current MAD methods **fail to consistently outperform simpler single-agent strategies, even with increased computational resources.**"

**Finding 5 — Equal-budget single agent wins on multi-hop.**
arXiv:2604.02460: "Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning **Under Equal Thinking Token Budgets**." This is the correct comparison and it is the one that matters for a token-constrained sovereign: the question is never "1 model vs 3 models," it is "**1 model with 3× the thinking budget vs 3 models with 1× each.**"

**Finding 6 — Voting ≫ debate, on cost-effectiveness.**
Agent MarketCap (Apr 2026) synthesis: "most of the performance gain comes from the **voting aggregation itself, not from the debate rounds**... simple majority voting among independent agents captures roughly **80-90% of the accuracy gains** you'd expect from full multi-round debate... **a voting ensemble without debate rounds often delivers 80% of the benefit at 30-40% of the cost.**"

**Finding 7 — Heterogeneity is the precondition, not a bonus.**
Du et al. (ICML 2024) cross-model result: ChatGPT + Bard on GSM8K solved 17/20 vs 11–14 for either alone — "the most striking result in the paper because it shows **heterogeneous** agents catching each other's errors." Conversely: "Agents sharing identical weights and identical context tend to agree, defeating the purpose."

**Finding 8 — Task type decides.**
Agent MarketCap: "For tasks that require systematic multi-step reasoning... debate rounds deliver measurable gains. For tasks that rely primarily on **factual recall, agents tend to confidently reinforce each other's errors**. A group of agents who all hallucinate the same citation doesn't produce a better answer by debating it."

**Finding 9 — Selective triggering is the state of the art.**
iMAD (Fan, Yoon & Ji, Virginia Tech): "triggering MAD for every query is inefficient, as it incurs substantial computational (token) cost and **may even degrade accuracy by overturning correct answers from single-agent**." Their answer is a learned trigger — precisely the model our `dialectic_sessions.jsonl` schema (§3.5) is designed to train.

> **The Alchemist's reframe:** the interesting asymmetry is that our SDP already gets most of the ensemble benefit *for free*. Phase 1 → Phase 2 → Phase 3 uses **different models in different roles** — that is heterogeneity with *zero* duplicated work. Sequential role-diversity is strictly cheaper than parallel opinion-diversity and captures the same error-catching effect. **The SDP is already an ensemble; we should be reluctant to bolt a second one on top.**

### 4.2 Cost/Burn Analysis — 8 Accounts, Weekly Pools

Grounding in our actual constraint (`AGY_SESSION_LEDGER.md`, `SDP_FORMAL_ROUTING_SPEC.md` §1.2, `SAFETY_MARGIN = 5000`):

Observed AGY session costs from the ledger (2026-08-09): 45K, 15K, 20K → **mean ≈ 27K tokens/session**.

| Strategy | Tokens/decision | Decisions per account-week (assume 1M pool) | Fleet capacity (8 accounts) |
|---|---|---|---|
| Single | 27K | ~37 | **~296 decisions/week** |
| Ensemble-2 | 54K | ~18 | ~148 decisions/week |
| Ensemble-3 | 81K | ~12 | **~98 decisions/week** |
| Debate-3 (2 rounds) | ~160K | ~6 | ~49 decisions/week |

**Ensemble-3 costs 67% of the fleet's weekly decision capacity.** Debate-3 costs 83%.

Combined with Finding 6 (voting gets 80–90% of debate's gain at 30–40% of cost) and Finding 5 (single-agent-with-bigger-budget wins on multi-hop), the economics are stark:

> **For an equal 81K token spend, we can have: (a) three 27K opinions that may collude, or (b) one 81K deep reasoning pass. The literature says (b) wins on reasoning tasks and (a) only wins on tasks with independent verifiable answers and genuinely diverse models.**

### 4.3 Decision Tree

```
                    ┌─────────────────────────────┐
                    │  AGY escalation requested   │
                    └──────────────┬──────────────┘
                                   ▼
                    ┌─────────────────────────────┐
              NO ◄──┤ Is task REASONING-heavy?    │
              │     │ (architecture, refactoring, │
              │     │  synthesis, compliance)     │
              │     └──────────────┬──────────────┘
              │                    │ YES
              ▼                    ▼
      ╔═══════════════╗  ┌─────────────────────────────┐
      ║ SINGLE MODEL  ║  │ Is the cost of being WRONG  │
      ║ (mandatory)   ║◄─┤ > 3x the cost of compute?   │ NO
      ║ Retrieval &   ║  └──────────────┬──────────────┘
      ║ factual tasks ║                 │ YES
      ║ AMPLIFY error ║                 ▼
      ╚═══════════════╝  ┌─────────────────────────────┐
                     NO ─┤ Can we field ≥2 models from  │
              ┌─────────►│ DIFFERENT families?          │
              │          │ (Gemini vs Claude — not      │
              │          │  two Gemini variants)        │
      ╔═══════════════╗  └──────────────┬──────────────┘
      ║ SINGLE MODEL  ║                 │ YES
      ║ + bigger      ║                 ▼
      ║ thinking      ║  ┌─────────────────────────────┐
      ║ budget        ║◄─┤ Fleet pool health:           │ NO
      ║ (beats homo-  ║  │ ≥3 accounts >200K remaining? │
      ║  geneous      ║  └──────────────┬──────────────┘
      ║  ensemble)    ║                 │ YES
      ╚═══════════════╝                 ▼
                         ┌─────────────────────────────┐
                         │ Does the answer have an     │
                         │ INDEPENDENTLY VERIFIABLE    │ NO
                         │ form? (tests pass, schema   ├──► SINGLE + CRITIC
                         │  validates, benchmark runs) │    (2x, sequential,
                         └──────────────┬──────────────┘     critic reads
                                        │ YES                 proposer)
                                        ▼
                            ╔═══════════════════════╗
                            ║  ENSEMBLE-3 (VOTING)  ║
                            ║  parallel, no debate  ║
                            ║  rounds, majority     ║
                            ║  vote, log dissent    ║
                            ╚═══════════════════════╝
```

### 4.4 Implementation Heuristic

```python
# src/omega/oracle/ensemble_router.py
# Evidence: arXiv:2509.05396 (debate harms), ICLR2025 MAD, arXiv:2604.02460
#           (single-agent wins at equal budget), AgentMarketCap 2026 (voting>debate)

RETRIEVAL_TASKS = {"research"}                      # error-amplifying — NEVER ensemble
REASONING_TASKS = {"architecture", "refactoring", "synthesis", "compliance"}

MIN_POOL_FOR_ENSEMBLE = 200_000
HIGH_STAKES_MULTIPLIER = 3.0

def should_ensemble(req: RoutingRequest, fleet: List[AGYAccount]) -> EnsembleDecision:
    # GATE 1 — task type. Finding 8: debate amplifies error on factual recall.
    if req.problem_type in RETRIEVAL_TASKS:
        return EnsembleDecision(False, "single", "retrieval_task_amplifies_error")
    if req.problem_type not in REASONING_TASKS:
        return EnsembleDecision(False, "single", "unknown_task_type_conservative")

    # GATE 2 — stakes. 2-7x overhead only justified by asymmetric downside.
    if req.error_cost_ratio < HIGH_STAKES_MULTIPLIER:
        return EnsembleDecision(False, "single", "stakes_below_compute_cost")

    # GATE 3 — heterogeneity. Finding 7: homogeneous agents collude.
    healthy = [a for a in fleet if a.is_healthy
               and a.pool_remaining >= req.estimated_tokens + MIN_POOL_FOR_ENSEMBLE]
    families = {model_family(m) for a in healthy for m in a.models}   # {"gemini","claude",...}
    if len(families) < 2:
        # Finding 5: single agent with larger budget beats homogeneous ensemble.
        return EnsembleDecision(False, "single_extended_budget",
                                "insufficient_model_diversity")

    # GATE 4 — fleet health. Ensemble-3 burns 67% of weekly capacity.
    if len(healthy) < 3:
        return EnsembleDecision(True, "single_plus_critic", "degraded_pool_2x_only")

    # GATE 5 — verifiability. Voting needs a convergent right answer.
    if not req.has_verifiable_form:
        # No ground truth to vote toward -> sequential critique, not parallel vote.
        return EnsembleDecision(True, "single_plus_critic", "unverifiable_use_critique")

    # Finding 6: voting captures 80-90% of debate gain at 30-40% cost.
    return EnsembleDecision(True, "ensemble_3_voting", "all_gates_passed",
                            models=pick_diverse(healthy, n=3))
```

**Aggregation rule** (from the ensemble-math analysis): match the aggregator to the failure mode. Random/bidirectional errors → **majority vote with odd n**. Directional bias (e.g. models systematically under-scoping a refactor) → **max/union**. Never use mean over positions.

**Entropy injection interaction:** `SDP_FORMAL_ROUTING_SPEC.md` §4 injects 10% second-best selection to force cross-model dialectics. This is **compatible and complementary** — it produces heterogeneity cheaply over time (across sessions) rather than expensively at once (within a session). Recommend *raising* entropy to ~15% as partial compensation for making ensembles rarer.

### 4.5 Expected Outcome

Applying these gates to typical Omega workloads:

| Task type | Frequency | Gate outcome |
|---|---|---|
| research | High | **Never ensemble** (Gate 1) |
| compliance | Medium | Usually `single_plus_critic` (verifiable, but stakes vary) |
| refactoring | Medium | `ensemble_3_voting` when tests exist (verifiable form ✓) |
| architecture | Low | `single_plus_critic` (rarely verifiable) |
| synthesis | Medium | Single (stakes rarely 3×) |

**Projected ensemble rate: <15% of AGY escalations**, preserving ~85% of the ~296 decisions/week fleet capacity while concentrating the 3× spend where the literature says it actually pays.

---

## 5. Local Executor Capability Profile

### 5.1 Our Own Measured Data (highest-authority evidence)

`data/benchmarks/bench_qwen3-1.7b_p7_context_2026-08-09.json` — measured today, on the target hardware:

| Metric | Value |
|---|---|
| Model | qwen3-1.7b (Q6_K) |
| Role tested | `p7_context` |
| Samples | 5 |
| TTFT | 185.73 ms |
| Throughput | **45.13 tok/s** |
| Peak RAM | **1,028.2 MB** |
| Accuracy / Adherence / Conciseness / Structure | pass / pass / pass / pass |
| **avg_quality_score** | **0.65** |
| **factuality_rate** | **0.9545** |
| Judge scale | 3-point, calibration κ = 0.75 |

Hardware envelope (`config/hardware_profile.yaml`): AMD Ryzen 7 5700U (Zen2), 8C/16T, **14.4 GB total / 10.3 GB available**, 512 MB VRAM, `recommended_threads: 7`.

**Reading this honestly:** 4/4 categorical passes but quality 0.65 on a 3-point scale. The categorical passes mean "did not fail catastrophically"; 0.65 means "adequate, not good." **κ=0.75 with n=5 is a thin basis** — this is a smoke test, not a capability profile. Factuality 0.954 is genuinely strong and is the number to lean on: qwen3-1.7b **does not hallucinate much**. That makes it an excellent *classifier and verifier* and says nothing about its ability to *author* code.

### 5.2 The 3B Structured-Output Cliff

AscentCore (1 Apr 2026), 22 quantized configs, 11 models, 1,012 inference runs, Ollama-served GGUF — the most directly transferable external benchmark to our stack:

| Model | Tier | JSON Parse % | **Schema Comply %** | Extraneous Output % | TPS |
|---|---|---|---|---|---|
| **llama3.1:8b-q8_0** | B | **100.0%** | **95.7%** | **0.0%** | 29.3 |
| llama3.1:8b-q4_K_M | B | 91.3% | **91.3%** | 0.0% | 46.6 |
| qwen2.5:1.5b-q8_0 | A | 95.7% | — | — | 121.9 |
| phi3:14b-q4_K_M | B | 95.7% | 78.3% | 34.8% | 23.6 |
| mistral:7b-q8_0 | B | 100.0% | **47.8%** | 0.0% | 31.2 |
| **llama3.2:3b** | A | **47.8–56.5%** | — | — | 98.7 |
| gemma3:12b-q4_K_M | B | 100.0% | **43.5%** | **100.0%** | 27.3 |
| **smollm2:1.7b-q4_K_M** | A | **26.1%** | **4.3%** | — | 157.3 |

Verbatim findings:
- "**Llama 3.1 8B is the JSON champion** — Q8_0 achieves 100% parse rate and 95.7% schema compliance — the highest of any model — while producing **zero extraneous output**."
- "**Llama 3.2 3B struggles with JSON format**... only 47.8–56.5% JSON parse rate... **The 3B scale appears insufficient for reliable structured output.**"
- "**SmolLM2 1.7B fails JSON tasks** — 26.1% parse rate and 4.3% schema compliance — **unusable for structured output.**"
- "**Large models don't justify the cost at this scale.** Gemma 3 12B and Phi-3 14B offer ROUGE-L below Llama 3.1 8B while running under 28 TPS."

> **Two critical structural lessons.** (1) **Parse rate ≠ schema compliance.** Mistral 7B Q8: 100% parse, 47.8% compliance. Valid JSON with wrong fields is *more* dangerous than a parse error, because it fails silently downstream. (2) **Bigger is not better.** Gemma 3 12B (43.5% compliance, 100% extraneous output) is worse than Llama 3.1 8B on the axis that matters. Parameter count does not predict executor reliability — **family and post-training do.**

### 5.3 The Constraint Tax — Why "Just Use Constrained Decoding" Is Not a Free Fix

*The Constraint Tax: Measuring Validity-Correctness Tradeoffs in Structured Outputs for Small Language Models* (arXiv:2605.26128) — tested on **exactly our size class** (Qwen2.5-0.5B/1.5B/3B, SmolLM2-1.7B) with executable checkers and exact ground truth:

> "The usual engineering assumption is that hard output constraints improve reliability without changing the underlying answer. We show that **this assumption is unsafe for small models.**"

Constrained decoding (Outlines, vLLM `guided_json`, XGrammar) guarantees *syntactic* validity by construction — it cannot produce malformed JSON. But it **costs semantic accuracy** in sub-3B models: the FSM constrains the token distribution, and a small model with limited capacity spends that capacity satisfying the grammar instead of solving the task.

**Direct SDP consequence:** we cannot rescue Qwen3-1.7B as an executor by wrapping it in Outlines. We would trade "produces invalid JSON" for "produces valid JSON containing the wrong answer" — strictly worse, because it defeats the validator.

### 5.4 Capability Profile — Qwen3-1.7B (native-gguf)

| Capability | Verdict | Evidence | Notes |
|---|---|---|---|
| Intent classification / routing | ✅ **RELIABLE** | factuality 0.954; TTFT 186 ms | Already in production (Iris speculative decode, triage) |
| Context gauge / arithmetic reporting | ✅ **RELIABLE** | structure: pass | Deterministic-adjacent; low output entropy |
| Yes/no verification against explicit criteria | ✅ **RELIABLE** | factuality 0.954 | Its strongest genuine capability |
| Short summarization (<500 tok) | 🟡 **CONDITIONAL** | quality 0.65 | Acceptable for logs, not for handoff artifacts |
| Structured JSON output | ❌ **UNRELIABLE** | 1.7B class: 26.1% parse (SmolLM2) | Sub-3B cliff. Constraint tax blocks the workaround |
| Single-file atomic edit (authoring) | ❌ **UNRELIABLE** | 3B insufficient for structured output | Cannot be trusted to emit a correct diff |
| Multi-file refactor | ❌ **PROHIBITED** | far beyond 3B cliff | Never assign |
| Test generation | ❌ **PROHIBITED** | quality 0.65 | Would generate passing-but-vacuous tests |
| Code review | ❌ **PROHIBITED** | quality 0.65 | Would produce confident, shallow approval |

**Hard limits:** 8,192 token context (`models.yaml`), context_budget 15,000, 2,048 MB declared RAM (1,028 MB measured), 45 tok/s → a 2,000-token output takes ~44 s.

### 5.5 Capability Profile — Llama-3.1-8B-class (proposed Phase 3 executor)

| Capability | Verdict | Evidence |
|---|---|---|
| Structured JSON output | ✅ **RELIABLE** | 95.7% schema compliance @ Q8_0, **0% extraneous output** |
| Apply a pre-authored unified diff | ✅ **RELIABLE** | 100% length compliance, zero extraneous output |
| Single-file atomic edit (authoring) | 🟡 **CONDITIONAL** | best-in-class small-model compliance, but no SWE-bench evidence at this quant |
| Multi-file refactor | ❌ **UNRELIABLE** | no benchmark support; exceeds demonstrated scope |
| Test generation | 🟡 **CONDITIONAL** | requires the AGY model to specify assertions |

**Hardware reality check (the blocker).** An 8B model at Q4_K_M is ~4.7 GB weights (cf. our `mimo-7b-rl-q4_k_m`: 4.7 GB, `ram_mb: 6144`). Against 10,305 MB available and the OOMProtector rule (`available > model_ram + 1 GB`): 6,144 + 1,024 = **7,168 MB required vs 10,305 available → FITS, with ~3.1 GB headroom.** Q8_0 (~8.5 GB) **does not fit** and must not be attempted.

> **The Adversary's warning:** the AscentCore JSON champion is specifically **Q8_0** (95.7%); Q4_K_M drops to 91.3%. We can only run Q4_K_M. We therefore inherit the *lower* number — still far above the 3B cliff, but the headline 95.7% is **not available to us on this hardware.** Plan for ~91%, and note that ~9% schema failure demands a validator + retry loop regardless.

**Candidate already on disk:** `mimo-7b-rl-q4_k_m` (4.7 GB, 32,768 context, "strong reasoning/coding") is the incumbent to benchmark first — it has 4× the context of qwen3-1.7b and is already registered in `models.yaml`. **Recommend benchmarking MiMo-7B before acquiring a Llama-3.1-8B GGUF.**

### 5.6 Failure Modes

| ID | Failure | Trigger | Detection | Mitigation |
|---|---|---|---|---|
| LE-01 | **Silent schema drift** — valid JSON, wrong fields | Any sub-8B on nested schema | `jsonschema` validate (deterministic) | Validate; retry ≤2; escalate |
| LE-02 | **Extraneous commentary** wrapping JSON | Gemma-family (100% rate) | Non-JSON leading/trailing bytes | Strip fences; prefer Llama family |
| LE-03 | **Constraint tax** — schema-valid, semantically wrong | sub-3B + constrained decoding | Executable check only | Do not use sub-3B for structured output |
| LE-04 | **Partial application** — applies 2 of 5 edits | Multi-file scope on small model | `git diff --stat` vs expected | One file per invocation; never batch |
| LE-05 | **Repetition loop** | Long generation, low rep-penalty | Token-level n-gram detect | `sampling_overrides` (precedent: gemma-4-31b) |
| LE-06 | **Context overflow → OOM** | Input > 8,192 (qwen3-1.7b) | Pre-flight token count | Reject at gateway; escalate |
| LE-07 | **Confident vacuous approval** | Code review assigned to small model | None (this is why it's prohibited) | Never assign review to <8B |

### 5.7 Recommended Task Boundaries — and the SDP Design Change They Force

| SDP Phase 3 task | Assign to | Never assign to |
|---|---|---|
| Verify `make test` output parses as pass/fail | qwen3-1.7b | — |
| Classify which file a change belongs to | qwen3-1.7b | — |
| Emit context-gauge JSON | qwen3-1.7b (fixed template) | — |
| Apply a supplied unified diff | **deterministic code** (`git apply`) | any LLM |
| Author a single-file edit from an exact spec | MiMo-7B / Llama-3.1-8B Q4 | qwen3-1.7b |
| Author a multi-file refactor | **AGY model (Phase 2)** | any local model |
| Generate tests from specified assertions | MiMo-7B / 8B-class | qwen3-1.7b |
| Review a diff for correctness | **AGY model or human** | any local model |

> **The Architect's ruling — this changes the SDP contract.** The manifesto (§Phase 3) says local models "take the highly structured plan produced in Phase 2 and execute it mechanically." The evidence says a small model cannot *interpret* prose into a correct edit. Therefore **Phase 2's output schema must change**: the AGY model must emit **directly executable artifacts** — unified diffs, exact shell commands, exact file+line+replacement tuples — not prose instructions.
>
> Then Phase 3 becomes: `git apply` (deterministic, 100% reliable) + `make test` (deterministic) + qwen3-1.7b classifying the result (0.954 factuality). **The local model's job is to *verify*, not to *author*.** That plays to its one genuine strength and eliminates every failure mode in §5.6 except LE-06.
>
> This is also strictly more sovereign: it moves work from a fallible small model to *deterministic code*, which is the most local, most free, most reliable executor available.

### 5.8 Required Validation Before Shipping Phase 3

Current evidence is n=5 on one role. Before Phase 3 is trusted:

| Test | Models | Success criterion |
|---|---|---|
| JSON schema compliance, n≥50, nested depth 3 | qwen3-1.7b, mimo-7b-q4 | ≥90% for executor promotion |
| Unified-diff application, n≥30 real repo diffs | `git apply` vs model-authored | deterministic path = 100% |
| Instruction adherence (IFEval subset), n≥100 | both | establish local IF baseline |
| RAM ceiling under concurrent load | mimo-7b-q4 | no OOMProtector trip at 10.3 GB avail |
| Constraint-tax delta (free vs Outlines-constrained) | both | quantify our own tax |

**Until these run, Phase 3 must be restricted to the "verify, don't author" contract of §5.7.**

---

## 6. Sources & Citations

### 6.1 External — Model Benchmarks (Gap 1)

| # | Source | Date | Used for |
|---|---|---|---|
| S1 | Artificial Analysis — *Nemotron 3 Ultra 550B A55B Intelligence, Performance & Price* | 2026 | **260K served context** (contradicts 1M claim); Intelligence #20/101; Speed #11/101 @ 119.4 tok/s; $0.60/$2.75 |
| S2 | BenchLM.ai — *Nemotron 3 Ultra Benchmarks & Context* | 2026-08-07 | Overall #155/216 (44.4); **Instruction Following #4**; **Agentic #121**; 19/381 slots, "Estimated" |
| S3 | research.nvidia.com/labs/nemotron/Nemotron-3-Ultra | 2026-06-04 | 1M RULER validation (self-hosted architectural claim) |
| S4 | poolside.ai — *Introducing Laguna S 2.1* | 2026-07-21 | 118B-A8B, 1M context; T-Bench 70.2; full comparison table; **vendor-admitted nested-JSON defect** |
| S5 | AIToolsReview — *Laguna S 2.1 Review* | 2026-07-27 | SWE-Bench Multilingual 78.5, SWE Atlas 46.2, SWE-Bench Pro 59.4; Nemotron 3 Ultra T-Bench 56.4 |
| S6 | VentureBeat — *Poolside drops Laguna S 2.1* | 2026-07-21 | Independent confirmation, 1M context, OpenMDW-1.1 |
| S7 | NYU Shanghai RITS | 2026-07-22 | 59 GB quantized; Laguna family lineage (M.1 225B-A23B, XS 2.1 33B-A3B) |
| S8 | longcatai.org/benchmarks | 2026 | Longcat 2.0: SWE-bench Pro 59.5, Multilingual 77.3, T-Bench 70.8, RWSearch 78.8, BrowseComp 79.9, FORTE 73.2, MMLU 89.71, IFEval 89.65 |
| S9 | llm-stats.com — Nemotron 3 Ultra | 2026-06-04 | 550B/55B, 20T tokens, LatentMoE, OpenMDW v1.1 |
| S10 | benchable.ai — Laguna S 2.1 | 2026 | Laguna family context windows (XS 2.1 262K, XS.2 262K, M.1 262K) |

### 6.2 External — Attestation & Provenance (Gap 2)

| # | Source | Date | Used for |
|---|---|---|---|
| S11 | arXiv:2606.22560 — *Evidence-Bound Gateway-Path Provenance for Third-Party LLM Inference* (Wang & Tian) | 2026-06-21 | Cryptographic attestation design **and its threat-coverage table** — the basis for rejecting it (RAG poisoning / malicious output explicitly uncovered) |
| S12 | Giskard — *Best hallucination detection tools for LLMs and AI agents 2026* | 2026 | **"Retrieval that never ran"**; "invented citations pass judges"; **deterministic `FnCheck` before `Groundedness` judges** (adopted as ordering law) |
| S13 | Openlayer — *RAG Groundedness Evaluation Guide* | 2026-02-11 | Failure taxonomy: invention / contradiction / partial hallucination / scope expansion; LLM-judge ~80% human agreement; >0.85 threshold |
| S14 | arXiv:2603.28988 — *Attesting LLM Pipelines* (FSE '26) | 2026-04-01 | Artifact provenance gaps; integrity checks cannot rule out behavior-level compromise |
| S15 | Corbits — *Context Loss in Multi-Agent Systems* | 2026-05-28 | Handoff as the dominant failure locus |
| S16 | XTrace — *AI Agent Handoff: Why Context Breaks* | 2026-02-20 | Decisions/reasoning/evidence lost at handoff |
| S17 | SyncSoft — *Agent Handoff: Fix Multi-Agent Context Loss* | 2026-05-23 | Partial transfer → receiving agent reasons from degraded picture |
| S18 | Microsoft Agent Framework — Handoff orchestration | 2026-05-09 | Industry handoff baseline |

### 6.3 External — Ensemble & Debate (Gap 4)

| # | Source | Date | Used for |
|---|---|---|---|
| S19 | arXiv:2509.05396 — *Talk Isn't Always Cheap: Failure Modes in Multi-Agent Debate* | — | Debate degrades performance systematically; CommonSenseQA "debate always harms"; correctness-payoff prompting **increases** correct→incorrect flips; heterogeneous groups converge on wrong answers |
| S20 | ICLR 2025 Blogpost — *Multi-LLM-Agents Debate: Performance, Efficiency, Scaling* | 2025/2026 | 5 frameworks × 9 benchmarks: MAD "fails to consistently outperform simpler single-agent strategies" |
| S21 | arXiv:2604.02460 — *Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets* | 2026 | **The equal-budget comparison** — the decisive economic argument |
| S22 | arXiv:2511.11306 — *iMAD: Intelligent Multi-Agent Debate* (Fan, Yoon, Ji — Virginia Tech) | — | Selective triggering; MAD "may degrade accuracy by overturning correct answers from single-agent" |
| S23 | Agent MarketCap — *Multi-Agent Debate and Consensus Architecture 2026* | 2026-04-09 | **Voting captures 80–90% of debate gain at 30–40% cost**; 3–20× overhead; critic pattern ≈2×; task-type dependence; homogeneous pools fail |
| S24 | Beancount.io Bean Labs research log | 2026-05-24 | Du et al. ICML 2024 numbers: MMLU 71.1 vs 63.9; **cross-model ChatGPT+Bard 17/20 vs 11–14**; diminishing returns past 4 rounds; M3MAD-Bench "Collective Delusion" taxonomy |
| S25 | NeurIPS 2024 — *Multi-LLM Debate: Framework, Principals, Interventions* | 2024-10-30 | Similar capabilities → static dynamics → convergence to majority opinion |
| S26 | alphaXiv 2502.08788 — *Stop Overvaluing Multi-Agent Debate* | — | Evaluation critique; model heterogeneity as precondition |
| S27 | shibaprasadb.com — *From 75% to 99.6%: The Math of LLM Ensembles* | 2026-01-20 | Aggregator-to-failure-mode matching (max/min/majority); diminishing returns past n=3 |

### 6.4 External — Local Model Limits (Gap 5)

| # | Source | Date | Used for |
|---|---|---|---|
| S28 | AscentCore — *Small LLM Performance Benchmark* (22 configs, 11 models, 1,012 runs, Ollama GGUF) | 2026-04-01 | **The core Gap-5 dataset**: Llama 3.1 8B Q8 95.7% schema / Q4 91.3%; Llama 3.2 3B 47.8–56.5% parse; SmolLM2 1.7B 26.1%/4.3%; Gemma 12B 43.5% + 100% extraneous; "3B scale insufficient for reliable structured output" |
| S29 | arXiv:2605.26128 — *The Constraint Tax* | 2026 | Sub-3B (Qwen2.5-0.5B/1.5B/3B, SmolLM2-1.7B): hard constraints **change the answer**; validity-correctness tradeoff — blocks the constrained-decoding workaround |
| S30 | arXiv:2604.25359 — *The Structured Output Benchmark* | 2026-04-28 | Prompting strategy > model size; semantic errors persist despite structural validity; ExtractBench 4.6% frontier field-level pass |
| S31 | BenchLM.ai — *Instruction Following Leaderboard* | 2026-08-06 | IFEval/IFBench methodology; "a model that ignores constraints is unusable in automated pipelines" |
| S32 | collinwilkins.com — *LLM Structured Outputs: Schema Validation for Real Pipelines* | 2026-05-15 | JSONSchemaBench; XGrammar/Guidance/Outlines decision guide |
| S33 | eastondev.com — *LLM Structured Output: Schemas, Retries, Constrained Decoding* | 2026-07-30 | Outlines / vLLM `guided_json` implementation patterns |
| S34 | pulsar-edit-mcp-server — `LLM-FAILURE-MODES.md` | — | Code-editing failure taxonomy from production use |

### 6.5 Internal — Omega Engine Sources

| Path | Used for |
|---|---|
| `data/benchmarks/bench_qwen3-1.7b_p7_context_2026-08-09.json` | **Primary measured evidence** for §5.1 |
| `config/hardware_profile.yaml` | Zen2 8C/16T, 14.4 GB / 10.3 GB avail, 512 MB VRAM — RAM feasibility math |
| `config/models.yaml` | Context budgets, RAM, sampling overrides, `mimo-7b-rl-q4_k_m` candidate |
| `config/providers.yaml` | 12 providers, fallback chain, streaming timeouts, MaKaLi routing |
| `config/model_registry/models/cloud/*.yaml.md` | Per-model context windows; **the Laguna M.1 frontmatter/body contradiction (M23 finding)** |
| `config/entity_model_affinity.yaml` | 3-tier affinity precedent for the matrix schema |
| `src/omega/observability/metrics_db.py` | `performance`, `vault_audit` table patterns for the dialectic index |
| `data/datasets/finetune_*.jsonl` | Existing schema — migration source for §3.6 |
| `docs/strategy/COGNITIVE_SCAFFOLDING_PROTOCOL.md` | Phase definitions; message-count compaction rule; 150K switch rule |
| `docs/strategy/SDP_FORMAL_ROUTING_SPEC.md` | Constraints C₁–C₄, utility fn, `SAFETY_MARGIN`, entropy injection |
| `docs/strategy/SDP_IMPLEMENTATION_SPEC.md` | Gauge schema, SSP, `AGYAccount`, integration points |
| `docs/strategy/SDP_FAILURE_MODE_ANALYSIS.md` | FM-01..FM-10 (extended with FM-11..13) |
| `docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md` | **Contains the 1M Nemotron assumption corrected in §1.1** |
| `data/coordination/AGY_SESSION_LEDGER.md` | Observed session costs (45K/15K/20K) for §4.2 |
| `data/entities/roc_racoon/workspace/mining_reports/SDP_INTEGRATION_MINING_REPORT_20260809.md` | Existing-system inventory; confirms no dialectic capture exists |

### 6.6 Search Provenance (M23)

All external searches executed **2026-08-09** via `parallel-search_web_search` (Tier T1 equivalent), temporal mandate satisfied ("2026"/"latest" in every query). **Four search batches, 14 queries, 0 tool failures. No `[TOOL-CHAIN-COLLAPSE]` conditions encountered.** No parametric-only synthesis was performed; every claim in §§1–5 traces to a cited source or a measured local artifact.

---

## 7. Consolidated Action Register

| # | Action | Gap | Priority | Owner | Effort |
|---|---|---|---|---|---|
| A1 | **Reconcile Laguna M.1 frontmatter (262144) vs body (131072)** | 1 | 🔴 P0 | N2 Persistence | 10 min |
| A2 | **Correct Nemotron 3 Ultra context 1M → 260K** in gauge spec + providers.yaml | 1 | 🔴 P0 | N6 Cognition | 30 min |
| A3 | Re-key `context_window` on `(model, provider)` tuple | 1 | 🔴 P0 | N6 Cognition | 2 h |
| A4 | Add `task_affinity` / `task_antiaffinity` / `emits_reliable_json` to models.yaml | 1 | 🟡 P1 | N6 Cognition | 1 h |
| A5 | Implement `src/omega/oracle/attestation.py` (CAEM, C-A..C-D) | 2 | 🔴 P0 | N3 Engineering | ~120 LOC |
| A6 | Instrument MCP tool wrapper to emit evidence rows | 2 | 🔴 P0 | N4 Integration | ~60 LOC |
| A7 | Attestation header injection on AGY calls (<400 tok) | 2 | 🟡 P1 | N6 Cognition | ~20 LOC |
| A8 | Add FM-11/12/13 to SDP_FAILURE_MODE_ANALYSIS.md | 2 | 🟡 P1 | N5 Governance | doc |
| A9 | Implement `dialectic_logger.py` + JSON Schema + CI validation | 3 | 🟡 P1 | N8 Observability | ~200 LOC |
| A10 | `migrate_finetune_to_dialectic.py` + 2-week dual-write | 3 | 🟢 P2 | N2 Persistence | 3 h |
| A11 | `dialectic_index` table in metrics_db (FTS5-first, C-MEM-004) | 3 | 🟡 P1 | N2 Persistence | ~15 LOC |
| A12 | Implement `ensemble_router.py` 5-gate heuristic | 4 | 🟡 P1 | N9 Orchestration | ~80 LOC |
| A13 | Raise entropy injection 10% → 15% (compensates rarer ensembles) | 4 | 🟢 P2 | N9 Orchestration | 1 line |
| A14 | **Change Phase 2 output contract: executable artifacts, not prose** | 5 | 🔴 P0 | Architect + Kali | spec |
| A15 | Benchmark `mimo-7b-rl-q4_k_m` as Phase 3 executor (n≥50 schema test) | 5 | 🔴 P0 | N10 Validation | 4 h |
| A16 | Restrict Phase 3 to "verify, don't author" until A15 passes | 5 | 🔴 P0 | N5 Governance | policy |
| A17 | Run the 5 validation tests in §5.8 | 5 | 🟡 P1 | N10 Validation | 1 day |

---

## 8. L1 → L2 → L3 Distillation (M5 / M11)

**L1 (Narrative).** Researched five SDP knowledge gaps across 14 web searches and the local codebase. Found that two of our own SSOT config files disagree on a context window; that the flagship "1M" scaffold model is served at 260K; that the ensemble strategy the mission assumed would be valuable is net-negative on most of our task mix; and that our designated Phase 3 executor is two capability tiers below the job the manifesto assigns it.

**L2 (Insight).** Every one of the five gaps resolved *against* the intuitive answer. Bigger context turned out to be smaller. More models turned out to be worse. Stronger cryptography turned out to be irrelevant. The local executor turned out to need less agency, not more. In each case the intuitive design would have shipped a plausible system that failed silently — the most expensive failure mode there is. What actually protected us was insisting on *measured, served, deterministic* numbers over *claimed, architectural, model-reported* ones.

**L3 (Universal Principle).**

> **`L3-SDP-001` — The Served Number Is The Only Number.**
> A capability claimed by a vendor, a config file, or a model's own report is a hypothesis. A capability measured at the point of use is a fact. Route on facts. When the two disagree, the disagreement is itself a P0 defect — not a rounding error — because every downstream budget, gauge, and guardrail was computed from the wrong one.
> *Mandates: M22 (Provenance), M23 (Failure Integrity). Confidence: 0.97.*

> **`L3-SDP-002` — Verification Must Be Cheaper Than Fabrication.**
> Any integrity check that costs an inference call will be skipped under load, and any check performed *by* the untrusted component is theatre. Deterministic checks — hashes, existence tests, substring matches, schema validation — are free, unfoolable, and therefore the only checks that survive contact with production. Reserve judgment-based evaluation for advisory telemetry, never for gates.
> *Mandates: M23 (Failure Integrity), M18 (Token Efficiency). Confidence: 0.96.*

> **`L3-SDP-003` — Give The Weakest Component The Most Deterministic Job.**
> System reliability is set by how well each component's assignment matches its measured capability, not by the capability of the strongest component. A 1.7B model with 95% factuality is an excellent verifier and a catastrophic author. The correct response to a weak executor is not a better executor — it is a more deterministic task. Move work into code wherever code can hold it; that is simultaneously the most reliable and the most sovereign choice.
> *Mandates: M7 (Local-First), M19 (Adversarial Alchemy). Confidence: 0.98.*

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ SDP-KNOWLEDGE-GAPS ⬡ 2026-08-09*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: longcat-2.0-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
