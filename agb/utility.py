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

import discord
from discord.ext import commands
import logging
import uuid
import random
import agb.cogwheel

class UtilityCog(agb.cogwheel.Cogwheel):


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

    @commands.slash_command(name="dnd", description="Roll some D&D dice!")
    async def _dnd(self, interaction,
                   modifier: discord.Option(int, description="Modifier to be added to the roll.", required=False,
                                            default=0),
                   d4: discord.Option(int, description="Amount of D4 dice to roll", required=False, default=0),
                   d6: discord.Option(int, description="Amount of D6 dice to roll", required=False, default=0),
                   d8: discord.Option(int, description="Amount of D8 dice to roll", required=False, default=0),
                   d10: discord.Option(int, description="Amount of D10 dice to roll", required=False, default=0),
                   d12: discord.Option(int, description="Amount of D12 dice to roll", required=False, default=0),
                   d20: discord.Option(int, description="Amount of D20 dice to roll", required=False, default=0),
                   d100: discord.Option(int, description="Amount of D100 (D%) dice to roll", required=False, default=0)):
        total = 0

        totalDice = d4 + d6 + d8 + d10 + d12 + d20 + d100
        if totalDice > 1000:
            await interaction.response.send_message(f":x: Number of dice too high! ({totalDice} > 1000)")
            return
        # Roll x amount of d4
        for _d4 in range(d4):
            total += random.randint(1, 4)

        # Roll x amount of d6
        for _d6 in range(d6):
            total += random.randint(1, 6)

        # Roll x amount of d8
        for _d8 in range(d8):
            total += random.randint(1, 8)

        # Roll x amount of d10
        for _d10 in range(d10):
            total += random.randint(1, 10)

        # Roll x amount of d12
        for _d12 in range(d12):
            total += random.randint(1, 12)

        # Roll x amount of d20
        for _d20 in range(d20):
            total += random.randint(1, 20)

        # Roll x amount of d100 (or D% / Percent)
        for _d100 in range(d100):
            total += random.choice(
                [(_+1)*10 for _ in range(10)]
            )

        # Add the modifier at the end.  This allows for rolls like
        # 2d6 + 10, where 10 is the modifier.  It can be negative,
        # i guess.
        # By default this does nothing, as it defaults to zero.
        total += modifier

        await interaction.response.send_message(":game_die: {0}".format(total))

    def dnd_verifyUpperLimit(self, value):
        return (value <= 1000)