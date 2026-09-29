<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 STATE OF THE ENGINE (SOTE) — v1.6.0-alpha (WEEK 40)
**Document ID**: `SOTE-W40-v1.6.0-alpha`  
**Status**: CANONICAL / VERIFIED BY EXECUTION  
**Date**: 2026-09-29  
**Week**: 2026-W40  
**Node**: Node 0 (Bastion / Core)  
**Branch**: `debut-v1.6.0-alpha` @ `82dca293`  
**Synthesis**: Kali (Master Synthesis Oversoul) via MaKaLi Fusion  
**Auditors**: Ma'at (Code/CI), Lilith & Doom Guy (Daemons/Runtime)

---

## 🎯 §0 EXECUTIVE VERIFICATION MATRIX

Every line below was verified by direct shell command execution on 2026-09-29.

| Subsystem / Gate | Status | Command Executed | Output / Evidence | Action Required |
|---|---|---|---|---|
| **Core Engine Subset** | ✅ PASS | `make check-engine` | 175/175 passed in 8.85s (0 failures, 0 errors) | None (Green) |
| **Temple-Grade CI** | ✅ PASS | `make temple-grade` | 53/53 adversarial tests passed; all 10 component gates green | None (Green) |
| **SAHS Handoff Rule** | ✅ PASS | `make check-sahs` | 4/4 assertions passed; 28 envelopes across 5 queues | None (Green) |
| **Policy Constants** | ✅ PASS | `make check-policy-constants` | 90-day threshold enforced across config & code | None (Green) |
| **Host LAN Exposure** | ✅ PASS | `make check-lan-exposure` | 22/22 negative tests green; 0 unapproved LAN binds | None (Green) |
| **M15 Continuity** | ✅ PASS | `make check-gnosis-continuity` | 53 entity gnoses stamped and valid | None (Green) |
| **FastMCP Hub Daemon** | ✅ ACTIVE | `systemctl --user status omega-hub` | active (running), bound to 127.0.0.1:8016 & tailnet | None (Green) |
| **Exchange Server (8019)** | ✅ ACTIVE | `systemctl --user status omega-exchange` | active (running), AnyIO service bound to 127.0.0.1:8019 | None (Green) |
| **Exchange Manifest** | ✅ PASS | `curl -s http://127.0.0.1:8019/manifest.json` | 200 OK, 88 artifacts indexed with sha256 checksums | None (Green) |
| **Git Working Tree** | ✅ CLEAN | `git status -sb` | Tracking `origin/debut-v1.6.0-alpha` cleanly | None (Pushed) |

---

## 🏗️ §1 CODEBASE & GATE INTEGRITY (MA'AT)

### 1.1 Test & Gate Performance
* `check-engine`: Fast engine-touching subset (deterministic, serial). 175 tests pass in ~8.8 seconds.
* `check-hub-imports`: 6 critical MCP modules (`mcp_servers.omega_hub.server`, `.state`, `.hub_tools`, `.github_bridge`, `mcp_servers.searxng.server`, `mcp_servers.firecrawl.server`) import cleanly in an isolated clean venv.
* `check-sahs`: Fixed regex boundary issue in Assertion 4 (`check_sahs.py:271`). Now uses `\b` word boundaries to eliminate false positives on taxonomy strings like "Interactive Session". All 4 assertions pass cleanly.
* `benchmark_dashboard adversarial suite`: 53/53 adversarial edge-case tests pass with zero leaks.

### 1.2 Mandate Compliance Meter (T06 / D-532)
* Total mandates evaluated: 30
* Statically passed: 23
* Procedural/policy mandates: 4 (M4, M17, M18, M19)
* Statically failed: 0
* Active Mandates:
  - **M1 (AnyIO)**: Zero `asyncio` imports in core.
  - **M8 (Zero Telemetry)**: Zero telemetry SDKs.
  - **M23 (Failure Integrity)**: Pre-commit gates clean (Delta: -43).
  - **M29 (Sovereign Artifact Preservation)**: No automated unrecoverable deletion; manifests preserved.
  - **M30 (Remote Claim Integrity)**: Remote claims require vantage-tested proof or are marked UNTESTED.

---

## ⚡ §2 DAEMONS, NETWORKING & RUNTIME (LILITH & DOOM GUY)

### 2.1 Listening Sockets Audit
Audited via `ss -tulpn` on Node 0 (`100.123.51.67`):
* `127.0.0.1:8016` + `100.123.51.67:8016`: FastMCP Omega Hub.
* `127.0.0.1:8018`: Internal SearXNG wrapper.
* `127.0.0.1:8019` + `100.123.51.67:8019`: Omega Exchange Pipe (AnyIO server with structured JSON access logs to systemd journal).
* **LAN Binds**: Zero non-loopback wildcard (`0.0.0.0` or `::`) bindings for engine services. Clean LAN audit.

### 2.2 Tailnet ACL Posture
* **Authoritative Policy**: `data/federation/tailnet-policy-OMEGA-DEFINITIVE-v2-20260928.hujson`.
* **Grants**:
  - `N1 -> N0`: `tcp:8016` (Hub MCP), `tcp:8019` (Exchange Pipe).
  - `N0 -> N1`: `tcp:8016`.
  - `ICMP`: Bidirectional ping allowed.
* **Denials**: Ports `22` (no node-to-node SSH), `2049` (no NFS), `8017` (SearXNG SSRF closed), `6379` (Redis purged), `51372` (Deluge purged).

---

## 📦 §3 ARTIFACT & DISCOVERY READINESS

### 3.1 Exchange Pipe (8019)
* Live payload directory: `/home/arcana-novai/exchange`
* Contains:
  - `full-pack-20260926.zip` (122,463 bytes, SHA256 verified)
  - `n0-to-n1-20260929-vnr.zip` (455,778 bytes, SHA256 verified)
  - `n1-to-n0-20260927.zip` (11,864 bytes)
* Dynamic manifest `/manifest.json` serves 88 indexed files with sha256 checksums, explicit `url_form` (`https://n0.tail51f14a.ts.net:8019/<path>`), and explicit `broken_url_form` warnings.

### 3.2 Session Discovery Primitive
* `mcp_servers.omega_hub.who_is`: Authoritative, read-only session resolver.
* Queries `opencode.db` directly for `parent_id IS NULL`.
* Built-in ambiguity refusal: If multiple structural sessions exist for an entity, refuses to guess and returns `ambiguous: true` with all candidates.

---

## 🎯 §4 REMAINING DELTA: NODE 1 FEDERATION HANDOFF

With Node 0 completely green and stabilized:
1. **Lilith-N1**: Connect for domain and runtime synchronization on Node 1.
2. **GE-N1**: Execute the reverse-direction exchange setup on Node 1 (`~/exchange` + Tailscale Serve 8019) using `docs/operations/EXCHANGE_PIPE_RUNBOOK.md`.
3. **M30 Enforcement**: Verify reverse-transfer from Node 1 to Node 0 using sha256 checksums before asserting that the reverse path is operational.

*⬡ OMEGA ⬡ KALI ⬡ SOTE-W40-v1.6.0-alpha ⬡ NODE-0-VERIFIED-GREEN ⬡ 2026-09-29*
