---
schema_version: "1.0"
document_type: reference
document_id: knowledge-gap-closure
title: Fleet Knowledge Gap Closure Report
status: ACTIVE
version: "1.1.0"
date: "2026-08-07"
owner: kali
tags: [knowledge-gaps, research, fleet, phase-d]
priority: P1
depends_on: []
blocks: []
acceptance_gates:
  - "5/5 critical gaps documented with actionable findings"
cross_references:
  - docs/sprints/current/KNOWLEDGE_GAP_CLOSURE_FULL.md
  - docs/archive/sprints/EXECUTION_PLAN_20260725.md
llm_metadata:
  token_budget: 3000
  chunk_strategy: section_per_topic
  answer_first_sections: true
  self_contained_code: false
---

# 🔱 Fleet Knowledge Gap Closure Report
**AP Token**: `AP-KNOWLEDGE-GAP-CLOSURE-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ RESEARCH ⬡ 2026-07-25

**Status**: ALL 5 Critical Gaps RESEARCHED — 5/5 domains with actionable findings
**Deadline Impact**: 1 domain now **URGENT** (MCP 2026-07-28 spec drops in 3 days)

---

> **⚠️ RESEARCH-VS-EXECUTION CORRECTION (2026-07-25):** This document correctly reports **research** closure for 5 critical domains. It does **not** assert execution closure.  
> Always cross-reference `docs/archive/sprints/EXECUTION_PLAN_20260725.md` §0 (probe-backed status) before acting on any claim.  
> See `R_CRITICAL_SPRINT_AGENT_SUPPORT_GAPS_20260725.md` §1 for residual execution gaps (SG-01..10).

## §1 Summary — What We Researched

| Domain | Gap ID | Source Docs | Status | Confidence |
|--------|--------|-------------|--------|------------|
| MCP 2026-07-28 Spec Migration | CG-01 | 8 web sources + MCP blog + SDK beta docs | ✅ **RESOLVED** | High |
| VaultCore Credential Vault | CG-04, GAP-08 | 7 web sources + SOPS/Age patterns | ✅ **RESOLVED** | High |
| Restic Backup Strategy | GAP-04, C-3 | 6 web sources + restic docs | ✅ **RESOLVED** | High |
| Ryzen 5700U Hardware Constraints | GAP-03, GAP-05, CG-02 | TechPowerUp + AMD docs | ✅ **RESOLVED** | High |
| MCP Python SDK Migration Path | CG-01 (extended) | MCP SDK beta blog + migration guides | ✅ **RESOLVED** | Medium-High |

**Research Method**: T1 websearch + T2 webfetch on all 5 domains, cross-referenced against existing research docs (KGC_DEEP_RESEARCH_REPORT.md, R_CRITICAL_GAPS_DEEP_DIVE_CAMPAIGN.md, R_KNOWLEDGE_GAPS_DEEP_RESEARCH_20260720.md, R_MAKALI_COUNCIL_KNOWLEDGE_GAPS_20260719.md, UNKNOWN_UNKNOWNS_AUDIT_20260721.md)

---

## §2 Finding 1: MCP 2026-07-28 — THE URGENT ONE

**Status**: 🚨 Spec ships **July 28, 2026 — 3 days from now**

### What the RC Changes

The 2026-07-28 release candidate is the **largest revision since MCP launched**. It has 5 pillars:

| Pillar | What Changes | Impact on Omega Hub |
|--------|-------------|---------------------|
| **1. Stateless Core** | No `initialize`/`initialized` handshake. No `Mcp-Session-Id` header. Protocol version + capabilities in `_meta` on every request. | **BREAKING** — C-4b dual transport uses `initialize` |
| **2. Operability Layer** | Required `Mcp-Method` and `Mcp-Name` HTTP headers. W3C Trace Context. Cache TTL metadata. | **REQUIRED** — add to middleware |
| **3. Extensions Framework** | Tasks and MCP Apps move out of core spec into extensions. Full JSON Schema 2020-12. | **LOW** — we don't use Tasks directly |
| **4. Auth Hardening** | 6 SEPs aligning with OAuth 2.1/OIDC. ISS validation per RFC 9207. | **MEDIUM** — verify if used |
| **5. Deprecation Policy** | Roots, Sampling, Logging deprecated. 12-month removal window. Formal sunset process. | **LOW** — we don't depend on these |

### What This Means for Our Execution Plan

| Action | Owner | Timeline | Priority |
|--------|-------|----------|----------|
| **Pin mcp version**: Set `mcp>=1.27,<2` in `pyproject.toml` to prevent accidental v2 upgrade | @maat/P3 | **TODAY** | 🔴 P0 |
| **Audit C-4b dual transport** for `Mcp-Method`/`Mcp-Name` header requirements | @maat/P4 | **Jul 27** | 🟡 P1 |
| **Verify backward compat**: v2 servers answer `initialize` handshake, so SSE still works | @maat/P4 | **Jul 27** | 🟡 P1 |
| **Add upper bound for mcp dependency**: `mcp>=1.27,<2` in install requires | @maat/P3 | **TODAY** | 🔴 P0 |
| **Don't migrate to v2 yet** — Dual transport + v1 pinning buys us 12 months+ | @kali | **Hold** | ✅ |

### Evidence
> *"If you publish a library that depends on the Python mcp package, add an upper bound now (for example `mcp>=1.27,<2`) so the stable v2 release does not surprise your users."*
> — MCP Blog, Beta SDK Announcement, July 1, 2026

> *"The 2026-07-28 release candidate makes MCP stateless — no more initialize handshake or Mcp-Session-Id pinning clients to one server... Requests now carry Mcp-Method and Mcp-Name headers."*
> — MCP Blog, RC Announcement, May 22, 2026

---

## §3 Finding 2: VaultCore — Age + Argon2id Pattern VALIDATED

**Status**: ✅ Our approach is correct and industry-standard.

### Industry Consensus (2026)
| Pattern | Status | Source |
|---------|--------|--------|
| **Age encryption** (X25519 + ChaCha20-Poly1305) | ✅ Gold standard for local-first | SOPS docs, symaira-vault, GitHub |
| **Argon2id KDF** | ✅ 2026 industry standard | CIAM Compass, NIST guidance |
| **File-level encryption** (encrypt values, not files) | ✅ SOPS pattern validated | SOPS + Age guide, multiple sources |
| **Envelope encryption** (data key + key encryption) | ✅ Best practice | HashiCorp, AWS KMS patterns |
| **Separate CI/CD keys from personal keys** | ✅ VaultCore design supports this | StrongDM, SOPS docs |
| **Never store plaintext in git** | ✅ `data/gitignore` prevents this | Universal consensus |

### Recommendations for VaultCore Week 2
1. **No change needed** — Age + Argon2id is correct
2. Consider SOPS-style `.sops.yaml` config for multi-key scenarios
3. Add `restic encrypted-backup` command that backs up vault key alongside data

---

## §4 Finding 3: Restic Backup — LOCAL FIRST IS VIABLE

**Status**: ✅ Local-only repo is valid first tier. B2 cloud deferred is acceptable.

### What the Research Says
| Aspect | Finding | Implication |
|--------|---------|-------------|
| **Local repo** | Fully supported by restic, uses same encryption + dedup as remote repos | Viable for Phase D gate |
| **Systemd timer** | `OnCalendar=*-*-* 02:00:00` + `RandomizedDelaySec=30m` + `Persistent=true` | Canonical pattern |
| **3-2-1 without B2** | Local backup is "copy 2 on same media" — not ideal but valid for interim | Accept trade-off |
| **Restore testing** | `restic restore --target /tmp/test-restore latest` + `restic check --read-data-subset 5%` | Weekly cron |  
| **B2 cost** | ~$1.20/month for 200GB after dedup | Cheap, add in Week 2 |

### Action Items
1. **Initialize local repo NOW**: `restic init -r /mnt/backup/omega-engine`
2. **Create systemd timer**: `scripts/restic-backup.service` + `restic-backup.timer`
3. **Add restore test script**: Weekly `restic restore --target /tmp/test-restore latest` + `restic check`
4. **Defer B2**: Add as VaultCore Week 2 item

---

## §5 Finding 4: Ryzen 5700U HARDWARE PROFILE CONFIRMED

**Status**: ✅ Our C-2'/C-10 admission control assumptions are validated.

### Hardware Reality Check
| Spec | Value | Inference Impact |
|------|-------|-----------------|
| **CPU** | Ryzen 7 5700U (Zen 2 Lucienne) | **NOT** Zen 3 Cezanne (5800U has 16MB L3) |
| **L3 Cache** | 8MB shared (split across 2 CCXs) | Cross-CCX ~20ns vs intra-CCX ~10ns |
| **Threads** | 8C/16T | |
| **TDP** | 15W (configurable to 25W) | Sustained load = throttling |
| **Memory** | DDR4-3200 dual-channel ~51.2 GB/s | Shared with iGPU |
| **iGPU** | Radeon Graphics 512SP (Vega) | No NPU, no ROCm support for llama.cpp |
| **RAM available for models** | ~8GB (OS + system takes ~4-6GB of 16GB) | 4B Q4 model (~3GB) fits; 8B Q4 (~5.5GB) risks OOM |

### What This Means
| Assumption | Validated? | Action |
|------------|-----------|--------|
| Max 1 concurrent local inference | ✅ Yes — C-10 is correct | No change |
| 4B Q4 model safe | ✅ ~3GB, fits with 2GB headroom | Keep as default |
| 8B Q4 marginal | ⚠️ ~5.5GB, leaves 0.5GB headroom | Use only with ResourceGuard |
| No hardware acceleration | ✅ Vega iGPU is not usable for llama.cpp | CPU-only inference by default |
| 2 concurrent would thrash | ✅ L3 cache + memory bandwidth are bottlenecks | Enforced by C-10 |

### One Surprise
The 5700U is **Zen 2 Lucienne**, not Zen 3 Cezanne. This means:
- 8MB L3 (5800U has 16MB!)
- No unified CCX (2 separate CCXs with 4 cores each)
- Cross-CCX penalty applies

Previous docs assumed "Zen 3-like performance." This is a correction — but it **validates our conservative admission control limits** even more strongly.

---

## §6 Finding 5: MCP Python SDK Migration Path

**Status**: ⚠️ Action needed in next 3 days.

### Current State
| Component | Current | Required for 2026-07-28 |
|-----------|---------|------------------------|
| `mcp` Python package | Unpinned (tracking latest) | Pin to `mcp>=1.27,<2` |
| `mcp_runtime.py` | Uses `SseServerTransport` + `StreamableHTTPSessionManager` | Must handle `Mcp-Method` and `Mcp-Name` headers |
| `mcp_client.py` | Uses `sse_client()` + `streamablehttp_client()` | Should handle `_meta` field per-request |

### Migration Decision
| Option | Pros | Cons | Recommendation |
|--------|------|------|---------------|
| **Pin to v1** (`mcp>=1.27,<2`) | Stable, no breakage, backward compat | Need to eventually migrate | ✅ **DO THIS NOW** |
| **Migrate to v2 beta** (`mcp==2.0.0b1`) | Future-proof, no rework later | Beta may have breaking changes, docs incomplete | ❌ **NOT YET** — wait for stable v2 |

**Timeline**: Pin immediately. Migrate to v2 stable when shipped (~Aug 2026).

---

## §7 Updated Execution Plan — Changes Based on Research

### 🔴 NEW URGENT ITEMS (Add to Track D)

| Item | Assignee | Action | Priority |
|------|----------|--------|----------|
| **Pin mcp dependency** | @maat/P3 | Add `mcp>=1.27,<2` to `pyproject.toml` | 🔴 P0 — TODAY |
| **Verify C-4b transport** | @maat/P4 | Check `Mcp-Method`/`Mcp-Name` header handling in `mcp_runtime.py` | 🟡 P1 — Jul 27 |

### 🔴 EXISTING BLOCKERS (Unchanged)

| Blocker | Owner | Fix |
|---------|-------|-----|
| **C-0.5 hook registration** | @kali | Edit `.opencode/opencode.json` + restart OpenCode |
| **PolicyKit rule** | @john_carmack | `sudo cp /tmp/99-omega-warp.rules /etc/polkit-1/rules.d/` |
| **temple-grade doc style** | @verity | Add YAML frontmatter, split oversized doc |

### ✅ RESEARCH VALIDATED (No Change Needed)

| Area | Verdict |
|------|---------|
| VaultCore (age + Argon2id) | ✅ Pattern is correct. Proceed. |
| Local restic backup | ✅ Viable for Phase D gate. Create systemd timer. |
| Admission control (C-10) | ✅ Conservative limits validated by hardware profile. |
| OOMProtector (C-2') | ✅ 3-signal fusion is correct approach. |
| CRITICAL GAPS DEEP DIVE CAMPAIGN | ✅ All 5 CG domains now have actionable findings. |

---

## §8 Raw Evidence Sources

| Domain | Sources Used | Key URLs |
|--------|-------------|----------|
| MCP 2026-07-28 RC | 8 sources | blog.modelcontextprotocol.io, mcpplaygroundonline.com, byteiota.com, luismori.dev, mcp.directory |
| MCP SDK Beta | 2 sources | blog.modelcontextprotocol.io/posts/sdk-betas |
| Vault/SOPS/Age | 7 sources | wgall.com, guptadeepak.com, dotfiles.io, github.com/danieljustus/symaira-vault |
| Restic Backup | 6 sources | the47network.com, techfuelhq.com, restic.net, cb.vu |
| Ryzen 5700U | 5 sources | techpowerup.com, techspot.com, amd.com, archlinux BBS, carteakey.dev |
| Existing Research | 5 docs | KGC_DEEP_RESEARCH_REPORT.md, R_CRITICAL_GAPS_DEEP_DIVE_CAMPAIGN.md, R_KNOWLEDGE_GAPS_DEEP_RESEARCH_20260720.md, R_MAKALI_COUNCIL_KNOWLEDGE_GAPS_20260719.md, UNKNOWN_UNKNOWNS_AUDIT_20260721.md |

---

---

## §9 Residual Meta-Gaps (Agent Support — 2026-07-25T21:35Z)

> **Correction**: §§1–8 closed **research** questions. They did **not** prove execution closure.
> Full audit: `docs/research/R_CRITICAL_SPRINT_AGENT_SUPPORT_GAPS_20260725.md`
> Live ops card: `docs/sprints/current/AGENT_SPRINT_CARD.md`
> Plan: `docs/archive/sprints/EXECUTION_PLAN_20260725.md` v1.1

| Gap | Name | Research | Execution | Owner |
|-----|------|----------|-----------|-------|
| **SG-01** | SSOT plan/hub/anchor drift | CLOSED (this audit) | OPEN — keep LAST_VERIFIED ≤12h | @kali |
| **SG-02** | Phase D gate vanity/inverted checks | CLOSED | FIXED in `scripts/verify_phase_d_gate.py` v1.1 | @verity |
| **SG-03** | C-0.5 hook unregistered | CLOSED | OPEN — register + restart | @kali |
| **SG-04** | Dirty VaultCore tree hazard | CLOSED | OPEN — land or freeze | @maat/P3 |
| **SG-05** | W-1 phantom (no SOCKS) | CLOSED | OPEN — live bring-up | Carmack/P1 |
| **SG-06** | Workhorse under D-432 | CLOSED chain | PARTIAL — enforce model card | Architect+Kali |
| **SG-07** | Soul Hardening pre-consensus | RFC open | No impl until replies | fleet |
| **SG-08** | Playbook stale mission queue | Noted | Point to sprint card | @kali |
| **SG-09** | mcp pin vs installed 1.28.x | CLOSED | Align docs | @maat/P3 |
| **SG-10** | “No blind spots” overclaim | CLOSED | Ban without EXEC column | all |

**Immediate actions** (replace §7 “pin mcp TODAY” if already pinned):

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | Pin mcp `>=1.27,<2` | @maat/P3 | ✅ pyproject done; align requirements story |
| 2 | Register C-0.5 + restart OpenCode | @kali | ❌ OPEN |
| 3 | Vault dirty-tree commit/freeze | @maat/P3 | ❌ OPEN |
| 4 | W-1 SOCKS probe green | Carmack/P1 | ❌ OPEN (no 8081–8083) |
| 5 | Run fail-closed gate script | @verity | 🔄 script fixed; run + post |

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH ⬡ GAP-CLOSURE ⬡ 2026-07-25 · residual SG-* v1.1*
