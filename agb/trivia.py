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
    def __init__(self, answers: list[str|bool], correctAnswer: str | bool, intendedUser: discord.User):
        super().__init__()
        self.correctAnswer = correctAnswer
        self.intendedUser = intendedUser
        self.answers = answers
        self.logger = logging.getLogger("cogwheel")
        self.logger.debug("Correct answer is %s" % self.correctAnswer)
        self.logger.debug("Intended user is %s (ID: %s)", self.intendedUser.name, self.intendedUser.id)
        
    async def isCorrectUser(self, interaction: discord.context.ApplicationContext, autoRespond: bool = True) -> bool:
        """Check if the user is the intended user to answer the question
        
        Args:
            interaction (discord.context.ApplicationContext): The interaction context
            autoRespond (bool, optional): If true, will automatically respond with an error message using the given `ApplicationContext`.  Defaults to True."""
        re = interaction.user.id == self.intendedUser.id
        self.logger.debug("isCorrectUser: %s (Comparing Intended:%s to Actual:%s)", re, self.intendedUser.id, interaction.user.id)
        if not re and autoRespond:
            self.logger.debug("isCorrectUser: Responding with error message")
            await interaction.response.send_message(f":x: You are not the intended user to answer this question.  This one's for {self.intendedUser.mention}!", ephemeral=True)
        return re
    
    async def handleAnswer(self, interaction, answer):
        """Handle the user's answer
        
        Args:
            interaction (discord.context.ApplicationContext): The interaction context
            answer (bool): The user's answer"""
        logging.getLogger("system").debug("Answer: %s", answer)

        if not await self.isCorrectUser(interaction):
            return
        
        self.logger.debug("Comparing user answer \"%s\" (Type: %s) to correct answer \"%s\" (Type: %s)", answer, type(answer).__name__, self.correctAnswer, type(self.correctAnswer).__name__)
        previous_type = type(answer)
        # Here's my extremely hacky way of comparing the answer to the correct answer even if the types are different
        # A problem with it is that it will error out if the types are not compatible, or it'll return a bad result if
        # the value evaluates to True, such as (if "string") will evaluate to True, unless if the string is empty.
        answer = type(self.correctAnswer)(answer)
        current_type = type(answer)

        if previous_type != current_type:
            self.logger.debug("Converted answer from %s to %s" % (previous_type.__name__, current_type.__name__))
            
        if answer == self.correctAnswer:
            await interaction.response.send_message(":white_check_mark: Correct!")
        else:
            await interaction.response.send_message(":x: Incorrect!  The correct answer was `%s`" % self.correctAnswer)
        self.disable_all_items()
        await interaction.message.edit(view=self)
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        self.stop()    


class TrueFalseDisplayView(BaseTriviaOptionDisplayView):
    @discord.ui.button(label="False", style=discord.ButtonStyle.red)
    async def _false(self, button, interaction):
        return await self.handleAnswer(interaction, False)

    @discord.ui.button(label="True", style=discord.ButtonStyle.green)
    async def _true(self, button, interaction):
        return await self.handleAnswer(interaction, True)
        
class TriviaOptionDisplayView(BaseTriviaOptionDisplayView):
    def __init__(self, answers: list[str], correct_answer: str, intendedUser: discord.User):
        super().__init__(answers, correct_answer, intendedUser)
        self._option_button_1.label = answers[0]
        self._option_button_2.label = answers[1]
        self._option_button_3.label = answers[2]
        self._option_button_4.label = answers[3]
        self.intendedUser = intendedUser


    @discord.ui.button(label="Placeholder Value 1", style=discord.ButtonStyle.primary)
    async def _option_button_1(self, button: discord.ui.Button, interaction: discord.ApplicationContext):
        return await self.handleAnswer(interaction, button.label)

    @discord.ui.button(label="Placeholder Value 2", style=discord.ButtonStyle.primary)
    async def _option_button_2(self, button: discord.ui.Button, interaction: discord.ApplicationContext):
        return await self.handleAnswer(interaction, button.label)

    @discord.ui.button(label="Placeholder Value 3", style=discord.ButtonStyle.primary)
    async def _option_button_3(self, button: discord.ui.Button, interaction: discord.ApplicationContext):
        return await self.handleAnswer(interaction, button.label)

    @discord.ui.button(label="Placeholder Value 4", style=discord.ButtonStyle.primary)
    async def _option_button_4(self, button: discord.ui.Button, interaction: discord.ApplicationContext):
        return await self.handleAnswer(interaction, button.label)


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
        correct_answer = data["results"][0]["correct_answer"]
        answers.append(correct_answer)
        self.logger.debug("Answers: %s" % answers)
        random.shuffle(answers)

        answerView = (TrueFalseDisplayView if type == "boolean" else TriviaOptionDisplayView)(answers, correct_answer, interaction.author)
        await interaction.followup.send(html.unescape(question), view=answerView)
