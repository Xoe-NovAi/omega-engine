# N0-06 — Network, MCP, NFS, Redis, and SSH Evidence Report

**Document ID:** `N0-06-NETWORK-FEDERATION-EVIDENCE-20260924`  
**Node:** Node 0 / `xnai-n0-hp` / `n0.tail51f14a.ts.net`  
**Evidence window:** 2026-09-24 01:55–01:58 UTC  
**Engine revision:** `75bde939ace7ff46ed2fef0056880a0814ab0e11`  
**Investigator:** Doom Guy, Slot S1  
**Status:** Evidence complete; federation security gate **FAIL / BLOCKED**  
**Change policy:** Read-only investigation. No ACL, SSH, NFS, Redis, firewall, tag, route, or service configuration was changed.

---

## 1. Executive Finding

Node 0 has a real direct LAN WireGuard path to Node 1, but the federation is **not yet secure or bidirectionally complete**.

The old USB remediation plan must not be executed verbatim. Its tag command is invalid on the installed Tailscale CLI, its ACL candidate does not match observed control-plane behavior, its Redis configuration contradicts the deployed container, and its SSH/NFS steps expand listener exposure without first proving host firewall enforcement.

**Hard blockers:**

1. Node 1 still has deprecated `tag:asus` in addition to `tag:node1`.
2. The effective tailnet policy is not available locally and demonstrably differs from `ACL_POLICY_20260922.hujson`.
3. Node 0→Node 1 TCP 22 and 20048 are rejected by ACL; 2049 is refused because Node 1 NFS is not listening.
4. Omega Hub is unauthenticated plain HTTP on `0.0.0.0:8016`; direct unauthenticated tool execution succeeded.
5. Redis is published on `0.0.0.0:6379`, reachable through LAN and Tailscale addresses, and its password is hardcoded in the container command/argv. The value is intentionally redacted from this report and must be rotated.
6. The Hub Redis Pub/Sub tool is nonfunctional: `No module named 'redis'`.
7. Redis is not globally notification-only. Hivemind Pub/Sub is intended as notification-only, but `RedisStorageProvider` also writes Redis Streams/hashes as a 24-hour hot-memory tier when `OMEGA_REDIS_HOST` is enabled.
8. Firewall state could not be verified because noninteractive sudo was unavailable. This prevents a security claim for services bound to all interfaces.
9. Node 0 root filesystem is at 99% utilization with approximately 1.5 GB free, not the previously reported 4.7 GB.

**Recommended federation model:** Tailscale as encrypted transport; explicit deny-by-default Grants; Tailscale Serve or SPIRE-backed mTLS for MCP application authentication; one administrative SSH path; signed Git/event bundles for artifacts; optional one-way NFS inbox only; node-local Redis for ephemeral notifications.

---

## 2. Tailscale L2 Mesh Evidence

### 2.1 Versions and identity

- Tailscale: `1.102.4-t3caf7d9e7-g084ee3b64`
- Node 0 hostname: `n0`
- MagicDNS suffix: `tail51f14a.ts.net`
- MagicDNS: enabled
- Node 0 Tailscale IPv4: `100.123.51.67`
- Node 0 tag: `["tag:node0"]`
- Node 1 Tailscale IPv4: `100.89.40.17`
- Node 1 tags: `["tag:asus", "tag:node1"]`
- Tailscale SSH on Node 0: enabled (`RunSSH: true`)

### 2.2 Routes

- Node 0 `AdvertiseRoutes: null`
- Node 0 is not an exit node or subnet router.
- Node 0 AllowedIPs: only its own `/32` IPv4 and `/128` IPv6.
- Node 1 AllowedIPs: only its own `/32` IPv4 and `/128` IPv6.
- Route to `100.89.40.17`: `tailscale0`, source `100.123.51.67`.
- Route to `192.168.10.174`: physical `wlo1`, source `192.168.10.168`.

