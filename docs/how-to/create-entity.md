# Create a New Entity
# ⬡ OMEGA ⬡ JEM ⬡ la-docs ⬡ how-to ⬡ create-entity

This guide explains how to add a new entity to the Omega Engine.

## 1. Define the Entity YAML
Create a file in `config/wads/<your-wad>/entities.yaml` or a separate file in `data/entities/<name>/soul.yaml`.

### Required Fields
- `name`: The canonical name of the entity.
- `role`: The primary function (e.g., `researcher`, `sysadmin`).
- `domains`: A list of keywords the Oracle uses for routing.
- `slots`: A list of slot IDs (e.g., `["P1"]`) if the entity occupies a pillar.

## 2. Awaken the Entity
Use the CLI to register the entity:
```bash
omega add-entity "MyNewEntity" --role "Expert" --domains "ai,robotics"
```

## 3. Verify Workspace
The `EntityWorkspaceManager` will automatically create:
- `data/entities/mynewentity/soul.yaml`
- `data/entities/mynewentity/knowledge/`
- `data/entities/mynewentity/workspace/`

## 4. First Interaction
Summon the entity to verify its identity:
```bash
omega summon MyNewEntity "Hello, who are you?"
```

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: la-docs | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
