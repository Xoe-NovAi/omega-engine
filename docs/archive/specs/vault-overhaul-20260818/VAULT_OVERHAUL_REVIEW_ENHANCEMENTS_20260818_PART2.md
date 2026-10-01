# 🔱 Omega Engine — Vault Overhaul: Enhanced Architecture (Part 2)
**AP Token**: `AP-VAULT-REVIEW-ENHANCED-20260818-v1.0.0`
**Part**: 2 of 3 — Corrected Components (Supersedes spec Parts 1-4 where noted)

---

## 🔐 E-1: CredentialProvider v2 — Headless-Safe Resolution Chain

**Supersedes**: Spec Part 2 `CredentialProvider`. Fixes F-3 (NoKeyringError) + G-6 (typed errors) + G-5 (locks) + G-3 (audit).

### Resolution Order (Deterministic)

```
get_provider_credential(provider, account_id):
  1. OS keyring (SecretService/Keychain/wincred)     ← primary (encrypted at rest by OS)
  2. Envelope file ~/.omega/secrets/<p>_<a>.enc       ← long secrets (>2000 chars)
  3. Environment OMEGA_<PROVIDER>_<ACCOUNT>_API_KEY   ← CI only (documented)
  → CredentialNotFoundError(OmegaError) if all miss   ← M9 typed, no bare KeyError
```

### KEK Resolution Order (NEW — fixes headless crash)

```
_get_or_create_kek():
  1. keyring.get_password("omega-engine", "kek")      ← primary
  2. ~/.omega/kek.key (0600, created if missing)      ← headless fallback (F-3)
  3. OMEGA_KEK env var (64 hex chars)                 ← CI/container explicit
  → if none available: CREATE ~/.omega/kek.key (0600) + warn "headless mode"
```

### Corrected Implementation

