# Skills Opt-In Configuration — permission.skill Patterns

**Authority**: Phase 1 Plan + Carmack Review (Lazy Skills pattern) · **REMEDIATED 2026-08-21** per Architect ruling Q2  
**Mechanism**: `permission.skill` glob patterns in `opencode.json` (+ optional per-agent overrides) — the REAL upstream lever  
**Superseded approach**: `auto_load:` SKILL.md frontmatter — **NOT an opencode feature** (zod parses only `name`/`description`; web Q-B5). Original sed-loop plan was a no-op. Full audit: `09_SPEC_DEVIATIONS.md` DEV-04. Hazard ref: N7_DOMAIN_INDEX D8.

---

## How Skills Actually Load (verified)

1. Discovery scans `.opencode/skills/*/SKILL.md`, `~/.config/opencode/skills/`, `.claude/skills/`, `.agents/skills/`.
2. Only `name` + `description` are advertised — inside the `skill` tool description (`<available_skills>` block).
3. Full body enters context ONLY when an agent calls `skill({name})`.
4. `Skill.available(agent)` filters by `Permission.evaluate("skill", name, agent.permission)`:
   - `allow` → visible/loadable
   - `deny` → **hidden from the agent entirely** (not advertised, load rejected)
   - `ask` → prompts on load

**Token honesty (DEV-05)**: skills were ALREADY on-demand (RESEARCH_EXPLORE_LOCAL T6). The original
"23K → 150 tokens" claim assumed upfront injection — false premise. Real Phase 1 saving = shrinking
the advertisement list (~22 × ~50 tok ≈ 1.1K → ~150 tok for 3 visible). Modest but real; and denial
also prevents accidental loads of heavy utility skills.

## Core Set (remain visible to all agents)

| Skill | Why visible |
|-------|-------------|
| `research` | Core research capability — researcher agent constantly |
| `spec-generator` | Spec generation — kali/maat implementation specs |
| `knowledge-miner` | Legacy mining — roc_racoon pattern extraction |

All other repo skills are denied globally by default; any agent that legitimately needs one gets a
targeted `allow` override in its own agent config (explicit > ambient).

## Implementation — opencode.json (global permission block)

```json
{
  "permission": {
    "skill": {
      "research": "allow",
      "spec-generator": "allow",
      "knowledge-miner": "allow",
      "legacy-pattern-miner": "deny",
      "blitz-tunnel": "deny",
      "blitz-validate": "deny",
      "git-secret-scrub": "deny",
      "hf-cli": "deny",
      "omega-doc-architect": "deny",
      "pr-readiness-checker": "deny",
      "provider-validator": "deny",
      "sovereign-refinement-protocol": "deny",
      "sovereign-search": "deny"
    }
  }
}
```

Notes:
- Exact-name keys, not wildcards, for auditability. A `*-tool` wildcard would be tempting for
  built-ins, but built-in tool skills (#14–22 of the original table) mostly have no repo SKILL.md —
  DD-II-3 found the skill list drifted from the spec's 13-name sed loops. Deny only what exists.
- Per-agent override example (researcher may also mine):

```json
"agent": {
  "researcher": {
    "permission": {
      "skill": { "legacy-pattern-miner": "allow", "sovereign-search": "allow" }
    }
  }
}
```

## Rollback

```bash
# Remove the permission.skill block from opencode.json (git checkout or jq del):
jq 'del(.permission.skill)' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json
```

All skills return to default visibility (allow). No SKILL.md files are touched by this subtask.

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ci_phase1_spec ⬡ 2026-08-20 · REMEDIATED N7 2026-08-21*
