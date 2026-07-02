"""Command-line interface for the TCSP-MCG reproducibility package."""

from __future__ import annotations

import typer
import sys

from . import output_generation as out


app = typer.Typer(help="Generate and validate the TCSP-MCG reproducibility artifact.")


def safe_echo(text: object) -> None:
    """Print text robustly when Windows console encoding is not UTF-8."""

    payload = str(text) + "\n"
    try:
        typer.echo(payload, nl=False)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(payload.encode("utf-8"))
        sys.stdout.buffer.flush()


@app.command("generate-table14")
def generate_table14_command() -> None:
    """Generate corrected Table 14 and formula breakdown worksheets."""

    paths = out.generate_table14()
    for index, path in enumerate(paths, 1):
        safe_echo(f"{index}. Saved {path}")


@app.command("generate-plots")
def generate_plots_command() -> None:
    """Generate all reproducibility plots."""

    paths = out.generate_plots()
    for index, path in enumerate(paths, 1):
        safe_echo(f"{index}. Saved {path}")


@app.command("generate-test-vectors")
def generate_test_vectors_command(seed: str = "artifact-v1") -> None:
    """Generate deterministic public test vectors and private debug vectors."""

    paths = out.generate_test_vectors(seed=seed)
    for index, path in enumerate(paths, 1):
        safe_echo(f"{index}. Saved {path}")


@app.command("validate")
def validate_command() -> None:
    """Run tests and validate all corrected manuscript values."""

    ok, messages = out.validate_all(run_pytest=True)
    out.generate_reports(messages)
    summary = out.final_summary(ok, messages)
    report_dir = out.OUTPUTS / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "validation_summary.txt").write_text(summary, encoding="utf-8")
    (report_dir / "run_log.txt").write_text(summary, encoding="utf-8")
    safe_echo(summary)
    raise typer.Exit(code=0 if ok else 1)


@app.command("run-all")
def run_all_command() -> None:
    """Generate tables, plots, test vectors, reports, and validation logs."""

    ok, summary = out.run_all()
    safe_echo(summary)
    raise typer.Exit(code=0 if ok else 1)


if __name__ == "__main__":
    app()
