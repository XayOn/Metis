#!/bin/bash -x

# Initialize project with default deps.
poetry init -q -n --name="{{cookiecutter.project_slug}}" \
        --description="{{cookiecutter.project_summary}}" \
        --author="{{cookiecutter.author_name}} <{{cookiecutter.author_email}}>"  \
        --dependency=aiohttp  \
        --dependency=toml \
        --dependency=semver \
        --dependency=aiohttp_apiset \
        --dependency=cleo \
        --dependency=pygogo \
        --dependency=aiozipkin \
        --dev-dependency=aiohttp-devtools \
        --dev-dependency=auto-changelog \
        --dev-dependency=sphinx \
        --dev-dependency=bandit \
        --dev-dependency=pytest-pydocstyle \
        --dev-dependency=pytest-pycodestyle \
        --dev-dependency=hypothesis \
        --dev-dependency=aioresponses \
        --dev-dependency=pytest-asyncio \
        --dev-dependency=pytest-aiohttp \
        --dev-dependency=pytest-cov
poetry install

# Make docs structure and defaults
mkdir docs; poetry run sphinx-quickstart -q \
    --makefile \
    --sep \
    -p "{{cookiecutter.project_slug}}"  \
    -a "{{cookiecutter.author_name}} <{{cookiecutter.author_email}}>"  \
    -v 0.0.0 docs

# Start git flow and get it with its first tag to enable direct auto-changelog usage
git flow init -d
git tag 0.0.0

# Configure git hooks
git config core.hooksPath `pwd`/.git_hooks
git config gitflow.path.hooks `pwd`/.git_hooks
