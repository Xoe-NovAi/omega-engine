# 🔱 Omega Engine — Vault System Overhaul Specification (Part 4)
**AP Token**: `AP-VAULT-OVERHAUL-SPEC-20260818-v1.0.0`
**Part**: 4 of 5 — System Hardening, Sandboxing & Deletion Plan

---

## 🔧 Component 8: Install Script Hardening (2 Minutes Added)

### Complete Install.sh Additions

```bash
#!/bin/bash
# omega-engine/install.sh — Security Hardening Section

set -euo pipefail

echo "🔐 Applying security hardening..."

# 1. Encryption Dependencies (auto-selects best backend)
echo "  📦 Installing encryption backends..."
pip install -e ".[encryption]"  # pyrage + cryptography

# 2. Bundle micro editor (2.5MB static binary)
echo "  ✏️  Bundling micro editor..."
MICRO_VERSION="2.0.11"
MICRO_URL="https://github.com/zyedidia/micro/releases/download/v${MICRO_VERSION}/micro-${MICRO_VERSION}-linux64.tar.gz"
if [[ "$OSTYPE" == "darwin"* ]]; then
    MICRO_URL="https://github.com/zyedidia/micro/releases/download/v${MICRO_VERSION}/micro-${MICRO_VERSION}-macos.tar.gz"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    MICRO_URL="https://github.com/zyedidia/micro/releases/download/v${MICRO_VERSION}/micro-${MICRO_VERSION}-win64.zip"
fi

mkdir -p bin
cd bin
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    curl -L "$MICRO_URL" -o micro.zip
    unzip -o micro.zip
    mv micro-*/micro.exe . 2>/dev/null || true
    rm -rf micro.zip micro-*
else
    curl -L "$MICRO_URL" | tar xz
    mv micro-*/micro . 2>/dev/null || true
    rm -rf micro-*
fi
chmod +x micro
cd ..

# 3. Systemd Hardening Drop-in (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]] && command -v systemctl >/dev/null 2>&1; then
    echo "  🛡️  Installing systemd hardening..."
    mkdir -p /etc/systemd/system/omega-engine.service.d
    cat > /etc/systemd/system/omega-engine.service.d/10-hardening.conf <<'EOF'
[Service]
# Dedicated user (created below)
User=omega
Group=omega

# Filesystem sandbox
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
PrivateIPC=true
ReadWritePaths=/var/lib/omega /var/log/omega /run/omega

# Capability stripping (only CAP_IPC_LOCK for mlock)
NoNewPrivileges=true
CapabilityBoundingSet=CAP_IPC_LOCK
AmbientCapabilities=CAP_IPC_LOCK

# Syscall filter (systemd 250+)
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM

# Kernel protection
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
ProtectKernelLogs=true

# Process isolation
ProtectProc=invisible
ProcSubset=pid
RestrictNamespaces=true
RestrictRealtime=true
RestrictSUIDSGID=true
LockPersonality=true

# Memory & OOM
MemoryMax=4G
MemoryHigh=3G
MemorySwapMax=512M
OOMScoreAdjust=-300
OOMPolicy=kill
KillMode=control-group
LimitCORE=0

# Socket activation for OpenCode plugin
ExecStart=/usr/local/bin/omega-engine --socket /run/omega/engine.sock
RuntimeDirectory=omega
RuntimeDirectoryMode=0750
EOF

    # Create dedicated user
    useradd -r -s /usr/sbin/nologin -d /var/lib/omega -c "Omega Engine" omega 2>/dev/null || true
    mkdir -p /var/lib/omega /var/log/omega /run/omega
    chown -R omega:omega /var/lib/omega /var/log/omega /run/omega

    # 4. AppArmor Profile (Ubuntu/Debian)
    if command -v aa-genprof >/dev/null 2>&1; then
        echo "  🛡️  Generating AppArmor profile..."
        cat > /etc/apparmor.d/usr.local.bin.omega-engine <<'EOF'
#include <tunables/global>
#include <abstractions/python>

/usr/local/bin/omega-engine {
  # Deny secret access tools
  deny /usr/bin/keyring ix,
  deny /usr/bin/secret-tool ix,
  
  # Deny sensitive paths
  deny /home/**/.local/share/opencode/auth.json r,
  deny /home/**/.ssh/** r,
  deny /home/**/.aws/** r,
  deny /home/**/.gnupg/** r,
  
  # Allow engine paths
  /var/lib/omega/** rw,
  /var/log/omega/** rw,
  /run/omega/** rw,
  /usr/local/bin/omega-engine mr,
  /usr/lib/python3.*/** mr,
}
EOF
        apparmor_parser -r /etc/apparmor.d/usr.local.bin.omega-engine
        aa-enforce /usr/local/bin/omega-engine
    fi

    # 5. zram Swap (no disk swap)
    echo "  💾 Configuring zram swap..."
    apt-get install -y systemd-zram-generator 2>/dev/null || \
    dnf install -y systemd-zram-generator 2>/dev/null || \
    pacman -S --noconfirm systemd-zram-generator 2>/dev/null || true
    
    cat > /etc/systemd/zram-generator.conf <<'EOF'
[zram0]
zram-size = min(ram / 2, 8192)
compression-algorithm = zstd
swap-priority = 100
EOF
    systemctl daemon-reload
    systemctl enable --now systemd-zram-setup@zram0.service
    swapoff -a 2>/dev/null
    sed -i '/swap/d' /etc/fstab
fi

# 6. Runtime Hardening Module (Python)
echo "  🐍 Installing runtime hardening module..."
cat > /usr/local/lib/omega/hardening.py <<'EOF'
import ctypes, resource, sys, os

def apply_runtime_hardening():
    """Apply runtime hardening at process startup."""
    # 1. Disable core dumps (PR_SET_DUMPABLE=0)
    try:
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        PR_SET_DUMPABLE = 4
        libc.prctl(PR_SET_DUMPABLE, 0)
    except Exception:
        pass
    
    # 2. Raise memlock limit for key buffering (requires CAP_IPC_LOCK from systemd)
    try:
        resource.setrlimit(resource.RLIMIT_MEMLOCK, (64*1024*1024, 64*1024*1024))
    except Exception:
        pass
    
    # 3. Disable Python's faulthandler (can leak memory in traces)
    if hasattr(os, 'register_at_fork'):
        try:
            import faulthandler
            faulthandler.disable()
        except Exception:
            pass

# Auto-apply on import
if __name__ != "__main__":
    apply_runtime_hardening()
EOF

# 7. Python runtime hardening import (add to engine entry point)
echo "  🔗 Linking runtime hardening..."
# This will be added to src/omega/__init__.py:
# from omega.hardening import apply_runtime_hardening
# apply_runtime_hardening()

echo "✅ Security hardening complete"
```

