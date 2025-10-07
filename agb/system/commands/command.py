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
import agb.system.onboarding
import agb.system.cogwheel
import agb.system.leveling
import logging
import time

async def handleApplicationCommand(interaction: discord.context.ApplicationContext, CAN_USE_DATABASE, cnx, tracking, prometheus_exporter=None):
    l = logging.getLogger("system")
    start_time = time.time()
    
    command_name = interaction.command.name if interaction.command else "unknown"
    l.debug("handleApplicationCommand: Handling command /{0} from {1}".format(command_name, interaction.author.id))
    
    try:
        if CAN_USE_DATABASE and tracking:
            # attempt to make a new user if not already in the database
            await agb.system.onboarding.initializeNewUser(cnx, CAN_USE_DATABASE, interaction.author.id, interaction.guild.id)

            if agb.system.cogwheel.getUserSetting(cnx, interaction.author.id, "message_tracking_consent") == 1:
                await agb.system.leveling.countPoints(interaction, cnx, agb.system.leveling.CountingEvent.COMMAND, CAN_USE_DATABASE, tracking)
            else:
                l.debug("Not tracking command usage for /{0} because user {1} has not consented to message tracking.".format(command_name, interaction.author.id))

        
        notification = "**[Command]** /{0}".format(command_name)
        data = interaction.interaction.to_dict()

        arguments = ""
        for x in data["data"].get("options", []):
            rtype = type(x["value"])
            if isinstance(x["value"], bool):
                rtype = "Boolean"
            elif isinstance(x["value"], int):
                rtype = "Integer"
            elif isinstance(x["value"], str):
                rtype = "String"
            else:
                rtype = type(x["value"]).__name__
            
            arguments = arguments + "* `{0}: {1}` (Type: `{2}`)\n".format(x["name"], x["value"], rtype)

        notification += "\n**[Arguments]**\n{0}".format(arguments)
        agb.system.cogwheel.webhook(notification)
        
    except Exception as e:
        l.error("Error in handleApplicationCommand: %s", e)
        if prometheus_exporter:
            prometheus_exporter.track_error("command_handler_error")
    finally:
        # Track command execution metrics
        if prometheus_exporter:
            execution_time = time.time() - start_time
            try:
                prometheus_exporter.track_command_execution(
                    command_name=command_name,
                    execution_time=execution_time,
                    user_id=interaction.author.id if interaction.author else None
                )
            except Exception as e:
                l.warning("Failed to track command metrics: %s", e)