import logging

from discord.ext import commands
import discord
import json
import random
from . import requestHandler
import logging
from . import cogwheel

class xkcdCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("xkcdCog has been initalized!")

    @commands.slash_command(name="xkcd", description="Get a random XKCD :)")
    async def _random(self, interaction: discord.Interaction, number:int=None):
        cur = self.getComic()[0]
        r = range(1, cur["num"])
        if not number:
            # if no number is given, do random
            num = random.choice(r)
            xkcd = self.getComic(num)[0]

        else:
            comic = self.getComic(number)
            xkcd = comic[0]
            request = comic[1] # requests object
            if request.status_code == 404:
                self.logger.error("404 error >:(")
                await interaction.response.send_message(":x: Comic not found! (`HTTP/2 404: Not Found!`)")
                return
        embed = cogwheel.Embed(title="Random XKCD", description=xkcd['alt'])
        embed.set_image(url=xkcd['img'])
        await interaction.response.send_message(embed=embed)


    def getComic(self, num: int = None):
        self.logger.debug("Getting XKCD #{}".format(num if num != None else "CURRENT"))
        if num == None:
            u = "https://xkcd.com/info.0.json"
        else:
            u = "https://xkcd.com/{}/info.0.json".format(num)

        r = requestHandler.handler.get(u)
        return [json.loads(r.text), r]