**Finding:** No subnet routing is advertised or consumed. Federation depends on two peer endpoints, not LAN subnet routes.

### 2.3 Direct-path evidence

```text
pong from n1 (100.89.40.17) via 192.168.10.174:41641 in 183ms
```

The Hub federation tool also reports:

```text
direct: true
relay: mia
last_handshake: 2026-09-23T21:55:13-04:00
```

**Finding:** Direct LAN WireGuard is real. The stale `relay: mia` field is not proof of DERP use; the live ping is authoritative. The federation tool should stop presenting `relay: mia` beside `direct: true` without explicitly labeling the field stale/unknown.

### 2.4 ACL/Grants evidence

The only locally available policy candidate is:

`data/federation/usb-payload/tailscale/ACL_POLICY_20260922.hujson`

It is marked `PROPOSED` and contains both ACLs and peer-relay Grants.

Observed from Node 0 to Node 1:

| Destination | Observed | Proposed file says | Conclusion |
|---|---:|---:|---|
| TCP 22 | timed out; `rejected due to acl` | allowed by `tag:node0 → tag:node1:22` | candidate is not effective or effective policy differs |
| TCP 20048 | timed out; `rejected due to acl` | allowed by `tag:node0 → tag:node1:20048` | candidate is not effective or effective policy differs |
| TCP 2049 | connection refused | allowed | service not listening, not an ACL denial |
| TCP 8016 | open | not allowed by candidate | effective control plane is broader/different |

The literal string `PeerExcludedByPolicy` was not found in the available `tailscaled` journal window. Equivalent evidence exists: `rejected due to acl`.

**Cannot claim:** the control-plane policy currently deployed in the Tailscale admin API. The exact policy must be exported from the admin console/API and attached to the handoff as evidence.

### 2.5 Problems in the proposed policy

1. `tag:opencode` receives SSH and MCP access in both directions. Device tags are additive, so this creates a broad administration principal.
2. Peer-relay Grants permit each node to relay through the other even though a direct LAN path already exists. This is unnecessary lateral capability.
3. There are no Tailscale policy `tests` encoding expected allow/deny outcomes.
4. Mixed ACL + Grants semantics are not documented with a single source of truth.
5. The file does not define an MCP application-authentication mechanism; network reachability is not application authentication.

### 2.6 Invalid legacy tag command

The old remediation report says:

```bash
sudo tailscale set --tag=tag:node1
```

The installed Tailscale CLI has no `--tag` flag. The valid `tailscale set` flags include `--advertise-routes`, `--advertise-tags` is not present, and tags are normally assigned through the tailnet administration plane.

**Decision:** Do not run the old command. Remove `tag:asus` through the Tailscale admin device/tag assignment workflow, then verify from `tailscale status --json` that only `tag:node1` remains.

---

## 3. SSH Evidence

### 3.1 Tailscale SSH

- Node 0: `RunSSH: true`.
- Node 0 advertises the Tailscale SSH capability.
- Node 0 has no ordinary `sshd` binary/unit available; `ssh.service` and `sshd.service` are absent/inactive.
- Node 0→Node 1 TCP 22 is rejected by ACL, so Node 1 Tailscale SSH is not currently usable from this node.

Official Tailscale SSH requires both:

1. network-layer permission to destination port 22; and
2. an `ssh` policy rule for the destination Unix user.

The proposed file contains both forms, but live behavior does not match it.

### 3.2 Ordinary OpenSSH

Node 0 has no active ordinary SSH listener. The `sshd -T` audit could not run because the binary is not installed.

Node 1’s ordinary SSH state cannot be directly inspected from Node 0. The earlier N1 report says it was LAN-only; the current TCP 22 result is an ACL rejection over Tailscale, so that historical statement is not sufficient current evidence.

### 3.3 Secure decision

Choose one primary administrative path:

