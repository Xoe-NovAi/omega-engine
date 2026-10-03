# 🔱 Tutorial: How to Create a WAD
**AP Token**: `AP-TUTORIAL-WAD-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_user ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Step-by-step tutorial for creating a WAD (Where's All Data) bundle for the Omega Engine.
**Prerequisites**: Python 3.11+, `omega-engine` repo cloned, `omega.cli.bundle` available
**Tags**: tutorial, wad, bundle, content, distribution

---

## Overview

This tutorial walks through creating a **WAD (Where's All Data)** bundle — the Omega Engine's content distribution format, inspired by id Software's WAD system from Doom (1993).

**What you'll build**: A complete WAD bundle containing a custom entity, skill, and configuration.

**Time estimate**: 20-30 minutes

---

## Prerequisites

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate

# Verify CLI works
python -m omega.cli.bundle --help
```

---

## Understanding WAD Structure

A WAD bundle is a structured archive with this layout:

```
my_wad.wad
├── manifest.json          # Metadata: name, version, author, dependencies
├── content/               # Content files
│   ├── entities/          # Entity definitions (SOUL.md + config)
│   ├── skills/            # Skill definitions (SKILL.md)
│   ├── configs/           # Configuration files (YAML)
│   └── prompts/           # Prompt templates
└── signatures/            # Cryptographic signatures (optional)
```

**Heritage**: `[id-soft: doom-1993] WAD System — Engine-content separation philosophy`

---

## Step 1: Prepare Content Directory

Create a working directory with your content:

```bash
mkdir -p my_wad_content/{entities,skills,configs,prompts}
```

### Create an Entity

`my_wad_content/entities/my_entity/SOUL.md`:

```markdown
# 🔱 My Custom Entity
**AP Token**: `AP-ENTITY-MY_ENTITY-v1.0.0`
⬡ OMEGA ⬡ MY_ENTITY ⬡ opencode ⬡ trc_doc_agent ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: A custom entity for demonstrating WAD creation.
**Tags**: custom, demo, tutorial
**Cross-references**: 

---

## Identity

- **Name**: MyEntity
- **Role**: Demonstrator
- **Slots**: ["P1"]
- **Domains**: ["tutorial", "demo"]

## Configuration

```yaml
model_preferences:
  by_domain:
    tutorial: ["qwen3-1.7b-local"]
    demo: ["gemma-4b-local"]
```

## Personality

I am a demonstration entity created for the WAD tutorial. I help users understand how to package entities into WAD bundles.

## Capabilities

- Explain WAD structure
- Demonstrate entity packaging
- Answer tutorial questions
```

`my_wad_content/entities/my_entity/config.yaml`:

```yaml
# Entity runtime configuration
model: "qwen3-1.7b-local"
temperature: 0.7
max_tokens: 4096
system_prompt: |
  You are MyEntity, a helpful demonstration entity.
  Keep responses concise and tutorial-focused.
```

### Create a Skill

`my_wad_content/skills/demo_skill/SKILL.md`:

```markdown
# Skill: demo_skill
description: "A demonstration skill for WAD tutorial"
version: "1.0.0"
author: "Tutorial Author"

# Commands
commands:
  - name: "demo_hello"
    description: "Say hello from the demo skill"
    arguments:
      - name: "name"
        type: "string"
        required: false
        default: "World"
```

`my_wad_content/skills/demo_skill/__init__.py`:

```python
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""Demo Skill Implementation."""

async def demo_hello(name: str = "World") -> str:
    """Say hello from the demo skill."""
    return f"Hello, {name}! This is the demo skill from the WAD tutorial."
```

### Create a Config

`my_wad_content/configs/demo_config.yaml`:

```yaml
# Demo configuration for WAD tutorial
demo:
  enabled: true
  message: "This config came from a WAD bundle!"
  settings:
    verbosity: "info"
    max_retries: 3
```

### Create a Prompt Template

`my_wad_content/prompts/demo_prompt.md`:

```markdown
# Demo Prompt Template

You are a helpful assistant demonstrating WAD bundle capabilities.

## Task
{{task_description}}

## Context
{{context}}

## Instructions
1. Be concise
2. Reference the WAD structure
3. Explain the heritage: [id-soft: doom-1993] WAD System
```

---

## Step 2: Create the Manifest

`my_wad_content/manifest.json`:

```json
{
  "name": "tutorial-wad",
  "version": "1.0.0",
  "author": "Tutorial Author",
  "description": "A demonstration WAD bundle for the Omega Engine tutorial",
  "license": "Apache-2.0",
  "homepage": "https://github.com/Xoe-NovAi/omega-engine",
  "dependencies": {
    "omega-engine": ">=1.0.0"
  },
  "content": {
    "entities": ["my_entity"],
    "skills": ["demo_skill"],
    "configs": ["demo_config.yaml"],
    "prompts": ["demo_prompt.md"]
  },
  "tags": ["tutorial", "demo", "wad"],
  "created_at": "2026-10-02T00:00:00Z"
}
```

