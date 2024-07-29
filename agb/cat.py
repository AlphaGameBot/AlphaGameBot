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
from agb.requestHandler import handler
import discord
from json import loads

class CatCog(agb.cogwheel.Cogwheel):
    group = discord.SlashCommandGroup(name="cat", description="For all your kitty needs!")

    @group.command(name="image", description="Get a cat image!")
    async def _image(self, interaction: discord.context.ApplicationContext):
        endpoint = agb.cogwheel.getAPIEndpoint("cat", "RANDOM_IMAGE")

        response = loads(handler.get(endpoint, attemptCache=False).text)[0]

        await interaction.response.send_message(response["url"])

    @group.command(name="http", description="Get a cat for your HTTP response code!")
    async def _http(self, interaction: discord.context.ApplicationContext,
                        code: discord.Option(int, description="HTTP code")): # type: ignore
        endpoint = agb.cogwheel.getAPIEndpoint("cat", "GET_HTTP_CAT").format(code)

        response = agb.requestHandler.handler.get(endpoint)
        
        if response.status_code != 200:
            await interaction.response.send_message(":x: HTTP code not found!")
            
        await interaction.response.send_message(endpoint)

    @group.command(name="fact", description="Get a random cat fact!")
    async def _fact(self, interaction: discord.context.ApplicationContext):
        endpoint = agb.cogwheel.getAPIEndpoint("cat", "GET_RANDOM_CAT_FACT")

        response = loads(handler.get(endpoint, attemptCache=False).text)

        await interaction.response.send_message(response["text"])

    @group.command(name="random", description="Get a random cat image!")
    async def _random(self, interaction: discord.context.ApplicationContext):
        endpoint = agb.cogwheel.getAPIEndpoint("cat", "GET_RANDOM_CAT_JSON")
        api_json = json.loads(
            handler.get(endpoint, attemptCache=False).text
        )[0]

        # API Endpoint result:
        # tags: List[string]
        # mimetype: string
        # size: int, size in bytes
        # _id: string, append to 'https://cataas.com/cat/(_id)' to get the actual image URL

        await interaction.response.send_message(
            agb.cogwheel.getAPIEndpoint("cat", "GET_CAT_IMAGE").format(api_json["_id"])
        )
