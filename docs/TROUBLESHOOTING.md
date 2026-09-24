# Troubleshooting — Omega Engine Alpha Node 1

**Audience:** Operators and agents diagnosing Node 1.  
**Principle:** Measure the current state, preserve durable data, and recover through the authoritative layer rather than editing projected memory by hand.

## 1. First-response sequence

Run these before changing configuration:

```bash
make status
make env-show
make docs
make gnosis-leash-status
```

Then identify the layer:

```text
Ollama → local model runtime
Python/Open WebUI → user interface
MemPalace → searchable projection
SQLite continuity → authoritative state/event store
Gnosis → reflection/recovery ledger
WanderGround → sibling knowledge system
Federation → external Node 0 dependency
```

## 2. Ollama and inference

### Ollama is not responding

```bash
make status
systemctl status ollama --no-pager
journalctl -u ollama -n 100 --no-pager
```

Recovery:

```bash
make restart
make status
```

If systemd is unavailable, inspect the Ollama process and logs before starting a second daemon. Do not run two Ollama servers against the same model files without understanding the state.

### Throughput collapsed near 0.5 t/s

Check the CPU mask:

```bash
grep -E 'AllowedCPUs|OLLAMA_NUM_THREADS|OLLAMA_MAX_LOADED_MODELS' .env.ollama
systemctl show ollama --property=Environment
```

The Node 1 hybrid profile is:

```text
AllowedCPUs=0-11
OLLAMA_NUM_THREADS=8
```

Do not use physical-P-core-only masking such as `0,2,4,6,8,10`. Measure again with:

```bash
make bench MODEL=phi4-mini
```

### Model reloads or swap thrash occurs

```bash
ollama ps
free -h
zramctl
swapon --show
```

On the 16 GB single-channel Node 1 profile, keep:

```text
OLLAMA_MAX_LOADED_MODELS=1
```

If two models are resident, reduce to one before changing other tuning.

### `env-apply` fails

Check that the environment file exists:

```bash
ls -l .env.ollama
make env-show
```

`env-setup` is not a dry-run command; it requires permission to write the systemd override and restart Ollama.

## 3. Python and HTTP interfaces

### Python cannot import Ollama

```bash
.venv/bin/python3 -c 'import ollama; print("ok")'
make python-setup
make python-test
```

The repository-local `.venv` is separate from the WanderGround venv.

### HTTP server does not start

```bash
make python-serve
curl http://localhost:8000/health
```

The default port is `8000`. To select another port:

```bash
make python-serve PORT=8080
```

If the service is already running, inspect the port before starting another process.

### Open WebUI cannot reach Ollama

```bash
make status
make webui-status
make webui-logs
```

Check:

- Ollama responds on port `11434`;
- the WebUI container can resolve `host.docker.internal`;
- port `3000` is available;
- the container is using the expected Ollama base URL.

Stop and restart only after recording the logs:

```bash
make webui-down
make webui
```

## 4. Memory and WanderGround

### MemPalace is unavailable

MemPalace is a sibling WanderGround service. Check:

```bash
make -C ~/WanderGround status
```

Do not open or mutate the live MemPalace SQLite database directly. The continuity adapter reaches it through the MCP drawer boundary.

### Atlas or 3D viewer is missing

Current Node 1 state is expected to be:

```text
MemPalace: available
spatial/knowledge_atlas.db: absent
viewer on :8088: absent
embedding server on :8090: absent
```

These are target services, not failures of basic local inference. Do not mix current 384-D data with a future 768-D index.

### A 384-D/768-D mismatch is reported

Stop the migration. Do not insert vectors of the wrong dimension into the same `vec0` table.

1. identify the model and dimension;
2. inspect the active index version;
3. keep the legacy index read-only;
4. build a separate shadow index;
5. compare retrieval quality;
6. cut over only after acceptance.

## 5. SQLite continuity

### SQLite version gate fails

```bash
python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'
```

The production floor is:

```text
3.51.3+
or documented fixed backport 3.50.7 / 3.44.6
```

The current Node 1 runtime may be usable for reference tests while below this floor. Do not label it production-safe.

### Pending intent or recovery error

