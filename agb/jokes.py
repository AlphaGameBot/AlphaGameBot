import logging

import discord
from discord.ext import commands
import agb.requestHandler
import json
from nltk.corpus import words
import random

class jokesCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("jokesCog has been initalized.")

    @commands.slash_command(name="joke", description="I'm so funny, right?")
    async def _joke(self, interaction: discord.Interaction):
        r = agb.requestHandler.handler.get("https://official-joke-api.appspot.com/random_joke", attemptCache=False)
        joke = json.loads(r.text)

        embed = discord.Embed(title="Joke #{}".format(joke["id"]), description="{0}\n{1}".format(joke["setup"], joke["punchline"]))
        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="wisdom", description="Get a word of wisdom")
    async def _wisdom(self, interaction: discord.Interaction):
        await interaction.response.send_message(random.choice(words()))

    @commands.slash_command(name="hello", description="I'm polite, you know!")
    async def _hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(":wave: Hi, {0}".format(interaction.user.mention))

    @commands.slash_command(name="dog", description="Get a dog picture!")
    async def _dog(self, interaction):
        r = agb.requestHandler.handler.get("https://dog.ceo/api/breeds/image/random", attemptCache=False)
        embed = discord.Embed(title="Dog")
        url = json.loads(r.text)["message"]
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="dogbreed", description="Dog breeds :3")
    async def _dogbreeds(self, interaction: discord.Interaction):
        r = agb.requestHandler.handler.get("https://dog.ceo/api/breeds/list/all")
        j = json.loads(r.text)
        a = list(j["message"].keys())
        breed = random.choice(list(a))
        await interaction.response.send_message(":dog: `{0}`".format(breed))

