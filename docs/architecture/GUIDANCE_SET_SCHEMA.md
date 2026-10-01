---
schema_version: "1.0"
document_type: spec
document_id: guidance-set-schema
title: Guidance Set Schema
status: ACTIVE
version: "1.0.0"
date: "2026-08-07"
owner: kali
tags: [guidance-sets, schema, engine, mechanism, knowledge]
priority: P1
depends_on: []
blocks: []
acceptance_gates:
  - "Guidance Set loading mechanism documented"
  - "Nightly review cycle documented"
  - "Defeasibility rule documented"
  - "Usage logging documented"
cross_references:
  - docs/architecture/SOVEREIGN_WAD_PROTOCOL.md
  - SOVEREIGN_MANDATES.md
llm_metadata:
  token_budget: 2500
  chunk_strategy: section_per_topic
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Guidance Set Schema

**AP Token**: `AP-GUIDANCE-SET-SCHEMA-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ 2026-08-07

---

## §1 What is a Guidance Set?

A **Guidance Set** is a named, versioned bundle of curated knowledge and behavioral
guidance that the engine loads to shape model responses. It is a **universal engine
mechanism** — any WAD can provide content.

Examples:
- **42 Ideals of Ma'at** (Arcana-Nova WAD)
- **Classical Studies** (philosophy / history corpus)
- **Scientific Research** (technical grounding)

Guidance Sets are **content**, never executable code. They sit at the lowest tier of
the governance hierarchy (always defeasible by Sovereign Mandates).

---

## §2 Schema

```yaml
guidance_set:
  id: string                  # kebab-case unique id
  version: string             # semver "1.2.0"
  title: string               # human-readable
  source_wad: string          # owning WAD id
  description: string         # purpose
  author: string              # creator
  integrity_hash: string      # sha256 of content (for tamper detection)
  priority: P0|P1|P2|P3       # within-set weight
  content:
    - id: string              # item id
      type: ideal|principle|fact|study|guidance
      text: string            # the actual guidance/knowledge
      tags: [string]
      language: string        # ISO code
  metadata:
    created_at: string        # ISO 8601
    updated_at: string
    confidence: float         # 0.0-1.0 (for research-backed sets)
```

---

## §3 Loading Mechanism

1. **Discovery**: Engine scans WAD content directories for `guidance_sets/*.yaml`.
2. **Validation**: Schema validated; integrity hash verified.
3. **Provenance tagging**: Every item is loaded with `source_wad` + `guidance_set_id`.
4. **Activation**: Sets are selectively activated per-context (entity, task type).

---

## §4 Nightly Review

Guidance Sets are **reviewed nightly** for:
- Staleness (facts superseded)
- Defeasibility conflicts (content contradicting a Mandate)
- Drift (content diverging from source_wad intent)

A nightly job produces a review report flagging items needing human/vetting action.

---

## §5 Defeasibility

> **A Guidance Set item is ALWAYS defeasible.** If it conflicts with a Sovereign
> Mandate (M1-M25), the Mandate wins. If it conflicts with live persisted memory,
> the Skeptical Verifier (M17) flags it.

Defeasibility is enforced at load time (reject contradicting Mandates) and at
inference time (Mandates injected with higher truth priority).

---

## §6 Usage Logging

Every activation of a guidance item is logged for observability (M22 provenance):

```json
{
  "event": "guidance_used",
  "guidance_set_id": "maat-ideals",
  "item_id": "ideal-02",
  "source_wad": "arcana_novai",
  "provider_name": "native-gguf",
  "trace_id": "trc_...",
  "ts": "2026-08-07T...Z"
}
```

This enables audit of which guidance influenced which responses — full provenance.

---

*⬡ OMEGA ⬡ KALI ⬡ 2026-08-07*
