# 🔱 Web Claude Review — Upload Handoff (Manual Operator Step)
**Date**: 2026-07-12 (Fable 5 deadline — TODAY)
**Status**: Packs GENERATED + VALIDATED. Upload is a MANUAL step (agent has no claude.ai session).
**Pre-req docs**: `R_CLAUDE_PROJECT_SETUP_PLAN.md` (§7 upload protocol), `R_CLAUDE_PROJECT_INSTRUCTIONS.md` (XML Custom Instructions to paste).

---

## ✅ Pack Readiness (verified)
- **24 XML bundles** across 4 profiles — all pass `xml.etree.ElementTree` well-formed check (single `<pack>` root, fully-escaped content).
- **PII masked**: packs contain `[EMAIL_n]` / `[PHONE_n]` placeholders — no raw keys/emails (SEC blocker resolved).
- **Correct theming**: `observability.xml`=12 files, `providers.xml`=7 (B8 fnmatch fixed).
- **oracle_core split** into `_a/_b/_c` (~28K tokens each) for Pattern-Miners RAG mode.

## 🚫 Excluded from upload
- `sovereign-audit/general.xml` (130 files / 1229KB) — low-signal catch-all; dilutes retrieval. Do NOT upload.

## 📋 Account → Bundle Assignment (8 accounts = 4 teams × P+R)

| Account | Bundles to Upload | Mode | Custom Instructions |
|---------|-------------------|------|---------------------|
| **Void-Seekers-P1** | `youtube-research-primer/*.xml` (5) + `sprint-context/*.xml` (4) | Direct | §1 Void-Seekers |
| **Void-Seekers-R2** | (mirror of P1) | Direct | §1 Void-Seekers |
| **Pattern-Miners-P1** | `oracle_core_a.xml`, `_b.xml`, `_c.xml`, `providers.xml`, `mcp_hub.xml` | RAG | §2 Pattern-Miners |
| **Pattern-Miners-R2** | (mirror of P1) | RAG | §2 Pattern-Miners |
| **Scribes-P1** | `kali-oversight/*.xml` (5) + `sovereign-audit/mandates.xml` + `strategy.xml` | RAG (strategy large) | §3 Scribes |
| **Scribes-R2** | (mirror of P1) | RAG | §3 Scribes |
| **Sentinels-P1** | `sovereign-audit/observability.xml` + `mandates.xml` + `kali-oversight/heritage.xml` + `coordination.xml` | Direct | §4 Sentinels |
| **Sentinels-R2** | (mirror of P1) | Direct | §4 Sentinels |

## 🔧 Upload Protocol (per account)
1. Create Project named for outcome (e.g., `Void-Seekers-YT-Research-P1`).
2. Upload `00_PROJECT_MANIFEST.md` FIRST (lists bundles, token counts, sha256).
3. Upload assigned Knowledge bundles (≤12 project files in Direct mode; RAG-mode accounts accept the large bundles).
4. Paste the matching Custom Instructions from `R_CLAUDE_PROJECT_INSTRUCTIONS.md` into the Instructions box (<1,000 words).
5. **Test retrieval** (3 queries/account — keyword, semantic, cross-file):
   - e.g. *"Based on `oracle_core_a.xml` in project knowledge, what is the ModelGateway provider priority order?"*
6. Write `decisions.md` with sprint kickoff note; re-upload after each concluded chat.

## ⚠️ Cache Bug Protocol (addendum N2)
Re-uploading a file with the same name keeps the OLD cached version. To update: **delete old → wait → upload new → new conversation → clear cache.**

## 🔄 Quota Rotation (Fable 5 5-hour limit)
- P (primary) for ~2h active work, then switch to R (mirror). Stretches 8 accounts across ~20h before July 12.
- Keep Direct Context accounts <40% utilization (≤80K tokens/theme, ≤12 files).

## ✅ Validation Gates (already passed by agent)
- `xml.etree.ElementTree` parse: 24/24 OK
- PII masking: active (no raw keys/emails)
- Theming: observability=12, providers=7 (B8 fixed)
- `make test`: 1155 passed / 34 env-fail (qdrant `localhost:6333` unreachable — infra issue, NOT packer)

*🔱 OMEGA ⬡ KALI ⬡ WEB-3-HANDOFF ⬡ 2026-07-12*
