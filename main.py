import discord
from discord.ext import commands
import os
import nltk
import sys
import logging
import logging.config
import agb.cogwheel
import threading
#import webui.app as webui
# commands
import agb.utility
import agb.xkcd
import agb.memes
import agb.jokes
import agb.rps

# if you wanna set custom logging configs i guess
# this is in .gitignore and .dockerignore because
# not everyone needs it, and if they do, it will
# be automatically loaded. :) --Damien 12.22.23
# TODO: Add base logging.cfg for people to copy
try:
    logging.config.fileConfig("logging.ini")
except:
    logging.basicConfig(level=logging.WARNING)
    logging.warn("CANNOT READ LOGGING CONFIGURATION FILE 'logging.ini'!")
#logging.basicConfig(level=logging.DEBUG)
intents = discord.Intents.all()

DAMIEN = 420052952686919690

#if os.getenv("DEBUG") != None:
#    logging.basicConfig(level=logging.DEBUG)
#else:
#    logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="?", intents=intents)
nltk.download('words')
@bot.event
async def on_ready():
    status = discord.Game("with the API")
    await bot.change_presence(activity=status)
    bot.auto_sync_commands = True
    print("Bot is ready! :)")

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: discord.DiscordException):
    embed = agb.cogwheel.embed(title="An error occured...", description="An internal server error has occured, and the bot cannot fulfill your request.  You may be able \
                                                                   to make it work by trying again.\nSorry about that! (awkward face emoji)", color=discord.Color.red())


    embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/error.png")
    await interaction.response.send_message(embed=embed)
    raise error


@bot.command(name="say")
async def _say(ctx: discord.ext.commands.context.Context, *, text:str=None):
    if ctx.author.id != DAMIEN:
        print("{0} tried to make me say \"{1}\", but I successfully ignored it.")
        await ctx.send(":x: I beg your pardon, but my creator only wants me to say his opinions.")
        return
    if text == None:
        return
    print("I was told to say: \"{}\".".format(text))
    await ctx.send(text)
    await ctx.message.delete()

# set command cogs
bot.add_cog(agb.utility.UtilityCog(bot))
bot.add_cog(agb.xkcd.xkcdCog(bot))
bot.add_cog(agb.memes.MemesCog(bot))
bot.add_cog(agb.jokes.jokesCog(bot))
bot.add_cog(agb.rps.rpsCog(bot))

if __name__ == "__main__":
    #threading.Thread(target=webui.start).start()
    bot.run(os.getenv("TOKEN") if os.getenv("TOKEN") != None else sys.argv[1])