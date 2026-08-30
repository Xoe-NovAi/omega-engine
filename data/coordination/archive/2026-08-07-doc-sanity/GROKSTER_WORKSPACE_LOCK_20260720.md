<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Grokster Workspace Lock
**Domain**: grokster-exploration
**Channel**: grokster
**Entity**: grokster
**Acquired**: 2026-07-20T19:59:34.775823Z
**TTL**: 7200 seconds (2 hours)
**Expires**: 2026-07-20T21:59:34.775823Z
**Session**: ses_bbf049be6360

## Scope
- Grok ecosystem research & reconnaissance
- Grok Build CLI codebase audit (`third_party/grok-build/`)
- ACP protocol handshake validation
- Headless mode testing
- Fleet architecture design (16 accounts)
- Self-search reflex architecture
- Web Grok Project persona specification

## Exclusive Rights
- Read/write `data/entities/grokster/**`
- Read/write `data/coordination/GROKSTER_*`
- Spawn Grok CLI / Web Grok subagents via Hivemind
- Post to Hivemind channel `grokster`
- Access Omega-Vault for Grok credentials (when provisioned)

## Renewal
Auto-renew on heartbeat (`omega-hub_hivemind_heartbeat`) every 5-10 minutes during active work.
Manual renewal: `omega-hub_hivemind_workspace_lock_acquire` with same domain.

## Release
On session end: `omega-hub_hivemind_workspace_lock_release`