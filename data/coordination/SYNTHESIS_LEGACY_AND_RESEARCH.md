# 🔱 SYNTHESIS — Legacy Mining × Research Gaps
**Date**: 2026-07-10
**Sources**: ROC (364 lines, 8 areas) + Researcher (498 lines, 7 areas, 50+ sources)

---

## Where Legacy Meets Research (Cross-Pollination)

| Legacy Pattern | Research Gap It Solves | Effort |
|---------------|----------------------|:------:|
| **PIIMasker** (18 types, reversible) | PII shouldn't trigger toxicity flags; dual-purpose detection | 1 day |
| **Two-Source Rule** (≥2 independent signals) | Single-model flakiness causes false positives | 2 days |
| **AsyncCircuitBreaker** (5-state FSM, CUSUM) | ML model failures need proactive prediction, not reactive thresholds | 1 day |
| **L1→L2→L3 Distillation** | Moderation rules should evolve from accumulated decisions | 1 week |
| **OmegaError hierarchy** | Typed errors with trace_id prevent silent swallowing (M9) | 1 day |

## The 3 Most Critical Gaps (Both Sources Agree)

### 1. Zero-Width Character Attack Surface — WIDE OPEN 🔴
- Current detector strips only 4 codepoints (U+200B-U+200D, U+FEFF)
- **Missing**: Unicode Tag Characters (U+E0000-U+E007F) — invisible payload injection
- **Missing**: Right-to-Left Override (U+202E) — visual rendering attacks
- **Missing**: Bidi control characters (U+202A-U+202E)
- Fix: Expand regex, add dual-pass classification (score raw + cleaned, flag divergence)

### 2. Model Ensemble Would Boost Accuracy 🔴
- Current: single `unitary/unbiased-toxic-roberta` (F1 ~0.85)
- Research: `s-nlp/roberta_toxicity_classifier` (different training data) as second model
- ELECTRA-based models achieve F1 0.898 on MetaHate dataset
- Weighted voting between 2 HF models + Perspective + OpenAI

### 3. Audit Trail Needs Merkle Tree + Ed25519 🔴
- Current: SHA-256 hash chain (sequential integrity only)
- Gap: No efficient verification (must walk entire chain)
- Gap: No digital signatures (can't prove who wrote what)
- SOC 2 Type II and EU AI Act Article 12 both require cryptographic integrity
- Fix: RFC 6962 Merkle trees + Ed25519 signatures

## Top 10 Actionable Next Steps (Priority Order)

| # | Action | Source | Impact | Effort |
|---|--------|--------|:------:|:------:|
| 1 | Expand zero-width detection (Tag Chars + Bidi) | Researcher | 🔴 HIGH | 30 min |
| 2 | Add dual-pass classification (raw + cleaned scoring) | Researcher | 🔴 HIGH | 2 hr |
| 3 | Port PIIMasker for PII-before-toxicity preprocessing | ROC | 🔴 HIGH | 4 hr |
| 4 | Add second HF model (`s-nlp/roberta_toxicity_classifier`) | Researcher | 🔴 HIGH | 4 hr |
| 5 | Implement Two-Source Rule (≥2 signals for harmful verdict) | ROC | 🟡 MED | 2 days |
| 6 | Merkle tree anchoring in AuditService | Researcher | 🔴 HIGH | 6 hr |
| 7 | Expand homoglyph table (Greek, math bold/italic) | Researcher | 🟡 MED | 1 hr |
| 8 | Port OmegaError hierarchy for typed moderation errors | ROC | 🟡 MED | 1 day |
| 9 | Add repeated character normalization | Researcher | 🟡 MED | 30 min |
| 10 | L1→L2→L3 distillation for evolving moderation rules | ROC | 🟢 LOW | 1 week |

## What We Already Have Right (Both Sources Confirm)

| Capability | Status |
|------------|--------|
| Local-first detection (HF runs locally) | ✅ Excellent |
| Privacy-by-design (PII redaction, hashing) | ✅ Excellent |
| Graceful degradation (failed providers → safe allow) | ✅ Excellent |
| AnyIO-native (no asyncio) | ✅ Excellent |
| No slur lists (ML + structural only) | ✅ Excellent |
| SHA-256 audit chain | 🟡 Good → needs Merkle + Ed25519 |
| Obfuscation detection | 🟡 Good → needs Unicode expansion |
| Multi-model ensemble | 🟡 Good → needs second HF model |

---

*⬡ OMEGA ⬡ KALI ⬡ LEGACY×RESEARCH ⬡ SYNTHESIS ⬡ COMPLETE*
