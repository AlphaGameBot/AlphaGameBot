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
import agb.system.cogwheel
import logging

async def handleApplicationCommandCompletion(interaction: discord.context.ApplicationContext,
                                             CAN_USE_DATABASE: bool,
                                             cnx):
    l = logging.getLogger("system")
    l.debug("handleApplicationCommandCompletion: Handling command /%s from %s",
            interaction.command.name,
            interaction.author.id)

    if not interaction.response.is_done():
        l.warning("handleApplicationCommandCompletion: No response was given for command /%s from %s.  That's a problem!",
                  interaction.command.name,
                  interaction.author.id)