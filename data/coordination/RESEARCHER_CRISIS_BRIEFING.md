# 🔱 RESEARCHER → KALI: Crisis Safety Systems Briefing (v2.1)
**AP Token**: `AP-CRISIS-BRIEF-v2.1.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ BRIEFING
**Date**: 2026-07-10 | **For**: Kali (Grand Oversight) | **Spec**: `SEMANTIC_RESONANCE_CRISIS_MATRIX.md` (v2.1)

---

## 1. What Exists Today (the honest answer: almost nothing for *inbound* crisis)

Omega has **content-safety** but **no distress-recognition**. Three real systems:

- **`omega-vetala`** (ex `omega-moderation`) — `omega-moderation/omega_moderation/__init__.py:8`.
  Local-first ML toxicity/obfuscation detection, 124 tests, **explicitly no slur lists**.
  It judges *whether text is harmful* — it does **not** recognize a *human in pain*.
- **`TDPGate`** — `src/omega/oracle/oracle.py:392`. Isolates tainted external input.
  A security boundary, not a compassion layer.
- **`SemanticRouter`** — `src/omega/oracle/semantic_router.py:30`. Already does
  embedding→cosine routing (threshold 0.4) to *entities*. This is the **exact primitive**
  to reuse; Crisis Matrix = a second index of *crisis states* on the same cosine math.

No `soul.yaml` (of 30) encodes a crisis L3 principle. Crisis handling is **net-new**.

---

## 2. Strategy & Philosophy

Current safety = **refuse/isolate outbound harm**. The gap = **inbound empathy**. The
2026 "Alignment Paradox" (futureagi.com, 2026-05-20) proves over-refusal is a live harm:
heavily aligned models refuse 25–40% of benign queries. A distressed user met with
"I can't help" is abandoned. **Semantic Resonance** flips the model: detect distress
semantically, route to an *empathetic* entity/module, reserve hard refusal for outbound
harm (vetala's lane). Refusal ≠ compassion.

---

## 3. How Semantic Resonance Enhances (not replaces)

- **Reuses** `EmbeddingManager` (`embeddings.py:22`) + `_cosine_similarity`
  (`semantic_router.py:30`) — zero new embedding infra, local-first (M7).
- **Pre-filter** in `oracle.talk()` at `oracle.py:396`, *before* Iris decode — a routing
  hint, never a hard block. Prompt still reaches an entity, just empathy-tuned.
- **Fuses** with vetala as a *second axis*: vetala = outbound safety; Crisis Matrix =
  inbound empathy. High vetala-toxicity + high C1 = user *describing* harm (not target).
  Crisis routing must NOT be suppressed by vetala.
- **7-state taxonomy** (C1 self-harm … C7 hopelessness), acute vs chronic, existential vs
  practical — grounded in PLOS Digital Health 2026-05-13 multi-label hotline detection.

---

## 4. Key Risks + Mitigations (updated with 2026 research)

| Risk | Severity | Mitigation |
|------|----------|------------|
| **False negative** (missed C1 self-harm) | 🔴 CRITICAL | Acute states (`escalate_human=True`) ALWAYS inject local resource list (988/regional). Never let model "resolve" acute risk. |
| **False positive** (philosophy query → crisis module) | 🟡 HIGH | Threshold 0.55 (> entity 0.4); ambiguous band 0.45–0.55 → general empathetic entity, no lock-in. Avoids over-refusal trap. |
| **Cloud dependency** | 🔴 BLOCKER | Local `qwen-embedding`/`embedding-gemma` only. Hashing fallback disabled for crisis (`semantic_router.py:106`). M7/M8. |
| **AI oversteps clinical role** | 🔴 CRITICAL | Iris Telehealth 2026: 73% demand human control. Module acknowledges + connects + stays present; never asserts "you're safe." |
| **Slur-list creep** | 🟡 MED | Seeds are natural-language *anchors*, not lexical lists (mirrors vetala `__init__.py:8`). |
| **Audit/accountability** | 🟡 MED | Acute escalations → ZONEID Merkle audit (reuse `omega-vetala` `governance/audit.py`, `HERITAGE_VET_LOG.md:73`). |

---

## 5. NEW GAPS FOUND & FILLED (since v1)

### 5.1 Multilingual crisis detection
**Gap**: Crisis doesn't arrive in English. Current embedding chain (Gemma→Ollama→MiniLM→Static→Hash) has **zero cross-lingual models**.
**Fill**: **Qwen3-Embedding** (0.6B/4B/8B, 100+ languages, Apache 2.0, `arxiv.org/pdf/2506.05176`) runs locally via llama-cpp-python (same loader as `LocalGGUFEmbeddingProvider`, `embeddings.py:149`). Add to `EmbeddingManager` chain (Horizon 2). Seeds authored in EN + top-5 user languages; cross-lingual cosine transfers per Qwen3 MMTEB scores. No cloud call → M7 holds.

### 5.2 Over-refusal mitigation (2026 research)
**Gap**: v1 had threshold + ambiguous band but no theoretical grounding.
**Fill**: **LLM-VA** (Zhang et al., ACL 2026, `aclanthology.org/2026.acl-long.260/`) proves `va` (willingness-to-respond) ⊥ `vb` (input-safety) in aligned LLMs. Our two-axis split is the *pre-response* analogue: Crisis Resonance ⊥ vetala. Coupling them (so response depends on safety) causes the jailbreak↔over-refusal trade-off. **Orthogonality is the design principle.**
Additional mitigation: **ACTOR** / **Deactivating Refusal Triggers** (Xue et al., TrustNLP 2026, `aclanthology.org/2026.trustnlp-main.26/`) show refusal triggers are linguistic cues; over-refusal from non-harmful cues → ambiguous band + no lexical slur lists is the correct defense.

### 5.3 Legal/ethical guardrails (2026 litigation landscape)
**Gap**: v1 mentioned "duty to warn" but lacked concrete 2026 case law.
**Fill**: **Tarasoff-in-AI** (`globalcybersecurityreport.com/.../tarasoff-meets-the-ai-age`, 2026-04-21) + **OpenAI/Character.AI lawsuits** (Tumbler Ridge, FSU shootings, `news.bloomberglaw.com/.../chatgpt-linked-mass-shootings-drive-developer-liability-concerns`, 2026-05-13) establish:
- Courts treat chatbots as **products** (failure-to-warn, foreseeability), not speakers.
- NY + CA companion-bot laws **require** crisis detection + referral + human-disclosure.
- Acute escalation MUST be **code-enforced**, not policy — omission = foreseeable product failure.
- Audit trail (§8) is the liability shield; document every acute decision.
- Minors: CA SB 243 requires minor notification/reporting → `region`/`age` in `escalation_contacts`.

### 5.4 Empathetic response scaffolding
**Gap**: v1 had no response strategy for the crisis module.
**Fill**: **STRIDE-ED** (Ji et al., ACL 2026, `arxiv.org/html/2604.07100v3`) — 14-strategy system (restatement→cognitive reframing); multi-stage reasoning (Summary→Emotion→Strategy→Action→Response) usable as module prompt scaffold. SOTA emotion accuracy 57.25%, generalizes across Qwen3/Llama3.2.

### 5.5 White-box safety eval (SafeVec/RAS)
**Gap**: v1 mentioned "representation-level" but didn't assess feasibility.
**Fill**: **SafeVec/RAS** (Huang et al., 2026-06-24, `arxiv.org/html/2606.25750v1`) measures safety from hidden states (refusal directions). **Requires white-box access → NOT usable on local GGUF** (llama-cpp-python doesn't expose residual stream). Defer to Horizon 3 *if* hidden-state access becomes available.

### 5.6 Clinical consensus mapping
**Gap**: v1 had C-SSRS levels but no 2026 clinical consensus.
**Fill**: **Khazanov Delphi Consensus** (2026-06-21, `osf.io/txpem_v1`) — validation/support + coping at low risk; **encouragement to reach human providers appropriate at ALL risk levels**; crisis-resource connection at higher risk; direct contact-outreach at high risk (more for youth). Maps cleanly to our acute/chronic escalation logic.

---

## 6. Recommended Next Step for Kali

Ratify **Horizon 1** of the spec: a local, contract-tested `CrisisResonanceFilter`
reusing existing embedding + cosine primitives, wired as an `oracle.talk()` pre-filter,
with **acute-state human-escalation enforced by code, not policy**. Do NOT modify core
engine WAD logic — ship as OMS module per D207 (`PIVOT_LOG.md`).

---

## 7. Citations (local + web)

**Local**: `omega-moderation/omega_moderation/__init__.py:8` · `src/omega/oracle/semantic_router.py:30,80,106,201` · `src/omega/memory/embeddings.py:22,40,149,349` · `src/omega/oracle/oracle.py:392,396,449` · `data/entities/verity/proposed_lessons.yaml` · `docs/decisions/PIVOT_LOG.md` D207 · `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md:73`

**Web (2026)**:
- futureagi.com/alignment-paradox-llm-safety-2026
- partnershiponai.org/.../how-ai-companies-are-handling-suicide-and-self-harm-today/
- osf.io/txpem_v1 (Khazanov Delphi C-SSRS 5-level)
- arxiv.org/abs/2605.04321 (Saltz & Leibowicz cross-sector primer)
- library.samhsa.gov/.../pep24-01-037.pdf (SAMHSA Crisis Care Guidelines)
- arxiv.org/html/2604.07100v3 (STRIDE-ED 14-strategy empathetic reasoning)
- arxiv.org/html/2606.25750v1 (SafeVec/RAS white-box safety)
- aclanthology.org/2026.acl-long.260/ (LLM-VA orthogonality proof)
- openreview.net/pdf?id=TiYOHdK35L (ACTOR over-refusal mitigation)
- aclanthology.org/2026.trustnlp-main.26/ (Deactivating Refusal Triggers)
- arxiv.org/pdf/2506.05176 (Qwen3-Embedding 100+ languages)
- medrxiv.org/content/10.64898/2026.01.12.26343914v1 (LLM crisis-risk detection)
- globalcybersecurityreport.com/.../tarasoff-meets-the-ai-age (Tarasoff-in-AI)
- torhoermanlaw.com/ai-lawsuit/can-you-sue-for-ai-assisted-suicide/ (product liability)
- iristelehealth.com 2025-09-17 (73% human control, 8% AI trust)
- news.bloomberglaw.com/.../chatgpt-linked-mass-shootings-drive-developer-liability-concerns (OpenAI lawsuits)
- theconversation.com/should-ais-be-required-to-report-a-human-user-contemplating-violence-282561 (Tarasoff framework for AI)

---

*End of briefing. Spec v2.1 at `data/coordination/SEMANTIC_RESONANCE_CRISIS_MATRIX.md` contains full architectural detail, data contracts, compliance mapping, and 3-horizon roadmap.*