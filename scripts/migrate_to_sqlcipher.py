#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""One-shot migration: plaintext omega_memory.db → SQLCipher-encrypted.
AP: AP-SQLCIPHER-ENCRYPTION-v1.0.0

Migrates an existing SQLite database to a SQLCipher-encrypted copy using the
canonical Zetetic `sqlcipher_export` recipe. Atomic on success; safe rollback
to the plaintext original if verification fails.

Usage:
    # Dry-run: verify the source DB is readable, no files written
    python scripts/migrate_to_sqlcipher.py --dry-run

    # Live migration (with confirm prompt)
    python scripts/migrate_to_sqlcipher.py

    # Live migration, non-interactive (env-driven)
    OMEGA_SQLCIPHER_KEY=... python scripts/migrate_to_sqlcipher.py --yes

Process:
    1. Verify source DB integrity (PRAGMA integrity_check).
    2. Open new encrypted DB; run sqlcipher_export from source.
    3. Verify encrypted DB integrity + spot-check schema.
    4. Atomically swap: rename original to .plaintext.bak, move encrypted
       to original path.
    5. Print operator instructions for cleanup.

References:
    - Zetetic, "How to Encrypt a Plaintext SQLite Database"
    - coleifer/sqlcipher3 (maintained Python binding)
    - Tian Pan 2026-04-28: backups are encryption targets.

Safety:
    - Source file is NEVER modified in place.
    - If anything fails, the .plaintext.bak file remains untouched.
    - Operator must explicitly remove the .plaintext.bak file after
      verifying the encrypted copy works (we do NOT auto-delete).
