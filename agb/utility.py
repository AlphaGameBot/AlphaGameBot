import discord
from discord.ext import commands
import logging

class UtilityCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("UtilityCog has been initalized!")

    @commands.slash_command(name="whoami", description="For whose who need a discord bot to help with an identity crisis.")
    async def whoami(self, interaction: discord.Interaction):

        user = interaction.user.name
        nick = interaction.user.nick

        if nick != None:
            text = "**{0}** ( `{1}` )".format(nick, user)
        else:
            text = "`{0}`".format(user)

        await interaction.response.send_message(text)