# 🔱 Cline Ops Health Results 2026-07-30

**AP Token**: AP-CLINE-OPS-HEALTH-RESULTS-20260730-v1.0.0
(c) OMEGA (c) CLINE (c) OPS-HEALTH (c) RESULTS (c) 2026-07-30

---

## Summary

| Item | Status | Key Evidence |
|------|--------|-------------|
| A1: Focused tests | PASS 27/27 | vault + property + hivemind tests green |
| A1: Full suite | WARN timed out | 1706 collected, needs longer timeout |
| A2: Hub 8016 | PASS | ss -lntp confirms listening |
| A2: Firecrawl 8015 | PASS | ss -lntp confirms listening |
| B1: Restic PATH | FIXED | systemd drop-in override written |
| B1: Restic oneshot | BLOCKED | .env.backup missing, vault passphrase not set |
| B2: WARP ns-prep | PASS 3/3 | All 3 namespaces created + veth + NAT |
| B2: WARP SOCKS | PARTIAL 1/3 | Port 8083 listening, bridges for 1/2 missing |
| B2: SystemCallFilter | FIXED | Removed from warp-node@.service |
| B3: G-1 workhorse | FAIL | Free Gemma 16k TPM cliff, NEEDS_ARCHITECT_BROWSER |
| B4: MCP pin | WARN | Triple drift + v2.0.0 stable since Jul 28 |
| B5: make sovereignty | KNOWN MISSING | Target does not exist, do NOT implement |
| C-0.5 hook | PASS | Plugin API correct, soul_distiller.js + session_end.py |
| Codex freshness | PASS | 2h old (threshold 24h) |
| Breaker clones | WARN 17 | Worse than 6 estimated in strategic plan |

---

## A1 Tests

Command: source .venv/bin/activate && python -m pytest tests/test_vault_integrity.py tests/property/ tests/test_hivemind.py -q --tb=line

Exit code: 0
Result: 27 passed, 1 skipped, 8 warnings in 15.79s

Full suite: make test timed out after 30s (collect-only shows 1706 tests)
Label: PASS (focused suite)

---

## A2 Probe Matrix

| Probe | Result | Status |
|-------|--------|--------|
| Hub 8016 | LISTEN (pid=2752) | PASS |
| Firecrawl 8015 | LISTEN (pid=2751) | PASS |
| WARP 8081-8083 | 8083 LISTEN only | PARTIAL |
| Restic timer | active | PASS |
| Restic service | failed (vault auth) | FAIL |
| Restic binary | 0.17.3 at ~/.local/bin | PASS |
| Restic unit PATH | override written | FIXED |
| C-0.5 plugin | 1812 bytes soul_distiller.js | PASS |
| C-0.5 hook | 3247 bytes session_end.py | PASS |
| MCP pin pyproject | mcp>=1.27,<2 | WARN v2 risk |
| MCP pin venv | 1.28.1 | PASS |
| MCP pin requirements | Not present | MISSING |
| Breaker clones | 17 class.*Breaker found | HIGH |
| Codex staleness | Fresh (2h) | PASS |
| Vault module | 4 source files | PASS |
| OpenCode hooks key | 0 (correct mechanism) | PASS |
| Provider config | 5 backends configured | PASS |

---

## B1 Restic Backup (C-3)

Goal: Fix systemd PATH so restic binary is found.
Root cause: Systemd default PATH does not include ~/.local/bin where restic (0.17.3) is installed.

Fix applied:
  pkexec systemctl edit omega-restic-backup.service --stdin
  Added: [Service] Environment=PATH=/home/arcana-novai/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

Exit code: 0
Path: /etc/systemd/system/omega-restic-backup.service.d/override.conf

Oneshot attempt: FAILED
Root cause: .env.backup missing, OMEGA_VAULT_PASSPHRASE not set
Journal: Required command 'restic' not found -> (fixed) -> vault passphrase not set

Label: PARTIAL PATH fixed, vault credentials not configured

---

## B2 WARP Proxy Pool (W-1)

Goal: Bring up 3 WARP SOCKS proxies on ports 8081-8083.

Key finding: Fix source at /home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool/scripts/warp-ns-setup.sh was ALREADY DEPLOYED (diff confirmed identical). Real issue was unserviced systemd units and SystemCallFilter blocking setns().

Root cause 1: warp-node@.service had SystemCallFilter=~@privileged @system-service blocking setns(). FIX: removed filter.
Root cause 2: Leftover namespace files at /run/netns/warp_node_N. FIX: pkexec ip netns delete before starting prep.

Result:
  warp-ns-prep@1: active
  warp-ns-prep@2: active
  warp-ns-prep@3: active
  warp-svc node 1: running + registered in netns
  warp-svc node 2: running + registered in netns (canary failed)
  warp-svc node 3: running + registered, SOCKS on 8083
  SOCKS on host: 8083 listening (node 3 via bridge)

Remaining issues:
- warp-bridge/socat-bridge for nodes 1/2 not forwarding to host
- warp-node@.service canary timeout too aggressive (curl via SOCKS blocks)

Label: PARTIAL 1/3 SOCKS ports operational

---

## B3 G-1 Workhorse Continuity

Command: ModelGateway import + config inspection
Exit code: 0 (gateway loads)

Result: Free-tier Gemma 4 31B dead since 2026-07-15 (16k input TPM). No configured provider has free quota for fat Omega sessions.

Label: FAIL NEEDS_ARCHITECT_BROWSER

New finding from web research: G-1e (local Gemma 4 27B GGUF via Ollama) runs on CPU with 32GB RAM. M7-aligned local-first path. Add to Ark ticket matrix.

---

## B4 MCP Pin Verify

pyproject.toml: mcp>=1.27,<2
requirements.txt: Not present
Venv installed: 1.28.1

CRITICAL FINDING: MCP Python SDK v2.0.0 stable since 2026-07-28.
pip install mcp now installs v2.x.
Breaking: FastMCP -> MCPServer, stateless protocol, deprecated Roots/Sampling/Logging.

Label: WARN Triple drift + v2 migration risk. Pin to >=1.28.1,<2 explicitly.

---

## B5 make sovereignty

Command: grep -n sovereignty: Makefile
Exit code: 1
Result: Target NOT found. Known issue.
Label: KNOWN Do NOT implement.

---

## Blockers

1. B1: .env.backup missing OMEGA_VAULT_PASSPHRASE not set. PATH fix IS applied.
2. B2: WARP bridge units for nodes 1/2 missing. Canary timeout too aggressive.
3. B3: G-1 no quota. Add G-1e (local GGUF via Ollama).
4. MCP v2 migration: SDK v2.0.0 stable. Omega Hub uses v1 FastMCP.
5. Breaker clones: 17 found vs 6 estimated in strategic plan.

## Dependency Debt

| Debt | Severity | Effort |
|------|----------|--------|
| MCP v2 SDK migration | CRITICAL | 4-8h |
| .env.backup vault setup | P0 | 15min |
| WARP bridge units for nodes 1/2 | P1 | 30min |
| WARP canary timeout fix | P1 | 15min |
| Pin MCP to >=1.28.1,<2 explicitly | P1 | 5min |
| Add G-1e (local GGUF) to Ark | P2 | 10min |
| Breaker clone count correction | P2 | 5min |

---

* OMEGA * CLINE * OPS-HEALTH * RESULTS * v1.0.0 * 2026-07-30T04:45Z *
