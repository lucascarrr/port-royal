import os
from typing import Callable
import readline  # noqa: F401 - enables arrow key navigation in input

from portroyal.context import FormalContext
from portroyal.ranked_context import RankedContext
from portroyal.implication import Implication

from portroyal.cli.context_commands import (
    cmd_list, cmd_load, cmd_show, cmd_info, cmd_save, cmd_reset,
)
from portroyal.cli.fca_commands import (
    cmd_intents, cmd_extents, cmd_closure, cmd_extent, cmd_intent, cmd_basis,
)
from portroyal.cli.ranking_commands import (
    cmd_impl, cmd_impls, cmd_clear_impls, cmd_rank,
    cmd_satisfies, cmd_cond, cmd_defeasible_basis, cmd_rational_concepts,
)


class PortRoyalREPL:
    def __init__(self) -> None:
        self.context: FormalContext | RankedContext | None = None
        self.ranked_context: RankedContext | None = None
        self.implications: list[Implication] = []
        self.running: bool = True

    @property
    def active_context(self) -> FormalContext | RankedContext | None:
        """Return the ranked context if available, otherwise the plain context."""
        return self.ranked_context or self.context

    def run(self) -> None:
        """Main REPL loop."""
        print("=" * 60)
        print("Port Royal - Formal Concept Analysis REPL")
        print("=" * 60)
        print("Type 'help' for commands, 'quit' to exit.\n")

        commands: dict[str, Callable[[PortRoyalREPL, list[str]], None]] = {
            "help": cmd_help,
            "list": cmd_list,
            "load": cmd_load,
            "show": cmd_show,
            "info": cmd_info,
            "intents": cmd_intents,
            "extents": cmd_extents,
            "closure": cmd_closure,
            "extent": cmd_extent,
            "intent": cmd_intent,
            "impl": cmd_impl,
            "impls": cmd_impls,
            "clear-impls": cmd_clear_impls,
            "rank": cmd_rank,
            "satisfies": cmd_satisfies,
            "cond": cmd_cond,
            "basis": cmd_basis,
            "defeasible-basis": cmd_defeasible_basis,
            "rational-concepts": cmd_rational_concepts,
            "save": cmd_save,
            "clear": cmd_clear,
            "reset": cmd_reset,
        }

        while self.running:
            try:
                prompt: str = "port-royal> "
                if self.ranked_context:
                    prompt = f"port-royal [{self.ranked_context.num_objects}obj, ranked]> "
                elif self.context:
                    prompt = f"port-royal [{self.context.num_objects}obj]> "

                line: str = input(prompt).strip()
                if not line:
                    continue

                parts: list[str] = line.split()
                cmd: str = parts[0].lower()
                args: list[str] = parts[1:]

                if cmd in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break

                if cmd in commands:
                    commands[cmd](self, args)
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit.")
            except EOFError:
                print("\nGoodbye!")
                break


def cmd_help(repl: PortRoyalREPL, args: list[str]) -> None:
    """Display help information."""
    print(
        """
Port Royal REPL - Formal Concept Analysis with Preferential Semantics

Commands:
  help                    Show this help message
  list                    List available context files
  load <filename>         Load a context from data/<filename>
  show                    Display the current context
  info                    Show context statistics

  intents                 List all concept intents
  extents                 List all concept extents
  closure <attrs>         Compute closure of attributes (comma-separated)
  extent <attrs>          Get objects with attributes (comma-separated)
  intent <objects>        Get attributes of objects (comma-separated)

  impl <premise> -> <conclusion>   Add an implication
  impls                   List current implications
  clear-impls             Clear all implications
  rank                    Create ranked context from implications

  satisfies <premise> -> <conclusion>    Check if implication holds
  cond <premise> |~ <conclusion>         Check conditional (ranked context)

  basis                   Compute canonical basis (classical)
  defeasible-basis        Compute defeasible basis (ranked)
  rational-concepts       Enumerate all rational concepts (ranked)

  save <filename>         Save current context to file
  clear                   Clear the screen
  reset                   Unload the current context
  quit / exit             Exit the REPL
"""
    )


def cmd_clear(repl: PortRoyalREPL, args: list[str]) -> None:
    """Clear the screen."""
    os.system("clear" if os.name != "nt" else "cls")


def main() -> None:
    repl: PortRoyalREPL = PortRoyalREPL()
    repl.run()
