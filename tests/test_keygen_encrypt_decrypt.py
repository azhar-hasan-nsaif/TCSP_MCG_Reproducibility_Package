from src.crypto_workflow import decrypt, encrypt, generate_test_vector, keygen
from src.parameters import FormulaParameters, compute_profile


def test_symbolic_encrypt_decrypt_roundtrip():
    profile = compute_profile("A", FormulaParameters(lambda_q=128, lambda_c=128))
    keys = keygen(profile, "roundtrip")
    encrypted = encrypt(profile, {"a": keys["a"], "b": keys["b"]}, b"abc", "enc")
    recovered = decrypt({"h": keys["h"]}, {"c1": encrypted["c1"], "c2": encrypted["c2"]})
    assert recovered == encrypted["mu"]


def test_public_vector_hides_raw_k_and_verifies():
    profile = compute_profile("B", FormulaParameters(lambda_q=192, lambda_c=192))
    vector = generate_test_vector(profile, "artifact-v1")
    assert vector["verification"]["decrypts_correctly"] is True
    assert "raw_k_test_only" not in vector["ciphertext"]["k_metadata"]
    assert vector["ciphertext"]["k_metadata"]["E_bits_not_serialized"] == 768
    model = vector["table14_serialization_model"]
    assert model["s_E"] == 0
    assert model["E_is_serialized"] is False
    assert model["ciphertext_bits_table14"] == (2 * 144 + 256) * 4
    assert vector["ciphertext"]["table14_representative_lengths"]["table14_c1_representative_length"] == 144
    assert "raw_symbolic_c1_length" in vector["ciphertext"]["raw_symbolic_lengths"]
