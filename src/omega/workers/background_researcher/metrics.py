# 🔱 Omega Engine — Background Researcher Metrics
# AP: AP-JEM-METRICS-v1.0.0
# ⬡ OMEGA ⬡ MAAT ⬡ metrics ⬡ PHASE-2

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any
from pathlib import Path

class ResearchMetrics:
    """Logs per-cycle performance and quality metrics for the 3-tier pipeline.
    
    Outputs to JSONL files for later analysis and synthetic dataset auditing.
    """
    
    def __init__(self, log_dir: str = "data/research/metrics"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "cycle_metrics.jsonl"

    def log_cycle(self, topic: str, metrics: Dict[str, Any]):
        """Log a complete cycle's metrics.
        
        Expected metrics schema:
        {
            "t1_latency": float,
            "t1_tokens": int,
            "t1_quality": float,
            "t2_latency": float,
            "t2_tokens": int,
            "t2_quality": float,
            "t3_latency": float,
            "t3_tokens": int,
            "t3_quality": float,
            "circuit_states": {"t1": str, "t2": str, "t3": str},
            "training_triple_saved": bool
        }
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topic": topic,
            **metrics
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    def get_summary(self) -> Dict[str, Any]:
        """Calculate aggregate performance metrics from the log file."""
        if not self.log_file.exists():
            return {"status": "no logs found"}
            
        cycles = []
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    cycles.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
                    
        if not cycles:
            return {"status": "empty logs"}
            
        return {
            "total_cycles": len(cycles),
            "avg_t1_latency": sum(c.get("t1_latency", 0) for c in cycles) / len(cycles),
            "avg_t2_latency": sum(c.get("t2_latency", 0) for c in cycles) / len(cycles),
            "avg_t3_latency": sum(c.get("t3_latency", 0) for c in cycles) / len(cycles),
            "success_rate": sum(1 for c in cycles if c.get("t3_quality", 0) > 0.7) / len(cycles)
        }
