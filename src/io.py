import os
from bitarray import bitarray
from src.context import FormalContext


def load_context(file_name: str, format: str) -> FormalContext:
    """
    Loads a formal context from a file located in the project's 'data' directory.
    Currently only supports the '.ctx' (ConImp) format.
    """

    if format.lower() != "ctx":
        raise ValueError(f"Unsupported format: '{format}'. Only 'ctx' is supported.")

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    file_path = os.path.join(data_dir, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Context file not found: {os.path.abspath(file_path)}")

    objects: list[str] = []
    attributes: list[str] = []
    incidence: list[bitarray] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if f.readline().strip() != "B":
                raise ValueError("Invalid .ctx format: Expected 'B' on the first line.")

            try:
                f.readline()
                num_objects = int(f.readline().strip())
            except ValueError:
                raise ValueError(
                    "Invalid .ctx format: Expected number of objects on line 2."
                )

            try:
                num_attributes = int(f.readline().strip())
            except ValueError:
                raise ValueError(
                    "Invalid .ctx format: Expected number of attributes on line 3."
                )

            if f.readline().strip() != "":
                raise ValueError(
                    "Invalid .ctx format: Expected empty line after counts."
                )

            for _ in range(num_objects):
                obj_name = f.readline().strip()
                if not obj_name:
                    raise ValueError("Invalid .ctx format: Found empty object name.")
                objects.append(obj_name)

            for _ in range(num_attributes):
                attr_name = f.readline().strip()
                if not attr_name:
                    raise ValueError("Invalid .ctx format: Found empty attribute name.")
                attributes.append(attr_name)

            for obj_idx in range(num_objects):
                line = f.readline().strip()

                if len(line) != num_attributes:
                    raise ValueError(
                        f"Incidence row {obj_idx} (object '{objects[obj_idx]}') has incorrect length. Expected {num_attributes}, got {len(line)}."
                    )

                row = bitarray([char.lower() == "x" for char in line])
                incidence.append(row)

    except IOError as e:
        raise IOError(f"Error reading or parsing file {file_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during file parsing: {e}")

    return FormalContext(objects, attributes, incidence)
