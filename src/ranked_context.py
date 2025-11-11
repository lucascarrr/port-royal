from typing import override

from bitarray import bitarray

from src.context import FormalContext


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
            self.rankings = [FormalContext(objects, attributes, incidence)]
        else:
            # Optionally ensure all rankings are compatible
            for ctx in rankings:
                if ctx.attributes != attributes:
                    raise ValueError(
                        "All rankings must share the same objects and attributes."
                    )
            self.rankings: list[FormalContext] = rankings

    @override
    def __repr__(self) -> str:
        """Pretty-print the formal context as a cross table."""
        obj_width = max(len(o) for o in self.objects) if self.objects else 5
        attr_widths = [max(len(a), 1) for a in self.attributes]

        # 1. Calculate the width for the 'RANK' column
        # It must be wide enough for the word 'RANK' or the largest rank number
        rank_width = 4  # Default width for "RANK"
        if self.rankings:
            max_rank_num_width = len(str(len(self.rankings) - 1))
            rank_width = max(rank_width, max_rank_num_width)

        # 2. Build the header string with correct spacing
        header = f"{'Rank':<{rank_width}} | {'Object':<{obj_width}} |"
        for a, w in zip(self.attributes, attr_widths):
            header += f"{a:>{w + 2}}"

        lines = [header]
        lines.append("-" * len(header))

        # 3. Build data rows, aligning them with the new header
        for i in range(len(self.rankings)):
            rank = self.rankings[i]
            for o, row in zip(rank.objects, rank.incidence):
                # Use f-string formatting for alignment
                line = f"{i:<{rank_width}} | {o:<{obj_width}} |"

                for bit, w in zip(row, attr_widths):
                    mark = "X" if bit else " "
                    line += f"{mark:>{w + 2}}"
                lines.append(line)

        return "\n".join(lines)
