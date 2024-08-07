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

from mysql.connector import connection
import discord

async def countMessage(
                       ctx: discord.Message,
                       cnx: connection.MySQLConnection | None,

                       CAN_USE_DATABASE: bool,
                       CAN_DO_TRACKING:  bool) -> int:
    """This function is responsible for counting messages for the given user.

    This function is ran once every message, called by `agb.system.message.message`, which in
    turn is ran by the Pycord `on_message` event.

    This function should only run given two conditions are True, as the function will exit without
    doing anything and return failure (1) in a bad state.  The two conditions are:
        (1) The database connection is availiable (`CAN_USE_DATABASE`)
        (2) Tracking is enabled (`CAN_DO_TRACKING`)

    This function also assumes that the user has been initialized into the database, so ensure that
    this condition is met, as it is difficult to check for it reliably in the function.
    """
    # Check if this function should even be called in the first place!
    if not CAN_USE_DATABASE: return 1
    if not CAN_DO_TRACKING:  return 1

    cursor = cnx.cursor()

    user_id = ctx.author.id
    guild_id = ctx.guild.id
    # Update the user_stats table
    cursor.execute("UPDATE user_stats SET commands_ran = commands_ran + 1 WHERE userid = %s;", [user_id])

    # Update the guild_user_stats (Guild-specific user stats) table
    cursor.execute("UPDATE guild_user_stats SET messages_sent = messages_sent + 1 WHERE userid = %s AND guildid = %s;", (user_id, guild_id))

    cursor.close()
    cnx.commit()
    
    return 0
