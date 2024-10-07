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
from discord.ext import commands
import logging
import agb.system.cogwheel
import time
from agb.system.requestHandler import handler
from mysql.connector import connection

with open("assets/dms_announcemment_template.txt", "r") as f:
    announcement_template = f.read()

def render_announcement_template(text: str) -> str:
    return announcement_template.format(content=text, time=int(time.time()))

async def blast_announcement(
        bot: commands.Bot,
        cnx: connection.MySQLConnection,
        CAN_USE_DATABASE: bool,
        dry_run: bool = False) -> str | None:
    """Blasts an announcement to DM to all users *who have opted in*"""    
    if not CAN_USE_DATABASE: return

    cursor = cnx.cursor()
    logger = logging.getLogger("system")

    text = handler.get(
        agb.system.cogwheel.getBotInformation()["ANNOUNCEMENT_URL"],
        attemptCache=False).text
    
    cursor.execute("SELECT userid FROM user_settings WHERE announcements = 1")
    db_users = cursor.fetchall()

    errNotFound = 0
    errForbidden = 0

    rendered_text = render_announcement_template(text)

    for user_id in db_users:
        _id = user_id[0]
        logger.debug(_id)
        user = await bot.fetch_user(_id)
        if user is None:
            errNotFound += 1
            logger.warning("blast_announcement: User %s is none (What o_0)", _id)
            continue
        try:
            if dry_run:
                logger.info("blast_announcement: Dry run, not sending message to user %s", _id)
                continue
            dm = await user.create_dm()
            await dm.send(rendered_text)
        except discord.Forbidden:
            logger.warning("blast_announcement: Can't send message to user %s (Forbidden)", user_id)
    
    return """## Announcement Blast Results
Results of the announcement blast: **{status}**
Users Sent To (Total): {total}
Users Not Found: {notfound}
Users Forbidden: {forbidden}
""".format(total=len(db_users), notfound=errNotFound, forbidden=errForbidden, status="Dry Run" if dry_run else "Complete")