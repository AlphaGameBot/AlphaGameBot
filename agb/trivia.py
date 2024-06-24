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
import agb.requestHandler
from discord.ext import commands
import discord
import json

class TriviaOptionDisplayView(discord.ui.View):
    pass
    
class TriviaCog(agb.cogwheel.Cogwheel):
    def __init__(self, bot):
        super().__init__(bot)
        with agb.requestHandler.handler.get(agb.cogwheel.getAPIEndpoint("trivia", "GET_CATEGORIES")) as r:
            self.CATEGORIES = json.loads(r.text)["trivia_categories"]
            self.logger.debug("Retrieved %s categories" % len(self.CATEGORIES))
        
    async def _trivia_category_autocomplete(self, interaction: discord.AutocompleteContext):
        i = interaction.value
        if i.strip() == "":
            return [
                discord.OptionChoice(name="Any Category", value=0)
            ]
        
        results = []

        for entry in self.CATEGORIES:
            if i.lower() in entry["name"].lower():
                results.append(discord.OptionChoice(name=entry["name"], value=entry["id"]))
            if i.lower() in str(entry["id"]).lower():
                results.append(discord.OptionChoice(name=entry["name"], value=entry["id"]))
        
        return results
    
    @commands.slash_command(name="trivia", description="Play a game of trivia")
    async def trivia(self, interaction: discord.ApplicationContext,
                     category: discord.Option(int, "Category", required=False, default=0, autocomplete=_trivia_category_autocomplete), # type: ignore
                     difficulty: discord.Option(str, "Difficulty", required=False, default="easy", choices=["easy", "medium", "hard"]), # type: ignore
                     type: discord.Option(str, "Type", 
                                          required=False, 
                                          default="multiple", 
                                          choices=[
                                            discord.OptionChoice(name="Multiple Choice", value="multiple"), 
                                            discord.OptionChoice(name="True/False", value="boolean")])): # type: ignore
        await interaction.response.defer()
        api_args = {
            "category": category,
            "difficulty": difficulty,
            "type": type,
            "amount": 1
        }
        u = agb.requestHandler.formatQueryString(agb.cogwheel.getAPIEndpoint("trivia", "API_ENDPOINT"),
                                                 api_args)

        await interaction.followup.send(u)
        with agb.requestHandler.handler.get(u) as r:
            data = json.loads(r.text)
            if len(data["results"]) == 0:
                await interaction.followup.send("No results found.")
                return
            question = data["results"][0]["question"]
            answers = data["results"][0]["incorrect_answers"]
            answers.append(data["results"][0]["correct_answer"])
            answers = sorted(answers)
            embed = agb.cogwheel.embed(title="Trivia", description=question)
            for i, answer in enumerate(answers):
                embed.add_field(name=f"Answer {i+1}", value=answer, inline=False)
            await interaction.followup.send(embed=embed)
            return
