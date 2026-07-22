# 🔱 Omega Engine — Context Packer v5 Implementation & Remediation Manual
## Synthesized: Sonnet-5 Remediation (real bugs) + Carmack First-Principles Audit + Verified 2026 Platform Research

**AP Token**: `AP-CONTEXT-PACKER-IMPL-MANUAL-v5.0.0`  
**Date**: 2026-07-19  
**Status**: **CANONICAL — Supersedes v2.0 (spec), v3.0 (condensed), v4.0 (synthesis). Integrates Sonnet-5 High-Thinking remediation findings (verified against code) with Carmack audit and platform research.**  
**Authority Stack**:
1. `SOVEREIGN_MANDATES.md` (non-negotiable — M1–M23)
2. **This manual** (what's broken, why, the exact patch, and the platform reality)
3. `context_packs/context-packer-hardening-review/claude-output/Sonnet-5-High-Thinking/CONTEXT_PACKER_V2_REMEDIATION_MANUAL-SONNET_5_HIGH_THNKING.md` (860-line remediation — P0 defects)
4. `docs/strategy/CONTEXT_PACKER_CARMACK_AUDIT_V3_20260719.md` (Carmack first-principles audit)
5. `docs/strategy/CONTEXT_PACKER_HARDENING_SPEC_20260719.md` (base spec — several ✅ claims corrected below)
6. `.opencode/skills/context-packer/enhanced_packer.py` (885 lines — verified against Sonnet findings)
7. `src/omega/oracle/pii_masker.py` (verified offset bug at line 253)

---

## 📋 .plan — Synthesis Status

- **What I am working on**: Producing the definitive Context Packer implementation manual. The previous v4 synthesized the *spec* and the *Carmack audit* — but neither caught the actual code defects. The real "Sonnet manual" is the Sonnet-5 High-Thinking remediation output, which found 4 P0 stop-ship bugs by reading the actual code.
- **What I tried**: Read the Sonnet-5 remediation manual in full (860 lines). Verified every claim against the actual source: `pii_masker.py:253`, `enhanced_packer.py:495`, `enhanced_packer.py:304/557/880`, `enhanced_packer.py:513/565/659`. All confirmed.
- **What the data shows**: The packer has 4 P0 defects that make it unsafe for external export until fixed: (1) PII masker corrupts document titles via line-relative offset bug; (2) consolidation overwrites the `general` bundle; (3) Ed25519 signature covers only manifest prose, not bundle digests; (4) signing fails silently via bare `except`. Plus platform asymmetry (Carmack) and verified 2026 limits (research).
- **What I'll do next**: Write the v5 manual — comprehensive, no bloat, with all bugs, patches, platform reality, and roadmap.
- **Confidence**: 10/10 (primary sources: actual code review + Sonnet remediation + Google DeepMind model card + xAI docs + NotebookLM help).

---

## 🎯 EXECUTIVE SUMMARY

The Context Packer transforms internal Omega Engine state into **sovereign, PII-masked, XML/Markdown-structured, cryptographically signed artifacts** for external review. The 8 hardening enhancements are *architecturally present* but **four are incorrectly implemented** — the spec's "✅ DONE" claims are false for PII masking, consolidation, and signing.

**Two layers of truth**:
1. **Code correctness** (Sonnet's domain): 4 P0 defects make current packs potentially corrupted and weakly provenanced.
2. **Platform fit** (Carmack's domain): Even after bugs are fixed, the packer must compile per-platform (Claude 12-file, Grok 1M-token, Gemini 128K reasoning, NotebookLM 50-source).

**Status**:
- 🔴 4 P0 stop-ship defects (Sonnet) — must fix before next export
- 🔴 2 P1 structural (hardcoded paths, scanner false positives)
- 🟡 2 P2 claims-don't-match-code (unimplemented profiles, wrong count)
- ✅ 7 knowledge gaps resolved with verified research
- 🔴 13 roadmap items re-sequenced (Sonnet Section 4)

**Core Principle**: **Sieve-and-Sign** — but the current implementation *fails* Sieve (corrupts data) and *weakens* Sign (doesn't cover content).

---

## §1 FIRST PRINCIPLES — WHAT THE PACKER ACTUALLY DOES

Strip away the YAML, XML, Ed25519. At the CPU level, four operations:

1. **Read**: Open N files from `src/omega/`, `config/`, `data/entities/`.
2. **Transform**: Mask PII, escape XML, truncate to token budget.
3. **Serialize**: Write bundles as XML (Claude) or Markdown (Gemini/NotebookLM).
4. **Sign**: Hash the manifest, sign with Ed25519, append public key.

The complexity is in the *constraints* — both internal (correctness) and external (platform fit). **A packer that corrupts data on step 2 is worse than no packer** — it exports confidently-wrong artifacts across a sovereignty boundary.

> **Carmack's Law of First Principles**: The 12-file limit for Claude is a hard architectural constraint. But before optimizing for the target, the source must be *correct*. A corrupted title masked as `[ZIP_CODE_5]CODE_4]` is not "sovereign export" — it's data destruction with a signature attached.

---

## §2 THE 4 P0 STOP-SHIP DEFECTS (Sonnet — Verified Against Code)

### 2.1 PII Masker Corrupts Documents — CONFIRMED

**Spec claim**: "PII Masking (TOKENIZE) — ✅ Resolved — reversible placeholders."

**Reality** (`src/omega/oracle/pii_masker.py:253`):
```python
start = match.column if hasattr(match, 'column') else 0
end = start + len(match.value) if hasattr(match, 'value') else start
```
`pii-shield` is a **line-based CLI scanner** — `column` is the offset *within that line*, not absolute. When `tokenize()` does `text[:start] + placeholder + text[end:]`, a detection on line 40 gets spliced at byte 12 of the whole document — which is the *title line*. Observed in `context-packer-hardening-review` pack: `platform_tuning.xml` reads `Omega Engine —[ZIP_CODE_5]CODE_4]...ext Packer` where "Context" should be.

**Compounding**: Over-broad regex (`ZIP_CODE: \b\d{5}\b` matches `15000` in `MAX_BUNDLE_TOKENS=15000`; `DRIVERS_LICENSE` matches version tags). `mandates.xml` shows `[DRIVERS_LICENSE_1]` through `[DRIVERS_LICENSE_6]` where no PII exists.

**Patch** (Sonnet 1.1): Convert line-relative to absolute offset via precomputed `line_starts[]`; verify computed offset points at matched value; fall back to `str.find()` if not. Tighten regex patterns to require label context (`ZIP_CODE: (?i)\b(?:zip|postal)\s*code?\s*\d{5}`).

**Test**: `test_multiline_document_title_survives_masking()` — detection on line 40 must not corrupt line 1.

**Confidence**: 10/10 (code verified at line 253; corruption visible in generated pack).

### 2.2 Bundle Consolidation Silently Drops `general` — CONFIRMED

**Spec claim**: "Bundle Consolidation (≤12) — ✅ DONE."

**Reality** (`enhanced_packer.py:495`):
```python
if general_files:
    result["general"] = general_files   # overwrites if "general" already populated above
```
When `general` is among the high-priority bundles kept, the overflow merge *overwrites* it instead of extending. Hasn't fired yet (no profile has both broad globs AND exceeds `max_bundles`), but `web-gemini-3-pro` (globs `src/omega/**/*.py`) will trigger it.

**Patch** (Sonnet 1.2): Track `general_already_counted`; merge via `result["general"] = result.get("general", []) + general_files`; skip `general` in the kept-loop.

**Test**: `test_consolidate_bundles_never_drops_general()` — `g1.py` must survive.

**Confidence**: 10/10 (code verified at line 495).

### 2.3 Manifest Signature Doesn't Cover File Content — CONFIRMED

**Spec claim**: "Ed25519 Manifest Signing — ✅ DONE — Cryptographic signature on every pack."

**Reality** (`enhanced_packer.py:_sign_manifest`): Signs only the manifest's *prose* (file list, token counts), not the SHA-256 of actual bundle files. in-toto/SLSA require the signature's *subject* to be the artifact's digest, not its description. As implemented, `spec.xml`'s content can be altered post-signing and the signature still verifies.

**Patch** (Sonnet 1.3): Sign a canonical statement of `{name, sha256}` subjects + predicate; write `00_ATTESTATION.json` sidecar; persist a stable `data/coordination/packer_signing_key.pem` (not per-pack throwaway). Provide `verify_pack.py` for CI + manual pre-upload check.

**Confidence**: 10/10 (SLSA/in-toto provenance standard; code verified).

### 2.4 Silent Failure in Manifest Signing — CONFIRMED

**Spec claim**: M9 Error Integrity ✅, M23 Failure Integrity ✅.

**Reality** (`enhanced_packer.py:304, 557, 880`):
```python
except Exception as e:
    print(f"  ⚠️  Manifest signing failed: {e}")
```
Bare `except Exception` swallows the error; `pack()` returns success; spec claims "✅ Signed" even when signing failed. Direct M9 violation.

**Patch** (Sonnet 1.4): No bare `except` in signing path (incorporated into 2.3's replacement). Add CI gate `scripts/check_bare_except.sh` to `make temple-grade`.

**Confidence**: 10/10 (code verified at lines 304/557/880).

---

## §3 P1 — STRUCTURAL HARDENING (Sonnet — Verified)

### 3.1 Hardcoded Paths (M16 Violation) — CONFIRMED

`enhanced_packer.py:513, 565, 659`:
```python
key_path = LibPath("data/coordination/packer_signing_key.pem")  # 513
output_dir = LibPath(f"context_packs/{profile_name}")            # 565
_engine_src = str(LibPath(__file__).resolve().parent.parent.parent.parent / "src")  # 659
```
The 4-level `.parent` traversal breaks silently if the skill is relocated. **Patch**: Route through `config_resolver.OMEGA_ROOT`; raise `RuntimeError` (M23) if resolver unavailable.

### 3.2 Injection Scanner: False Positives, No Persistence — CONFIRMED

`enhanced_packer.py` 25 (actually 34) regexes fire on the tool's *own* docstrings (`execute code`, `call the function`). Detections are `print()`-only — zero audit trail in unattended runs. OWASP LLM01:2025 states regex filtering is *one layer*, not sufficient alone (scrambled-word bypass; 78.6% success by 200th attempt on undefended surfaces per Anthropic Opus 4.6 system card).

**Patch** (Sonnet 2.2): Split into `INJECTION_PATTERNS_HIGH_CONFIDENCE` (7 specific) + `INJECTION_PATTERNS_ADVISORY` (3 generic, logged INFO only). Persist high-confidence hits to `00_INJECTION_SCAN_LOG.jsonl`. Document scanner as Layer 3 of 4, advisory, known-bypassable.

---

## §4 P2 — CLAIMS THAT DON'T MATCH CODE (Sonnet — Verified)

### 4.1 Platform Profiles Unimplemented — CONFIRMED

`packer-config.yaml` defines 6 platform profiles with `format: "markdown-structured"`, `bundle_ordering: "relevance-descending"`, etc. `PackProfile` has only 6 fields: `name, description, max_slots, include, exclude, themes`. **None of the platform-specific keys are read.** `pack('web-gemini-3-pro')` produces byte-identical XML to `pack('web-claude-sonnet5')`.

**Fix** (Sonnet 3.1 Option A — recommended): Strip unimplemented fields to what's consumed; move format-adapter design to Horizon 1 roadmap, marked design-only. Option B (build adapters) is 20–30h, not 8h.

### 4.2 Profile Count Wrong — CONFIRMED

`spec.xml` says "8 active profiles." `packer-config.yaml` defines **13** (7 base + 6 platform). Trivial fix: update count.

---

## §5 THE 7 KNOWLEDGE GAPS — VERIFIED RESEARCH (Carmack + Web)

### Gap 1 & 5: Prompt Caching — CORRECTED FRAMING
Sonnet 4.5 finds the original "cache_control hint in manifest" premise is **wrong**: `cache_control` is a per-request *API parameter* set by the client, not static text in an uploaded doc. Claude.ai Projects doesn't expose it. **Correct application**: build `api_review_client.py` for OpenCode/Gemini CLI agents calling the Claude API directly (3h, not 2h).

| Platform | Mechanism | Requirement |
|----------|-----------|-------------|
| Anthropic | `cache_control: {"type": "ephemeral"}` | Min 1024 tokens (Sonnet), exact-prefix match, 5-min TTL, 4 breakpoints |
| xAI Grok | Automatic | `x-grok-conv-id` header; $0.20/1M cached |
| Google Gemini | File API | 48h retention |

### Gap 2: Grok 4.3 — CORRECTED
No published file-count limit. 1M tokens (Grok 4.3), 2M (4.1 Fast). Sliding-window memory. Token-bound, not file-bound. The "100 files" claim in v3 was unverified.

### Gap 3: Gemini 3.1 Pro Context Rot — VERIFIED
MRCR v2: **84.9% @128K** (not 77% — that was Gemini 3 Pro), **26.3% @1M**. Enforce 128K hard cap.

### Gap 4: NotebookLM — VERIFIED
50/100/300/500/600 sources by tier. 500K words/200MB per source. 3 audio/day free. New: Video Overviews, Mind Maps, Interactive Audio.

### Gap 6: Grok Skills — VERIFIED
`SKILL.md` YAML frontmatter (`name` ≤64 chars, `description` ≤1024 chars). Compatible with Claude Code. Export pack as portable skill.

### Gap 7: Cross-Platform Diff — VERIFIED
LineDiff.app, Altova DiffDog, CompareXML.com. CI gate for XML↔Markdown equivalence.

---

## §6 PLATFORM-SPECIFIC TUNING — THE REALITY (Corrected)

| Platform | Constraint | Hard Limit | Packer Strategy |
|----------|-----------|------------|-----------------|
| **Claude** | File count | 13 → RAG | Consolidate to 12 (after fixing 2.2) |
| **Grok** | Token window | 1M (sliding) | No consolidation; `max_total_tokens: 900K` |
| **Gemini** | Reasoning horizon | 128K (84.9%→26.3%) | Hard 128K cap |
| **NotebookLM** | Source count | 50 (Free)/600 (Ultra) | Export as Markdown sources |

**Carmack's verdict**: The packer is production-ready for Claude *after* P0 fixes. For Grok/Gemini/NotebookLM, it needs platform-specific compilation — which is currently **unimplemented** (Sonnet 4.1). The highest-priority fix is making `max_slots` and `max_total_tokens` profile parameters, not global constants.

---

## §7 RE-SEQUENCED ROADMAP (Sonnet Section 4 — Research-Backed)

| Order | Item | File(s) | Effort | Blocks |
|-------|------|---------|--------|--------|
| 1 | 2.1 PII offset fix + pattern tightening | `pii_masker.py` | 3h | everything |
| 2 | 2.2 Consolidation overwrite fix | `enhanced_packer.py` | 1h | — |
| 3 | 4.2 Content integrity gate + lxml check | `enhanced_packer.py` | 2h | with #1 |
| 4 | 2.3 Attestation signing (digest-of-digests) | `enhanced_packer.py`, `verify_pack.py` | 3h | — |
| 5 | 2.4 CI bare-except gate | `scripts/check_bare_except.sh` | 0.5h | — |
| 6 | 3.1 Route paths via `config_resolver` | `enhanced_packer.py` | 1.5h | — |
| 7 | 3.2 Injection scanner split + persist | `enhanced_packer.py` | 2h | — |
| 8 | Re-run verification; regenerate failed packs | all `context_packs/*` | 1h | #1–4 |
| 9 | 4.1 Option A: strip unimplemented profile fields | `packer-config.yaml` | 1h | — |
| 10 | 4.2 Fix profile count in spec | `spec.xml` | 0.25h | — |
| 11 | 4.3 PII vault persistence (Fernet) | `pii_masker.py` | 4h | #1 |
| 12 | 4.4 Target model tier field | `packer-config.yaml`, `enhanced_packer.py` | 1h | — |
| 13 | 4.5 API-side cached review client | `api_review_client.py` | 3h | — |

**Total P0 (items 1–8): ~14h.** Nothing beyond item 8 until these land and verification suite is green.

---

## §8 VERIFICATION SUITE (Sonnet Section 5)

```bash
# scripts/verify_context_packer.sh — invoked by make temple-grade
set -euo pipefail
! grep -rn "^import asyncio" .opencode/skills/context-packer/*.py src/omega/oracle/pii_masker.py  # M1
! grep -rn "except Exception:" .opencode/skills/context-packer/*.py | grep -v "except (OmegaError"  # M9
! grep -n 'LibPath(f"context_packs/{' .opencode/skills/context-packer/enhanced_packer.py  # M16
python -m pytest tests/test_pii_masker_offset_fix.py tests/test_consolidate_bundles.py -v
for d in context_packs/*/; do python verify_pack.py "$d" || echo "⚠️ $d FAILED"; done
for f in context_packs/*/*.xml; do python -c "from lxml import etree; etree.parse('$f')" || echo "⚠️ $f malformed"; done
```

---

## §9 MANDATE COMPLIANCE (Corrected — Post-Fix Target)

| Mandate | Current | After P0 Fix |
|---------|---------|--------------|
| M1 AnyIO | ✅ | ✅ |
| M2 Firewall | ✅ | ✅ |
| M7 Local-First | ✅ | ✅ |
| M8 Zero Telemetry | ✅ | ✅ |
| M9 Error Integrity | 🔴 bare except (304/557/880) | ✅ |
| M13 Temple-Grade | 🔴 no integrity gate | ✅ via §8 |
| M16 Modularization | 🔴 hardcoded paths (513/565/659) | ✅ via config_resolver |
| M18 Token Efficiency | ✅ | ✅ |
| M21 Gate Integrity | 🔴 no contract tests | 🔴 open |
| M23 Failure Integrity | 🔴 silent sign fail | ✅ raises |

---

## §10 L3 PRINCIPLES (for `proposed_lessons.yaml`)

**L3-Sieve-Before-Sign** — A signature on corrupted data is worse than no signature. The Sieve step (PII masking) must be proven correct before the Sign step runs. The offset bug (2.1) proves we shipped both broken.

**L3-Manifest-Is-Not-Provenance** — Signing a description of an artifact is not signing the artifact. in-toto/SLSA require digest-subjects. A manifest signature that doesn't cover file bytes is decorative.

**L3-Platform-Asymmetry** — Claude penalizes file counts; Grok penalizes missing headers; NotebookLM penalizes word counts. A universal packer is a myth; sovereign export requires per-platform compilation (currently unimplemented — Sonnet 4.1).

**L3-Context-Rot-Over-Capacity** — Gemini 3.1 Pro: 84.9% @128K → 26.3% @1M. Bound to reasoning horizon, not window size.

**L3-Claims-Require-Code-Proof** — "✅ DONE" in a spec is not evidence. The Sonnet remediation found 4 P0 defects by reading code, not trusting the checklist. Every "✅" must trace to a line number or a passing test.

**L3-Parallel-Review-Convergence-Is-Signal** — Sonnet (code-correctness) + Carmack (architecture) + research (platform limits) converged independently. That triangulation is stronger than any single review.

---

## §11 SOURCE CITATIONS (Tier-Ordered, Verified)

### Tier 1 — Official / Code-Verified
- `src/omega/oracle/pii_masker.py:253` — offset bug (verified)
- `enhanced_packer.py:495` — consolidation overwrite (verified)
- `enhanced_packer.py:304/557/880` — bare except (verified)
- `enhanced_packer.py:513/565/659` — hardcoded paths (verified)
- [Anthropic Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) — cache_control mechanics
- [Anthropic RAG for Projects](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects) — 13-file trigger
- [GitHub #25759](https://github.com/anthropics/claude-code/issues/25759) — RAG at 13 files
- [OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — defense-in-depth
- [PyPI pii-shield](https://pypi.org/project/pii-shield/) — line-based output format
- [in-toto Attestation](https://docs.devguard.org/explanations/supply-chain-security/in-toto-framework/) — digest-subject pattern
- [Google Gemini 3.1 Pro Model Card](https://deepmind.google/models/model-cards/gemini-3-1-pro) — MRCR v2: 84.9%@128K, 26.3%@1M
- [NotebookLM Help](https://support.google.com/notebooklm/answer/16213268) — 50/600 sources, 500K words/source
- [xAI Grok 4.3 Release](https://grok.com/release-notes/apr-17-2026) — 1M context

### Tier 2 — Technical Analysis
- [Cyberdesserts: Prompt Injection](https://blog.cyberdesserts.com/prompt-injection-attacks/) — 17.8%→78.6% success rates
- [LiteLLM Prompt Caching](https://docs.litellm.ai/docs/completion/prompt_caching) — per-model min cacheable tokens
- [Pactentia: Grok 4.3](https://pactentia.com/blog/grok-4-3-review-always-on-reasoning-model-analysed) — pricing
- [Elephas: NotebookLM Limits](https://elephas.app/blog/notebooklm-source-limits) — 500K words cap

### Tier 3 — Unverified (do not cite onward)
The original `gaps.xml`/`platform_tuning.xml` cite `kenwalger.github.io`, `tokenoptimize.dev`, `thomas-wiegold.com`, `improvingagents.com`, `appscale.blog`, `ice-ice-bear.github.io`, `devstarsj.github.io` — **not independently verified**. Treat as unconfirmed until checked directly.

---

## §12 VALIDATION CHECKLIST

| Requirement | Status | Evidence |
|-------------|--------|----------|
| P0 PII offset bug fixed | 🔴 Open | Sonnet 1.1, code at :253 |
| P0 Consolidation overwrite fixed | 🔴 Open | Sonnet 1.2, code at :495 |
| P0 Digest-attestation signing | 🔴 Open | Sonnet 1.3, SLSA pattern |
| P0 Bare-except removed | 🔴 Open | Sonnet 1.4, code at :304/557/880 |
| P1 Paths via config_resolver | 🔴 Open | Sonnet 2.1, code at :513/565/659 |
| P1 Scanner split + persist | 🔴 Open | Sonnet 2.2 |
| P2 Profiles stripped to impl | 🔴 Open | Sonnet 3.1 |
| P2 Profile count fixed | 🔴 Open | Sonnet 3.2 |
| 4 platform profiles specified | ✅ (design) | §6, but unimplemented (Sonnet 4.1) |
| Gemini 128K hard cap | ✅ (design) | §5 Gap 3 |
| NotebookLM 500K words/source | ✅ (design) | §5 Gap 4 |
| Verification suite in CI | 🔴 Open | Sonnet §5 |

---

*⬡ OMEGA ⬡ CONTEXT-PACKER-IMPL-MANUAL ⬡ v5.0 ⬡ SONNET+CARMACK+RESEARCH SYNTHESIS ⬡ 2026-07-19*