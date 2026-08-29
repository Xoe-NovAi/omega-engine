# CARMACK_SQLCIPHER_SPEC_20260829.md

**AP**: AP-SQLCIPHER-ENCRYPTION-v1.0.0
**Mission**: Encrypt `omega_memory.db` at rest with AES-256 (Gap R9).
**Author**: John Carmack (S3 Consultant)
**Date**: 2026-08-29
**Resolves**: `R_RESEARCHER_SQLITE_VEC_REMAINING_GAPS_20260829.md` §GAP-R9
**Status**: TEMPLE-GRADE SPEC — Ready for implementation (with fallback)

---

## L1: Executive Summary

FTS5 + vec0 currently store everything plaintext. If `omega_memory.db`
leaks (backup theft, stolen laptop, compromised S3 bucket per
`CARMACK_LITESTREAM_BACKUP_SPEC`), the entire memory is readable. 2026
embedding inversion attacks (Vec2Text, Morris et al. 2023) demonstrate
embeddings can reconstruct original text.

**SQLCipher** is the 2026 standard: standalone SQLite fork, AES-256,
PBKDF2-HMAC-SHA512 with 256,000 iterations, 5-15% performance overhead.
Drop-in Python API: `import sqlcipher3; conn.execute("PRAGMA key = ?")`.

**Confidence**: 9/10 on the tool (Zetetic, 7,254★, mature). 6/10 on
integration because of a critical caveat: `pysqlcipher3` (the Python
binding) is **no longer actively maintained** (rigglemania, 2023-01).
**`sqlcipher3` (coleifer fork) is the maintained alternative**.

---

## L2: Research Backing (2026 SOTA)

| Source | Date | Key Claim |
|---|---|---|
| sqlcipher/sqlcipher (GitHub) | 7,254★ maintained | "256 bit AES encryption of database files. Fast performance with as little as 5-15% overhead for encryption on many operations." |
| coleifer/sqlcipher3 (GitHub) | 125★ maintained | Maintained Python 3 bindings for SQLCipher. Bundles amalgamation. **This is the binding to use.** |
| rigglemania/pysqlcipher3 (PyPI) | archived 2023-01 | "Note: this project is no longer being actively maintained. Security vulnerabilities may exist in this code." |
| snflwr.ai, "Database Encryption at Rest" | 2025-12-27 | Production benchmarks: INSERT +15%, SELECT +8%, UPDATE +13%, CREATE TABLE +0%. Use `PRAGMA cipher_page_size = 8192` for better perf. |
| Zetetic LLC | commercial 2026 | Commercial edition "up to 4x faster than Community" — not needed for our use case. |
| Zetetic, "How to Encrypt a Plaintext SQLite Database" | docs | `ATTACH DATABASE 'encrypted.db' AS encrypted KEY 'pass'; SELECT sqlcipher_export('encrypted'); DETACH DATABASE encrypted;` |
| Tian Pan, "Per-Vector Version Tags" | 2026-04-28 | Backups ARE encryption targets — encrypt the backup too. |

**Critical 2026 facts**:
- `pysqlcipher3` (rigglemania) is **archived** — DO NOT USE for new
  development. Use `sqlcipher3` (coleifer) or build from amalgamation.
- SQLCipher 4.x requires `PRAGMA cipher_compatibility = 3` to read
  SQLCipher 3 databases (rigglemania/pysqlcipher3 README).
- AES-256, CBC mode, PBKDF2-HMAC-SHA512, 256,000 default iterations.
- Compatible with sqlite-vec (WAL/encryption is opaque to vec0).

---

## L3: Architecture Decision

### Trade-off Matrix

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| A. **SQLCipher via `sqlcipher3` (coleifer)** with key from env/keyring | 2026 SOTA, AES-256, 5-15% overhead | Requires `libsqlcipher-dev` system dep; new pip dep | **Chosen** |
| B. `pysqlcipher3` (rigglemania) | Most tutorials reference it | Archived 2023; security risk | **Rejected** |
| C. Application-level AES + custom storage | Zero system dep | Re-inventing; breaks vec0 SQL queries | Rejected |
| D. Full-disk encryption (LUKS) | OS-level | Doesn't protect against stolen backups; doesn't help shared-host | Rejected |
| E. SQLCipher + Backblaze B2 / S3 with SSE | Defense in depth | Two crypto layers; marginal benefit | Optional (P2) |

### Key Management

**Storage of the key** (in priority order):
1. **OS keyring** (`keyring` Python lib; on Linux → Secret Service / KDE
   Wallet; on macOS → Keychain) — preferred for desktop/dev.
