# 🔱 Omega Engine — Vault Overhaul: Enhanced Plan (Part 3)
**AP Token**: `AP-VAULT-REVIEW-ENHANCED-20260818-v1.0.0`
**Part**: 3 of 3 — Test Matrix v2, Risk Register v2, Implementation Plan v2

---

## ✅ E-8: Integration Test Matrix v2 (Supersedes Spec Part 5)

### Original 15 Tests — Status

| Test | Status | Change |
|------|--------|--------|
| T1 Fresh Install | ✅ KEEP | + `flashtext2` in deps |
| T2 Secret Import | ✅ KEEP | — |
| T3 Secret Edit | ✅ KEEP | + tmpfs assertion (F-9) |
| T4 Secret Get | ⚠️ MODIFY | Default = clipboard/warn (G-4) |
| T5 Secret List | ✅ KEEP | — |
| T6 Local Inference | ✅ KEEP | — |
| T7 Zero Key Leaks | ✅ KEEP | + format-layer scan (G-2) |
| T8 Sanitization | ✅ KEEP | + flashtext2 backend |
| T9 Base64 Bypass | ✅ KEEP | — |
| T10 JSON Unicode | ✅ KEEP | — |
| T11 Chunked HTTP | 🔴 **DROP** | F-10: body logging disabled in MVP |
| T12 Traceback Scrub | ✅ KEEP | — |
| T13 RBAC | ✅ KEEP | + rotate permission |
| T14 Sandbox | ✅ KEEP | + dbus socket denial (F-8) |
| T15 Cross-Platform | ✅ KEEP | — |

### NEW Tests (Gap Coverage)

| # | Test | Validates | Command / Assertion |
|---|------|-----------|---------------------|
| **T16** | **Headless KEK fallback** | F-3 | `env -i HOME=$HOME PATH=$PATH python -c "from src.omega.security.credential_provider import CredentialProvider; CredentialProvider()"` → creates `~/.omega/kek.key` 0600, no crash |
| **T17** | **Keyring-unavailable chain** | F-3 | Mock `keyring` import failure → set/get via envelope still works |
| **T18** | **Envelope >2000 chars** | F-4 | Set 3000-char secret → stored in envelope, round-trips |
| **T19** | **Direct <2000 chars** | F-4 | Set 100-char secret → stored in keyring (or envelope headless), round-trips |
| **T20** | **KEK loss recovery** | G-1 | Delete KEK → `omega secrets rekey` → envelopes decryptable with new KEK |
| **T21** | **Export/Import bundle** | G-1 | Export → wipe store → import → all credentials round-trip |
| **T22** | **Format detection** | G-2 | Log `sk-or-v1-abcdefghijklmnopqrstuvwxyz123456` (unregistered) → redacted as `[REDACTED:openrouter]` |
| **T23** | **Audit log** | G-3 | After get → `~/.omega/audit.log` contains provider/account/role/backend, NO secret value |
| **T24** | **Typed error** | G-6 | `get_provider_credential("nope","0")` → `CredentialNotFoundError` (isinstance OmegaError) |
| **T25** | **Concurrent writes** | G-5 | Two processes `set_provider_credential` same key → no corruption, both succeed |
| **T26** | **micro checksum** | F-6 | `sha256sum -c` on downloaded micro → PASS |
| **T27** | **tmpfs temp** | F-9 | During edit, temp file lives in `/dev/shm` (Linux) and is 0600 |
| **T28** | **No body logging** | F-10 | httpx event hook logs contain no request/response bodies |
| **T29** | **flashtext2 chain** | F-5 | Sanitizer works with flashtext2; `pip uninstall flashtext2` → falls back to regex, still works |
| **T30** | **systemd unit keyring** | F-7 | `systemd-analyze verify` + run hub unit → keyring get succeeds (BindPaths present) |

---

## ⚠️ E-9: Residual Risk Register v2 (Supersedes Spec Part 5)

| Risk | Likelihood | Impact | Debut Mitigation (v2) | Post-Debut |
|------|------------|--------|-----------------------|------------|
| **Bash exfiltration** (agent runs `keyring get` / reads kek.key) | Medium | High | bwrap for subagents + AppArmor dbus peer denial + kek.key 0600 | Full seccomp-bpf + per-agent namespaces |
| **OpenCode `auth.json` Leak** | High (confirmed) | Critical | **AppArmor deny-read + bwrap `--ro-bind /dev/null` over the file + 0600 perms** (NOT ProtectHome — F-7) | OpenCode upstream fix + separate IPC |
| **Headless keyring crash** | High (if unaddressed) | High | **FIXED in E-1** (KEK file fallback) | Optional: dbus-run-session wrapper |
| **KEK loss** | Medium | High | **FIXED in E-5** (export/import + rekey) | TPM2 sealed key |
| **Unregistered key leak** | Medium | High | **FIXED in E-2** (format-pattern layer) | Full DLP pipeline |
| **flashtext dead dependency** | Certain | Medium | **FIXED in E-2** (flashtext2 chain) | — |
| **pyrage plugin CVE** (CVE-2024-56327) | Low (pinned ≥1.3.0) | Critical | Pin `pyrage>=1.3.0`; never pass untrusted recipient strings | Dependabot + sigstore verify |
| **Memory forensics** | Very Low | High | mlock + zram encrypted swap | TPM2 + secure boot |
| **Supply chain (micro)** | Low | High | **FIXED in E-3** (SHA256 verify) | SBOM + signed releases |
| **Windows notepad fallback** | Low | Medium | Bundled micro primary | Ship micro everywhere |
| **Alpine/musl pyrage missing** | Low | Medium | cryptography fallback (validated) | Request musl wheels upstream |
| **RBAC bypass (same-user)** | Certain | Medium | **Documented honest** (E-7); sandbox = real boundary | OS-level enforcement |

