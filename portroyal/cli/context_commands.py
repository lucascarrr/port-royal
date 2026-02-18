from __future__ import annotations
from typing import TYPE_CHECKING

from portroyal.io import load_context, save_context, list_context_files

if TYPE_CHECKING:
    from portroyal.cli import PortRoyalREPL


def cmd_list(repl: PortRoyalREPL, args: list[str]) -> None:
    """List available context files."""
    contexts: list[str] = list_context_files()
    if not contexts:
        print("No context files found in data/")
    else:
        print("Available contexts:")
        for ctx in contexts:
            print(f"  {ctx}")


def cmd_load(repl: PortRoyalREPL, args: list[str]) -> None:
    """Load a context from file."""
    if not args:
        print("Usage: load <filename>")
        return

    filename: str = args[0]

    try:
        repl.context = load_context(filename)
        repl.ranked_context = None
        repl.implications = []
        print(f"Loaded context: {filename}")
        print(f"  Objects: {repl.context.num_objects}")
        print(f"  Attributes: {repl.context.num_attributes}")
    except FileNotFoundError:
        print(f"File not found: {filename}")
        print("Use 'list' to see available files.")
    except Exception as e:
        print(f"Error loading context: {e}")


def cmd_show(repl: PortRoyalREPL, args: list[str]) -> None:
    """Display the current context."""
    if repl.ranked_context:
        print(repl.ranked_context)
    elif repl.context:
        print(repl.context)
    else:
        print("No context loaded. Use 'load <filename>' first.")


def cmd_info(repl: PortRoyalREPL, args: list[str]) -> None:
    """Show context information."""
    ctx = repl.active_context
    if not ctx:
        print("No context loaded.")
        return

    print(f"Objects ({ctx.num_objects}):")
    for obj in ctx.objects[:100]:
        print(f"  {obj}")

    print(f"\nAttributes ({ctx.num_attributes}):")
    for attr in ctx.attributes[:100]:
        print(f"  {attr}")

    if repl.ranked_context:
        print(f"\nRanked context with {len(repl.ranked_context.rankings)} ranks")
        for i, rank in enumerate(repl.ranked_context.rankings):
            print(f"  Rank {i}: {rank.num_objects} objects")


def cmd_save(repl: PortRoyalREPL, args: list[str]) -> None:
    """Save current context to file."""
    ctx = repl.active_context
    if not ctx:
        print("No context loaded.")
        return

    if not args:
        print("Usage: save <filename>")
        return

    filename: str = args[0]

    try:
        save_context(ctx, filename)
        print(f"Saved to data/{filename}")
    except Exception as e:
        print(f"Error saving: {e}")


def cmd_reset(repl: PortRoyalREPL, args: list[str]) -> None:
    """Unload the current context."""
    repl.context = None
    repl.ranked_context = None
    repl.implications = []
    print("Context unloaded.")