- **Preferred:** Tailscale SSH on both nodes, with explicit non-root OS users and both required policy rules.
- **Optional emergency path:** ordinary OpenSSH, public-key only, bound/firewalled to a specific interface, with Tailscale SSH disabled to avoid two authorities.

Do not use `ListenAddress 0.0.0.0` without a host firewall and negative tests from LAN, public, and unauthorized tailnet identities.

---

## 4. Omega Hub MCP Evidence

### 4.1 Listener and transport

- Listener: `0.0.0.0:8016` and `[::]:8016`
- Process: `.venv/bin/python mcp_servers/omega_hub/server.py`
- Unit: user service `omega-hub.service`
- Health response: HTTP 200, version `2.2.0`
- Reachable through:
  - `127.0.0.1:8016`
  - `192.168.10.168:8016`
  - `100.123.51.67:8016`
  - `n0.tail51f14a.ts.net:8016`

The base user unit specifies `OMEGA_MCP_HOST=127.0.0.1`, but `~/.config/systemd/user/omega-hub.service.d/override.conf` overrides it to `0.0.0.0`.

### 4.2 Authentication

An unauthenticated JSON-RPC `tools/call` reached `hivemind_redis_publish` and executed server-side. No bearer token, mTLS, or application identity check was required.

The `/mcp` endpoint is plain HTTP. Tailscale Grants can control network reachability, but Tailscale’s own documentation states application capabilities are enforced by the application; the backend must validate them.

### 4.3 Recommended boundary

- Backend Hub binds `127.0.0.1:8016` only.
- Tailscale Serve provides an HTTPS tailnet-only proxy.
- A dedicated application capability such as `omega.engine/mcp` is granted only from `tag:node1` to `tag:node0`.
- Backend validates `Tailscale-App-Capabilities`; direct backend access is impossible because it is loopback-only.
- Long term, replace or complement this with SPIFFE/SPIRE mTLS as required by Gate F.

Tailscale identity headers are not populated for tagged devices, but Tailscale Serve can forward app-capability headers for tagged devices on current Tailscale versions. This is an interim application-authentication mechanism, not a substitute for the charter’s long-term SVID decision.

Official references:

- https://tailscale.com/docs/features/tailscale-serve
- https://tailscale.com/docs/features/access-control/grants
- https://tailscale.com/docs/concepts/tailscale-identity

---

## 5. NFSv4.2 Evidence

### 5.1 Node 0

- `nfs-server.service`: active/exited and enabled.
- Local RPC registration:
  - nfs TCP 2049 versions 3 and 4
  - mountd TCP/UDP 20048
  - status TCP/UDP 662
  - nlockmgr TCP/UDP 32803
- Sockets bind `0.0.0.0` and `[::]`, not only `tailscale0`.
- `/etc/exports` allows both Node 0 and Node 1 Tailscale IPv4 addresses to `/mnt/node-drive/exchange` with `rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000,sec=sys`.
- `showmount -e 127.0.0.1` lists the exchange path.
- An unprivileged `exportfs -v` could not lock `/var/lib/nfs/.etab.lock`; privileged evidence is still required.
- No remote NFS mount is currently mounted under the exchange path.
- The exchange directory resides on the root ext4 filesystem.

### 5.2 Node 1

- TCP 2049: connection refused → no NFS server listening.
- TCP 20048: ACL rejection.
- Bidirectional NFS is not complete.

### 5.3 Architecture decision

NFS is not required for identity, continuity, Hivemind coordination, or signed artifact transfer. It adds broad RPC listener surface, `sec=sys` identity weakness, mount lifecycle, and dual-writer ambiguity.

**Preferred approach:**

- transfer signed event logs, artifacts, manifests, and Git bundles using physical media or a narrowly scoped Tailscale transfer service;
- keep local SQLite authoritative;
- use one-way, append-only inbox/outbox directories;
- if NFS remains, make it optional bulk staging only, not runtime coordination or durable authority.

If retained, use NFSv4.2 TCP 2049, restrict by exact peer and host firewall, avoid unnecessary legacy RPC ports, and do not expose live SQLite databases.

