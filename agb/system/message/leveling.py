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

import discord
import agb.cogwheel
import json
import logging
from mysql.connector import (connection)

global levels
with open("assets/levels.json", "r") as f:
    levels = json.load(f)["levels"]
    
def get_level_from_message_count(messages: int) -> int:
    levelNumber = 0 # to show errors in the code, we set a value that will 100% be overwritten
    for level in reversed(levels):
        if level["messages_required"] > messages:
            continue
        else:
            levelNumber = level["level"]
            logging.getLogger('system').debug("get_level_from_message_count: Level %s (Requirement %s), Messages %s" % (
                                                levelNumber, 
                                                level["messages_required"],
                                                messages)
                                             )
            break
            
    return levelNumber

async def handleMessageLevelUp( ctx: discord.Message,
                                cnx: connection.MySQLConnection | None,
                                CAN_USE_DATABASE: bool,
                                CAN_DO_TRACKING: bool) -> None:
    # This function assumes that the message counter was invoked.

    # We need the database, and if none, game over :(
    if not CAN_USE_DATABASE: return

    # We also need the ability to track messages...
    if not CAN_DO_TRACKING: return
    
    # Load the levels in
    # 'levels' is an iterable of dict, with structure
        # [{"level": int, "messages_required": int}, etc, etc, etc]
        
    logger = logging.getLogger('system')
    cursor = cnx.cursor()


    # Check if the leveling feature should be enabled in the first place
    cursor.execute("SELECT leveling_enabled FROM guild_settings WHERE guildid = %s", [ctx.guild.id])

    enabled = bool(cursor.fetchone()) # 1 or 0
    # 3.8.1: bug (fixed):
    #           The fact that ctx.guild.id was mistakenly set to
    #           ctx.id, the message ID, exposed a problem where
    #           it assumes that the guild disabled leveling
    #           (because None evaluates to False). This should
    #           not happen because agb.system.message.onboarding
    #           runs before this, and initializes everything in the
    #           database.
    if not enabled:
        logger.debug("handleMessageLevelUp: This guild has disabled leveling. (Got %s from database)", enabled)
        return
    # Get message count
    query = "SELECT messages_sent, user_level FROM guild_user_stats WHERE userid = %s AND guildid = %s;" % (ctx.author.id, ctx.guild.id)
    cursor.execute(query)

    data = cursor.fetchone()

    # Big fat bug, but I cannot seem to recreate it...  I am doing this
    # so I can do a proper fix later on!
    try:
        # This line has been causing some problems...
        messages, level = data  
    except Exception as e:
        logger.warning("Getting user leveling information failed.  Data: '%s', User: '%s', Guild: '%s', and the complete query was '%s'.  The error was `%s`.",
                       data,
                       ctx.author.id,
                       ctx.guild.id,
                       query,
                       repr(e))
        return

            
    # check if there is any change to the level
    c_level = get_level_from_message_count(messages)


    if c_level == level:
        # nothing to do!
        return

    # update level in DB
    cursor.execute("UPDATE guild_user_stats SET user_level = %s WHERE userid = %s AND guildid = %s", (c_level, ctx.author.id, ctx.guild.id))

    logger.debug("Current data is: (Calculated Level = %s, Database Level = %s, Rows Affected = %s)", c_level, level, cursor.rowcount)
        
    cnx.commit()    
    await ctx.reply(":tada: Congrats, %s, you just advanced to level **%s**!  Nice!" % (ctx.author.mention, c_level))
