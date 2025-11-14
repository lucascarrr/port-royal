from src import (
    FormalContext,
    load_context,
    object_rank,
    Implication,
    Conditional,
    TranslatedContext,
)


def main():
    # Load the example context
    example_context = load_context("example_sergei_talk.ctx", "ctx")
    print("=" * 60)
    print("FORMAL CONTEXT")
    print("=" * 60)
    print(example_context)
    print()

    # Demonstrate frozenset-based concept intents/extents
    print("=" * 60)
    print("CONCEPT INTENTS (frozensets)")
    print("=" * 60)
    for i, intent in enumerate(example_context.intents_list):
        print(f"Concept {i}: {intent}")
    print()

    print("=" * 60)
    print("CONCEPT EXTENTS (frozensets)")
    print("=" * 60)
    for i, extent in enumerate(example_context.extents_list):
        print(f"Concept {i}: {extent}")
    print()

    # Create implications with frozenset premises/conclusions
    print("=" * 60)
    print("CLASSICAL IMPLICATIONS")
    print("=" * 60)
    implications = [
        Implication(["D"], ["a"], example_context.attributes),
        Implication(["w"], ["D"], example_context.attributes),
        Implication(["w", "p"], ["R"], example_context.attributes),
    ]
    for impl in implications:
        satisfied = example_context.satisfies(impl)
        print(f"{impl}: {'✓ satisfied' if satisfied else '✗ not satisfied'}")
    print()

    # Create a ranked context using object_rank
    print("=" * 60)
    print("RANKED CONTEXT (using implications as delta)")
    print("=" * 60)
    ranked_context = object_rank(example_context, implications)
    print(ranked_context)
    print()

    # Test classical implications on ranked context (should use super().satisfies())
    print("=" * 60)
    print("RANKED CONTEXT: Classical Implication Satisfaction")
    print("=" * 60)
    for impl in implications:
        satisfied = ranked_context.satisfies(impl)
        print(f"{impl}: {'✓ satisfied' if satisfied else '✗ not satisfied'}")
    print()

    # Create conditionals and test ranked satisfaction
    print("=" * 60)
    print("CONDITIONALS (ranked semantics)")
    print("=" * 60)
    conditionals = [
        Conditional(["w"], ["D"], ranked_context.attributes),
        Conditional(["w"], ["a"], ranked_context.attributes),
        Conditional(["p"], ["R"], ranked_context.attributes),
        Conditional(["D"], ["a"], ranked_context.attributes),
    ]
    for cond in conditionals:
        satisfied = ranked_context.satisfies(cond)
        print(f"{cond}: {'✓ satisfied' if satisfied else '✗ not satisfied'}")
    print()

    # Compute and display defeasible basis
    print("=" * 60)
    print("DEFEASIBLE BASIS (all valid conditionals)")
    print("=" * 60)
    basis = ranked_context.compute_defeasible_basis()
    print(f"Found {len(basis)} conditionals in defeasible basis:")
    for cond in basis[:10]:  # Show first 10 to avoid overwhelming output
        print(f"  {cond}")
    if len(basis) > 10:
        print(f"  ... and {len(basis) - 10} more")
    print()

    # # Uncomment to see translated context
    # translated_context = TranslatedContext(ranked_context)
    # print(translated_context)


if __name__ == "__main__":
    main()
