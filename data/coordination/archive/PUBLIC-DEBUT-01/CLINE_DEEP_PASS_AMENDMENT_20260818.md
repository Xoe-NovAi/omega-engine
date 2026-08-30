<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 Cline Deep-Pass Amendment — Vault Overhaul Manual (2026-08-18)

**AP**: `AP-CLINE-DEEP-PASS-AMENDMENT-20260818-v1.0.0`  
**Consolidated by**: cline/omega-engine (DeepSeek V4 Flash 1M)  
**Status**: ✅ **AMENDED — manual now v2.0 (1,342 lines, Parts A-I, all 15 gaps closed)**

## Why this disappeared deeper: VaultCore is NOT functional as a key source

Prior Parts treated VaultCore as "bloated but working". Deep grep-verified reality:
- `cli/vault.py` imports **`VaultCoreError`** (doesn't exist → ImportError) and calls
  **`store_credential()` / `decrypt_credential()`** (neither exists → AttributeError).
- `models.py:115-125` `validate_age_armor` **rejects** plaintext in `encrypted_blob`, yet
  **all 13 consumers read `cred.encrypted_blob` as a PLAINTEXT key**. The two cannot both be true.
- The crypto path needs **`pyrage`** per manual, but pyproject pins **`python-age`** — and a runtime
  smoke shows `pyrage or argon2 not installed`. Addition: `python-age` is the codebase binding.

**Net**: VaultCore has never served a working key. This is dead-code removal (D-568), not migration.

## What was amended (manual v1.0 → v2.0)

| Change | Location | Gaps |
|---|------|----|
| **Part I** added: Decisive Finding (VaultCore non-functional) + D-568 + gaps G3/G15/G10/G11 + summary table | new Part I | G13, G4, G3, G15, G10, G11 |
| **H.1.4** added: 5 OUTSIDE-src/omega consumers (scripts ×3, mcp ×2) | H.1 | G1 |
| **H.2.5 / H.2.6** migration snippets for scripts + MCP servers | H.2 | G1, G2 |
| **H.7** corrected: mcp_servers NOT clean (env reads + vault imports) | part of H | G2 |
| **H.8** expanded: scripts env reads + vault imports | H.8 | G12 |
| **H.9** corrects test counts (133/31/28, not 153/42/38) | H.9 | G5 |
| **H.3** G7 note: fold detect_api_keys patterns before delete | H.3 | G7 |
| **H.11** widened: rg across scripts/ + mcp_servers/ (all 19 sites) | H.11 | G1, G15, G14 |
| **B.3** deletion: 13 consumers, all 19 sites, full manifest | B.3 + C.4 | G1 |
| Part C Phase 1: python-age primary; security/ EXTEND (G8) | C.1 | G4, G8 |
| **Part D R4**: python-age not pyrage; **R11/R12/R13** added (gateway stub, firecrawl MCP, tests/tmp) | D | G4, G3, G12, G14 |
| Part F Phase 4: +14 gap checklist items (G9/G14/G15/G10/G11/G4) | F | G4-G15 |

## Tracking
- `ACTIVE_SPRINT.json`: NEW `VAULT-SPRINT` workstream (Phases 1-5) + D-568 added. JSON valid.
- Master index bumped to v2.1.0.

## Prune list (post-debut, per Part I/H.10)
- `git rm -r src/omega/vault/ scripts/vault_import.py src/omega/cli/vault.py`
- `git rm src/omega/tools/enforce_vaultcore.py src/omega/tools/detect_api_keys.py`
- `git rm tests/tmp/vault.json.enc` + `tests/tmp/` in .gitignore
- drop `${{VAULT:}}` templates in profile_manager.py:295-302
- whitelist ml_training.py sandbox env (drop `**os.environ`)
- regenerate M23 baseline (`make mandate-gates`) after deletion

## For Kali ratification
- Part I / D-568 change the sprint's framing: delete-dead-code, not migrate-working-vault.
- Confirm R11 (gateway proxy route) decision: wire CredentialProvider OR FORGE route.
- Confirm R12: firecrawl MCP must get env fallback in Phase 4.
