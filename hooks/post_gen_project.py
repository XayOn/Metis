"""Post gen project."""

from contextlib import suppress
import os
import subprocess


def startenv():
    """Use pipenv and install development deps (and first freeze)."""
    os.environ['PATH'] += ':~/.local/bin'
    subprocess.check_call(['git', 'init'])

    with suppress(Exception):
        subprocess.check_call(['git', 'flow', 'init', '-d'])

    subprocess.check_call(['pip', 'install', '--user', 'pipenv'])
    subprocess.check_call(['pipenv', 'install', '--dev', 'behave'])
    subprocess.check_call(['pipenv', 'install', 'docopt'])
    subprocess.check_call(['pipenv', 'lock'])
    subprocess.check_call(['pipenv', 'run', 'pip', 'install', '-e', '.[doc]'])
    subprocess.check_call(['pipenv', 'run', 'sphinx-quickstart', '-q', '-p',
                           '{{cookiecutter.project_slug}}', '-a',
                           "{{cookiecutter.author_name}}", '-v' '0.0.1', '-l',
                           'rst', '--master', 'index', '--sep', '--dot=.',
                           '--ext-autodoc', '--ext-todo', '--ext-coverage',
                           '--ext-viewcode', '--makefile', 'docs'])


startenv()
