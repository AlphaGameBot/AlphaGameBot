import logging

from discord.ext import commands
import discord
import json
import random
import agb.requestHandler
import logging
import agb.cogwheel

class xkcdCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("xkcdCog has been initalized!")

    @commands.slash_command(name="xkcd", description="Get a random XKCD :)")
    async def _random(self, interaction, number:int=None):
        cur = self.getComic()[0]
        r = range(1, cur["num"])
        if not number:
            # if no number is given, do random
            number = random.choice(r)
            xkcd = self.getComic(number)[0]

        else:
            comic = self.getComic(number)
            xkcd = comic[0]
            request = comic[1] # requests object
            if request.status_code == 404:
                self.logger.error("404 error >:(")
                await interaction.response.send_message(":x: Comic not found! (`HTTP/2 404: Not Found!`)")
                return
        embed = agb.cogwheel.Embed(title="#{0}: {1}".format(number, xkcd["safe_title"]),
                                   description="{1}".format(number, xkcd['alt']))
        embed.set_footer(text="XKCD #{0} - {1}/{2}/{3} - \"{4}\"".format(number,
                                                                         xkcd["month"],
                                                                         xkcd["day"],
                                                                         xkcd["year"],
                                                                         xkcd["safe_title"]))
        embed.set_image(url=xkcd['img'])
        await interaction.response.send_message(embed=embed)


    def getComic(self, num: int = None):
        self.logger.debug("Getting XKCD #{}".format(num if num != None else "CURRENT"))
        if num == None:
            u = agb.cogwheel.getAPIEndpoint("xkcd", "GET_CURRENT")
        else:
            u = agb.cogwheel.getAPIEndpoint("xkcd", "GET_SPECIFIC").format(num)

        r = agb.requestHandler.handler.get(u)
        return [json.loads(r.text), r]
