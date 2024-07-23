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
import time
import uuid
import discord
from discord.ext import commands

class GuildCog(agb.cogwheel.MySQLEnabledCogwheel):
    group = discord.SlashCommandGroup(name="guild", description="Current Discord Server commands")

    @group.command(name="settings", description="d")
    @commands.has_permissions(administrator = True)
    async def _settings(self, interaction: discord.context.ApplicationContext):
        if not self.canUseDatabase:
            await interaction.response.send_message(":x: Database is not enabled.  This command cannot be used.")
            return
        
        c = self.cnx.cursor()
        # create a token
        expires = int(time.time()) + 3600 # 1 hour
        token = str(uuid.uuid4())
        c.execute("INSERT INTO webui_tokens VALUES (%s, %s, %s, %s, %s)", [interaction.user.id, interaction.guild.id, token, time.time(), "GUILD_SETTINGS"])
        c.close()

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Guild Settings", url=f"{agb.cogwheel.getAPIEndpoint('webui', 'GUILD_SETTINGS')}?token={token}"))

        await interaction.response.send_message("Here is your WebUI link.\n*(Do NOT share it with anyone, as it will let them change your server settings!)*", view=view, ephemeral=True)
