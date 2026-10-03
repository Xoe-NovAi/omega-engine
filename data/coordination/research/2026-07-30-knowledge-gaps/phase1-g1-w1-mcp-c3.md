<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Phase 1 — G-1 / W-1 / MCP / C3-6 Research

**Timestamp**: 2026-07-30T06:10Z  
**Status**: Web research + live truth synthesis

## 1. G-1 Workhorse continuity

### Current live truth
- Free Gemma 4 31B 16k input TPM cliff remains real from prior forensic evidence.
- Current ports: Hub 8016, Firecrawl 8015, WARP 8083 only.
- MCP 1.28.1 confirmed installed; pin present.

### Web research synthesis
- **Google AI Studio billing**: Free tier exists; paid tiers start at Tier 1 with a $250 cap, Tier 2 at $2,000 after $100 paid usage. Rate limits are spend/RPM/TPM/RPD based and per-project. Billing often removes free-tier caps, but whether it specifically restores Gemma-model fat-session TPM is not confirmed in snippets.  
- **Antigravity OAuth / frontier models**: research docs indicate this path exists, requires browser OAuth login, and is a recommended alternate fat-session path.  
- **Local Gemma 4 27B via Ollama**: multiple 2026 setup guides confirm Gemma 4 27B and smaller sizes run on CPU+RAM. CPU-only inference is possible; quality/speed depend on quantization and hardware. Ryzen 5700U + 32GB RAM is plausible but slow for 27B-class workloads without GPU offload.  
- **G-1e viability**: remains viable as a local-first path, but introduces latency vs cloud and still needs OS-level Ollama setup validation.

### Open knowledge gaps after research
- Exact AI Studio rate-limit table for Gemma 4 31B today: need live AI Studio rate-limit page for current TPM/RPM values if billing path chosen.
- Antigravity OAuth current model catalog + pricing unknown from current scrape; need live provider list.
- Local Gemma 4 27B CPU throughput on 5700U/32GB: need benchmark rather than generic guide.

## 2. W-1 WARP proxy pool

### Current live truth
- Only 8083 is listening.
- `warp-ns-prep@1/2/3` are active per prior results; node/bridge bring-up is incomplete.
- `warp-svc` in-container status unknown from recent probes.

### Web research synthesis
- Multiple community wrappers exist (`warp-svc`, WARProxy, dockerized Cloudflare WARP SOCKS5). That implies WARP as SOCKS is viable and widely replicated.
- Reliability focus areas: license/registration state, bridge unit health, distinct exit IP validation, canary timeout tuning.

### Open knowledge gaps after research
- Cloudflare account license/renewal state for free WARP nodes is not machine-probed.
- Bridge unit config/status for 8081/8082 is unverified in this pass.
- Whether 3 distinct exit IPs are achievable on this host/network.

## 3. MCP v2 / FastMCP migration

### Current live truth
- Repo currently uses `mcp` python SDK v1 path: `mcp.server.fastmcp`.
- Installed: 1.28.1; schedule pins `<2`.

### Web research synthesis
- MCP Python SDK v2.0.0 targeted stable around 2026-07-27/28.
- 2026-07-28 spec revision drops session handshake, adds Tasks/Apps extensions, deprecates Roots/Sampling/Logging.
- FastMCP standalone is now part of MCP SDK lineage; `gofastmcp` also exists.
- Streamable HTTP is now the default/standard transport; SSE deprecated.

### Open knowledge gaps after research
- Exact Hub code delta to v2 on `:8016` plus Firecrawl delta still needs spike.
- Client configs needing repoint for OpenCode/Cline not yet inventoried in this pass.
- Rollback plan is documented in schedule but not rehearsed.

## 4. C3-6 Backup verification

### Current live truth
- restic timer active, service failed since 01:34Z.
- `.env.backup` missing; vault passphrase not set.

### Web research synthesis
- `restic check` validates repo structure but not full data readability.
- `restic check --read-data` is thorough but slow.
- Best-practice stack: `check` + periodic `restore` smoke test to `/tmp` and selective file validation.
- 2026 self-hosted guides recommend automated restore smoke + storage backend health checks.

### Open knowledge gaps after research
- Actual repo path/repo existence unknown until vault/env fixed.
- Restore smoke cadence not chosen.
- Whether to add `--read-data` to gate script is a cost/time tradeoff on current dataset size.

## 5. Structural/code gaps confirmed from repo scan
- Breaker classes: **18** hits (`rg class.*Breaker/breaker`) in `src/omega` + `mcp_servers`; strategic plan says 17. Incremental gap: +1 found in `workers/background_researcher/distiller.py` and `ingestion/pipeline.py` and `research/sandbox.py`.
- `yaml.safe_load` usage: **60** files. Audit should focus on async hot paths, not all 60.
- `anyio.to_thread.run_sync` is present in many files, suggesting partial M1 compliance, but `soul_updater.py` and some registry/workspace paths still use sync I/O at write time; need targeted audit for actual bottleneck paths.

## 6. Recommended next actions (knowledge resolution)
1. **G-1**: Architect provides one decision: billing, Antigravity OAuth, or local GGUF. Cline/Grok cannot decide.
2. **W-1**: One privileged pass to validate/bring bridges online, then canary timeout fix.
3. **MCP**: Approve M1 spike only after doc sanity stable; keep pin `<2` until smoke green.
4. **C3-6**: After `.env.backup`, add weekly/monthly `restic check` + quarterly restore smoke-test policy.
5. **Breaker unification**: freeze current count at 18, update strategic plan number, then proceed with pybreaker migration after doc sanity.

---
*⬡ OMEGA ⬡ CLINE ⬡ KNOWLEDGE-GAP RESEARCH ⬡ PHASE 1 ⬡ 2026-07-30*