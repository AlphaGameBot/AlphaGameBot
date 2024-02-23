import json
import discord
from discord.ext import commands
import agb.requestHandler
import logging


class MemesCog(discord.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("MemesCog has been initalized")

    @commands.slash_command(name="meme", description="Get a meme from reddit!  (Where best memes come from)")
    async def meme(self, interaction: discord.Interaction):
        # get the meme from the memes api
        r = agb.requestHandler.handler.get("https://meme-api.com/gimme", attemptCache=False)
        d = json.loads(r.text)
        embed = discord.Embed(title=d["title"], description="Subreddit: r/{0}, by ".format(d["subreddit"], d["author"]))
        i = d["preview"][len(d["preview"])-1]
        embed.set_image(url=i)
        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="helloworld", description="It's industry standard, right?")
    async def hworld(self, interaction: discord.Interaction):
        await interaction.response.send_message(":earth_americas: Hello, World!")