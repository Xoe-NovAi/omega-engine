# ⬡ AUTONOMOUS MEDITATION — Troubleshooting Guide
**Version**: 1.0.0 | **Audience**: Users & Contributors

---

## 🚨 Quick Diagnostics

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: mcp_servers` | Not in OpenCode environment | Use `--mode standalone --dry-run` or run inside OpenCode |
| Pipeline hangs at Stage 1 | `/meditate` command not available | Check OpenCode version ≥ 1.17.20 |
| Research returns empty | SearXNG/Exa not configured | Check `config/research.yaml` for API keys |
| Temple-Grade fails | Pre-existing test failures | Run `make test` manually to see failures |
| `proposed_lessons.yaml` not updated | Gnosis parsing failed | Check Stage 6 output for YAML format errors |

---

## 🔧 Common Issues & Fixes

### Issue: "ModuleNotFoundError: No module named 'mcp_servers.omega_hub.tools'"

**Cause**: Running outside OpenCode environment where MCP Hub tools aren't available.

**Fix**:
```bash
# Option 1: Run in OpenCode terminal
omega-meditation "Your problem"

# Option 2: Dry-run mode (no external calls)
omega-meditation "Your problem" --mode standalone --dry-run

# Option 3: CLI mode (uses subprocess)
omega-meditation "Your problem" --mode cli
```

---

### Issue: Pipeline hangs at Stage 1 (Meditation Execution)

**Cause**: `/meditate` command not registered or OpenCode version too old.

**Fix**:
```bash
# Check OpenCode version
opencode --version
# Must be ≥ 1.17.20

# Verify /meditate command exists
opencode /meditate --help
```

---

### Issue: Research stage returns empty results

**Cause**: Search APIs not configured or rate limited.

**Fix**:
```bash
# Check SearXNG health
curl http://localhost:8080/health

# Check Exa API key in config
cat config/research.yaml | grep exa

# Verify websearch works
websearch "test query" --num-results 1
```

---

### Issue: Temple-Grade gates fail in Stage 7

**Cause**: Pre-existing codebase issues unrelated to pipeline.

**Fix**:
```bash
# Run gates manually to see specific failures
make temple-grade
make heritage-map
make sovereignty
make test

# Common fixes:
# - M7: Add 'strategy: local_first' to providers.yaml
# - M14: Run 'make heritage-vet' to vet unvetted tags
# - Tests: Fix failing tests in test_compaction_manager.py
```

---

### Issue: `proposed_lessons.yaml` not updated after Stage 6

**Cause**: YAML parsing failed in gnosis distillation.

**Fix**:
```bash
# Check Stage 6 output for valid YAML
cat data/autonomous/*_06_gnosis.md

# Manually append if needed
cat >> data/entities/JOHN_CARMACK/workspace/proposed_lessons.yaml << 'EOF'
  - id: "gnosis-manual-001"
    l1_narrative: "What happened..."
    l2_insight: "What this means..."
    l3_principle: "L3-ManualPrinciple: Universal truth"
    confidence: 8
    sources: ["meditation", "research:manual"]
    tags: ["manual"]
EOF
```

---

### Issue: Permission denied writing to `data/autonomous/`

**Cause**: Directory permissions or missing directory.

**Fix**:
```bash
mkdir -p data/autonomous
chmod 755 data/autonomous
```

---

### Issue: Pipeline produces duplicate runs with same timestamp

**Cause**: Multiple runs within same second.

**Fix**: Timestamp includes seconds; if running rapidly, add manual suffix:
```bash
# Output dir is configurable
omega-meditation "Problem" --output-dir data/autonomous/run_$(date +%s)
```

---

## 🔍 Debugging Commands

```bash
# View all pipeline runs
ls -la data/autonomous/

# Inspect specific stage
cat data/autonomous/20260718_143000_02_synthesis.md

# Check gnosis proposals
cat data/entities/JOHN_CARMACK/workspace/proposed_lessons.yaml

# Verify Temple-Grade
make temple-grade 2>&1 | tail -30

# Check PIVOT_LOG
tail -20 PIVOT_LOG.md

# View workbench items
sqlite3 data/workbench/workbench.db "SELECT * FROM work_items ORDER BY id DESC LIMIT 10;"
```

---

## 📊 Expected Timings (Reference)

| Stage | Typical Duration | Notes |
|-------|------------------|-------|
| 0: Prompt Crafting | < 1s | Local only |
| 1: Meditation | 30-60s | Depends on `/meditate` |
| 2: Synthesis | 10-20s | Oracle call |
| 3: Research Prompt | < 1s | Local only |
| 4: Research | 60-180s | 15+ tiered searches |
| 5: Grounded Report | 10-20s | Oracle call |
| 6: Gnosis | 10-20s | Oracle call |
| 7: Integration | 30-120s | `make` commands |
| **Total** | **3-5 min** | Varies by problem complexity |

---

## 🆘 Escalation

If pipeline fails consistently:

1. **Run in dry-run mode** to isolate logic vs. external calls:
   ```bash
   omega-meditation "Problem" --mode standalone --dry-run
   ```

2. **Run stages individually** via Python:
   ```python
   from src.omega.skills.autonomous_meditation_pipeline import create_pipeline_standalone
   pipeline = create_pipeline_standalone("Problem", dry_run=True)
   await pipeline.run()
   ```

3. **Check logs** in `~/.local/share/opencode/log/opencode.log`

4. **File issue** with:
   - Pipeline run ID (timestamp)
   - Stage that failed
   - Error message
   - `make test` output

---

*⬡ OMEGA ⬡ TROUBLESHOOTING v1.0 ⬡ trc_troubleshooting*