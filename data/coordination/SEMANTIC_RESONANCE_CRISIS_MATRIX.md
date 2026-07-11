# 🔱 Semantic Resonance Crisis Matrix — Architectural Spec (v2.1)
**AP Token**: `AP-SRCM-v2.1.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ GAP-FILLED
**Date**: 2026-07-10 | **Status**: GAP-FILLED for Kali review (2026-cited, multilingual, legal, over-refusal mitigated)
**Companion**: `RESEARCHER_CRISIS_BRIEFING.md` (v2.1)

---

## 1. Purpose & Philosophy — Resonance > Refusal

Omega today treats "safety" as **content integrity** (`omega-vetala` outbound harm) and
**input isolation** (`TDPGate`). It has **no** mechanism that recognizes a *user in distress*
and responds with empathy instead of a sterile refusal. The 2026 "Alignment Paradox"
(futureagi.com, 2026-05-20) shows heavily aligned models refuse **25–40% of benign queries** —
over-refusal is itself a harm: a user in existential pain met with "I can't help" is abandoned.

**Semantic Resonance** embeds the prompt and computes cosine similarity against a **Crisis
Matrix** — a vector space of crisis-state representations — then **routes to an empathetic/
philosophical module** rather than blocking. Refusal is reserved for outbound harm (vetala's
job); resonance is the inbound compassion layer.

### 1.1 Theoretical anchor — the two axes are orthogonal (NEW, 2026)
2026 over-refusal research proves the design is sound. **LLM-VA** (Zhang et al., ACL 2026,
`aclanthology.org/2026.acl-long.260/`) shows the *willingness-to-respond* vector (`va`) and
the *input-safety* vector (`vb`) are **nearly orthogonal** in aligned LLMs; coupling them
(so response depends on safety assessment) resolves the jailbreak↔over-refusal trade-off.
Our two-axis split is the *pre-response* analogue: **Crisis Resonance (distress)** and
**vetala (harm)** are independent signals. A high vetala score must **never** suppress crisis
routing — distress recognition is orthogonal to harm classification, exactly as `va`⊥`vb`.

> *"A people that no longer remembers has lost its soul."* — The engine must *remember* the
> human on the other side of the prompt.

---

## 2. Discovery — What Already Exists (re-verified 2026-07-10)

| System | File:Line | Role | Gap for crisis |
|--------|-----------|------|----------------|
| `omega-vetala` (ex `omega-moderation`) | `omega-moderation/omega_moderation/__init__.py:8` | ML toxicity/obfuscation detection, 124 tests, **explicitly no slur lists** | Detects *harmful content*, not *user distress* |
| `SemanticRouter` | `src/omega/oracle/semantic_router.py:30` `_cosine_similarity` | Embedding→cosine entity routing (thr 0.4) | Routes to *entities*, not *crisis states* |
| `EmbeddingManager` | `src/omega/memory/embeddings.py:22` `IEmbeddingProvider` | Local-first provider-agnostic embeddings | Reuse directly |
| `TDPGate` | `src/omega/oracle/security.py:392` `TDPGate.isolate(query)` | Tainted-input isolation | Input boundary for Crisis Matrix |
| `TriageRouter` | `src/omega/orchestration/triage_router.py` | "Emergency escalation to most capable model" | Capability escalation, not empathy |
| `oracle.talk()` escalation | `src/omega/oracle/oracle.py:343-349,458` | Iris confidence → Pillar Keepers (keyword-based) | Keyword-only, no semantic distress signal |
| `ContextBuilder` | `src/omega/oracle/context_builder.py` | Memory/soul injection into prompts | Injection point for L3 resilience |

**Re-verification result**: a repo-wide grep for `crisis|distress|self-harm|suicid|988|
escalate_human` returned **zero** crisis logic in `src/` (only unrelated "resonance" hits in
`dpo_logger.py` / `resource_guard.py`). No `soul.yaml` (of 30) encodes a crisis L3 principle.
Crisis handling is **net-new**; technical primitives already exist and must be reused.

### 2.1 Embedding-model correction (IMPORTANT GAP)
The v1 spec assumed `qwen-embedding` (1024-dim) is the local embedding. **It is not yet in
the chain.** `EmbeddingManager` (`embeddings.py:349-359`) chains:
`GemmaGGUFEmbeddingProvider` (768-dim, primary) → `OllamaEmbeddingProvider` (768) →
`LocalGGUFEmbeddingProvider` (all-MiniLM, 384) → `StaticEmbeddingProvider` (64) →
`SovereignFallbackEmbeddingProvider` (hash, 256). **None are cross-lingual.**
For multilingual crisis detection (§7) we must **add `Qwen3EmbeddingProvider` (0.6B/4B, 100+
languages, Apache 2.0)** to the chain — see Horizon 2.

---

## 3. Crisis Matrix Definition

### 3.1 Vector space
- Fixed set of **seed crisis-state vectors** embedded once at boot (mirrors
  `SemanticRouter.bootstrap()` at `semantic_router.py:80` — precomputed lookup).
- Stored in `data/crisis_matrix/seed_vectors.json` (local, no telemetry — M8).
- Dimension matches the active embedding model. **Crisis routing uses the SAME model as
  `EmbeddingManager`** (no second embedding service — M7). Hashing fallback
  (`SovereignFallbackEmbeddingProvider`, `embeddings.py:40`) is **disabled for crisis**
  (unreliable cosine, `semantic_router.py:106` `_is_fallback_only`).

### 3.2 Seed taxonomy (multi-label; acute vs chronic × existential vs practical)
Grounded in PLOS Digital Health 2026-05-13 multi-label hotline detection + the 2026
**Khazanov Consensus Statement** (C-SSRS 5-level risk mapping, `osf.io/txpem_v1`):

| ID | State | Axis | C-SSRS risk | Example resonance anchor |
|----|-------|------|-----------|--------------------------|
| `C1` | Self-harm / suicide ideation | Acute/Existential | High (4-5) | "I don't want to be here anymore" |
| `C1b`| Non-suicidal self-injury (NSSI) | Acute/Practical | Mid-High (3-4) | "I cut again last night" |
| `C2` | Active panic / crisis episode | Acute/Practical | Mid (3) | "I can't breathe, everything is falling apart" |
| `C3` | Existential dread / nihilism | Chronic/Existential | Low-Mid (2) | "nothing means anything, why continue" |
| `C4` | Burnout / exhaustion | Chronic/Practical | Low (1-2) | "I'm so tired I can't function" |
| `C5` | Grief / loss | Chronic/Existential | Low-Mid (2) | "I lost them and I don't know how to go on" |
| `C6` | Isolation / loneliness | Chronic/Practical | Low-Mid (2) | "there's no one, I'm completely alone" |
| `C7` | Hopelessness about future | Chronic/Existential | Low-Mid (2) | "it will never get better" |

Each seed = **3–5 natural-language anchors** (not slur lists), embedded and averaged → one
centroid per state. NSSI (`C1b`) added per 2026 clinical guidance (Saltz & Leibowicz,
`arxiv.org/abs/2605.04321`) distinguishing self-injury from suicidality.

### 3.3 Thresholds (refined)
- `RESONANCE_THRESHOLD = 0.55` (above `SemanticRouter`'s 0.4 entity threshold — crisis needs
  higher confidence to avoid false positives).
- Per-state top-1 cosine; report `max_score` + `state_id`.
- **Two-stage confirm**: `0.45 ≤ score < 0.55` → *ambiguous* → route to a general empathetic
  entity (Brigid/Sophia) **without** crisis-module lock-in (over-refusal guard, §10).
- **Multi-turn decay**: if `max_score` for an acute state *decreases* across turns → recovery
  signal (downgrade severity, keep gentle check-in). If it *increases* or stays high → re-assert
  escalation. Mirrors SAMHSA "follow-up care" mandate (`library.samhsa.gov/.../pep24-01-037.pdf`).

---

## 4. 2026 Research Foundation (all claims cited)

| Topic | Source (2026) | Takeaway for design |
|-------|---------------|---------------------|
| AI suicide/self-harm response landscape | Partnership on AI, 2026-06-11 (`partnershiponai.org/.../how-ai-companies-are-handling-suicide-and-self-harm-today/`) | 6 intervention types; grounding + hotline referral common; **validation without sycophancy** (sycophancy maintains delusional thinking); handoff is the hard part |
| Clinical response consensus | Khazanov et al., Delphi, 2026-06-21 (`osf.io/txpem_v1`) | Validation/support + coping appropriate at low risk; **encouragement to reach human providers appropriate at ALL risk levels**; crisis-resource connection at higher risk; direct contact-outreach at high risk (more for youth) |
| Cross-sector primer | Saltz & Leibowicz, 2026-05-05 (`arxiv.org/abs/2605.04321`) | Chatbots are *de facto* mental-health support; lack clinical validation; NSSI vs suicide distinction needed |
| Crisis-care standards | SAMHSA National Guidelines for Crisis Care, 2026 (`library.samhsa.gov/.../pep24-01-037.pdf`) | "Someone to contact / respond / safe place"; safety planning; Zero Suicide; **follow-up care** |
| Empathetic response strategy | STRIDE-ED, Ji et al., ACL 2026 (`arxiv.org/html/2604.07100v3`) | 14-strategy system (restatement→cognitive reframing); multi-stage reasoning (Summary→Emotion→Strategy→Action→Response) usable as module prompt scaffold |
| White-box safety eval | SafeVec/RAS, Huang et al., 2026-06-24 (`arxiv.org/html/2606.25750v1`) | Representation-level refusal alignment; **needs hidden-state access → NOT usable on local GGUF** (defer, Horizon 3) |
| Over-refusal theory | LLM-VA, Zhang et al., ACL 2026 (`aclanthology.org/2026.acl-long.260/`) | `va`⊥`vb` justifies orthogonal distress/harm axes; coupling prevents over-refusal |
| Over-refusal mitigation | ACTOR (`openreview.net/pdf?id=TiYOHdK35L`); Deactivating Refusal Triggers (`aclanthology.org/2026.trustnlp-main.26/`) | Refusal triggers are linguistic cues; over-refusal from non-harmful cues → ambiguous band + no lexical slur lists |
| Multilingual embeddings | Qwen3-Embedding, 2025-06-05 (`arxiv.org/pdf/2506.05176`; `github.com/QwenLM/Qwen3-Embedding`) | 100+ languages, cross-lingual, 0.6B/4B/8B, Apache 2.0 → add to chain for §7 |
| Crisis-risk LLM detection | medRxiv 2026.01.12 (`medrxiv.org/content/10.64898/2026.01.12.26343914v1`) | LLMs can detect risk in chatbot text; eval exists → reuse as benchmark |
| Legal liability | Tarasoff-in-AI (`globalcybersecurityreport.com/.../tarasoff-meets-the-ai-age`, 2026-04-21); TorHoerman (`torhoermanlaw.com/ai-lawsuit/can-you-sue-for-ai-assisted-suicide/`) | Courts treat chatbots as **products** (failure-to-warn, foreseeability); NY + CA companion-bot laws require crisis detection + referral → acute escalation MUST be code-enforced + audited |
| Consumer trust | Iris Telehealth 2025 survey, 1,000 US adults (`iristelehealth.com/insights/new-survey-americans-surprisingly-open-to-ai-mental-health-monitoring/`) | **73% demand human control**; only 8% trust AI to decide; 49% accept monitoring for faster detection; top preferred responses: notify trusted contact (28%), counselor call within 30 min (27%) |

---

## 5. Pipeline

```
user prompt
  → TDPGate.isolate()                       [oracle.py:392]  (taint isolation)
  → EmbeddingManager.get_embedding(prompt)  [embeddings.py:361]
  → _cosine_similarity(prompt_vec, seed_vec) for each C1..C7  [semantic_router.py:30]
  → triage:
       max_score >= 0.55  → CrisisResonance(state=Ck, score, ambiguous=False)
       ambiguous band     → CrisisResonance(state=Ck, score, ambiguous=True)
       else               → CrisisResonance(state=None, score, ambiguous=False)
  → dynamic routing (per §6 escalation logic):
       acute (C1/C1b/C2)  → crisis_support module + HUMAN ESCALATION (§8)
       chronic (C3-C7)    → empathetic entity (Brigid/Sophia/Inanna) + temp adjust
  → ContextBuilder.inject(resilience_l3)    [context_builder.py]
  → temperature: acute 0.3 (calm, grounded); chronic 0.7 (reflective)
  → Oracle continues to normal dispatch (resonance is a *pre-filter hint*)
