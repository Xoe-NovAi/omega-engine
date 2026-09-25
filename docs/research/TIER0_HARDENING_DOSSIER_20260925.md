# Tier-0 Hardening Dossier — Research Folio (Humboldt, 2026-09-25)

**Mode:** research-only. **Legend:** `[VERIFIED-LIVE]` = fetched this session; `[REPORTED-NOT-VERIFIED]` = excerpts only.

## 1. Ollama 0.33.3 → 0.34.4 — CONDITIONAL GO

| Release | Changes (load-bearing only) |
|---|---|
| 0.33.3 | Report cached prompt tokens (observability — free verification instrument for persona-prefix reuse) |
| 0.34.0 | ChatGPT Desktop integration; faster structured outputs (Apple Silicon); OpenAI-compatible tool-search + compaction |
| 0.34.1 | MLX safetensors `create` stable; GGUF creation requires llama.cpp tooling; repeat-token runaway threshold → 100; `/api/tags` 3.1s → 294ms; **`typical_p` deprecated — 0.34.1 REJECTS entire requests carrying it, even passively (issue #18542)** |
| 0.34.2 | First-run setup shared with desktop app; fixed MLX speculative memory growth |
| 0.34.3 | `GET /api/show` advertises thinking levels; HuggingFace pull fix |
| 0.34.4 | **Single-pass structured outputs on thinking models** (PR #18479, previously two-pass); intermittent "model not found" fix; Qwen 3.8 prompt speedup (Apple Silicon) |

**No release note in-window mentions thread-pool, spin-wait, n_threads derivation, cgroup, or CFS** — provisional: no stated change to convoy mechanics (absence-of-evidence, not proof; compare-diffs must be grepped). **No OLLAMA_* env renames in-window.** `typical_p` removal is API/validation-layer (sampler chain still shows the stage in old logs). Downgrade path: reinstall prior binary + restart; model store (`~/.ollama/models`, digest-named blobs) is version-independent across minors. **Rebench gate: mean ≥ 13.0 t/s (10% guard-band), no run < 12.5, else roll back.**

**Preconditions (all verified-or-grepped before upgrade):** A) `typical_p` sweep across Modelfiles/configs/harness — zero hits; B) snapshot (`ollama list`, manifests tar, unit, `.env.ollama`); C) per-hop compare grep for `n_thread|GOMAXPROCS|cgroup|cpuset|discover|typical_p|context_shift|gguf|quantize` + bundled llama.cpp builds.

## 2. CVE full texts + reconciliation

**CVE-2026-27940 / GHSA-3p4r-fq3f-q74v (High 7.8, CVSS `AV:L/AC:L/PR:N/UI:R`):** `gguf_init_from_file_impl()` computes `mem_size = (n_tensors+1)*overhead + ctx->size` WITHOUT the overflow check the CVE-2025-53630 fix added to the accumulation loop. Two large I8 tensors push `ctx->size` near SIZE_MAX; final add wraps small (PoC: 1,072 bytes); undersized alloc; `fread` writes 528+ attacker bytes past heap. Glibc slow-path bypass → RCE (`system("/bin/sh")`, root, Ubuntu 22.04). Affected ≤ b8145, patched ≥ b8146. **Whether Ollama 0.33.3's bundle contains the fix: UNVERIFIED** (needs release→bundle mapping; likely yes given March fix vs September release — do not assert).

**GHSA-96jg-mvhq-q7q7 = CVE-2026-33298 (High 7.8, NOT a second 27940):** `ggml_nbytes()` `(ne[i]-1)*nb[i]` overflows 64-bit (PoC F32 `ne=[1024,1024,2^42+1,1]` → term = 2^64 = 0 → ~4MB allocated for exabyte-logical tensor → heap overflow). Affected < b7437, patched b7824.

**21869 severity conflict RESOLVED:** GitHub page header says Low 0.0 (`C:N/I:N/A:N`) while its own Summary/Impact prose says "Severity: Critical… RCE" — **the machine-readable block is a scoring-form error.** CNA record: **8.8 High**; NVD enrichment: 9.8 Critical. CNA vs NVD differ by exactly one metric (UI:R vs UI:N — the `--context-shift` + context-fill precondition). **Working severity: 8.8 High** (CNA authoritative over NVD); note 9.8 as upper bound; disregard the header. Fix: patched ≥ c78fb90. Exposure note: this is a *llama.cpp server* flaw (raw `n_discard` forwarding) — Ollama exposure depends on an unfound forwarding path (open question).

**Ollama-side:** CVE-2026-5757 "Bleeding Llama" (unauthenticated remote heap-disclosure via quantization engine, exfil via registry API, ~300k exposed, CERT unable to reach vendor, **NO patch**) → bind loopback + firewall + vetted models only. CVE-2026-85180 SSRF on pull (window 0.30.0–0.33.2 → **0.33.3 probably just outside**, fix release unconfirmed; 0.34.3-rc1 allowlist language consistent with fix landing in 0.34 line). CVE-2026-65315 (sub-1KB GGUF → OOM server-kill; treat 0.33.3 as exposed until parser-fix version pinned). CVE-2026-86289 (fixed 0.31.2-rc1 → **0.33.3 clear**, one-line verify).

