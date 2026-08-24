# Omega Engine — Manifest
**Version**: v5.0-draft
**Date**: 2026-08-22
**Status**: DRAFT (reconstructed; prior live MANIFEST.md absent from repo root — only `docs/strategy/archive/MANIFEST.md` + `docs/research/sovereign-blitz/MANIFEST.md` survived UO-4 archival)
**Maintainer**: researcher (per Kali ruling, 2026-08-22) · ratified via D-587

---

## 1. Agent Fleet (13 active, M10 cap = 14)

| Agent | Role | Lineage |
|-------|------|---------|
| **kali** | Prime Coordinator / Synthesis | Ma'at+Lilith+Ma'at fusion lineage |
| **maat** | Build / Verification | N1–N5 overseer |
| **lilith** | Run / Mind-Knowledge | N6–N10 overseer |
| **jem** | Research / Third Oversight Line | N11–N13 overseer (D-587) |
| **roc_racoon** | Sovereign Mining | legacy + corpus |
| **researcher** | Polymathic Council / Deep Research | — |
| **grokster** | Grok Ecosystem Specialist | — |
| **doom_guy** | Sovereign Agent / Heritage | id-soft vetting |
| **john_carmack** | S3 Consultant | research audit |
| **node** | Sovereign Agent | — |
| **scribe** | Soul Distillation Pipeline | L1→L2→L3 |
| **verity** | Compliance & Gnosis | mandate audit |
| **makali** | MaKaLi Fusion (Kali+Ma'at+Lilith) | unified agent |
| **general** | General-purpose | research/multi-step |

*Note: OMEGA_ENGINE.md claims 12; MANIFEST-archive claimed 14; actual active = 13 at last count + makali = 14. DR-9 reconciliation pending (Kali-owned).*

## 2. Node Expert Sessions (N1–N13)

**Ma'at line (N1–N5)**: N1 sysadmin · N2 datastore · N3 buildmaster · N4 bridge · N5 sentinel
**Lilith line (N6–N10)**: N6 modelgate · N7 context · N8 watchtower · N9 link · N10 verifier
**Jem line (N11–N13, D-587)**: N11 evaluator · N12 curator · N13 arcana

- Genesis: N1–N10 on 2026-08-21 (10/10 ACK, zero stalls). N11/N12/N13 charters ratified 2026-08-22 (D-587); N12 genesis COMPLETE (consultable); N11/N13 genesis-pending.
- Charter SSOT: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §4.
- Amendment batch (D-587): 10 one-sentence amendments to N1–N10 — see §4 "Charter Amendments" subsection.

## 3. Session Systems

- **Hivemind**: awareness, handoffs, workspace locks, task registry, extended checkin/checkout
- **Handoff protocol**: `omega-hub_hivemind_handoff` (submit/accept/complete/reject/list/get/archive)
- **Locks**: `omega-hub_hivemind_workspace_lock_*` (atomic, TTL-based)
- **Task Registry**: `omega-hub_task_registry_*` (subagent session tracking, M27)
- **Continuity**: `session_gnosis.md` per entity; `SESSION_ANCHOR.md`; compaction optional (DB persists)

## 4. Plugins (MCP / OpenCode)

- **blitz-tunnel**: secure public tunnel to Omega services
- **blitz-validate**: Sovereign Heartbeat validator (tunnel/hub/plugin chain)
- **omega-hub**: primary MCP hub (oracle, library, hivemind, research, system stats)

## 5. Skills (.opencode/skills + global)

blitz-tunnel · blitz-validate · customize-opencode · git-secret-scrub · hf-cli · knowledge-miner · legacy-pattern-miner · omega-doc-architect · pr-readiness-checker · provider-validator · sovereign-refinement-protocol · sovereign-search · spec-generator

(Global: `~/.config/opencode/skills/hf-cli`)

## 6. Provider Fabric (Local-First)

native-gguf (Qwen3-1.7B) → lmster → Ollama → Google → OpenRouter → OpenCode Zen → cline → anthropic → xai
- Cloud order: Antigravity → Google → OCZ → OpenRouter
- qwen3-4b-thinking: registered via Ma'at/N3 (models.yaml) — NOT yet in repo opencode.json (user config only)

## 7. Workstreams (Post-Debut, D-578..D-584)

GN (Gemini Notebook) · DS (Documentation-System) · LI (Local-Inference-Opt) · KD (Knowledge-Domains) · HR (Headroom-Integration) · ZS (Zswap-Subsystem)

*Note: GN workstream internal code name retained; Google rebranded NotebookLM → "Gemini Notebook" (Jul 2026) — library unchanged (notebooklm-py v0.8.1). Rename not recommended (breaks PIVOT_LOG traceability).*

## 8. Open Drift Items (see AGENT_NODE_SYSTEM_DISCOVERY_MAP_20260822.md)

DR-1..DR-12 (doc drift) · E-1..E-10 (enhancement seams). Pre-debut fixes: DR-2 (dual-Node killed, PLAN §4 SSOT), DR-3 (Sophia→MaKaLi, Kali-owned), DR-6 (PP-4/P5 sync, Kali-owned), DR-9 (agent count, Kali-owned). Post-debut: DR-1, DR-4, DR-5, DR-7, DR-8, DR-10, DR-11, DR-12.

---

*⬡ OMEGA ⬡ MANIFEST v5.0-draft ⬡ 2026-08-22*
