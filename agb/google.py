from googlesearch import search
import discord
import logging
import agb.cogwheel

class GoogleCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("GoogleCog has been initalized!")

    @discord.slash_command(name="google", description="Search on Google (for those of you who don't wanna open Chrome :/)")
    async def _google(self, interaction: discord.Interaction, query: str, number:int=10, lang:str="en"):
        data = search(query, num_results=number, lang=lang, advanced=True)
        text = ""
        for result in data:
            text = text + "[{0}]({1}) - {2}\n".format(result.title, result.url, result.description)
        return
        await interaction.response.send_message(text)