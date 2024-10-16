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

import discord
from discord.ext import commands
from mcstatus import JavaServer, BedrockServer
import logging
from socket import gaierror

from mcstatus.querier import QueryResponse

import agb.system.cogwheel


class MinecraftCog(agb.system.cogwheel.Cogwheel):
    group = discord.SlashCommandGroup(name="minecraft", description="Minecraft-related commands")

    @group.command(name="java", description="Ping a Minecraft: Java Edition server amd get data!")
    async def _java(self, interaction,
                         host: discord.Option(str, description="The host IP address of the server"), # type: ignore
                         port: discord.Option(int, description="The port of the Minecraft server", default=25565)): # type: ignore
        if port == 25565:
            addr = "{0}".format(host)
        else:
            addr = "{0}:{1}".format(host, port)
        server = JavaServer.lookup(addr)
        await interaction.response.defer()
        try:
            status = server.status()
        except gaierror as e:  # socket.gaierror: [Errno -2] Name or service not known
            interaction.followup.send(":x: The server data cannot be found!  Check the domain name and/or the port.")
            return 1
        except TimeoutError as e:
            await interaction.followup.send(":x: Timed Out.  The server took too long to respond.")
            return
        #except ConnectionRefusedError as e:
        #    await interaction.followup.send(":x: The server refused the connection.  Is the server running?")
        #    return
        enableQuery = False
        query = None
        try:
            query = server.query()
            enableQuery = True
        except TimeoutError:
            pass

        embed = agb.system.cogwheel.embed(title="Server info for {}".format(addr),
                       description="Server information is limited as server disabled advanced query." if enableQuery == False else "")

        embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/minecraft.png")
        embed.add_field(name="Players Online", value="{}/{}".format(status.players.online, status.players.max))
        embed.add_field(name="Latency", value=round(status.latency/10, 2))
        embed.add_field(name="Version", value="{} (Protocol {})".format(status.version.name, status.version.protocol))
        embed.add_field(name="Secure Chat", value=str(status.enforces_secure_chat))
        if enableQuery:
            embed.add_field(name="Software", value="{} {}".format(query.software.brand, query.software.version))

        await interaction.followup.send(embed=embed)

    @group.command(name="bedrock", description="Ping a Minecraft: Bedrock Edition server and get data!")
    async def _bedrock(self, interaction,
                       host: discord.Option(str, description="The host IP of the Minecraft server"), # type: ignore
                       port: discord.Option(int, description="The port that the Minecraft server us running on", # type: ignore
                                            default=19132)):
        if port == 25565:
            addr = "{0}".format(host)
        else:
            addr = "{0}:{1}".format(host, port)
        server = BedrockServer.lookup(addr)
        await interaction.response.defer()
        try:
            status = server.status()
        except gaierror as e:  # socket.gaierror: [Errno -2] Name or service not known
            embed = agb.system.cogwheel.embed(title="Error!",
                                       description="The server data cannot be found!  Check the domain name and/or the port.\n\nThe reason for this is:\n`{0}`".format(
                                           repr(e)))
            embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/minecraft-error.png")
            await interaction.followup.send(embed=embed)
            return 1
        except TimeoutError as e:
            embed = agb.system.cogwheel.embed(title="Error!",
                                       description="The server timed out!\n`{0}`".format(repr(e)))
            embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/minecraft-error.png")
            await interaction.followup.send(embed=embed)
            return e

        embed = agb.system.cogwheel.embed(title="Server info for {0}".format(addr),
                                   description=status.description)
        embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/minecraft.png")

        embed.add_field(name="Players online", value="{0}/{1}".format(status.players.online, status.players.max))
        embed.add_field(name="Version", value="{0} (Protocol {1})".format(status.version.name, status.version.protocol))
        embed.add_field(name="Map Name", value=status.map_name)
        embed.add_field(name="Gamemode", value=status.gamemode)

