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
import agb.requestHandler
import logging
import agb.cogwheel

class xkcdCog(agb.cogwheel.Cogwheel):
    @commands.slash_command(name="xkcd", description="XKCD Integrations in Discord!")
    async def _xkcd(self, interaction,
                      recent: discord.Option(bool, description="Get the most recent XKCD comic", required=False, default=False), # type: ignore
                      number: discord.Option(int, description="The ID of the desired XKCD comic", required=False, default=None)): # type: ignore
        
        # Get the current XKCD comic!
        current = self.getComic()[0]
        if not number and recent == False:
            # if no number is given, do random
            # Get some random xkcd comic
            print((1, current["num"]))
            number = random.randint(1, current["num"])
            xkcd = self.getComic(number)[0]

        elif recent == True:
            # Pass most recent XKCD along (current)
            # Note: yes, i could do current[:] but it is read-only
            # so that would be pretty-useless (and memory-intensive)
            # to do so! (Kinda like a linux symlink when i think about it ☻)
            xkcd = current
            number = xkcd["num"]
        else:
            # Check if the number is under zero, I found that this was (quite) problematic!
            if number < 0:
                await interaction.response.send_message(":x: You know, these comics don't go into the negatives... That'd be weird!")
                return
            if number > current["num"]:
                await interaction.response.send_message(":x: XKCD number does not exist.  Currently, the highest value is {}!".format(current["num"]))
                return
            comic = self.getComic(number)
            xkcd = comic[0]
            request = comic[1] # requests object
            if request.status_code == 404:
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


    def getComic(self, num: int = None) -> list:
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
