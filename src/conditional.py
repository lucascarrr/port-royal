from typing import override
from bitarray import bitarray

from src.implications import Implication


class Conditional(Implication):
    def __init__(
        self, premise: list[str], conclusion: list[str], attributes: list[str]
    ) -> None:
        super().__init__(premise, conclusion, attributes)
