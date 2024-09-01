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
import agb.system.requestHandler
import logging
import agb.cogwheel

class MemesCog(agb.cogwheel.Cogwheel):

    @commands.slash_command(name="meme", description="Get a meme from reddit!  (Where best memes come from)")
    async def meme(self, interaction: discord.context.ApplicationContext, 
                   subreddit: discord.Option(str, description="The subreddit that you want to get a meme from", default=None, required=False)): # type: ignore
        # get the meme from the memes api
        if subreddit == None:
            endpoint = agb.cogwheel.getAPIEndpoint("meme", "GET_MEME")
        else:
            endpoint = agb.cogwheel.getAPIEndpoint("meme", "GET_MEME_BY_SUBREDDIT").format(subreddit)
            
        r = agb.system.requestHandler.handler.get(endpoint, attemptCache=False)
        d = json.loads(r.text)
        if r.status_code != 200:
            await interaction.response.send_message(":x: `%s`" % d["message"])
            return
        if d["nsfw"] and not interaction.channel.nsfw:
            self.logger.debug("Rejecting this meme because it is a NSFW meme sent in a non-age-restricted channel.")
            await interaction.response.send_message(":x: NSFW memes can only be sent in NSFW channels.")
            return
        embed = agb.cogwheel.embed(title=d["title"])
        embed.set_footer(text="Sent in r/{0} by u/{1}".format(d["subreddit"], d["author"]))
        embed.set_image(url=d["preview"][len(d["preview"])-1])
        
        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="helloworld", description="It's industry standard, right?")
    async def hworld(self, interaction):
        await interaction.response.send_message(":earth_americas: Hello, World!")
