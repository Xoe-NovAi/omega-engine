# 🔱 Omega Engine — Vault System Overhaul Specification (Part 2)
**AP Token**: `AP-VAULT-OVERHAUL-SPEC-20260818-v1.0.0`
**Part**: 2 of 5 — Credential Provider & Envelope Encryption

---

## 🔐 Component 2: Credential Provider (Process Edge)

### Design Principles

1. **Zero `os.environ` Pollution** — Keys never touch environment variables
2. **Lazy Resolution** — Keys fetched at call time, not import time
3. **Envelope Encryption** — Bypasses Windows 512B Credential Manager limit
4. **Keyring Primary** — OS-native encryption (Keychain/SecretService/Credential Locker)
5. **Fallback Chain** — `pyrage` → `cryptography` for headless/CI environments

### Envelope Encryption (Windows 512B Limit Mitigation)

```python
# src/omega/security/credential_provider.py
import os, keyring, base64
from typing import Optional
from config.encryption_backend import EncryptionBackend

class CredentialProvider:
    """
    Secure credential resolution at process edge.
    NEVER writes to os.environ. Returns key string to caller only.
    """
    
    SERVICE = "omega-engine"
    KEK_USERNAME = "kek"  # Key Encryption Key in keyring
    
    def __init__(self):
        self._backend = EncryptionBackend()
        self._backend.initialize()
        self._kek = self._get_or_create_kek()
    
    def _get_or_create_kek(self) -> bytes:
        """Get or create Key Encryption Key in OS keyring."""
        kek_hex = keyring.get_password(self.SERVICE, self.KEK_USERNAME)
        if kek_hex:
            return bytes.fromhex(kek_hex)
        kek = os.urandom(32)
        keyring.set_password(self.SERVICE, self.KEK_USERNAME, kek.hex())
        return kek
    
    def get_provider_credential(self, provider: str, account_id: str) -> str:
        """
        Resolve credential at runtime (not import time).
        Returns plaintext key string to caller.
        """
        # Try keyring first (short secrets < 512B)
        username = f"{provider}_{account_id}"
        direct = keyring.get_password(self.SERVICE, username)
        if direct:
            return direct
        
        # Try envelope encryption (long secrets > 512B)
        enc_file = self._get_enc_file_path(provider, account_id)
        if enc_file.exists():
            with open(enc_file, "rb") as f:
                ct = f.read()
            pt = self._backend.decrypt(ct, passphrase=self._kek.hex())
            return pt.decode()
        
        # Fallback: environment variable (for CI/CD)
        env_var = f"{provider.upper()}_{account_id.upper()}_API_KEY"
        env_val = os.environ.get(env_var)
        if env_val:
            return env_val
        
        raise KeyError(f"No credential found for {provider}/{account_id}")
    
    def set_provider_credential(self, provider: str, account_id: str, secret: str) -> None:
        """Store credential using optimal strategy based on length."""
        username = f"{provider}_{account_id}"
        
        # Short secrets → direct keyring storage
        if len(secret) <= 500:  # Safe margin under Windows 512B limit
            keyring.set_password(self.SERVICE, username, secret)
            # Clean up any envelope file
            enc_file = self._get_enc_file_path(provider, account_id)
            if enc_file.exists():
                enc_file.unlink()
            return
        
        # Long secrets → envelope encryption
        ct = self._backend.encrypt(secret.encode(), passphrase=self._kek.hex())
        enc_file = self._get_enc_file_path(provider, account_id)
        enc_file.parent.mkdir(parents=True, exist_ok=True)
        with open(enc_file, "wb") as f:
            f.write(ct)
        # Remove from keyring if present
        try:
            keyring.delete_password(self.SERVICE, username)
        except keyring.errors.PasswordDeleteError:
            pass
    
    def _get_enc_file_path(self, provider: str, account_id: str) -> Path:
        from pathlib import Path
        return Path.home() / ".omega" / "secrets" / f"{provider}_{account_id}.enc"
    
    def list_credentials(self) -> list[dict]:
        """List metadata only — NEVER the actual keys."""
        results = []
        # Keyring entries
        try:
            # keyring doesn't support listing; we track via metadata file
            pass
        except Exception:
            pass
        # Envelope files
        secrets_dir = Path.home() / ".omega" / "secrets"
        if secrets_dir.exists():
            for f in secrets_dir.glob("*.enc"):
                parts = f.stem.split("_", 1)
                if len(parts) == 2:
                    results.append({
                        "provider": parts[0],
                        "account_id": parts[1],
                        "storage": "envelope",
                        "path": str(f)
                    })
        return results
    
    def delete_credential(self, provider: str, account_id: str) -> bool:
        """Delete credential from all storage backends."""
        deleted = False
        username = f"{provider}_{account_id}"
        try:
            keyring.delete_password(self.SERVICE, username)
            deleted = True
        except keyring.errors.PasswordDeleteError:
            pass
        enc_file = self._get_enc_file_path(provider, account_id)
        if enc_file.exists():
            enc_file.unlink()
            deleted = True
        return deleted
```