```python
# src/omega/security/credential_provider.py (v2)
import os, sys, logging, time
from pathlib import Path
from typing import Optional

from omega.errors import OmegaError  # M9 typed error base

class CredentialNotFoundError(OmegaError):
    """Raised when no credential exists for provider/account in ANY backend."""

class CredentialProvider:
    SERVICE = "omega-engine"
    KEK_USERNAME = "kek"
    KEK_FILE = Path.home() / ".omega" / "kek.key"
    SECRETS_DIR = Path.home() / ".omega" / "secrets"
    AUDIT_LOG = Path.home() / ".omega" / "audit.log"
    DIRECT_THRESHOLD = 2000  # F-4: CRED_MAX_CREDENTIAL_BLOB_SIZE = 2560 bytes

    def __init__(self, backend=None):
        self._backend = backend or EncryptionBackend()
        self._backend.initialize()
        self._kek = self._get_or_create_kek()
        self._lock = _FileLock(self.SECRETS_DIR)  # G-5

    # ---- KEK management (F-3 headless fix) ----
    def _get_or_create_kek(self) -> bytes:
        # 1. keyring
        try:
            import keyring
            kek_hex = keyring.get_password(self.SERVICE, self.KEK_USERNAME)
            if kek_hex:
                return bytes.fromhex(kek_hex)
        except Exception as e:  # NoKeyringError, KeyringLocked, dbus errors
            logging.warning("keyring unavailable (%s); falling back to KEK file", e)

        # 2. KEK file (0600)
        if self.KEK_FILE.exists():
            return bytes.fromhex(self.KEK_FILE.read_text().strip())

        # 3. env (CI)
        env_kek = os.environ.get("OMEGA_KEK")
        if env_kek:
            return bytes.fromhex(env_kek)

        # 4. create file fallback (headless mode)
        kek = os.urandom(32)
        self.KEK_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.KEK_FILE.write_text(kek.hex())
        os.chmod(self.KEK_FILE, 0o600)
        logging.warning("headless mode: created %s (0600)", self.KEK_FILE)
        return kek

    # ---- credential resolution ----
    def get_provider_credential(self, provider: str, account_id: str, role: str = "runtime") -> str:
        username = f"{provider}_{account_id}"

        # 1. keyring direct (short secrets)
        try:
            import keyring
            direct = keyring.get_password(self.SERVICE, username)
            if direct:
                self._audit(provider, account_id, role, "keyring")
                return direct
        except Exception:
            pass  # headless — continue chain

        # 2. envelope file (long secrets)
        enc_file = self.SECRETS_DIR / f"{username}.enc"
        if enc_file.exists():
            with self._lock:
                ct = enc_file.read_bytes()
            pt = self._backend.decrypt(ct, passphrase=self._kek.hex())
            self._audit(provider, account_id, role, "envelope")
            return pt.decode()

        # 3. env (CI)
        env_var = f"OMEGA_{provider.upper()}_{account_id.upper()}_API_KEY"
        env_val = os.environ.get(env_var)
        if env_val:
            self._audit(provider, account_id, role, "env")
            return env_val

        raise CredentialNotFoundError(
            f"No credential for {provider}/{account_id} in keyring, envelope, or env"
        )

    def set_provider_credential(self, provider: str, account_id: str, secret: str) -> None:
        username = f"{provider}_{account_id}"
        with self._lock:
            if len(secret.encode()) <= self.DIRECT_THRESHOLD:
                try:
                    import keyring
                    keyring.set_password(self.SERVICE, username, secret)
                    self._remove_envelope(username)
                    return
                except Exception:
                    pass  # headless → envelope
            # envelope path (long OR headless)
            ct = self._backend.encrypt(secret.encode(), passphrase=self._kek.hex())
            self.SECRETS_DIR.mkdir(parents=True, exist_ok=True)
            (self.SECRETS_DIR / f"{username}.enc").write_bytes(ct)
            os.chmod(self.SECRETS_DIR / f"{username}.enc", 0o600)

    def delete_credential(self, provider: str, account_id: str) -> bool:
        username = f"{provider}_{account_id}"
        deleted = False
        try:
            import keyring
            keyring.delete_password(self.SERVICE, username)
            deleted = True
        except Exception:
            pass
        enc = self.SECRETS_DIR / f"{username}.enc"
        if enc.exists():
            with self._lock:
                enc.unlink()
            deleted = True
        return deleted

    # ---- audit (G-3, M22 provenance) ----
    def _audit(self, provider: str, account_id: str, role: str, backend: str) -> None:
        try:
            entry = f"{int(time.time())} provider={provider} account={account_id} role={role} backend={backend}\n"
            with open(self.AUDIT_LOG, "a") as f:
                f.write(entry)
            os.chmod(self.AUDIT_LOG, 0o600)
        except Exception:
            pass  # audit must never break credential resolution

# ---- G-5: cross-platform file lock ----
class _FileLock:
    def __init__(self, directory: Path):
        self._dir = directory
        self._dir.mkdir(parents=True, exist_ok=True)
        self._fd = None

    def __enter__(self):
        import fcntl if os.name == "posix" else msvcrt  # noqa
        self._fd = open(self._dir / ".lock", "a+b")
        if os.name == "posix":
            fcntl.flock(self._fd, fcntl.LOCK_EX)
        else:
            msvcrt.locking(self._fd, msvcrt.LK_LOCK, 1)
        return self

    def __exit__(self, *exc):
        if os.name == "posix":
            fcntl.flock(self._fd, fcntl.LOCK_UN)
        else:
            self._fd.seek(0); msvcrt.locking(self._fd, msvcrt.LK_UNLCK, 1)
        self._fd.close()
```

### ModelGateway Integration (unchanged from spec Part 2, but with role)

```python
# src/omega/oracle/model_gateway.py
async def generate(self, request, identity: ProviderIdentity, agent_role: AgentRole = None):
    if agent_role and not validate_agent_access(agent_role, "generate", identity):
        raise PermissionError(...)
    api_key = self._credential_provider.get_provider_credential(
        identity.provider, identity.account_id, role=agent_role.value if agent_role else "runtime"
    )
    # api_key lives ONLY in this scope; never stored on self
```

---

## 🛡️ E-2: Sanitizer v2 — flashtext2 Chain + Format Patterns

**Supersedes**: Spec Part 3 `EgressSanitizer` (flashtext → flashtext2, F-5) + `SecretRegistry` (adds G-2 format layer).

### Backend Chain

