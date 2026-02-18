from __future__ import annotations
from typing import TYPE_CHECKING

from portroyal.implication import Implication, Conditional
from portroyal.algorithms import object_rank

if TYPE_CHECKING:
    from portroyal.cli import PortRoyalREPL


def cmd_impl(repl: PortRoyalREPL, args: list[str]) -> None:
    """Add an implication."""
    if not repl.context:
        print("No context loaded.")
        return

    line: str = " ".join(args)
    if "->" not in line:
        print("Usage: impl <premise> -> <conclusion>")
        print("Example: impl road -> tarmac")
        return

    parts: list[str] = line.split("->")
    premise: list[str] = [a.strip() for a in parts[0].split(",") if a.strip()]
    conclusion: list[str] = [a.strip() for a in parts[1].split(",") if a.strip()]

    try:
        impl: Implication = Implication(premise, conclusion, repl.context.attributes)
        repl.implications.append(impl)
        print(f"Added: {impl}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_impls(repl: PortRoyalREPL, args: list[str]) -> None:
    """List current implications."""
    if not repl.implications:
        print("No implications defined.")
        return

    print(f"Current implications ({len(repl.implications)}):")
    for i, impl in enumerate(repl.implications):
        print(f"  {i}: {impl}")


def cmd_clear_impls(repl: PortRoyalREPL, args: list[str]) -> None:
    """Clear all implications."""
    repl.implications = []
    print("Implications cleared.")


def cmd_rank(repl: PortRoyalREPL, args: list[str]) -> None:
    """Create ranked context from implications."""
    if not repl.context:
        print("No context loaded.")
        return

    if not repl.implications:
        print("No implications defined. Use 'impl' to add some first.")
        return

    repl.ranked_context = object_rank(repl.context, repl.implications)
    print(f"Created ranked context with {len(repl.ranked_context.rankings)} ranks:")
    for i, rank in enumerate(repl.ranked_context.rankings):
        print(f"  Rank {i}: {rank.num_objects} objects - {rank.objects}")


def cmd_satisfies(repl: PortRoyalREPL, args: list[str]) -> None:
    """Check if an implication is satisfied."""
    ctx = repl.active_context
    if not ctx:
        print("No context loaded.")
        return

    line: str = " ".join(args)
    if "->" not in line:
        print("Usage: satisfies <premise> -> <conclusion>")
        return

    parts: list[str] = line.split("->")
    premise: list[str] = [a.strip() for a in parts[0].split(",") if a.strip()]
    conclusion: list[str] = [a.strip() for a in parts[1].split(",") if a.strip()]

    try:
        impl: Implication = Implication(premise, conclusion, ctx.attributes)
        satisfied: bool = ctx.satisfies(impl)
        print(f"{impl}: {'satisfied' if satisfied else 'not satisfied'}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_cond(repl: PortRoyalREPL, args: list[str]) -> None:
    """Check a conditional (ranked semantics)."""
    if not repl.ranked_context:
        print("No ranked context. Use 'rank' first.")
        return

    line: str = " ".join(args)
    if "|~" not in line:
        print("Usage: cond <premise> |~ <conclusion>")
        return

    parts: list[str] = line.split("|~")
    premise: list[str] = [a.strip() for a in parts[0].split(",") if a.strip()]
    conclusion: list[str] = [a.strip() for a in parts[1].split(",") if a.strip()]

    try:
        cond: Conditional = Conditional(premise, conclusion, repl.ranked_context.attributes)
        satisfied: bool = repl.ranked_context.satisfies(cond)
        print(f"{cond}: {'satisfied' if satisfied else 'not satisfied'}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_defeasible_basis(repl: PortRoyalREPL, args: list[str]) -> None:
    """Compute defeasible basis."""
    if not repl.ranked_context:
        print("No ranked context. Use 'rank' first.")
        return

    basis: list[Conditional] = repl.ranked_context.compute_defeasible_basis()
    print(f"Defeasible basis ({len(basis)} conditionals):")
    for cond in basis[:200]:
        print(f"  {cond}")


def cmd_rational_concepts(repl: PortRoyalREPL, args: list[str]) -> None:
    """Enumerate all rational concepts."""
    if not repl.ranked_context:
        print("No ranked context. Use 'rank' first.")
        return

    concepts: list[tuple[frozenset[str], frozenset[str]]] = repl.ranked_context.generate_all_rational_concepts()
    print(f"Found {len(concepts)} rational concepts:")
    for i, (extent, intent) in enumerate(concepts):
        print(f"  {i}: ({set(extent) if extent else '{}'}, {set(intent) if intent else '{}'})")