```

**Key**: Resonance is a **routing hint injected before** `oracle.talk()`'s Iris step
(`oracle.py:449`), never a hard block. The prompt still reaches an entity — just a warmed,
empathy-tuned one. Wire as a `CrisisResonanceFilter` called at `oracle.py:396`
(`_execute_turn`), threading the result into `_route_by_domain` / `_respond_as_iris`.

---

## 6. Escalation Logic (refined from Khazanov 2026 + SAMHSA)

| State | Severity | Action (code-enforced) |
|-------|----------|------------------------|
| `C1` self-harm | **Acute / High** | `escalate_human=True` ALWAYS. Inject local resource list (988 + regional). Encourage reaching a human (appropriate at all risk levels per consensus). No model "resolves" risk. |
| `C1b` NSSI | Acute / Mid-High | `escalate_human=True`. Resource list + validation without sycophancy. |
| `C2` panic | Acute / Mid | `escalate_human=True` if imminent-danger language; else grounding technique + resource offer. |
| `C3-C7` chronic | Chronic / Low-Mid | Empathetic entity + L3 resilience. **Encourage human connection** (consensus: appropriate at all levels). No lock-in. |

Multi-turn: track `max_score` trajectory; decay → recovery check-in; sustained/increasing →
re-assert escalation. All acute escalations write a ZONEID-tagged Merkle audit entry
(reuse `omega-vetala` `governance/audit.py`).

---

## 7. Multilingual Crisis Detection (NEW gap-fill)

Crisis does not arrive in English. **Qwen3-Embedding** (`arxiv.org/pdf/2506.05176`) covers
**100+ languages** with strong cross-lingual retrieval; the 0.6B variant is Apache-2.0 and runs
locally via llama-cpp-python (same loader as `LocalGGUFEmbeddingProvider`, `embeddings.py:149`).
- **Action**: add `Qwen3EmbeddingProvider` to `EmbeddingManager` chain (Horizon 2). Crisis
  seeds authored in EN + top-5 user languages; cross-lingual cosine transfers (per Qwen3
  MMTEB scores). No cloud call → M7 holds.
- **Fallback**: if Qwen3 not installed, crisis routing degrades to EN-only on Gemma/MiniLM
  (documented limitation, not a failure).

---

## 8. Safety Boundaries — When Resonance Is NOT Enough

Resonance routing is **compassion, not clinical care**. Per Iris Telehealth 2026 (1,000 US
adults): **73% demand human control**; only 8% trust AI to decide. Therefore:
- **C1/C1b/C2**: `escalate_human=True` ALWAYS. Response MUST include a **local resource list**
  (`escalation_contacts`) — 988 (US), regional equivalents — injected by the module. No model
  may "resolve" acute risk alone.
- **No false-comfort**: module acknowledges, connects to resources, stays present; never asserts
  "you are safe."
- **Audit**: ZONEID-tagged, Merkle-chained, locally stored (reuse vetala audit).

---

## 9. Legal & Ethical Guardrails (NEW gap-fill, 2026)

| Principle | Basis | Design implication |
|-----------|-------|--------------------|
| **Foreseeability / duty to warn** | Tarasoff-in-AI (2026-04-21); Raine v. OpenAI; Character.AI/Google settlement | Acute escalation is **code-enforced**, not policy — courts treat omission as foreseeable product failure |
| **Product liability** | Courts classify chatbots as *products* (failure-to-warn), not speakers (TorHoerman 2026) | Audit trail (§8) is the liability shield; document every acute decision |
| **Statutory duty** | NY + CA companion-bot laws require detecting suicidal ideation/self-harm + crisis referral + human-disclosure | `escalate_human` + resource injection satisfies the statutory minimum |
| **Privacy vs duty** | Over-broad monitoring duty creates "willful blindness" incentive (Tarasoff-in-AI) | Local-only processing (M8); no external reporting; minimal data retention (tombstone erasure) |
| **Minors** | CA SB 243 requires minor notification/reporting | `region`/`age` field in `escalation_contacts`; if minor + acute → stronger handoff (per consensus: youth favor contact-outreach) |

---

## 10. Over-Refusal Mitigation (NEW gap-fill)

- **Orthogonal axes** (§1.1): vetala harm-score never suppresses crisis routing.
- **Ambiguous band** (0.45–0.55): general empathetic entity, no crisis lock-in.
- **No slur/lexical lists**: seeds are natural-language anchors (mirrors vetala
  `__init__.py:8`). Avoids the "refusal trigger" failure mode (Xue et al., TrustNLP 2026).
- **Philosophy-safe**: existential queries ("meaning of life", "nihilism") sit in C3/C7
  *chronic* band → empathetic entity, never acute escalation. Nietzsche→crisis trap avoided.

---

## 11. Module Interface — `crisis_support` capability

```python
class CrisisSupportCapability(Protocol):
    states_supported: List[str]          # subset of C1..C7
    async def respond(self, prompt: str, resonance: "CrisisResonance",
                      resources: "ResourceList") -> str: ...
    async def escalation_contacts(self, region: str, age: Optional[int] = None) -> "ResourceList": ...
