# Generator Set

The artifact fixes a finite symmetric generator set with `r0 = 8` generator
pairs. The signed-generator alphabet is

```latex
G = \{g_1, g_1^{-1}, \ldots, g_8, g_8^{-1}\}.
```

There are

```latex
2r_0 = 16
```

signed symbols. Therefore

```latex
C_{\mathrm{pk}} = \lceil \log_2(16) \rceil = 4
```

bits are sufficient for each signed-generator letter.

The serializer maps positive generator `g_i` and inverse generator `g_i^-1`
to stable 4-bit codes. This package uses those codes for deterministic JSON
test vectors, bit-size estimates, and formula validation.

Future exact mapping-class-group implementations can replace this abstract
alphabet with a concrete Dehn-twist generating set. Such a replacement should
preserve the documented signed-symbol cardinality, bit-cost convention, and
stable serialization interface when reproducing the manuscript table.