1. stop additional writers;
2. inspect the continuity state and event log;
3. verify artifact hashes and sequence continuity;
4. replay the prepared intent through the kernel;
5. rebuild the checkpoint;
6. project to MemPalace only after SQLite commit succeeds.

Do not “fix” a missing pointer by editing MemPalace directly.

### MemPalace projection failed

The source SQLite event remains authoritative. Retry the projection with the same event ID and idempotency key. A retry must not create a second semantic event.

If repeated projection failures remain, preserve:

- event ID;
- sequence;
- entity ID;
- projection target;
- last successful cursor;
- error and timestamp.

### SQLite or continuity files are on NFS

Do not use NFS for a live SQLite authority. Move the database to local POSIX storage, verify the runtime version, and recover from a signed export or event bundle.

## 6. Gnosis and compaction

### Ledger reports an untriaged captured pack

```bash
make gnosis-ledger
```

Do not use `/compact` until the pack is reflected. Follow the Gnosis reflection procedure or explicitly triage a legacy pack according to its provenance.

### Leash watchdog is degraded

```bash
make gnosis-leash-status
```

Inspect:

```text
~/.config/opencode/plugins/gnosis-leash.js
~/.config/opencode/plugins/state/gnosis-events.jsonl
~/.config/opencode/plugins/state/gnosis-errors.jsonl
```

A degraded leash is a continuity incident; do not suppress it by deleting the error log.

### `/compact` behaved like a normal prompt

`/compact` must be typed alone on a line. Text after it becomes part of the normal prompt.

## 7. Federation

### Federation is unavailable

Check local state first:

```bash
make gnosis-leash-status
make docs
```

Then confirm with Node 0:

- Tailscale tags and policy;
- Node 0 service health;
- MCP endpoint;
- SPIRE identity;
- signed manifest and Git bundle;
- current runtime report.

Do not simulate a successful federation result. A tailnet ping proves reachability, not application authorization.

### WAD loader rejects the manifest

Stop promotion. Compare:

- `wads/arcana_novai/manifest.yaml`;
- Node 0's exact loader schema;
- adapter whitelist;
- hierarchy type;
- entity file envelope;
- WAD signature and dependency manifest.

The current Node 1 manifest is not considered Engine-loadable until Node 0's actual loader accepts it.

### Git bundle verification fails

```bash
git bundle verify <bundle>
git fetch <bundle> <ref>:refs/remotes/<peer>/<ref>
```

Do not merge or run code until prerequisite commits and hashes are verified.

## 8. Data-risk classification

| Situation | Risk | Safe action |
|---|---|---|
| Wrong model loaded | Performance/quality only | Stop benchmark and select the intended model |
| WebUI unavailable | UI availability | Keep Ollama/API running and repair container |
| MemPalace projection failed | Projection consistency | Retry from SQLite event; do not direct-edit palace |
| SQLite version below floor | Durability risk | Keep as reference only; select fixed runtime |
| Tailscale policy changed | Connectivity risk | Use documented Phase A/Phase B sequence |
| WAD hash/signature failed | Supply-chain risk | Quarantine and reject promotion |
| Credential exposed | Security incident | Revoke/rotate and sanitize logs immediately |
| NFS contains live SQLite | Corruption risk | Stop writes and move authority to local storage |

## 9. Escalation format

When escalating, include:

```text
date/time:
command:
working directory:
expected:
observed:
exit code:
model/provider:
host state:
data class:
last known good checkpoint:
files changed:
secrets present: yes/no
```

Never include:

- API keys;
- OAuth tokens;
- SSH/Tailscale private keys;
- cookies;
- private Lilith material;
- raw secret-bearing diagnostic dumps.

## 10. Related documents

- `docs/INSTALLATION.md` — setup and verification;
- `docs/USER_GUIDE.md` — normal workflows;
- `docs/PRIVACY_SECURITY.md` — data and credential policy;
- `docs/AGENT_RUNBOOK.md` — agent/session operations;
- `docs/CONTINUITY_KERNEL.md` — continuity architecture;
- `docs/federation/README.md` — Node 0 federation;
- `docs/HARDWARE.md` — hardware and power state.