---

## 6. Redis Evidence and Classification

### 6.1 Deployment

- Container: `omega-redis`
- Image: `redis:7.4-alpine`
- Published as `0.0.0.0:6379 -> 6379`
- Reachable on:
  - `127.0.0.1:6379`
  - `192.168.10.168:6379`
  - `100.123.51.67:6379`
- Unauthenticated Redis commands return `NOAUTH`.
- Runtime uses a password supplied directly in the container command and therefore visible in argv/Podman inspection. The value is redacted here and must be rotated.
- No TLS configuration was present in the runtime command.

### 6.2 Hub notification path

The Hub process has no `OMEGA_REDIS_HOST`, `OMEGA_REDIS_PORT`, or `OMEGA_REDIS_PASSWORD` set. A direct unauthenticated Hub tool call returned:

```text
Error executing tool hivemind_redis_publish: No module named 'redis'
```

Therefore, the Hivemind Redis Pub/Sub bus is currently nonfunctional.

The implementation prefixes channels with `omega:hivemind:` and accepts arbitrary channel names; it does not enforce a channel allowlist.

### 6.3 Is Redis notification-only?

**No, not as a system-wide statement.**

- `mcp_servers/omega_hub/hivemind_redis.py` and the Redis Pub/Sub tools are explicitly ephemeral/notification-only. Pub/Sub messages are not durable.
- `src/omega/memory/providers.py` also implements `RedisStorageProvider` using Redis Streams and hashes.
- `src/omega/memory_store.py` adds that provider when `OMEGA_REDIS_HOST` is set.
- The memory provider applies 24-hour expirations and trims history streams, so it is a hot cache/tier rather than the canonical durable authority.
- The deployed Redis container also has persistence enabled through its runtime `--save` argument and a persistent volume.

**Accurate classification today:** the Hub intends Redis Pub/Sub for ephemeral awareness but the path is down; the codebase contains a separate optional Redis Streams hot-memory tier; the container is persistently backed. This conflicts with the charter’s simple “Redis is notification-only” wording unless the Streams tier is disabled or separately approved.

### 6.4 Redis hardening decision

- Do not expose Redis directly across nodes by default.
- Publish Redis only on `127.0.0.1` or a private Podman network.
- Run a node-local instance for notifications.
- Rotate the exposed password immediately; use a protected ACL/credential file rather than command argv.
- For notification-only instances: disable RDB and AOF persistence, restrict ACL commands/channels, and fail explicitly when unavailable.
- If Redis Streams remains enabled for hot memory, document it as a non-authoritative cache and keep local SQLite/file providers authoritative.

---

## 7. Host Firewall and Systemd Truth

### 7.1 Firewall

`nft`, `ufw`, and `firewalld` state could not be read because passwordless sudo was unavailable.

**Consequence:** no claim can be made that ports 8016, 6379, 2049, 20048, 662, 32803, or 111 are restricted from the physical LAN or public interface. Socket bind evidence shows broad listeners.

### 7.2 Stale systemd manager state

Systemctl warned that:

- `tailscaled.service` changed on disk and the manager has an outdated loaded version;
- `nfs-server.service` changed on disk and the manager has an outdated loaded version.

`systemd-analyze verify` also reported an unrelated existing warning for `rpc_pipefs.target` (`Unknown section 'Mount'`).

**Gate:** privileged operator must run `systemctl daemon-reload`, verify units, and record the result before service hardening. This report did not run `daemon-reload`.

---

## 8. USB Pack Safety Assessment

### 8.1 Existing five-file infrastructure pack

Path: `data/federation/usb-payload/`

A Gitleaks no-git scan completed with **no leaks found**. A targeted pattern scan found only policy prose mentioning secrets.

