# Serialization Model

Each signed-generator letter is encoded in 4 bits because the artifact fixes
`r0 = 8` generator pairs and therefore `2r0 = 16` signed symbols.

The stable symbol order is:

```text
g1, g1^-1, g2, g2^-1, ..., g8, g8^-1
```

The code for a letter is:

```text
code(g_i)    = 2(i - 1)
code(g_i^-1) = 2(i - 1) + 1
```

The hexadecimal serializer writes each 4-bit code as one hex digit. Word
length is the number of signed-generator letters after free reduction. Word
bit size is `length * C_pk`.

The artifact separates raw message bits from encoded generator slots. The raw
message length is `m_b`; the encoded mapping-class representation has length
`ell_mu`. In the representative profiles, both numbers are 256, but they have
different units.

## Representative Lengths and Symbolic Test Vectors

Table 14 uses a representative serialized communication model:

```text
size(C) = (2L + ell_mu) C_pk + s_E
```

with `s_E = 0` in the manuscript profiles. In this model, `c1` has
representative length `L`, the `c2` mask has representative length `L`, and
the encoded message has length `ell_mu`.

The deterministic test-vector engine expands powers symbolically before
deterministic reduction. As a result, raw symbolic demonstration lengths for
`c1` and `c2` may be larger than the representative Table 14 lengths. This is
expected and does not change the communication-size estimate. Public test
vectors therefore record both raw symbolic lengths and the
`table14_serialization_model` used for the paper's size table.

The exponent `k` is ephemeral and not serialized. The `E` column is used for
security and runtime estimation only.
