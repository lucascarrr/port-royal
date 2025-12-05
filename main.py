from src import (
    FormalContext,
    load_context,
    save_context,
    object_rank,
    Implication,
    Conditional,
    TranslatedContext,
)
from src.ranked_context import RankedContext
import os
import readline  # enables arrow key navigation in input


class PortRoyalREPL:
    def __init__(self):
        self.context: FormalContext | RankedContext | None = None
        self.ranked_context: RankedContext | None = None
        self.implications: list[Implication] = []
        self.running = True

    def list_contexts(self) -> list[str]:
        """List all available .ctx files in the data directory."""
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        if not os.path.exists(data_dir):
            return []
        return [f for f in os.listdir(data_dir) if f.endswith(".ctx")]

    def cmd_help(self, args: list[str]) -> None:
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

  save <filename>         Save current context to file
  clear                   Clear the screen
  reset                   Unload the current context
  quit / exit             Exit the REPL
"""
        )

    def cmd_list(self, args: list[str]) -> None:
        """List available context files."""
        contexts = self.list_contexts()
        if not contexts:
            print("No .ctx files found in data/")
        else:
            print("Available contexts:")
            for ctx in sorted(contexts):
                print(f"  {ctx}")

    def cmd_load(self, args: list[str]) -> None:
        """Load a context from file."""
        if not args:
            print("Usage: load <filename>")
            return

        filename = args[0]
        if not filename.endswith(".ctx"):
            filename += ".ctx"

        try:
            self.context = load_context(filename, "ctx")
            self.ranked_context = None
            self.implications = []
            print(f"Loaded context: {filename}")
            print(f"  Objects: {self.context.num_objects}")
            print(f"  Attributes: {self.context.num_attributes}")
        except FileNotFoundError:
            print(f"File not found: {filename}")
            print("Use 'list' to see available files.")
        except Exception as e:
            print(f"Error loading context: {e}")

    def cmd_show(self, args: list[str]) -> None:
        """Display the current context."""
        if self.ranked_context:
            print(self.ranked_context)
        elif self.context:
            print(self.context)
        else:
            print("No context loaded. Use 'load <filename>' first.")

    def cmd_info(self, args: list[str]) -> None:
        """Show context information."""
        ctx = self.ranked_context or self.context
        if not ctx:
            print("No context loaded.")
            return

        print(f"Objects ({ctx.num_objects}):")
        for obj in ctx.objects[:100]:
            print(f"  {obj}")
        # if ctx.num_objects > 20:
        #     print(f"  ... and {ctx.num_objects - 20} more")

        print(f"\nAttributes ({ctx.num_attributes}):")
        for attr in ctx.attributes[:100]:
            print(f"  {attr}")
        # if ctx.num_attributes > 20:
        #     print(f"  ... and {ctx.num_attributes - 20} more")

        if self.ranked_context:
            print(f"\nRanked context with {len(self.ranked_context.rankings)} ranks")
            for i, rank in enumerate(self.ranked_context.rankings):
                print(f"  Rank {i}: {rank.num_objects} objects")

    def cmd_intents(self, args: list[str]) -> None:
        """List all concept intents."""
        ctx = self.ranked_context or self.context
        if not ctx:
            print("No context loaded.")
            return

        intents = ctx.intents_list
        print(f"Found {len(intents)} concept intents:")
        for i, intent in enumerate(intents[:100]):
            print(f"  {i}: {set(intent) if intent else '{}'}")
        # if len(intents) > 30:
        #     print(f"  ... and {len(intents) - 30} more")

    def cmd_extents(self, args: list[str]) -> None:
        """List all concept extents."""
        ctx = self.ranked_context or self.context
        if not ctx:
            print("No context loaded.")
            return

        extents = ctx.extents_list
        print(f"Found {len(extents)} concept extents:")
        for i, extent in enumerate(extents[:100]):
            print(f"  {i}: {set(extent) if extent else '{}'}")
        # if len(extents) > 30:
        #     print(f"  ... and {len(extents) - 30} more")

    def cmd_closure(self, args: list[str]) -> None:
        """Compute closure of attributes."""
        ctx = self.ranked_context or self.context
        if not ctx:
            print("No context loaded.")
            return

        if not args:
            print("Usage: closure <attr1,attr2,...>")
            return

        attrs = [a.strip() for a in " ".join(args).split(",")]
        try:
            attr_bits = ctx._attributes_to_bitarray(frozenset(attrs))
            closure_bits = ctx.closure(attr_bits)
            closure = ctx._bitarray_to_attributes(closure_bits)
            print(f"Closure of {{{', '.join(attrs)}}}:")
            print(f"  {set(closure)}")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_extent(self, args: list[str]) -> None:
        """Get objects with given attributes."""
        ctx = self.ranked_context or self.context
        if not ctx:
            print("No context loaded.")
            return

        if not args:
            print("Usage: extent <attr1,attr2,...>")
            return

        attrs = [a.strip() for a in " ".join(args).split(",")]
        try:
            attr_bits = ctx._attributes_to_bitarray(frozenset(attrs))
            extent_bits = ctx.prime_attributes(attr_bits)
            extent = ctx._bitarray_to_objects(extent_bits)
            print(f"Objects with {{{', '.join(attrs)}}}:")
            print(f"  {set(extent)}")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_intent(self, args: list[str]) -> None:
        """Get attributes of given objects."""
        ctx = self.ranked_context or self.context
        if not ctx:
            print("No context loaded.")
            return

        if not args:
            print("Usage: intent <obj1,obj2,...>")
            return

        objs = [o.strip() for o in " ".join(args).split(",")]
        from bitarray import bitarray

        obj_bits = bitarray(ctx.num_objects)
        obj_bits.setall(0)

        try:
            for obj in objs:
                idx = ctx.objects.index(obj)
                obj_bits[idx] = 1
            intent_bits = ctx.prime_objects(obj_bits)
            intent = ctx._bitarray_to_attributes(intent_bits)
            print(f"Attributes of {{{', '.join(objs)}}}:")
            print(f"  {set(intent)}")
        except ValueError:
            print(f"Error: Object not found in context")

    def cmd_impl(self, args: list[str]) -> None:
        """Add an implication."""
        if not self.context:
            print("No context loaded.")
            return

        line = " ".join(args)
        if "->" not in line:
            print("Usage: impl <premise> -> <conclusion>")
            print("Example: impl road -> tarmac")
            return

        parts = line.split("->")
        premise = [a.strip() for a in parts[0].split(",") if a.strip()]
        conclusion = [a.strip() for a in parts[1].split(",") if a.strip()]

        try:
            impl = Implication(premise, conclusion, self.context.attributes)
            self.implications.append(impl)
            print(f"Added: {impl}")
        except Exception as e:
            print(f"Error: {e}")

    def cmd_impls(self, args: list[str]) -> None:
        """List current implications."""
        if not self.implications:
            print("No implications defined.")
            return

        print(f"Current implications ({len(self.implications)}):")
        for i, impl in enumerate(self.implications):
            print(f"  {i}: {impl}")

    def cmd_clear_impls(self, args: list[str]) -> None:
        """Clear all implications."""
        self.implications = []
        print("Implications cleared.")

    def cmd_rank(self, args: list[str]) -> None:
        """Create ranked context from implications."""
        if not self.context:
            print("No context loaded.")
            return

        if not self.implications:
            print("No implications defined. Use 'impl' to add some first.")
            return

        self.ranked_context = object_rank(self.context, self.implications)
        print(f"Created ranked context with {len(self.ranked_context.rankings)} ranks:")
        for i, rank in enumerate(self.ranked_context.rankings):
            print(f"  Rank {i}: {rank.num_objects} objects - {rank.objects}")

    def cmd_satisfies(self, args: list[str]) -> None:
        """Check if an implication is satisfied."""
        ctx = self.ranked_context or self.context
        if not ctx:
            print("No context loaded.")
            return

        line = " ".join(args)
        if "->" not in line:
            print("Usage: satisfies <premise> -> <conclusion>")
            return

        parts = line.split("->")
        premise = [a.strip() for a in parts[0].split(",") if a.strip()]
        conclusion = [a.strip() for a in parts[1].split(",") if a.strip()]

        try:
            impl = Implication(premise, conclusion, ctx.attributes)
            satisfied = ctx.satisfies(impl)
            print(f"{impl}: {'✓ satisfied' if satisfied else '✗ not satisfied'}")
        except Exception as e:
            print(f"Error: {e}")

    def cmd_cond(self, args: list[str]) -> None:
        """Check a conditional (ranked semantics)."""
        if not self.ranked_context:
            print("No ranked context. Use 'rank' first.")
            return

        line = " ".join(args)
        if "|~" not in line:
            print("Usage: cond <premise> |~ <conclusion>")
            return

        parts = line.split("|~")
        premise = [a.strip() for a in parts[0].split(",") if a.strip()]
        conclusion = [a.strip() for a in parts[1].split(",") if a.strip()]

        try:
            cond = Conditional(premise, conclusion, self.ranked_context.attributes)
            satisfied = self.ranked_context.satisfies(cond)
            print(f"{cond}: {'✓ satisfied' if satisfied else '✗ not satisfied'}")
        except Exception as e:
            print(f"Error: {e}")

    def cmd_basis(self, args: list[str]) -> None:
        """Compute canonical basis."""
        ctx = self.ranked_context or self.context
        if not ctx:
            print("No context loaded.")
            return

        basis = ctx.get_canonical_basis()
        if basis:
            print(f"Canonical basis ({len(basis)} implications):")
            for impl in basis[:40]:
                print(f"  {impl}")
            # if len(basis) > 20:
            #     print(f"  ... and {len(basis) - 20} more")
        else:
            print("No implications in canonical basis.")

    def cmd_defeasible_basis(self, args: list[str]) -> None:
        """Compute defeasible basis."""
        if not self.ranked_context:
            print("No ranked context. Use 'rank' first.")
            return

        basis = self.ranked_context.compute_defeasible_basis()
        print(f"Defeasible basis ({len(basis)} conditionals):")
        for cond in basis[:200]:
            print(f"  {cond}")
        # if len(basis) > 20:
        #     print(f"  ... and {len(basis) - 20} more")

    def cmd_save(self, args: list[str]) -> None:
        """Save current context to file."""
        ctx = self.ranked_context or self.context
        if not ctx:
            print("No context loaded.")
            return

        if not args:
            print("Usage: save <filename>")
            return

        filename = args[0]
        if not filename.endswith(".ctx"):
            filename += ".ctx"

        try:
            save_context(ctx, filename)
            print(f"Saved to data/{filename}")
        except Exception as e:
            print(f"Error saving: {e}")

    def cmd_clear(self, args: list[str]) -> None:
        """Clear the screen."""
        os.system("clear" if os.name != "nt" else "cls")

    def cmd_reset(self, args: list[str]) -> None:
        """Unload the current context."""
        self.context = None
        self.ranked_context = None
        self.implications = []
        print("Context unloaded.")

    def run(self) -> None:
        """Main REPL loop."""
        print("=" * 60)
        print("Port Royal - Formal Concept Analysis REPL")
        print("=" * 60)
        print("Type 'help' for commands, 'quit' to exit.\n")

        commands = {
            "help": self.cmd_help,
            "list": self.cmd_list,
            "load": self.cmd_load,
            "show": self.cmd_show,
            "info": self.cmd_info,
            "intents": self.cmd_intents,
            "extents": self.cmd_extents,
            "closure": self.cmd_closure,
            "extent": self.cmd_extent,
            "intent": self.cmd_intent,
            "impl": self.cmd_impl,
            "impls": self.cmd_impls,
            "clear-impls": self.cmd_clear_impls,
            "rank": self.cmd_rank,
            "satisfies": self.cmd_satisfies,
            "cond": self.cmd_cond,
            "basis": self.cmd_basis,
            "defeasible-basis": self.cmd_defeasible_basis,
            "save": self.cmd_save,
            "clear": self.cmd_clear,
            "reset": self.cmd_reset,
        }

        while self.running:
            try:
                prompt = "port-royal> "
                if self.ranked_context:
                    prompt = f"port-royal [{self.context.num_objects}obj, ranked]> "
                elif self.context:
                    prompt = f"port-royal [{self.context.num_objects}obj]> "

                line = input(prompt).strip()
                if not line:
                    continue

                parts = line.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break

                if cmd in commands:
                    commands[cmd](args)
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit.")
            except EOFError:
                print("\nGoodbye!")
                break


def main():
    repl = PortRoyalREPL()
    repl.run()


if __name__ == "__main__":
    main()
