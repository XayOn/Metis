"""{{cookiecutter.project_name}}.

{{cookiecutter.project_summary}}
"""

from docopt import docopt


def main():
    """{{cookiecutter.project_slug}}.

    {{cookiecutter.project_summary}}

    Usage: {{cookiecutter.project_slug}} [options]
    """
    options = docopt(main.__doc__)
    return options
