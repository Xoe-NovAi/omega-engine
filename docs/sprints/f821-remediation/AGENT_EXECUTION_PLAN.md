---
ap_token: AP-F821-EXECUTION-FINAL-v1.0.0
artifact: B
artifact_type: MACHINE-EXECUTABLE
author: DeepSeek V4 Flash Max Thinking (Synthesizing Model)
date: 2026-08-16
supersedes:
  - F821_REMEDIATION_PLAN.md
  - OPUS_STRATEGIC_GUIDE.md
  - HYBRID_STRATEGIC_GUIDE.md
task_id: f821-remediation-execution-20260816
status: READY TO EXECUTE
---

# AGENT EXECUTION PLAN — F821 Remediation (FINAL)

## TASK CONTRACT

- task_id: f821-remediation-execution-20260816
- objective: Resolve 27 F821 undefined-name violations across 13 files and close the pipeline gaps that allowed them to accumulate.
- working_directory: /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
- verify_command: source .venv/bin/activate && flake8 src/omega/ --select=F821

## PROHIBITIONS (VIOLATIONS ARE FAILURES)

1. Do NOT read any other file in this sprint directory. This file is the only source of truth.
2. Do NOT copy instructional markers into code. No comment containing "<--", "ADD", "CHANGE", or "TODO(plan)" may be written.
3. Do NOT use regex, sed, or scripted import injection. Use the edit tool only.
4. Do NOT add "# noqa" or "# type: ignore" suppressions.
5. Do NOT add a top-level import when this plan specifies an inline import.
6. Do NOT add an import when this plan specifies a call-site rename.
7. Do NOT modify any file not listed in this plan.

## PHASE 2 — REAL IMPORTS (10 OPERATIONS)

### OP-01: src/omega/infra/subagent_pool/orchestrator.py
- action: insert import
- anchor: existing block starts "import anyio"
- result:
```
import anyio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
```
- constraint: Path is required at runtime (isinstance checks). Not TYPE_CHECKING.

### OP-02: src/omega/ingestion/extractors.py
- action: delete duplicated file prefix, then add import
- steps:
  1. Delete lines 1-62 (first docstring, first import block, first EXTRACTION_SCHEMA).
  2. Delete the duplicate docstring lines (originally lines 64-65).
  3. In the surviving import block, add "from pydantic import ValidationError" after "import time".
- result (surviving import block):
```
import json
import time
import httpx2 as httpx
import anyio
from pydantic import ValidationError
from typing import AsyncGenerator, Optional, Dict, Any
from pathlib import Path
from .ingestion_types import ExtractionSchema, IngestionConfig
```
- constraint: ValidationError is Pydantic's exception (raised by model_validate). Do NOT import from omega.errors.

### OP-03: src/omega/library/discovery.py
- action: insert import + remove duplicate
- steps:
  1. Insert "import yaml" after "import uuid" in the stdlib block.
  2. Remove the duplicate "OmegaError," line inside the from omega.errors import ( ) block. Keep one occurrence.
- result (stdlib block):
```
import json
import logging
import os
import uuid
import yaml
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
```

### OP-04: src/omega/library/rate_limiter.py
- action: insert import
- result:
```
import anyio
import logging
import math
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
```

### OP-05: src/omega/observability/otel_exporter.py
- action: insert import
- result:
```
import anyio
import logging
import time
from typing import Any, Dict, Optional
```
- constraint: anyio.from_thread.run() is the correct M1 bridge. Do NOT replace with asyncio.run_coroutine_threadsafe.

### OP-06: src/omega/observability/regression_watcher.py
- action: rename call site
- location: line 98
- before: obs = get_engine()
- after: obs = _get_obs_engine()
- constraint: The file already defines _get_obs_engine() as a lazy wrapper to avoid circular imports. Do NOT add "from omega.observability import get_engine".

### OP-07: src/omega/oracle/feed_utils.py
- action: extend existing import
- location: line 15
- before: from datetime import datetime
- after: from datetime import datetime, timezone
- constraint: Do NOT add a second "from datetime import timezone" line.

