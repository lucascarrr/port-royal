from src.context import FormalContext
from src.implications import Implication
from src.ranked_context import RankedContext


def object_rank(
    input_context: FormalContext, delta: list[Implication]
) -> RankedContext:
    unranked_objects = set(input_context.objects)
    obj_to_idx = {obj: idx for idx, obj in enumerate(input_context.objects)}

    ranks = []
    while unranked_objects:
        current_rank = FormalContext([], input_context.attributes, [])
        witnessed = set()
        to_remove = set()

        for g in unranked_objects:
            g_idx = obj_to_idx[g]
            g_intent = input_context.incidence[g_idx]
            # print(f"considering object: {g}")

            remove = True
            witnessed_by_this_object = set()
            for impl in delta:
                sat, wit = impl.sat_wit(g_intent)
                if not sat:
                    # print(f"Object {g} does not satisfy {impl}")
                    remove = False
                if wit:
                    # print(f"Object {g} witnesses {impl}")
                    witnessed_by_this_object.add(impl)

            if remove:
                current_rank.add_object(g, g_intent)
                # print(f"Object {g} added to rank: {len(ranks)}")
                to_remove.add(g)
                witnessed.update(witnessed_by_this_object)

        unranked_objects -= to_remove

        delta = [impl for impl in delta if impl not in witnessed]
        ranks.append(current_rank)

    return RankedContext(
        input_context.objects, input_context.attributes, input_context.incidence, ranks
    )
