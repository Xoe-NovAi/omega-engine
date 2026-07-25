# 🔱 Legal & Licensing Compliance Guide
**AP Token**: `AP-LEGAL-LICENSING-GUIDE-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_legal_compliance ⬡ 2026-07-25

---

## Executive Summary

This guide provides a comprehensive legal and licensing framework for the Omega Engine team, synthesized from KG-6 research findings. Incorrect licensing can lead to legal issues, takedowns, or inability to distribute contributions.

**Purpose**: Ensure all contributions and distributions comply with legal requirements.

**Scope**: Applies to all code, documentation, and distributions across the Omega Engine ecosystem.

---

## 🎯 Core Principle: License Audit First

**Rule**: Your first commit on any fork should be a license audit.

**Why**: Individual files can carry different SPDX identifiers than the root LICENSE file. Forking does not remove the original license — it inherits all its terms.

---

## 📋 Three-Tier License Classification

### Tier A: Permissive

| License | Key Obligation | Commercial Safe? |
|---------|----------------|------------------|
| **MIT** | Attribution + notice retention | ✅ Yes |
| **BSD-2/3** | Attribution + notice retention | ✅ Yes |
| **Apache 2.0** | Attribution + notice retention + state changes | ✅ Yes |

### Tier B: Weak Copyleft

| License | Key Obligation | Commercial Safe? |
|---------|----------------|------------------|
| **LGPL** | Source for library on request | ✅ With disclosure |
| **MPL-2.0** | Source for modified files | ✅ With disclosure |

### Tier C: Strong Copyleft

| License | Key Obligation | Commercial Safe? |
|---------|----------------|------------------|
| **GPL v2/v3** | Full source for derivative works | ⚠️ May force open source |
| **AGPL v3** | Full source for derivative works (including SaaS) | ⚠️ May force open source |

---

## 🔧 Fork License Requirements

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

### Omega Engine License: Apache 2.0

The Omega Engine uses **Apache 2.0**, which is:
- ✅ **Permissive** — commercial use allowed
- ✅ **Patent grant** — protects against patent trolls
- ✅ **State changes** — requires documentation of modifications
- ✅ **GPL-compatible** — can be incorporated into GPL projects

---

## 📝 SPDX Identifiers

### What Are SPDX Identifiers?

SPDX (Software Package Data Exchange) identifiers are standardized labels for licenses. They enable:
- Automated license compliance checks
- Clear attribution in multi-license projects
- Machine-readable license information

### How to Add SPDX Headers

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Xoe-NovAi Foundation

"""Module docstring."""

def my_function():
    """Function docstring."""
    pass
```

### SPDX for Different File Types

| File Type | Header Format |
|-----------|---------------|
| **Python** | `# SPDX-License-Identifier: Apache-2.0` |
| **JavaScript/TypeScript** | `// SPDX-License-Identifier: Apache-2.0` |
| **Markdown** | `<!-- SPDX-License-Identifier: Apache-2.0 -->` |
| **YAML** | `# SPDX-License-Identifier: Apache-2.0` |
| **Shell** | `# SPDX-License-Identifier: Apache-2.0` |

---

## 🛡️ CLA vs DCO

### Contributor License Agreement (CLA)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Clarifies intellectual property rights |
| **Complexity** | Requires signing legal document |
| **Used by** | Microsoft, Google, Apache Foundation |
| **Mechanism** | CLA bot on GitHub |
| **Enforcement** | Must sign before PR merge |

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

**Omega Engine Decision**: Use **CLA** for foundation-backed project, with DCO as alternative for individual contributors.

---

## 🚨 EU Cyber Resilience Act (CRA)

### What Is EU CRA?

The EU Cyber Resilience Act (2026 enforcement) requires:
- Cybersecurity requirements for products with digital elements
- Vulnerability handling processes
- Security updates for 5-10 years
- CE marking for commercial products

### Impact on Open Source

| Scenario | Requirement |
|----------|-------------|
| **Commercial product using OSS** | Must comply with EU CRA |
| **Free OSS (no commercial use)** | Exempt |
| **OSS in commercial SaaS** | Must comply with EU CRA |
| **OSS in internal tools** | Exempt |

### Compliance Checklist

- [ ] **Vulnerability Handling** — Process for reporting and fixing vulnerabilities
- [ ] **Security Updates** — Commitment to provide security updates
- [ ] **Documentation** — Security documentation for users
- [ ] **CE Marking** — If commercial product, CE marking required

---

## 📋 Pre-Commit License Checklist

### For New Files

- [ ] **Add SPDX Header** — License identifier in file header
- [ ] **Add Copyright Notice** — Your name or organization
- [ ] **Verify Compatibility** — License compatible with project license
- [ ] **Document Changes** — State changes if required by license

### For Forks

- [ ] **Audit Root License** — Understand original project license
- [ ] **Scan All Files** — Check SPDX headers match root license
- [ ] **Check NOTICE File** — Additional attribution requirements
- [ ] **Verify Compatibility** — Your changes compatible with license
- [ ] **Document Fork** — Clearly state fork status and license

### For Contributions

- [ ] **Sign CLA/DCO** — As required by project
- [ ] **Add SPDX Headers** — For new files
- [ ] **Update LICENSE** — If adding new license
- [ ] **Document Changes** — State changes in PR description

---

## 🚨 Emergency Procedures

### License Violation Found

1. **Immediate**: Stop distribution of violating code
2. **Assess**: Determine scope and impact
3. **Fix**: Remove or replace violating code
4. **Notify**: Inform affected users
5. **Document**: Record violation and resolution

### Takedown Request

1. **Immediate**: Remove violating code
2. **Assess**: Determine if request is valid
3. **Respond**: Acknowledge request
4. **Fix**: Resolve violation
5. **Prevent**: Update processes to prevent recurrence

### Legal Action Threat

1. **Immediate**: Stop distribution
2. **Consult**: Legal counsel
3. **Assess**: Determine validity
4. **Respond**: Formal response
5. **Resolve**: Negotiate or litigate

---

## Decision Gate: Legal Compliance Compliance

✅ **ACHIEVED**: This guide provides comprehensive legal and licensing guidance, synthesized from KG-6 research findings.

**Next Steps**:
1. Apply this guide to Omega Engine fork
2. Add SPDX headers to all new files
3. Set up license compliance checks
4. Create CLA/DCO process

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_legal_compliance ⬡ COMPLETE*
