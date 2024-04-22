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
from discord import Permissions
import logging

import agb.cogwheel


class ModerationCog(agb.cogwheel.Cogwheel):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("ModerationCog has been initalized!")
    
    group = discord.SlashCommandGroup(name="moderation", description="Moderation-related commands")

    @group.command(name="kick", description="Kicks a user.")
    @commands.has_permissions(kick_members = True)
    async def _kick(self, interaction, user: discord.Option(discord.Member, description="User to kick", required=True), 
                  reason: discord.Option(str, description="Reason for ban", required=True)):
        
        await user.kick(reason = reason)
        
        embed = discord.Embed(
        title="User Kicked",
        description="The user " + str(user) + " has been kicked from the server.",
        color=discord.Colour.red(),
        )
        embed.set_footer(text="Reason: " + reason)

        await interaction.response.send_message(embed=embed)

    @group.command(name="ban", description="Ban a user!")
    @commands.has_permissions(ban_members=True)
    async def _ban(self, interaction,
            user: discord.Option(discord.Member, description="The user to ban"),
            reason: discord.Option(str, description="The reason for the ban", required=False, default="No Reason Given")):
        await user.ban(reason=reason)
        embed = discord.Embed(
        title="User Kicked",
        description="The user " + str(user) + " has been kicked from the server.",
        color=discord.Colour.red(),
        )
        embed.set_footer(text="Reason: " + reason)

        await interaction.response.send_message(embed=embed)
    
    @_kick.error
    @_ban.error
    async def _error(self, interaction, error):
        if isinstance(error, discord.Forbidden):
            await interaction.response.send_message(":x: The bot does not have sufficient permissions to do that.")
            return
        elif isinstance(error, discord.MissingPermissions):
            await interaction.response.send_message(":x: Sorry, but you don't have sufficient permissions to do that!")
            return
        else: # what the junk is this error?  pass it on to global bot handler
            raise error