import discord
from discord.ext import commands
import logging


class UtilityCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("UtilityCog has been initalized!")

    @commands.slash_command(name="whoami",
                            description="For whose who need a discord bot to help with an identity crisis.")
    async def whoami(self, interaction: discord.Interaction):

        user = interaction.user.name
        nick = interaction.user.nick

        if nick != None:
            text = "**{0}** ( `{1}` )".format(nick, user)
        else:
            text = "`{0}`".format(user)

        await interaction.response.send_message(text)

    @commands.slash_command(name="about", description="About AlphaGameBot!")
    async def _about(self, interaction):

        view = discord.ui.View()
        linkStyle = discord.ButtonStyle.link
        addTheBot = discord.ui.Button(style=linkStyle, label="Add the Bot!",
                                      url="https://discord.com/oauth2/authorize?client_id=946533554953809930&permissions=8&scope=bot")
        checkItOut = discord.ui.Button(style=linkStyle, label="Learn More!", url="https://alphagame.dev/alphagamebot/")
        githubBtn = discord.ui.Button(style=linkStyle, label="GitHub",
                                      url="https://github.com/AlphaGameDeveloper/AlphaGameBot")
        view.add_item(item=addTheBot)
        view.add_item(item=checkItOut)
        view.add_item(item=githubBtn)
        embed = discord.Embed(title="About the Bot",
                              description="AlphaGameBot is a discord bot made by AlphaGameDeveloper. Featuring many high-quality commands, AlphaGameBot is a must-have for any friend-group on Discord!")
        embed.add_field(name="Bot Ping", value="{0} milliseconds".format(round(self.bot.latency * 100, 2)))
        await interaction.response.send_message(embed=embed, view=view)
