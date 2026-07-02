# TCSP-MCG Reproducibility Report

This report was generated from the package code and the corrected manuscript parameter model.

## Corrected Table 14

| Profile   |   Nominal PQ target lambda_q |   L |   Genus g = ceil(g0 + beta L) |   E bits, not serialized |   log2 T_cl |   log2 T_q |   Public key bits |   Secret key bits |   Ciphertext bits |
|:----------|-----------------------------:|----:|------------------------------:|-------------------------:|------------:|-----------:|------------------:|------------------:|------------------:|
| A         |                          128 |  96 |                            70 |                      512 |         384 |        192 |              1536 |               384 |              1792 |
| B         |                          192 | 144 |                           102 |                      768 |         576 |        288 |              2304 |               576 |              2176 |
| C         |                          256 | 192 |                           134 |                     1024 |         768 |        384 |              3072 |               768 |              2560 |

## Conventions

- Nominal PQ target lambda_q is the intended post-quantum target against the quantum-amplified generic conjugator-search attack, not the final classical search exponent.
- The profiles are conservative because Eq. (6.4) uses max(lambda_c, 2lambda_q) and Eq. (6.5) applies alpha = 1.5.
- E is not serialized. The ephemeral exponent k is sampled locally during encryption and is not transmitted.
- Ciphertext size uses (2L + ell_mu)C_pk + s_E, with s_E = 0 for the manuscript profiles.
- m_b is raw plaintext bits; ell_mu is encoded-message signed-generator slots.
- Public test vectors are symbolic demonstrations. Raw expanded symbolic word lengths may exceed the representative Table 14 lengths because powers are expanded before deterministic reduction. Table 14 uses the representative model c1 length L, c2 mask length L, and encoded-message length ell_mu.

## Validation

- Table 14 exactly matches corrected manuscript rows.
- E is excluded from ciphertext size unless s_E is explicitly nonzero.
- ell_mu, not raw m_b, is used in ciphertext-size formulas.
- Public test vectors include Table 14 representative serialization metadata.
- pytest stdout:
  ................                                                         [100%]
- All pytest tests passed.
