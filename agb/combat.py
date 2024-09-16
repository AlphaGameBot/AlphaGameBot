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
import agb.system.cogwheel
import json
from asyncio import sleep
import logging

class CombatTurn(Enum):
    HOME = 0
    VISITOR = 1

class ReadyStatus(Enum):
    NOTREADY = 0
    READY = 1

class Combat:
    challenger: discord.User
    competitor: discord.User
    thread: discord.Thread
    currentTurn: CombatTurn
    readyStatus: dict[CombatTurn, ReadyStatus]
    players: dict[CombatTurn, dict[str, any]]
    winReason: str
    strings: dict[str, list[str]]

    # -- game settings --
    max_hp: int
    healing_potions: int
    healing_potion_hp_min: int
    healing_potion_hp_max: int
    small_attack_min: int
    small_attack_max: int
    small_attack_chance: int | float
    large_attack_min: int
    large_attack_max: int
    large_attack_chance: int | float
    shield_offset: int | float

    def __init__(self,
                 competitor: discord.User,
                 challenger: discord.User,
                 
                 # game settings, if the players want to change them
                 # they can do so in the game
                 
                 max_hp: int = 100,
                 healing_potions: int = 2,
                 healing_potion_hp_min: int = 10,
                 healing_potion_hp_max: int = 20,
                 small_attack_min: int = 5,
                 small_attack_max: int = 10,
                 small_attack_chance: int | float = 0.50,
                 large_attack_min: int = 15,
                 large_attack_max: int = 20,
                 large_attack_chance: int | float = 0.20,
                 shield_offset: int | float = .70,
                 shield_turns: int = 2,
                 shield_count: int = 2):
        self.challenger = challenger
        self.competitor = competitor

        # game settings
        self.max_hp = max_hp
        self.healing_potions = healing_potions
        self.healing_potion_hp_min = healing_potion_hp_min
        self.healing_potion_hp_max = healing_potion_hp_max
        self.small_attack_min = small_attack_min
        self.small_attack_max = small_attack_max
        self.small_attack_chance = small_attack_chance
        self.large_attack_min = large_attack_min
        self.large_attack_max = large_attack_max
        self.large_attack_chance = large_attack_chance
        self.shield_offset = shield_offset
        self.shield_turns = shield_turns
        self.shield_count = shield_count

        self.winReason = "UNKNOWN"

        with open("assets/combat.json", "r") as combatStringsFile:
            self.data = json.load(combatStringsFile)

            self.strings = self.data["STRINGS"]

        self.thread = None
        self.currentTurn = CombatTurn.HOME

        self.readyStatus = {
            CombatTurn.HOME: ReadyStatus.NOTREADY,
            CombatTurn.VISITOR: ReadyStatus.NOTREADY
        }

        self.players = {
            CombatTurn.HOME: {
                "user": self.competitor,
                "hp": self.max_hp,
                "healing_potions": self.healing_potions,
                "shield": False,
                "shield_remaining_for": 0,
                "shields_remaining": self.shield_count
            },
            CombatTurn.VISITOR: {
                "user": self.challenger,
                "hp": self.max_hp,
                "healing_potions": self.healing_potions,
                "shield": False,
                "shield_remaining_for": 0,
                "shields_remaining": self.shield_count
            }
        }

        self.logger = logging.getLogger("cogwheel")

    def identifyUser(self, 
                     user: discord.User):
        if user.id == self.competitor.id:
            return CombatTurn.HOME
        elif user.id == self.challenger.id:
            return CombatTurn.VISITOR
        else:
            raise ValueError("Unknown User for identifyUser.")

    def otherTurn(self) -> CombatTurn:
        if self.currentTurn == CombatTurn.HOME:
            return CombatTurn.VISITOR
        elif self.currentTurn == CombatTurn.VISITOR:
            return CombatTurn.HOME
        else:
            raise ValueError("otherTurn: neither home nor visitor??? o_0")
            
    def verifyOkUser(self, 
                     user: discord.User,
                     role: CombatTurn | int | None = None
                    ) -> bool:
        """Verify if the user is in the game.
        If role is `None`, it will check if the user is either the challenger or the competitor."""
        if role is None:
            return (user.id in [self.challenger.id, self.competitor.id]) 

        elif role == CombatTurn.HOME:
            return (user.id == self.competitor.id)

        elif role == CombatTurn.VISITOR:
            return (user.id == self.challenger.id)

        else:
            raise ValueError("Invalid role for verifyOkUser!")
    
    def calculate_hit_chance(self,
                             base: float,
                             player: CombatTurn) -> float:
        """Get the total chance of hitting a player, all things considered."""
        player = self.players[player]
        chance = base
        offsets = []
        if player["shield"]:
            chance = chance * self.shield_offset
            offsets.append("shield")
        
        self.logger.debug("combat: calculate_hit_chance: %s (Modifiers: %s)" % (chance, ",".join(offsets)))
        return chance

    async def begin(self,
              interaction: discord.context.ApplicationContext):
        await interaction.response.send_message("Please continue in the following thread!")
        msg = await interaction.channel.send("%s vs. %s combat!" % (self.competitor.mention, self.challenger.mention))
        self.thread = await msg.create_thread(name="%s challenged %s to a duel" % (self.competitor.name, self.challenger.name), auto_archive_duration=60)        
        await self.openingScreen()
        
    async def openingScreen(self):
        """Opening screen for the combat.  Ask the user if they're ready to fight."""
        embed = agb.system.cogwheel.embed(
            title = "Combat",
            description = "%s, %s just challenged you to a duel.  Are you ready to "
                          "prove your worth in a duel to the death?  If you are, "
                          "press the *Ready!* button." % (self.challenger.name, self.competitor.name)
        )
        # add fields for all game settings
        embed.add_field(name="Max HP", value=str(self.max_hp))
        embed.add_field(name="Healing Potions", value=str(self.healing_potions))
        embed.add_field(name="Healing Potion HP Range", value="%s-%s" % (self.healing_potion_hp_min, self.healing_potion_hp_max))
        embed.add_field(name="Small Attack Damage Range", value="%s-%s" % (self.small_attack_min, self.small_attack_max))
        embed.add_field(name="Small Attack Hit Chance", value="%s%%" % (round(self.small_attack_chance * 100)))
        embed.add_field(name="Large Attack Damage Range", value="%s-%s" % (self.large_attack_min, self.large_attack_max))
        embed.add_field(name="Large Attack Hit Chance", value="%s%%" % (round(self.large_attack_chance * 100)))
        embed.add_field(name="Shield Offset", value="%s%%" % round(self.shield_offset*100))
        embed.add_field(name="Shield Turns", value=str(self.shield_turns))
        embed.add_field(name="Shields Count", value=str(self.shield_count))

        await self.thread.send(embed=embed, view=ReadyView(self))

    async def startFight(self):
        """Entry point for the combat.  This is where the combat actually starts."""
        await self.thread.send("Get ready to fight!")
        await self.handleUserTurn(rotate=False) # rotate=False because we already know who's going first
            
    async def handleUserTurn(self, rotate=True):
        if rotate:
            self.currentTurn = self.otherTurn()
        
        if self.players[self.currentTurn]["shield_remaining_for"] > 0:
            self.players[self.currentTurn]["shield_remaining_for"] -= 1
            if self.players[self.currentTurn]["shield_remaining_for"] == 0:
                self.players[self.currentTurn]["shield"] = False
                await self.thread.send(":shield: %s's shield has expired." % self.players[self.currentTurn]["user"].mention)
        player = self.players[self.currentTurn]
        opponent = self.players[self.otherTurn()]

        if player["hp"] <= 0:
            await self.handleUserWon(self.currentTurn)
            return
        elif opponent["hp"] <= 0:
            await self.handleUserWon(self.otherTurn())
            return
        
    

        await self.thread.send(embed=agb.system.cogwheel.embed(
            title = "%s, you're up!" % player["user"].name,
            description="""**What do you want to do?**\n
You can either:
* Do a small attack ({0}-{1} damage with {2}% chance of hitting!)
* Do a large attack ({3}-{4} damage with {5}% chance of hitting!)
* Drink a healing potion ({6}-{7} HP restored) {8}

**HP Stats**
* You: {9} HP
* Opponent: {10} HP""".format(
    self.small_attack_min,
    self.small_attack_max,
    round(self.small_attack_chance * 100), # we use round() to make it like 50% instead of 50.0%.  I find that to look better.
    self.large_attack_min,
    self.large_attack_max,
    round(self.large_attack_chance * 100),
    self.healing_potion_hp_min,
    self.healing_potion_hp_max,
    ("(You have no healing potions left!)" if player["healing_potions"] == 0 else "(%s left)" % player["healing_potions"]),
    player["hp"],
    opponent["hp"])
        ), view=CombatOptionView(self))

    async def handleUserWon(self, winner):
        winningPlayer = self.players[winner]

        # We need to make all the player's HP 0 or greater to prevent negative HP
        for player in [CombatTurn.HOME, CombatTurn.VISITOR]:
            if self.players[player]["hp"] < 0:
                self.players[player]["hp"] = 0
        await self.thread.send(random.choice(self.strings["WIN_COMBAT_EFFECTS"]).format(
            player_mention = winningPlayer["user"].mention,
            player_name = winningPlayer["user"].name,
            opponent_mention = self.players[self.otherTurn()]["user"].mention,
            opponent_name = self.players[self.otherTurn()]["user"].name
        ))
        self.winReason = "Opponent's HP reached 0."
        await self.closeCombat()

    async def closeCombat(self):
        await self.thread.send(":crossed_swords: The combat has ended.  Thanks for playing!")
        await sleep(5)
        
        embed = agb.system.cogwheel.embed(
            title = "Combat Results",
            description = """**Combat Results**
* %s: %s HP (%s healing potions left)
* %s: %s HP (%s healing potions left)

Winner: %s (by %s)""" % (
            self.players[CombatTurn.HOME]["user"].name,
            self.players[CombatTurn.HOME]["hp"],
            self.players[CombatTurn.HOME]["healing_potions"],

            self.players[CombatTurn.VISITOR]["user"].name,
            self.players[CombatTurn.VISITOR]["hp"],
            self.players[CombatTurn.VISITOR]["healing_potions"],

            self.players[self.currentTurn]["user"].name,
            self.winReason
        ))
        await self.thread.starting_message.edit(content="Here are the results of the battle between %s and %s." % (self.competitor.mention, self.challenger.mention), embed=embed)
        await self.thread.delete()