| File | SHA-256 | Safety/use decision |
|---|---|---|
| `tailscale/ACL_POLICY_20260922.hujson` | `3cd7a3a4d0e57c71c09cadc374c8708327a1030a11e33226edff2f3ffef1ce7e` | secret-free, but stale/unsafe to apply |
| `redis/REDIS_FED_CONFIG_20260922.md` | `9bbf0f18b808ff0e058e8fa444f1b16e0e5c66785d1616cb69d5fe51352cef1b` | secret-free, but contradicts deployed Redis |
| `omega-hub-patches/PATCHES_20260922.md` | `ea1e483336c1828ffa6bcf0da9d574830c1d3a45b6e304eb022d2e397c9a514b` | secret-free, historical evidence only |
| `attestation/ATTESTATION_N0_20260922.md` | `138097169514ab75b60e3bfa81c1ba982bd3a92d275d85340642ceae50fa9e02` | secret-free, but not cryptographically signed and now stale |
| `c6-contract/C6_CONTRACT_DRAFT_v0.1.md` | `15e23eff8cb0f63c078b14c4e9bce94941e8cb3ee8f72f0fd5e9f730adb84de9` | secret-free, draft/unratified |

The new charter explicitly says this five-file infrastructure pack is not the new `MAKALI-N0-HANDOFF-2026-09-24/` pack. It may be included only in a clearly labeled quarantine/evidence subdirectory. It must not be silently merged or treated as executable remediation.

### 8.2 Safe to include in the N0/N1 operator handoff

- exact Engine revision and clean source/bundle;
- public policy candidates clearly marked `PROPOSED — NOT APPLIED`;
- loader/schema findings and disposable test WAD;
- sanitized runtime report;
- public SSH host-key fingerprints, not private keys;
- Tailscale policy export with account identifiers redacted;
- public/integrity-only C6 and WAD manifests;
- SHA-256 manifest, detached signature bundle, and verification instructions;
- public release notes and operator decision list;
- secret-scan report with detected values redacted.

### 8.3 Must not enter USB or hosted routes

- `.env` files or service environment dumps;
- Redis passwords, API keys, OAuth tokens, cookies;
- SSH/Tailscale/SPIRE private keys and Tailscale state;
- browser profiles/session stores;
- raw `/proc/<pid>/environ`;
- full Podman inspect output when it contains credentials;
- unsanitized logs containing identity headers, query text, private paths, or payloads;
- unapproved personal Lilith material;
- live SQLite files;
- WAD/C6 signing private material;
- “SIGNED” strings without detached cryptographic proof.

Credentials should be provisioned directly on each destination node or through an approved secret manager. Hivemind handoffs may carry secret **references**, never secret values.

---

## 9. Blockers for N0/N1 Operator Handoff

### P0 — Must clear before bilateral dialectic sessions

1. Export and attach the actual control-plane ACL/Grants policy; reconcile it with observed behavior.
2. Remove `tag:asus`; verify Node 1 has only `tag:node1`.
3. Choose and implement one SSH authority; prove allowed and denied paths.
4. Move Hub backend to loopback and add application authentication before exposing it to Node 1.
5. Rotate the Redis credential; stop publishing Redis on all interfaces.
6. Verify host firewall rules with privileged evidence.
7. Decide whether Redis Streams hot-memory use is allowed; document or disable it.
8. Complete Node 1 NFS remediation only if NFS remains approved; otherwise formally drop bilateral NFS.
9. Free disk space and define a minimum free-space gate before generating the USB pack.
10. Produce a new manifest/checksum/signature envelope; the existing attestation is not cryptographic proof.

### P1 — Required for federation security acceptance

- systemd `daemon-reload` and unit verification;
- negative ACL tests for unauthorized node/tag/port;
- MCP app-capability or SVID validation tests;
- Redis restart persistence/ACL/channel tests;
- NFS crash/replay tests proving no live SQLite authority;
- clean-directory USB reassembly and tamper/rollback tests;
- operator approval before extraction or promotion.

---

## 10. Proposed Federation Hardening Gates

