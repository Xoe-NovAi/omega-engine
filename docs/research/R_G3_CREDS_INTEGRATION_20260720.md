# 🔬 G3: systemd-creds TPM2 + Rootless Integration — Domain Research Report

**AP Token**: `AP-G3-CREDS-INTEGRATION-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ big-pickle ⬡ opencode ⬡ trc_g3_creds ⬡ ACTIVE

**Date**: 2026-07-20
**Campaign**: Research Campaign Manual v1.0.0 — Day 1-2 P0 Complete (G1/D308 only)
**Baseline**: Researcher's Deep Dive (R_SYSTEMD_CREDS_TPM2_ROOTLESS_20260720.md) — 482 lines, 10 questions answered

---

## 📋 Domain Overview

| Metric | Value |
|--------|-------|
| **Total Gaps** | 5 (G3.1–G3.5) |
| **P1 Target** | 1 (G3.1) |
| **P2 Target** | 4 (G3.2–G3.5) |
| **Architecture Decision** | **Hybrid mandatory** — systemd-creds for system services, custom provider for rootless (until Ubuntu 26.04) |
| **Hardware Reality** | AMD fTPM on Zen 2 = **UNSTABLE** (Linus: "plague") |

---

## 🎯 Gap Research Cards — Completed (from Baseline)

### Baseline Summary (Researcher's Deep Dive — COMPLETE)
| Question | Answer | Blocker for Omega? |
|----------|--------|-------------------|
| **1. TPM2 credential format** | Base64-encoded AES256-GCM ciphertext with embedded metadata (name, key type, PCR policy). Self-describing. | No |
| **2. Rootless quadlet + TPM2 on Ubuntu 25.04/25.10?** | **BROKEN** — systemd 257 fails with "Permission denied" at CREDENTIALS step | **YES** — D-299 Phase 1 |
| **3. AMD fTPM on Zen 2 (5700U)?** | **UNSTABLE** — Linus: "plague". Stutters, freezes, TPM command timeouts. | **YES** — Hardware risk |
| **4. Default PCRs** | PCR 11 (UKI). Configurable via `--tpm2-public-key-pcrs=`. Requires `systemd-measure` signed policy. | No |
| **5. Credential rotation** | Manual: re-encrypt with same key type, atomic swap, reload service. No native API. | Medium |
| **6. systemd 258+ migration** | Per-user creds via `systemd-creds --user encrypt`. Key derivation: UID+username+machine-id+TPM2. Target: Ubuntu 26.04 LTS (Apr 2026). | **YES** — Timeline |
| **7. Podman quadlet examples** | Exist in podman #26762, Reddit, GitHub. Pattern: `LoadCredentialEncrypted=name:/path/file.cred` in `[Service]`. `%d` specifier for cred dir. | No |
| **8. LUKS2 + TPM2 interaction** | Independent. LUKS2 uses TPM2 for disk unlock (clevis/tang). systemd-creds uses TPM2 for credential sealing. No conflict. | No |
| **9. systemd-creds as omega-vault backend** | **YES for system services (v257+). NO for rootless/user services until v258+.** Hybrid architecture mandatory. | **YES** — Architecture decision |
| **10. TPM2 encrypt/decrypt overhead** | ~1-5ms per operation (TPM2 command round-trip via `tpm2-abrmd` or kernel RM). Negligible for service startup. | No |

**Bottom Line**: 
- systemd 257 (Ubuntu 25.04/25.10) **cannot** do rootless TPM2 credentials
- AMD fTPM on 5700U is **unreliable** for production
- **Hybrid architecture mandatory**: systemd-creds (system) + age/rage (rootless) → migrate to systemd-creds --user on 258+

---

## 🎯 Gap Research Cards — Pending (Day 3-4)

### Gap G3.1 — TPM2 Health Monitoring Protocol
**Priority**: P1 | **Status**: ⏳ PENDING
**Research Queries**: `systemd-analyze has-tpm2 production monitoring 2026`, `TPM2 health check before credential sealing 2026`, `systemd-creds TPM2 failure detection journal`
**Success Criteria**: Pre-seal health check protocol
**Baseline**: `systemd-analyze has-tpm2 -v` shows `yes +firmware +driver +system +subsystem +libraries`; need runtime health probe before sealing

### Gap G3.2 — age/rage vs libsodium Benchmark
**Priority**: P2 | **Status**: ⏳ PENDING
**Research Queries**: `age encryption performance vs libsodium 2026`, `rage CLI benchmark 2026`, `age vs libsodium for credential store 2026`
**Success Criteria**: Encrypt/decrypt latency, binary size, auditability
**Baseline**: age/rage = modern, audited, public-key based; libsodium = lower-level, faster, requires key management

### Gap G3.3 — Credential Migration Tooling
**Priority**: P2 | **Status**: ⏳ PENDING
**Research Queries**: `systemd-creds --user migrate from age 2026`, `credential migration systemd 258 upgrade 2026`, `omega-vault credential migration strategy`
**Success Criteria**: Migration script + test plan
**Baseline**: systemd 258 adds per-user cred store at `/run/user/$UID/credstore.encrypted/`; key derivation = UID+username+machine-id+TPM2

### Gap G3.4 — Provider Registry API Contracts
**Priority**: P2 | **Status**: ⏳ PENDING
**Research Queries**: `Google AI Studio API key rotation API 2026`, `Anthropic API key rotation console API 2026`, `OpenRouter API key rotation API 2026`, `Antigravity quota API 2026`
**Success Criteria**: API specs for automated rotation
**Baseline**: omega-vault Phase 3 requires provider registry with rotation APIs

### Gap G3.5 — ForensicReceipt (Signet) Integration
**Priority**: P2 | **Status**: ⏳ PENDING
**Research Queries**: `Signed credential rotation audit trail 2026`, `systemd-creds rotation receipt signing 2026`, `M23 Failure Integrity credential audit 2026`
**Success Criteria**: Signed receipt format + verification
**Baseline**: M23 mandates no soft-failures; audit trail must be tamper-evident

---

## 🏗️ Architecture Decision (Validated)

### Hybrid Credential Architecture (from Baseline §7.2)
```
omega-vault (Custom Provider)
├── System Credential Backend → systemd-creds (TPM2 + host key)
│   ├── Encrypt: systemd-creds encrypt --with-key=auto
│   ├── Store: /etc/credstore.encrypted/
│   └── Load: LoadCredentialEncrypted= in quadlet [Service]
│
├── User Credential Backend (257) → Custom encrypted store
│   ├── Encrypt: age/rage (public key) or libsodium
│   ├── Store: ~/.local/share/omega-vault/credentials/
│   ├── Load: Custom exec wrapper injects via env/file
│   └── Migration: Auto-migrate to systemd-creds --user on 258+
│
├── Portable Credential Backend → SOPS/age + git
│   ├── Encrypt: age -r <pubkey> (multiple recipients)
│   ├── Store: Git repo (encrypted) or S3-compatible
│   └── Sync: omega-vault sync across machines
│
└── Provider Registry
    ├── Google AI Studio → API key rotation via OAuth
    ├── Anthropic → API key rotation via console API
    ├── OpenRouter → API key rotation via API
    ├── Antigravity → Quota monitoring + account rotation
    └── Local models → No credentials needed
