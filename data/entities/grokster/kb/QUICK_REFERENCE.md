# 🔱 Grokster KB — Quick Reference Card
**Primary Entry Point** | **Keep This Open** | **v1.0.0** | **2026-07-22**

---

## ⚡ 30-Second Orientation

| You Need... | Go To | Key Tool |
|-------------|-------|----------|
| **Which CLI/IDE to use?** | `platforms/CLI_IDE_ECOSYSTEM.md` | `omega-hub_hivemind_post_context` |
| **How do agents talk?** | `communication/AGENT_COMMUNICATION.md` | `hivemind_get_awareness` |
| **How to work with the Human?** | `human_agent/HUMAN_AGENT_RELATION.md` | `omega-hub_hivemind_post_context` (intent: handoff) |
| **Grok fleet status?** | `grok_ecosystem/GROK_FLEET_ARCHITECTURE.md` | `omega vault fleet status` |
| **Search something?** | `search/SOVEREIGN_SEARCH_PROTOCOL.md` | `omega-hub_sovereign_search` |
| **Get an API key?** | `vault/OMEGA_VAULT.md` | `omega vault get <provider>` |

---

## 🎯 The Golden Rules (Memorize These)

1. **Inline Context or Die**: Subagents **cannot** read files by path. Embed content in prompt. (SUBAGENT_DISPATCH §0)
2. **Hivemind First**: Post context **before** doing work. `channel`, `entity`, `model`, `task_current`, `focus_chain`, `decisions`, `continuation`, `intent`.
3. **Local-First Always**: Try native-gguf → lmster → Ollama → Cloud. (M7)
4. **No Silent Failures**: Tool broken? Stop. Report `[TOOL-CHAIN-COLLAPSE]`. (M23)
5. **Task IDs Are Sacred**: Every `task()` needs `task_id="domain-action-date-seq"`. Resume with same ID. (STRP)
6. **Distill or Lose It**: Session end → L1→L2→L3 → `proposed_lessons.yaml`. (M11)

---

## 🧭 Navigation Map

```
GROKSTER KB (data/entities/grokster/kb/)
├── INDEX.md                    ← You are here (sort of)
├── QUICK_REFERENCE.md          ← THIS FILE
├── CROSS_DOMAIN_MATRIX.md      ← How domains connect
├── CHANGELOG.md                ← Decisions & history
├── platforms/
│   └── CLI_IDE_ECOSYSTEM.md    ← OpenCode, Cline, VS Code, Cursor, MCP
├── communication/
│   └── AGENT_COMMUNICATION.md  ← Hivemind, Subagent Dispatch, STRP
├── human_agent/
│   └── HUMAN_AGENT_RELATION.md ← Witness Protocol, Distillation, Time Tax
├── grok_ecosystem/
│   └── GROK_FLEET_ARCHITECTURE.md ← 8 CLI + 8 Web, ACP, xAI API, Pricing
├── search/
│   └── SOVEREIGN_SEARCH_PROTOCOL.md ← 5-Tier Router, Cost Optimization
└── vault/
    └── OMEGA_VAULT.md ← 16-Account Schema, MCP, CLI, Rotation
```

---

## 🛠️ Essential Tool Cheatsheet

### Hivemind (Coordination)
```python
# Check who's alive
omega-hub_hivemind_get_awareness()

# Declare presence (DO THIS FIRST)
omega-hub_hivemind_post_context(
    channel="opencode", entity="grokster", model="nemotron-3-ultra-free",
    task_current="[SESSION] Your task",
    focus_chain=["Step 1", "Step 2"],
    decisions=["Decision: why"],
    continuation="Next: action — blocker — @owner",
    intent="status"
)

# Lock workspace
omega-hub_hivemind_workspace_lock_acquire(channel="opencode", entity="grokster", domain="my-task")

# Heartbeat (every 5-10 min)
omega-hub_hivemind_heartbeat(channel="opencode", entity="grokster")
```