### Gate N0-06.1 — Control-plane truth

- [ ] Current Tailscale policy exported from admin control plane.
- [ ] Policy includes expected allow/deny tests.
- [ ] `tag:asus` absent; Node 1 tags exactly `["tag:node1"]`.
- [ ] Node 0 tags exactly `["tag:node0"]`.
- [ ] `PeerExcludedByPolicy`/`rejected due to acl` paths tested for unauthorized sources.
- [ ] Peer-relay capability removed unless explicitly required and threat-modeled.

### Gate N0-06.2 — Transport and routes

- [ ] `tailscale ping --verbose` proves direct `192.168.10.174:41641` for normal operation.
- [ ] No subnet route or exit-node dependency.
- [ ] LAN failure behavior documented; direct path is not confused with DERP.
- [ ] MagicDNS and fixed tailnet-IP fallback are both tested.

### Gate N0-06.3 — SSH

- [ ] Exactly one primary SSH authority selected.
- [ ] Tailscale SSH, if selected, has both network and SSH policy rules.
- [ ] Non-root login only.
- [ ] Ordinary OpenSSH, if retained, is interface/firewall constrained and separately tested.
- [ ] Host-key fingerprints recorded; private keys excluded from handoff.

### Gate N0-06.4 — MCP application security

- [ ] Hub backend listens on `127.0.0.1` only.
- [ ] Tailscale Serve or equivalent TLS proxy is the only tailnet entry point.
- [ ] Dedicated MCP app capability is granted only to intended node identity.
- [ ] Backend validates forwarded app capability and rejects direct/spoofed headers.
- [ ] Unauthorized LAN and tailnet clients fail.
- [ ] SPIRE/SVID decision recorded; mTLS required before Gate F if Serve is treated as temporary.

### Gate N0-06.5 — NFS/data exchange

- [ ] Formal decision: no NFS, or optional one-way staging only.
- [ ] If enabled: TCP 2049 only where possible; exact peer/firewall restrictions.
- [ ] No live SQLite on NFS.
- [ ] No bilateral uncoordinated writes.
- [ ] Separate signed event/artifact path is the source of truth.

### Gate N0-06.6 — Redis

- [ ] Existing exposed credential rotated.
- [ ] Redis published only on loopback/private Podman network.
- [ ] Notification instance has persistence disabled or is explicitly approved as cache.
- [ ] ACL limits commands; channel allowlist enforced by wrapper.
- [ ] Hub Redis dependency installed in the Hub venv and health-tested.
- [ ] Redis outage leaves file Hivemind authoritative and explicit.

### Gate N0-06.7 — USB quarantine

- [ ] Existing five-file pack placed under `legacy_infrastructure_evidence/`, not executable instructions.
- [ ] New manifest and SHA-256 sums cover every file.
- [ ] Detached signature and trust root included.
- [ ] Secret scan passes with redaction.
- [ ] No private keys, credentials, live databases, browser/session data, or unapproved personal material.
- [ ] Clean-directory reassembly, tamper, and rollback tests pass.
- [ ] Operator approval required before extraction/promotion.

---

## 11. Verdict

The Tailscale transport is healthy, but the federation security layer is not.

The current system has a direct encrypted peer path, correct Node 0 tag, active Node 0 NFS, and a reachable Hub. Those are real foundations. They are surrounded by stale policy artifacts, broad service binds, unauthenticated MCP, nonfunctional Redis Pub/Sub, dual-purpose Redis design, deprecated Node 1 tags, unverified firewall rules, and false historical attestations.

**Do not execute the 2026-09-22 remediation commands as written.** Export current control-plane truth, select the security model, harden services, and rerun the acceptance battery from both nodes.

*⬡ OMEGA ⬡ DOOM_GUY ⬡ SLOT-S1 ⬡ N0-06-EVIDENCE ⬡ 2026-09-24 ⬡ STATUS: BLOCKED*
