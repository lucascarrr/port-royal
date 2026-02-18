import os
from bitarray import bitarray
from portroyal.context import FormalContext


def save_context(context: FormalContext, file_name: str) -> None:
    """Save a formal context to a file in the project's 'data' directory.

    Uses the Burmeister (.cxt) format. If no extension is provided, .cxt is appended.
    """
    if not file_name.endswith((".ctx", ".cxt")):
        file_name += ".cxt"

    data_dir: str = os.path.join(os.path.dirname(__file__), "..", "data")
    file_path: str = os.path.join(data_dir, file_name)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("B\n")
            f.write("\n")
            f.write(f"{context.num_objects}\n")
            f.write(f"{context.num_attributes}\n")
            f.write("\n")

            for obj in context.objects:
                f.write(f"{obj}\n")

            for attr in context.attributes:
                f.write(f"{attr}\n")

            for row in context.incidence:
                line: str = "".join("X" if bit else "." for bit in row)
                f.write(f"{line}\n")

    except IOError as e:
        raise IOError(f"Error writing file {file_path}: {e}")


def load_context(file_name: str) -> FormalContext:
    """Load a formal context from the project's 'data' directory.

    Supports both .ctx and .cxt files. If no extension is given, tries .cxt then .ctx.
    """
    data_dir: str = os.path.join(os.path.dirname(__file__), "..", "data")

    if file_name.endswith((".ctx", ".cxt")):
        file_path: str = os.path.join(data_dir, file_name)
    else:
        cxt_path: str = os.path.join(data_dir, file_name + ".cxt")
        ctx_path: str = os.path.join(data_dir, file_name + ".ctx")
        if os.path.exists(cxt_path):
            file_path = cxt_path
        elif os.path.exists(ctx_path):
            file_path = ctx_path
        else:
            raise FileNotFoundError(
                f"Context file not found: tried {os.path.abspath(cxt_path)} and {os.path.abspath(ctx_path)}"
            )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Context file not found: {os.path.abspath(file_path)}")

    objects: list[str] = []
    attributes: list[str] = []
    incidence: list[bitarray] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if f.readline().strip() != "B":
                raise ValueError("Invalid format: Expected 'B' on the first line.")

            try:
                f.readline()
                num_objects: int = int(f.readline().strip())
            except ValueError:
                raise ValueError(
                    "Invalid format: Expected number of objects on line 2."
                )

            try:
                num_attributes: int = int(f.readline().strip())
            except ValueError:
                raise ValueError(
                    "Invalid format: Expected number of attributes on line 3."
                )

            if f.readline().strip() != "":
                raise ValueError(
                    "Invalid format: Expected empty line after counts."
                )

            for _ in range(num_objects):
                obj_name: str = f.readline().strip()
                if not obj_name:
                    raise ValueError("Invalid format: Found empty object name.")
                objects.append(obj_name)

            for _ in range(num_attributes):
                attr_name: str = f.readline().strip()
                if not attr_name:
                    raise ValueError("Invalid format: Found empty attribute name.")
                attributes.append(attr_name)

            for obj_idx in range(num_objects):
                line: str = f.readline().strip()

                if len(line) != num_attributes:
                    raise ValueError(
                        f"Incidence row {obj_idx} (object '{objects[obj_idx]}') has incorrect length. "
                        f"Expected {num_attributes}, got {len(line)}."
                    )

                row: bitarray = bitarray([char.lower() == "x" for char in line])
                incidence.append(row)

    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}")

    return FormalContext(objects, attributes, incidence)


def list_context_files() -> list[str]:
    """List all available .ctx and .cxt files in the data directory."""
    data_dir: str = os.path.join(os.path.dirname(__file__), "..", "data")
    if not os.path.exists(data_dir):
        return []
    return sorted(
        f for f in os.listdir(data_dir) if f.endswith((".ctx", ".cxt"))
    )