### OP-08: src/omega/oracle/iterative_research.py
- action: insert import
- result:
```
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union
```

### OP-09: src/omega/oracle/orchestrator.py
- action: add inline import
- location: inside the "if updater_cfg.get('enabled', True):" branch
- result (branch):
```
if updater_cfg.get("enabled", True):
    from omega.oracle.health_monitor import get_health_monitor
    from omega.workers.model_updater import ModelUpdaterWorker
    self.model_updater = ModelUpdaterWorker(...)
```
- constraint: Inline only. Do NOT add to top-level imports. ModelUpdaterWorker loads heavy inference deps.

### OP-10: src/omega/oracle/subagent_dispatcher.py
- action: insert import
- result:
```
import anyio
import json
import logging
import uuid
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
```

## PHASE 3 — BLAST RADIUS (1 OPERATION)

### OP-11: src/omega/research/scorecard.py
- action: pre-initialize scope variable
- location: in _run_tier(), immediately before the "try:" block
- before:
```
    prompt = self._build_tier_prompt(proposal, tier)

    try:
```
- after:
```
    prompt = self._build_tier_prompt(proposal, tier)

    tier_start = time.perf_counter()
    try:
```
- constraint: Use time.perf_counter() (real value), NOT a dummy such as 0. Not at function top. Not inside try.

## PHASE 4 — TYPE_CHECKING (5 OPERATIONS)

- rule: TYPE_CHECKING blocks are analysis-time only. Never use these classes at runtime.
- rule: file WITH "from __future__ import annotations" may use bare names; file WITHOUT must keep string quotes.

### OP-12: src/omega/ics.py (HAS __future__)
- steps:
  1. Change "from typing import Optional" to "from typing import Optional, TYPE_CHECKING".
  2. After all imports, add:
```
if TYPE_CHECKING:
    from omega.oracle.oracle import OracleResponse
```
  3. Remove "# type: ignore[name-defined]" from the annotation at line 374. Keep the quotes.

### OP-13: src/omega/ingestion/pipeline.py (NO __future__)
- steps:
  1. Change "from typing import List, Optional, AsyncGenerator, Dict, Any" to include ", TYPE_CHECKING".
  2. After local imports, add:
```
if TYPE_CHECKING:
    from omega.oracle.health_monitor import AsyncCircuitBreaker
```
- constraint: annotation already quoted ('AsyncCircuitBreaker'). No call-site change.

### OP-14: src/omega/oracle/backends/remote_provider.py (NO __future__)
- steps:
  1. Change "from typing import Any, Dict, List, Optional" to include ", TYPE_CHECKING".
  2. After the provider_registry import, add:
```
if TYPE_CHECKING:
    from omega.observability.metrics_db import MetricsDB
```
- constraint: The runtime "from omega.observability.metrics_db import MetricsDB" inside _get_metrics_db() stays. Dual import is intentional.

### OP-15: src/omega/oracle/model_gateway.py (NO __future__)
- steps:
  1. Change "from typing import Any, Dict, List, Optional, Tuple, NamedTuple, AsyncIterator" to include ", TYPE_CHECKING".
  2. After local imports, add:
```
if TYPE_CHECKING:
    from omega.oracle.cpu_optimizer import SpeculativeDecodeConfig
```
- constraint: annotation already quoted. No call-site change.

### OP-16: src/omega/research/sandbox.py (NO __future__)
- steps:
  1. Change "from typing import Any, Optional" to include ", TYPE_CHECKING".
  2. After imports, add:
```
if TYPE_CHECKING:
    from omega.research.schema import ResearchProposal
```
  3. Verify annotations at lines 399, 502, 556 are string-quoted ("ResearchProposal"). Quote them if not.

## PHASE 5 — VERIFICATION (3 GATES, ALL MUST PASS)

### GATE 1: Zero F821
```
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate
flake8 src/omega/ --select=F821
```
- pass: empty output.

