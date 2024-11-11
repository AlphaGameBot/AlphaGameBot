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
import logging
import agb.system.cogwheel
from os import getenv

async def handleSay(ctx: discord.Message,
                    forcesay: bool,
                    global_say_enabled: bool,
                    say_trigger: str | None = None) -> None:
    """This function handles the say command.  It is called every time a message is sent,
    however, it will only respond if the message is a say command.  It will then say the message,
    and delete the original message.
    
    Args:
        ctx (discord.Message): The context of the message.
        forcesay (bool): Whether or not to force the bot to enable say, regardless of the debug mode (This is really stupid, and will be removed in a future release.).
        global_say_enabled (bool): Whether or not the say command is enabled globally.
        say_trigger (str | None, optional): The trigger for the say command.  Defaults to None.
    """
    # Due to privileged intents, if you don't have the "Message Content" intent (or you weren't approved for it), you can't
    # get the content of the message.  This is a problem, as the say command relies on the content of the message.
    if not ctx.content: return

    logger = logging.getLogger("system")
    bot_information = agb.system.cogwheel.getBotInformation()

    
    if say_trigger is None:
        say_trigger = ctx.guild.me.mention
    
    say_prompted = ctx.content.startswith(say_trigger)

    if ctx.content.startswith(say_trigger) == False and not say_prompted:
        return

    # Disable the say command for all servers except for the ones in which they are explicitly
    # enabled in alphagamebot.json, key "SAY_EXCEPTIONS"
    if ctx.guild.id not in bot_information["SAY_EXCEPTIONS"]:
        return
    
    if agb.system.cogwheel.isDebugEnv and not forcesay:
        logger.info("Say was ignored as I think this is a development build.")
        return EnvironmentError("Bot is in development build")
    
    if ctx.author.id != getenv("ALPHAGAMEBOT_OWNER_ID", 420052952686919690) and not global_say_enabled:
        logger.warning("%s tried to make me say \"%s\", but I successfully ignored it.".format(ctx.author.name,
                                                                                               ctx.content))
        return

    text = ctx.content[len(say_trigger):].strip()
    logger.debug("handleOnMessage: say: Final text cut is \"%s\"", text)
    logger.info("I was told to say: \"%s\"." % text)
    
    # Check if the message is a reply (.. or a reference)
    if ctx.reference is not None:
        logger.debug("handleOnMessage: say: Message is a reply. (ctx.reference exists)")
        await ctx.reference.resolved.reply(text)
    else:
        await ctx.channel.send(text)

    # Delete the original message, so it looks better in the application!
    await ctx.delete()
