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
from discord.ext import commands
from discord.embeds import *
import os
import json
import logging

global isDebugEnv

def getVersion() -> str:
    return json.load(open("alphagamebot.json", "r"))["VERSION"]

def getBotInformation() -> dict:
    return json.load(open("alphagamebot.json", "r"))

def getAPIEndpoint(apiName, process):
    _d = getBotInformation()
    _a = _d["API_ENDPOINTS"][apiName]
    _p = _a[process]
    return _p

def isDebug(argp=None) -> bool:
    global isDebugEnv
    useArgp = False
    
    if argp:
        _ = argp.debug
        useArgp = True
    else:
        _ = False
        argp = None
    debug_value =  _ if useArgp else (os.getenv("DEBUG") not in {"no", "false", "0", "", None})
    if isinstance(debug_value, bool):
        isDebugEnv = debug_value
        return debug_value
    r =  debug_value not in {"no", "false", "0", "", None}
    isDebugEnv = r
    return r


isDebugEnv = isDebug()

def embed(**kwargs) -> discord.Embed:
    """Easy way to set default embed characteristics.  Rather than using discord.Embed, you use cogwheel.embed which
    returns the discord.Embed, with default settings.  These can be overwritten after initalization.
    :rtype: object
    :returns discord.Embed"""

    _embed = discord.Embed(**kwargs)
    _embed.set_footer(text="AlphaGameBot version {0}{1}".format(
        getVersion(),
        " (development build)" if isDebugEnv else ""
    ),
                      icon_url="https://static.alphagame.dev/alphagamebot/img/icon.png")
    return _embed


class CogwheelLoggerHelper:
    def __init__(self, logger, cogname):
        self.logger = logger
        self.cogname = cogname
        self.constructor = "{0}: %s".format(self.cogname)

    def info(self, text: str = ""):
        """Proxy for `logging.info` but only for Cogs.  This will give a unified
        appearance that will allow different cogs to be distinguished in the console."""
        self.logger.info(self.constructor % text)
        return

    def warn(self, text: str = ""):
        """Proxy for `logging.warn` but only for Cogs.  This will give a unified
        appearance that will allow different cogs to be distinguished in the console."""
        self.logger.warn(self.constructor % text)
        return

    def error(self, text: str = ""):
        """Proxy for `logging.error` but only for Cogs.  This will give a unified
        appearance that will allow different cogs to be distinguished in the console."""
        self.logger.error(self.constructor % text)
        return

    def debug(self, text: str = ""):
        """Proxy for `logging.debug` but only for Cogs.  This will give a unified
        appearance that will allow different cogs to be distinguished in the console."""
        self.logger.debug(self.constructor % text)
        return

class Cogwheel(commands.Cog):
    """Cogwheel (`agb.cogwheel.Cogwheel`) is a customized version of `Cog` (`discord.ext.commands.Cog`)
    It allows for more predictable (and unified) behavior of Cogs.  All cogs used by AlphaGameBot are
    derived of `agb.cogwheel.Cogwheel`

    :param bot: Bot instance of which the cog is being deployed upon.
    :returns: Cogwheel (`agb.cogwheel.Cogwheel`) derived from `discord.ext.commands.Cog`"""
    def __init__(self, bot: commands.Bot):
        self.loggerInstance = logging.getLogger("cogwheel")
        self.cogName = type(self).__name__
        self.logger = CogwheelLoggerHelper(self.loggerInstance, self.cogName)
        self.bot = bot

        # Attempt to run cog-specific tasks in self.init (NOT __init__)
        self.init()
        # init can be overwritten when needed

        self.logger.info("Cog has successfully initalized!")

    def init(self):
        """This is a function that can be used in place of `__init__`.
        This function is *called* by __init__ on cog initialization.

        By default, this does nothing (meant to be overwritten)"""
        return