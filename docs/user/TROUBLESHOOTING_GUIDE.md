<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Troubleshooting & Debugging Guide
**AP Token**: `AP-TROUBLESHOOTING-GUIDE-v1.0.0`
⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ nemotron-3-ultra ⬡ trc_doc_user ⬡ DOCUMENTATION-HARDENING

**Date**: 2026-07-06
**Purpose**: Comprehensive troubleshooting guide for common issues, debugging techniques, and recovery procedures.

---

## 🚨 Quick Diagnosis

### Run Health Check First
```bash
make infer-status                 # native-gguf server: PIDs, health, memory
make infer-health                 # status + memory + log tail
omega model-status                # providers + models
curl -s http://127.0.0.1:8016/health   # Omega Hub (if running)
```
This reports local inference state, provider status and (for the Hub) uptime.
**There is no `make health` or `make doctor` target in this release** — use the
`infer-*` targets and the `omega` CLI shown above.

---

## 🔧 Common Issues & Solutions

### 1. Permission & Ownership Issues

#### "Permission denied" on files/directories
```bash
# Inspect ownership
ls -la data/ config/ | head -20

# Fix project file ownership (UID 1000)
sudo chown -R "$(id -u):$(id -g)" data/ config/
```
**Root cause**: container operations or manual edits changed file ownership. M6 rule: containers run with `UserNS=keep-id` (never `:U`), which prevents drift.

#### "UID drift detected" warnings
```bash
# Check current ownership
ls -la data/
ls -la config/

# Fix with chown
sudo chown -R "$(id -u):$(id -g)" data/ config/
```

### 2. Python Environment Issues

#### "No module named 'omega'" or import errors
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -e ".[native,cli]"
```

#### "ModuleNotFoundError" for specific packages
```bash
# Check if package is in requirements
grep "package_name" requirements.txt

# Install missing package
.venv/bin/pip install package_name

# Or reinstall all
pip install -e ".[native,cli,dev]"
```

#### "Event loop is closed" warnings
**Status**: Known benign issue from `aiosqlite` thread cleanup during test shutdown.
**Impact**: None - does not affect functionality.
**Action**: Ignore these warnings.

### 3. Test Failures

#### Tests failing after changes
```bash
# make test already stops on first failure (-x)
make test

# Single test, verbose output
make test-debug TEST=test_entity_registry
make test-debug TEST=test_oracle
make test-debug TEST=test_health_monitor
make test-debug TEST=test_error_gauntlet

# Whole suite, parallel
make test-all

# Run with coverage
make test-cov
```

#### Specific test failures
| Test Pattern | Common Cause | Fix |
|--------------|--------------|-----|
| `test_entity_registry` | YAML syntax in entities.yaml | Check YAML syntax |
| `test_oracle` | Provider not available | `omega model-status` |
| `test_health_monitor` | Circuit breaker state | Wait for cooldown, then `omega model-status` |
| `test_error_gauntlet` | Missing error handling | Check error hierarchy |

#### Test count changed

Counts vary by environment (markers, skips, optional deps). **CI is the single
source of truth** for the full-suite result — read the `pytest` job on the PR.
There is no `make test-badge` target and no `TEST_STATUS.md` in this release.

### 4. Inference & Provider Issues

#### Local inference not responding
```bash
# Engine-side provider + model status
omega model-status
omega backends

# native-gguf server state (primary local provider)
make infer-status
make infer-health
```
> **Ollama is enabled by default** in this release (`config/providers.yaml` →
> `providers.ollama.enabled: true`).

#### Provider always falls back to mock
```bash
# Check local inference backends
make infer-status
make infer-models

# Check which providers are enabled
grep -A2 'enabled:' config/providers.yaml | head -30

# Try direct inference
omega talk "hello"
```

#### Circuit breaker tripping too often
```bash
# Check provider health
make infer-status
omega model-status

# Circuit breaker auto-recovers after cooldown (default: 60s)
# Check circuit breaker state in health output
```

#### "No NativeGGUFProvider available"
```bash
# Check if llama-cpp-python is installed
.venv/bin/pip list | grep llama-cpp

# Install if missing
.venv/bin/pip install llama-cpp-python

