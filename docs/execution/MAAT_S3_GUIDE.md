# 🔱 EXECUTION GUIDE: MA'AT (The Builder)
**S3 Ingestion Hardening — Infrastructure & Engineering**
**Jurisdiction**: P1 (Infrastructure), P3 (Engineering), P4 (Integration), P5 (Governance)

## 🎯 OBJECTIVE
Establish the physical and logical foundation for the Ingestion Pipeline. You are responsible for the "Pipe"—from the raw environment to the worker that drives the data.

---

## 🛠️ PHASE 0: THE BLOCKERS (Day 0)
**MUST be completed and verified via Hivemind before any other agent starts.**

### B1: Redis Health Check
- **Action**: Verify `omega-redis` is healthy.
- **Verification**: Run `redis-cli ping` $\rightarrow$ expect `PONG`.
- **Config**: Ensure `config/omega.yaml` `redis:` block is correct.

### B2: CLTK Model Provisioning
- **Action**: Pre-download Greek models for the Linguistic Observatory.
- **Path**: `/media/arcana-novai/omega_library/models/cltk/`
- **Env**: Set `CLTK_DATA` environment variable in `scripts/setup.sh`.

### B3: Sovereign Proxy Deployment (P0)
- **Action**: Deploy `omega-sovereign-proxy` (Nginx/Envoy).
- **Implementation**:
    - Configure Nginx to strip identifying headers (`User-Agent`, `X-Forwarded-For`).
    - Route all traffic through local Tor SOCKS5 (`127.0.0.1:9050`).
- **Verification**: `curl http://omega-sovereign-proxy/health` $\rightarrow$ `200 OK`.

### B4: crawl4ai System Dependencies
- **Action**: Install Playwright Chromium and required system libraries.
- **Command**: `playwright install chromium` + `apt-get install libnss3 libatk1.0-0 ...`
- **Verification**: `crawl4ai-doctor` returns clean.

---

## 🏗️ PHASE 1: THE PIPE (Day 3-6)
*Dependency: T1 (Double-Fsync) must be complete.*

### T2: IngestionWorker Implementation (Persistent Pool)
- **File**: `src/omega/ingestion/worker.py`
- **Logic**:
    1. Rename `SovereignWorker` $\rightarrow$ `IngestionWorker`.
    2. Implement a **Persistent Worker Pool** using `concurrent.futures.ProcessPoolExecutor`.
    3. Wrap pool calls in `anyio.to_thread.run_sync`.
    4. Use `anyio.Semaphore(2)` to limit concurrent jobs (CPU-friendly).
    5. Implement `_execute_job` with `anyio.move_on_after(300)` for timeouts.
- **Acceptance**: Worker processes 5 concurrent jobs without cold-start latency on subsequent runs.

### T3: WebScraper Implementation (Context Recycling)
- **File**: `src/omega/ingestion/scraper.py`
- **Logic**:
    1. Rename `SovereignScraper` $\rightarrow$ `WebScraper`.
    2. Implement `scrape(url, tier="fast")`:
       - **Fast**: `AsyncWebCrawler(headless=True)`.
       - **Deep**: `AsyncWebCrawler(headless=False, undetected_browser=True)`.
       - **Somatic Reset**: Close and recreate `browser_context` every 50 pages to prevent memory leaks.
       - Use `BM25ContentFilter` for surgical extraction.
    3. Implement `validate_safe_input(url)`: Block `file://`, `javascript:`, and private IP ranges.
- **Acceptance**: Successfully scrapes a standard page (Fast) and a complex SPA (Deep) without OOM.

---

## 📜 PHASE 3: THE RECORD (Day 9-10)
*Dependency: T2-T6 complete.*

### T9: Blueprint Sync & Governance
- **File**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`
- **Action**: 
    1. Update §5.1d (Iron Wall) and §5.2 (Tier 2) to reflect S3 completion.
    2. Strip all "Sovereign" branding from the blueprint.
    3. Lock the A2A Agent Card schema in the documentation.
- **Acceptance**: Blueprint is a clean, technical SSOT with zero cargo-cult terminology.

---

## 🛡️ MANDATES & CONSTRAINTS
- **M1 (AnyIO)**: No `asyncio`. Use `anyio.to_thread.run_sync` for blocking I/O.
- **M13 (Temple-Grade)**: All new code must have 100% test coverage.
- **M16 (Modularization)**: No hardcoded paths. Use `DATA_DIR`.
- **Sovereign Proxy**: Ensure all external calls in T3/T4 route through the proxy.

*⬡ OMEGA ⬡ MA'AT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_execution ⬡ BUILD_GUIDE*