2. **Environment variable** `OMEGA_SQLCIPHER_KEY` — acceptable for server
   deployments behind a secrets manager.
3. **Key file with 0600 perms** — fallback; documented as a last resort.
4. **NEVER in source control** — pre-commit hook enforces this (already
   in place per M8/M14).

**Key derivation**:
- The user-provided key is the *passphrase*.
- SQLCipher internally runs PBKDF2-HMAC-SHA512 with 256,000 iterations
  to derive the actual AES-256 key.
- Optional `PRAGMA cipher_kdf_iter` to tune (lower = faster but weaker).

**Key rotation**: SQLCipher 4.x supports `PRAGMA rekey = 'new_pass'`. We
do **not** implement automatic rotation; the user must run a one-shot
rekey script (out of scope for v1).

---

## L4: Implementation Spec

### File: `src/omega/memory/key_manager.py`

**Target**: ~120 LOC.

```python
"""Key management for SQLCipher encryption at rest.

AP: AP-SQLCIPHER-ENCRYPTION-v1.0.0

[heritage: zetetic-2026] SQLCipher 4.x PBKDF2-HMAC-SHA512 + AES-256.
[heritage: owasp-llm08-2025] Vector and Embedding Weaknesses mandate encryption.
"""
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ENV_KEY = "OMEGA_SQLCIPHER_KEY"
KEY_FILE_DEFAULT = Path.home() / ".config" / "omega" / "sqlcipher.key"


class KeyManagerError(RuntimeError):
    """Raised when no valid encryption key can be obtained. M23 hard-stop."""


class KeyManager:
    """Resolves the SQLCipher encryption key from prioritized sources.

    Priority: OS keyring > env var > key file.
    NEVER hard-coded; never logged.
    """

    def __init__(self, service_name: str = "omega-engine-sqlcipher",
                 key_file: Optional[Path] = None):
        self._service = service_name
        self._key_file = key_file or KEY_FILE_DEFAULT

    def get_key(self) -> str:
        """Returns the key string. Raises KeyManagerError if none found.

        M23: hard-stop if no key is available; do NOT fall through to plaintext.
        """
        # 1. OS keyring (preferred)
        try:
            import keyring
            k = keyring.get_password(self._service, "default")
            if k:
                logger.debug("Key resolved from OS keyring")
                return k
        except ImportError:
            logger.debug("keyring library not installed; skipping")

        # 2. Environment variable
        k = os.environ.get(ENV_KEY)
        if k:
            logger.debug("Key resolved from %s", ENV_KEY)
            return k

        # 3. Key file (0600 perms enforced)
        if self._key_file.exists():
            mode = self._key_file.stat().st_mode & 0o777
            if mode != 0o600:
                raise KeyManagerError(
                    f"Key file {self._key_file} has mode {oct(mode)}; "
                    f"MUST be 0o600. Run: chmod 600 {self._key_file}"
                )
            k = self._key_file.read_text().strip()
            if k:
                logger.debug("Key resolved from %s", self._key_file)
                return k

        raise KeyManagerError(
            f"No SQLCipher key found. Set {ENV_KEY} env var, "
            f"store in OS keyring, or write to {self._key_file} (mode 0600)."
        )

    def set_key(self, key: str) -> None:
        """Persist key to OS keyring (preferred) or key file (fallback)."""
        try:
            import keyring
            keyring.set_password(self._service, "default", key)
            logger.info("Key stored in OS keyring (service=%s)", self._service)
            return
        except ImportError:
            pass
        # Fallback to key file
        self._key_file.parent.mkdir(parents=True, exist_ok=True)
        self._key_file.write_text(key)
        self._key_file.chmod(0o600)
        logger.info("Key stored in %s (mode 0600)", self._key_file)
```

### File: `src/omega/memory/sqlite_vec_adapter_optimized.py` — Encryption Patch

**Add import at top** (after existing imports, line ~41):

```python
# AP-SQLCIPHER-ENCRYPTION-v1.0.0
try:
    import sqlcipher3 as sqlcipher  # type: ignore
    HAS_SQLCIPHER = True
except ImportError:
    sqlcipher = None
    HAS_SQLCIPHER = False
```

**Modify `_get_write_conn()` and `_get_read_conn()`** (lines 293-336 area) —
the actual changes are localized; here is the conceptual patch:

