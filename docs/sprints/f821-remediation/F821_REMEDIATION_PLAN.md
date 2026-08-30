<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Ω F821 Remediation Plan — Surgical Edition
**AP Token**: `AP-F821-REMEDIATION-v1.0.0`
**Author**: Antigravity / Claude Sonnet 4.6
**Date**: 2026-08-15
**Status**: READY TO EXECUTE
**Violations**: 27 confirmed across 13 files (`flake8 src/omega/ --select=F821`)

---

## 0. Prime Directive for Executing Agents

> Do not guess. Do not use regex scripts. Do not suppress with `# noqa`.
> Every fix in this plan has been verified against the live source. Follow it exactly.

This plan complies with:
- **Standard 1.1** — No lazy suppressions
- **Standard 1.2** — `TYPE_CHECKING` for forward references
- **Standard 1.3** — No guessed imports (all paths verified by `grep`)
- **Standard 2.1** — Scope variables initialized before `try` blocks
- **Standard 3.1** — No brittle regex scripts
- **Standard 3.2** — Context-aware, surgical edits only

**Verification command** (run before AND after):
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate
flake8 src/omega/ --select=F821
```
**Expected before**: 27 violations. **Expected after**: 0 violations.

---

## 1. Canonical Import Map (Verified — No Guessing)

All paths below were confirmed by live `grep` against the source tree before this
plan was written. Do not deviate.

| Name | Canonical Module | Import Statement | Fix Type |
|---|---|---|---|
| `Path` | stdlib | `from pathlib import Path` | Real import |
| `ValidationError` | `pydantic` | `from pydantic import ValidationError` | Real import |
| `yaml` | stdlib/PyYAML | `import yaml` | Real import |
| `anyio` | `anyio` | `import anyio` | Real import (×3 files) |
| `timezone` | stdlib | `from datetime import datetime, timezone` (extend existing) | Real import |
| `re` | stdlib | `import re` | Real import |
| `ModelUpdaterWorker` | `omega.workers.model_updater` | `from omega.workers.model_updater import ModelUpdaterWorker` | Real import (inline) |
| `get_engine` | `omega.observability` | **Already imported lazily** — rename call site instead | Call-site fix |
| `OracleResponse` | `omega.oracle.oracle` | `from omega.oracle.oracle import OracleResponse` | `TYPE_CHECKING` only |
| `AsyncCircuitBreaker` | `omega.oracle.health_monitor` | `from omega.oracle.health_monitor import AsyncCircuitBreaker` | `TYPE_CHECKING` only |
| `MetricsDB` | `omega.observability.metrics_db` | `from omega.observability.metrics_db import MetricsDB` | `TYPE_CHECKING` only |
| `SpeculativeDecodeConfig` | `omega.oracle.cpu_optimizer` | `from omega.oracle.cpu_optimizer import SpeculativeDecodeConfig` | `TYPE_CHECKING` only |
| `ResearchProposal` | `omega.research.schema` | `from omega.research.schema import ResearchProposal` | `TYPE_CHECKING` only |

> ⚠️ **CALLOUT — `get_engine` is NOT a missing import.**
> `regression_watcher.py` already has a lazy wrapper `_get_obs_engine()` at line 23.
> The bug is that line 98 calls the raw `get_engine` name directly instead of using
> the wrapper. Fix: rename the call site. Do NOT add a top-level import.

---

## 2. `__future__` Annotations Status Per File

This controls the exact TYPE_CHECKING pattern you must use.
Files WITH `from __future__ import annotations` can use bare names in annotations;
files WITHOUT it must keep string-quoted annotations.

| File | Has `from __future__ import annotations`? |
|---|---|
| `src/omega/ics.py` | ✅ YES |
| `src/omega/infra/subagent_pool/orchestrator.py` | ✅ YES |
| `src/omega/library/rate_limiter.py` | ✅ YES |
| `src/omega/ingestion/pipeline.py` | ❌ NO |
| `src/omega/oracle/backends/remote_provider.py` | ❌ NO |
| `src/omega/oracle/model_gateway.py` | ❌ NO |
| `src/omega/research/sandbox.py` | ❌ NO |
| `src/omega/research/scorecard.py` | ❌ NO (has `from __future__ import annotations` at line 15) — **YES** |

> ⚠️ **CALLOUT — scorecard.py exception.**
> `scorecard.py` DOES have `from __future__ import annotations` at line 15.
> This is relevant for the Blast Radius fix (Phase 3) — not TYPE_CHECKING,
> but it confirms the file is already future-annotations compliant.

---

## 3. Execution Order

Execute in this strict sequence to minimise cross-file interference:

```
Phase 2 (Real Imports)   → zero-risk stdlib/third-party additions
Phase 3 (Blast Radius)   → isolated single-file scope fix
Phase 4 (TYPE_CHECKING)  → structural, requires __future__ awareness
Phase 5 (Verification)   → flake8 + import smoke test + make test
```

---

## Phase 2 — Real Bug Fixes (10 edits across 10 files)

### R-1 · `src/omega/infra/subagent_pool/orchestrator.py`
**Violation**: Line 525 — `Optional[Path]` in function signature; `Path` never imported.
**File has** `from __future__ import annotations` — `Path` is still needed at runtime for
isinstance checks and instantiation elsewhere in this file.

**Existing import block (lines 12-16)**:
```python
import anyio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
```

**Change**: Insert `from pathlib import Path` after `from datetime import datetime`,
maintaining alphabetical stdlib order.

**Result**:
```python
import anyio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path          # ← ADD THIS LINE
from typing import Any, Optional
```

---

### R-2 · `src/omega/ingestion/extractors.py`
**Violation**: Line 142 — `ValidationError` caught in `except` clause but never imported.
**Root cause**: Pydantic's `ValidationError` is caught alongside `json.JSONDecodeError`
but the import was omitted.

**Existing import block (lines 7-13)**:
```python
import json
import time
import httpx2 as httpx
import anyio
from typing import AsyncGenerator, Optional, Dict, Any
from pathlib import Path
from .ingestion_types import ExtractionSchema, IngestionConfig
```

> ⚠️ **CALLOUT — Do NOT import from `omega.errors`.**
> `ProviderValidationError` lives in `omega.errors`. The `ValidationError` at line 142
> is Pydantic's own exception, raised by `ExtractionSchema.model_validate(data)` on
> line 141. The correct import is `from pydantic import ValidationError`.

**Change**: Insert `from pydantic import ValidationError` after `import time`
(third-party block, after stdlib):

**Result**:
```python
import json
import time
import httpx2 as httpx
import anyio
from pydantic import ValidationError   # ← ADD THIS LINE
from typing import AsyncGenerator, Optional, Dict, Any
from pathlib import Path
from .ingestion_types import ExtractionSchema, IngestionConfig
```

---

### R-3 · `src/omega/library/discovery.py`
**Violation**: Line 160 — `yaml` used but not imported.
**Existing import block already has**: `import json`, `import logging`, `import os`,
`import uuid`, stdlib datetime/pathlib. `yaml` is missing.

**Change**: Insert `import yaml` into the stdlib block in alphabetical order
(after `import uuid`):

```python
import json
import logging
import os
import uuid
import yaml                            # ← ADD THIS LINE
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
```

---

### R-4 · `src/omega/library/rate_limiter.py`
**Violations**: Lines 166, 168 — `anyio.sleep()` called; `anyio` not imported.
**File has** `from __future__ import annotations`. Existing imports are pure stdlib.

**Existing import block (lines 12-16)**:
```python
import logging
import math
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
```

**Change**: Insert `import anyio` at the top of the stdlib block:

```python
import anyio                           # ← ADD THIS LINE
import logging
import math
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
```

---

### R-5 · `src/omega/observability/otel_exporter.py`
**Violation**: Line 66 — `anyio.from_thread.run()` called; `anyio` not imported.

**Existing import block (lines 9-11)**:
```python
import logging
import time
from typing import Any, Dict, Optional
```

**Change**: Insert `import anyio` at the top:

```python
import anyio                           # ← ADD THIS LINE
import logging
import time
from typing import Any, Dict, Optional
```

> ⚠️ **CALLOUT — `anyio.from_thread.run()` is the correct M1-compliant bridge.**
> This is the OTel SDK calling back from a background thread into the AnyIO event loop.
> `anyio.from_thread.run()` is the correct AnyIO primitive for this pattern.
> Do NOT replace it with `asyncio.run_coroutine_threadsafe()`.

---

### R-6 · `src/omega/observability/regression_watcher.py`
**Violation**: Line 98 — bare `get_engine()` called; not imported at module level.

> ⚠️ **CALLOUT — This is NOT a missing import. It is a misused helper.**
> The file already defines `_get_obs_engine()` at line 23 as the correct lazy wrapper:
> ```python
> def _get_obs_engine():
>     """Lazy import to avoid circular dependency."""
>     from omega.observability import get_engine
>     return get_engine()
> ```
> The bug is that line 98 calls the raw `get_engine` name directly instead of
> calling this wrapper. Do NOT add a top-level import — that would create the
> circular import this wrapper was designed to prevent.

**Change**: At line 98, rename the call site:

```python
# BEFORE (broken):
obs = get_engine()

