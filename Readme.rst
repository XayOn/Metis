.. image:: /doc/logo.png?raw=true

Metis - Software craftmanship made right on :octocat:
-----------------------------------------------------

.. image:: https://travis-ci.org/xayon/metis.svg?branch=master
    :target: https://travis-ci.org/xayon/metis

.. image:: https://coveralls.io/repos/github/XayOn/Metis/badge.svg?branch=master
 :target: https://coveralls.io/github/XayOn/Metis?branch=master

.. image:: https://badge.fury.io/py/metis.svg
    :target: https://badge.fury.io/py/metis

`Metis <https://en.wikipedia.org/wiki/Metis_(mythology)>`_, (Μῆτις, "wisdom,"
"skill," or "craft"), mother of wisdom and deep tought on ancient greek
religion.

This package will setup an API service based on aiohttp with a few goodies:

- Organised project structure with poetry
- Automatic *API* versioning with semver and git-hooks
- Testable HTTP "models" that act as connections to other services
- Inter-service automatic tracing with zipking. Automatically propagates when using HTTP models.
- Behave, pytest and hypothesis, and helpers to quickly use them to test your API
- Direct swagger support with aiohttp-apiset
- Docker with healtcheck automatic command
- Travis configuration with tox
- ReadTheDocs configuration + sphinx enabled by default

Usage
-----

First, get `cookiecutter <https://github.com/audreyr/cookiecutter>`_.::

    pip install --user cookiecutter


Now, execute it and answer its questions::

    cookiecutter https://github.com/XayOn/Metis

Now, go to your ``project_slug`` directory, for example "metis_test"::

    cd metis_test


And have a look at its readme.
