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


#    This is the main file for the AlphaGameBot Discord bot.  Start the bot using this file.
#    Most code is in other directories.  Here is a quick overview of the directories:

#    agb/ - The main directory for the bot.  Contains all cogs.
#    agb/cogwheel.py - Contains miscellaneous functions and variables used throughout the bot.
#    agb/requestHandler.py - Contains functions for handling requests to external APIs.
#    agb/system/ - Contains system functions and classes.
#    agb/tests/ - Contains unit tests for the bot.  Not used in production.

#    This file contains command-line flags to control bot behavior.  Use -h or --help for more information.
#    Run the command < python3 main.py -h > for some help with command-line flags.

import discord
from discord.ext import commands
from discord.ext import tasks
import os
import time
import logging
import logging.config
import agb.cogwheel
import sys
from dotenv import load_dotenv
from aiohttp import client_exceptions
import datetime
import argparse
import mysql.connector
import threading
# system
import agb.system.commandError
import agb.system.message
import agb.system.applicationCommand
import agb.system.rotatingStatus
import agb.system.databaseUpdate
# commands
import agb.user
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
import agb.rssFeedCog
import agb.suntsu 
import agb.myersbriggs
import agb.wikipedia
import agb.mathematics
import agb.dog
import agb.cat
import agb.hyrule
import agb.enneagram
import agb.trivia
import agb.reddit
print(os.environ)
##### LIST OF COGS #####
BOT_LOADED_COGS = [
    agb.utility.UtilityCog,
    agb.xkcd.xkcdCog,
    agb.memes.MemesCog,
    agb.jokes.jokesCog,
    agb.jojo.JojoCog,
    agb.rps.rpsCog,
    agb.minecraft.MinecraftCog,
    agb.moderation.ModerationCog,
    agb.rssFeedCog.RSSFeedCog,
    agb.fun.FunCog,
    agb.botinfo.BotInformationCog,
    agb.suntsu.SunTsuCog,
    agb.myersbriggs.MyersBriggsTypeIndicatorCog,
    agb.wikipedia.WikipediaCog,
    agb.mathematics.MathematicsCog,
    agb.dog.DogCog,
    agb.cat.CatCog,
    agb.user.UserStatsCog,
    agb.hyrule.HyruleCog,
    agb.enneagram.EnneagramCog,
    agb.trivia.TriviaCog,
    agb.reddit.RedditCog
]
# parsing command line arguments
if __name__ == "__main__":
    d = datetime.date.today()
    parser = argparse.ArgumentParser(
        prog="AlphaGameBot Discord Bot",
        description="A Discord Bot that's free and (hopefully) doesn't suck.",
        epilog=f"(c) Damien Boisvert (AlphaGameDeveloper) {d.year}.  Licensed under GNU GPL v3"
    )
    parser.add_argument("-d", "--debug", help="Enable debug mode for the bot.", action="store_true")
    parser.add_argument("-e", "--environment", help="Automatically load a environment file for the bot.")
    parser.add_argument("-t", "--token", help="Set the bot's token via the command line. (Not recommended)")
    parser.add_argument("-n", "--nodatabase", help="Force database to be disabled regardless of environment", action="store_true")
    parser.add_argument("-r", "--requiredatabase", help="Force database to be enabled.  This will error if the database is not configured correctly.", action="store_true")
    parser.add_argument("-v", "--version", help="Print the version of the bot and exit.", action="store_true")
    parser.add_argument("-q", "--notracking", help="Disable tracking of user data", action="store_false")    
    args = parser.parse_args()
# Initalize logging services
LOG_LEVEL = logging.INFO
if args.debug: # args.debug:
    LOG_LEVEL = logging.DEBUG

# Load the logging file (logging/main.ini)
logging.lastResort.setLevel(logging.INFO)
logging.config.fileConfig("logging/main.ini") # load the config

CONFIGURED_LOGGERS = [
	"root",
	"cogwheel",
	"requesthandler",
	"listener",
	"system"
]

for l in CONFIGURED_LOGGERS:
	logging.getLogger(l).setLevel(LOG_LEVEL)
if args.version:
    print(f"AlphaGameBot Discord Bot Version {agb.cogwheel.getBotInformation()['VERSION']}")
    print(f"Copyright (C) {d.year}  Damien Boisvert (AlphaGameDeveloper); See LICENSE for licensing information.")
    sys.exit(0)

