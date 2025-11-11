from typing import override

from bitarray import bitarray

from src.implications import Implication


class FormalContext:
    """Represents a formal context (G, M, I) where G is objects, M is attributes,
    and I is the incidence relation."""

    def __init__(
        self,
        objects: list[str],
        attributes: list[str],
        incidence: list[bitarray] | None = None,
    ) -> None:
        self.objects: list[str] = objects
        self.attributes: list[str] = attributes
        self.num_objects: int = len(objects)
        self.num_attributes: int = len(attributes)

        if incidence is None:
            self.incidence: list[bitarray] = [
                bitarray(self.num_attributes) for _ in range(self.num_objects)
            ]
        else:
            if len(incidence) != self.num_objects:
                raise ValueError(
                    "Incidence matrix size doesn't match number of objects"
                )
            for row in incidence:
                if len(row) != self.num_attributes:
                    raise ValueError(
                        "Incidence row size doesn't match number of attributes"
                    )
            self.incidence = incidence

    def set_relation(self, obj_idx: int, attr_idx: int, value: bool = True) -> None:
        """Set whether object obj_idx has attribute attr_idx."""
        self.incidence[obj_idx][attr_idx] = value

    def add_object(self, name: str, incidence_row: bitarray | None = None) -> None:
        """Add a new object (row) to the context."""
        if name in self.objects:
            raise ValueError(f"Object '{name}' already exists.")
        if incidence_row is None:
            incidence_row = bitarray(self.num_attributes)
            incidence_row.setall(0)
        elif len(incidence_row) != self.num_attributes:
            raise ValueError("Incidence row length must match number of attributes.")

        self.objects.append(name)
        self.incidence.append(incidence_row)
        self.num_objects += 1

    def add_relation(self, obj_name: str, attr_name: str) -> None:
        """Add a relation (object has attribute).Does not create a new element if missing"""

        obj_idx = self.objects.index(obj_name)
        attr_idx = self.attributes.index(attr_name)
        self.set_relation(obj_idx, attr_idx, True)

    def has_attribute(self, obj_idx: int, attr_idx: int) -> bool:
        """Check if object obj_idx has attribute attr_idx."""
        return bool(self.incidence[obj_idx][attr_idx])

    def object_intent(self, obj_idx: int) -> bitarray:
        """Get all attributes of a given object."""
        return self.incidence[obj_idx].copy()

    def attribute_extent(self, attr_idx: int) -> bitarray:
        """Get all objects that have a given attribute."""
        extent = bitarray(self.num_objects)
        for i in range(self.num_objects):
            extent[i] = self.incidence[i][attr_idx]
        return extent

    def satisfies(self, implication: "Implication") -> bool:
        """Check whether all objects in the context satisfy the implication."""
        return all(
            implication.satisfied(self.object_intent(i), self.attributes)
            for i in range(self.num_objects)
        )

    def prime_objects(self, objects: bitarray) -> bitarray:
        """Compute the intent of a set of objects (all common attributes)."""
        if objects.count() == 0:
            result = bitarray(self.num_attributes)
            result.setall(1)
            return result

        result = bitarray(self.num_attributes)
        result.setall(1)

        for obj_idx in range(self.num_objects):
            if objects[obj_idx]:
                result &= self.incidence[obj_idx]

        return result

    def prime_attributes(self, attributes: bitarray) -> bitarray:
        """Compute the extent of a set of attributes (all objects having these attributes)."""
        if attributes.count() == 0:
            result = bitarray(self.num_objects)
            result.setall(1)
            return result

        result = bitarray(self.num_objects)
        result.setall(1)

        for attr_idx in range(self.num_attributes):
            if attributes[attr_idx]:
                result &= self.attribute_extent(attr_idx)

        return result

    def closure(self, attributes: bitarray) -> bitarray:
        """Compute the closure of a set of attributes (A'')."""
        return self.prime_objects(self.prime_attributes(attributes))

    @override
    def __repr__(self) -> str:
        """Pretty-print the formal context as a cross table."""
        obj_width = max(len(o) for o in self.objects) if self.objects else 5
        attr_widths = [max(len(a), 1) for a in self.attributes]

        header = " " * (obj_width + 2)
        for a, w in zip(self.attributes, attr_widths):
            header += f"{a:>{w + 2}}"
        lines = [header]
        lines.append("-" * len(header))
        for o, row in zip(self.objects, self.incidence):
            line = f"{o:<{obj_width}} |"

            for bit, w in zip(row, attr_widths):
                mark = "X" if bit else " "
                line += f"{mark:>{w + 2}}"
            lines.append(line)

        return "\n".join(lines)
