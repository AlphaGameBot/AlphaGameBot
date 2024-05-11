#    AlphaGameBot - A Discord bot that's free and (hopefully) doesn't suck
#    Copyright (C) 2024  Damien Boisvert (AlphaGameDeveloper)

#    AlphaGameBot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    AlphaGameBot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with AlphaGameBot.  If not, see <https://www.gnu.org/licenses/>.


# We create some Docker build arguments, which allow you to pass environment variables into the
# built container.  I use Jenkins for deployment, so this is *really* useful as environment 
# variables like COMMIT_MESSAGE and other Git stuff need to be passed with the image.
ARG COMMIT_MESSAGE="No Git commit message given!"
# Set build number to -1.  I could have chosen Infinity for this but whatever.
ARG BUILD_NUMBER="-1"
ARG BRANCH_NAME="unknown"

# We use Python 3.11, as 3.12 is not compatable with Pycord for some reason :/
FROM python:3.11.2


# Now, we must set the build arguments to be in the environment variables.
ENV COMMIT_MESSAGE=${COMMIT_MESSAGE}
ENV BUILD_NUMBER=${BUILD_NUMBER}
ENV BRANCH_NAME=${BRANCH_NAME}
# - - - - -

# All program code is located in the /docker directory (in the container)
WORKDIR /docker

COPY requirements.txt /docker/requirements.txt

RUN /usr/local/bin/python3 -m pip install -r /docker/requirements.txt

COPY . /docker

CMD ["python3", "/docker/main.py"]