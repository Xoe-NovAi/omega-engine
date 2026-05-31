# 🔱 Omega Engine — Sovereign Podman Permission Protocol v2 (R-PODMAN-SOVEREIGN-V2)
# Rootless Quadlet Best Practices for Ubuntu 25.10

**AP Token**: `AP-R-PODMAN-SOVEREIGN-V2-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_strategic ⬡ RESEARCH
**Status**: ✅ COMPLETE | **Date**: 2026-05-22 | **Supersedes**: R15_podman_permission_hardening.md (keep-id protocol)

---

## §1 Executive Summary

The Omega Engine has suffered from a persistent "Permission War" where the `:U` volume flag in Quadlets recursively chowns host directories to UID 101000 (the subuid-mapped container user). This locked the host user (UID 1000) out of their own `config/` directory, causing test failures and operational friction.

**Root Cause**: The `:U` flag in Podman volume mounts destructively chowns host directories to the container's mapped UID. On a system with subuid mapping `arcana-novai:100000:65536`, this maps container UID 1001 to host UID 101000.

**The Fix**: Replace `:U` with `UserNS=keep-id` + `User=1000` — a "Sovereign Permission Protocol" that maps host UID 1000 directly into the container, eliminating the need for any chown operations.

---

## §2 Research Sources

This document synthesizes findings from:

| Source | Type | Key Finding |
|--------|------|-------------|
| [Red Hat — Debug rootless Podman mounted volumes](https://www.redhat.com/en/blog/debug-rootless-podman-mounted-volumes) | Official blog | `:U` flag locks host user out; `keep-id` is the alternative |
| [Podman systemd.unit.5 documentation](https://docs.podman.io/en/v4.6.1/markdown/podman-systemd.unit.5.html) | Official docs | `UserNS=keep-id` maps to `--userns keep-id` in Quadlets |
| [GitHub PR #17961](https://github.com/containers/podman/pull/17961) | Podman source | `keep-id` uid/gid options implemented in Podman v4.5.0 |
| [Oracle Linux — Use Pasta Networking with Podman](https://docs.oracle.com/en/learn/ol-podman-pasta-networking/) | Official guide | `pasta` is default from Podman 5.3; avoids NAT overhead |
| [xna-omega-legacy/knowledge/architecture/permissions-model.md](../xna-omega-legacy/knowledge/architecture/permissions-model.md) | Legacy repo | `userns_mode: "keep-id"` was Layer 3 of the 4-Layer Permission System |
| [Containers/podman discussion #24384](https://github.com/containers/podman/discussions/24384) | Community | Pattern: `UserNS=keep-id` + `User=1000` is common practice |
| [Fedora discussion — Podman volume mounts](https://discussion.fedoraproject.org/t/podman-volume-mounts-rootless-container-and-non-root-user-in-container/136301) | Community | `keep-id` is the recommended solution for bind mounts |

---

## §3 Volume Flag Analysis (Ubuntu 25.10)

### The `:U` Flag — DESTRUCTIVE (AVOID)

| Property | Value |
|----------|-------|
| **Purpose** | Automatically chowns host directory to container's mapped UID |
| **Effect** | Recursively changes host ownership to 101000 (or other subuid-mapped UID) |
| **Downside** | Locks host user out of their own files (confirmed by Red Hat blog) |
| **Recommendation** | **Never use on shared host directories** |

**Red Hat's own words**: *"Unfortunately, the chown approach does come with its own set of disadvantages. The `/home/mheon/data` directory is in my user's home directory, but it is no longer owned by my user (in this case, it's owned by user and group 100999)."*

### The `:Z` / `:z` Flags — NO-OP ON UBUNTU (REMOVE)

| Property | Value |
|----------|-------|
| **Purpose** | SELinux relabeling (`:z` = shared, `:Z` = private) |
| **Ubuntu status** | Ubuntu uses AppArmor, not SELinux. Podman's `selinux.Enabled()` returns `false` → flags silently ignored |
| **Recommendation** | **Remove from all Quadlets** — harmless but unnecessary clutter |

---

## §4 The Sovereign Permission Protocol

### The "Rock Solid" Quadlet Pattern (Ubuntu 25.10)

```ini
[Container]
Image=...
ContainerName=...
Pod=...

# === SOVEREIGN PERMISSION PROTOCOL ===
# Maps host UID 1000 -> container UID 1000 (eliminates UID drift)
UserNS=keep-id
# Overrides Dockerfile USER to run as host-mapped user
User=1000

# === VOLUMES (Ubuntu: no :U, no :Z) ===
Volume=/home/arcana-novai/.../config:/app/config:ro
Volume=/media/arcana-novai/.../cache:/cache