class ReadyView(agb.system.cogwheel.DefaultView):
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

class CombatOptionView(agb.system.cogwheel.DefaultView):
    def __init__(self, instance: Combat):
        super().__init__()
        self.instance = instance
        player = self.instance.players[self.instance.currentTurn]

        if player["healing_potions"] == 0:
            self._healing_potion.disabled = True
        self._healing_potion.label = "Healing Potion (%s remaining)" % str(player["healing_potions"])

        self.select_callback.options[0].label = "Shield (%s remaining)" % str(player["shields_remaining"])
        if player["shields_remaining"] == 0:
            self.select_callback.options[0].disabled = True


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
        
        roll_chance = self.instance.calculate_hit_chance(self.instance.small_attack_chance, self.instance.otherTurn())
        roll = agb.system.cogwheel.percent_of_happening(roll_chance)

        player = self.instance.players[self.instance.currentTurn]
        opponent = self.instance.players[self.instance.otherTurn()]
        if roll:
            damage = random.randint(
                self.instance.small_attack_min,
                self.instance.small_attack_max)
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
        
        roll_chance = self.instance.calculate_hit_chance(self.instance.small_attack_chance, self.instance.otherTurn())
        roll = agb.system.cogwheel.percent_of_happening(roll_chance)

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
        hp_recieved = random.randint(
            self.instance.healing_potion_hp_min,
            self.instance.healing_potion_hp_max
        )

        if player["hp"] + hp_recieved > self.instance.max_hp:
            # override it so there is a cap
            hp_recieved = self.instance.max_hp - player["hp"]
            
        player = self.instance.players[self.instance.currentTurn]

        player["hp"] += hp_recieved
        player["healing_potions"] -= 1
        
        await self.instance.thread.send("%s drank a healing potion, healing them for %s HP." % (
            player["user"].mention,
            str(hp_recieved)
        ))

        await self.instance.handleUserTurn()

    @discord.ui.select(placeholder="Use a special ability...", options=[
        discord.SelectOption(label="Shield", value="ability_shield", emoji="🛡️")
    ])
    async def select_callback(self, select, interaction):
        if not await self.validate_user(interaction.user, interaction): return
        self.disable_all_items()

        if select.values[0] == "ability_shield":
            player = self.instance.players[self.instance.currentTurn]
            if player["shield"]:
                await interaction.response.send_message(":shield: You already have a shield up!", ephemeral=True)
                return
            if player["shields_remaining"] == 0:
                await interaction.response.send_message(":shield: You're out of shields!", ephemeral=True)
                return
            player["shields_remaining"] -= 1
            player["shield"] = True
            player["shield_remaining_for"] = self.instance.shield_turns
            await self.instance.thread.send(":shield: %s activated a shield, protecting them from attacks for the next %s." % (
                player["user"].mention,
                "turn" if self.instance.shield_turns == 1 else "%s turns" % self.instance.shield_turns))

            await self.instance.handleUserTurn()
        await interaction.response.edit_message(view=self)

            
    # surrender button
    @discord.ui.button(label="Surrender", style=discord.ButtonStyle.gray, emoji="🏳️")
    async def _surrender(self, button, interaction):
        if not await self.validate_user(interaction.user, interaction): return
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        await self.instance.thread.send(":flag_white: %s has surrendered.  %s wins!" % (
            interaction.user.mention,
            self.instance.players[self.instance.otherTurn()]["user"].mention
        ))
        self.instance.winReason = "Surrender"
        await self.instance.closeCombat()
    
