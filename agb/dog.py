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

        http_codes = [
            100, # Continue
            101, # Switching Protocols
            102, # Processing
            103, # Early Hints
            200, # OK
            201, # Created
            202, # Accepted
            203, # Non-Authoritative Information
            204, # No Content
            205, # Reset Content
            206, # Partial Content
            207, # Multi-Status
            208, # Already Reported
            226, # IM Used
            300, # Multiple Choices
            301, # Moved Permanently
            302, # Found
            303, # See Other
            304, # Not Modified
            305, # Use Proxy
            307, # Temporary Redirect
            308, # Permanent Redirect
            400, # Bad Request
            401, # Unauthorized
            402, # Payment Required
            403, # Forbidden
            404, # Not Found
            405, # Method Not Allowed
            406, # Not Acceptable
            407, # Proxy Authentication Required
            408, # Request Timeout
            409, # Conflict
            410, # Gone
            411, # Length Required
            412, # Precondition Failed
            413, # Payload Too Large
            414, # URI Too Long
            415, # Unsupported Media Type
            416, # Range Not Satisfiable
            417, # Expectation Failed
            418, # I'm a teapot
            421, # Misdirected Request
            422, # Unprocessable Entity
            423, # Locked
            424, # Failed Dependency
            425, # Too Early
            426, # Upgrade Required
            428, # Precondition Required
            429, # Too Many Requests
            450, # Blocked by Windows Parental Control
            431, # Request Header Fields Too Large
            451, # Unavailable For Legal Reasons
            500, # Internal Server Error
            501, # Not Implemented
            502, # Bad Gateway
            503, # Service Unavailable
            504, # Gateway Timeout
            505, # HTTP Version Not Supported
            506, # Variant Also Negotiates
            507, # Insufficient Storage
            508, # Loop Detected
            510, # Not Extended
            511, # Network Authentication Required
            999
        ]

        if code not in http_codes:
            await interaction.response.send_message(":x: Invalid HTTP code")
            return
        
        await interaction.response.send_message(endpoint)