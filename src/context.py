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

        # Lazy-loaded concept storage
        self._intents_list: list[frozenset[T]] | None = None
        self._extents_list: list[frozenset[str]] | None = None
        self._concepts_dirty: bool = True

        # Cached attribute extents for performance
        self._attribute_extents_cache: list[bitarray] | None = None

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

        # Initialize attribute extent cache
        self._build_attribute_extent_cache()

    @property
    def intents_list(self) -> list[frozenset[T]]:
        """Lazily compute and cache all concept intents."""
        if self._concepts_dirty or self._intents_list is None:
            self._compute_all_concepts()
        return self._intents_list  # type: ignore

    @property
    def extents_list(self) -> list[frozenset[str]]:
        """Lazily compute and cache all concept extents."""
        if self._concepts_dirty or self._extents_list is None:
            self._compute_all_concepts()
        return self._extents_list  # type: ignore

    def _build_attribute_extent_cache(self) -> None:
        """Build cache of attribute extents for fast lookup."""
        self._attribute_extents_cache = []
        for attr_idx in range(self.num_attributes):
            extent = bitarray(self.num_objects)
            for obj_idx in range(self.num_objects):
                extent[obj_idx] = self.incidence[obj_idx][attr_idx]
            self._attribute_extents_cache.append(extent)

    def _invalidate_caches(self) -> None:
        """Invalidate all caches when context is mutated."""
        self._concepts_dirty = True
        self._intents_list = None
        self._extents_list = None
        # Rebuild attribute extent cache
        self._build_attribute_extent_cache()

    def _compute_all_concepts(self) -> None:
        """
        Internal method to generate and store all concepts.
        Converts bitarray concepts into frozensets.
        """
        self._intents_list = []
        self._extents_list = []

        for extent_bits, intent_bits in self.generate_all_concepts():
            # Convert the bitarrays to frozensets before storing
            self._extents_list.append(self._bitarray_to_objects(extent_bits))
            self._intents_list.append(self._bitarray_to_attributes(intent_bits))

        self._concepts_dirty = False

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

    def _bitarray_to_objects(self, bits: bitarray) -> frozenset[str]:
        """Converts an object bitarray to a frozenset of object names."""
        return frozenset(self.objects[i] for i, bit in enumerate(bits) if bit)

    def _bitarray_to_attributes(self, bits: bitarray) -> frozenset[T]:
        """Converts an attribute bitarray to a frozenset of attribute names."""
        return frozenset(self.attributes[i] for i, bit in enumerate(bits) if bit)

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
        self._invalidate_caches()

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
        self._invalidate_caches()

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

    def has_attribute(self, obj_idx: int, attr_idx: int) -> bool:
        """Check if object obj_idx has attribute attr_idx."""
        return bool(self.incidence[obj_idx][attr_idx])

    def object_intent(self, obj_idx: int) -> bitarray:
        """Get all attributes of a given object."""
        return self.incidence[obj_idx].copy()

    def attribute_extent(self, attr_idx: int) -> bitarray:
        """Get all objects that have a given attribute."""
        if self._attribute_extents_cache is None:
            self._build_attribute_extent_cache()
        return self._attribute_extents_cache[attr_idx].copy()  # type: ignore

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
