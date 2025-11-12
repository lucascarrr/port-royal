# Preferential FCA

##

### Input

A formal context in burgmeister format (see `./data/` for examples) may be loaded by calling, for e.g.

```python
    example_context = load_context("../data/input.ctx", "ctx")
```

### Implications

Attribute implications are created with three arguments.

```python
    example_implication = Implication(["a", "b"], ["c"], example_context.attributes)
```

Corresponds to the implication `{a,b} -> {c}` defined over the set of attributes from `example_context`. You may query whether a _context_ satisfies an implication:

```python
example_context.satisfies(example_implication)
```

Or whether an implication is satisfied by an object (intent):

```python
example_implication.satisfied(example_context.incidence[0]) # incidence[0] is the intent of object[0]
```

