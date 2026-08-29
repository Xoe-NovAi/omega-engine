---
schema_version: "1.0"
document_type: protocol
document_id: sovereign-wad-protocol
title: Sovereign WAD Protocol
status: ACTIVE
version: "1.0.0"
date: "2026-08-07"
owner: kali
tags: [wad, security, sandboxing, protocol, m2, prompt-injection]
priority: P1
depends_on: []
blocks: []
acceptance_gates:
  - "Prompt injection risk in WAD content documented with mitigations"
  - "Resource abuse sandboxing documented"
  - "Engine/WAD boundary preserved (M2)"
cross_references:
  - SOVEREIGN_MANDATES.md
  - src/omega/oracle/wad_loader.py
  - CREDITS.md
llm_metadata:
  token_budget: 2500
  chunk_strategy: section_per_topic
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Sovereign WAD Protocol

**AP Token**: `AP-SOVEREIGN-WAD-PROTOCOL-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ 2026-08-07

---

## §1 The Engine/WAD Boundary (M2)

> **Engine = Pure Runtime; WAD = Cosmology.**

The Engine (`src/omega/`, `config/omega.yaml`) is a universal, opinion-free runtime.
Each WAD (`config/wads/<stack>/`) supplies its own cosmology — entities, traits,
governance, guidance — via Base IWAD + PWADs.

**Users never fork core code.** They add layers. Third-party WADs are content, not code.

---

## §2 Threat Model for Third-Party WADs

WAD content is **attacker-controlled data** until reviewed. Threats:

| Threat | Vector | Severity |
|--------|--------|----------|
| **Prompt injection** | Entity trait text, guidance sets, governance rules instruct the model to bypass constraints | HIGH |
| **Resource abuse** | WAD declares huge models, excessive thread counts, malicious commands | MEDIUM |
| **Soul poisoning** | WAD overwrites entity soul/memory with adversarial content | HIGH |
| **Privilege escalation** | WAD references absolute paths / system commands outside sandbox | MEDIUM |

---

## §3 Security & Sandboxing Model

### 3.1 WAD Content is Data, Not Code
- WAD YAML/JSON is **validated** against schema on load (WAD Loader v2).
- WAD files are **never executed** — only parsed and consumed as configuration.
- Model *generation* from WAD-provided guidance is always bounded by Engine governance.

### 3.2 Input Sanitization
- Entity trait fields: strip control characters, cap length, reject embedded system-prompt delimiters.
- Guidance sets: treated as untrusted documents, marked in logs as `source: wad`.

### 3.3 Resource Quarantine
- Model choices resolved through `model_registry` allowlist — a WAD cannot name an arbitrary path.
- Thread count, batch size clamped to `config/hardware_profile.yaml` maxima.
- Path resolution goes through `PathResolver` allowlist (FS-B3, 77-entry semantic CI).

### 3.4 Review Gate
- Third-party WADs are reviewed before activation (human or verity audit).
- Signature/metadata checks (author, version, integrity hash) recorded on load.

---

## §4 Prompt Injection Mitigation

1. **Tag provenance**: Guidance from WADs is logged with `source: <wad_id>` — the model and audit trail know where each instruction came from.
2. **Defeasibility**: WAD guidance is always *below* Sovereign Mandates in the truth hierarchy (M1-M25 win every conflict).
3. **No auto-exec**: A WAD cannot instruct the engine to run commands, exfiltrate data, or touch other entities' souls.
4. **Skeptical Verifier**: Contradictions between WAD content and persisted memory are flagged (M17).

---

## §5 The 3-tier Governance Hierarchy

```
SOVEREIGN MANDATES (M1-M25)  ← highest, never overridable
   └── Engine governance (core config)
          └── WAD governance (per-stack)  ← lowest, always defeasible
```

WAD content can *customize* presentation, but can never *contradict* a Mandate.

---

*⬡ OMEGA ⬡ KALI ⬡ 2026-08-07*