**OWUI v0.11.3 trio — all clear subject to two config checks:** CVE-2026-0767 **REJECTED, not a vulnerability** (describes HTTP, not OWUI; ZDI agreed; no action provided TLS terminates :3000). CVE-2026-44549 stored-XSS (≤0.7.2, patched 0.8.0; regression -45318 fixed 0.9.3; 0.11.3 postdates both). GHSA-4r2p (stored Pyodide XSS → RCE chain, <0.10.0, patched 0.10.0) — **confirm `ENABLE_PYODIDE_FILE_PERSISTENCE` is unset/false.**

**GGUF verification practices (2026, layered — no single control suffices, all trigger at parse time):** digest-pin at rest (blob filenames ARE sha256 — recompute vs manifest); registry/commit pin at fetch (`revision=<commit-hash>`, never branch/tag; `ollama pull model@sha256`); quarantine-before-load (isolated, resource-capped context; no secrets in env); provenance record per model (source URL, commit, digest, date). **No universal GGUF signature scheme exists in Ollama's path** — digest + commit-pin + quarantine is the achievable triad. Tier-0: add `models.manifest` + pre-upgrade `ollama list` + blob-hash spot check to the runbook.

## 3. Budget-rule restatement (replacement wording)

> **Thread-budget rule:** Set inference threads from the *effective* CPU budget (min of cgroup quota, cpuset size, and schedulable cores), never from host core count alone; oversubscribing threads beyond the budget convoys llama.cpp's spin-wait barriers against CFS throttling and collapses throughput. *Current measured instance (re-derive on any change): i7-13620H systemd unit, `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8` = 14.4 t/s; narrowing to physical-P-cores-only or raising threads beyond the budget reproduces the collapse.*

**Mechanism (verified):** persistent llama.cpp thread pool parked on a spin barrier; cgroup `cpu.max` = quota+period (average, not parallelism cap) — exceeding quota deschedules ALL threads until refill; N spinning threads burn quota without progress = convoy. Go is moving GOMAXPROCS toward min(logical, affinity, quota) with auto-updates — Ollama's plausible fix shape.

**5-line verification (any future machine):** (1) record budget B = min(quota CPUs, cpuset count, schedulable cores); (2) bench at B ×3; (3) repeat at B/2 and 2B, keep best mean, reject >10% below best; (4) 3 runs within ±5%, `cpu.stat nr_throttled` flat; (5) file the instance line in docs + Well. **Whether 0.34.x ships quota-aware n_threads: no evidence either way** — treat 0.33.3 behavior as 0.34.4 behavior until the compare-grep proves otherwise.

## 4. MCP Tasks verdict: HYBRID

SEP-2663 (`io.modelcontextprotocol/tasks`): opt-in per request, server advertises via `server/discover`; immediate `CreateTaskResult` (taskId, TTL, poll interval); poll `tasks/get`; `tasks/cancel` (cooperative); `tasks/update` mid-flight; terminal states immutable; `resultType` required; persistence explicitly left to deployers (reference SDKs in-memory only; Redis/docket or `mcp-durable-tasks` for durability). **FastMCP serves Tasks TODAY** (`pip install "fastmcp[tasks]"`, `@mcp.tool(task=True)`, legacy clients get sync behavior transparently). **No evidence any host (OpenCode/Cline/Antigravity/Claude Code) negotiates it as a client** — treat host support as unverified/absent. **Verdict: keep the curator on systemd-timer + sync tools now; make omega-hub Tasks-capable at next FastMCP touch (no-regret, backward-compatible); promote to durable backend only after a live handshake proves host support. Do NOT gate Tier-0 on Tasks.**

## 5. Speculative decoding: JUSTIFIED PUNT (Ollama-native)

No verified CPU-only sub-16GB small-model result exists. Credible multipliers (1.46–2.10×) all come from GPU/unified-memory pipelines with 70B targets — opposite bottleneck to our CPU-only DDR5-single-channel 4B regime. **Ollama does not support draft models in 0.34.x** (no knob surfaced); an A/B is executable only via `llama-server --model-draft` CLI. Design exists if wanted (same-family ≤0.5B draft, `--draft-max 5`, 20+ prompts, adopt iff ≥+15% sustained + acceptance ≥55% + 2GB swap clearance) — but the CLI answers a question the production path cannot consume. **Punt until Ollama advertises draft support or the 32GB upgrade lands.**

## 6. Execution order (Tier-0)

0. Snapshot everything → 1. `typical_p` sweep → 2. compare-grep (bundle map, SSRF allowlist, parser fix) → 3. network posture NOW (loopback bind, firewall, vetted registries) → 4. upgrade → 5. rebench + probes (**the real go/no-go**) → 6. budget-rule docs + Well update → 7. OWUI pin + Pyodide/TLS verify → 8. rollback receipt even on success. Rollback short-circuits any failing gate.

## 7. Operator decisions

(1) Approve the conditional-go window + 10% guard-band vs exact-14.4 parity. (2) Confirm where TLS terminates for :3000. (3) Authorize `fastmcp[tasks]` on omega-hub (zero client-visible effect). (4) CLI-only spec-decoding A/B vs justified punt (punt recommended). (5) Grants-vs-ACLs timing. (6) `ENABLE_PYODIDE_FILE_PERSISTENCE` must remain unset.
