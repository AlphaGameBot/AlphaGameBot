import logging
from mysql.connector import connection

async def initalizeNewUser(cnx: connection.MySQLConnection,
                           CAN_USE_DATABASE: bool,
                           user_id: int, 
                           guild_id: int = None):
    l = logging.getLogger("cogwheel")

    rc = 0 # rows changed
    c = cnx.cursor()
    
    l.debug("Attempting to run onboarding routine...")    

    if guild_id:
        # Guild User Stats
        c.execute("INSERT INTO guild_user_stats (userid, guildid) SELECT %s AS userid, %s AS guildid WHERE NOT EXISTS (SELECT 1 FROM guild_user_stats WHERE userid = %s AND guildid = %s);", [
        user_id,
        guild_id,
        user_id,
        guild_id])
        
        rc += c.rowcount

    # Global User Stats
    c.execute("INSERT INTO user_stats (userid) SELECT %s AS userid WHERE NOT EXISTS (SELECT 1 FROM user_stats WHERE userid = %s);", [user_id, user_id])
    rc += c.rowcount

    # User Settings (other values are defaulted)
    c.execute("INSERT INTO user_settings (userid) SELECT %s AS userid WHERE NOT EXISTS (SELECT 1 FROM user_settings WHERE userid = %s);", [user_id, user_id])
    rc += c.rowcount

    l.debug("%s rows affected", rc)

    c.close()    
    cnx.commit()
