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
import discord
from discord.ext import commands
from enum import Enum
import agb.cogwheel
import json

class CombatTurn(Enum):
    HOME = 0
    VISITOR = 1

class ReadyStatus(Enum):
    NOTREADY = 0
    READY = 1

class ReadyView(discord.ui.View):
    def __init__(self, combatInstance):
        super().__init__()
        self.instance = combatInstance
        
    @discord.ui.button(label="Ready!", emoji="⚔️")
    async def _ready(self, button, interaction):
        if self.instance.verifyOkUser(interaction.user):
            if self.instance.readyStatus[self.instance.identifyUser(interaction.user)] != ReadyStatus.READY:
                self.instance.readyStatus[
                    self.instance.identifyUser(interaction.user)
                ] = ReadyStatus.READY
            else:
                await interaction.response.send_message(":x: I appreciate the enthusiasm, but you're already ready.", ephemeral=True)
                return
        else:
            await interaction.response.send_message("You're not a player in this game.", ephemeral=True)
            return
            
        await self.instance.thread.send(":crossed_swords: %s is now ready." % interaction.user.mention)

        if (self.instance.readyStatus[CombatTurn.HOME] == ReadyStatus.READY
            ) and (self.instance.readyStatus[CombatTurn.VISITOR] == ReadyStatus.READY):
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await self.instance.startFight()
        else:
            await interaction.response.edit_message()

class CombatOptionView(discord.ui.View):
    def __init__(self, instance):
        super().__init__()
        self.instance = instance
        player = self.instance.players[self.instance.currentTurn]

        if player["healing_potions"] == 0:
            self._healing_potion.disabled = True
        self._healing_potion.label = "Healing Potion (%s remaining)" % str(player["healing_potions"])

    async def validate_user(self, user, interaction) -> bool:
        if self.instance.verifyOkUser(user):
            if self.instance.identifyUser(user) == self.instance.currentTurn:
                return True
            await interaction.response.send_message("Nice try, but this is your opponent's turn!", ephemeral=True) 
            return False
        await interaction.response.send_message("Hey!  You're not even in this game!", ephemeral=True)
        return False

    @discord.ui.button(label="Small Attack", emoji="🗡️", style=discord.ButtonStyle.green)
    async def _small_attack(self, button, interaction):
        if not await self.validate_user(interaction.user, interaction): return

        self.disable_all_items()
        button.label = "Small Attack Chosen!"
        await interaction.response.edit_message(view=self)
        
        roll = random.choice([True, False])
        player = self.instance.players[self.instance.currentTurn]
        opponent = self.instance.players[self.instance.otherTurn()]
        if roll:
            damage = random.randint(5, 10)
            opponent["hp"] -= damage
            await self.instance.thread.send("%s did a small attack on %s, taking %s HP, and %s" % (
                player["user"].mention,
                opponent["user"].mention,
                str(damage),
                random.choice(self.instance.strings["SMALL_ATTACK_SUCCESS_PAIN_EFFECTS"])))
        else:
            await self.instance.thread.send("%s tried to do a small attack on %s, but %s" % (
                player["user"].mention,
                opponent["user"].mention,
                random.choice(self.instance.strings["SMALL_ATTACK_FAILURE_MISS_EFFECTS"])
            ))
            
        await self.instance.handleUserTurn()

    @discord.ui.button(label="Large Attack", emoji="⚔️", style=discord.ButtonStyle.red)
    async def _large_attack(self, button, interaction):
        if not await self.validate_user(interaction.user, interaction): return
        self.disable_all_items()
        button.label = "Large Attack Chosen!"
        await interaction.response.edit_message(view=self)
        
        roll = random.choice([True, False, False, False, False])
        player = self.instance.players[self.instance.currentTurn]
        opponent = self.instance.players[self.instance.otherTurn()]
        if roll:
            damage = random.randint(15, 20)
            opponent["hp"] -= damage
            await self.instance.thread.send("%s did a large attack on %s, taking %s HP, and %s" % (
                player["user"].mention,
                opponent["user"].mention,
                str(damage),
                random.choice(self.instance.strings["LARGE_ATTACK_SUCCESS_PAIN_EFFECTS"])))
        else:
            await self.instance.thread.send("%s tried to do a large attack on %s, but %s" % (
                player["user"].mention,
                opponent["user"].mention,
                random.choice(self.instance.strings["LARGE_ATTACK_FAILURE_MISS_EFFECTS"])
            ))
            
        await self.instance.handleUserTurn()

    @discord.ui.button(label="Healing Potion", style=discord.ButtonStyle.blurple)
    async def _healing_potion(self, button, interaction):
        if not await self.validate_user(interaction.user, interaction): return
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        player = self.instance.players[self.instance.currentTurn]
        hp_recieved = random.randint(5, 20)

        if player["hp"] + hp_recieved > 100:
            # override it so only 100 hp max
            hp_recieved = 100 - player["hp"]
            
        player = self.instance.players[self.instance.currentTurn]

        player["hp"] += hp_recieved
        player["healing_potions"] -= 1
        
        await self.instance.thread.send("%s drank a healing potion, healing them for %s HP." % (
            player["user"].mention,
            str(hp_recieved)
        ))

        await self.instance.handleUserTurn()

