from bitarray import bitarray
import operator
from functools import reduce
from typing import override
from src.context import FormalContext
from src.ranked_context import RankedContext


class TranslatedContext(FormalContext[list[str]]):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and hasattr(args[0], "objects"):
            ranked_context: RankedContext = args[0]
            objects = ranked_context.objects
            attributes = ranked_context.intents_list
            incidence = self.make_incidence(ranked_context, attributes)
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
    ) -> list[bitarray]:
        base_context = ranked_context.rankings[0]
        incidence: list[bitarray] = []

        for obj_idx in range(base_context.num_objects):
            row = bitarray(len(attributes))
            row.setall(0)

            for attr_idx, attr_list in enumerate(attributes):
                has_all = all(
                    base_context.incidence[obj_idx][base_context.attributes.index(attr)]
                    for attr in attr_list
                )
                row[attr_idx] = has_all

            incidence.append(row)

        to_append = []
        for sub_context_indx in range(1, len(ranked_context.rankings)):
            sub_context = ranked_context.rankings[sub_context_indx]
            for obj_idx in range(sub_context.num_objects):
                row = bitarray(len(attributes))
                row.setall(0)

                for attr_idx, attr_list in enumerate(attributes):
                    has_all = all(
                        sub_context.incidence[obj_idx][
                            sub_context.attributes.index(attr)
                        ]
                        for attr in attr_list
                    )

                    row[attr_idx] = has_all

                row = reduce(operator.or_, incidence, row)
                to_append.append(row)

            for row in to_append:
                incidence.append(row)

        return incidence

    @override
    def __repr__(self) -> str:
        """Pretty-print the translated formal context with list attributes."""
        obj_width = max(len(o) for o in self.objects) if self.objects else 5
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
