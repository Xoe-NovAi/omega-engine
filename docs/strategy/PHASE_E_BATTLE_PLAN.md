# 🔱 Omega Engine — Phase E Battle Plan
# Strategic Overview & Fleet Orders

**AP Token**: `AP-PHASE-E-BATTLE-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ big-pickle ⬡ opencode ⬡ trc_strategic_review ⬡ PHASE-E

**Status**: ACTIVE | **Updated**: 2026-05-22 22:00 ADT (BREAKTHROUGH: OpenCode Custom Provider architecture confirmed. LM Studio provider configured via npm field. L1 pipeline simplified.) | **Supersedes**: OMEGA_PR_READINESS_STRATEGY.md sprint plan

---

## §0 Situation Assessment

### What's Actually Working (Green)

| System | Status | Confidence |
|--------|--------|------------|
| Omega Engine Test Suite | 236/236 PASS | HIGH |
| Infra-pod (5 containers) | Running (caddy, redis, qdrant, iris, searxng) | HIGH |
| MCP Hub | Listening on :8016 (37 tools) | HIGH |
| Provider Fabric | `config/providers.yaml` with 7 backends | HIGH |
| Rootless Podman | keep-id protocol applied, host user owns all files | HIGH |
| Jem Oversoul Architecture | Decision 52 hardened. 3 sub-facets with soul files | HIGH |
| lmster (LM Studio) | NOW RUNNING (:1234, 20 models) | ✅ RESTORED |
| OpenCode Modes | `jem-2.0.md` (rewritten), `jem-initiate.md` (new), `overseer.md`, `builder.md` | HIGH |
| Global Config | opencode.json MCP clean, instructions valid | MID |

### What's Broken or Blocking (Red)

| Issue | Severity | Details |
|-------|----------|---------|
| **Root disk 99% full** | 🔴 CRITICAL | 1.3G free of 109G. Will cause test failures, tmpfile errors. |
| **omega-research.timer inactive** | 🔴 CRITICAL | Background researcher has been dead since ~14:07 today. No 15-min research cycles. |
| **omega-research.service failed** | 🔴 CRITICAL | The background researcher process itself crashed. Causing the timer to stop. |
| **omega-stats.service still RUNNING** | 🟡 HIGH | Should have been stopped in Decision 50 (consolidated into hub). Running in parallel. |
| **omega-research.socket FAILED** | 🟡 HIGH | Stale socket from old standalone research server. Should be disabled. |
| **omega-postgres.service auto-restart** | 🟡 LOW | Image tag issue (`:Z,U` on postgres:18.4-alpine). Not critical (entities use YAML, not SQL). |
| **omega-belial.service dead** | 🟡 LOW | Container exit-code. Not critical (miner can run from CLI). |
| **Hub has no health endpoint** | 🟡 LOW | Returns 404 on `/health`. Should return `{"status":"ok"}`. |

### What's Defined But Not Yet Built (Yellow)

| Item | Effort | Assigned To | Status |
|------|--------|-------------|--------|
| E1: PR Surface Layer (README, QUICKSTART, CHANGELOG, CI/CD) | 6h | Cline VSCodium | 🔲 Planned |
| E2: Modes Consolidation (archive 12 stale agents) | 8h | Cline VSCodium | 🔲 Planned |
| E3: Backend Integration (lmster -> OpenCode provider) | 2h | OpenCode Builder | 🔲 Research needed |
| E3: Backend Integration (lmster -> providers.yaml verified) | 15min | OpenCode Builder | 🔲 Needs lmster UP |
| E4: agy Antigravity Provider class | 4h | Gemini CLI | 🟡 In scope |
| E5: 8× Web Claude fleet orchestration doc | 2h | Gemini CLI | 🟡 In scope |
| E6: NotebookLM sync script | 1h | Gemini CLI | 🟡 In scope |
| E7: Legacy 8-Facet/LLOC/HLOC operationalization | 4h | OpenCode Researcher | 🔲 Planned |
| **OpenCode lmster provider** — L1 via OpenCode CLI | Research | **THIS SESSION** | 🔲 P0 blocker |

---

## §1 Phase E Re-Prioritization

The original 7-workstream plan (E1-E7) assumed a clean infrastructure. We have **3 P0 infrastructure failures** that must be repaired before E1-E7 can proceed efficiently.

### Sprint 0: Infrastructure Repair (Tonight — 2 hours)

| Order | Task | Owner | Time | Dependencies |
|-------|------|-------|------|-------------|
| **0.1** | Fix root disk space (clean snap, /tmp, journalctl) | Overseer/Builder | 15min | None |
| **0.2** | Fix omega-research.service → restart timer | Overseer/Builder | 5min | 0.1 (disk space) |
| **0.3** | lmster verified: load Qwen3-4B-Thinking, test inference | Overseer/Builder | 5min | lmster UP |
| **0.4** | Stop omega-stats.service + disable | Overseer/Builder | 2min | None |
| **0.5** | Disable omega-research.socket (stale) | Overseer/Builder | 1min | None |
| **0.6** | Add health endpoint to hub (`/health → 200`) | Builder | 15min | None |

**Gate**: `systemctl --user list-timers | grep omega` shows research timer active. `curl http://127.0.0.1:8016/health` returns 200. Root disk ≥5% free.