# Check models.yaml has native-gguf entries
grep -A10 "native-gguf" config/models.yaml
```

### 5. Entity & IWAD Issues

#### Entity not found ("default" response)
```bash
# Check active IWAD
grep active_iwad config/omega.yaml

# Load a different IWAD for one invocation
omega talk "hello" --iwad arcana_novai

# List available entities
omega list-entities
```

#### IWAD switching seems stuck

IWADs are selected in `config/omega.yaml` — there is **no `make wad*` target**:
```bash
grep -A2 'omega:' config/omega.yaml

# Switch by editing: omega.entity.active_iwad: "_omega_default" | "arcana_novai"
# Or override per invocation:
omega talk "hello" --iwad arcana_novai
```

#### Custom entity not loading
```bash
# Check entities.yaml syntax
yamllint config/wads/arcana_novai/entities.yaml

# Check entity name matches exactly (case-sensitive)
grep "name:" config/wads/arcana_novai/entities.yaml
```

### 6. Memory & Soul Issues

#### Soul not updating
```bash
# Check proposed lessons (staging area)
cat data/entities/kali/proposed_lessons.yaml

# Check soul file
cat data/entities/kali/soul.yaml

# Force distillation
# (happens automatically at session end)
```

#### Memory not persisting
```bash
# Check MemoryStore directories
ls -la data/memory/

# Check session files
ls -la data/sessions/

# Verify add_exchange is being called
grep "add_exchange" src/omega/oracle/oracle.py
```

#### "None.json" file created
**Status**: Fixed in codebase (A1.2 fix)
**Action**: Delete the file and ensure latest code is running
```bash
rm -f data/memory/None.json
```

### 7. Infrastructure & Container Issues

#### Containers not starting
```bash
# Check Podman status
podman ps -a

# Check container logs (containers present on this host)
podman logs omega-redis
podman logs omega-qdrant
podman logs omega-searxng
podman logs omega-iris

# Containers are quadlet-managed — restart via podman or systemd
podman restart omega-redis
```

#### "Port already in use"
```bash
# Check what's using the port
ss -tlnp | grep 8016
ss -tlnp | grep 6379
ss -tlnp | grep 6333

# Kill conflicting process or change port in config
```

#### Caddy not serving

This release ships **no Caddy container and no `config/caddy/Caddyfile`**.
If you added one locally:
```bash
podman ps -a | grep -i caddy
podman logs <caddy-container>
```

### 8. Hivemind & Coordination Issues

#### Hivemind not showing other agents
```bash
# Check Hub is running
curl http://127.0.0.1:8016/health

# Check Hivemind awareness
curl http://127.0.0.1:8016/hivemind/awareness

