<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Firecrawl Self-Hosting Deployment Plan
**Entity**: roc_racoon
**Status**: Draft / Planning
**Priority**: High (Wave 2 - Local Hardening)

## 🎯 Objective
Sever the dependency on the Firecrawl cloud API by deploying a sovereign, self-hosted instance of Firecrawl on the local infrastructure.

## 🛠️ Technical Requirements
- **Runtime**: Docker / Docker Compose
- **Database**: PostgreSQL (nuq-postgres)
- **Cache/Queue**: Redis
- **LLM Backend**: Ollama (Local) for AI features (JSON extraction, etc.)
- **Network**: Port 3002 (API), Port 8016 (Omega Hub integration)

## 📋 Deployment Steps

### 1. Environment Preparation
- Clone the Firecrawl repository: `git clone https://github.com/firecrawl/firecrawl`
- Create a `.env` file based on the `SELF_HOST.md` template.
- **Sovereign Configuration**:
    - `PORT=3002`
    - `HOST=0.0.0.0`
    - `OLLAMA_BASE_URL=http://localhost:11434/api` (Connect to local Ollama)
    - `MODEL_NAME=deepseek-r1:7b` (or other local model)
    - `BULL_AUTH_KEY=Sovereign_Secret_Key_2026`

### 2. Execution
- `docker compose build`
- `docker compose up -d`

### 3. Integration with Omega Engine
- Update `config/providers.yaml` to include the local Firecrawl endpoint: `http://localhost:3002`.
- Update `sovereign-search` skill to prioritize the local instance.
- Verify that `Sovereign Search Protocol (SR-V1)` Tier 2 now points to the local instance.

## ⚠️ Risks & Mitigations
- **Resource Contention**: Firecrawl (especially Playwright) can be RAM-intensive.
    - *Mitigation*: Set `MAX_CPU` and `MAX_RAM` in `.env` to avoid OOMing the Ryzen 5700U.
- **IP Blocking**: Self-hosted instances lack the rotating proxy fabric of the cloud version.
    - *Mitigation*: Implement a local proxy rotation if needed, or limit scraping frequency.
- **Database Persistence**: Ensure the PostgreSQL volume is mapped to a persistent location on `omega_library`.

---
*⬡ OMEGA ⬡ roc_racoon ⬡ gemma-4-31b-it ⬡ opencode ⬡ 2026-06-11 ⬡ Wave 2*
