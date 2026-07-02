"""Streamlit dashboard for the TCSP-MCG reproducibility package."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.crypto_workflow import generate_test_vector  # noqa: E402
from src.output_generation import generate_plots, generate_table14, table14_dataframe  # noqa: E402
from src.parameters import FormulaParameters, compute_profile  # noqa: E402


st.set_page_config(page_title="TCSP-MCG Reproducibility", layout="wide")


STEP_COMMANDS = [
    ("Environment check", [sys.executable, "--version"]),
    ("Install requirements", [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]),
    ("Run pytest suite", [sys.executable, "-m", "pytest", "-q"]),
    ("Generate Table 14", [sys.executable, "-m", "src.cli", "generate-table14"]),
    ("Generate plots", [sys.executable, "-m", "src.cli", "generate-plots"]),
    ("Generate test vectors", [sys.executable, "-m", "src.cli", "generate-test-vectors"]),
    ("Validate artifact", [sys.executable, "-m", "src.cli", "validate"]),
]


def run_step(step_name: str, command: list[str]) -> dict[str, object]:
    """Run one artifact step and return structured execution metadata."""

    started = datetime.now()
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    finished = datetime.now()
    return {
        "step": step_name,
        "command": " ".join(command),
        "returncode": result.returncode,
        "started": started.strftime("%Y-%m-%d %H:%M:%S"),
        "finished": finished.strftime("%Y-%m-%d %H:%M:%S"),
        "seconds": round((finished - started).total_seconds(), 2),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def show_step_log(entry: dict[str, object], index: int) -> None:
    """Render one step log in an organized Streamlit block."""

    ok = entry["returncode"] == 0
    with st.expander(f"{index}. {entry['step']} - {'PASS' if ok else 'FAIL'}", expanded=not ok):
        st.write(f"Command: `{entry['command']}`")
        st.write(f"Started: `{entry['started']}`")
        st.write(f"Finished: `{entry['finished']}`")
        st.write(f"Duration: `{entry['seconds']} seconds`")
        st.write(f"Exit code: `{entry['returncode']}`")
        if entry["stdout"]:
            st.code(str(entry["stdout"]), language="text")
        if entry["stderr"]:
            st.error("stderr")
            st.code(str(entry["stderr"]), language="text")


def editable_profile() -> tuple[str, FormulaParameters]:
    st.sidebar.header("Parameters")
    profile = st.sidebar.selectbox("Profile", ["A", "B", "C"])
    defaults = {"A": 128, "B": 192, "C": 256}
    r0 = st.sidebar.number_input("r0", min_value=1, value=8, step=1)
    alpha = st.sidebar.number_input("alpha", min_value=1.0001, value=1.5, step=0.1)
    beta = st.sidebar.number_input("beta", min_value=0.0001, value=2 / 3, step=0.01, format="%.6f")
    delta = st.sidebar.number_input("delta", min_value=1.0001, value=2.0, step=0.1)
    g0 = st.sidebar.number_input("g0", min_value=3, value=6, step=1)
    C_pk = st.sidebar.number_input("C_pk", min_value=1, value=4, step=1)
    lambda_q = st.sidebar.number_input("lambda_q", min_value=1, value=defaults[profile], step=1)
    lambda_c = st.sidebar.number_input("lambda_c", min_value=1, value=defaults[profile], step=1)
    m_b = st.sidebar.number_input("m_b raw plaintext bits", min_value=0, value=256, step=1)
    ell_mu = st.sidebar.number_input("ell_mu encoded generator slots", min_value=0, value=256, step=1)
    use_override = st.sidebar.checkbox("Use L override", value=False)
    L_override = None
    if use_override:
        L_override = st.sidebar.number_input("L override", min_value=1, value=defaults[profile] * 3 // 4, step=1)
    s_E = st.sidebar.number_input("s_E optional extension bits", min_value=0, value=0, step=1)
    params = FormulaParameters(
        r0=int(r0),
        alpha=float(alpha),
        beta=float(beta),
        delta=float(delta),
        g0=int(g0),
        C_pk=int(C_pk),
        lambda_q=int(lambda_q),
        lambda_c=int(lambda_c),
        m_b=int(m_b),
        ell_mu=int(ell_mu),
        L_override=None if L_override is None else int(L_override),
        s_E=int(s_E),
    )
    return profile, params


page = st.sidebar.radio(
    "Page",
    ["Dashboard", "Step-by-step runner", "Formula explorer", "Test vectors", "Reviewer artifact"],
)

st.title("TCSP-MCG Reproducibility Package")
st.warning(
    "Research reproducibility code for formulas, serialization, and deterministic symbolic test vectors only; "
    "not production cryptographic software."
)

if page == "Dashboard":
    st.subheader("Corrected Table 14")
    st.dataframe(table14_dataframe(), use_container_width=True)
    if st.button("Regenerate tables and plots"):
        table_paths = generate_table14()
        plot_paths = generate_plots()
        st.success("Generated outputs.")
        st.write([str(path) for path in table_paths + plot_paths])

elif page == "Step-by-step runner":
    st.subheader("Step-by-Step Reproduction Runner")
    st.write(
        "Run the artifact workflow one step at a time and inspect the captured terminal output. "
        "Each step uses the same Python interpreter that launched this UI."
    )

    if "step_logs" not in st.session_state:
        st.session_state.step_logs = []
    if "next_step" not in st.session_state:
        st.session_state.next_step = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        run_next = st.button("Run next step", use_container_width=True)
    with col2:
        run_all_steps = st.button("Run all remaining", use_container_width=True)
    with col3:
        clear_logs = st.button("Clear logs", use_container_width=True)

    if clear_logs:
        st.session_state.step_logs = []
        st.session_state.next_step = 0
        st.rerun()

    if run_next and st.session_state.next_step < len(STEP_COMMANDS):
        name, command = STEP_COMMANDS[st.session_state.next_step]
        with st.spinner(f"Running: {name}"):
            entry = run_step(name, command)
        st.session_state.step_logs.append(entry)
        if entry["returncode"] == 0:
            st.session_state.next_step += 1

    if run_all_steps:
        while st.session_state.next_step < len(STEP_COMMANDS):
            name, command = STEP_COMMANDS[st.session_state.next_step]
            with st.spinner(f"Running: {name}"):
                entry = run_step(name, command)
            st.session_state.step_logs.append(entry)
            if entry["returncode"] != 0:
                break
            st.session_state.next_step += 1

    total = len(STEP_COMMANDS)
    completed = st.session_state.next_step
    st.progress(completed / total, text=f"{completed} of {total} steps completed")

    st.subheader("Execution Plan")
    plan_rows = []
    for idx, (name, command) in enumerate(STEP_COMMANDS, 1):
        if idx <= completed:
            status = "completed"
        elif idx == completed + 1:
            status = "next"
        else:
            status = "pending"
        plan_rows.append({"#": idx, "Step": name, "Status": status, "Command": " ".join(command)})
    st.dataframe(pd.DataFrame(plan_rows), use_container_width=True, hide_index=True)

    st.subheader("Execution Output")
    if not st.session_state.step_logs:
        st.info("No steps have been run yet.")
    for index, entry in enumerate(st.session_state.step_logs, 1):
        show_step_log(entry, index)

    if completed == total:
        st.success("All reproduction steps completed successfully.")
        st.write(f"Run log: `{ROOT / 'outputs' / 'reports' / 'run_log.txt'}`")
        st.write(f"Validation summary: `{ROOT / 'outputs' / 'reports' / 'validation_summary.txt'}`")

elif page == "Formula explorer":
    profile, params = editable_profile()
    result = compute_profile(profile, params)
    st.subheader("Real-Time Formula Results")
    st.dataframe(pd.DataFrame([result.table14_row()]), use_container_width=True)
    st.json(result.formula_breakdown_row())

    if params.m_b == params.ell_mu:
        st.info("m_b and ell_mu are numerically equal here, but m_b is raw bits and ell_mu is generator slots.")
    else:
        st.warning("m_b and ell_mu differ. This is valid only if the message encoding intentionally changes length.")

    st.subheader("Why E is not included in ciphertext size")
    st.write(
        "E controls the locally sampled ephemeral exponent k. The exponent is not transmitted; it is used only "
        "to compute c1 = a^k and c2 = mu(m)b^k. Ciphertext size is (2L + ell_mu)C_pk + s_E."
    )

    st.subheader("Nominal PQ target versus conservative estimates")
    st.write(
        "lambda_q is the nominal post-quantum target against the quantum-amplified generic search. "
        "The corrected model uses max(lambda_c, 2lambda_q) and then multiplies L_min by alpha = 1.5, "
        "so the reported log2 costs are larger than lambda_q."
    )

    st.subheader("Genus integer rule")
    st.write("The genus is computed as g = ceil(g0 + beta L).")

elif page == "Test vectors":
    profile, params = editable_profile()
    result = compute_profile(profile, params)
    seed = st.text_input("Seed", value="artifact-v1")
    if st.button("Generate deterministic test vector"):
        vector = generate_test_vector(result, seed)
        path = ROOT / "outputs" / "test_vectors" / f"profile_{profile}_ui_test_vector.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(vector, indent=2), encoding="utf-8")
        st.success(f"Saved {path}")

        st.subheader("Key-Generation / Encryption / Decryption Demonstration")
        col1, col2, col3 = st.columns(3)
        col1.metric("a length", vector["keys"]["a"]["serialization_length"])
        col1.metric("b = h a h^-1 length", vector["keys"]["b_public_conjugate"]["serialization_length"])
        col2.metric("raw symbolic c1 length", vector["ciphertext"]["raw_symbolic_lengths"]["raw_symbolic_c1_length"])
        col2.metric("raw symbolic c2 length", vector["ciphertext"]["raw_symbolic_lengths"]["raw_symbolic_c2_length"])
        col3.metric("mu length", vector["ciphertext"]["mu"]["serialization_length"])
        col3.metric("Decrypts correctly", str(vector["verification"]["decrypts_correctly"]))
        st.write("Table 14 representative serialization model:")
        st.json(vector["table14_serialization_model"])
        st.write(
            "The demonstration computes a, h, b = h a h^-1, a seeded local exponent k, "
            "c1 = a^k, c2 = mu(m)b^k, and then checks that decryption recovers mu(m). "
            "The public UI output saves k metadata and a hash, not raw k."
        )
        st.json(vector)

elif page == "Reviewer artifact":
    st.subheader("How this answers reviewer comment 8")
    st.write(
        "The reproducibility package includes scripts and worksheets for Table 14, exact formulas, representation "
        "and serialization rules, the signed-generator set, deterministic word-reduction rules, deterministic seeds, "
        "test vectors for key generation, encryption, and decryption, exported plots, and validation reports."
    )
    st.code("python -m src.cli run-all", language="bash")
