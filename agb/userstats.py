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

import agb.cogwheel
import discord
from discord.ext import commands

class UserStatsCog(agb.cogwheel.MySQLEnabledCogwheel):
    @commands.slash_command(name="userstats", description="Get user stats")
    async def _userstats(self, interaction: discord.commands.context.ApplicationContext):
        # note, if using agb.cogwheel.MySQLEnabledCogwheel, BE SURE TO INCLUDE THIS CHECK
        if not self.canUseDatabase:
            await interaction.response.send_message(":x: Database is not enabled.  This command cannot be used.")
            return

        c = self.cnx.cursor()

        c.execute("SELECT messages_sent, commands_ran from user_stats WHERE userid = %s", [interaction.user.id])


        user = interaction.user.name
        nick = interaction.user.nick

        if nick != None:
            presented_username = "{0} ({1})".format(nick, user)
        else:
            presented_username = "{0}".format(user)
        
        (messages_sent, commands_ran) = c.fetchall()[0]
        embed = agb.cogwheel.embed(
            title=presented_username
        )

        embed.add_field(name="Messages Sent", value=messages_sent)
        embed.add_field(name="Commands Ran", value=commands_ran)

        await interaction.response.send_message(embed=embed)