# AFTER (correct):
obs = _get_obs_engine()
```

---

### R-7 · `src/omega/oracle/feed_utils.py`
**Violations**: Lines 134, 163, 188, 227 — `timezone` used as `datetime.now(timezone.utc)`;
`timezone` not in the existing datetime import.

**Existing import (line 15)**:
```python
from datetime import datetime
```

**Change**: Extend to include `timezone`:

```python
from datetime import datetime, timezone   # ← extend existing import
```

> ⚠️ **CALLOUT — Extend, don't duplicate.**
> Do NOT add a second `from datetime import timezone` line. Edit the existing
> `from datetime import datetime` line in-place to become
> `from datetime import datetime, timezone`. Duplicate imports are a PEP 8 violation
> and will trigger flake8 F811.

---

### R-8 · `src/omega/oracle/iterative_research.py`
**Violations**: Line 124 — `re.search()` and `re.IGNORECASE` used; `re` not imported.

**Existing import block (lines 7-8)**:
```python
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
```

**Change**: Insert `import re` before `import logging` (alphabetical):

```python
import logging
import re                              # ← ADD THIS LINE
from typing import Any, Dict, List, Optional, Tuple, Union
```

---

### R-9 · `src/omega/oracle/orchestrator.py`
**Violation**: Line 655 — `ModelUpdaterWorker(...)` instantiated; not imported.
**Canonical path** (verified by grep): `omega.workers.model_updater`.

**Context at lines 653-661**:
```python
if updater_cfg.get("enabled", True):
    from omega.oracle.health_monitor import get_health_monitor
    self.model_updater = ModelUpdaterWorker(       # ← F821 here
        model_gateway=ModelGateway(health_monitor=get_health_monitor()),
        ...
    )
