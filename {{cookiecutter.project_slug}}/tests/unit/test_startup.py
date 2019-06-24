from hypothesis import given
from hypothesis import assume
import hypothesis.strategies as st


@given(st.integers())
def test_app_version(ver):
    """Test app version autodetection."""
    from pathlib import Path
    import tempfile
    import {{cookiecutter.project_slug}}

    assume(ver > 0)

    directory = tempfile.mkdtemp()
    (Path(directory) / 'pyproject.toml').write_text(f"""
[tool.poetry]
version = "{ver}.1.2"
    """)

    {{cookiecutter.project_slug}}.MAIN_DIR = Path(directory)
    assert {{cookiecutter.project_slug}}.get_app_version('v') == f'v{ver}'
