from bitarray import bitarray
from typing import override
from src.context import FormalContext
from src.ranked_context import RankedContext


class TranslatedContext(FormalContext):
    def __init__(self, *args, **kwargs) -> None:
        if len(args) == 1 and hasattr(args[0], "objects"):
            ranked_context: RankedContext = args[0]
            # Use concept intents from the underlying context (rank 0)
            attributes = ranked_context.rankings[0].intents_list
            incidence, objects = self.make_incidence(ranked_context, attributes)
            super().__init__(objects, attributes, incidence)
        elif len(args) == 3:
            objects, attributes, incidence = args
            super().__init__(objects, attributes, incidence)
        else:
            raise TypeError(
                "TranslatedContext() expects either a RankedContext "
                "or (objects, attributes, incidence)"
            )

    def make_incidence(
        self, ranked_context: RankedContext, attributes: list[list[str]]
    ) -> tuple[list[bitarray], list[str]]:
        incidence: list[bitarray] = []
        new_objects: list[str] = []

        # Track which attributes are satisfied by ANY object in lower ranks (cumulative)
        # This represents the attributes that are "true in better/more normal worlds"
        cumulative_satisfies = bitarray(len(attributes))
        cumulative_satisfies.setall(0)

        # Process each rank in order (0, 1, 2, ...)
        for rank_idx, context in enumerate(ranked_context.rankings):
            # Track what THIS rank satisfies (before inheritance)
            current_rank_satisfies = bitarray(len(attributes))
            current_rank_satisfies.setall(0)

            for obj_idx in range(context.num_objects):
                obj_name = context.objects[obj_idx]
                row = bitarray(len(attributes))
                row.setall(0)

                # Check if this object at this rank satisfies each attribute
                for attr_idx, attr_list in enumerate(attributes):
                    has_all = all(
                        context.incidence[obj_idx][context.attributes.index(attr)]
                        for attr in attr_list
                    )
                    if has_all:
                        row[attr_idx] = 1
                        current_rank_satisfies[attr_idx] = 1

                # Inherit from ANY object in lower ranks (0..rank_idx-1)
                # If any object in a better world satisfies an attribute, all objects in
                # worse worlds inherit it
                row |= cumulative_satisfies

                incidence.append(row)
                new_objects.append(obj_name)

            # Update cumulative: add what this rank satisfies
            cumulative_satisfies |= current_rank_satisfies

        return incidence, new_objects

    @override
    def __repr__(self) -> str:
        """Pretty-print the translated formal context with list attributes."""
        obj_width: int = max(len(o) for o in self.objects) if self.objects else 5
        # Convert list attributes to strings for display
        attr_strs = [str(a) for a in self.attributes]
        attr_widths = [max(len(s), 1) for s in attr_strs]

        header = " " * (obj_width + 2)
        for s, w in zip(attr_strs, attr_widths):
            header += f"{s:^{w + 2}}"

        lines = [header]
        lines.append("-" * len(header))

        if not self.objects:
            lines.append("[No objects in context]")
            return "\n".join(lines)

        for o, row in zip(self.objects, self.incidence):
            line = f"{o:<{obj_width}} |"
            for bit, w in zip(row, attr_widths):
                mark = "X" if bit else " "
                line += f"{mark:^{w + 2}}"
            lines.append(line)

        return "\n".join(lines)
