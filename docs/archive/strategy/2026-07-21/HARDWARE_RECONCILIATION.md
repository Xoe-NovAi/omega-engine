# 🔱 Hardware-Software Reconciliation (HSR)
**AP Token**: `AP-HSR-v1.0.0`
⬡ OMEGA ⬡ MALKUTH ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_grounding ⬡ HARDWARE

## 💻 Physical Specifications
- **CPU**: AMD Ryzen 7 5700U (8C/16T, Zen 2)
- **Physical RAM**: 14GB
- **zRAM Swap**: 8GB (Compressed)
- **Effective Memory Pool**: ~22GB

## 🚦 Resource Zones (The Pulse)
The `SystemResource` module monitors the system and triggers the following behaviors:

| Zone | Range | State | Action |
|------|-------|--------|---------|
| **Green** | 0 - 14GB | Optimal | Full local model residency allowed. |
| **Yellow** | 14 - 18GB | Pressure | zRAM active. Trigger "Soft Eviction" of background models. |
| **Red** | 18GB+ | Critical | Force-escalate all new requests to Cloud (Gemma 4-31B). |

## 🌐 Hybrid Inference Strategy
- **Cloud Track (Gemma 4-31B)**: Parallel instances allowed. RAM-negligible.
- **Local Track (GGUF/Iris/Qwen)**: Managed by `ResourceGuard`.
    - **Iris**: Always-on (Podman).
    - **Background Models**: Allowed if `Total_Local_RAM < 14GB`.
    - **Routing**: Iris triggers larger local models only if headroom exists or lower-priority models are evicted.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
