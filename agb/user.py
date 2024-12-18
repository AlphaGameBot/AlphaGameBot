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

import agb.system.cogwheel
import discord
import time
import uuid
from discord.ext import commands
from mysql.connector import OperationalError

class UserStatsCog(agb.system.cogwheel.MySQLEnabledCogwheel):
    group = discord.SlashCommandGroup(name="user", description="user-related commands")
    @group.command(name="stats", description="Get user stats")
    async def _userstats(self, interaction: discord.commands.context.ApplicationContext,
                         user: discord.Option(discord.User, "User to get stats for", required=False)): # type: ignore
        await interaction.response.defer()
        
        # note, if using agb.cogwheel.MySQLEnabledCogwheel, BE SURE TO INCLUDE THIS CHECK
        if not await self.verifyDatabaseUtility(interaction, True):
            return

        if not user:
            user = interaction.user

        if not agb.system.cogwheel.getUserSetting(self.cnx, user.id, "message_tracking_consent"):
            await interaction.followup.send(":x: This user has not consented to message tracking.")
            return

        if user.bot:
            await interaction.followup.send(":x: This user is a bot.  Support for bot tracking *may* be added in the future.")
            return
            
        c = self.cnx.cursor()

        c.execute("SELECT user_level, points, messages_sent, commands_ran from guild_user_stats WHERE userid = %s AND guildid = %s", [user.id, interaction.guild.id])
        level, points, messages_sent, commands_ran = c.fetchone()

        self.logger.debug(c.statement)
        username = user.name
        nick = user.nick

        if nick != None:
            presented_username = "%s (%s)".format(nick, username)
        else:
            presented_username = "{0}".format(username)
        
        embed = agb.system.cogwheel.embed(
            title=presented_username
        )

        embed.add_field(name="Messages Sent", value=messages_sent)
        embed.add_field(name="Commands Ran", value=commands_ran)
        embed.add_field(name="Level", value=level)
        embed.add_field(name="Points", value=points)

        await interaction.followup.send(embed=embed)

    @group.command(name="settings", description="User Settings Web Interface")
    async def _settings(self, interaction: discord.context.ApplicationContext):
        if not await self.verifyDatabaseUtility(interaction, False):
            return
        
        c = self.cnx.cursor()
        # create a token
        expires = int(time.time()) + 3600 # 1 hour
        token = str(uuid.uuid4())
        c.execute("INSERT INTO webui_tokens VALUES (%s, %s, %s, %s, %s)", [interaction.user.id, interaction.guild.id, token, time.time(), "USER_SETTINGS"])
        c.close()

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="User Settings", url=f"{agb.system.cogwheel.getAPIEndpoint('webui', 'USER_SETTINGS')}?token={token}"))

        await interaction.response.send_message("Here is your WebUI link.\n-# Do NOT share it with anyone, as it will let them change your user settings!", view=view, ephemeral=True)

    @group.command(name="level", description="Get user level")
    async def _userlevel(self, interaction: discord.commands.context.ApplicationContext,
                         user: discord.Option(discord.User, "User to get level for", required=False)): # type: ignore
        await interaction.response.defer()

        if not await self.verifyDatabaseUtility(interaction, True):
            return
        
        if not user:
            user = interaction.user

        if not agb.system.cogwheel.getUserSetting(self.cnx, user.id, "message_tracking_consent"):
            await interaction.followup.send(":x: This user has not consented to message tracking.")
            return

        if user.bot:
            await interaction.followup.send(":x: This user is a bot.")
            return

        c = self.cnx.cursor()
        c.execute("SELECT user_level from guild_user_stats WHERE userid = %s AND guildid = %s", [user.id, interaction.guild.id])

        try:
            level = c.fetchone()[0]
        except TypeError:
            await interaction.followup.send(":x: I cannot find that user... they might have not sent any messages yet."
                                            "\n-# If you're sure they have, then make a [bug report](https://github.com/AlphaGameDeveloper/AlphaGameBot/issues/new/choose)!")
            return
        
        self.logger.debug(c.statement)


        await interaction.followup.send(f"{user.mention}'s level is **{level}**!")