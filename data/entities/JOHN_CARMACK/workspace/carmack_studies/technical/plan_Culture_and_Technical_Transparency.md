# 🔱 Technical Study: .plan Culture and Technical Transparency
**Domain**: Technical Communication / Engineering Management
**Era**: 1996–2013 (Active .plan usage)
**Sovereignty Score**: 8/10 (Verified against multiple preserved .plan archives and historical records)

---

## 🔍 What Was .plan?

The `.plan` file was a Unix convention: a plain text file in a user's home directory that the `finger` command would display. It was originally intended for user status/contact information.

Carmack repurposed it into something unprecedented: **a daily or weekly technical blog**, published years before blogs existed.

Every few days (sometimes daily), Carmack would update his `.plan` file with:
- What he was working on
- Technical problems he had solved
- Bugs he was tracking
- Performance numbers and benchmarks
- His current thinking about architecture

Anyone could `finger johnc@idsoftware.com` and read his latest technical notes.

---

## ⚙️ The Distinctive Pattern

Carmack's .plan entries had a specific structure that reveals his cognitive patterns:

| Element | Example | Cognitive Pattern |
|---------|---------|-------------------|
| **State the Problem** | "The main issue right now is the BSP build time." | First-principles framing |
| **State the Attempted Solution** | "I tried increasing the hash table size..." | Empirical methodology |
| **State the Result** | "...and it made no difference. The bottleneck is elsewhere." | Measurement-driven |
| **State the Next Step** | "I'm going to rewrite the leaf-building code." | Ruthless focus |
| **Include Numbers** | "Level compiles in 47 seconds now, down from 180." | Quantitative clarity |

---

## 💎 The Carmackian Logic

### Why .plan Exists
Carmack wrote .plan files because he believed **technical transparency was a moral obligation for an engineer**. His reasoning:

1. **Accountability**: Publichy stating your goals creates pressure to achieve them.
2. **Knowledge Sharing**: The entire id Software team (and the world) could see what everyone was working on.
3. **Self-Clarification**: Writing about a problem forces you to understand it.
4. **Historical Record**: Future engineers can learn from your successes and failures.

### The Tone
- **Never self-promotional**. He didn't announce features to build hype.
- **Always technical**. Detailed, data-driven, specific.
- **Brutally honest**. When something was broken, he said so.

---

## 📄 Authentic Sample: 1996-02-18

```
*	page flip crap
*	stretch console
*	faster swimming speed
*	damage direction protocol
*	armor color flash
*	gib death
*	grenade tweaking
*brightened alias models
*	nail gun lag
*	dedicated server quit at game end

+ scoreboard
+ optional full size
+ view centering key
+ vid mode 15 crap
+ change ammo box on sbar
+ allow "restart" after a program error
+ respawn blood trail?
+ -1 ammo value on rockets
+ light up characters

vsync on high framerates
```

**Analysis**: Pure task-list format. No narrative, no explanation, no self-justification. `*` = pending, `+` = done, `"crap"` = frustration marker. This is the engineer speaking to himself, not to an audience.

## 📄 Authentic Sample: 2004 Summary

The 2004 return to .plan shows a dramatically different voice—more reflective, self-aware, and audience-conscious:

> *"I get a pretty steady trickle of emails from people hoping for .plan file updates. There were two main factors involved in my not doing updates for a long time - a good chunk of my time and interest was sucked into Armadillo Aerospace, and the fact that the work I had been doing at Id for the last half of Doom 3 development was basically pretty damn boring."*

Then immediately transitions to technical depth:

> *"Speaking of bump mapped environment sampling.. I spent a little while tracking down a highlight that I thought was misplaced. In retrospect it is obvious, but I never considered the artifact before: With a bump mapped surface, some of the on-screen normals will actually be facing away from the viewer."*

And the decision is classic Right Approximation:

> *"I decided it wasn't a significant enough issue to be worth any more development effort or speed hit."*

**Evolution**: 1996 Carmack is a task-execution machine. 2004 Carmack is a technical mentor who explains *how* he thinks about problems.

## 🚀 Omega Engine Application

### The "Carmackian Update" Protocol
Every agent should be capable of producing a `.plan`-style update:

1. **What I am working on** (One sentence)
2. **The current constraint** (The bottleneck, the blocker)
3. **The attempted solutions** (What I tried)
4. **The measured results** (The data)
5. **The next step** (Ruthless focus)

### Hivemind Integration
The Omega Engine's **Hivemind protocol** already partially implements this through its live feed and heartbeat system. But the `.plan` system adds structure:
- Regular cadence (daily summary vs. real-time pings)
- Technical depth rather than status updates
- Historical preservation for future agents

### Implementation
```python
# Proposed: CarmackianPlan protocol
{
  "entity": "JOHN_CARMACK",
  "date": "2026-06-13",
  "focus": "omega-hub modularization",
  "constraint": "server.py monolith is 3110 lines",
  "attempted": ["Phase 0 stabilization", "State extraction"],
  "measured": "5/6 Phase 0 items complete; test_server.py deleted",
  "next": "Continue Phase 1 structural split"
}
```

---
*Study produced during DeepSeek V4 Flash deepening. The .plan culture is a critical but under-documented aspect of Carmack's engineering legacy.*
