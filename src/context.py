from itertools import chain, combinations
from typing import override, Generator, Tuple, TypeVar, Generic
from bitarray import bitarray
from src.implications import Implication

T = TypeVar("T", str, list[str])


class FormalContext(Generic[T]):

    def __init__(
        self,
        objects: list[str],
        attributes: list[T],
        incidence: list[bitarray] | None = None,
    ) -> None:
        self.objects: list[str] = objects
        self.attributes: list[T] = attributes
        self.num_objects: int = len(objects)
        self.num_attributes: int = len(attributes)
        self.intents_list: list[list[T]] = []
        self.extents_list: list[list[str]] = []

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

        self._compute_all_concepts()

    def _compute_all_concepts(self) -> None:
        """
        Internal method to generate and store all concepts.
        Converts bitarray concepts into lists of strings.
        """
        self.intents_list = []
        self.extents_list = []

        for extent_bits, intent_bits in self.generate_all_concepts():

            # Convert the bitarrays to lists of strings before storing
            self.extents_list.append(self._bitarray_to_objects(extent_bits))
            self.intents_list.append(self._bitarray_to_attributes(intent_bits))

    def generate_all_concepts(self) -> Generator[Tuple[bitarray, bitarray], None, None]:
        """
        The pairs are (extent, intent) bitarray objects.
        """
        current_intent = self.closure(bitarray("0" * self.num_attributes))
        current_extent = self.prime_attributes(current_intent)
        yield current_extent, current_intent

        top_intent = bitarray("1" * self.num_attributes)

        while current_intent != top_intent:
            current_intent = self._next_intent(current_intent)
            current_extent = self.prime_attributes(current_intent)
            yield current_extent, current_intent

    def _next_intent(self, intent: bitarray) -> bitarray:
        temp_intent = intent.copy()

        for i in range(self.num_attributes - 1, -1, -1):
            if temp_intent[i] == 1:
                temp_intent[i] = 0  # "unset" the bit
            else:
                candidate_basis = temp_intent.copy()
                candidate_basis[i] = 1

                new_intent = self.closure(candidate_basis)

                mask = bitarray("1" * self.num_attributes)
                for j in range(i, self.num_attributes):
                    mask[j] = 0

                if (new_intent & mask) == (temp_intent & mask):
                    return new_intent  # This is the next valid intent

        return bitarray("1" * self.num_attributes)

    def _bitarray_to_objects(self, bits: bitarray) -> list[str]:
        """Converts an object bitarray to a list of object names."""
        if bits.count() == 0:
            return []
        return [self.objects[i] for i, bit in enumerate(bits) if bit]

    def _bitarray_to_attributes(self, bits: bitarray) -> list[T]:
        """Converts an attribute bitarray to a list of attribute names."""
        if bits.count() == 0:
            return []
        return [self.attributes[i] for i, bit in enumerate(bits) if bit]

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
        self._compute_all_concepts()

    def add_relation(self, obj_name: str, attr_name: T) -> None:
        try:
            obj_idx = self.objects.index(obj_name)
        except ValueError:
            raise ValueError(f"Object '{obj_name}' not in context.")
        try:
            attr_idx = self.attributes.index(attr_name)
        except ValueError:
            raise ValueError(f"Attribute '{attr_name}' not in context.")

        self.set_relation(obj_idx, attr_idx, True)
        self._compute_all_concepts()

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

    def satisfies(self, implication: Implication) -> bool:
        """returns True if the implication is satisfied by the context"""
        return all(
            implication.satisfied(self.object_intent(i))
            for i in range(self.num_objects)
        )

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

        if not self.objects:
            lines.append("[No objects in context]")
            return "\n".join(lines)

        for o, row in zip(self.objects, self.incidence):
            line = f"{o:<{obj_width}} |"

            for bit, w in zip(row, attr_widths):
                mark = "X" if bit else " "
                line += f"{mark:>{w + 2}}"
            lines.append(line)

        return "\n".join(lines)
