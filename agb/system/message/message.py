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

import agb.system.cogwheel
import agb.system.leveling
import agb.system.message.say
import agb.system.onboarding
import mysql.connector
import discord
from discord.ext import commands
import logging
import os

async def handleOnMessage(bot: commands.Bot,
                          ctx: discord.Message,
                          cnx: mysql.connector.connection.MySQLConnection, 
                          CAN_USE_DATABASE: bool,
                          tracking: bool, 
                          forcesay: bool,
                          global_say_enabled: bool,
                          say_trigger: str | None = None) -> None:
    """This function handles messages sent by users.  It is called every time a message is sent,
    and it will handle dispatching the message to the appropriate functions.
    
    Args:
        bot (commands.Bot): The bot object.
        ctx (discord.Message): The message object.
        cnx (mysql.connector.connection.MySQLConnection): The database connection.
        CAN_USE_DATABASE (bool): Whether or not the database is enabled.
        tracking (bool): Whether or not to track messages.
        forcesay (bool): Whether or not to force the bot have say functionality regardless of the environment.
        global_say_enabled (bool): Whether or not the bot can say messages in all guilds.
        say_trigger (str): The trigger to make the bot say something."""
    logger = logging.getLogger("system")
    
    if ctx.author.bot:
        logger.debug("handleOnMessage: ignoring messages sent by bots. (id: {0}, userid: {1})".format(ctx.id, ctx.author.id))
        return
    
    if tracking and CAN_USE_DATABASE:
        await agb.system.onboarding.initializeNewUser(cnx, ctx.author.id, ctx.guild.id)
        await agb.system.leveling.countPoints(ctx, cnx, agb.system.leveling.CountingEvent.MESSAGE, CAN_USE_DATABASE, tracking)
        await agb.system.leveling.handleMessageLevelUp(ctx, cnx, CAN_USE_DATABASE, tracking)
    else:
        logging.debug("handleOnMessage: Not dispatching tracking functions because %s", 
                      "tracking is disabled" if not tracking else "the database is disabled")
    
    if ctx.content:
        logger.debug("handleOnMessage: Received bot-readable message: '%s'", ctx.content)
    
    await agb.system.message.say.handleSay(ctx, forcesay, global_say_enabled, say_trigger)