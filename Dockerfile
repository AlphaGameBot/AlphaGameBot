# AlphaGameBot - A Discord bot that's free and (hopefully) doesn't suck
# Copyright (C) 2024  Damien Boisvert (AlphaGameDeveloper)

# AlphaGameBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# AlphaGameBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with AlphaGameBot.  If not, see <https://www.gnu.org/licenses/>.


# Define build arguments before the FROM instruction
ARG COMMIT_MESSAGE="No Git commit message given!"
ARG BUILD_NUMBER=INFINITY
ARG BRANCH_NAME=unknown

# Use Python 3.11 for pycord compatibility
FROM python:3.14.0a3

# Re-define the arguments after the FROM instruction
ARG COMMIT_MESSAGE
ARG BUILD_NUMBER
ARG BRANCH_NAME

# Now, we must set the build arguments to be in the environment variables.
ENV COMMIT_MESSAGE=${COMMIT_MESSAGE}
ENV BUILD_NUMBER=${BUILD_NUMBER}
ENV BRANCH_NAME=${BRANCH_NAME}

# - - - - -

# All program code is located in the /docker directory (in the container)
WORKDIR /docker

COPY requirements.txt /docker/requirements.txt

RUN /usr/local/bin/python3 -m pip install -r /docker/requirements.txt

# Run tasks
COPY docker/* /

RUN /usr/local/bin/python3 /setup.py inContainer

COPY . /docker

ENTRYPOINT [ "/docker/docker/entrypoint.sh" ]