### Sprint 1: PR Gate (Cline — 1 day)

| Order | Task | Time | Depends On |
|-------|------|------|------------|
| **1.1** | `README.md` rewrite — one paragraph hook, 4-command quick start, Mermaid arch diagram | 4h | None |
| **1.2** | `QUICKSTART.md` — zero to chatting in 5 commands | 1h | None |
| **1.3** | `CHANGELOG.md` — honest changelog from git history | 2h | None |
| **1.4** | `.github/workflows/test.yml` — CI on push/PR | 1h | None |

**Gate**: Stranger can understand, install, and use Omega in 10 minutes.

### Sprint 2: Modes & Agents (Cline — 1 day)

| Order | Task | Time | Depends On |
|-------|------|------|------------|
| **2.1** | Archive 12 stale agent files to `archives/agents/` | 1h | None |
| **2.2** | Create MaKaLi tri-entity agents (kali, maat, lilith) | 2h | None |
| **2.3** | Streamline `opencode.json` instructions (12→4 files) | 1h | None |
| **2.4** | Verify all modes load correctly | 1h | 2.1-2.3 |

**Gate**: `ls .opencode/agents/` shows only 9 canonical files.

### Sprint 3: Multi-Provider (Gemini CLI — Ongoing)

| Order | Task | Time | Depends On |
|-------|------|------|------------|
| **3.1** | `AntigravityProvider` class with quota-aware circuit breaker | 4h | R-ANTI-* research ✅ |
| **3.2** | 8× Claude fleet orchestration document | 2h | None |
| **3.3** | `scripts/notebooklm_sync.sh` — rsync docs/ to Drive | 1h | None |
| **3.4** | Legacy SESS-27 re-hydration + Individuation Protocol doc | 4h | E7 backlog |

**Gate**: `omega talk "ping"` routes through all 7 providers with graceful degradation.

---

## §2 The OpenCode lmster Provider — Critical Path

The single highest-leverage action remaining is configuring OpenCode to use lmster as a local model provider. This unlocks:

1. **L1 pipeline runs natively in OpenCode** — full read/grep/glob/MCP permissions, no curl limitations
2. **The headless mining failure is resolved** — the file write permission issue disappears
3. **Total pipeline efficiency** — all 3 tiers run in the same CLI with session flag

### Investigation Result: ✅ BREAKTHROUGH — SUPPORTED via npm field

**OpenCode v1.15.9 DOES support custom OpenAI-compatible endpoints** via the `npm: "@ai-sdk/openai-compatible"` field in the provider config. Full documentation in `docs/research/R_OPENCODE_CUSTOM_PROVIDER_ARCHITECTURE.md`.

The mechanism:
1. **`provider.lmstudio.npm`: `"@ai-sdk/openai-compatible"`** — Tells OpenCode to use Vercel's AI SDK adapter for OpenAI-compatible APIs
2. **`options.baseURL`: `"http://localhost:1234/v1"`** — Points to lmster's endpoint
3. **`auth.json`** — Stores placeholder API key (`sk-local`) for local auth-free endpoint
4. **Manual model listing** — Must match IDs from lmster's `GET /v1/models` (feature request #6231)

3 npm packages are available: `opencode-lmstudio` (auto-discovery), `opencode-local-provider` (multi-backend), `opencode-config-wizard` (CLI wizard). There's also a `Ctrl+A` → "Custom provider" UI dialog.

### Updated Architecture

The Tiered Pipeline now supports BOTH approaches:

