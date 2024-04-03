from googlesearch import search
import discord
import logging
import agb.cogwheel

class GoogleCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("GoogleCog has been initalized!")

    @discord.command(name="google", description="Search on Google (for those of you who don't wanna open Chrome :/)")
    async def _google(self, interaction,
                      query: discord.Option(str, description="The search term that you want"),
                      number: discord.Option(int, description="The number of results you want the bot to yield",
                                             default=5),
                      lang: discord.Option(str, description="The language for the searches!", value="en")):
        self.logger.debug("Google called")
        data = search(query, num_results=number, lang=lang, advanced=True)
        text = ""
        for result in data:
            text = text + "[{0}]({1}) - {2}\n".format(result.title, result.url, result.description)
        if len(text) > 2000:
            await interaction.response.send_message(":x: ERROR: Message body too long ({} > 2000)".format(len(text)))
        await interaction.response.send_message(text)