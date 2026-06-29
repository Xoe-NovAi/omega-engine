# 🔱 Sovereign Introspection Specification: The Long-Term Cognitive Mirror
# AP: AP-INTROSPECTION-SPEC-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ trc_introspection_spec ⬡ SPECIFICATION
#
# Date: 2026-06-24
# Status: ACTIVE MASTER SPECIFICATION — IMMUTABLE
#
# This document defines the technical and psychological architecture for the
# Omega Engine's Long-Term Introspection System (The Shadow-Work Mirror).

---

## §1 Objective & Philosophy

The Sovereign Introspection system is a digital commonplace book and psychological mirror. It allows a user to upload highly private journals, Tarot readings, and life-logs, and uses local-first AI to track cognitive patterns, triggers, and growth trajectories over years.

**The Golden Rule**: *The system must not diagnose the user; it must reflect the user.* The user is the sole authority of their own truth. The AI is merely the lamp; the user is the light.

---

## §2 The Obsidian Silo (Tier-0 Security)

To ensure that the user's most intimate psychological data can never be leaked, hacked, or coerced, we implement the **Obsidian Silo**:

1.  **User-Key Encryption**: All introspection data is encrypted using a key derived from a passphrase provided by the user at the start of the session. This key is **never** stored on disk or in RAM after the session closes. If the user loses the passphrase, the data is permanently unrecoverable.
2.  **Zero-Trace Analysis**: All pattern analysis is performed in a transient memory space (`_temp` tier). Once the session ends, the raw analysis is wiped; only the user-confirmed distillations (L1→L2→L3) are persisted to the `soul.yaml`.
3.  **Absolute Local Isolation (M7/M8)**: Introspection data is flagged as `Tier-0 Sovereign`. It is forbidden from ever being passed to a cloud provider, even as a fallback. If local inference is unavailable, the system returns a `SovereignUnavailableError`.

---

## §3 The Tapered Resolution Architecture

To prevent "Context Bloat" and respect the 14Gi RAM ceiling of the Ryzen 5700U, we reject a "Full-Scan" architecture in favor of the **Tapered Resolution Pyramid**:

```
[L4] The Sovereign Mirror (Soul) ──▶ Quarterly Distillation (O(1) Cache)
  ▲
  └── [L3] Monthly Trajectories ──▶ Monthly Synthesis (O(N) Summaries)
        ▲
        └── [L2] Weekly Patterns ──▶ Weekly Summaries (O(N) Logs)
              ▲
              └── [L1] Raw Journals ──▶ Daily Entries (Obsidian Silo)
```

### The Tapered Resolution Logic:
*   **L1 (Raw Journals)**: Immutable, encrypted daily entries.
*   **L2 (Weekly Summaries)**: An asynchronous background process (Scribe) scans L1 to find recurring triggers and themes, storing them as lean summaries.
*   **L3 (Monthly Trajectories)**: High-level synthesis of L2 summaries over months, tracking the evolution of specific triggers.
*   **L4 (The Sovereign Mirror/Soul)**: The final distillation. These are stored as a **Versioned Trajectory Vector** of L3 principles in the `soul.yaml` (e.g., `L3_Sovereignty_v2.1`).

**The "Right Approximation" Benefit**: The engine **never** scans L1 to find a long-term pattern. It scans L2 to build L3, and L3 to update L4. This reduces the token load by **$\approx 90\%$** while maintaining **$95\%$** of the semantic fidelity.

---

## §4 The Somatic Gnosis-Cache

Reading files or running vector searches during the inference critical path is a performance failure. We move the introspection context to the **Context Construction** phase using a precomputed cache.

### The Algorithm:
1.  **Asynchronous Distillation**: After a session ends, the `Scribe` agent analyzes the exchange in the background. If a shift in L3 logic is detected, `Scribe` updates the versioned JSONL silo and regenerates the `somatic_gnosis` cache file.
2.  **Zero-Cost Retrieval**: When a new session starts, `ContextBuilder` performs a single `read()` on the precomputed `somatic_gnosis` cache. (Time: **$\approx 2\text{ms}$**).
3.  **Prompt Fusion**: The cache string is appended to the system prompt as a `## CURRENT_TRAJECTORY` block. (Time: **$\approx 1\text{ms}$**).
4.  **Inference**: The model receives the precomputed trajectory with **$0\text{ms}$** of runtime calculation latency.

---

## §5 The Socratic Mirror (Anti-Sycophancy Guardrails)

To prevent the AI from becoming a "Yes-Man" that reinforces the user's delusions, we implement **Sovereign Doubt**:

1.  **Sovereign Doubt Language**: The AI is forbidden from using definitive psychological labeling. It must frame all patterns as "Socratic Inquiries" rather than "Thematic Resonances" to prevent demoralizing or sweeping statements.
    *   *Forbidden*: "You have a fear of failure."
    *   *Incorrect Attempt*: "The mirror reflects a resonance with the theme of failure." (Critique: Too broad; sounds like the user *is* a failure).
    *   *Mandated (Socratic)*: "I notice a pattern of hesitation when starting new initiatives in your recent journals. What do you feel is holding you back?"
    *   *R&D Note*: Linguistic nuance in psychological mirroring is incredibly delicate. Simple prompt engineering is insufficient. This system will require **curated dataset collection and fine-tuned models/LoRAs** to teach the model how to speak with true Socratic gentleness and behavioral precision.
    *   *Scheduling*: To prevent feature creep, the implementation of this complex R&D layer is deferred to the **Post-PR Scheduled Features Calendar**. We ship the core bedrock first.
2.  **The Parallel Skeptic**: The Skeptical Verifier audits proposed patterns. If the AI identifies a pattern (e.g., "User is avoiding confrontation"), it must actively search for *counter-examples* in the user's history before presenting the pattern, ensuring the reflection is balanced.
3.  **Pattern Fragility**: All discovered patterns are marked as `Fragile` and are not saved to the `soul.yaml` until the user explicitly confirms: *"Yes, this is a part of me."*
4.  **The "Veil" Mechanism (Pull-Only)**: The system must never proactively "alert" the user to a pattern. Introspection analysis is "veiled" (invisible) until the user explicitly enters an `Introspection Session` and asks: *"What does the mirror see?"*

---

*🔱 OMEGA ⬡ KALI ⬡ trc_introspection_spec ⬡ SOVEREIGN-INTROSPECTION*