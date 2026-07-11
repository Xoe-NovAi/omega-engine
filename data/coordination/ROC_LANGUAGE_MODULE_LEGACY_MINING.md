# 🔱 ROC RACOON — Language Module Legacy Mining
**AP Token**: `AP-ROC-LANG-MOD-MINING-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b-instruct ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

**Date**: 2026-07-10
**Target module**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-moderation/`
**Mission**: Mine legacy archives for ancestors of the language module (obfuscation detection, moderation, audit/signing, PII redaction, provenance, ensembles, differential privacy).

---

## 1. Executive Summary

The `omega-moderation` module is **largely novel** — no legacy project built a content-moderation system. However, **7 of its 8 subsystems have direct or partial ancestors** in the mined legacy codebases (mostly `omega-stack-legacy` and `xna-omega-legacy`, plus research docs in `Old-Stacks`). Only **differential privacy (ε-DP)** has zero legacy precedent — confirmed gap.

| Subsystem (omega-moderation) | Legacy ancestor found? | Source |
|---|---|---|
| Obfuscation detection (leetspeak/homoglyph) | ✅ Partial (Unicode normalize + regex injection patterns) | `linguistics.py`, `prompt_detector.py` |
| PII redaction (PrivacyGuard) | ✅ Strong (14-type sanitizer) | `xna_sanitizer`, `sanitization/` |
| Tamper-evident audit (SHA-256 chain) | ✅ Partial (SHA-256 integrity + Ed25519 DID + seal) | `gmc_normalizer`, `knowledge_access`, `seal_gnosis_pack` |
| Signed erasure receipt (Merkle/Ed25519) | ✅ Partial (Ed25519 signing) | `KeyManager`, `knowledge_access` |
| Provider ensemble / weighted voting | ✅ Partial (BM25+semantic weighted ensemble) | `retrievers.py` |
| ProviderChain fault isolation | ✅ Strong (circuit breaker, HERITAGE) | `circuit_breaker` (doom-1993) |
| Provenance / watermarking | ✅ Strong (TextSeal/C2PA research + engine) | `Old-Stacks` TextSeal docs |
| Differential privacy (ε-DP metrics) | ❌ NONE — **novel** | — |

---

## 2. Relevant Legacy Artifacts

