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
import agb.cogwheel

async def handleApplicationCommand(interaction: discord.context.ApplicationContext, CAN_USE_DATABASE, cnx):
    if not agb.cogwheel.getUserSetting(cnx, interaction.user.id, "message_tracking_consent"):
        await interaction.channel.send("not tracking commands because of consent settings owo")
    if CAN_USE_DATABASE:
        # attempt to make a new user if not already in the database
        agb.cogwheel.initalizeNewUser(cnx, interaction.author.id)

        # Increase the value of commands_ran by 1 for the given user id
        query = "UPDATE user_stats SET commands_ran = commands_ran + 1 WHERE userid = %s"
        values = [interaction.author.id]
        cursor = cnx.cursor()
        cursor.execute(query, values)
        cnx.commit()
        cursor.close()