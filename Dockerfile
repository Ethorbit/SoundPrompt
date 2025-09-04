FROM python:3.11 AS base
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} python &&\
    useradd -m -g ${GID} -u ${UID} python
USER ${UID}:${GID}

FROM base AS develop
WORKDIR /app

FROM base AS app
WORKDIR /home/python
COPY --chown=${UID}:${GID} ./requirements.txt .
RUN pip install -r ./requirements.txt
COPY --chown=${UID}:${GID} ./src .
ENTRYPOINT [ "python" ]
CMD [ "./src/main.py" ]
