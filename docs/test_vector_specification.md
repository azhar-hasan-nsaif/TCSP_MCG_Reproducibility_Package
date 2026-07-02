# Test Vector Specification

Each public test-vector JSON file contains the following sections.

## warning

A statement that the file is research reproducibility data, not production
cryptographic material.

## profile

The profile label: `A`, `B`, or `C`.

## seeds

The master seed and SHA-256 hashes of the derived key-generation and
encryption seeds. Public files do not expose seed-expanded private randomness
beyond reproducibility metadata.

## parameters

The validated formula inputs: `r0`, `alpha`, `beta`, `delta`, `g0`, `C_pk`,
`lambda_q`, `lambda_c`, `m_b`, `ell_mu`, optional `L_override`, and `s_E`.

## computed_profile

The corrected Table 14 row for the profile.

## word_model

The generator-pair count, signed-symbol count, 4-bit signed-letter cost, and
the normalization rule: adjacent inverse-pair free reduction with stable
serialization.

The base element is sampled using the documented deterministic
pseudo-Anosov-biased signed-word sampler. The secret conjugator is sampled
using the deterministic signed-word sampler. Both samplers are seeded and
avoid immediate inverse backtracking.

## message

The raw plaintext length `m_b`, encoded-message generator-slot length
`ell_mu`, and SHA-256 hash of the deterministic message bytes.

## keys

The base element `a`, public conjugate `b = h a h^-1`, and secret-conjugator
metadata for `h`. Public vectors include the hash, length, and bit size of
`h`, not the secret word itself.

## ciphertext

The symbolic ciphertext components `c1`, `c2`, encoded message `mu`, raw
symbolic length metadata, Table 14 representative length metadata, and
ephemeral exponent metadata. Public vectors include `E`, the bounded
test-vector exponent mode, and a hash of `k`. They do not expose raw exponent
values.

## table14_serialization_model

Each public test vector contains a `table14_serialization_model` object with:

- `c1_representative_length`
- `c2_mask_representative_length`
- `encoded_message_length_ell_mu`
- `C_pk`
- `ciphertext_bits_table14`
- `s_E`
- `E_is_serialized`
- `note`

These fields state the representative serialized model used in Table 14. Raw
expanded symbolic word lengths may be larger because the test-vector engine
expands powers before deterministic reduction. Table 14 uses the stated
representative model, not the raw expanded symbolic word length.

Optional local debug files under `outputs/test_vectors/private_debug/` may
include raw `k` for developer-only auditing, but that directory is excluded
by `.gitignore` and from the public release ZIP.

## verification

The correctness result, recovered `mu` hash, and expected `mu` hash. A valid
vector has `decrypts_correctly = true`.
