#  Copyright (c) 2024. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.
#
#

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
import os
import nltk
import logging
import logging.config
import agb.cogwheel
import threading
# commands
import agb.utility
import agb.xkcd
import agb.memes
import agb.jokes
import agb.jojo
import agb.rps
import agb.minecraft
import agb.google
import agb.moderation
# import agb.mbtitest
import agb.rssFeedCog
# if you wanna set custom logging configs i guess
# this is in .gitignore and .dockerignore because
# not everyone needs it, and if they do, it will
# be automatically loaded. :) --Damien 12.22.23
# TODO: Add base logging.cfg for people to copy
logging.config.fileConfig("logging.ini")
#logging.basicConfig(level=logging.DEBUG)
intents = discord.Intents.all()

SAY_EXCEPTIONS = [
    1180023544042770533, # The Nerds with No Life
    1179187852601479230  # AlphaGameDeveloper
]
DAMIEN = 420052952686919690
HOLDEN = 951639877768863754

global isDebugEnv, cogw, listener
isDebugEnv = (os.getenv("DEBUG_ENV") != None)
cogw = logging.getLogger("cogwheel")
listener = logging.getLogger("listener")
#if os.getenv("DEBUG") != None:
#    logging.basicConfig(level=logging.DEBUG)
#else:
#    logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="?", intents=intents)
nltk.download('words')
@bot.event
async def on_ready():
    if not isDebugEnv:
        status = discord.Game("with the API")
    else:
        logging.debug("note: Using debug Discord activity")
        status = discord.Streaming(name="Squash That Bug!", url="https://alphagame.dev/alphagamebot")
    await bot.change_presence(activity=status)
    bot.auto_sync_commands = True
    logging.info("Bot is now ready!")
    logging.info("Bot user is \"{0}\".".format(bot.user.name))

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: discord.DiscordException):
    listener.error("Error in slash command /{0} - \"{1}\"".format(interaction.command, repr(error)))
    embed = agb.cogwheel.embed(title="An error occured...", description="An internal server error has occured, and the bot cannot fulfill your request.  You may be able \
                                                                   to make it work by trying again.\nSorry about that! (awkward face emoji)", color=discord.Color.red())


    embed.add_field(name="Error message", value="`{0}`".format(repr(error)))
    embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/error.png")
    try:
        await interaction.response.send_message(embed=embed)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(embed=embed)
    if isDebugEnv:
        raise error

@bot.listen()
async def on_application_command(ctx: discord.ApplicationContext):
    listener.info("Command Called: /{0}".format(ctx.command.name))

@bot.command(name="say")
async def _say(ctx: discord.ext.commands.context.Context, *, text:str=None):
    if isDebugEnv:
        cogw.info("?say was ignored as I think this is a development build.")
        return EnvironmentError("Bot is in development build")
    if ctx.message.guild.id not in SAY_EXCEPTIONS:
        return
    if ctx.author.id == HOLDEN:
        await ctx.send(":middle_finger: Nice try, bozo")
        cogw.warning("Holden tried to use ?say to say \"{0}\".  L bozo".format(text))
        return
    if ctx.author.id != DAMIEN:
        cogw.warning("{0} tried to make me say \"{1}\", but I successfully ignored it.".format(ctx.author.name, text))
        await ctx.send(":x: I beg your pardon, but my creator only wants me to say his opinions.")
        return

    if text == None:
        return
    logging.info("I was told to say: \"{}\".".format(text))
    await ctx.send(text)
    await ctx.message.delete()

# set command cogs
bot.add_cog(agb.utility.UtilityCog(bot))
bot.add_cog(agb.xkcd.xkcdCog(bot))
bot.add_cog(agb.memes.MemesCog(bot))
bot.add_cog(agb.jokes.jokesCog(bot))
bot.add_cog(agb.jojo.JojoCog(bot))
bot.add_cog(agb.rps.rpsCog(bot))
bot.add_cog(agb.minecraft.MinecraftCog(bot))
bot.add_cog(agb.moderation.ModerationCog(bot))
# bot.add_cog(agb.mbtitest.MBTITestCog(bot))
bot.add_cog(agb.rssFeedCog.RSSFeedCog(bot))
# don't want to put half-working code in production
# Uncomment this line if you want to use the /google
# command.

# bot.add_cog(agb.google.GoogleCog(bot))

if __name__ == "__main__":
    logging.info("Starting the bot...")
    bot.run(os.getenv("TOKEN"))