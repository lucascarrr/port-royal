from typing import override
from bitarray import bitarray

from src.implications import Implication


class Conditional(Implication):
    def __init__(
        self, premise: list[str], conclusion: list[str], attributes: list[str]
    ) -> None:
        super().__init__(premise, conclusion, attributes)

    @override
    def __repr__(self) -> str:
        premise_str = ", ".join(self.premise)
        conclusion_str = ", ".join(self.conclusion)
        return f"({premise_str} |~ {conclusion_str})"