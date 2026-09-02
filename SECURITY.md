<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔐 Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.6.x (alpha) | ✅ |
| < 1.6 | ❌ |

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

Instead, report security issues via:

- **Email**: security@xoe-novai.com (PGP key available on request)
- **GitHub Security Advisories**: Use the "Report a vulnerability" tab in the Security section of this repository

We aim to:
- Acknowledge receipt within **48 hours**
- Provide a preliminary assessment within **7 days**
- Release a fix or mitigation within **30 days** for critical issues

## Scope

This policy covers the Omega Engine core (`src/omega/`), CLI (`omega`), and bundled MCP servers (`mcp_servers/`).

**Out of scope**:
- Third-party dependencies (report upstream)
- Configuration files on your machine
- Local model files (GGUF weights)
- User data directories (`~/omega/data/`)

## Disclosure Timeline

1. **Day 0**: Vulnerability reported
2. **Day 1-2**: Acknowledgment + triage
3. **Day 3-7**: Preliminary assessment + severity classification
4. **Day 7-30**: Fix development + testing
5. **Day 30**: Coordinated disclosure (advisory + patch release)

## Severity Classification

| Severity | CVSS Range | Response |
|----------|------------|----------|
| Critical | 9.0-10.0 | Emergency patch within 7 days |
| High | 7.0-8.9 | Patch within 14 days |
| Medium | 4.0-6.9 | Patch within 30 days |
| Low | 0.1-3.9 | Next scheduled release |

## Security Architecture

The Omega Engine is designed with security as a sovereign mandate:

- **M7 Local-First**: Cloud is opt-in fallback; local inference primary
- **M8 Zero Telemetry**: No external phone-home, no analytics
- **M22 Provenance**: Every response carries provider identity
- **M23 Failure Integrity**: No soft failures; broken tools → hard stop
- **PII Masking**: Cloud backends receive masked observations (M21)
- **Credential Isolation**: VaultCore removed (D-565); python-age for encryption

## Known Security Considerations

| Area | Status | Notes |
|------|--------|-------|
| Local model execution | ✅ | Runs in-process, no sandbox (CPU-only GGUF) |
| Cloud provider fallback | ⚠️ | Opt-in only; PII masking applied |
| MCP server exposure | ⚠️ | Localhost-only by default; no auth on local loopback |
| Model weight verification | ⚠️ | SHA256 checksums on download; no signature verification yet |
| Dependency scanning | ✅ | Gitleaks + dependency audit in CI |

## Contact

- **Security Team**: security@xoe-novai.com
- **PGP Key**: Available on request
- **Response SLA**: 48 hours acknowledgment

---

*⬡ OMEGA ⬡ SECURITY-POLICY-v1.0.0 ⬡ 2026-09-02*