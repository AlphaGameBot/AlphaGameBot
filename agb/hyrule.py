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

from agb.system.requestHandler import handler as requesthandler
from json import loads
import agb.cogwheel
import discord
import random
import agb.system.requestHandler


class CompodiumEntrySchema:
    """Base schema for the Hyrule Compodium API response. This is the base class for all compendium entries. It is not meant to be used directly."""
    raw_api_response: dict
    name: dict
    id: int
    category: str
    description: str
    image: str
    common_locations = list[str]
    dlc: bool

    def __init__(self, apiResponse: dict) -> None:
        self.raw_api_response = apiResponse
        self.name = apiResponse["name"]
        self.id = apiResponse["id"]
        self.category = apiResponse["category"]
        self.description = apiResponse["description"]
        self.image = apiResponse["image"]
        self.common_locations = apiResponse["common_locations"]
        self.dlc = apiResponse["dlc"]

    def createBaseEmbed(self) -> discord.Embed:
        """Creates a base embed for the compendium entry."""
        embed = discord.Embed(title=' '.join(word.capitalize() for word in self.name.split()),
                            description=self.description)
        embed.set_thumbnail(url=self.image)
        embed.add_field(name="ID", value=self.id)
        embed.add_field(name="Category", value=self.category.capitalize())
        embed.add_field(name="DLC", value="Yes" if self.dlc else "No")
        embed.add_field(name="Common Locations", value=", ".join(self.common_locations) if self.common_locations else "Unknown")
        return embed
    
class CompodiumMonster(CompodiumEntrySchema):
    """Schema for Monsters from the Hyrule Compodium API."""
    drops: list[str]

    def __init__(self, apiResponse: dict):
        super().__init__(apiResponse)
        self.drops = apiResponse["drops"]

    def getEmbed(self):
        embed = self.createBaseEmbed()
        embed.add_field(name="Drops", value=", ".join(self.drops) if self.drops else "None")
        return embed

class CompodiumEquipment(CompodiumEntrySchema):
    """Schema for Equipment from the Hyrule Compodium API."""
    properties: dict
    attack: float
    defense: float
    effect: str
    type: str
    
    def __init__(self, apiResponse: dict):
        super().__init__(apiResponse)
        hasEffect = "effect" in apiResponse.keys()
        self.properties = apiResponse["properties"]
        self.attack = self.properties["attack"]
        self.defense = self.properties["defense"]
        if hasEffect:
            self.effect = self.properties["effect"]
        else:
            self.effect = "No Effect."

    def getEmbed(self):
        embed = self.createBaseEmbed()
        embed.add_field(name="Attack", value=self.attack)
        embed.add_field(name="Defense", value=self.defense)
        embed.add_field(name="Effect", value=self.effect)
        return embed
    
class CompodiumMaterial(CompodiumEntrySchema):
    """Schema for Materials from the Hyrule Compodium API."""
    hearts_recovered: float
    cooking_effect: str
    fuse_attack_power: float

    def __init__(self, apiResponse):
        super().__init__(apiResponse)
        self.hearts_recovered = apiResponse["hearts_recovered"]
        self.cooking_effect = apiResponse["cooking_effect"]
        # TODO: add fuse attack power to the embed
    def getEmbed(self):
        embed = self.createBaseEmbed()
        embed.add_field(name="Hearts Recovered", value=self.hearts_recovered)
        embed.add_field(name="Cooking Effect", value=self.cooking_effect)
        return embed
    
class CompodiumCreature(CompodiumEntrySchema):
    """Schema for Creatures from the Hyrule Compodium API."""
    edible: bool
    hearts_recovered: float
    cooking_effect: str

    def __init__(self, apiResponse: dict):
        super().__init__(apiResponse)
        self.edible = apiResponse["edible"]
        self.hearts_recovered = apiResponse["hearts_recovered"]
        self.cooking_effect = apiResponse["cooking_effect"]
    
    def getEmbed(self):
        embed = self.createBaseEmbed()
        embed.add_field(name="Edible", value="Yes" if self.edible else "No")
        embed.add_field(name="Hearts Recovered", value=self.hearts_recovered)
        embed.add_field(name="Cooking Effect", value=self.cooking_effect)
        return embed

class CompodiumTreasure(CompodiumEntrySchema):
    """Schema for Treasures from the Hyrule Compodium API."""
    def __init__(self, apiResponse: dict):
        super().__init__(apiResponse)
        self.drops = apiResponse["drops"]

    def getEmbed(self):
        embed = self.createBaseEmbed()
        embed.add_field(name="Drops", value=", ".join(self.drops) if self.drops else "None")
        return embed

# make the discord cog
class HyruleCog(agb.cogwheel.Cogwheel):
    group = discord.SlashCommandGroup(name="hyrule", description="Hyrule Compendium-related commands")
    
    def __init__(self, bot):
        super().__init__(bot)

        # Initialize the internal list of compendium entries
        self.compodiumEntries = []
        self.compodium = loads(
            requesthandler.get(
                agb.cogwheel.getAPIEndpoint("hyrule", "GET_ALL")
            ).text
        )["data"]
        for entry in self.compodium:
            self.compodiumEntries.append(
                {
                    "name": entry["name"],
                    "id": entry["id"]
                }
            )
        self.logger.debug("Initialized Internal Hyrule Compendium with %d entries" % len(self.compodiumEntries))
    
    async def compodium_autocomplete(self, interaction: discord.AutocompleteContext):
        """Autocomplete function to search the self.compodiumEntries for the given input."""
        self.logger.debug("Autocompleting with value %s" % interaction.value)
        matching_entries = []
        for entry in self.compodiumEntries:
            if interaction.value.lower() in entry["name"].lower() or interaction.value.lower() in str(entry["id"]):
                matching_entries.append(
                    discord.OptionChoice(
                        name=entry["name"],
                        value=entry["id"]
                    )
                )
        return matching_entries
    
    @group.command(name="compendium", description="Get a compendium entry.")
    async def _compendium(self, interaction,
                   entry: discord.Option(int, description="The name of the compendium entry you want to get.", 
                                         required=True, 
                                         autocomplete=compodium_autocomplete)): # type: ignore
        r = requesthandler.get(
                agb.cogwheel.getAPIEndpoint("hyrule", "GET_ONE").format(entry))
        apiresponse = loads(
            r.text
        )
        if r.status_code != 200:
            await interaction.response.send_message(":x: `%s`" % apiresponse["message"])
            return
        apiresponse = apiresponse["data"]
        if apiresponse["category"] == "monsters":
            compendiumEntry = CompodiumMonster(apiresponse)
        elif apiresponse["category"] == "equipment":
            compendiumEntry = CompodiumEquipment(apiresponse)
        elif apiresponse["category"] == "materials":
            compendiumEntry = CompodiumMaterial(apiresponse)
        elif apiresponse["category"] == "creatures":
            compendiumEntry = CompodiumCreature(apiresponse)
        elif apiresponse["category"] == "treasure":
            compendiumEntry = CompodiumTreasure(apiresponse)
        else:
            await interaction.response.send_message(":x: Internal Error: Unknown category `%s`" % apiresponse["category"])
            return
    
        await interaction.response.send_message(embed=compendiumEntry.getEmbed())

    @group.command(name="random", description="Get a random compendium entry.")
    async def _random(self, interaction: discord.ApplicationContext):
        n = random.randint(0, len(self.compodiumEntries) - 1)
        entry = self.compodiumEntries[n]
        await self._compendium(interaction, entry=entry["id"]) 