```python
# src/omega/security/sanitizer.py (v2)
class SanitizerBackend(ABC):
    @abstractmethod
    def build(self, keywords: dict[str, str]) -> None: ...
    @abstractmethod
    def replace(self, text: str) -> str: ...

class Flashtext2Backend(SanitizerBackend):      # PRIMARY (F-5)
    def build(self, keywords):
        from flashtext2 import KeywordProcessor
        self._kp = KeywordProcessor(case_sensitive=False)
        for k, v in keywords.items():
            self._kp.add_keyword(k, v)
    def replace(self, text):
        return self._kp.replace_keywords(text)

class AhoCorasickBackend(SanitizerBackend):     # FALLBACK 1
    def build(self, keywords):
        import ahocorasick
        self._auto = ahocorasick.Automaton()
        for k, v in keywords.items():
            self._auto.add_word(k, (k, v))
        self._auto.make_automaton()
    def replace(self, text):
        out, last = [], 0
        for end, (k, v) in self._auto.iter(text):
            start = end - len(k) + 1
            if start >= last:
                out.append(text[last:start]); out.append(v); last = end + 1
        out.append(text[last:])
        return "".join(out)

class RegexBackend(SanitizerBackend):           # FALLBACK 2 (zero-dep)
    def build(self, keywords):
        pat = "|".join(sorted((re.escape(k) for k in keywords), key=len, reverse=True))
        self._re = re.compile(pat, re.IGNORECASE)
        self._map = keywords
    def replace(self, text):
        return self._re.sub(lambda m: self._map[m.group(0).lower()], text)

def build_sanitizer(keywords: dict[str, str]) -> SanitizerBackend:
    for cls in (Flashtext2Backend, AhoCorasickBackend, RegexBackend):
        try:
            b = cls(); b.build(keywords); return b
        except ImportError:
            continue
    raise RuntimeError("no sanitizer backend")  # unreachable (regex is built-in)
```

### G-2: Format-Based Detection Layer (NEW)

Catches **unregistered** secrets by provider key format — the layer the original spec lacked:

```python
# src/omega/security/secret_registry.py — ADDITION
KEY_FORMAT_PATTERNS = [
    (r"sk-or-v1-[A-Za-z0-9]{20,}",            "openrouter"),
    (r"sk-ant-[A-Za-z0-9_-]{20,}",             "anthropic"),
    (r"AIza[0-9A-Za-z_-]{30,}",                "google"),
    (r"sk-[A-Za-z0-9]{32,}",                   "openai-generic"),
    (r"ghp_[A-Za-z0-9]{36,}",                  "github-pat"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}",          "slack"),
    (r"AKIA[0-9A-Z]{16}",                      "aws-access-key"),
    (r"age1[0-9a-z]{50,}",                     "age-recipient"),
    (r"AGE-SECRET-KEY-1[0-9A-Z]{50,}",         "age-identity"),
    (r"Bearer\s+[A-Za-z0-9._~+/=-]{20,}",      "bearer-token"),
]

class SecretRegistry:
    def scan_formats(self, text: str) -> list[tuple[str, str]]:
        """Detect provider-format key patterns (catches unregistered secrets)."""
        hits = []
        for pattern, provider in KEY_FORMAT_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                hits.append((m.group(), provider))
        return hits

    def sanitize_formats(self, text: str) -> str:
        """Redact any provider-format key, registered or not."""
        for pattern, provider in KEY_FORMAT_PATTERNS:
            text = re.sub(pattern, f"[REDACTED:{provider}]", text, flags=re.IGNORECASE)
        return text
```

**Egress flow (all 4 hooks)**: `sanitize(text) = format_redact(registered_replace(text))` — format layer first (catches everything), then exact-secret replacement for non-format secrets.

---

## ✏️ E-3: Editor Policy v2 — micro 2.0.15 + Checksum + tmpfs

**Supersedes**: Spec Part 2 `editor_policy.py` + Part 4 install.sh micro section. Fixes F-6, F-9.

