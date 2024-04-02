import discord
from discord.ext import commands

import agb.cogwheel
from . import requestHandler
import json
import random
import logging

class JojoCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("JoJoCog has been initalized!")

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