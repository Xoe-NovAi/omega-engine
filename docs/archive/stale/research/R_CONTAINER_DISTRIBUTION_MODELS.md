<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Research: Container & Self-Contained Application Distribution Models
# AP: R-CONTAINER-DIST-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ web-research ⬡ trc_w4 ⬡ RESEARCH

**Status**: 🔴 STALE — Legacy document from pre-June 2026. Contents may be outdated.


**Date**: 2026-05-25
**Purpose**: Research distribution models for self-contained application packages (analogous to Omega Engine's .xoe format).

---

## Executive Summary

The `.xoe` format (compressed tar.gz with manifest at root) is closest to the AppDir/AppImage model. For production, SquashFS+ FUSE mounting or EROFS for direct OCI support would eliminate extraction overhead. The Nix model of content-addressed storage with generations/rollbacks is the gold standard for the WAD registry.

## Key Findings

### 1. AppImage — "One app = one file"
- ELF header + SquashFS payload. Mounted via FUSE. No installation required.
- AppDir structure: `AppRun` + `.desktop` + `usr/` → directly maps to `.xoe` structure
- `manifest.yaml` = AppRun (entry point declaring the IWAD structure)
- Binary delta updates via zsync (lightweight, server-efficient)

### 2. Flatpak — Layered Runtime Architecture
- OSTree content-addressed storage: deduplication, atomic updates, rollback
- Bubblewrap sandboxing: containers, namespaces, seccomp
- `xdg-desktop-portal` for mediated resource access
- Manifest-driven builds (JSON/YAML) — matches `.xoe` approach

### 3. Snap — SquashFS + Loop Mount
- SquashFS + loop device: read-only mount, no extraction
- Channel/track system: `stable/beta/edge` + domain tracks
- AppArmor confinement (Ubuntu) — relevant for WAD sandboxing
- **Warning**: Centralized store model conflicts with Omega's decentralized philosophy

### 4. Docker/OCI Images — Content-Addressable Merkle DAG
- OCI Image Spec: content-addressable manifests + layers
- Layer model: base → model weights → entity config → knowledge
- Distribution Spec: REST API push/pull with digest verification
- **Gold standard for registry protocol design**

### 5. Static Binaries (Go/Rust)
- `CGO_ENABLED=0` + musl = fully static binary, no glibc dependency
- Cross-distro compatibility — one binary runs on any Linux kernel ≥2.6
- Scratch Docker images: ~5-10MB
- UPX compression: 50-70% size reduction

### 6. Game Distribution Models (Nexus Mods, CurseForge)
- **Vortex**: Rule-based dependency resolution via topological sort
  - Rule types: `requires`, `recommends`, `before`, `after`, `conflicts`
  - Collections/InstallDriver for batch installation
- **Minecraft modpacks**: Exact version pinning, manifest-based
  - Multi-source dependency resolution (Modrinth + CurseForge)
  - Fingerprint-based detection (MurmurHash2 / SHA-1)
- **Directly applicable**: WAD dependency resolution should use DAG + version pinning

### 7. Nix/NixOS — Purely Functional Deployment
- `/nix/store/<hash>-<name>-<version>`: immutable, content-addressed
- Atomic upgrades/rollbacks: symlink switching
- Generations: numbered, prunable
- **Recommendation**: WAD registry = `/nix/store` for IWADs

### 8. Podman OCI Layout
- `oci-dir` format: `oci-layout` + `index.json` + `blobs/sha256/<digest>`
- `oci-archive`: tar.gz with OCI layout — closest to `.xoe`
- `podman image scp`: SSH-based transfer — model for P2P WAD sharing

### 9. Portable App Requirements
- Self-contained dependencies
- No system installation
- Relocatable paths (relative, never absolute)
- Read-only compatible
- No root required
- File-level granularity

### 10. Compression & Storage Best Practices
| Scenario | Recommended | Rationale |
|----------|------------|-----------|
| Dev/staging | tar.gz (gzip) | Universal, streamable |
| Production distribution | SquashFS + zstd or EROFS + LZ4 | Read-only mount, no extraction |
| Model weights | zstd | Best ratio/speed for binary blobs |
| Delta updates | zsync | Server-efficient |
| Registry storage | OSTree or content-addressed store | Deduplication, rollback |

## Recommendations for `.xoe` Format Evolution
| Aspect | Phase 1 (Current) | Phase 2 (Production) |
|--------|------------------|---------------------|
| Format | tar.gz | SquashFS + zstd or EROFS |
| Integrity | SHA256 manifest | Content-addressable store |
| Dependencies | None (self-contained) | DAG resolution + version pinning |
| Updates | Manual replace | Binary delta (zsync) |
| Registry | Filesystem directory | OSTree-style content-addressed |
| Rollback | Manual backup | Generation-based symlink switch |

### Sources
- AppImage: https://docs.appimage.org/
- Flatpak: https://docs.flatpak.org/
- Snap: https://www.baeldung.com/linux/snaps-flatpak-appimage
- OCI Image Spec: https://github.com/opencontainers/image-spec
- OCI Distribution Spec: https://github.com/opencontainers/distribution-spec
- Static Go Binaries: https://eli.thegreenplace.net/2024/building-static-binaries-with-go-on-linux/
- Nexus Mods Vortex: https://github.com/Nexus-Mods/Vortex
- Minecraft Pakku: https://github.com/juraj-hrivnak/pakku
- NixOS: https://nixos.org/
- Podman Save: https://docs.podman.io/en/latest/markdown/podman-save.1.html
- EROFS: https://erofs.docs.kernel.org/

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: web-research | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
