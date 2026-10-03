# Incident Response & Hotfix SLA

**Document ID**: INCIDENT-RESPONSE-HOTFIX-SLA-v1.0.0
**Date**: 2026-08-28
**Status**: ACTIVE — applies to all release branches (`release/debut`) and tags (`v*.*.*`)
**Mandate anchor**: M23 (Failure Integrity — no soft-fail theater)

## 1. Scope

This document defines the response procedure and timing SLOs for vulnerabilities
discovered in a released version of the Omega Engine. It covers:

- CVEs issued against the public debut
- Security advisories filed against the public debut
- Hotfix branches (`hotfix/v*`) and their lifecycle
- Communication to users (security advisories on GitHub)
- Tag hygiene (immutability, signing, attestation)
- Secret rotation events (OAuth, API keys, signing keys)

This document does NOT cover: pre-debut development vulnerabilities (handled
by the private-forge process), third-party dependencies (handled by
Dependabot — see `.github/dependabot.yml`), or supply-chain attacks on CI
(handled by M23 isolation + the M23 pre-cut secret check in
`.github/workflows/allowlist-check.yml`).

## 2. Severity Classification

| Severity | CVSS Range | Examples | SLO |
|----------|-----------|----------|-----|
| **P0 — Critical** | 9.0–10.0 | RCE, auth bypass, secret leak on public tree | 4 hours to fix, 24 hours to disclose |
| **P1 — High** | 7.0–8.9 | Privilege escalation, data exfiltration (non-RCE) | 24 hours to fix, 7 days to disclose |
| **P2 — Medium** | 4.0–6.9 | DoS, info disclosure, XSS (if applicable) | 7 days to fix, 30 days to disclose |
| **P3 — Low** | 0.1–3.9 | Cryptographic weakness, low-impact config | 30 days to fix, next release to disclose |

