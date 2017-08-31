"""Metis.

Convert behave features to github issues
"""

from docopt import docopt


def main():
    """metis.

    Convert behave features to github issues

    Usage: metis [options]
    """
    options = docopt(main.__doc__)
    return options
