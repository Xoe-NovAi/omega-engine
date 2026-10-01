<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# KEY_MGMT_DESIGN_delta — Ma'at Session Paging Report
**AP Token**: AP-MAAT-PAGING-v1.0
**From**: maat (opencode) — paged back from dormant key-management-design session
**To**: kali (ses_fdef2be4effe4pAaLXCTUx62GO)
**Date**: 2026-08-21
**Original scope**: Research + design simple secure key mgmt for 8x accounts/providers
**Hydration**: ACTIVE_SPRINT.json D-562, D-565, D-566, D-567, D-568 only

---

## §1 Forgotten Design Conclusions (relevant to CredentialProvider / V-1 MVP)

1. **`api_keys` list already exists in ModelGateway** — `_create_openrouter` /
   `_create_antigravity` factories (model_gateway.py ~343-397, D205) accept an
   `api_keys` list for 8-account Active-Passive sharding. CredentialProvider must
   feed THIS interface, not invent a parallel one.
2. **`env:VAR_NAME` indirection is the established lookup syntax** — providers.yaml
   uses `api_key: env:GOOGLE_API_KEY`. CredentialProvider should extend this same
   indirection (e.g., `keyring:omega-engine/openrouter_1`) rather than new syntax.
3. **Resolution order recommendation**: explicit env var → keyring
   (service="omega-engine", username=`{provider}_{N}`) → absent+log. keyring>=24.0.0
   is ALREADY a hard dep in pyproject.toml — zero new dependencies for Path B.
4. **keyring multi-account is native** — service+username tuple works on all
   backends (libsecret schema carries service/username/application attributes).
   `set_password("omega-engine", "openrouter_1", k)` needs no custom schema.
5. **CRITICAL CAVEAT — no enumeration**: OS keyrings have NO native listing API.
   Cannot discover "all keys for service X" without an index entry or fixed
   account range convention. CredentialProvider needs a manifest entry or the
   zero-padded NN range scan (try 01..08, stop at first miss).
6. **Headless Linux gap**: libsecret backend requires gnome-keyring daemon + D-Bus
   session; fails in containers/headless unless `dbus-run-session` wraps the process.
   This validates D-568's python-age as EncryptionBackend primary — keyring is a
   convenience tier, not the durability tier. Podman containers (roc_racoon) cannot
   reach host keyring without socket mounts — env-injection at container start
   (host resolves, passes via `--env`) remains the correct container pattern.
7. **Size limits**: OS keyrings cap per-secret (~16KB macOS, ~2.5KB Windows).
   Fine for API keys; GCP SA JSON blobs (CredentialType.GCP_SA) may exceed Windows.
   python-age file backend is correct home for blob-type credentials.

## §2 Multi-Account (8x) Patterns Worth Preserving for Fabric Pool

1. **Zero-padded numbering**: `{PROVIDER}_API_KEY_{NN}` (01-08) — .env.example
   already documents "01-08 auto-collected". Zero-padding preserves sort order in
   both env vars and keyring usernames. Keep this convention in CredentialProvider.
2. **Active-Passive, NOT round-robin** (D205 + D-563): sticky account routing;
   8 accounts = rate-limit resilience, not parallelism. Future fabric pool should
   mine zaxbycodexauth patterns only when pool sprint opens: rotation strategies
   (round-robin/least-used/weighted), force-mode pinning, limits probing,
   atomic account-store writes.
3. **OpenRouter BYOK separation**: app-facing keys rotate independently of provider
   keys. For fabric: keep account identity separate from credential storage —
   CredentialProvider stores secrets; rotation policy lives elsewhere.
4. **Community precedent for plaintext-at-rest**: OpenCode stores auth in
   ~/.local/share/opencode/auth.json (user-scoped JSON outside repo). Aider uses
   plain .env. The user's plain-text .md requirement is within community norms —
   the security boundary is git-exclusion (PUBLIC_ALLOWLIST.txt / .gitignore),
   not encryption-at-rest. SOPS+age exists for teams sharing via git; single-user
   local-first tools overwhelmingly do NOT encrypt at rest.

## §3 Flagged Important, Never Executed

1. **THE DECISION DOC NEVER LANDED** — original session completed local discovery
   + web research but was cut off before writing
   `data/coordination/KEY_MGMT_DESIGN_20260818.md`. This delta partially
   discharges it; the options table verdict: given D-568, implement a B/C hybrid —
   env vars first-class (plain text, human-editable), keyring runtime fallback,
   python-age only for blob credentials. Option D (1Password/Bitwarden CLI)
   rejected: external dep violates M16 for debut.
2. **scripts/vault_import.py is broken as-written** — imports module-level
   `encrypt` from omega.vault.crypto (only VaultCrypto class exists there) AND
   defines its own duplicate get_or_create_master_key. Would ImportError on run.
   Include in the VaultCore dead-code deletion sweep (D-568).
3. **omega vault CLI is doubly dead** (675 LOC) — imports via wrong path
   (`src.omega.vault.vault_core`, src-prefixed) and calls methods that do not
   exist on current VaultCore (store_credential, decrypt_credential,
   get_recovery_code, rotate_master_password). Confirms D-562 delete verdict;
   nothing to salvage.
4. **VaultCore LOC recount**: ~2,139 across 5 files (vault_core 885, models 432,
   crypto 208, blindvault_resolver 542, __init__ 71) + vault CLI 675 +
   vault_import.py 126 ≈ **2,940 LOC deletable** post-debut. blindvault_resolver
   `_get_secret_value` returns FAKE keys (`sk-or-v1-{name}-{timestamp}`) — it is
   a stub that never touched real secrets. Deletion is pure win.
5. **INST-1-fix4 synergy**: sibling sessions found the env-dump gap live; my
   research adds that _load_sovereign_secrets is ALSO the only thing currently
   feeding providers their env vars at all — when removing it, CredentialProvider
   must land in the same change or every cloud provider goes keyless.

## §4 File Complete Confirmation

Sections: header + §1 (7 conclusions) + §2 (4 patterns) + §3 (5 items) + §4.
No other files written. Lock `key-management-design` released below.

*⬡ OMEGA ⬡ MAAT ⬡ PAGING-DELTA ⬡ KEY-MGMT ⬡ 2026-08-21*
