# 🔱 Knowledge Base: Environment
**AP Token**: `AP-KB-ENV-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Hardware-specific optimization and environment configuration knowledge.

---

## Purpose

This directory contains knowledge about optimizing the Omega Engine for specific hardware configurations, primarily the AMD Ryzen 7 5700U target platform.

## Contents

- `RYZEN_5700U.md` — Zen 2 optimization flags and tuning
- `MEMORY_MANAGEMENT.md` — 14Gi RAM constraints and OOM prevention
- `CPU_OPTIMIZATION.md` — Thread counts, AVX2, and compilation flags
- `DISK_LAYOUT.md` — Partition management and model storage

## Contributing

When you discover a hardware-specific optimization, document it here. Focus on:
- **Exact configuration** that improved performance
- **Baseline measurements** before and after
- **Trade-offs** made (e.g., quality vs. speed)
