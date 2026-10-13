<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# Web Research Part 3/3 — Safety, Storage, Inference, Observability (2026-10-13)

## 6. Governance Decay — the paper behind our P0 (numbers inside)

**Source**: arXiv 2606.22528 (Chen, v2 Jun 2026) — abstract + history verified.

- **Result**: ConstraintRot benchmark, 1,323 episodes, 7 model families.
  Violation 0% in-context → **30% after compaction** (59% worst model).
  Constraint survives summary → 0%; dropped → **38%**.
- **Attack**: Compaction-Eviction — adversarial content biases the summarizer
  to omit a legitimate policy; optimized injections defeat EVERY model tested.
- **Mitigation**: Constraint Pinning (quarantine constraints from lossy
  compaction) restores 0% — training-free. This is the mechanism our
  compaction-immune `CONSTRAINTS.md` proposal implements; the paper is its
  empirical license.
- **Omega relevance**: P0 stays P0. Additionally: our Headroom semantic
  compression for tools/RAG is itself a compaction surface — pin constraints
  *before* routing context through it, or the compressor becomes the evictor.

## 7. SQLite corruption — the official catalog backs TRUNCATE-on-NFS

**Source**: sqlite.org/howtocorrupt (updated 2026-04-13).

- File-locking failures (§2) are the NFS story: broken/missing locks,
  close()-cancels-advisory-locks, two processes on different locking
  protocols, unlink/rename-while-in-use. WAL's `-shm` shared memory is the
  concrete incoherence (§8.1 WAL write race, §8.4 mode-switch corruption).
- Rollback journal (DELETE/TRUNCATE) degrades to plain file I/O + POSIX
  locks — no shared memory to go incoherent. TRUNCATE over DELETE: same
  safety, avoids file growth churn on repeated transactions.
- **Omega relevance**: RES-GAPS gap-17 stands as written
  (`PRAGMA journal_mode=TRUNCATE` on NFS). Also cross-links our reclaim
  lore: "never `mv` under a live reader" is §2.5 (unlink/rename while in
  use) — Gate 4 enforces the official guidance, not just our scar tissue.

## 8. llama.cpp RPC — upstream says fragile/insecure, verbatim

**Source**: ggml-org/llama.cpp `tools/rpc/README.md` (live tree).

- *"This example and the RPC backend are currently in a **proof-of-concept
  development stage**. As such, the functionality is **fragile and insecure.
  Never run the RPC server on an open network or in a sensitive
  environment!**"*
- Default exposure is maximal: all accelerator devices (or CPU if none);
  weights + KV distributed proportionally unless `--tensor-split` overrides.
  RDMA/RoCE + Thunderbolt transports widen the surface further.
- **Omega relevance**: L4 distributed inference stays gated on SPIRE mTLS —
  now with an upstream quote to end any "just try it on the tailnet"
  argument. Even tailnet-trusted RPC deserves mTLS + `--tensor-split`
  pinning before first use. (GHSA-j8rj-fmpv-wcxw details live in the
  advisory DB, not the README — cite the README for posture, the advisory
  for the CVE.)

## 9. OTel GenAI conventions — moved house

**Source**: opentelemetry.io/docs/specs/semconv/gen-ai (v1.44.0).

- The conventions **moved out of the main repo** into a dedicated
  `open-telemetry/semantic-conventions` GenAI area ("this page is no longer
  maintained"). Any doc deep-linking the old in-repo path will rot — link
  the new location.
- Structure covers spans (inference request shape: model id, token
  in/out, cost attributes), metrics instruments, and a dedicated **MCP
  conventions** section — the last is directly relevant to instrumenting
  our Hub. Local Prometheus = OTel Collector with Prometheus exporter,
  no cloud span exporter configured — standard pattern, no new research
  needed to design it.
- **Omega relevance**: P2 (OTel spans + `/metrics` alongside `latest.json`)
  unblocked on spec location. Read the moved repo, not the stale page.

## 10. ACON — compression that *improves* success, not just shrinks

**Source**: arXiv 2510.00615 (Kang et al., ICML 2026, v3 Jun 2026).

- **Numbers**: 26–54% peak-token reduction on AppWorld/OfficeBench/Multi-QA
  **while improving task success** over baselines; smaller LMs gain up to
  46% as long-horizon agents (distraction mitigation, not just savings).
- **Method**: optimization in *natural language space* — iteratively refine
  compression guidelines from the agent's own failure analysis; no
  fine-tuning (works for proprietary models); distill the compressor into
  smaller models to cut overhead.
- **Omega relevance**: this is the paper our Headroom-integration workstream
  (HR) wants to be measured against. Headroom semantic compression should
  benchmark success-rate delta, not just token delta — ACON proves the
  former is achievable. Also pairs with §6: compress observations/history,
  PIN constraints.

## 11. Tool-chain health (load-bearing for M23)

During this research the sovereign chain collapsed tier by tier:
`library_discovery` 10/10 empty or circuit-open → SearXNG connection
failed → Firecrawl `No module named 'firecrawl'` → Exa 401 invalid key.
Only direct `fetch_web_content` worked. **Actions**: rotate the Exa key,
health-check the SearXNG daemon, reinstall/rewire the Firecrawl module —
until then, web research is single-threaded through fetch, and any
"no results" claim from the upper tiers is suspect.

*⬡ OMEGA ⬡ CLINE ⬡ WEB-RESEARCH-20261013 ⬡ 3/3 ⬡*