intents = discord.Intents.all()

OWNER = os.getenv("ALPHAGAMEBOT_OWNER_ID", 420052952686919690)

global cogw, listener
cogw = logging.getLogger("cogwheel")
listener = logging.getLogger("listener")
#if os.getenv("DEBUG") != None:
#    logging.basicConfig(level=logging.DEBUG)
#else:
#    logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="?", intents=intents)

##### BOT RECURRING BOT TASKS #####
@tasks.loop() # run forever when the function completes.
async def rotate_status():
    logging.getLogger("listener").debug("Dispatching RotateStatus task to agb.system.rotatingStatus.rotatingStatus")
    await agb.system.rotatingStatus.rotatingStatus(bot, cnx, CAN_USE_DATABASE)

@tasks.loop(seconds=15)
async def database_update():
    logging.getLogger("listener").debug("Dispatching DatabaseUpdate task to agb.system.databaseUpdate.handleDatabaseUpdate")
    agb.system.databaseUpdate.handleDatabaseUpdate(cnx, CAN_USE_DATABASE)

##### BOT EVENTS #####
@bot.listen('on_ready', once=True)
async def on_ready():
    bot.auto_sync_commands = True # Sync new commands with Discord.
    BOT_TASKS = [database_update, rotate_status]
    for task in BOT_TASKS:
        if not task.is_running():
            task.start()


    logging.info("Bot is now ready!")
    logging.info("Bot user is \"{0}\". (ID={1})".format(bot.user.name, bot.user.id))
    logging.info(f"Application ID is \"{bot.application_id}\".")
    logging.info(f"Syncronized {len(bot.application_commands)} application (slash) commands.")
@bot.listen('on_application_command_error')
async def on_application_command_error(interaction: discord.Interaction, error: discord.DiscordException):
    listener.debug("Dispatching ApplicationCommandError (/{0}) to agb.system.commandError.handleApplicationCommandError".format(interaction.command))
    # Essentially a proxy function
    return await agb.system.commandError.handleApplicationCommandError(interaction, error)

@bot.listen('on_message')
async def on_message(ctx: discord.Message):
    # Essentially a proxy function
    listener.debug(f"Dispatching message {ctx.id} to agb.system.message.handleOnMessage")
    return await agb.system.message.handleOnMessage(ctx, CAN_USE_DATABASE, cnx, args.notracking)

@bot.listen()
async def on_application_command(ctx: discord.context.ApplicationContext):
    listener.debug("Dispatching slash command /{0} to agb.system.applicationCommand.handleApplicationCommand".format(ctx.command))
    return await agb.system.applicationCommand.handleApplicationCommand(ctx, CAN_USE_DATABASE, cnx, args.notracking)

@bot.listen()
async def on_application_command_completion(interaction):
    if CAN_USE_DATABASE:
        cnx.commit()

MYSQL_SERVER = os.getenv("MYSQL_HOST", False)
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", False)
MYSQL_USER = os.getenv("MYSQL_USER", False)
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", False)

# helper function for human-readable strings (uses lambda because it's a one-liner)
humanString = lambda x: "[  SET]" if x else "[UNSET]"

# we rely on the fact that all strings are True, and if not found, default is the boolean False.
if args.nodatabase and args.requiredatabase:
    logging.warning("Conflicting flags!  You cannot have --nodatabase and --requiredatabase at the same time.  Please fix that!")
    sys.exit(1)

if not (MYSQL_SERVER and MYSQL_DATABASE and MYSQL_USER and MYSQL_PASSWORD) and not args.nodatabase:
    logging.warning("MySQL connection information is invalid!  MySQL connection is required to use specific commands.")
    logging.warning("These environment variables must be set:")
    logging.warning(f"{humanString(MYSQL_SERVER)} * MYSQL_HOST")
    logging.warning(f"{humanString(MYSQL_DATABASE)} * MYSQL_DATABASE")
    logging.warning(f"{humanString(MYSQL_USER)} * MYSQL_USER")
    logging.warning(f"{humanString(MYSQL_PASSWORD)} * MYSQL_PASSWORD")
    logging.warning("If you do not want to use the database, use the '-n' or '--nodatabase' flag.")

    if args.requiredatabase:
        logging.fatal("Database was force-enabled with '-r' or '--requiredatabase', but the database is not configured correctly.  Please check the environment variables and try again.")
        sys.exit(1)
    CAN_USE_DATABASE = False
    cnx = None
