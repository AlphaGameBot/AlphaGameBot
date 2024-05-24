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
import discord
import random
import json

class DogCog(agb.cogwheel.Cogwheel):
    group = discord.SlashCommandGroup(name="dog", description="For all your dog needs!")

    @group.command(name="picture", description="Get a dog picture!")
    async def _dog(self, interaction):
        endpoint = agb.cogwheel.getAPIEndpoint("dog", "GET_PICTURE")
        r = agb.requestHandler.handler.get(endpoint, attemptCache=False)
        embed = discord.Embed(title="Dog")
        url = json.loads(r.text)["message"]
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    @group.command(name="breed", description="Dog breeds :3")
    async def _dogbreeds(self, interaction):
        endpoint = agb.cogwheel.getAPIEndpoint("dog", "GET_BREEDS")
        r = agb.requestHandler.handler.get(endpoint)
        j = json.loads(r.text)
        a = list(j["message"].keys())
        breed = random.choice(list(a))
        await interaction.response.send_message(":dog: `{0}`".format(breed))



    @group.command(name="http", description="Get a dog for your HTTP response code!")
    async def _http(self, interaction: discord.context.ApplicationContext,
                        code: discord.Option(int, description="HTTP code")):
        endpoint = agb.cogwheel.getAPIEndpoint("dog", "GET_HTTP_DOG").format(code)

        response = agb.requestHandler.handler.get(endpoint)
        
        if response.status_code != 200:
            await interaction.response.send_message(":x: HTTP code not found!")
        await interaction.response.send_message(endpoint)