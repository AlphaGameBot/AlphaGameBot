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
import logging
from mysql.connector import (connection)

async def handleGuildAvailiable(ctx: discord.guild.Guild,
                                cnx: connection.MySQLConnection | None,
                                CAN_USE_DATABASE: bool):
    """Contains code that is executed when a new guild is seen by the bot.  This defaults some settings and other routines.

    No operations are taken if the row already exists in the database."""
    if not CAN_USE_DATABASE: return

    logger = logging.getLogger('system')
    cursor = cnx.cursor()
    rc = 0
    
    cursor.execute("INSERT INTO guild_settings (guildid) SELECT %s AS guildid FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM guild_settings WHERE guildid = %s);", (ctx.id, ctx.id))    
    rc += cursor.rowcount

    cursor.close()
    cnx.commit()
        
    logger.debug("handleGuildAvailiable: Guild Onboarding complete. Rows Affected: %s", rc)
    
    
