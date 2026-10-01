<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Sovereign Mail Strategy Dossier (2026)
**Date**: 2026-07-10
**Status**: RESEARCH COMPLETE / READY FOR IMPLEMENTATION
**Context**: Authored by @researcher, synthesized by @jem.

## 1. The Architectural Insight (M7 Alignment)
Pure home-server email sending is effectively dead in 2026 due to ISP port 25 blocking and aggressive anti-spam algorithms by major providers (Microsoft, Google). 
**The Sovereign Solution**: Split the storage plane from the deliverability plane.
*   **Storage Plane (Local)**: Your hardware, your disk, your rules.
*   **Deliverability Plane (Relay)**: A cheap VPS or dedicated SMTP relay (e.g., Amazon SES, SendGrid, Hetzner) to handle outbound reputation.

## 2. Stack Recommendations
### Primary: Stalwart Mail Server
*   **Why**: Written in Rust. Memory footprint is incredibly low (~150MB), making it the *only* modern, secure suite that comfortably fits on a 14GB RAM machine already running local LLMs.
*   **Features**: JMAP, IMAP4, SMTP, DMARC/DKIM/SPF built-in, LDAP/SQL backends.

### Rejected: Mailcow / Mail-in-a-Box
*   **Why**: Mailcow requires 6-8GB of RAM (ClamAV, Solr, etc.). It violates the hardware constraints of the Omega Engine host (Ryzen 5700U / 14GB RAM).

## 3. Deployment Tiers
*   **Tier 0 (Absolute Sovereignty)**: Full self-host on a clean-IP VPS. High maintenance.
*   **Tier 1 (The Omega Recommendation)**: Local storage (Stalwart via Podman Quadlet) + Outbound SMTP Relay. Perfect balance of data ownership and deliverability.
*   **Tier 2 (Sovereign Co-op)**: Shared VPS among trusted peers.
*   **Tier 3 (Transitional)**: ProtonMail / Tuta (Zero-knowledge, but not self-hosted).

## 4. Implementation Blueprint (Phase 4)
1.  **DNS Configuration**: Setup MX, TXT (SPF), TXT (DMARC), and CNAME (DKIM) records on the domain registrar.
2.  **Quadlet Creation**: Deploy `sovereign-mail.container` using rootless Podman (`UserNS=keep-id`).
3.  **TLS Provisioning**: Use Caddy (already running on Omega Engine) to reverse-proxy and provision Let's Encrypt certificates for the mail subdomains.
4.  **Relay Configuration**: Bind Stalwart's outbound routing to the chosen SMTP relay.
5.  **Migration**: Use `imapsync` to pull historical archives from the legacy cloud provider into the local Stalwart instance.