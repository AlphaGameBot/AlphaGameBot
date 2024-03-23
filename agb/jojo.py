import discord
from discord.ext import commands
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
    async def _jojocharacter(self, interaction: discord.Interaction):
        r = requestHandler.handler.get("https://stand-by-me.herokuapp.com/api/v1/characters")
        j = json.loads(r.text)

        character = random.choice(j)

        embed = discord.Embed(title=character["name"], description=character["catchphrase"])

        image = "https://jojos-bizarre-api.netlify.app/assets/{}".format(character["image"])
        print(image)
        embed.set_image(url=image)

        await interaction.response.send_message(embed=embed)