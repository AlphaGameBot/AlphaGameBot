#      AlphaGameBot - A Discord bot that's free and (hopefully) doesn't suck
#      Copyright (C) 2024  Damien Boisvert (AlphaGameDeveloper)
#
#      AlphaGameBot is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      AlphaGameBot is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with AlphaGameBot.  If not, see <https://www.gnu.org/licenses/>.

# This file is to run during docker build, after libraries are downloaded.

import sys
import nltk
import logging

def main(argv=sys.argv) -> int:
    logging.info("Starting Docker Build tasks!")

    logging.info("Step #1: Install NLTK (Natural Language ToolKit) stuff")
    nltk.download('words')
    logging.info("Step #1: COMPLETE")

    logging.info("Docker Build tasks DONE!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())