```python
# config/editor_policy.py (v2)
MICRO_VERSION = "2.0.15"  # F-6: pinned, Dec 2025
MICRO_SHA256 = {
    "linux64": "…",   # from GitHub release digests (fill at impl time)
    "linux-arm64": "…",
    "linux-arm": "…",
    "win64": "…",
    "macos": "…",
}

def _secure_temp_dir() -> Path:
    """F-9: prefer tmpfs; fall back to controlled dir with 0600."""
    if sys.platform.startswith("linux") and Path("/dev/shm").is_dir():
        d = Path("/dev/shm") / f"omega-{os.getuid()}"
    else:
        d = Path.home() / ".omega" / "tmp"
    d.mkdir(mode=0o700, parents=True, exist_ok=True)
    return d

def edit_yaml_safely(initial_content: dict) -> Optional[dict]:
    editor = get_safe_editor()          # micro 2.0.15 primary (verified)
    tmp_dir = _secure_temp_dir()
    fd, tmp_name = tempfile.mkstemp(suffix=".yaml", dir=tmp_dir)
    os.close(fd)
    tmp_path = Path(tmp_name)
    os.chmod(tmp_path, 0o600)           # never world-readable
    try:
        with open(tmp_path, "w") as f:
            yaml.safe_dump(initial_content, f)
        while True:
            try:
                subprocess.run([editor, str(tmp_path)], check=True)
                with open(tmp_path) as f:
                    content = yaml.safe_load(f)
                if content is not None:
                    return content
                input("❌ Invalid YAML. Enter to re-edit, Ctrl+C to abort.")
            except (subprocess.CalledProcessError, KeyboardInterrupt):
                return None
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
```

**install.sh micro section (v2)** — checksum-verified download:

```bash
MICRO_VERSION="2.0.15"
MICRO_SHA256_LINUX64="<fill-from-github-release>"
curl -fsSL "https://github.com/micro-editor/micro/releases/download/v${MICRO_VERSION}/micro-${MICRO_VERSION}-linux64.tar.gz" -o /tmp/micro.tgz
echo "${MICRO_SHA256_LINUX64}  /tmp/micro.tgz" | sha256sum -c -   # F-6 supply chain
tar xzf /tmp/micro.tgz -C bin --strip-components=1 micro-${MICRO_VERSION}/micro
chmod 0755 bin/micro && rm /tmp/micro.tgz
```

---

## 🏰 E-4: systemd/AppArmor Reconciliation (F-7, F-8)

**Supersedes**: Spec Part 4 systemd drop-in + AppArmor profile.

### Principle
- **Interactive engine** (OpenCode host, `omega talk`, CLI): **user session** — no systemd unit. Keyring works natively. ✅
- **MCP hub daemon** (long-running): hardened unit but **keyring-compatible**:

```ini
# /etc/systemd/system/omega-hub.service.d/10-hardening.conf
[Service]
User=%i                      # keep the USER's uid (NOT a dedicated omega user)
ProtectSystem=strict
ProtectHome=read-only        # F-7 FIX: NOT true — /run/user must stay visible
ReadWritePaths=/home/%u/.omega /var/log/omega
BindPaths=/run/user/%U       # F-7: D-Bus session socket for keyring
PrivateTmp=true
PrivateDevices=true
NoNewPrivileges=true
CapabilityBoundingSet=
SystemCallFilter=@system-service
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictNamespaces=true
RestrictRealtime=true
RestrictSUIDSGID=true
LockPersonality=true
MemoryMax=4G
MemoryHigh=3G
OOMScoreAdjust=-300
LimitCORE=0
```

### AppArmor v2 (F-8 fix — real enforcement)

```apparmor
# /etc/apparmor.d/omega.engine
#include <tunables/global>
#include <abstractions/python>

/usr/local/bin/omega-engine {
  # D-Bus mediation (REAL protection — F-8):
  #   deny peer=(label=org.freedesktop.secrets) — blocks keyring reads
  #   (only for sandboxed subagent profile, NOT the engine itself)
  dbus (receive) peer=(label=org.freedesktop.secrets),
  dbus (send) peer=(label=org.freedesktop.DBus),

  # Sensitive paths — deny reads (real protection for auth.json)
  deny /home/*/.local/share/opencode/auth.json r,
  deny /home/*/.ssh/** r,
  deny /home/*/.aws/** r,
  deny /home/*/.gnupg/** r,

  # Engine paths
  /home/*/.omega/** rw,
  /var/log/omega/** rw,
}
```

