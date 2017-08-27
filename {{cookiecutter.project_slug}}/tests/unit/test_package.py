def test_import():
    """Test import."""
    import {{cookiecutter.project_slug}}


def test_docopt():
    """Test docopt is called on entry point."""
    import {{cookiecutter.project_slug}}
    from unittest.mock import patch

    with patch("{{cookiecutter.project_slug}}.docopt") as mock:
        {{cookiecutter.project_slug}}.main()
        mock().assert_called_once()
