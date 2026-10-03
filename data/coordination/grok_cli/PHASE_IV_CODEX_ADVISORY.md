<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# D-281 Phase IV — Codex Mechanism Separation (Advisory Spec)
**Packet**: `ho_c53a339b155e`  
**Author**: `grok-cli/grok` · 2026-07-17  
**Role**: Advisory only — **do not** write `scripts/` under this packet (M16)

---

## Live evidence

### Hydration block location
`scripts/codex_cat.py` — after groups load, approx **lines 63–76** (not only 63–72):

Hardcoded strings for D-277 sequence:
1. `hivemind_get_awareness`
2. `git status && git log`
3. Read OMEGA_CODEX.md full
4. Read `.opencode/anchored-summary.md`
5. Rehydration report + pause

Plus timestamp footer lines.

### Makefile (fragile subset targets)

| Target | Behavior | Risk |
|--------|----------|------|
| `codex` / `codex-all` | `python3 scripts/codex_cat.py` | Low |
| `codex-mandates` | **overwrites** `scripts/groups.json` then `make codex` | **P0** — no backup/restore |
| `codex-agents` | same | **P0** |
| `codex-arch` | same | **P0** |
| `codex-heritage` | same | **P0** |

If `make codex` fails mid-flight after overwrite, `groups.json` stays specialized → next full codex is wrong.

---

## Spec for Triad

### 1. Create `scripts/hydration_header.md`

Extract the markdown body that is currently appended as Python string literals. Suggested content:

```markdown
## 🔄 HYDRATION SEQUENCE (D-277)

After compaction or restart, execute in strict order:

1. `omega-hub_hivemind_get_awareness()` — Who is here?
2. `git status && git log --oneline -5` — What is committed?
3. Read OMEGA_CODEX.md — FULL file, no limit parameter.
4. Read `.opencode/anchored-summary.md` — What was I doing?
5. Present a rehydration report. Pause. Await user direction.

> Codex generated: {{TIMESTAMP}} | Regenerate: `make codex`
> If timestamp is >24h old, run `make codex` before reading further.

---
```

Use a simple `{{TIMESTAMP}}` placeholder replaced at generate time (stdlib only).

### 2. Refactor `codex_cat.py`

```python
header_path = Path(__file__).resolve().parent / "hydration_header.md"
header = header_path.read_text(encoding="utf-8").replace("{{TIMESTAMP}}", ts)
codex_content.append(header)
```

**Fail-closed**: if header missing, raise explicit error (do not silently skip D-277).

### 3. Makefile restore-on-failure (all four subset targets)

```make
codex-mandates:
	cp scripts/groups.json scripts/groups.json.bak
	@echo '{"mandates": ["SOVEREIGN_MANDATES.md"]}' > scripts/groups.json
	python3 scripts/codex_cat.py || (mv scripts/groups.json.bak scripts/groups.json && exit 1)
	mv scripts/groups.json.bak scripts/groups.json
```

Same pattern for agents/arch/heritage. Prefer a shared macro if Make style allows.

**Better long-term**: pass group filter as CLI arg to `codex_cat.py` so `groups.json` is never mutated (`--groups mandates`). Advisory: Phase IV minimum is backup/restore; CLI filter is Phase IV+.

---

## Test / gate

1. `make codex` produces OMEGA_CODEX with hydration section matching header file.  
2. Force fail after groups overwrite → groups.json restored.  
3. Header edit changes next codex without editing Python.

---

## Verdict

| Item | Status |
|------|--------|
| Kali line range | ~63–76 confirmed; extract all hydration lines |
| Restore pattern | **Mandatory** for subset targets |
| Grok implement under advisory? | **No** |
| Risk if delayed | Medium — wrong groups.json after failed `codex-mandates` |

*Deliverable for `ho_c53a339b155e`.*
