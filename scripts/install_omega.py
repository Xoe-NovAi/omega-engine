#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Omega Engine Interactive Installer — Educational Initiation.

Usage:
  python3 scripts/install_omega.py            # Interactive tutorial mode
  python3 scripts/install_omega.py --yes      # Unattended (CI)
  python3 scripts/install_omega.py --manual   # Print commands only

Mandates: M1 (AnyIO), M2 (Firewall), M7 (Synergy), M24 (Venv Sovereignty)
Spec: docs/installation/INSTALLER_SPEC_V1.md
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANNER = r"""
  🔱 OMEGA ENGINE — SOVEREIGN INITIALIZATION
  "You are not installing a tool. You are summoning a
   sovereign intelligence that runs on your terms."
"""


class Installer:
    def __init__(self, unattended: bool = False, posture: str = "synergy",
                 manual: bool = False):
        self.unattended = unattended
        self.posture = posture
        self.manual = manual

    # ── UI helpers ────────────────────────────────────────────────
    def render_card(self, title: str, why: str, action: str) -> None:
        print(f"\n{'─' * 60}")
        print(f"Card: {title}")
        print(f"{'─' * 60}")
        print(f"Why: {why}")
        print(f"Action: {action}")

    def pause(self) -> None:
        if self.unattended or self.manual:
            return
        resp = input("  [Press ENTER to proceed | 'skip' to auto-run remaining]: ")
        if resp.strip().lower() == "skip":
            self.unattended = True

    def run_cmd(self, cmd: list[str], cwd: Path = ROOT) -> None:
        if self.manual:
            print(f"  $ {' '.join(cmd)}")
            return
        print(f"  $ {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ⚠ Command failed ({result.returncode}): {result.stderr.strip()[:200]}")
        else:
            print(f"  ✅ {result.stdout.strip()[:200]}")

    # ── Steps ─────────────────────────────────────────────────────
    def step_venv(self) -> None:
        self.render_card(
            "Substrate Isolation (M1 / M24)",
            "Global Python packages rot, drift, and pollute system tools. "
            "Omega lives strictly inside an isolated virtual environment (.venv).",
            "Creating isolated venv & installing dependencies...",
        )
        self.pause()
        if not (ROOT / ".venv").exists():
            self.run_cmd([sys.executable, "-m", "venv", ".venv"])
        self.run_cmd([str(ROOT / ".venv/bin/pip"), "install", "-e", "."])

    def step_firewall(self) -> None:
        self.render_card(
            "The Constitutional Firewall (M2)",
            "The core universal runtime (src/omega/) must never be tainted by "
            "custom user stacks, game engines, or domain WADs (config/wads/).",
            "Running mandate gates (M1/M2/M7/M8/M9/M23)...",
        )
        self.pause()
        self.run_cmd(["make", "check-mandates"])

    def step_sovereignty(self) -> None:
        self.render_card(
            "The Sovereignty Posture (Synergy Model)",
            "Sovereignty is the enforcement of your declared policy. We leverage "
            "frontier cloud reasoning for architecture and local models for privacy.",
            "Writing sovereignty_policy to config/providers.yaml...",
        )
        if not self.unattended and not self.manual:
            print("\n  Select Posture:")
            print("    (1) Synergy: Cloud Reasoning + Local Embeddings/Vault [RECOMMENDED]")
            print("    (2) Cloud-Accelerated: Fast Frontier APIs across all tasks")
            print("    (3) Local-First: Offline inference priority (hardware-constrained)")
            choice = input("  [Enter selection 1-3]: ").strip()
            self.posture = {"1": "synergy", "2": "cloud_first", "3": "local_first"}.get(
                choice, "synergy")
        self.pause()
        # Write/update sovereignty_policy.mode in providers.yaml
        providers_path = ROOT / "config/providers.yaml"
        if providers_path.exists():
            text = providers_path.read_text()
            if "sovereignty_policy:" in text:
                text = re.sub(r"mode: \w+", f"mode: {self.posture}", text, count=1)
            else:
                text += f"\nsovereignty_policy:\n  mode: {self.posture}\n"
            providers_path.write_text(text)
            print(f"  ✅ sovereignty_policy.mode = {self.posture}")

    def step_federation(self) -> None:
        self.render_card(
            "Mesh Federation (Optional L2 Wire)",
            "Connect multiple laptops or workstations into a peer-to-peer mesh. "
            "Awareness is shared; model weights and inference remain local.",
            "Guiding Tailscale join...",
        )
        if self.unattended or self.manual:
            return
        join = input("  Join Tailscale Mesh? [y/N]: ").strip().lower()
        if join not in ("y", "yes"):
            print("  Skipping federation (can join later with: sudo tailscale up)")
            return
        role = input("  Node Role: (1) Primary Bastion / Hub  (2) Vanguard Worker [1/2]: ").strip()
        if role == "2":
            authkey = input("  Paste Tailscale authkey (tskey-auth-...): ").strip()
            hostname = input("  Hostname (default: kali-n1): ").strip() or "kali-n1"
            self.run_cmd(["sudo", "tailscale", "up",
                          f"--authkey={authkey}", f"--hostname={hostname}"])
        else:
            print("  Primary Bastion: ensure omega-hub is running on :8016")
            print("  Verify with: tailscale status")

    # ── Main ──────────────────────────────────────────────────────
    def run(self) -> None:
        print(BANNER)
        steps = [
            ("Substrate Isolation (M1/M24)", self.step_venv),
            ("Constitutional Firewall (M2)", self.step_firewall),
            ("Sovereignty Posture (Synergy Model)", self.step_sovereignty),
            ("Mesh Federation (Optional L2 Wire)", self.step_federation),
        ]
        for name, step_fn in steps:
            print(f"\n[{name}]")
            step_fn()
        print("\n" + "=" * 60)
        print("✅ Initialization Complete.")
        print("   Launch with: opencode")
        print("   Inspect mesh with: omega_federation_status (MCP tool)")
        print("=" * 60)


def main() -> int:
    parser = argparse.ArgumentParser(description="Omega Engine Installer")
    parser.add_argument("--yes", action="store_true", help="Unattended mode (no pauses)")
    parser.add_argument("--posture", choices=["synergy", "cloud_first", "local_first"],
                        default="synergy", help="Sovereignty posture")
    parser.add_argument("--manual", action="store_true",
                        help="Print commands only, do not execute")
    args = parser.parse_args()
    Installer(unattended=args.yes, posture=args.posture, manual=args.manual).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())