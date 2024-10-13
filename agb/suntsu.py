#      AlphaGameBot - A Discord bot that's free and (hopefully) doesn't suck
#      Copyright (C) 2024  Damien Boisvert (AlphaGameDeveloper)
#
#      AlphaGameBot is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      AlphaGameBot is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with AlphaGameBot.  If not, see <https://www.gnu.org/licenses/>.

import discord
import agb.system.cogwheel
import random
import json
from discord.ext import commands


class SunTsuCog(agb.system.cogwheel.Cogwheel):
    def init(self):
        with open("assets/suntsu.json") as f:
            self.SUNTSU_QUOTES = json.load(f)
        self.logger.debug("Loaded %s Sun Tsu quotes" % len(self.SUNTSU_QUOTES))

    @commands.slash_command(name="suntsu", description="Get a quote from Sun Tsu: The Art of War")
    async def _SunTsuCog(self, interaction: discord.context.ApplicationContext):
        await interaction.response.send_message("> *\"%s\"*\n> \- Sun Tzu, *The Art of War*" % random.choice(
                                                                                            self.SUNTSU_QUOTES))
