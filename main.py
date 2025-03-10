#!/usr/bin/env python
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
import logging
import logging.config
import agb.system.cogwheel
import sys
from dotenv import load_dotenv
from aiohttp import client_exceptions
import datetime
import argparse
import mysql.connector
import json
# system
import agb.system.commands.error
import agb.system.commands.command
import agb.system.guild.available
import agb.system.message.message
import agb.system.message.dms
import agb.system.rotatingStatus
import agb.system.commands.completion

# RequestHandler
import agb.system.requestHandler
# commands
import agb.user
import agb.utility
import agb.xkcd
import agb.memes
import agb.jokes
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
import agb.guild
import agb.combat
import agb.github

##### LIST OF COGS #####
BOT_LOADED_COGS = [
    agb.utility.UtilityCog,
    agb.xkcd.xkcdCog,
    agb.memes.MemesCog,
    agb.jokes.jokesCog,
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
    agb.guild.GuildCog,
    agb.combat.CombatCog,
    agb.github.GithubCog
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
    parser.add_argument("--discord-debug", help="Show debug discord gateway/client information, this will be noisy!", action="store_true")
    parser.add_argument("-s", "--enable-say", help="Enable the say functionality regardless of environment or debug mode.", action="store_true")
    parser.add_argument("-l", "--log-level", help="Set the log level to a specified level.  Valid levels are FATAL, ERROR, WARN, INFO, and DEBUG.")
    parser.add_argument("--silent", help="Synonym for --log-level FATAL.  Note that this will override any value specified in --log-level.", action="store_true")
    parser.add_argument("--strict", help="Kill the program if a cog fails to initialize", action="store_true")
    parser.add_argument("--say-trigger", help="Set the trigger for the say command.  Default is the bot's mention.")
    parser.add_argument("--dry-run", help="Run the bot in dry-run mode.  This will not connect to Discord.", action="store_true")
    args = parser.parse_args()
# Initalize logging services

logging.config.fileConfig("logging/main.ini") # load the config
LOG_LEVEL = logging.INFO
if args.debug: # args.debug:
    LOG_LEVEL = logging.DEBUG

# after above to override it
if args.log_level is not None:
    if args.log_level.upper() == "FATAL":
        LOG_LEVEL = logging.FATAL
    elif args.log_level.upper() == "ERROR":
        LOG_LEVEL = logging.ERROR
    elif args.log_level.upper() == "WARN" or args.log_level.upper() == "WARNING":
        LOG_LEVEL = logging.WARNING
    elif args.log_level.upper() == "INFO":
        LOG_LEVEL = logging.INFO
    elif args.log_level.upper() == "DEBUG":
        # you know, you could use -d to enable debug mode...
        LOG_LEVEL = logging.DEBUG
    else:
        logging.fatal("Invalid logging type \'%s\'!  --log-level should be FATAL, ERROR, WARN, INFO, or DEBUG", args.log_level)
        sys.exit(1)

if args.silent:
    LOG_LEVEL = logging.FATAL
# Load the logging file (logging/main.ini)
logging.lastResort.setLevel(logging.INFO)

if args.discord_debug:
    logging.getLogger("discord.client").setLevel(logging.DEBUG)
    logging.getLogger("discord.gateway").setLevel(logging.DEBUG)

if args.debug:
    os.environ["DEBUG"] = "1"
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
    print(f"AlphaGameBot Discord Bot Version {agb.system.cogwheel.getBotInformation()['VERSION']}")
    print(f"Copyright (C) {d.year}  Damien Boisvert (AlphaGameDeveloper); See LICENSE for licensing information.")
    sys.exit(0)

# ----- Initialize RequestHandler -----
agb.system.requestHandler.handler.initialize()
logging.info("Using %s version %s", discord.__name__, discord.__version__)
# ----- -----
if args.environment != None:
    if not os.path.isfile(args.environment):
        logging.error("Environment file %s doesn't exist." % args.environment)
    else:
        load_dotenv(args.environment)
        logging.info("Loaded environment file %s" % args.environment)

OWNER = os.getenv("ALPHAGAMEBOT_OWNER_ID", 420052952686919690)

global cogw, listener
cogw = logging.getLogger("cogwheel")
listener = logging.getLogger("listener")
#if os.getenv("DEBUG") != None:
#    logging.basicConfig(level=logging.DEBUG)
#else:
#    logging.basicConfig(level=logging.INFO)

# DISCORD GATEWAY ITENTS
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="?", intents=intents)

##### BOT RECURRING BOT TASKS #####
@tasks.loop() # run forever when the function completes.
async def rotate_status():
    logging.getLogger("listener").debug("Dispatching RotateStatus task to agb.system.rotatingStatus.rotatingStatus")
    await agb.system.rotatingStatus.rotatingStatus(bot, cnx, CAN_USE_DATABASE)

@tasks.loop(seconds=1)
async def database_reconnect():
    # source: https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-ping.html
    l = logging.getLogger("listener")
    if not CAN_USE_DATABASE: return
    
    try:
        cnx.ping()
    except mysql.connector.errors.InterfaceError:
        l.info("MySQL server connection was lost.  Attempting to reconnect...")
        cnx.ping(reconnect=True, attempts=5, delay=1)
    
##### BOT EVENTS #####
@bot.listen('on_ready', once=True)
async def on_ready():
    bot.auto_sync_commands = True # Sync new commands with Discord.
    BOT_TASKS = [database_reconnect, rotate_status]
    logging.debug("Starting tasks...")
    for task in BOT_TASKS:
        if not task.is_running():
            task.start()
    logging.debug("%s tasks started." % len(BOT_TASKS))
    logging.info("Bot is now ready!")
    logging.info("Bot user is \"{0}\". (ID={1})".format(bot.user.name, bot.user.id))
    logging.info(f"Application ID is \"{bot.application_id}\".")
    logging.info(f"Syncronized {len(bot.application_commands)} application (slash) commands.")

