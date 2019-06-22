FROM python:3.7

ENV port
ENV host

RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime
RUN apt-get update
RUN apt-get install -y graphviz

RUN pip install poetry
WORKDIR /usr/src/app

COPY poetry.lock /usr/src/app
COPY pyproject.toml /usr/src/app
RUN poetry install --no-dev

COPY . /usr/src/app
RUN poetry install --no-dev

CMD ["poetry", "run", "{{cookiecutter.project_slug}}", "start_server"]
HEALTHCHECK --interval=5m --timeout=3s --retries=1 CMD ["poetry", "run", "{{cookiecutter.project_slug}}", "check_status"]

EXPOSE 8080
