from src.context import FormalContext
from bitarray import bitarray
from src.io import load_context
from src.algorithms import object_rank
from src.implications import Implication
from src.conditional import Conditional
from src.translated_ranked_context import TranslatedContext


def main():
    example_context = load_context("../data/input.ctx", "ctx")
    print(example_context)
    delta = [
        Implication(["a"], ["b"], example_context.attributes),
        Implication([], ["c"], example_context.attributes),
    ]
    ranked_context = object_rank(example_context, delta)
    print(ranked_context)
    translated_context = TranslatedContext(ranked_context)
    print(translated_context)


if __name__ == "__main__":
    main()