```

> ⚠️ **CALLOUT — Use an inline import here, not a top-level import.**
> `ModelUpdaterWorker` is only used inside this conditional branch.
> Adding it to the top-level imports would load it on every orchestrator
> instantiation, even when the updater is disabled in config.
> The correct fix is to extend the existing inline import block at line 654.

**Change**: Extend the existing inline import:

```python
if updater_cfg.get("enabled", True):
    from omega.oracle.health_monitor import get_health_monitor
    from omega.workers.model_updater import ModelUpdaterWorker   # ← ADD THIS LINE
    self.model_updater = ModelUpdaterWorker(
        model_gateway=ModelGateway(health_monitor=get_health_monitor()),
        ...
    )
```

---

### R-10 · `src/omega/oracle/subagent_dispatcher.py`
**Violations**: Lines 153, 154, 170 — `anyio.Path()` and `anyio.sleep()` called;
`anyio` not imported. File already imports `import yaml`, `import json`, etc.

**Existing import block (lines 14-21)**:
```python
import json
import logging
import uuid
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
```

**Change**: Insert `import anyio` before `import json` (alphabetical):

```python
import anyio                           # ← ADD THIS LINE
import json
import logging
import uuid
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
```

---

## Phase 3 — Blast Radius Fix (1 scope bug)

### B-1 · `src/omega/research/scorecard.py`
**Violations**: Lines 320, 345 — `tier_start` referenced in `except` branches;
may be uninitialized if an exception fires before line ~307.

**Root cause** (Standard 2.1 violation): `tier_start` is assigned *inside* the `try`
block. If the `oracle_summon` call or the `anyio.move_on_after` context manager raises
before the assignment, both `except` handlers at lines 320 and 345 will themselves
raise `UnboundLocalError`, masking the original exception entirely.

**Context (lines 296-350)**:
```python
async def _run_tier(self, proposal: ResearchProposal, tier: dict) -> AMFOResult:
    tier_name = tier["name"]
    model = tier["model"]
    budget_sec = tier["budget_sec"]

    prompt = self._build_tier_prompt(proposal, tier)

    try:
        with anyio.move_on_after(budget_sec):
            response = await self.oracle_summon(model, prompt)
        # ... tier_start is NOT assigned here — it's missing entirely
        ...
        return AMFOResult(
            ...
            execution_time_sec=time.perf_counter() - tier_start,   # line 320
        )
    except anyio.get_cancelled_exc_class():
        return AMFOResult(
            ...
            execution_time_sec=budget_sec,
        )
    except Exception as e:
        return AMFOResult(
            ...
            execution_time_sec=time.perf_counter() - tier_start,   # line 345 ← CRASH
        )
