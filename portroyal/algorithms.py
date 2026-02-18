from bitarray import bitarray
from portroyal.context import FormalContext
from portroyal.implication import Implication
from portroyal.ranked_context import RankedContext


def object_rank(
    input_context: FormalContext, implications: list[Implication]
) -> RankedContext:
    unranked_objects: set[str] = set(input_context.objects)
    obj_to_idx: dict[str, int] = {obj: idx for idx, obj in enumerate(input_context.objects)}

    ranks: list[FormalContext] = []
    while unranked_objects:
        current_rank: FormalContext = FormalContext([], input_context.attributes, [])
        witnessed: set[Implication] = set()
        to_remove: set[str] = set()

        for obj_name in unranked_objects:
            obj_idx: int = obj_to_idx[obj_name]
            obj_intent: bitarray = input_context.incidence[obj_idx]

            remove: bool = True
            witnessed_by_this_object: set[Implication] = set()
            for impl in implications:
                sat: bool
                wit: bool
                sat, wit = impl.check(obj_intent)
                if not sat:
                    remove = False
                if wit:
                    witnessed_by_this_object.add(impl)

            if remove:
                current_rank.add_object(obj_name, obj_intent)
                to_remove.add(obj_name)
                witnessed.update(witnessed_by_this_object)

        unranked_objects -= to_remove
        implications = [impl for impl in implications if impl not in witnessed]
        ranks.append(current_rank)

    return RankedContext(
        input_context.objects, input_context.attributes, input_context.incidence, ranks
    )
