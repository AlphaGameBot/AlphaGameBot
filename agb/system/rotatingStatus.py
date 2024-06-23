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

from discord.ext import commands
import discord
import asyncio
import agb.cogwheel
import os
import logging

async def rotatingStatus(bot: commands.Bot, cnx, CAN_USE_DATABASE: bool):
    logger = logging.getLogger("system")
    botinfo = agb.cogwheel.getBotInformation()
    
    # We will have a format for all of the statuses, in JSON form being:
    #{
    #   "type": "PLAYING", (can be PLAYING, LISTENING or WATCHING)
    #   "status": "a super fun game!",
    #}
    if CAN_USE_DATABASE:
        c = cnx.cursor()
        c.execute("SELECT COUNT(*) FROM user_settings")
        usercount = c.fetchone()[0]
        c.close()
    else:
        usercount = 0
        for user in bot.get_all_members():
            if user.bot:
                continue
            usercount += 1
    
    logger.debug(f"Got user count of {usercount}.")

    
    for status in botinfo["ROTATING_STATUS"]:
        # get user count
        
        activity = discord.ActivityType.unknown
        if status["type"] == "PLAYING":
            activity = discord.ActivityType.playing
        elif status["type"] == "LISTENING":
            activity = discord.ActivityType.listening
        elif status["type"] == "WATCHING":
            activity = discord.ActivityType.watching
        elif status["type"] == "STREAMING":
            logger.warning("STREAMING is unsupported.  Please use WATCHING instead. (defaulting to WATCHING)")
            activity = discord.ActivityType.watching
        else:
            logger.error(f"Unknown status type: {status['type']}.  Skipping this status.  Please check your configuration.")
            continue

        # get the inteded bot status (idle, online, dnd, etc)
        if botinfo["STATUS"] == "idle":
            online_status = discord.Status.idle
        elif botinfo["STATUS"] == "dnd":
            online_status = discord.Status.dnd
        elif botinfo["STATUS"] == "offline":
            online_status = discord.Status.offline
        elif botinfo["STATUS"] == "online":
            online_status = discord.Status.online
        else:
            logger.error(f"Unknown online status type: {botinfo['STATUS']}.  Defaulting to online.")
            online_status = discord.Status.online
        status = status["status"].format( # to allow for placeholders in the status
            version=agb.cogwheel.getVersion(), 
            build=os.getenv("BUILD_NUMBER"), 
            guilds=len(bot.guilds),
            users=usercount,
            commands=len(bot.application_commands)
        )

        real_activity = discord.Activity(type=activity, name=status)
        await bot.change_presence(activity=real_activity, status=online_status)
        await asyncio.sleep(botinfo["ROTATING_STATUS_INTERVAL"])