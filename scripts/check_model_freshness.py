#!/usr/bin/env python3
"""
CLI wrapper for Freshness Checker.

Usage:
    python scripts/check_model_freshness.py --tier standard --notify
    python scripts/check_model_freshness.py --tier all --dry-run --json
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.omega.workers.freshness_checker import main

if __name__ == "__main__":
    sys.exit(main())