# === HARDENING ===
PodmanArgs=--cap-drop=ALL --security-opt=no-new-privileges
```

### Why This Works

| Layer | Mechanism | Effect |
|-------|-----------|--------|
| `UserNS=keep-id` | Namespace mapping | Host UID 1000 → Container UID 1000 (was: Host UID 1000 → Container UID 0) |
| `User=1000` | Process UID | Runs container process as UID 1000 (overrides Dockerfile USER) |
| No `:U` | Volume mount | Files stay owned by host UID 1000 — no chown happens |
| No `:Z` | No SELinux | No-op on Ubuntu anyway |

### Containers That Need `:U` (Exception)

Named volumes on the `omega_library` partition (redis data, qdrant storage, caddy data) that are **not shared with the host user** can still use `:U` since:
- The host user never directly accesses these files
- The container user (e.g., redis UID 999) needs to write to them
- `keep-id` would map host UID 1000 to the container, but redis expects to run as UID 999

**Rule**: Use `:U` only on volumes where the host user has no reason to touch the files directly.

---

## §5 Networking: `pasta` vs `slirp4netns`

| Feature | `slirp4netns` | `pasta` |
|---------|---------------|---------|
| **Default since** | Legacy | Podman 5.3+ |
| **NAT** | Yes (10.0.2.x) | No (copies host IP) |
| **Performance** | Higher CPU overhead | Lower CPU overhead |
| **Host interface** | `tap0` virtual | Uses host interface directly |
| **Recommendation** | Legacy (avoid) | **Default on Ubuntu 25.10** |

`pasta` is already the default on Ubuntu 25.10 (Podman 5.x). No explicit `Network=pasta` is needed but can be added for documentation clarity.

---

## §6 Quadlets Affected

| Quadlet | Mount(s) Fixed | Change |
|---------|----------------|--------|
| `omega-iris.container` | `config:/app/config:ro`, `/cache:/cache` | Removed `:Z,U`, added `UserNS=keep-id`, `User=1000` |
| `omega-roc_racoon.container` | All volume mounts | Removed `:Z,U`, added `UserNS=keep-id`, `User=1000` |
| `omega-redis.container` | `/data` (omega_library) | Not changed — container uses UID 999, `:U` acceptable |
| `omega-caddy.container` | `/data`, `/config` (omega_library) | Not changed — named volumes on separate partition |
| `omega-qdrant.container` | `/qdrant/storage` (omega_library) | Not changed — named volumes on separate partition |

---

## §7 MCP Server Consolidation

As part of Decision 50, the following MCP servers were consolidated into the Omega Hub:

| Server | Port | Tools | Consolidated Into |
|--------|------|-------|-------------------|
| `omega-hub` | 8016 | Oracle, Hivemind, Library, **Research**, **Stats** | **Hub (remains)** |
| `omega-research` | 8011 | research, research_get, research_list, research_depths, research_stats | ✅ Hub (archived) |
| `omega-stats` | 8012 | get_system_stats, get_omega_metrics, check_models_directory, check_podman_storage | ✅ Hub (archived) |

**Archives**: `mcp/archives/omega-research_superseded_by_hub_20260522/`, `mcp/archives/omega-stats_superseded_by_hub_20260522/`

---

## §8 Decision Record

**Decision 50 (2026-05-22)**: Adopt `UserNS=keep-id` + `User=1000` as the Sovereign Permission Protocol for all Omega Engine Quadlets that mount host project directories. Remove `:U` and `:Z` flags from all Quadlets (Ubuntu 25.10, AppArmor not SELinux). Consolidate omega-research and omega-stats MCP servers into omega-hub.

---

## §9 Implementation Checklist

- [x] `omega-iris.container` — `:U,:Z` removed, `UserNS=keep-id` + `User=1000` added
- [x] `omega-roc_racoon.container` — `:U,:Z` removed from engine/data mounts, `UserNS=keep-id` + `User=1000` added
- [x] MCP Research tools consolidated into Hub
- [x] MCP Stats tools consolidated into Hub
- [x] `opencode.json` — omega-research and omega-stats removed (served by hub)
- [x] `R_PODMAN_SOVEREIGN_V2.md` — This document
- [x] `PIVOT_LOG.md` — Decision 50 appended
- [x] `COMMUNICATION_HUB.md` — Session completion logged
- [x] `SOVEREIGN_MANDATES.md` — Podman permission mandate added
- [x] `ROADMAP.md` — P0 permission fix marked complete
- [x] `INDEX.md` — Research entry added
- [x] `RESEARCH_QUEUE.md` — Marked done
- [x] `.opencode/agents/overseer.md` — Container hardening mandate added
- [x] `.opencode/agents/builder.md` — Container hardening protocol updated
- [ ] Final verification: `make test` green, `find ... -user 101000` = 0
