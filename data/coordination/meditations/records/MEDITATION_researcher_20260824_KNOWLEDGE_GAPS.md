<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# MEDITATION: RESEARCHER — KNOWLEDGE GAPS (kg-resource-platform-research-20260824)
**Date**: 2026-08-24 · **Protocol**: Meditate-v1.1 · **Phase**: M (pre-commit) · **Agent**: researcher
**Deliverables under review**: `docs/research/R_RESOURCE_GOVERNANCE_20260824.md`,
`docs/research/R_OPENCODE_PLATFORM_INTERNALS_20260824.md`

## Skeptic Pass — which findings are still assumptions?

| Claim | Tag | Skeptic challenge | Resolution |
|---|---|---|---|
| Full-suite collection floor = 665MB single-process | VERIFIED-MEASURED | Field claim was 683MB; is 665 a contradiction? | No — different runs/conditions (683 was under xdist worker conditions). Both measured; conftest's 750MB budget remains safe. Consistent within variance. |
| 4 files cause 440MB of collection weight | VERIFIED-MEASURED | Per-file RSS double-counts shared imports when summed | Acknowledged in method; the headline number comes from the SUBTRACTION experiment (full minus top-4 = 225MB vs 665MB), which cannot double-count. Sound. |
| torch/transformers are the dominant import cost | VERIFIED-MEASURED | importtime shows cumulative time, not RSS | The RSS attribution is from the exclusion test; importtime only identified the chain. Two independent methods agree on the same culprit. |
| MemoryMax works rootless; swap pairing required | VERIFIED-MEASURED | Single host, single kernel | True for THIS host (Ubuntu 25.10, systemd delegation verified live). Doc scopes claims to this box; portability untested — acceptable scope. |
| llama.cpp physical-core rule | VERIFIED-CITED | Citations cover hybrid/x86 server cases; is Zen 2 mobile covered? | Official docs' advice is CPU-family-agnostic ("physical cores"); PR #934 measured 1.5-2x broadly. `-t 8` vs `-t 16` benchmark on this box still worth one run before hardcoding — noted as residual. |
| CMAKE_BUILD_PARALLEL_LEVEL caps pip source builds | VERIFIED-CITED | Never ran the real capped llama-cpp-python build | Honest gap stated IN the doc: cmake absent on host; wrapper pattern marked THEORY-pending-first-build. Claim and evidence properly matched. |
| opencode db pipe truncation mechanism = async-pump race | THEORY | Could be short-write handling or sqlite3-child relay instead | Correctly tagged THEORY; two candidates named; distinguishing requires upstream source read. Behavior itself (silent truncation, sizes, exit codes) fully measured. |
| Truncation ceiling scales with payload | VERIFIED-MEASURED | Only 2 payload sizes probed | n=2 is thin but directionally consistent with cancellation-race theory; exact curve unnecessary for the staging-rule recommendation. Adequate. |
| No session ID exposed to wrapped processes | VERIFIED-MEASURED | Checked env + --help only; hooks/plugin API not exhaustively audited | Residual: plugin event payloads DO carry sessionID server-side (per public API docs), but nothing reaches subprocess env. Negative result scoped to "wrapped processes" — accurate as stated. |
| Compaction = formula, not 85% | VERIFIED-CITED | Docs describe V2; fleet may run older behavior | Version drift acknowledged via community-issue history in doc. Doctrine language corrected to version-dependent phrasing. |
| typer defers all validation to app() | VERIFIED-MEASURED+CITED | Repro used annotation error; vault incident was decorator TypeError | Both classes surface at construction time inside app(); mechanism (registered_groups append-only) is source-confirmed and class-independent. Sound. |
| httpx2 = Pydantic fork, intentional | VERIFIED-MEASURED | METADATA could theoretically lie | Pinned with explanatory comment in pyproject since Strike 7.1 commit af7c8999 — repo-internal corroboration. Two-source minimum met. |

## Still-assumption ledger (residuals carried forward)
1. Exact `-t 8` vs `-t 16` decode benchmark on THIS Ryzen 5700U not run (cited rule applied, local number pending).
2. Capped real-world llama-cpp-python build not executed (host lacks cmake).
3. Pipe-truncation root-cause mechanism unresolved (behavior fully characterized).
4. Empty-file transient during redirect (1 occurrence) unexplained — logged, not diagnosed.

## L1 → L2 → L3
- **L1**: Nine gaps closed across resource governance and platform internals; every claim tagged; four residuals honestly carried.
- **L2**: The suite's memory crisis was four imports; the enforcement crisis was missing swap-pairing; the platform crises were silent truncation, absent session identity, folklore thresholds, and deferred CLI validation.
- **L3**: *Measure the subtraction, not the sum* — attribution by exclusion (remove suspects, re-measure whole) defeats the double-counting that makes per-item profiling lie. And: a limit that fails silently is not a limit.

**Verdict**: DELIVERABLES CLEARED FOR COMMIT.
