from src.output_generation import EXPECTED_ROWS, table14_dataframe


def test_table14_exact_rows_and_columns():
    df = table14_dataframe()
    assert df.values.tolist() == EXPECTED_ROWS
    assert list(df["Profile"]) == ["A", "B", "C"]
