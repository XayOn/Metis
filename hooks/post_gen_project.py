"""Post gen project."""

import subprocess
from getpass import getpass


def create_gh_repo():
    """Startup project on github."""
    import requests

    user_url = ("http://github.com/{{cookiecutter.github_username}}")
    repos_url = ('https://api.github.com/user/repos')
    repo_url = user_url + "/{{cookiecutter.project_slug}}/"

    if requests.get(repo_url).status_code == 200:
        return  # Repo already existent.

    data = {'name': '{{cookiecutter.project_slug}}'}
    auth = ("{{cookiecutter.github_username}}",
            getpass("Enter your github password: "))

    requests.post(repos_url, json=data, auth=auth)

    # Ok, repo initialized, init locally and make the first push.
    subprocess.check_output(("git", "init"))
    subprocess.check_output(("git", "add", "."))
    subprocess.check_call(("git", "remote", "add", "origin", repo_url))
    subprocess.check_output(("git", "commit", "-m", "Initial commit", "-a"))
    subprocess.check_output(("git", "push", "origin", "master"))


def create_rtd():
    """Create the readthedocs instance."""
    # TODO: Can't do with current RTD api...
    input("Please, manually create a project on readthedocs.org")


def create_travis():
    """Now create the travis instance."""
    # TODO: Not doing it right now... requires a GH access token with
    # travis enabled. And that requires about the same user interaction as
    # setting up the project...
    input("Please, manually create a project "
          "on travis-ci.com and coveralls.io")


def quickstart_sphinx():
    """Quickstart the documentation and make another commit so RTD gets it."""
    subprocess.check_call('sphinx-quickstart'.split())


create_gh_repo()
create_rtd()
create_travis()
quickstart_sphinx()
