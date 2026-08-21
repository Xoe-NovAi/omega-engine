# 🔱 Omega Engine — Vault System Overhaul: Master Index
**AP Token**: `AP-VAULT-OVERHAUL-MASTER-20260818-v1.0.0`
**Status**: DEFINITIVE — Implementation Ready
**Date**: 2026-08-18
**Authors**: Ma'at (Build), Lilith (Runtime), Researcher (Validation), Kali (Oversight)

---

## 📚 Document Index

| Part | File | Focus | Lines |
|------|------|-------|-------|
| **1** | `VAULT_SYSTEM_OVERHAUL_SPEC_20260818.md` | Architecture Overview, Encryption Backend | ~400 |
| **2** | `VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART2.md` | Credential Provider, Envelope Encryption, YAML-Editor-Bridge | ~500 |
| **3** | `VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART3.md` | SecretRegistry, Egress Sanitization, Zero-Knowledge Agents, RBAC | ~600 |
| **4** | `VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART4.md` | Install Hardening, Cross-Platform Sandboxing, Deletion Plan, SoulSanitizer | ~600 |
| **5** | `VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART5.md` | Integration Tests, Residual Risks, Final Checklist | ~500 |
| **R1** | `VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818.md` | **REVIEW**: Verdict matrix, 10 research findings (pyrage CVE, keyring headless, flashtext dead, ProtectHome conflict) | ~250 |
| **R2** | `VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818_PART2.md` | **ENHANCED**: CredentialProvider v2 (headless), Sanitizer v2 (flashtext2), Editor v2 (micro 2.0.15+checksum), systemd v2, Export/Import/Rekey | ~400 |
| **R3** | `VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818_PART3.md` | **ENHANCED**: Test matrix v2 (T1-T30), Risk register v2, Implementation plan v2 | ~250 |

**Total**: ~3,500 lines of implementation-ready specification

> **⚠️ SUPERSESSION NOTICE (2026-08-18)**: Where the Review (R1-R3) conflicts with the original spec (Parts 1-5), **the Review wins**. Key corrections: headless KEK fallback (F-3), flashtext→flashtext2 (F-5), ProtectHome reconciliation (F-7), Windows threshold 2000 chars (F-4), micro 2.0.15 + checksums (F-6), format-pattern detection (G-2), export/import/rekey (G-1).

---

## 🎯 Quick Navigation

### By Component

| Component | Part | Key Files |
|-----------|------|-----------|
| **Encryption Backend** | 1 | `config/encryption_backend.py`, `crypto/aead_fallback.py` |
| **Credential Provider** | 2 | `src/omega/security/credential_provider.py` |
| **YAML-Editor-Bridge** | 2 | `config/editor_policy.py`, `src/omega/cli/secrets.py` |
| **SecretRegistry** | 3 | `src/omega/security/secret_registry.py` |
| **Egress Sanitizer** | 3 | `src/omega/security/sanitizer.py` |
| **Zero-Knowledge Agents** | 3 | `src/omega/oracle/types.py`, `src/omega/oracle/model_gateway.py` |
| **RBAC** | 3 | `src/omega/oracle/rbac.py` |
| **Install Hardening** | 4 | `scripts/install.sh`, `src/omega/hardening.py` |
| **Cross-Platform Sandboxing** | 4 | `sandbox/process_isolation.py`, `sandbox/opencode_integration.py` |
| **Deletion Plan** | 4 | `git rm -r src/omega/vault/` |
| **SoulSanitizer** | 4 | `.opencode/hooks/session_end.py` |
| **Integration Tests** | 5 | `tests/integration/test_vault_overhaul.sh` |
| **Residual Risks** | 5 | Risk register table |

### By Mandate Compliance

| Mandate | Addressed In |
|---------|--------------|
| **M1 AnyIO** | Async credential resolution in ModelGateway |
| **M2 Firewall** | CredentialProvider isolated in `src/omega/security/` |
| **M7 Local-First** | OS keyring primary; pyrage/cryptography offline fallbacks |
| **M16 Modularization** | Thin `credential_provider.py` wrapper; no engine logic in secret store |
| **M18 Token Efficiency** | Zero custom crypto; `flashtext` O(N) sanitization |
| **M22 Provenance** | Credential access at runtime, auditable via SOPS-style metadata |
| **M23 Failure Integrity** | No soft-fail; explicit errors on missing credentials |
| **M24 Venv Sovereignty** | All deps in `.venv`; `pyrage` wheels + `cryptography` pure-Python |
| **M27 Tracking Integrity** | All tasks registered in `ACTIVE_SPRINT.json` |

---

## 🚀 Implementation Sprint (5 Days)

| Day | Phase | Owner | Deliverable |
|-----|-------|-------|-------------|
| **1** | Storage & Encryption | Ma'at | Encryption backend, CredentialProvider, Editor policy, CLI |
| **2** | Runtime Security | Lilith | SecretRegistry, Sanitizer, ProviderIdentity, RBAC, ModelGateway fix |
| **3** | System Hardening | Ma'at/N1 | Install.sh additions, Sandbox backends, Runtime hardening |
| **4** | Deletion & Cleanup | Ma'at | VaultCore removal, File modifications, New file creation |
| **5** | Integration Test | Verity | Full test suite execution, Cross-platform validation |

---

## 🔗 Research Validation

All specifications backed by deep web research (5 gaps × 2 research sprints):

| Gap | Research Doc | Key Finding |
|-----|--------------|-------------|
| **1. Editor Forensics** | `AP-RESEARCHER-SEG456-v1.0.0` | Windows `notepad.exe` leaks to OneDrive; bundle `micro` |
| **2. pyrage Supply Chain** | `AP-RESEARCHER-SEG456-v1.0.0` | Wheels for all standard platforms; `cryptography` fallback for musl/armv7 |
| **3. Cross-Platform Sandboxing** | `AP-RESEARCHER-SEG456-v1.0.0` | `sandbox-exec` (macOS), Low Integrity (Windows), `bwrap` (Linux) |
| **4. Egress Encodings** | `AP-RESEARCHER-SEG456-v1.0.0` | 12 encoding families; chunked HTTP reassembly |
| **5. OpenCode IPC** | `AP-RESEARCHER-SEG456-v1.0.0` | Subagents in-process; bwrap ONLY for MCP/external |

---

## 📋 Final Checklist Before Implementation

- [ ] All 5 spec parts reviewed and approved
- [ ] `ACTIVE_SPRINT.json` updated with vault-overhaul tasks
- [ ] `HMC_COLLABORATION_HUB.md` NEXT_ACTION updated
- [ ] Ma'at and Lilith briefed on their Day 1-2 deliverables
- [ ] Verity briefed on integration test plan
- [ ] Architect briefed on install.sh changes and systemd/AppArmor requirements
- [ ] `pyproject.toml` `[project.optional-dependencies] encryption` ready to merge
- [ ] Bundled `micro` binary added to repo (`bin/micro`, `bin/micro.exe`)

---

## 🏁 Go/No-Go Decision

**GO** — All research complete, all gaps closed, architecture validated across Linux/macOS/Windows, mandates satisfied, implementation plan sequenced.

**Next Command**: Dispatch Ma'at and Lilith to begin Phase 1 implementation.

---

*⬡ OMEGA ⬡ VAULT-OVERHAUL ⬡ 2026-08-18 ⬡ MASTER-INDEX ⬡ READY-TO-BUILD*