<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->
# 🔱 Knowledge Gap 6: Legal & Licensing Compliance for Forks
**AP Token**: `AP-KG6-LEGAL-LICENSING-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ RESEARCH ⬡ 2026-07-25

## Executive Summary

Incorrect licensing can lead to legal issues, takedowns, or inability to distribute contributions. Every open source component carries obligations that vary by license type. Forking a project does not remove the original license — it inherits all its terms and adds attribution requirements.

**Key Finding**: Your first commit on any fork should be a license audit. Individual files can carry different SPDX identifiers than the root LICENSE file.

---

## §1 License Types and Obligations

### Three-Tier Classification

| Tier | Type | Licenses | Key Obligation | Commercial Safe? |
|------|------|----------|----------------|------------------|
| **A** | Permissive | MIT, BSD-2/3, Apache 2.0 | Attribution + notice retention | ✅ Yes |
| **B** | Weak Copyleft | LGPL, MPL-2.0 | Source for library on request | ✅ With disclosure |
| **C** | Strong Copyleft | GPL v2/v3, AGPL v3 | Full source for derivative works | ⚠️ May force open source |

### Key License Features

| Feature | MIT | Apache 2.0 | GPL v3 | AGPL v3 |
|---------|-----|------------|--------|---------|
| Attribution required | ✅ | ✅ | ✅ | ✅ |
| Patent grant | ❌ | ✅ | ✅ | ✅ |
| Patent retaliation | ❌ | ✅ | ✅ | ✅ |
| State changes documentation | ❌ | ✅ (§4) | ✅ | ✅ |
| Copyleft (share-alike) | ❌ | ❌ | ✅ | ✅ |
| Network copyleft (SaaS) | ❌ | ❌ | ❌ | ✅ |
| Anti-tivoization | ❌ | ❌ | ✅ | ✅ |

---

## §2 Fork License Requirements

### General Rule

A fork inherits the original project's license. You cannot change the license of existing code without permission from all copyright holders.

| Action | Allowed? | Condition |
|--------|----------|-----------|
| Fork MIT/Apache project, keep code private | ✅ Yes | Must preserve attribution notices |
| Fork MIT/Apache project, relicense to GPL | ⚠️ Debatable | MIT allows sublicensing; legal consensus varies |
| Fork GPL project, keep code private | ❌ No | GPL requires derivative works to be GPL |
| Fork GPL project, incorporate MIT code | ✅ Yes | MIT is GPL-compatible |
| Fork Apache 2.0, incorporate GPLv2 code | ❌ No | FSF: Apache 2.0 and GPLv2 are incompatible |
| Fork Apache 2.0, incorporate GPLv3 code | ✅ Yes | GPLv3 was designed to be Apache 2.0 compatible |

### Fork Distribution Requirements

| License | Must Include | May Omit |
|---------|--------------|----------|
| MIT/BSD | Original LICENSE, copyright notice | Your changes (can be private) |
| Apache 2.0 | LICENSE, NOTICE file, change records | Your proprietary additions |
| GPL v3 | Full source code under GPL v3 | — |
| AGPL v3 | Full source + network use notice | — |

---

## §3 SPDX Identifier System

### Standard Identifiers

| Identifier | License |
|------------|---------|
| `MIT` | MIT License |
| `Apache-2.0` | Apache License 2.0 |
| `BSD-3-Clause` | BSD 3-Clause "New" License |
| `GPL-3.0-only` | GNU GPL v3 only |
| `GPL-3.0-or-later` | GNU GPL v3 or later |
| `AGPL-3.0-only` | GNU AGPL v3 only |
| `LGPL-3.0-only` | GNU LGPL v3 only |

### SPDX Requirements for Forks

<!-- REUSE-IgnoreStart -->
Every file in a fork must carry:
1. `SPDX-License-Identifier:` matching the source file
2. Copyright notice (original author or "Copyright (c) [year] [holder]")
3. Any `NOTICE` file from upstream must be preserved unmodified
<!-- REUSE-IgnoreEnd -->

**Warning**: A repository can have MIT at root while individual files carry Apache-2.0 or proprietary SPDX headers. The SPDX header on the file you're modifying is the one that governs.

---

## §4 CLA vs DCO

### Contributor License Agreement (CLA)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Grants the project legal rights to distribute your contribution |
| **Complexity** | Legal document, may require lawyer review |
| **Used by** | Apache Foundation, Kubernetes, Node.js, React |
| **Ownership** | Contribution remains yours; you grant a license to the project |
| **Management** | Requires infrastructure (CLA assistant, EasyCLA) |

### Developer Certificate of Origin (DCO)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Certifies you have the right to submit the contribution |
| **Complexity** | Simple: `Signed-off-by: Name <email>` in commit message |
| **Used by** | Linux Kernel, Git, Docker |
| **Mechanism** | `git commit -s` adds sign-off automatically |
| **Enforcement** | GitHub DCO app checks commits |

### Which to Choose?

| Factor | Choose CLA | Choose DCO |
|--------|------------|------------|
| Corporate contributions | ✅ (legal entity clarity) | ❌ (may need additional agreements) |
| Individual contributors | ⚠️ (friction) | ✅ (low friction) |
| Large foundations | ✅ (standard) | ❌ (uncommon) |
| Small projects | ❌ (overhead) | ✅ (simple) |

---

## §5 Legal Compliance Checklist for Fork Contributions

### Pre-Fork Audit
- [ ] Root LICENSE file identified and understood
- [ ] All SPDX headers scanned and match root license
- [ ] NOTICE file checked for additional attribution requirements
- [ ] Patent grant implications understood (esp. Apache 2.0 §3)
- [ ] Copyright notices documented for attribution

### During Development
- [ ] Original LICENSE file preserved (never delete or modify)
- [ ] NOTICE file preserved (if present in upstream)
- [ ] Changes documented (state changes per Apache 2.0 §4 if applicable)
- [ ] Third-party dependency licenses tracked in dependency tree
- [ ] No GPL/AGPL code incorporated without legal review

### Before Distribution
- [ ] LICENSE file included in distribution
- [ ] NOTICE file included (if upstream had one)
- [ ] SPDX headers present in all source files
- [ ] Attribution requirements met (copyright notices preserved)
- [ ] Copyleft obligations satisfied (source code available if distributing GPL)
- [ ] SBOM generated with license data (SPDX or CycloneDX format)

### Ongoing
- [ ] Dependency license changes monitored on version bumps
- [ ] License compatibility verified for all new dependencies
- [ ] Export controls checked (cryptographic software — US origin)
- [ ] Trademark usage rules followed (project names, logos not reused)

---

## §6 Common Licensing Traps

| Trap | Risk | Mitigation |
|------|------|------------|
| **No LICENSE file** | "All rights reserved" — no permission to use | Find explicit license or choose alternative |
| **Mixed SPDX headers** | Different obligations per file | Scan all SPDX identifiers before modifying |
| **GPL in transitive dependency** | Unintended copyleft trigger | Automated SBOM scanning in CI |
| **License change on version bump** | Permissive→source-available (Redis, Terraform) | Watch for license changes on upgrades |
| **Apache 2.0 + GPLv2** | Incompatible (FSF guidance) | Upgrade GPLv2 to "GPLv2 or later" or split codebases |
| **AI model licenses** | Separate from code license | Audit model weights, training data, orchestration code separately |
| **Export controls** | Crypto software restrictions | Check BIS/EAR regulations for US-origin code |

---

## §7 Sources

1. Daeryun Law, "Open Source Compliance: How Do GPL, MIT, and Apache Licenses Work?" (2026-05-11) — https://www.daeryunlaw.com/us/practices/detail/open-source-compliance
2. Safeguard.sh, "Open Source License Compliance FAQ (2026)" (2026-07-05) — https://safeguard.sh/resources/blog/open-source-license-compliance-faq
3. Mehmet Gökçe, "Why Your First Commit on Any Fork Should Be a License Audit" (2026-04-15) — https://mehmetgoekce.substack.com/p/why-your-first-commit-on-any-fork
4. Safeguard.sh, "GPL vs MIT vs Apache License: Security and Compliance Risks" (2026-05-09) — https://safeguard.sh/resources/blog/gpl-vs-mit-vs-apache-license-security-and-compliance-implications
5. OSS Stack Exchange, "Are you allowed to create a GPL fork of an MIT/Apache licensed project?" — https://opensource.stackexchange.com/questions/12265/

---

## Decision Gate

✅ **License classification table** — 3 tiers (A/B/C) with obligations and commercial safety
✅ **Legal compliance checklist** — Pre-fork, during development, pre-distribution, ongoing
✅ **CLA vs DCO comparison** — When to choose each, with real-world examples
✅ **Common licensing traps** — 8 traps with mitigation strategies
✅ **SPDX identifier reference** — Standard identifiers for all common licenses

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: RESEARCH | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