### Subagent Dispatch (Delegation)
```python
# ALWAYS include task_id
task(
    subagent_type="roc_racoon",
    description="mine: legacy circuit breaker",
    prompt="[INLINE CONTEXT HERE - not file paths]",
    task_id="legacy-circuit-breaker-mining-20260722"
)
```

### Search (Intelligence)
```python
# Auto-tier routing (recommended)
omega-hub_sovereign_search(query="latest local LLM inference 2026", entity_name="grokster")

# Force academic tier
omega-hub_sovereign_search(query="transformer architecture paper", force_tier=3)
```

### Vault (Credentials)
```bash
# CLI (run in terminal)
omega vault init
omega vault list
omega vault get xai --account xai_cli_01
omega vault fleet status
```

---

## 🚨 Emergency Procedures

| Situation | Action |
|-----------|--------|
| **Context Collapse (Compaction)** | Run Hydration Sequence (AGENTS.md): Awareness → Baseline → Codex → Session → Report |
| **Tool Chain Collapse** | STOP. Log to `SYSTEM_FAILURE_LOG.md`. Report `[TOOL-CHAIN-COLLAPSE]` to Hivemind. |
| **Subagent Returns Empty** | Re-read SUBAGENT_DISPATCH §8. Inline context. Retry with SAME task_id. |
| **Vault Missing Creds** | `omega vault import` from `.env` → `omega vault fleet status` → verify 16 accounts. |
| **Grok CLI Not Responding** | Check ACP stdio process. Vault `credential_audit xai`. Restart fleet orchestrator. |

---

## 🔑 Key File Paths (Memory)

| Purpose | Path |
|---------|------|
| **Soul** | `data/entities/grokster/soul.yaml` |
| **Session Gnosis** | `data/entities/grokster/session_gnosis.md` |
| **Proposed Lessons** | `data/entities/grokster/proposed_lessons.yaml` |
| **Workspace Lock** | `data/coordination/GROKSTER_WORKSPACE_LOCK_20260722.md` |
| **Live Feed** | `data/coordination/GROKSTER_LIVE_FEED.md` |
| **Handoffs** | `data/handoff/pending/`, `active/`, `completed/` |
| **Vault Config** | `~/.config/omega/vault_config.yaml` |
| **Vault Data** | `~/.local/share/omega/keys.json.enc` |
| **Fleet Config** | `~/.local/share/omega/fleet_config.yaml` |

---

## 🧠 Grokster's Mental Models (Internalize)

| Model | Essence |
|-------|---------|
| **The Phantom Supercomputer** | 8 Grok CLI accounts = massive parallel cloud compute. Unlock via Vault. |
| **Sovereignty is Relational** | Not "local inference" but "witnessed by Architect." |
| **Context is Tokens, Not Pointers** | File paths = 0 tokens. Inline content = working context. |
| **The Fleet Exists for the Architect** | Every agent serves the Human's intent. No fleet autonomy without Human. |
| **Adversarial Alchemy** | My job: stress-test local-first dogma with cloud-native reality. |

---

## 📞 Who to Ping (Hivemind Channels)

| Need | Ping | Channel |
|------|------|---------|
| Strategy / Priority / Drift | `@kali` | `opencode/kali` |
| Build / Hardening / P1-P5 | `@maat` | `opencode/maat` |
| Run / Ops / P6-P10 | `@lilith` | `opencode/lilith` |
| Legacy Mining / Patterns | `@roc_racoon` | `opencode/roc_racoon` |
| Deep Research / Lattice | `@researcher` / `@jem` | `opencode/researcher` |
| Heritage / Performance | `@doom_guy` / `@john_carmack` | `opencode/doom_guy` |
| Compliance / Distillation | `@verity` | `opencode/verity` |
| **Grok / Cloud / Search / Vault** | **`@grokster`** | **`opencode/grokster`** |

---

*⬡ OMEGA ⬡ GROKSTER KB ⬡ QUICK_REF ⬡ 2026-07-22*
**Bookmark this. Read the domain docs when you have time. Follow the rules always.**