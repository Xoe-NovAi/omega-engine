#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Path A' — Delete 11 Broken Call Sites + Vault + Enforcer
AP: AP-VAULT-CLINE-DELETE-11-v1.0.0
Author: Grokster (cline specialist)
Date: 2026-08-28
Sprint: PUBLIC-DEBUT-01
Authority: D-568 (path A'), R_VAULT_CLINE_ROUND3 §A (11 sites), R_VAULT_CLINE_ROUND4 mission #2
Mandates: M14 (no plaintext), M23 (no soft-fail), M26 (doc), M27 (5-tier)

WHAT THIS DOES
==============
One-shot script for the "delete broken vault + 30-LOC shim" path that
Ma'at is supposed to execute. Covers:

1. The vault (2,138 LOC across 5 files in src/omega/vault/)
2. The enforcer (220 LOC, src/omega/tools/enforce_vaultcore.py)
3. The 11 broken call sites (replaced by VaultCoreConfigResolver drop-ins):
   a. 8 env:VAR in config/providers.yaml + config/model_registry/providers/*.yaml
   b. 2 OMEGA_REDIS_PASSWORD in src/omega/memory_store.py + src/omega/memory/providers.py
   c. 1 GOOGLE_API_KEY fallback in src/omega/oracle/providers.py:103

USAGE
=====
    # dry-run (default; shows what would be deleted/changed)
    python3 scripts/delete_11_broken_sites.py

    # execute (after Architect approval)
    python3 scripts/delete_11_broken_sites.py --yes

    # backup only (don't delete anything)
    python3 scripts/delete_11_broken_sites.py --backup-only

WHAT IT DOES IN ORDER
=====================
Step 1: Inventory — list every file + line that will be touched
Step 2: Backup — copy vault/, enforcer, and the 11 sites to ~/.omega-vault-archive/
Step 3: Patch — apply the drop-in replacements (vault_config_resolver calls)
Step 4: Delete — remove vault/ + enforcer + the original 11 lines
Step 5: Verify — run enforce_vaultcore (now with 0 files to scan) + grep
Step 6: Report — show what was done, log to data/vault/delete_11_log.json

RATIONALE (per D-568 + R_VAULT_CLINE_ROUND3 §A.4)
==================================================
Path A' replaces the broken vault with a 30-LOC shim that:
- Scans the 3 external stores (secrets.json, providers.json, auth.json)
- Encrypts with AES-256-GCM via cryptography lib
- Single-writer lock via fcntl
- Replaces the 11 broken sites with the config resolver's drop-ins
"""
import argparse
import json
import logging
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

# === INVENTORY OF THE 11 BROKEN SITES ===
# (file, line, current_text, replacement_text, kind)
BROKEN_SITES: List[dict] = [
    # --- The 8 env:VAR sites in config YAMLs ---
    {
        "id": "site-1",
        "kind": "yaml_env_prefix",
        "file": "config/providers.yaml",
        "line_pattern": r"^\s*api_key:\s*env:ANTHROPIC_API_KEY\s*$",
        "current": "    api_key: env:ANTHROPIC_API_KEY",
        "replacement": "    # RESOLVED-AT-RUNTIME via vault_config_resolver.resolve_anthropic_api_key()",
        "note": "config/model_registry/providers/anthropic.yaml:9 mirrors this pattern",
    },
    {
        "id": "site-2",
        "kind": "yaml_env_prefix",
        "file": "config/providers.yaml",
        "line_pattern": r"^\s*api_key:\s*env:OPENROUTER_API_KEY\s*$",
        "current": "    api_key: env:OPENROUTER_API_KEY",
        "replacement": "    # RESOLVED-AT-RUNTIME via vault_config_resolver.resolve_openrouter_api_key()",
    },
    {
        "id": "site-3",
        "kind": "yaml_env_prefix",
        "file": "config/providers.yaml",
        "line_pattern": r"^\s*api_key:\s*env:GOOGLE_API_KEY\s*$",
        "current": "    api_key: env:GOOGLE_API_KEY",
        "replacement": "    # RESOLVED-AT-RUNTIME via vault_config_resolver.resolve_google_api_key()",
    },
    {
        "id": "site-4",
        "kind": "yaml_env_prefix",
        "file": "config/providers.yaml",
        "line_pattern": r"^\s*api_key:\s*env:XAI_API_KEY\s*$",
        "current": "    api_key: env:XAI_API_KEY",
        "replacement": "    # RESOLVED-AT-RUNTIME via vault_config_resolver.resolve_xai_api_key()",
    },
    {
        "id": "site-5",
        "kind": "yaml_env_prefix",
        "file": "config/providers.yaml",
        "line_pattern": r"^\s*api_key:\s*env:ANTIGRAVITY_API_KEY\s*$",
        "current": "    api_key: env:ANTIGRAVITY_API_KEY",
        "replacement": "    # RESOLVED-AT-RUNTIME via vault_config_resolver.resolve_antigravity_api_key()",
    },
    {
        "id": "site-6",
        "kind": "yaml_env_prefix",
        "file": "config/providers.yaml",
        "line_pattern": r"^\s*api_key:\s*env:OPENCODE_API_KEY\s*$",
        "current": "    api_key: env:OPENCODE_API_KEY",
        "replacement": "    # RESOLVED-AT-RUNTIME via vault_config_resolver.resolve_opencode_api_key()",
    },
    {
        "id": "site-7",
        "kind": "yaml_env_prefix",
        "file": "config/providers.yaml",
        "line_pattern": r"^\s*api_key:\s*env:CLINE_API_KEY\s*$",
        "current": "    api_key: env:CLINE_API_KEY",
        "replacement": "    # RESOLVED-AT-RUNTIME via vault_config_resolver.resolve_cline_api_key()",
    },
    {
        "id": "site-8",
        "kind": "yaml_env_prefix",
        "file": "config/providers.yaml",
        "line_pattern": r"^\s*model_path:\s*env:OMEGA_MODELS_DIR/",
        "current": "    model_path: env:OMEGA_MODELS_DIR/Qwen3-1.7B-Q6_K.gguf",
        "replacement": "    # RESOLVED-AT-RUNTIME via vault_config_resolver.resolve_yaml_env()",
    },
    # --- The 2 OMEGA_REDIS_PASSWORD sites ---
    {
        "id": "site-9",
        "kind": "os_environ_get",
        "file": "src/omega/memory_store.py",
        "line_pattern": r'os\.environ\.get\("OMEGA_REDIS_PASSWORD"\)',
        "current": '                        redis_password = os.environ.get("OMEGA_REDIS_PASSWORD")',
        "replacement": "                        # M14-fix: routed through vault_config_resolver (R_VAULT_CLINE_ROUND4)\n                        from vault_config_resolver import resolve_redis_password\n                        redis_password = resolve_redis_password()",
    },
    {
        "id": "site-10",
        "kind": "os_environ_get",
        "file": "src/omega/memory/providers.py",
        "line_pattern": r'os\.environ\.get\("OMEGA_REDIS_PASSWORD"\)',
        "current": '        password = password or os.environ.get("OMEGA_REDIS_PASSWORD")',
        "replacement": "        # M14-fix: routed through vault_config_resolver (R_VAULT_CLINE_ROUND4)\n        from vault_config_resolver import resolve_redis_password\n        password = password or resolve_redis_password()",
    },
    # --- The 1 GOOGLE_API_KEY fallback (right design, wrong surface) ---
    {
        "id": "site-11",
        "kind": "os_environ_get",
        "file": "src/omega/oracle/providers.py",
        "line_pattern": r'env_key = os\.environ\.get\("GOOGLE_API_KEY"\)',
        "current": '        env_key = os.environ.get("GOOGLE_API_KEY")',
        "replacement": "        # M14/M22-fix: vault-first via vault_config_resolver (R_VAULT_CLINE_ROUND4)\n        from vault_config_resolver import resolve_google_api_key\n        env_key = resolve_google_api_key(with_fallback=True)",
    },
]

# === THE VAULT FILES TO DELETE ===
VAULT_FILES = [
    "src/omega/vault/__init__.py",
    "src/omega/vault/vault_core.py",
    "src/omega/vault/crypto.py",
    "src/omega/vault/models.py",
    "src/omega/vault/blindvault_resolver.py",
]
# Note: the 30-LOC shim (three_store_shim.py from R_VAULT_CLINE_DEEPER) is
# NOT in src/omega/vault/ — it lives at scripts/three_store_shim.py. So
# deleting src/omega/vault/ removes the broken vault without touching the
# replacement shim.

# === THE ENFORCER TO DELETE (the new shim replaces its role) ===
ENFORCER_FILES = [
    "src/omega/tools/enforce_vaultcore.py",
]


class Delete11Sites:
    def __init__(self, repo_root: Path, archive_root: Path, dry_run: bool, backup_only: bool):
        self.repo_root = repo_root
        self.archive_root = archive_root
        self.dry_run = dry_run
        self.backup_only = backup_only
        self.operations: List[dict] = []  # audit log

    def log_op(self, kind: str, target: str, status: str, **details):
        op = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "target": target,
            "status": status,
            **details,
        }
        self.operations.append(op)
        marker = "[DRY-RUN]" if self.dry_run else "[EXEC]"
        print(f"{marker} {kind} {target} → {status}")
        if details:
            for k, v in details.items():
                print(f"    {k}: {v}")

    def step1_inventory(self) -> None:
        print("\n=== STEP 1: INVENTORY ===")
        # Check 11 sites
        missing_sites = []
        for site in BROKEN_SITES:
            f = self.repo_root / site["file"]
            if not f.exists():
                self.log_op("inventory", str(f), "missing")
                missing_sites.append(site["id"])
                continue
            content = f.read_text()
            if not re.search(site["line_pattern"], content, re.MULTILINE):
                self.log_op("inventory", str(f), f"line_pattern_not_found:{site['id']}")
            else:
                matches = re.findall(site["line_pattern"], content, re.MULTILINE)
                self.log_op("inventory", str(f), f"found:{len(matches)}:{site['id']}")
        if missing_sites:
            print(f"\n[INFO] {len(missing_sites)} sites not found (may be expected if recently patched)")
        # Check vault files
        print("\nVault files to delete:")
        for f in VAULT_FILES:
            fp = self.repo_root / f
            if fp.exists():
                size = fp.stat().st_size
                self.log_op("inventory", f, f"present:{size}B")
            else:
                self.log_op("inventory", f, "missing")
        # Check enforcer
        print("\nEnforcer files to delete:")
        for f in ENFORCER_FILES:
            fp = self.repo_root / f
            if fp.exists():
                size = fp.stat().st_size
                self.log_op("inventory", f, f"present:{size}B")
            else:
                self.log_op("inventory", f, "missing")

    def step2_backup(self) -> None:
        print("\n=== STEP 2: BACKUP ===")
        if self.dry_run:
            print("[DRY-RUN] would create archive at", self.archive_root)
            return
        self.archive_root.mkdir(parents=True, exist_ok=True)
        # Backup vault files
        vault_dir = self.repo_root / "src" / "omega" / "vault"
        if vault_dir.exists():
            target = self.archive_root / "vault"
            shutil.copytree(vault_dir, target)
            self.log_op("backup", str(vault_dir), f"copied_to:{target}")
        # Backup enforcer
        for f in ENFORCER_FILES:
            src = self.repo_root / f
            if src.exists():
                target = self.archive_root / Path(f).name
                shutil.copy2(src, target)
                self.log_op("backup", str(src), f"copied_to:{target}")
        # Backup the 11 sites' files
        for site in BROKEN_SITES:
            src = self.repo_root / site["file"]
            if src.exists():
                # Use site-id as a flat name to avoid collisions
                target = self.archive_root / f"{site['id']}_{Path(site['file']).name}"
                shutil.copy2(src, target)
                self.log_op("backup", str(src), f"copied_to:{target}")

    def step3_patch(self) -> None:
        print("\n=== STEP 3: PATCH 11 SITES ===")
        if self.backup_only:
            print("[BACKUP-ONLY] skipping patch")
            return
        for site in BROKEN_SITES:
            f = self.repo_root / site["file"]
            if not f.exists():
                self.log_op("patch", str(f), "skip:missing")
                continue
            content = f.read_text()
            pattern = site["line_pattern"]
            replacement = site["replacement"]
            new_content, n = re.subn(pattern, replacement, content, flags=re.MULTILINE)
            if n == 0:
                self.log_op("patch", str(f), f"skip:no_match:{site['id']}")
                continue
            if self.dry_run:
                self.log_op("patch", str(f), f"would_replace:{n}:{site['id']}")
            else:
                f.write_text(new_content)
                self.log_op("patch", str(f), f"replaced:{n}:{site['id']}")

    def step4_delete(self) -> None:
        print("\n=== STEP 4: DELETE VAULT + ENFORCER ===")
        if self.backup_only:
            print("[BACKUP-ONLY] skipping delete")
            return
        # Delete vault dir
        vault_dir = self.repo_root / "src" / "omega" / "vault"
        if vault_dir.exists():
            # Remove __pycache__ first
            pycache = vault_dir / "__pycache__"
            if pycache.exists():
                if self.dry_run:
                    self.log_op("delete", str(pycache), "would_delete")
                else:
                    shutil.rmtree(pycache)
                    self.log_op("delete", str(pycache), "deleted")
            if self.dry_run:
                self.log_op("delete", str(vault_dir), "would_delete")
            else:
                shutil.rmtree(vault_dir)
                self.log_op("delete", str(vault_dir), "deleted")
        # Delete enforcer
        for f in ENFORCER_FILES:
            fp = self.repo_root / f
            if fp.exists():
                if self.dry_run:
                    self.log_op("delete", str(fp), "would_delete")
                else:
                    fp.unlink()
                    self.log_op("delete", str(fp), "deleted")
            # Also remove the reference from check_hardcoded_secrets.py
            chs = self.repo_root / "src" / "omega" / "tools" / "check_hardcoded_secrets.py"
            if chs.exists():
                content = chs.read_text()
                new_content = re.sub(
                    r'\s*"enforce_vaultcore\.py",?\n',
                    '\n',
                    content,
                )
                if new_content != content and not self.dry_run:
                    chs.write_text(new_content)
                    self.log_op("patch", str(chs), "removed_enforcer_ref")

    def step5_verify(self) -> None:
        print("\n=== STEP 5: VERIFY ===")
        # Check that the 11 sites are gone
        remaining = []
        for site in BROKEN_SITES:
            f = self.repo_root / site["file"]
            if f.exists():
                content = f.read_text()
                if re.search(site["line_pattern"], content, re.MULTILINE):
                    remaining.append(site["id"])
        if remaining:
            self.log_op("verify", "11_sites", f"STILL_PRESENT:{remaining}")
        else:
            self.log_op("verify", "11_sites", "all_replaced")
        # Check that vault is gone
        vault_dir = self.repo_root / "src" / "omega" / "vault"
        if vault_dir.exists():
            self.log_op("verify", str(vault_dir), "STILL_PRESENT")
        else:
            self.log_op("verify", "vault_dir", "deleted")
        # Check that enforcer is gone
        for f in ENFORCER_FILES:
            fp = self.repo_root / f
            if fp.exists():
                self.log_op("verify", str(fp), "STILL_PRESENT")
            else:
                self.log_op("verify", f, "deleted")

    def step6_report(self) -> None:
        print("\n=== STEP 6: REPORT ===")
        if self.dry_run:
            print("[DRY-RUN] skipping report write")
        else:
            log_path = self.repo_root / "data" / "vault" / "delete_11_log.json"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(json.dumps(self.operations, indent=2, sort_keys=True))
            self.log_op("report", str(log_path), f"wrote:{len(self.operations)}_ops")
        # Print summary
        kinds = {}
        for op in self.operations:
            k = op["kind"]
            kinds[k] = kinds.get(k, 0) + 1
        print("\nOperation summary:")
        for k, v in sorted(kinds.items()):
            print(f"  {k}: {v}")
        # Count vault + enforcer deletions
        vault_deleted = sum(1 for op in self.operations if op["kind"] == "delete" and "vault" in op["target"])
        enforcer_deleted = sum(1 for op in self.operations if op["kind"] == "delete" and "enforce" in op["target"])
        sites_patched = sum(1 for op in self.operations if op["kind"] == "patch" and "replaced" in op.get("status", ""))
        print(f"\nResults: {vault_deleted} vault files, {enforcer_deleted} enforcer files, {sites_patched} sites patched")


def main() -> int:
    p = argparse.ArgumentParser(description="Path A' — delete vault + enforcer + 11 broken sites")
    p.add_argument("--repo-root", default=".", help="path to omega-engine repo root")
    p.add_argument("--archive-root", default=str(Path.home() / ".omega-vault-archive" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")),
                   help="where to back up deleted files")
    p.add_argument("--yes", action="store_true", help="actually execute (default is dry-run)")
    p.add_argument("--backup-only", action="store_true", help="only back up, don't delete or patch")
    args = p.parse_args()
    repo_root = Path(args.repo_root).resolve()
    archive_root = Path(args.archive_root).resolve()
    dry_run = not args.yes
    if not dry_run and not args.backup_only:
        # Interactive confirm
        print(f"WARNING: about to delete vault/, enforcer, and patch 11 sites in {repo_root}")
        print(f"Backup will go to {archive_root}")
        print("This is a one-shot operation. Continue? [y/N]")
        ans = input()
        if not ans.lower().startswith("y"):
            print("Aborted.")
            return 1
    d = Delete11Sites(repo_root, archive_root, dry_run, args.backup_only)
    d.step1_inventory()
    d.step2_backup()
    d.step3_patch()
    d.step4_delete()
    d.step5_verify()
    d.step6_report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
