"""
Scribe Hub Master — Broadcast Parser
Structured schema for Hivemind broadcasts consumed by the Scribe Hub Master loop.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Dict, Any
from datetime import datetime


class HubBroadcast(BaseModel):
    """Structured broadcast from agents via Hivemind."""
    agent: str
    timestamp: datetime
    intent: Literal["status", "decision", "blocker", "handoff_complete", "meta"]
    summary: str
    
    # High-Leverage / Carmack Mode Fields
    ticket_id: Optional[str] = Field(default=None, description="Associated Ark ticket (e.g., C-4b)")
    decision_id: Optional[str] = Field(default=None, description="Ratified decision ID (e.g., D-436)")
    blocker_severity: Optional[Literal["high", "medium", "low"]] = None
    leverage_ratio: Optional[str] = Field(default=None, description="Carmack mode leverage ratio assessment")
    carmack_mode: bool = Field(default=False, description="Flag indicating max leverage / min effort execution")
    handoff_packet_id: Optional[str] = Field(default=None, description="Associated handoff packet ID")
    
    # Extensible payload for agent-specific state
    data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_iso_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class HubUpdatePlan(BaseModel):
    """Plan for updating the Hub file."""
    agent_section_updates: Dict[str, str] = Field(default_factory=dict)
    decisions_log_entries: list = Field(default_factory=list)
    blockers_table_entries: list = Field(default_factory=list)
    sprint_status_updates: Dict[str, str] = Field(default_factory=dict)