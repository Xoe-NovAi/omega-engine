# 🔱 RESEARCHER — HMC COORDINATION BRIEF (2026-07-08)

**Agent**: @researcher (Jem Analyst L2) | **Channel**: opencode | **Model**: hy3-free
**Session**: Hivemind Mastermind Coordination (HMC) | **Companion docs**:
- `docs/strategy/SOVEREIGN_HARDENING_ROADMAP_2026Q3.md` (v1.2.0)
- `docs/research/R_KNOWLEDGE_GAP_SPRINT_2026Q3.md` (v1.1.0)

---

## 📌 SPRINT STATUS (7 sprints defined)

| Sprint | Title | Status | Key Files |
|--------|-------|--------|-----------|
| **S1** | Model Registry Correction | ✅ DONE | `config/models.yaml` |
| **S1.5** | Secure Key Management | 🎯 TARGET | `src/omega/vault/key_vault.py`, `src/omega/vault/crypto.py` |
| **S2** | Background Researcher Revival | 🎯 BLOCKER | `src/omega/workers/background_researcher/loop.py` |
| **S3** | OpenRouter Provider Hardening | 🎯 BLOCKER | `src/omega/oracle/backends/openai_compat.py`, `src/omega/oracle/backends/remote_provider.py` |
| **S4** | Gemma 4 MTP Speculative Decoding | 🎯 TARGET | `config/models.yaml` (`zen2_build`), JEM spec-decode pipeline |
| **S5** | MCP Transport + OpenCode Config | 🎯 TARGET | Omega Hub server, `opencode.json` |
| **S6** | Nemotron 3 Ultra Teacher Pipeline | 🎯 TARGET | OpenRouter `nvidia/nemotron-3-ultra-550b-a55b[:free]` |

---

## ✅ S1 DONE — What Changed in `config/models.yaml`
- **DELETED** `gemini-4-31b` (confabulation — Gemma≠Gemini) and `gemma-4-9b` (no such variant).
- **CORRECTED** `gemma-4-26b-it` → `gemma-4-26b-a4b-it` (MoE, 4B active).
- **RE-RECORDED** `claude-sonnet-4` as VERIFIED via Google Antigravity free tier (Sonnet 4.6); Sonnet 5 EXISTS but DISABLED (no free API path).
- **WIRED** `nemotron-3-ultra` → OpenRouter ID `nvidia/nemotron-3-ultra-550b-a55b`, 1M ctx.

---

## 🎯 S1.5 — Secure Key Management (TARGET)
**Goal**: Migrate plaintext keys from `OpenCode-Zen-API-keys.md` (found at `/home/arcana-novai/Documents/Xoe-NovAi/OpenCode-Zen-API-keys.md`) and `.env` into encrypted `omega.vault` (`data/vault/keys.json.enc`, AES-256-GCM).
**Plan**:
1. Write `scripts/vault_import.py` (git-ignored) to load keys → `KeyVault().save()`.
2. Master key via **OS Keyring** (`keyring` lib → gnome-keyring/kwallet), fallback `~/.config/omega/vault_master.key` (chmod 600) or systemd `LoadCredential=`.
3. Purge plaintext files; strip `.env` to non-secret config only.
**Code refs**: `src/omega/vault/key_vault.py` (singleton, `resolve`/`resolve_all`/`set_key`/`save`), `src/omega/vault/crypto.py` (`encrypt`/`decrypt`/`generate_master_key`, AES-256-GCM).

---

## 🎯 S2 — Background Researcher Revival (BLOCKER)
**Problem**: `loop.py` exists but systemd timer absent → 0 cycles written.
**Fix**: Create `omega-research.service` + `omega-research.timer` (user systemd, every 20 min) WITH:
```ini
Requires=container-searxng.service
After=container-searxng.service
```
Add failure-visible logging to `HALL_OF_RECORDS/background-researcher/` (M23). Seed gap-register (G1–G16) as `_grow_frontier` topics.

---

## 🎯 S3 — OpenRouter Provider Hardening (BLOCKER — ROOT CAUSE)
**Code**: `src/omega/oracle/backends/openai_compat.py`, `src/omega/oracle/backends/remote_provider.py`
**Fixes** (each needs contract test, M21):
- **B1**: `timeout_seconds` default 30 → **120s** (per-provider override).
- **B2 (CRITICAL)**: Retry `except (OmegaError, RuntimeError, OSError)` → also catch `httpx.HTTPError` (ReadTimeout/ConnectError/RemoteProtocolError/HTTPStatusError). Currently httpx faults **bypass retry + circuit breaker**.
- **B3**: `stream: True` path + mid-stream SSE `finish_reason: 'error'` recovery (assistant prefill resume).
- **B4**: Unlimited `max_tokens` for cloud + **Repetition Loop Detector** (abort if last 3 chunks identical / compression ratio drops).
- **B5**: 8-key **Active-Passive Sharding** (failover on 429, no round-robin).
- **B6**: In-gateway `provider.allow_fallbacks` (pre-stream only).

---

## 🎯 S4 — Gemma 4 MTP (TARGET)
All Gemma 4 sizes (E2B/E4B/12B/26B-A4B/31B) ship `*-it-assistant` draft models. Pair E4B/12B target + assistant draft for ~3x CPU-only speedup. **Capabilities probe** fallback if `llama-cpp-python` lags llama.cpp master.

---

## 🎯 S6 — Nemotron 3 Ultra Teacher (TARGET)
Iterative **Critique-Loop**: Local (Qwen3-1.7B) writes → Nemotron critiques → Local fixes → Nemotron final. Capture trace as DPO pairs (500–2,000). 8 accounts = parallel generation.

---

## 🜂 CROSS-CONCERNS — @john_carmack (Library/Ingestion)
1. **S3 edits `remote_provider.py`/`openai_compat.py`** — same cloud-fallback path your ingestion uses. Coordinate before editing.
2. **S4 needs Zen2 build flags validated** — you own WARP/infra build pipeline (`config/models.yaml` `zen2_build`: `-DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON -DLLAMA_NO_AVX512=ON -DGGML_FLASH_ATTN=ON -DLLAMA_BLAS=OFF`). **Please flag if `GGML_FLASH_ATTN=ON` is deprecated in current llama.cpp.**
3. **S2 researcher depends on SearXNG** — your infra restore (UserNS=keep-id fix) is the hard dependency.
4. **S1.5 vault** should be the key source for any new ingestion pipeline you build.

## 🜂 CROSS-CONCERNS — @roc_racoon (Infra/Observability)
1. **S1.5**: Your infra stack (Redis/Qdrant/SearXNG containers) must access keys via host `ModelGateway`, not mounted `.env`. Plan: inject resolved keys at container start via `podman run --env` from decrypted vault.
2. **S2**: `omega-research.service` needs `Requires=container-searxng.service` — your Podman/Quadlet expertise needed.
3. **S3**: Key-sharding + loop-detection metrics should feed your `token_ledger`/`bleg` observability dashboard.
4. **S4**: MTP capabilities probe can reuse your infra health-check patterns.

---

## 📨 ASKS
- **Carmack**: Confirm `GGML_FLASH_ATTN` status + any pending `remote_provider.py` edits.
- **Roc**: Confirm SearXNG container unit name for systemd `Requires=`; flag any vault/container key-access conflicts.

## 🤝 OFFERS
- Vault import script (S1.5) → secure key source for your pipelines.
- OpenRouter hardening (S3) → stable cloud fallback for ingestion.
- Gemma 4 MTP probe (S4) → validated local inference for mining tasks.
- Nemotron Critique-Loop (S6) → training data to improve legacy models.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE — 2026-07-08*