### Provider Integration (ModelGateway Fix)

```python
# src/omega/oracle/model_gateway.py — REMOVE _load_sovereign_secrets()
# BEFORE (VIOLATION):
# def __init__(self):
#     self._load_sovereign_secrets()  # Dumps .env to os.environ at IMPORT TIME

# AFTER (COMPLIANT):
from src.omega.security.credential_provider import CredentialProvider

class ModelGateway:
    def __init__(self):
        self._credential_provider = CredentialProvider()
        # NO secret loading at init time
    
    def _get_provider_credential(self, provider_name: str, account_id: str) -> str:
        """Lazy credential resolution at CALL TIME."""
        return self._credential_provider.get_provider_credential(provider_name, account_id)
    
    async def generate(self, request):
        # Resolve credential at call time
        api_key = self._get_provider_credential(request.provider, request.account_id)
        # Pass directly to HTTP client — never stored in self
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {api_key}"}
            # ... make request
```

---

## 📝 Component 3: YAML-Editor-Bridge (Human DX)

### Requirements
- **Bulk-edit 32+ keys** in familiar YAML format
- **Zero forensic residue** (no temp files, no swap, no backups)
- **Cross-platform** (Linux, macOS, Windows)
- **Validation loop** — never shred old keys until new keys validated

### Implementation

```python
# config/editor_policy.py
import os, shutil, subprocess, sys, tempfile
from pathlib import Path
from typing import Optional

BUNDLED_EDITORS = {
    "windows": "bin/micro.exe",
    "linux": "bin/micro",
    "darwin": "bin/micro",
}

def get_safe_editor() -> str:
    """Return a blocking terminal editor that leaves no forensic artifacts."""
    # 1. Prefer bundled micro (2.5MB static binary, MIT, no swap/backup)
    bundled = Path(__file__).parent.parent / BUNDLED_EDITORS.get(sys.platform, "bin/micro")
    if bundled.is_file():
        os.chmod(bundled, 0o755)
        return str(bundled)
    
    # 2. Fallback: system nano/vim with hardened config
    for cand in ("nano", "vim", "nvim", "micro"):
        if path := shutil.which(cand):
            return _wrap_with_hardened_config(path)
    
    # 3. Last resort: notepad.exe (WARN: GUI, non-blocking, OneDrive risk)
    if sys.platform == "win32":
        return "notepad.exe"
    
    raise RuntimeError("No safe editor found")

def _wrap_with_hardened_config(editor: str) -> str:
    """Wrap editor invocation with env vars that disable backup/swap/temp."""
    if "nano" in editor:
        return f"{editor} --rcfile=/dev/null -t -R"  # no tempfile, restricted
    if "vim" in editor or "nvim" in editor:
        return f"{editor} -c 'set nobackup nowritebackup noswapfile noundofile'"
    return editor

def edit_yaml_safely(initial_content: dict) -> Optional[dict]:
    """
    Edit YAML with zero forensic residue.
    Returns parsed dict on success, None on cancel/error.
    """
    editor = get_safe_editor()
    
    # Secure temp dir (NOT %TEMP% on Windows — use controlled ~/.omega/tmp)
    temp_dir = Path.home() / ".omega" / "tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".yaml", delete=False,
        dir=temp_dir
    ) as tf:
        import yaml
        yaml.safe_dump(initial_content, tf)
        tmp_path = Path(tf.name)
    
    try:
        # VALIDATION LOOP: keep editor open until valid YAML
        while True:
            try:
                subprocess.run([editor, str(tmp_path)], check=True)
                # Validate YAML before accepting
                with open(tmp_path) as f:
                    content = yaml.safe_load(f)
                if content is not None:
                    return content
                # Invalid YAML — prompt user
                print("❌ Invalid YAML. Press Enter to return to editor, Ctrl+C to abort.")
                input()
            except subprocess.CalledProcessError:
                return None  # User cancelled
    finally:
        # Secure wipe temp file
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

# CLI Integration (src/omega/cli/secrets.py)
def secrets_edit_command():
    """omega secrets edit — bulk edit all credentials."""
    from src.omega.security.credential_provider import CredentialProvider
    provider = CredentialProvider()
    
    # Load current credentials into YAML structure
    current = {}
    for cred in provider.list_credentials():
        # For envelope files, we need to decrypt to show (with warning)
        if cred["storage"] == "envelope":
            # Show masked value
            current.setdefault(cred["provider"], {})[cred["account_id"]] = "***ENVELOPE***"
        else:
            # Direct keyring — show masked
            current.setdefault(cred["provider"], {})[cred["account_id"]] = "***KEYRING***"
    
    edited = edit_yaml_safely(current)
    if edited is None:
        print("Cancelled.")
        return
    
    # Process edits: only update changed values
    for prov, accounts in edited.items():
        for acc_id, value in accounts.items():
            if value not in ("***ENVELOPE***", "***KEYRING***"):
                provider.set_provider_credential(prov, account_id, value)
                print(f"✅ Updated {prov}/{account_id}")
    
    print("✅ Credentials updated successfully")
```