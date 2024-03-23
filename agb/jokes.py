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
    async def _wisdom(self, interaction):
        await interaction.response.send_message(random.choice(words.words()))

    @commands.slash_command(name="shakespeare", description="Shakespeare translator!")
    async def _shakespeare(self, interaction, text:str):
        endpoint = "https://api.funtranslations.com/translate/shakespeare.json"
        params = {"text": text}
        if text[len(text) - 1] == " ":
            text[len(text) - 1] = ""
        text = text.lower()
        # following spaces so cache is possible lol
        r = agb.requestHandler.handler.get(endpoint + "?text=" + text)
        j = json.loads(r.text)
        await interaction.response.send_message(j['contents']["translated"])