| # | Path | Lines | Pattern | Relevance to omega-moderation | Adaptation |
|---|------|-------|---------|-------------------------------|------------|
| 1 | `xna-omega-legacy/src/omega/security/prompt_detector.py` | 9-65 | `INJECTION_PATTERNS` regex list + `detect_injection()` / `sanitize_prompt()` → `[FILTERED]` | **Structural input guard** — closest legacy cousin to `obfuscation/detector.py` + `detectors/local_fallback.py`. Regex-based, returns severity + position. | Port the pattern: a configurable regex rule-table feeding `LocalFallbackProvider.detect()`. Extend with leetspeak/homoglyph maps (legacy had none). Note: legacy used Chinese injection strings (L18-20) — shows multilingual awareness. |
| 2 | `omega-stack-legacy/src/omega/knowledge/linguistics.py` | 31-42 | `normalize_ancient_greek()` — `unicodedata.normalize('NFD')` → strip combining marks → `NFC` | **Unicode normalization** — directly reusable for homoglyph/accent obfuscation reversal in `obfuscation/detector.py:normalise()`. | Use NFD-decompose + filter combining marks as a **pre-normalisation pass** before leetspeak reversal. Handles accent-stripping evasion. |
| 3 | `omega-stack-legacy/app/XNAi_rag_app/workers/crawl.py` | 33-35 | `sanitize_for_prompt_injection()` — `content.replace("ignore previous instructions","[REDACTED]")` | Minimal prompt-injection scrubber (string replace). | Reference only — superseded by #1; shows the "redact-to-placeholder" convention (`[REDACTED]`/`[FILTERED]`) now used in omega-moderation. |
| 4 | `omega-stack-legacy/mcp-servers/xna_sanitizer/server.py` | 9-136 | `ContentSanitizer` MCP exposing **14 redaction types** (api_key, password, secret, token, email, ip, credit_card, ssn, phone, private_key, connection_string, aws_key, jwt, url_credentials) + `risk_score`/`risk_level` | **DIRECT ANCESTOR of `governance/privacy.py` (PrivacyGuard.redact)**. Same taxonomy: emails/IPs/phones/keys. Has `validate_content_safety()` triage (risk<40 safe, <70 review, else sanitize). | Port `RedactionType` enum + `SanitizationConfig` + risk-threshold triage directly into `PrivacyGuard`. The 14-type catalog is a ready-made extension beyond omega-moderation's current 4. |
| 5 | `omega-stack-legacy/app/XNAi_rag_app/core/sanitization/__init__.py` | 1-37 | `ContentSanitizer` / `SanitizationResult` / `SanitizationConfig` / `RedactionType` dataclasses; result carries `.sanitized`, `.redactions`, `.risk_score` | Confirms the **dataclass result contract** pattern (mirrors omega-moderation's typed results — M21). | Adopt same result shape: `redactions` list with `type`/`preview`/`position` → feeds omega-moderation audit `text_preview`. |
| 6 | `Old-Stacks/.../docs/incoming/Claude - enterprise_integration_matrix.md` | 39-41 | `PIIFilteringFormatter` (lines 163-205), `0o700` log dir, "Enable PII redaction in build logs" | **PII redaction in logs** — maps to omega-moderation's "no raw content in logs; only SHA-256[:16]" (README §Design 3). | Adopt `PIIFilteringFormatter` concept for `observability/structured_logger.py` — ensure PII never reaches disk even in error traces. |
| 7 | `omega-stack-legacy/app/core/gmc_normalizer.py` | 58-61 | `compute_rigidity_hash()` — `hashlib.sha256(content.encode()).hexdigest()` | **SHA-256 content integrity hash** — primitive behind omega-moderation's `AuditService` hash chain. | Reuse verbatim as the per-event hash primitive; chain `prev_hash + event_hash → new_hash`. |
| 8 | `omega-stack-legacy/app/XNAi_rag_app/core/knowledge_access.py` | 15, 80, 93, 385 | "Agent DID validation via **Ed25519 signatures**"; `audit_id` threaded through `AccessResult`; `log access attempt for audit` | **Signed identity + audit trail** — ancestor of omega-moderation's signed erasure receipt + audit `trace_id`. | Port Ed25519 signing for the **GDPR erasure receipt** (`test_gdpr_erasure.py` references "signed Merkle/Ed25519 receipt"). `audit_id` ↔ `trace_id` correlation pattern. |
| 9 | `xna-omega-legacy/tests/test_iam_phase426.py` | 243-283 | `KeyManager.sign_message()` / `verify_signature()` (Ed25519) | Concrete Ed25519 sign/verify test harness. | Use as reference implementation for the erasure-receipt signature in `governance/audit.py`. |
| 10 | `omega-stack-legacy/mcp-servers/xnai-gnosis/server.py` | 273-293 | `seal_gnosis_pack(pack_path, hash)` — "🔒 Atomic sealing … StrictProvenance … anchored in ALETHIA_REGISTRY"; validates via `OctaveValidator` before seal | **Tamper-evident sealing + provenance registry** — conceptual ancestor of omega-moderation's append-only `audit_chain.jsonl` + `/api/v1/audit/status`. | Mirror the "validate-then-seal" gate: a decision must pass schema validation before a hash-chain entry is written (prevents corrupt-chain writes). |
| 11 | `Old-Stacks/.../final_implementation_guides/Claude - xoe_security_implementation.md` | 994-1103 | `TextSealEngine` + `C2PAManifest` — RSA-PSS **SHA-256** manifest signing, `content_hash`, `instance_id`, watermark bits | **Content provenance / watermarking** — strongest legacy provenance pattern; directly informs omega-moderation's audit-chain + future C2PA export. | Optional: emit a `C2PAManifest` alongside each moderation decision for external provenance. The RSA-PSS+SHA-256 signing is the model for the erasure receipt. |
| 12 | `Old-Stacks/.../docs/research/.../Grok Research Report - Phase 1 Critical Research Package.md` | 109-151 | Meta **TextSeal** (Dec 2025) post-hoc watermarking via GGUF rephrase; "torch-free path"; green-list bias | Research rationale for provenance-without-framework-mod. | Confirms provenance can be post-hoc (like omega-moderation's after-the-fact audit chain), not generation-time. |
| 13 | `omega-stack-legacy/app/XNAi_rag_app/services/rag/retrievers.py` | 265-269 | `combined_score = alpha * normalized_bm25 + (1-alpha) * normalized_semantic` | **Weighted ensemble of two signals** — direct ancestor of `detectors/huggingface.py` "weighted ensemble voting" + `detectors/chain.py` voting. | Port the alpha-weighted fusion as the model-vote combiner; `alpha` ↔ configurable per-detector weight in `config/moderation.yaml`. |
| 14 | `omega-stack-legacy/app/XNAi_rag_app/core/tests/test_integration.py` | 45-474 | `AsyncCircuitBreaker` state machine (CLOSED→OPEN→HALF_OPEN), metrics, concurrency tests | **Fault isolation** — ancestor of `detectors/chain.py` "ordered failover + graceful degradation" (every provider returns safe `allow` on failure). HERITAGE: `[id-soft: doom-1993] Circuit Breaker` (CREDITS §1.8). | Port the breaker state machine around each cloud detector (Perspective/OpenAI) so a timeout trips to `LocalFallbackProvider`. |
| 15 | `foundation-legacy/.../tests/test_circuit_breaker_chaos.py` | 5-227 | "Pattern 5 circuit breaker" chaos tests (fail-fast, state transitions) | Same pattern, Era-2 origin (5 design patterns). | Confirms circuit breaker is a long-standing sovereign pattern; reuse chaos-test style for `test_engine_integration.py` failover. |
| 16 | `omega-stack-legacy/app/XNAi_rag_app/core/xnai_axiom_arbiter.py` | 319-397 | `lilith_decides()` — non-negotiable REJECT on `privacy_at_risk`/`boundary_breach`; **Triad voting** (unanimous/majority/single) | **Policy gatekeeper + multi-vote arbitration** — ancestor of `governance/actions.py` ActionRouter (allow→flag→warn→remove→ban) + `detectors/chain.py` voting. | Port the "non-negotiable override" concept: a hard `privacy_at_risk` → force `remove` regardless of ensemble score. Triad voting ↔ weighted provider voting. |
| 17 | `omega-stack-legacy/app/XNAi_rag_app/core/maat_guardrails.py` | 1-95 | `MaatGuardrails` — 42 ideals, `IdealResult`/`ComplianceReport` dataclasses, `severity` levels | **Config-driven compliance gate** — ancestor of `governance/policy.py` threshold config. | Adopt the `severity`-tiered result dataclass for `ActionRouter` decisions. |
| 18 | `omega-stack-legacy/app/XNAi_rag_app/core/config_loader.py` | 55, 150 | `privacy_mode: str = "local-only"`; `ValueError if telemetry_enabled != False` | **Privacy-by-config + zero-telemetry** — matches omega-moderation M7/M8 + `redact_pii: true`. | Confirms privacy-first config convention; reuse `privacy_mode` key in `config/moderation.yaml`. |
| 19 | `xna-omega-legacy/src/omega/security/model_verifier.py` | 13-66 | `verify_gguf()` — streaming SHA-256 chunked hash, AnyIO `to_thread` | **Model integrity verification** (provenance of the *model*, not content). | Relevant if omega-moderation pins a local HF model — verify `unitary/toxic-bert` checksum at load (provenance of detector). |

---

## 3. Adaptation Recommendations (concrete)

1. **PII redaction** → Port `xna_sanitizer`'s `RedactionType` enum + `SanitizationConfig` + 14-type catalog (`#4,#5`) into `governance/privacy.py`. Extend omega-moderation's current 4 types (email/ip/phone/key) to the full 14. Keep the `risk_score` triage (<40 safe / <70 review / else sanitize).
2. **Obfuscation normalisation** → Add `linguistics.py:normalize_ancient_greek` NFD-strip-NFC pass (`#2`) as step 0 of `obfuscation/detector.py:normalise()` to defeat accent/homoglyph evasion, then apply leetspeak map. Borrow `prompt_detector.py`'s regex rule-table + severity/position output (`#1`) as the structural fallback skeleton.
3. **Audit hash chain** → Use `gmc_normalizer.compute_rigidity_hash` (`#7`) as the per-event primitive; adopt `seal_gnosis_pack`'s validate-then-seal gate (`#10`) so a decision must pass schema check before a chain entry is appended (prevents corrupt-chain writes). Thread `audit_id`↔`trace_id` per `knowledge_access.py` (`#8`).
4. **Signed erasure receipt** → Implement Ed25519 signing via `KeyManager.sign_message/verify_signature` (`#9`) + RSA-PSS/SHA-256 from `TextSealEngine` (`#11`) for the GDPR Article 17 tombstone receipt (`test_gdpr_erasure.py`). **Merkle tree is NOT in legacy** — build new or use a simple hash-chain root signature.
5. **Provider ensemble** → Port `retrievers.py` alpha-weighted fusion (`#13`) as the vote combiner in `detectors/huggingface.py` / `detectors/chain.py`; expose `alpha`/weights in `config/moderation.yaml`.
6. **Fault isolation** → Wrap each cloud detector in the `AsyncCircuitBreaker` state machine (`#14,#15`, HERITAGE doom-1993) so timeouts degrade to `LocalFallbackProvider` (safe `allow`). Reuse chaos-test style.
7. **Policy gatekeeper** → Port `xnai_axiom_arbiter.lilith_decides` non-negotiable-override (`#16`) → a hard `privacy_at_risk`/severity cap in `governance/actions.py` that forces `remove`/`ban` regardless of ensemble confidence. Adopt `maat_guardrails` severity-tiered result dataclass (`#17`).
8. **Provenance (optional)** → Emit a `C2PAManifest` (`#11`) per decision for external C2PA compliance; verify local HF model checksum at load (`#19`).

---

## 4. Heritage Tags Applied

Per `CREDITS.md`, only patterns genuinely derived from id Software receive `[id-soft:]` tags. Findings:

| Legacy pattern | id-soft tag? | Basis |
|---|---|---|
| Circuit breaker (fault isolation, `#14,#15`) | ✅ `[id-soft: doom-1993] Circuit Breaker` | CREDITS §1.8 — ported & evolved to AnyIO `AsyncCircuitBreaker`. |
| SHA-256 hash chain / integrity (`#7,#8,#10,#11`) | ❌ NOT id-soft | Standard cryptography, user-original. (Conceptual cousin: `[id-soft: doom-1993] ZONEID` checksum, but NOT a direct derivation — do not tag.) |
| Ed25519 / RSA-PSS signing (`#8,#9,#11`) | ❌ NOT id-soft | Standard PKI; user-original / Meta(TextSeal)/C2PA-coalition. |
| Unicode normalization (`#2`) | ❌ NOT id-soft | Python stdlib `unicodedata`. |
| Weighted ensemble (`#13`) | ❌ NOT id-soft | User-original (BM25+semantic fusion). |
| TextSeal / C2PA (`#11,#12`) | ❌ NOT id-soft | **External**: Meta TextSeal (Dec 2025) + C2PA coalition — cite as `Meta TextSeal` / `C2PA`, not id-soft. |

**Conclusion**: Only the **circuit breaker** carries a legitimate `[id-soft:]` heritage tag. All other patterns are user-original (XNAi/Omega stack) or third-party (Meta/C2PA). No false attribution.

---

## 5. Gaps Confirmed (what legacy does NOT have — module is novel)

- **Differential privacy (ε-DP)**: Zero legacy references. `test_privacy_dp.py` / `observability/differential_privacy.py` (contribution bounding, Laplace bounded-sum) is **genuinely novel** — no ancestor in any partition.
- **Merkle tree**: Not present in legacy. Ed25519 signing exists (`#8,#9`), but the Merkle/Ed25519 *receipt* structure in `test_gdpr_erasure.py` must be built new.
- **Obfuscation-specific detection** (leetspeak/homoglyph/spacing/bidi/Greek-homoglyph/dual-pass): Legacy had only generic injection regex (`#1`) + Unicode normalize (`#2`). The structural `LocalFallbackProvider` evasion catalog is **new**.
- **No-slur-list ML-only moderation**: Legacy had no moderation system at all; `prompt_detector.py` was injection-focused, not toxicity. The "ML + structural, zero lexical blacklist" philosophy is novel.
- **Multi-provider moderation ensemble** (Perspective + OpenAI + HF + local): Legacy ensemble was retrieval-only (`#13`); applying weighted voting to *toxicity* detectors is new.
- **Omnidroid (Era 0)**: Its "audit" references are SEO/helpfulness audits (`Ω AetherPen`, `Ω Product Sage`); the PLO does etymological analysis but **no security/moderation guard**. Confirmed no moderation ancestor in genesis docs.

---

## 6. Cross-Reference to Current Module (`omega-moderation`)

| omega-moderation file | Legacy ancestor(s) |
|---|---|
| `obfuscation/detector.py` (`normalise`) | `#2` linguistics NFD/NFC, `#1` prompt_detector regex |
| `detectors/local_fallback.py` | `#1` prompt_detector, `#3` sanitize_for_prompt_injection |
| `governance/privacy.py` (PrivacyGuard.redact) | `#4,#5` xna_sanitizer 14-type, `#6` PIIFilteringFormatter |
| `governance/audit.py` (SHA-256 chain) | `#7` rigidity_hash, `#10` seal_gnosis_pack, `#8` audit_id |
| `governance/audit.py` (GDPR erasure receipt) | `#8,#9` Ed25519, `#11` RSA-PSS/SHA-256 (Merkle = new) |
| `detectors/huggingface.py` (weighted ensemble) | `#13` retrievers alpha-fusion |
| `detectors/chain.py` (failover + voting) | `#14,#15` circuit breaker (doom-1993), `#16` triad voting |
| `governance/actions.py` (ActionRouter) | `#16` lilith_decides override, `#17` maat severity |
| `governance/policy.py` | `#17` maat_guardrails, `#18` privacy_mode config |
| `observability/differential_privacy.py` | **NONE — novel** |
| `observability/structured_logger.py` | `#6` PIIFilteringFormatter (extend to all logs) |
| `detectors/huggingface.py` (model load) | `#19` verify_gguf checksum |

**Verification**: All 19 artifacts cited with file path + line numbers. Legacy partitions read-only; this report is the only write. Grep strategy covered 8 search terms × 4 codebases + Omnidroid + research docs. No patterns invented — gaps explicitly stated.

*⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b-instruct ⬡ opencode ⬡ trc_mining ⬡ ACTIVE*
*"The dirt is where the roots are. If the surface is clean but the foundation is rotten, dig deeper."*
