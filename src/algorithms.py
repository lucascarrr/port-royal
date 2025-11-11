from src.context import FormalContext
from src.implications import Implication
from src.ranked_context import RankedContext


def object_rank(
    input_context: FormalContext, delta: list[Implication]
) -> RankedContext:
    unranked_objects = input_context.objects.copy()
    ranks = []
    while unranked_objects != []:
        current_rank = FormalContext([], input_context.attributes, [])
        witnessed = []
        to_remove = []

        for g in unranked_objects:
            g_idx = input_context.objects.index(g)
            g_intent = input_context.incidence[g_idx]
            # print(f"considering object: {g}")

            remove = True
            witnessed_by_this_object = []
            for impl in delta:
                sat, wit = impl.sat_wit(g_intent)
                if not sat:
                    # print(f"Object {g} does not satisfy {impl}")
                    remove = False
                if wit:
                    # print(f"Object {g} witnesses {impl}")
                    witnessed_by_this_object.append(impl)

            if remove:
                current_rank.add_object(g, g_intent)
                # print(f"Object {g} added to rank: {len(ranks)}")
                to_remove.append(g)
                for impl in witnessed_by_this_object:
                    if impl not in witnessed:
                        witnessed.append(impl)

        for g in to_remove:
            unranked_objects.remove(g)

        delta = [impl for impl in delta if impl not in witnessed]
        ranks.append(current_rank)

    return RankedContext(
        input_context.objects, input_context.attributes, input_context.incidence, ranks
    )
