from __future__ import annotations
from typing import TYPE_CHECKING

from bitarray import bitarray

if TYPE_CHECKING:
    from portroyal.cli import PortRoyalREPL


def cmd_intents(repl: PortRoyalREPL, args: list[str]) -> None:
    """List all concept intents."""
    ctx = repl.active_context
    if not ctx:
        print("No context loaded.")
        return

    intents: list[frozenset[str]] = ctx.intents
    print(f"Found {len(intents)} concept intents:")
    for i, intent in enumerate(intents[:100]):
        print(f"  {i}: {set(intent) if intent else '{}'}")


def cmd_extents(repl: PortRoyalREPL, args: list[str]) -> None:
    """List all concept extents."""
    ctx = repl.active_context
    if not ctx:
        print("No context loaded.")
        return

    extents: list[frozenset[str]] = ctx.extents
    print(f"Found {len(extents)} concept extents:")
    for i, extent in enumerate(extents[:100]):
        print(f"  {i}: {set(extent) if extent else '{}'}")


def cmd_closure(repl: PortRoyalREPL, args: list[str]) -> None:
    """Compute closure of attributes."""
    ctx = repl.active_context
    if not ctx:
        print("No context loaded.")
        return

    if not args:
        print("Usage: closure <attr1,attr2,...>")
        return

    attrs: list[str] = [a.strip() for a in " ".join(args).split(",")]
    try:
        attr_bits: bitarray = ctx._attributes_to_bitarray(frozenset(attrs))
        closure_bits: bitarray = ctx.closure(attr_bits)
        closure: frozenset[str] = ctx._bitarray_to_attributes(closure_bits)
        print(f"Closure of {{{', '.join(attrs)}}}:")
        print(f"  {set(closure)}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_extent(repl: PortRoyalREPL, args: list[str]) -> None:
    """Get objects with given attributes."""
    ctx = repl.active_context
    if not ctx:
        print("No context loaded.")
        return

    if not args:
        print("Usage: extent <attr1,attr2,...>")
        return

    attrs: list[str] = [a.strip() for a in " ".join(args).split(",")]
    try:
        attr_bits: bitarray = ctx._attributes_to_bitarray(frozenset(attrs))
        extent_bits: bitarray = ctx.prime_attributes(attr_bits)
        extent: frozenset[str] = ctx._bitarray_to_objects(extent_bits)
        print(f"Objects with {{{', '.join(attrs)}}}:")
        print(f"  {set(extent)}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_intent(repl: PortRoyalREPL, args: list[str]) -> None:
    """Get attributes of given objects."""
    ctx = repl.active_context
    if not ctx:
        print("No context loaded.")
        return

    if not args:
        print("Usage: intent <obj1,obj2,...>")
        return

    objs: list[str] = [o.strip() for o in " ".join(args).split(",")]

    obj_bits: bitarray = bitarray(ctx.num_objects)
    obj_bits.setall(0)

    try:
        for obj in objs:
            idx: int = ctx.objects.index(obj)
            obj_bits[idx] = 1
        intent_bits: bitarray = ctx.prime_objects(obj_bits)
        intent: frozenset[str] = ctx._bitarray_to_attributes(intent_bits)
        print(f"Attributes of {{{', '.join(objs)}}}:")
        print(f"  {set(intent)}")
    except ValueError:
        print("Error: Object not found in context")


def cmd_basis(repl: PortRoyalREPL, args: list[str]) -> None:
    """Compute canonical basis."""
    ctx = repl.active_context
    if not ctx:
        print("No context loaded.")
        return

    basis = ctx.get_canonical_basis()
    if basis:
        print(f"Canonical basis ({len(basis)} implications):")
        for impl in basis[:40]:
            print(f"  {impl}")
    else:
        print("No implications in canonical basis.")
