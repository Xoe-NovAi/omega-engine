# Session Anchor — Grokster 2026-07-26

## Session Objective
Complete knowledge gaps research, LiteLLM deep dive, Carmack S3 review, and sprint reordering. Document all findings for team.

## What Was Done

### 1. LiteLLM Integration Deep Dive Research ✅
- **File**: `docs/research/R_LITELLM_INTEGRATION_DEEP_DIVE_20260726.md` (713 lines)
- **Verdict**: **DEFER** — 7 CVEs in June 2026 (CVSS 10.0 RCE chain + PyPI supply chain compromise), 3 new services (PG/Redis/Proxy), 7-32ms overhead, Python GIL ceiling
- **Only 3/12 dimensions favor proxy** — all multi-team governance features we don't have
- **Action**: Use OpenCode native providers + `opencode-plugin-litellm` (SDK mode, no proxy) for dynamic model discovery. Client-side failover wrapper for critical paths.

### 2. Carmack S3 Consultant Review ✅
- **File**: `docs/reviews/CARMACK_REVIEW_RESEARCH_STRATEGY_20260726.md` (202 lines)
- **Leverage ratios computed** for all major initiatives
- **Sprint reordered by impact/effort** — Grok CLI fleet promoted to P0-1 (leverage 2.50)
- **Hardware reality check** — 5700U constraints documented
- **Sovereignty baseline defined** — "local-only functional" = engine executes core mission with ZERO network

### 3. Sprint Reordering (Guard & Distill + Super-Urgent) ✅

| Priority | Ticket | Owner | Effort | Leverage | Status |
|----------|--------|-------|--------|----------|--------|
| **SUPER-URGENT** | G-1 Workhorse continuity | Architect | Variable | — | Gemma 4 free tier cliff |
| **SUPER-URGENT** | W-1 WARP proxy pool | Architect (sudo) | 2-4h | — | Fix `warp-ns-setup` |
| **P0-1** | **Wire Grok CLI Fleet (ACP stdio)** | Researcher+Grokster→Ma'at/P3 | **4h** | **2.50** | **NEW P0 — highest leverage** |
| **P0-2** | **ResourceGuard RAM fix + psutil** | Ma'at/P3 | **0.25h** | **9.00** | 15 min, prevents OOM |
| **P0-3** | **Run `make test` → real numbers** | Ma'at/P3 | **0.1h** | **∞** | Truth anchor |
| **P0-4** | **V-1 VaultCore MVP** | Researcher+Grokster→Ma'at/P1 | 8h | 1.13 | Blocks Grok automation |
| **P0-5** | **C-3 Restic Backup (local + timer)** | Lilith/P6 | 8h | 0.88 | Single SSD = SPOF |
| **P1-1** | Identity Fluidity Phase 0 | Grokster | 2h | 4.00 | After C-1′ (done) |
| **P1-2** | MaKaLi Config (Kali local, Ma'at+Lilith cloud) | Ma'at/P3 | 0.5h | 3.50 | Not 4h build — config only |

### 4. Explicitly DEFERRED (Per Carmack + Researcher Council) ✅
- **LiteLLM Proxy (full stack)** — 7 CVEs in June, 3 new services, violates M2/M7/M16/M23
- **Gap Detector Service (Phase 4)** — Overengineered; `_grow_frontier()` does 80% in 20 lines
- **SQLite Research Job Store** — 18 jobs, single researcher; YAML + `fcntl.flock()` sufficient
- **MaKaLi Sequential Mode (4h build)** — Simplify to 0.5h config: Kali local, Ma'at+Lilith cloud
- **New free-tier providers (Cerebras/Groq)** — Systematize existing 6 first
- **Full ACP Bridge (20h+)** — V-1 MVP + ACP stdio smoke only

### 5. HMC Hub Updated ✅
- Appended all research findings, sprint reordering, hardware reality check to @grokster section
- Documented all deferrals with rationale
- Added task IDs for traceability

### 6. Session Anchor Updated ✅
- This file updated with complete session summary

## Key Decisions
1. **Wire Grok CLI fleet NOW (P0-1, 4h)** — unlocks 8 parallel Opus-class streams, solves MaKaLi OOM + search + distillation
2. **Fix ResourceGuard default (15 min)** — 12GB → 6GB + psutil check prevents OOM on 8B models
3. **Run `make test` and report REAL numbers** — stop citing "1,572 collected" as quality metric (vanity metric violates M18)
4. **Define "local-only functional" baseline** — 8 of 10 providers are cloud free tiers; roadmap assumes cloud for every critical path
5. **LiteLLM Proxy DEFERRED** — Use `opencode-plugin-litellm` (SDK mode) for model discovery only

## Next Actions (Post-Compact)
1. Add 8 GitHub Copilot accounts in OpenCode: `/connect` → GitHub Copilot → "Login / Add GitHub.com Account" ×8
2. Add API keys to `~/.bashrc`:
   ```bash
   export GROQ_API_KEY="gsk_..."
   export NVIDIA_API_KEY="nvapi_..."
   export CEREBRAS_API_KEY="csk_..."
   export SAMBANOVA_API_KEY="..."
   export SILICONFLOW_API_KEY="..."
   export OPENROUTER_API_KEY="sk-or-..."
   ```
3. Fix ResourceGuard default (15 min): Edit `src/omega/cognition/resource_guard.py` — `max_ram_mb=12288` → `6144`, add `psutil.virtual_memory().available` check
4. Run `make test` and report: "X passed, Y failed, Z skipped" — NOT "1,572 collected"
5. Wire Grok CLI fleet (P0-1, 4h) — ACP stdio integration via `src/omega/integrations/grok_cli.py`
6. Enable restic backup timer: `systemctl --user enable --now restic-backup.timer`

## Files Modified
- `docs/research/R_LITELLM_INTEGRATION_DEEP_DIVE_20260726.md` — Created (713 lines)
- `docs/reviews/CARMACK_REVIEW_RESEARCH_STRATEGY_20260726.md` — Created (202 lines)
- `data/coordination/HMC_COLLABORATION_HUB.md` — Appended @grokster section
- `data/coordination/SESSION_ANCHOR.md` — This file
- `~/.config/opencode/opencode.json` — 6 providers + plugin (from previous session)
- `~/.local/bin/aider` — Working wrapper (from previous session)

## Verification Commands
```bash
aider --version                    # → 0.86.2
opencode --version                 # → current version
/tmp/Python-3.12.11/python --version  # → 3.12.11
make test                          # → report REAL pass/fail/skip
grep -c "provider" ~/.config/opencode/opencode.json  # → 8 providers
```

---

*Session complete. Ready for compact.*