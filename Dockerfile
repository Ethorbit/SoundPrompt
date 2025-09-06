# LICENSE HEADER MANAGED BY add-license-header
#
# Copyright (C) 2025 Ethorbit
#
# This file is part of SoundPrompt.
#
# SoundPrompt is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# SoundPrompt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the
# GNU General Public License along with SoundPrompt.
# If not, see <https://www.gnu.org/licenses/>.
#

FROM python:3.11 AS base
ARG UID=1000
ARG GID=1000
ENV SENTENCE_TRANSFORMER_MODEL="all-MiniLM-L6-v2"
COPY --chown=${UID}:${GID} requirements.txt .
RUN groupadd -g ${GID} python &&\
    useradd -m -g ${GID} -u ${UID} python &&\
    pip install -r requirements.txt


FROM base AS develop
WORKDIR /app
VOLUME /app
COPY --chown=${UID}:${GID} ./requirements-dev.txt .
RUN pip install -r requirements-dev.txt
USER ${UID}:${GID}
ENTRYPOINT [ "bash" ]


FROM base AS app
WORKDIR /home/python
VOLUME /input /output
COPY --chown=${UID}:${GID} src .
USER ${UID}:${GID}
RUN python -c "from sentence_transformers \
    import SentenceTransformer; \
    SentenceTransformer('${SENTENCE_TRANSFORMER_MODEL}')"
ENTRYPOINT [ "python" ]
CMD [ "./src/main.py" ]