class Combat:
    def __init__(self,
                 competitor: discord.User,
                 challenger: discord.User):
        self.challenger = challenger
        self.competitor = competitor

        with open("assets/combat_strings.json", "r") as f:
            self.strings = json.load(f)

        self.thread = None
        self.currentTurn = CombatTurn.HOME

        self.readyStatus = {
            CombatTurn.HOME: ReadyStatus.NOTREADY,
            CombatTurn.VISITOR: ReadyStatus.NOTREADY
        }

        self.players = {
            CombatTurn.HOME: {
                "user": self.competitor,
                "hp": 100,
                "healing_potions": 2
            },
            CombatTurn.VISITOR: {
                "user": self.challenger,
                "hp": 100,
                "healing_potions": 2
            }
        }

    def identifyUser(self, 
                     user: discord.User):
        if user.id == self.competitor.id:
            return CombatTurn.HOME
        elif user.id == self.challenger.id:
            return CombatTurn.VISITOR
        else:
            raise ValueError("Unknown User for identifyUser.")

    def otherTurn(self):
        if self.currentTurn == CombatTurn.HOME:
            return CombatTurn.VISITOR
        elif self.currentTurn == CombatTurn.VISITOR:
            return CombatTurn.HOME
        else:
            raise ValueError("otherTurn: neither home nor visitor??? o_0")
            
    def verifyOkUser(self, 
                     user: discord.User,
                     role:int=None):
        if role is None:
            return (user.id in [self.challenger.id, self.competitor.id])

        elif role == CombatTurn.HOME:
            return (user.id == self.competitor.id)

        elif role == CombatTurn.VISITOR:
            return (user.id == self.challenger.id)

        else:
            raise ValueError("Invalid role for verifyOkUser!")
             
    async def begin(self,
              interaction: discord.context.ApplicationContext):
        await interaction.response.send_message("Please continue in the following thread!")
        msg = await interaction.channel.send("%s vs. %s combat!" % (self.competitor.mention, self.challenger.mention))
        self.thread = await msg.create_thread(name="%s challenged %s to a duel" % (self.competitor.name, self.challenger.name), auto_archive_duration=60)        
        await self.openingScreen()
        
    async def openingScreen(self):
        await self.thread.send(embed=agb.cogwheel.embed(
            title = "Combat",
            description = "%s, %s just challenged you to a duel.  Are you ready to "
                          "prove your worth in a duel to the death?  If you are, "
                          "press the *Ready!* button." % (self.challenger.name, self.competitor.name)
        ), view=ReadyView(self))

    async def startFight(self):
        await self.thread.send("Get ready to fight!")

        try:
            await self.handleUserTurn(rotate=False)
        except Exception as e:
            await self.thread.send("`%s`" % repr(e))
            
    async def handleUserTurn(self, rotate=True):
        if rotate:
            self.currentTurn = self.otherTurn()
            
        player = self.players[self.currentTurn]
        opponent = self.players[self.otherTurn()]

        if player["hp"] <= 0:
            await self.handleUserWon(self.currentTurn)
            return
        elif opponent["hp"] <= 0:
            await self.handleUserWon(self.otherTurn())
            return
            
        await self.thread.send(embed=agb.cogwheel.embed(
            title = "%s, you're up!" % player["user"].name,
            description="""**What do you want to do?**\n
You can either:
* Do a small attack (5-10 damage with 50% chance of hitting!)
* Do a large attack (15-20 damage with 20% chance of hitting!)

**HP Stats**
* You: {0}
* Opponent: {1}""".format(player["hp"], opponent["hp"])
        ), view=CombatOptionView(self))

    async def handleUserWon(self, winner):
        winningPlayer = self.players[winner]

        await self.thread.send("%s won the game!" % winningPlayer["user"].name)
                
class CombatCog(agb.cogwheel.Cogwheel):
    @commands.slash_command(name="combat", description="Challenge another user to a combat!")
    async def _combat_begin(
        self,
        interaction: discord.context.ApplicationContext,
        challenger: discord.Option(discord.User, description="The user to combat with!") # type: ignore
    ):
        if interaction.user.id == challenger.id:
            await interaction.response.send_message(":x: You played yourself.  Wait, You can't.", ephemeral=True)
            return
            
        instance = Combat(interaction.user, challenger)

        await instance.begin(interaction)  
