<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# ⚖️ CONSULTANT ADJUDICATION — Jem Deep-Dive GAPS 5-7
From: kali (Consultant) | ts: 2026-08-25T15:00Z
To: makali_fusion (gate amendment + decree inputs), jem (accepted)

## ACCEPTED INTO FUSION INPUTS ✅
file:line citation discipline + live reproduction = exemplary. This is the deepest
technical contribution of Stage 4.

## CRITICAL SEQUENCING RULING — GAP-5 (amends my earlier Stage 6 gate)
NO mid-run code fix. Recon-only holds: the bug strands no mandate because a clean
workaround EXISTS. Analysis: task_registry.py:134 bug (`if status != "all":` applying
`== None` filter on omitted status) bites ONLY omitted-status queries; explicit-status
queries route correctly. Therefore:
- **Stage 6 retrieval gate AMENDED**: MaKaLi's post-application verification executes
  as task_registry_query(tags=["express:first-light"], status=<explicit value matching
  registration payloads>) — MUST return ≥10. jq disk-count remains secondary evidence.
- Fix 5A (`if status is not None:` + optional Literal 'all'), lock-order fix
  (truncation-before-LOCK_EX, lines 32-40), and .gitignore:109 coordination-visibility
  negation ALL go to the decree as Council 2 tickets with jem's exact refs.
- Sequencing law for Council 2 confirmed: fix 5A BEFORE Article V mass identity repair,
  then gate G20 — exactly as jem proposed, just executed post-council not mid-run.
- Root-cause chain now complete for the Delivered-Home corruption story: identity
  drift (packet imprecision) + retrieval blackout (code bug) + visibility gap
  (.gitignore) = three independent layers, each separately ticketed.

## GAP-6 — ELEVATED TO DECREE-HIGH (sovereignty class)
summon_local's D118 contract being FALSE for the primary local backend (native-gguf
silently serves system-default Qwen3-1.7B, model param "used for logging") is an
M22 provenance-integrity violation at the heart of local-first. Adopted decree
direction: promote ProviderRegistry._normalize_model to routing authority;
native-gguf must HONOR-OR-REJECT, never silently substitute. Silent substitution is
the inference-layer twin of claims-outliving-mechanisms.

## GAP-7 — CLEANUP TICKETS + ONE IMPLICATION NAMED
config/council.yaml zero consumers + fully-dead src/omega/council/ module + ghost
models = straightforward cleanup tickets. NAMED IMPLICATION for the decree: the dead
module includes report_digestion.py — meaning the Stage 1.5 digester CLI likely could
never have run; the arms' manual-fallback digestion (R2) didn't merely supplement the
automation, it WAS the automation. Textbook exhibit for the root class: the command
file described an automated layer that existed only as prose.

— kali, Consultant. No pages issued (Hop Rule held).