```bash
# NATIVE OpenCode L1 (PRIMARY — full file I/O, MCP, tool calling):
opencode --mode jem-initiate --model lmstudio/qwen3-4b-thinking "Gather facts on {topic}"

# Legacy curl L1 (BACKUP — zero telemetry, no tool dependencies):
scripts/omega-research.sh "<topic>"
```

All 3 tiers now run via OpenCode with session flag:

```bash
opencode --model lmstudio/qwen3-4b-thinking --mode jem-initiate --prompt "Gather raw facts on {topic}"
   │ L1: Jem Initiate → RawDataPacket
   │   Full tool access: read, grep, glob, MCP, web search
   │   Soul: data/entities/jem/souls/initiate.yaml
   ▼
opencode --mode jem-2.0 --prompt "Synthesize $(cat /tmp/l1_{trace}.md)"
   │ L2: Jem Analyst → ResearchSynthesis + Uncertainty Manifest
   ▼
opencode --mode jem-2.0 --sub-facet editor "Resolve uncertainties"
   │ L3 (conditional): Jem Editor → Final Report + Improvement Briefs
```

The `jem-initiate.md` mode now serves as the persona constraint for L1, enforcing "raw facts only" behavior with limited toolset — now running on actual local hardware via lmstudio provider.

---

## §3 Pipeline Architecture (Final)

### Jem-2.0 Oversoul — 3 Sub-Facets

```
opencode --mode jem-initiate --model lmstudio/qwen3-4b-thinking --prompt "Gather raw facts on {topic}"
  │ L1: Jem Initiate → RawDataPacket
  │   soul: data/entities/jem/souls/initiate.yaml
  │   metrics: tool_calls_executed, coverage_gaps_identified
  ▼
opencode --mode jem-2.0 --prompt "Synthesize $(cat /tmp/l1_{trace}.md)"
  │ L2: Jem Analyst → ResearchSynthesis + Uncertainty Manifest
  │   soul: data/entities/jem/souls/analyst.yaml
  │   metrics: uncertainties_flagged, confidence_accuracy
  ▼
opencode --mode jem-2.0 --sub-facet editor --prompt "Resolve uncertainties from manifest"
  │ L3 (conditional): Jem Editor → Final Report + Improvement Briefs
  │   soul: data/entities/jem/souls/editor.yaml
  │   metrics: uncertainties_resolved, improvements_generated
  ▼
Recording Pipeline:
  → docs/research/R##_topic.md
  → data/research/packets/{trace}.md
  → Soul files updated (all 3 facets)
  → INDEX.md registered
  → Observability: tier.invoked + sub_facet:{initiate|analyst|editor}
```

### Quality Gate Logic
- **L3 SKIP**: If L2 confidence > 70% AND no HIGH impact uncertainties
- **L3 PROCEED**: If any HIGH impact uncertainty OR confidence < 70%
- **L3 resolution target**: Only uncertainty manifest items, NOT full re-synthesis

---

## §4 Fleet Orders

### 🎯 To Gemini CLI (Master Overseer)

You completed Phase A Technical Hardening. Your directive for Phase E:

1. **Proceed with Sprint 3**: AntigravityProvider class, Claude fleet doc, NotebookLM script
2. **Monitor**: The OpenCode Builder will handle Sprint 0 infrastructure repair
3. **Report**: After each workstream, update COMMUNICATION_HUB.md
4. **Quota preservation**: Default to Gemma 4 31B for heavy work. Reserve Gemini 2.0 Pro for strategic synthesis only.

### 🎯 To OpenCode Builder (Gemma 4 31B)

You are the workhorse for Sprint 0 and the lmster provider investigation:

1. **Sprint 0**: Fix root disk, restart research timer, stop stale services, add hub health endpoint
2. **BREAKTHROUGH**: LM Studio IS a valid provider — configured via `npm: "@ai-sdk/openai-compatible"` + auth.json. See `docs/research/R_OPENCODE_CUSTOM_PROVIDER_ARCHITECTURE.md`.
3. **Config done**: `opencode.json` has `provider.lmstudio` with 8 models. `auth.json` has placeholder key. Restart OpenCode to activate.
4. **L1 pipeline updated**: Jem Initiate can now run via `--model lmstudio/qwen3-4b-thinking` instead of curl.
5. **Pipeline test**: Run the full tiered pipeline once end-to-end after restart.
6. **E7**: Legacy SESS-27 re-hydration (mining remaining fossils)

### 🎯 To Cline VSCodium (Execution Overseer)