"""
from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

# Third-party — only required for live mode.
try:
    import sqlcipher3 as _sqlcipher  # type: ignore[import-untyped]
    HAS_SQLCIPHER = True
except ImportError:
    _sqlcipher = None  # type: ignore[assignment]
    HAS_SQLCIPHER = False


# ── Errors ────────────────────────────────────────────────────────────────
class MigrationError(RuntimeError):
    """Raised on any non-recoverable failure. Operator should investigate."""


# ── Helpers ───────────────────────────────────────────────────────────────
def log(msg: str) -> None:
    print(f"  → {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"  ! {msg}", file=sys.stderr, flush=True)


def fail(msg: str) -> None:
    print(f"  ✗ {msg}", file=sys.stderr, flush=True)


def check_source_integrity(db_path: Path) -> None:
    """Run PRAGMA integrity_check on the source DB. M9 Error Integrity."""
    log(f"Verifying source DB integrity: {db_path}")
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        result = conn.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise MigrationError(
                f"Source DB integrity_check failed: {result[0] if result else 'no result'}. "
                f"Run sqlite3 {db_path} 'PRAGMA integrity_check;' before migrating."
            )
        table_count = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        log(f"Source DB integrity OK. {table_count} tables found.")
    finally:
        conn.close()


def encrypt_database(
    source: Path, encrypted: Path, key: str
) -> None:
    """Run the canonical sqlcipher_export recipe.

    1. ATTACH the encrypted DB with the key.
    2. sqlcipher_export reads the entire schema + contents from the
       plaintext DB and writes them encrypted.
    3. DETACH.

    This is the Zetetic-documented pattern; do not improvise.
    """
    if not HAS_SQLCIPHER or _sqlcipher is None:  # type: ignore[truthy-bool]
        raise MigrationError("sqlcipher3 is not installed")
    log(f"Opening encrypted target: {encrypted}")
    enc_conn = _sqlcipher.connect(str(encrypted))
    try:
        # PRAGMA key MUST be first — SQLCipher refuses otherwise.
        enc_conn.execute("PRAGMA key = ?", (key,))
        enc_conn.execute("PRAGMA cipher_kdf_iter = 256000")
        # 4.x default; explicit for clarity.

        log("Attaching source DB (plaintext, read-only)…")
        enc_conn.execute(f"ATTACH DATABASE ? AS source KEY ''", (str(source),))

        log("Running sqlcipher_export (copies schema + all rows)…")
        enc_conn.execute("SELECT sqlcipher_export('source')")

        log("Detaching source…")
        enc_conn.execute("DETACH DATABASE source")
        enc_conn.commit()
    finally:
        enc_conn.close()


def check_encrypted_integrity(db_path: Path, key: str) -> None:
    """Open the encrypted DB with the key and verify integrity."""
    if not HAS_SQLCIPHER or _sqlcipher is None:  # type: ignore[truthy-bool]
        raise MigrationError("sqlcipher3 is not installed")
    log(f"Verifying encrypted DB integrity: {db_path}")
    conn = _sqlcipher.connect(str(db_path))
    try:
        conn.execute("PRAGMA key = ?", (key,))
        # Read the page header to force KDF. If the key is wrong, this fails.
        result = conn.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise MigrationError(
                f"Encrypted DB integrity_check failed: {result[0] if result else 'no result'}"
            )
        table_count = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        log(f"Encrypted DB integrity OK. {table_count} tables found.")
        if table_count == 0:
            raise MigrationError(
                "Encrypted DB has zero tables — sqlcipher_export likely failed silently."
            )
    finally:
        conn.close()


# ── Main ─────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate plaintext omega_memory.db → SQLCipher-encrypted.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(os.environ.get("OMEGA_MEMORY_DB", "/var/lib/omega/omega_memory.db")),
        help="Path to the plaintext database (default: $OMEGA_MEMORY_DB)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify source integrity only; do not write any files",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirm prompt (for scripted migrations)",
    )
    args = parser.parse_args()

    source: Path = args.db
    if not source.exists():
        fail(f"Source DB not found: {source}")
        return 1

    # Pre-flight: integrity check
    try:
        check_source_integrity(source)
    except MigrationError as e:
        fail(str(e))
        return 2

    if args.dry_run:
        log("DRY RUN: source is healthy. Re-run without --dry-run to migrate.")
        return 0

    # Required tools
    if not HAS_SQLCIPHER:
        fail(
            "sqlcipher3 not installed. Install: pip install sqlcipher3 "
            "(requires libsqlcipher-dev system package)."
        )
        return 3

    # Resolve key — must use the same resolver as the engine
    try:
        from omega.memory.key_manager import KeyManager  # type: ignore
        key = KeyManager().get_key()
    except Exception as e:  # ImportError or KeyManagerError
        fail(f"Could not resolve encryption key: {e}")
        return 4

    if not args.yes:
        print()
        print("  ⚠  About to migrate: %s" % source)
        print("     - Source will be moved to %s.plaintext.bak" % source)
        print("     - Encrypted copy will be created at the same path")
        print("     - The plaintext .bak will NOT be auto-deleted")
        print()
        try:
            confirm = input("  Continue? [yes/no]: ").strip().lower()
        except EOFError:
            confirm = "no"
        if confirm != "yes":
            log("Aborted by operator.")
            return 0

    # 1. Encrypt to a tempfile in the same directory (atomic rename later)
    source_dir = source.parent
    with tempfile.NamedTemporaryFile(
        prefix=source.name + ".enc.",
        suffix=".tmp",
        dir=str(source_dir),
        delete=False,
    ) as tmp:
        tmp_path = Path(tmp.name)
    try:
        encrypt_database(source, tmp_path, key)
        check_encrypted_integrity(tmp_path, key)

        # 2. Atomic swap: original → .plaintext.bak, encrypted → original
        backup = source.with_suffix(source.suffix + ".plaintext.bak")
        if backup.exists():
            # If a previous migration's backup is still here, don't clobber.
            backup = source.with_suffix(
                f".plaintext.bak.{int(time.time())}"
            )
            warn(f"Existing backup found; using timestamped name: {backup}")

        log(f"Renaming original → {backup}")
        shutil.move(str(source), str(backup))

        log(f"Renaming encrypted tmp → {source}")
        shutil.move(str(tmp_path), str(source))

        # 3. Permissions
        try:
            os.chmod(source, 0o640)
            log("Set perms 0640 on encrypted DB.")
        except OSError as e:
            warn(f"Could not set perms on encrypted DB: {e}")

        print()
        log("Migration complete.")
        log("Original plaintext DB is preserved at: %s" % backup)
        log("Encrypted DB is now at:                 %s" % source)
        log("")
        log("Next steps:")
        log("  1. Verify the engine can read the encrypted DB:  systemctl restart <omega>")
        log("  2. After 7 days of successful operation:")
        log("       sudo rm %s" % backup)
        log("  3. If something is wrong, restore plaintext:")
        log("       sudo systemctl stop <omega>")
        log("       sudo mv %s %s" % (backup, source))
        log("       sudo systemctl start <omega>")
        return 0
    except Exception as e:
        fail(f"Migration failed: {e}")
        # Cleanup: remove the partial encrypted tmp if it exists
        if tmp_path.exists():
            try:
                tmp_path.unlink()
                log("Removed partial encrypted file.")
            except OSError:
                warn(f"Could not remove partial file: {tmp_path}")
        return 5


if __name__ == "__main__":
    sys.exit(main())
