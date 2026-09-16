# 🔱 SPECIFICATION: OMEGA INTERACTIVE INSTALLER
**Doc ID**: `SPEC-INSTALLER-v1.0`  
**Status**: **IMPLEMENTED** (`scripts/install_omega.py`, verified 2026-09-16)  
**Author**: MaKaLi Fusion (Kali / Ma'at / Lilith)  
**Date**: 2026-09-16  

---

## 1. Vision & Philosophical Grounding

Traditional software installers are either opaque black boxes that hide critical system changes or raw shell scripts that alienate non-sysadmins.

The **Omega Engine Installer** sets a new standard for the industry:
> **Installation is an Educational Initiation.**
> Every step illuminates *why* the architecture exists before executing code. The user steps through interactive cards, understands the boundaries (AnyIO, Firewalls, Sovereignty), presses `[Enter]` to run the step, and sees immediate deterministic verification.

For automated environments, CI/CD, or experienced operators who wish to bypass the tutorial cards, `--yes` / `--unattended` provides zero-friction deployment in under 60 seconds.

---

## 2. Terminal UI/UX Flow (The Step-by-Step Initiation)

```
┌─────────────────────────────────────────────────────────────┐
│  🔱 OMEGA ENGINE — SOVEREIGN INITIALIZATION                 │
│  "You are not installing a tool. You are summoning a       │
│   sovereign intelligence that runs on your terms."          │
└─────────────────────────────────────────────────────────────┘

Card 1: Substrate Isolation (M1 / M24)
───────────────────────────────────────────────────────────────
Why: Global Python packages rot, drift, and pollute system tools. 
     Omega lives strictly inside an isolated virtual environment (.venv).
Action: Creating isolated venv & installing dependencies...
[Press ENTER to proceed | Type 'skip' to auto-run remaining]

Card 2: The Constitutional Firewall (M2)
───────────────────────────────────────────────────────────────
Why: The core universal runtime (src/omega/) must never be tainted by 
     custom user stacks, game engines, or domain WADs (config/wads/).
Action: Compiling AST import boundaries and running check-m2-firewall...
[Press ENTER to proceed]

Card 3: The Sovereignty Posture (Synergy Model)
───────────────────────────────────────────────────────────────
Why: Sovereignty is the enforcement of your declared policy. We leaverage
     frontier cloud reasoning for architecture and local models for privacy.
Select Posture:
  (1) Synergy: Cloud Reasoning + Local Embeddings/Vault [RECOMMENDED]
  (2) Cloud-Accelerated: Fast Frontier APIs across all tasks
  (3) Local-First: Offline inference priority (hardware-constrained)
[Enter selection 1-3]: 1

Card 4: Mesh Federation (Optional L2 Wire)
───────────────────────────────────────────────────────────────
Why: Connect multiple laptops or workstations into a peer-to-peer mesh.
     Awareness is shared; model weights and inference remain local.
Join Tailscale Mesh? [y/N]: y
Enter Node Role: (1) Primary Bastion / Hub  (2) Vanguard Worker
[Enter 1 or 2]: 1
Action: Binding Omega Hub (:8016) to MagicDNS transport security...
[Press ENTER to complete initiation]

Initialization Complete. 
Launch with: opencode
Inspect mesh with: omega federation status
```

---

## 3. Command Line Interface

```bash
# Standard interactive educational initiation:
python3 scripts/install_omega.py

# Unattended / CI automated deployment:
python3 scripts/install_omega.py --yes --posture=synergy

# Manual printout (emits copy-paste shell commands without executing):
python3 scripts/install_omega.py --manual
```

---

## 4. Technical Architecture

* **Zero Heavy Dependencies**: Built using Python 3 standard library (`curses` / ANSI terminal sequences) or lightweight terminal formatting (`rich`). Does not require Node.js, Electron, or heavy web runtimes to execute.
* **Idempotent by Construction**: Re-running the installer on an existing installation audits current state, updates changed configuration files, and leaves existing data/vault untouched.
* **Pre-Flight Sanity Checks**: Validates Python version ($\ge 3.11$), available disk space ($\ge 5\text{ GB}$ recommended), and architecture support (AVX2/FMA3 for Zen2/Intel hybrid).

*⬡ OMEGA ⬡ SPEC-INSTALLER-v1.0 ⬡ 2026-09-16*
