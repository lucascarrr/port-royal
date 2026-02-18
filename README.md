# Port Royal

A Python library for Formal Concept Analysis (FCA) with support for preferential semantics, defeasible reasoning, and ranked contexts.

## Overview

Port Royal provides tools for working with formal contexts and attribute implications, with extensions for non-monotonic reasoning:

- **Formal Contexts**: Create and manipulate cross-tables of objects and attributes
- **Concept Lattices**: Compute all formal concepts (extents and intents) using the NextClosure algorithm
- **Implications**: Work with attribute implications and compute the canonical (Duquenne-Guigues) basis
- **Ranked Contexts**: Partition objects by how well they satisfy a set of defeasible implications
- **Defeasible Conditionals**: Query conditionals under preferential semantics

## Installation

```bash
pip install bitarray
```

## Quick Start

### Loading a Context

Formal contexts can be loaded from `.ctx` or `.cxt` files (Burmeister format):

```python
from portroyal import load_context

context = load_context("input.ctx")
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

Access all formal concepts via the `intents` and `extents` properties:

```python
# Get all concept intents (closed attribute sets)
for intent in context.intents:
    print(intent)

# Get all concept extents (closed object sets)
for extent in context.extents:
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
from portroyal import Implication

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
from portroyal import object_rank, Implication

# Define defeasible rules
implications = [
    Implication(["a"], ["b"], context.attributes),  # a's typically have b
    Implication([], ["c"], context.attributes),     # typically c
]

# Rank objects: rank 0 = most typical, higher = less typical
ranked_context = object_rank(context, implications)
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
from portroyal import Conditional

# Create a conditional: b |~ a (b's typically have a)
cond = Conditional(["b"], ["a"], ranked_context.attributes)

# Check if the ranked context satisfies it
# (looks at the most typical objects with b)
ranked_context.satisfies(cond)
```

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
| `rational-concepts` | Enumerate all rational concepts |
| `save <file>` | Save context to file |

## File Format

Port Royal uses the Burmeister `.cxt` / `.ctx` format:

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

## Project Structure

```
port-royal/
├── main.py                 # Entry point
├── portroyal/
│   ├── __init__.py         # Public API
│   ├── context.py          # FormalContext class
│   ├── implication.py      # Implication + Conditional classes
│   ├── ranked_context.py   # RankedContext class
│   ├── algorithms.py       # object_rank algorithm
│   ├── io.py               # File I/O (load/save)
│   └── cli/
│       ├── __init__.py     # REPL core + dispatch
│       ├── context_commands.py   # load, save, show, info, list, reset
│       ├── fca_commands.py       # intents, extents, closure, basis
│       └── ranking_commands.py   # impl, rank, cond, defeasible-basis
└── data/                   # Example context files
```
