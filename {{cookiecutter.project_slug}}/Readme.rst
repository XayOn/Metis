{{cookiecutter.project_name}}
---------------------------------------------------

{{cookiecutter.project_description}}

Running tests
--------------

This project will automatically try to run the tests using tox each time you
make a git push.

To manually execute them, just run tox::

   tox


Versioning
-----------

API Versioning is automatic based on the software's version, so be careful with
making major releases

Making a semver release is automatic with git flow and hooks. To do so, just
execute git flow release with the semver keyword for the type of release you
want to do, for example::

   git flow release major


Distributing
-------------

This project uses poetry, poetry supports publishing projects to pypi and
making packages out-of-the-box::

   poetry build
   poetry publish


Executing the service
---------------------

To execute the service in development mode, use::

   poetry run adev runserver {{cookiecutter.project_slug}}/__init__.py


This will enable autoreload.

Building docker
----------------

This service is able to read the port and host to be executed on from
environment variables.

To use this feature, just pass port and host as env vars with docker run::

   docker run {{cookiecutter.project_slug}} -e port=8080 -e host=0.0.0.0
