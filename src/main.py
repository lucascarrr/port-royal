from src.context import FormalContext
from bitarray import bitarray
from src.io import load_context
from src.algorithms import object_rank
from src.implications import Implication
from src.conditional import Conditional
from src.translated_ranked_context import TranslatedContext


def main():
    example_context = load_context("../data/example_sergei_talk.ctx", "ctx")
    print()
    print(example_context)
    print()
    delta = [
        Implication(["D"], ["a"], example_context.attributes),
        Implication(["w"], ["D"], example_context.attributes),
        Implication(["w", "p"], ["R"], example_context.attributes),
    ]
    ranked_context = object_rank(example_context, delta)
    print(ranked_context)
    print()
    print()
    print(ranked_context.compute_defeasible_basis())

    # translated_context = TranslatedContext(ranked_context)
    # print(translated_context)


if __name__ == "__main__":
    main()