@bot.listen('on_application_command_error')
async def on_application_command_error(interaction: discord.Interaction, error: discord.DiscordException):
    listener.debug("Dispatching ApplicationCommandError (/{0}) to agb.system.commandError.handleApplicationCommandError".format(interaction.command))
    # Essentially a proxy function
    return await agb.system.commands.error.handleApplicationCommandError(interaction, error)

@bot.listen('on_message')
async def on_message(ctx: discord.Message):
    # Essentially a proxy function
    if not ctx.guild:
        listener.debug(f"Dispatching DM {ctx.id} to agb.system.dms.handleDMMessage")
        return await agb.system.message.dms.handleDMMessage(bot, ctx, cnx, CAN_USE_DATABASE)
    
    listener.debug(f"Dispatching message {ctx.id} to agb.system.message.handleOnMessage")
    return await agb.system.message.message.handleOnMessage(bot, ctx, cnx, CAN_USE_DATABASE, args.notracking, args.enable_say, args.say_trigger)

@bot.listen()
async def on_application_command(ctx: discord.context.ApplicationContext):
    listener.debug("Dispatching slash command /{0} to agb.system.applicationCommand.handleApplicationCommand".format(ctx.command))
    return await agb.system.commands.command.handleApplicationCommand(ctx, CAN_USE_DATABASE, cnx, args.notracking)

@bot.listen()
async def on_application_command_completion(interaction):
    listener.debug("Dispatching slash command /{0} to agb.system.commands.completion.handleApplicationCommandCompletion".format(interaction.command))
    return await agb.system.commands.completion.handleApplicationCommandCompletion(interaction, cnx, CAN_USE_DATABASE)

@bot.listen('on_guild_available')
async def guild_available(ctx):
    listener.debug("Dispatching guild_availiable to agb.system.guild.availiable.handleGuildAvailiable (GuildID: %s)", ctx.id)
    # Essentially a proxy function
    return await agb.system.guild.available.handleGuildAvailiable(ctx, cnx, CAN_USE_DATABASE)


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
    cnx.autocommit = True
# set command cogs
if not CAN_USE_DATABASE:
    logging.info("Database functionality is disabled!")
    
mysql_cogs = 0
normal_cogs = 0
base_cogs = 0
invalid_cogs = 0
failed_cogs = 0

for cog in BOT_LOADED_COGS:
    # this is first b/c MySQLEnabledCogwheel inherits Cogwheel.
    logging.debug(f"Loading cog \"{cog.__name__}\"...")
    if issubclass(cog, agb.system.cogwheel.MySQLEnabledCogwheel):
        mysql_cogs += 1

        addcog = lambda: bot.add_cog(cog(bot, cnx, CAN_USE_DATABASE))
        t = "MySQLEnabledCogwheel"
    elif issubclass(cog, agb.system.cogwheel.Cogwheel):
        normal_cogs += 1
        addcog = lambda: bot.add_cog(cog(bot))
        t = "Cogwheel"
    elif issubclass(cog, commands.Cog):
        base_cogs += 1
        addcog = lambda: bot.add_cog(cog(bot))
        t = "DiscordBaseCog"
    else:
        invalid_cogs += 1
        t = "Unknown"
        logging.warning(f"Cog \"{cog.__name__}\" is of invalid type {cog}!  Skipping it...")
    try:
        addcog() 
    except Exception as e:
        if args.strict:
            raise e
        failed_cogs += 1
        logging.error("An error occured whilst initializing cog \"%s\": %s", cog.__name__, repr(e))
    logging.debug("The type of this cog is %s" % t)
logging.info("Loaded {0} cogs: MySQLEnabledCogwheel: {1}, Cogwheel: {2}, Commands.Cog: {3}, with {4} invalid cogs.".format(
    mysql_cogs + normal_cogs + invalid_cogs,
    mysql_cogs,
    normal_cogs,
    base_cogs,
    invalid_cogs
))
if invalid_cogs > 0:
    logging.warning(f"{invalid_cogs} failed to initalize: They're not decendants of Cogwheel!")

if failed_cogs > 0:
    logging.error(f"{failed_cogs} failed to initialize!")
    
if __name__ == "__main__":
    logging.info("Starting the bot...")
    token = os.getenv("TOKEN")
    tokenSource = "environment"

    if args.environment is not None:
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
        if args.dry_run:
            logging.info("Ignoring the above, as dry-run mode does not require a token.")
        else:
            sys.exit(1)

    if agb.system.cogwheel.isDebug(argp=args) == True:
        logging.warning("Debug mode is ENABLED.  This is a development build.  Do not use this in a production environment.")
    
    webhook_url = os.getenv("WEBHOOK")
    if webhook_url:
        try:
            webhook_data = json.loads(agb.system.requestHandler.handler.get(webhook_url).text)
            logging.info("Webhook URL is set.  Webhook name is %s; Channel ID: %s.", webhook_data["name"], webhook_data["channel_id"])
        except json.JSONDecodeError:
            logging.error("The webhook URL is invalid!  Please check the URL and try again.")
            sys.exit(1)
    try:
        if args.dry_run:
            logging.info("Dry-run mode is enabled.  Stopping now, and not connecting to Discord.")
            sys.exit(0)
        logging.info("Logging in using static token from %s" % tokenSource)
        bot.run(token)
    except client_exceptions.ClientConnectorError as e:
        logging.fatal("Cannot connect to Discord's gateway!")
        logging.fatal("Maybe check your internet connection?")
        logging.fatal("Complete Error: %s" % repr(e))
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
    finally:
        if CAN_USE_DATABASE:
            cnx.close()
