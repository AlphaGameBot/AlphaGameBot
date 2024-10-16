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
import datetime
import agb.cogwheel


class ModerationCog(agb.cogwheel.Cogwheel):
    group = discord.SlashCommandGroup(name="moderation", description="Moderation-related commands")

    @group.command(name="kick", description="Kicks a user.")
    @commands.has_permissions(kick_members = True)
    async def _kick(self, interaction, user: discord.Option(discord.Member, description="User to kick", required=True),  # type: ignore
                  reason: discord.Option(str, description="Reason for ban", required=False, default=None)): # type: ignore # type: ignore
        
        await user.kick(reason = reason) # reason will be None if not set
        await interaction.response.send_message(":white_check_mark:  {} has been kicked. {}".format(user.mention, "(Reason: *%s*)" % reason if reason else ""))


    @group.command(name="ban", description="Ban a user!")
    @commands.has_permissions(ban_members=True)
    async def _ban(self, interaction,
            user: discord.Option(discord.Member, description="The user to ban"), # type: ignore
            reason: discord.Option(str, description="The reason for the ban", required=False, default=None)): # type: ignore
        await user.ban(reason=reason)
        await interaction.response.send_message(":white_check_mark:  {} has been kicked. {}".format(user.mention, "(Reason: *%s*)" % reason if reason else ""))


    @group.command(name="purge", description="Purges a certain number of messages from a channel")
    @commands.has_permissions(manage_messages = True)
    @commands.has_permissions(read_message_history = True)
    async def _purge(self, interaction: discord.ApplicationContext,
                     number: discord.Option(int, description="Maximum number of messages to purge.")): # type: ignore
        await interaction.channel.purge(limit=number)
        await interaction.response.send_message(":white_check_mark:  Purged **{}** messages.".format(number))
        
    @group.command(name="timeout", description="Timeout a user.")
    @commands.has_permissions(moderate_members=True)
    async def _timeout(self, interaction: discord.ApplicationContext,
                        user: discord.Option(discord.Member, description="User to timeout."), # type: ignore
                        minutes: discord.Option(int, description="Time (in minutes) to time-out the user..", default=5)): # type: ignore
        await user.timeout_for(datetime.timedelta(minutes=minutes))
        await interaction.response.send_message(":white_check_mark:  {} has been put on timeout.".format(user.mention))
        
    @group.command(name="untimeout", description="Removes a timeout from a user.")
    @commands.has_permissions(moderate_members=True)
    async def _untimeout(self, interaction: discord.ApplicationContext, 
                         user: discord.Option(discord.Member, description="User to remove timeout from.", required=True)): # type: ignore
        await user.remove_timeout()
        await interaction.response.send_message(":white_check_mark:  {}'s timeout has been removed.".format(user.mention))
