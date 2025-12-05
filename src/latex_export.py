from src.context import FormalContext


def export_to_latex(
    context: FormalContext,
    label: str = "ctx:context",
    name: str = "Formal Context",
    resize: bool = False,
) -> str:
    """
    Export a FormalContext to LaTeX format using the cxt environment from fca.sty.

    Args:
        context: The FormalContext to export
        label: LaTeX label for the context (default: "ctx:context")
        name: Display name for the context (default: "Formal Context")
        resize: Whether to wrap in resizebox (default: False)

    Returns:
        LaTeX code as a string
    """
    lines = []

    # Begin cxt environment
    lines.append("\\begin{cxt}%")
    lines.append(f"\\cxtName{{{name}}}%")
    lines.append("")

    # Add attributes
    for attr in context.attributes:
        # Escape LaTeX special characters in attribute names
        escaped_attr = escape_latex(attr)
        lines.append(f"\\att{{{escaped_attr}}}%")

    lines.append("")

    # Add objects with their incidence vectors
    for obj_idx, obj_name in enumerate(context.objects):
        # Build incidence string: x for cross, . for empty
        incidence_str = "".join(
            "x" if context.has_attribute(obj_idx, attr_idx) else "."
            for attr_idx in range(context.num_attributes)
        )

        # Escape LaTeX special characters in object names
        escaped_obj = escape_latex(obj_name)

        lines.append(f"\\obj{{{incidence_str}}}{{{escaped_obj}}}")

    lines.append("")

    # End cxt environment
    lines.append("\\end{cxt}")

    return "\n".join(lines)


def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters in text.

    Args:
        text: The text to escape

    Returns:
        Escaped text safe for LaTeX
    """
    # Define replacements for LaTeX special characters
    replacements = {
        "\\": "\\textbackslash{}",
        "{": "\\{",
        "}": "\\}",
        "$": "\\$",
        "&": "\\&",
        "%": "\\%",
        "#": "\\#",
        "_": "\\_",
        "~": "\\textasciitilde{}",
        "^": "\\textasciicircum{}",
    }

    result = text
    # Handle backslash first to avoid double-escaping
    if "\\" in result:
        result = result.replace("\\", replacements["\\"])

    # Handle other special characters
    for char, replacement in replacements.items():
        if char != "\\":
            result = result.replace(char, replacement)

    return result


def export_context_to_file(
    context: FormalContext,
    output_path: str,
    label: str = "ctx:context",
    name: str = "Formal Context",
    resize: bool = False,
) -> None:
    """
    Export a FormalContext to a LaTeX file.

    Args:
        context: The FormalContext to export
        output_path: Path to the output .tex file
        label: LaTeX label for the context (default: "ctx:context")
        name: Display name for the context (default: "Formal Context")
        resize: Whether to wrap in resizebox (default: False)
    """
    latex_code = export_to_latex(context, label, name, resize)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex_code)
        f.write("\n")