class CombatCog(agb.system.cogwheel.Cogwheel):
    @commands.slash_command(name="combat", description="Challenge another user to a combat!")
    async def _combat_begin(
        self,
        interaction: discord.context.ApplicationContext,
        challenger: discord.Option(discord.User, description="The user to combat with!"), # type: ignore
        # -- game settings --
        max_hp: discord.Option(int, description="The maximum HP for the game.", default=100), # type: ignore
        healing_potions: discord.Option(int, description="The number of healing potions each player gets.", default=2), # type: ignore
        healing_potion_hp_min: discord.Option(int, description="The minimum HP a healing potion can restore.", default=5), # type: ignore
        healing_potion_hp_max: discord.Option(int, description="The maximum HP a healing potion can restore.", default=20), # type: ignore
        small_attack_min: discord.Option(int, description="The minimum damage for a small attack.", default=5), # type: ignore
        small_attack_max: discord.Option(int, description="The maximum damage for a small attack.", default=10), # type: ignore
        small_attack_chance: discord.Option(float, description="The chance of a small attack hitting. (Percentage)", default=0.50), # type: ignore
        large_attack_min: discord.Option(int, description="The minimum damage for a large attack.", default=15), # type: ignore
        large_attack_max: discord.Option(int, description="The maximum damage for a large attack.", default=20), # type: ignore
        large_attack_chance: discord.Option(float, description="The chance of a large attack hitting. (Percentage)", default=0.20), # type: ignore
        shield_offset: discord.Option(float, description="The offset for the shield to change the chance of hitting by", default=0.70), # type: ignore
        shield_turns: discord.Option(int, description="The amount of turns that a shield lasts for", default=2), # type: ignore
        shield_count: discord.Option(int, description="The amount of times that you can use the shield.", default=2) # type: ignore
    ):
        
        # LOTS OF SAFEGUARDS to prevent a bad situation.
        if interaction.channel.type in [discord.ChannelType.public_thread, discord.ChannelType.private_thread]:
            await interaction.response.send_message(":x: You can't start a combat in a thread!", ephemeral=True)
            return
        
        if challenger.bot:
            await interaction.response.send_message(":x: To prevent you human meat piles from preparing for the inevitable robot apocalypse, I can't let you fight a bot. :robot:", ephemeral=True)
            return
        
        if interaction.user.id == challenger.id:
            await interaction.response.send_message(":x: You played yourself.  Wait, You can't.", ephemeral=True)
            return
        
        if max_hp < 1:
            await interaction.response.send_message(":x: Well, you died.  The maximum HP for a combat cannot be less than 1.", ephemeral=True)
            return
        
        if (small_attack_chance > 1 or small_attack_chance < 0) or (large_attack_chance > 1 or large_attack_chance < 0):
            await interaction.response.send_message(":x: The chance of hitting for a small attack or large attack must be between 0 and 1, as it is a percentage.", ephemeral=True)
            return
        
        # We want to make sure that min is not less than max, as that can cause problems with the game, randint specifically

        message: str | None = None
        if healing_potion_hp_min > healing_potion_hp_max:
            message = "The minimum HP a healing potion can restore cannot be greater than the maximum HP a healing potion can restore."
        
        elif small_attack_min > small_attack_max:
            message = "The minimum damage for a small attack cannot be greater than the maximum damage for a small attack."

        elif large_attack_min > large_attack_max:
            message = "The minimum damage for a large attack cannot be greater than the maximum damage for a large attack."

        if message is not None:
            await interaction.response.send_message(":x: %s" % message, ephemeral=True)
            return
        
        
        instance = Combat(interaction.user,
                          challenger,
                          max_hp,
                          healing_potions,
                          healing_potion_hp_min,
                          healing_potion_hp_max,
                          small_attack_min,
                          small_attack_max,
                          small_attack_chance,
                          large_attack_min,
                          large_attack_max,
                          large_attack_chance,
                          shield_offset,
                          shield_turns,
                          shield_count)

        await instance.begin(interaction)  
