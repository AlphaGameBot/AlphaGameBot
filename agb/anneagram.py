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
    

class AnneagramTest:
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

    def __init__(self, user, logger: agb.cogwheel.CogwheelLoggerHelper):
        self.user = user # discord.User
        self.id = self.user.id
        self.logger = logger
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
        self.QUESTIONS = [
            {
                "question": "You have a strong sense of right and wrong.",
                "type": "1"
                
            },
            {
                "question": "You heavily care about improving the world around you.",
                "type": "1"
                
            },
            {
                "question": "I always love when I'm the center of attention.",
                "type": "1"
                
            },
            {
                "question": "You want to be useful.",
                "type": "1"
                
            },
            {
                "question": "You feel the need often to justify your actions.",
                "type": "1"
                
            },
            {
                "question": "You have a set of principles that must be followed at all times.",
                "type": "1"
                
            },
            {
                "question": "I always put others first.",
                "type": "2"
                
            },
            {
                "question": "I want to help people a lot",
                "type": "2"
                
            },
            {
                "question": "The best thing is to put other people's needs first.",
                "type": "2"
                
            },
            {
                "question": "You love unconditionally.",
                "type": "2"
                
            },
            {
                "question": "You are goal oriented.",
                "type": "3"
                
            },
            {
                "question": "You exhibit charisma and charm onto others.",
                "type": "3"
                
            },
            {
                "question": "To be seen as a loser would be the worst thing for you.",
                "type": "3"
                
            },
            {
                "question": "You are VERY competitive.",
                "type": "3"
            
            },
            {
                "question": "You want to be noticed through success.",
                "type": "3"
                
            },
            {
                "question": "My self-image is very important to me.",
                "type": "4"
                
            },
            {
                "question": "I like to look at myself as different from other people.",
                "type": "5"
                
            },
            {
                "question": "You base your identity on emotional reactions.",
                "type": "4"
                
            },
            {
                "question": "When not stressed, you like to be honest to yourself.",
                "type": "4"
               
            },
            {
                "question": "You always feel like you're missing something in life.",
                "type": "4"
                
            },
            {
                "question": "You focus heavily on understanding complex ideas and skills.",
                "type": "5"
                
            },
            {
                "question": "You have specialized skill sets for your expertise.",
                "type": "5"
                
            },
            {
                "question": "You want to understand how the world works more than anything.",
                "type": "5"
                
            },
            {
                "question": "You want to acquire as much knowledge as possible to understand something.",
                "type": "5",
                
            },
            {
                "question": "You are scared of not being able to do things as well as others.",
                "type": "5",
                
            },
            {
                "question": "You are very loyal to your friends and beliefs.",
                "type": "6",
                
            },
            {
                "question": "You need guidance and help in life.",
                "type": "6",
                
            },
            {
                "question": "You believe that all authority must be questioned.",
                "type": "6",
                
            },
            {
                "question": "You get very anxious when doing a big thing on your own.",
                "type": "6",
                
            },
            {
                "question": "You are easily influenced by others.",
                "type": "6",
                
            },
            {
                "question": "You like working on a multitude of projects at the same time.",
                "type": "7",
                
            },
            {
                "question": "You enjoy intellecually-stimulating activities.",
                "type": "7",
                
            },
            {
                "question": "You are good at brainstorming.",
                "type": "7",
                
            },
            {
                "question": "You have trouble listening to people.",
                "type": "7",
                
            },
            {
                "question": "You fear boredom.",
                "type": "7",
                
            },
            {
                "question": "You desire being in control of your life more than anything else.",
                "type": "8",
                
            },
            {
                "question": "You like improving yourself with challenges.",
                "type": "8",
                
            },
            {
                "question": "You don't care much about what other people think of you.",
                "type": "8",
                
            },
            {
                "question": "You don't like showing weakness to others.",
                "type": "8",
                
            },
            {
                "question": "You have a lot of determination and willpower.",
                "type": "8",
                
            },
            {
                "question": "You are spiritual.",
                "type": "9",
                
            },
            {
                "question": "You greatly value deep connections with others.",
                "type": "9",
                
            },
            {
                "question": "You try to keep the peace between others.",
                "type": "9",
                
            },
            {
                "question": "You would give up your own needs to benefit others.",
                "type": "9",
                
            },
            {
                "question": "You value other perspectives on things.",
                "type": "9",
                
            }
        ]
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
        # GET THE HIGHEST VALUE IN THE STATS DICTIONARY
        maxValue = -1 # WE NEED TO START AT -1 TO MAKE SURE WE GET THE FIRST VALUE TO OVERWRITE
        currentMaxIndex = "INVALID."
        possibleEnneagrams = []
        for x in range(1, 10):
            if self.stats[x] > maxValue:
                maxValue = self.stats[x]
                currentMaxIndex = x
                possibleEnneagrams = [x]
            elif self.stats[x] == maxValue:
                possibleEnneagrams.append(x)
        maxvalue = maxValue
        anneagram = currentMaxIndex
        self.logger.debug("Max value: %s" % maxvalue)
        # for x in range(1, 10):
        #     if self.stats[x] == maxvalue: # we found it
        #         maxvaluename = self.key[x]
        #         anneagram = x
        #         self.logger.debug("({0}) Value: {1} which is {2} (FOUND IT!)".format(x, self.stats[x], maxvalue))
        #     else:
        #         self.logger.debug("({0}) Value: {1} which is not {2}".format(x, self.stats[x], maxvalue))
        # if anneagram is None:
        #     raise ValueError("INVALID INTERNAL STATE: maximum is None.")
        
        # GET WING
        wings = [(anneagram - 1) if anneagram != 1 else 9, anneagram + 1 if anneagram != 9 else 1]

        if wings[0] > wings[1]:
            wing = wings[0]
            
        else:
            wing = wings[1]
        self.logger.debug("Anneagram: %s, Wing: %s" % (anneagram, wing))
        # TODO: i will add tritype later

        embed = agb.cogwheel.embed(title="Anneagram Test Results ({0}w{1})".format(anneagram, wing), 
                                   description="Other possible enneagrams include {}".format(
                                       ", ".join([self.key[x] for x in possibleEnneagrams if x != anneagram])))
        embed.add_field(name="Anneagram Type", value=self.key[anneagram], inline=False)
        embed.add_field(name="Wing", value=self.key[wing], inline=False)
        for x in range(1, 10):
            embed.add_field(name="Score for {}".format(self.key[x]), value=str(self.stats[x]), inline=True)
        await self.thread.send(embed=embed, view=TestCompleteOptionView(self.message, self.thread))
        
    async def startTest(self,  interaction: discord.context.ApplicationContext):
        await interaction.response.send_message("**Please continue in the following thread.**")
        self.message = await interaction.channel.send("**%s's Enneagram Test**" % self.user.name)
        self.thread = await self.message.create_thread(name="*%s's Enneagram Test*" % self.user.name, auto_archive_duration=60)
        self.stats = {1: 6.7, 2: 4, 3: 5.7, 4: 8, 5: 11, 6: 5.7, 7: 7.2, 8: 7.2, 9: 7.2} # TODO: remove bullshit
        await self.showResults()
        #await self.nextQuestion(advance=False)  # advance=False tells the function not to increase the question counter, as we are just starting.

class AnneagramCog(agb.cogwheel.Cogwheel):
    @commands.slash_command(name="anneagram", description="Take the Anneagram test!")
    async def anneagram(self, interaction: discord.context.ApplicationContext):
        await AnneagramTest(interaction.author, self.logger).startTest(interaction)