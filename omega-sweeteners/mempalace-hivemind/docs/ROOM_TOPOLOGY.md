# Hivemind Room Topology — Omega Engine Standard

**Version**: 1.0 | **Scope**: All Omega Engine deployments

---

## 🏗️ Wing → Room → Topic Hierarchy

```
MemPalace (sqlite_exact.sqlite3)
│
├── project/omega-engine          ← Wing: Project-level coordination
│   ├── federation                ← Room: Mesh ops, ACL, NFS, Tailscale
│   │   ├── pr-delivery          ← Topic: PR sweetener deliveries
│   │   ├── acl-migration        ← Topic: Phase A/B ACL transitions
│   │   ├── nfs-ops              ← Topic: NFS mount/unmount events
│   │   └── tailscale-ops        ← Topic: Tailscale SSH, tag changes
│   │
│   ├── cicd                      ← Room: GitHub Actions, builds, deploys
│   │   ├── workflow-run         ← Topic: Individual workflow runs
│   │   ├── build-status         ← Topic: Build pass/fail
│   │   ├── deploy-status        ← Topic: Deployment status
│   │   └── artifact-ready       ← Topic: Artifacts ready for sync
│   │
│   ├── agents                    ← Room: Agent registry & handoffs
│   │   ├── spawn                ← Topic: New agent created
│   │   ├── retire               ← Topic: Agent retired
│   │   ├── handoff              ← Topic: Cross-agent task handoff
│   │   ├── status               ← Topic: Agent health/status
│   │   └── sync                 ← Topic: Cross-node agent sync
│   │
│   ├── sync                      ← Room: Airgap/USB sync ceremonies
│   │   ├── payload-out          ← Topic: Node 0 → Node 1 payload
│   │   ├── payload-in           ← Topic: Node 1 → Node 0 payload
│   │   ├── manifest             ← Topic: SHA256 manifests
│   │   └── ceremony             ← Topic: Ceremony state
│   │
│   └── gnosis                   ← Room: Gnosis/ritual events
│       ├── ritual-start         ← Topic: Pre-compaction ritual start
│       ├── ritual-end           ← Topic: Pre-compaction ritual end
│       ├── reflection           ← Topic: Human reflection captured
│       └── compaction           ← Topic: Context compaction events
│
├── gnosis                        ← Wing: Internal agent memory
│   ├── rituals                  ← Room: Ritual state & history
│   ├── evolution                ← Room: Evolution log events
│   ├── well                     ← Room: The Well corpus
│   └── identity                 ← Room: Agent identity & state
│
└── well                          ← Wing: The Well corpus
    ├── corrections              ← Room: Correction records
    ├── preferences              ← Room: Preference records
    ├── insights                 ← Room: Insight records
    └── dreams                   ← Room: Dream/aspiration records
```

---

## Room Registry (Canonical)

| Wing | Room | Purpose | Primary Agents | Event Types |
|------|------|---------|----------------|-------------|
| `project/omega-engine` | `federation` | Mesh ops, ACL, NFS, Tailscale | `kali-n1`, `makali-n0` | `hivemind.briefing`, `sync.*`, `acl.*` |
| `project/omega-engine` | `cicd` | GitHub Actions, builds, deploys | `kali-n1`, `makali-n0` | `cicd.*`, `build.*`, `deploy.*` |
| `project/omega-engine` | `agents` | Agent registry & handoffs | `kali-n1`, `makali-n0` | `agent.*`, `task.*`, `handoff.*` |
| `project/omega-engine` | `sync` | Airgap/USB sync ceremonies | `kali-n1`, `makali-n0` | `sync.*`, `payload.*`, `manifest.*` |
| `project/omega-engine` | `gnosis` | Rituals, reflections, compactions | `kali-n1` | `ritual.*`, `session.*`, `reflection.*` |
| `gnosis` | `rituals` | Ritual state & history | `kali-n1` | `ritual.*` |
| `gnosis` | `evolution` | Evolution log events | `kali-n1`, `makali-n0` | `evolution.*` |
| `gnosis` | `well` | The Well corpus | `kali-n1`, `makali-n0` | `well.*` |
| `gnosis` | `identity` | Agent identity & state | `kali-n1`, `makali-n0` | `identity.*` |
| `well` | `corrections` | Correction records | `kali-n1`, `makali-n0` | `well.add`, `well.supersede` |
| `well` | `preferences` | Preference records | `kali-n1`, `makali-n0` | `well.add` |
| `well` | `insights` | Insight records | `kali-n1`, `makali-n0` | `well.add` |
| `well` | `dreams` | Dream/aspiration records | `kali-n1`, `makali-n1` | `well.add` |

---

## Topic Naming Convention

```
<domain>.<action>                    # e.g., cicd.build-failed
<domain>.<action>.<qualifier>        # e.g., acl.migration.phase-a
<domain>.<entity>.<action>           # e.g., agent.kali-n1.spawned
```

### Examples

| Topic | Meaning |
|-------|---------|
| `cicd.workflow-failed` | GitHub Actions workflow failed |
| `acl.migration.phase-a` | ACL Phase A migration |
| `acl.migration.phase-b` | ACL Phase B lockdown |
| `sync.payload-out` | Node 0 → Node 1 payload |
| `sync.payload-in` | Node 1 → Node 0 payload |
| `sync.manifest.verify` | Manifest SHA256 verification |
| `agent.kali-n1.spawned` | New agent `kali-n1` created |
| `task.sync-20260922-001.request` | Sync task request |
| `task.sync-20260922-001.reply` | Sync task reply |
| `ritual.pre-compact.start` | Pre-compaction ritual started |
| `ritual.pre-compact.end` | Pre-compaction ritual completed |
| `session.kali-n1.compacted` | Session compaction occurred |

---

## Room Access Control

| Room | Read | Write | Admin |
|------|------|-------|-------|
| `federation` | `kali-n1`, `makali-n0` | `kali-n1`, `makali-n0` | `xnai-n1`, `arcana-n0` |
| `cicd` | `kali-n1`, `makali-n0` | `kali-n1`, `makali-n0` | `xnai-n1` |
| `agents` | `kali-n1`, `makali-n0` | `kali-n1`, `makali-n0` | `xnai-n1`, `arcana-n0` |
| `sync` | `kali-n1`, `makali-n0` | `kali-n1`, `makali-n0` | `xnai-n1`, `arcana-n0` |
| `gnosis` | `kali-n1` | `kali-n1` | `xnai-n1` |
| `well` | `kali-n1`, `makali-n0` | `kali-n1` | `xnai-n1` |

---

## Subscription Patterns

```python
# Subscribe to all federation events
subscribe(stream="project/omega-engine", room="federation", topic="*")

# Subscribe to CI/CD failures only
subscribe(stream="project/omega-engine", room="cicd", topic="*.failed")

# Subscribe to all agent handoffs
subscribe(stream="project/omega-engine", room="agents", topic="handoff.*")

# Subscribe to sync ceremonies
subscribe(stream="project/omega-engine", room="sync", topic="*")

# Subscribe to all gnosis rituals
subscribe(stream="project/omega-engine", room="gnosis", topic="ritual.*")
```

---

## Validation Rules

1. **Stream** must be registered wing
2. **Room** must exist in wing registry
3. **Topic** must follow naming convention
4. **Events** in room must use registered topic patterns
5. **Agents** must have node suffix matching their deployment

---

*Part of MemPalace Hivemind spec. Room topology is the spatial index for the distributed mind.*