elif args.nodatabase:
    logging.warning("Database was force-disabled with '-n' or '--nodatabase'.  Database functionality is DISABLED.")
    CAN_USE_DATABASE = False
    cnx = None
else:
    logging.info(f"Connecting to MySQL server at \"{MYSQL_SERVER}\" using database \"{MYSQL_DATABASE}\" as DB user \"{MYSQL_USER}\".  MySQL/Connector version is {mysql.connector.__version__}.")
    CAN_USE_DATABASE = True
    cnx = mysql.connector.connect(
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_SERVER,
        database=MYSQL_DATABASE
    )
# set command cogs
mysql_cogs = 0
normal_cogs = 0
base_cogs = 0
invalid_cogs = 0
for cog in BOT_LOADED_COGS:
    # this is first b/c MySQLEnabledCogwheel inherits Cogwheel.
    logging.debug(f"Loading cog \"{cog.__name__}\"...")
    if issubclass(cog, agb.cogwheel.MySQLEnabledCogwheel):
        mysql_cogs += 1

        bot.add_cog(cog(bot, cnx, CAN_USE_DATABASE))
    elif issubclass(cog, agb.cogwheel.Cogwheel):
        normal_cogs += 1
        bot.add_cog(cog(bot))
    elif issubclass(cog, commands.Cog):
        base_cogs += 1
        bot.add_cog(cog(bot))
    else:
        invalid_cogs += 1
        logging.warning(f"Cog \"{cog.__name__}\" is of invalid type {cog}!  Skipping it...")

logging.info("Loaded {0} cogs: MySQLEnabledCogwheel: {1}, Cogwheel: {2}, Commands.Cog: {3}, with {4} invalid cogs.".format(
    mysql_cogs + normal_cogs + invalid_cogs,
    mysql_cogs,
    normal_cogs,
    base_cogs,
    invalid_cogs
))
if invalid_cogs > 0:
    logging.warning(f"{invalid_cogs} failed to initalize: They're not decendants of Cogwheel!")

if __name__ == "__main__":
    logging.info("Starting the bot...")
    token = os.getenv("TOKEN")
    tokenSource = "environment"

    if args.environment != None:
        logging.info("Loading the %s environment file because it was explicitly requested with '-e' or '--environment'." % args.environment)
        if not os.path.isfile(args.environment):
            logging.fatal("The environment file %s does not exist!  Please check the path and try again." % args.environment)
            sys.exit(1)
        if not load_dotenv(args.environment):
            logging.info("No (new) environment variables were loaded from the .env file.  This is normal if the file does not exist.")
        token = os.getenv("TOKEN")
        tokenSource = "environmentfile"

    if args.token:
        logging.warning("You tried to use the command line to set the bot's token.  This is insecure.  Please use the environment variable 'TOKEN' instead.")
        token = args.token
        tokenSource = "commandline"

    if token == None or token == "":
        logging.error("No token was given via the environment variable 'TOKEN', nor was one given via the commandline using '-t' or '--token'!")
        logging.error("Use '-e' or '--environment' to automatically load your .env file.")
        sys.exit(1)

    if agb.cogwheel.isDebug(argp=args) == True:
        logging.warning("Debug mode is ENABLED.  This is a development build.  Do not use this in a production environment.")
        
    try:
        logging.info("Logging in using static token from %s" % tokenSource)
        bot.run(token)
    except client_exceptions.ClientConnectorError as e:
        logging.fatal("Cannot connect to Discord's gateway!")
        logging.fatal("Maybe check your internet connection?")
        sys.exit(1)
    except discord.errors.LoginFailure as e:
        logging.fatal("LoginFailure: Invalid token given.  Please check the token and try again.")
        sys.exit(1)
    except Exception as e:
        logging.fatal("The bot has encountered a critical error and cannot continue.")
        logging.fatal("This is an uncaught exception on the bot run command.")
        logging.fatal("--- Here is some error information ---")
        logging.fatal("Error Type: %s" % str(type(e).__name__))
        logging.fatal("Error Message: %s" % repr(e))
        sys.exit(1)
