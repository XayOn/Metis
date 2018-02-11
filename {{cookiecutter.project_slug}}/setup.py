#!/usr/bin/env python
"""Postilion."""

import os
import sys
import subprocess
from setuptools import setup

action = sys.argv[1]


def update_reqs():
    """Updates requirements files."""
    if not os.path.exists('Pipfile'):
        return
    subprocess.check_call('pipenv lock', shell=True)
    subprocess.check_call(
        'pipenv lock -r | cut -d\- -f1 > tools/pip-requires',
        shell=True)
    subprocess.check_call(
        'pipenv lock --dev -r |cut -d\- -f1 > tools/test-requires',
        shell=True)


if action == "update_requirements":
    update_reqs()
    sys.exit(0)
elif action == "build_sphinx":
    subprocess.check_call('pipenv run pip install -e ".[doc]"', shell=True)
elif 'dist' in action:
    update_reqs()


if action == 'docker':
    subprocess.check_call(
        'docker build --build-arg distfile={}'.format(sys.argv[2]), shell=True)
    sys.exit(0)


setup(setup_requires=['pbr>=1.9', 'setuptools>=17.1', 'pytest-runner'],
      pbr=True)
