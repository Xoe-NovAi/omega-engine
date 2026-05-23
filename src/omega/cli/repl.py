# 🔱 Omega REPL — Interactive Chat Loop
# AP: AP-OMEGA-REPL-v1.0.0
#
# Interactive chat interface to the Oracle.
# Uses prompt_toolkit 3.x with AnyIO (shared asyncio backend).
# Screen-reader accessible: no full-screen mode, Emacs key bindings.

import logging
from pathlib import Path
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from omega.oracle.oracle import Oracle, OracleResponse
from omega.oracle.entity_registry import EntityRegistry

logger = logging.getLogger(__name__)

# REPL state file for persistent settings across sessions
REPL_STATE_DIR = Path.home() / ".omega"
REPL_STATE_FILE = REPL_STATE_DIR / "repl_state.yaml"
REPL_HISTORY_FILE = REPL_STATE_DIR / "repl_history"

SLASH_COMMANDS = [
    "/entity", "/transient", "/header", "/help", "/status",
    "/entities", "/exit", "/quit",
]


class OmegaCompleter(Completer):
    """Tab-completes slash commands and entity names."""

    def __init__(self, entity_names: list[str]):
        self._entity_names = entity_names

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()

        # Slash commands
        if text.startswith("/"):
            for cmd in SLASH_COMMANDS:
                if cmd.startswith(text):
                    yield Completion(cmd, start_position=-len(text))

        # Entity names after /entity
        if text.startswith("/entity "):
            prefix = text[len("/entity "):]
            for name in self._entity_names:
                if name.lower().startswith(prefix.lower()):
                    yield Completion(name, start_position=-len(prefix))


