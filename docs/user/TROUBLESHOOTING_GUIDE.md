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
make health
```
This checks: Ollama connectivity, LM Studio, Redis, Qdrant, PostgreSQL, Caddy, provider status, circuit breakers, and test status.

### Check System Status
```bash
make doctor
```
Full system diagnosis including: UID guard, test suite, infrastructure, providers, and configuration validation.

---

## 🔧 Common Issues & Solutions

### 1. Permission & Ownership Issues

#### "Permission denied" on files/directories
```bash
# Fix ownership drift (UID 1000)
make guard
```
**Root cause**: Container operations or manual file edits changed ownership changes caused UID drift.

#### "UID drift detected" warnings
```bash
# Check current ownership
ls -la data/
ls -la config/

# Fix with guard
make guard
```

### 2. Python Environment Issues

#### "No module named 'omega'" or import errors
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
make setup
```

#### "ModuleNotFoundError" for specific packages
```bash
# Check if package is in requirements
grep "package_name" requirements.txt

# Install missing package
.venv/bin/pip install package_name

# Or reinstall all
make setup
```

#### "Event loop is closed" warnings
**Status**: Known benign issue from `aiosqlite` thread cleanup during test shutdown.
**Impact**: None - does not affect functionality.
**Action**: Ignore these warnings.

### 3. Test Failures

#### Tests failing after changes
```bash
# Stop on first failure
make test ARGS='-x'

# Verbose output for debugging
make test ARGS='-v'

# Run specific test pattern
make test ARGS='-k test_entity_registry'
make test ARGS='-k test_oracle'
make test ARGS='-k test_health_monitor'
make test ARGS='-k test_error_gauntlet'

# Run with coverage
make test-cov
```

#### Specific test failures
| Test Pattern | Common Cause | Fix |
|--------------|--------------|-----|
| `test_entity_registry` | YAML syntax in entities.yaml | Check YAML syntax |
| `test_oracle` | Provider not available | Check `make health` |
| `test_health_monitor` | Circuit breaker state | Wait for cooldown or `make health` |
| `test_error_gauntlet` | Missing error handling | Check error hierarchy |

#### All tests passing but count changed
```bash
# Verify test count
make test-badge
cat TEST_STATUS.md
```

### 4. Inference & Provider Issues

#### Ollama not responding
```bash
# Check if Ollama is running
ollama list

# Check engine connectivity
make ollama-status

# Common fix: endpoint format
# config/providers.yaml → ollama endpoint: http://127.0.0.1:11434 (NO /v1 suffix)
```

#### Provider always falls back to mock
```bash
# Check local inference backends
ollama list
make lmster-status

# Check model overrides exist
grep -A5 "ollama" config/providers.yaml

# Try direct inference
omega talk "hello"
```

#### Circuit breaker tripping too often
```bash
# Check provider health
make health

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
make wad-status

# Switch to IWAD that has your entity
make wad NAME=arcana_novai

# List available entities
make entities
```

#### WAD switching seems stuck
```bash
# Force reset
make wad-reset

# Verify
make wad-status
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
cat data/entities/sekhmet/proposed_lessons.yaml

# Check soul file
cat data/entities/sekhmet/soul.yaml

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

# Check container logs
podman logs omega-redis
podman logs omega-qdrant
podman logs omega-postgres
podman logs omega-caddy

# Restart infrastructure
make restart-infra
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
```bash
# Check Caddy logs
podman logs omega-caddy

# Check Caddyfile syntax
cat config/caddy/Caddyfile

# Restart Caddy
podman restart omega-caddy
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

# Verify WAD is active
make wad-status

# Restart services after config changes
make restart-infra
```

#### Model not found errors
```bash
# Check models.yaml
grep "model_name" config/models.yaml

# Check provider overrides
grep -A10 "model_overrides" config/providers.yaml

# Verify model is pulled
ollama list | grep model_name
```

### 10. Performance Issues

#### Slow inference
```bash
# Check hardware stats
omega-hub_get_hardware_stats

# Check if using correct thread count
grep "LLAMA_CPP_N_THREADS" /etc/environment

# Check CPU governor
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
```

#### High memory usage
```bash
# Check memory pressure
free -h

# Check for memory leaks
make health

# Restart if needed
make restart-infra
```

#### Slow test execution
```bash
# Run specific test subsets
make test ARGS='-k test_entity_registry'
make test ARGS='-k test_oracle'

# Skip slow tests
make test ARGS='-k "not slow"'
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
# Hot tier (RAM)
# Not directly inspectable - use make health

# Warm tier (JSON files)
ls data/memory/warm/

# Cold tier (archives)
ls data/memory/cold/
```

### Inspect Soul Files
```bash
# View entity's soul
cat data/entities/sekhmet/soul.yaml

# View proposed lessons
cat data/entities/sekhmet/proposed_lessons.yaml
```

### Check Provider Health
```bash
# Full health check
make health

# Just provider status
make health | grep -A20 "Provider"
```

### Database Inspection
```bash
# Sessions database
sqlite3 data/sessions.db ".tables"
sqlite3 data/sessions.db "SELECT * FROM sessions LIMIT 5;"

# Metrics database
sqlite3 data/metrics.db ".tables"
sqlite3 data/metrics.db "SELECT * FROM events ORDER BY timestamp DESC LIMIT 10;"

# Research database
sqlite3 data/research.db ".tables"
```

---

## 🛠️ Recovery Procedures

### Complete System Reset
```bash
# 1. Stop everything
make stop-infra
pkill -f "mcp_servers.omega_hub.server"

# 2. Clean artifacts
make clean

# 3. Fix permissions
make guard

# 4. Restart infrastructure
make start-infra

# 5. Verify
make health
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
make setup

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
1. Run `make doctor` for full diagnosis
2. Check `make health` for system status
3. Search logs in `data/events/` and `data/traces/`
4. Review this troubleshooting guide

### Community Support
- **GitHub Issues**: https://github.com/Xoe-NovAi/omega-engine/issues
- **Discussions**: https://github.com/Xoe-NovAi/omega-engine/discussions

### When Reporting Issues
Include:
1. Output of `make doctor`
2. Output of `make health`
3. Relevant log excerpts from `data/events/` or `data/traces/`
4. Steps to reproduce
5. Environment details (OS, Python version, hardware)

---

## 📋 Quick Reference

### Essential Commands
```bash
make health          # System health check
make doctor          # Full diagnosis
make test            # Run all tests
make guard           # Fix permissions
make menu            # Interactive menu
make wad-status      # Check active IWAD
omega talk "q"       # Quick query
omega summon E "q"   # Summon entity
```

### Key Log Locations
| Log Type | Location |
|----------|----------|
| Events | `data/events/events.log` |
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

*When in doubt: `make doctor` → `make health` → check logs → ask community.*

⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ opencode ⬡ trc_doc_user ⬡ DOCUMENTATION-HARDENING
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
