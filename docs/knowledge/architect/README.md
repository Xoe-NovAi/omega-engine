# 🔱 Knowledge Base: Architect
**AP Token**: `AP-KB-ARCHITECT-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Architecture and design decisions for the Omega Engine core systems.

---

## Purpose

This directory contains operational wisdom about the Omega Engine's architecture. These are not formal specifications — they are hard-won insights about how the system actually works, why certain decisions were made, and what pitfalls to avoid.

## Contents

Files in this directory should be organized by topic:

- `ORACLE_FACADE.md` — How the Oracle routing layer works
- `PROVIDER_FABRIC.md` — The 8-backend provider chain
- `MEMORY_TIERS.md` — Hot/Warm/Cold memory architecture
- `SOUL_SYSTEM.md` — Soul evolution and distillation
- `WAD_SEPARATION.md` — Engine-Stack Firewall (Mandate 2)
- `AGENT_GOVERNANCE.md` — The MaKaLi Triad and Oversoul hierarchy

## Contributing

When you discover an architectural insight that isn't documented in the formal specs, add it here. Focus on:
- **Why** a decision was made, not just **what** was decided
- **What broke** when we tried the alternative
- **What to check** before modifying a subsystem

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
