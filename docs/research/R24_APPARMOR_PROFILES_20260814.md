<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gap R24: AppArmor Container Profiles

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** V-10 (container hardening — currently unconfined)
**Status:** ✅ RESOLVED

## Summary
Podman supports custom AppArmor profiles via `--security-opt apparmor=<profile>` (or quadlet `SecurityOpt=apparmor:<profile>`). Profiles live in `/etc/apparmor.d/`, are loaded with `apparmor_parser -r`, and should be **generated in complain mode first** (`aa-genprof`), then enforced. Ubuntu uses AppArmor (not SELinux), so this is the correct MAC for this host. This closes the V-10 GAP (containers currently unconfined).

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| Configure AppArmor for Podman | https://oneuptime.com/blog/post/2026-03-18-configure-apparmor-profiles-podman-containers/view | 2026-03-18 | End-to-end profile + apply |
| Practical AppArmor (Podman/Docker) | https://dev.to/lyraalishaikh/stop-leaving-containers-exposed-practical-apparmor-profiles-for-podman-and-docker-on-linux-j40 | 2026-06-17 | aa-genprof workflow |
| Secure Podman SELinux/AppArmor | https://binadit.com/tutorials/secure-podman-containers-selinux-apparmor | 2026-04-01 | Podman config + wrapper |
| Podman security-opt docs | https://docs.podman.io/en/v4.6.0/markdown/options/security-opt.html | 2026 | `apparmor=`, `apparmor=unconfined` |

## Findings
- **Apply**: `podman run --security-opt apparmor=omega-roc_racoon ...` or quadlet `SecurityOpt=apparmor:omega-roc_racoon`.
- **Generate**: `sudo aa-genprof /usr/bin/<svc>` puts the profile in complain mode; exercise the workload, then `aa-logprof` builds rules. `deny` rules are enforced even in complain mode.
- **Load**: `sudo apparmor_parser -r /etc/apparmor.d/omega-<svc>`; verify with `sudo aa-status | grep omega-`.
- **Debug**: `sudo dmesg | grep apparmor` / `journalctl -xe | grep apparmor`.
- **Defense in depth**: combine with `--cap-drop=ALL` and a tight seccomp profile.
- Podman already ships a default profile; custom ones tighten per-service filesystem/network/capability access.

## Recommendation
For V-10, write per-container AppArmor profiles for the engine's quadlets (omega-hub, omega-roc_racoon, etc.):
1. `sudo aa-genprof` each service binary in complain mode; run real workloads.
2. `aa-logprof` to finalize allow rules; add explicit `deny` for `/etc/shadow`, `/root/**`, raw network.
3. `apparmor_parser -r /etc/apparmor.d/omega-<svc>`.
4. Add `SecurityOpt=apparmor:omega-<svc>` to each quadlet; keep `--cap-drop=ALL` + seccomp.
5. Switch complain→enforce after a stabilization period.
This removes the "containers unconfined" GAP and satisfies V-10.

## Confidence
**HIGH** — AppArmor+Podman integration is well-documented and the host is Ubuntu (AppArmor default).

## Remaining Unknowns
- Exact capability/filesystem needs per service (resolved during the complain-mode tuning pass).
- Whether any service needs `network raw`/`packet` (deny by default).
