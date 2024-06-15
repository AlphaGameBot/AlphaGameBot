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

import json
import agb.cogwheel
import discord
from discord.ext import commands

class TestButtonView(discord.ui.View):
    def __init__(self, test):
        super().__init__()
        self.test = test

    @discord.ui.button(label="Strongly Disagree",
                       style=discord.ButtonStyle.red)
    async def _strongly_disagree(self, button, interaction):
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        self.test.handleAnswer(0)
        await self.test.nextQuestion()

    @discord.ui.button(label="Disagree", style=discord.ButtonStyle.red)
    async def _disagree(self, button, interaction):
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        self.test.handleAnswer(.2)
        await self.test.nextQuestion()
    
    @discord.ui.button(label="Neutral", style=discord.ButtonStyle.grey)
    async def _neutral(self, button, interaction):
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        self.test.handleAnswer(1)
        await self.test.nextQuestion()
    
    @discord.ui.button(label="Agree", style=discord.ButtonStyle.green)
    async def _agree(self, button, interaction):
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        self.test.handleAnswer(1.5)
        await self.test.nextQuestion()

    @discord.ui.button(label="Strongly Agree", style=discord.ButtonStyle.green)
    async def _strongly_agree(self, button, interaction):
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        self.test.handleAnswer(2)
        await self.test.nextQuestion()

class TestCompleteOptionView(discord.ui.View):
    def __init__(self, message: discord.Message, channel: discord.Thread):
        super().__init__()
        self.channel = channel

    @discord.ui.button(label="Close Test",
                       style=discord.ButtonStyle.blurple)
    async def _close(self, button, interaction):
        # Close the thread in which the mbti test was preformed
        await self.channel.delete()
    

