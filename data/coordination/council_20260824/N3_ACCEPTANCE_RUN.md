<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N3 — INST-1 FRESH-VENV ACCEPTANCE RUN (roc_racoon)
**Date**: 2026-08-24 · **Decree**: H_KALI_UNIFIED_VERDICT.md (MaKaLi council DAG, node N3)
**Procedure**: E_MAAT_BUILD_ARM.md §1 skeleton × G2_ROC_LOCALFIRST_REVIEW.md §2 3-layer amendment (reconciled — Ma'at's step-5 prose greps REPLACED per the ban)
**Fix commit**: `d16558c7` · **Predecessors**: `0d1ee1cb` (N0), `d17ae4d3` (N1), `ea8d3f2e` (N2)

---

## VERDICT MATRIX

| Layer | Assertion | Result |
|---|---|---|
| MODEL-PRESENCE | GGUF file exists before talk | ✅ PASS — `OMEGA_MODELS_DIR=/media/arcana-novai/omega_library/models/gguf`, `Qwen3-1.7B-Q6_K.gguf` (1.6G) present |
| INSTALL | fresh venv + `pip install -e ".[native,cli]"` exit 0 | ✅ PASS (after fix `d16558c7`; see DEFECT-1/2) |
| HYGIENE | redis/qdrant/youtube NOT importable in fresh venv | ✅ PASS — extras split holds; N2 lazy-guards effective |
| LAYER 0 PHYSICS | talk succeeds inside NO-NETWORK sandbox, all cloud keys unset | ✅ PASS — exit 0, response generated. Local by construction |
| LAYER 1 PROVENANCE | structured provider receipt = native-gguf | ✅ PASS (interim trace-grep method; `--json` flag absent → ticket stands) |
| LAYER 2 NEGATIVE | `! grep -qF "[Sovereignty Alert]"` | ✅ PASS — exact marker absent |
| VERSION | `omega.__version__ == pyproject version` | ✅ PASS — 1.2.0 |

**N3: GREEN.**

---

## EXACT COMMANDS

### Sandbox note (environment finding)
`unshare -rn` FAILS on this host (`write failed /proc/self/uid_map: Operation not permitted`) despite
`kernel.unprivileged_userns_clone=1` and `max_user_namespaces=58656` — userns syscalls blocked by
seccomp/confinement layer. No passwordless sudo. **Substitute**: `bwrap --unshare-net --dev-bind / / --proc /proc`
(bubblewrap at `/usr/bin/bwrap`) — verified working network-isolation equivalent. Do NOT treat unshare's
absence as "no physics possible"; bwrap is the airtight fallback on this machine.

### The executed sequence
```bash
# [1] Disk gate: df -h / → 8.3G free (>3GB threshold) → proceed
# [2] Fresh venv
python3 -m venv /tmp/omega-n3-venv && /tmp/omega-n3-venv/bin/pip install --quiet --upgrade pip
/tmp/omega-n3-venv/bin/pip install --quiet -e ".[native,cli]"        # exit 0 (typer warning, see MINOR-1)

# [3] Hygiene gate (extras split)
/tmp/omega-n3-venv/bin/python -c "...find_spec('redis'|'qdrant_client'|'youtube_transcript_api'|'yt_dlp')..."
# → all clean: PASS

# [4] THE TALK — Layer 0 physics
env -u ANTIGRAVITY_API_KEY -u GOOGLE_API_KEY -u GOOGLE_COMPAT_API_KEY \
    -u OPENROUTER_API_KEY -u OPENCODE_API_KEY -u ANTHROPIC_API_KEY \
    -u XAI_API_KEY -u CLINE_API_KEY -u CEREBRAS_API_KEY -u DEEPSEEK_API_KEY \
    -u EXA_API_KEY -u GROQ_API_KEY -u SAMBANOVA_API_KEY \
    -u OMEGA_REDIS_HOST -u OMEGA_REDIS_PASSWORD \
    bwrap --unshare-net --dev-bind / / --proc /proc \
    /tmp/omega-n3-venv/bin/omega talk "hello"
# → exit 0; output tail:
#   ⬡ IRIS ⬡ EXECUTION_MINIMAL
#   Iris
#   Hello! How can I assist you today? 😊

# [5] Layer 2: ! grep -qF "[Sovereignty Alert]" <<<"$OUT"   → PASS
# [6] Layer 1 interim: grep receipts in data/logs/events/2026-08-24.jsonl
#     run A trace trc_37f956482f5c → "provider_name": "native-gguf" (×2 token.consumption, 300+535 prompt / 9+9 completion — Iris speculative draft+verify)
#     run B trace trc_d8240f788049 → "provider_name": "native-gguf"
# [7] Version honesty: omega.__version__ == pyproject 1.2.0 → PASS

# [8] VERIFICATION BUILD after fix d16558c7 (clean-room, zero manual patches):
python3 -m venv /tmp/omega-n3-venv-b && /tmp/omega-n3-venv-b/bin/pip install --quiet -e ".[native,cli]"  # exit 0
# same env -u ... bwrap talk → exit 0, response generated, trace trc_d8240f788049 → native-gguf
```

