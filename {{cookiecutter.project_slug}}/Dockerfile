FROM python:3.6
ARG distfile

COPY ${distfile} /tmp
RUN pip install -e /tmp/${distfile}

ENTRYPOINT ["{{cookiecutter.project_slug}}"]
