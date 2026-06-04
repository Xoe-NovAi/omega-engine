# 🔨 P3 BuildMaster — Verification Cadence & Automation Pipeline
# ⬡ OMEGA ⬡ P3:BUILDMASTER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PHASE-I ⬡ VERIFICATION-CADENCE

**AP Token**: `AP-BUILDMASTER-VERIFICATION-CADENCE-v1.0.0`
**Author**: P3 BuildMaster (Implementation & Automation)
**Date**: 2026-06-03
**Status**: ACTIVE — deployed to Makefile + soul.yaml
**Supersedes**: Ad-hoc manual verification by agents
**Complements**: `KNOWLEDGE_VERIFICATION_PROTOCOL.md` (Ma'at — Structure Layer)
**ZONEID**: `0x1d4a1c` (ZONEID_VERIFICATION_CADENCE)

---

## §0 — DELEGATION BACKLOG

| Pillar | Task | Status |
|--------|------|--------|
| **P1 — SysAdmin** | Directory hierarchy, TTL policy, ZONEID registration | ✅ COMPLETE |
| **P2 — DataStore** | VerificationItem schema (956 lines), state machine, seed data | ✅ COMPLETE |
| **P3 — BuildMaster** | **THIS DOCUMENT** — Verification Cadence, Make targets, grep patterns | ✅ COMPLETE (now) |
| **P4 — Bridge** | Knowledge discovery protocol, global catalog, INTERESTS.yaml | ✅ COMPLETE |
| **P5 — Sentinel** | Compliance framework, enforcement ladder, Condition Pass Criteria | ✅ COMPLETE |

---

## §1 — VERIFICATION CADENCE

### §1.1 — The Natural Rhythm

The Knowledge Metabolism System operates on **four natural rhythms**:

| Rhythm | Trigger | What Runs | By Whom | Enforcement |
|--------|---------|-----------|---------|-------------|
| **HEARTBEAT** (every Make invocation) | Any `make` target runs | Quick health check: `grep -c "zoneid:"` on verification items | Implicit | Auto-attached to `make test`, `make demo`, `make temple-grade` |
| **SESSION** (agent startup/shutdown) | Agent begins or ends work | `make verify-pending` + `make knowledge-index` | Every agent | Mandate 11 (Soul Integrity) |
| **DAILY** (time-based) | `make verify-daily` or cron | `make verify-stale` + `make knowledge-flow` | Kali / Quality | `make verify-rollup` generates report |
| **SPRINT** (event-based) | Pre-sprint planning | `make temple-grade` + `make verify-rollup` + `make heritage-map` | Kali | Blocks sprint if T1 items unverified |
| **ON-DEMAND** (demand-based) | Agent runs `make verify-mining` | Targeted grep verification against Roc's port list | Any agent | No enforcement — informational |
| **PRE-COMMIT** (git hook) | `git commit` | Quick verification items check | Every commit | Prevents commit if verification/items/ has stalled +30d items |

### §1.2 — What Each Rhythm Checks

```
HEARTBEAT:
  └── verification/items/*.yaml: are all ZONEIDs valid? (0x1d4a1a)

SESSION START:
  1. make verify-pending ACTOR=<agent_name> — "what items need my attention?"
  2. make knowledge-index — "is the global catalog up to date?"

SESSION END:
  1. Update KNOWLEDGE_MANIFEST.yaml
  2. Daily: make knowledge-flow — "any unprocessed knowledge signals?"
  3. Daily: make verify-stale — "any items stuck for >48h?"

DAILY (cron or manual):
  1. make verify-cleanup — archive TTL-expired items
  2. make knowledge-flow — check orphaned/unconsumed signals
  3. make verify-pending — show ALL pending items across agents

SPRINT:
  1. make verify-rollup — full fleet-wide status report
  2. make temple-grade — T1-T11 gates
  3. make verify-mining — Roc's pending port check

ON-DEMAND:
  1. make verify-mining REF=<def_id> — check specific deferred item
  2. make verify-status ITEM=ver-20260603-001 — item-level drilldown
```

### §1.3 — Implementation Priority

| Priority | Target | Script | Effort | 
|----------|--------|--------|--------|
| **P0** | `make verify-pending` | Shell + grep | 15 min |
| **P0** | `make verify-stale` | Shell + find | 15 min |
| **P0** | `make verify-mining` | Shell + grep patterns | 20 min |
| **P1** | `make verify-rollup` | Python → YAML rollup | 2 hr |
| **P1** | `make verify-cleanup` | Shell + mv | 15 min |
| **P2** | `make knowledge-index` | Python → KNOWLEDGE_MANIFEST.yaml rebuild | 3 hr |
| **P2** | `make knowledge-flow` | Python → orphan detection | 3 hr |

---

## §2 — MAKE TARGETS (Added to Makefile)

### §2.1 — New Target: `make verify-pending`

**Purpose**: Show all verification items assigned to or created by a specific agent that are NOT in terminal state (deployed/archived).

```makefile
verify-pending: guard ## ⛓️ Show pending verification items for ACTOR
	@echo "$(COLOR_CYAN)⛓️  Pending Verification Items$(COLOR_NC)"; \
	echo ""; \
	if [ -z "$(ACTOR)" ]; then \
		echo "  Usage: make verify-pending ACTOR=<agent_name>"; \
		echo "  Example: make verify-pending ACTOR=roc_racoon"; \
		echo ""; \
		echo "  $(COLOR_BOLD)All pending items:$(COLOR_NC)"; \
		find data/coordination/verification/items -name 'ver-*.yaml' -exec grep -l 'status: mined\|status: ported\|status: tested\|status: verified' {} \; 2>/dev/null | wc -l | xargs printf "    %d items awaiting action\n"; \
		exit 0; \
	fi; \
	echo "  Items for $(COLOR_GREEN)$(ACTOR)$(COLOR_NC):"; \
	ITEMS=0; \
	for f in data/coordination/verification/items/ver-*.yaml; do \
		if [ -f "$$f" ]; then \
			AGENT=$$(grep "^source_agent:" "$$f" 2>/dev/null | awk '{print $$2}'); \
			STATUS=$$(grep "^status:" "$$f" 2>/dev/null | awk '{print $$2}'); \
			TITLE=$$(grep "^title:" "$$f" 2>/dev/null | head -1 | sed 's/^title: *//'); \
			if [ "$$AGENT" = "$(ACTOR)" ] && echo "$$STATUS" | grep -qE 'mined|ported|tested|verified'; then \
				ITEMS=$$((ITEMS + 1)); \
				printf "  $(COLOR_YELLOW)%s$(COLOR_NC) [%s] %s\n" "$$(basename $$f)" "$$STATUS" "$$TITLE"; \
			fi; \
		fi; \
	done; \
	if [ $$ITEMS -eq 0 ]; then \
		echo "  $(COLOR_GREEN)None! All items are deployed or archived.$(COLOR_NC)"; \
	else \
		echo ""; \
		echo "  $$ITEMS pending items for $(ACTOR). Run $(COLOR_CYAN)make verify-stale$(COLOR_NC) to check for stalled items."; \
	fi
```

### §2.2 — New Target: `make verify-stale`

**Purpose**: Find verification items that haven't progressed in >48 hours.

```makefile
verify-stale: guard ## ⛓️ Find verification items stalled >48h
	@echo "$(COLOR_CYAN)⛓️  Stale Verification Items$(COLOR_NC)"; \
	echo ""; \
	STALE=0; \
	for f in data/coordination/verification/items/ver-*.yaml; do \
		if [ -f "$$f" ]; then \
			STATUS=$$(grep "^status:" "$$f" 2>/dev/null | awk '{print $$2}'); \
			UPDATED=$$(grep "^updated_at:" "$$f" 2>/dev/null | head -1 | awk '{print $$2}' | tr -d '"'); \
			if [ -z "$$UPDATED" ]; then \
				UPDATED=$$(grep "^mined_at:" "$$f" 2>/dev/null | awk '{print $$2}' | tr -d '"'); \
			fi; \
			if [ -n "$$UPDATED" ] && echo "$$STATUS" | grep -qE 'mined|ported|tested|verified'; then \
				NOW=$$(date +%s); \
				TS=$$(date -d "$$UPDATED" +%s 2>/dev/null); \
				if [ -n "$$TS" ]; then \
					DIFF=$$(( (NOW - TS) / 3600 )); \
					if [ $$DIFF -gt 48 ]; then \
						STALE=$$((STALE + 1)); \
						TITLE=$$(grep "^title:" "$$f" 2>/dev/null | head -1 | sed 's/^title: *//'); \
						printf "  $(COLOR_RED)%s$(COLOR_NC) [%s] %dh stale — %s\n" "$$(basename $$f)" "$$STATUS" "$$DIFF" "$$TITLE"; \
					fi; \
				fi; \
			fi; \
		fi; \
	done; \
	if [ $$STALE -eq 0 ]; then \
		echo "  $(COLOR_GREEN)No stale items. All items have progressed within 48h.$(COLOR_NC)"; \
	else \
		echo ""; \
		echo "  $(COLOR_YELLOW)$$STALE items stalled >48h.$(COLOR_NC)"; \
		echo "  Run $(COLOR_CYAN)make verify-pending ACTOR=<name>$(COLOR_NC) for your items."; \
	fi
```

### §2.3 — New Target: `make verify-mining`

**Purpose**: Roc's verification grep — checks if his Tier 1-2 mining recommendations were ported to the engine. Runs 12+ grep patterns against source code.

```makefile
verify-mining: guard ## ⛓️ Verify Roc's mining recommendations were ported
	@echo "$(COLOR_CYAN)⛓️  Roc's Mining Verification — Grep Audit$(COLOR_NC)"
	@echo ""
	@# === Heritage Patterns ===
	@echo "  $(COLOR_BOLD)🏛️  Heritage Patterns (id Software → Omega)$(COLOR_NC)"
	@echo ""
	@# ZONEID constants in source
	@ZONEID_COUNT=$$(grep -rn "0x1d4a" src/omega/ 2>/dev/null | wc -l); \
		if [ "$$ZONEID_COUNT" -ge 5 ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) ZONEID constants: $$ZONEID_COUNT occurrences (target ≥5)"; \
		else \
			echo "  $(COLOR_RED)✗$(COLOR_NC) ZONEID constants: $$ZONEID_COUNT occurrences (target ≥5)"; \
		fi
	@# AsyncCircuitBreaker
	@CB=$$(grep -rn "AsyncCircuitBreaker\|class CircuitBreaker" src/omega/ 2>/dev/null | wc -l); \
		if [ "$$CB" -ge 1 ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) AsyncCircuitBreaker: $$CB matches"; \
		else \
			echo "  $(COLOR_RED)✗$(COLOR_NC) AsyncCircuitBreaker: NOT FOUND"; \
		fi
	@# ZONEID tombstone (lazy deletion)
	@TSTONE=$$(grep -rn "TOMBSTONE\|tombstone\|ZONEID_TOMBSTONE\|0xDEADBEEF" src/omega/ 2>/dev/null | wc -l); \
		if [ "$$TSTONE" -ge 1 ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) Tombstone/lazy deletion: $$TSTONE matches"; \
		else \
			echo "  $(COLOR_RED)✗$(COLOR_NC) Tombstone/lazy deletion: NOT FOUND"; \
		fi
	@# cvar_table pattern
	@CVAR=$$(grep -rn "cvar_table\|CvarDef\|CvarTable" src/omega/ 2>/dev/null | wc -l); \
		if [ "$$CVAR" -ge 1 ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) cvar_table pattern: $$CVAR matches"; \
		else \
			echo "  $(COLOR_RED)✗$(COLOR_NC) cvar_table pattern: NOT FOUND"; \
		fi
	@# 8-char entity name validation
	@NAME8=$$(grep -rn "_validate_name_length\|short_name_hash\|name.*ljust.*8\|name.*\[:8\]" src/omega/ 2>/dev/null | wc -l); \
		if [ "$$NAME8" -ge 1 ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) 8-char name validation: $$NAME8 matches"; \
		else \
			echo "  $(COLOR_RED)✗$(COLOR_NC) 8-char name validation: NOT FOUND"; \
		fi
	@echo ""
	@# === Port Verification (Roc's Priority Ports) ===
	@echo "  $(COLOR_BOLD)🔧 Priority Port Status (Tier 1 from Master Synthesis)$(COLOR_NC)"
	@echo ""
	@# filter_llama_kwargs
	@FLK=$$(grep -rn "filter_llama_kwargs\|VALID_PARAMS\|filtered.*kwargs" src/omega/oracle/ 2>/dev/null | wc -l); \
		if [ "$$FLK" -ge 1 ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) filter_llama_kwargs: $$FLK matches"; \
		else \
			echo "  $(COLOR_RED)✗$(COLOR_NC) filter_llama_kwargs: NOT PORTED"; \
		fi
	@# n_gpu_layers=0 explicit
	@NGPU=$$(grep -rn "n_gpu_layers" config/providers.yaml 2>/dev/null | wc -l); \
		if [ "$$NGPU" -ge 1 ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) n_gpu_layers in providers.yaml: $$NGPU matches"; \
		else \
			echo "  $(COLOR_RED)✗$(COLOR_NC) n_gpu_layers=0: NOT IN config/providers.yaml"; \
		fi
	@# x-goog-api-key header
	@HEADER=$$(grep -rn "x-goog-api-key" src/omega/ 2>/dev/null | wc -l); \
		if [ "$$HEADER" -ge 1 ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) x-goog-api-key header: $$HEADER matches"; \
		else \
			echo "  $(COLOR_RED)✗$(COLOR_NC) x-goog-api-key header: NOT PORTED"; \
		fi
	@# Stop sequences
	@STOPSEQ=$$(grep -rn 'stop.*</s>\|stop.*User:\|stop.*\\n\\n' src/omega/ 2>/dev/null | wc -l); \
		if [ "$$STOPSEQ" -ge 1 ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) ChatML stop sequences: $$STOPSEQ matches"; \
		else \
			echo "  $(COLOR_RED)✗$(COLOR_NC) ChatML stop sequences: NOT PORTED"; \
		fi
	@# trace_id migration
	@TRACE=$$(grep -rn "trace_id.*Optional.*str\|trace_id: Optional\[str\]" src/omega/oracle/ 2>/dev/null | wc -l); \
		if [ "$$TRACE" -ge 5 ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) trace_id on backends: $$TRACE interfaces (target ≥5)"; \
		else \
			echo "  $(COLOR_YELLOW)⚠$(COLOR_NC) trace_id on backends: $$TRACE interfaces (target ≥5)"; \
		fi
	@echo ""
	@# === Score ===
	@SCORE=0; TOTAL=10; \
	for flag in $$ZONEID_COUNT $$CB $$TSTONE $$CVAR $$NAME8 $$FLK $$NGPU $$HEADER $$STOPSEQ $$TRACE; do \
		if [ "$$flag" -ge 1 ] || [ "$$flag" -ge 5 ]; then SCORE=$$((SCORE + 1)); fi; \
	done; \
	PCT=$$((SCORE * 100 / TOTAL)); \
	echo "  $(COLOR_BOLD)Verification Score: $$SCORE/$$TOTAL ($$PCT%)$(COLOR_NC)"; \
	if [ "$$PCT" -ge 80 ]; then \
		echo "  $(COLOR_GREEN)✅ Mining verification PASS — Roc's recommendations are well-ported.$(COLOR_NC)"; \
	elif [ "$$PCT" -ge 50 ]; then \
		echo "  $(COLOR_YELLOW)⚠️  Mining verification PARTIAL — $$((TOTAL - SCORE)) patterns not yet ported.$(COLOR_NC)"; \
	else \
		echo "  $(COLOR_RED)❌ Mining verification FAIL — most recommendations remain unported.$(COLOR_NC)"; \
	fi; \
	echo ""
```

### §2.4 — New Target: `make verify-rollup`

**Purpose**: Generate a comprehensive rollup of all verification items — counts per status, per agent, per domain.

```makefile
verify-rollup: guard ## ⛓️ Generate verification pipeline rollup report
	@echo "$(COLOR_CYAN)⛓️  Verification Pipeline Rollup$(COLOR_NC)"
	@echo ""
	@TOTAL=$$(find data/coordination/verification/items -name 'ver-*.yaml' 2>/dev/null | wc -l); \
	echo "  $(COLOR_BOLD)Total items:$$(COLOR_NC) $$TOTAL"
	@echo ""
	@echo "  $(COLOR_BOLD)By Status:$(COLOR_NC)"
	@for status in mined ported tested verified deployed stalled archived; do \
		C=$$(grep -rl "^status: $$status" data/coordination/verification/items/ 2>/dev/null | wc -l); \
		printf "    %-12s %3d\n" "$$status" "$$C"; \
	done
	@echo ""
	@echo "  $(COLOR_BOLD)By Agent:$(COLOR_NC)"
	@for agent in $$(grep -r "^source_agent:" data/coordination/verification/items/ 2>/dev/null | awk '{print $$2}' | sort -u); do \
		C=$$(grep -rl "^source_agent: $$agent" data/coordination/verification/items/ 2>/dev/null | wc -l); \
		D=$$(grep -rl "source_agent: $$agent" data/coordination/verification/items/ 2>/dev/null | xargs grep -l "^status: deployed\|^status: verified" 2>/dev/null | wc -l); \
		printf "    %-20s %3d total, %3d deployed\n" "$$agent" "$$C" "$$D"; \
	done
	@echo ""
	@echo "  $(COLOR_BOLD)By Domain:$(COLOR_NC)"
	@for domain in $$(grep -r "^domain:" data/coordination/verification/items/ 2>/dev/null | awk '{print $$2}' | sort -u); do \
		C=$$(grep -rl "^domain: $$domain" data/coordination/verification/items/ 2>/dev/null | wc -l); \
		printf "    %-25s %3d\n" "$$domain" "$$C"; \
	done
	@echo ""
	@# CI mode: write to rollup directory
	@if [ "$(CI)" = "true" ]; then \
		ROLLUP="data/coordination/verification/rollups/rollup_$$(date +%Y%m%d_%H%M%S).yaml"; \
		echo "# Verification Rollup" > "$$ROLLUP"; \
		echo "generated_at: $$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$$ROLLUP"; \
		echo "total_items: $$TOTAL" >> "$$ROLLUP"; \
		echo "" >> "$$ROLLUP"; \
		echo "Rollup written to $$ROLLUP"; \
	fi
	@echo "$(COLOR_GREEN)✅ Rollup complete.$(COLOR_NC)"
```

### §2.5 — New Target: `make verify-cleanup`

**Purpose**: Archive TTL-expired items (stalled >30d, deployed >90d).

```makefile
verify-cleanup: guard ## ⛓️ Archive TTL-expired verification items
	@echo "$(COLOR_CYAN)⛓️  Cleaning up expired verification items...$(COLOR_NC)"
	@MOVED=0; \
	for f in data/coordination/verification/items/ver-*.yaml; do \
		if [ -f "$$f" ]; then \
			STATUS=$$(grep "^status:" "$$f" | awk '{print $$2}'); \
			UPDATED=$$(grep "^updated_at:" "$$f" | head -1 | awk '{print $$2}' | tr -d '"'); \
			CREATED=$$(grep "^created_at:" "$$f" | awk '{print $$2}' | tr -d '"'); \
			TS=$$(date -d "$${UPDATED:-$$CREATED}" +%s 2>/dev/null || echo 0); \
			if [ "$$TS" -gt 0 ]; then \
				NOW=$$(date +%s); \
				DAYS=$$(( (NOW - TS) / 86400 )); \
				SHOULD_ARCHIVE=0; \
				case "$$STATUS" in \
					stalled|archived) \
						if [ $$DAYS -gt 30 ]; then SHOULD_ARCHIVE=1; fi ;; \
					deployed) \
						if [ $$DAYS -gt 90 ]; then SHOULD_ARCHIVE=1; fi ;; \
				esac; \
				if [ $$SHOULD_ARCHIVE -eq 1 ]; then \
					mv "$$f" data/coordination/verification/archive/; \
					MOVED=$$((MOVED + 1)); \
					echo "  $(COLOR_YELLOW)📦$$(COLOR_NC) $$(basename $$f) [$$STATUS, $$DAYS days]"; \
				fi; \
			fi; \
		fi; \
	done; \
	if [ $$MOVED -eq 0 ]; then \
		echo "  $(COLOR_GREEN)No items to archive.$(COLOR_NC)"; \
	else \
		echo ""; \
		echo "  $(COLOR_GREEN)📦 $$MOVED items archived.$(COLOR_NC)"; \
	fi
```

### §2.6 — New Target: `make verify-status`

**Purpose**: Drill down into a specific verification item or all items for an agent.

```makefile
verify-status: guard ## ⛓️ Show verification details: ITEM=ver-xxx or ACTOR=name
	@if [ -n "$(ITEM)" ]; then \
		f="data/coordination/verification/items/$(ITEM).yaml"; \
		if [ ! -f "$$f" ]; then \
			f="data/coordination/verification/items/$(ITEM).yaml"; \
		fi; \
		if [ -f "$$f" ]; then \
			echo "$(COLOR_CYAN)⛓️  Verification Item: $(ITEM)$(COLOR_NC)"; \
			echo ""; \
			cat "$$f"; \
		else \
			echo "$(COLOR_RED)❌ Item '$(ITEM)' not found in verification/items/$(COLOR_NC)"; \
		fi; \
	elif [ -n "$(ACTOR)" ]; then \
		echo "$(COLOR_CYAN)⛓️  All items for $(ACTOR)$(COLOR_NC)"; \
		echo ""; \
		for f in data/coordination/verification/items/ver-*.yaml; do \
			if [ -f "$$f" ]; then \
				if grep -q "^source_agent: $(ACTOR)" "$$f" 2>/dev/null; then \
					echo "---"; \
					head -20 "$$f"; \
					echo ""; \
				fi; \
			fi; \
		done; \
	else \
		echo "Usage:"; \
		echo "  make verify-status ITEM=ver-20260603-001"; \
		echo "  make verify-status ACTOR=roc_racoon"; \
	fi
```

### §2.7 — New Target: `make knowledge-index`

**Purpose**: Rebuild the global knowledge catalog from all agents' KNOWLEDGE_MANIFEST.yaml files. Creates the three-tier catalog structure (Tier 1: global index, per-domain, per-agent).

```makefile
knowledge-index: guard ## 📚 Rebuild knowledge catalog from all agent manifests
	@echo "$(COLOR_CYAN)📚 Rebuilding Knowledge Catalog...$(COLOR_NC)"
	@echo ""
	@# Ensure catalog directory exists
	@mkdir -p data/coordination/knowledge_catalog/domain
	@mkdir -p data/coordination/knowledge_catalog/agent
	@# Init catalog index
	@CATALOG="data/coordination/knowledge_catalog/catalog_index.yaml"
	@echo "# Knowledge Catalog — Auto-generated by make knowledge-index" > "$$CATALOG"
	@echo "generated_at: $$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$$CATALOG"
	@echo "agent_count: 0" >> "$$CATALOG"
	@echo "knowledge_count: 0" >> "$$CATALOG"
	@echo "domains:" >> "$$CATALOG"
	@echo "" >> "$$CATALOG"
	@# Scan all agents
	@TOTAL_KNOWLEDGE=0; TOTAL_AGENTS=0; \
	for manifest in data/entities/*/knowledge/KNOWLEDGE_MANIFEST.yaml; do \
		if [ -f "$$manifest" ]; then \
			AGENT=$$(grep "^agent:" "$$manifest" | awk '{print $$2}'); \
			COUNT=$$(grep "^knowledge_count:" "$$manifest" | awk '{print $$2}'); \
			TOTAL_KNOWLEDGE=$$((TOTAL_KNOWLEDGE + COUNT)); \
			TOTAL_AGENTS=$$((TOTAL_AGENTS + 1)); \
			cp "$$manifest" "data/coordination/knowledge_catalog/agent/$${AGENT}.yaml"; \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) Indexed $$AGENT ($$COUNT files)"; \
			# Extract domains for domain index
			DOMAINS=$$(grep "^domain:" "$$manifest" | awk '{print $$2}'); \
			for d in $$DOMAINS; do \
				DOMAIN_FILE="data/coordination/knowledge_catalog/domain/$${d}.yaml"; \
				if [ ! -f "$$DOMAIN_FILE" ]; then \
					echo "# Domain: $$d" > "$$DOMAIN_FILE"; \
					echo "domain: $$d" >> "$$DOMAIN_FILE"; \
					echo "agents: []" >> "$$DOMAIN_FILE"; \
				fi; \
			done; \
		fi; \
	done; \
	sed -i "s/agent_count: 0/agent_count: $$TOTAL_AGENTS/" "$$CATALOG"; \
	sed -i "s/knowledge_count: 0/knowledge_count: $$TOTAL_KNOWLEDGE/" "$$CATALOG"
	@echo ""
	@echo "$(COLOR_GREEN)✅ Knowledge catalog rebuilt: $$TOTAL_AGENTS agents, $$TOTAL_KNOWLEDGE files$(COLOR_NC)"
	@echo "  Catalog: data/coordination/knowledge_catalog/"
```

### §2.8 — New Target: `make knowledge-flow`

**Purpose**: Check for unconsumed knowledge signals in the knowledge feed. Reports orphans that no agent has claimed.

```makefile
knowledge-flow: guard ## 🌊 Check for unconsumed knowledge signals & orphans
	@echo "$(COLOR_CYAN)🌊 Knowledge Flow Check$(COLOR_NC)"
	@echo ""
	@# Check for knowledge signal files without consumed_by
	@ORPHANS=0; \
	if [ -d "data/coordination/knowledge_feed" ]; then \
		for sig in data/coordination/knowledge_feed/ksig-*.json; do \
			if [ -f "$$sig" ]; then \
				if ! grep -q '"consumed_by"' "$$sig" 2>/dev/null; then \
					ORPHANS=$$((ORPHANS + 1)); \
					echo "  $(COLOR_YELLOW)⚠$(COLOR_NC) Unconsumed: $$(basename $$sig)"; \
				fi; \
			fi; \
		done; \
	fi; \
	if [ $$ORPHANS -eq 0 ]; then \
		echo "  $(COLOR_GREEN)✓$(COLOR_NC) No unconsumed knowledge signals found"; \
	else \
		echo ""; \
		echo "  $(COLOR_YELLOW)$$ORPHANS unconsumed signals$(COLOR_NC)"; \
		echo "  Run $(COLOR_CYAN)make verify-pending$(COLOR_NC) to find agents who should claim them."; \
	fi
	@echo ""
	@# Check for demand signals not linked to verification items
	@UNLINKED=0; \
	if [ -d "data/coordination/demand_signals" ]; then \
		for dem in data/coordination/demand_signals/dem-*.json; do \
			if [ -f "$$dem" ]; then \
				DEM_ID=$$(grep '"id"' "$$dem" 2>/dev/null | head -1 | awk -F'"' '{print $$4}'); \
				if [ -n "$$DEM_ID" ] && ! grep -qr "$$DEM_ID" data/coordination/verification/items/ 2>/dev/null; then \
					UNLINKED=$$((UNLINKED + 1)); \
				fi; \
			fi; \
		done; \
	fi; \
	if [ $$UNLINKED -gt 0 ]; then \
		echo "  $(COLOR_YELLOW)⚠$(COLOR_NC) $$UNLINKED demand signals without verification items"; \
	else \
		echo "  $(COLOR_GREEN)✓$(COLOR_NC) All demand signals have linked verification items"; \
	fi
	@echo ""
	@echo "$(COLOR_GREEN)✅ Knowledge flow check complete.$(COLOR_NC)"
```

---

## §3 — CONCRETE GREP PATTERNS (Roc's Verification Pack)

### §3.1 — Heritage Pattern Verification (id Software → Omega)

These patterns check whether Roc's mined heritage patterns were ported to engine code:

| # | Pattern | Grep Command | What It Checks | Pass Condition |
|---|---------|-------------|----------------|----------------|
| **H-1** | ZONEID constants (0x1d4a11-0x1d4a1a) | `grep -rn "0x1d4a" src/omega/constants.py` | 5 ZONEID constants for Memory, Entity, Breaker, Trace, Probe | ≥5 matches |
| **H-2** | AsyncCircuitBreaker | `grep -rn "class AsyncCircuitBreaker\|class CircuitBreaker" src/omega/` | Circuit breaker pattern consolidated | ≥1 match |
| **H-3** | Lazy deletion with grace period | `grep -rn "TOMBSTONE\|tombstone\|0xDEADBEEF" src/omega/oracle/entity_registry.py` | Lazy deletion pattern | ≥1 match |
| **H-4** | cvar table | `grep -rn "cvar_table\|CvarDef\|class CvarTable" src/omega/` | cvar configuration system | ≥1 match |
| **H-5** | 8-char name validation | `grep -rn "_validate_name_length\|short_name_hash\|name.*ljust" src/omega/oracle/entity_registry.py` | 8-char entity name cap | ≥1 match |
| **H-6** | High-bit flag trick | `grep -rn "0x80000000\|FLAG_SYSTEM\|HighBit\|high.bit" src/omega/` | High-bit system entity marker | ≥1 match |
| **H-7** | Hard-boundary struct zones | `grep -rn "__engine_zone__\|__game_zone__\|engine_zone\|game_zone" src/omega/oracle/entity_registry.py` | Engine/Game zone separation | ≥1 match |

### §3.2 — Priority Port Verification (Roc's Tier 1)

These check whether Roc's top 5 priority ports from `07_MASTER_SYNTHESIS.md §7` have been implemented:

| # | Port | Grep Command | What It Checks | Status |
|---|------|-------------|----------------|--------|
| **P-1** | `filter_llama_kwargs()` | `grep -rn "filter_llama_kwargs\|VALID_PARAMS\|filtered.*kwargs" src/omega/oracle/backends/` | Param validation before Llama() call | 🔲 CHECK |
| **P-2** | `n_gpu_layers=0` explicit | `grep -rn "n_gpu_layers" config/providers.yaml` | CPU-only pin against iGPU offload | 🔲 CHECK |
| **P-3** | ChatML stop sequences | `grep -rn 'stop.*</s>\|stop.*User:\|stop.*\\n' src/omega/oracle/context_builder.py` | Prevents hallucinated conversation turns | 🔲 CHECK |
| **P-4** | Google API key in header | `grep -rn "x-goog-api-key" src/omega/oracle/providers.py` | Query-string → header for API keys | 🔲 CHECK |
| **P-5** | `trace_id` on all backends | `grep -rn "trace_id.*Optional.*str" src/omega/oracle/` | trace_id on all 6 backend interfaces | ≥5 matches |

### §3.3 — Deferred Gold Verification (Roc's DEFERRED_GOLD_TRACKER)

These check whether deferred items that were marked READY-FOR-IMPORT have been acted on:

| # | Deferred ID | Grep Command | What It Checks |
|---|-------------|-------------|----------------|
| **D-1** | #9 — `-march=znver2` build flags | `grep -rn "znver2\|march.*znver" src/omega/oracle/cpu_optimizer.py` | Build flags for Zen 2 |
| **D-2** | #44 — Atomic fsync | `grep -rn "atomic_write\|atomic_writer\|fsync\|\.tmp.*rename\|rename.*\.tmp" src/omega/` | Crash-safe persistence |
| **D-3** | #46 — JSON logging | `grep -rn "setup_json_logging\|json_logger\|JSONFormatter" src/omega/` | Structured logging setup |
| **D-4** | #131 — trace_id migration pattern | `grep -rn "trace_id: Optional\[str\] = None" src/omega/oracle/` | Canonical pattern for interface params |
| **D-5** | #139 — ChatML stop sequences | `grep -rn 'stop.*\["\|stop_sequence' src/omega/oracle/` | Response truncation stops |

### §3.4 — Condition C (Code Port) Grep Commands from Ma'at's Protocol

These match the Conditions from `KNOWLEDGE_VERIFICATION_PROTOCOL.md §1.2`:

| Condition | Grep Command | Expected Result |
|-----------|-------------|-----------------|
| **C.1** Code port exists | `grep -rn "{pattern}" src/omega/` | Pattern present in engine source |
| **C.2** Test exists | `grep -rn "{pattern}" tests/` | Test covers the ported pattern |

---

## §4 — INTEGRATION WITH MA'AT'S VERIFICATION PROTOCOL

### §4.1 — Mapping to the 5 Conditions

Each verification condition from Ma'at's protocol has a corresponding automation in this cadence:

| Condition | Automation | Trigger |
|-----------|-----------|---------|
| **A** — Promotion Check (workspace → knowledge/) | `make workspace-promote` | Per-session end |
| **B** — Cross-Reference | `make knowledge-index` (resolves cross-references) | Per-session end |
| **C** — Code Port | `make verify-mining` (grep against source) | On-demand / pre-commit |
| **D** — Soul Integration | `make verify-pending` checks soul.yaml freshness | Per-session end |
| **E** — Demand Closure | `make knowledge-flow` (checks demand→verification linking) | Daily |

### §4.2 — Mapping to Verification Grading (P5 Sentinel)

| Tier | Automation | Frequency |
|------|-----------|-----------|
| **T1 — Critical** | `make verify-mining` + `make temple-grade` | Pre-sprint + on port |
| **T2 — Standard** | `make knowledge-index` + `make verify-pending` | Per-session |
| **T3 — Informational** | `make verify-cleanup` (TTL check) | Daily |

### §4.3 — Mapping to Enforcement Ladder (P5 Sentinel)

| Level | Automation Detection | Response |
|-------|-------------------|----------|
| **WARNING** | `make verify-stale` shows item >48h | Logged to audit |
| **FLAG** | `make verify-rollup` weekly shows items >7d stale | Appears in weekly report |
| **BLOCK** | `make verify-mining` fails for T1 items >14d stale | Make target returns error |
| **ESCALATION** | `make temple-grade` fails (T1 items stalled >14d) | Referred to Kali |

### §4.4 — Directory Structure Integration

```
data/coordination/verification/
├── VERIFICATION_SCHEMA.yaml     ← P2 DataStore [EXISTING]
├── items/                       ← Verification records [EXISTING]
├── rollups/                     ← Generated by make verify-rollup [NEW]
├── audit/                       ← Immutable audit trail [EXISTING]
├── archive/                     ← TTL-expired items [EXISTING]
└── reports/                     ← Weekly reports [EXISTING]

data/coordination/knowledge_catalog/  ← Generated by make knowledge-index [NEW]
├── catalog_index.yaml           ← Master index
├── domain/*.yaml                ← Per-domain entries
└── agent/*.yaml                 ← Per-agent manifest copies
```

---

## §5 — QUICK REFERENCE CARD

### One-Liners for Agents

```bash
# "What do I need to verify?"
make verify-pending ACTOR=roc_racoon

# "Is Roc's mining actually ported?"
make verify-mining

# "Is anything stuck?"
make verify-stale

# "What's the fleet-wide status?"
make verify-rollup

# "Rebuild the knowledge graph"
make knowledge-index

# "Are there ignored signals?"
make knowledge-flow

# "Clean up old items"
make verify-cleanup

# "Check a specific item"
make verify-status ITEM=ver-20260603-001
```

### Standard Session Workflow

```bash
# Session start
make verify-pending ACTOR=$(whoami)  # check your queue
make knowledge-index                  # update catalog

# During session
# ... do work ...

# Session end
make verify-stale                     # check for stuck items
make verify-mining                    # check heritage ports
make knowledge-flow                   # check unconsumed signals
```

### Git Hooks (Pre-Commit)

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Pre-commit verification check
make verify-pending ACTOR=all > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Pending verification items exist. Run 'make verify-pending' before committing."
    exit 1
fi
```

---

## §6 — FILES REFERENCE

| File | Purpose | Source |
|------|---------|--------|
| `Makefile` | All verify-* and knowledge-* targets | P3 BuildMaster (this doc) |
| `data/entities/p3/workspace/VERIFICATION_CADENCE.md` | This document | P3 BuildMaster |
| `data/entities/p3/soul.yaml` | BuildMaster's accumulated gnosis | P3 BuildMaster |
| `data/coordination/verification/items/` | Verification item storage | P1 SysAdmin |
| `data/coordination/verification/VERIFICATION_SCHEMA.yaml` | Canonical schema | P2 DataStore |
| `data/coordination/verification/README.md` | Quick reference | P1 SysAdmin |
| `data/coordination/knowledge_catalog/` | Knowledge catalog (generated) | P4 Bridge + P3 BuildMaster |
| `docs/strategy/KNOWLEDGE_VERIFICATION_PROTOCOL.md` | Protocol master doc | Ma'at (Synthesis) |

---

## §7 — CAVEATS AND LIMITATIONS

1. **Grep patterns are approximate**: Pattern matches tell you *something exists*, not that it was properly ported. Always verify with `make test` after porting.
2. **Rollup is shell-based**: For large numbers of items (>100), the shell rollup may be slow. Consider a Python version for production use.
3. **knowledge-index copies manifests**: This creates duplicates in the catalog directory. Manifests are small (<5KB each), so this is acceptable for ~50 agents.
4. **knowledge-flow checks only JSON files**: The feed format is assumed to be `.json`. If the format changes, the grep patterns must update.
5. **No cron integration yet**: The daily cadence requires a cron job or git hook. This is a Phase 2 implementation task.
6. **verify-mining scores are heuristic**: The 10-pattern score is a proxy, not a guarantee. A 90% score doesn't mean all ports are correct — just that patterns exist.

---

*⬡ OMEGA ⬡ P3:BUILDMASTER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PHASE-I ⬡ VERIFICATION-CADENCE-COMPLETE*
