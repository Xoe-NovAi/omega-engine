<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Vault Overhaul: Full Review & Enhanced Plan
**AP Token**: `AP-VAULT-REVIEW-ENHANCED-20260818-v1.0.0`
**Status**: DEFINITIVE — Supersedes spec sections where noted
**Date**: 2026-08-18
**Author**: Kali (Oversight Review) — with Ma'at/Lilith/Researcher validation
**Scope**: Full adversarial review of `VAULT_SYSTEM_OVERHAUL_SPEC_20260818*` (5 parts) + gap research + enhanced architecture

---

## 📋 Part 1 — Review Verdict & Research Findings

### 1.1 Component Verdict Matrix

| # | Component | Spec Part | Verdict | Severity of Change |
|---|-----------|-----------|---------|---------------------|
| 1 | Encryption Backend (pyrage→cryptography) | 1 | ✅ **VALIDATED** (wheels confirmed) | None |
| 2 | CredentialProvider (keyring + envelope) | 2 | ⚠️ **CORRECTED** (headless fallback missing) | **HIGH** |
| 3 | YAML-Editor-Bridge (micro) | 2 | ⚠️ **CORRECTED** (version pin + checksum + tmpfs) | **MEDIUM** |
| 4 | SecretRegistry (12 encodings) | 3 | ⚠️ **CORRECTED** (format-pattern layer missing) | **MEDIUM** |
| 5 | Egress Sanitizer (flashtext) | 3 | 🔴 **REPLACED** (flashtext dead → flashtext2 chain) | **HIGH** |
| 6 | Zero-Knowledge ProviderIdentity | 3 | ✅ **VALIDATED** | None |
| 7 | RBAC Matrix | 3 | ⚠️ **CORRECTED** (advisory-only honesty + rotate perms) | **LOW** |
| 8 | Install Hardening (systemd/AppArmor) | 4 | 🔴 **CONFLICT FOUND** (ProtectHome vs keyring) | **CRITICAL** |
| 9 | Cross-Platform Sandboxing | 4 | ✅ **VALIDATED** (bwrap/sandbox-exec/Low-Integrity) | None |
| 10 | Deletion Plan (VaultCore) | 4 | ✅ **VALIDATED** | None |
| 11 | SoulSanitizer | 4 | ✅ **VALIDATED** | None |
| 12 | Integration Tests | 5 | ⚠️ **EXPANDED** (headless/KEK-loss/format tests) | **MEDIUM** |

### 1.2 Research Findings (All Verified 2026-08-18)

#### F-1: pyrage 1.3.0 Wheel Matrix CONFIRMED ✅
Source: PyPI `pyrage-1.3.0` (uploaded 2025-06-14, Trusted Publishing + Sigstore attestations)

| Platform | Wheel | Status |
|----------|-------|--------|
| Windows x64 | `cp39-abi3-win_amd64.whl` | ✅ EXISTS |
| Linux x86_64 glibc | `manylinux_2_17_x86_64.manylinux2014_x86_64` | ✅ EXISTS |
| Linux ARM64 glibc | `manylinux_2_17_aarch64` | ✅ EXISTS |
| macOS Intel | `macosx_10_12_x86_64` | ✅ EXISTS |
| macOS ARM64 | `macosx_11_0_arm64` | ✅ EXISTS |
| macOS Universal2 | `macosx_10_12_universal2` | ✅ EXISTS |
| **Alpine/musl** | — | ❌ **NO WHEEL** → cryptography fallback REQUIRED |
| **armv7 32-bit** | — | ❌ **NO WHEEL** → cryptography fallback REQUIRED |

**Spec impact**: Part 1 wheel matrix VALIDATED as-is. `pyrage>=1.3.0` pin correct.

#### F-2: pyrage CVE-2024-56327 (CRITICAL 9.8) — Plugin Execution 🔴
Source: CVE-2024-56327 / GHSA-4fg7-vxc8-qx5w / GHSA-47h8-jmp3-9f28

