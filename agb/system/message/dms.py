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


async def handleDMMessage(ctx: discord.Message):
    """This function handles messages sent to the bot in DMs.
    
    Doesn't do much at the moment, but I'm planning on adding some cool features using this!
    
    Args:
        ctx (discord.Message): The message context.
    """
    if ctx.guild: return
    if ctx.author.bot: return
    
    await ctx.channel.trigger_typing()
    content = ctx.content.strip()


    v = discord.ui.View()

    # support server
    v.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Support Server", url="https://discord.gg/ECJS6ssyf4"))

    # github
    v.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="GitHub", url="https://github.com/AlphaGameBot/AlphaGameBot"))

    # webpage
    v.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Webpage", url="https://alphagame.dev/alphagamebot"))

    await ctx.channel.send(f"Hello, {ctx.author.mention}! DMs are not supported at this time. If you need help, please join the support server!\n"
                           "Don't worry, though!  I've got some nice features planned that involve DMs!", view=v)