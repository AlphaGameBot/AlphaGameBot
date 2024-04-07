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
import agb.cogwheel
import logging
import random


class rpsCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("cogwheel")
        self.logger.info("rpsCog has been initalized!")
        self.gameData = {
            "rock": {
                "name": "Rock",
                "beats": "scissors"
            },
            "paper": {
                "name": "Paper",
                "beats": "rock"
            },
            "scissors": {
                "name": "Scissors",
                "beats": "paper"
            }
        }

    def getWinnerState(self, player_choice, computer_choice):
        data = {
            "winner": -1,  # the number
            "human-win-status": "<ERROR:UNCHANGED VALUE>",
            "players": {
                "computer": computer_choice,
                "player": player_choice
            }
        }

        if player_choice == computer_choice:
            data["winner"] = 2
            data["human-win-status"] = "TIED"
        elif (player_choice == "rock" and computer_choice == "scissors") or \
                (player_choice == "paper" and computer_choice == "rock") or \
                (player_choice == "scissors" and computer_choice == "paper"):
            data["winner"] = 0
            data["human-win-status"] = "WON"
        else:
            data["winner"] = 1
            data["human-win-status"] = "LOST"
        return data

    @commands.slash_command(name="rockpaperscissors", description="Let's play Rock Paper Scissors!")
    async def _rps(self, interaction,
                   playerchoice: discord.Option(str, description="Your Choice!", choices=[
                       "rock",
                       "paper",
                       "scissors"
                   ])):
        if playerchoice.lower() not in self.gameData.keys():
            # well shit I guess you entered something wrong :/
            embed = agb.cogwheel.embed(title="Error!",
                                       description="Well this is awkward... '{}' doesn't seem to be a valid option.  Please use:\nrock,paper,scissors".format(
                                           playerchoice))
            await interaction.response.send_message(embed=embed)
            return None
        ai = random.choice(["rock", "paper", "scissors"])
        pl = playerchoice.lower()  # player's choice
        state = self.getWinnerState(pl, ai)
        # 1 --> Player wins
        # 2 --> AI wins
        # 0 --> Draw

        embed = agb.cogwheel.embed(title="Rock Paper Scissors",
                                   description=(
                                           "You %s" % state["human-win-status"]))
        embed.add_field(name="Your choice", value=state["players"]["player"])
        embed.add_field(name="Bot's choice", value=state["players"]["computer"])

        await interaction.response.send_message(embed=embed)