- age crate plugin support (age 0.11+) allows **arbitrary binary execution** via malicious plugin names in recipients/identities
- Fixed in pyrage **1.2.3**; our pin `>=1.3.0` is SAFE ✅
- **NEW CONSTRAINT**: Never pass attacker-controlled strings as recipients/identities to pyrage. Our design only passes the KEK passphrase (internal, 32-byte random hex) — safe. Document this in code comments.

#### F-3: keyring FAILS on Headless Linux — NoKeyringError 🔴
Source: jaraco/keyring docs + issue #609 + StackOverflow agent research

- Linux SecretService backend requires: D-Bus session (`DBUS_SESSION_BUS_ADDRESS`) + gnome-keyring/kwallet daemon
- Headless/CI/container: `keyring.errors.NoKeyringError: No recommended backend was available`
- `keyring.backends.fail.Keyring` is the default when nothing viable
- Windows wincred backend: ctypes-based, **no extra deps** ✅
- macOS Keychain backend: ctypes-based, **no extra deps** ✅
- Linux: requires `secretstorage` + D-Bus

**SPEC BUG**: Part 2 `CredentialProvider` calls `keyring.get_password()` unconditionally → **crashes on headless Linux** (the exact environment where `omega talk` must work per INST-1 acceptance!). MUST add deterministic fallback chain.

#### F-4: Windows Credential Manager Limit = 2560 Bytes (not 512) ✅
Source: wincred.h `CRED_MAX_CREDENTIAL_BLOB_SIZE = 5*512` (Win7+), verified Win10/Win11/WinServer2016/2019

- Our 500-char direct-storage threshold is **overly conservative** — raise to **2000 chars** (UTF-8 bytes < 2560)
- Envelope encryption still needed for >2000-char secrets (rare; e.g., multi-line JWTs)

#### F-5: flashtext is DEAD (2018) — Replace with flashtext2 🔴
Source: PyPI flashtext 2.7 (2018-02-16, Py2.7/3.5/3.6 classifiers only); flashtext2 1.1.0 (2024-07-04)

| Library | Status | Notes |
|---------|--------|-------|
| `flashtext` 2.7 | 🔴 **UNMAINTAINED 8 years** | Py2.7-era; ASCII token regex `[A-Za-z0-9_]+` |
| **`flashtext2`** 1.1.0 | ✅ **MAINTAINED (Rust)** | 3-10x faster, Unicode UAX#29 tokens, case folding, type-hinted, MIT, drop-in API |
| `pyahocorasick` 1.1.x | ✅ MAINTAINED (C) | Fast, memory-efficient, wheels incl. musllinux |
| regex alternation | ✅ Built-in | Zero-dep fallback (already in SecretRegistry) |

**Decision**: Sanitizer backend chain = **flashtext2 → pyahocorasick → regex alternation**. flashtext2 is the primary (drop-in API: `KeywordProcessor(case_sensitive=False)`, `add_keyword`, `replace_keywords`).

#### F-6: micro Editor — 2.0.15 + SHA256 Digests Available ✅
Source: micro-editor/micro releases (2.0.15, 2025-12-31); GitHub changelog 2025-06-03 (digests for release assets)

- **Pin `micro 2.0.15`** (spec said 2.0.11 — UPDATE)
- GitHub now auto-publishes SHA256 digests per asset + `.sha` files → **checksum verification in install.sh** (supply-chain fix)
- Repo moved to `micro-editor/micro` org (redirects still work)
- Assets: `micro-2.0.15-linux64.tar.gz`, `-linux-arm64`, `-linux-arm`, `-win64.zip`, `-macos.tar.gz` etc.

#### F-7: systemd ProtectHome=true BREAKS Keyring 🔴 CRITICAL CONFLICT
Source: systemd.exec(5) — "ProtectHome=... If set to true, the directories /home, /root, and /run/user are made inaccessible"

