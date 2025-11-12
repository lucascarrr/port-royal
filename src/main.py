# import argparse

from src.io import load_context
from src.algorithms import object_rank
from src.implications import Implication
from src.conditional import Conditional


def main():
    # load a context from ctx file
    ctx = load_context("../data/input.ctx", "ctx")
    print(ctx)

    # there should be 8 concepts (i only care about intents right now)
    # {}, {dem,hci}, {rep,wpc}, {dem}, {wpc}, {dem,wpc}, {dem,wpc,hci}, {dem,wpc,hci,rep}
    print(ctx.intents_list)

    # object_rank algorithm
    # delta : objects are usually democrats & democrats are usually hci
    delta = [
        Implication([], ["hci"], ctx.attributes),
    ]
    rctx = object_rank(ctx, delta)
    print(rctx)

    # test defeasible entailment
    # c1: usually democrats are hci
    c1 = Conditional(["dem"], ["hci"], rctx.attributes)

    print(ctx.satisfies(c1))  # false
    print(rctx.satisfies(c1))  # true

    # TODO
    # defeasible


if __name__ == "__main__":
    main()
