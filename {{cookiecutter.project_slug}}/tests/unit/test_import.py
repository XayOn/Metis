"""Base library tests."""


def test_import():
    """Test basic import."""
    import importlib
    try:
        importlib.import_module('{{cookiecutter.project_slug}}')
    except ImportError:
        assert False
