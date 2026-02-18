from typing import override, Iterable
from bitarray import bitarray


class Implication:
    def __init__(
        self, premise: Iterable[str], conclusion: Iterable[str], attributes: list[str]
    ) -> None:
        self.premise: frozenset[str] = frozenset(premise)
        self.conclusion: frozenset[str] = frozenset(conclusion)
        self.attributes: list[str] = attributes
        self.premise_bits: bitarray = bitarray(len(attributes))
        self.premise_bits.setall(0)
        self.conclusion_bits: bitarray = bitarray(len(attributes))
        self.conclusion_bits.setall(0)
        self.attr_to_idx: dict[str, int] = {
            attr: i for i, attr in enumerate(attributes)
        }

        for attr in self.premise:
            self.premise_bits[self.attr_to_idx[attr]] = 1
        for attr in self.conclusion:
            self.conclusion_bits[self.attr_to_idx[attr]] = 1

    def satisfied(self, obj_intent: bitarray) -> bool:
        """Return True if the object with intent obj_intent satisfies this implication."""
        satisfied, _ = self.check(obj_intent)
        return satisfied

    def check(self, obj_intent: bitarray) -> tuple[bool, bool]:
        """Check an object intent against this implication.

        Returns (satisfied, witnessed) where:
        - satisfied: True if the object satisfies the implication
        - witnessed: True if the object's intent contains the premise
        """
        if (obj_intent & self.premise_bits) != self.premise_bits:
            return True, False
        return (obj_intent & self.conclusion_bits) == self.conclusion_bits, True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Implication):
            return False
        return (self.premise == other.premise and
                self.conclusion == other.conclusion)

    def __hash__(self) -> int:
        return hash((self.premise, self.conclusion))

    @override
    def __repr__(self) -> str:
        premise_str: str = ", ".join(sorted(self.premise))
        conclusion_str: str = ", ".join(sorted(self.conclusion))
        return f"({premise_str} -> {conclusion_str})"


class Conditional(Implication):
    def __init__(
        self, premise: Iterable[str], conclusion: Iterable[str], attributes: list[str]
    ) -> None:
        super().__init__(premise, conclusion, attributes)

    @override
    def __repr__(self) -> str:
        premise_str: str = ", ".join(sorted(self.premise))
        conclusion_str: str = ", ".join(sorted(self.conclusion))
        return f"({premise_str} |~ {conclusion_str})"
