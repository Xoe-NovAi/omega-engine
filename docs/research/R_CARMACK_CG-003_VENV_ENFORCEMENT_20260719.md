# 🔱 CG-003: Venv Enforcement CI Gate
**AP Token**: `AP-CARMACK-CG003-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19

---

## 🎯 Research Target
How to inject `source .venv/bin/activate &&` into every OpenCode `task()` subagent spawn + CI gate for `sys.prefix` verification

---

## 📋 Primary Source Findings

### OpenCode Subagent Spawn Mechanism

From OpenCode source (`packages/opencode/src/session/prompt.ts` and agent configs):

1. **Agent config** (`.opencode/agent/*.md`) defines:
   - `model`: which model to use
   - `permission`: tool allow/deny lists
   - **No built-in venv activation field**

2. **Task tool** (`packages/opencode/src/tool/task.ts`):
   - Spawns child session via `session.create()`
   - Passes `prompt` + `model` + `permission` overrides
   - **No environment variable injection hook**

3. **System prompt construction** (`packages/opencode/src/session/prompt.ts`):
   - Builds system prompt from: environment block + AGENTS.md + agent prompt + instructions
   - **Hook point**: `experimental.chat.system.transform` plugin API

### OpenCode Plugin Hook for System Prompt Injection

```typescript
// ~/.config/opencode/plugin/venv-injector.ts
import type { Plugin } from "@opencode-ai/plugin"

export const VenvInjector: Plugin = async ({ client }) => {
  return {
    "experimental.chat.system.transform": async (input, output) => {
      // Inject venv activation into EVERY subagent's system prompt
      const venvBlock = `
## VIRTUAL ENVIRONMENT (MANDATORY - M24)
All Python operations MUST run within the project virtual environment.
Prefix every command with: source .venv/bin/activate &&
NEVER use --break-system-packages, --user, or bare pip install.
Current venv: ${process.env.VIRTUAL_ENV || ".venv (not activated)"}
Python: ${process.env.PYTHON_PATH || ".venv/bin/python"}
`
      return output + venvBlock
    }
  }
}
```

### Subagent Prompt Template (Injected via AGENTS.md)

Per OpenCode docs: **AGENTS.md is injected into every fresh-context subagent**.

```markdown
# AGENTS.md (Project Root)

## M24 Venv Sovereignty — NON-NEGOTIABLE
Every Python command MUST be prefixed:
```bash
source .venv/bin/activate && python -m pytest
source .venv/bin/activate && pip install package
.venv/bin/pip install package  # Absolute path alternative
```

**FORBIDDEN** (CI will fail):
- `pip install --break-system-packages`
- `pip install --user`
- `python -m pip install` (without venv activation)
- Any command not prefixed with venv activation

**CI Gate**: `sys.prefix` MUST equal `.venv` path. Check runs in GitHub Actions.
```

---

## 🔧 CI Gate Implementation

### GitHub Actions: `.github/workflows/venv-enforcement.yml`

```yaml
name: Venv Sovereignty Enforcement (M24)

on:
  push:
    branches: [main]
  pull_request:
  workflow_call:  # Allow subagent workflows to call this

jobs:
  venv-check:
    name: Verify Venv Isolation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
          cache-dependency-path: |
            **/requirements*.txt
            **/pyproject.toml
      
      - name: Create Venv
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -e ".[dev]"
      
      - name: Verify sys.prefix == .venv
        run: |
          source .venv/bin/activate
          python -c "
import sys
import os
venv_path = os.path.abspath('.venv')
actual_prefix = os.path.abspath(sys.prefix)
if actual_prefix != venv_path:
    print(f'FAIL: sys.prefix={actual_prefix} != venv={venv_path}')
    exit(1)
print(f'OK: sys.prefix={actual_prefix}')
"
      
      - name: Scan for Forbidden Patterns
        run: |
          # Check all Python files for forbidden patterns
          FORBIDDEN=(
            "--break-system-packages"
            "--user"
            "pip install [^&]*$"  # bare pip install without venv prefix
          )
          for pattern in "${FORBIDDEN[@]}"; do
            if grep -r "$pattern" --include="*.py" --include="*.sh" --include="*.md" . ; then
              echo "FAIL: Found forbidden pattern: $pattern"
              exit 1
            fi
          done
          echo "OK: No forbidden patterns found"

  subagent-venv-check:
    name: Verify Subagent Prompt Injection
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Verify AGENTS.md Contains Venv Mandate
        run: |
          if ! grep -q "VIRTUAL ENVIRONMENT (MANDATORY - M24)" AGENTS.md; then
            echo "FAIL: AGENTS.md missing M24 venv mandate"
            exit 1
          fi
          if ! grep -q "source .venv/bin/activate &&" AGENTS.md; then
            echo "FAIL: AGENTS.md missing venv activation prefix"
            exit 1
          fi
          echo "OK: AGENTS.md contains M24 mandate"
      
      - name: Verify OpenCode Plugin Exists
        run: |
          if [ ! -f ~/.config/opencode/plugin/venv-injector.ts ]; then
            echo "FAIL: venv-injector plugin not installed"
            exit 1
          fi
          echo "OK: Plugin installed"
```

### Pre-commit Hook: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: venv-sovereignty-check
        name: M24 Venv Sovereignty Check
        entry: bash -c '
          if grep -r "--break-system-packages\|--user" --include="*.py" --include="*.sh" .; then
            echo "FAIL: Forbidden pip flags detected"
            exit 1
          fi
          if grep -r "pip install [^&]*$" --include="*.py" --include="*.sh" . | grep -v "source .venv/bin/activate &&" | grep -v ".venv/bin/pip"; then
            echo "FAIL: Bare pip install without venv activation"
            exit 1
          fi
        '
        language: system
        stages: [commit]
```

---

## 🎯 Subagent Prompt Template (For `task()` Tool)

When spawning subagents via `task()`, the prompt MUST include:

```python
# In agent code that spawns subagents:
subagent_prompt = f"""
{task_description}

## M24 VENV SOVEREIGNTY — INJECTED INTO YOUR SYSTEM PROMPT
You are running in a subagent context. The project virtual environment is at:
  VIRTUAL_ENV=.venv
  PYTHON_PATH=.venv/bin/python

ALL Python operations MUST use:
  source .venv/bin/activate && <command>
  OR
  .venv/bin/<command>

NEVER use: --break-system-packages, --user, or bare pip/python.
The CI gate will verify sys.prefix == .venv path.
"""
```

---

## 🔬 id Software Qualification Gate

| Aspect | id Software Analog | M24 Venv Enforcement |
|--------|-------------------|---------------------|
| **Constraint** | 15W TDP, no active cooling | System Python pollution breaks reproducibility |
| **Technique** | Zone memory allocator (tagged, purgeable) | Venv isolation + CI gate + prompt injection |
| **Justification** | Fragmentation kills performance silently | `--break-system-packages` pollutes globally, silent breakage |
| **Scope** | Engine memory only | All Python operations in project |

**Verdict**: **PASSES** — System package pollution is a real constraint (P3 Engineering incident), not cargo-cult.

---

## 📝 Implementation Checklist

- [ ] Create `~/.config/opencode/plugin/venv-injector.ts` plugin
- [ ] Add M24 mandate block to `AGENTS.md` (project root)
- [ ] Add `.github/workflows/venv-enforcement.yml`
- [ ] Add pre-commit hook for forbidden patterns
- [ ] Update all agent spawn sites to inject venv context
- [ ] Add `make venv-check` target
- [ ] Verify subagent inherits venv mandate via AGENTS.md

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