```

### Implementation Priority (from Baseline §7.3)
| Phase | Deliverable | Depends On |
|-------|-------------|------------|
| **1** | VaultCore: OS keyring + SQLite event log + `vault` CLI | None |
| **2** | CAP Adapters: OpenCode, Omega Engine, generic `.env` | Phase 1 |
| **3** | Policy Engine + Rotation Orchestrator | Phase 2 |
| **4** | systemd-creds Backend (system services) | Phase 2 + Ubuntu 26.04 |
| **5** | Passive watcher (inotify/fanotify) + MCP server | Phase 3 |
| **6** | Context bundle backup/restore + Chaos testing CLI | Phase 4 |

---

## 📚 Source Index (from Baseline)

| # | Source | Type | Access Date | Key Content |
|---|--------|------|-------------|-------------|
| 1 | `man systemd-creds` (freedesktop.org) | Official manpage | 2026-07-20 | Format, --with-key, PCR policy, JSON output |
| 2 | `systemd.io/CREDENTIALS/` | Official docs | 2026-07-20 | Architecture, encryption, generators, runtime paths |
| 3 | `github.com/systemd/systemd/blob/main/docs/CREDENTIALS.md` | Source docs | 2026-07-20 | AES256-GCM, key derivation, credential store dirs |
| 4 | `github.com/systemd/systemd/releases/tag/v258` | Release notes | 2026-07-20 | Per-user creds, PrivateDevices fix, userdbctl |
| 5 | `github.com/systemd/systemd/pull/30968` | PR (merged) | 2026-07-20 | Per-user creds design, UID+username+machine-id key |
| 6 | `github.com/systemd/systemd/issues/27192` | Issue (closed) | 2026-07-20 | Rootless creds history, podman Type=notify problem |
| 7 | `github.com/systemd/systemd/issues/30191` | Issue (closed) | 2026-07-20 | Per-user creds feature request |
| 8 | `github.com/containers/podman/discussions/26762` | Discussion | 2026-07-20 | systemd-creds driver for podman secrets |
| 9 | `github.com/containers/podman/issues/36895` | Issue | 2026-07-20 | User service SetCredentialEncrypted permission denied |
| 10 | `github.com/systemd/systemd/pull/41193` | PR (merged) | 2026-07-20 | TPM2 SRK pinning, owner password support |
| 11 | `github.com/systemd/systemd/pull/41016` | PR (merged) | 2026-07-20 | Software TPM fallback (swtpm) |
| 12 | `manpages.ubuntu.com/questing/man1/systemd-creds.1.html` | Ubuntu 25.10 manpage | 2026-07-20 | Ubuntu-specific version |
| 13 | `wiki.archlinux.org/title/Systemd-creds` | Community wiki | 2026-07-20 | Practical examples, has-tpm2 check |
| 14 | `linuxsecurity.com/news/.../torvalds-critiques-amd-ftpm` | News article | 2026-07-20 | Linus Torvalds "plague" quote |
| 15 | `reddit.com/r/podman/comments/1mhjo8p/` | Community | 2026-07-20 | Rootless quadlet + TPM2 question |

---

## 🏁 Domain Status

**Baseline Complete**: ✅ All 10 priority questions answered with primary sources
**Architecture Decided**: ✅ Hybrid (systemd-creds system + custom rootless)
**P1 Ready**: G3.1 (TPM2 health monitoring)
**P2 Queued**: G3.2–G3.5 (benchmarks, migration, provider APIs, audit receipts)

**Critical Path**: 
- Ubuntu 26.04 LTS (Apr 2026) = natural migration point for rootless TPM2
- AMD fTPM instability = don't rely on it; use host key fallback
- omega-vault Phase 1 (VaultCore) unblocks all downstream phases

**Next Session**: Execute G3.1 (TPM2 health) + G3.4 (provider APIs) — highest impact for omega-vault design

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ big-pickle ⬡ opencode ⬡ trc_g3_creds ⬡ BASELINE COMPLETE — INTEGRATION PHASE PENDING*