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

import json
import discord
from discord.ext import commands
import agb.requestHandler
import logging
import agb.cogwheel

class MemesCog(agb.cogwheel.Cogwheel):

    @commands.slash_command(name="meme", description="Get a meme from reddit!  (Where best memes come from)")
    async def meme(self, interaction):
        # get the meme from the memes api
        endpoint = agb.cogwheel.getAPIEndpoint("meme", "GET_MEME")
        r = agb.requestHandler.handler.get(endpoint, attemptCache=False)
        d = json.loads(r.text)
        embed = discord.Embed(title=d["title"], description="Subreddit: r/{0}".format(d["subreddit"]))
        embed.set_footer(text="By: u/{}".format(d["author"]))
        i = d["preview"][len(d["preview"])-1]
        embed.set_image(url=i)
        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="helloworld", description="It's industry standard, right?")
    async def hworld(self, interaction):
        await interaction.response.send_message(":earth_americas: Hello, World!")