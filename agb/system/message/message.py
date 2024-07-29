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
import agb.system.message.onboarding
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
                          forcesay: bool):
    orc = ctx.content
    bot_information = agb.cogwheel.getBotInformation()
    logger = logging.getLogger("system")
    bot_mention_string = bot.user.mention
    isSay = False
    isSay = ctx.content.startswith(bot_mention_string)
    ctx.content = ctx.content.strip(bot_mention_string).strip()
    if tracking:
        if isSay:
            logger.debug("Recieved 'say' message: (original: %s, valuetosay: %s, isSay: %s)" % (orc, ctx.content, isSay))
        if ctx.author.bot:
            logger.debug("handleOnMessage: ignoring messages sent by bots. (id: {0}, userid: {1})".format(ctx.id, ctx.author.id))
            return
        
        # Fire the messageLevelUp -> In another file to be more organized (ME? ORGANIZED? INSANE!!)
        await agb.system.message.onboarding.initalizeNewUser(cnx, ctx.author.id, ctx.guild.id)
        await agb.system.message.counting.countMessage(ctx, cnx, CAN_USE_DATABASE, tracking)
        await agb.system.message.leveling.handleMessageLevelUp(ctx, cnx, CAN_USE_DATABASE, tracking)
        
    else:
        logging.debug("handleOnMessage: Not tracking message count because CAN_USE_DATABASE is False or tracking is False.")

    if ctx.content.startswith("..") == False and not isSay:
        return
    if ctx.content.startswith("...") == True: 
        # Sometimes, I make sarcastic comments, starting with ...
        # Example: "... blah blah blah", and the bot responds to it as
        # ". blah blah blah".  This prevents the bot from responding.
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
    
    if ctx.author.id != os.getenv("ALPHAGAMEBOT_OWNER_ID", 420052952686919690):
        logger.warning("{0} tried to make me say \"{1}\", but I successfully ignored it.".format(ctx.author.name,
                                                                                               ctx.content))
#        await ctx.reply("> \"You can go fuck yourself with that!\", Brewstew, *Devil Chip*")
        return

    text = ctx.content
    if not isSay:
        text = text[2:]
    if text == None:
        # No text given, so give up...
        return
    
    # Put in the console that it was told to say something!
    logger.info("I was told to say: \"%s\"." % text)
    await ctx.channel.send(text)

    # Delete the original message, so it looks better in the application!
    await ctx.delete()
