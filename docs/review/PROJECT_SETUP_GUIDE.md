# 🔱 Claude Project Setup Guide — 8 Web Accounts

⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_project_setup ⬡ PHASE-E

**Date**: 2026-05-22
**Purpose**: Step-by-step instructions for creating 8 Claude Projects, one per Web Claude account

---

## Overview

Each of your 8 Web Claude accounts needs a **Claude Project** with:
1. A **Project Name** and optional description
2. **Project Instructions** (pasted from the `project_instructions_0X_*.md` files)
3. **Project Knowledge** (files synced from the GitHub repo)
4. **Account-specific email for sign-in**

---

## Pre-Flight Checklist

- [ ] GitHub repo is **public**: `https://github.com/Xoe-NovAi/omega-engine`
- [ ] All 8 accounts are logged in on separate browser tabs or profiles
- [ ] All `project_instructions_0X_*.md` and `review_0X_*.md` files are created
- [ ] Project Instructions are saved locally for copy-paste

---

## Step-by-Step for Each Account

### Step 1: Create the Project

1. Go to `https://claude.ai/projects`
2. Click **"Create Project"** or **"New Project"**
3. Fill in:
   - **Name**: Use the name from the table below
   - **Description**: Optional, but recommended (use the description from the table)

### Step 2: Set Project Instructions

1. In the Project settings, find the **Instructions** field (this is the system prompt)
2. Copy the entire contents of the corresponding `project_instructions_0X_*.md` file
3. Paste into the Instructions field
4. Click Save

### Step 3: Add Project Knowledge

For each project, you need to add key reference files. Use the **GitHub Connector** to sync files:

1. In the Project, click **"+ Add"** or the Project Knowledge section
2. Choose **"GitHub"** from the sources
3. Connect to `Xoe-NovAi/omega-engine`
4. Select the files listed in the "Knowledge Files" column below
5. Click **"Add to Project"**

**RAG Threshold Warning**: Keep Project Knowledge to **12 files or fewer** per project. Beyond 12 files, Claude is forced into RAG mode (retrieval-augmented generation) which reduces accuracy. See the RAG Bug report in the research document for details.

### Step 4: Verify

Send a test message: *"Read my project instructions and summarize my role in 3 sentences."* Claude should accurately describe its role as the specialized reviewer.

---

## Account Configuration Table

| # | Email | Project Name | Instructions File | Review File | Knowledge Files (via GitHub Connector) |
|---|-------|-------------|-------------------|-------------|---------------------------------------|
| 1 | `Arcana.NovAi@gmail.com` | **Omega — Core Architecture** | `project_instructions_01_core_architecture.md` | `review_01_core_architecture.md` | `src/omega/oracle/oracle.py`, `entity_registry.py`, `wad_loader.py`, `config/entities.yaml`, `hierarchy.yaml`, `SOVEREIGN_MANDATES.md` |
| 2 | `ArcanaNovaAi@gmail.com` | **Omega — Provider Fabric** | `project_instructions_02_provider_fabric.md` | `review_02_provider_fabric.md` | `src/omega/oracle/model_gateway.py`, `config/providers.yaml`, `config/models.yaml` |
| 3 | `xoe.nova.ai@gmail.com` | **Omega — Memory & Knowledge** | `project_instructions_03_memory_knowledge.md` | `review_03_memory_knowledge.md` | `src/omega/memory_store.py`, `oracle/context_builder.py`, `oracle/session_manager.py`, `data/entities/arch/soul.yaml` |
| 4 | `antipode2727@gmail.com` | **Omega — Jem 2.0 Pipeline** | `project_instructions_04_jem_pipeline.md` | `review_04_jem_pipeline.md` | `src/omega/workers/background_researcher/loop.py`, `distiller.py`, `config/research_topics.yaml`, `data/entities/jem/soul.yaml` |
| 5 | `antipode7474@gmail.com` | **Omega — Security & Hardening** | `project_instructions_05_security_hardening.md` | `review_05_security_hardening.md` | `src/omega/observability.py`, `oracle/health_monitor.py`, `Dockerfile.iris`, `Dockerfile.roc_racoon`, `SOVEREIGN_MANDATES.md` |
| 6 | `lilithasterion@gmail.com` | **Omega — MCP Infrastructure** | `project_instructions_06_mcp_infrastructure.md` | `review_06_mcp_infrastructure.md` | `mcp/omega_hub/server.py`, `src/omega/mcp_runtime.py`, `opencode.json`, `deploy/infra/docker-compose.yml` |
| 7 | `thejedifather@gmail.com` | **Omega — CLI & Developer Experience** | `project_instructions_07_cli_dx.md` | `review_07_cli_dx.md` | `src/omega/cli/oracle_cli.py`, `oracle/orchestrator.py`, `.opencode/agents/builder.md`, `AGENTS.md`, `Makefile` |
| 8 | `taylorbare27@gmail.com` | **Omega — Strategy & Community** | `project_instructions_08_strategy_docs.md` | `review_08_strategy_docs.md` | `docs/MASTER_LEDGER.md`, `decisions/PIVOT_LOG.md`, `strategy/XOE_NOVAI_FOUNDATION_STRATEGIC_PLAN.md`, `LICENSE`, `CONTRIBUTING.md` |

---

## Critical Notes

### RAG Threshold Bug
Claude Projects uses a file-count-based RAG trigger (~13 files), not a token-size trigger. If you add more than 12 files to Project Knowledge, Claude is forced into RAG mode regardless of how small the files are. **Keep each project at 12 knowledge files or fewer.**

The knowledge files listed above are the **essential minimum**. If you want to add more, consolidate by merging related content into fewer files rather than adding new files.

### Instructions vs Knowledge Files
- **Project Instructions** (the text field): Part of the system prompt. Not counted toward RAG threshold. Higher priority.
- **Project Knowledge** (file attachments): RAG-indexed. Counted toward RAG threshold (~13 file cap). Lower priority than instructions.

Put critical context in **Instructions**, supplementary context in **Knowledge**.

### Post-Review Cleanup
After the fleet review completes:
1. Collect all 8 reports into `docs/review/report_0X_*.md`
2. Set repo back to **Private**
3. Optionally archive the Projects or repurpose for future review cycles

---

*One account, one domain, one project. The fleet is assembled.*
