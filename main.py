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
import sys
from dotenv import load_dotenv
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
import agb.fun
import agb.botinfo
import agb.system.commandError
import agb.rssFeedCog
import agb.suntsu 
import agb.myersbriggs
import agb.wikipedia
import agb.mathematics
import agb.dog
# - - - - - - - - - - - - - - - - - - - - - - -
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
OWNER = os.getenv("ALPHAGAMEBOT_OWNER_ID", 420052952686919690)

global cogw, listener
cogw = logging.getLogger("cogwheel")
listener = logging.getLogger("listener")
#if os.getenv("DEBUG") != None:
#    logging.basicConfig(level=logging.DEBUG)
#else:
#    logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="?", intents=intents)

@bot.event
async def on_ready():
    if not agb.cogwheel.isDebugEnv:
        game_name = os.getenv("DISCORD_STATUS", "Whack A Bug!")
    else:
        logging.debug("note: Using debug Discord activity")
        game_name = os.getenv("DISCORD_STATUS", "With the Discord API.")
    
    status = discord.Game(game_name)
    await bot.change_presence(activity=status)
    logging.info(f"Set the bot's Discord activity to playing \"{game_name}\".")
    bot.auto_sync_commands = True
    logging.info("Bot is now ready!")
    logging.info("Bot user is \"{0}\". (ID={1})".format(bot.user.name, bot.user.id))

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: discord.DiscordException):
    listener.error("Error in slash command /{0} - \"{1}\"".format(interaction.command, repr(error)))
    return await agb.system.commandError.handleApplicationCommandError(interaction, error)


@bot.listen()
async def on_application_command(ctx: discord.ApplicationContext):
    listener.info("Command Called: /{0}".format(ctx.command.name))

@bot.event
async def on_message(ctx: discord.Message):
    #   As this is a public Discord bot, I can see multiple people getting
    #   scared of this function, possibly processing their messages.  I want
    #   to point out the order of the if statements that follow.  Nothing is
    #   processed, unless the discord server is in SAY_EXCEPTIONS.  If it is not,
    #   NO DATA IS PROCESSED.
    if ctx.content.startswith("..") == False:
        return
    if ctx.content.startswith("...") == True: 
        # Sometimes, I make sarcastic comments, starting with ...
        # Example: "... blah blah blah", and the bot responds to it as
        # ". blah blah blah".  This prevents the bot from responding.
        return


    # Disable the say command for all servers except for the ones in which they are explicitly
    # enabled in alphagamebot.json, key "SAY_EXCEPTIONS"
    if ctx.guild.id not in SAY_EXCEPTIONS:
        return
    
    # When I run 2 instances of AlphaGameBot at the same time, both will reply to my message.
    # What it does is that if it is in a debug environment, it will ignore the command.  When testing,
    # I will just remove the `DEBUG=1` environment variable.
    if agb.cogwheel.isDebugEnv:
        cogw.info("Say was ignored as I think this is a development build.")
        return EnvironmentError("Bot is in development build")
    
    if ctx.author.id != OWNER:
        cogw.warning("{0} tried to make me say \"{1}\", but I successfully ignored it.".format(ctx.author.name,
                                                                                               ctx.content))
        await ctx.reply("> \"You can go fuck yourself with that!\", Brewstew, *Devil Chip*")
        return

    text = ctx.content
    text = text[2:]
    if text == None:
        # No text given, so give up...
        return
    
    # Put in the console that it was told to say something!
    logging.info("I was told to say: \"%s\"." % text)
    await ctx.channel.send(text)

    # Delete the original message, so it looks better in the application!
    await ctx.delete()


# set command cogs
bot.add_cog(agb.utility.UtilityCog(bot))
bot.add_cog(agb.xkcd.xkcdCog(bot))
bot.add_cog(agb.memes.MemesCog(bot))
bot.add_cog(agb.jokes.jokesCog(bot))
bot.add_cog(agb.jojo.JojoCog(bot))
bot.add_cog(agb.rps.rpsCog(bot))
bot.add_cog(agb.minecraft.MinecraftCog(bot))
bot.add_cog(agb.moderation.ModerationCog(bot))
bot.add_cog(agb.rssFeedCog.RSSFeedCog(bot))
bot.add_cog(agb.fun.FunCog(bot))
bot.add_cog(agb.botinfo.BotInformationCog(bot))
bot.add_cog(agb.suntsu.SunTsuCog(bot))
bot.add_cog(agb.myersbriggs.MyersBriggsTypeIndicatorCog(bot))
bot.add_cog(agb.wikipedia.WikipediaCog(bot))
bot.add_cog(agb.mathematics.MathematicsCog(bot))
bot.add_cog(agb.dog.DogCog(bot))
# don't want to put half-working code in production
# Uncomment this line if you want to use the /google
# command.

# bot.add_cog(agb.google.GoogleCog(bot))

if __name__ == "__main__":
    logging.info("Starting the bot...")
    if len(sys.argv) >= 2:
        if sys.argv[1].lower() == "useEnvironment":
            logging.info("Using .env environment file because it was explicitly requested with 'useEnvironment'!")
            load_dotenv()
        else:
            logging.warning(f"Unknown value for argv location 1: '{sys.argv[1]}'!")
    token = os.getenv("TOKEN")
    if token == None:
        logging.error("No token was given via the environment variable 'TOKEN'!")
        logging.error("Use the argument 'useEnvironment' to automatically load your .env file.")
        sys.exit(1)
    bot.run(token)
