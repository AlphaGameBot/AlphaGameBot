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

import mysql.connector
import logging

def handleDatabaseUpdate(cnx: mysql.connector.MySQLConnection, CAN_USE_DATABASE: bool):
    l = logging.getLogger("system")
    if not CAN_USE_DATABASE:
        l.debug("handleDatabaseUpdate: Database is not enabled... Skipping the task.")
        return        
    # Get the latest database data, and current DB writes
    # will be written to the DB.  Makes the bot less loud with
    # DB usage.

    # NOTE - 6.24.2024
    # ================

    # This is *not* a good way to handle database updates, or rather, database
    # writes.  The reason is that this function is called periodically is that
    # we can GET the latest data from the database.  This isn't intended to do writes.

    # please make a pr if you know a way to improve it.
    if cnx.is_connected() == False:
        l.debug("handleDatabaseUpdate: Connection is not open.  Reconnecting.")
        cnx.reconnect()
    cnx.commit()

    
