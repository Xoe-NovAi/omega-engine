# 🔱 Omega Engine — Token Budget & Daily Quota Management
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-08

**AP Token**: `AP-R08-BUDGET-DESIGN-v1.0.0`
**Status**: ✅ READY
**Last Updated**: 2026-05-14

---

## 🎯 Objectives
Design a lightweight, persistent system to track daily token and request usage across multiple inference providers to ensure the Omega Engine remains within free-tier limits and avoids API bans.

## 🛠️ Storage Evaluation

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **Flat JSON** | Zero dependencies, human-readable. | No atomicity, potential for corruption on crash, slow for frequent updates. | ❌ Rejected |
| **Redis** | Extremely fast, existing infra. | Volatile (unless AOF enabled), dependency on container uptime. | ⚠️ Secondary |
| **SQLite** | Atomic, persistent, single-file, built-in to Python, structured queries. | Slightly slower than Redis (negligible for budget tracking). | ✅ **Recommended** |

**Decision**: Use **SQLite** stored at `data/budget.db`. This provides the best balance of reliability and performance for a low-frequency (daily) update cycle.

## 📐 Persistence Strategy

### Schema Design
A single table `usage_stats` to track aggregates per provider per day.

```sql
CREATE TABLE usage_stats (
    date TEXT,           -- Format: YYYY-MM-DD
    provider TEXT,       -- e.g., 'google', 'sambanova', 'cerebras'
    tokens INTEGER,      -- Total tokens consumed
    requests INTEGER,    -- Total requests made
    PRIMARY KEY (date, provider)
);
```

### Lifecycle & Reset
- **Midnight UTC Reset**: The system does not need a cron job. Instead, it uses a "lazy reset" strategy. Every call to `consume()` checks the current UTC date. If no entry exists for `(current_date, provider)`, a new row is initialized.
- **Survival**: Being file-based, the budget survives process restarts, container re-deploys, and system reboots.

## 📊 Budget Schema & Configuration

Budgets are defined in `config/providers.yaml` to allow easy adjustments without code changes.

```yaml
# config/providers.yaml snippet
providers:
  google:
    daily_token_limit: 1000000
    daily_request_limit: 1500
    priority: 1
  sambanova:
    daily_token_limit: 500000
    daily_request_limit: 1000
    priority: 2
  cerebras:
    daily_token_limit: 2000000
    daily_request_limit: 2000
    priority: 3
```

## ⚠️ Exhaustion Behavior

When a provider's `daily_token_limit` or `daily_request_limit` is reached:

1. **Silent Fallback (Primary)**: The `ModelGateway` receives a `BudgetExhausted` signal and immediately proceeds to the next provider in the fallback chain. This ensures zero interruption to the user experience.
2. **Observability Log**: An `EVENT_BUDGET_EXHAUSTED` is logged with the provider name and trace ID.
3. **User Notification (Optional)**: If the system is in `full` header mode, a transient warning `[Quota: Provider X Exhausted]` can be appended to the session header for one turn.
4. **Hard Stop**: Only occurs if the *entire* fallback chain (including local `lmster`) is exhausted or unavailable.

## 💻 Proposed Interface: `resource_budget.py`

```python
import sqlite3
from datetime import datetime
from typing import Dict, Optional

class BudgetManager:
    def __init__(self, db_path: str = "data/budget.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    date TEXT, provider TEXT, tokens INTEGER, requests INTEGER,
                    PRIMARY KEY (date, provider)
                )
            """)

    def consume(self, provider: str, tokens: int, requests: int = 1, limits: Optional[Dict] = None) -> bool:
        """
        Updates usage and returns True if within limits, False if exhausted.
        """
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            # Get current usage
            cursor = conn.execute(
                "SELECT tokens, requests FROM usage_stats WHERE date = ? AND provider = ?", 
                (today, provider)
            )
            row = cursor.fetchone()
            
            current_tokens, current_requests = row if row else (0, 0)
            
            # Check limits
            if limits:
                if current_tokens + tokens > limits.get('daily_token_limit', float('inf')):
                    return False
                if current_requests + requests > limits.get('daily_request_limit', float('inf')):
                    return False
            
            # Update usage
            conn.execute("""
                INSERT INTO usage_stats (date, provider, tokens, requests)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(date, provider) DO UPDATE SET
                tokens = tokens + excluded.tokens,
                requests = requests + excluded.requests
            """, (today, provider, tokens, requests))
            
            return True

    def get_remaining(self, provider: str, limits: Dict) -> Dict:
        today = datetime.utcnow().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT tokens, requests FROM usage_stats WHERE date = ? AND provider = ?", 
                (today, provider)
            )
            row = cursor.fetchone()
            tokens, requests = row if row else (0, 0)
            
            return {
                "tokens_remaining": limits.get('daily_token_limit', 0) - tokens,
                "requests_remaining": limits.get('daily_request_limit', 0) - requests
            }
```

---
**Implementation Note for Antigravity/Cline**: 
Integrate `BudgetManager` into `src/omega/oracle/model_gateway.py`. Wrap the `_send_request` call in a `consume()` check. If it returns `False`, trigger the next provider in the `fallback_chain`.