class EnneagramTest:
    logger: agb.cogwheel.CogwheelLoggerHelper
    cog: agb.cogwheel.Cogwheel
    key: dict
    user: discord.User
    id: int
    stats: dict
    currentquestion: int
    thread: discord.Thread
    QUESTIONS: list[dict]
    question: dict
    message: discord.Message
    mbti: str
    mbti_list: list

    def __init__(self, cog: agb.cogwheel.Cogwheel, user: discord.User):
        self.user = user # discord.User
        self.id = self.user.id
        self.cog = cog
        self.logger = cog.logger
        self.key = {
            1: "Type 1: The Reformer",
            2: "Type 2: The Helper",
            3: "Type 3: The Achiever",
            4: "Type 4: The Individualist",
            5: "Type 5: The Investigator",
            6: "Type 6: The Loyalist",
            7: "Type 7: The Enthusiast",
            8: "Type 8: The Challenger",
            9: "Type 9: The Peacemaker"
        }

        self.stats = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            8: 0,
            9: 0
        }
        self.currentquestion = 0
        self.thread = None 
        with open("assets/enneagram.json", "r") as f:
            self.QUESTIONS = json.load(f)
        self.logger.debug("Loaded %d questions" % len(self.QUESTIONS))
        self.question = self.QUESTIONS[self.currentquestion]
        
    async def nextQuestion(self, advance=True):
        """Prepares and shows the next question"""
        if advance:
            self.currentquestion += 1
        if self.currentquestion >= len(self.QUESTIONS):
            await self.showResults()
            return
        self.question = self.QUESTIONS[self.currentquestion]

        await self.thread.send("{0}/{1}. {2}".format(self.currentquestion + 1, len(self.QUESTIONS), self.question["question"]), view=TestButtonView(self))

    def handleAnswer(self, answer):
        """Handles the answer to the current question"""
        self.stats[int(self.question["type"])] += answer
        self.logger.debug("Stats: %s" % str(self.stats))
    
    async def showResults(self):
        """Displays the results to the user"""
        # Get the base enneagram type
        
        maxValue = -1 # WE NEED TO START AT -1 TO MAKE SURE WE GET THE FIRST VALUE TO OVERWRITE
        for x in range(1, 10):
            if self.stats[x] > maxValue:
                maxValue = self.stats[x]
                

        possibleEnneagrams = []
        for enneagram, score in self.stats.items():
            if score == maxValue:
                possibleEnneagrams.append(enneagram)

        self.logger.debug("Possible Enneagrams: %s" % possibleEnneagrams)
        enneagram = possibleEnneagrams[0] # we know there is AT LEAST ONE.
        self.logger.debug("Max value: %s" % maxValue)
        
        # GET WING
        wings = [(enneagram - 1) if enneagram != 1 else 9, enneagram + 1 if enneagram != 9 else 1]

        if wings[0] > wings[1]:
            wing = wings[0]
            
        else:
            wing = wings[1]
        self.logger.debug("Enneagram: %s, Wing: %s" % (enneagram, wing))
        
        # Get last number in tritype
        _stats = self.stats.copy() # make a copy of stats
        HEART = [2,3,4]
        ANGER = [8,9,1]
        MIND = [5,6,7]

        MIND_MX = -1
        ANGER_MX = -1
        HEART_MX = -1

        MIND_TYPE = 0
        ANGER_TYPE = 0
        HEART_TYPE = 0

        # get highest for MIND.
        for x in MIND:
            if _stats[x] > MIND_MX:
                MIND_MX = _stats[x]
                MIND_TYPE = x
        
        # get highest for ANGER.
        for x in ANGER:
            if _stats[x] > ANGER_MX:
                ANGER_MX = _stats[x]
                ANGER_TYPE = x
        
        # get highest for HEART.
        for x in HEART:
            if _stats[x] > HEART_MX:
                HEART_MX = _stats[x]
                HEART_TYPE = x

        # get them in order of most to least.
        tritype = [MIND_TYPE, ANGER_TYPE, HEART_TYPE]
        tritype.sort(key=lambda x: _stats[x], reverse=True)
        self.logger.debug("Tritype: %s" % tritype)
        # Here, we set the embed to be displayed to the user.
        description = "**Here is some more information.**\n"
        description = description + "Your highest score was for the type %s, with a score of %s.\n" % (self.key[enneagram], self.stats[enneagram])
        description = description + "Other possible enneagrams include {}\n".format(", ".join(["*" + self.key[x] + "*" for x in possibleEnneagrams if x != enneagram])) if len(possibleEnneagrams) > 1 else "No other possible enneagrams found, but you might be able to find something by looking at the scores.\n"
        embed = agb.cogwheel.embed(title="Enneagram Test Results ({0}w{1}) [{2}]".format(enneagram, 
                                                                                         wing, 
                                                                                         "".join([str(x) for x in tritype])), 
                                   description=description)
        embed.add_field(name="Enneagram Type", value=self.key[enneagram], inline=False)
        embed.add_field(name="Wing", value=self.key[wing], inline=False)
        for x in range(1, 10):
            embed.add_field(name="Score for {}".format(self.key[x]), value=str(self.stats[x]), inline=True)

        v = TestCompleteOptionView(self.message, self.thread)
        learnmore = discord.ui.Button(style=discord.ButtonStyle.link, label="Learn More!", url="https://www.enneagraminstitute.com/type-%s" % (enneagram))
        winglearnmore = discord.ui.Button(style=discord.ButtonStyle.link, label="Learn More about your wing!", url="https://www.enneagraminstitute.com/type-%s" % (wing))
        whatisanenneagram = discord.ui.Button(style=discord.ButtonStyle.link, label="What is an Enneagram?", url="https://www.enneagraminstitute.com/how-the-enneagram-system-works")
        v.add_item(learnmore)
        v.add_item(winglearnmore)
        v.add_item(whatisanenneagram)
        await self.thread.delete()
        # send to main channel
        await self.message.edit(content="**%s's Enneagram Test Results**" % self.user.name, view=None, embed=embed)
        
    async def startTest(self,  interaction: discord.context.ApplicationContext):
        await interaction.response.send_message("**Please continue in the following thread.**")
        self.message = await interaction.channel.send("**%s's Enneagram Test**" % self.user.name)
        self.thread = await self.message.create_thread(name="*%s's Enneagram Test*" % self.user.name, auto_archive_duration=60)
        await self.nextQuestion(advance=False)  # advance=False tells the function not to increase the question counter, as we are just starting.

class EnneagramCog(agb.cogwheel.Cogwheel):
    @commands.slash_command(name="enneagram", description="Take the Enneagram test!")
    async def enneagram(self, interaction: discord.context.ApplicationContext):
        await EnneagramTest(self, interaction.author).startTest(interaction)