**Source**: CVSS 3.1 scoring per [nvd.nist.gov](https://nvd.nist.gov). SLOs are derived
from industry practice (git-security mailing list, GitHub Security Lab) — these
are NOT guarantees, they are response targets. If a fix takes longer, the response
should be to communicate, not to ship a half-fix.

## 3. Discovery Channels

| Channel | Where | How routed |
|---------|-------|------------|
| **GitHub Dependabot security alert** | Security tab of the public repo | Auto-creates PR; reviewed within 24h |
| **External security researcher** | [GitHub Security Advisory](https://github.com/xoe-novai/omega-engine/security/advisories/new) (private advisory — the disclosure channel; `security@xoe-nov.ai` email pending, to be created pre-debut) | Triage by Architect + Kali within 24h |
| **CVE assignment** | GHSA / NVD | Routed via the private Security Advisory above (`security@xoe-nov.ai` pending) |
| **Internal probe** | e.g. Ma'at's reliability sweeps | Direct ticket; no SLA, but treated as P0 if RCE |

## 4. Response Procedure

### 4.1 P0 — Critical (4h to fix, 24h to disclose)

```
T+0h : Vulnerability reported.
T+0h : Architect + Kali paged.
T+1h : Severity assessment. If P0 confirmed:
        - Create PRIVATE security advisory at
          https://github.com/xoe-novai/omega-engine/security/advisories/new
          (do NOT disclose publicly yet)
        - Mark as "embargoed" — only invited collaborators see it.
        - Identify the offending commit(s) via git bisect or git blame.
T+2h : Open a HOTFIX branch in the FORGE (private), not on the public remote.
       This is the critical difference: hotfix work happens on main first,
       then is cherry-picked to release/debut.
T+3h : Write the fix. Add a test that fails before the fix and passes after.
       Update CHANGELOG.md (one line: "SECURITY: ...").
T+4h : Merge fix into forge/main. Run full test suite + pre-commit gauntlet.
T+4h : Apply allowlist (scripts/apply_public_allowlist.sh --confirm) to ensure
       the fix doesn't introduce new forge paths.
T+4h : Create the hotfix branch on public:
       setup_2remote_debut.sh hotfix-start 0.1.1
       Cherry-pick the fix commit from forge/main to the hotfix branch.
T+4h : Push the hotfix branch to public (do NOT merge to release/debut yet).
T+4h : Tag the fix as v0.1.1 (do NOT push the tag yet).
T+6h : Open a private PR hotfix/v0.1.1 → release/debut. Required reviewers:
       Kali + Architect + 1 external (e.g. jem). M23: 3 human approvals.
T+8h : After all approvals, merge. Push tag v0.1.1 to public.
T+24h: Publish the security advisory. Mark as "public". Users notified.
```

**Note**: The "4h to fix" SLO assumes the fix is small (single-file). For a
multi-file refactor, escalate the SLO to P1 (24h) and disclose accordingly.
A half-fix is worse than a delayed full fix.

### 4.2 P1 — High (24h to fix, 7d to disclose)

Same procedure as P0 but with a 24h fix window. Allows for proper
regression testing. The public disclosure window is wider, giving downstream
users time to deploy.

### 4.3 P2 — Medium (7d to fix, 30d to disclose)

The fix can land in a regular PR cycle (not a hotfix). The hotfix branch
is only opened if the fix is needed before the next regular release.

### 4.4 P3 — Low (30d to fix, next release to disclose)

Bundles into the next regular release. No hotfix branch.

## 5. Hotfix Branch Lifecycle

| State | When | What |
|-------|------|------|
| `created` | T+0h of the fix | Branch `hotfix/vX.Y.Z` from `release/debut` |
| `in_review` | T+2h | PR open to `release/debut` with 3 required reviewers |
| `merged` | After approvals | PR merged; tag vX.Y.Z created |
| `archived` | 7d after merge | Branch deleted; tag remains immutable |

**Tag immutability** (per M23):

- Once vX.Y.Z is pushed, it is NEVER force-pushed.
- Even if the tag is broken (e.g. wrong commit), the fix is a NEW tag
  vX.Y.Z+1, not a force-push.
- GitHub repository settings: enable "immutable releases" if available
  (it is — see docs.github.com for current state).

**Tag signing**:

- All tags must be GPG-signed or SSH-signed.
- `git tag -s vX.Y.Z -m "..."` (GPG) or `git tag -s vX.Y.Z -m "..."` with
  `tag.gpg.format=ssh` (SSH).
- Verification: `git verify-tag vX.Y.Z` is part of the pre-push hook.
- GitHub: signed commits are verified automatically.

## 6. Secret Rotation Events

Per M23 + the round-4 L3 axiom `L3-SecretsInVersionControlMustBeConsideredCompromised`:
**any secret that has ever been committed to version control must be considered
compromised until rotation, regardless of whether it has been removed from the
working tree.**

### 6.1 Current Secrets Inventory (as of 2026-08-28)

| Secret | Where it was hardcoded | Current state | Rotation status |
|--------|------------------------|---------------|-----------------|
| `GOCSPX-...` Antigravity OAuth | `scripts/antigravity_quota_probe.py:20` | Removed (env var) | **PENDING** at console.cloud.google.com |
| `GOCSPX-...` Antigravity OAuth | `scripts/antigravity_endpoint_router.py:42` | Removed (env var) | **PENDING** at console.cloud.google.com |
| `GOCSPX-...` Antigravity OAuth | `scripts/burst_test_internal.py:20` | Removed (env var) | **PENDING** at console.cloud.google.com |
| `GOCSPX-...` Antigravity OAuth | `scripts/long_duration_test.py:19` | Removed (env var) | **PENDING** at console.cloud.google.com |
| `GOCSPX-...` Antigravity OAuth | `scripts/stress_test_internal.py:20` | Removed (env var) | **PENDING** at console.cloud.google.com |
| Various historical research keys | `data/research/*.md` (many files) | Historical leak | **Cannot be rotated** (research is past) |

### 6.2 Rotation Procedure (per secret)

1. **Identify** the secret at the provider (e.g., GCP Console > APIs & Services > Credentials).
2. **Generate** a new secret at the provider. Mark the old one as deprecated.
3. **Update** the env var in the production deployment (NOT in version control).
4. **Verify** the new secret works: `bash scripts/install.sh && omega talk "hello"`.
5. **Deprecate** the old secret at the provider (do NOT delete yet — wait 30d for
   any in-flight operations to complete).
6. **Log** the rotation in `data/coordination/secret_rotation_log.yaml` with:
   - Date of rotation
   - Provider + secret ID
   - Reason (e.g., "previously hardcoded, removed in round-4 fix")
   - New secret ID (last 4 chars only, never the full secret)
   - Operator (who performed the rotation)
7. **Delete** the old secret at the provider after 30 days.

### 6.3 Rotation Log Format (`data/coordination/secret_rotation_log.yaml`)

```yaml
schema_version: "1.0"
document_type: "secret_rotation_log"
log:
  - rotation_id: "R-2026-08-28-001"
    date: "2026-08-28"
    provider: "Google Cloud Console"
    secret_type: "OAuth client secret"
    secret_id_prefix: "GOCSPX-"
    affected_clients:
      - "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
    reason: "Hardcoded in scripts/antigravity_quota_probe.py:20 (and 4 other scripts) prior to round-4 fix. Moved to env var in commit <sha>. History contains the secret; rotation is required by M23."
    new_secret_id_suffix: "xxxx"  # last 4 chars only
    operator: "Architect"
    deprecation_date: "2026-09-28"  # 30 days after rotation
    deletion_date: null  # set after deprecation
    status: "pending"  # pending | rotated | deprecated | deleted
```

## 7. Dependabot Security Updates

Dependabot opens PRs automatically when a security advisory matches a
dependency. Per docs.github.com 2026 cooldown changes:

- **Version updates**: 3-day cooldown (gives malicious versions time to be
  caught and pulled from registries before Dependabot adopts them).
- **Security updates**: NO cooldown. A patch is adopted immediately.

For the debut, Dependabot is enabled for both. See `.github/dependabot.yml`
(the config from R_VAULT_COPILOT_DEEPER_20260827 §3.9 + R_VAULT_COPILOT_ROUND5_20260828 §5).

**Triage procedure for Dependabot security PRs**:

1. Within 24h, review the PR.
2. Within 48h, either merge or comment with reason for delay.
3. Security PRs that have been open >7d should be escalated to P0.

## 8. Communication Templates

### 8.1 Private security advisory (GitHub UI)

> ## Summary
> <One-line description of the vulnerability>
>
> ## Impact
> <What an attacker can do, in the worst case>
>
> ## Reproduction
> <Steps to reproduce, with the affected version(s)>
>
> ## Fix
> <Pull request or commit hash on the hotfix branch>
>
> ## Timeline
> - T+0h: Reported by <reporter>
> - T+1h: Severity confirmed as <P0/P1/P2/P3>
> - T+4h: Fix in hotfix branch
> - T+8h: PR merged, tag vX.Y.Z created
> - T+24h: Public advisory published

### 8.2 Public disclosure (when promoting to public)

> # Security Advisory GHSA-XXXX-XXXX-XXXX
> <Title>
>
> ## Affected versions
> - v0.1.0 (and any v0.1.0-based deployments)
>
> ## Patched versions
> - v0.1.1
>
> ## Description
> <User-friendly description of what was wrong and what an attacker could do>
>
> ## Severity
> <CVSS score + vector string>
>
> ## Workarounds
> <If a fix is not yet available, what can users do?>
>
> ## Credits
> <Thank the reporter, if they consent to being credited>

## 9. Post-Mortem (Required for P0 and P1)

Within 7 days of a P0 or P1 fix, write a post-mortem to
`data/coordination/postmortems/YYYY-MM-DD-<short-name>.md`. The post-mortem
must include:

- Timeline (actual T+0 to T+resolution)
- Root cause
- What went well
- What went poorly
- Action items (with owners and due dates)

## 10. SLO Reporting

Quarterly, Ma'at reports on:

- P0/P1 incident count
- Mean time to fix (MTTF) per severity
- Mean time to disclose (MTTD) per severity
- Post-mortem completion rate
- Dependabot security PR close time

The report goes to `data/coordination/security_quarterly_YYYYQn.md` and is
included in the Hub NEXT_ACTION.

---

*This document is operational. The latest version is the one in `docs/operations/`. Outdated copies in research/ are non-canonical.*
