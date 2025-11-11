from typing import override

from bitarray import bitarray


class Implication:
    def __init__(
        self, premise: list[str], conclusion: list[str], attributes: list[str]
    ) -> None:
        self.premise: list[str] = premise
        self.conclusion: list[str] = conclusion
        self.attributes: list[str] = attributes
        self.premise_bits = bitarray(len(attributes))
        self.premise_bits.setall(0)
        self.conclusion_bits = bitarray(len(attributes))
        self.conclusion_bits.setall(0)
        self.attr_to_idx = {
            attr: i for i, attr in enumerate(attributes)
        }  # index of each attribute i.e. C = 2

        for attr in self.premise:
            self.premise_bits[self.attr_to_idx[attr]] = 1
        for attr in self.conclusion:
            self.conclusion_bits[self.attr_to_idx[attr]] = 1

    def satisfied(self, obj_intent: "bitarray") -> bool:
        """Return True if the object with intent obj_intent satisfies this implication."""
        satisfied, _ = self.sat_wit(obj_intent)
        return satisfied

    def sat_wit(self, obj_intent: bitarray) -> tuple[bool, bool]:
        if (obj_intent & self.premise_bits) != self.premise_bits:
            return True, False
        return (obj_intent & self.conclusion_bits) == self.conclusion_bits, True

    @override
    def __repr__(self) -> str:
        premise_str = ", ".join(self.premise)
        conclusion_str = ", ".join(self.conclusion)
        return f"({premise_str} -> {conclusion_str})"
