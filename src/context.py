from itertools import chain, combinations
from typing import override, Generator, Tuple

from bitarray import bitarray

# Assuming 'Implication' is defined in a local file as in your original code
# If not, you may need to comment this line out or define a placeholder
from src.implications import Implication


class FormalContext:
    """Represents a formal context (G, M, I) where G is objects, M is attributes,
    and I is the incidence relation.

    Includes methods to compute all formal concepts (extents, intents)
    using Ganter's NextClosure algorithm.
    """

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

        # These lists will store the human-readable string names
        self.intents_list: list[list[str]] = []
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

        # Populate intents and extents upon initialization
        self._compute_all_concepts()

    # --- Concept Generation (Ganter's Algorithm) ---

    def _compute_all_concepts(self) -> None:
        """
        Internal method to generate and store all concepts.
        Converts bitarray concepts into lists of strings.
        """
        self.intents_list = []
        self.extents_list = []

        # The generator efficiently yields bitarrays
        for extent_bits, intent_bits in self.generate_all_concepts():

            # Convert the bitarrays to lists of strings before storing
            self.extents_list.append(self._bitarray_to_objects(extent_bits))
            self.intents_list.append(self._bitarray_to_attributes(intent_bits))

    def generate_all_concepts(self) -> Generator[Tuple[bitarray, bitarray], None, None]:
        """
        Generates all formal concepts (extent, intent) using Ganter's NextClosure.
        Yields them in lectical (lexicographical) order of intents.
        The pairs are (extent, intent) as bitarray objects.
        """
        # Start with the bottom concept (closure of empty set)
        current_intent = self.closure(bitarray("0" * self.num_attributes))
        current_extent = self.prime_attributes(current_intent)
        yield current_extent, current_intent

        # Prepare the "top" intent (all attributes) for comparison
        top_intent = bitarray("1" * self.num_attributes)

        while current_intent != top_intent:
            current_intent = self._next_intent(current_intent)
            current_extent = self.prime_attributes(current_intent)
            yield current_extent, current_intent

    def _next_intent(self, intent: bitarray) -> bitarray:
        """
        Computes the next concept intent in lectical order.
        This is the core of Ganter's algorithm.
        """
        temp_intent = intent.copy()

        # 1. Iterate attributes from right-to-left (m-1 down to 0)
        for i in range(self.num_attributes - 1, -1, -1):
            if temp_intent[i] == 1:
                temp_intent[i] = 0  # "unset" the bit
            else:
                # 2. Found the pivot 'i'. Form candidate basis B := (A \cap {0..i-1}) U {i}
                candidate_basis = temp_intent.copy()
                candidate_basis[i] = 1

                # 3. Compute closure: C := closure(B)
                new_intent = self.closure(candidate_basis)

                # 4. Canonicity test: C is lectically next if it agrees with B on all bits < i
                mask = bitarray("1" * self.num_attributes)
                for j in range(i, self.num_attributes):
                    mask[j] = 0

                if (new_intent & mask) == (temp_intent & mask):
                    return new_intent  # This is the next valid intent

        # Only reached if the input was the top_intent (all 1s)
        return bitarray("1" * self.num_attributes)

    # --- Bitarray to String List Helpers ---

    def _bitarray_to_objects(self, bits: bitarray) -> list[str]:
        """Converts an object bitarray to a list of object names."""
        if bits.count() == 0:
            return []
        return [self.objects[i] for i, bit in enumerate(bits) if bit]

    def _bitarray_to_attributes(self, bits: bitarray) -> list[str]:
        """Converts an attribute bitarray to a list of attribute names."""
        if bits.count() == 0:
            return []
        return [self.attributes[i] for i, bit in enumerate(bits) if bit]

    # --- Core FCA Derivation Operators (Prime/Closure) ---

    def prime_objects(self, objects: bitarray) -> bitarray:
        """Compute the intent of a set of objects (all common attributes)."""
        if objects.count() == 0:
            # Intent of empty set is all attributes
            result = bitarray(self.num_attributes)
            result.setall(1)
            return result

        result = bitarray(self.num_attributes)
        result.setall(1)  # Start with all attributes

        for obj_idx in range(self.num_objects):
            if objects[obj_idx]:
                result &= self.incidence[obj_idx]  # Intersect with object's intent

        return result

    def prime_attributes(self, attributes: bitarray) -> bitarray:
        """Compute the extent of a set of attributes (all objects having these attributes)."""
        if attributes.count() == 0:
            # Extent of empty set is all objects
            result = bitarray(self.num_objects)
            result.setall(1)
            return result

        result = bitarray(self.num_objects)
        result.setall(1)  # Start with all objects

        for attr_idx in range(self.num_attributes):
            if attributes[attr_idx]:
                result &= self.attribute_extent(
                    attr_idx
                )  # Intersect with attribute's extent

        return result

    def closure(self, attributes: bitarray) -> bitarray:
        """Compute the closure of a set of attributes (A'')."""
        return self.prime_objects(self.prime_attributes(attributes))

    # --- Context Modification & Utility Methods ---

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

        # Note: In a real application, adding an object would
        # require regenerating the concepts.
        # self._compute_all_concepts()

    def add_relation(self, obj_name: str, attr_name: str) -> None:
        """Add a relation (object has attribute)."""
        try:
            obj_idx = self.objects.index(obj_name)
        except ValueError:
            raise ValueError(f"Object '{obj_name}' not in context.")
        try:
            attr_idx = self.attributes.index(attr_name)
        except ValueError:
            raise ValueError(f"Attribute '{attr_name}' not in context.")

        self.set_relation(obj_idx, attr_idx, True)

        # Note: Modifying relations also requires regenerating concepts.
        # self._compute_all_concepts()

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
        """Check whether all objects in the context satisfy the implication."""
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
