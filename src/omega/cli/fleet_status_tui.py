# 🔱 Omega Engine — Fleet Status TUI
# AP: AP-FLEET-TUI-v1.0.0
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: OBSERVABILITY-TUI]
# Status: ACTIVE
# 
# This TUI provides a real-time view of the Sovereign Agent Fleet,
# monitoring agent presence, session activity, and resource pressure.
# 
"""
Sovereign Observatory TUI (fleet_status_tui.py)
High-density terminal dashboard for the Omega Engine.

Mandate 1: AnyIO Absolute (Reader handles thread offloading)
Mandate 8: Zero Telemetry
Mandate 2: Engine-Stack Firewall — WAD-loadable entity display (M2 Phase E)
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Tree, Static, DataTable
from textual.reactive import reactive

# Import the SovereignReader
from omega.observability.observability_reader import SovereignReader, TraceEvent

# M2 Phase E: WAD-loadable entity display — use dispatch_registry (FS-Β2 / A6-A7)
from omega.governance.dispatch_registry import load_dispatch_yaml, get_dispatch_entities, get_entity_by_role
from omega.ics import ROLE_CONSTANTS

# ─── UI Styling ───────────────────────────────────────────────────────────────

CSS = """
Screen {
    background: $surface;
}

#fleet-tree {
    width: 25%;
    height: 100%;
    border-right: solid $primary;
    padding: 1;
}

#right-pane {
    width: 75%;
    height: 100%;
}

.panel {
    border: round $accent;
    padding: 1;
    height: auto;
    background: $panel;
}

#global-vitals {
    height: 5;
    content-align: center middle;
    text-style: bold;
}

#entity-focus {
    height: 8;
}

