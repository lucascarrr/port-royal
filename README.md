# Port Royal

A Python library for Formal Concept Analysis (FCA) with support for preferential semantics, defeasible reasoning, and ranked contexts.

## Overview

Port Royal provides tools for working with formal contexts and attribute implications, with extensions for non-monotonic reasoning:

- **Formal Contexts**: Create and manipulate cross-tables of objects and attributes
- **Concept Lattices**: Compute all formal concepts (extents and intents) using the NextClosure algorithm
- **Implications**: Work with attribute implications and compute the canonical (Duquenne-Guigues) basis
- **Ranked Contexts**: Partition objects by how well they satisfy a set of defeasible implications
- **Defeasible Conditionals**: Query conditionals under preferential semantics
- **Translated Contexts**: Transform ranked contexts for reasoning about typicality

## Installation

```bash
pip install bitarray
```

## Quick Start

### Loading a Context

Formal contexts can be loaded from `.ctx` files (Burmeister format):

```python
from src import load_context

context = load_context("input.ctx", "ctx")
print(context)
```

```
        a  b  c  d
------------------
obj1 |  X
obj2 |  X  X
obj3 |        X
obj4 |        X  X
```

### Computing Concepts

Access all formal concepts via the `intents_list` and `extents_list` properties:

```python
# Get all concept intents (closed attribute sets)
for intent in context.intents_list:
    print(intent)

# Get all concept extents (closed object sets)
for extent in context.extents_list:
    print(extent)

# Compute the closure of an attribute set
from bitarray import bitarray
attrs = context._attributes_to_bitarray(frozenset(["a"]))
closure = context.closure(attrs)
print(context._bitarray_to_attributes(closure))
```

### Attribute Implications

Create and check implications:

```python
from src import Implication

# Create an implication: {a, b} -> {c}
impl = Implication(["a", "b"], ["c"], context.attributes)

# Check if the context satisfies the implication
context.satisfies(impl)  # True if all objects satisfy it

# Check if a specific object satisfies it
impl.satisfied(context.incidence[0])  # Check first object
```

### Canonical Basis

Compute the Duquenne-Guigues basis (minimal complete set of implications):

```python
basis = context.get_canonical_basis()
for impl in basis:
    print(impl)
```

### Object Ranking

Given a set of defeasible implications, partition objects into ranks based on how "typical" they are:

```python
from src import object_rank, Implication

# Define defeasible rules
delta = [
    Implication(["a"], ["b"], context.attributes),  # a's typically have b
    Implication([], ["c"], context.attributes),     # typically c
]

# Rank objects: rank 0 = most typical, higher = less typical
ranked_context = object_rank(context, delta)
print(ranked_context)
```

```
Rank |      |  a  b  c  d
-------------------------
0    | obj3 |        X
0    | obj4 |        X  X
1    | obj2 |  X  X
2    | obj1 |  X
```

Objects in rank 0 satisfy all implications. Objects are promoted when they witness (provide a counterexample to) an implication that is then removed.

### Defeasible Conditionals

Query conditionals under preferential semantics:

```python
from src import Conditional

# Create a conditional: b |~ a (b's typically have a)
cond = Conditional(["b"], ["a"], ranked_context.attributes)

# Check if the ranked context satisfies it
# (looks at the most typical objects with b)
ranked_context.satisfies(cond)
```

### Translated Contexts

Transform a ranked context into a classical context for reasoning about typicality inheritance:

```python
from src import TranslatedContext

translated = TranslatedContext(ranked_context)
print(translated)
```

The translated context uses concept intents as attributes and implements inheritance: if any object in a lower (better) rank satisfies an attribute, all objects in higher ranks inherit it.

## Interactive REPL

Port Royal includes an interactive command-line interface:

```bash
python main.py
```

Available commands:

| Command | Description |
|---------|-------------|
| `load <file>` | Load a context from `data/<file>` |
| `show` | Display the current context |
| `info` | Show context statistics |
| `intents` | List all concept intents |
| `extents` | List all concept extents |
| `closure <attrs>` | Compute closure of comma-separated attributes |
| `extent <attrs>` | Get objects with given attributes |
| `intent <objs>` | Get attributes of given objects |
| `impl <P> -> <C>` | Add an implication |
| `impls` | List current implications |
| `rank` | Create ranked context from implications |
| `satisfies <P> -> <C>` | Check if implication holds |
| `cond <P> \|~ <C>` | Check conditional (ranked context) |
| `basis` | Compute canonical basis |
| `defeasible-basis` | Compute defeasible basis |
| `save <file>` | Save context to file |

## File Format

Port Royal uses the Burmeister `.ctx` format:

```
B

4
4

obj1
obj2
obj3
obj4
a
b
c
d
X...
XX..
..X.
..XX
```

- Line 1: `B` (format identifier)
- Line 2: empty
- Line 3: number of objects
- Line 4: number of attributes
- Line 5: empty
- Following lines: object names, then attribute names
- Final lines: incidence matrix (`X` = has attribute, `.` = doesn't)

## LaTeX Export

Export contexts to LaTeX using the `fca.sty` format:

```python
from src.latex_export import export_to_latex, export_context_to_file

# Get LaTeX string
latex = export_to_latex(context, label="ctx:example", name="Example Context")

# Or save directly to file
export_context_to_file(context, "output.tex")
```

## Project Structure

```
port-royal/
├── main.py                 # Interactive REPL
├── src/
│   ├── context.py          # FormalContext class
│   ├── implications.py     # Implication class
│   ├── conditional.py      # Conditional class (defeasible)
│   ├── ranked_context.py   # RankedContext class
│   ├── translated_ranked_context.py  # TranslatedContext class
│   ├── algorithms.py       # object_rank algorithm
│   ├── io.py               # File I/O (load/save)
│   └── latex_export.py     # LaTeX export utilities
└── data/                   # Example context files
```
