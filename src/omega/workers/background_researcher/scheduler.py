# 🔱 Omega Engine — Background Researcher Topic Scheduler
# AP: AP-JEM-SCHEDULER-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ scheduler ⬡ PHASE-2

import yaml
import os
from datetime import datetime, timezone
from typing import Optional
from .models import ResearchTask, RotationState

class TopicScheduler:
    """Manages the round-robin rotation and deepening of scheduled research topics.
    
    Ensures that the background researcher rotates through a set of high-priority
    strategic topics while allowing them to deepen over time.
    """
    
    def __init__(self, config_path: str = "config/research_topics.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.state = RotationState()
        
    def _load_config(self) -> dict:
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            # In a real worker, this would use the logger
            print(f"Error loading research topics config: {e}")
            return {}

    def get_next_topic(self) -> Optional[ResearchTask]:
        """Selects the next topic based on round-robin rotation and updates state.
        
        Returns:
            ResearchTask: The next scheduled task to be enqueued.
            None: If no topics are configured.
        """
        if not self.config or "scheduled_topics" not in self.config:
            return None
            
        rotation_cfg = self.config.get("rotation", {})
        cycle_order = rotation_cfg.get("cycle_order", [])
        topics_cfg = self.config["scheduled_topics"]
        
        if not cycle_order:
            return None
            
        # 1. Determine current topic key
        topic_key = cycle_order[self.state.current_topic_index]
        topic_data = topics_cfg.get(topic_key)
        
        if not topic_data:
            # Skip missing topic and move to next
            self._rotate()
            return self.get_next_topic()
            
        # 2. Calculate priority with aging and deepening
        # Scheduled topics start with high priority (0.9) to ensure they are processed
        base_priority = 0.9 
        aging_decay = rotation_cfg.get("aging_decay_per_cycle", 0.85)
        deepening_factor = rotation_cfg.get("deepening_factor", 1.15)
        priority_floor = rotation_cfg.get("priority_floor", 0.3)
        
        # Priority decays over cycles, but increases with deepening level
        # Formula: base * (decay ^ cycles) * (deepening ^ level)
        final_priority = base_priority * (aging_decay ** self.state.cycle_count) * (deepening_factor ** self.state.deepening_level)
        final_priority = max(final_priority, priority_floor)
        
        # 3. Create the task
        task = ResearchTask(
            topic=topic_data["title"],
            priority=final_priority,
            depth=topic_data.get("cloud_search", {}).get("depth", 2)
        )
        
        # 4. Update rotation state
        self.state.cycle_count += 1
        self.state.last_rotation = datetime.now(timezone.utc).isoformat()
        
        # Handle deepening: every 3rd cycle, increase deepening level to trigger deeper research
        if self.state.cycle_count % 3 == 0:
            self.state.deepening_level += 1
            
        self._rotate()
        
        return task

    def _rotate(self):
        """Advance the rotation index to the next topic in the cycle."""
        cycle_order = self.config.get("rotation", {}).get("cycle_order", [])
        if not cycle_order:
            return
            
        self.state.current_topic_index = (self.state.current_topic_index + 1) % len(cycle_order)
