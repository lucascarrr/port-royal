from typing import override
import itertools
from bitarray import bitarray
from src.conditional import Conditional
from src.context import FormalContext
from src.implications import Implication


class RankedContext(FormalContext[str]):
    def __init__(
        self,
        objects: list[str],
        attributes: list[str],
        incidence: list[bitarray] | None = None,
        rankings: list[FormalContext] | None = None,
    ) -> None:
        super().__init__(objects, attributes, incidence)

        if rankings is None:
            self.rankings = [FormalContext(objects, attributes, incidence)]
        else:
            for ctx in rankings:
                if ctx.attributes != attributes:
                    raise ValueError(
                        "All rankings must share the same objects and attributes."
                    )
            self.rankings: list[FormalContext] = rankings

    @override
    def satisfies(
        self, implication: Implication
    ) -> bool:  # this should be conditional, but typechecker issue
        """returns true if the conditional is satisfied by the ranked context"""
        for rank in self.rankings:
            if not any(
                (object_intent & implication.premise_bits) == implication.premise_bits
                for object_intent in (
                    rank.object_intent(i) for i in range(rank.num_objects)
                )
            ):
                continue
            return rank.satisfies(implication)

        return False

    def compute_defeasible_basis(self) -> list[Conditional]:
        """
        returns a set of conditionals of the form {X'' -> Y'' | X'' subseteq Y''}
        Maybe this is sound & complete w.r.t. preferential entailment from self.

        """
        include = []
        candidates = (
            (prem, concl)
            for prem, concl in itertools.product(self.intents_list, self.intents_list)
            if prem != concl
        )

        pairs = [(set(x), set(y)) for x, y in candidates]

        valid_pairs = []
        for X, Y in pairs:
            if X.issubset(Y):
                valid_pairs.append((X, Y))

        for premise, conclusion in valid_pairs:
            query = Conditional(premise, conclusion, self.attributes)
            if self.satisfies(query):
                include.append(query)

        return include

    @override
    def __repr__(self) -> str:
        """Pretty-print the formal context as a cross table."""
        obj_width = max(len(o) for o in self.objects) if self.objects else 7
        attr_widths = [max(len(a), 1) for a in self.attributes]
        rank_width = 4

        if self.rankings:
            max_rank_num_width = len(str(len(self.rankings) - 1))
            rank_width = max(rank_width, max_rank_num_width)

        header = f"{'Rank':<{rank_width}} | {' ':<{obj_width}} |"
        for a, w in zip(self.attributes, attr_widths):
            header += f"{a:>{w + 2}}"

        lines = [header]
        lines.append("-" * len(header))

        for i in range(len(self.rankings)):
            rank = self.rankings[i]
            for o, row in zip(rank.objects, rank.incidence):
                line = f"{i:<{rank_width}} | {o:<{obj_width}} |"

                for bit, w in zip(row, attr_widths):
                    mark = "X" if bit else " "
                    line += f"{mark:>{w + 2}}"
                lines.append(line)

        return "\n".join(lines)
