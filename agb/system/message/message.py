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

import agb.cogwheel
import agb.system.message.leveling
import agb.system.onboarding
import agb.system.message.counting
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
    bot_information = agb.cogwheel.getBotInformation()
    
    if say_trigger is None:
        say_trigger = bot.user.mention # <@BOT_ID>
    
    say_prompted = ctx.content.startswith(say_trigger)
    
    ctx.content = ctx.content.strip(say_trigger).strip()
    if say_prompted:
        logger.debug("Recieved say message: (original: %s, valuetosay: %s, isSay: %s)", ctx.content, ctx.content, say_prompted)

    if ctx.author.bot:
        logger.debug("handleOnMessage: ignoring messages sent by bots. (id: {0}, userid: {1})".format(ctx.id, ctx.author.id))
        return
    
    if tracking and CAN_USE_DATABASE:
        await agb.system.onboarding.initalizeNewUser(cnx, ctx.author.id, ctx.guild.id)
        await agb.system.message.counting.countMessage(ctx, cnx, CAN_USE_DATABASE, tracking)
        await agb.system.message.leveling.handleMessageLevelUp(ctx, cnx, CAN_USE_DATABASE, tracking)
    else:
        logging.debug("handleOnMessage: Not dispatching tracking functions because %s", "tracking is disabled" if not tracking else "the database is disabled")

    if ctx.content.startswith(say_trigger) == False and not say_prompted:
        return

    # Disable the say command for all servers except for the ones in which they are explicitly
    # enabled in alphagamebot.json, key "SAY_EXCEPTIONS"
    if ctx.guild.id not in bot_information["SAY_EXCEPTIONS"]:
        return
    
    # When I run 2 instances of AlphaGameBot at the same time, both will reply to my message.
    # What it does is that if it is in a debug environment, it will ignore the command.  When testing,
    # I will just remove the `DEBUG=1` environment variable.
    if agb.cogwheel.isDebugEnv and not forcesay:
        logger.info("Say was ignored as I think this is a development build.")
        return EnvironmentError("Bot is in development build")
    
    if ctx.author.id != os.getenv("ALPHAGAMEBOT_OWNER_ID", 420052952686919690) and not global_say_enabled:
        logger.warning("%s tried to make me say \"%s\", but I successfully ignored it.".format(ctx.author.name,
                                                                                               ctx.content))
        return

    text = ctx.content[len(say_trigger):].strip()
    logger.debug("handleOnMessage: say: Final text cut is \"%s\"", text)
    
    # Put in the console that it was told to say something!
    logger.info("I was told to say: \"%s\"." % text)
    await ctx.channel.send(text)

    # Delete the original message, so it looks better in the application!
    await ctx.delete()
