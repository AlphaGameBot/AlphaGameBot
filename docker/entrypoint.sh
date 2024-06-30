#!/bin/bash

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

# This script is the entrypoint for the Docker container. It is responsible for
# setting up the environment and running the bot.

# We pass all arguments to the main.py script, so you can run the script with
# any arguments you want.

echo "entrypoint: Starting AlphaGameBot with arguments: $*"
python /docker/main.py $*