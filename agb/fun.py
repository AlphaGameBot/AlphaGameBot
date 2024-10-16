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

import agb.system.cogwheel
import discord
import random
from discord.ext import commands

class FunCog(agb.system.cogwheel.Cogwheel):
    @commands.slash_command(name="magic8ball", description="It's a magic 8 ball!")
    async def _magic8ball(self, interaction: discord.commands.context.ApplicationContext,
                          prompt: discord.Option(str, description="What do you want to know?", required=True)): #type: ignore
        answers = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes – definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy, try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful"
        ]

        embed = agb.system.cogwheel.embed(title=prompt, description=random.choice(answers))
        embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/8ball.png")
        await interaction.response.send_message(embed=embed)