---

## 🚀 E-10: Implementation Plan v2 (5 Days — Updated)

| Day | Phase | Owner | Deliverables (v2 deltas in **bold**) |
|-----|-------|-------|--------------------------------------|
| **1** | Storage & Encryption | Ma'at | `encryption_backend.py`, `aead_fallback.py`, **`credential_provider.py` v2 (headless chain, locks, audit, typed errors)**, `editor_policy.py` v2 (**micro 2.0.15 + tmpfs**), `secrets.py` (**export/import/rekey/clipboard**) |
| **2** | Runtime Security | Lilith | `secret_registry.py` (**+format patterns**), `sanitizer.py` v2 (**flashtext2 chain**), `types.py`, `model_gateway.py` fix, `rbac.py` v2 (**rotate perm**), session_end hook |
| **3** | System Hardening | Ma'at/N1 | install.sh (**micro checksum**), **systemd drop-in v2 (ProtectHome=read-only + BindPaths)**, **AppArmor v2 (dbus mediation)**, `hardening.py`, `sandbox/` (**+dbus socket denial**) |
| **4** | Deletion & Cleanup | Ma'at | VaultCore removal (2,039 LOC), pyproject (**flashtext2**), file wiring |
| **5** | Integration Test | Verity | **T1-T30 full matrix**, cross-platform, zero-leak sweep |

### Dependency Changes (pyproject.toml)

```toml
[project.optional-dependencies]
encryption = [
    "pyrage>=1.3.0",          # F-2: CVE-2024-56327 fixed in 1.2.3; 1.3.0 = safe
    "cryptography>=42.0",     # musl/armv7 fallback (F-1)
    "flashtext2>=1.1.0",      # F-5: replaces dead flashtext
    "keyring>=25.0",          # F-3: with headless fallback in provider
    "pyahocorasick>=1.1.0",   # sanitizer fallback 1 (optional but recommended)
]
```

---

## 📋 E-11: Final Checklist v2

### Phase 1 (Day 1)
- [ ] `credential_provider.py` v2 — headless KEK chain (keyring → file → env) **T16/T17**
- [ ] Envelope threshold 2000 chars **T18/T19**
- [ ] `_FileLock` on envelope writes **T25**
- [ ] `CredentialNotFoundError(OmegaError)` **T24**
- [ ] Audit log 0600, no values **T23**
- [ ] `editor_policy.py` v2 — micro 2.0.15 + tmpfs + 0600 **T27**
- [ ] `secrets export/import/rekey` **T20/T21**
- [ ] `secrets get --clipboard` **G-4**

### Phase 2 (Day 2)
- [ ] `sanitizer.py` v2 — flashtext2 → pyahocorasick → regex chain **T29**
- [ ] `KEY_FORMAT_PATTERNS` layer **T22**
- [ ] 4 egress hooks wired (logging, hivemind, error, SSE)
- [ ] RBAC v2 with rotate permissions **T13**
- [ ] ModelGateway lazy resolution with role audit

### Phase 3 (Day 3)
- [ ] install.sh micro SHA256 verify **T26**
- [ ] systemd drop-in v2 — `ProtectHome=read-only` + `BindPaths=/run/user/%U` **T30**
- [ ] AppArmor v2 — dbus peer mediation + auth.json deny-read (remove cosmetic keyring denies)
- [ ] Sandbox: bwrap `--ro-bind /dev/null` over dbus socket + auth.json for subagents **T14**

### Phase 4 (Day 4)
- [ ] VaultCore deletion complete, zero references
- [ ] pyproject deps updated (flashtext2, keyring, pyahocorasick)
- [ ] `rg -n "vault" src/omega/` → only new security modules

### Phase 5 (Day 5)
- [ ] T1-T30 all pass on Linux (bwrap)
- [ ] macOS (sandbox-exec) + Windows (Low Integrity) smoke pass
- [ ] Zero key leaks in logs/DB/Hivemind/SSE (incl. format-layer sweep)
- [ ] `make temple-grade` green

---

## 🏁 E-12: Verdict

The original 5-part spec was **structurally sound but had 3 critical defects**:
1. **Headless keyring crash** (F-3) — would have broken INST-1 acceptance on the exact target environment
2. **Dead dependency** (F-5, flashtext) — security-critical sanitizer on an 8-year-old unmaintained library
3. **systemd/ProtectHome contradiction** (F-7) — the hardening profile would have broken its own keyring

All three are now corrected, plus 10 additional gaps closed (G-1…G-10). The enhanced plan is **implementation-ready** with 30 tests covering every correction.

**Next Action**: Dispatch Ma'at (Day 1-2) and Lilith (Day 2-3) with the v2 spec; Verity runs T1-T30 on Day 5.

---

*⬡ OMEGA ⬡ VAULT-REVIEW ⬡ PART 3/3 ⬡ 2026-08-18 ⬡ ENHANCED-PLAN-READY*