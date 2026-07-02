# Corrected Table 14 Formulas

This document states the corrected formulas used to regenerate Table 14.
All logarithms are base 2.

## Security Costs

Let `r_0 = 8`. Then

```latex
\gamma = \log_2(2r_0)
```

For the representative profiles,

```latex
\gamma = \log_2(16) = 4.
```

The classical and quantum-amplified generic conjugator-search estimates are

```latex
T_{\mathrm{cl}}(L) \approx (2r_0)^L
```

```latex
\log_2 T_{\mathrm{cl}} = \gamma L
```

```latex
T_q(L) \approx (2r_0)^{L/2}
```

```latex
\log_2 T_q = \frac{\gamma L}{2}.
```

## Parameter Rules

The corrected representative-profile rules are

```latex
L_{\min} = \frac{\max(\lambda_c, 2\lambda_q)}{\gamma}
```

```latex
L = \lceil \alpha L_{\min} \rceil
```

```latex
g = \lceil g_0 + \beta L \rceil
```

```latex
E = \lceil \delta \max(\lambda_c, 2\lambda_q) \rceil.
```

The constants are

```latex
r_0=8,\quad \alpha=1.5,\quad \beta=2/3,\quad \delta=2,\quad
g_0=6,\quad C_{\mathrm{pk}}=4.
```

For the representative profiles, `lambda_c = lambda_q`.

## Size Formulas

The public-key word length is

```latex
\ell_{\mathrm{pk}} = 2L.
```

The public-key size is

```latex
\mathrm{size(pk)} = 2\ell_{\mathrm{pk}} C_{\mathrm{pk}}
                 = 4LC_{\mathrm{pk}}.
```

The secret-key size is

```latex
\mathrm{size(sk)} = LC_{\mathrm{pk}}.
```

The ciphertext size is

```latex
\mathrm{size(C)}
  = (\ell(c_1) + \ell_{\mathrm{mask}}(c_2) + \ell_\mu)C_{\mathrm{pk}} + s_E
```

with

```latex
\ell(c_1)=L,\quad \ell_{\mathrm{mask}}(c_2)=L.
```

Therefore

```latex
\mathrm{size(C)} = (2L + \ell_\mu)C_{\mathrm{pk}} + s_E.
```

The manuscript profiles set `s_E = 0`.

## Unit Convention

`m_b` is the raw plaintext length in bits. `ell_mu` is the encoded-message
length in signed-generator-letter units after embedding into the commuting
Dehn-twist subgroup. `C_pk` is the bit cost per signed-generator letter.
`C_pk` is applied only to mapping-class word units and encoded generator slots,
not directly to raw message bits.

In the representative profile, a one-bit-per-Dehn-twist padded encoding is
used, so `m_b = 256` bits corresponds numerically to `ell_mu = 256` generator
slots. The units are conceptually different.

## E Is Not Serialized

`E` is not included in ciphertext size. The exponent `k` is ephemeral, sampled
locally during encryption, and not transmitted. It is used only to compute
`c_1 = a^k` and `c_2 = mu(m)b^k`. Hence `E` affects security and runtime, not
ciphertext communication size.
