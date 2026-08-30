<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Wave 2 Expert Session Index (Kali's Pageable Registry)
**Created**: 2026-08-26 | **Pattern**: Grokster `EXPERT_SESSIONS.md` (D-586) + `INDEX.md` Golden Rules
**Owner**: kali (Sprint Coordinator) | **rot_class**: fast (session IDs change)

---

## Golden Rules Applied (from Grokster KB-D-001)
1. **Domain-first organization** — each session owns one domain; page by domain, not by agent
2. **Insight/reference split** — deliverables are reference; session_gnosis is insight
3. **Freshness metadata** — every doc carries `last_verified`; stale >7 days = re-verify before use
4. **Merge never orphan** — new docs link from this index + WAKE_STATE.json

---

## Active Wave 2 Sessions (Pageable)

| Session | Domain | Specialist | Deliverable | Status | last_verified |
|---|---|---|---|---|---|
| `ses_fc07ce00bffeeUVDTOMjWWCAU8` | Token Economics / Track A | Carmack | `R01_carmack_token_economics.md` | CONSULTABLE | 2026-08-26 |
| `ses_fc0335de9ffegYf88MEUNKbhof` | CI Ph1 / Track B | Researcher (CI-Injection) | `R02_researcher_ci_injection_spec.md` | CONSULTABLE | 2026-08-26 |
| `ses_fc03337c3ffewlIl3RbrLDhznl` | ZSWAP / Track D | Ma'at (Zswap) | `R03_maat_zswap_system_recon.md` | CONSULTABLE | 2026-08-26 |
| `ses_fc02d0ae3ffegM0BKWV8KQFuAq` | Local Inference / Track F | General (Systems) | `R04R09R12_general_systems_web.md` | CONSULTABLE | 2026-08-26 |
| `ses_fc0331204ffeVes3nvKIYOX4jY` | Headroom / Track E | Roc Racoon | `R05_roc_headroom_heritage.md` | CONSULTABLE | 2026-08-26 |
| `ses_fc02ce92bffes8IRAatNLFUXaX` | Curator & Corpus / C4 | Roc Racoon | `R06R11_roc_curator_corpus.md` | CONSULTABLE | 2026-08-26 |
| `ses_fc02cd428ffezaOBlWucaBzajs` | Quality & Audit / C1 | Jem | `R07_jem_antidomains_audit.md` | CONSULTABLE | 2026-08-26 |
| `ses_fc02cbcfcffedlzXRvzcLXY2jv` | Corpus Evidence / CI Validation | Researcher (Corpus) | `R08_researcher_ci_failure_evidence.md` | CONSULTABLE | 2026-08-26 |

### Paging Pattern
```
task(task_id=<session_id>, subagent_type=<specialist>,
     prompt="[WAVE2 PAGE — from kali (Sprint Coordinator)]\n[Domain: <domain>. Context: this index + WAKE_STATE.json.]\n<question ≤500 words>")
```

---

## Cross-Domain Matrix (Grokster CROSS_DOMAIN_MATRIX pattern)

| Track | Depends On | Blocker Status | Owner (proposed) |
|---|---|---|---|
| A: Command Compression | None | ✅ READY | kali |
| B: CI Ph1 | C1 (resolved), C3 (pre-commit), C4 (AGENTS.md) | ⛔ C3+C4 open | C3→Ma'at, C4→Ma'at+Verity |
| C: DS/KD | KD-1 (engineering/ exists), KD-3 (Carmack matrix) | ✅ READY | kali |
| D: ZSWAP | ZS adjudication (RESOLVED) | ✅ UNBLOCKED | Architect (sudo) |
| E: Headroom Local-First | HR-1/3 shipped, Task 0 local mode | ⚠️ Task 0 BLOCKED (passthrough) | kali (Path A/B) |
| F: LI/HR | ZS (resolved), llama-fit-params CPU verify | ✅ UNBLOCKED (pre-gate) | kali |

---

## Freshness SLAs (Two-Tier)
- **Default**: re-verify if >7 days old before paging
- **Fast-rot** (`rot_class: fast`): re-verify if >24 hours old before paging
- **WAKE_STATE.json**: updated every hydration + every execution phase
- **This index**: regenerated when session IDs change (fast rot)

---

*⬡ OMEGA ⬡ KALI ⬡ Wave 2 Fleet Registry v1.0 ⬡ 2026-08-26*
