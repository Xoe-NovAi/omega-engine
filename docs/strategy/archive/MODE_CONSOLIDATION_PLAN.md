# 🔱 Mode Consolidation Plan — Target Architecture

⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_strategic ⬡ PHASE‑B  
**Status**: Design complete — ready for Gemma execution  
**Current**: 24 entries across global config + project agents + modes  
**Target**: 11 modes + 1 reference document  

---

## Current Inventory

| # | Name | Source | Decision | Why |
|---|------|--------|----------|-----|
| 1 | `builder` | `.opencode/agents/builder.md` | ✅ KEEP | Primary workhorse (Gemma 4 31B) |
| 2 | `researcher` | `.opencode/agents/researcher.md` | ✅ KEEP | Deep research, Jem persona |
| 3 | `tester` | `.opencode/agents/tester.md` | ✅ KEEP | Quality gate, stress tests |
| 4 | `scribe` | `.opencode/agents/scribe.md` | ✅ KEEP | Documentation, gnosis distillation |
| 5 | `overseer` | `.opencode/agents/overseer.md` | ✅ KEEP | Strategic direction (DeepSeek V4) |
| 6 | `reviewer` | `.opencode/agents/reviewer.md` | ✅ KEEP | Code review, compliance |
| 7 | `opencode-expert` | `.opencode/agents/opencode-expert.md` | ✅ KEEP | CLI config, platform awareness |
| 8 | `kali` | `.opencode/agents/kali.md` | ✅ KEEP | MaKaLi: Grand Oversoul |
| 9 | `maat` | `.opencode/agents/maat.md` | ✅ KEEP | MaKaLi: Light Oversoul |
| 10 | `lilith` | `.opencode/agents/lilith.md` | ✅ KEEP | MaKaLi: Dark Oversoul |
| 11 | `jem-2.0` | `.opencode/modes/jem-2.0.md` | ✅ KEEP | Custom research mode |
| 12 | `isis` | `.opencode/agents/isis.md` | ❌ REMOVE | Redundant — Isis is an entity, not a mode |
| 13 | `OMEGAVERSE_INSTRUCTIONS` | `.opencode/agents/OMEGAVERSE_INSTRUCTIONS.md` | ✂️→📄 MOVE | Is a reference doc, not an agent. Move to `docs/gnosis/omni/OMEGAVERSE_VISION.md` |
| 14 | `malkuth` | `~/.config/opencode/opencode.json` | ❌ REMOVE | OpenCode‑Zen internal — not part of Omega project |
| 15–24 | `binah`, `daath`, `yesod`, `architect`, `security`, `explore`, `general`, `minimax`, `build`, `plan` | `~/.config/opencode/opencode.json` | ❌ REMOVE | Same — OpenCode‑Zen internal agents |

---

## Execution Steps (for Gemma)

### Step 1: Remove project agents
```bash
rm .opencode/agents/isis.md
mv .opencode/agents/OMEGAVERSE_INSTRUCTIONS.md docs/gnosis/omni/OMEGAVERSE_VISION.md
```

### Step 2: Clean global config
Edit `~/.config/opencode/opencode.json` — remove the `"agent"` block entirely (these are OpenCode‑Zen internal agents that do not belong in the Omega project). Keep only:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "big-pickle",
  "instructions": [
    "~/Documents/Xoe-NovAi/omega-engine/AGENTS.md",
    "~/Documents/Xoe-NovAi/omega-engine/ORACLE_STACK.md"
  ],
  "permission": { ... }
}
```

### Step 3: Verify result
```bash
ls .opencode/agents/ | wc -l    # should be ≤11
ls .opencode/modes/ | wc -l     # should be ≥1
cat ~/.config/opencode/opencode.json | grep -c '"agent"'  # should be 0
```

---

## Target State

```
.opencode/
├── agents/
│   ├── builder.md
│   ├── kali.md
│   ├── lilith.md
│   ├── maat.md
│   ├── opencode-expert.md
│   ├── overseer.md
│   ├── researcher.md
│   ├── reviewer.md
│   ├── scribe.md
│   └── tester.md          (10 agent files)
├── modes/
│   └── jem-2.0.md          (1 mode file)
├── skills/                 (existing — unchanged)
├── MANIFEST.md             (update §2 Active Operational Modes to match)
```

---

*Design approved by Overseer. Ready for Gemma execution.*