class OmegaREPL:
    """Interactive chat loop for the Omega Engine."""

    def __init__(self):
        self.oracle: Optional[Oracle] = None
        self.transient = False
        self.current_entity = "SOPHIA"
        self.header_mode = "compact"
        self._running = True

        # Ensure state directory exists
        REPL_STATE_DIR.mkdir(parents=True, exist_ok=True)

        # Load persisted state
        self._load_state()

        # Build entity list for completion
        registry = EntityRegistry()
        entity_names = [e.name for e in registry.list() if not e.container]

        # Style (minimal, screen-reader friendly)
        style = Style.from_dict({
            "prompt": "ansicyan bold",
            "input": "",
        })

        self.session = PromptSession(
            history=FileHistory(str(REPL_HISTORY_FILE)),
            completer=OmegaCompleter(entity_names),
            complete_while_typing=True,
            style=style,
            mouse_support=False,
        )

    def _load_state(self):
        """Load REPL state from disk."""
        import yaml
        if REPL_STATE_FILE.exists():
            try:
                with open(REPL_STATE_FILE) as f:
                    state = yaml.safe_load(f) or {}
                self.transient = state.get("transient", False)
                self.current_entity = state.get("current_entity", "SOPHIA")
                self.header_mode = state.get("header_mode", "compact")
            except Exception:
                pass  # Use defaults

    def _save_state(self):
        """Persist REPL state to disk."""
        import yaml
        state = {
            "transient": self.transient,
            "current_entity": self.current_entity,
            "header_mode": self.header_mode,
        }
        try:
            with open(REPL_STATE_FILE, "w") as f:
                yaml.dump(state, f, default_flow_style=False)
        except Exception as e:
            logger.warning(f"Failed to save REPL state: {e}")

    async def run(self):
        """Main REPL loop."""
        self.oracle = Oracle()
        await self.oracle.bootstrap()

        self._print_banner()

        while self._running:
            try:
                # Use anyio.to_thread.run_sync for prompt_toolkit (asyncio-based)
                # Since AnyIO defaults to asyncio backend, this runs on the same loop
                query = await self._get_input()

                if not query:
                    continue

                query = query.strip()

                # Handle slash commands
                if query.startswith("/"):
                    await self._handle_command(query)
                    continue

                # Route to Oracle
                await self._send_query(query)

            except EOFError:
                # Ctrl+D — graceful exit
                self._running = False
            except KeyboardInterrupt:
                # Ctrl+C — cancel current input
                continue
            except Exception as e:
                print(f"\n[error] Error: {e}")
                logger.error(f"REPL error: {e}", exc_info=True)

        self._save_state()
        print("\n🔱 The Oracle rests. Until next time, Architect.")

    async def _get_input(self) -> str:
        """Get input from user via prompt_toolkit."""

        # prompt_toolkit uses asyncio internally. Since AnyIO's default backend
        # is asyncio, they share the same event loop. We can call prompt_async
        # directly within an anyio.run() context.
        entity_label = self.current_entity.upper()
        mode_tag = " [transient]" if self.transient else ""
        prompt_text = f"⬡ {entity_label}{mode_tag} > "

        # Run prompt_toolkit on the current event loop
        # prompt_toolkit's prompt_async is asyncio-native, compatible with
        # AnyIO's asyncio backend
        return await self.session.prompt_async(prompt_text)

    async def _send_query(self, query: str):
        """Send query to Oracle and display response."""
        if not self.oracle:
            return

        # If current_entity is set, use summon; otherwise use talk
        if self.current_entity and self.current_entity != "SOPHIA":
            result = await self.oracle.summon(
                self.current_entity, query, transient=self.transient
            )
        else:
            result = await self.oracle.talk(query, transient=self.transient)

        self._display_response(result)

    def _display_response(self, result: OracleResponse):
        """Format and display response."""
        # Header
        if self.header_mode == "full":
            trace = result.trace_id[:8] if result.trace_id else "unknown"
            header = (
                f"⬡ OMEGA ⬡ {result.entity.upper()} ⬡ "
                f"{result.model or 'unknown'} ⬡ repl ⬡ {trace} ⬡ {result.phase}"
            )
            print(f"\n[dim]{header}[/dim]")
        elif self.header_mode == "compact":
            header = f"⬡ {result.entity.upper()} ⬡ {result.phase}"
            print(f"\n[dim]{header}[/dim]")

        # Entity prefix
        prefix = result.entity
        if result.pillars:
            prefix += f" ({', '.join(result.pillars)})"
        if result.sigil:
            prefix += f" {result.sigil}"

        print(f"\n{prefix}")
        print(f"{result.text}\n")

    async def _handle_command(self, command: str):
        """Handle slash commands."""
        parts = command.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else None

        if cmd in ("/exit", "/quit"):
            self._running = False

        elif cmd == "/help":
            self._print_help()

        elif cmd == "/entity":
            if arg:
                registry = EntityRegistry()
                entity = registry.get(arg)
                if entity:
                    self.current_entity = arg
                    print(f"[green]✓ Entity set to: {arg}[/green]")
                else:
                    # Try case-insensitive match
                    for e in registry.list():
                        if e.name.lower() == arg.lower():
                            self.current_entity = e.name
                            print(f"[green]✓ Entity set to: {e.name}[/green]")
                            return
                    print(f"[red]✗ Entity '{arg}' not found.[/red]")
            else:
                print(f"Current entity: [bold]{self.current_entity}[/bold]")

        elif cmd == "/transient":
            if arg and arg.lower() in ("on", "off"):
                self.transient = arg.lower() == "on"
            else:
                self.transient = not self.transient
            status = "ON" if self.transient else "OFF"
            print(f"[green]✓ Transient mode: {status}[/green]")
            self._save_state()

        elif cmd == "/header":
            if arg and arg.lower() in ("full", "compact", "off"):
                self.header_mode = arg.lower()
                print(f"[green]✓ Header mode: {arg.lower()}[/green]")
            else:
                print(f"Header mode: [bold]{self.header_mode}[/bold] (full/compact/off)")
            self._save_state()

        elif cmd == "/status":
            await self._print_status()

        elif cmd == "/entities":
            self._print_entities()

        else:
            print(f"[red]Unknown command: {cmd}[/red]")
            print("Type /help for available commands.")

    async def _print_status(self):
        """Print current session status."""
        if not self.oracle:
            return

        print(f"\n{'=' * 50}")
        print("  Omega REPL Status")
        print(f"{'=' * 50}")
        print(f"  Entity:        {self.current_entity}")
        print(f"  Transient:     {'ON' if self.transient else 'OFF'}")
        print(f"  Header:        {self.header_mode}")
        print(f"  Default:       {self.oracle.default_entity.name if self.oracle.default_entity else 'None'}")

        # WADs
        wads = []
        try:
            for name, success in self.oracle.wad_loader.load_all_wads():
                if success:
                    wads.append(name)
        except Exception:
            pass
        print(f"  Active WADs:   {', '.join(wads) if wads else 'None'}")
        print(f"{'=' * 50}\n")

    def _print_entities(self):
        """Print available entities."""
        registry = EntityRegistry()
        print(f"\n{'=' * 50}")
        print("  Available Entities")
        print(f"{'=' * 50}")
        for entity in registry.list():
            if entity.container:
                continue
            pillars = ", ".join(entity.pillars) if entity.pillars else "—"
            marker = " ← current" if entity.name == self.current_entity else ""
            print(f"  {entity.name:20s} {pillars}{marker}")
        print(f"{'=' * 50}\n")

    def _print_help(self):
        """Print help message."""
        print(f"""
{'=' * 50}
  Omega REPL — Commands
{'=' * 50}
  /entity <name>    Switch to entity (e.g., /entity sophia)
  /transient        Toggle transient mode (no soul updates)
  /header <mode>    Set header: full, compact, or off
  /status           Show session status
  /entities         List all available entities
  /help             Show this help
  /exit or /quit    Exit the REPL
  Ctrl+D            Exit the REPL
  Ctrl+C            Cancel current input

  Type any message to talk to the Oracle.
{'=' * 50}
""")

    def _print_banner(self):
        """Print startup banner."""
        print(f"""
🔱 Omega Engine — Interactive REPL
{'=' * 50}
  Entity:  {self.current_entity}
  Type /help for commands, /exit to quit.
{'=' * 50}
""")
