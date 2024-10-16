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

from discord.ext import commands
import discord
import json
import random
import requests
import agb.requestHandler
import logging
import agb.cogwheel

class xkcdCog(agb.cogwheel.Cogwheel):
    group = discord.SlashCommandGroup(name = "xkcd",
                                      description = "XKCD Integrations in Discord!")
    
    @group.command(name="recent", description="Get the most recent XKCD comic")
    async def _recent(self, interaction: discord.context.ApplicationContext):
        await interaction.response.defer()

        current, request = self.getComic()
        
        embed = self.makeEmbedFromXKCD(current)
        await interaction.followup.send(embed=embed)
    
    @group.command(name="random", description="Get a random XKCD comic")
    async def _random(self, interaction: discord.context.ApplicationContext):
        await interaction.response.defer()
        current = self.getComic()[0]

        number = random.randint(1, current["num"])
        xkcd = self.getComic(number)[0]
        embed = self.makeEmbedFromXKCD(xkcd)
        await interaction.followup.send(embed=embed)

    @group.command(name="number", description="Get a specific XKCD comic")
    async def _number(self, interaction: discord.context.ApplicationContext, number: int):
        await interaction.response.defer()

        current = self.getComic()[0]
        if number < 0:
            await interaction.response.send_message(":x: You know, these comics don't go into the negatives... That'd be weird!")
            return
        if number > current["num"]:
            await interaction.response.send_message(":x: XKCD number does not exist.  Currently, the most recent is {}!".format(current["num"]))
            return
        xkcd, request = self.getComic(number)
        
        if request.status_code == 404:
            await interaction.response.send_message(":x: Comic not found! (`HTTP/2 404: Not Found!`)")
            return
        embed = self.makeEmbedFromXKCD(xkcd)
        await interaction.followup.send(embed=embed)

    def getComic(self, 
                 num: int | None = None) -> list[dict, requests.models.Response]:
        self.logger.debug("Getting XKCD #{}".format(num if num != None else "CURRENT"))
        if num == None:
            url = agb.cogwheel.getAPIEndpoint("xkcd", "GET_CURRENT")
        else:
            url = agb.cogwheel.getAPIEndpoint("xkcd", "GET_SPECIFIC").format(num)

        response = agb.requestHandler.handler.get(url)
        if response.status_code == 200:
            xkcd = json.loads(response.text)
        else:
            # Response is not 200 OK, return empty dictionary because womp womp
            xkcd = {}
        return [xkcd, response]
    
    def makeEmbedFromXKCD(self, comic: dict) -> dict:
        embed = agb.cogwheel.Embed(title="#{0}: {1}".format(comic["num"], comic["safe_title"]),
                                   description="{1}".format(comic["num"], comic['alt']))
        embed.set_footer(text="XKCD #{0} - {1}/{2}/{3} - \"{4}\"".format(comic["num"],
                                                                         comic["month"],
                                                                         comic["day"],
                                                                         comic["year"],
                                                                         comic["safe_title"]))
        embed.set_image(url=comic['img'])
        return embed