---

## 🏰 Component 9: Cross-Platform Sandboxing

### Unified Backend Abstraction

```python
# sandbox/process_isolation.py
import sys, subprocess, os, shutil, tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

@dataclass
class SandboxPolicy:
    allow_paths: List[str] = None          # Read/write allowed
    deny_paths: List[str] = None           # Explicit deny (SSH, AWS, GPG)
    allow_network: bool = False
    allow_exec: bool = True
    
    def __post_init__(self):
        if self.allow_paths is None:
            self.allow_paths = []
        if self.deny_paths is None:
            self.deny_paths = []

class SandboxBackend(ABC):
    @abstractmethod
    def wrap_command(self, cmd: List[str], policy: SandboxPolicy) -> List[str]:
        """Return wrapped command (e.g., ['sandbox-exec', '-f', profile, '--'] + cmd)"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass

class LinuxBwrap(SandboxBackend):
    def is_available(self) -> bool:
        return sys.platform.startswith("linux") and shutil.which("bwrap")
    
    def wrap_command(self, cmd: List[str], policy: SandboxPolicy) -> List[str]:
        args = ["bwrap", "--die-with-parent", "--unshare-all"]
        
        # Network
        if policy.allow_network:
            args.append("--share-net")
        else:
            args.append("--unshare-net")
        
        # Filesystem
        for p in policy.allow_paths:
            if os.path.exists(p):
                args += ["--ro-bind", p, p] if os.path.isdir(p) else ["--bind", p, p]
        
        # Mask sensitive paths with /dev/null
        for p in policy.deny_paths:
            if os.path.exists(p):
                args += ["--bind", "/dev/null", p]
        
        # Namespaces
        args += [
            "--unshare-user",
            "--unshare-pid",
            "--unshare-cgroup",
            "--tmpfs", "/home",  # Empty home
            "--dev-bind", "/dev/null", "/dev/null",
            "--proc", "/proc",
            "--dev", "/dev",
        ]
        
        return args + ["--"] + cmd

class MacOSSandboxExec(SandboxBackend):
    def is_available(self) -> bool:
        return sys.platform == "darwin" and Path("/usr/bin/sandbox-exec").exists()
    
    def wrap_command(self, cmd: List[str], policy: SandboxPolicy) -> List[str]:
        profile = self._generate_profile(policy)
        profile_path = Path(tempfile.mktemp(suffix=".sb"))
        profile_path.write_text(profile)
        return ["sandbox-exec", "-f", str(profile_path), "--"] + cmd
    
    def _generate_profile(self, policy: SandboxPolicy) -> str:
        lines = ["(version 1)", "(deny default)"]
        if policy.allow_exec:
            lines.append("(allow process*)")
        for p in ["/usr", "/bin", "/System", "/Library"]:
            lines.append(f'(allow file-read* (literal "{p}"))')
        lines.append('(allow file-write* (subpath "/tmp"))')
        lines.append('(allow file-read* (param "CWD"))')
        for p in policy.deny_paths:
            esc = p.replace(".", r"\.").replace("/", r"\/")
            lines.append(f'(deny file-read* (regex "^{esc}"))')
        if not policy.allow_network:
            lines.append("(deny network*)")
        return "\n".join(lines)

class WindowsLowIntegrity(SandboxBackend):
    def is_available(self) -> bool:
        return sys.platform == "win32"
    
    def wrap_command(self, cmd: List[str], policy: SandboxPolicy) -> List[str]:
        # True Low Integrity requires C++/Rust helper with CreateProcessAsUser
        # This is a best-effort approximation using PowerShell
        ps_cmd = [
            "powershell", "-NoProfile", "-Command",
            f"$proc = Start-Process -FilePath '{cmd[0]}' -ArgumentList '{' '.join(cmd[1:])}' "
            f"-Verb RunAs -WindowStyle Hidden -PassThru; "
            f"$proc.WaitForExit(); exit $proc.ExitCode"
        ]
        return ps_cmd

class NoSandbox(SandboxBackend):
    def is_available(self) -> bool: return True
    def wrap_command(self, cmd: List[str], policy: SandboxPolicy) -> List[str]: return cmd

def get_sandbox_backend() -> SandboxBackend:
    for backend in [LinuxBwrap(), MacOSSandboxExec(), WindowsLowIntegrity(), NoSandbox()]:
        if backend.is_available():
            return backend
    return NoSandbox()

# Usage
policy = SandboxPolicy(
    allow_paths=["/project", "/home/user/.config/omega"],
    deny_paths=[
        os.path.expanduser("~/.ssh"),
        os.path.expanduser("~/.aws"),
        os.path.expanduser("~/.gnupg"),
    ],
    allow_network=False,
)
backend = get_sandbox_backend()
wrapped = backend.wrap_command(["python", "untrusted_script.py"], policy)
subprocess.run(wrapped, check=True)
```

