# Ma'at N0→N1 Handoff and Federation Evidence Report

**Date:** 2026-09-24 UTC  
**Entity:** Ma'at / Build Oversoul  
**Model:** `space-bunny-free`  
**Status:** **BLOCKED FOR PROMOTION; QUARANTINE EVIDENCE COMPLETE**

## Scope

This report records the independent N0-03 live omega-hub inventory and the readiness/conflict assessment for the N0→N1 handoff. It supersedes reliance on historical tool-count claims and proposed filenames.

## Evidence location

The quarantine-safe evidence bundle is located at:

```text
data/federation/quarantine/MAAT_N0_N1_EVIDENCE_20260924/
```

The bundle contains runtime evidence, a fresh tool inventory, package integrity inventory, conflict/blocker report, and a passing `SHA256SUMS` ledger.

## Live N0-03 result

- `omega-hub.service`: `active/running`.
- `/health`: `healthy`.
- Live listener: `0.0.0.0:8016`.
- Fresh local MCP `initialize`: HTTP 200 JSON-RPC result; server reported `Omega Core Hub`, version `1.30.0`.
- Fresh local MCP `tools/list`: HTTP 200 JSON-RPC result.
- Fresh tool count: **66 unique tools**.
- Fresh `tools/list` response SHA-256: `b0c5dc7a6cfa5883ab60eee4d62dc5770293d0d2343179e7ec6e59837d24564a`.

The historical 92-tool claim in the 2026-09-22 attestation and patch note is **stale**. The fresh 66-tool result is a timestamped measurement, not a quota or a claim that every retained tool is useful.

## Version and provenance conflict

The live handoff has no canonical version identity:

- package metadata: `1.2.0`;
- `/health`: hard-coded `2.2.0`;
- MCP `serverInfo.version`: `1.30.0`;
- Git commit: `75bde939ace7ff46ed2fef0056880a0814ab0e11`;
- branch: `release/debut-v1.6.0`;
- worktree: dirty, with unrelated pre-existing changes preserved.

Node 0 and Node 1 cannot prove official-Engine parity or reproduce the live MCP surface until one immutable build identity is established and used consistently.

## Authorization and listener blockers

The live service binds `0.0.0.0:8016`. The systemd base unit says `127.0.0.1`, but the drop-in override changes the host to `0.0.0.0`.

The local MCP endpoint accepted JSON-RPC requests without an `Authorization` header. Host/origin allowlisting exists, but no application-level OAuth/Bearer enforcement was evidenced. The gateway API-key header implementation is a stub. The Tailscale ACL payload is marked `PROPOSED`, not live policy evidence.

Conclusion: network reachability must not be treated as authentication. The operator must choose loopback-only exposure or implement and test application-level authentication.

Redis also has a `*:6379` listener while the payload document describes loopback binding; effective ownership and bind policy require reconciliation.

## Intake/package integrity blockers

The existing `data/federation/usb-payload/` is incomplete and must not be promoted:

- only five tracked files are present;
- `spire/` exists but is empty;
- no `PAYLOAD_MANIFEST.md` or complete `MANIFEST.yaml`;
- no package `SHA256SUMS`;
- no `docs/federation/node0_received/` intake tree;
- no `data/staging/node0/` staging tree;
- no intake verification report;
- documented `scripts/federation/intake_node0.py` is absent from the current tree.

The intake manual therefore describes a procedure that cannot currently be executed as written. Gate A is blocked.

## C6 and federation-security blockers

- C6 is a draft with unsigned ratification checkboxes.
- The attestation's `SIGNED` status is a text banner, not a detached cryptographic signature.
- No trust root, key ID, signature algorithm, or tamper test was found.
- SPIRE evidence is absent.

Gate F remains blocked. Historical `SIGNED` strings and proposed ACLs are not promotion evidence.

## Positive evidence

- Hub is healthy.
- Fresh `initialize` and `tools/list` calls succeeded over local HTTP.
- Federation diagnostic passed its local Tailscale/ping/MCP/direct-WireGuard checks.
- The quarantine evidence bundle checksums pass.
- No personal Lilith material, credentials, private keys, tokens, browser/session data, or unapproved personal material was intentionally included.

## Required next sequence

1. Establish one canonical Engine build/version identity.
2. Resolve the effective `0.0.0.0:8016` and Redis bind policies.
3. Decide whether federation MCP access is loopback-only or authenticated.
4. Restore or replace the missing intake verifier.
5. Build a new complete quarantine package with manifest, privacy classification, per-file hashes, package hash, and clean-reassembly proof.
6. Produce detached C6/signature evidence or keep Gate F blocked.
7. Run capability-level tests for unified tools; do not use tool count as the acceptance criterion.
8. Obtain explicit operator approval before any promotion, merge, or external handoff.

## Safety statement

No core runtime files were modified. No files were deleted. Existing unrelated working-tree changes were preserved. This report and the evidence bundle are quarantine artifacts, not an approved handoff package.
