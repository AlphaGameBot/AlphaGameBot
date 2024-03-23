import discord
from discord.ext import commands
import logging
import uuid
import random
class UtilityCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("UtilityCog has been initalized!")

    @commands.slash_command(name="whoami", description="For whose who need a discord bot to help with an identity crisis.")
    async def whoami(self, interaction):

        user = interaction.user.name
        nick = interaction.user.nick

        if nick != None:
            text = "**{0}** ( `{1}` )".format(nick, user)
        else:
            text = "`{0}`".format(user)

        await interaction.response.send_message(text)

    @commands.slash_command(name="uuid", description="Get a version 4 UUID")
    async def _uuid(self, interaction, count:int=1):
        if count > 100:
            await interaction.response.send_message(":x: Way too spicy!  You can only create 100 UUIDs per request!")
            return
        r = ""
        for a in range(count):
            r = r + "`{0}`\n".format(uuid.uuid4())

        await interaction.response.send_message(r)

    @commands.slash_command(name="randomstring", description="Get a random string!")
    async def _randstr(self, interaction, length:int=12):
        if length > 120:
            await interaction.response.send_message(":x: Woah, there!  Random strings can only be up to 120 characters long!")
            return
        all_characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + [chr(i) for i in
                                                                            range(ord('A'), ord('Z') + 1)] + [str(i) for
                                                                                                              i in
                                                                                                              range(0,
                                                                                                                    10)]
        r = ""
        for a in range(length):
            r = r + random.choice(all_characters)

        await interaction.response.send_message("`{}`".format(r))