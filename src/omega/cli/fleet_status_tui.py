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
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import os
from pathlib import Path
from datetime import datetime
from typing import List

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Tree, Static, DataTable
from textual.reactive import reactive

# Import the SovereignReader we just built
from omega.observability.observability_reader import SovereignReader, TraceEvent

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

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Tree("Agent Fleet", id="fleet-tree")
            with Vertical(id="right-pane"):
                yield Static("Loading Vitals...", id="global-vitals", classes="panel")
                yield Static("Select an entity to view focus metrics.", id="entity-focus", classes="panel")
                yield DataTable(id="trace-feed")
        yield Footer()

    def on_mount(self) -> None:
        """Setup the UI components on startup."""
        # 1. Setup Tree
        tree = self.query_one("#fleet-tree", Tree)
        tree.root.expand()
        
        # ── Transcendent Triad ──────────────────────────────────────────────
        kali = tree.root.add("Kali (Grand Oversight)", data="kali", expand=True)
        
        maat = kali.add("Ma'at (Light Oversoul)", data="maat", expand=True)
        maat.add("P1: SysAdmin", data="sysadmin")
        maat.add("P2: DataStore", data="datastore")
        maat.add("P3: BuildMaster", data="buildmaster")
        maat.add("P4: Bridge", data="bridge")
        maat.add("P5: Sentinel", data="sentinel")
        
        lilith = kali.add("Lilith (Dark Oversoul)", data="lilith", expand=True)
        lilith.add("P6: ModelGate", data="modelgate")
        lilith.add("P7: Context", data="context")
        lilith.add("P8: WatchTower", data="watchtower")
        lilith.add("P9: Link", data="link")
        lilith.add("P10: Verifier", data="verifier")
        
        # ── Sovereign Specialists ───────────────────────────────────────────
        specialists = tree.root.add("Sovereign Specialists", data="specialists", expand=True)
        specialists.add("Doom Guy (Heritage Aspect)", data="doom_guy")
        specialists.add("Roc Racoon (Legacy Aspect)", data="roc_racoon")
        specialists.add("Jem (Sovereign Synthesizer)", data="jem")
        specialists.add("Researcher (Master Researcher)", data="researcher")
        specialists.add("Makali (Parallel Council)", data="makali")
        specialists.add("John Carmack (S3 Consultant)", data="john_carmack")
        specialists.add("Verity (Unified Steward)", data="verity")
        
        # ── Core Infrastructure ─────────────────────────────────────────────
        tree.root.add("Iris (Voice Bridge)", data="iris")
        tree.root.add("Sophia (Akashic Record)", data="sophia")

        # 2. Setup DataTable
        table = self.query_one("#trace-feed", DataTable)
        table.add_columns("Time", "Level", "Entity", "Message", "Trace ID")
        table.cursor_type = "row"
        table.zebra_stripes = True

        # 3. Start the refresh loop (every 2 seconds)
        self.set_interval(2.0, self.refresh_observability_data)
        
        # Initial fetch
        self.refresh_observability_data()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle entity selection in the tree."""
        if event.node.data:
            self.selected_entity = event.node.data
            self.refresh_observability_data()

    async def refresh_observability_data(self) -> None:
        """Background worker to fetch data and update the UI."""
        try:
            # Fetch data using the SovereignReader (which offloads to threads internally)
            health = await self.reader.get_fleet_health()
            traces = await self.reader.tail_live_traces(max_lines=30)
            velocity = await self.reader.get_cognitive_velocity(self.selected_entity)
            cost = await self.reader.get_entity_cost(self.selected_entity)
            
            # Update UI directly (we're on the event loop thread)
            self._update_ui(health, traces, velocity, cost)
        except Exception as e:
            self._show_error(str(e))

    def _update_ui(self, health, traces: List[TraceEvent], velocity, cost) -> None:
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
        focus_text += f"Tokens (P/C): {cost.prompt_tokens} / {cost.completion_tokens}"
        
        focus_widget.update(focus_text)

        # Update Trace Feed
        table = self.query_one("#trace-feed", DataTable)
        table.clear()
        
        # Filter traces by selected entity (or show all if 'system' or 'kali' selected)
        display_traces = traces
        if self.selected_entity not in ["system", "kali"]:
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