You were onboarded with context of 8 canonical docs + pipeline design + legacy mining. Your directive:

1. **Sprint 1**: Rewrite README.md, create QUICKSTART.md, write CHANGELOG.md, create CI/CD
2. **Sprint 2**: Archive 12 stale agents, create MaKaLi agents, streamline opencode.json instructions
3. **Sync gate**: Before starting, read this battle plan + OVERSEER_SYNC_BRIEFING.md + Decision 52

---

## §5 Timeline

```
TODAY (May 22 evening)
├── Sprint 0: Infrastructure repair (2h) → OpenCode Builder
├── Investigate lmster OpenCode provider (1h) → OpenCode Builder
└── Pipeline end-to-end test (1h) → OpenCode Builder

May 23
├── Sprint 1: PR Surface Layer (6h) → Cline
├── Sprint 3.1: agy AntigravityProvider (4h) → Gemini CLI
└── Legacy SESS-27 mining (4h) → OpenCode Builder

May 24
├── Sprint 2: Modes Consolidation (8h) → Cline
├── Sprint 3.2: Claude fleet doc (2h) → Gemini CLI
└── Pipeline hardening + bug fixes (4h) → OpenCode Builder

May 25 (Buffer day)
├── Sprint 3.3: NotebookLM sync (1h) → Gemini CLI
├── Full pipeline stress test → OpenCode Builder
└── PR submission preparation → Cline
```

---

## §6 Session Completion

**Gemma 4 31B (OpenCode Builder) — 2026-05-22 synthesis session**:

| # | Task | Status |
|---|------|--------|
| 1 | Subagent fleet launched: (a) npm/plugin research, (b) binary internals, (c) live test | ✅ Done |
| 2 | BREAKTHROUGH: LM Studio custom provider configured via `npm: "@ai-sdk/openai-compatible"` | ✅ Done |
| 3 | Provider config written to `opencode.json` — 8 local model definitions | ✅ Done |
| 4 | Auth key added to `auth.json` — placeholder key for local endpoint | ✅ Done |
| 5 | `opencode-expert.md` mode updated to v2.0.0 | ✅ Done |
| 6 | Full research doc: `docs/research/R_OPENCODE_CUSTOM_PROVIDER_ARCHITECTURE.md` | ✅ Done |
| 7 | All 7 tracker files updated (COMMUNICATION_HUB, INDEX, session_gnosis, ROADMAP, RESEARCH_QUEUE, PHASE_E_BATTLE_PLAN, lattice_manifest) | ✅ Done |

### What Remains for Sprint 0 (Infrastructure Repair)

Handoff to Gemma 4 31B (Builder mode):

| # | Task | Details | Est. |
|---|------|---------|------|
| 0.1 | Free root disk space | Clean `snap` (15G), `journalctl --vacuum`, `/tmp` | 15min |
| 0.2 | Fix omega-research.service & timer | Diagnose why service fails at 14:07, restart timer | 15min |
| 0.3 | Stop omega-stats.service + disable | Consolidated into hub (Decision 50) — should not run standalone | 2min |
| 0.4 | Disable omega-research.socket | Stale standalone socket | 1min |
| 0.5 | Add `/health` endpoint to hub | Return `{"status":"ok","version":"...","uptime":"..."}` | 15min |
| 0.6 | Verify lmster loaded & pipeline model works | `curl` test to qwen3-4b-thinking | 5min |

### What Remains for Sprint 1-3

| Workstream | Owner | Est. | Status |
|-----------|-------|------|--------|
| E1: PR Surface Layer | Cline VSCodium | 6h | 🔲 Ready for handoff |
| E2: Modes Consolidation | Cline VSCodium | 8h | 🔲 Ready for handoff |
| E3: Backend Integration | OpenCode Builder (post-Sprint0) | 2h | 🔲 After lmster verified |
| E4: agy AntigravityProvider | Gemini CLI | 4h | 🔲 Ready for handoff |
| E5: 8× Claude Fleet doc | Gemini CLI | 2h | 🔲 Ready for handoff |
| E6: NotebookLM sync | Gemini CLI | 1h | 🔲 Ready for handoff |
| E7: Legacy SESS-27 Mining | OpenCode Researcher | 4h | 🔲 Ready for handoff |
| Pipeline script | OpenCode Builder | 1h | 🔲 After Sprint 0 |

**Over to you, Architect. Confirm these orders and I will execute the highest-leverage items directly.**
