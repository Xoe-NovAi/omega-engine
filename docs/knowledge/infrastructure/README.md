# 🔱 Knowledge Base: Infrastructure
**AP Token**: `AP-KB-INFRA-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Infrastructure and deployment operational wisdom for the Omega Engine.

---

## Purpose

This directory contains hard-won knowledge about deploying and operating the Omega Engine infrastructure — Podman containers, Redis, Qdrant, PostgreSQL, and system-level configuration.

## Contents

- `PODMAN_ROOTLESS.md` — Rootless Podman setup and gotchas
- `CONTAINER_HARDENING.md` — Security hardening for Quadlets
- `MODEL_STORAGE.md` — GGUF model management and storage
- `SYSTEMD_SERVICES.md` — Service management and health checks
- `DISK_MANAGEMENT.md` — Partition management and cleanup

## Contributing

When you solve an infrastructure problem, document the solution here. Focus on:
- **The exact commands** that worked
- **What went wrong** before finding the solution
- **System-specific details** (hardware, OS, kernel version)

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