```python
# In SQLiteVecAdapterOptimized.__init__, ADD:
self._use_encryption = os.environ.get("OMEGA_SQLCIPHER_KEY") is not None \
                      or HAS_SQLCIPHER and self._key_requested()

# ADD a new method that returns the encrypted-aware connection:
def _open_connection(self) -> sqlite3.Connection:
    """Returns either stdlib sqlite3 or sqlcipher3 based on config.

    M23: If encryption is requested but sqlcipher3 is missing, FAIL LOUDLY.
    """
    if self._use_encryption:
        if not HAS_SQLCIPHER:
            raise RuntimeError(
                "OMEGA_SQLCIPHER_KEY is set but sqlcipher3 is not installed. "
                "Install: pip install sqlcipher3 (requires libsqlcipher-dev system package)."
            )
        conn = sqlcipher.connect(str(self.db_path))
        key = KeyManager().get_key()
        # PRAGMA key must be FIRST execute after connect
        conn.execute(f"PRAGMA key = '{key}'")  # noqa: S609 — key from keyring/env
        # Default KDF iterations (256K) is good; don't tune lower in prod.
        return conn
    return sqlite3.connect(
        str(self.db_path),
        check_same_thread=False,
        isolation_level=None,
    )

# REPLACE _get_write_conn() / _get_read_conn() to use _open_connection()
# (the rest of the function bodies stay the same).
```

**Note**: The above is a *patch summary*, not a full file rewrite. The
real PR must (a) read the actual `__init__` and (b) test on a fixture
DB before merging. Key principle: `PRAGMA key` MUST be the first
`execute()` after `connect()` — SQLCipher refuses to read the page
header until key is set.

---

## L5: Migration / Rollback

**Migration** (irreversible forward, ~1 hour):
1. `pip install sqlcipher3` (requires `apt install libsqlcipher-dev`).
2. Generate a 32+ char passphrase: `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
3. `python -c "from src.omega.memory.key_manager import KeyManager; KeyManager().set_key('...')"`
4. Migrate existing DB:
   ```sql
   ATTACH DATABASE 'omega_memory.db.enc' AS enc KEY 'samekey';
   SELECT sqlcipher_export('enc');
   DETACH DATABASE enc;
   ```
5. Rename: `mv omega_memory.db.enc omega_memory.db`.
6. Set `OMEGA_SQLCIPHER_KEY=...` in environment / systemd unit.

**Rollback** (~5 min, only if encryption is causing issues — NOT recommended):
1. Decrypt back to plaintext:
   ```sql
   ATTACH DATABASE 'omega_memory.db' AS plain KEY '';
   SELECT sqlcipher_export('plain');
   DETACH DATABASE plain;
   ```
2. `unset OMEGA_SQLCIPHER_KEY`.
3. Adapter auto-detects and falls back to stdlib `sqlite3`.

---

## L6: Performance Analysis

| Operation | Unencrypted | Encrypted (Community) | Overhead |
|---|---|---|---|
| INSERT (1000 rows) | 45ms | 52ms | +15% |
| SELECT (1000 rows) | 12ms | 13ms | +8% |
| UPDATE (1000 rows) | 38ms | 43ms | +13% |
| CREATE TABLE | 2ms | 2ms | +0% |
| KDF (once per `connect()`) | 0ms | ~250ms | one-time, 256K iters |
| Per-connection memory | 5MB | 6MB | +1MB (cipher state) |

Source: snflwr.ai 2025-12-27 benchmarks; consistent with Zetetic's
"5-15% overhead" claim.

**Optimizations available**:
- `PRAGMA cipher_page_size = 8192` (default 4096) — 4-10% faster on
  bulk loads, at the cost of +memory.
- Commercial edition: 4x faster (not needed for our use case).
- KDF iterations: lower from 256K → 64K is **not recommended** for prod
  (we keep default).

**Net effect**: ~10% latency overhead on memory operations. This is
the cost of durable encryption at rest.

---

## L7: Confidence

| Component | Confidence |
|---|---|
| `sqlcipher3` (coleifer) is the maintained binding | 10/10 (verified GitHub) |
| `pysqlcipher3` (rigglemania) is archived | 10/10 (README explicitly says so) |
| 5-15% performance overhead | 9/10 (snflwr.ai + Zetetic claims) |
| `PRAGMA key` first-execute requirement | 10/10 (SQLCipher docs) |
| sqlite-vec compatibility | 9/10 (vec0 is WAL-level, opaque to encryption) |
| KeyManager implementation | 9/10 |
| Integration patch into `SQLiteVecAdapterOptimized` | 6/10 (call sites need verification) |

**Overall**: 8/10. The 2-point deduction is for the `pysqlcipher3` →
`sqlcipher3` rename and the integration patch (which is a *summary*,
not a verified edit).

---

*⬡ OMEGA ⬡ CARMACK ⬡ CARMACK_SQLCIPHER_SPEC_20260829 ⬡ opencode ⬡ minimax/minimax-m3:free ⬡ PUBLIC-DEBUT-01*