**Note**: The `deny /usr/bin/keyring` lines from spec Part 4 are REMOVED (cosmetic, F-8). Real subagent isolation = bwrap with `--ro-bind /dev/null` over the D-Bus socket + AppArmor dbus peer denial.

---

## 🔄 E-5: Export/Import/Rekey (G-1 — NEW)

```python
# src/omega/cli/secrets.py — ADDITIONS
def secrets_export_command(out_path: Path, passphrase: str = None):
    """Export ALL credentials as one age-encrypted bundle (G-1)."""
    provider = CredentialProvider()
    bundle = {}
    for cred in provider.list_credentials():
        try:
            bundle[f"{cred['provider']}_{cred['account_id']}"] = \
                provider.get_provider_credential(cred["provider"], cred["account_id"])
        except CredentialNotFoundError:
            continue
    data = json.dumps(bundle).encode()
    ct = provider._backend.encrypt(data, passphrase=passphrase or _prompt_passphrase())
    out_path.write_bytes(ct)
    os.chmod(out_path, 0o600)
    print(f"✅ Exported {len(bundle)} credentials to {out_path}")

def secrets_import_command(in_path: Path, passphrase: str = None):
    """Import credentials from an encrypted bundle (G-1)."""
    provider = CredentialProvider()
    ct = in_path.read_bytes()
    data = provider._backend.decrypt(ct, passphrase=passphrase or _prompt_passphrase())
    bundle = json.loads(data)
    for key, value in bundle.items():
        prov, acc = key.rsplit("_", 1)
        provider.set_provider_credential(prov, acc, value)
    print(f"✅ Imported {len(bundle)} credentials")

def secrets_rekey_command():
    """Re-encrypt all envelope files with a fresh KEK (G-1)."""
    provider = CredentialProvider()
    old_kek = provider._kek
    new_kek = os.urandom(32)
    for enc in provider.SECRETS_DIR.glob("*.enc"):
        ct = enc.read_bytes()
        pt = provider._backend.decrypt(ct, passphrase=old_kek.hex())
        enc.write_bytes(provider._backend.encrypt(pt, passphrase=new_kek.hex()))
    # persist new KEK (keyring first, then file)
    try:
        import keyring
        keyring.set_password(provider.SERVICE, provider.KEK_USERNAME, new_kek.hex())
    except Exception:
        provider.KEK_FILE.write_text(new_kek.hex()); os.chmod(provider.KEK_FILE, 0o600)
    print("✅ Rekeyed all envelope files")
```

---

## 🖥️ E-6: CLI Exposure Reduction (G-4)

```python
def secrets_get_command(provider: str, account_id: str, clipboard: bool = False):
    """Get a credential WITHOUT printing to stdout by default (G-4)."""
    value = CredentialProvider().get_provider_credential(provider, account_id)
    if clipboard:
        _copy_to_clipboard(value)   # pyperclip (optional dep) or OSC52
        print(f"✅ Copied {provider}/{account_id} to clipboard")
    else:
        print("⚠️  Printing secret to stdout — scrollback risk!")
        print(value)
```

**Shell history**: `omega secrets get` never accepts the secret as an argument (only provider/account names) — no secret ever enters shell history. ✅

---

## 📋 E-7: RBAC v2 — Honest Advisory + Rotate Permissions (G-7)

| Agent Role | generate | list_providers | see_metadata | **rotate** | see_value |
|------------|----------|----------------|--------------|------------|-----------|
| ORCHESTRATOR | ✅ | ✅ | ✅ | ✅ | ❌ (never) |
| BUILDER | ✅ | ✅ | ✅ | ✅ | ❌ |
| RESEARCHER | ✅ | ✅ | ❌ | ❌ | ❌ |
| RUNTIME | ❌ (via Oracle) | ❌ | ❌ | ❌ | ❌ |

**Honesty note (G-7)**: RBAC is enforced at the ModelGateway API boundary. Any agent running as the same OS user can read `~/.omega/kek.key` or call keyring directly — **true enforcement requires OS-level sandboxing** (bwrap for subagents, AppArmor dbus mediation). Documented as accepted for debut; OS enforcement is the post-debut hardening item.

---

*⬡ OMEGA ⬡ VAULT-REVIEW ⬡ PART 2/3 ⬡ 2026-08-18*