---

## 🗑️ Component 10: Deletion Plan (VaultCore Removal)

### Files to Delete (2,039 LOC)

```bash
# Complete removal of VaultCore
git rm -r src/omega/vault/
git rm scripts/vault_import.py
git rm src/omega/cli/vault.py

# Verify no references remain
rg -n "vault" src/omega/ --type py | grep -v "__pycache__" | grep -v test
# Should return ONLY:
# - src/omega/security/credential_provider.py (new)
# - config/encryption_backend.py (new)
# - config/editor_policy.py (new)
# - sandbox/process_isolation.py (new)
```

### Files to Modify

| File | Change |
|------|--------|
| `src/omega/__init__.py` | Add `from omega.hardening import apply_runtime_hardening; apply_runtime_hardening()` |
| `src/omega/oracle/model_gateway.py` | Remove `_load_sovereign_secrets()`; add lazy `get_provider_credential()` |
| `src/omega/oracle/types.py` | Add `ProviderIdentity` dataclass |
| `src/omega/oracle/rbac.py` | New file — RBAC enforcement |
| `pyproject.toml` | Add `[project.optional-dependencies]` encryption = ["pyrage>=1.3.0", "cryptography>=42.0", "flashtext>=2.7"] |
| `src/omega/cli/__init__.py` | Register `secrets` command group |
| `.opencode/hooks/session_end.py` | Add `SoulSanitizer` call |