- Part 4 spec sets `ProtectHome=true` → **/run/user/1000 (D-Bus socket) becomes inaccessible** → SecretService keyring FAILS inside the hardened unit
- The residual-risk table's "dedicated omega user + ProtectHome isolates OpenCode auth.json" mitigation **contradicts keyring access**
- **Resolution** (Part 2 of this doc): 
  - Interactive engine (OpenCode host): runs in **user session** — no systemd unit, keyring works
  - MCP hub daemon: `ProtectHome=read-only` + `ReadWritePaths=/home/<user>/.omega` + `BindPaths=/run/user/<uid>` (or `PrivateTmp` only)
  - OpenCode auth.json mitigation: **bwrap sandbox for subagents + file perms 0600 + AppArmor deny-read** — NOT ProtectHome

#### F-8: AppArmor `deny /usr/bin/keyring` is COSMETIC ⚠️
- Python `keyring` talks to SecretService **over D-Bus directly** (via secretstorage) — it does NOT exec `/usr/bin/keyring` or `/usr/bin/secret-tool`
- The Part 4 AppArmor denies are theater → **replace with real enforcement**: deny D-Bus peer access to org.freedesktop.secrets for sandboxed subagents (bwrap `--unshare-net` doesn't block dbus; use `--ro-bind` empty over the bus socket or AppArmor dbus mediation)

#### F-9: Envelope Temp File is DECRYPTED ON DISK ⚠️
- Part 2 `edit_yaml_safely()` writes decrypted YAML to `~/.omega/tmp/` — plaintext residue risk (crash, swap, backup)
- **Resolution**: Linux → tmpfs `/dev/shm` (or memfd via `/proc/self/fd`); macOS → `TMPDIR` + note; Windows → controlled dir + 0600; always `unlink` + `os.O_TMPFILE` where available; document swap risk

#### F-10: ChunkedBodyReassembler is a STUB ⚠️
- Part 3 `_extract_chunked_body` contains `pass` — "use httpcore's parser in production" is not a plan
- **Decision**: For debut, **disable raw HTTP body logging entirely** (httpx event hooks log only method/URL/status). Drop the chunked reassembler from MVP; revisit if body logging is ever enabled.

---

### 1.3 Additional Gaps Found (Not in Original Spec)

| # | Gap | Severity | Resolution (Part 2) |
|---|-----|----------|---------------------|
| G-1 | KEK loss = total secret loss (no backup path) | **HIGH** | `omega secrets export/import` encrypted bundle + `rekey` |
| G-2 | No format-based detection (unregistered keys leak) | **HIGH** | Regex pattern layer (sk-or-v1-, AIza, sk-ant-, ghp_, xoxb-, …) |
| G-3 | No credential-access audit log (M22 provenance) | **MEDIUM** | `~/.omega/audit.log` (provider, account, ts, role — never values) |
| G-4 | `omega secrets get` prints plaintext to stdout (scrollback/history) | **MEDIUM** | `--clipboard` mode + warning + no-history |
| G-5 | No concurrency lock on envelope writes (two editors) | **MEDIUM** | `fcntl.flock` / `msvcrt.locking` on `.lock` files |
| G-6 | No typed errors (M9) — bare KeyError | **MEDIUM** | `CredentialNotFoundError(OmegaError)` |
| G-7 | RBAC is advisory (same OS user can read keyring directly) | **LOW** | Document honestly; OS enforcement = sandbox only |
| G-8 | No rotate semantics specified | **LOW** | `omega secrets rotate <provider> <account>` = set + verify + old-key invalidation checklist |
| G-9 | pyrage plugin-execution footgun undocumented | **LOW** | Code comment + doc note (F-2) |
| G-10 | `keyrings.alt` PlaintextKeyring tempting but insecure | **LOW** | Explicitly REJECTED in doc (never plaintext) |

---

*⬡ OMEGA ⬡ VAULT-REVIEW ⬡ PART 1/3 ⬡ 2026-08-18*