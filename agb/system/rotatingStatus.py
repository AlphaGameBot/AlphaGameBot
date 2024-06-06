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

BOT_STATUS_INDEX = 0
async def rotatingStatus(bot: commands.Bot):
    botinfo = agb.cogwheel.getBotInformation()
    

    for status in botinfo["ROTATING_STATUS"]:
        # get user count
        usercount = 0
        for user in bot.users:
            if not user.bot:
                usercount += 1
        status = status.format( # to allow for placeholders in the status
            version=agb.cogwheel.getVersion(), 
            build=os.getenv("BUILD_NUMBER"), 
            guilds=len(bot.guilds),
            users=usercount
        )
        await bot.change_presence(activity=discord.Game(name=status))
        await asyncio.sleep(botinfo["ROTATING_STATUS_INTERVAL"])