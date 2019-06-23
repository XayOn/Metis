#!/bin/bash -x
poetry init -q -n --name=base \
        --description=base \
        --author=author  \
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

mkdir docs;
poetry run sphinx-quickstart -q \
    --makefile \
    --sep \
    -p "{{cookiecutter.project_slug}}"  \
    -a "{{cookiecutter.author_name}} <{{cookiecutter.author_email}}>"  \
    -v 0.0.0 docs

git flow init -d
git tag 0.0.0

git config core.hooksPath `pwd`/.git_hooks
git config gitflow.path.hooks `pwd`/.git_hooks
