# Normal Form and Reduction

This package implements a deterministic signed-word normalization rule for
reproducibility. It does not claim to compute a complete mathematical normal
form in the mapping class group.

## Rule

Words are represented as lists of signed-generator letters over
`{g1, g1^-1, ..., g8, g8^-1}`. The reduction rule scans from left to right and
cancels adjacent inverse pairs:

```text
... g_i g_i^-1 ... -> ...
... g_i^-1 g_i ... -> ...
```

The procedure is deterministic and stack-based. After reduction, serialization
uses the stable signed-symbol order and 4-bit codes defined in
`docs/generator_set.md`.

## Supported Operations

The word engine supports multiplication, inversion, exponentiation,
conjugation, serialization length, bit-size estimates, stable textual output,
hex encoding, and SHA-256 metadata.

## Deterministic Sampling Rule

For reproducible experiments, the package provides a deterministic
pseudo-Anosov-biased signed-word sampler. Given a seed and target length, it
uses Python's deterministic `random.Random(seed)` stream, chooses signed
letters from the fixed alphabet, avoids immediate inverse cancellation, and
prefers a different absolute generator index than the previous letter when
possible. The sign is selected deterministically from the seeded stream and
the letter position.

This rule is intended to make experiments reproducible and to avoid visibly
degenerate short-support words. It is not a proof or certificate that the
sampled symbolic word is pseudo-Anosov in a concrete mapping class group.

## Limitations

The reduction procedure is a reproducibility normalizer, not a certified exact
mapping-class-group normal form. It is sufficient for regenerating the
manuscript's numerical estimates and deterministic symbolic test vectors. A
future implementation may substitute a certified MCG library while retaining
the same external serialization and formula model.