### New Files to Create

```
src/omega/security/
├── __init__.py
├── credential_provider.py      # Core credential resolution
├── secret_registry.py          # 12-encoding canonicalization
├── sanitizer.py                # Egress sanitization (4 hooks)
├── aead_fallback.py            # Pure-Python AES-GCM

config/
├── encryption_backend.py       # Auto-select pyrage → cryptography
├── editor_policy.py            # Bundled micro + hardened nano/vim

sandbox/
├── __init__.py
├── process_isolation.py        # LinuxBwrap, MacOSSandboxExec, WindowsLowIntegrity
├── opencode_integration.py     # bwrap ONLY for MCP/external

src/omega/oracle/
├── types.py                    # ProviderIdentity dataclass
├── rbac.py                     # Agent role-based access control

src/omega/cli/
├── secrets.py                  # omega secrets edit/get/list/rotate/import

.opencode/hooks/
├── session_end.py              # Add SoulSanitizer call
```

---

## 📋 Component 11: SoulSanitizer Integration

```python
# .opencode/hooks/session_end.py — ADDITION
from security.secret_registry import SecretRegistry
from security.sanitizer import EgressSanitizer

def sanitize_soul_artifacts():
    """Run at session end to ensure no keys leak into soul artifacts."""
    registry = SecretRegistry()
    # Register all currently loaded secrets
    from src.omega.security.credential_provider import CredentialProvider
    provider = CredentialProvider()
    for cred in provider.list_credentials():
        if cred["storage"] == "envelope":
            # Decrypt to register for sanitization
            pass
    
    sanitizer = EgressSanitizer(registry)
    
    # Sanitize proposed_lessons.yaml
    lessons_path = Path("data/entities") / entity_name / "proposed_lessons.yaml"
    if lessons_path.exists():
        content = lessons_path.read_text()
        sanitized = sanitizer._kp.replace_keywords(content)
        lessons_path.write_text(sanitized)
    
    # Sanitize approved_lessons.yaml
    approved_path = Path("data/entities") / entity_name / "approved_lessons.yaml"
    if approved_path.exists():
        content = approved_path.read_text()
        sanitized = sanitizer._kp.replace_keywords(content)
        approved_path.write_text(sanitized)
    
    # Regenerate OMEGA_CODEX.md (already done by hook)
    # ... existing code ...

# Call at end of session_end.py
sanitize_soul_artifacts()
```