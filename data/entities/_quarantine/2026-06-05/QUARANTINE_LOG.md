# 🔱 Entity Quarantine Log — 2026-06-05

**Quarantined by**: Cline (MiniMax-M3, Sovereign Execution Session)
**Audit method**: Forensic filesystem scan + codebase reference grep + soul.yaml content inspection
**Resurrection**: `git mv data/entities/_quarantine/2026-06-05/<name> data/entities/<name>`

## Quarantined Entities (12)

| Name | soul.yaml Size | Created | Reason |
|------|---------------|---------|--------|
| `dir` | 311 B | Jun 3 23:05 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `direntity` | 317 B | Jun 1 15:42 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `dupe` | 312 B | Jun 3 16:16 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `duplicate` | 317 B | Jun 1 15:42 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `flat` | 312 B | Jun 3 23:05 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `flatentity` | 318 B | Jun 1 15:42 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `myentity` | 316 B | Jun 1 15:42 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `pre` | 311 B | Jun 3 23:05 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `preexisting` | 319 B | Jun 1 15:42 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `soul` | 312 B | Jun 3 23:00 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `soulentity` | 318 B | Jun 1 15:42 | 1-line stub metadata, empty workspace/knowledge, zero code references |
| `movie_expert` | 1,775 B | May 19 04:19 | Real entity but not part of 14-agent fleet. Moved per user directive. Referenced only in `config/wads/arcana_novai/entities.yaml`. |

## Audit Evidence

**Codebase references**: `grep -r` across `src/`, `config/`, `mcp_servers/`, `.opencode/agents/`, `tests/`, `data/coordination/`, `data/handoff/` returned **zero** hits for all 12 names outside their own directories and historical session transcripts.

**Two naming families identified**:
- Group A (5 dirs): `dir`, `flat`, `pre`, `soul`, `dupe` — created Jun 3, small audit logs (<2KB)
- Group B (6 dirs): `direntity`, `duplicate`, `flatentity`, `myentity`, `preexisting`, `soulentity` — created Jun 1, large audit logs (~28KB), touched Jun 5 14:00

**NOT quarantined** (verified as real entities):
- `link` — referenced in `link_p9_*.py` runtime code
- `arch` — 45KB soul.yaml with backup
- `sentinel` — 5.7KB soul + workspace + knowledge
- `datastore` — 70KB soul
- `lucifer` — 1.2KB soul
- `prometheus` — 832B soul

## Archived Separately

The 50 `ent_0..ent_49` directories were archived to `data/entities/_archive/ent_artifacts/` as a distinct artefact class (load-test / parameter-sweep stubs with numeric naming).