---

## DEFECTS FOUND & DISPOSITION

### 🔴 DEFECT-1 (HIGH, debut-blocking) — `aiofiles` missing from core deps — FIXED in `d16558c7`
- **Repro**: fresh venv + `pip install -e ".[native,cli]"` → `omega talk` crashes at import:
  `oracle_cli:36 → oracle/__init__:9 → oracle.py:22 → orchestrator.py:35 → resource_guard.py:25
  → oom_protector.py:21 → psi_monitor.py:17 → ModuleNotFoundError: aiofiles`
- **Root cause of invisibility**: host `.venv` has aiofiles==25.1.0 **transitively via Crawl4AI**
  (ad-hoc install, not a declared dep). Exact reproduction of Ma'at's R1 mechanism (redis) on a second dep.
- **Scope**: 3 top-level import sites, all core talk path: `psi_monitor.py:17`, `memavailable.py:15`, `cgroup_pressure.py:17`.
- **Fix**: `aiofiles>=23.2` added to `[project].dependencies` (commit `d16558c7`). Verified by clean-room rebuild.

### 🔴 DEFECT-2 (HIGH, debut-blocking) — `opentelemetry-sdk` missing from core deps — FIXED in `d16558c7`
- **Repro**: same fresh venv, next import failure after patching aiofiles:
  `orchestrator.py:40 → observability/__init__.py:60 → otel_exporter.py:13 → ModuleNotFoundError: opentelemetry.sdk`
- **Note**: host .venv got otel-sdk transitively via `opentelemetry-exporter-otlp-proto-http`. Same drift class.
- **Fix**: `opentelemetry-sdk>=1.20` added to core deps. Lazy-guarding was the alternative but exceeds the
  <20-line N3 fix budget — flagged for the N2 owner if extras-split purity is desired later.

### 🟡 MINOR-1 — `typer[full]` extra no longer exists
- pip warns: `typer 0.25.1 does not provide the extra 'full'`. Harmless today (rich/shellingham declared
  separately in the `cli` extra) but the specifier is dead weight. Suggested cleanup: drop `[full]` from
  `pyproject.toml:75`. NOT fixed (cosmetic; outside fix budget justification).

### 🟡 MINOR-2 — config/code provider drift
- Fresh run logs `Unrecognized provider 'anthropic' in config. Skipping.` (+ xai) ×3. providers.yaml
  declares anthropic/xai fallback-chain entries the provider registry doesn't know. Degradation is graceful
  (skip) but it's config noise on every talk. Ticket for fabric owner; not fixed here.

### 🟢 OBSERVED (acceptable degradations, no action)
- `pyrage or argon2 not installed` (vault crypto optional) · `pii-shield not installed` regex fallback ·
  sklearn missing → RAGRouter heuristic fallback · BatchPersistenceWriter direct-write fallback.
- Disk-space guards fired on `/media` archive (4.33% free) and repo data/memory (<10%) — non-fatal, noted for Architect.

### 🎫 CONFIRMED GAP (ticket stands) — no `--json` on talk
- `talk` (oracle_cli.py:112-118) has no JSON output mode; only `hardware-stats` does (:1014).
- Receipt records carry `provider_name` but NOT `is_cloud`. Layer 1 remains interim (trace-grep by trace_id).
- G2 §2-B Layer-1 ticket (`omega talk --json` → `{provider_name, backend, model, is_cloud, trace_id}`) remains OPEN for the fabric owner.

---

## RESOURCE REPORT
- No pytest runs (per discipline). No subagents.
- Disk: started 8.3G free → peak ~5.8G (two venvs) → both venvs removed post-run (cleanup below).
- RAM: single local inference, well under ceiling; no OOM events.

## N4 READINESS VERDICT
**READY.** The CLI entry point survives a cold-room install and proves local inference by physics
(no-network namespace + keys unset + sovereignty-marker absence + native-gguf receipt). DEL-1 deletion
work can now rely on the "after each delete, talk still local" protocol being actually runnable —
with the caveat that the runner must use **bwrap**, not unshare, on this host.

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ N3-ACCEPTANCE ⬡ GREEN-WITH-2-FIXED-DEFECTS ⬡ trc_d8240f788049 ⬡ 2026-08-24*
