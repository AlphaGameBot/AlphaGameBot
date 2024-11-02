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

import logging
from mysql.connector import connection

async def initializeNewUser(cnx: connection.MySQLConnection,
                           CAN_USE_DATABASE: bool,
                           user_id: int, 
                           guild_id: int = None):
    """This function will initialize a new user in the database.
    
    Args:
        cnx (connection.MySQLConnection): The database connection.
        CAN_USE_DATABASE (bool): Whether or not the database is enabled.
        user_id (int): The user ID.
        guild_id (int): The guild/server ID."""
    if not CAN_USE_DATABASE: return
    if cnx is None: return
    
    logger = logging.getLogger("cogwheel")

    try:

        rows_affected = 0 # rows changed
        cursor = cnx.cursor()
        
        logger.debug("Attempting to run onboarding routine...")    

        if guild_id:
            # Guild User Stats
            cursor.execute("INSERT INTO guild_user_stats (userid, guildid) SELECT %s AS userid, %s AS guildid WHERE NOT EXISTS (SELECT 1 FROM guild_user_stats WHERE userid = %s AND guildid = %s);", [
                user_id,
                guild_id,
                user_id,
                guild_id
            ])
            
            rows_affected += cursor.rowcount

        # Global User Stats
        cursor.execute("INSERT INTO user_stats (userid) SELECT %s AS userid WHERE NOT EXISTS (SELECT 1 FROM user_stats WHERE userid = %s);", [user_id, user_id])
        rows_affected += cursor.rowcount

        # User Settings (other values are defaulted so we only )
        cursor.execute("INSERT INTO user_settings (userid) SELECT %s AS userid WHERE NOT EXISTS (SELECT 1 FROM user_settings WHERE userid = %s);", [user_id, user_id])
        rows_affected += cursor.rowcount

        logger.debug("%s rows affected", rows_affected)

        cursor.close()    
        cnx.commit()
    except Exception as e:
        logger.error("Error in onboarding routine: %s", e)
        cnx.rollback()
        raise e
