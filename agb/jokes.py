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

import logging

import discord
from discord.ext import commands
import agb.requestHandler
import json
from nltk.corpus import words
import random
import cowsay
import agb.cogwheel

class jokesCog(agb.cogwheel.Cogwheel):
    @commands.slash_command(name="joke", description="I'm so funny, right?")
    async def _joke(self, interaction):
        r = agb.requestHandler.handler.get(agb.cogwheel.getAPIEndpoint("joke", "GET_JOKE"), attemptCache=False)
        joke = json.loads(r.text)

        embed = discord.Embed(title="Joke #{}".format(joke["id"]), description="{0}\n{1}".format(joke["setup"], joke["punchline"]))
        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="wisdom", description="Get a word of wisdom")
    async def _wisdom(self, interaction):
        await interaction.response.send_message(random.choice(words.words()))

    @commands.slash_command(name="shakespeare", description="Shakespeare translator!")
    async def _shakespeare(self, interaction,
                           text: discord.Option(str, description="Text to translate!")):
        endpoint = agb.cogwheel.getAPIEndpoint("shakespeare", "TRANSLATE")
        if text[len(text) - 1] == " ":
            text[len(text) - 1] = ""
        text = text.lower()
        # following spaces so cache is possible lol
        r = agb.requestHandler.handler.get(endpoint + "?text=" + text)
        j = json.loads(r.text)
        await interaction.response.send_message(j['contents']["translated"])

    @commands.slash_command(name="hello", description="I'm polite, you know!")
    async def _hello(self, interaction):
        await interaction.response.send_message(":wave: Hi, {0}".format(interaction.user.mention))

    @commands.slash_command(name="coinflip", description="Flip a coin!")
    async def _coinflip(self, interaction):
        await interaction.response.send_message(":coin: %s" % "Heads" if random.choice([True,False]) else "Tails")

    @commands.slash_command(name="cowsay", description="Linux cowsay command in Discord")
    async def _cowsay(self, interaction,
                      text: discord.Option(str, description="The text for the cow to say!"),
                      character: discord.Option(str, description="The character you want to use!",
                                                default="cow", choices=cowsay.char_names)):
        t = cowsay.get_output_string(character, text)
        if len(t) > 2000:
            await interaction.response.send_message(":x: Too long! ({0} > 2000)".format(len(t)))
            return
        await interaction.response.send_message("```\n{0}\n```".format(t))

