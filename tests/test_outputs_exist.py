from pathlib import Path
import json

import pandas as pd

from src.output_generation import (
    final_summary,
    generate_plots,
    generate_reports,
    generate_table14,
    generate_test_vectors,
    validate_all,
)


def test_requested_outputs_are_generated():
    paths = generate_table14() + generate_plots() + generate_test_vectors()
    required = [
        "outputs/tables/table14_corrected.csv",
        "outputs/tables/table14_corrected.xlsx",
        "outputs/tables/table14_corrected.json",
        "outputs/tables/table14_corrected.md",
        "outputs/tables/formula_breakdown.csv",
        "outputs/tables/formula_breakdown.xlsx",
        "outputs/test_vectors/profile_A_test_vector.json",
        "outputs/test_vectors/profile_B_test_vector.json",
        "outputs/test_vectors/profile_C_test_vector.json",
        "outputs/test_vectors/test_vector_summary.csv",
        "outputs/test_vectors/test_vector_summary.xlsx",
        "outputs/test_vectors/test_vector_summary.json",
        "outputs/test_vectors/test_vector_summary.md",
        "outputs/plots/security_costs_classical.png",
        "outputs/plots/security_costs_quantum.png",
        "outputs/plots/key_sizes.png",
        "outputs/plots/ciphertext_sizes.png",
        "outputs/plots/genus_vs_L.png",
    ]
    for relative in required:
        assert Path(relative).exists(), relative
    assert all(path.exists() for path in paths)


def test_public_reports_do_not_contain_absolute_local_paths():
    ok, messages = validate_all(run_pytest=False)
    assert ok
    generate_reports(messages)
    summary = final_summary(ok, messages)
    assert "C:\\Users\\" not in summary
    assert "Desktop\\INASS-EDITED" not in summary
    report_paths = [
        Path("outputs/reports/reproducibility_report.md"),
        Path("outputs/reports/reviewer_response_artifact.md"),
    ]
    for path in report_paths:
        text = path.read_text(encoding="utf-8")
        assert "C:\\Users\\" not in text
        assert "Desktop\\INASS-EDITED" not in text


def test_public_test_vectors_include_table14_serialization_model():
    generate_test_vectors()
    expected = {
        "A": (96, 1792),
        "B": (144, 2176),
        "C": (192, 2560),
    }
    for profile, (length, ciphertext_bits) in expected.items():
        path = Path(f"outputs/test_vectors/profile_{profile}_test_vector.json")
        vector = json.loads(path.read_text(encoding="utf-8"))
        model = vector["table14_serialization_model"]
        assert model["c1_representative_length"] == length
        assert model["c2_mask_representative_length"] == length
        assert model["encoded_message_length_ell_mu"] == 256
        assert model["C_pk"] == 4
        assert model["ciphertext_bits_table14"] == ciphertext_bits
        assert model["s_E"] == 0
        assert model["E_is_serialized"] is False
        assert "raw_symbolic_lengths" in vector["ciphertext"]
        assert "raw_k_test_only" not in vector["ciphertext"]["k_metadata"]
        assert vector["verification"]["decrypts_correctly"] is True


def test_public_summary_uses_raw_symbolic_column_names():
    generate_test_vectors()
    df = pd.read_csv("outputs/test_vectors/test_vector_summary.csv")
    assert "c1 length" not in df.columns
    assert "c2 length" not in df.columns
    for column in [
        "raw symbolic c1 length",
        "raw symbolic c2 length",
        "table14 c1 representative length",
        "table14 c2 mask representative length",
        "table14 ell_mu",
        "table14 ciphertext bits",
    ]:
        assert column in df.columns


def test_private_debug_is_ignored_for_public_release():
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    assert "outputs/test_vectors/private_debug/" in gitignore
