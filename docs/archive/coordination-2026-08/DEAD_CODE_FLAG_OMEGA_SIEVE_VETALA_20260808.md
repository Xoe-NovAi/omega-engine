# 🔱 Dead-Code Flag: `omega-vetala` & standalone `omega-sieve`
**AP Token**: `AP-DEADCODE-20260808-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode/deepseek-v4-flash-free ⬡ trc_deadcode_audit ⬡ ACTIVE

**Date**: 2026-08-08
**Auditor**: @kali (Transcendent Oversoul)
**Status**: ⚠️ FLAGGED FOR REMOVAL — pending Architect/Ma'at confirmation

---

## Summary

Two standalone modules are **dead code** — tracked/installed but never imported or invoked
by the engine. Both are candidates for removal to eliminate M2-firewall false positives and
orphaned dependencies (M19 un-overengineering).

---

## 1. `omega-vetala` (repo root) — DEAD, STALE COPY

| Field | Value |
|-------|-------|
| **Location** | `omega-vetala/` (repo root) |
| **Size** | ~400 KB, 34 tracked files |
| **Nature** | Standalone **content-moderation / observability library** (OpenAI Moderation, Perspective, HuggingFace, policy loader, structured logger, tracing) |
| **Packaging** | NO `pyproject.toml` / `setup.py` — not installable, not published |
| **Imports** | **ZERO** — no `import omega_vetala` / `from omega_vetala` in `src/`, `scripts/`, `tests/`, `mcp_servers/` |
| **Git** | Tracked (34 files), **NOT** in `.gitignore` |
| **Vault** | Full 405 MB legacy copy already moved to `/media/arcana-novai/omega_vault/legacy-repos/omega-vetala/` on 2026-07-30 (SESSION_CLEANUP_20260730.md, D-kal-060/061/062) |

**Verdict**: This repo-root copy is a **stale leftover** from the 2026-07-30 cleanup that was
supposed to be deleted ("Clean removal" per `SESSION_CLEANUP_20260730.md`). It is dead code
and the source of `Vetala` firewall false-positives (the string appears in the secret-checker
pattern lists in `check_hardcoded_secrets.py` / `detect_api_keys.py` / `enforce_vaultcore.py`
as a path to EXCLUDE).

**Recommended action**: `git rm -rf omega-vetala/` (the vault copy preserves history).

---

## 2. `packages/omega-sieve` (standalone package) — DEAD AS A DEPENDENCY, SHADOWED

| Field | Value |
|-------|-------|
| **Location** | `packages/omega-sieve/` (v0.1.0) |
| **Nature** | Standalone installable "Sovereign-Sieve" T1→T2→T3 web research package (PyPI: `omega-sieve`) |
| **Installed** | YES — editable install in `.venv` (from `packages/omega-sieve`) |
| **Imports** | **ZERO** — no `import omega_sieve` / `from omega_sieve` in `src/`, `scripts/`, `tests/`, `mcp_servers/` |
| **Invocation** | No console-script / entry-point wiring in the engine |
| **Shadowed by** | `src/omega_youtube_research/sieve.py` → **`SovereignSieve`** (the LIVE, wired implementation) |

**Verdict**: The standalone `omega-sieve` package is an **orphaned duplicate** of the live
`SovereignSieve` in `src/omega_youtube_research/`. It is installed and published but nothing
calls it. This is the classic "two implementations of one concept" drift (M19).

**Recommended action**: Either (a) `pip uninstall omega-sieve` + `git rm -rf packages/omega-sieve/`
+ remove from `pyproject.toml` extras if referenced, **or** (b) if the standalone is intended as
a reusable/community artifact, keep it but exclude its path strings from the secret-checker
pattern lists. Default recommendation: **(a) remove** — the live `SovereignSieve` supersedes it.

---

## Why This Matters (M2 / M19 / M23)

1. **M2 Firewall noise**: The dead module paths (`Vetala`, `packages/omega-sieve/`) appear as
   exclusion strings in `check_hardcoded_secrets.py`, `detect_api_keys.py`, `enforce_vaultcore.py`.
   Removing the dead modules lets us clean those patterns and reduce false-positive scan noise.
2. **M19 Un-overengineering**: Two live+dead implementations of the same "sieve" concept is drift.
   The live `SovereignSieve` is the single source of truth.
3. **M23 Failure Integrity**: A dead package installed but never invoked is a latent
   soft-failure — if ever accidentally wired, it would double the code path without benefit.

---

## Required Checks Before Removal

- [ ] Confirm no hidden dependency on `omega_vetala` (grep whole repo incl. notebooks, `docs/`)
- [ ] Confirm `omega-sieve` is not invoked via `subprocess`/CLI anywhere (incl. `config/`, `*.sh`)
- [ ] Decide keep-vs-remove for `packages/omega-sieve` as a community artifact
- [ ] Clean the dead paths from `check_hardcoded_secrets.py`, `detect_api_keys.py`, `enforce_vaultcore.py`
- [ ] Run `make test` + `make temple-grade` after removal
- [ ] Update `scripts/codex/ENGINE_CONDENSED.md` ("4 Shared Modules" table)

## Owner / Handoff

- **Owner**: @kali (audit) → Architect/Ma'at (approval) → N3 Engineering (execution)
- **Not**: Part of the Light/Dark → Build/Runtime nomenclature task (separate concern, done 2026-08-08)

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