#trace-feed {
    height: 1fr;
    border: round $secondary;
}
"""

# ─── Helper Functions ─────────────────────────────────────────────────────────

def generate_sparkline(values: List[float], width: int = 20) -> str:
    """Generates a Unicode sparkline from a list of floats."""
    if not values:
        return " " * width
    
    bars = " ▂▃▄▅▆▇█"
    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val if max_val > min_val else 1
    
    # Take the last `width` values
    recent_values = values[-width:]
    
    line = ""
    for v in recent_values:
        normalized = int(((v - min_val) / range_val) * 7)
        line += bars[normalized]
        
    return line.ljust(width, " ")


# ─── WAD-Loadable Fleet Tree Builder ──────────────────────────────────────────

def build_fleet_tree(iwad: str = DEFAULT_IWAD) -> Tree:
    """Build the fleet tree dynamically from WAD dispatch configuration.
    
    This replaces hardcoded entity names with runtime lookup from dispatch.yaml.
    M2 Firewall Phase E compliant.
    
    Args:
        iwad: The IWAD name to load entities from.
        
    Returns:
        A populated Textual Tree widget.
    """
    tree = Tree("Agent Fleet", id="fleet-tree")
    tree.root.expand()
    
    # Load entity definitions from WAD
    try:
        entities = get_dispatch_entities(iwad)
    except Exception:
        # Fallback to minimal structure if WAD config unavailable
        entities = []
    
    # Build lookup: role -> entity
    role_to_entity = {}
    for ent in entities:
        role = ent.get("role")
        if role:
            role_to_entity[role] = ent
    
    # Helper to get display name for a role
    def get_display_name(role: str) -> str:
        entity = role_to_entity.get(role)
        if entity:
            name = entity.get("name", role.lower())
            purpose = entity.get("purpose", "")
            # Extract short purpose for display
            short_purpose = purpose.split("—")[0].strip() if "—" in purpose else purpose
            return f"{name.title()} ({short_purpose})"
        return role.replace("_", " ").title()
    
    # Helper to get entity key for tree data
    def get_entity_key(role: str) -> str:
        entity = role_to_entity.get(role)
        return entity.get("name", role.lower()) if entity else role.lower()
    
    # ── Transcendent Triad ──────────────────────────────────────────────
    kali_role = ROLE_CONSTANTS["GRAND_OVERSIGHT"]
    maat_role = ROLE_CONSTANTS["LIGHT_OVERSOUL"]
    lilith_role = ROLE_CONSTANTS["DARK_OVERSOUL"]
    
    kali_node = tree.root.add(get_display_name(kali_role), data=get_entity_key(kali_role), expand=True)
    
    maat_node = kali_node.add(get_display_name(maat_role), data=get_entity_key(maat_role), expand=True)
    # P1-P5 under Light Oversoul (Build Side)
    for p in ["P1", "P2", "P3", "P4", "P5"]:
        p_role = ROLE_CONSTANTS[p]
        p_entity = role_to_entity.get(p_role)
        if p_entity:
            maat_node.add(f"P{p[-1]}: {p_entity.get('purpose', '').split('—')[0].strip()}", data=p_entity.get("name", p.lower()))
        else:
            maat_node.add(f"P{p[-1]}: {p_role}", data=p.lower())
    
    lilith_node = kali_node.add(get_display_name(lilith_role), data=get_entity_key(lilith_role), expand=True)
    # P6-P10 under Dark Oversoul (Run Side)
    for p in ["P6", "P7", "P8", "P9", "P10"]:
        p_role = ROLE_CONSTANTS[p]
        p_entity = role_to_entity.get(p_role)
        if p_entity:
            lilith_node.add(f"P{p[-1]}: {p_entity.get('purpose', '').split('—')[0].strip()}", data=p_entity.get("name", p.lower()))
        else:
            lilith_node.add(f"P{p[-1]}: {p_role}", data=p.lower())
    
    # ── Sovereign Specialists ───────────────────────────────────────────
    specialists = tree.root.add("Sovereign Specialists", data="specialists", expand=True)
    
    # Specialists are entities with P1 role that are not pillar slots
    # plus MAKALI_COUNCIL. Build dynamically from WAD config.
    specialist_entities = []
    for ent in entities:
        role = ent.get("role")
        name = ent.get("name")
        if not name:
            continue
        # Include P1 entities that are specialists (not pillar slots)
        # and MAKALI_COUNCIL
        if role == "P1" and ent.get("pillar_slot") is None:
            specialist_entities.append(ent)
        elif role == "MAKALI_COUNCIL":
            specialist_entities.append(ent)
    
    for entity in specialist_entities:
        name = entity.get("name", "")
        purpose = entity.get("purpose", "").split("—")[0].strip()
        specialists.add(f"{name.replace('_', ' ').title()} ({purpose})", data=name)
    
    # ── Core Infrastructure ─────────────────────────────────────────────
    # Messenger Bridge
    iris_role = ROLE_CONSTANTS["MESSENGER_BRIDGE"]
    tree.root.add(get_display_name(iris_role), data=get_entity_key(iris_role))
    
    # Sophia (Containing Field)
    sophia_role = ROLE_CONSTANTS["CONTAINING_FIELD"]
    tree.root.add(get_display_name(sophia_role), data=get_entity_key(sophia_role))
    
    return tree


# ─── Main Application ─────────────────────────────────────────────────────────

class FleetStatusApp(App):
    """Sovereign Observatory Terminal UI."""
    
    CSS = CSS
    TITLE = "🔱 Omega Engine — Sovereign Observatory"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Force Refresh"),
    ]

    # Reactive state
    selected_entity = reactive("system")

    def __init__(self):
        super().__init__()
        # Initialize the reader with standard paths
        data_dir = Path(os.environ.get("OMEGA_DATA_DIR", "data"))
        self.reader = SovereignReader(
            db_path=data_dir / "observability" / "metrics.db",
            trace_dir=data_dir / "traces",
            crash_dir=data_dir / "crashes"
        )
        # Build fleet tree from WAD config
        self.fleet_tree = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            # Tree will be built in on_mount
            yield Tree("Agent Fleet", id="fleet-tree")
            with Vertical(id="right-pane"):
                yield Static("Loading Vitals...", id="global-vitals", classes="panel")
                yield Static("Select an entity to view focus metrics.", id="entity-focus", classes="panel")
                yield DataTable(id="trace-feed")
        yield Footer()

    async def on_mount(self) -> None:
        """Setup the UI components on startup."""
        # 1. Build fleet tree from WAD config (M2 Phase E)
        tree = self.query_one("#fleet-tree", Tree)
        self.fleet_tree = build_fleet_tree()
        
        # Replace the placeholder tree with our WAD-built tree
        # We need to transfer the nodes
        tree.root.remove()
        for child in self.fleet_tree.root.children:
            tree.root.add_node(child)
        tree.root.expand()
        
        # 2. Setup DataTable
        table = self.query_one("#trace-feed", DataTable)
        table.add_columns("Time", "Level", "Entity", "Message", "Trace ID")
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        # 3. Start the refresh loop (every 2 seconds)
        self.set_interval(2.0, self.refresh_observability_data)
        
        # Initial fetch
        await self.refresh_observability_data()


    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle entity selection in the tree."""
        if event.node.data:
            self.selected_entity = event.node.data
            self.refresh_observability_data()

    async def refresh_observability_data(self) -> None:
        """Background worker to fetch data and update the UI."""
        try:
            # Diagnostic logging to find the hang
            with open("data/coordination/TUI_DEBUG.log", "a") as f:
                f.write(f"[{datetime.now(timezone.utc)}] Starting refresh...\n")
            
            health = await self.reader.get_fleet_health()
            with open("data/coordination/TUI_DEBUG.log", "a") as f:
                f.write(f"[{datetime.now(timezone.utc)}] Health fetched\n")
                
            traces = await self.reader.tail_live_traces(max_lines=30)
            with open("data/coordination/TUI_DEBUG.log", "a") as f:
                f.write(f"[{datetime.now(timezone.utc)}] Traces fetched\n")
                
            velocity = await self.reader.get_cognitive_velocity(self.selected_entity)
            with open("data/coordination/TUI_DEBUG.log", "a") as f:
                f.write(f"[{datetime.now(timezone.utc)}] Velocity fetched\n")
                
            cost = await self.reader.get_entity_cost(self.selected_entity)
            with open("data/coordination/TUI_DEBUG.log", "a") as f:
                f.write(f"[{datetime.now(timezone.utc)}] Cost fetched\n")
                
            sovereignty = await self.reader.get_sovereignty_ratio(self.selected_entity)
            with open("data/coordination/TUI_DEBUG.log", "a") as f:
                f.write(f"[{datetime.now(timezone.utc)}] Sovereignty fetched\n")
                
            somatic = await self.reader.get_somatic_pressure(self.selected_entity)
            with open("data/coordination/TUI_DEBUG.log", "a") as f:
                f.write(f"[{datetime.now(timezone.utc)}] Somatic fetched\n")
            
            # Update UI directly (we're on the event loop thread)
            self._update_ui(health, traces, velocity, cost, sovereignty, somatic)
        except Exception as e:
            with open("data/coordination/TUI_DEBUG.log", "a") as f:
                f.write(f"[{datetime.now(timezone.utc)}] ERROR: {str(e)}\n")
            self._show_error(str(e))

    def _update_ui(self, health, traces: List[TraceEvent], velocity, cost, sovereignty, somatic) -> None:
        """Updates the widgets with the fetched data."""
        # Update Global Vitals
        vitals_widget = self.query_one("#global-vitals", Static)
        error_pct = health.global_error_rate * 100
        status_color = "green" if error_pct < 5 else "yellow" if error_pct < 15 else "red"
        
        vitals_text = f"[{status_color}]● SYSTEM STATUS[/{status_color}] | "
        vitals_text += f"Global Error Rate: {error_pct:.1f}% | "
        vitals_text += f"Active Breakers: {len(health.breaker_states)}"
        vitals_widget.update(vitals_text)

        # Update Entity Focus
        focus_widget = self.query_one("#entity-focus", Static)
        
        accel_color = "red" if velocity.acceleration > 5.0 else "green"
        
        focus_text = f"[bold cyan]Entity Focus: {self.selected_entity.upper()}[/bold cyan]\n\n"
        focus_text += f"Cognitive Velocity: {velocity.tokens_per_second:.1f} tok/s\n"
        focus_text += f"Token Acceleration: [{accel_color}]{velocity.acceleration:+.2f} tok/s²[/{accel_color}]\n"
        focus_text += f"Session Cost: ${cost.cost_usd:.4f} ({cost.provider_name})\n"
        focus_text += f"Tokens (P/C): {cost.prompt_tokens} / {cost.completion_tokens}\n"
        focus_text += f"Sovereignty Ratio: {sovereignty:.2f} (local/cloud)\n"
        focus_text += f"Avg Latency: {somatic['avg_latency_ms']:.1f}ms | Max Latency: {somatic['max_latency_ms']:.1f}ms | Requests: {somatic['request_count']}"
        
        focus_widget.update(focus_text)

        # Update Trace Feed
        table = self.query_one("#trace-feed", DataTable)
        table.clear()
        
        # Filter traces by selected entity (or show all if 'system' or GRAND_OVERSIGHT selected)
        grand_oversight_key = ROLE_CONSTANTS["GRAND_OVERSIGHT"]
        grand_oversight_entity = get_entity_by_role(grand_oversight_key)
        grand_oversight_name = grand_oversight_entity.get("name") if grand_oversight_entity else None
        
        display_traces = traces
        if self.selected_entity not in ["system", grand_oversight_name]:
            display_traces = [t for t in traces if t.entity == self.selected_entity]
            
        for t in display_traces:
            # Colorize level
            level_fmt = t.level
            if t.level == "ERROR": level_fmt = f"[red]{t.level}[/red]"
            elif t.level == "WARN": level_fmt = f"[yellow]{t.level}[/yellow]"
            elif t.level == "INFO": level_fmt = f"[cyan]{t.level}[/cyan]"
            
            table.add_row(
                t.timestamp[-12:-4] if len(t.timestamp) > 12 else t.timestamp, # Just time
                level_fmt,
                t.entity,
                t.message[:80] + "..." if len(t.message) > 80 else t.message,
                t.trace_id[:8]
            )

    def _show_error(self, error_msg: str) -> None:
        """Displays errors in the vitals panel if the reader fails."""
        vitals_widget = self.query_one("#global-vitals", Static)
        vitals_widget.update(f"[bold red]OBSERVATORY ERROR:[/bold red] {error_msg}")

if __name__ == "__main__":
    app = FleetStatusApp()
    app.run()