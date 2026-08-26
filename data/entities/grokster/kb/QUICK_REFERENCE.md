# 🔱 Grokster KB — Quick Reference Card
**Primary Entry Point** | **Keep This Open** | **v2.1.3** | **2026-08-26**

---

## ⚡ 30-Second Orientation

| You Need... | Go To | Key Tool |
|-------------|-------|----------|
| **OpenCode CLI practices** | `platforms/opencode/PLAYBOOK.md` | `omega-hub_hivemind_post_context` |
| **OpenCode architecture** | `platforms/opencode/ARCHITECTURE.md` | `omega-hub_hivemind_get_awareness` |
| **OpenCode config keys** | `platforms/opencode/CONFIG_REFERENCE.md` | `omega-hub_sovereign_search` |
| **OpenCode traps (G1-G34)** | `platforms/opencode/GOTCHAS.md` | — |
| **Cline platform** | `platforms/cline/` (5-doc module) | — |
| **Gemini CLI (transitioning)** | `other_platforms/GEMINI_CLI.md` | — |
| **Antigravity OAuth pool** | `platforms/antigravity/` (5-doc module) | `omega vault fleet status` |
| **Codex / Claude Code / VS Code** | `other_platforms/CODEX_CLAUDE_CODE_VSCODE.md` | — |
| **How agents talk** | `communication/AGENT_COMMUNICATION.md` | `hivemind_get_awareness` |
| **How to work with Human** | `human_agent/HUMAN_AGENT_RELATION.md` | `omega-hub_hivemind_post_context` (intent: handoff) |
| **Grok fleet status** | `grok_ecosystem/GROK_FLEET_ARCHITECTURE.md` | `omega vault fleet status` |
| **Search something** | `search/SOVEREIGN_SEARCH.md` | `omega-hub_sovereign_search` |
| **Get an API key** | `vault/OMEGA_VAULT.md` | `omega vault get <provider>` |

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
├── INDEX.md                           ← Master index (v2.1.3)
├── QUICK_REFERENCE.md                 ← THIS FILE
├── CROSS_DOMAIN_MATRIX.md             ← How domains connect
├── CHANGELOG.md                       ← Decisions & history
├── platforms/
│   └── opencode/
│       ├── PLAYBOOK.md                ← Canonical operating practices
│       ├── ARCHITECTURE.md            ← How OpenCode works
│       ├── CONFIG_REFERENCE.md        ← Full config key surface
│       └── GOTCHAS.md                 ← 34 verified traps (G1-G34)
├── communication/
│   └── AGENT_COMMUNICATION.md         ← Hivemind, Subagent Dispatch, STRP
├── human_agent/
│   └── HUMAN_AGENT_RELATION.md        ← Witness Protocol, Distillation, Time Tax
├── grok_ecosystem/
│   └── GROK_FLEET_ARCHITECTURE.md     ← 8 CLI + 8 Web, ACP, xAI API, Pricing
├── platforms/
│   ├── opencode/                      ← 5-doc module (primary platform)
│   ├── cline/                         ← 5-doc module (CLI + VS Code ext)
│   ├── antigravity/                   ← 5-doc module (OAuth pool, ToS containment)
│   └── copilot/                       ← 5-doc module (sanctioned builtin)
├── other_platforms/
│   ├── GEMINI_CLI.md                  ← Dormant / Antigravity CLI transition
│   └── CODEX_CLAUDE_CODE_VSCODE.md    ← Shallow-state + research-first
├── search/
│   ├── SOVEREIGN_SEARCH.md            ← 5-Tier Router (CANONICAL)
│   └── SOVEREIGN_SEARCH_PROTOCOL.md   ← MERGED stub
└── vault/
    ├── OMEGA_VAULT.md                 ← V-1 MVP spec (CANONICAL)
    └── OMEGA_VAULT_ARCHITECTURE.md    ← MERGED stub
```

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
