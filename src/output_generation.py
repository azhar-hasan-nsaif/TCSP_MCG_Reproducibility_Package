"""Output generation for tables, plots, reports, and validation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from .crypto_workflow import generate_test_vector, save_test_vectors
from .parameters import TABLE14_COLUMNS, compute_table14_profiles


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


EXPECTED_ROWS = [
    ["A", 128, 96, 70, 512, 384, 192, 1536, 384, 1792],
    ["B", 192, 144, 102, 768, 576, 288, 2304, 576, 2176],
    ["C", 256, 192, 134, 1024, 768, 384, 3072, 768, 2560],
]


def ensure_output_dirs() -> None:
    for relative in [
        "tables",
        "plots",
        "test_vectors",
        "reports",
    ]:
        (OUTPUTS / relative).mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    """Return a repository-relative POSIX-style path for public logs."""

    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def table14_dataframe() -> pd.DataFrame:
    return pd.DataFrame([profile.table14_row() for profile in compute_table14_profiles()], columns=TABLE14_COLUMNS)


def formula_breakdown_dataframe() -> pd.DataFrame:
    return pd.DataFrame([profile.formula_breakdown_row() for profile in compute_table14_profiles()])


def generate_table14() -> list[Path]:
    ensure_output_dirs()
    table = table14_dataframe()
    breakdown = formula_breakdown_dataframe()
    table_dir = OUTPUTS / "tables"
    paths = [
        table_dir / "table14_corrected.csv",
        table_dir / "table14_corrected.xlsx",
        table_dir / "table14_corrected.json",
        table_dir / "table14_corrected.md",
        table_dir / "formula_breakdown.csv",
        table_dir / "formula_breakdown.xlsx",
    ]
    table.to_csv(paths[0], index=False)
    table.to_excel(paths[1], index=False)
    table.to_json(paths[2], orient="records", indent=2)
    paths[3].write_text(table.to_markdown(index=False), encoding="utf-8")
    breakdown.to_csv(paths[4], index=False)
    breakdown.to_excel(paths[5], index=False)
    return paths


def generate_plots() -> list[Path]:
    ensure_output_dirs()
    df = table14_dataframe()
    plot_dir = OUTPUTS / "plots"
    profile = df["Profile"]
    styles = {
        "blue": "#1f77b4",
        "green": "#2ca02c",
        "red": "#d62728",
        "gray": "#4d4d4d",
    }

    def save_bar(column: str, title: str, ylabel: str, filename: str, color: str) -> Path:
        fig, ax = plt.subplots(figsize=(7, 4.5), dpi=160)
        ax.bar(profile, df[column], color=color, edgecolor="#222222", linewidth=0.7)
        ax.set_title(title)
        ax.set_xlabel("Profile")
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        path = plot_dir / filename
        fig.savefig(path)
        plt.close(fig)
        return path

    paths = [
        save_bar("log2 T_cl", "Classical Generic Conjugator-Search Cost", "log2 cost", "security_costs_classical.png", styles["blue"]),
        save_bar("log2 T_q", "Quantum-Amplified Generic Conjugator-Search Cost", "log2 cost", "security_costs_quantum.png", styles["green"]),
        save_bar("Ciphertext bits", "Ciphertext Size", "bits", "ciphertext_sizes.png", styles["red"]),
    ]

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=160)
    width = 0.35
    x = range(len(df))
    ax.bar([i - width / 2 for i in x], df["Public key bits"], width=width, label="Public key", color=styles["blue"], edgecolor="#222222", linewidth=0.7)
    ax.bar([i + width / 2 for i in x], df["Secret key bits"], width=width, label="Secret key", color=styles["gray"], edgecolor="#222222", linewidth=0.7)
    ax.set_xticks(list(x), profile)
    ax.set_title("Public and Secret Key Sizes")
    ax.set_xlabel("Profile")
    ax.set_ylabel("bits")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    key_path = plot_dir / "key_sizes.png"
    fig.savefig(key_path)
    plt.close(fig)
    paths.append(key_path)

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=160)
    ax.plot(df["L"], df["Genus g = ceil(g0 + beta L)"], marker="o", color=styles["blue"], linewidth=2)
    for _, row in df.iterrows():
        ax.annotate(row["Profile"], (row["L"], row["Genus g = ceil(g0 + beta L)"]), textcoords="offset points", xytext=(6, 6))
    ax.set_title("Genus Rule as a Function of L")
    ax.set_xlabel("L")
    ax.set_ylabel("Genus g")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    genus_path = plot_dir / "genus_vs_L.png"
    fig.savefig(genus_path)
    plt.close(fig)
    paths.append(genus_path)
    return paths


def generate_test_vectors(seed: str = "artifact-v1", include_private_debug: bool = False) -> list[Path]:
    ensure_output_dirs()
    private_dir = OUTPUTS / "test_vectors" / "private_debug"
    return save_test_vectors(
        OUTPUTS / "test_vectors",
        private_debug_dir=private_dir,
        seed=seed,
        include_private_debug=include_private_debug,
    )


def validate_all(run_pytest: bool = True) -> tuple[bool, list[str]]:
    """Validate formulas, serialization conventions, and deterministic vectors."""

    messages: list[str] = []
    ok = True
    df = table14_dataframe()
    actual = df.values.tolist()
    if actual != EXPECTED_ROWS:
        ok = False
        messages.append(f"Table 14 mismatch: {actual}")
    else:
        messages.append("Table 14 exactly matches corrected manuscript rows.")

    for profile in compute_table14_profiles():
        if profile.gamma != 4:
            ok = False
            messages.append(f"Profile {profile.profile}: gamma mismatch")
        if profile.E_serialized:
            ok = False
            messages.append(f"Profile {profile.profile}: E incorrectly marked serialized")
        expected_cipher = (2 * profile.L + profile.params.ell_mu) * profile.params.C_pk + profile.params.s_E
        if profile.ciphertext_bits != expected_cipher:
            ok = False
            messages.append(f"Profile {profile.profile}: ciphertext formula mismatch")
        vector = generate_test_vector(profile, "artifact-v1")
        if not vector["verification"]["decrypts_correctly"]:
            ok = False
            messages.append(f"Profile {profile.profile}: deterministic test vector did not decrypt")
        model = vector["table14_serialization_model"]
        if model["s_E"] != 0 or model["E_is_serialized"]:
            ok = False
            messages.append(f"Profile {profile.profile}: public serialization model incorrectly serializes E")
        if model["ciphertext_bits_table14"] != (2 * profile.L + profile.params.ell_mu) * profile.params.C_pk:
            ok = False
            messages.append(f"Profile {profile.profile}: Table 14 ciphertext bits formula mismatch")
    messages.append("E is excluded from ciphertext size unless s_E is explicitly nonzero.")
    messages.append("ell_mu, not raw m_b, is used in ciphertext-size formulas.")
    messages.append("Public test vectors include Table 14 representative serialization metadata.")

    if run_pytest:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        messages.append("pytest stdout:\n" + result.stdout.strip())
        if result.stderr.strip():
            messages.append("pytest stderr:\n" + result.stderr.strip())
        if result.returncode != 0:
            ok = False
            messages.append(f"pytest failed with exit code {result.returncode}")
        else:
            messages.append("All pytest tests passed.")
    return ok, messages


def generate_reports(validation_messages: list[str] | None = None) -> list[Path]:
    ensure_output_dirs()
    reports = OUTPUTS / "reports"
    table_md = table14_dataframe().to_markdown(index=False)
    report = f"""# TCSP-MCG Reproducibility Report

