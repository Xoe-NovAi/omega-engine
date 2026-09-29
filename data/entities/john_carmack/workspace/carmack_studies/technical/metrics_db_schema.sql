-- 🔱 Omega Engine Metrics Schema (WAL Mode)
-- ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ METRICS-SCHEMA ⬡ 2026-07-01

-- Enable Write-Ahead Logging for high-concurrency, non-blocking reads/writes
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA temp_store=MEMORY;
PRAGMA mmap_size=3000000000;

-- 1. General Events Ledger
CREATE TABLE IF NOT EXISTS ufl_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    payload JSON
);

-- 2. Error Ledger (Separated for fast anomaly querying)
CREATE TABLE IF NOT EXISTS ufl_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    trace_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    error_type TEXT NOT NULL,
    error_message TEXT NOT NULL,
    context JSON
);

-- 3. Circuit Breaker State Transitions
CREATE TABLE IF NOT EXISTS ufl_breaker_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    provider TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    reason TEXT
);

-- 4. Token & Latency Ledger (For fast cost/performance analytics)
CREATE TABLE IF NOT EXISTS ufl_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    trace_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    model_used TEXT,
    latency_ms REAL NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    is_cloud BOOLEAN NOT NULL
);

-- Indices for fast forensic lookups
CREATE INDEX IF NOT EXISTS idx_events_trace ON ufl_events(trace_id);
CREATE INDEX IF NOT EXISTS idx_events_provider ON ufl_events(provider);
CREATE INDEX IF NOT EXISTS idx_errors_trace ON ufl_errors(trace_id);
CREATE INDEX IF NOT EXISTS idx_perf_provider ON ufl_performance(provider);
CREATE INDEX IF NOT EXISTS idx_perf_latency ON ufl_performance(latency_ms);
