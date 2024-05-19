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

import agb.cogwheel
from . import requestHandler
import json
import random
import logging

class JojoCog(agb.cogwheel.Cogwheel):

    @discord.slash_command(name="jojocharacter", description="Get a random JoJo's Bizarre Adventure character!")
    async def _jojocharacter(self, interaction):
        endpoint = agb.cogwheel.getAPIEndpoint("jojo", "GET_CHARACTERS")
        r = requestHandler.handler.get(endpoint)
        j = json.loads(r.text)
        character = random.choice(j)
        embed = discord.Embed(title=character["name"], description=character["catchphrase"])
        image = agb.cogwheel.getAPIEndpoint("jojo", "GET_CHARACTER_IMAGE").format(character["image"])
        embed.set_image(url=image)

        await interaction.response.send_message(embed=embed)