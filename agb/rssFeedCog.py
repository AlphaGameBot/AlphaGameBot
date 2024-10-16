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
import requests.exceptions

import agb.cogwheel
import agb.requestHandler
import feedparser
import re
from discord.ext import commands


class RSSFeedCog(agb.cogwheel.Cogwheel):
    def cleanString(self, text):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    @commands.slash_command(name="rss", description="Reed a site's RSS feed")
    async def _rss(self, interaction: discord.commands.context.ApplicationContext,
                   feed: discord.Option(str, description="The Location of the RSS feed")): # type: ignore
        # acknowledge Discord's request for the slash command!
        # This gives us some breathing room with the 3-second
        # "Command timed out".  This also gives the "AlphaGameBor
        # is thinking" message in Discord.
        await interaction.response.defer()

        # We need to have exception handling for the request because
        # it uses a user-supplied url, which can have errors!
        try:
            request = agb.requestHandler.handler.get(feed)
        except requests.exceptions.MissingSchema as e:
            await interaction.followup.send(":x: No schema set!  You must set the url to have either `http://` or `https://`")
            return e

        fp = feedparser.parse(request.text)
        embed = agb.cogwheel.embed(title=self.cleanString(fp.feed.title),
                                   description=self.cleanString(fp.feed.description))
        for a in fp.entries:
            s = a.summary[:1000]
            self.logger.debug("Length is {0}.  This should be under 1024!".format(len(s)))
            embed.add_field(name=a.title, value="[LINK](%s)" % a.link)
        await interaction.followup.send(embed=embed)
