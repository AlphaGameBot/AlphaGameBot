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

import agb.cogwheel
import discord

class MathematicsCog(agb.cogwheel.Cogwheel):
    group = discord.SlashCommandGroup(name="math", description="For all your calculating needs!")

    def formatNumber(self, number):
        if number > 0 and number < 1:
            return number
        try:
            return int(number)
        except ValueError:
            return number

    @group.command(name="add", description="Get the sum of any 2 numbers")
    async def _add(self, interaction: discord.context.ApplicationContext,
                   value1: discord.Option(float, description="The first number to add"), # type: ignore
                   value2: discord.Option(float, description="The second number to add")): # type: ignore
        await interaction.response.send_message("**{0}** + **{1}** = **{2}**".format(
            self.formatNumber(value1), 
            self.formatNumber(value2), 
            value1 + value2))

    @group.command(name="subtract", description="Subtract any 2 numbers")
    async def _subtract(self, interaction: discord.context.ApplicationContext,
                   value1: discord.Option(float, description="The first number"), # type: ignore
                   value2: discord.Option(float, description="The second number")): # type: ignore
        await interaction.response.send_message("**{0}** - **{1}** = **{2}**".format(
            self.formatNumber(value1), 
            self.formatNumber(value2),
            value1 - value2))

    @group.command(name="multiply", description="Multiply any 2 numbers")
    async def _subtract(self, interaction: discord.context.ApplicationContext,
                   value1: discord.Option(float, description="The first number to multiply"), # type: ignore
                   value2: discord.Option(float, description="The second number to multiply")): # type: ignore
        await interaction.response.send_message("**{0}** x **{1}** = **{2}**".format(
            self.formatNumber(value1), 
            self.formatNumber(value2),
            value1 * value2))
    
    @group.command(name="divide", description="Divide any 2 numbers")
    async def _subtract(self, interaction: discord.context.ApplicationContext,
                   value1: discord.Option(float, description="The first number to divide (numerator)"), # type: ignore
                   value2: discord.Option(float, description="The second number to divide (denominator)")): # type: ignore
        if value2 == 0:
            await interaction.response.send_message(":x: Cannot divide by zero!")
            return
        await interaction.response.send_message("**{0}** / **{1}** = **{2}**".format(
            self.formatNumber(value1), 
            self.formatNumber(value2),
            value1 / value2))