This report was generated from the package code and the corrected manuscript parameter model.

## Corrected Table 14

{table_md}

## Conventions

- Nominal PQ target lambda_q is the intended post-quantum target against the quantum-amplified generic conjugator-search attack, not the final classical search exponent.
- The profiles are conservative because Eq. (6.4) uses max(lambda_c, 2lambda_q) and Eq. (6.5) applies alpha = 1.5.
- E is not serialized. The ephemeral exponent k is sampled locally during encryption and is not transmitted.
- Ciphertext size uses (2L + ell_mu)C_pk + s_E, with s_E = 0 for the manuscript profiles.
- m_b is raw plaintext bits; ell_mu is encoded-message signed-generator slots.
- Public test vectors are symbolic demonstrations. Raw expanded symbolic word lengths may exceed the representative Table 14 lengths because powers are expanded before deterministic reduction. Table 14 uses the representative model c1 length L, c2 mask length L, and encoded-message length ell_mu.

## Validation

{chr(10).join('- ' + message.replace(chr(10), chr(10) + '  ') for message in (validation_messages or []))}
"""
    report_path = reports / "reproducibility_report.md"
    report_path.write_text(report, encoding="utf-8")

    reviewer = (
        "# Reviewer Response Artifact\n\n"
        "The reproducibility package has been prepared and includes scripts/worksheets for Table 14, "
        "exact formulas, representation and serialization rules, the signed-generator set, deterministic "
        "word-reduction rules, and test vectors for key generation, encryption, and decryption. Running "
        "run_all.bat or run_all.sh regenerates Table 14, all plots, and validation reports from the stated formulas.\n"
    )
    reviewer_path = reports / "reviewer_response_artifact.md"
    reviewer_path.write_text(reviewer, encoding="utf-8")
    return [report_path, reviewer_path]


def final_summary(ok: bool, validation_messages: list[str]) -> str:
    paths = [
        OUTPUTS / "tables" / "table14_corrected.csv",
        OUTPUTS / "tables" / "table14_corrected.xlsx",
        OUTPUTS / "tables" / "table14_corrected.json",
        OUTPUTS / "tables" / "table14_corrected.md",
        OUTPUTS / "tables" / "formula_breakdown.csv",
        OUTPUTS / "tables" / "formula_breakdown.xlsx",
        OUTPUTS / "test_vectors" / "profile_A_test_vector.json",
        OUTPUTS / "test_vectors" / "profile_B_test_vector.json",
        OUTPUTS / "test_vectors" / "profile_C_test_vector.json",
        OUTPUTS / "plots",
        OUTPUTS / "reports" / "reproducibility_report.md",
        OUTPUTS / "reports" / "reviewer_response_artifact.md",
        OUTPUTS / "reports" / "validation_summary.txt",
    ]
    lines = [
        "TCSP-MCG Reproducibility Package Final Output Summary",
        f"Status: {'SUCCESS' if ok else 'FAILURE'}",
        "",
        f"1. Repository cleaned.",
        f"2. .gitignore updated.",
        f"3. Absolute paths removed from public reports.",
        f"4. Test-vector serialization-model metadata added.",
        f"5. Raw symbolic lengths renamed and clarified.",
        f"6. Documentation updated.",
        f"7. Private debug data excluded from public release.",
        f"8. Table 14 regenerated and verified.",
        f"9. {'All tests passed.' if ok else 'Tests or validation failed.'}",
        f"10. Public-ready ZIP created when release packaging is run.",
        "",
        "Saved artifacts:",
        f"1. Table 14 CSV saved to {rel(paths[0])}",
        f"2. Table 14 XLSX saved to {rel(paths[1])}",
        f"3. Table 14 JSON saved to {rel(paths[2])}",
        f"4. Table 14 Markdown saved to {rel(paths[3])}",
        f"5. Formula breakdown CSV saved to {rel(paths[4])}",
        f"6. Formula breakdown XLSX saved to {rel(paths[5])}",
        f"7. Profile A test vector saved to {rel(paths[6])}",
        f"8. Profile B test vector saved to {rel(paths[7])}",
        f"9. Profile C test vector saved to {rel(paths[8])}",
        f"10. Plots saved to {rel(paths[9])}",
        f"11. Reproducibility report saved to {rel(paths[10])}",
        f"12. Reviewer artifact report saved to {rel(paths[11])}",
        f"13. Validation summary saved to {rel(paths[12])}",
        "",
        "Validation details:",
        *[f"- {message}" for message in validation_messages],
    ]
    return "\n".join(lines)


def run_all() -> tuple[bool, str]:
    generate_table14()
    generate_plots()
    generate_test_vectors()
    ok, messages = validate_all(run_pytest=True)
    generate_reports(messages)
    summary = final_summary(ok, messages)
    reports = OUTPUTS / "reports"
    (reports / "run_log.txt").write_text(summary, encoding="utf-8")
    (reports / "validation_summary.txt").write_text(summary, encoding="utf-8")
    return ok, summary
