"""Package related tests."""


def test_import():
    """Test import."""
    import {{cookiecutter.project_slug}}  # noqa


def test_options():
    """Test options are called."""
    import {{cookiecutter.project_slug}}
    import sys
    sys.argv = [sys.argv[0]]
    assert {{cookiecutter.project_slug}}.main() == {}