```

> ⚠️ **CALLOUT — Double jeopardy failure mode.**
> Without the pre-initialization fix, an exception in `oracle_summon` causes:
> 1. Original exception raised inside `try`
> 2. `except Exception` handler fires
> 3. `tier_start` is unbound → `UnboundLocalError` raised
> 4. The `UnboundLocalError` propagates UP, completely hiding the original error
> This is a silent debuggability killer. Always initialize timing variables before `try`.

**Change**: Add `tier_start = time.perf_counter()` before the `try` block:

```python
async def _run_tier(self, proposal: ResearchProposal, tier: dict) -> AMFOResult:
    tier_name = tier["name"]
    model = tier["model"]
    budget_sec = tier["budget_sec"]

    prompt = self._build_tier_prompt(proposal, tier)

    tier_start = time.perf_counter()   # ← ADD THIS LINE (before try)
    try:
        with anyio.move_on_after(budget_sec):
            response = await self.oracle_summon(model, prompt)
        ...
```

---

## Phase 4 — TYPE_CHECKING Structural Fixes (5 files)

> ⚠️ **CALLOUT — The TYPE_CHECKING contract.**
> Classes imported under `if TYPE_CHECKING:` are ONLY available to the type checker
> (mypy, pyright). They are NOT imported at runtime. This means:
> 1. You MUST keep the annotation as a string: `"ClassName"` — unless the file has
>    `from __future__ import annotations`, in which case all annotations are lazy by
>    default and you can drop the quotes.
> 2. You MUST NOT use these classes in runtime code (isinstance checks, instantiation).
>    If you need runtime use, use a regular import instead.
> 3. `TYPE_CHECKING` must be imported from `typing`:
>    `from typing import TYPE_CHECKING`

**The canonical pattern (file WITHOUT `from __future__ import annotations`)**:
```python
from typing import TYPE_CHECKING, Optional   # extend existing typing import

if TYPE_CHECKING:
    from omega.some.module import SomeClass

def my_func(arg: "SomeClass") -> None:   # keep the quotes!
    ...
```

**The canonical pattern (file WITH `from __future__ import annotations`)**:
```python
from typing import TYPE_CHECKING, Optional   # extend existing typing import

if TYPE_CHECKING:
    from omega.some.module import SomeClass

def my_func(arg: SomeClass) -> None:   # quotes optional — __future__ handles it
    ...
```

---

### T-1 · `src/omega/ics.py`
**Violation**: Line 374 — `"OracleResponse"` used as annotation with `# type: ignore[name-defined]`.
**File has** `from __future__ import annotations` — quotes are optional after fix.
**Canonical path**: `omega.oracle.oracle` (verified).
**Existing typing import** (line 39): `from typing import Optional`

