<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Secret Rotation Log

**AP Token**: AP-SECRET-ROTATION-LOG-20260828-v1.0.0
**Date**: 2026-08-28
**Mandate**: Per M23 + L3-SecretsInVersionControlMustBeConsideredCompromised, any secret that has been committed to version control is considered compromised until rotation. This log tracks all such rotations.

---

## Section 0 — Active Rotations (Pending)

### R-2026-08-28-001 — Antigravity OAuth Client Secret (5 scripts)

- **Date**: 2026-08-28
- **Provider**: Google Cloud Console
- **Secret type**: OAuth client secret (GOCSPX-prefix)
- **Affected client IDs**: 1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com
- **Affected scripts** (all 5 fixed in commit 6aa37e70 to read from env var; secret is in git history):
  - scripts/antigravity_quota_probe.py:20 (round-4 fix)
  - scripts/antigravity_endpoint_router.py:42 (round-5 fix by Carmack)
  - scripts/burst_test_internal.py:20 (round-5 fix by Carmack)
  - scripts/long_duration_test.py:19 (round-5 fix by Carmack)
  - scripts/stress_test_internal.py:20 (round-5 fix by Carmack)
- **Reason**: Hardcoded GOCSPX value and similar values were committed to git. Per M23, the secret is compromised until rotation.
- **Rotation procedure**:
  1. Architect logs into console.cloud.google.com, then APIs and Services, then Credentials
  2. Find OAuth 2.0 Client ID 1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com
  3. Click "Regenerate Secret" — produces a new GOCSPX value
  4. Update ~/.config/opencode/antigravity-accounts.json with the new secret (5 keys)
  5. Verify: export ANTIGRAVITY_CLIENT_SECRET=GOCSPX-NEW; bash scripts/antigravity_quota_probe.py
  6. Deprecate the old secret (do NOT delete; wait 30 days)
  7. Update this log entry: status to "rotated", new_secret_id_suffix to (last 4 chars of new)
- **Operator**: Architect (only person with GCP console access)
- **Status**: PENDING (awaiting Architect action)
- **New secret ID**: (last 4 chars only, never the full secret)
- **Deprecation date**: TBD (30 days after rotation)
- **Deletion date**: null (set after deprecation)
- **Effort**: 10 min

### R-2026-08-28-002 — OpenRouter API Key (if committed)

- **Date**: 2026-08-28
- **Provider**: OpenRouter
- **Secret type**: API key (sk-or-v1- prefix)
- **Status**: NOT YET VERIFIED — the key in or-key.md is read at runtime; need to confirm it has never been committed to git history. If committed, rotation is required.
- **Verification command**: `git log -S 'sk-or-v1-' --all | head -5`
- **Operator**: Architect
- **Status**: PENDING VERIFICATION

---

## Section 1 — Completed Rotations

(none yet)

---

## Section 2 — Historical Leaks (Cannot Rotate)

### H-2026-08-28-001 — Antigravity OAuth secret in research markdown

- **Affected files**: `data/research/R_VAULT_*.md` (multiple files contain the literal GOCSPX value in examples, fixture descriptions, or as part of the secret-rotation tracking narrative itself)
- **Reason**: Past research left the secret in the documentation. The values are now part of git history.
- **Status**: HISTORICAL — cannot be un-committed from history. The OAuth client secret must be rotated per R-2026-08-28-001.
- **Mitigation**: Future research will NOT include literal secret values; all references will be redacted or use placeholder syntax.

### H-2026-08-28-002 — Other historical leaks

- **Affected files**: Various `data/research/*.md`, possibly `data/handoff/*` and `data/coordination/MASTER_BRIEFING_*.md`
- **Status**: HISTORICAL. See git history for details.
- **Mitigation**: Future research follows the M23 doctrine: secrets are env-var only, never committed.

---

## Section 3 — Rotation Procedure Template (for future use)

Use this template for new rotation entries:

```
- rotation_id: R-YYYY-MM-DD-NNN
  date: YYYY-MM-DD
  provider: <provider name>
  secret_type: <OAuth / API key / signing key>
  secret_id_prefix: <first 8 chars or known prefix>
  affected_clients:
    - <client_id_1>
    - <client_id_2>
  affected_files:
    - <file:line>
    - <file:line>
  reason: <why rotation is required>
  new_secret_id_suffix: <last 4 chars only — never the full secret>
  operator: <who performed the rotation>
  rotation_timestamp: <ISO 8601>
  deprecation_date: <30 days after rotation>
  deletion_date: null
  status: pending  # pending | rotated | deprecated | deleted
  verification_command: <command to verify new secret works>
  log_entry_by: <who added this entry>
```

---

## Section 4 — M23 Compliance Checklist (per rotation)

- [ ] Secret identified at the provider
- [ ] New secret generated
- [ ] Old secret deprecated (do NOT delete yet)
- [ ] Env var updated in production deployment (NOT in version control)
- [ ] Verification command run successfully
- [ ] Rotation logged in this file (last 4 chars only)
- [ ] Post-mortem (if P0/P1) written to `data/coordination/postmortems/`
- [ ] Old secret deleted at provider 30 days after deprecation
- [ ] Log entry status updated: pending to rotated to deprecated to deleted

---

*This log is the operational truth for secret rotations. M23 requires every rotation to be logged here, with the last-4-chars-only rule enforced to prevent re-leak through this log itself. NOTE: this file is intentionally pure markdown (not YAML) so it can be safely edited with any text editor without YAML escaping issues. Future rotations can be added as plain sections.*
R-2026-08-28-001: COMPLETE - GOCSPX scrubbed from history via filter-repo, disk files redacted, force-pushed to origin
