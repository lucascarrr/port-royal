from typing import override, Iterable

from src.implications import Implication


class Conditional(Implication):
    def __init__(
        self, premise: Iterable[str], conclusion: Iterable[str], attributes: list[str]
    ) -> None:
        super().__init__(premise, conclusion, attributes)

    @override
    def __repr__(self) -> str:
        premise_str = ", ".join(sorted(self.premise))
        conclusion_str = ", ".join(sorted(self.conclusion))
        return f"({premise_str} |~ {conclusion_str})"