### GATE 2: Import Smoke Test
```
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
    __import__(m)
print('All imports clean.')
"
```
- pass: prints "All imports clean."

### GATE 3: Test Suite
```
source .venv/bin/activate
make test
```
- pass: no new failures.

## PHASE 6 — HARDENING (4 OPERATIONS)

### OP-17: Makefile
- action: remove both "--ignore=F821" flags from the lint target.
- before comment: "# Ignore F821: forward-reference type hints and TYPE_CHECKING-only imports are pervasive in this codebase and not actionable lint failures."
- after comment: "# F821 (undefined names) is now a HARD GATE after AP-F821-REMEDIATION-v1.0.0. All forward-reference type hints resolved via TYPE_CHECKING guards. All missing imports fixed. No more blanket suppression."

### OP-18: .pre-commit-config.yaml
- action: add hook after existing "omega-check-m23-failure-integrity" hook:
```
      - id: omega-check-f821-undefined-names
        name: Check F821 (no undefined names)
        entry: bash -c 'python -m flake8 src/omega/ --select=F821 --count --quiet && echo "No F821 violations"'
        language: system
        pass_filenames: false
        always_run: true
```

### OP-19: docs/standards/FRONTIER_AI_CODING_STANDARDS.md
- action: append Section 8 "Prevention Gates" with:
  - 8.1 The Three-Step Close: fix all violations, remove suppressions, add gate.
  - 8.2 Ban on Class-Wide Suppression: never --ignore an entire class; fix false positives structurally.
  - 8.3 Opportunistic Cleanup: fix adjacent violations in the same import block.

### OP-20: .github/workflows/ci.yml
- action: verify lint step contains "--select=E9,F63,F7,F82" with no "--ignore=F821".
- action: add comment: "Lint with flake8 (blocking — F821 is a hard gate per AP-F821-REMEDIATION-v1.0.0)".

## COMMIT CONTRACT (2 ATOMIC COMMITS)

### COMMIT 1 — fixes (Phases 2-4)
- subject: fix: resolve 27 F821 undefined-name violations across 13 files
- body:
```
- 10 real missing imports (anyio, re, yaml, Path, timezone, ValidationError)
- 1 scope bug (tier_start pre-initialization in scorecard.py)
- 5 TYPE_CHECKING structural fixes (OracleResponse, AsyncCircuitBreaker,
  MetricsDB, SpeculativeDecodeConfig, ResearchProposal)
- Bonus: delete extractors.py file duplication (12 F811s eliminated)
- Bonus: deduplicate OmegaError import in discovery.py

Root Cause: Makefile --ignore=F821 blanket suppression hid real NameError
bugs; CI lint was non-blocking; no pre-commit hook existed.
Prevention Gate: F821 pre-commit hook + Makefile hard gate (Commit 2).

AP: AP-F821-EXECUTION-FINAL-v1.0.0
```

### COMMIT 2 — hardening (Phase 6)
- subject: ci: add F821 prevention gate and remove blanket suppression
- body:
```
- Remove --ignore=F821 from Makefile lint target
- Add omega-check-f821-undefined-names pre-commit hook
- Update FRONTIER_AI_CODING_STANDARDS.md with Section 8 Prevention Gates
- Update ci.yml lint step comment for traceability

Root Cause: Pipeline divergence — F821 suppressed locally, non-blocking in CI,
absent from pre-commit.
Prevention Gate: Three-layer enforcement (Makefile + pre-commit + CI comment).

AP: AP-F821-EXECUTION-FINAL-v1.0.0
```

## COMPLETION CRITERIA

- All 3 gates pass.
- grep -r "# <--" src/omega/ returns nothing.
- grep "ignore=F821" Makefile returns nothing.
- Both commits created with Root Cause and Prevention Gate markers.
- Task registered complete in TASK_REGISTRY (status: completed).

*AP-F821-EXECUTION-FINAL-v1.0.0*
