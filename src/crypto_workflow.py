"""Deterministic symbolic key-generation, encryption, decryption, and vectors."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any

from .parameters import ProfileResult, compute_table14_profiles
from .word_engine import Word, deterministic_word, pseudo_anosov_biased_word


WARNING = (
    "Research reproducibility code for formulas, serialization, and deterministic "
    "symbolic test vectors only; not production cryptographic software."
)


def seed_hash(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def encode_message(message: bytes, ell_mu: int) -> Word:
    """Encode raw message bits into ell_mu signed-generator slots.

    Bit 0 maps to g7 and bit 1 maps to g8. The bit stream is padded with zeros
    or truncated to exactly ell_mu slots. The unit is generator slots, not raw
    plaintext bits.
    """

    if ell_mu < 0:
        raise ValueError("ell_mu must be nonnegative")
    bits: list[int] = []
    for byte in message:
        bits.extend((byte >> shift) & 1 for shift in range(7, -1, -1))
    if len(bits) < ell_mu:
        bits.extend([0] * (ell_mu - len(bits)))
    bits = bits[:ell_mu]
    return Word(8 if bit else 7 for bit in bits)


def deterministic_ephemeral_exponent(seed: str, E: int) -> int:
    """Sample a deterministic compact positive exponent for finite test vectors.

    The manuscript parameter E is still recorded as the exponent security and
    runtime budget and is not serialized. Public JSON vectors use a bounded
    test-vector exponent so words can be expanded, checked, and archived.
    """

    if E < 0:
        raise ValueError("E must be nonnegative")
    if E == 0:
        return 0
    rng = random.Random(seed)
    return rng.randrange(2, 8)


def keygen(profile: ProfileResult, seed: str) -> dict[str, Word]:
    """Generate deterministic symbolic keys for a profile."""

    a = pseudo_anosov_biased_word(f"{seed}:base:a", profile.L)
    h = deterministic_word(f"{seed}:secret:h", profile.L)
    b = a.conjugate_by(h)
    return {"a": a, "h": h, "b": b}


def encrypt(profile: ProfileResult, public: dict[str, Word], message: bytes, seed: str) -> dict[str, Any]:
    """Encrypt deterministically in the symbolic model using a seeded exponent."""

    k = deterministic_ephemeral_exponent(seed, profile.E)
    mu = encode_message(message, profile.params.ell_mu)
    c1 = public["a"].power(k)
    c2 = mu * public["b"].power(k)
    return {"c1": c1, "c2": c2, "mu": mu, "k": k}


def decrypt(secret: dict[str, Word], ciphertext: dict[str, Word]) -> Word:
    """Recover the encoded message word through the symbolic correctness chain."""

    shared = ciphertext["c1"].conjugate_by(secret["h"])
    return ciphertext["c2"] * shared.inverse()


def word_payload(word: Word) -> dict[str, Any]:
    """Return public serialization metadata for a raw symbolic word."""

    raw_length = word.serialization_length()
    raw_bits = word.bit_size()
    return {
        "word": word.to_string(),
        "letters": word.to_codes(),
        "serialized_hex": word.to_hex(),
        "serialization_length": raw_length,
        "bit_size": raw_bits,
        "raw_symbolic_serialization_length": raw_length,
        "raw_symbolic_bit_size": raw_bits,
        "sha256": word.sha256(),
    }


def table14_serialization_model(profile: ProfileResult) -> dict[str, Any]:
    """Return the representative serialization model used for Table 14."""

    return {
        "c1_representative_length": profile.L,
        "c2_mask_representative_length": profile.L,
        "encoded_message_length_ell_mu": profile.params.ell_mu,
        "C_pk": profile.params.C_pk,
        "ciphertext_bits_table14": profile.ciphertext_bits,
        "s_E": profile.params.s_E,
        "E_is_serialized": profile.E_serialized,
        "note": (
            "These are the representative serialized lengths used in Table 14. "
            "Raw symbolic demonstration lengths may be larger because the test-vector "
            "engine expands powers before deterministic reduction. Table 14 uses the "
            "stated representative serialization model, not raw expanded symbolic word length."
        ),
    }


def generate_test_vector(profile: ProfileResult, seed: str, include_private_k: bool = False) -> dict[str, Any]:
    """Generate a deterministic public test vector for one profile."""

    key_seed = f"TCSP-MCG:{profile.profile}:{seed}:keygen"
    enc_seed = f"TCSP-MCG:{profile.profile}:{seed}:encrypt"
    message = hashlib.sha256(f"message:{profile.profile}:{seed}".encode("utf-8")).digest()
    keys = keygen(profile, key_seed)
    encrypted = encrypt(profile, {"a": keys["a"], "b": keys["b"]}, message, enc_seed)
    recovered = decrypt({"h": keys["h"]}, {"c1": encrypted["c1"], "c2": encrypted["c2"]})
    ok = recovered == encrypted["mu"]
    k_hash = hashlib.sha256(str(encrypted["k"]).encode("utf-8")).hexdigest()
    payload: dict[str, Any] = {
        "warning": WARNING,
        "profile": profile.profile,
        "seeds": {
            "master_seed": seed,
            "keygen_seed_hash": seed_hash(key_seed),
            "encryption_seed_hash": seed_hash(enc_seed),
        },
        "parameters": profile.params.model_dump(),
        "computed_profile": profile.table14_row(),
        "table14_serialization_model": table14_serialization_model(profile),
        "word_model": {
            "generator_pairs": profile.params.r0,
            "signed_symbols": 2 * profile.params.r0,
            "C_pk_bits_per_letter": profile.params.C_pk,
            "normalization": "adjacent inverse-pair free reduction with stable serializer",
        },
        "message": {
            "raw_plaintext_bits_m_b": profile.params.m_b,
            "encoded_slots_ell_mu": profile.params.ell_mu,
            "message_sha256": hashlib.sha256(message).hexdigest(),
        },
        "keys": {
            "a": word_payload(keys["a"]),
            "b_public_conjugate": word_payload(keys["b"]),
            "h_secret_metadata": {
                "serialization_length": keys["h"].serialization_length(),
                "bit_size": keys["h"].bit_size(),
                "sha256": keys["h"].sha256(),
            },
        },
        "ciphertext": {
            "c1": word_payload(encrypted["c1"]),
            "c2": word_payload(encrypted["c2"]),
            "mu": word_payload(encrypted["mu"]),
            "raw_symbolic_lengths": {
                "raw_symbolic_c1_length": encrypted["c1"].serialization_length(),
                "raw_symbolic_c2_length": encrypted["c2"].serialization_length(),
                "raw_symbolic_mu_length": encrypted["mu"].serialization_length(),
            },
            "table14_representative_lengths": {
                "table14_c1_representative_length": profile.L,
                "table14_c2_mask_representative_length": profile.L,
                "table14_encoded_message_length_ell_mu": profile.params.ell_mu,
                "table14_ciphertext_bits": profile.ciphertext_bits,
            },
            "k_metadata": {
                "E_bits_not_serialized": profile.E,
                "test_vector_exponent_mode": "bounded deterministic expansion for finite public vectors",
                "k_sha256": k_hash,
                "public_file_contains_raw_k": include_private_k,
            },
        },
        "verification": {
            "decrypts_correctly": ok,
            "recovered_mu_sha256": recovered.sha256(),
            "expected_mu_sha256": encrypted["mu"].sha256(),
        },
    }
    if include_private_k:
        payload["ciphertext"]["k_metadata"]["raw_k_test_only"] = encrypted["k"]
    return payload


def save_test_vectors(
    output_dir: Path,
    private_debug_dir: Path | None = None,
    seed: str = "artifact-v1",
    include_private_debug: bool = False,
) -> list[Path]:
    """Save deterministic public vectors, optionally with private debug copies."""

    output_dir.mkdir(parents=True, exist_ok=True)
    if include_private_debug and private_debug_dir is not None:
        private_debug_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    summary: list[dict[str, Any]] = []
    for profile in compute_table14_profiles():
        vector = generate_test_vector(profile, seed, include_private_k=False)
        path = output_dir / f"profile_{profile.profile}_test_vector.json"
        path.write_text(json.dumps(vector, indent=2), encoding="utf-8")
        paths.append(path)
        if include_private_debug and private_debug_dir is not None:
            private = generate_test_vector(profile, seed, include_private_k=True)
            private_path = private_debug_dir / f"profile_{profile.profile}_test_vector_private_debug.json"
            private_path.write_text(json.dumps(private, indent=2), encoding="utf-8")
            paths.append(private_path)
        model = vector["table14_serialization_model"]
        summary.append(
            {
                "Profile": profile.profile,
                "Seed": seed,
                "Decrypts correctly": vector["verification"]["decrypts_correctly"],
                "raw symbolic c1 length": vector["ciphertext"]["raw_symbolic_lengths"]["raw_symbolic_c1_length"],
                "raw symbolic c2 length": vector["ciphertext"]["raw_symbolic_lengths"]["raw_symbolic_c2_length"],
                "raw symbolic mu length": vector["ciphertext"]["raw_symbolic_lengths"]["raw_symbolic_mu_length"],
                "table14 c1 representative length": model["c1_representative_length"],
                "table14 c2 mask representative length": model["c2_mask_representative_length"],
                "table14 ell_mu": model["encoded_message_length_ell_mu"],
                "table14 ciphertext bits": model["ciphertext_bits_table14"],
                "s_E": model["s_E"],
                "E is serialized": model["E_is_serialized"],
                "E bits not serialized": profile.E,
                "k sha256": vector["ciphertext"]["k_metadata"]["k_sha256"],
            }
        )
    import pandas as pd

    summary_path = output_dir / "test_vector_summary.csv"
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(summary_path, index=False)
    paths.append(summary_path)

    summary_xlsx = output_dir / "test_vector_summary.xlsx"
    summary_json = output_dir / "test_vector_summary.json"
    summary_md = output_dir / "test_vector_summary.md"
    summary_df.to_excel(summary_xlsx, index=False)
    summary_df.to_json(summary_json, orient="records", indent=2)
    summary_md.write_text(summary_df.to_markdown(index=False), encoding="utf-8")
    paths.extend([summary_xlsx, summary_json, summary_md])
    return paths
