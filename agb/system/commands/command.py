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
import agb.system.onboarding
import agb.system.leveling
import logging

async def handleApplicationCommand(interaction: discord.context.ApplicationContext, CAN_USE_DATABASE, cnx, tracking):
    l = logging.getLogger("system")
    l.debug("handleApplicationCommand: Handling command /{0} from {1}".format(interaction.command.name, interaction.author.id))
    if CAN_USE_DATABASE and tracking:
        # attempt to make a new user if not already in the database
        agb.system.onboarding.initializeNewUser(cnx, CAN_USE_DATABASE, interaction.author.id, interaction.guild.id)

        if agb.system.cogwheel.getUserSetting(cnx, interaction.author.id, "message_tracking_consent") == 1:
            await agb.system.leveling.countPoints(interaction, cnx, agb.system.leveling.CountingEvent.COMMAND, CAN_USE_DATABASE, tracking)
        else:
            l.debug("Not tracking command usage for /{0} because user {1} has not consented to message tracking.".format(interaction.command.name, interaction.author.id))
