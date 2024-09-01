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

import random
import agb.cogwheel
import agb.system.requestHandler
from discord.ext import commands
import discord
import json
import logging
import html

class BaseTriviaOptionDisplayView(discord.ui.View):
    def __init__(self, correctAnswer: bool, intendedUser: discord.User):
        super().__init__()
        self.correctAnswer = correctAnswer
        self.intendedUser = intendedUser
        self.logger = logging.getLogger("cogwheel")
        self.logger.debug("Correct answer is %s" % self.correctAnswer)
        self.logger.debug("Intended user is %s (ID: %s)" % self.intendedUser.name, self.intendedUser.id)
        
    def isCorrectUser(self, interaction: discord.context.ApplicationContext, autoRespond: bool = True) -> bool:
        """Check if the user is the intended user to answer the question
        
        Args:
            interaction (discord.context.ApplicationContext): The interaction context
            autoRespond (bool, optional): If true, will automatically respond with an error message using the given `ApplicationContext`.  Defaults to True."""
        re = interaction.author.id == self.intendedUser.id
        self.logger.debug("isCorrectUser: %s (Comparing Intended:%s to Actual:%s)" % re, self.intendedUser.id, interaction.author.id)
        if not re and autoRespond:
            self.logger.debug("isCorrectUser: Responding with error message")
            interaction.response.send_message(f":x: You are not the intended user to answer this question.  This one's for {self.intendedUser.mention}!", ephemeral=True)
        return re
    
    async def handleAnswer(self, interaction, answer):
        """Handle the user's answer
        
        Args:
            interaction (discord.context.ApplicationContext): The interaction context
            answer (bool): The user's answer"""
        logging.getLogger("system").debug("Answer: %s", answer)

        if not self.isCorrectUser(interaction):
            return
        
        if answer == self.correctAnswer:
            await interaction.response.send_message(":white_check_mark: Correct!")
        else:
            await interaction.response.send_message(":x: Incorrect!")
        self.disable_all_items()
        await interaction.message.edit(view=self)
        
class BaseTriviaOptionDisplayView(BaseTriviaOptionDisplayView):
    @discord.ui.button(label="False", style=discord.ButtonStyle.red)
    async def _false(self, button, interaction):
        return await self.handleAnswer(interaction, False)

    @discord.ui.button(label="True", style=discord.ButtonStyle.green)
    async def _true(self, button, interaction):
        return await self.handleAnswer(interaction, True)
        
class TriviaOptionDisplayView(discord.ui.View):
    def __init__(self, options: list[str], correctValueIndex: int, intendedUser: discord.User):
        super().__init__()
        self.options = options
        self.correctValueIndex = correctValueIndex
        self._option_button_1.label = options[0]
        self._option_button_2.label = options[1]
        self._option_button_3.label = options[2]
        self._option_button_4.label = options[3]
        self.intendedUser = intendedUser

    async def handle_response(self, interaction, button_option_index: int):
        if interaction.user.id != self.intendedUser.id:
            await interaction.response.send_message(f":x: You are not the intended user to answer this question.  This one's for {self.intendedUser.mention}!", ephemeral=True)
            return
        if button_option_index - 1 == self.correctValueIndex:
            await interaction.response.send_message(":white_check_mark: Correct!  The answer was **%s**." % self.options[self.correctValueIndex])
        else:
            await interaction.response.send_message(f":x: Incorrect!  The correct answer was `{self.options[self.correctValueIndex]}`")
        self.disable_all_items()
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Placeholder Value 1", style=discord.ButtonStyle.primary)
    async def _option_button_1(self, button: discord.ui.Button, interaction: discord.ApplicationContext):
        return await self.handle_response(interaction, 1)

    @discord.ui.button(label="Placeholder Value 2", style=discord.ButtonStyle.primary)
    async def _option_button_2(self, button: discord.ui.Button, interaction: discord.ApplicationContext):
        return await self.handle_response(interaction, 2)

    @discord.ui.button(label="Placeholder Value 3", style=discord.ButtonStyle.primary)
    async def _option_button_3(self, button: discord.ui.Button, interaction: discord.ApplicationContext):
        return await self.handle_response(interaction, 3)

    @discord.ui.button(label="Placeholder Value 4", style=discord.ButtonStyle.primary)
    async def _option_button_4(self, button: discord.ui.Button, interaction: discord.ApplicationContext):
        return await self.handle_response(interaction, 4)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        self.stop()    


class TriviaCog(agb.cogwheel.Cogwheel):
    def __init__(self, bot):
        super().__init__(bot)
        with agb.system.requestHandler.handler.get(agb.cogwheel.getAPIEndpoint("trivia", "GET_CATEGORIES")) as r:
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
        u = agb.system.requestHandler.formatQueryString(agb.cogwheel.getAPIEndpoint("trivia", "API_ENDPOINT"),
                                                 api_args)

        with agb.system.requestHandler.handler.get(u, attemptCache=False) as r:
            data = json.loads(r.text)
            if data["response_code"] == 1:
                await interaction.followup.send("No results found.")
                return
            elif data["response_code"] == 2:
                await interaction.followup.send("Invalid parameter.")
                return
            elif data["response_code"] == 3:
                await interaction.followup.send("Token not found.")
                return
            elif data["response_code"] == 4:
                await interaction.followup.send("Token empty.")
                return
            elif data["response_code"] == 5:
                await interaction.followup.send(":x: Hold it!  I'm currently being rate limited.  Give me a sec...")
                return
            
        question = data["results"][0]["question"]
        answers = data["results"][0]["incorrect_answers"]
        answers.append(data["results"][0]["correct_answer"])
        self.logger.debug("Answers: %s" % answers)
        random.shuffle(answers)

        answerView = (f type == "boolean" else TriviaOptionDisplayView)(answers, answers.index(data["results"][0]["correct_answer"]), interaction.author)
        await interaction.followup.send(html.unescape(question), view=answerView)
