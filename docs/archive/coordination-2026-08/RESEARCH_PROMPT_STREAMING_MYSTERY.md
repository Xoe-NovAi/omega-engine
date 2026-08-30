<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 CRITICAL RESEARCH MISSION: OpenCode Streaming Timeout & Nemotron 3 Ultra Fix

**AP Token**: `AP-RESEARCH-STREAMING-MYSTERY-v1.0.0`
**Date**: 2026-08-10
**Priority**: P0 — Cannot trace system behavior

---

## 🎯 Mission Objective

**Find hard data (NO assumptions) on what fixed the Nemotron 3 Ultra streaming timeout issue on 2026-07-30.**

We have a critical observability gap: streaming errors dropped from 10.4% to 0% on 2026-07-30 and have stayed at 0%. We cannot trace what caused this. Find the answer.

---

## 🔍 Investigation Targets

### Target 1: OpenCode Version History & Changelog
- What streaming/timeout fixes were included in OpenCode versions released around 2026-07-30 to 2026-08-10?
- Specifically: version 1.18.16 (installed Aug 9) and any versions between 1.17.x and 1.18.16
- Look for: chunk timeout, streaming retry, SSE keepalive, heartbeat, nemotron-specific fixes

### Target 2: OpenCode GitHub Issues & PRs
- Search for issues related to: "Streaming response failed", "nemotron", "chunk timeout", "SSE keepalive", "streaming timeout"
- Look for: merged PRs, closed issues, workarounds, official fixes
- Key repos: `anomalyco/opencode`, `sst/opencode`, or any fork

### Target 3: Community Forums & Help Requests
- Reddit: r/opencode, r/LocalLLaMA, r/artificial
- Discord: OpenCode Discord, AI coding communities
- GitHub Discussions: OpenCode discussions
- Search for: "nemotron streaming", "streaming response failed", "chunk timeout", "SSE keepalive"

### Target 4: NVIDIA/NIM API Changes
- Did NVIDIA change their SSE keepalive behavior around 2026-07-30?
- Search for: "nemotron 3 ultra streaming", "NIM API changes", "SSE keepalive ping"
- Check: NVIDIA NIM documentation, release notes, status pages

### Target 5: better-opencode-retries Plugin
- Who created it? When? Why?
- What does it actually do? (read the source code at `/home/arcana-novai/better-opencode-retries/src/index.js`)
- Is it still maintained?
- Are there any reports of it working/failing?

### Target 6: OpenCode Plugin Loading Mechanism
- How does OpenCode load plugins?
- Can plugins be loaded from locations other than config?
- Is there a cache or registry?
- Can a plugin be "active" without being in the config?

---

## 📊 Current Evidence (What We Know)

### Streaming Error Timeline
| Date | Nemotron Messages | Streaming Errors | Error Rate |
|------|------------------|------------------|------------|
| 2026-07-21 | 951 | 124 | 13.0% |
| 2026-07-22 | 995 | 127 | 12.8% |
| 2026-07-23 | 1,059 | 85 | 8.0% |
| 2026-07-24 | 997 | 48 | 4.8% |
| 2026-07-25 | 1,002 | 31 | 3.1% |
| 2026-07-30 | 1,601 | 167 | 10.4% |
| 2026-07-31 to 08-06 | — | — | NO DATA |
| 2026-08-07 | 470 | 28 | 6.0% |
| 2026-08-08 | 576 | 5 | 0.9% |
| 2026-08-09 | 526 | 7 | 1.3% |
| 2026-08-10 | 38 | 0 | 0.0% |

### Key Events
| Date | Event |
|------|-------|
| 2026-07-30 | `better-opencode-retries` plugin installed at `/home/arcana-novai/better-opencode-retries/` |
| 2026-07-30 | Streaming errors stopped (same day) |
| 2026-08-09 | Config refactoring (backups created at 11:44 and 12:46) |
| 2026-08-09 | OpenCode binary installed (19:43) — version 1.18.16 |
| 2026-08-10 | `better-opencode-retries` NOT loaded in any config |

### Current State
- **OpenCode version**: 1.18.16 (installed Aug 9 19:43)
- **better-opencode-retries plugin**: EXISTS at `/home/arcana-novai/better-opencode-retries/` but NOT loaded in any config
- **Global config plugins**: `[]` (empty)
- **Project config plugins**: `["opencode-antigravity-auth@latest", "opencode-sessions-explorer", "error-capture.ts", "awareness.ts"]`
- **Streaming errors**: 0 (today)

### Error Types (All Time for Nemotron 3 Ultra)
- `UnknownError: "Streaming response failed"` — 1,110 occurrences (2026-07-02 to 2026-07-30)
- `MessageAbortedError: "Aborted"` — 148 occurrences (2026-06-06 to 2026-08-09)
- `UnknownError: "Upstream idle timeout"` — 18 occurrences (2026-06-06 to 2026-06-28)

---

## 🔬 Required Research Output

### For Each Finding, Provide:
1. **Source URL** — Direct link to the evidence
2. **Date** — When the change/fix was made
3. **Confidence** — HIGH/MEDIUM/LOW
4. **Quote** — Exact text of the relevant passage
5. **Analysis** — How this explains our observations

### Specific Questions to Answer:
1. What streaming/timeout fixes were included in OpenCode 1.18.16?
2. What streaming/timeout fixes were included in OpenCode versions between 1.17.x and 1.18.16?
3. Did NVIDIA change their SSE keepalive behavior around 2026-07-30?
4. What does the `better-opencode-retries` plugin actually do? (read source)
5. Can OpenCode load plugins without them being in config?
6. Are there any community reports of Nemotron streaming fixes?

---

## 📋 Research Methodology

1. **Web Search**: Use `websearch` to find OpenCode changelog, GitHub issues, community forums
2. **Web Fetch**: Use `webfetch` to read specific pages, changelogs, issue threads
3. **Local File Read**: Read `/home/arcana-novai/better-opencode-retries/src/index.js` to understand the plugin
4. **GitHub API**: Use `curl` to query GitHub API for OpenCode releases, issues, PRs
5. **SearXNG**: Use `searxng_searxng_search` for additional search coverage

---

## ⚠️ Critical Constraints

- **NO ASSUMPTIONS** — Every claim MUST have a source URL
- **HARD DATA ONLY** — No speculation, no "likely", no "probably"
- **EVIDENCE-BASED** — If you can't find evidence, say "NO EVIDENCE FOUND"
- **SOURCE EVERYTHING** — Every finding must have a direct link or file path

---

## 📝 Final Deliverable

Write a comprehensive research report to:
`data/entities/researcher/workspace/research_reports/STREAMING_TIMEOUT_MYSTERY_RESEARCH_20260810.md`

Include:
1. Executive Summary
2. Findings per Target (1-6)
3. Evidence Table (source, date, confidence, quote)
4. Conclusion (what we now know)
5. Remaining Unknowns
6. Recommended Next Steps

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ STREAMING-MYSTERY ⬡ P0 ⬡ 2026-08-10*