---

## Step 3: Build the WAD

```bash
# Create the WAD bundle
python -m omega.cli.bundle create my_wad_content tutorial_wad.wad \
  --name "Tutorial WAD" \
  --version "1.0.0" \
  --author "Tutorial Author"
```

**Output**:
```
Creating WAD bundle: tutorial_wad.wad
Adding: manifest.json
Adding: content/entities/my_entity/SOUL.md
Adding: content/entities/my_entity/config.yaml
Adding: content/skills/demo_skill/SKILL.md
Adding: content/skills/demo_skill/__init__.py
Adding: content/configs/demo_config.yaml
Adding: content/prompts/demo_prompt.md
WAD bundle created: tutorial_wad.wad (12.3 KB)
```

---

## Step 4: Inspect the WAD

```bash
# Inspect contents
python -m omega.cli.bundle inspect tutorial_wad.wad
```

**Output**:
```
WAD Bundle: tutorial_wad.wad
==============================
Name: Tutorial WAD
Version: 1.0.0
Author: Tutorial Author
Description: A demonstration WAD bundle for the Omega Engine tutorial
License: Apache-2.0

Contents:
  manifest.json
  content/
    entities/
      my_entity/
        SOUL.md
        config.yaml
    skills/
      demo_skill/
        SKILL.md
        __init__.py
    configs/
      demo_config.yaml
    prompts/
      demo_prompt.md

Total files: 7
Total size: 12.3 KB
```

---

## Step 5: Validate the WAD

```bash
# Validate structure
python -m omega.cli.bundle validate tutorial_wad.wad
```

**Output**:
```
✅ Manifest valid
✅ All referenced files present
✅ Entity SOUL.md format valid
✅ Skill SKILL.md format valid
✅ Config YAML syntax valid
✅ No missing dependencies
Validation passed!
```

---

## Step 6: Extract and Test

```bash
# Extract to test directory
mkdir test_extract
python -m omega.cli.bundle extract tutorial_wad.wad test_extract

# Verify extracted content
ls -la test_extract/
cat test_extract/content/entities/my_entity/SOUL.md
```

---

## Step 7: Deploy (Optional)

To install the WAD in your Omega Engine:

```bash
# Copy to WAD directory (typically config/wads/)
cp tutorial_wad.wad config/wads/

# Or install via CLI (if supported)
python -m omega.cli.bundle install tutorial_wad.wad
```

The WAD will be available on next engine restart.

---

## Advanced: Signing the WAD

For production WADs, add cryptographic signatures:

```bash
# Generate keypair (one-time)
openssl genpkey -algorithm ED25519 -out wad_private.key
openssl pkey -in wad_private.key -pubout -out wad_public.key

# Sign the WAD
python -m omega.cli.bundle sign tutorial_wad.wad \
  --key wad_private.key \
  --output tutorial_wad.wad.sig

# Verify signature
python -m omega.cli.bundle verify tutorial_wad.wad \
  --key wad_public.key \
  --signature tutorial_wad.wad.sig
```

---

## WAD Manifest Schema

```json
{
  "name": "string (kebab-case, required)",
  "version": "string (semver, required)",
  "author": "string (required)",
  "description": "string (required)",
  "license": "string (SPDX, optional)",
  "homepage": "string (URL, optional)",
  "dependencies": {
    "omega-engine": "string (semver range, optional)"
  },
  "content": {
    "entities": ["string (entity_id)"],
    "skills": ["string (skill_name)"],
    "configs": ["string (filename)"],
    "prompts": ["string (filename)"]
  },
  "tags": ["string"],
  "created_at": "string (ISO 8601, required)"
}
```

---

## Best Practices

| Practice | Reason |
|----------|--------|
| Use kebab-case for WAD names | Consistency, filesystem safety |
| Pin `omega-engine` dependency | Avoid breaking changes |
| Include all content in manifest | Validation catches missing files |
| Sign production WADs | Supply chain security |
| Test extraction before deploy | Catch packaging errors early |
| Keep WADs focused | Single responsibility per WAD |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `manifest.json` not found | Ensure manifest.json is in source root |
| Entity not loading | Check SOUL.md format; validate YAML frontmatter |
| Skill not registering | Ensure SKILL.md has correct format; check `__init__.py` |
| Config not applying | Verify YAML syntax; check config path in manifest |
| Validation fails | Run `bundle validate` for detailed errors |

---

## Next Steps

1. **Create a real entity** — Replace demo with your actual agent
2. **Add tests** — Include test cases in WAD for validation
3. **Publish** — Share via Omega Exchange or GitHub releases
4. **Version** — Follow semver; increment on changes

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ TUTORIAL-WAD-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

