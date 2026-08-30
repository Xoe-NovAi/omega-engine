# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Sovereign Soul Staging Gate TUI.
AP: AP-SOUL-STAGE-v1.0.0

Allows the user to review, approve, or reject proposed L3 principles
before they are committed to an entity's soul.yaml.
"""
# DocRef: docs/architecture/SOUL_ARCHITECTURE_PROTOCOL.md

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Button, Label
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding

from omega.oracle.entity_registry import EntityRegistry
from omega.state import get_usm


class SoulStageApp(App):
    """TUI for staging soul distillation proposals."""

    CSS = """
    Screen {
        align: center middle;
    }
    #main_container {
        width: 90%;
        height: 90%;
        border: solid green;
        padding: 1;
    }
    .proposal_detail {
        border: double white;
        padding: 1;
        margin: 1;
        height: auto;
    }
    .action_bar {
        height: 3;
        align: center middle;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "approve", "Approve"),
        Binding("r", "reject", "Reject"),
        Binding("d", "defer", "Defer"),
    ]

    def __init__(self, entity_name: str):
        super().__init__()
        self.entity_name = entity_name
        self.registry = EntityRegistry()
        self.usm = get_usm()
        self.current_proposal = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main_container"):
            yield Label(f"Sovereign Soul Staging: {self.entity_name}")
            yield DataTable(id="proposal_table")
            with Vertical(classes="proposal_detail", id="detail_view"):
                yield Label("Select a proposal to review...")
            with Horizontal(classes="action_bar"):
                yield Button("Approve", id="btn_approve", variant="success")
                yield Button("Reject", id="btn_reject", variant="error")
                yield Button("Defer", id="btn_defer", variant="warning")
        yield Footer()

    async def on_mount(self) -> None:
        await self.load_proposals()

    async def load_proposals(self) -> None:
        """Load proposed lessons from proposed_lessons.yaml."""
        table = self.query_one("#proposal_table", DataTable)
        table.clear()
        table.add_columns("ID", "L1 Narrative", "L2 Insight", "L3 Principle")

        # In a real implementation, this reads from proposed_lessons.yaml
        # For now, we mock some data to verify the TUI
        mock_proposals = [
            {
                "id": "prop_001",
                "L1": "Observed that local inference is 10x faster for 1.7B models.",
                "L2": "Small models are sufficient for routing tasks.",
                "L3": "The Right Approximation: Use the smallest model that meets the precision requirement.",
            },
            {
                "id": "prop_002",
                "L1": "SomaticState capture caused a segfault in llama-cpp.",
                "L2": "C-FFI calls are unstable in the main thread.",
                "L3": "Sovereign Isolation: Wrap all C-FFI in isolated processes.",
            },
        ]

        for p in mock_proposals:
            table.add_row(p["id"], p["L1"][:50] + "...", p["L2"][:50] + "...", p["L3"][:50] + "...")

        self.proposals = mock_proposals

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        proposal = self.proposals[event.cursor_row]
        self.current_proposal = proposal
        detail = self.query_one("#detail_view", Vertical)
        detail.children.clear()
        detail.mount(Label(f"ID: {proposal['id']}"))
        detail.mount(Label(f"\n[L1 Narrative]\n{proposal['L1']}"))
        detail.mount(Label(f"\n[L2 Insight]\n{proposal['L2']}"))
        detail.mount(Label(f"\n[L3 Principle]\n{proposal['L3']}"))

    async def action_approve(self) -> None:
        if self.current_proposal:
            # Logic to move from proposed_lessons.yaml to soul.yaml
            self.notify(f"Approved {self.current_proposal['id']}")
            # Implementation: update soul.yaml

    async def action_reject(self) -> None:
        if self.current_proposal:
            self.notify(f"Rejected {self.current_proposal['id']}")

    async def action_defer(self) -> None:
        if self.current_proposal:
            self.notify(f"Deferred {self.current_proposal['id']}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_approve":
            await self.action_approve()
        elif event.button.id == "btn_reject":
            await self.action_reject()
        elif event.button.id == "btn_defer":
            await self.action_defer()


if __name__ == "__main__":
    # Example usage
    app = SoulStageApp(entity_name="sophia")
    app.run()
