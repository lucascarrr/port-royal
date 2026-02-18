from typing import override
from collections import defaultdict
import itertools
from bitarray import bitarray
from portroyal.implication import Conditional, Implication
from portroyal.context import FormalContext


class RankedContext(FormalContext):
    def __init__(
        self,
        objects: list[str],
        attributes: list[str],
        incidence: list[bitarray] | None = None,
        rankings: list[FormalContext] | None = None,
    ) -> None:
        super().__init__(objects, attributes, incidence)

        if rankings is None:
            self.rankings: list[FormalContext] = [FormalContext(objects, attributes, incidence)]
        else:
            for ctx in rankings:
                if ctx.attributes != attributes:
                    raise ValueError(
                        "All rankings must share the same objects and attributes."
                    )
            self.rankings = rankings

    @override
    def satisfies(self, implication: Implication) -> bool:
        """Dispatches based on implication type:
        - If Conditional: uses ranked context semantics
        - If Implication: delegates to classical context semantics
        """
        if isinstance(implication, Conditional):
            for rank in self.rankings:
                if not any(
                    (object_intent & implication.premise_bits)
                    == implication.premise_bits
                    for object_intent in (
                        rank.object_intent(i) for i in range(rank.num_objects)
                    )
                ):
                    continue
                return rank.satisfies(implication)
            return False
        else:
            return super().satisfies(implication)

    def compute_defeasible_basis_helper(self) -> dict[frozenset[str], frozenset[str]]:
        include: defaultdict[frozenset[str], frozenset[str]] = defaultdict(frozenset)
        for premise, conclusion in itertools.combinations(self.intents, 2):
            if premise < conclusion:
                query: Conditional = Conditional(premise, conclusion.union(premise), self.attributes)
                if self.satisfies(query):
                    include[premise] = include[premise].union(conclusion)
            elif conclusion < premise:
                query = Conditional(conclusion, premise, self.attributes)
                if self.satisfies(query):
                    include[premise] = include[premise].union(conclusion)

        return dict(include)

    def compute_defeasible_basis(self) -> list[Conditional]:
        basis: list[Conditional] = []
        store: dict[frozenset[str], frozenset[str]] = self.compute_defeasible_basis_helper()
        for premise, conclusion in store.items():
            basis.append(Conditional(premise, conclusion, self.attributes))
        return basis

    def minimise(self, objects: bitarray) -> bitarray:
        """Return only the lowest-ranked objects from the given object set."""
        object_names: frozenset[str] = self._bitarray_to_objects(objects)

        for rank in self.rankings:
            rank_objects: set[str] = set(rank.objects)
            min_objects: frozenset[str] = object_names & rank_objects
            if min_objects:
                result: bitarray = bitarray(self.num_objects)
                result.setall(0)
                for obj_name in min_objects:
                    idx: int = self.objects.index(obj_name)
                    result[idx] = 1
                return result

        result = bitarray(self.num_objects)
        result.setall(0)
        return result

    def rational_concept(self, attributes: bitarray) -> tuple[bitarray, bitarray]:
        """Compute the rational concept of an attribute set X.

        Returns (extent, intent) where extent and intent use the minimise operator.
        """
        x_prime: bitarray = self.prime_attributes(attributes)
        min_x_prime: bitarray = self.minimise(x_prime)
        intent: bitarray = self.prime_objects(min_x_prime)
        extent: bitarray = self.prime_attributes(intent)
        return (extent, intent)

    def generate_all_rational_concepts(
        self,
    ) -> list[tuple[frozenset[str], frozenset[str]]]:
        """Enumerate all distinct rational concepts of the ranked context."""
        seen: set[tuple[frozenset[str], frozenset[str]]] = set()
        rational_concepts: list[tuple[frozenset[str], frozenset[str]]] = []

        for intent in self.intents:
            attr_bits: bitarray = self._attributes_to_bitarray(intent)
            extent_bits: bitarray
            intent_bits: bitarray
            extent_bits, intent_bits = self.rational_concept(attr_bits)

            extent_fs: frozenset[str] = self._bitarray_to_objects(extent_bits)
            intent_fs: frozenset[str] = self._bitarray_to_attributes(intent_bits)

            key: tuple[frozenset[str], frozenset[str]] = (extent_fs, intent_fs)
            if key not in seen:
                seen.add(key)
                rational_concepts.append(key)

        return rational_concepts

    @override
    def __repr__(self) -> str:
        """Pretty-print the ranked context as a cross table."""
        obj_width: int = max(len(o) for o in self.objects) if self.objects else 7
        attr_widths: list[int] = [max(len(a), 1) for a in self.attributes]
        rank_width: int = 4

        if self.rankings:
            max_rank_num_width: int = len(str(len(self.rankings) - 1))
            rank_width = max(rank_width, max_rank_num_width)

        header: str = f"{'Rank':<{rank_width}} | {' ':<{obj_width}} |"
        for a, w in zip(self.attributes, attr_widths):
            header += f"{a:>{w + 2}}"

        lines: list[str] = [header]
        lines.append("-" * len(header))

        for i in range(len(self.rankings)):
            rank: FormalContext = self.rankings[i]
            for o, row in zip(rank.objects, rank.incidence):
                line: str = f"{i:<{rank_width}} | {o:<{obj_width}} |"

                for bit, w in zip(row, attr_widths):
                    mark: str = "X" if bit else " "
                    line += f"{mark:>{w + 2}}"
                lines.append(line)

        return "\n".join(lines)