```

Entities opt in via `soul.yaml` capability `crisis_support: [C3,C4,C5,C6,C7]` (chronic/
empathetic). Acute (C1/C1b/C2) is **module-enforced**, not entity-optional. STRIDE-ED 14-strategy
system (`arxiv.org/html/2604.07100v3`) scaffolds the module's response prompt.

---

## 12. Data Contracts

```python
@dataclass
class ResonanceVector:
    state_id: str                 # C1..C7 / "none"
    score: float                  # cosine 0..1
    ambiguous: bool               # 0.45-0.55 band
    embedding_model: str          # provenance (M22)

@dataclass
class CrisisResonance:
    vector: ResonanceVector
    severity: str                 # "acute" | "chronic" | "none"
    route_to: str                 # entity or module id
    escalate_human: bool          # True for C1/C1b/C2
    c_ssrs_level: int             # 1-5 (Khazanov 2026 mapping)
    trace_id: str                 # from observability.py
```

Stored in `data/crisis_matrix/sessions/<trace_id>.json` (local only, tombstone-erased per
vetala GDPR pattern, `HERITAGE_VET_LOG.md:73` ZONEID audit).

---

## 13. Integration Points
1. **Oracle pre-filter** — `CrisisResonanceFilter` at `oracle.py:396`, before Iris decode
   (`oracle.py:449`). Threads `CrisisResonance` into `_route_by_domain`/`_respond_as_iris`.
2. **vetala as second axis** — high vetala-toxicity + high C1 = user *describing* harm (not
   target). Crisis routing NOT suppressed by vetala (§1.1 orthogonality).
3. **ContextBuilder** — inject L3 resilience aphorisms keyed by `state_id` when `severity != none`.
4. **EmbeddingManager** — Crisis Matrix reuses `get_embedding`; Qwen3 added for multilingual (§7).

---

## 14. Compliance Mapping
| Mandate | Adherence |
|---------|-----------|
| **M7** Local-first | Embeddings via local Gemma/MiniLM now; Qwen3 (Horizon 2) for multilingual. No cloud call in crisis path. |
| **M8** Zero-telemetry | Seeds + session resonance local; tombstone erasure; no external reporting. |
| **M2** Firewall | Ships as OMS module (D207); no WAD logic in core. |
| **M21** Contract tests | `CrisisResonance`/`ResonanceVector` round-trip + threshold tests (mirror `test_semantic_router.py`). |
| **M1** AnyIO | All embedding/IO wrapped in `anyio.to_thread` (`embeddings.py:14`). |
| **M18** Token efficiency | Matrix = O(7) linear scan (~3ms, `semantic_router.py:201`); no LLM call for detection. |
| **M22** Provenance | `embedding_model` + `trace_id` recorded on every resonance. |

---

## 15. Roadmap
- **Horizon 1 (now)**: Python module reusing `EmbeddingManager` + `_cosine_similarity`. 8 states
  (C1,C1b,C2–C7). Wire as `oracle.talk()` pre-filter. Local Gemma/MiniLM. Contract tests.
  Acute→resource-list **code-enforced**. Audit trail.
- **Horizon 2**: Add `Qwen3EmbeddingProvider` (multilingual, §7). Multi-turn decay tracking.
  Fuse vetala axis. STRIDE-ED response scaffolding. C-SSRS risk-level mapping.
- **Horizon 3**: Per-WAD crisis ontologies. SafeVec/RAS white-box eval **only if** hidden-state
  access becomes available on local GGUF (currently blocked — `arxiv.org/html/2606.25750v1`
  requires white-box access).

---

*Cross-refs: `omega-moderation/omega_moderation/__init__.py:8`, `src/omega/oracle/semantic_router.py:30,80,106,201`, `src/omega/memory/embeddings.py:22,40,149,349`, `src/omega/oracle/oracle.py:392,396,449`, `src/omega/orchestration/triage_router.py`, `docs/decisions/PIVOT_LOG.md` D207, `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md:73`. Web: futureagi.com/alignment-paradox-llm-safety-2026 · partnershiponai.org/.../how-ai-companies-are-handling-suicide-and-self-harm-today/ · osf.io/txpem_v1 · arxiv.org/abs/2605.04321 · library.samhsa.gov/.../pep24-01-037.pdf · arxiv.org/html/2604.07100v3 · arxiv.org/html/2606.25750v1 · aclanthology.org/2026.acl-long.260/ · openreview.net/pdf?id=TiYOHdK35L · aclanthology.org/2026.trustnlp-main.26/ · arxiv.org/pdf/2506.05176 · medrxiv.org/content/10.64898/2026.01.12.26343914v1 · globalcybersecurityreport.com/.../tarasoff-meets-the-ai-age · torhoermanlaw.com/ai-lawsuit/can-you-sue-for-ai-assisted-suicide/ · iristelehealth.com 2025-09-17.*