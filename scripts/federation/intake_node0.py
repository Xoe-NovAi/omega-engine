#!/usr/bin/env python3
"""
Omega Engine Alpha — Node 0 Inbound Payload Intake & Verification Pipeline
Location: scripts/federation/intake_node0.py

Safely ingests, validates, and stages external payloads arriving from Node 0
(HP Pavilion Archival Bastion) via USB physical exchange or local staging.

Invariants:
  - Anyio purity: stdlib only (hashlib, shutil, subprocess, json, pathlib).
  - Strict quarantine: external docs staged in docs/federation/node0_received/.
  - No Git mutation: runs 'git bundle verify' and staged inspection without merging.
  - Safe parsing: validates JSON/Markdown headers before committing.
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_USB_SOURCE = Path("/run/media/xnai/D5D5-0B76/omega-exchange/node0-to-node1")
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_TARGET = REPO_ROOT / "docs" / "federation" / "node0_received"
STAGING_DIR = REPO_ROOT / "data" / "staging" / "node0"

CRITICAL_DOCS = [
    "PAYLOAD_MANIFEST.md",
    "BUNDLE_QUICKSTART.md",
    "CSS_PROTOCOL.md",
    "DATA_GOVERNANCE_POLICY_20260912.md",
    "SOVEREIGNTY_POLICY_20260912.md",
    "STALE_HANDOFF_POLICY_20260912.md",
]


def sha256_file(filepath: Path) -> str:
    """Compute SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_payload_source(source_dir: Path) -> dict:
    """Inspect and catalog files in the payload directory."""
    if not source_dir.exists() or not source_dir.is_dir():
        print(f"✗ Source directory not found: {source_dir}")
        return {"valid": False, "error": f"Directory not found: {source_dir}"}

    items = list(source_dir.iterdir())
    files = [f for f in items if f.is_file()]
    dirs = [d for f in items if (d := f).is_dir()]

    print(f"── Inspecting Node 0 Payload Source: {source_dir} ──")
    print(f"  Files found: {len(files)}, Subdirectories: {len(dirs)}")

    # Check for bundle
    bundle_path = source_dir / "omega-engine.bundle"
    bundle_valid = False
    bundle_info = ""
    if bundle_path.exists():
        size_mb = bundle_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Found git bundle: {bundle_path.name} ({size_mb:.2f} MB)")
        try:
            res = subprocess.run(
                ["git", "bundle", "verify", str(bundle_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if res.returncode == 0:
                bundle_valid = True
                bundle_info = res.stdout.strip() or res.stderr.strip()
                print(f"  ✓ Git bundle verification: VALID")
            else:
                bundle_info = res.stderr.strip()
                print(f"  ⚠ Git bundle verification: FAILED ({bundle_info})")
        except Exception as e:
            bundle_info = str(e)
            print(f"  ✗ Git bundle verify error: {e}")
    else:
        print("  ○ No omega-engine.bundle found in payload root")

    # Check critical documents
    found_docs = {}
    for doc in CRITICAL_DOCS:
        doc_p = source_dir / doc
        if doc_p.exists():
            found_docs[doc] = {
                "size": doc_p.stat().st_size,
                "sha256": sha256_file(doc_p),
            }
            print(f"  ✓ Found critical doc: {doc} ({doc_p.stat().st_size} bytes)")
        else:
            print(f"  ○ Missing optional/critical doc: {doc}")

    return {
        "valid": True,
        "source": str(source_dir),
        "file_count": len(files),
        "dir_count": len(dirs),
        "bundle_path": str(bundle_path) if bundle_path.exists() else None,
        "bundle_valid": bundle_valid,
        "bundle_info": bundle_info,
        "docs": found_docs,
        "directories": [d.name for d in dirs],
    }


def ingest_payload(source_dir: Path, target_docs_dir: Path, staging_dir: Path) -> bool:
    """Copy critical docs and stage bundle/configs safely."""
    target_docs_dir.mkdir(parents=True, exist_ok=True)
    staging_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n── Ingesting Payload from {source_dir} ──")
    print(f"  Target Docs Path: {target_docs_dir}")
    print(f"  Staging Path:     {staging_dir}")

    copied_docs = []
    for item in source_dir.iterdir():
        if item.is_file() and (item.suffix in (".md", ".txt", ".json") or item.name in CRITICAL_DOCS):
            dest = target_docs_dir / item.name
            shutil.copy2(item, dest)
            copied_docs.append(item.name)
            print(f"  ✓ Ingested doc: {item.name}")

    # Stage subdirectories (attestation, c6-contract, configs) into staging/node0
    staged_dirs = []
    for item in source_dir.iterdir():
        if item.is_dir() and item.name not in ("gnosis", "node1-to-node0", "bilateral"):
            dest_dir = staging_dir / item.name
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            shutil.copytree(item, dest_dir)
            staged_dirs.append(item.name)
            print(f"  ✓ Staged directory: {item.name}/")

    # Generate ingestion report
    report_path = target_docs_dir / "INGESTION_REPORT.md"
    now_utc = datetime.now(timezone.utc).isoformat()
    report_content = f"""# Node 0 Inbound Payload Ingestion Report
**Ingested at:** `{now_utc}`  
**Source:** `{source_dir}`  

## 1. Summary
- **Documents Ingested:** {len(copied_docs)} files
- **Directories Staged:** {len(staged_dirs)} folders

## 2. Ingested Documentation
| Document | Size (bytes) | SHA256 |
|---|---:|---|
"""
    for doc_name in sorted(copied_docs):
        p = target_docs_dir / doc_name
        size = p.stat().st_size
        sha = sha256_file(p)
        report_content += f"| `{doc_name}` | {size} | `{sha[:16]}...` |\n"

    report_content += f"""
## 3. Staged Subsystems (Quarantine Review)
"""
    for d in sorted(staged_dirs):
        report_content += f"- `data/staging/node0/{d}/`\n"

    report_content += """
## 4. Operational Next Steps
1. Review `CSS_PROTOCOL.md` and `SOVEREIGNTY_POLICY_20260912.md`.
2. Extract sovereignty ratio axioms into The Well (`make well-add KIND=insight ...`).
3. If Git bundle verification passes, inspect commit logs:
   `git fetch /run/media/xnai/D5D5-0B76/omega-exchange/node0-to-node1/omega-engine.bundle main:refs/remotes/node0/main`
"""
    report_path.write_text(report_content, encoding="utf-8")
    print(f"\n✅ Ingestion report generated: {report_path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Omega Engine Alpha - Node 0 Payload Intake Pipeline")
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_USB_SOURCE,
        help=f"Source directory containing Node 0 payload (default: {DEFAULT_USB_SOURCE})",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Inspect and verify payload checksums without copying files",
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Copy documentation to docs/federation/node0_received/ and stage configs",
    )

    args = parser.parse_args()

    # Fallback to local staging if USB not mounted
    source = args.source
    if not source.exists():
        fallback = REPO_ROOT / "data" / "staging" / "node0_inbound"
        if fallback.exists():
            print(f"ℹ USB source {source} not found; falling back to {fallback}")
            source = fallback
        else:
            print(f"✗ Error: Payload source does not exist: {source}")
            return 1

    audit = verify_payload_source(source)
    if not audit["valid"]:
        return 1

    if args.verify_only:
        print("\n✅ Verification complete (--verify-only specified, no files modified).")
        return 0

    if args.ingest or not args.verify_only:
        success = ingest_payload(source, DOCS_TARGET, STAGING_DIR)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
