#!/usr/bin/env python3
"""Convert zoo.data to ctx format."""

# Attribute names from zoo.names (excluding animal name)
attributes = [
    "hair",
    "feathers",
    "eggs",
    "milk",
    "airborne",
    "aquatic",
    "predator",
    "toothed",
    "backbone",
    "breathes",
    "venomous",
    "fins",
    "legs=0",
    "legs=2",
    "legs=4",
    "legs=6",
    "legs=8",
    "tail",
    "domestic",
    "catsize",
    "type=Mammal",
    "type=Bird",
    "type=Reptile",
    "type=Fish",
    "type=Amphibian",
    "type=Bug",
    "type=Invertebrate",
]

# Type mapping
type_names = {
    1: "Mammal",
    2: "Bird",
    3: "Reptile",
    4: "Fish",
    5: "Amphibian",
    6: "Bug",
    7: "Invertebrate",
}

# Read the data
objects = []
matrix = []

with open("zoo_small.data", "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        parts = line.split(",")
        name = parts[0]
        features = [int(x) for x in parts[1:-1]]  # Exclude name and type
        animal_type = int(parts[-1])  # Get the type

        objects.append(name)

        # Build row with special handling for legs
        row_parts = []

        # Process attributes up to legs (indices 0-11)
        for i in range(12):
            row_parts.append("X" if features[i] > 0 else ".")

        # Handle legs specially - create one-hot encoding for leg values
        legs_value = features[12]
        for leg_count in [0, 2, 4, 6, 8]:
            row_parts.append("X" if legs_value == leg_count else ".")

        # Process remaining attributes after legs (indices 13-15)
        for i in range(13, 16):
            row_parts.append("X" if features[i] > 0 else ".")

        # Add type as one-hot encoded attributes
        for type_num in [1, 2, 3, 4, 5, 6, 7]:
            row_parts.append("X" if animal_type == type_num else ".")

        row = "".join(row_parts)
        matrix.append(row)

# Write ctx file
with open("zoo.ctx", "w") as f:
    f.write("B\n\n")
    f.write(f"{len(objects)}\n")
    f.write(f"{len(attributes)}\n\n")

    # Write object names
    for obj in objects:
        f.write(f"{obj}\n")

    # Write attribute names
    for attr in attributes:
        f.write(f"{attr}\n")

    # Write cross table
    for row in matrix:
        f.write(f"{row}\n")

    f.write("\n")

print(f"Created zoo.ctx with {len(objects)} objects and {len(attributes)} attributes")
