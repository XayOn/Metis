"""Package related tests."""


def test_import():
    """Test import."""
    import metis  # noqa


def test_options():
    """Test options are called."""
    import metis
    import sys
    sys.argv = [sys.argv[0]]
    assert metis.main() == {}
