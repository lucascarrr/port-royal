"""
Example script to export the Zoo dataset to LaTeX format.
"""

from src import load_context, export_to_latex, export_context_to_file


def main():
    # Load the zoo context
    zoo_context = load_context("zoo/zoo.ctx", "ctx")

    # Export to LaTeX string
    latex_code = export_to_latex(
        context=zoo_context,
        label="ctx:zoodata",
        name="\\textbf{\\texttt{Zoo Data}}",
        resize=True,
        resize_width="1.1\\textwidth",
    )

    # Print to console
    print(latex_code)
    print("\n" + "=" * 60)
    print("LaTeX code generated successfully!")
    print("=" * 60)

    # Optionally, save to a file
    output_file = "zoo_context.tex"
    export_context_to_file(
        context=zoo_context,
        output_path=output_file,
        label="ctx:zoodata",
        name="\\textbf{\\texttt{Zoo Data}}",
    )
    print(f"\nLaTeX code also saved to: {output_file}")

    # You can also export a subset of the data
    print("\n" + "=" * 60)
    print("Example: First 5 animals only")
    print("=" * 60)

    # Create a subset context (first 5 animals)
    from src.context import FormalContext
    from bitarray import bitarray

    subset_context = FormalContext(
        objects=zoo_context.objects[:5],
        attributes=zoo_context.attributes,
        incidence=[row.copy() for row in zoo_context.incidence[:5]],
    )

    subset_latex = export_to_latex(
        context=subset_context,
        label="ctx:zoodata_subset",
        name="\\textbf{\\texttt{Zoo Data (Sample)}}",
        resize=True,
    )

    print(subset_latex)


if __name__ == "__main__":
    main()
