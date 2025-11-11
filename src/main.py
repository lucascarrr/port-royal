# import argparse
from bitarray import bitarray

import sys
from pathlib import Path
from src.io import load_context
from src.algorithms import object_rank
from src.context import FormalContext
from src.implications import Implication


def main():
    # Define context
    ctx1 = load_context("../data/input.ctx", "ctx")
    delta = [
        Implication(["dem"], ["hci"], ctx1.attributes),
        Implication(["wpc"], ["hci"], ctx1.attributes),
    ]
    rtx1 = object_rank(ctx1, delta)
    print(rtx1)
    sys.exit(1)

    objects = ["con-18", "con-4", "con-1", "con-9", "con-17"]
    attributes = [
        "dem",
        "rep",
        "hci",
        "wpc",
        "abr",
        "pff",
        "esa",
        "rgs",
        "ast",
        "anc",
        "mxm",
        "imm",
        "scc",
        "edu",
        "rts",
        "crm",
        "dfe",
        "aas",
    ]

    incidence = [
        bitarray("101010001110001011"),
        bitarray("100110010000101001"),
        bitarray("010101110001011101"),
        bitarray("010101110000011101"),
        bitarray("101010010101110001"),
    ]

    ctx = FormalContext(objects, attributes, incidence)
    i1 = Implication(["imm"], ["crm"], ctx.attributes)
    i2 = Implication(["wpc"], ["scc"], ctx.attributes)
    delta = [i1, i2]
    print(f"Unranked Context:\n\n{ctx}\n")
    print(f"Object rank with delta ={delta}\n")
    print(object_rank(ctx, delta))

    # # Implications
    # i1 = Implication(["a", "c"], ["b"], ctx.attributes)
    # print(i1.sat_wit(bitarray("011")))
    # print(i1.sat_wit(bitarray("111")))
    # print(i1.sat_wit(bitarray("101")))
    # i2 = Implication(["b"], ["a"])
    # i3 = Implication(["a"], ["c"])
    # print(i1.sat_wit(bitarray("010"), ["a", "b", "c"]))

    # # Check per object
    # for o_idx, obj in enumerate(objects):
    #     print(f"{obj}:")
    #     print("  i1:", i1.satisfied(ctx.object_intent(o_idx), ctx.attributes))
    #     print("  i2:", i2.satisfied(ctx.object_intent(o_idx), ctx.attributes))
    #     print("  i3:", i3.satisfied(ctx.object_intent(o_idx), ctx.attributes))

    # # Check globally
    # print("\nGlobal satisfaction:")
    # print("i1:", ctx.satisfies(i1))
    # print("i2:", ctx.satisfies(i2))
    # print("i3:", ctx.satisfies(i3))


if __name__ == "__main__":
    main()
