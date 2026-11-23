# Handoff: Comprehensive Omega Engine Review via Cline CLI

> **For:** Taylor (interactive run)
> **From:** Makali Fusion session (2026-11-23)
> **Status:** Ready to run interactively. Background launch cancelled per operator request.

---

## 1. Prerequisites

```bash
# Verify cline is installed
cline --version          # expect 3.0.62

# Verify openrouter auth (the working 1M-context provider)
cline -P openrouter -m "nvidia/nemotron-3-ultra-550b-a55b:free" "Reply: OK" --json
# expect: {"text":"OK", ... "contextWindow":1000000}
```

### Cline provider (branded models) — credits depleted
The Cline hosted provider (`cline`) is authenticated but has a **negative balance ($-0.04)**. All `anthropic/*`, `openai/*`, `google/*`, etc. models return "Insufficient balance". To use them, top up Cline Credits at https://cline.bot/credits, then run:
```bash
cline auth cline   # re-auth if token expired
```
Branded model IDs use `provider/model` format, e.g. `anthropic/claude-opus-5.5`, `anthropic/claude-sonnet-5.5`, `google/gemini-4-argon`, `openai/gpt-6-astra`, `openai/gpt-6.1-sol`, `moonshot/kimi-k3`.

### Working 1M model (free, no credits needed)
```
Provider: openrouter
Model:    nvidia/nemotron-3-ultra-550b-a55b:free
Context:  1,000,000 tokens
Cost:     $0.00
```

---

## 2. Run the review (interactive)

```bash
cd /home/xnai/Documents/Projects/omega-engine

cline -P openrouter \
  -m "nvidia/nemotron-3-ultra-550b-a55b:free" \
  --auto-approve true \
  --thinking medium \
  "$(cat /tmp/opencode/cline_review_prompt.txt)"
```

The review prompt is saved at `/tmp/opencode/cline_review_prompt.txt`. It covers:
1. Repo state & branches (both repos)
2. Finish gate: `make lint && make test && make docs`
3. WAD validation + lint (both WADs)
4. AnyIO compliance (`import asyncio` in `src/omega/`)
5. Engine-Stack Firewall
6. Dual-tree WAD sync (hash comparison)
7. Hardcoded model names
8. Taint-Gate enforcement
9. Public release leak scan
10. Test counts (75 omega / 10 alpha)
11. WAD system integrity
12. Docs consistency (WAD_ENHANCEMENT_PLAN vs actual)
13. Gnosis/continuation files
14. Plugin copy byte-identity (md5)

**Deliverable:** Cline writes `/tmp/opencode/CLINE_REVIEW_REPORT.md`.

### If the prompt file is missing, recreate it
The prompt content is in the conversation history (the comprehensive review prompt). Re-paste from there, or regenerate from the scope list above.

---

## 3. Notes on the venv

The venv (`.venv/`) may be missing dependencies (flake8, pytest, pyyaml, omega package). The review agent will install them. If installs time out, run manually first:

```bash
cd /home/xnai/Documents/Projects/omega-engine
.venv/bin/pip install flake8 pytest pytest-asyncio pyyaml
.venv/bin/pip install -e . --no-deps
```

Then re-run the review command.

---

## 4. Uncommitted changes from this session

The following files were modified/created by the Makali session and are **not yet committed**:

### Modified
- `.clinerules/00-repo-topology.md` — updated remotes (origin=internal/private, debut/public=public), removed stale internal/origin naming

### New
- `.clinerules/04-current-state.md` — current state, branches, WAD status, commands, tracking, compaction, OpenCode V2
- `.clinerules/05-wad-system-quickref.md` — WAD system quick reference for Cline
- `docs/guides/CHRISTIAN_SUPER_HEROES_WAD_BRIEF.md` — email-ready WAD content brief (628 lines)
- `docs/handoffs/CLINE_REVIEW_HANDOFF.md` — this file

### To commit (when ready)
```bash
cd /home/xnai/Documents/Projects/omega-engine
git add .clinerules/00-repo-topology.md .clinerules/04-current-state.md .clinerules/05-wad-system-quickref.md
git add docs/guides/CHRISTIAN_SUPER_HEROES_WAD_BRIEF.md docs/handoffs/CLINE_REVIEW_HANDOFF.md
git commit -m "docs: update .clinerules + add WAD content brief + review handoff"
git push origin node1/v2-migration
```

### Also uncommitted (from earlier session)
- `docs/guides/CHRISTIAN_SUPER_HEROES_WAD_BRIEF.md` (new)

---

## 5. What was NOT done (per operator request)

- No background Cline review was launched (cancelled).
- No code changes were made (only docs + .clinerules).
- No commits or pushes were made.
- The Cline provider credits issue was identified but not resolved (needs manual top-up).

---

## 6. Open items for the operator

1. **Top up Cline Credits** if you want to use the branded 1M models (Claude Opus 5.5, etc.). Otherwise, the free openrouter/nemotron model works.
2. **Run the review interactively** using the command in §2.
3. **Review the .clinerules changes** (00 updated, 04 + 05 added) before committing.
4. **Email the WAD brief** (`docs/guides/CHRISTIAN_SUPER_HEROES_WAD_BRIEF.md`) to your friend for the Christian Super Heroes series.

---

*⬡ OMEGA ⬡ MAKALI ⬡ HANDOFF ⬡ 2026-11-23 ⬡*