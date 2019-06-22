#!/bin/bash
poetry init --name=base --description=base --author=author --dependency=aiohttp --dependency=toml --dependency=semver --dependency=aiohttp_apiset --dependency=cleo --dependency=pygogo --dependency=aiozipkin --dev-dependency=aiohttp-devtools --dev-dependency=auto-changelog --dev-dependency=sphinx --dev-dependency=bandit --dev-dependency=pytest-pydocstyle --dev-dependency=pytest-pycodestyle --dev-dependency=pytest-cov -q -n
poetry install
mkdir docs; poetry run sphinx-quickstart --makefile --sep -p base -a author -v 0.0.0  -q docs
git flow init -d
git tag 0.0.0
git config core.hooksPath `pwd`/.git_hooks
git config gitflow.path.hooks `pwd`/.git_hooks
