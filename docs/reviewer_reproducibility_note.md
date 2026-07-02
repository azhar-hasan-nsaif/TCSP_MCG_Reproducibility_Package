# Reviewer Reproducibility Note

This repository provides a complete reproducibility artifact for the corrected
parameter model used in Table 14 of the manuscript *Post-Quantum Public-Key
Cryptosystem from Topological Conjugacy in Mapping Class Groups*. It is
designed to answer reviewer comment 8 by making the numerical estimates,
serialization conventions, and symbolic correctness workflow independently
regenerable.

The repository contains scripts and worksheets used to generate Table 14,
exact formulas for each security and size estimate, representation and
serialization rules for mapping-class words, the signed-generator set
definition, the deterministic word-reduction procedure used by the artifact,
test vectors for key generation, encryption, and decryption, deterministic
seeds, validation outputs, exported tables, plots, and reports.

The package explicitly documents that the nominal post-quantum target
`lambda_q` is the intended target against the quantum-amplified generic
conjugator-search attack, not the final classical search exponent. The
reported profiles are conservative because the length rule uses
`max(lambda_c, 2lambda_q)` and then applies the expansion factor `alpha = 1.5`.
Consequently, the profiles with `L = 96, 144, 192` yield classical search
estimates `2^384, 2^576, 2^768` and quantum-amplified estimates
`2^192, 2^288, 2^384`.

The package also documents that `E` is not serialized. The ephemeral exponent
`k` is sampled locally during encryption and is used only to compute
`c1 = a^k` and `c2 = mu(m)b^k`. It is not transmitted, so `E` affects security
and runtime rather than ciphertext communication size.

The public test vectors are deterministic symbolic signed-generator-word
demonstrations. Raw expanded symbolic lengths may be larger than the
representative lengths used in Table 14 because powers are expanded before
deterministic reduction. The size table uses the representative serialization
model `size(C) = (2L + ell_mu)C_pk` with `s_E = 0`, and each public vector
records this model explicitly in `table14_serialization_model`. Public vectors
include enough metadata to reproduce and validate key generation, encryption,
and decryption while avoiding publication of private debug exponent values.

Running `run_all.bat` on Windows or `run_all.sh` on Linux/macOS regenerates
Table 14, the formula breakdown worksheets, plots, deterministic test vectors,
and validation reports.
