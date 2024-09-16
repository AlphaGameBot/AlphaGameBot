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
import random
import mysql.connector
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

def initalizeNewUser(cnx, user_id):
    """This is depricated and no longer needed, in favor of the newer `agb.system.message.onboarding` routine!"""

    logging.warning("initializeNewUser is depricated.  Move to the onboarding routine!")
    
    l = logging.getLogger("cogwheel")
    c = cnx.cursor()
    c.execute("SELECT * FROM user_settings WHERE userid = %s" % str(user_id))
    result = c.fetchone()
    if result is None:
        l.info("Adding user {0} to the database because they are not in it already.".format(user_id))
        l.debug(f"Adding user {user_id} to the database because they are not in it already.")
        
        # User Stats
        c.execute("INSERT INTO user_stats (userid, messages_sent, commands_ran) SELECT %s AS userid, %s AS messages_sent, %s AS commands_ran FROM DUAL WHERE NOT EXISTS ( SELECT 1 FROM user_stats WHERE userid = %s);", (user_id,0,0,user_id))

        # User Settings
        c.execute("INSERT INTO user_settings (userid) SELECT %s AS userid WHERE NOT EXISTS (SELECT 1 FROM user_settings WHERE userid = %s)", [user_id,user_id])
#        cnx.commit()
    c.close()

isDebugEnv = isDebug()

def getUserSetting(cnx: mysql.connector.MySQLConnection, user_id, setting):
    if cnx == None: return
    try:
        l = logging.getLogger("system")
        c = cnx.cursor()
        query = "SELECT {} FROM user_settings WHERE userid = %s".format(setting)
        fq = query % str(user_id)
        c.execute(query, [user_id])
        result = c.fetchone()
        if result is None:
            initalizeNewUser(cnx, user_id)
            return 
        r = result[0] 
        l.debug("SQL Query for user {0} (\"{1}\") returned {2}".format(user_id, fq, r))
        return result[0]
    except mysql.connector.errors.OperationalError as e:
        l.error("Cannot get user setting because the database connection is not working.  Error: '%s'" % repr(e))
        return None
    
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

def percent_of_happening(percent: float) -> bool:
    """Gets a percentage and compares it to a random call.  This gives a percentage of a certain event happening.
    
    Returns a boolean."""
    return random.random() < percent

class CogwheelLoggerHelper:
    """In hindsight, this was kind of a dumb idea.  This would do the logging but just prepend
    the cog name.

    Depricated."""
    def __init__(self, logger, cogname):
        self.logger = logger
        self.cogname = cogname
        self.constructor = "{0}: %s".format(self.cogname)
        self.logger.warning("CogwheelLoggerHelper is DEPRICATED.  All Cogwheel loggers should be moved over.")

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
        self.logger = logging.getLogger("cogwheel")
        self.cogName = type(self).__name__
        self.bot = bot

        # Attempt to run cog-specific tasks in self.init (NOT __init__)
        self.init()
        # init can be overwritten when needed

        self.logger.debug("Cog has successfully initalized!")

    def init(self):
        """This is a function that can be used in place of `__init__`.
        This function is *called* by __init__ on cog initialization.

        By default, this does nothing (meant to be overwritten)"""
        return
    
class MySQLEnabledCogwheel(Cogwheel):
    """Extended version of `Cogwheel`, but includes stuff for interacting with the MySQL database"""
    def __init__(self, bot: commands.Bot, cnx: mysql.connector.connection.MySQLConnection, canUseDatabase: bool = False):
        super().__init__(bot)
        self.cnx = cnx
        self.canUseDatabase = canUseDatabase
        if canUseDatabase:
            self.cursor = cnx.cursor()
        else:
            self.cursor = None

class DefaultView(discord.ui.View):
    """Extended version of `discord.ui.view` that includes default settings for the view, such as behavior for timeout."""

    force_no_timeout: bool = False
    async def on_timeout(self):
        """This function is called when the view times out.  By default, it closes all buttons."""
        if self.force_no_timeout: return
        # This code is stolen from the pycord default on_timeout source.
    
        self.disable_all_items()

        if not self._message or self._message.flags.ephemeral:
            message: discord.Message = self.parent
        else:
            message: discord.Message = self.message

        if message:
            m = await message.edit(view=self)
            if m:
                self._message = m

