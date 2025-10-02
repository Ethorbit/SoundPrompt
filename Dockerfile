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
RUN groupadd -g ${GID} python &&\
    useradd -m -g ${GID} -u ${UID} python &&\
    apt update -y &&\
    apt install -y \
        pulseaudio \
        ffmpeg \
        libportaudio2


FROM base AS develop
ENV PYTHONPATH=/app/src
WORKDIR /app
VOLUME /app
COPY --chown=${UID}:${GID} pyproject.toml .
RUN pip install \
    --no-build-isolation \
    --editable .[dev]
USER ${UID}:${GID}
ENTRYPOINT [ "bash" ]


FROM base AS app
WORKDIR /home/python
VOLUME /input /output
ADD https://github.com/Ethorbit/SoundPrompt/releases/download/v0.1.0/soundprompt-0.1.0-py3-none-any.whl .
RUN pip install --no-build-isolation *.whl
USER ${UID}:${GID}
ENTRYPOINT [ "soundprompt" ]
