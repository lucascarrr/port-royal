# Port Royal

##

### Input

A formal context in burgmeister format (see `./data/` for examples) may be loaded by calling, for e.g.

```python
example_context = load_context("../data/input.ctx", "ctx")
print(example_context)
```

```bash
        a  b  c  d
------------------
obj1 |  X         
obj2 |  X  X      
obj3 |        X   
obj4 |        X  X
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

Sets of implications are just lists of `Implication` type.

### Ranked Context

`RankedContext` is a subclass of `FormalContext`.
It maintains the original (unranked context) but adds a list `rankings: list[FormalContext]` which store each partition.
A ranked context may be constructed by calling the `object_rank: RankedContext` method from `algorithms`.

```python
delta = [
    Implication(["a"], ["b"], example_context.attributes),
    Implication([], ["c"], example_context.attributes),
]

ranked_context = object_rank(example_context, delta)
print(ranked_context)
```

```bash
Rank |      |  a  b  c  d
-------------------------
0    | obj3 |        X   
0    | obj4 |        X  X
1    | obj2 |  X  X      
2    | obj1 |  X         
```

### Defeasible Conditionals

Defeasible conditionals are implemented as `Conditional` type, which is a subclass of `Implication`. Really they are the same thing, but it is useful to have a distinction conceptually.
A conditional may be satisfied by a ranked context; but there is no notion of a set of attributes satisfying a conditional.

```python
defeasible_conditional = Conditional(["b"], ["a"], ranked_context.attributes)
defeasible_conditional_false = Conditional(["c"], ["d"], ranked_context.attributes)

print(ranked_context.satisfies(defeasible_conditional))
print(ranked_context.satisfies(defeasible_conditional_false))
```

```bash
True
False
```

### Translated Context

A ranked contexet may be _translated_ into a `TranslatedContext`, which is a subclass of `FormalContext`.

```python
translated_context = TranslatedContext(ranked_context)
print(translated_context)
```

```bash
       []  ['c']  ['c', 'd']  ['a']  ['a', 'b']  ['a', 'b', 'c', 'd'] 
----------------------------------------------------------------------
obj3 | X     X                                                        
obj4 | X     X        X                                               
obj2 | X     X        X         X        X                            
obj1 | X     X        X         X        X                            
```