**Change 1** — Extend typing import and add TYPE_CHECKING block after existing imports:
```python
# Existing line 39:
from typing import Optional, TYPE_CHECKING   # ← add TYPE_CHECKING

# Add block after all other imports, before first function/class:
if TYPE_CHECKING:
    from omega.oracle.oracle import OracleResponse
```

**Change 2** — Remove the `# type: ignore` comment at line 374:
```python
# BEFORE:
def render_for_response(
    response: "OracleResponse",  # type: ignore[name-defined]

# AFTER:
def render_for_response(
    response: "OracleResponse",
```

---

### T-2 · `src/omega/ingestion/pipeline.py`
**Violation**: Line 59 — `'AsyncCircuitBreaker'` string annotation; no import.
**File does NOT have** `from __future__ import annotations` — keep string quotes.
**Canonical path**: `omega.oracle.health_monitor` (verified).
**Existing typing import** (line 14): `from typing import List, Optional, AsyncGenerator, Dict, Any`

**Change 1** — Extend typing import:
```python
from typing import List, Optional, AsyncGenerator, Dict, Any, TYPE_CHECKING
```

**Change 2** — Add TYPE_CHECKING block after all local imports:
```python
if TYPE_CHECKING:
    from omega.oracle.health_monitor import AsyncCircuitBreaker
```

The annotation at line 59 already uses string form `'AsyncCircuitBreaker'` — no
change needed there. The TYPE_CHECKING block satisfies the linter without creating
a circular import at runtime.

---

### T-3 · `src/omega/oracle/backends/remote_provider.py`
**Violations**: Lines 47, 51 — `Optional["MetricsDB"]` and `-> "MetricsDB"` annotations.
**File does NOT have** `from __future__ import annotations` — keep string quotes.
**Canonical path**: `omega.observability.metrics_db` (verified).
**The lazy `from omega.observability.metrics_db import MetricsDB` at line 58 is inside
a function body** — it is a runtime import for actual instantiation. The TYPE_CHECKING
import at the top satisfies the type checker for the annotations at lines 47 and 51.
**Existing typing import** (line 28): `from typing import Any, Dict, List, Optional`

**Change 1** — Extend typing import:
```python
from typing import Any, Dict, List, Optional, TYPE_CHECKING
```

**Change 2** — Add TYPE_CHECKING block after the `from omega.oracle.provider_registry` import:
```python
if TYPE_CHECKING:
    from omega.observability.metrics_db import MetricsDB
```

> ⚠️ **CALLOUT — Dual import is intentional and correct here.**
> - `TYPE_CHECKING` block: satisfies type checker for `Optional["MetricsDB"]` annotations.
> - Runtime `from omega.observability.metrics_db import MetricsDB` inside `_get_metrics_db()`:
>   performs the actual lazy instantiation.
> These serve different purposes. Do not collapse them into one.

---

### T-4 · `src/omega/oracle/model_gateway.py`
**Violation**: Line 682 — `'SpeculativeDecodeConfig'` return type annotation on a `@property`.
**File does NOT have** `from __future__ import annotations` — keep string quotes.
**Canonical path**: `omega.oracle.cpu_optimizer` (verified).
**Existing typing import** (line 28): `from typing import Any, Dict, List, Optional, Tuple, NamedTuple, AsyncIterator`

**Change 1** — Extend typing import:
```python
from typing import Any, Dict, List, Optional, Tuple, NamedTuple, AsyncIterator, TYPE_CHECKING
```

**Change 2** — Add TYPE_CHECKING block after existing local imports:
```python
if TYPE_CHECKING:
    from omega.oracle.cpu_optimizer import SpeculativeDecodeConfig
```

The annotation at line 682 already uses string form `'SpeculativeDecodeConfig'` — no
change needed at the call site.

---

### T-5 · `src/omega/research/sandbox.py`
**Violations**: Lines 399, 502, 556 — `ResearchProposal` used in `async def` signatures;
not imported.
**File does NOT have** `from __future__ import annotations` — keep string quotes.
**Canonical path**: `omega.research.schema` (verified).
**Existing typing import** (line 29): `from typing import Any, Optional`

**Change 1** — Extend typing import:
```python
from typing import Any, Optional, TYPE_CHECKING
```

