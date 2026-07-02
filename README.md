# TCSP-MCG Reproducibility Package

This repository is a public-ready reproducibility artifact for the paper
*Post-Quantum Public-Key Cryptosystem from Topological Conjugacy in Mapping
Class Groups*. It regenerates corrected Table 14, formula worksheets, plots,
deterministic symbolic test vectors, and reviewer-facing reports from the
stated parameter model.

Warning: this is research reproducibility code for formulas, serialization,
and deterministic symbolic test vectors. It is not production cryptographic
software and does not claim to be a certified computational mapping-class-group
implementation.

## Reviewer Comment 8

The artifact answers the reviewer reproducibility request by providing scripts
and worksheets for Table 14, exact formulas, representation and serialization
rules for mapping-class words, a signed-generator set, deterministic
word-reduction rules, and deterministic test vectors for key generation,
encryption, and decryption.

## Installation

Windows:

```powershell
cd TCSP_MCG_Reproducibility_Package
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Linux/macOS:

```bash
cd TCSP_MCG_Reproducibility_Package
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Python 3.11 or newer is required.

## One-Click Reproduction

Windows:

```powershell
.\run_all.bat
```

Linux/macOS:

```bash
chmod +x run_all.sh launch_ui.sh
./run_all.sh
```

The run script installs requirements, runs tests, regenerates Table 14,
generates plots and test vectors, writes reports, and prints a numbered output
summary.

## CLI

```bash
python -m src.cli generate-table14
python -m src.cli generate-plots
python -m src.cli generate-test-vectors
python -m src.cli validate
python -m src.cli run-all
```

## Streamlit UI

Windows:

```powershell
.\launch_ui.bat
```

For a guided execution screen with one step at a time and visible terminal
output, use:

```powershell
.\launch_step_by_step_ui.bat
```

Linux/macOS:

```bash
./launch_ui.sh
```

The dashboard shows corrected Table 14, editable formulas, unit warnings,
explanations of why E is not serialized, a test-vector generator, and a
reviewer artifact page.

## Corrected Parameter Model

The manuscript convention fixes `r0 = 8`, so `gamma = log2(2*r0) = 4`.
For representative profiles, `lambda_c = lambda_q`, `alpha = 1.5`,
`beta = 2/3`, `delta = 2`, `g0 = 6`, `C_pk = 4`, raw plaintext length
`m_b = 256` bits, encoded-message length `ell_mu = 256` generator slots,
and optional exponent-extension field `s_E = 0`.

Nominal PQ target `lambda_q` is the intended post-quantum target against the
quantum-amplified generic conjugator-search attack, not the final classical
search exponent. The profiles are conservative because Eq. (6.4) uses
`max(lambda_c, 2lambda_q)` and Eq. (6.5) applies `alpha = 1.5`. Thus
`L = 96, 144, 192` yields classical estimates `2^384, 2^576, 2^768`
and quantum-amplified estimates `2^192, 2^288, 2^384`.

## Serialization

The signed-generator alphabet is
`G = {g1, g1^-1, ..., g8, g8^-1}`. There are `2*r0 = 16` signed symbols,
so each signed-generator letter uses `C_pk = ceil(log2(16)) = 4` bits. The
artifact applies `C_pk` only to mapping-class word units and encoded generator
slots, not directly to raw message bits.

## Normal Form and Reduction

The package implements deterministic adjacent inverse-pair cancellation and a
stable serializer. This is the reproducible word-normalization rule used by
the artifact. Exact mathematical mapping-class normal forms can be substituted
by future implementations without changing Table 14 formulas.

The deterministic pseudo-Anosov-biased sampler is seed-driven, avoids
immediate inverse backtracking, and prefers changing generator support between
adjacent letters. It is a reproducible experiment sampler, not a mathematical
pseudo-Anosov certificate.

## Why k and E Are Not Serialized

The exponent `k` is ephemeral and sampled locally during encryption. It is used
only to compute `c1 = a^k` and `c2 = mu(m)b^k`; it is not transmitted. The
parameter `E` affects security and runtime, not ciphertext communication size.
The ciphertext formula is `(2L + ell_mu)C_pk + s_E`, with `s_E = 0` in the
manuscript. Public test vectors include only a hash of the bounded test-vector
exponent and do not publish raw exponent values. Optional local debug files
under `outputs/test_vectors/private_debug/` are excluded from the public
release by `.gitignore` and from the release ZIP.

## Test-Vector Lengths Versus Table 14 Lengths

The test-vector engine is a deterministic symbolic signed-generator-word
demonstration. Raw expanded symbolic word lengths may be larger than the
representative lengths used in Table 14 because powers may be expanded before
deterministic reduction. Table 14 reports the conservative representative
serialized model

```text
size(C) = (2L + ell_mu) C_pk
```

with `s_E = 0`. Each public JSON test vector includes a
`table14_serialization_model` object giving the representative `c1` length
`L`, representative `c2` mask length `L`, encoded-message length `ell_mu`,
`C_pk`, `s_E`, and the Table 14 ciphertext-bit value. The public vectors also
include raw symbolic demonstration lengths under explicit `raw_symbolic_*`
names.

## Reproducing Table 14

Run:

```bash
python -m src.cli generate-table14
```

The generated files are:

- `outputs/tables/table14_corrected.csv`
- `outputs/tables/table14_corrected.xlsx`
- `outputs/tables/table14_corrected.json`
- `outputs/tables/table14_corrected.md`
- `outputs/tables/formula_breakdown.csv`
- `outputs/tables/formula_breakdown.xlsx`

## Plots and Test Vectors

Run:

```bash
python -m src.cli generate-plots
python -m src.cli generate-test-vectors
```

Plots are saved under `outputs/plots/`. Profile A, B, and C test vectors are
saved under `outputs/test_vectors/`.

## Citation

Use `CITATION.cff` when citing this artifact, together with the associated
manuscript.

## Limitations

This repository is an archival reproducibility system for the corrected
numerical estimates, serialization conventions, and symbolic deterministic
workflow. It is not a production cryptographic implementation and does not
certify pseudo-Anosov behavior or exact mapping-class-group normal forms.