# Restart Hub
omega mcp-restart omega-hub
```

#### Workspace lock conflicts
```bash
# Check existing locks
ls data/coordination/*_WORKSPACE_LOCK_*.md

# Read other agent's lock
cat data/coordination/OTHER_ENTITY_WORKSPACE_LOCK_20260706.md

# Post ACK if no conflict
# Create data/coordination/YOUR_ACK_20260706.md
```

### 9. Configuration Issues

#### Configuration not taking effect
```bash
# Check which config is active
cat config/omega.yaml

# Verify the active IWAD
grep active_iwad config/omega.yaml

# Restart a container after config changes (quadlet-managed)
podman restart omega-redis
```

#### Model not found errors
```bash
# Check models.yaml
grep "model_name" config/models.yaml

# Check provider overrides
grep -A10 "model_overrides" config/providers.yaml

# Verify the GGUF model is present
make infer-models | grep model_name
```

### 10. Performance Issues

#### Slow inference
```bash
# Check hardware stats
omega hardware-stats
make infer-memory

# Check if using correct thread count
grep -rn 'n_threads' config/models.yaml | head

# Check CPU governor
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
```

#### High memory usage
```bash
# Check memory pressure
free -h

# Check model memory footprint
make infer-memory

# Unload models if needed
make infer-stop
```

#### Slow test execution
```bash
# Run specific test subsets
make test-debug TEST=test_entity_registry
make test-debug TEST=test_oracle

# Skip slow tests (no ARGS= passthrough on make test)
.venv/bin/pytest -k "not slow" tests/
```

---

## 🔍 Debugging Techniques

### Enable Debug Logging
```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run with debug
omega talk "test query"
```

### Trace a Specific Request
```bash
# Get trace ID from output
# ⬡ OMEGA ⬡ SEKHMET ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_xxx ⬡ PHASE-I

# Search traces
grep "trc_xxx" data/traces/*.jsonl
```

### Inspect Memory Store
```bash
# Memory tiers live in data/memory/
ls data/memory/

# FTS index (keyword recall)
ls data/memory/fts_*.db

# Archive
ls data/memory/archive/ | head
```

### Inspect Soul Files
```bash
# View entity's soul
cat data/entities/kali/soul.yaml

# View proposed lessons
cat data/entities/kali/proposed_lessons.yaml
```

### Check Provider Health
```bash
# Local inference state
make infer-status
make infer-health

# Provider + model status
omega model-status
```

### Database Inspection

The databases that exist in this release:
```bash
# Memory + FTS databases
sqlite3 data/memory/omega_memory.db ".tables"
sqlite3 data/memory/fts_memory.db ".tables"

# All databases present
ls data/*.db data/memory/*.db 2>/dev/null
```
> `data/sessions.db`, `data/metrics.db` and `data/research.db` are **not** created by
> this release — do not look for them.

---

## 🛠️ Recovery Procedures

### Complete System Reset
```bash
# 1. Stop the Hub and local inference servers
pkill -f "mcp_servers.omega_hub.server"
make infer-stop

# 2. Clean artifacts
make clean

# 3. Fix permissions
sudo chown -R "$(id -u):$(id -g)" data/ config/

# 4. Restart a container (quadlet-managed)
podman restart omega-redis

# 5. Verify
make infer-status
make test
```

### Reset to Known Good State
```bash
# 1. Stash local changes
git stash

# 2. Reset to main
git checkout main
git pull origin main

# 3. Reinstall
make clean
pip install -e ".[native,cli,dev]"

# 4. Verify
make test
```

### Restore from Backup
```bash
# Run backup script
scripts/backup_to_8tb.sh

# Restore specific component
# (depends on backup structure)
```

---

## 📞 Getting Help

### Self-Service
1. Run `make infer-health` for native-gguf server diagnosis
2. Run `omega model-status` for provider status
3. Search logs in `data/traces/`, `data/crashes/` and via `make infer-logs`
4. Review this troubleshooting guide

### Community Support
- **GitHub Issues**: https://github.com/Xoe-NovAi/omega-engine/issues
- **Discussions**: https://github.com/Xoe-NovAi/omega-engine/discussions

### When Reporting Issues
Include:
1. Output of `make infer-health`
2. Output of `omega model-status`
3. Relevant excerpts from `make infer-logs` or `data/traces/`
4. Steps to reproduce
5. Environment details (OS, Python version, hardware)

---

## 📋 Quick Reference

### Essential Commands
```bash
make infer-status    # native-gguf server status
make infer-health    # status + memory + log tail
make test            # unit-tier test suite
make test-cov        # coverage report
make check-mandate-compliance   # 28-row mandate meter
grep active_iwad config/omega.yaml   # active IWAD
omega talk "q"       # quick query
omega summon ma'at "q"   # summon an entity
```

### Key Log Locations
| Log Type | Location |
|----------|----------|
| Inference events | `make infer-events` (events.jsonl) |
| Traces | `data/traces/YYYY-MM-DD.jsonl` |
| Sessions | `data/sessions/` |
| Crash Dumps | `data/crash_dumps/` |
| Benchmarks | `data/benchmarks/` |

### Key Config Files
| Config | Location |
|--------|----------|
| Engine | `config/omega.yaml` |
| Providers | `config/providers.yaml` |
| Models | `config/models.yaml` |
| Entities (IWAD) | `config/wads/<name>/entities.yaml` |
| Roles | `config/wads/<name>/roles.yaml` |

---

*When in doubt: `make infer-health` → `omega model-status` → check logs → ask community.*

⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ opencode ⬡ trc_doc_user ⬡ DOCUMENTATION-HARDENING
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