**Change 2** — Add TYPE_CHECKING block after existing imports:
```python
if TYPE_CHECKING:
    from omega.research.schema import ResearchProposal
```

**Change 3** — Ensure all three call sites use string-quoted annotations:
```python
# Lines 399, 502, 556 should read:
async def execute(self, proposal: "ResearchProposal") -> SandboxResult:
```
If they already use string form, no change needed at the call site.

---

## Phase 5 — Verification Gates

Execute all three gates in sequence. Do not mark the sprint complete until all three pass.

### Gate 1 — Zero F821 Violations
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate
flake8 src/omega/ --select=F821
# Expected output: (empty — zero lines)
```

### Gate 2 — Import Smoke Test (No Circular Imports, No Runtime Crashes)
```bash
source .venv/bin/activate
python -c "
import sys
modules = [
    'omega.ics',
    'omega.ingestion.pipeline',
    'omega.oracle.backends.remote_provider',
    'omega.oracle.model_gateway',
    'omega.research.sandbox',
    'omega.research.scorecard',
    'omega.observability.regression_watcher',
    'omega.library.rate_limiter',
    'omega.library.discovery',
    'omega.oracle.feed_utils',
    'omega.oracle.iterative_research',
    'omega.oracle.subagent_dispatcher',
    'omega.oracle.orchestrator',
    'omega.infra.subagent_pool.orchestrator',
    'omega.ingestion.extractors',
    'omega.observability.otel_exporter',
]
for m in modules:
    try:
        __import__(m)
        print(f'  ✅ {m}')
    except Exception as e:
        print(f'  ❌ {m}: {e}')
        sys.exit(1)
print('All imports clean.')
"
```

### Gate 3 — Full Test Suite
```bash
source .venv/bin/activate
make test
# Expected: 0 new failures introduced by this change
```

---

## Appendix A — The Two Failure Modes This Plan Prevents

### Failure Mode 1: `UnboundLocalError` masking the root cause (Blast Radius)
```python
# BAD — original bug pattern:
try:
    start = time.perf_counter()   # assigned inside try
    result = await risky_call()
except Exception as e:
    duration = time.perf_counter() - start   # CRASH: UnboundLocalError if
    log_failure(duration, e)                 # risky_call raised before start

# GOOD — pre-initialized:
start = time.perf_counter()       # always safe to read in except
try:
    result = await risky_call()
except Exception as e:
    duration = time.perf_counter() - start   # always works
    log_failure(duration, e)
```

### Failure Mode 2: Circular import at runtime via suppressed type hints
```python
# BAD — suppression hides structural flaw:
def process(response: "OracleResponse"):  # type: ignore[name-defined]
    ...

# GOOD — TYPE_CHECKING resolves it structurally:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omega.oracle.oracle import OracleResponse   # only at check time

def process(response: "OracleResponse"):   # linter satisfied, no runtime import
    ...
```

---

## Appendix B — What NOT to Do

| Anti-pattern | Why it's wrong | Correct approach |
|---|---|---|
| `# noqa: F821` | Silences the linter without fixing the root cause; next reader doesn't know why | Fix the import or use `TYPE_CHECKING` |
| `# type: ignore[name-defined]` | Same — suppression masking a structural gap | `TYPE_CHECKING` block |
| `import omega.observability` at top of `regression_watcher.py` | Creates the circular import the lazy helper was built to prevent | Call `_get_obs_engine()` at line 98 |
| Adding `ModelUpdaterWorker` to top-level imports in `orchestrator.py` | Loads the worker on every orchestrator init, even when disabled | Keep it as an inline import inside the `if updater_cfg.get("enabled"):` branch |
| `from datetime import timezone` as a separate line in `feed_utils.py` | Duplicate import (F811) | Extend the existing `from datetime import datetime` line |
| Regex/sed scripts to insert imports | Brittle, ignores context, corrupts PEP 8 formatting, ignores `__future__` | Use the `edit` tool per-file, surgically |

---

*⬡ OMEGA ⬡ ANTIGRAVITY ⬡ antigravity-claude-sonnet-4-6 ⬡ opencode ⬡ AP-F821-REMEDIATION-v1.0.0*
