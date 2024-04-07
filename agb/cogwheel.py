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

import discord
from discord.embeds import *
import os
import json

def getVersion() -> str:
    return json.load(open("alphagamebot.json", "r"))["VERSION"]

def getBotInformation() -> dict:
    return json.load(open("alphagamebot.json", "r"))

def getAPIEndpoint(apiName, process):
    _d = getBotInformation()
    _a = _d["API_ENDPOINTS"][apiName]
    _p = _a[process]
    return _p

def embed(**kwargs) -> discord.Embed:
    """Easy way to set default embed characteristics.  Rather than using discord.Embed, you use cogwheel.embed which
    returns the discord.Embed, with default settings.  These can be overwritten after initalization.
    :rtype: object
    :returns discord.Embed"""

    __IS_DEBUG = (os.getenv("DEBUG_ENV") is not None)

    _embed = discord.Embed(**kwargs)
    _embed.set_footer(text="AlphaGameBot version {0}{1}".format(
        getVersion(),
        " (development build)" if __IS_DEBUG else ""
    ),
                      icon_url="https://static.alphagame.dev/alphagamebot/img/icon.png")
    return _embed
