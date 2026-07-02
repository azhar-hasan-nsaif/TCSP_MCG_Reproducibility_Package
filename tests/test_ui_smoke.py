from pathlib import Path


def test_streamlit_app_exists_and_imports_core_paths():
    app_path = Path("ui/app.py")
    assert app_path.exists()
    text = app_path.read_text(encoding="utf-8")
    assert "streamlit" in text
    assert "generate_test_vector" in text
