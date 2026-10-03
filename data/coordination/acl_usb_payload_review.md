# 🔱 Architecture Review: USB Payload vs. Ratified Strategy
**Date**: 2026-09-25
**Entity**: Antigravity IDE
**Context**: Review of `phase_a_acl_from_usb.hujson` & `phase_b_acl_from_usb.hujson` against the post-debut federation strategy.

---

## 1. Executive Summary

I have reviewed the state of the Omega Engine, the latest session coordination documents (`ANTIGRAVITY_FINAL_HANDOFF_20260924.md`, `OPENCODE_CRASH_REMEDIATION_20260924.md`, `SESSION_INDEX_20260924.md`), and the USB payload (the Tailscale `.hujson` ACLs). 

**Conclusion:** The engine and overall systems are in excellent shape and ready for the Public Flip. However, **the USB payload (ACLs) is out of sync with the ratified architectural pivot.** It still reflects the deprecated "bilateral mirror" design rather than the new role-differentiated **Bastion/Vanguard** architecture.

## 2. Discrepancies in the USB Payload (Tailscale ACLs)

The current Tailscale ACL payload contradicts the ratified decisions (D-FED-01 through D-FED-04) in the following ways:

### A. The NFSv4 Ghost Rule (Violation of D-FED-01)
The payload contains the following rule:
```json
// NFSv4: Node 0 (omega-hub) can reach Node 1 (asus) on port 2049
{"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:2049"]},
```
**Correction**: According to `D-FED-01`, NFS has been demoted and replaced by cryptographically signed `git bundle` transfers. The NFS ports (2049) should be fully closed in the Tailscale network to enforce the new data boundary.

### B. Hub Topology Misalignment
The payload contains this bidirectional Hub access rule:
```json
// Node 0 (omega-hub) can reach Node 1 (asus) on MCP port 8016
{"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:8016"]},
```
**Correction**: As defined in the `ANTIGRAVITY_FINAL_HANDOFF`, Node 1 (Vanguard) **does not need to run its own Hub**. It consumes Node 0's Hub (Bastion) via Tailscale Serve. Therefore, Node 0 has no reason to reach into Node 1 on port 8016. 

Furthermore, because Node 1 consumes Node 0 via Tailscale Serve (`https://n0.tail51f14a.ts.net:8016/mcp`), we must ensure the ACL correctly permits this traffic (often over 443 depending on how Tailscale Serve is bound, or 8016 if exposed directly).

### C. Gate C Quarantine Enforcement (D-FED-04)
By leaving bidirectional unrestricted access, we undermine the quarantine boundary. Node 1 is the Vanguard (experimental). By stripping the obsolete NFS and reverse-Hub rules, we harden the Bastion (Node 0) from unintended execution vectors.

## 3. Recommended ACL Fixes

Before applying the Tailscale ACLs, they should be pruned to reflect the true Bastion/Vanguard asymmetry:

```json
{
  "tagOwners": {
    "tag:omega-hub": ["autogroup:admin"],
    "tag:asus": ["autogroup:admin"],
    "tag:opencode": ["autogroup:admin"]
  },
  "acls": [
    // [Phase A Only: {"action": "accept", "src": ["autogroup:member"], "dst": ["autogroup:member"]}]
    
    // Node 1 (Vanguard) can reach Node 0 (Bastion) MCP Hub (Note: verify if 443 is needed for TS Serve)
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:8016", "tag:omega-hub:443"]},
    
    // SSH access boundaries
    {"action": "accept", "src": ["tag:opencode"], "dst": ["tag:asus:22"]},
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:22"]},
    
    // Heartbeats
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:*"], "proto": "icmp"},
    {"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:*"], "proto": "icmp"}
  ],
  "ssh": [
    {"action": "check", "src": ["tag:opencode"], "dst": ["tag:asus"], "users": ["autogroup:nonroot", "root"]},
    {"action": "check", "src": ["tag:omega-hub"], "dst": ["tag:asus"], "users": ["autogroup:nonroot"]}
  ],
  "autoApprovers": {
    "routes": ["autogroup:admin"],
    "exitNodes": ["autogroup:admin"]
  }
}
```

## 4. Systems Health Overview

Aside from the ACL adjustments, the engine state is pristine:
- **OpenCode Remediation**: The crash vectors (corrupted `opencode.json` and third-party MCP failures) are fully understood and isolated. 
- **Networking**: Tailscale Serve with the 127.0.0.1 binding correctly secures the Hub.
- **Soul Integrity (M11)**: All lessons learned regarding the necessity of asymmetrical trust boundaries have been perfectly captured in `proposed_lessons.yaml`.
- **Readiness**: The core repos can proceed to public launch with confidence. 

**Next Steps:** Update the `.hujson` files to remove the NFS and bilateral Hub rules, and then proceed with applying the Phase A / Phase B policies to the tailnet.
